# group4_areas: 8개 회사 Area 생성 결과 (수동 프롬프팅)

engineering_focus -> v4 embedding -> clustering(complete linkage) -> LLM 병합 -> deterministic membership -> 키워드 태깅 전체 파이프라인을 8개 회사에 독립적으로 적용한 결과다 (LLM 두 단계는 claude.ai 수동 프롬프팅으로 수행).

그룹4 8곳. 수기 필터 후 **171건** 중 evidence **149건**, unassigned **22건**.

각 Area는 안정적인 `id`(예: `nds-01`)를 갖는다. 스키마와 한계는
`../../../pipeline/experiments/tech_blog_engineering_focus_29/config/README.md` 참고.
직무 4개(서버·백엔드 / 웹 프론트엔드 / 모바일 / 데이터·AI)는 Area 이름이 아니라
`roles`다. Area 이름은 회사별 기술 주제다.

예전에는 그룹2와 묶어 `group24_areas`로 두었다. 지금은 그룹4만 이 파일에 둔다.

## 알려진 한계

RSS 상한으로 창이 짧았던 곳을 보강한 뒤, 수기 필터 → 임베딩 → Area를
다시 돌린 결과다 (2026-09-14). census `roles`는 키워드 1차 게이트라 오탐이
있을 수 있다. LLM이 직무를 다시 판단하지 않았다. 홍보성·HR·세션 참관기는
수기로 걸렀고, 제목에 해커톤·후기가 있어도 시스템을 만든 글은 남겼다.

NDS(wp-json=수집과 동일), 아임웹(블로그 수명 ~7개월), 안랩·버즈빌 등(창이
닫힘)은 더 긁지 않았다.

## LG AI연구원 (17개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 파운데이션 모델 및 멀티모달 AI 개발 | 7 | EXAONE, 멀티모달, MoE(Mixture-of-Experts), AGAPO 강화학습, Vision Language Model, 멀티 에이전트 파이프라인, 구조적 인과모형(SCM), spatial biology |
| 도메인 특화 예측 모델링 | 1 | 하이브리드 예측 시스템, 인과맵, 도메인 시뮬레이터, 설명 가능한 예측, 중장기 가격 예측 |
| Agentic AI 기반 산업 자동화 시스템 | 4 | Agentic AI, Tool Orchestration, On-Premise 경량화, MAPPO/QMIX, MC Dropout, 지식그래프(Ontology), Red Team 시뮬레이션 |
| LLM 알고리즘 및 서빙 인프라 연구 | 4 | Text-to-SQL, RAG(검색증강생성), 토픽 모델링, Mixture-Of-Experts(MoE) Upcycling, Spherical K-means, GPU Job 스케줄링, Argo Workflows |

unassigned: 1

## 농심데이터시스템(NDS) (14개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| AWS 클라우드 인프라 아키텍처 설계 및 운영 | 7 | Amazon Bedrock, EKS, IAM, CloudWatch, EBS, AWS Backup, Terraform, IRSA |
| AWS 네트워크 아키텍처 설계 | 1 | Direct Connect Gateway, Transit Gateway, VPC Attachment, 라우팅, 멀티계정 온프레미스 통신 |
| S3 스토리지 운영 및 비용 최적화 | 6 | S3 Lifecycle, S3 Batch Operations, AWS Amplify, Route 53, IAM Role, 버킷 정책, 교차계정 리전 간 복제 |

unassigned: 0

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

## 카카오엔터프라이즈 / 카카오클라우드 (22개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 클라우드 보안 및 인프라 자동화(IaC) | 6 | SECaaS, Terraform Provider, 제로트러스트, Multi-AZ, OpenStack, RBAC, CSAP |
| 클라우드 인프라 비용·성능 최적화 | 12 | GPUaaS, Kubeflow, HPA, Transit Gateway(TGW), KMS, Object Storage, A100 GPU, MSA |
| 대규모 GPU 분산학습 인프라 | 2 | Blackwell B200, InfiniBand, NCCL, Fat-Tree, SHARP, Kubeflow |

unassigned: 2
