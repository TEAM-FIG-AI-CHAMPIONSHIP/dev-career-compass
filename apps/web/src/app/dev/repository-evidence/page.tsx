import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { PageHeader } from "@/components/ui/PageHeader";
import { RepositoryEvidencePreview } from "./RepositoryEvidencePreview";

export const metadata: Metadata = {
  title: "GitHub 근거 수집기 미리보기",
  robots: { index: false, follow: false },
};

export const dynamic = "force-dynamic";

export default function RepositoryEvidencePreviewPage() {
  if (process.env.NODE_ENV === "production") notFound();

  return (
    <>
      <PageHeader
        crumbs={[
          <span key="development" className="text-body-sm text-ink-soft">
            개발 도구
          </span>,
          <span key="collector" className="text-body-sm text-ink">
            GitHub 근거 수집기
          </span>,
        ]}
      />
      <RepositoryEvidencePreview />
    </>
  );
}
