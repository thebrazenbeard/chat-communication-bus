import "jsr:@supabase/functions-js/edge-runtime.d.ts";
import { createClient } from "npm:@supabase/supabase-js@2";

const OIDC_ISSUER = "https://token.actions.githubusercontent.com";
const JWKS_URL = `${OIDC_ISSUER}/.well-known/jwks`;
const EXPECTED_AUDIENCE = "chat-communication-bus-supabase";
const EXPECTED_REPOSITORY = "thebrazenbeard/chat-communication-bus";
const EXPECTED_WORKFLOW = `${EXPECTED_REPOSITORY}/.github/workflows/radar-bus-projection.yml@refs/heads/bus/`;
const MAX_FILES = 500;
const MAX_FILE_BYTES = 512 * 1024;
const MAX_BATCH_BYTES = 5 * 1024 * 1024;

let jwksCache: { expiresAt: number; keys: JsonWebKey[] } | null = null;

type Claims = Record<string, unknown>;
type Headers = Record<string, string>;

type SourceFile = {
  path: string;
  source_commit: string;
  source_committed_at: string;
  blob_sha: string;
  content_base64: string;
};

type Batch = {
  projection_version: number;
  repository: string;
  ref: string;
  branch_head: string;
  files: SourceFile[];
};

class HttpError extends Error {
  status: number;
  code: string;
  constructor(status: number, code: string) {
    super(code);
    this.status = status;
    this.code = code;
  }
}

function jsonResponse(status: number, body: Record<string, unknown>): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "content-type": "application/json; charset=utf-8" },
  });
}

