# [experiment] 기술블로그 census 제목 보강 후 1차 게이트 재집계

라벨: 없음
담당자: 이슈 작성자
이슈: #40
관련: #30

---

## 작업 내용

- #30 1·2라운드에서 sitemap URL은 모았지만 lastmod만 있는 글은 제목이 비어 있다. 빈 제목은 전부 비기술로 분류되어, URL이 많은 회사도 `unknown`으로 남는다.
- sitemap에는 태그·페이지네이션·홈 같은 목록 URL도 섞여 있다. 글이 아닌 URL은 빼고, 남는 글의 제목을 HTML(`og:title` 포함)에서 채운 뒤 게이트를 다시 센다.
- Area / embedding / clustering / LLM은 범위 밖이다. 뉴스·공고로 블로그 공백을 메우지 않는다.
- 우아한형제들처럼 robots/sitemap이 403인 곳은 이번에도 custom을 만들지 않는다. 제목 보강 후에도 `unknown`이면 다음 이슈로 둔다.
- 본문은 `data/work`에만 두고 커밋하지 않는다. 60~80개를 맞추려고 기준을 낮추지 않는다.

## 완료 기준

- [ ] sitemap에서 태그·목록·홈 URL을 제외한다.
- [ ] 남는 글의 빈 제목을 HTML(`og:title` 포함)에서 보강한다.
- [ ] 제목(+있으면 본문)으로 기술글·직무를 다시 분류하고 1차 게이트를 재집계한다.
- [ ] `data/research/tech_blog_company_role_census/`의 summary·selected·unknown을 갱신한다.
- [ ] 표의 X와 `unknown`은 탈락이 아님을 유지한다.
- [ ] Area / LLM / 본문 커밋 / 403 custom / 회사 목록 확정은 하지 않는다.

## 참고 사항

- 브랜치: `experiment/tech-blog-census-title-gate`
- 이슈: #40
- 관련: #30
- 실행:

```bash
python pipeline/experiments/tech_blog_company_role_census/scripts/backfill_titles.py
python pipeline/experiments/tech_blog_company_role_census/scripts/extract.py
python pipeline/experiments/tech_blog_company_role_census/scripts/classify_and_gate.py
```
