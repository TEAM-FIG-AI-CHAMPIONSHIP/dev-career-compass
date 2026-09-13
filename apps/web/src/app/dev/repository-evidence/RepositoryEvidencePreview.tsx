"use client";

import { useState, type FormEvent } from "react";
import { Button } from "@/components/ui/Button";
import { RepoField } from "@/components/ui/RepoField";
import { ExternalIcon, GithubIcon } from "@/components/ui/icons";
import { parseGithubUrl } from "@/lib/repo-keywords";
import type {
  PreviewDiagnosticReason,
  PreviewEvidenceFile,
  RepositoryEvidencePreviewData,
  RepositoryEvidencePreviewResponse,
} from "@/types/repository-evidence-preview";

const ROLE_OPTIONS = [
  { id: "backend", label: "서버·백엔드" },
  { id: "frontend", label: "웹 프론트엔드" },
  { id: "data-ai", label: "데이터·AI" },
  { id: "mobile", label: "모바일" },
] as const;

const KIND_LABELS: Record<PreviewEvidenceFile["kind"], string> = {
  readme: "README",
  manifest: "매니페스트",
  delivery: "배포·운영",
  test: "테스트",
  source: "소스",
};

const EXCLUSION_LABELS: Record<PreviewDiagnosticReason, string> = {
  not_a_file: "파일이 아닌 트리 항목",
  unsafe_path: "안전하지 않은 경로",
  oversized: "파일 크기 상한 초과",
  sensitive_path: "자격증명 가능성이 있는 경로",
  generated_or_binary: "생성물·의존성·바이너리",
  unsupported_file_type: "분석 대상이 아닌 파일 형식",
  selection_limit: "후보였지만 8개 선별에서 제외",
};

const ERROR_MESSAGES: Record<
  Exclude<RepositoryEvidencePreviewResponse, { ok: true }>["reason"],
  string
> = {
  invalid_request: "입력값을 확인해 주세요.",
  invalid_role: "지원하는 직무를 선택해 주세요.",
  invalid_url: "GitHub 저장소 주소 형태를 확인해 주세요.",
  not_found_or_private: "공개 저장소를 찾지 못했습니다. 비공개 저장소는 지원하지 않습니다.",
  github_rate_limited: "GitHub 요청 한도에 도달했습니다. 잠시 뒤 다시 시도해 주세요.",
  github_timeout: "GitHub 응답 시간이 초과되었습니다. 다시 시도해 주세요.",
  unknown: "근거 수집을 완료하지 못했습니다.",
};

function formatBytes(value: number | undefined): string {
  if (value === undefined) return "크기 미상";
  if (value < 1_000) return `${value} B`;
  return `${(value / 1_000).toFixed(1)} KB`;
}

function SummaryCard({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="flex min-h-24 flex-col justify-between gap-3 rounded-card border border-line bg-surface p-4">
      <dt className="text-caption text-pretty text-ink-soft">{label}</dt>
      <dd className="font-mono text-h2 font-semibold tabular-nums text-ink">{value}</dd>
    </div>
  );
}

function EvidenceFileCard({ file, index }: { file: PreviewEvidenceFile; index: number }) {
  return (
    <article className="rounded-card border border-line bg-surface">
      <div className="flex flex-col gap-3 p-4 sm:flex-row sm:items-start sm:justify-between">
        <div className="min-w-0">
          <div className="mb-1.5 flex flex-wrap items-center gap-2">
            <span className="rounded-pill bg-accent-tint px-2.5 py-1 text-caption text-accent">
              {KIND_LABELS[file.kind]}
            </span>
            <span className="font-mono text-meta tabular-nums text-ink-soft">
              #{index + 1} · {file.score}점
            </span>
          </div>
          <a
            href={file.sourceUrl}
            target="_blank"
            rel="noreferrer"
            className="inline-flex max-w-full items-center gap-1.5 font-mono text-body-sm"
          >
            <span className="truncate">{file.path}</span>
            <ExternalIcon size={14} className="shrink-0" />
          </a>
        </div>
        <span className="shrink-0 font-mono text-meta tabular-nums text-ink-muted">
          {formatBytes(file.size)} · L{file.startLine}–L{file.endLine}
        </span>
      </div>

      <details className="border-t border-line">
        <summary className="cursor-pointer px-4 py-3 text-body-sm text-ink-soft hover:text-ink">
          수집된 원문 보기{file.truncated ? " · 상한에 맞춰 잘림" : ""}
        </summary>
        <pre className="max-h-80 overflow-auto border-t border-line bg-sunken p-4 font-mono text-meta leading-6 whitespace-pre text-ink">
          {file.content}
        </pre>
      </details>
    </article>
  );
}

