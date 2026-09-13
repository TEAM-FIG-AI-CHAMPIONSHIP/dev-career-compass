# 6개 회사 embedding→clustering→Area 최종 결과 (#73)

census에서 이미 engineering_focus·Area까지 완료된 6개 회사(CJ올리브영·kt cloud·
라인플러스·컬리·NHN Cloud·우아한형제들)의 3~4단계(embedding→clustering→LLM Area
병합·명명→키워드 태깅) 결과를 확정한다.

## 재검증 방법

5개 회사(CJ올리브영·kt cloud·라인플러스·컬리·NHN Cloud)는 Track B 파일럿(#44) 때
이미 이 파이프라인을 돌렸다. 그 이후 날짜 복구(#69)·12개월 컷오프(#70) 등 수정이
있었으므로, 이번에 다시 계산한 게 아니라 **입력 데이터 자체가 그대로인지** 직접
비교해서 확인했다:

- `data/work/tech_blog_engineering_focus_29/articles.json`(현재)과
  `embeddings_v4/articles.json`(Track B 당시 임베딩 대상)의 5개 회사분 378건을
  title·engineering_focus 기준으로 전수 비교 → **차이 0건**
- embedding은 결정적 계산(같은 텍스트 → 같은 벡터)이라, 입력이 동일하면 clustering
  결과도 동일함이 보장된다.
- 따라서 stage 4(LLM Area 병합·명명)만 재실행 여부가 남는데, 클러스터 자체가
  안 바뀌었으므로 API 비용을 들여 다시 돌리지 않고 기존 Track B 결과를 그대로
  최종 확정하기로 함(팀 판단).

우아한형제들은 별도 파이프라인(F-02, `tech_blog_areas` 실험)으로 이미 완료·병합됨
(PR #28). 이번 재검증 대상이 아니라 기존 결과를 그대로 가져온다.

## 최종 집계

| 회사 | 기술글 수 | Area 수 | evidence 합 | unassigned |
|---|---:|---:|---:|---:|
| CJ올리브영 | 44 | 4 | 32 | 12 |
| NHN Cloud | 102 | 5 | 72 | 30 |
| kt cloud | 134 | 5 | 113 | 21 |
| 라인플러스 | 80 | 5 | 70 | 10 |
| 컬리 | 18 | 3 | 15 | 3 |
| 우아한형제들 / 배달의민족 | 42 | 5 | 36 | 6 |
| **합계** | **420** | **27** | **338** | **82** |

상세 Area별 키워드·근거 글 목록은 아래 파일 참고:

- CJ올리브영·kt cloud·라인플러스·컬리·NHN Cloud:
  `data/research/tech_blog_engineering_focus_29/track_b_pilot_areas.md`
- 우아한형제들: `data/research/tech_blog_areas/summary.md`

## 알려진 한계 (다음 단계 참고)

- API 경로(`extract_engineering_focus.py`)의 SYSTEM_PROMPT는 수동 프롬프팅
  경로와 달리 "이 글은 엔지니어링 내용이 없다"고 명시적으로 답하도록 지시하지
  않는다. 그 결과 CJ올리브영의 "한 끼의 점심이 협업 문화를 만든다면?" 같은
  비기술 콘텐츠가 그럴듯한 기술 요약으로 둔갑해 Area에 소량(1~5건 수준) 섞여
  들어간 것으로 확인됨 (예: CJ올리브영 "조직문화·협업 프로세스"/"사내 행사·워크숍
  (비-엔지니어링)" Area, kt cloud "AI 트렌드 및 조직 뉴스레터(비엔지니어링 성격)"
  Area).
- 이번 작업 범위에서는 고치지 않고 알려진 한계로 남긴다. 고치려면 SYSTEM_PROMPT에
  규칙 추가 + `FOCUS_VERSION` 상향으로 캐시 무효화 + 5개 회사 재추출(API 비용
  재발생)이 필요하다.
- `embed_v4.py`의 `LOW_SIGNAL_MARKERS`(`확인할 수 없음`/`판단할 수 없음`/
  `알 수 없음`)와 수동 프롬프팅 경로의 `NO_CONTENT_MARKERS`(`엔지니어링 내용이
  없음`/`기술적 내용 없음`)가 서로 다른 표현 집합이라는 것도 이번에 확인함 —
  통합하면 더 견고해지지만 이번 이슈 범위에서는 보류.
