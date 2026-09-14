# Track B: 파일럿 5개 회사 Area 생성 결과

engineering_focus -> v4 embedding -> clustering(complete linkage) -> LLM 병합 -> deterministic membership -> 키워드 태깅 전체 파이프라인을 5개 회사에 독립적으로 적용한 결과다.

각 Area는 안정적인 `id`(예: `oliveyoung-01`)를 갖는다. 스키마와 한계는
`../../../pipeline/experiments/tech_blog_engineering_focus_29/config/README.md` 참고.

## CJ올리브영 (44개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 백엔드 아키텍처·대규모 트랜잭션 처리 | 25 | Kafka, CDC, Circuit Breaker, Spring Batch Partitioning, MSA, 전략 패턴, Redis, Web Component |
| 조직문화·협업 프로세스 | 5 | AI-DLC, 애자일, 워크숍, QA 컨퍼런스, AI STUDIOS, Vrew, 랜덤 매칭 |
| 사내 행사·워크숍(비-엔지니어링) | 1 | GenAI 해커톤, 기술 로드맵, 옴니채널, 프로토타입, 글로벌엔지니어링센터 |
| 타입스크립트 타입 시스템 | 1 | 제네릭, 변성(Variance), 매개변수 다형성, 서브타입, 타입 안전성 |

unassigned: 12

## NHN Cloud (102개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 모바일/프론트엔드 앱 아키텍처 및 개발환경 | 30 | Webpack 4, ES6, Clean Architecture, MVVM, WebView, frida-gum, sandhook, Expo Web |
| 클라우드 인프라 및 쿠버네티스 운영 | 9 | Kubernetes, Portainer, Rancher, Github Actions, Lettuce client, CFS 스케줄러, CloudTrail, NHN Cloud Pipeline |
| 시스템 성능 및 네트워크 튜닝 | 13 | TCP 커널 파라미터, ClickHouse, Redis, Valkey, nmap, 톰캣 쿠키 프로세서, Kotlin 메모리릭, 웹 캐시 |
| 백엔드 웹 프레임워크 및 데이터 처리 | 7 | Spring Interceptor, Servlet Filter, BindingResult, Kotlin, Jupyter Extension, Spring MVC |
| 데이터 분석 및 AI 활용 | 13 | 리버스 지오코딩, 고객 세분화, AI Fashion, AI EasyMaker, DevContainer, AI 주도 개발방법론, 데이터 모델링 |

unassigned: 30

## kt cloud (134개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 데이터센터 전력·냉각 인프라 | 32 | Direct-to-Chip 액체 냉각, WUE, 800V DC, UPS, 고조파, 액침냉각, 전압 강하(Voltage Sag), 무효전력 |
| 클라우드 플랫폼 아키텍처 및 운영 안정성 | 21 | Multi-AZ, Multi-Region DR, Terraform, IAM, 제로 트러스트, 카오스 엔지니어링, Active-Active |
| 쿠버네티스·오픈스택 인프라 운영 및 플랫폼 엔지니어링 | 31 | OpenStack on Kubernetes, GitOps, Vault, OVN, Gateway API, Ceph, RoCEv2, Cluster API |
| AI 서비스화 및 LLM 인프라 최적화 | 26 | RAG, 양자화, KV 캐시, Vector DB, 임베딩, 리랭킹, Claude Code, 청킹 |
| AI 트렌드 및 조직 뉴스레터(비엔지니어링 성격) | 3 | DR, Multi-Region, Cilium, cgroups, AI Agent |

unassigned: 21

## 라인플러스 (80개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AI 에이전트 개발 및 조직 도입 | 22 | MCP, 컨텍스트 엔지니어링, ADK, Claude Code, 멀티 에이전트, RAG, human-in-the-loop, AIDD |
| AI 보안 및 가드레일 | 8 | ID-JAG, 프롬프트 인젝션, 가드레일 모델, GEPA, LLM-as-a-Judge, Athenz, CTFd |
| 백엔드 인프라 및 분산 시스템 아키텍처 | 6 | Kafka, Athenz, Central Dogma, xDS 프로토콜, Armeria, 오퍼레이터 패턴, DEK/KEK 이중 암호화 |
| 데이터 플랫폼 및 대규모 데이터 처리 | 8 | HDFS, Iceberg, Spark on Kubernetes, vLLM, Flink, Cassandra, ViewFS |
| 코드 품질·서비스 신뢰성(SLO)·AI 활용 도구화 잡다 사례 | 26 | SLI/SLO, 에러 버짓, OpenTofu, ChatOps, 이중 읽기(dual read), AttributedString, 함수형 인덱스, 비자기회귀 디코더 |

unassigned: 10

## 컬리 (18개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 물류·검수 자동화 및 이벤트 기반 백엔드 시스템 | 5 | On-device Re-ID, YOLOv11, Kafka Streams 윈도우, 아웃박스 패턴, Zero-shot 일반화, nginx, Redis 캐싱 |
| AI 코딩 에이전트 활용 생산성 워크플로우 | 6 | Claude Code, 클로드 코드, Remote Control, Task DAG, Ralph Loop, 로컬 RAG, CLAUDE.md, 서브에이전트 병렬화 |
| 프론트엔드 빌드 시스템 및 도메인 지식 검색 인프라 개선 | 4 | RAG, multilingual-e5-small, FTS5, Bun, Vite, Rollup, 트리셰이킹, ESM |

unassigned: 3
