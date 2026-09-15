# Area × 공고 매칭

확정 Area의 `area_name` 토큰과 채용 공고 제목·직무 필드가 겹치는 건을 붙인다.
Area JSON은 읽기만 하고 이름·keywords를 바꾸지 않는다.

`tech_blog_engineering_focus_29`는 Area 원본 실험이다. `_29`는 그 실험을
시작했을 때 게이트 통과가 29곳이었다는 뜻이고, 이 매칭은 census 통과 34곳에서
구름을 뺀 **33곳**이다.

## 입력과 출력

| 종류 | 위치 | Git |
| --- | --- | --- |
| Area 원본 | `data/research/tech_blog_engineering_focus_29/`, `data/research/tech_blog_areas/` | 커밋 (읽기 전용) |
| 공고 processed | `data/work/job_postings/processed/` | 제외 |
| 회사 JSON | `data/research/area_postings_match/json/` | 커밋 |
| 회사 MD | `data/research/area_postings_match/md/` | 커밋 |

## 실행

```bash
cd pipeline/experiments/area_postings_match
python3 scripts/match_postings_to_areas.py
```

한 회사만:

```bash
python3 scripts/match_postings_to_areas.py --company 여기어때
```
