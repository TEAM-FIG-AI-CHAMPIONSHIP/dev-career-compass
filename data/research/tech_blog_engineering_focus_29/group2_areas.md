# group2_areas: 8개 회사 Area 생성 결과 (수동 프롬프팅)

engineering_focus -> v4 embedding -> clustering(complete linkage) -> LLM 병합 -> deterministic membership -> 키워드 태깅 전체 파이프라인을 8개 회사에 독립적으로 적용한 결과다 (LLM 두 단계는 claude.ai 수동 프롬프팅으로 수행).

그룹2 8곳. 수기 필터 후 **402건** 중 evidence **308건**, unassigned **94건**.

각 Area는 안정적인 `id`(예: `gabia-01`)를 갖는다. 스키마와 한계는
`../../../pipeline/experiments/tech_blog_engineering_focus_29/config/README.md` 참고.
직무 4개(서버·백엔드 / 웹 프론트엔드 / 모바일 / 데이터·AI)는 Area 이름이 아니라
`roles`다. Area 이름은 회사별 기술 주제다.

예전에는 그룹4와 묶어 `group24_areas`로 두었다. 지금은 그룹2만 이 파일에 둔다.

## 알려진 한계

RSS 상한으로 창이 짧았던 곳을 보강한 뒤, 수기 필터 → 임베딩 → Area를
다시 돌린 결과다 (2026-09-14). census `roles`는 키워드 1차 게이트라 오탐이
있을 수 있다. LLM이 직무를 다시 판단하지 않았다. 홍보성·HR·세션 참관기는
수기로 걸렀고, 제목에 해커톤·후기가 있어도 시스템을 만든 글은 남겼다.

### collected 보강 → 수기 필터

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

업스테이지(날짜 없는 페이지 207건), 라포랩스(창이 닫힘)는 더 긁지 않았다.

넥스트리 unassigned 64/210은 글이 넓게 퍼져 membership 임계를 못 넘긴 몫이다.
토스 unassigned 16/56도 레거시 개편·QA·지표가 한 Area에 안 붙는 글이 있다.

## 업스테이지 (21개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 에이전틱 LLM 성능 개선 및 서빙 인프라 | 5 | MoE, SnapPO, Commitment Tiers, SWE Bench, Terminal Bench, 긴 컨텍스트, 모듈형 AI 아키텍처 |
| 산업별 비정형 문서 자동화 파이프라인 구축 | 6 | Upstage Studio, Classify, Extract, ACORD, Agentic IE, OCR, Validate |
| 언어모델 및 문서인식 AI 기술 개발 | 10 | Document Parse, Information Extract, Reasoning Mode, Reasoning Budget, SolarBox, Vision Language Action, Sim2Real, tool use |

unassigned: 0

## 라포랩스 / 퀸 (24개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AI 기반 업무 자동화 및 개발 생산성 도구 | 11 | MCP, Google Apps Script, Playwright, OpenAI API, BigQuery, AI 이미지 생성, AI 프롬프트 자동화 |
| 실험 기반 문제 재정의와 추천시스템 최적화 | 4 | Item-based CF, Reranking, Realtime Action Encoder, Candidate×Sequence Early Fusion, recency bias 완화, ad_tag 기반 세션 추천, catalog coverage |
| 백엔드 인프라 성능 및 검색 최적화 | 6 | StarRocks, Colocate Join, Elasticsearch, RRF(Reciprocal Rank Fusion), EntityManagerFactory, Async Profiler, Tanstack Query, Next.js SSR |

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

## 넥스트리 (210개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 백엔드 기능 구현 및 시스템 안정성 트러블슈팅 | 56 | OOMKilled, Java 25 StructuredTaskScope, MSA, Outbox Pattern, CQRS, WebSocket/STOMP, Spring WebClient, 전략 패턴 |
| 프론트엔드 아키텍처, 디자인 시스템 및 모바일/폼 상태관리 | 47 | React Hook Form, React Query, 디자인 토큰, Micro-Frontend, Keycloakify, React Native, Monorepo, Figma Variables |
| 요구사항 정의 및 품질관리 프로세스 | 10 | 화면 설계서, 통합테스트 시나리오, Git 브랜치 전략, CI 게이트, IA, PMO, 프롬프트 엔지니어링 |
| AI 에이전트 기반 개발 워크플로우 및 도구 활용 | 21 | Claude Code, MCP, Multi-Agent Workflow, Context Window, CLAUDE.md, Codex, AGENTS.md |
| 인프라 운영 안정성 및 데이터 파이프라인 관리 | 12 | NATS JetStream, Flyway, KubeEdge, ROS2, MQTT, InfluxDB, 테이블 파티셔닝 |

unassigned: 64

## 구름 (21개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 기술 스택·아키텍처 선택과 RAG 검색 품질 문제 | 3 | MSA, 모놀리식 아키텍처, RAG, 하이브리드 검색, 리랭킹, Graph RAG, 청킹 전략, Node.js |
| AI 코딩 도구 및 개발 워크플로우 자동화 | 10 | Claude Code, MCP, 바이브코딩, n8n, TDD, 스펙 주도 개발, DDD, 코드 리뷰 |
| 제품 기획 프로세스 | 3 | 글로벌 제품 기획, 스토리보드, 기획 프로세스, 기획 조직 구축, 사용자 시나리오 |

unassigned: 5

## 가비아 (21개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AI/클라우드 인프라 자원 운영 | 11 | GPU, VDI, DaaS, 액체 냉각, PUE, AWS Config, RTO/RPO, API Gateway |
| 보안 위협 탐지 및 인증·정책 대응 | 4 | SAST/DAST, AWS Security Agent, SSL 인증서, 침투 테스트, WHOIS, ICANN RDP, 침해사고 탐지 |
| 하이웍스 API·AI채팅 연동 자동화 | 5 | 하이웍스 API, 하이웍스 AI채팅, 전자세금계산서, 홈택스, RAG, 전자서명, ChatGPT·Gemini·Claude |

unassigned: 1

## 한컴 (20개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 에이전틱 AI 시스템 아키텍처 설계 | 5 | 하네스, LLM-as-judge, SLM, Planner-Caller-Generator, OpenClaw, MoltBook, KoBART |
| 문서 파일 포맷 파싱 엔지니어링 | 5 | OOXML, OLE2, HWPX, HWP, FIB, PlcPcd, CharShape |
| AI 협업 개발 도구 및 워크플로 자동화 | 7 | CLAUDE.md, MCP, n8n, Health Check, 테스트 케이스 자동 생성, 모노레포, @DisplayName |

unassigned: 3

## 컴투스 (29개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 게임 데이터 애널리틱스 플랫폼(Hive 애널리틱스) | 13 | Hive 애널리틱스, 퍼널 분석, 기간 비교, 통화 환산, 지표 필터, BigQuery SQL, PG 결제 연동 |
| 백엔드 인프라·시스템 엔지니어링 | 10 | eBPF, Kubernetes, InnoDB Cluster, GitOps, Linux epoll, WebRTC, PHP-FPM, Zend Memory Manager |
| 행사·커뮤니티 소개성 콘텐츠 | 4 | IMAGINE 2026, OWASP, Tableau DataFest 2025, AI MeetUP, 바이브코딩, 생성형AI |

unassigned: 2
