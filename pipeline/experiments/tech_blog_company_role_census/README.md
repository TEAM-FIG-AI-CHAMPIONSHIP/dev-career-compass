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
python pipeline/experiments/tech_blog_company_role_census/scripts/extract.py
python pipeline/experiments/tech_blog_company_role_census/scripts/classify_and_gate.py
```

수집은 회사 단위로 저장하므로 중간에 멈춰도 이어서 돈다.

## 출력

| 경로 | Git |
| --- | --- |
| `data/work/tech_blog_company_role_census/` | 제외 (본문 포함) |
| `data/research/tech_blog_company_role_census/summary.md` | 커밋 |
| `data/research/tech_blog_company_role_census/selected_companies.json` | 커밋 (게이트 통과 34곳) |
| `data/research/tech_blog_company_role_census/candidate_companies.json` | 커밋 (미확인 후보 16곳. pass가 아님) |
