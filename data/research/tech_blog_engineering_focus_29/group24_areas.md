# group24_areas: 16개 회사 Area 생성 결과 (수동 프롬프팅)

engineering_focus -> v4 embedding -> clustering(complete linkage) -> LLM 병합 -> deterministic membership -> 키워드 태깅 전체 파이프라인을 16개 회사에 독립적으로 적용한 결과다 (LLM 두 단계는 claude.ai 수동 프롬프팅으로 수행).

그룹2 8곳 + 그룹4 8곳. 수기 필터 후 491건 중 evidence 402건, unassigned 89건.

각 Area는 안정적인 `id`(예: `gabia-01`)를 갖는다. 스키마와 한계는
`../../../pipeline/experiments/tech_blog_engineering_focus_29/config/README.md` 참고.
직무 4개(서버·백엔드 / 웹 프론트엔드 / 모바일 / 데이터·AI)는 Area 이름이 아니라
`roles`다. Area 이름은 회사별 기술 주제다.

## 알려진 한계

16곳을 수집 창·건수로 다시 보면, "12개월 미달"로 묶어 쓸 수 있는 회사는 없다.
짧은 창의 이유는 RSS 상한, 날짜 없는 글, 블로그 수명, 수기 필터가 섞여 있다.

RSS 항목 수 상한 (증상은 당근과 같고, 원인은 다름):
- 토스: RSS 20건 상한, sitemap 404. 2026-06-23 ~ 09-09(약 2.5개월) 20건.
  자체 호스팅(Next.js). 온사이트 목록 아카이브는 돌렸으나 날짜 없는 후보 83건을
  못 넣어 0건 추가. archive.org Wayback은 별도로 안 했다.
- 가비아: RSS 10건 상한, sitemap 없음. 2026-08-07 ~ 09-08(약 1개월) 10건.
  그중 HR·행사·멘토링 후기를 걸러 기술글 4건. 글이 적어서가 아니다.
  자체 호스팅(워드프레스 계열). 온사이트 아카이브 추가 0건. Wayback은 안 했다.
- 한컴: RSS가 정확히 10건. 2025-12-24 ~ 2026-08-26(약 8개월). WP 기본 10건
  상한일 수 있으나, 게시 빈도가 낮아 10건이 8개월을 덮는 형태다. cutoff 대비
  앞쪽 약 3개월은 비어 있다.

사이트 목록 아카이브로 RSS를 보강한 곳:
- 넥스트리: RSS는 15건(2026-09만)이었다. rel_next 아카이브로 201건을 더해
  216건, 2026-04-06 ~ 09-14(약 5.3개월). 12개월은 닫지 못했다. Area
  unassigned 57/210.
- 컴투스: RSS 10건(9월) → 아카이브 +19 → 29건, 약 11.5개월. 수기 필터 후 20건.
- 농심데이터시스템(NDS): RSS 10건 → 아카이브 +22 → 32건, 약 10.6개월.
  세션 참관기를 걸러 14건.

그 외:
- 업스테이지: classified 245건 중 날짜 없음 207건. Area는 날짜 있는 21건만.
  제목이 `upstage.ai`인 글이 다수다.
- 구름: 12건 전부 행사/VOD(`[오프라인/마감]`). 2025-11-11 ~ 2026-05-15
  (약 6개월) 이후 글이 없다.
- 아임웹: 2026-01-26부터(새 기술블로그). 28건·약 7개월. RSS 10/20 상한이 아니라
  블로그 수명에 가깝다. 수기 필터 후 26건.
- 안랩클라우드메이트: 12건 중 월간소식·AWS 기능소개 3건을 제외하면 남은 9건이
  2025-12 ~ 2026-03에 몰려 있다.
- 라포랩스 / 퀸, LG AI연구원, 마이리얼트립, 카카오클라우드, 삼성, 버즈빌은
  12개월 창이 대체로 닫혀 있다 (버즈빌만 cutoff 대비 앞쪽 약 47일 공백).

census `roles`는 키워드 1차 게이트라 오탐이 있을 수 있다. LLM이 직무를 다시
판단하지 않았다. 홍보성·HR·세션 참관기 등은 수기로 1차 걸렀고, 제목에
해커톤·후기가 있어도 시스템을 만든 글은 남겼다.

