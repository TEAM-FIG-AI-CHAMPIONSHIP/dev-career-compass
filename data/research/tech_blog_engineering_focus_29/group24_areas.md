# group24_areas: 16개 회사 Area 생성 결과 (수동 프롬프팅)

engineering_focus -> v4 embedding -> clustering(complete linkage) -> LLM 병합 -> deterministic membership -> 키워드 태깅 전체 파이프라인을 16개 회사에 독립적으로 적용한 결과다 (LLM 두 단계는 claude.ai 수동 프롬프팅으로 수행).

그룹2 8곳 + 그룹4 8곳. 수기 필터 후 **573건** 중 evidence **456건**, unassigned **117건**.

각 Area는 안정적인 `id`(예: `gabia-01`)를 갖는다. 스키마와 한계는
`../../../pipeline/experiments/tech_blog_engineering_focus_29/config/README.md` 참고.
직무 4개(서버·백엔드 / 웹 프론트엔드 / 모바일 / 데이터·AI)는 Area 이름이 아니라
`roles`다. Area 이름은 회사별 기술 주제다.

## 알려진 한계

RSS 상한으로 창이 짧았던 곳을 보강한 뒤, 수기 필터 → 임베딩 → Area를
다시 돌린 결과다 (2026-09-14). census `roles`는 키워드 1차 게이트라 오탐이
있을 수 있다. LLM이 직무를 다시 판단하지 않았다. 홍보성·HR·세션 참관기는
수기로 걸렀고, 제목에 해커톤·후기가 있어도 시스템을 만든 글은 남겼다.

### collected 보강 → 수기 필터 (그룹2)

건수는 `data/work/tech_blog_company_role_census/collected/articles.json`
→ `data/work/tech_blog_engineering_focus_29/articles.json` 기준.

| 회사 | collected | Area 입력 | 창·방법 | 수기에서 뺀 것 |
|---|---:|---:|---|---|
| 토스 | 93 | **56** | Wayback CDX `toss.tech/article/*` + 라이브 `publishedTime`. sitemap 404 | 브랜드·디자인 직무·TPM 에세이, 한영 중복 |
| 가비아 | 70 | **21** | wp-json. 2025-10-02 ~ 2026-09-14 | HR·법정의무교육·제품소개·행사 후기 |
| 한컴 | 24 | **20** | wp-json. 12개월 닫힘 | 페스티벌·테크세미나 운영기, AI 규제·트렌드 에세이 |
| 구름 | 21 | **21** | wp-json. 행사/VOD가 대부분 | 기존과 같이 행사/VOD 유지 |
| 컴투스 | 44 | **29** | wp-json `categories=13`(Tech) | 게임 홍보, 오픈AI 개최 보도, 참관기 |
| 넥스트리 | 217 | **210** | `sitemap-posts.xml` 한국어. 12개월 +1 | 신규 7건은 비기술 |

업스테이지(날짜 없는 페이지 207건), NDS(wp-json=수집과 동일), 아임웹(블로그
수명 ~7개월), 안랩·버즈빌·라포랩스 등(창이 닫힘)은 더 긁지 않았다.

넥스트리 unassigned 64/210은 글이 넓게 퍼져 membership 임계를 못 넘긴 몫이다.
토스 unassigned 16/56도 레거시 개편·QA·지표가 한 Area에 안 붙는 글이 있다.

한컴은 재클러스터 이후에도 이전 merge 응답이 남아 있어 cluster_rank가
문서 포맷↔에이전틱으로 뒤집혀 있었다. 새 3개 cluster 기준으로 merge/tag를
다시 맞춰 Area를 냈다.

