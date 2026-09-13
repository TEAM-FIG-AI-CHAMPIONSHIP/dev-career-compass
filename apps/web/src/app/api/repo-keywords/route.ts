import {
  extractKeywordsFromManifest,
  pickLanguageKeywords,
  mergeKeywords,
} from "@/lib/repo-keywords";
import {
  fetchPublicRepositorySnapshot,
  fetchRepositoryTextFiles,
  GithubRepositoryError,
} from "@/lib/github-repository";
import { isDockerfilePath, isRecognizedManifestPath } from "@/lib/repository-evidence";

/**
 * GitHub 공개 저장소를 서버에서 훑어 표준 키워드를 뽑는다. 아무것도 저장하지
 * 않는다 — 요청마다 새로 조회하고 응답만 돌려준다.
 *
 * GITHUB_TOKEN 환경 변수가 있으면 시간당 5000회, 없으면 60회로 제한된다. 없어도
 * 정상 동작해야 한다(선택적).
 */

type Reason = "invalid_url" | "not_found" | "private" | "rate_limited" | "unknown";

const MAX_MANIFEST_SIZE_BYTES = 512000;
/** 아주 큰 모노레포에서 매니페스트를 무한정 받아오지 않도록 저장소당 상한을 둔다. */
const MAX_MANIFESTS_PER_REPO = 5;

function errorResponse(reason: Reason, status: number): Response {
  return Response.json({ ok: false, reason }, { status });
}

function repositoryErrorResponse(error: GithubRepositoryError): Response {
  switch (error.reason) {
    case "invalid_url":
      return errorResponse("invalid_url", 400);
    case "not_found_or_private":
      return errorResponse("not_found", 404);
    case "rate_limited":
      return errorResponse("rate_limited", 429);
    default:
      return errorResponse("unknown", 502);
  }
}

export async function POST(request: Request): Promise<Response> {
  let body: unknown;
  try {
    body = await request.json();
  } catch {
    return errorResponse("invalid_url", 400);
  }

  const url =
    typeof body === "object" && body !== null && "url" in body
      ? (body as { url: unknown }).url
      : undefined;

  if (typeof url !== "string") return errorResponse("invalid_url", 400);

  try {
    const snapshot = await fetchPublicRepositorySnapshot(url);
    const manifestEntries = snapshot.files
      .filter(
        (entry) =>
          entry.type === "blob" &&
          isRecognizedManifestPath(entry.path) &&
          (entry.size ?? 0) <= MAX_MANIFEST_SIZE_BYTES,
      )
      .slice(0, MAX_MANIFESTS_PER_REPO);
    const manifests = await fetchRepositoryTextFiles(snapshot, manifestEntries, {
      maxBlobBytes: MAX_MANIFEST_SIZE_BYTES,
    });
    const manifestKeywords = manifests.flatMap((file) =>
      extractKeywordsFromManifest(file.content),
    );
    const languageKeywords = pickLanguageKeywords(snapshot.languages);
    const dockerKeyword = snapshot.files.some(
      (entry) => entry.type === "blob" && isDockerfilePath(entry.path),
    )
      ? ["Docker"]
      : [];

    const keywords = mergeKeywords(languageKeywords, manifestKeywords, dockerKeyword);

    return Response.json({ ok: true, keywords });
  } catch (error) {
    if (error instanceof GithubRepositoryError) return repositoryErrorResponse(error);
    return errorResponse("unknown", 502);
  }
}
