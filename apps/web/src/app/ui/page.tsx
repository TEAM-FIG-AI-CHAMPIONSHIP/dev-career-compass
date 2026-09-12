import type { Metadata } from "next";
import { Button } from "@/components/ui/Button";
import { Chip, EvidenceCount } from "@/components/ui/Chip";
import { StageBadge, STAGE_ORDER } from "@/components/ui/StageBadge";
import { Empty } from "@/components/ui/state/Empty";
import { Loading } from "@/components/ui/state/Loading";
import { ErrorState } from "@/components/ui/state/Error";
import { ThemeToggle } from "./ThemeToggle";
import { InteractiveSamples } from "./Interactive";

export const metadata: Metadata = {
  title: "컴포넌트",
  robots: { index: false, follow: false },
};

const NEUTRALS = [
  ["paper", "bg-paper"],
  ["surface", "bg-surface"],
  ["sunken", "bg-sunken"],
  ["line", "bg-line"],
  ["line-strong", "bg-line-strong"],
  ["ink-muted", "bg-ink-muted"],
  ["ink-soft", "bg-ink-soft"],
  ["ink", "bg-ink"],
] as const;

const TYPE_SCALE = [
  ["display", "text-display", "지금 뭘 만들지 알려줍니다"],
  ["h1", "text-h1", "올리브영 · 서버·백엔드"],
  ["h2", "text-h2 font-semibold", "지금부터 만들면 좋을 것"],
  ["h3", "text-h3 font-semibold", "재고 차감 경합을 직접 만들어 깨뜨려 보기"],
  ["body", "text-body", "같은 상품 재고를 동시에 줄이는 요청이 몰릴 때 무엇이 깨지는지 재현합니다."],
  ["body-sm", "text-body-sm text-ink-soft", "선택한 값은 이 브라우저에만 남습니다."],
  ["caption", "text-caption text-ink-soft", "최근 12개월 수집분 기준"],
  ["meta", "text-meta font-mono font-medium", "2026.04 · 기술 블로그 · 5건"],
] as const;

function Section({
  title,
  note,
  children,
}: {
  title: string;
  note?: string;
  children: React.ReactNode;
}) {
  return (
    <section className="flex flex-col gap-4">
      <div className="flex flex-wrap items-baseline gap-2.5 border-b border-line-strong pb-2.5">
        <h2 className="text-h2 font-semibold">{title}</h2>
        {note && <span className="text-body-sm text-ink-soft">{note}</span>}
      </div>
      {children}
    </section>
  );
}

