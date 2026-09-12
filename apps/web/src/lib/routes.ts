/**
 * 제품의 공개 URL을 한곳에서 만듭니다.
 *
 * 회사와 직무처럼 화면을 식별하는 값만 경로에 넣고, 사용자가 고른 저장소와
 * 경험은 브라우저 저장소에만 둡니다.
 */
const segment = (value: string) => encodeURIComponent(value);

export const routes = {
  home: "/",
  companies: "/companies",
  match: "/match",
  companyResult: (company: string, role: string) =>
    `/companies/${segment(company)}/${segment(role)}`,
  matchRepository: (role: string) => `/match/${segment(role)}/repository`,
  matchExperience: (role: string) => `/match/${segment(role)}/experience`,
  matchResult: (role: string) => `/match/${segment(role)}/result`,
} as const;
