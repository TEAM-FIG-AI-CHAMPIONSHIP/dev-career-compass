import type { Metadata } from "next";
import { notFound } from "next/navigation";
import {
  getAnalysis,
  getExperienceCatalog,
  listCombinations,
  dataSource,
} from "@/lib/data";
import { routes } from "@/lib/routes";
import { PageWidth } from "@/components/ui/PageWidth";
import {
  NewSuggestions,
  DeepenSuggestions,
} from "@/components/result/SuggestionCards";
import { DomainChips } from "@/components/result/DomainChips";
import { PickedExport } from "@/components/result/PickedExport";
import { AppHeader } from "@/components/ui/AppHeader";
import { ButtonLink } from "@/components/ui/Button";
import { StepNav } from "@/components/ui/StepNav";
import { DataSourceNote } from "@/components/ui/DataSourceNote";
import { ExperiencePanel } from "./ExperiencePanel";
import { ArrowLeftIcon } from "@/components/ui/icons";

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
 * 제안 무리의 제목.
 *
 * 카드 제목보다 큰 글자를 씁니다. 라벨이 그 아래 내용보다 작으면 카드만 눈에
 * 들어와 두 무리가 왜 나뉘어 있는지 보이지 않습니다.
 */
function GroupTitle({
  children,
  caption,
}: {
  children: string;
  caption: string;
}) {
  return (
    <div className="flex flex-wrap items-baseline gap-3 border-b border-line-strong pb-2.5">
      <h2 className="text-h2 font-semibold text-ink">{children}</h2>
      <span className="text-caption text-ink-muted">{caption}</span>
    </div>
  );
}

/**
 * 화면 순서는 이렇습니다.
 *
 *  1. 이 조직이 반복해서 다루는 일   — 제목 바로 아래 배지
 *  2. 새로 시작할 것
 *  3. 이미 만든 것을 발전시킬 것
 *  4. 내 경험                        — 유도 카드와 요약이 같은 자리를 씁니다
 *
 * 영역 배지가 위에 있는 이유는 제안 카드마다 그 영역 이름이 태그로 붙기
 * 때문입니다. 배지가 아래에 있으면 태그에 쓰인 말을 화면 끝에 가서야 배웁니다.
 *
 * 두 제안 무리를 한 절로 묶지 않습니다. 바깥 제목을 하나 더 두면 무리 제목이
 * 가운데 눌려 카드 제목보다 작아집니다.
 */
export default async function CompanyResultPage({ params }: Props) {
  const { company, role } = await params;
  const analysis = getAnalysis(company, role);
  if (!analysis) notFound();

  const catalog = getExperienceCatalog();
  const returnTo = routes.companyResult(company, role);
  /* 제안 카드는 클라이언트 컴포넌트입니다. Map 이나 함수는 서버 경계를 넘지
     못하므로 평범한 객체로 만들어 넘깁니다. */
  const evidence = Object.fromEntries(
    analysis.evidence.map((item) => [item.id, item]),
  );
  const domainLabels = Object.fromEntries(
    analysis.domains.map((domain) => [domain.id, domain.label]),
  );

  return (
    <>
      <AppHeader
        right={
          <span className="text-body-sm text-ink-soft">
            {analysis.company.name} · {analysis.job.name}
          </span>
        }
      />

      <main className="grow pb-16">
        <PageWidth className="flex flex-col gap-12">
          <header className="flex flex-col gap-5 pt-10 lg:pt-12">
            <div className="flex max-w-3xl flex-col gap-2">
              <h1 className="text-display font-semibold text-balance">
                {analysis.company.name} {analysis.job.name}
              </h1>
              <p className="text-body text-pretty text-ink-soft sm:text-base">
                이 조직이 반복해서 다루는 일입니다. 아래 제안은 모두 여기서
                나왔습니다.
              </p>
            </div>
            {analysis.domains.length > 0 && (
              <DomainChips domains={analysis.domains} />
            )}
          </header>

          {analysis.suggestions.new.length > 0 && (
            <section className="flex flex-col gap-4">
              <GroupTitle caption="만든 게 없어도 바로 시작할 수 있습니다">
                새로 시작할 것
              </GroupTitle>
              <NewSuggestions
                suggestions={analysis.suggestions.new}
                evidence={evidence}
                domainLabels={domainLabels}
              />
            </section>
          )}

          {analysis.suggestions.deepen.length > 0 && (
            <section className="flex flex-col gap-4">
              <GroupTitle caption="이미 만든 것 위에 한 겹 더 얹습니다">
                이미 만든 것을 발전시킬 것
              </GroupTitle>
              <DeepenSuggestions
                suggestions={analysis.suggestions.deepen}
                evidence={evidence}
                domainLabels={domainLabels}
              />
            </section>
          )}

          {/* 고른 제안은 여기서 밖으로 나갑니다. 제안 무리 바로 아래에 두어,
              체크한 다음 눈을 멀리 옮기지 않고 담긴 것을 확인하게 합니다. */}
          <PickedExport
            heading={`${analysis.company.name} · ${analysis.job.name} — 다음에 만들 것`}
          />

          <ExperiencePanel catalog={catalog} role={role} returnTo={returnTo} />

          <StepNav
            back={
              <ButtonLink variant="secondary" href={routes.companies}>
                <ArrowLeftIcon size={14} strokeWidth={1.7} />
                회사 선택
              </ButtonLink>
            }
          />
        </PageWidth>
      </main>

      <footer className="mt-auto">
        <DataSourceNote source={dataSource()} />
      </footer>
    </>
  );
}
