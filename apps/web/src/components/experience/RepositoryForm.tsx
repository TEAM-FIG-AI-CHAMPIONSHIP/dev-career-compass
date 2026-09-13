"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { StepNav } from "@/components/ui/StepNav";
import { cardStyle } from "@/components/ui/Card";
import {
  AnalysisTerminal,
  type TerminalStep,
} from "@/components/ui/state/AnalysisTerminal";
import { Chip } from "@/components/ui/Chip";
import { RepoField } from "@/components/ui/RepoField";
import { ArrowLeftIcon, PlusIcon } from "@/components/ui/icons";
import { useExperience } from "@/lib/experience-store";
import {
  saveMatchRepositories,
  useMatchExit,
  useMatchFlow,
} from "@/lib/match-flow-store";
import { parseGithubUrl } from "@/lib/repo-keywords";
import { routes } from "@/lib/routes";

const MAX_REPOSITORIES = 3;

/* 저장소를 살펴보는 동안 보여줄 줄. 렌더마다 새로 만들면 타이핑이 다시
   시작되므로 모듈 상수로 둡니다. */
const SCAN_STEPS: TerminalStep[] = [
  {
    command: "refactor scan --repos",
    output: "Reading repository metadata...",
  },
  {
    command: "refactor extract --keywords",
    output: "Matching what you built to job areas...",
  },
];

