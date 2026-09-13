import "server-only";

import { parseGithubUrl } from "@/lib/repo-keywords";
import {
  DEFAULT_CONTENT_LIMITS,
  DEFAULT_SELECTION_LIMITS,
  evidenceExclusionReason,
  prepareEvidenceFiles,
  rankEvidenceFile,
  selectRepositoryEvidenceFiles,
  type EvidenceExclusionReason,
  type EvidenceContentLimits,
  type EvidenceSelectionLimits,
  EVIDENCE_SELECTION_VERSION,
  type PreparedEvidenceFile,
  type RepositoryTreeFile,
  type SelectedEvidenceFile,
} from "@/lib/repository-evidence";

const GITHUB_API = "https://api.github.com";
const DEFAULT_TIMEOUT_MS = 8_000;

export type GithubRepositoryFailure =
  | "invalid_url"
  | "not_found_or_private"
  | "rate_limited"
  | "timeout"
  | "unknown";

export class GithubRepositoryError extends Error {
  constructor(
    readonly reason: GithubRepositoryFailure,
    message: string,
  ) {
    super(message);
    this.name = "GithubRepositoryError";
  }
}

export type GithubRepositorySnapshot = {
  owner: string;
  repo: string;
  url: string;
  defaultBranch: string;
  commitSha: string;
  treeSha: string;
  treeTruncated: boolean;
  languages: Record<string, number>;
  files: RepositoryTreeFile[];
};

export type RepositoryEvidenceBundle = {
  repository: Omit<GithubRepositorySnapshot, "files" | "languages">;
  selectionVersion: number;
  languages: Record<string, number>;
  files: Array<
    PreparedEvidenceFile & {
      startLine: number;
      endLine: number;
      sourceUrl: string;
    }
  >;
  selectedFileCount: number;
  omittedFileCount: number;
  omittedFiles: Array<
    SelectedEvidenceFile & {
      sourceUrl: string;
    }
  >;
};

export type EvidenceDiagnosticReason = EvidenceExclusionReason | "selection_limit";

export type RepositoryEvidenceDiagnostics = {
  totalTreeEntries: number;
  eligibleFileCount: number;
  exclusions: Array<{
    reason: EvidenceDiagnosticReason;
    count: number;
    examplePaths: string[];
  }>;
};

export type RepositoryEvidencePreview = RepositoryEvidenceBundle & {
  diagnostics: RepositoryEvidenceDiagnostics;
};

type Fetcher = (input: string | URL | Request, init?: RequestInit) => Promise<Response>;

type GithubOptions = {
  fetcher?: Fetcher;
  timeoutMs?: number;
};

type CollectOptions = GithubOptions & {
  selectionLimits?: EvidenceSelectionLimits;
  contentLimits?: EvidenceContentLimits;
};

type BlobOptions = GithubOptions & {
  maxBlobBytes?: number;
};

type GithubRepoResponse = { private?: boolean; default_branch?: string };
type GithubCommitResponse = { sha?: string; commit?: { tree?: { sha?: string } } };
type GithubTreeResponse = {
  sha?: string;
  truncated?: boolean;
  tree?: RepositoryTreeFile[];
};
type GithubBlobResponse = { content?: string; encoding?: string };

function githubHeaders(): HeadersInit {
  const headers: Record<string, string> = {
    Accept: "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
  };
  if (process.env.GITHUB_TOKEN) headers.Authorization = `Bearer ${process.env.GITHUB_TOKEN}`;
  return headers;
}

async function fetchGithub(
  path: string,
  { fetcher = fetch, timeoutMs = DEFAULT_TIMEOUT_MS }: GithubOptions = {},
): Promise<Response> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetcher(`${GITHUB_API}${path}`, {
      headers: githubHeaders(),
      signal: controller.signal,
      cache: "no-store",
    });
  } catch (error) {
    if (error instanceof Error && error.name === "AbortError") {
      throw new GithubRepositoryError("timeout", "GitHub request timed out");
    }
    throw new GithubRepositoryError("unknown", "GitHub request failed");
  } finally {
    clearTimeout(timeout);
  }
}

function failureFromResponse(response: Response): GithubRepositoryError {
  if (response.status === 404) {
    return new GithubRepositoryError("not_found_or_private", "Repository was not found");
  }
  if (response.status === 403 || response.status === 429) {
    return new GithubRepositoryError("rate_limited", "GitHub request was rate limited");
  }
  return new GithubRepositoryError("unknown", `GitHub returned ${response.status}`);
}

