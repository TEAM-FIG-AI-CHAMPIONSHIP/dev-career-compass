# Tech Blog Company × Role Census

관련 이슈: census 보강 (이전 #40 #30)

111개 기술블로그를 저비용으로 전수 조사해 `회사 × 직무` 1차 게이트를 만든다.
회사 이름으로 60~80개를 먼저 고르지 않는다.

Area / embedding / clustering / LLM은 이 실험에 없다.

## 1차 게이트

- 최근 12개월 기술글만 센다.
- 직무당 기술글 8개 이상이면 그 직무를 연다.
- 통과 직무가 1개 이상이면 회사를 노출 후보로 둔다.
- 8개는 글 수 게이트일 뿐이고, Area 3개·근거 2개는 다음 단계다.
- 판정은 `pass` / `fail` / `unknown` 이다. RSS를 못 받은 회사는 탈락이 아니라 `unknown`이다.

## 실행

```bash
python3 -m pip install -r pipeline/experiments/tech_blog_company_role_census/requirements.txt
python pipeline/experiments/tech_blog_company_role_census/scripts/collect.py
python pipeline/experiments/tech_blog_company_role_census/scripts/collect_round2.py
python pipeline/experiments/tech_blog_company_role_census/scripts/backfill_titles.py
python pipeline/experiments/tech_blog_company_role_census/scripts/collect_priority.py
python pipeline/experiments/tech_blog_company_role_census/scripts/collect_expand.py
python pipeline/experiments/tech_blog_company_role_census/scripts/collect_wayback.py
python pipeline/experiments/tech_blog_company_role_census/scripts/extract.py
python pipeline/experiments/tech_blog_company_role_census/scripts/classify_and_gate.py
```

수집은 회사 단위로 저장하므로 중간에 멈춰도 이어서 돈다.

`collect_wayback.py`는 RSS 항목 수 상한으로 창이 짧아진 회사를 보강한다.
토스는 sitemap이 없어 Wayback CDX가 기본이고, 가비아·한컴·구름·컴투스는
wp-json, 넥스트리는 `sitemap-posts.xml`(한국어만)을 탄다.

그룹2·4 collected 보강 결과(2026-09-14): 토스 20→93, 가비아 10→70,
한컴 10→24, 구름 12→21, 컴투스 29→44, 넥스트리 216→217.
업스테이지(날짜 없는 페이지), NDS(이미 wp-json과 동일), 아임웹(블로그 수명),
안랩·버즈빌·라포랩스 등(창이 닫힘)은 더 긁지 않았다.

보강 후 `classify_and_gate.py`를 다시 돌리고, HR·홍보·한영 중복은 수기로
걸렀다. Area 입력은 그룹2 402 + 그룹4 171 = 573건.
결과: `data/research/tech_blog_engineering_focus_29/group24_areas.md`.

## 출력

| 경로 | Git |
| --- | --- |
| `data/work/tech_blog_company_role_census/` | 제외 (본문 포함) |
| `data/research/tech_blog_company_role_census/summary.md` | 커밋 |
| `data/research/tech_blog_company_role_census/selected_companies.json` | 커밋 (게이트 통과 34곳) |
| `data/research/tech_blog_company_role_census/candidate_companies.json` | 커밋 (미확인 후보 16곳. pass가 아님) |
