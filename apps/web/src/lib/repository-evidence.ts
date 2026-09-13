/**
 * GitHub 파일 트리에서 LLM에 전달할 근거 후보를 고르는 순수 함수 모음.
 *
 * 이 모듈은 네트워크와 Node 전용 API에 의존하지 않는다. 저장소 내용은 신뢰할 수
 * 없는 입력이므로 경로, 크기와 파일 종류를 허용 목록 중심으로 판단한다.
 */

export type RepositoryTreeFile = {
  path: string;
  type: string;
  sha: string;
  size?: number;
};

export type EvidenceFileKind = "readme" | "manifest" | "delivery" | "test" | "source";

export type EvidenceExclusionReason =
  | "not_a_file"
  | "unsafe_path"
  | "oversized"
  | "sensitive_path"
  | "generated_or_binary"
  | "unsupported_file_type";

export type SelectedEvidenceFile = RepositoryTreeFile & {
  kind: EvidenceFileKind;
  score: number;
};

export type RepositoryTextFile = SelectedEvidenceFile & {
  content: string;
};

export type PreparedEvidenceFile = Omit<RepositoryTextFile, "content"> & {
  content: string;
  lineCount: number;
  truncated: boolean;
};

export type EvidenceSelectionLimits = {
  maxFiles: number;
  maxFileBytes: number;
};

export type EvidenceContentLimits = {
  maxTotalCharacters: number;
  maxCharactersPerFile: number;
};

export const DEFAULT_SELECTION_LIMITS: EvidenceSelectionLimits = {
  maxFiles: 8,
  maxFileBytes: 100_000,
};

export const DEFAULT_CONTENT_LIMITS: EvidenceContentLimits = {
  maxTotalCharacters: 40_000,
  maxCharactersPerFile: 12_000,
};

/** 파일 선별 규칙이 바뀌면 분석 결과와 함께 올려 이전 결과와 구분한다. */
export const EVIDENCE_SELECTION_VERSION = 1;

const MANIFEST_NAMES = new Set([
  "package.json",
  "requirements.txt",
  "pyproject.toml",
  "pipfile",
  "pom.xml",
  "build.gradle",
  "build.gradle.kts",
  "go.mod",
  "cargo.toml",
  "gemfile",
  "composer.json",
]);

const LOCKFILE_NAMES = new Set([
  "package-lock.json",
  "npm-shrinkwrap.json",
  "yarn.lock",
  "pnpm-lock.yaml",
  "bun.lock",
  "bun.lockb",
  "pipfile.lock",
  "poetry.lock",
  "uv.lock",
  "cargo.lock",
  "gemfile.lock",
  "composer.lock",
  "go.sum",
]);

const EXCLUDED_SEGMENTS = new Set([
  "node_modules",
  "vendor",
  "dist",
  "build",
  "out",
  "coverage",
  ".next",
  "target",
  ".venv",
  "venv",
  "__pycache__",
  ".git",
  ".idea",
  ".vscode",
]);

const BINARY_EXTENSIONS = new Set([
  ".7z",
  ".a",
  ".avi",
  ".bin",
  ".class",
  ".db",
  ".dmg",
  ".doc",
  ".docx",
  ".eot",
  ".exe",
  ".gif",
  ".gz",
  ".ico",
  ".jar",
  ".jpeg",
  ".jpg",
  ".lockb",
  ".mov",
  ".mp3",
  ".mp4",
  ".o",
  ".otf",
  ".pdf",
  ".png",
  ".pyc",
  ".sqlite",
  ".tar",
  ".tif",
  ".tiff",
  ".ttf",
  ".wav",
  ".webm",
  ".webp",
  ".woff",
  ".woff2",
  ".xls",
  ".xlsx",
  ".zip",
]);

const SOURCE_EXTENSIONS = new Set([
  ".c",
  ".cc",
  ".cpp",
  ".cs",
  ".dart",
  ".ex",
  ".exs",
  ".go",
  ".graphql",
  ".gql",
  ".h",
  ".hpp",
  ".java",
  ".js",
  ".jsx",
  ".kt",
  ".kts",
  ".mjs",
  ".php",
  ".proto",
  ".py",
  ".rb",
  ".rs",
  ".scala",
  ".sh",
  ".sql",
  ".svelte",
  ".swift",
  ".ts",
  ".tsx",
  ".vue",
]);