function EvidenceResult({ evidence, elapsedMs }: { evidence: RepositoryEvidencePreviewData; elapsedMs: number }) {
  const totalCharacters = evidence.files.reduce((sum, file) => sum + file.content.length, 0);
  const languages = Object.entries(evidence.languages).sort((a, b) => b[1] - a[1]);

  return (
    <div className="flex flex-col gap-10">
      <section className="flex flex-col gap-5" aria-labelledby="repository-summary">
        <div className="flex flex-col gap-2 border-b border-line-strong pb-4 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <span className="font-mono text-meta text-ink-soft">COLLECTION RESULT</span>
            <h2 id="repository-summary" className="mt-1 text-h1 font-semibold text-balance">
              {evidence.repository.owner}/{evidence.repository.repo}
            </h2>
          </div>
          <span className="font-mono text-meta tabular-nums text-ink-soft">
            {elapsedMs.toLocaleString()}ms · 규칙 v{evidence.selectionVersion}
          </span>
        </div>

        <dl className="grid grid-cols-2 gap-3 lg:grid-cols-4">
          <SummaryCard label="전체 트리 항목" value={evidence.diagnostics.totalTreeEntries} />
          <SummaryCard label="선별 가능 파일" value={evidence.diagnostics.eligibleFileCount} />
          <SummaryCard label="최종 수집 파일" value={evidence.files.length} />
          <SummaryCard label="LLM 입력 예정 글자" value={totalCharacters.toLocaleString()} />
        </dl>

        <div className="grid gap-3 text-body-sm text-ink-soft sm:grid-cols-2">
          <p className="text-pretty">
            커밋 <code className="font-mono text-ink">{evidence.repository.commitSha.slice(0, 12)}</code>에
            고정했습니다. 파일 링크도 같은 커밋을 가리킵니다.
          </p>
          <p className="text-pretty">
            언어: {languages.length ? languages.map(([name]) => name).slice(0, 6).join(", ") : "확인되지 않음"}
          </p>
        </div>

        {evidence.repository.treeTruncated && (
          <p role="status" className="rounded-card border border-warn bg-warn-tint p-4 text-body-sm text-pretty text-warn">
            GitHub가 큰 저장소의 파일 트리를 일부만 반환했습니다. 아래 결과는 확인된 범위만 반영합니다.
          </p>
        )}
        {evidence.omittedFileCount > 0 && (
          <div role="status" className="rounded-card border border-warn bg-warn-tint p-4 text-warn">
            <p className="text-body-sm text-pretty">
              선택된 파일 중 {evidence.omittedFileCount}개는 조회 실패 또는 실제 크기 초과로 원문을 가져오지 못했습니다.
            </p>
            <ul className="mt-3 flex flex-col gap-1.5">
              {(evidence.omittedFiles ?? []).map((file) => (
                <li key={file.path} className="flex flex-wrap items-center justify-between gap-2 text-caption">
                  <a href={file.sourceUrl} target="_blank" rel="noreferrer" className="font-mono break-all text-warn underline">
                    {file.path}
                  </a>
                  <span className="shrink-0 font-mono tabular-nums">{KIND_LABELS[file.kind]} · {file.score}점</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </section>

      <section className="flex flex-col gap-4" aria-labelledby="selected-files">
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-line-strong pb-2.5">
          <h2 id="selected-files" className="text-h2 font-semibold text-balance">
            선택된 근거 파일
          </h2>
          <span className="font-mono text-meta tabular-nums text-ink-soft">
            {evidence.files.length}/{evidence.selectedFileCount}개 읽기 성공
          </span>
        </div>
        {evidence.files.length ? (
          <div className="grid gap-3 lg:grid-cols-2">
            {evidence.files.map((file, index) => (
              <EvidenceFileCard key={file.path} file={file} index={index} />
            ))}
          </div>
        ) : (
          <p className="rounded-card border border-line bg-surface p-5 text-body-sm text-pretty text-ink-soft">
            현재 규칙으로 읽을 수 있는 근거 파일이 없습니다. 제외 사유를 확인하거나 다른 공개 저장소로 다시 시도해 주세요.
          </p>
        )}
      </section>

      <section className="flex flex-col gap-4" aria-labelledby="excluded-files">
        <div className="flex flex-wrap items-baseline justify-between gap-2 border-b border-line-strong pb-2.5">
          <h2 id="excluded-files" className="text-h2 font-semibold text-balance">
            제외 사유
          </h2>
          <span className="text-caption text-ink-soft">사유별 예시는 최대 5개</span>
        </div>
        {evidence.diagnostics.exclusions.length ? (
          <div className="overflow-x-auto rounded-card border border-line bg-surface">
            <table className="w-full min-w-2xl border-collapse text-left text-body-sm">
              <thead className="bg-sunken text-ink-soft">
                <tr>
                  <th scope="col" className="px-4 py-3 font-medium">사유</th>
                  <th scope="col" className="px-4 py-3 font-medium">개수</th>
                  <th scope="col" className="px-4 py-3 font-medium">경로 예시</th>
                </tr>
              </thead>
              <tbody>
                {evidence.diagnostics.exclusions.map((exclusion) => (
                  <tr key={exclusion.reason} className="border-t border-line align-top">
                    <th scope="row" className="px-4 py-3 font-medium text-ink">
                      {EXCLUSION_LABELS[exclusion.reason]}
                    </th>
                    <td className="px-4 py-3 font-mono tabular-nums text-ink-soft">
                      {exclusion.count}
                    </td>
                    <td className="px-4 py-3">
                      <ul className="flex flex-col gap-1 font-mono text-meta text-ink-soft">
                        {exclusion.examplePaths.map((path) => (
                          <li key={path} className="break-all">{path}</li>
                        ))}
                      </ul>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-body-sm text-ink-soft">제외된 트리 항목이 없습니다.</p>
        )}
      </section>
    </div>
  );
}

export function RepositoryEvidencePreview() {
  const [url, setUrl] = useState("");
  const [roleId, setRoleId] = useState<(typeof ROLE_OPTIONS)[number]["id"]>("backend");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ evidence: RepositoryEvidencePreviewData; elapsedMs: number } | null>(null);

  const invalidUrl = url.trim() !== "" && parseGithubUrl(url) === null;

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!url.trim() || invalidUrl) {
      setResult(null);
      setError("GitHub 공개 저장소 주소를 입력해 주세요.");
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const response = await fetch("/api/dev/repository-evidence", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: url.trim(), roleId }),
      });
      const data = (await response.json()) as RepositoryEvidencePreviewResponse;
      if (!data.ok) {
        setResult(null);
        setError(ERROR_MESSAGES[data.reason]);
        return;
      }
      setResult({ evidence: data.evidence, elapsedMs: data.elapsedMs });
    } catch {
      setResult(null);
      setError("서버 응답을 읽지 못했습니다. 개발 서버 상태를 확인해 주세요.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="mx-auto flex w-full max-w-6xl flex-col gap-10 px-4 py-12 sm:px-8">
      <header className="flex max-w-3xl flex-col gap-3">
        <div className="flex size-11 items-center justify-center rounded-card bg-accent-tint text-accent">
          <GithubIcon size={22} strokeWidth={1.5} />
        </div>
        <h1 className="text-display font-semibold text-balance">GitHub 근거 수집기 미리보기</h1>
        <p className="text-body text-pretty text-ink-soft">
          Claude 호출 없이 실제 공개 저장소에서 어떤 파일이 선택되고 제외되는지 확인합니다. 원문은 저장하지 않으며 이 화면과 API는 개발 환경에서만 열립니다.
        </p>
      </header>

      <form onSubmit={submit} className="flex max-w-3xl flex-col gap-5 rounded-card border border-line bg-surface p-5" aria-busy={loading}>
        <div className="flex flex-col gap-2">
          <label htmlFor="preview-role" className="text-body-sm font-medium text-ink">검증할 직무</label>
          <select
            id="preview-role"
            value={roleId}
            onChange={(event) => {
              setRoleId(event.target.value as typeof roleId);
              setResult(null);
            }}
            className="min-h-11 rounded-btn border border-line-strong bg-surface px-3.5 py-2.5 text-body-sm text-ink"
          >
            {ROLE_OPTIONS.map((role) => (
              <option key={role.id} value={role.id}>{role.label}</option>
            ))}
          </select>
        </div>

        <div className="flex flex-col gap-2">
          <label htmlFor="preview-url" className="text-body-sm font-medium text-ink">공개 GitHub 저장소</label>
          <RepoField
            id="preview-url"
            value={url}
            onChange={(next) => {
              setUrl(next);
              setError(null);
              setResult(null);
            }}
            error={invalidUrl ? "GitHub 저장소 링크 형태로 적어주세요." : undefined}
            disabled={loading}
          />
        </div>

        {error && <p role="alert" className="text-body-sm text-pretty text-warn">{error}</p>}

        <div className="flex flex-wrap items-center gap-3 border-t border-line pt-4">
          <Button type="submit" variant="primary" disabled={loading || !url.trim() || invalidUrl}>
            {loading ? "저장소를 살펴보는 중…" : "근거 파일 확인"}
          </Button>
          <span className="text-caption text-pretty text-ink-muted">GitHub API만 사용하며 Claude 비용은 발생하지 않습니다.</span>
        </div>
      </form>

      {loading && (
        <div role="status" aria-live="polite" className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }, (_, index) => (
            <div key={index} className="flex min-h-24 flex-col gap-4 rounded-card border border-line bg-surface p-4">
              <div className="skeleton h-3 w-2/3 rounded-[3px] bg-line" />
              <div className="skeleton h-6 w-1/3 rounded-[3px] bg-line" />
            </div>
          ))}
          <span className="sr-only">GitHub 저장소 근거를 수집하고 있습니다.</span>
        </div>
      )}

      {!loading && result && <EvidenceResult evidence={result.evidence} elapsedMs={result.elapsedMs} />}
    </main>
  );
}
