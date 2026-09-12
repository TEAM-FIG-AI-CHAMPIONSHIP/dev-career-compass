import type { Metadata } from "next";
import { notFound } from "next/navigation";
import {
  getAnalysis,
  getExperienceCatalog,
  listCombinations,
  dataSource,
} from "@/lib/data";
import { NewSuggestions, DeepenSuggestions } from "@/components/result/SuggestionCards";
import { DomainChips } from "@/components/result/DomainChips";
import { EvidenceTimeline } from "@/components/result/EvidenceTimeline";
import { PageHeader, DataSourceNote } from "@/components/ui/PageHeader";
import { PersonalizedPanel } from "./PersonalizedPanel";

/** 게시된 조합만 페이지를 만듭니다. 나머지는 404 입니다. */
export const dynamicParams = false;

export function generateStaticParams() {
  return listCombinations();
}

export async function generateMetadata({
  params,
}: PageProps<"/[company]/[job]">): Promise<Metadata> {
  const { company, job } = await params;
  const analysis = getAnalysis(company, job);
  if (!analysis) return { title: "결과" };
  return { title: `${analysis.company.name} · ${analysis.job.name}` };
}

/**
 * S2 결과 + S4 개인화. 같은 URL 입니다.
 *
 * 공유 URL 에 개인화가 들어가면 안 되므로 별도 경로를 두지 않았습니다. 개인화는
 * 브라우저에 저장된 입력이 있을 때만 이 화면 위에 얹힙니다.
 *
 * 세로 순서는 제품의 주장입니다. 제안이 맨 위, 조직 영역은 그 아래, 근거
 * 타임라인은 접힌 채로 맨 끝. 이 순서는 바꾸지 않습니다.
 */
export default async function ResultPage({ params }: PageProps<"/[company]/[job]">) {
  const { company, job } = await params;
  const analysis = getAnalysis(company, job);
  if (!analysis) notFound();

  const catalog = getExperienceCatalog();
  const byId = new Map(analysis.evidence.map((e) => [e.id, e]));
  const experienceHref = `/experience?job=${job}&from=${encodeURIComponent(`/${company}/${job}`)}`;

  const window = `${analysis.window.from.slice(0, 7).replace("-", ".")} – ${analysis.window.to
    .slice(0, 7)
    .replace("-", ".")}`;

  return (
    <>
      <PageHeader
        crumbs={[
          <span key="c" className="text-[0.875rem] leading-[1.6] text-ink-soft">
            {analysis.company.name}
          </span>,
          <span key="j" className="text-[0.875rem] leading-[1.6] text-ink">
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
        {/* 제안이 최상단. 조직 영역보다 아래로 내려가지 않습니다. */}
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

        <PersonalizedPanel catalog={catalog} experienceHref={experienceHref} />

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
