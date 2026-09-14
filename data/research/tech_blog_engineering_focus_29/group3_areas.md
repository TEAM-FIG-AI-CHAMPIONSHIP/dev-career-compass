# group3_areas: 8개 회사 Area 생성 결과 (수동 프롬프팅)

engineering_focus -> v4 embedding -> clustering(complete linkage) -> LLM 병합 -> deterministic membership -> 키워드 태깅 전체 파이프라인을 8개 회사에 독립적으로 적용한 결과다 (LLM 두 단계는 claude.ai 수동 프롬프팅으로 수행).

전체 196건 중 evidence 173건, unassigned 23건.

## 알려진 한계

- 어피닛·메가존클라우드·인프랩/인프런·당근은 #60에서 이미 "12개월 미달" 알려진
  한계로 문서화된 회사들이다. 이 Area 결과도 그 제한된 데이터 범위 안에서
  나온 것이다 (당근은 특히 7건뿐이라 회사의 실제 기술 스펙트럼을 대표하기
  어렵다는 점을 merge rationale에서도 직접 언급함).

## GS리테일 (11개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 커머스 검색·추천 시스템과 LLM 기반 콘텐츠 이해 | 3 | OpenSearch, 하이브리드 검색 (BM25+벡터), 임베딩 (BGE-M3, Cohere), Query Understanding, Claude tool use, TwelveLabs Pegasus, Redis 선호 신호, 추천 랭킹 스코어링 |
| 사내 지식 RAG 파이프라인과 권한 기반 벡터 검색 | 5 | AgenticRAG, Qdrant, payload 필터 RBAC, Temporal 워크플로, 멀티테넌시 (named vector), blue/green 무중단 재색인, Query Expansion·대화 재작성, PII 스크럽·검수 게이트 |
| 사내 AI 봇의 채널 연동과 인증 게이트웨이 | 2 | Thin 플랫폼, Teams·Google Chat 연동, A2A, OIDC/OBO 인증 어댑터, 카드 렌더링 검증 파이프라인, 노코드 에이전트 워크플로우 (MISO) |

unassigned: 1

## SK플래닛 (13개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| LLM 기반 데이터 조회·마케팅 서비스 구축 | 4 | Text2SQL, LangChain/LangGraph, RAG + Reranker, 벡터 DB (Elasticsearch), SSE 스트리밍, react-window 리스트 가상화, Bedrock Prompt Caching (cachePoint), Batch API |
| 멀티모달 센싱과 웹 기반 실시간 렌더링 | 2 | Late Fusion, Environmental Attention Layer, WebRTC 카메라 스트리밍, A-Frame, 마커 기반 추적, 쉐이더·프레임 속도 조정, 프로그레시브 로딩 |
| 외부 LLM 활용 사례와 기술 조직 운영 | 7 | Multi-stage RAG, Llama 3.3 70B 양자화, MAB 강화학습, Voice Conversion 파이프라인, U-DiT Diffusion Decoder + BigVGAN, Speaker Similarity·F₀ 평가, SEO/AEO 최적화, GA4 유입 분석 |

unassigned: 0

## 네이버 (49개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AI 에이전트 개발 환경과 GPU·LLM 서빙 인프라 | 17 | Claude Code Skill, 에이전트 기억·컨텍스트 관리, 멀티 에이전트 파이프라인 (AutoGen), Playwright E2E 하네스, Kubernetes GPU 서빙, KV Cache·Prefix Cache 라우팅, vLLM, Event-driven MLOps |
| 대규모 데이터 파이프라인과 시계열 모니터링 저장소 운영 | 8 | VictoriaMetrics, 메트릭 카디널리티, Hot/Warm 계층 저장, dual write 무중단 전환, CDC 복제 (Apache Flink), Iceberg Materialized View, DBT·Airflow 데이터 계보 |
| 서비스 클라이언트 성능·품질과 로그 처리 파이프라인 | 9 | LCP p95, DOM 재구성·텍스트 애니메이션, Logiss 로그 파이프라인, Storm 토폴로지, Jetpack Compose·View 대응, Baseline 기반 회귀 방어 (Manifest Shield), 클릭 로그 히트맵 시각화, 이미지 워터마킹·protective perturbation |
| 언어 런타임 동작과 저수준 코드 정합성 | 7 | 미정의 동작 (엄격한 앨리어싱), std::bit_cast, 객체 수명·placement new, JVM JIT 웜업, ThreadLocal 요청 범위 캐싱, fork vs spawn 멀티프로세싱, Kafka Consumer Group Protocol v2 |

unassigned: 8

## 당근마켓 / 당근 (7개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 앱 렌더링 런타임 전환과 배포 정보 자동화 | 3 | Lynx, PrimJS (QuickJS), IFR (Instant First-Frame Rendering), Brownfield 점진 도입 (LynxView), CDN 번들 분리 배포, Rspeedy 툴체인, PR description 기반 LLM 요약, Notion DB + CronJob 파이프라인 |
| 대규모 트래픽 서비스 아키텍처와 사내 데이터 플랫폼 | 3 | 선언적 정의 계층 분리, Airflow + Spark (EMR on EKS), Dynamic DAG Generation, 모듈 경계와 계약, 공유 플랫폼 모듈 (모델 변환), A/B 테스트 상호배제 그룹, Experiment MCP, RPS 스케일 대응 |
| 사용자 인증 체계와 계정 식별 | 1 | CI 기반 본인인증, SMS 점유 인증, OAuth 2.0 / OIDC, 단일 인증 도메인 통합, 앱 리다이렉트 로그인, QR 로그인 |

