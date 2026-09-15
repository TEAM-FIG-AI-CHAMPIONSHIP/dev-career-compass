/**
 * data/ 디렉터리가 담고 있는 모양입니다.
 *
 * 계약(contract)이 아니라 웹이 fixture 를 읽기 위해 쓰는 내부 타입입니다.
 * 파이프라인 산출물의 실제 모양은 담당자가 정하며, 그것이 정해지면 이 파일을
 * 거기에 맞춰 고칩니다. 지금 이 타입에 맞춰 파이프라인을 만들라는 뜻이 아닙니다.
 */

/** data/index.json */
export type CompanyIndex = {
  generatedAt: string;
  /** 이 회사×직무 범위를 확정한 PR 번호. fixture 인덱스의 추적용 메타데이터입니다. */
  sourcePullRequests?: number[];
  /** 직무를 노출하기 위한 회사별 최소 evidence 글 수. */
  threshold?: number;
  /** 회사×직무 조합 총수. 화면에서는 companies 로 다시 계산해 검증합니다. */
  pairCount?: number;
  companies: Company[];
};

export type Company = {
  /** URL 과 파일 이름에 그대로 쓰입니다. 소문자·숫자·하이픈. */
  slug: string;
  name: string;
  /** public 아래에 둔 회사 로고 경로. 예: /company-logos/example.svg */
  logoSrc?: string;
  /** 로고가 아직 없을 때 보여주는 한 글자 fallback. */
  mark?: string;
  /** 이 조직이 반복해서 다루는 영역을 한 줄로. */
  summary?: string;
  evidenceCount?: number;
  /** collecting 이면 S1 목업에는 보이지만 결과 페이지 링크를 만들지 않습니다. */
  status: "published" | "collecting";
  jobs?: Job[];
};

export type Job = {
  slug: string;
  name: string;
  evidenceCount?: number;
};

/**
 * 근거 문서 한 건.
 *
 * 본문을 담는 필드가 없습니다. 화면에는 제목·발행일·출처·원문 링크까지만
 * 보여주며 본문을 다시 싣지 않습니다.
 */
export type Evidence = {
  id: string;
  title: string;
  /** YYYY-MM-DD. 정렬에 쓰고 화면에는 연월까지만 보여줍니다. */
  publishedAt: string;
  /** 뉴스는 MVP 범위에서 제외했습니다. */
  source: "blog" | "job";
  url: string;
};

/** 출처별 근거 건수. 파이프라인이 센 값을 그대로 쓰며 화면에서 다시 세지 않습니다. */
export type EvidenceCounts = {
  blog: number;
  /** 채용 데이터가 없으면 이 필드가 아예 없습니다. */
  job?: number;
};

export type Domain = {
  id: string;
  /** 예: 재고 정합성·품절 반영 */
  label: string;
  counts: EvidenceCounts;
  evidenceIds: string[];
};

/** 새로 시작할 것. 만든 게 없어도 착수할 수 있는 제안입니다. */
export type NewSuggestion = {
  id: string;
  title: string;
  body: string;
  /**
   * 해볼 것. 화면은 문단이 아니라 이 목록을 보여줍니다.
   *
   * 문장을 나누는 일은 사람(또는 생성 단계)이 합니다. 화면에서 문장 부호로
   * 자르면 "…가 핵심입니다" 같은 조언까지 할 일로 섞입니다.
   */
  steps: string[];
  domainId: string;
  /**
   * 이 제안이 쓰는 경험 항목(`data/experience.json` 의 item id).
   *
   * 고른 경험과 겹치면 카드에 "내 경험과 겹침" 이름표가 붙습니다. 순서는
   * 바꾸지 않습니다 — 쉬운 것이 먼저 와야 할 이유가 없습니다.
   */
  coversItemIds: string[];
  evidenceIds: string[];
  /** 신입 공고에서도 요구되는지. 채용 데이터가 있을 때만 붙습니다. */
  juniorDemand?: boolean;
};

/** 이미 만든 것을 발전시킬 것 — A를 만들었다면 → B. */
export type DeepenSuggestion = {
  id: string;
  from: string;
  to: string;
  body: string;
  /** 해볼 것. NewSuggestion 과 같은 규칙입니다. */
  steps: string[];
  domainId: string;
  /**
   * 이 제안이 전제하는 경험 항목.
   *
   * `from` 이 "…만들었다면" 이므로, 그 경험이 없는 사람에게는 제안 자체가
   * 성립하지 않습니다. 그래서 이쪽은 순서를 바꿉니다 — 전제가 있는 제안이
   * 먼저입니다.
   */
  fromItemIds: string[];
  evidenceIds: string[];
  juniorDemand?: boolean;
};

/** data/published/{회사}/{직무}.json */
export type Analysis = {
  company: { slug: string; name: string };
  job: { slug: string; name: string };
  generatedAt: string;
  /** 수집 기간. YYYY-MM-DD. */
  window: { from: string; to: string };
  domains: Domain[];
  suggestions: {
    new: NewSuggestion[];
    deepen: DeepenSuggestion[];
  };
  evidence: Evidence[];
};

/** data/experience.json — 경험 입력(F-05)이 읽어 체크 항목을 그립니다. */
export type ExperienceCatalog = {
  /**
   * 항목을 추가·삭제·변경하면 올립니다. 브라우저에 저장된 입력의
   * catalogVersion 과 다르면 그 입력은 버립니다 — 사라진 항목 id 가 남아
   * 엉뚱한 결과가 나가는 것을 막습니다.
   */
  version: number;
  groups: ExperienceGroup[];
  /** 배열 순서가 화면 순서이자 깊이 순서입니다. */
  levels: ExperienceLevel[];
};

export type ExperienceGroup = {
  id: string;
  title: string;
  caption?: string;
  /** 이 그룹을 보여줄 직무 슬러그. 없으면 모든 직무에 보입니다. */
  appliesTo?: string[];
  items: ExperienceItem[];
};

export type ExperienceItem = {
  id: string;
  label: string;
  description?: string;
};

export type ExperienceLevel = {
  id: string;
  step: string;
  title: string;
  description: string;
};

/** 사용자가 고른 값. 브라우저에만 저장하고 서버에 보관하지 않습니다. */
export type ExperienceInput = {
  catalogVersion: number;
  /** 최소 개수를 강제하지 않으므로 빈 배열일 수 있습니다. */
  itemIds: string[];
  levelId: string;
  /** GitHub 사용자명/저장소. 최대 3개. */
  repos?: string[];
};
