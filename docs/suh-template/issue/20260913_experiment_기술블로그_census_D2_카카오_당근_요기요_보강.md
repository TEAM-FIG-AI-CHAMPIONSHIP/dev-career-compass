# [experiment] 기술블로그 census D2·카카오·당근·요기요 보강

라벨: 없음
담당자: 이슈 작성자
관련: #40

---

## 작업 내용

- 1차 게이트(직무당 최근 12개월 기술글 8개)는 낮추지 않는다. 60개를 맞추려고 pass를 주지 않는다.
- 지금 코드 통과는 32곳이다. generic RSS/sitemap이 최근 N건만 주거나 과소 집계인 아래를 한 이슈에서 보강한 뒤 같은 게이트를 다시 센다.
  - 네이버 D2: 기존 custom adapter 목록 API를 census에 합친다. Atom은 최신 20건만 준다.
  - 카카오: sitemap `lastmod` + 글 HTML의 `datePublished`로 12개월을 채운다. RSS는 최신 10건만 준다.
  - 당근: Medium collection stream API. RSS는 최신 10건만 준다.
  - 요기요: Medium collection stream + 남은 sitemap 글. 글은 있으나 직무당 8이 안 되고 창이 안 닫혔다.
- 같은 Medium stream으로 값싸게 닫히는 unknown(딜라이트룸, SSG.COM, 미리디 등)도 같이 넣는다. 회사별 크롤러를 더 늘리지는 않는다.
- Area / embedding / clustering / LLM은 건드리지 않는다. 본문은 `data/work`에만 두고 커밋하지 않는다.

## 완료 기준

- [ ] D2 목록 API 결과가 census `articles.json`에 합쳐진다.
- [ ] 카카오·당근·요기요에 custom/Medium 수집이 돈다.
- [ ] 같은 1차 게이트로 `pass` / `fail` / `unknown`을 다시 집계한다. 기준은 8개 그대로다.
- [ ] `data/research/tech_blog_company_role_census/`를 갱신한다.
- [ ] 모이지 않거나 직무당 8 미만이면 pass 목록에 넣지 않는다.
- [ ] Area / LLM / 본문 커밋 / 회사 목록 확정은 하지 않는다.

## 참고 사항

- 브랜치: `experiment/tech-blog-census-expand-collect`
- 관련: #40 (이전 #30)
- 카카오뱅크·페이·모빌리티는 이미 12개월을 닫고 fail이다. 이번 대상이 아니다.
- 우아한형제들은 별도 조사로 이미 pass다.
