import type { Metadata } from "next";
import { notFound } from "next/navigation";
import {
  getAnalysis,
  getExperienceCatalog,
  listCombinations,
  dataSource,
} from "@/lib/data";
import { routes } from "@/lib/routes";
import { NewSuggestions, DeepenSuggestions } from "@/components/result/SuggestionCards";
import { DomainChips } from "@/components/result/DomainChips";
import { EvidenceTimeline } from "@/components/result/EvidenceTimeline";
import { BackHeader } from "@/components/ui/BackHeader";
import { DataSourceNote } from "@/components/ui/PageHeader";
import { CircleCheckIcon, ClockIcon, SparkleIcon } from "@/components/ui/icons";
import { PersonalizedPanel } from "./PersonalizedPanel";

type Props = { params: Promise<{ company: string; role: string }> };

export const dynamicParams = false;

export function generateStaticParams() {
  return listCombinations().map(({ company, job }) => ({ company, role: job }));
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const { company, role } = await params;
  const analysis = getAnalysis(company, role);
  if (!analysis) return { title: "결과" };
  return { title: `${analysis.company.name} · ${analysis.job.name}` };
}

/**
 * 제안 무리의 소제목.
 *
 * "지금부터 만들면 좋을 것"과 "이미 만든 게 있다면"은 읽는 사람이 자기에게
 * 해당하는 쪽을 고르는 단서입니다. 작은 회색 글씨로 흘리면 카드만 눈에 들어와
 * 두 무리가 왜 나뉘어 있는지 보이지 않습니다.
 */
function GroupTitle({ children, caption }: { children: string; caption: string }) {
  return (
    <div className="flex flex-wrap items-baseline gap-2.5 border-b border-line pb-2">
      <h3 className="text-body font-semibold text-ink">{children}</h3>
      <span className="text-body-sm text-ink-muted">{caption}</span>
    </div>
  );
}

/** 절 제목. 아이콘은 장식이며 의미는 글자가 집니다. */
function SectionTitle({
  icon,
  children,
}: {
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <h2 className="flex items-center gap-2.5 text-h2 font-semibold">
      <span aria-hidden="true" className="text-accent">
        {icon}
      </span>
      {children}
    </h2>
  );
}

/** 기본 결과와 개인화 결과는 브라우저 경험 유무에 따라 같은 URL에서 전환됩니다. */
export default async function CompanyResultPage({ params }: Props) {
  const { company, role } = await params;
  const analysis = getAnalysis(company, role);
  if (!analysis) notFound();

  const catalog = getExperienceCatalog();
  const byId = new Map(analysis.evidence.map((evidence) => [evidence.id, evidence]));
  const domainLabel = (id: string) =>
    analysis.domains.find((domain) => domain.id === id)?.label;
  const hasSuggestions =
    analysis.suggestions.new.length > 0 || analysis.suggestions.deepen.length > 0;

  return (
    <>
      <BackHeader
        href={routes.companies}
        label="회사 선택"
        right={
          <span className="text-[0.875rem] leading-[1.6] text-ink-soft">
            {analysis.company.name} · {analysis.job.name}
          </span>
        }
      />

      <main className="grow bg-[linear-gradient(180deg,var(--accent-tint)_0%,var(--paper)_20rem)] px-4 pb-16 sm:px-8 lg:px-12 xl:px-20">
        <div className="mx-auto flex w-full max-w-7xl flex-col gap-12">
          <header className="flex max-w-3xl flex-col gap-2 pt-10 lg:pt-12">
            <h1 className="text-display font-semibold text-balance sm:text-[2.125rem]">
              {analysis.company.name} {analysis.job.name}
            </h1>
            <p className="text-body text-pretty text-ink-soft sm:text-base">
              이 조직이 반복해서 다루는 일과, 당신이 만들 수 있는 것
            </p>
          </header>

          {/* 제안이 맨 위입니다. 조직 영역과 근거보다 아래로 내려가지 않습니다. */}
          {hasSuggestions && (
            <section className="flex flex-col gap-5">
              <SectionTitle icon={<SparkleIcon size={20} strokeWidth={1.6} />}>
                프로젝트 방향 제안
              </SectionTitle>

              {analysis.suggestions.new.length > 0 && (
                <div className="flex flex-col gap-3.5">
                  <GroupTitle caption="아직 만든 게 없다면 여기서 시작하세요">
                    지금부터 만들면 좋을 것
                  </GroupTitle>
                  <NewSuggestions
                    suggestions={analysis.suggestions.new}
                    byId={byId}
                    domainLabel={domainLabel}
                  />
                </div>
              )}

              {analysis.suggestions.deepen.length > 0 && (
                <div className="flex flex-col gap-3.5">
                  <GroupTitle caption="버리지 말고 한 겹 더 파세요">
                    이미 만든 게 있다면
                  </GroupTitle>
                  <DeepenSuggestions
                    suggestions={analysis.suggestions.deepen}
                    byId={byId}
                    domainLabel={domainLabel}
                  />
                </div>
              )}
            </section>
          )}

          <PersonalizedPanel
            catalog={catalog}
            role={role}
            returnTo={routes.companyResult(company, role)}
          />

          {analysis.domains.length > 0 && (
            <section className="flex flex-col gap-4">
              <SectionTitle icon={<CircleCheckIcon size={20} strokeWidth={1.6} />}>
                조직이 반복하는 영역
              </SectionTitle>
              <DomainChips domains={analysis.domains} />
            </section>
          )}

          <section className="flex flex-col gap-4">
            <SectionTitle icon={<ClockIcon size={20} strokeWidth={1.6} />}>
              근거 타임라인
            </SectionTitle>
            <EvidenceTimeline evidence={analysis.evidence} />
          </section>
        </div>
      </main>

      <footer className="mt-auto">
        <DataSourceNote source={dataSource()} />
      </footer>
    </>
  );
}
