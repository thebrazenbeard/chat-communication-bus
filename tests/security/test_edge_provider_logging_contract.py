"""Source-custody checks for the Bus Edge provider diagnostics boundary.

These tests do not assert that a particular Supabase version is deployed.
"""

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
EDGE = ROOT / "supabase" / "functions" / "github-bus-ingest"


class EdgeProviderLoggingContractTests(unittest.TestCase):
    def test_unknown_exceptions_do_not_log_raw_exception_objects(self) -> None:
        handler = (EDGE / "handler.ts").read_text(encoding="utf-8")
        self.assertNotIn("console.error(error)", handler)
        self.assertIn('console.error("RADAR_PROVIDER_INTERNAL_ERROR")', handler)
        self.assertIn('import { provider503LogEvent } from "./provider_503_log.ts"', handler)

    def test_handled_503_codes_are_redacted_by_a_strict_allowlist(self) -> None:
        handler = (EDGE / "handler.ts").read_text(encoding="utf-8")
        helper = (EDGE / "provider_503_log.ts").read_text(encoding="utf-8")
        self.assertIn("provider503LogEvent(error.status, error.code)", handler)
        self.assertIn("if (diagnostic !== null) console.warn(diagnostic)", handler)
        self.assertIn("if (status !== 503) return null", helper)
        self.assertIn('typeof code === "string" && PROVIDER_503_CODES.has(code)', helper)
        self.assertIn(': "UNKNOWN";', helper)
        self.assertEqual(helper.count('"OIDC_JWKS_'), 2)
        self.assertIn('"PROVIDER_CONFIGURATION_MISSING"', helper)


if __name__ == "__main__":
    unittest.main()
