import type {
  EvidenceExclusionReason,
  EvidenceFileKind,
} from "@/lib/repository-evidence";

export type PreviewEvidenceFile = {
  path: string;
  type: string;
  sha: string;
  size?: number;
  kind: EvidenceFileKind;
  score: number;
  content: string;
  lineCount: number;
  truncated: boolean;
  startLine: number;
  endLine: number;
  sourceUrl: string;
};

export type PreviewDiagnosticReason = EvidenceExclusionReason | "selection_limit";

export type RepositoryEvidencePreviewData = {
  repository: {
    owner: string;
    repo: string;
    url: string;
    defaultBranch: string;
    commitSha: string;
    treeSha: string;
    treeTruncated: boolean;
  };
  selectionVersion: number;
  languages: Record<string, number>;
  files: PreviewEvidenceFile[];
  selectedFileCount: number;
  omittedFileCount: number;
  omittedFiles: Array<{
    path: string;
    type: string;
    sha: string;
    size?: number;
    kind: EvidenceFileKind;
    score: number;
    sourceUrl: string;
  }>;
  diagnostics: {
    totalTreeEntries: number;
    eligibleFileCount: number;
    exclusions: Array<{
      reason: PreviewDiagnosticReason;
      count: number;
      examplePaths: string[];
    }>;
  };
};

export type RepositoryEvidencePreviewResponse =
  | { ok: true; elapsedMs: number; evidence: RepositoryEvidencePreviewData }
  | {
      ok: false;
      reason:
        | "invalid_request"
        | "invalid_role"
        | "invalid_url"
        | "not_found_or_private"
        | "github_rate_limited"
        | "github_timeout"
        | "unknown";
    };
