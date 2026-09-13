import {
  parseGithubUrl,
  extractKeywordsFromManifest,
  pickLanguageKeywords,
  mergeKeywords,
} from "@/lib/repo-keywords";

/**
 * GitHub 공개 저장소를 서버에서 훑어 표준 키워드를 뽑는다. 아무것도 저장하지
 * 않는다 — 요청마다 새로 조회하고 응답만 돌려준다.
 *
 * GITHUB_TOKEN 환경 변수가 있으면 시간당 5000회, 없으면 60회로 제한된다. 없어도
 * 정상 동작해야 한다(선택적).
 */

const GITHUB_API = "https://api.github.com";
const REQUEST_TIMEOUT_MS = 8000;

const RECOGNIZED_MANIFESTS = [
  "package.json",
  "requirements.txt",
  "pyproject.toml",
  "Pipfile",
  "pom.xml",
  "build.gradle",
  "build.gradle.kts",
  "go.mod",
  "Cargo.toml",
  "Gemfile",
  "composer.json",
];

type GithubRepoResponse = { private?: boolean; default_branch?: string };
type GithubTreeEntry = { path: string; type: string; sha: string; size?: number };
type GithubTreeResponse = { tree?: GithubTreeEntry[] };
type GithubBlobResponse = { content: string; encoding: string };
type Reason = "invalid_url" | "not_found" | "private" | "rate_limited" | "unknown";

const MAX_MANIFEST_SIZE_BYTES = 512000;
/** 아주 큰 모노레포에서 매니페스트를 무한정 받아오지 않도록 저장소당 상한을 둔다. */
const MAX_MANIFESTS_PER_REPO = 5;

/** "apps/api/package.json" → "package.json" */
function basename(path: string): string {
  const index = path.lastIndexOf("/");
  return index === -1 ? path : path.slice(index + 1);
}

function githubHeaders(url: string): HeadersInit {
  const headers: Record<string, string> = { Accept: "application/vnd.github+json" };
  if (process.env.GITHUB_TOKEN && new URL(url).hostname === "api.github.com") {
    headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  }
  return headers;
}

async function fetchGithub(url: string): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);
  try {
    return await fetch(url, {
      headers: githubHeaders(url),
      signal: controller.signal,
      cache: "no-store",
    });
  } finally {
    clearTimeout(timeout);
  }
}

function errorResponse(reason: Reason, status: number): Response {
  return Response.json({ ok: false, reason }, { status });
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

  const parsed = parseGithubUrl(url);
  if (!parsed) return errorResponse("invalid_url", 400);

  const { owner, repo } = parsed;

  try {
    const repoRes = await fetchGithub(`${GITHUB_API}/repos/${owner}/${repo}`);
    if (repoRes.status === 404) return errorResponse("not_found", 404);
    if (repoRes.status === 403) return errorResponse("rate_limited", 429);
    if (!repoRes.ok) return errorResponse("unknown", 502);

    const repoData = (await repoRes.json()) as GithubRepoResponse;
    if (repoData.private) return errorResponse("private", 403);

    const branch = repoData.default_branch ?? "main";

    const [languagesRes, treeRes] = await Promise.all([
      fetchGithub(`${GITHUB_API}/repos/${owner}/${repo}/languages`),
      fetchGithub(`${GITHUB_API}/repos/${owner}/${repo}/git/trees/${branch}?recursive=1`),
    ]);

    const languages = languagesRes.ok
      ? ((await languagesRes.json()) as Record<string, number>)
      : {};
    const treeJson = treeRes.ok ? ((await treeRes.json()) as GithubTreeResponse) : {};
    const allFiles = treeJson.tree ?? [];

    const manifestEntries = allFiles
      .filter(
        (entry) =>
          entry.type === "blob" &&
          RECOGNIZED_MANIFESTS.includes(basename(entry.path)) &&
          (entry.size ?? 0) <= MAX_MANIFEST_SIZE_BYTES,
      )
      .slice(0, MAX_MANIFESTS_PER_REPO);

    const manifestTexts = await Promise.all(
      manifestEntries.map(async (entry) => {
        const res = await fetchGithub(`${GITHUB_API}/repos/${owner}/${repo}/git/blobs/${entry.sha}`);
        if (!res.ok) return "";
        const blob = (await res.json()) as GithubBlobResponse;
        return Buffer.from(blob.content, "base64").toString("utf-8");
      }),
    );

    const manifestKeywords = manifestTexts.flatMap((text) => extractKeywordsFromManifest(text));
    const languageKeywords = pickLanguageKeywords(languages);
    const dockerKeyword = allFiles.some(
      (entry) => entry.type === "blob" && basename(entry.path) === "Dockerfile",
    )
      ? ["Docker"]
      : [];

    const keywords = mergeKeywords(languageKeywords, manifestKeywords, dockerKeyword);

    return Response.json({ ok: true, keywords });
  } catch {
    return errorResponse("unknown", 502);
  }
}
