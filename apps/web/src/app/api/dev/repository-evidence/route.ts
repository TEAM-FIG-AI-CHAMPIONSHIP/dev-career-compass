import { previewRepositoryEvidence, GithubRepositoryError } from "@/lib/github-repository";
import type { RepositoryEvidencePreviewResponse } from "@/types/repository-evidence-preview";

const ROLE_IDS = new Set(["backend", "frontend", "data-ai", "mobile"]);

function json(body: RepositoryEvidencePreviewResponse, status = 200): Response {
  return Response.json(body, {
    status,
    headers: { "Cache-Control": "no-store" },
  });
}

function githubError(error: GithubRepositoryError): Response {
  switch (error.reason) {
    case "invalid_url":
      return json({ ok: false, reason: "invalid_url" }, 400);
    case "not_found_or_private":
      return json({ ok: false, reason: "not_found_or_private" }, 404);
    case "rate_limited":
      return json({ ok: false, reason: "github_rate_limited" }, 429);
    case "timeout":
      return json({ ok: false, reason: "github_timeout" }, 504);
    default:
      return json({ ok: false, reason: "unknown" }, 502);
  }
}

/** 공개 저장소 원문 일부를 반환하므로 프로덕션에서는 존재하지 않는 개발 전용 API다. */
export async function POST(request: Request): Promise<Response> {
  if (process.env.NODE_ENV === "production") {
    return new Response(null, { status: 404 });
  }

  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return json({ ok: false, reason: "invalid_request" }, 400);
  }

  const url =
    typeof body === "object" && body !== null && "url" in body
      ? (body as { url: unknown }).url
      : undefined;
  const roleId =
    typeof body === "object" && body !== null && "roleId" in body
      ? (body as { roleId: unknown }).roleId
      : undefined;

  if (typeof url !== "string") return json({ ok: false, reason: "invalid_request" }, 400);
  if (typeof roleId !== "string" || !ROLE_IDS.has(roleId)) {
    return json({ ok: false, reason: "invalid_role" }, 400);
  }

  const startedAt = performance.now();
  try {
    const evidence = await previewRepositoryEvidence(url, roleId);
    return json({ ok: true, elapsedMs: Math.round(performance.now() - startedAt), evidence });
  } catch (error) {
    if (error instanceof GithubRepositoryError) return githubError(error);
    return json({ ok: false, reason: "unknown" }, 502);
  }
}
