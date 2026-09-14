# 기술블로그 기반 Area 추출 실험 (F-02)

테스트 기업 1곳(우아한형제들)을 대상으로 기술블로그 게시글에서
사전 정의 없이 반복되는 기술 영역(Area) 후보를 뽑을 수 있는지 확인한 실험이다.
스크립트는 `pipeline/experiments/tech_blog_areas/scripts`에 있고,
실행 결과 데이터는 정책상 `data/work/`(git 제외)에 둔다.

Area·evidence마다 직무(roles) 정보를 추가한 기계 판독용 결과는
`data/research/tech_blog_areas/final_areas_with_roles.json`에 있다
(#80 — census가 계산해 둔 article 단위 roles를 그대로 재사용해 집계,
새로 판단하지 않음).

## 데이터 범위

- 대상 기업: 우아한형제들 1곳
- 수집: RSS 기준 53개, 게시일 2025-09-17 ~ 2026-09-08 (약 12개월)
- 기술 관련성 분류 후 Area 생성 대상: 42개 (11개는 홍보성/비기술로 제외)

## 파이프라인

```
수집(53) → 본문추출(53) → 기술관련성분류(42)
→ engineering_focus v2 추출 (본문 앞/중간/뒤 발췌 요약, LLM)
→ v4 임베딩 (title 30% + engineering_focus 70%, multilingual-e5-small)
→ Agglomerative clustering (cosine, complete linkage) → raw cluster 8개
→ LLM이 raw cluster를 최종 Area 3~5개로 병합·명명
→ 임베딩 기반 article-to-area deterministic 재매칭
  (evidence count는 LLM이 아니라 cosine 유사도 threshold+margin으로 결정)
→ Area별 대표 키워드 태그 추출 + 원문 대조 검증(grounding)
```

## 결과

최종 Area 5개, evidence 36개 + unassigned 6개 (총 42개).

| Area | 게시글 수 | 대표 키워드 |
|---|---:|---|
| AI·LLM 서비스 개발 및 플랫폼화 | 11 | RAG, MCP, Langfuse, LLMOps, SSE, LiteLLM, ESLint, 컨텍스트 엔지니어링 |
| 백엔드 인프라·시스템 안정성 | 9 | Redis, Kafka, SSE, KEDA, Lettuce, FinOps, @CacheEvict, MTTD |
| 클라이언트·프론트엔드 아키텍처 | 6 | 플로팅웹뷰, CloudFront Function, Flutter, Clean Architecture, Chrome DevTools Protocol, Vite, Lambda@Edge |
| 데이터·추천·실험 기반 프로덕트 개선 | 5 | Item2Vec, ELECTRA, A/B 테스트, RAG, Transformer, 컨텍스트 엔지니어링 |
| 개발 프로세스·품질 자동화 | 5 | ArchUnit, FreezingArchRule, Jira Automation, NACL, Flowkit, IntelliJ 플러그인 |
| unassigned | 6 | — |

evidence count 산출 기준: 각 게시글의 v4 임베딩과 Area 이름+설명 임베딩 간
cosine 유사도를 계산해, `best_similarity >= 0.86` **그리고**
`(1위-2위 유사도 격차) >= 0.0032`를 모두 만족할 때만 해당 Area의 근거로 인정한다.
두 조건 중 하나라도 미달이면 특정 Area로 강제 배정하지 않고 unassigned 처리한다.
계산은 `match_articles_to_areas.py`(순수 Python + 임베딩 코사인 유사도)로 수행하며
LLM은 이 카운팅 단계에 관여하지 않는다.

## 한계

- **단일 기업 검증**: 우아한형제들 1곳만으로 확인했다. 다른 기업, 다른 게시글 수(예: 10개
  미만 소량 기업)에서도 같은 threshold(0.86)·margin(0.0032) 값이 유효한지는 확인되지 않았다.
  이 값들은 이번 42개 데이터의 유사도 분포에서 자연스러운 간격을 찾아 정한 것이라
  기업이 바뀌면 재보정이 필요할 가능성이 높다.
- **unassigned 비율**: 6/42 (약 14%)가 어느 Area에도 확신 있게 배정되지 못했다. 그중 일부
  (카카오톡 바코드 연동, 접근성 개선, 디버깅 툴 2부)는 5개 Area 전부에 대해 유사도 격차가
  0.002 이하로 사실상 구분이 안 되는 경우였다.
- **경계 케이스**: "Flowkit 워크플로 엔진" 게시글은 내용상 백엔드 시스템 설계에 가깝다고
  볼 수도 있으나 실제로는 "개발 프로세스·품질 자동화" Area로 배정됐다. Area 설명 문구에
  "워크플로우 자동화"가 포함되어 있어 근거가 없는 배정은 아니지만, 사람이 보기엔 다른
  카테고리가 더 자연스러울 수 있는 경계 사례로 남아 있다.
- **초기 임베딩 표현의 한계**: engineering_focus 문장 전체를 그대로 임베딩했을 때는
  "AI/LLM"이라는 표면 주제로 서로 다른 엔지니어링 문제(번역 자동화, RAG, 컨텍스트
  엔지니어링 등)가 지나치게 뭉치는 경향이 있었다. title 30% + engineering_focus 70%
  가중 임베딩(v4)으로 완화했지만, "AI·LLM" Area(11개)의 내부 다양성이 여전히
  다른 Area보다 크다.
- **자동화 테스트 없음**: 파이프라인 일회성 실험 스크립트라 unit test는 작성하지 않았다.
  각 단계는 콘솔 출력으로 수동 확인했다.

## 다음 단계

- 뉴스, 채용 공고를 이번에 도출된 Area 5개에 attach하는 단계로 진행
- 다른 기업 1~2곳에 같은 파이프라인을 적용해 threshold·margin 값이 재사용 가능한지 확인
- 반복 검증되면 `pipeline/experiments/tech_blog_areas`의 로직을
  `pipeline/src/career_compass_pipeline`으로 이관