const ROLE_SIGNALS: Record<string, readonly string[]> = {
  backend: [
    "api",
    "controller",
    "handler",
    "middleware",
    "migration",
    "queue",
    "repository",
    "route",
    "schema",
    "server",
    "service",
    "worker",
  ],
  frontend: [
    "client",
    "component",
    "form",
    "frontend",
    "hook",
    "layout",
    "page",
    "router",
    "state",
    "store",
    "ui",
    "view",
  ],
  "data-ai": [
    "analytics",
    "dataset",
    "etl",
    "evaluation",
    "feature",
    "ingest",
    "model",
    "pipeline",
    "serving",
    "train",
    "transform",
    "warehouse",
  ],
  mobile: [
    "activity",
    "android",
    "deeplink",
    "fragment",
    "ios",
    "mobile",
    "networking",
    "push",
    "screen",
    "swiftui",
    "viewmodel",
    "widget",
  ],
};

const KIND_BASE_SCORE: Record<EvidenceFileKind, number> = {
  readme: 100,
  manifest: 88,
  delivery: 80,
  test: 68,
  source: 35,
};

const KIND_QUOTAS: readonly [EvidenceFileKind, number][] = [
  ["source", 3],
  ["readme", 1],
  ["manifest", 2],
  ["delivery", 1],
  ["test", 1],
];

const FALLBACK_KIND_ORDER: readonly EvidenceFileKind[] = [
  "source",
  "test",
  "delivery",
  "manifest",
  "readme",
];

function basename(path: string): string {
  const index = path.lastIndexOf("/");
  return index === -1 ? path : path.slice(index + 1);
}

function extension(path: string): string {
  const name = basename(path);
  const index = name.lastIndexOf(".");
  return index <= 0 ? "" : name.slice(index).toLowerCase();
}

function pathSegments(path: string): string[] {
  return path.toLowerCase().split("/");
}

function isSafePath(path: string): boolean {
  if (!path || path.startsWith("/") || path.includes("\\") || path.includes("\0")) return false;
  return !path.split("/").some((segment) => segment === "" || segment === "." || segment === "..");
}

function isSensitivePath(path: string): boolean {
  const lower = path.toLowerCase();
  const name = basename(lower);
  if (name === ".env" || name.startsWith(".env.")) return true;
  if (/^id_(?:rsa|dsa|ecdsa|ed25519)(?:\.pub)?$/.test(name)) return true;
  if (/\.(?:pem|key|p12|pfx)$/.test(name)) return true;
  return /^(?:credentials?|secrets?)(?:\..+)?$/.test(name);
}

function isGeneratedOrBinaryPath(path: string): boolean {
  const lower = path.toLowerCase();
  const name = basename(lower);
  const segments = pathSegments(lower);
  if (segments.some((segment) => EXCLUDED_SEGMENTS.has(segment))) return true;
  if (LOCKFILE_NAMES.has(name) || BINARY_EXTENSIONS.has(extension(name))) return true;
  if (name.endsWith(".min.js") || name.endsWith(".min.css") || name.endsWith(".map")) return true;
  return name.endsWith(".generated.ts") || name.endsWith(".generated.js");
}

function isReadme(path: string): boolean {
  return /^readme(?:\.[^/]+)?$/i.test(basename(path));
}

export function isRecognizedManifestPath(path: string): boolean {
  return MANIFEST_NAMES.has(basename(path).toLowerCase());
}

export function isDockerfilePath(path: string): boolean {
  return /^dockerfile(?:\.[^/]+)?$/i.test(basename(path));
}

function isDeliveryFile(path: string): boolean {
  const lower = path.toLowerCase();
  const name = basename(lower);
  return (
    isDockerfilePath(path) ||
    name === "docker-compose.yml" ||
    name === "docker-compose.yaml" ||
    name === "compose.yml" ||
    name === "compose.yaml" ||
    name === "jenkinsfile" ||
    name === ".gitlab-ci.yml" ||
    name === ".gitlab-ci.yaml" ||
    name === "makefile" ||
    name.endsWith(".tf") ||
    lower.startsWith(".github/workflows/") ||
    lower.includes("/helm/") ||
    lower.includes("/k8s/") ||
    lower.includes("/kubernetes/")
  );
}

function isTestFile(path: string): boolean {
  const lower = path.toLowerCase();
  const name = basename(lower);
  const segments = pathSegments(lower);
  return (
    segments.some((segment) => ["test", "tests", "__tests__", "spec", "specs"].includes(segment)) ||
    /(?:^|[._-])(?:test|spec)\.[^.]+$/.test(name)
  );
}