/** `owner/repo` 형태(프로토콜·github.com 없이)만 매칭하는 레거시 저장소 형식 감지용. */
const BARE_REPO_RE = /^[A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+$/;

/**
 * `experience?.repos`에는 이 브랜치 이전에 저장된 옛 `owner/repo` 형식이 남아
 * 있을 수 있다. `parseGithubUrl`은 전체 URL만 인정하므로, URL로 보이지 않으면서
 * 옛 형식과 일치하면 `https://github.com/`을 붙여 정상 URL로 되돌린다.
 */
function normalizeLegacyRepo(entry: string): string {
  const trimmed = entry.trim();
  if (parseGithubUrl(trimmed) !== null) return entry;
  if (BARE_REPO_RE.test(trimmed)) return `https://github.com/${trimmed}`;
  return entry;
}

type FieldStatus =
  | { kind: "loading" }
  | { kind: "done"; keywords: string[] }
  | { kind: "error"; message: string };

const REASON_MESSAGES: Record<string, string> = {
  not_found: "비공개 저장소이거나 찾을 수 없어요 — 이 저장소는 건너뜁니다.",
  private: "비공개 저장소이거나 찾을 수 없어요 — 이 저장소는 건너뜁니다.",
  rate_limited:
    "지금은 GitHub 확인이 지연되고 있어요. 나중에 다시 시도해 주세요.",
  unknown: "지금은 GitHub 확인이 지연되고 있어요. 나중에 다시 시도해 주세요.",
};

async function analyzeRepository(url: string): Promise<FieldStatus> {
  try {
    const res = await fetch("/api/repo-keywords", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = (await res.json()) as
      { ok: true; keywords: string[] } | { ok: false; reason: string };
    if (data.ok) return { kind: "done", keywords: data.keywords };
    return {
      kind: "error",
      message: REASON_MESSAGES[data.reason] ?? REASON_MESSAGES.unknown,
    };
  } catch {
    return { kind: "error", message: REASON_MESSAGES.unknown };
  }
}

export function RepositoryForm({
  role,
  catalogVersion,
}: {
  role: string;
  catalogVersion: number;
}) {
  const router = useRouter();
  const flow = useMatchFlow(role);
  const exit = useMatchExit(role);
  const experience = useExperience(catalogVersion);
  const [draft, setDraft] = useState<string[] | null>(null);
  const [statuses, setStatuses] = useState<Record<string, FieldStatus>>({});
  const [analyzing, setAnalyzing] = useState(false);
  const [analyzed, setAnalyzed] = useState(false);

  const repositories =
    draft ??
    (flow?.repositories.length
      ? flow.repositories
      : experience?.repos?.length
        ? experience.repos.map(normalizeLegacyRepo)
        : [""]);

  const nothingToAnalyze = repositories.every(
    (repository) => parseGithubUrl(repository.trim()) === null,
  );

  const invalid = repositories.some(
    (repository) =>
      repository.trim() !== "" && !parseGithubUrl(repository.trim()),
  );

  const updateField = (index: number, next: string) => {
    setDraft(
      repositories.map((current, currentIndex) =>
        currentIndex === index ? next : current,
      ),
    );
    setAnalyzed(false);
  };

  /**
   * 저장소는 선택 사항이라 넘어가기는 언제나 가능합니다. 분석을 했으면 찾은
   * 키워드까지, 안 했으면 적어 둔 주소까지만 들고 넘어갑니다.
   */
  const goNext = () => {
    const valid = repositories
      .map((repository) => repository.trim())
      .filter((repository) => parseGithubUrl(repository) !== null);
    const keywords: Record<string, string[]> = {};
    for (const url of valid) {
      const status = statuses[url];
      if (status?.kind === "done") keywords[url] = status.keywords;
    }
    saveMatchRepositories(role, valid, keywords);
    router.push(routes.matchExperience(role));
  };

  const runAnalysis = async () => {
    const candidates = repositories
      .map((repository) => repository.trim())
      .filter((repository) => parseGithubUrl(repository) !== null);

    setAnalyzing(true);
    setStatuses((prev) => {
      const next = { ...prev };
      for (const url of candidates) next[url] = { kind: "loading" };
      return next;
    });

    const results = await Promise.all(
      candidates.map(
        async (url) => [url, await analyzeRepository(url)] as const,
      ),
    );

    const nextStatuses: Record<string, FieldStatus> = { ...statuses };
    const keywordsByUrl: Record<string, string[]> = {};
    for (const [url, status] of results) {
      nextStatuses[url] = status;
      if (status.kind === "done") keywordsByUrl[url] = status.keywords;
    }
    setStatuses(nextStatuses);

    saveMatchRepositories(role, candidates, keywordsByUrl);
    setAnalyzed(true);
    setAnalyzing(false);
  };

  return (
    <div className="flex flex-col gap-6">
      {analyzing ? (
        <AnalysisTerminal
          steps={SCAN_STEPS}
          title="refactor.me — scan"
          label="저장소를 살펴보고 있습니다."
        />
      ) : (
        <div
          className={cardStyle("static", {
            className: "flex flex-col gap-4 p-5 sm:p-6",
          })}
        >
          <div className="flex flex-col gap-3">
            {repositories.map((repository, index) => {
              const trimmed = repository.trim();
              const fallbackKeywords = trimmed
                ? flow?.repositoryKeywords[trimmed]
                : undefined;
              const status: FieldStatus | undefined = trimmed
                ? (statuses[trimmed] ??
                  (fallbackKeywords
                    ? { kind: "done", keywords: fallbackKeywords }
                    : undefined))
                : undefined;
              const formatError =
                trimmed !== "" && !parseGithubUrl(trimmed)
                  ? "GitHub 저장소 링크 형태로 적어주세요."
                  : status?.kind === "error"
                    ? status.message
                    : undefined;

              return (
                <div key={index} className="flex flex-col gap-2">
                  <RepoField
                    value={repository}
                    onChange={(next) => updateField(index, next)}
                    error={formatError}
                  />
                  {status?.kind === "loading" && (
                    <span className="text-caption text-ink-soft">
                      저장소를 살펴보는 중이에요…
                    </span>
                  )}
                  {status?.kind === "done" && status.keywords.length > 0 && (
                    <div className="flex flex-wrap gap-1.5">
                      {status.keywords.map((keyword) => (
                        <Chip key={keyword} tone="accent">
                          {keyword}
                        </Chip>
                      ))}
                    </div>
                  )}
                  {status?.kind === "done" && status.keywords.length === 0 && (
                    <span className="text-caption text-ink-soft">
                      찾은 키워드가 없어요.
                    </span>
                  )}
                </div>
              );
            })}
          </div>

          <div className="flex flex-wrap items-center gap-3 border-t border-line pt-4">
            {repositories.length < MAX_REPOSITORIES && (
              <Button
                variant="secondary"
                onClick={() => setDraft([...repositories, ""])}
              >
                <PlusIcon size={14} strokeWidth={1.7} />
                저장소 추가
              </Button>
            )}
            <Button
              variant="secondary"
              onClick={runAnalysis}
              disabled={invalid || analyzing || nothingToAnalyze}
            >
              {analyzing
                ? "살펴보는 중…"
                : analyzed
                  ? "다시 살펴보기"
                  : "키워드 찾기"}
            </Button>
            {analyzed && !analyzing && (
              <span className="text-caption text-ink-soft">
                찾은 키워드는 다음 단계에서 미리 체크됩니다
              </span>
            )}
          </div>
        </div>
      )}

      <StepNav
        back={
          <Button
            variant="secondary"
            onClick={() => router.push(exit.href)}
            disabled={analyzing}
          >
            <ArrowLeftIcon size={14} strokeWidth={1.7} />
            {exit.label}
          </Button>
        }
        next={
          <Button
            variant="primary"
            onClick={goNext}
            disabled={invalid || analyzing}
          >
            경험 입력
          </Button>
        }
      />
    </div>
  );
}