## LG AI연구원 (17개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 파운데이션 모델 및 멀티모달 AI 개발 | 7 | EXAONE, 멀티모달, MoE(Mixture-of-Experts), AGAPO 강화학습, Vision Language Model, 멀티 에이전트 파이프라인, 구조적 인과모형(SCM), spatial biology |
| 도메인 특화 예측 모델링 | 1 | 하이브리드 예측 시스템, 인과맵, 도메인 시뮬레이터, 설명 가능한 예측, 중장기 가격 예측 |
| Agentic AI 기반 산업 자동화 시스템 | 4 | Agentic AI, Tool Orchestration, On-Premise 경량화, MAPPO/QMIX, MC Dropout, 지식그래프(Ontology), Red Team 시뮬레이션 |
| LLM 알고리즘 및 서빙 인프라 연구 | 4 | Text-to-SQL, RAG(검색증강생성), 토픽 모델링, Mixture-Of-Experts(MoE) Upcycling, Spherical K-means, GPU Job 스케줄링, Argo Workflows |

unassigned: 1

## 가비아 (21개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AI/클라우드 인프라 자원 운영 | 11 | GPU, VDI, DaaS, 액체 냉각, PUE, AWS Config, RTO/RPO, API Gateway |
| 보안 위협 탐지 및 인증·정책 대응 | 4 | SAST/DAST, AWS Security Agent, SSL 인증서, 침투 테스트, WHOIS, ICANN RDP, 침해사고 탐지 |
| 하이웍스 API·AI채팅 연동 자동화 | 5 | 하이웍스 API, 하이웍스 AI채팅, 전자세금계산서, 홈택스, RAG, 전자서명, ChatGPT·Gemini·Claude |

unassigned: 1

## 구름 (21개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 기술 스택·아키텍처 선택과 RAG 검색 품질 문제 | 3 | MSA, 모놀리식 아키텍처, RAG, 하이브리드 검색, 리랭킹, Graph RAG, 청킹 전략, Node.js |
| AI 코딩 도구 및 개발 워크플로우 자동화 | 10 | Claude Code, MCP, 바이브코딩, n8n, TDD, 스펙 주도 개발, DDD, 코드 리뷰 |
| 제품 기획 프로세스 | 3 | 글로벌 제품 기획, 스토리보드, 기획 프로세스, 기획 조직 구축, 사용자 시나리오 |

unassigned: 5

## 넥스트리 (210개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 백엔드 기능 구현 및 시스템 안정성 트러블슈팅 | 56 | OOMKilled, Java 25 StructuredTaskScope, MSA, Outbox Pattern, CQRS, WebSocket/STOMP, Spring WebClient, 전략 패턴 |
| 프론트엔드 아키텍처, 디자인 시스템 및 모바일/폼 상태관리 | 47 | React Hook Form, React Query, 디자인 토큰, Micro-Frontend, Keycloakify, React Native, Monorepo, Figma Variables |
| 요구사항 정의 및 품질관리 프로세스 | 10 | 화면 설계서, 통합테스트 시나리오, Git 브랜치 전략, CI 게이트, IA, PMO, 프롬프트 엔지니어링 |
| AI 에이전트 기반 개발 워크플로우 및 도구 활용 | 21 | Claude Code, MCP, Multi-Agent Workflow, Context Window, CLAUDE.md, Codex, AGENTS.md |
| 인프라 운영 안정성 및 데이터 파이프라인 관리 | 12 | NATS JetStream, Flyway, KubeEdge, ROS2, MQTT, InfluxDB, 테이블 파티셔닝 |

unassigned: 64

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

## 비바리퍼블리카 / 토스 (56개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 레거시 시스템 재설계와 AI/LLM 엔지니어링 적용 | 13 | LLM 서빙, 레거시 결제 시스템 재설계, es-toolkit, 컨텍스트 엔지니어링, Preview Runtime, 양자내성암호, TDS 컬러 토큰 시스템, commons-ml-model |
| SDK·API 연동 생태계와 QA 플랫폼 구축 | 12 | 토션(Tossion), Toss Front SDK, Open API 생태계, 디바이스 팜(네뷸라), MRAID, Web Worker, Spring AI, PR 위험도 분석 |
| 보안·테스트 자동화와 데이터 기반 실험 | 6 | 제로트러스트, 페이스페이, FedLPA, E2E 자동화, A/B 테스트, 암호화 트래픽 분석 |
| 인프라 운영과 대규모 설정 관리 | 6 | StarRocks, Resource Group, 하이브리드 클라우드, App Router, JVM 설정 관리, 레거시 정산 시스템 |
| 비즈니스 지표 설계와 데이터 리터러시 | 3 | Metric Review, BC Monthly Report, MTVi |

