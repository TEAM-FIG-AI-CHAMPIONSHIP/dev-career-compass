# 집계

재수집 뒤 보고서를 맞출 때 이 순서로 돌립니다. 스펙 키워드(`JOB_KEYWORDS`)는 바꾸지 않습니다.

```bash
python3 scripts/build_keyword_audit.py
python3 scripts/step6_aggregate.py
```

| 명령 | 산출 |
|---|---|
| `build_keyword_audit.py` | `data/research/job_postings/keyword_audit.md` |
| `step6_aggregate.py` | `data/research/job_postings/step6_summary.md`, `step6_summary.json` |

## STEP 6 잠정 규칙

`step6_aggregate.py` 상단과 `data/research/job_postings/step6_summary.md`에 그대로 적혀 있습니다. raw는 수정하지 않습니다.

1. 카카오: `company_id == kakao` 이면서 `group == 카카오`만 카카오 몫. 관계사는 제외. 페이·모빌리티는 그리팅 raw가 대표.
2. occupation 오염: `OCCUPATION_BLEED_VERDICT == 무관`만 「오염 제외」에서 미분류. 쏘카 `개발/데이터`, 컬리 `인프라`.
3. 저물량: 진행 중 < 10건 또는 분류 ≤ 2건.
4. S5 게이트: 직무별 회사 수 3곳 이상.

팀 결정을 바꾸면 스크립트 규칙만 고치고 위 두 명령을 다시 실행합니다.

미결정 항목은 `data/research/job_postings/team_decisions_needed.md`입니다. 자동 생성하지 않습니다.

## 분류 진단 (선택)

키워드를 넓히면 몇 건이 더 잡히는지 볼 때:

```bash
python3 scripts/diagnose_classification.py
```

`job_classifier.py`는 수정하지 않습니다. 화면에만 출력합니다.
