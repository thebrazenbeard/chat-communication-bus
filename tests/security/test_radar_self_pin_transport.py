"""Source-only tests of the pre-checkout Radar workflow OIDC bootstrap.

No real Actions token, provider, workflow dispatch, or external network access.
"""

from __future__ import annotations

import ast
import base64
from contextlib import ExitStack
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
from threading import Thread
import unittest
from unittest.mock import patch
import urllib.request


WORKFLOW = Path(__file__).resolve().parents[2] / ".github" / "workflows" / "radar-trusted-projector.yml"


def _inline_bootstrap() -> str:
    source = WORKFLOW.read_text(encoding="utf-8")
    marker = "          python - <<'PY'\n"
    assert marker in source, "missing self-pin bootstrap source"
    block = source.split(marker, 1)[1].split("\n          PY", 1)[0]
    return "\n".join(line[10:] if line.startswith("          ") else line for line in block.splitlines())


class _RedirectSink(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        self.server.auth_headers.append(self.headers.get("Authorization"))
        if self.server.redirect_to:
            self.send_response(302)
            self.send_header("Location", self.server.redirect_to)
            self.end_headers()
        else:
            body = b'{"value":"synthetic-invalid-jwt"}'
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    def log_message(self, *_args):
        return


class _MockHttpsResponse:
    def __init__(self, data):
        self.data = data

    def read(self, limit):
        return self.data[:limit]

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False


class WorkflowSelfPinTransportTests(unittest.TestCase):
    def setUp(self):
        self._stack = ExitStack()
        self.addCleanup(self._stack.close)
        self.sink = self._server()
        self.origin = self._server(redirect_to=f"http://127.0.0.1:{self.sink.server_port}/sink")

    def _server(self, redirect_to=None):
        server = ThreadingHTTPServer(("127.0.0.1", 0), _RedirectSink)
        server.redirect_to = redirect_to
        server.auth_headers = []
        thread = Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self._stack.callback(thread.join, 2)
        self._stack.callback(server.server_close)
        self._stack.callback(server.shutdown)
        return server

    def test_real_urllib_redirect_never_forwards_synthetic_runner_bearer(self):
        with TemporaryDirectory() as tmp:
            env = dict(os.environ)
            env.update({
                "ACTIONS_ID_TOKEN_REQUEST_URL": f"http://127.0.0.1:{self.origin.server_port}/oidc",
                "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "synthetic-runner-secret",
                "GITHUB_OUTPUT": str(Path(tmp) / "output"),
            })
            proc = subprocess.run(
                [sys.executable, "-c", _inline_bootstrap()],
                env=env,
                text=True,
                capture_output=True,
                timeout=8,
                check=False,
            )
        self.assertNotEqual(proc.returncode, 0)
        self.assertEqual(self.sink.auth_headers, [])

    def test_extracted_bootstrap_redirect_handler_rejects_real_urllib_302(self):
        module = ast.parse(_inline_bootstrap())
        classes = [
            node for node in module.body
            if isinstance(node, ast.ClassDef) and node.name == "RejectRunnerBearerRedirect"
        ]
        self.assertEqual(len(classes), 1)
        only_class = ast.Module(body=classes, type_ignores=[])
        namespace = {"urllib": urllib, "RuntimeError": RuntimeError}
        exec(compile(only_class, "workflow-inline-redirect-handler", "exec"), namespace)
        request = urllib.request.Request(
            f"http://127.0.0.1:{self.origin.server_port}/synthetic",
            headers={"Authorization": "Bearer synthetic-only"},
        )
        with self.assertRaises(Exception):
            urllib.request.build_opener(namespace["RejectRunnerBearerRedirect"]()).open(
                request, timeout=3
            )
        self.assertEqual(self.origin.auth_headers, ["Bearer synthetic-only"])
        self.assertEqual(self.sink.auth_headers, [])

    def test_inline_https_response_shapes_and_valid_claims(self):
        sha = "a" * 40
        claims = {
            "repository": "thebrazenbeard/chat-communication-bus",
            "job_workflow_sha": sha,
            "job_workflow_ref": (
                "thebrazenbeard/chat-communication-bus/.github/workflows/"
                f"radar-trusted-projector.yml@{sha}"
            ),
        }

        def jwt(claims_raw):
            segment = base64.urlsafe_b64encode(claims_raw).decode().rstrip("=")
            return json.dumps({"value": f"synthetic.{segment}.signature"}).encode()

        cases = (
            (b"[]", "RADAR_SELF_PIN_OIDC_RESPONSE_INVALID"),
            (jwt(b"[]"), "RADAR_SELF_PIN_CLAIMS_INVALID"),
            (b'{"value":"synthetic.*.signature"}', "RADAR_SELF_PIN_CLAIMS_INVALID"),
            (jwt(b'{"'), "RADAR_SELF_PIN_CLAIMS_INVALID"),
            (b"x" * (64 * 1024 + 1), "RADAR_SELF_PIN_OIDC_RESPONSE_TOO_LARGE"),
            (jwt(json.dumps(claims).encode()), None),
        )
        for raw, expected_error in cases:
            with self.subTest(expected_error=expected_error):
                with TemporaryDirectory() as tmp:
                    output_path = Path(tmp) / "output"
                    env = {
                        "ACTIONS_ID_TOKEN_REQUEST_URL": "https://pipelines.actions.githubusercontent.com/oidc",
                        "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "synthetic-runner-secret",
                        "GITHUB_OUTPUT": str(output_path),
                    }
                    response = _MockHttpsResponse(raw)

                    class _FakeOpener:
                        def open(self, request, *, timeout):
                            return response

                    with patch.dict(os.environ, env), patch(
                        "urllib.request.build_opener", return_value=_FakeOpener()
                    ):
                        if expected_error:
                            with self.assertRaises(SystemExit) as raised:
                                exec(_inline_bootstrap(), {"__name__": "__main__"})
                            self.assertEqual(str(raised.exception), expected_error)
                        else:
                            exec(_inline_bootstrap(), {"__name__": "__main__"})
                            self.assertEqual(output_path.read_text(), f"sha={sha}\n")


if __name__ == "__main__":
    unittest.main()