unassigned: 16

## 삼성 (22개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 신뢰 가능한 에이전틱 AI 시스템 설계 | 11 | RAG, LangGraph, 멀티 에이전트 아키텍처, 환각 차단, NL2SQL, QLoRA, 포트-어댑터 아키텍처, AUTOPILOT 루프 |
| 통신·미디어 신호처리 AI 최적화 | 6 | 5G vRAN, SIMD, JSCM, APV 코덱, GNN, Digital Twin, Diffusion 모델, On-Site Training |
| 자율 진단 및 복구 시스템 엔지니어링 | 2 | Expert-In-The-Loop, Self-Healing, BLE, mDNS, OCF Layer 3, Calm Connection Care |

unassigned: 3

## 아임웹 (26개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 데이터베이스/캐시 성능 및 동시성 최적화 | 4 | History List Length, InnoDB MVCC, Repeatable Read, Online DDL, 메타데이터 잠금, Aurora, Kafka, K6 부하 테스트 |
| AI 에이전트 기반 운영 자동화 | 12 | Multi-Agent, Hybrid RAG, CLAUDE.md, AST 파서, Slack Socket Mode, Testcontainers, OAuth 최소 스코프, Knowledge DB |
| 인프라 안정성 및 배포 신뢰성 개선 | 6 | VPC Lattice, EKS, Karpenter, Golden Image, CodeDeploy, Transit Gateway, Valkey, APM 트레이스 |

unassigned: 4

## 안랩클라우드메이트 (9개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AI 에이전트 기반 데이터 인프라 관리 및 검색 시스템 | 4 | MCP 서버, S3 Tables, Amazon MSK, RAG, Cosine Similarity, Amazon Q Developer CLI, approval_required |
| 인프라 장애 진단 및 보안 취약점 분석 | 2 | CVE, React Flight Protocol, ALB, Health Check Logs, DoS 취약점, S3 gzip 로그 |
| 서비스 성능 최적화 및 배포 안정화 | 3 | 커넥션 풀, 블루/그린 배포, HTTP/3, QUIC, 복합 인덱스, ECR, Netty |

unassigned: 0

## 업스테이지 (21개 글)

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

## 컴투스 (29개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 게임 데이터 애널리틱스 플랫폼(Hive 애널리틱스) | 13 | Hive 애널리틱스, 퍼널 분석, 기간 비교, 통화 환산, 지표 필터, BigQuery SQL, PG 결제 연동 |
| 백엔드 인프라·시스템 엔지니어링 | 10 | eBPF, Kubernetes, InnoDB Cluster, GitOps, Linux epoll, WebRTC, PHP-FPM, Zend Memory Manager |
| 행사·커뮤니티 소개성 콘텐츠 | 4 | IMAGINE 2026, OWASP, Tableau DataFest 2025, AI MeetUP, 바이브코딩, 생성형AI |

unassigned: 2

## 한컴 (20개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| Agentic AI 하네스 및 조합형 모델 설계 | 5 | LLM-as-judge, Planner–Caller–Generator, OpenClaw, MoltBook, KoBART, SLM/LLM 위임, VLM |
| 문서 파일 포맷 파싱과 한글 오픈소스 | 5 | OLE2, FIB, OOXML, HWPX, HWP, PlcPcd, CharShape |
| AI 코딩 하네스·테스트와 프론트/워크플로 도구 | 6 | 하네스 엔지니어링, CLAUDE.md, MCP, Vue3, @DisplayName, Health Check, JIT 전략 |

unassigned: 4