unassigned: 0

## 메가존클라우드 (23개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 멀티 클라우드 인프라 구축·운영과 Bedrock 모델 검증 | 8 | AWS Bedrock Converse API, 프롬프트 캐싱 (cachePoint), LLM 비용 절감 (캐시 재배치·호출 상한), TGW Native Network Firewall, Lambda 기반 라우팅 전환 자동화, AWS HealthOmics, Cloud Run + Pub/Sub 로그 파이프라인, gcloud·Cloud Asset Inventory 점검 스크립트 |
| 코딩 에이전트 실행 구조와 에이전트 친화적 코드 설계 | 5 | headless CLI 오케스트레이션, LiteLLM Proxy 게이트웨이, Amazon Cognito User Pool, Loop Engineering, Prompt/Context/Harness/Loop 4계층, Functional Core / Imperative Shell, 토큰 재전송 비용, Claude Code 스킬 |
| 하이브리드 사설망 연결과 경계 보안 아키텍처 | 6 | Private Service Connect (PSC), PSC-Interface·network-attachment, Cloud VPN·Interconnect, DNS 오버라이드 (/etc/hosts), VPC Service Controls, Vertex AI Agent Engine, Samba(SMB) 브릿지, 온프레미스 하이브리드 확장 (AWS Batch·Spot) |

unassigned: 4

## 어피닛 (30개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 신용 심사 모델링과 금융 플랫폼 아키텍처 | 6 | Behavior Cloning (XGBoost), logprobs 기반 PD 산출, Scheduled Amortization EMI 역산, DDD 마이크로서비스, Business Rule Engine 병렬 실행, LangChain/LangGraph 대화형 엔진, 사전 승인 오퍼 계산, LLM Rate-Limiting |
| 사내 AI 에이전트 업무 위임 구조와 데이터 거버넌스 | 15 | MCP 허브-스포크, Human-in-the-loop 승인 게이트, CLAUDE.md·공용 skills, Claude Agent SDK, PII 비식별화 (Presidio), Lake Formation Tag-Based Access Control, JupyterHub DockerSpawner 격리, n8n·슬랙봇 업무 자동화 |
| Apache Iceberg 기반 대용량 저장소 비용·성능 운영 | 5 | Apache Iceberg, Compaction (rewrite_data_files), 스냅샷 만료 정책, Parquet Rowgroup·버킷팅, Pyiceberg 직접 조회, 매니페스트 캐싱, 스캔량 기반 비용 검증, PyAthena 스트리밍 쿼리 |

unassigned: 4

## 인프랩 / 인프런 (11개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| LLM 서비스 구축과 미디어 처리 파이프라인 | 5 | SSE 스트리밍 + Virtual Thread, Spring AI Advisor, 컨텍스트 Tool 로딩, 프롬프트 캐싱, LLM-as-a-Judge (Golden Dataset), Envoy AI Gateway, OCR + VLM 문단 묶기 (XY Cut), Lambda@Edge 이미지 변환 (AVIF) |
| 배포 환경·의존성 공급망과 시스템 레벨 디버깅 | 4 | Argo CD PR Preview, HTTPRoute 쿠키 라우팅, pnpm minimumReleaseAge, postinstall 빌드 스크립트 차단, strace 시스템콜 추적, 동시성 경합 (EEXIST 처리 결함), codemod 기반 마이그레이션, Helm 템플릿 리소스 축소 |
| 프런트엔드 UI 구조 설계와 렌더링 제약 대응 | 2 | Module Federation, 하이드레이션 에러 회피, CSS 변수·속성 셀렉터 스냅샷, GPU composite 애니메이션, useFunnel hook, FunnelStep 선언적 정의 |

unassigned: 0

## 채널코퍼레이션 / 채널톡 (52개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 대규모 트래픽 처리와 데이터 저장소·성능 엔지니어링 | 10 | DynamoDB, 온라인 마이그레이션 (Export/Import, Dual Write), ClickHouse, 인덱스 히트 (IndexedDAO), 동적 스케일링 (Per-Worker Queue Depth), 렌더링 성능 프로파일링 (INP, flame chart), WebGL 프래그먼트 쉐이더, 셀 아키텍처·셔플 샤딩 |
| 상담 AI 에이전트와 음성·대화 데이터 처리 | 10 | RAG 청킹·검색, hybrid search (BM25+벡터), 자체 벤치마크 (Hit@k, nDCG@k, pass@k), TTS 파인튜닝 (GRPO, Iterative DPO), Turn Detection, 에이전트 자동 QA (시나리오 생성), Stateful Task / Agent Loop, dagster 전처리 파이프라인 |
| AI 에이전트를 전제로 한 디자인 시스템과 비개발 직군 실행 환경 | 19 | Cursor Agent / Codex, MCP 서버, Go AST 아키텍처 테스트, CLAUDE.md / AGENTS.md, 디자인 시스템 컴포넌트 추상화, 샌드박스 실행 환경, lazy-loading 툴 설계 (컨텍스트 비용), n8n 워크플로우 자동화 |
| Kubernetes 서비스 메시와 모니터링 인프라 운영 | 7 | Istio Ambient mode, ztunnel, Envoy config (HBONE, internal listener), istio-cni / untaint-controller, blue-green 무중단 업그레이드, readinessProbe·xDS 연결 탐지, Grafana Mimir, Kafka ingest-storage |

unassigned: 6