function kindOf(path: string): EvidenceFileKind | null {
  if (isReadme(path)) return "readme";
  if (isRecognizedManifestPath(path)) return "manifest";
  if (isDeliveryFile(path)) return "delivery";
  if (!SOURCE_EXTENSIONS.has(extension(path))) return null;
  return isTestFile(path) ? "test" : "source";
}

/** 개발용 진단과 실제 선별이 같은 제외 규칙을 사용하도록 사유를 한 곳에서 계산한다. */
export function evidenceExclusionReason(
  file: RepositoryTreeFile,
  limits: EvidenceSelectionLimits = DEFAULT_SELECTION_LIMITS,
): EvidenceExclusionReason | null {
  if (file.type !== "blob") return "not_a_file";
  if (!isSafePath(file.path)) return "unsafe_path";
  if ((file.size ?? 0) > limits.maxFileBytes) return "oversized";
  if (isSensitivePath(file.path)) return "sensitive_path";
  if (isGeneratedOrBinaryPath(file.path)) return "generated_or_binary";
  if (!kindOf(file.path)) return "unsupported_file_type";
  return null;
}

function roleSignalScore(path: string, roleId: string): number {
  const lower = path.toLowerCase();
  const signals = ROLE_SIGNALS[roleId] ?? [];
  const matches = signals.filter((signal) => lower.includes(signal)).length;
  return Math.min(matches, 5) * 10;
}

function compareFiles(a: SelectedEvidenceFile, b: SelectedEvidenceFile): number {
  return b.score - a.score || a.path.localeCompare(b.path);
}

export function rankEvidenceFile(
  file: RepositoryTreeFile,
  roleId: string,
  limits: EvidenceSelectionLimits = DEFAULT_SELECTION_LIMITS,
): SelectedEvidenceFile | null {
  if (evidenceExclusionReason(file, limits)) return null;

  const kind = kindOf(file.path);
  if (!kind) return null;

  const lower = file.path.toLowerCase();
  const name = basename(lower);
  const depth = file.path.split("/").length - 1;
  let score = KIND_BASE_SCORE[kind] + roleSignalScore(file.path, roleId);

  if (lower.startsWith("src/") || lower.includes("/src/")) score += 8;
  if (/^(?:app|index|main|server)\.[^.]+$/.test(name)) score += 8;
  if (
    pathSegments(lower).some((segment) =>
      ["example", "examples", "sample", "samples", "fixture", "fixtures"].includes(segment),
    )
  ) {
    score -= 30;
  }
  if (kind === "readme" || kind === "manifest" || kind === "delivery") score -= depth * 3;

  return { ...file, kind, score };
}

/**
 * 소스 파일 세 자리를 먼저 확보한 뒤 README·설정·배포·테스트 파일을 균형 있게
 * 고른다. 어떤 종류가 부족하면 구현 근거가 풍부해지도록 소스부터 빈 자리를 채운다.
 */
export function selectRepositoryEvidenceFiles(
  files: readonly RepositoryTreeFile[],
  roleId: string,
  limits: EvidenceSelectionLimits = DEFAULT_SELECTION_LIMITS,
): SelectedEvidenceFile[] {
  if (limits.maxFiles <= 0 || limits.maxFileBytes <= 0) return [];

  const ranked = files
    .map((file) => rankEvidenceFile(file, roleId, limits))
    .filter((file): file is SelectedEvidenceFile => file !== null)
    .sort(compareFiles);

  const selected: SelectedEvidenceFile[] = [];
  const chosenPaths = new Set<string>();

  const add = (file: SelectedEvidenceFile) => {
    if (selected.length >= limits.maxFiles || chosenPaths.has(file.path)) return;
    selected.push(file);
    chosenPaths.add(file.path);
  };

  for (const [kind, quota] of KIND_QUOTAS) {
    for (const file of ranked.filter((candidate) => candidate.kind === kind).slice(0, quota)) {
      add(file);
    }
  }
  for (const kind of FALLBACK_KIND_ORDER) {
    for (const file of ranked.filter((candidate) => candidate.kind === kind)) add(file);
  }

  return selected.sort(compareFiles);
}

function looksBinary(content: string): boolean {
  if (content.includes("\0")) return true;
  const sample = content.slice(0, 4_000);
  if (!sample) return false;
  let controls = 0;
  for (const character of sample) {
    const code = character.charCodeAt(0);
    if (code < 32 && character !== "\n" && character !== "\r" && character !== "\t") {
      controls += 1;
    }
  }
  return controls / sample.length > 0.01;
}