## LG AI연구원 (17개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 파운데이션 모델 및 멀티모달 AI 개발 | 7 | EXAONE, 멀티모달, MoE(Mixture-of-Experts), AGAPO 강화학습, Vision Language Model, 멀티 에이전트 파이프라인, 구조적 인과모형(SCM), spatial biology |
| 도메인 특화 예측 모델링 | 1 | 하이브리드 예측 시스템, 인과맵, 도메인 시뮬레이터, 설명 가능한 예측, 중장기 가격 예측 |
| Agentic AI 기반 산업 자동화 시스템 | 4 | Agentic AI, Tool Orchestration, On-Premise 경량화, MAPPO/QMIX, MC Dropout, 지식그래프(Ontology), Red Team 시뮬레이션 |
| LLM 알고리즘 및 서빙 인프라 연구 | 4 | Text-to-SQL, RAG(검색증강생성), 토픽 모델링, Mixture-Of-Experts(MoE) Upcycling, Spherical K-means, GPU Job 스케줄링, Argo Workflows |

unassigned: 1

## 가비아 (4개 글)

RSS 10건 상한, 수집 기간 약 1개월(2026-08-07 ~ 2026-09-08). 그 10건 중
HR·행사글을 걸러 기술글 4건이다. 글 수가 적어서가 아니라 RSS 상한 창이 짧다.

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 외부 API 연동 기반 업무 자동화 | 2 | 하이웍스 API, 전자세금계산서 발행, 계좌 거래내역 조회, 전자서명, 국세청 전송, 홈택스 |
| 데이터센터 전력 및 냉각 인프라 | 1 | GPU 추론, 랙당 전력밀도, 액체 냉각, 공기 냉각, 서버 배정 |
| AI 기반 보안 자동화 | 1 | SAST, DAST, 침투 테스트, 프론티어 AI 에이전트, 엔드포인트 정찰, 다단계 공격 시나리오 |

unassigned: 0

## 구름 (12개 글)

12건 전부 행사/VOD. 2025-11-11 ~ 2026-05-15(약 6개월) 이후 글 없음.

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AI 활용 개발 환경 구축과 서비스 아키텍처 의사결정 | 4 | MoAI-ADK, TDD Red-Green-Refactor, Claude Code, MSA, RAG, 하이브리드 검색, 리랭킹, Graph RAG |
| 노코드·AI 워크플로우 자동화 | 4 | Claude Cowork, MCP, 바이브코딩, n8n, Why-What-How, 프로덕트 엔지니어 |
| AI 시대 개발 판단 기준과 품질 검증 | 4 | 인지 부채, 코드 리뷰 승인·반려 기준, 비결정적 출력, QA, 최적해 설계, 사고력과 문해력 |

unassigned: 0

## 넥스트리 (210개 글)

RSS 15건(2026-09)에서 사이트 목록 아카이브로 보강해 216건.
창은 2026-04-06 ~ 09-14(약 5.3개월)이다.

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 프론트엔드 아키텍처 및 모바일 개발 | 45 | React Native, React Query, React Hook Form, 디자인 토큰, Micro Frontend, Module Federation, WebView |
| 분산 시스템 데이터 정합성 및 인증 아키텍처 | 23 | Keycloak, Outbox Pattern, Flyway, Debezium, CQRS, FHIR R4, RBAC |
| 백엔드 성능 최적화 및 인프라 안정성 | 48 | OOMKilled, Kubernetes, Kafka, NATS JetStream, StructuredTaskScope, GraalVM Native, SXSSF, MQTT |
| AI 에이전트·LLM 기반 개발 생산성 | 26 | Claude Code, MCP, Multi-Agent Workflow, Context Window, Task/Plan Harness, Structured Concurrency, AGENTS.md |
| 요구사항 정의, QA 및 프로젝트 관리 | 11 | IA, PMO, 통합테스트 시나리오, CCB, CI 게이트, 프롬프트 설계, WBS |

unassigned: 57

## 농심데이터시스템(NDS) (14개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AWS 클라우드 인프라 아키텍처 설계 및 운영 | 7 | Amazon Bedrock, EKS, IAM, CloudWatch, EBS, AWS Backup, Terraform, IRSA |
| AWS 네트워크 아키텍처 설계 | 1 | Direct Connect Gateway, Transit Gateway, VPC Attachment, 라우팅, 멀티계정 온프레미스 통신 |
| S3 스토리지 운영 및 비용 최적화 | 6 | S3 Lifecycle, S3 Batch Operations, AWS Amplify, Route 53, IAM Role, 버킷 정책, 교차계정 리전 간 복제 |