async function fetchRequiredJson<T>(path: string, options: GithubOptions): Promise<T> {
  const response = await fetchGithub(path, options);
  if (!response.ok) throw failureFromResponse(response);
  try {
    return (await response.json()) as T;
  } catch {
    throw new GithubRepositoryError("unknown", "GitHub returned invalid JSON");
  }
}

async function fetchOptionalJson<T>(
  path: string,
  fallback: T,
  options: GithubOptions,
): Promise<T> {
  try {
    return await fetchRequiredJson<T>(path, options);
  } catch {
    return fallback;
  }
}

function encodeSegment(value: string): string {
  return encodeURIComponent(value);
}

/** 공개 저장소의 현재 커밋, 언어와 재귀 파일 트리를 한 번만 조회한다. */
export async function fetchPublicRepositorySnapshot(
  repositoryUrl: string,
  options: GithubOptions = {},
): Promise<GithubRepositorySnapshot> {
  const parsed = parseGithubUrl(repositoryUrl);
  if (!parsed) throw new GithubRepositoryError("invalid_url", "Invalid GitHub repository URL");

  const owner = encodeSegment(parsed.owner);
  const repo = encodeSegment(parsed.repo);
  const basePath = `/repos/${owner}/${repo}`;
  const repository = await fetchRequiredJson<GithubRepoResponse>(basePath, options);
  if (repository.private) {
    throw new GithubRepositoryError("not_found_or_private", "Private repositories are unsupported");
  }

  const defaultBranch = repository.default_branch ?? "main";
  const [languages, commit] = await Promise.all([
    fetchOptionalJson<Record<string, number>>(`${basePath}/languages`, {}, options),
    fetchRequiredJson<GithubCommitResponse>(
      `${basePath}/commits/${encodeSegment(defaultBranch)}`,
      options,
    ),
  ]);
  const commitSha = commit.sha;
  const treeSha = commit.commit?.tree?.sha;
  if (!commitSha || !treeSha) {
    throw new GithubRepositoryError("unknown", "GitHub commit metadata was incomplete");
  }

  const tree = await fetchRequiredJson<GithubTreeResponse>(
    `${basePath}/git/trees/${encodeSegment(treeSha)}?recursive=1`,
    options,
  );

  return {
    owner: parsed.owner,
    repo: parsed.repo,
    url: `https://github.com/${parsed.owner}/${parsed.repo}`,
    defaultBranch,
    commitSha,
    treeSha: tree.sha ?? treeSha,
    treeTruncated: tree.truncated ?? false,
    languages,
    files: (tree.tree ?? []).filter(
      (entry): entry is RepositoryTreeFile =>
        typeof entry.path === "string" &&
        typeof entry.type === "string" &&
        typeof entry.sha === "string" &&
        (entry.size === undefined ||
          (typeof entry.size === "number" && Number.isFinite(entry.size) && entry.size >= 0)),
    ),
  };
}

export async function fetchRepositoryTextFiles<T extends RepositoryTreeFile>(
  snapshot: GithubRepositorySnapshot,
  files: readonly T[],
  options: BlobOptions = {},
): Promise<Array<T & { content: string }>> {
  const maximumBlobBytes = options.maxBlobBytes ?? DEFAULT_SELECTION_LIMITS.maxFileBytes;
  const owner = encodeSegment(snapshot.owner);
  const repo = encodeSegment(snapshot.repo);
  const fetched: Array<(T & { content: string }) | null> = await Promise.all(
    files.map(async (file): Promise<(T & { content: string }) | null> => {
      try {
        const blob = await fetchRequiredJson<GithubBlobResponse>(
          `/repos/${owner}/${repo}/git/blobs/${encodeSegment(file.sha)}`,
          options,
        );
        if (blob.encoding !== "base64" || typeof blob.content !== "string") return null;
        const decoded = Buffer.from(blob.content.replace(/\s/g, ""), "base64");
        if (maximumBlobBytes <= 0 || decoded.byteLength > maximumBlobBytes) {
          return null;
        }
        const content = decoded.toString("utf-8");
        return { ...file, content };
      } catch {
        return null;
      }
    }),
  );
  return fetched.filter((file): file is T & { content: string } => file !== null);
}

function encodeGithubPath(path: string): string {
  return path.split("/").map(encodeURIComponent).join("/");
}

function githubBlobUrl(snapshot: GithubRepositorySnapshot, path: string): string {
  return `${snapshot.url}/blob/${encodeURIComponent(snapshot.commitSha)}/${encodeGithubPath(path)}`;
}

function sourceUrl(snapshot: GithubRepositorySnapshot, file: PreparedEvidenceFile): string {
  const base = githubBlobUrl(snapshot, file.path);
  return file.lineCount > 1 ? `${base}#L1-L${file.lineCount}` : `${base}#L1`;
}

