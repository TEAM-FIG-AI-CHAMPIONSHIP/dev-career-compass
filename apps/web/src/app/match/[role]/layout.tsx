import type { ReactNode } from "react";
import { listRoles } from "@/lib/data";

/** 존재하는 직무 전부에 단계별 매칭 화면을 만듭니다 — 매칭 가능한 회사가
    아직 없어도 저장소·경험 입력 화면은 열려야 합니다. */
export const dynamicParams = false;

export function generateStaticParams() {
  return listRoles().map((role) => ({ role: role.slug }));
}

export default function MatchRoleLayout({ children }: { children: ReactNode }) {
  return children;
}
