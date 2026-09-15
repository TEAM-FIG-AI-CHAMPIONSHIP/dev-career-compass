# group1_areas: 그룹1 회사 Area 생성 결과 (수동 프롬프팅, 진행 중)

engineering_focus -> v4 embedding -> clustering(complete linkage) -> LLM 병합 -> deterministic membership -> 키워드 태깅 전체 파이프라인을 그룹1(#58) 회사에 독립적으로 적용한 결과다 (LLM 두 단계는 claude.ai 수동 프롬프팅으로 수행).

그룹1은 삼성반도체·여기어때·쏘카·카카오 4곳이다. 이 파일은 완료된 회사만
담는다 — 현재 쏘카·카카오·삼성반도체 3곳 완료, 여기어때는 engineering_focus
단계(#58)가 아직 안 끝나서 Area 대상이 아니다(사이트가 Cloudflare로
막혀 있어 수기로 확보 중).

각 Area는 안정적인 `id`(예: `socar-01`)를 갖는다. 스키마와 한계는
`../../../pipeline/experiments/tech_blog_engineering_focus_29/config/README.md` 참고.

## 알려진 한계

- 쏘카는 `tech.socar.kr/sitemap.xml`의 lastmod 기준으로 최근 12개월치를
  직접 재검증했다 — 9건이 실제로 전체 개수가 맞다(월 1회 정도 페이스,
  RSS 상한으로 인한 과소집계가 아님).
- 카카오는 census `tech_count: 73`과 초기 로컬 재수집(7건)이 크게 달라
  보였지만, 실제로는 census 쪽 82건 수집이 맞았고 로컬 재수집이
  과소집계였다(RSS 10건 상한). 최종 81건 중 71건은 engineering_focus로
  병합했고, 10건은 정당하게 제외했다 — 번역쌍 중복(영어판) 1건, 행사·
  모집공고·조직문화 같은 비기술 콘텐츠(모델이 "[기술적 내용 없음]"으로
  자체 판정) 9건.
- 카카오 Area 1("파운데이션 모델 학습·서빙과 AI 안전성")은 raw cluster가
  34건으로 응집도가 낮다고 merge rationale에 명시돼 있다 — 모델 개발 /
  AI 안전성 / AI 기반 개발 생산성 최소 3개로 나중에 분할하는 게 적절하다.
- 카카오는 unassigned가 18/71(25%)로 그룹1 중 가장 높다 — cluster 3
  ("개발자 대상 기술 공유와 문제 출제")이 행사 안내·모집 공고 같은 메타
  콘텐츠 위주라 응집도가 낮은 영향으로 보인다.
- 삼성반도체는 #58에 적혀 있던 "sitemap lastmod 383건이 전부 수집
  당일로 찍히는 버그성 데이터" 문제가 해결된 채로 전달됐다 — 최종
  41건의 발행일이 2025-10~2026-09로 정상 분포한다. census 키워드
  분류가 반도체 하드웨어 콘텐츠에도 backend/data-ai를 주로 매핑해서
  다른 소프트웨어 회사보다 역할 분포가 치우쳐 있다(#78에서 이미
  지적된 "census 키워드 분류 오탐 가능성" 범주에 속하는 사례로 보고,
  이번 작업에서 임의로 보정하지 않았다).
- 삼성반도체 Area 1("AI 인프라용 메모리·스토리지 아키텍처와 첨단
  패키징")도 raw cluster 33건으로 응집도가 낮다고 명시돼 있다 — 메모리
  제품 / 패키징·공정 / 시스템 인터페이스(CXL·NVMe) / 보안 / 소프트웨어
  툴체인 최소 4개로 나중에 분할하는 게 적절하다.

## 쏘카 (9개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 디자인 시스템과 크로스플랫폼 앱 프레임워크 설계 | 4 | Figma Code Connect, Slot 기반 합성 컴포넌트, 정책 객체 + Hook 어댑터, 트리쉐이킹 번들 구조, Figma Plugin 토큰 PR, BluetoothSpec / BluetoothHandle 분리 |
| 배포·종료 동작과 레거시 코드베이스 정리 | 3 | CloudFront invalidation 범위, ChunkLoadError, Graceful shutdown (SIGTERM), dumb-init (PID 1), terminationGracePeriodSeconds, 무중단 스키마 변경 절차 |
| LLM 에이전트의 판단 신뢰성 확보 | 2 | 지식 그래프 (Neo4j), 사람 정의 시드, LLM 신뢰도 점수 임계값, structured output 스키마, 안전한 기본값 폴백 |

unassigned: 0

## 카카오 (71개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 개발자 대상 기술 공유와 문제 출제 | 22 | Vibe Coding, Cursor / Claude Code, Cursor Rule·Claude Memory 룰셋, MCP / playMCP, 그래프 탐색 (DFS/BFS), 비트마스크 DP·단조 deque, Union-Find, 사람 주도 개발 (HDD) |
| 파운데이션 모델 학습·서빙과 AI 안전성 | 16 | MoE (Mixture of Experts), MLA (Multi-head Latent Attention), Pruning & Distillation, DPO / RLHF 정렬, vLLM continuous batching, Kanana Safeguard 가드레일, 한국어 벤치마크·데이터셋 (KoPDFBench, KoEmbed) |
| 서비스 백엔드·데이터 인프라 운영과 테스트 자동화 | 11 | Debezium CDC, Kafka Connect, Orchestrator HA, Single Writer Principle, Kubernetes Job + Helm, Locust 부하 테스트, LLM 기반 테스트 생성 (JUnit·Assertion), LLM Judge 회귀 검증 |
| PO/PM 교육 과정 설계 | 2 | 문제 정의-가설-지표-검증 루틴, 지표 기반 회고, 백로그 우선순위 결정, 만족도·중요도 매트릭스, 기회점수 기반 우선순위, 교육 과정의 제품화 |
| MySQL 데이터 타입 저장 구조 분석 | 2 | hexdump ibd 분석, JSON 타입 직렬화, TEXT 타입 무변환 저장, DATETIME Fraction Seconds, 바이너리 정렬 오프셋, TIMESTAMP UTC 변환, Y2K38 |

unassigned: 18

## 삼성반도체 (41개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AI 인프라용 메모리·스토리지 아키텍처와 첨단 패키징 | 21 | 3D 적층 (zHBM, zNAND-O), 하이브리드 구리 본딩 (HCB), CXL 메모리 풀링 (CMM-D), KV 캐시 오프로딩, V10 BV-NAND (400단 적층), HPB (Heat Path Block), DTCO (설계-공정 공동 최적화), SSD 하드웨어 가상화 (SR-IOV) |
| 모바일 SoC의 이미지센서·온디바이스 AI 연산 | 12 | DTI 구조 (DCC, FDTI), 픽셀 비닝·리모자이크, Arm SME2, VPS 카메라 AI 서브시스템, Exynos AI Studio (온디바이스 SDK), AI 업스케일링·프레임 생성 (ENSS), LPDDR6 저전력 DRAM |
| 반도체 분야 개방형 협업과 AI 연구 동향 공유 | 3 | HBM4 / HBM4E, SOCAMM2, CMM-D / CXL 메모리 풀링, CMX (Context Memory eXtension), AI-EDA, 에이전틱 AI 제조 이상탐지, Virtual SSD Migration·FDP |

unassigned: 5