async function collectFromSnapshot(
  snapshot: GithubRepositorySnapshot,
  roleId: string,
  options: CollectOptions,
): Promise<RepositoryEvidenceBundle> {
  const selectionLimits = options.selectionLimits ?? DEFAULT_SELECTION_LIMITS;
  const selected = selectRepositoryEvidenceFiles(snapshot.files, roleId, selectionLimits);
  const fetched = await fetchRepositoryTextFiles(snapshot, selected, {
    ...options,
    maxBlobBytes: selectionLimits.maxFileBytes,
  });
  const prepared = prepareEvidenceFiles(fetched, options.contentLimits ?? DEFAULT_CONTENT_LIMITS);
  const files = prepared.map((file) => ({
    ...file,
    startLine: 1,
    endLine: Math.max(1, file.lineCount),
    sourceUrl: sourceUrl(snapshot, file),
  }));
  const collectedPaths = new Set(files.map((file) => file.path));
  const omittedFiles = selected
    .filter((file) => !collectedPaths.has(file.path))
    .map((file) => ({ ...file, sourceUrl: githubBlobUrl(snapshot, file.path) }));

  return {
    repository: {
      owner: snapshot.owner,
      repo: snapshot.repo,
      url: snapshot.url,
      defaultBranch: snapshot.defaultBranch,
      commitSha: snapshot.commitSha,
      treeSha: snapshot.treeSha,
      treeTruncated: snapshot.treeTruncated,
    },
    selectionVersion: EVIDENCE_SELECTION_VERSION,
    languages: snapshot.languages,
    files,
    selectedFileCount: selected.length,
    omittedFileCount: omittedFiles.length,
    omittedFiles,
  };
}

const DIAGNOSTIC_REASON_ORDER: readonly EvidenceDiagnosticReason[] = [
  "not_a_file",
  "unsafe_path",
  "oversized",
  "sensitive_path",
  "generated_or_binary",
  "unsupported_file_type",
  "selection_limit",
];

function buildDiagnostics(
  snapshot: GithubRepositorySnapshot,
  roleId: string,
  selectedPaths: ReadonlySet<string>,
  limits: EvidenceSelectionLimits,
): RepositoryEvidenceDiagnostics {
  const pathsByReason = new Map<EvidenceDiagnosticReason, string[]>();
  let eligibleFileCount = 0;

  for (const file of snapshot.files) {
    const exclusion = evidenceExclusionReason(file, limits);
    if (exclusion) {
      const paths = pathsByReason.get(exclusion) ?? [];
      paths.push(file.path);
      pathsByReason.set(exclusion, paths);
      continue;
    }

    if (rankEvidenceFile(file, roleId, limits)) eligibleFileCount += 1;
    if (!selectedPaths.has(file.path)) {
      const paths = pathsByReason.get("selection_limit") ?? [];
      paths.push(file.path);
      pathsByReason.set("selection_limit", paths);
    }
  }

  return {
    totalTreeEntries: snapshot.files.length,
    eligibleFileCount,
    exclusions: DIAGNOSTIC_REASON_ORDER.flatMap((reason) => {
      const paths = pathsByReason.get(reason);
      if (!paths?.length) return [];
      return [{ reason, count: paths.length, examplePaths: paths.sort().slice(0, 5) }];
    }),
  };
}

/** 직무에 맞는 최대 8개 파일을 가져와 마스킹과 글자 예산을 적용한다. */
export async function collectRepositoryEvidence(
  repositoryUrl: string,
  roleId: string,
  options: CollectOptions = {},
): Promise<RepositoryEvidenceBundle> {
  const snapshot = await fetchPublicRepositorySnapshot(repositoryUrl, options);
  return collectFromSnapshot(snapshot, roleId, options);
}

/** 개발 환경에서 선별 결과와 제외 이유를 사람이 검증할 수 있게 만든 진단 묶음. */
export async function previewRepositoryEvidence(
  repositoryUrl: string,
  roleId: string,
  options: CollectOptions = {},
): Promise<RepositoryEvidencePreview> {
  const snapshot = await fetchPublicRepositorySnapshot(repositoryUrl, options);
  const evidence = await collectFromSnapshot(snapshot, roleId, options);
  const limits = options.selectionLimits ?? DEFAULT_SELECTION_LIMITS;
  const selectedPaths = new Set(
    selectRepositoryEvidenceFiles(snapshot.files, roleId, limits).map((file) => file.path),
  );

  return {
    ...evidence,
    diagnostics: buildDiagnostics(snapshot, roleId, selectedPaths, limits),
  };
}
