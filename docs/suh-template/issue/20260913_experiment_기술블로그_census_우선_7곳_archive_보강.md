# [experiment] 기술블로그 census 우선 7곳 archive/custom 보강

라벨: 없음
담당자: 이슈 작성자
관련: #30 #40

---

## 작업 내용

- 1차 게이트(직무당 최근 12개월 기술글 8개)는 낮추지 않는다. 60~80을 맞추려고 회사 이름으로 pass를 주지 않는다.
- 지금 코드 통과는 29곳이다. 제품 가치는 높은데 generic RSS/sitemap이 비어 있거나 과소 집계인 아래 7곳을 archive/custom으로 보강한 뒤 같은 게이트를 다시 센다.
  - 우아한형제들 / 배달의민족
  - 카카오뱅크
  - 카카오페이
  - 카카오모빌리티
  - 무신사 / 29CM
  - 여기어때
  - 위대한상상 / 요기요
- 팀원 `archive_collector`와 기존 census 스크립트를 재사용한다. Area / embedding / clustering / LLM은 건드리지 않는다.
- 본문은 `data/work`에만 두고 커밋하지 않는다.

## 완료 기준

- [ ] 위 7곳에 archive 또는 회사별 custom 수집이 돈다.
- [ ] 같은 1차 게이트로 `pass` / `fail` / `unknown`을 다시 집계한다. 기준은 8개 그대로다.
- [ ] `data/research/tech_blog_company_role_census/`를 갱신한다.
- [ ] 7곳 중 generic이 여전히 실패하면 이유를 기록하고, 통과하지 못한 곳은 pass 목록에 넣지 않는다.
- [ ] Area / LLM / 본문 커밋 / 회사 목록 확정은 하지 않는다.

## 참고 사항

- 브랜치: `experiment/tech-blog-census-priority-collect`
- 관련: #30, #40
- 네이버 D2·토스 custom adapter는 팀원 실험에 이미 있다. 이번 7곳에는 넣지 않는다.
- 우아한형제들은 별도 조사에서 기술블로그 수집이 가능하다. 이 census 경로의 표준 HTML/RSS/sitemap만 403이다.