/** 공개 저장소에 실수로 들어간 토큰 형태를 외부 LLM에 전달하기 전에 가린다. */
export function maskPotentialSecrets(content: string): string {
  return content
    .replace(
      /-----BEGIN [A-Z ]*PRIVATE KEY-----[\s\S]*?-----END [A-Z ]*PRIVATE KEY-----/g,
      (secret) =>
        `[REDACTED_PRIVATE_KEY]${"\n".repeat(secret.match(/\n/g)?.length ?? 0)}`,
    )
    .replace(/\bAKIA[0-9A-Z]{16}\b/g, "[REDACTED_AWS_KEY]")
    .replace(/\bgh[pousr]_[A-Za-z0-9_]{20,}\b/g, "[REDACTED_GITHUB_TOKEN]")
    .replace(/\bBearer\s+[A-Za-z0-9._~+/=-]{12,}/gi, "Bearer [REDACTED_TOKEN]")
    .replace(
      /((?:["'])?(?:api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|password|passwd|secret)(?:["'])?\s*[:=]\s*["'])([^"'\r\n]{8,})(["'])/gi,
      "$1[REDACTED_SECRET]$3",
    )
    .replace(
      /^(\s*(?:API_KEY|ACCESS_TOKEN|AUTH_TOKEN|CLIENT_SECRET|PASSWORD|PASSWD|SECRET)\s*=\s*)(?!["'])([^\s#]{8,})/gim,
      "$1[REDACTED_SECRET]",
    );
}

function fairCharacterBudgets(lengths: readonly number[], maximum: number): number[] {
  const budgets = lengths.map(() => 0);
  let remainingBudget = Math.max(0, maximum);
  let remaining = lengths.map((length, index) => ({ length, index }));

  while (remaining.length > 0 && remainingBudget > 0) {
    const share = Math.floor(remainingBudget / remaining.length);
    const small = remaining.filter(({ length }) => length <= share);
    if (small.length === 0) {
      for (const { index } of remaining) budgets[index] = share;
      let remainder = remainingBudget - share * remaining.length;
      for (const { index } of remaining) {
        if (remainder <= 0) break;
        budgets[index] += 1;
        remainder -= 1;
      }
      break;
    }

    const completed = new Set(small.map(({ index }) => index));
    for (const { index, length } of small) {
      budgets[index] = length;
      remainingBudget -= length;
    }
    remaining = remaining.filter(({ index }) => !completed.has(index));
  }

  return budgets;
}

function truncateAtLine(content: string, maximum: number): { content: string; truncated: boolean } {
  if (content.length <= maximum) return { content, truncated: false };
  const candidate = content.slice(0, maximum);
  const lastNewline = candidate.lastIndexOf("\n");
  const end = lastNewline >= Math.floor(maximum * 0.7) ? lastNewline : maximum;
  return { content: candidate.slice(0, end), truncated: true };
}

function countLines(content: string): number {
  if (content.length === 0) return 0;
  return content.endsWith("\n")
    ? content.slice(0, -1).split("\n").length
    : content.split("\n").length;
}

/**
 * 내려받은 텍스트를 마스킹하고 모든 파일이 일부 근거를 가질 수 있도록 전체 글자
 * 예산을 공평하게 나눈다. 반환된 content 합계는 항상 전체 상한 이하다.
 */
export function prepareEvidenceFiles(
  files: readonly RepositoryTextFile[],
  limits: EvidenceContentLimits = DEFAULT_CONTENT_LIMITS,
): PreparedEvidenceFile[] {
  if (limits.maxTotalCharacters <= 0 || limits.maxCharactersPerFile <= 0) return [];

  const cleaned = files
    .map((file) => ({
      ...file,
      content: maskPotentialSecrets(file.content.replace(/\r\n?/g, "\n")),
    }))
    .filter((file) => file.content.trim() !== "" && !looksBinary(file.content));

  const desiredLengths = cleaned.map((file) =>
    Math.min(file.content.length, limits.maxCharactersPerFile),
  );
  const budgets = fairCharacterBudgets(desiredLengths, limits.maxTotalCharacters);

  return cleaned.flatMap((file, index) => {
    const budget = budgets[index];
    if (budget <= 0) return [];
    const prepared = truncateAtLine(file.content, budget);
    return [
      {
        ...file,
        content: prepared.content,
        lineCount: countLines(prepared.content),
        truncated: prepared.truncated || prepared.content.length < file.content.length,
      },
    ];
  });
}
