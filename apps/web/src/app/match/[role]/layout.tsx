import type { ReactNode } from "react";
import { listJobs } from "@/lib/data";

/** 게시된 분석이 있는 직무만 단계별 매칭 화면을 만듭니다. */
export const dynamicParams = false;

export function generateStaticParams() {
  return listJobs().map((job) => ({ role: job.slug }));
}

export default function MatchRoleLayout({ children }: { children: ReactNode }) {
  return children;
}
