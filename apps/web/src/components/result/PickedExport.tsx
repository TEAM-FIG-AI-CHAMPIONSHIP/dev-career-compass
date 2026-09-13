"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { TerminalWindow } from "@/components/ui/TerminalWindow";
import {
  clearPicks,
  countPicked,
  toMarkdown,
  usePicks,
} from "@/lib/suggestion-picks";

/**
 * 고른 제안을 밖으로 내보냅니다.
 *
 * 이 서비스에는 로그인이 없습니다. 그래서 진행을 우리가 보관하는 대신,
 * 고른 것을 마크다운 체크리스트로 넘겨 각자 쓰는 도구(README, 노션, 이슈)로
 * 가져가게 합니다. 한 번의 방문으로 가치가 끝나야 로그인 없는 서비스가
 * 약속을 지킬 수 있습니다.
 *
 * 파일로 내려받지 않고 글로 보여줍니다. 붙여 넣을 곳이 대부분 웹 편집기라
 * 파일을 거치면 단계만 하나 늘어납니다.
 */
export function PickedExport({ heading }: { heading: string }) {
  const picks = usePicks();
  const [copied, setCopied] = useState(false);
  const total = countPicked(picks);

  async function copy() {
    try {
      await navigator.clipboard.writeText(toMarkdown(picks, heading));
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1600);
    } catch {
      /* 클립보드를 막아 둔 환경에서는 아래 글을 직접 선택해 복사합니다. */
    }
  }

  return (
    <TerminalWindow
      title="refactor.me — export"
      bodyClassName="flex flex-col gap-3 p-4 sm:p-5"
    >
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-body-sm text-ink">
          <span className="text-accent">$ </span>refactor export --md
        </p>
        {total > 0 && (
          <div className="flex items-center gap-2">
            <Button variant="ghost" onClick={clearPicks} className="px-3 py-2">
              비우기
            </Button>
            <Button variant="primary" onClick={copy} className="px-4 py-2">
              {copied ? "복사했습니다" : "복사하기"}
            </Button>
          </div>
        )}
      </div>

      {total === 0 ? (
        <p className="text-caption text-ink-muted">
          &gt; 해볼 것을 골라 보세요. 체크한 항목만 여기에 모입니다.
        </p>
      ) : (
        <>
          <p className="text-caption text-ink-muted">
            &gt; {total}개 담김 · 아래 글을 그대로 붙여 넣으면 체크리스트가
            됩니다
          </p>
          {/* 고정폭 그대로 둡니다. 붙여 넣을 곳에서 보일 모양과 같아야 합니다. */}
          <pre className="max-h-64 overflow-auto rounded-card border border-line bg-sunken p-3.5 text-caption whitespace-pre-wrap text-ink-soft">
            {toMarkdown(picks, heading)}
          </pre>
        </>
      )}
    </TerminalWindow>
  );
}
