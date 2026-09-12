"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { Chip } from "@/components/ui/Chip";
import { RepoField } from "@/components/ui/RepoField";
import { PlusIcon } from "@/components/ui/icons";
import { useExperience } from "@/lib/experience-store";
import { saveMatchRepositories, useMatchFlow } from "@/lib/match-flow-store";
import { parseGithubUrl } from "@/lib/repo-keywords";
import { routes } from "@/lib/routes";

const MAX_REPOSITORIES = 3;

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
  rate_limited: "지금은 GitHub 확인이 지연되고 있어요. 나중에 다시 시도해 주세요.",
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
      | { ok: true; keywords: string[] }
      | { ok: false; reason: string };
    if (data.ok) return { kind: "done", keywords: data.keywords };
    return { kind: "error", message: REASON_MESSAGES[data.reason] ?? REASON_MESSAGES.unknown };
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

  const invalid = repositories.some(
    (repository) => repository.trim() !== "" && !parseGithubUrl(repository.trim()),
  );

  const updateField = (index: number, next: string) => {
    setDraft(
      repositories.map((current, currentIndex) => (currentIndex === index ? next : current)),
    );
    setAnalyzed(false);
  };

  const goWithoutAnalysis = () => {
    saveMatchRepositories(role, [], {});
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
      candidates.map(async (url) => [url, await analyzeRepository(url)] as const),
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
    <div className="flex max-w-3xl flex-col gap-8">
      <div className="flex flex-col gap-3">
        {repositories.map((repository, index) => {
          const trimmed = repository.trim();
          const fallbackKeywords = trimmed ? flow?.repositoryKeywords[trimmed] : undefined;
          const status: FieldStatus | undefined = trimmed
            ? (statuses[trimmed] ??
              (fallbackKeywords ? { kind: "done", keywords: fallbackKeywords } : undefined))
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
                <span className="text-caption text-ink-soft">찾은 키워드가 없어요.</span>
              )}
            </div>
          );
        })}

        {repositories.length < MAX_REPOSITORIES && (
          <Button
            variant="secondary"
            onClick={() => setDraft([...repositories, ""])}
            className="w-fit"
          >
            <PlusIcon size={14} strokeWidth={1.7} />
            저장소 추가
          </Button>
        )}
      </div>

      <div className="flex flex-wrap items-center gap-3.5 border-t border-line pt-6">
        <Button
          variant="secondary"
          onClick={() => router.push(routes.match)}
          disabled={analyzing}
          className="min-h-12 px-6 py-4 text-[0.9375rem]"
        >
          ← 직무로
        </Button>
        <Button
          variant="primary"
          onClick={analyzed && !analyzing ? () => router.push(routes.matchExperience(role)) : runAnalysis}
          disabled={invalid || analyzing}
          className="min-h-12 px-6 py-4 text-[0.9375rem]"
        >
          {analyzing ? "분석하는 중…" : analyzed ? "다음: 경험 입력으로" : "분석하고 경험 선택으로"}
        </Button>
        <Button variant="ghost" onClick={goWithoutAnalysis} disabled={analyzing}>
          GitHub 없이 진행
        </Button>
      </div>
    </div>
  );
}