export default function UiGallery() {
  return (
    <main className="mx-auto flex w-full max-w-5xl flex-col gap-11 px-4 py-12 sm:px-8">
      <header className="flex flex-wrap items-end justify-between gap-5 border-b border-ink pb-6">
        <div className="flex flex-col gap-2">
          <span className="font-mono text-meta tracking-[0.08em] text-ink-soft">
            COMPONENTS
          </span>
          <h1 className="text-display font-semibold">컴포넌트 갤러리</h1>
          <p className="max-w-xl text-body text-ink-soft">
            design 캔버스의 토큰·컴포넌트 시트를 코드로 옮긴 것입니다. 제품
            화면이 아니라 확인용이며 색인되지 않습니다.
          </p>
        </div>
        <ThemeToggle />
      </header>

      <Section title="중립 스케일" note="이름이 같고 값만 뒤집힙니다">
        <div className="grid grid-cols-4 gap-2.5 sm:grid-cols-8">
          {NEUTRALS.map(([name, bg]) => (
            <div key={name} className="flex flex-col gap-1.5">
              <div className={`h-16 rounded-card border border-line-strong ${bg}`} />
              <span className="font-mono text-[0.6875rem] break-all">{name}</span>
            </div>
          ))}
        </div>
      </Section>

      <Section title="악센트 · 출처 · 3단계">
        <div className="grid grid-cols-1 gap-7 sm:grid-cols-3">
          <div className="flex flex-col gap-2.5">
            <span className="font-mono text-[0.71875rem] text-ink-muted">ACCENT</span>
            <div className="grid grid-cols-3 gap-2.5">
              <div className="h-14 rounded-card bg-accent" />
              <div className="h-14 rounded-card bg-accent-ink" />
              <div className="h-14 rounded-card border border-line-strong bg-accent-tint" />
            </div>
          </div>
          <div className="flex flex-col gap-2.5">
            <span className="font-mono text-[0.71875rem] text-ink-muted">
              SOURCE · WARN
            </span>
            <div className="grid grid-cols-3 gap-2.5">
              <div className="h-14 rounded-card bg-src-blog" />
              <div className="h-14 rounded-card bg-src-job" />
              <div className="h-14 rounded-card bg-warn" />
            </div>
          </div>
          <div className="flex flex-col gap-2.5">
            <span className="font-mono text-[0.71875rem] text-ink-muted">STAGE</span>
            <div className="grid grid-cols-3 gap-2.5">
              <div className="h-14 rounded-card bg-stage-fit" />
              <div className="h-14 rounded-card bg-stage-step" />
              <div className="h-14 rounded-card bg-stage-far" />
            </div>
          </div>
        </div>
      </Section>

      <Section title="타이포그래피" note="행간은 한글 기준입니다">
        <div className="flex flex-col border-t border-line-strong">
          {TYPE_SCALE.map(([name, cls, sample]) => (
            <div
              key={name}
              className="flex flex-col gap-1 border-b border-line py-4 sm:flex-row sm:items-baseline sm:gap-6"
            >
              <span className="w-28 shrink-0 font-mono text-[0.71875rem] text-ink-soft">
                {name}
              </span>
              <span className={cls}>{sample}</span>
            </div>
          ))}
        </div>
      </Section>

      <Section title="버튼">
        <div className="flex flex-wrap items-center gap-3">
          <Button variant="primary">내 경험 넣기</Button>
          <Button variant="secondary">다시 시도</Button>
          <Button variant="ghost">입력 지우기</Button>
          <Button variant="secondary" disabled>
            비활성
          </Button>
        </div>
      </Section>

      <Section title="영역 칩" note="건수는 집계 코드가 셉니다. LLM이 손대지 않습니다">
        <div className="flex flex-wrap gap-2.5">
          <Chip>
            재고·주문 동시성
            <span className="h-3.5 w-px bg-line" aria-hidden="true" />
            <EvidenceCount source="blog" count={5} />
            <EvidenceCount source="job" count={2} />
          </Chip>
          <Chip>
            배치를 이벤트로 옮기기
            <span className="h-3.5 w-px bg-line" aria-hidden="true" />
            <EvidenceCount source="blog" count={3} />
          </Chip>
          <Chip tone="ink">결제·정산 정합성</Chip>
          <Chip tone="accent">내 경험 반영됨</Chip>
        </div>
        <p className="text-body-sm text-ink-soft">
          공고 데이터가 없으면 공고 항목만 빠지고 칩은 그대로 뜹니다. 뉴스는 MVP
          범위에서 제외했습니다.
        </p>
      </Section>

      <Section
        title="역매칭 3단계"
        note="점수·퍼센트·순위를 쓰지 않습니다. 색·아이콘·문구로만 구분합니다"
      >
        <div className="flex flex-wrap gap-3">
          {STAGE_ORDER.map((stage) => (
            <StageBadge key={stage} stage={stage} />
          ))}
        </div>
      </Section>

      <Section title="입력" note="눌러서 상태를 확인할 수 있습니다">
        <InteractiveSamples />
      </Section>

      <Section title="상태">
        <div className="grid grid-cols-1 items-start gap-3.5 lg:grid-cols-3">
          <Empty />
          <Loading />
          <ErrorState />
        </div>
      </Section>
    </main>
  );
}