function b64urlBytes(value: string): Uint8Array {
  const normalized = value.replace(/-/g, "+").replace(/_/g, "/");
  const padded = normalized + "=".repeat((4 - (normalized.length % 4)) % 4);
  let binary: string;
  try {
    binary = atob(padded);
  } catch {
    throw new HttpError(401, "OIDC_BASE64_INVALID");
  }
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

function b64urlJson(value: string): Record<string, unknown> {
  const bytes = b64urlBytes(value);
  try {
    return JSON.parse(new TextDecoder().decode(bytes));
  } catch {
    throw new HttpError(401, "OIDC_JSON_INVALID");
  }
}

async function getJwks(): Promise<JsonWebKey[]> {
  const now = Date.now();
  if (jwksCache && jwksCache.expiresAt > now) return jwksCache.keys;
  const response = await fetch(JWKS_URL, { headers: { accept: "application/json" } });
  if (!response.ok) throw new HttpError(503, "OIDC_JWKS_UNAVAILABLE");
  const data = await response.json();
  if (!data || !Array.isArray(data.keys)) throw new HttpError(503, "OIDC_JWKS_INVALID");
  jwksCache = { expiresAt: now + 10 * 60 * 1000, keys: data.keys as JsonWebKey[] };
  return jwksCache.keys;
}

function stringClaim(claims: Claims, name: string): string {
  const value = claims[name];
  if (typeof value !== "string" || !value) throw new HttpError(403, `OIDC_${name.toUpperCase()}_MISSING`);
  return value;
}

function audienceIncludes(aud: unknown, expected: string): boolean {
  if (typeof aud === "string") return aud === expected;
  return Array.isArray(aud) && aud.some((value) => value === expected);
}

async function verifyGithubOidc(token: string): Promise<Claims> {
  const parts = token.split(".");
  if (parts.length !== 3) throw new HttpError(401, "OIDC_TOKEN_SHAPE_INVALID");
  const header = b64urlJson(parts[0]);
  const claims = b64urlJson(parts[1]);
  if (header.alg !== "RS256" || typeof header.kid !== "string") {
    throw new HttpError(401, "OIDC_ALGORITHM_INVALID");
  }

  const keys = await getJwks();
  const jwk = keys.find((candidate) => candidate.kid === header.kid);
  if (!jwk) throw new HttpError(401, "OIDC_KEY_NOT_FOUND");
  const key = await crypto.subtle.importKey(
    "jwk",
    jwk,
    { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
    false,
    ["verify"],
  );
  const verified = await crypto.subtle.verify(
    "RSASSA-PKCS1-v1_5",
    key,
    b64urlBytes(parts[2]),
    new TextEncoder().encode(`${parts[0]}.${parts[1]}`),
  );
  if (!verified) throw new HttpError(401, "OIDC_SIGNATURE_INVALID");

  const now = Math.floor(Date.now() / 1000);
  if (claims.iss !== OIDC_ISSUER) throw new HttpError(403, "OIDC_ISSUER_INVALID");
  if (!audienceIncludes(claims.aud, EXPECTED_AUDIENCE)) throw new HttpError(403, "OIDC_AUDIENCE_INVALID");
  if (typeof claims.exp !== "number" || claims.exp <= now) throw new HttpError(403, "OIDC_EXPIRED");
  if (typeof claims.nbf === "number" && claims.nbf > now + 30) throw new HttpError(403, "OIDC_NOT_YET_VALID");
  if (stringClaim(claims, "repository") !== EXPECTED_REPOSITORY) throw new HttpError(403, "OIDC_REPOSITORY_INVALID");
  if (stringClaim(claims, "event_name") !== "push") throw new HttpError(403, "OIDC_EVENT_INVALID");
  const ref = stringClaim(claims, "ref");
  if (!ref.startsWith("refs/heads/bus/")) throw new HttpError(403, "OIDC_REF_INVALID");
  const workflowRef = stringClaim(claims, "workflow_ref");
  if (!workflowRef.startsWith(EXPECTED_WORKFLOW)) throw new HttpError(403, "OIDC_WORKFLOW_INVALID");
  stringClaim(claims, "sha");
  return claims;
}

function requireString(value: unknown, code: string): string {
  if (typeof value !== "string" || !value.trim()) throw new HttpError(422, code);
  return value.trim();
}

function parseBatch(value: unknown, claims: Claims): Batch {
  if (!value || typeof value !== "object") throw new HttpError(400, "BATCH_REQUIRED");
  const raw = value as Record<string, unknown>;
  if (raw.projection_version !== 1) throw new HttpError(422, "PROJECTION_VERSION_INVALID");
  const repository = requireString(raw.repository, "BATCH_REPOSITORY_REQUIRED");
  const ref = requireString(raw.ref, "BATCH_REF_REQUIRED");
  const branchHead = requireString(raw.branch_head, "BATCH_HEAD_REQUIRED");
  if (repository !== stringClaim(claims, "repository")) throw new HttpError(403, "BATCH_REPOSITORY_MISMATCH");
  if (ref !== stringClaim(claims, "ref")) throw new HttpError(403, "BATCH_REF_MISMATCH");
  if (branchHead !== stringClaim(claims, "sha")) throw new HttpError(403, "BATCH_HEAD_MISMATCH");
  if (!Array.isArray(raw.files) || raw.files.length > MAX_FILES) throw new HttpError(422, "BATCH_FILES_INVALID");

  const files = raw.files.map((item): SourceFile => {
    if (!item || typeof item !== "object") throw new HttpError(422, "SOURCE_FILE_INVALID");
    const file = item as Record<string, unknown>;
    const path = requireString(file.path, "SOURCE_PATH_REQUIRED");
    if (!/^messages\/[A-Za-z0-9._/-]+\.md$/.test(path) || path.includes("..")) {
      throw new HttpError(422, "SOURCE_PATH_INVALID");
    }
    const sourceCommit = requireString(file.source_commit, "SOURCE_COMMIT_REQUIRED");
    const sourceCommittedAt = requireString(file.source_committed_at, "SOURCE_COMMITTED_AT_REQUIRED");
    const blobSha = requireString(file.blob_sha, "SOURCE_BLOB_REQUIRED");
    const contentBase64 = requireString(file.content_base64, "SOURCE_CONTENT_REQUIRED");
    if (!/^[0-9a-f]{40}$/.test(sourceCommit) || !/^[0-9a-f]{40}$/.test(blobSha)) {
      throw new HttpError(422, "SOURCE_GIT_SHA_INVALID");
    }
    return {
      path,
      source_commit: sourceCommit,
      source_committed_at: sourceCommittedAt,
      blob_sha: blobSha,
      content_base64: contentBase64,
    };
  });
  return { projection_version: 1, repository, ref, branch_head: branchHead, files };
}

function base64Bytes(value: string): Uint8Array {
  let binary: string;
  try {
    binary = atob(value);
  } catch {
    throw new HttpError(422, "SOURCE_CONTENT_BASE64_INVALID");
  }
  return Uint8Array.from(binary, (char) => char.charCodeAt(0));
}

function hex(bytes: ArrayBuffer): string {
  return Array.from(new Uint8Array(bytes), (value) => value.toString(16).padStart(2, "0")).join("");
}

async function sha256(bytes: Uint8Array): Promise<string> {
  return hex(await crypto.subtle.digest("SHA-256", bytes));
}

async function gitBlobSha1(bytes: Uint8Array): Promise<string> {
  const prefix = new TextEncoder().encode(`blob ${bytes.length}\0`);
  const combined = new Uint8Array(prefix.length + bytes.length);
  combined.set(prefix, 0);
  combined.set(bytes, prefix.length);
  return hex(await crypto.subtle.digest("SHA-1", combined));
}

function normalizeIdentity(value: string): string {
  const key = value.trim().toLowerCase();
  if (key === "bridget") return "brigit";
  if (key === "vera/sol" || key === "vera-sol") return "vera";
  return key;
}

function parseBool(value: string | undefined, code: string): boolean {
  if (value === undefined || value.trim() === "") return false;
  const normalized = value.trim().toLowerCase();
  if (["true", "yes", "1"].includes(normalized)) return true;
  if (["false", "no", "0"].includes(normalized)) return false;
  throw new HttpError(422, code);
}

function normalizeTimestamp(value: string, code: string): string {
  const trimmed = value.trim();
  let candidate = trimmed;
  if (/^\d{4}-\d{2}-\d{2}$/.test(candidate)) candidate = `${candidate}T00:00:00Z`;
  else if (!/(Z|[+-]\d{2}:\d{2})$/i.test(candidate)) throw new HttpError(422, code);
  if (!Number.isFinite(Date.parse(candidate))) throw new HttpError(422, code);
  return candidate;
}

function lineRecords(text: string): { content: string; start: number; end: number }[] {
  const records: { content: string; start: number; end: number }[] = [];
  let start = 0;
  while (start < text.length) {
    const newline = text.indexOf("\n", start);
    const end = newline === -1 ? text.length : newline + 1;
    let content = text.slice(start, newline === -1 ? text.length : newline);
    if (content.endsWith("\r")) content = content.slice(0, -1);
    records.push({ content, start, end });
    start = end;
  }
  if (text.length === 0) records.push({ content: "", start: 0, end: 0 });
  return records;
}

function splitDocument(text: string): { headers: Headers; body: string } {
  const lines = lineRecords(text);
  let index = 0;
  if (lines[index]?.content.trimStart().startsWith("#")) {
    index += 1;
    while (index < lines.length && lines[index].content.trim() === "") index += 1;
  }

  const headers: Headers = {};
  let started = false;
  let bodyStart = text.length;
  for (; index < lines.length; index += 1) {
    const line = lines[index];
    if (line.content.trim() === "") {
      if (started) {
        bodyStart = line.end;
        index += 1;
        break;
      }
      continue;
    }
    const match = /^([A-Za-z0-9_-]+)\s*:\s*(.*)$/.exec(line.content);
    if (!match) {
      if (!started) throw new HttpError(422, "HEADER_BLOCK_REQUIRED");
      bodyStart = line.start;
      break;
    }
    started = true;
    const key = match[1].toLowerCase().replaceAll("-", "_");
    if (Object.prototype.hasOwnProperty.call(headers, key)) throw new HttpError(422, `DUPLICATE_HEADER_${key.toUpperCase()}`);
    headers[key] = match[2].trim();
  }
  if (!started) throw new HttpError(422, "HEADER_BLOCK_REQUIRED");
  return { headers, body: text.slice(bodyStart) };
}

async function projectFile(
  supabase: ReturnType<typeof createClient>,
  batch: Batch,
  file: SourceFile,
): Promise<string> {
  const bytes = base64Bytes(file.content_base64);
  if (bytes.length > MAX_FILE_BYTES) throw new HttpError(422, "MESSAGE_FILE_TOO_LARGE");
  const observedBlob = await gitBlobSha1(bytes);
  if (observedBlob !== file.blob_sha) throw new HttpError(422, "GIT_BLOB_SHA_MISMATCH");

  let text: string;
  try {
    text = new TextDecoder("utf-8", { fatal: true }).decode(bytes);
  } catch {
    throw new HttpError(422, "MESSAGE_NOT_UTF8");
  }
  const { headers, body } = splitDocument(text);
  const messageId = requireString(headers.message_id, "MESSAGE_ID_REQUIRED");
  const writer = normalizeIdentity(requireString(headers.writer, "WRITER_REQUIRED"));
  const createdAt = headers.created_at
    ? normalizeTimestamp(headers.created_at, "INVALID_CREATED_AT")
    : normalizeTimestamp(file.source_committed_at, "INVALID_SOURCE_COMMITTED_AT");
  const createdAtBasis = headers.created_at ? "message_header" : "source_commit";
  const audience = (headers.intended_recipient ?? "")
    .split(",")
    .map((value) => value.trim())
    .filter(Boolean)
    .map(normalizeIdentity);
  const requiresAck = parseBool(headers.requires_reply, "INVALID_REQUIRES_REPLY") ||
    parseBool(headers.requires_ack, "INVALID_REQUIRES_ACK");

  const bodyBytes = new TextEncoder().encode(body);
  const fullHash = await sha256(bytes);
  const bodyHash = await sha256(bodyBytes);
  const sourceRefs = [
    `github://${batch.repository}@${file.source_commit}/${file.path}`,
    `github-ref://${batch.repository}/${batch.ref}@${batch.branch_head}`,
    `git-blob:${file.blob_sha}`,
  ];
  const metadata: Record<string, unknown> = {
    ...headers,
    created_at_basis: createdAtBasis,
    source_repository: batch.repository,
    source_ref: batch.ref,
    source_branch_head: batch.branch_head,
    source_path: file.path,
    source_commit: file.source_commit,
    source_blob_sha: file.blob_sha,
    body_sha256: bodyHash,
    body_length: bodyBytes.length,
  };

  const { data, error } = await supabase.rpc("radar_project_bus_message_v1", {
    p_message_id: messageId,
    p_created_at: createdAt,
    p_sender: writer,
    p_audience: audience,
    p_requires_ack: requiresAck,
    p_source_refs: sourceRefs,
    p_content_hash: fullHash,
    p_idempotency_key: `chat-bus:${messageId}:${fullHash}`,
    p_payload: metadata,
  });
  if (error) throw new HttpError(500, `PROJECTION_RPC_FAILED:${error.code ?? "unknown"}`);
  if (data !== "INSERTED" && data !== "IDEMPOTENT" && data !== "CONFLICT") {
    throw new HttpError(500, "PROJECTION_RPC_RESULT_INVALID");
  }
  return data;
}

Deno.serve(async (req: Request) => {
  if (req.method !== "POST") return jsonResponse(405, { error: "METHOD_NOT_ALLOWED" });
  try {
    const auth = req.headers.get("authorization") ?? "";
    if (!auth.startsWith("Bearer ")) throw new HttpError(401, "OIDC_BEARER_REQUIRED");
    const claims = await verifyGithubOidc(auth.slice("Bearer ".length).trim());
    const rawBody = await req.json();
    const batch = parseBatch(rawBody, claims);

    let totalBytes = 0;
    for (const file of batch.files) {
      const approxBytes = Math.floor(file.content_base64.length * 0.75);
      totalBytes += approxBytes;
      if (totalBytes > MAX_BATCH_BYTES) throw new HttpError(422, "BATCH_TOO_LARGE");
    }

    const supabaseUrl = Deno.env.get("SUPABASE_URL");
    const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY");
    if (!supabaseUrl || !serviceRoleKey) throw new HttpError(500, "SUPABASE_RUNTIME_CREDENTIALS_MISSING");
    const supabase = createClient(supabaseUrl, serviceRoleKey, {
      auth: { persistSession: false, autoRefreshToken: false },
    });

    const counts = { inserted: 0, idempotent: 0, conflicts: 0 };
    for (const file of batch.files) {
      const result = await projectFile(supabase, batch, file);
      if (result === "INSERTED") counts.inserted += 1;
      else if (result === "IDEMPOTENT") counts.idempotent += 1;
      else counts.conflicts += 1;
    }

    return jsonResponse(counts.conflicts > 0 ? 409 : 200, {
      ok: counts.conflicts === 0,
      repository: batch.repository,
      ref: batch.ref,
      branch_head: batch.branch_head,
      files: batch.files.length,
      ...counts,
    });
  } catch (error) {
    if (error instanceof HttpError) return jsonResponse(error.status, { ok: false, error: error.code });
    return jsonResponse(500, { ok: false, error: "UNEXPECTED_INGEST_FAILURE" });
  }
});