unassigned: 0

## 라포랩스 / 퀸 (24개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AI 기반 업무 자동화 및 개발 생산성 도구 | 11 | MCP, Google Apps Script, Playwright, OpenAI API, BigQuery, AI 이미지 생성, AI 프롬프트 자동화 |
| 실험 기반 문제 재정의와 추천시스템 최적화 | 4 | Item-based CF, Reranking, Realtime Action Encoder, Candidate×Sequence Early Fusion, recency bias 완화, ad_tag 기반 세션 추천, catalog coverage |
| 백엔드 인프라 성능 및 검색 최적화 | 6 | StarRocks, Colocate Join, Elasticsearch, RRF(Reciprocal Rank Fusion), EntityManagerFactory, Async Profiler, Tanstack Query, Next.js SSR |

unassigned: 3

## 마이리얼트립 (47개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AI 에이전트 기반 사내 업무 자동화 | 15 | Claude Code, Cursor, OCR, n8n, Lovable, 서브에이전트, Figma 플러그인 |
| 여행 데이터·서비스 실시간 연동 및 신뢰성 엔지니어링 | 18 | MCP, Cirium, mirrord, 셀프힐링 로케이터, Fact-First 워크플로우, Redis/Celery, On-Demand 요약, Live Activities |
| AI 코딩 워크플로우 및 개발 방법론 고도화 | 5 | Vibe Coding, Spec Driven Development, Harness Engineering, 3-Layer Context, 멀티 에이전트, TDD, agent.md |

unassigned: 9

## 버즈빌 (14개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AI 에이전트 기반 디자인 시스템 | 4 | ComponentManifest, 디자인 토큰, Figma Dev Mode, MCP, Claude, PR 검증 파이프라인, 커밋 전 검증 훅 |
| 개발 플랫폼 운영 및 백엔드 아키텍처 | 3 | Feature Flag, go-feature-flag, AsyncExporter, Turborepo, Kafka, Argo Workflow, JDBC Source/Sink Connector, Test in Production |
| 인프라 성능 최적화 및 비용 절감 | 4 | DynamoDB, Redis, guregu/dynamo, AWS SDK v2, Pyroscope, Radix Tree, Eventually Consistent Read, pip 캐싱 |

unassigned: 3

## 비바리퍼블리카 / 토스 (20개 글)

RSS 20건 상한 + sitemap 404. 2026-06-23 ~ 09-09(약 2.5개월).
온사이트 아카이브는 날짜 없는 후보 83건을 못 넣어 0건 추가.
당근과 증상(RSS 상한)은 같고 원인(자체 호스팅 vs Cloudflare)은 다르다.

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 사내 개발 플랫폼 및 프론트엔드 엔지니어링 | 5 | Mr. Park, Sillokbot, esbuild-wasm, Nebula Driver, ADB/XCTest, 토션(Tossion), scrcpy |
| 프론트엔드 모노리포 의존성 관리 | 1 | 모노리포, Yarn PnP, 카탈로그(중앙 버전 참조), 버전 릴리즈·검증 프로세스, 의존성 파편화 |
| LLM 서비스 엔지니어링 | 10 | 그래프 RAG, Neo4j, vLLM/SGLang, TTFT, Stylepack, todoc, commons-ml-model, es-toolkit |

unassigned: 4

## 삼성 (22개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 신뢰 가능한 에이전틱 AI 시스템 설계 | 11 | RAG, LangGraph, 멀티 에이전트 아키텍처, 환각 차단, NL2SQL, QLoRA, 포트-어댑터 아키텍처, AUTOPILOT 루프 |
| 통신·미디어 신호처리 AI 최적화 | 6 | 5G vRAN, SIMD, JSCM, APV 코덱, GNN, Digital Twin, Diffusion 모델, On-Site Training |
| 자율 진단 및 복구 시스템 엔지니어링 | 2 | Expert-In-The-Loop, Self-Healing, BLE, mDNS, OCF Layer 3, Calm Connection Care |

unassigned: 3

## 아임웹 (26개 글)

