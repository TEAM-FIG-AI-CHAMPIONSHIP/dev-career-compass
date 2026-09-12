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
import { PageHeader, DataSourceNote } from "@/components/ui/PageHeader";
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

/** 기본 결과와 개인화 결과는 브라우저 경험 유무에 따라 같은 URL에서 전환됩니다. */
export default async function CompanyResultPage({ params }: Props) {
  const { company, role } = await params;
  const analysis = getAnalysis(company, role);
  if (!analysis) notFound();

  const catalog = getExperienceCatalog();
  const byId = new Map(analysis.evidence.map((evidence) => [evidence.id, evidence]));
  const resultPath = routes.companyResult(company, role);
  const window = `${analysis.window.from.slice(0, 7).replace("-", ".")} – ${analysis.window.to
    .slice(0, 7)
    .replace("-", ".")}`;

  return (
    <>
      <PageHeader
        crumbs={[
          <span key="company" className="text-[0.875rem] leading-[1.6] text-ink-soft">
            {analysis.company.name}
          </span>,
          <span key="role" className="text-[0.875rem] leading-[1.6] text-ink">
            {analysis.job.name}
          </span>,
        ]}
        right={
          <span className="font-mono text-meta text-ink-muted">
            근거 {analysis.evidence.length}건 · {window}
          </span>
        }
      />

      <main className="flex grow flex-col gap-12 px-4 py-12 sm:px-8 lg:px-20 lg:py-14">
        <section className="flex flex-col gap-4">
          <div className="flex flex-wrap items-baseline gap-3 border-b border-ink pb-2.5">
            <h1 className="text-h1 font-semibold sm:text-[1.375rem]">
              지금부터 만들면 좋을 것
            </h1>
            <span className="text-body-sm text-ink-soft">
              아직 만든 게 없다면 여기서 시작하세요
            </span>
          </div>
          <NewSuggestions suggestions={analysis.suggestions.new} byId={byId} />
        </section>

        {analysis.suggestions.deepen.length > 0 && (
          <section className="flex flex-col gap-4">
            <div className="flex flex-wrap items-baseline gap-3 border-b border-ink pb-2.5">
              <h2 className="text-h1 font-semibold sm:text-[1.375rem]">
                이미 만든 게 있다면
              </h2>
              <span className="text-body-sm text-ink-soft">
                버리지 말고 한 겹 더 파세요
              </span>
            </div>
            <DeepenSuggestions suggestions={analysis.suggestions.deepen} byId={byId} />
          </section>
        )}

        <section className="flex flex-col gap-4">
          <div className="flex flex-wrap items-baseline gap-3 border-b border-line-strong pb-2.5">
            <h2 className="text-h2 font-semibold">이 조직이 반복해서 다루는 것</h2>
            <span className="text-body-sm text-ink-soft">
              회사 소개가 아니라, 실제로 쓴 글에서 세어 본 것입니다
            </span>
          </div>
          <DomainChips domains={analysis.domains} />
        </section>

        <PersonalizedPanel catalog={catalog} role={role} returnTo={resultPath} />

        <section className="flex flex-col gap-3.5">
          <div className="flex flex-wrap items-baseline gap-3">
            <h2 className="text-h2 font-semibold">근거</h2>
            <span className="text-body-sm text-ink-soft">
              위 제안이 어느 글에서 나왔는지 직접 확인하세요
            </span>
          </div>
          <EvidenceTimeline evidence={analysis.evidence} />
        </section>
      </main>

      <footer className="mt-auto">
        <DataSourceNote source={dataSource()} />
      </footer>
    </>
  );
}
