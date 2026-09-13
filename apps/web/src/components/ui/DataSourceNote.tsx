import { PageWidth } from "./PageWidth";

/** 지금 어떤 데이터를 보고 있는지. fixture 를 실제 결과로 오해하지 않게 합니다. */
export function DataSourceNote({
  source,
}: {
  source: "published" | "fixtures";
}) {
  if (source === "published") return null;
  return (
    <div className="border-t border-line">
      <PageWidth className="py-4">
        <p className="text-caption text-ink-muted">
          지금 보이는 회사와 근거는 화면 확인용 임시 데이터입니다. 기술 블로그와
          채용 공고의 검증·확정은 따로 진행 중이며, 그 결과가 들어오면 이 화면이
          그대로 바뀝니다.
        </p>
      </PageWidth>
    </div>
  );
}