2026-01-26부터의 새 기술블로그(28건, 약 7개월). RSS 10/20 상한이 아니다.

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 데이터베이스/캐시 성능 및 동시성 최적화 | 4 | History List Length, InnoDB MVCC, Repeatable Read, Online DDL, 메타데이터 잠금, Aurora, Kafka, K6 부하 테스트 |
| AI 에이전트 기반 운영 자동화 | 12 | Multi-Agent, Hybrid RAG, CLAUDE.md, AST 파서, Slack Socket Mode, Testcontainers, OAuth 최소 스코프, Knowledge DB |
| 인프라 안정성 및 배포 신뢰성 개선 | 6 | VPC Lattice, EKS, Karpenter, Golden Image, CodeDeploy, Transit Gateway, Valkey, APM 트레이스 |

unassigned: 4

## 안랩클라우드메이트 (9개 글)

월간소식 등을 제외한 9건이 2025-12 ~ 2026-03에 몰려 있다.

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AI 에이전트 기반 데이터 인프라 관리 및 검색 시스템 | 4 | MCP 서버, S3 Tables, Amazon MSK, RAG, Cosine Similarity, Amazon Q Developer CLI, approval_required |
| 인프라 장애 진단 및 보안 취약점 분석 | 2 | CVE, React Flight Protocol, ALB, Health Check Logs, DoS 취약점, S3 gzip 로그 |
| 서비스 성능 최적화 및 배포 안정화 | 3 | 커넥션 풀, 블루/그린 배포, HTTP/3, QUIC, 복합 인덱스, ECR, Netty |

unassigned: 0

## 업스테이지 (21개 글)

classified 245건 중 날짜 없음 207건. Area는 날짜 있는 21건만.

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 에이전틱 LLM 성능 개선 및 서빙 인프라 | 5 | MoE, SnapPO, Commitment Tiers, SWE Bench, Terminal Bench, 긴 컨텍스트, 모듈형 AI 아키텍처 |
| 산업별 비정형 문서 자동화 파이프라인 구축 | 6 | Upstage Studio, Classify, Extract, ACORD, Agentic IE, OCR, Validate |
| 언어모델 및 문서인식 AI 기술 개발 | 10 | Document Parse, Information Extract, Reasoning Mode, Reasoning Budget, SolarBox, Vision Language Action, Sim2Real, tool use |

unassigned: 0

## 카카오엔터프라이즈 / 카카오클라우드 (22개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 클라우드 보안 및 인프라 자동화(IaC) | 6 | SECaaS, Terraform Provider, 제로트러스트, Multi-AZ, OpenStack, RBAC, CSAP |
| 클라우드 인프라 비용·성능 최적화 | 12 | GPUaaS, Kubeflow, HPA, Transit Gateway(TGW), KMS, Object Storage, A100 GPU, MSA |
| 대규모 GPU 분산학습 인프라 | 2 | Blackwell B200, InfiniBand, NCCL, Fat-Tree, SHARP, Kubeflow |

unassigned: 2

## 컴투스 (20개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 게임 데이터 분석 플랫폼 기능 설계 | 4 | Hive 애널리틱스, 파이 차트, 퍼널, 리텐션, 통화 설정, 기간 비교 |
| 시스템 저수준 성능·안정성 엔지니어링 | 9 | eBPF, Cilium, InnoDB Cluster, Epoll, WebRTC, XDP, Zend Memory Manager, Helm Chart |
| 기술 외 콘텐츠(컨퍼런스·커뮤니티 참관기) | 5 | 바이브 코딩, AI MeetUp, 하네스 엔지니어링, IMAGINE 2026, OWASP, Tableau DataFest |

unassigned: 2

## 한컴 (9개 글)

RSS 정확히 10건, 2025-12-24 ~ 2026-08-26(약 8개월). 페스티벌 1건 제외.

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 문서 파일 포맷 구조 분석 | 2 | OLE2, FIB, PlcPcd, OOXML, document.xml, Twip, numbering 구조 |
| LLM 기반 개발 방법론 및 신뢰성 검증 설계 | 4 | 하네스 엔지니어링, LLM-as-judge, 결정론적 검사, 테스트 코드, @DisplayName, KoBART, 하이브리드 파이프라인 |
| 에이전틱 AI 생태계 및 MCP 연동 동향 | 2 | MCP, OpenClaw, MoltBook, SLM/LLM 위임, Terraform, Hugging Face, MongoDB |

unassigned: 1
