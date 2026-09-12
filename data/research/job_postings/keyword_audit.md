# 키워드 감사 자료 (원자료)

- 생성 시각: 2026-09-12T14:19:53+09:00
- 대상 ATS: greeting 11곳, ninehire 2곳, custom 11곳
- 대상 공고: `deploy=true` **1405건**
- 생성 스크립트: `scripts/build_keyword_audit.py` (재실행 시 갱신)
- 분류 기준: `common/job_classifier.py`의 **현재 스펙 키워드** (이 문서 작성 시점에 변경 없음)

> 이 문서는 참고자료이며 코드와 무관하다. `job_classifier.py`는 수정되지 않았고,
> STEP 6 집계도 현재 스펙 키워드 그대로 수행한다.

## 전체 규모

| 구분 | 건수 | 설명 |
|---|---:|---|
| 전체 (`deploy=true`) | 1405 | |
| 구조화 필드로 분류됨 | 249 | occupation / job 값이 스펙 카테고리에 매칭 |
| **제목 키워드로만 분류됨 (오탐 검토 대상)** | **112** | 구조화 분류 실패 → 제목 fallback (섹션 2) |
| **미분류 (누락)** | **1044** | `category = None` (섹션 1) |
| **부분일치 오탐** | **35** | 키워드가 더 긴 무관한 단어의 일부로 매칭 (섹션 3) |
| **단어 경계로 인한 역방향 미분류** | **8** | 키워드가 관련 있는 복합어 안에 있으나 `\b`로 미매칭 (섹션 4) |
| **구조화 필드 자체 오탐** | **9** | 직군 이름에 키워드가 섞여 무관한 업무가 분류됨 (섹션 5) |

검토 대상: **미분류(누락) 1044건 + 오탐 검토 대상 112건 + 부분일치 오탐 35건 + 역방향 미분류 8건**

> **섹션 3(부분일치 허용 시 웹툰 등 오탐 발생)과 섹션 4(부분일치 금지로 인한 Database 등 누락)는 같은 규칙 변경으로 서로 반대 방향에 영향받는다.**

섹션 2와 섹션 3은 기준이 달라 일부 겹친다. 겹치는 건수는 섹션 3-4에 정리했다.

### ⚠️ 우선순위 — 키워드 확장 결정 지연 시 영향 범위

> 채널톡은 Engineering팀 공고 10건 중 6건(Software Engineer x2, DevOps Engineer,
> Security Engineer, Machine Learning Engineer, Forward Deployed Engineer)이 전부
> 미분류됨. 원인 셋: (1) team 필드가 스펙 카테고리와 매핑 안 됨
> (2) DevOps/Security 키워드 부재 (3) Machine Learning/ML 키워드 부재.
> 키워드 확장 결정을 미루면 채널톡이 서버·백엔드·데이터·AI 보유 회사 목록에서
> 통째로 빠질 수 있음 — 다른 회사 사례보다 영향 범위가 큼.

해당 6건의 원자료는 섹션 1의 채널톡 항목에 있다.

동일 직무명(Machine Learning Engineer)이 하이퍼커넥트(team=AI/ML)에서는 분류되고 채널톡(team=Engineering)에서는 안 됨 — 분류 결과가 직무 성격이 아니라 회사별 ATS 팀 명명 방식에 좌우됨을 보여주는 사례.

ATS별 내역은 다음과 같다.

| ATS | 회사 수 | 공고 | 구조화 분류 | 제목 fallback | 미분류 |
|---|---:|---:|---:|---:|---:|
| greeting | 11 | 546 | 54 | 34 | 458 |
| ninehire | 2 | 31 | 5 | 2 | 24 |
| custom | 11 | 828 | 190 | 76 | 562 |

ATS마다 구조화 필드의 원래 이름이 다르다. 이 문서에서는 `occupation` / `job`으로 통일해 표기한다.

- **greeting**: occupation = `workspaceOccupation.occupation`, job = `workspaceJob.job`
- **ninehire**: occupation = `recruitment.jobGroup.title`, job = `recruitment.jobTask.title`
- **custom**: 회사마다 다름 — 네이버: occupation = `classCdNm`, job = `subJobCdNm` / 카카오뱅크: occupation = `recruitClassName`, job = 없음 / 라인: occupation = `job_unit[].name`, job = `job_fields[].name` / 당근: occupation = `data-division`, job = `data-department-slugs` / 티빙: occupation = Notion 컬렉션 이름, job = `기술스택`·`주요스킬` / 채널톡: occupation = `categories.team`, job = 없음 / 뱅크샐러드: occupation = 응답 그룹 키 `department`, job = `data[].job` / 하이퍼커넥트: occupation = `categories.team`, job = 없음 / 쏘카: occupation = `job_group_code` 라벨, job = 없음 / 카카오: occupation = `jobTypeName`, job = `skillSetList[].skillSetName` / 토스: occupation = metadata Job Category, job = metadata 세부 포지션 명

현재 적용 중인 키워드는 다음과 같다.

**제목(title)용 — 기능명세 스펙 원본**

| 직무 | 키워드 |
|---|---|
| 서버·백엔드 | `백엔드`, `서버`, `Backend`, `Server` |
| 웹 프론트엔드 | `프론트엔드`, `웹`, `Frontend`, `Web` |
| 모바일 | `모바일`, `iOS`, `Android`, `안드로이드` |
| 데이터·AI | `데이터`, `AI`, `머신러닝`, `ML`, `인공지능`, `Data` |

**구조화 필드(occupation/job)용 — 크롤러에서 추가한 사전**

| 직무 | 키워드 |
|---|---|
| 서버·백엔드 | `백엔드`, `서버`, `Backend`, `Back-end`, `Back End`, `Server`, `API`, `DevOps`, `SRE`, `인프라`, `Infrastructure`, `Platform Engineering` |
| 웹 프론트엔드 | `프론트엔드`, `프론트`, `웹`, `Frontend`, `Front-end`, `Front End`, `Web` |
| 모바일 | `모바일`, `Mobile`, `iOS`, `Android`, `안드로이드`, `Flutter`, `React Native` |
| 데이터·AI | `데이터`, `Data`, `AI`, `머신러닝`, `ML`, `인공지능`, `MLOps`, `Machine Learning`, `Analytics`, `분석`, `Scientist` |

---

## 1. 현재 스펙 키워드로 분류되지 않는 원본 값 — 우선 검토 대상

`deploy=true` 1405건 중 `category = None`으로 떨어진 **1044건**의 원본 값이다.

### 1-1. 미분류 공고의 title 전수 (회사별)

#### 올리브영 (`oliveyoung`, greeting) — 미분류 175건 / 전체 212건

| title | occupation | job |
|---|---|---|
|  디지털 사업 전략 담당자 | 경영지원(전략) | 사업전략 |
| AMD (정규직 전환형 계약직) | None | None |
| B2B 물류센터 운영 관리 담당자 (경산) | 물류 | None |
| B2B 물류센터 운영 관리 담당자 (양지) | 물류 | None |
| B2B 수출 운영 관리 담당자 (안성) | 물류 | SCM |
| B2C 물류센터 운영 관리 담당자 (양지) | 물류 | None |
| B2C 물류센터 운영 프로세스 기획 담당자 | 물류 | 전략기획 |
| BM 팀장 (색조사업부)  | None | None |
| BX 디자이너 | 디자인 | 비주얼디자인 |
| BX디자이너 (계약직)  | None | None |
| BX이벤트 전략/실행 담당자(시니어) | 마케팅 | 마케팅 |
| BX이벤트 전략/실행 담당자(주니어) | 마케팅 | 마케팅 |
| DBA | IT | None |
| DevRel (Developer Relations) | IT | DevRel |
| Global Product Designer | 디자인 | Product Design |
| Global User Researcher  | 기타/특수 | Research |
| IMC 마케터 | 마케팅 | 마케팅커뮤니케이션 |
| IP 콜라보 마케팅 기획 담당자 | 마케팅 | IP |
| IT 구매 담당자 | 경영지원 | 구매 |
| IT 인프라 기획 담당자 | 경영지원 | IT전략 |
| IT기획 담당자 | 경영지원 | IT전략 |
| Language Specialist (영어) | 기타/특수 | 글로벌사업 |
| MD (PB 운영) | None | MD운영지원 |
| MD사업관리 담당자 | 경영지원(사업관리/재무) | 사업관리 |
| MD사업전략/개발 담당자 (시니어) | 경영지원 | 사업전략 |
| MD사업전략/개발 담당자 (주니어) | 경영지원 | 사업전략 |
| MD스토어기획 담당자 | 경영지원 | MD스토어기획 |
| Marketing Designer | 디자인 | Marketing Design |
| Network RE | IT | None |
| PB 글로벌 GTM 담당자 | 경영지원(사업관리/재무) | None |
| PB 마케터 | 마케팅 | 브랜드마케팅 |
| PB 화장품 공급운영 관리 (SCM) | 물류 | SCM |
| PB브랜드 콘텐츠 디자인 | None | None |
| PB화장품 구매 담당자 (소싱/조달) | 경영지원 | 구매 |
| PB화장품 구매 담당자(기초/바디/프래그런스) | None | None |
| PMO | None | None |
| Platform Designer (디자인시스템구축) | 디자인 | Product Design |
| Product Designer | 디자인 | Product Design |
| Product Designer (B2B/광고플랫폼) | 디자인 | Product Design |
| Product Designer (팀장급) | 디자인 | Product Design |
| Product Manager - Account & Membership (회원&멤버십) | IT | Product Management |
| Product Manager - Campaign Platform (캠페인) | IT | Product Management |
| Product Manager - Catalog & Listing (상품) | IT | Product Management |
| Product Manager - Commerce Display | IT | Product Management |
| Product Manager - Coupons & Promotions (쿠폰&증정) | IT | Product Management |
| Product Manager - Discovery (US mall) | IT | Product Management |
| Product Manager - Discovery (발견) | IT | Product Management |
| Product Manager - Fulfillment | IT | Product Management |
| Product Manager - Gift/Promotion (US mall) | IT | Product Management |
| Product Manager - Global E-Commerce | None | Product Management |
| Product Manager - In-store Payment | IT | Product Management |
| Product Manager - Merchant Partner Platform (정산) | IT | Product Management |
| Product Manager - Merchant Platform (파트너플랫폼) | IT | Product Management |
| Product Manager - Omnichannel | IT | Product Management |
| Product Manager - Order/Payment/Point | IT | Product Management |
| Product Manager - PIS(파트너 인텔리전스 시스템) | IT | Product Management |
| Product Manager - Product (US mall) | IT | Product Management |
| Product Manager - Store Operations | IT | Product Management |
| Product Manager - 광고/DMP | IT | Product Management |
| Product Manager - 광고/DSP | IT | Product Management |
| Product Manager - 광고/SSP | IT | Product Management |
| Product Manager - 커머스 신사업(Review) | IT | Product Management |
| Product Strategist | None | 사업전략 |
| QA Engineer (Domestic) | IT | SW QA |
| QA Engineer (Global) | IT | SW QA |
| QA Ops Engineer (Test Automation) | IT | SW QA |
| Research Specialist | 마케팅 | Research |
| SCM 사업관리/기획 담당자 | 경영지원(전략) | 전략기획 |
| SCM 전략기획 담당자 | 경영지원(전략) | 전략기획 |
| SRE | IT | None |
| Staff Software Engineer (글로벌서비스 개발) | IT | Global Software Engineering |
| TPM (Tech. Project Management) | IT | Product Management |
| US E-Commerce 온사이트 마케터 | 마케팅 | 글로벌온사이트마케팅 |
| US E-Commerce 퍼포먼스/어필리에이트 마케터 | 마케팅 | 글로벌마케팅 |
| USE 온라인 플랫폼 사업관리/기획 담당자 | 경영지원(사업관리/재무) | 글로벌사업관리 |
| User Researcher | 기타/특수 | Research |
| VMD 담당자 | 디자인 | VMD |
| 개발 BM (PB 식품) | 제조 | BM |
| 개발 BM (기초화장품, 헤어용품) | None | BM |
| 개발 BM (미용소품/생활용품) | 제조 | BM |
| 검색 서비스 품질관리 담당자 (계약직) | None | None |
| 결제 제휴 및 프로모션 기획 담당자 | 마케팅 | 제휴마케팅 |
| 공간디자인(인테리어) 담당자 | 디자인 | 인테리어 |
| 공산품(잡화) 품질관리 담당자 | 경영지원 | 품질관리 |
| 광고 정산 및 운영 지원 담당자 (계약직) | None | None |
| 구매 담당자 | 경영지원 | 구매 |
| 국내 및 수출 입출고 품질관리 담당자 (안성) | 경영지원 | 품질관리 |
| 그로스마케터 | 마케팅 | 마케팅 |
| 글로벌 B2B SCM 팀장 | 물류 | None |
| 글로벌 B2B 마케팅커뮤니케이션 마케터 (Estern) | 마케팅 | 글로벌마케팅 |
| 글로벌 CX체계 설계 담당자 | None | None |
| 글로벌 MD 통합 채용 | None | 글로벌MD |
| 글로벌 SCM 전략/물류거점 구축 PM | 물류 | None |
| 글로벌 VMD 운영 Assistant (계약직) | None | None |
| 글로벌 VMD담당자 | 디자인 | VMD |
| 글로벌 개인정보보호 담당자 | 경영지원 | 정보보안/개인정보보호 |
| 글로벌 리테일미디어 컨설턴트 | 마케팅 | 퍼포먼스마케팅 |
| 글로벌 발주 프로세스 운영 담당자 | 물류 | SCM |
| 글로벌 상품운영전략 | None | 상품운영 |
| 글로벌 영업지원 담당자 (계약직) | None | None |
| 글로벌 이커머스 해외영업/운영 담당자(아마존/ 틱톡샵) | 영업 | 글로벌플랫폼운영 |
| 글로벌 인허가 (RA) 지원 담당자 (계약직) | None | None |
| 글로벌 재고운영 및 정산지원 담당자(계약직) | None | None |
| 글로벌 품질관리 담당자 (식품/건강기능식품/잡화) | 경영지원 | 품질관리 |
| 글로벌 품질관리 담당자 (화장품/OTC/의료기기) | 경영지원 | 품질관리 |
| 글로벌몰 CRM 마케터 | 마케팅 | 글로벌마케팅 |
| 글로벌몰 Technical Program Manager (TPM) | IT | TPM |
| 글로벌몰 마케팅 운영 Assistant (계약직) | None | None |
| 글로벌몰 멤버십 마케터 | 마케팅 | 글로벌마케팅 |
| 글로벌몰 시니어 그로스 마케터 | 마케팅 | 글로벌마케팅 |
| 글로벌몰 중화권 소셜/바이럴 마케터 (역직구 플랫폼) | 마케팅 | 글로벌마케팅 |
| 글로벌몰 퍼포먼스 마케터 | 마케팅 | 글로벌마케팅 |
| 글로벌몰 프로모션 마케터 | 마케팅 | 글로벌마케팅 |
| 글로벌커머스 일본 사업전략 담당자 | 경영지원(전략) | 글로벌사업전략 |
| 글로벌콘텐츠커머스팀 팀장 | 마케팅 | 글로벌마케팅 |
| 기초화장품 BM | None | BM |
| 노무관리/조직문화 담당자 | 경영지원(인사) | HRM |
| 도심물류매장 MFC 운영(무기계약직) - 인천점 | None | None |
| 디지털 마케팅 전략 담당자 | None | None |
| 디지털플랫폼 사업전략 팀장 | 경영지원(전략) | None |
| 라이브커머스 PD | None | None |
| 리테일 사업관리 담당자 | 경영지원(사업관리/재무) | 사업관리 |
| 리테일미디어 DMP 상품 기획/사업 담당자 (BPO) | None | BPO |
| 리테일미디어 광고 사업 담당자 | 마케팅 | None |
| 리테일미디어 광고 상품기획/사업 담당자 (BPO) | 마케팅 | 마케팅 |
| 리테일미디어 광고(AD) 퍼포먼스 마케터 | 마케팅 | 퍼포먼스마케팅 |
| 리테일미디어 구좌형 광고 상품기획/운영 담당자 (BPO) | 마케팅 | BPO |
| 매장 자동발주 기획/관리 담당자 | 물류 | SCM |
| 미국/웰니스 스토어기획 담당자 | 경영지원 | MD스토어기획 |
| 미주 글로벌 마케터 (컬러그램)  | 마케팅 | 브랜드마케팅 |
| 미주 마케팅 담당자 (바이오힐보) | 마케팅 | 마케팅 |
| 바이오힐 보 글로벌 퍼포먼스 마케터 (BIOHEAL BOH) | 마케팅 | 마케팅 |
| 바이오힐 보 동남아 마케터 (BIOHEAL BOH) | 마케팅 | 마케팅 |
| 바이오힐보 글로벌 채널 실적 전략 담당자 | 영업 | None |
| 뷰티 카테고리 MD | None | MD |
| 브랜드 디자이너 | 디자인 | 브랜드디자인 |
| 브랜드 마케터 (웨이크메이크)  | 마케팅 | 브랜드마케팅 |
| 비주얼 콘텐츠 기획자 (PB 브랜드) | None | None |
| 비주얼디자인 Assistant (계약직) | None | None |
| 상권개발 담당자 | 건설/개발 | 상권개발 |
| 소셜 콘텐츠 제작 담당자 | 마케팅 | 브랜드마케팅 |
| 소셜커머스 사업기획 담당자(BPO) | 경영지원 | BPO |
| 스토어 브랜딩 전략 담당자 | 마케팅 | 브랜딩마케팅 |
| 안성물류센터 입/출고 검사 담당자 (계약직) | None | None |
| 양지물류센터 입/출고 검사 담당자 (계약직) | None | None |
| 양지센터 입출고 품질관리 담당자 | 경영지원 | 품질관리 |
| 어필리에이트 광고 사업 담당자 | None | None |
| 오늘드림 기획 운영 담당자 | 물류 | None |
| 온라인 APP 온사이트 프로모션 | 마케팅 | 마케팅 |
| 온라인 프로모션 온사이트 마케팅 담당자 | 마케팅 | 온사이트마케팅 |
| 온사이트 마케팅 담당자 | 마케팅 | 온사이트마케팅 |
| 올리브영 PB브랜드 운영 지원 담당 (계약직) | None | None |
| 이커머스 재고수불 관리 담당자 (계약직) | None | None |
| 인테리어 설계 및 시공 관리 담당자 | 디자인 | 인테리어 |
| 일본 EC 영업 담당자 | 영업 | None |
| 전사 캠페인/프로모션 담당자 | 마케팅 | 프로모션마케팅 |
| 정산담당자 (계약직) | None | None |
| 제휴 프로모션 운영 및 사업지원 담당자 (계약직) | None | None |
| 채용 코디네이터(계약직)  | None | HRM |
| 커머스 신사업 BPO | 경영지원 | BPO |
| 커뮤니케이션 디자이너 | 디자인 | 브랜드디자인 |
| 컨텐츠 디자이너 | 디자인 | 비주얼디자인 |
| 콘텐츠 디자이너 (계약직) | None | None |
| 콘텐츠 마케팅 담당자(시니어) | 마케팅 | 브랜드마케팅 |
| 콘텐츠커머스 마케터/전략기획 담당자 | 마케팅 | 소셜콘텐츠마케팅 |
| 클라우드 인프라 보안 담당자 | 경영지원 | 정보보안/개인정보보호 |
| 통번역 담당자 (계약직) | 경영지원 | 사무지원 |
| 통합 마케팅 전략 담당자 | 마케팅 | 마케팅 |
| 패키지 디자이너 | 디자인 | 브랜드디자인 |
| 플랫폼 전략기획 담당자 (PM) | IT | Product Management |
| 헬시라이프 카테고리 MD | None | MD |
| 협력사발주 공급망 관리/기획 담당자 | 물류 | SCM |
| 화장품 품질관리 담당자(계약직) | None | None |
| 화장품 품질보증 담당자 | 경영지원 | 품질관리 |
| 📌채용 마케팅 인턴 | 경영지원(인사) | None |

#### 무신사(+29CM) (`musinsa`, greeting) — 미분류 107건 / 전체 123건

| title | occupation | job |
|---|---|---|
|  Brand & Contents Marketer (China) | None | Brand Marketing |
| 29CM HOME SNS 운영 담당자 | None | Content Planning |
| BM Lead (Beauty PB) | None | BM |
| Brand Marketer (Social Impact Manager) | None | Brand Marketing |
| Brand Marketer (글로벌 브랜드마케팅) | None | Brand Marketing |
| Buying MD (Footwear) | None | MD |
| Buying MD (Sports / Outdoor) | None | MD |
| CX Program Manager | None | CX |
| Commerce PM Assistant | None | MD |
| DBA (Foundation Platform) | None | DBA |
| Engineering Manager (무신사페이먼츠/결제) | None | Engineering Manager |
| Engineering Manager (무신사페이먼츠/정산) | None | Engineering Manager |
| Fashion Designer (IP Business) | None | MD |
| Fashion Designer (무신사 스탠다드/라이프웨어) | None | Fashion Design |
| Fashion Designer (무신사 스탠다드/우먼즈) | None | Fashion Design |
| FinOps Engineer | None | None |
| Global Brand Marketer | None | Brand Marketing |
| Global Brand Marketer (Beauty PB) | None | Brand Marketing |
| Global CX Specialist (Japan)  | None | CX |
| Global Contents Marketer (Beauty PB) | None | Global Marketing |
| Global Logistics 담당자 | None | Operation |
| Global Performance Marketer | None | Growth Marketing |
| Global Retail Manager (무신사 스탠다드) | None | Off-Line Planning |
| Growth Marketer (CRM) | None | Growth Marketing |
| Growth Marketer (O4O 옴니채널) | None | Growth Marketing |
| Growth Marketing Lead | None | Growth Marketing |
| Growth Marketing Lead (글로벌 스토어) | None | Growth Marketing |
| HR Generalist (무신사로지스틱스) | None | HRM |
| IMC Marketer (무신사 스탠다드) | None | Brand Marketing |
| IP 컬래버 소싱 담당자 (무신사 스탠다드) | None | Production Management |
| IT Service Administrator | None | System Engineering |
| Interpreter & Translator (Chinese - Korean) | None | General Affair |
| MD (IP Business) | None | MD |
| MD (남성패션) | None | MD |
| Network Security Engineer (SASE&CASB) | None | Security Engineering |
| On-Site Marketer (전사캠페인) | None | On-Site Marketing |
| On-Site Marketer (채널 기획) | None | On-Site Marketing |
| Operations Assistant (리테일 상품 운영) | None | Operation Management |
| Operations Assistant (이벤트 운영) | None | Sales Planning |
| Package Designer (Beauty PB) | None | Package Design |
| Performance Marketer (Beauty PB) | None | Brand Marketing |
| Photographer (무신사로지스틱스) | None | Photographer |
| Planning MD (Footwear) | None | MD |
| Product Designer (Commerce) | None | Product Design |
| Product Lead (Core Customer Growth) | None | Product Management |
| Product Lead (물류) | None | Product Management |
| Product Lead (유즈드) | None | Product Management |
| Product Manager (29CM Order & Pricing) | None | Product Management |
| Product Manager (Core Partner) | None | Product Management |
| Product Manager (PDP/캠페인/콘텐츠) | Product | Product Management |
| Product Manager (SCM) | None | Product Management |
| Product Manager (무신사페이먼츠/결제) | None | Product Management |
| Product Manager (앱테크) | None | Product Management |
| Product Manager(Core Catalog) | None | Product Management |
| Program Manager (Commerce Platform) | None | Program Manager |
| Program Manager (글로벌) | None | Program Manager |
| Program Manager (커머스 정책 기획) | None | Program Manager |
| Program Manager (29CM 커머스) | Program Manager | None |
| Retail Marketer (무신사 스탠다드) | None | Brand Marketing |
| Retail Media Experience Manager | None | Ad Business |
| Retail Media Growth Lead | None | Ad Business |
| Retail Media Growth Manager | None | Ad Business |
| Retail Operation Manager (무신사 스탠다드) | None | Off-Line Planning |
| SAP Engineer (MM) | None | None |
| SAP FI 개발·운영 (Platform Business Operation) | None | None |
| Security Compliance Manager | None | Security Management |
| Security Engineer (접근제어/암호키관리 운영) | None | Security Engineering |
| Senior MD (글로벌패션) | None | MD |
| Senior Retail Media Growth Manager | None | Ad Business |
| Social Marketing Lead (무신사·29CM) | None | Content Planning |
| Technical Program Manager (Infra) | None | Product Management |
| VMD (무신사동남아/중동) | None | VMD |
| Visual Retoucher (Beauty PB) | None | Content Design |
| 다이마루 소싱/생산관리 담당자 (무신사 스탠다드) | None | Production Management |
| 디지털/가전 MD (29CM) | None | MD |
| 머천다이징 VMD (무신사 스탠다드) | None | VMD |
| 무신사 오프라인 스토어 SNS 운영 담당자 | None | Content Planning |
| 물류 Program Manager (무신사로지스틱스)  | None | Program Management |
| 물류 운영 관리자 (무신사로지스틱스)  | None | FC운영 |
| 물류 전략 기획 담당자 (무신사로지스틱스)  | None | Business Analysis |
| 물류센터 정산 담당자 (무신사로지스틱스) | None | FC운영 |
| 반품 공정 관리자 (무신사로지스틱스) | None | FC운영 |
| 뷰티 오프라인 MD | None | MD |
| 브랜드 기획자 (29CM) | None | Content Planning |
| 상품컨트롤 MD (무신사 스탠다드) | None | Planning MD |
| 소싱/생산관리 담당자 (PB 브랜드) | None | Production Management |
| 소싱/생산관리 담당자 (무신사 스탠다드) | None | Production Management |
| 소재 소싱/생산관리 담당자 (무신사 스탠다드) | None | Production Management |
| 소재 소싱/생산관리 담당자 (통합소싱) | None | Production Management |
| 스킨케어 BM (Beauty PB) | None | BM |
| 오프라인 뷰티 영업 관리 담당자 | None | Off-Line Operation |
| 오프라인 커머스 마케팅 AMD | None | Brand Marketing |
| 오프라인 홈 MD (29CM) | None | MD |
| 온사이트 채널 플래너 (29CM) | Marketing | On-Site Marketing |
| 우먼즈 상품기획 MD (무신사 스탠다드) | None | Planning MD |
| 우븐 소싱/생산관리 담당자 (무신사 스탠다드) | None | Production Management |
| 유튜브 콘텐츠 기획/제작 매니저  | None | Video Production |
| 잡화 소싱/생산관리 담당자 (통합소싱) | None | Production Management |
| 재무기획 담당자 | None | Financial Planning |
| 카테고리 마케터 (29CM)  | None | On-Site Marketing |
| 컬래버 상품기획 MD (무신사 스탠다드) | None | MD |
| 컬래버레이션 Marketer (무신사 스탠다드) | None | Brand Marketing |
| 콘텐츠 기획 담당자 (무신사 스탠다드) | None | Content Planning |
| 콘텐츠 에디터 (29CM)  | None | Content Planning |
| 키즈 MD  | None | MD |
| 키즈 상품기획 MD (무신사 스탠다드) | None | Planning MD |
| 패션 오프라인 영업 담당자 (무신사 트레이딩) | None | Sales |

#### 컬리 (`kurly`, greeting) — 미분류 56건 / 전체 69건

| title | occupation | job |
|---|---|---|
|  물류센터 자동화 설비 구축 Project Assistant Manager (계약직) | FC기획 | None |
| BX 디자이너 | 디자인/컨텐츠 | None |
| CRM 마케팅 리드 | 마케팅 | None |
| EHS 보건관리자 (김포) | EHS | None |
| EHS 안전관리자 | EHS | None |
| EHS 진단 Auditor | EHS | None |
| FC프로세스 개선 담당자 (송파) | FC기획 | None |
| HMR MD | MD | None |
| HRBP(HR Business Partner) | 인사 | None |
| HRIS 담당자 | 인사 | None |
| Talent Acquisition Partner (5~8년) | 인사 | None |
| 가공 MD | MD | None |
| 개인정보보호 담당자 | 보안 | None |
| 고객경험지원 담당자 | 고객서비스 | None |
| 광고 영업 담당자 (중대형 광고주 세일즈) | 영업 | None |
| 국내 뷰티PB 마케터 (7년 이상) | 마케팅 | None |
| 그로스 Product Manager (어필리에이트 제품) | 프로덕트 매니지먼트 | None |
| 네트워크 보안 솔루션 운영 담당자 | 보안 | None |
| 물류신사업 사업관리 담당자 | 영업 | None |
| 미국 이커머스 마케터 | 마케팅 | None |
| 뷰티 MD | MD | None |
| 뷰티 MD 운영지원 담당자 (계약직) | MD | None |
| 뷰티 PB상품기획 담당자 | 영업 | None |
| 뷰티 에디터 | 디자인/컨텐츠 | None |
| 뷰티/패션 프로모션 기획 마케터 (3년 이상) | 마케팅 | None |
| 브랜드컨텐츠 기획 담당자 | 디자인/컨텐츠 | None |
| 사내 변호사 (Compliance) | 법무 | None |
| 사내 변호사 (개인정보 보호) | 법무 | None |
| 상세페이지 컨텐츠 디자이너 | 디자인/컨텐츠 | None |
| 생활 MD (주방/리빙) | MD | None |
| 생활 MD 운영지원 (계약직) | MD | None |
| 소셜 미디어 마케터(SNS) | 마케팅 | None |
| 시니어 그로스 마케터 | 마케팅 | None |
| 오프라인 스토어 BX 디자이너 | 디자인/컨텐츠 | None |
| 오프라인 스토어 마케팅기획 담당자 | 영업 | None |
| 오프라인 스토어 영업기획 담당자 | 영업 | None |
| 온라인 마케팅/프로모션 디자이너 | 디자인/컨텐츠 | None |
| 유저마케팅 그로스 마케터 (CRM기획 및 운영) | 마케팅 | None |
| 인사기획 담당자  | 인사 | None |
| 재무기획 담당자 (Strategic Finance) | Finance | None |
| 정보보호 정책 담당자 | 보안 | None |
| 주니어 뷰티 MD  | MD | None |
| 캠페인 매니저(브랜딩/프로모션) | 마케팅 | None |
| 커머스 Product Manager (상품) | 프로덕트 매니지먼트 | None |
| 커머스 Product Manager (홈/전시) | 프로덕트 매니지먼트 | None |
| 커머스사업 B2G 영업 담당자 | 영업 | None |
| 커머스사업 B2G 운영지원 담당자 (계약직) | 영업 | None |
| 컨텐츠 디자이너 (계약직) | 디자인/컨텐츠 | None |
| 패션 컨텐츠 디자이너 (계약직) | 디자인/컨텐츠 | None |
| 퍼포먼스 마케터 | 마케팅 | None |
| 퍼포먼스 마케터(UA프로모션 기획) | 마케팅 | None |
| 포장기획 담당자 (송파) | FC기획 | None |
| 푸드 에디터 | 디자인/컨텐츠 | None |
| 프로덕트 디자인 그룹장 | 프로덕트 디자인 | None |
| 프로모션 기획 마케터 (3년 이상) | 마케팅 | None |
| 핀테크 정보보호 관리자 | 보안 | None |

#### 캐치테이블 (`catchtable`, greeting) — 미분류 37건 / 전체 41건

| title | occupation | job |
|---|---|---|
| B2B Front-end Developer | Engineering | None |
| B2B 매장 영업 담당자 | Business & Sales | None |
| B2B 매장 영업 담당자 (계약직/정규직 전환 기회) | Business & Sales | None |
| B2B 매장 영업 인턴 (6개월/정규직 전환 기회) | Business & Sales | None |
| B2B 오퍼레이션 매니저 (2년차 이상)  | None | None |
| B2B 온라인 세일즈 담당자 | Business & Sales | None |
| B2C Product Manager (Search&Discovery-PM) | Product (기획) | None |
| Brand Contents Assistant (6개월 인턴) | Marketing | None |
| Business Development Manager (사업기획/사업개발) | Business & Sales | None |
| Business Owner (BO, 사업기획/관리) | Business & Sales | None |
| FP&A(경영기획) 리소스 분석 인턴 (6개월) | Finance | None |
| Management Trainee - 운영 (채용연계형 인턴, 6개월) | Customer | None |
| Marketing Designer | Design | None |
| Product Designer (Search&Discovery) | Design | None |
| Recruiting Manager | People | None |
| Technical Operator (Global-Japan) | Customer | None |
| 광고 영업 담당자 | Business & Sales | None |
| 광고 영업 담당자 (계약직/정규직 전환 기회) | Business & Sales | None |
| 광고 영업 인턴 (6개월/정규직 전환 기회) | Business & Sales | None |
| 사외 추천 | None | None |
| 인재풀 등록 - Business & Sales | 인재풀 | None |
| 인재풀 등록 - Design | 인재풀 | None |
| 인재풀 등록 - Engineering | 인재풀 | None |
| 인재풀 등록 - Marketing | 인재풀 | None |
| 인재풀 등록 - People | 인재풀 | None |
| 인재풀 등록 - Product | 인재풀 | None |
| 인재풀 등록 - Strategy | 인재풀 | None |
| 인재풀 등록 - 페이 서비스 기획 및 개발 | 인재풀 | None |
| 일본 GTM TF 영업 | Business & Sales | None |
| 자금 및 회계 담당자 (0~3년차) | Finance | None |
| 총무 담당자 (1년 계약직) | People | None |
| 총무 담당자 (6개월/정규직 전환 기회) | People | None |
| 캐치테이블페이_결제서비스팀 PM/PO 팀장 | PM | None |
| 콘텐츠 마케터 | Marketing | None |
| 프로모션 마케터 | Marketing | None |
| 플랫폼 디자이너 (Platform Designer) | Design | None |
| 필드세일즈 영업 지원 (6개월 인턴)  | Business & Sales | None |

#### 카카오페이 (`kakaopay`, greeting) — 미분류 22건 / 전체 31건

| title | occupation | job |
|---|---|---|
| [계약직] 정보 협력 담당자 - 대외기관 정보 제공 지원 | 스탭 | None |
| [디지털자산] DevOps 엔지니어 - 클라우드 기반 블록체인 서비스 인프라 구축 & 운영 | 기술 | None |
| [스테이블코인] 프로덕트 매니저 - 스테이블코인 & 월렛 프로덕트 | 프로덕트 | None |
| [어시스턴트] 대출 마케팅 업무 운영 지원 | None | None |
| [어시스턴트] 오프라인 가맹점 심사 업무 지원  | None | None |
| [어시스턴트] 오프라인 결제 마케팅 업무 지원 | None | None |
| [어시스턴트] 오프라인 롱테일 결제환경 개선 프로젝트 현장 운영 담당 | None | None |
| [어시스턴트] 카카오페이 광고 운영 지원 | None | None |
| 내부 감사 담당자 | 스탭 | None |
| 사업 담당자 - 오프라인 결제 롱테일 채널 | 비즈니스 | None |
| 사업 담당자 - 해외 온라인 결제 | 비즈니스 | None |
| 인재 pool - 기술 | None | None |
| 인재 pool - 디자인 | None | None |
| 인재 pool - 비즈니스 | None | None |
| 인재 pool - 스탭 | None | None |
| 인재 pool - 프로덕트 | None | None |
| 컴플라이언스 담당자 - 개인(신용)정보 보호 | 스탭 | None |
| 프로덕트 매니저 - 결제 서비스 (시니어) | 프로덕트 | None |
| 프로덕트 매니저 - 광고 수익화 및 혜택 서비스 그로스 | 프로덕트 | None |
| 프로덕트 매니저 - 광고 프로덕트 | 프로덕트 | None |
| 프로덕트 엔지니어 - 사내 생산성 플랫폼 | 기술 | None |
| 프로젝트 매니저 - 프로젝트 관리 | 프로덕트 | None |

#### 여기어때 (`yeogieotdae`, greeting) — 미분류 25건 / 전체 26건

| title | occupation | job |
|---|---|---|
| AD Sales Manager [강원지역] | 영업 | None |
| AD Sales Manager [경남지역/계약직(1년)] | 영업 | None |
| AD Sales Manager [경북지역] | 영업 | None |
| AD Sales Manager [서울•인천•경기지역] | 영업 | None |
| AD Sales Manager [제주지역] | 영업 | None |
| AD Sales Manager [충청지역/계약직(1년)] | 영업 | None |
| CRM Marketer | 마케팅 | None |
| Cloud Security & Tech Leader | 보안 | None |
| Contents Marketer | 마케팅 | None |
| DevOps Team Leader | 기술 | None |
| Enterprise Sales Manager | 영업 | None |
| Operations Manager [Enterprise Business] | 영업(운영/지원) | None |
| Pension Sales Manager [강원 담당/서울 근무] | 영업 | None |
| Photographer [Pension] | 디자인 | None |
| Privacy Team Leader | 보안 | None |
| Product Owner [상품/연동] | 프로덕트 | None |
| Product Owner [정산·재무·회계시스템] | 프로덕트 | None |
| Promotion Marketer [Sales Promotion] | 마케팅 | None |
| Security Engineer [모의해킹 및 취약점진단]  | 보안 | None |
| Site Reliability Engineer | 기술 | None |
| Strategic Planning Manager | 경영지원 | None |
| Tech Strategy Leader | 기술 | None |
| Technical Product Owner | 프로덕트 | None |
| UX Designer [Core UX] | 디자인 | None |
| ✈️ Talent Pool | (없음) | (없음) |

#### 카카오모빌리티 (`kakaomobility`, greeting) — 미분류 15건 / 전체 22건

| title | occupation | job |
|---|---|---|
| QA 엔지니어 | 기술 | QA |
| SLAM research scientist (R&D) | 기술 | 개발 |
| [Assistant] POI서비스팀 업무 보조 | 스탭 | Assistant |
| [Assistant] 영상콘텐츠팀 업무 보조 | 스탭 | Assistant |
| [Contract] 사업 운영지원 담당자 | 서비스사업 | 사업기획및운영 |
| [Contract] 자율주행 HW 테크니션 | 기술 | 개발 |
| [집중채용] 자율주행 Research Engineer (Internship) | 기술 | 개발 |
| [집중채용] 자율주행 Research Engineer (MS) | 기술 | 개발 |
| [집중채용] 자율주행 Research Engineer (Ph.D) | 기술 | 개발 |
| 공간정보 기획자 | 서비스사업 | 서비스기획및운영 |
| 내비게이션 3D 지도 렌더링 엔진 개발자 | 기술 | 개발 |
| 사내 변호사 | 스탭 | 법무 |
| 자율주행 SLAM 엔지니어 (R&D) | 기술 | 개발 |
| 자율주행 시스템 엔지니어 (R&D) | 기술 | 개발 |
| 자율주행 인증/규제 대응 담당자 | 서비스사업 | 사업기획및운영 |

#### 왓챠 (`watcha`, greeting) — 미분류 0건

#### SSG.COM (`ssg`, greeting) — 미분류 0건

#### 데브시스터즈 (`devsisters`, greeting) — 미분류 0건

#### 마이리얼트립 (`myrealtrip`, greeting) — 미분류 21건 / 전체 21건

| title | occupation | job |
|---|---|---|
| Flight실 항공사업팀 사업기획 매니저 | 사업개발/기획 | None |
| Global Stay실 Americas & EMEA팀 사업 개발 매니저 | 사업개발/기획 | None |
| Growth실 Ad Sales & Account Manager  | Sales | None |
| Growth실 인플루언서 마케팅 매니저(신입) | 마케팅 | None |
| T&A실 글로벌 파트너 마케팅 매니저 | 마케팅 | None |
| T&A실 글로벌 파트너 전략 매니저 (Global Partnership Strategy Manager) | 사업개발/기획 | None |
| T&A실 미주·대양주 사업개발 매니저 | 사업개발/기획 | None |
| T&A실 사업 개발 매니저(신입) | 사업개발/기획 | None |
| T&A실 유럽팀 사업개발 매니저 | 사업개발/기획 | None |
| T&A실 중화권 사업개발 매니저 (중국어 가능자 우대) | 사업개발/기획 | None |
| [AICX] 비항공지원팀 파트리더 (정규직)  | 고객지원 | None |
| [AICX] 항공응대 매니저  | 항공 | None |
| 국내 T&A팀 팀장 | 사업개발/기획 | None |
| 국내숙박실 국내사업 Account Manager | Sales | None |
| 웰니스실 메디컬팀 B2B 제휴 영업 매니저  | Sales | None |
| 웰니스실 뷰티웰니스팀 B2B 제휴 영업 매니저 | Sales | None |
| 인재풀 | None | None |
| 재무관리실 경영관리팀 IR Manager | 재무/회계 | None |
| 정보보안실 보안 분석&대응 매니저 | 정보보안 | None |
| 정보보안실 보안취약점 진단 매니저 | 정보보안 | None |
| 패키지실 신사업 팀장 (맞춤여행) | 사업개발/기획 | None |

#### 리멤버 (`remember`, ninehire) — 미분류 15건 / 전체 19건

| title | occupation | job |
|---|---|---|
| <리멤버 인재풀 등록> | 전체 직군 | (없음) |
| Brand Designer | MKT & Brand | (없음) |
| [리멤버 자회사] 이안손앤컴퍼니 Client Services Associate | (없음) | (없음) |
| 광고사업 B2B Sales Manager | Business | (없음) |
| 광고운영팀 운영 Manager | Business | (없음) |
| 교육 기획 및 운영 담당자(계약직) | Business | (없음) |
| 대학·공공기관 Sales Manager | Business | (없음) |
| 리멤버 직속 헤드헌팅 PM | Business | (없음) |
| 브랜드마케팅팀 팀장 | (없음) | (없음) |
| 영업 SDR 담당자 (B2B 영업대행 신사업 초기멤버) | Business | (없음) |
| 인재솔루션팀 Account Manager | Business | (없음) |
| 재무실 자금 담당자 | Support | (없음) |
| 정보 보호 담당자 | Support | (없음) |
| 채용사업 B2B Sales Manager | Business | (없음) |
| 채용사업실 Strategic Client Partner | Business | (없음) |

#### 요기요 (`yogiyo`, ninehire) — 미분류 9건 / 전체 12건

| title | occupation | job |
|---|---|---|
| [Finance] 재무회계 팀원 (2년 이상) | Corporate Staff | Finance |
| [Logistics] Logistics 사업운영 담당자 (2년 이상) | Business | Logistics |
| [Logistics] 모니터링 운영 지원 담당자 (계약직, 6개월) | Business | Logistics |
| [Merchant Growth] MG전략 기획 담당자(3년 이상) | Business | Merchant Growth 전략 기획 |
| [Product] Customer Product Owner (3년 이상) | Product | PO |
| [Security] Information Security Manager (관리보안 담당자/5년 이상) | Tech | security policy |
| [Security] Privacy Manager (개인정보보호 담당자/5년 이상) | Tech | security policy |
| [마케팅본부] Payment 제휴 기획 담당자 (4년 이상) | Business | 페이먼트 제휴 |
| [마케팅본부] 구독 멤버십 기획 및 운영 담당자 (4년 이상) | Business | 구독멤버십 |

#### 네이버 (`naver`, custom) — 미분류 14건 / 전체 42건

| title | occupation | job |
|---|---|---|
| [NAVER Cloud] Global HR 운영 지원 (계약) | Corporate | Human Resources |
| [NAVER Cloud] 글로벌 사업기획 및 개발 담당자 (경력) | Service & Business | Business Development |
| [NAVER Cloud] 대외정책대응 및 분석개발 담당자 (경력) | Corporate | Strategic Communication |
| [NAVER Cloud] 클라우드 비즈니스 사업/영업/파트너 관리 (경력) | Service & Business | Business Development |
| [NAVER Cloud] 클라우드 사업개발/세일즈 분야 채용 (경력) | Service & Business | 어카운트/세일즈 |
| [NAVER I&S] 소프트웨어 자산·라이선스 운영·기획 담당 (경력) | Corporate | 자산관리 |
| [NAVER] N배송 WMS(Warehouse Management System) 기획 (경력) | Service & Business | Business Development |
| [NAVER] 광고 프로덕트 기획 경력 채용 | Service & Business | Product Development |
| [NAVER] 산업보건 담당 (경력) | Corporate | Risk Management |
| [NAVER] 스마트스토어 판매자센터 운영 (계약) | Service & Business | Business Development |
| [SNOW] UI/프로모션 디자이너 (계약직) | Design | Product Design |
| [SNOW] 남미(스페인어권) 컨텐츠 마케터 (계약직) | Service & Business | 공통 |
| [네이버랩스] Embedded System Hardware Engineer | Tech | Hardware |
| [네이버랩스] Robot System Software Engineer | Tech | 공통 |

#### 카카오뱅크 (`kakaobank`, custom) — 미분류 29건 / 전체 33건

| title | occupation | job |
|---|---|---|
| DevOps 엔지니어 | Engineering | (없음) |
| FDS 전기통신금융사기 모니터링 담당자 - 주간 (계약직) | Customer Service | (없음) |
| SM 사업 관리 및 유지보수 담당자 (계약직) | Engineering | (없음) |
| STR 모니터링 담당자 (계약직) | Compliance | (없음) |
| 가계대출 상품 기획 및 운영 담당자 | Service & Biz | (없음) |
| 가계대출 상품 기획 및 운영 담당자 (계약직) | Service & Biz | (없음) |
| 금융기술연구소 콘텐츠 담당자 (계약직) | Strategy | (없음) |
| 금융업무 지원 담당자 (계약직) | Customer Service | (없음) |
| 금융업무 지원 담당자 - 국가보훈대상자 전형 (계약직) | Customer Service | (없음) |
| 기술연구 사무 어시스턴트 (체험형 인턴) | Management | (없음) |
| 담보여신 운영 담당자 | Service & Biz | (없음) |
| 방카슈랑스 사업 기획 담당자 | Service & Biz | (없음) |
| 법인 여신 상품 기획 담당자 | Service & Biz | (없음) |
| 법인 여신 제도 기획 및 운영 담당자 | Service & Biz | (없음) |
| 부동산 감정평가 업무 담당자 | Service & Biz | (없음) |
| 사업 전략 및 제휴 담당자 - 투자 | Service & Biz | (없음) |
| 서비스 기획자 - 신사업 | Service & Biz | (없음) |
| 서비스 기획자 - 여신 | Service & Biz | (없음) |
| 수신 상품/서비스 운영 담당자 (계약직) | Service & Biz | (없음) |
| 수신제도(정책) 담당자 | Service & Biz | (없음) |
| 신사업(서베이) 운영 및 기획 어시스턴트 (체험형 인턴) | Service & Biz | (없음) |
| 여신 운영 업무 지원 담당자 (계약직) | Service & Biz | (없음) |
| 여신 전자등기 운영 담당자 (계약직) | Service & Biz | (없음) |
| 여신업무 도메인 개발자 | Core Banking | (없음) |
| 여신플랫폼사업 운영 담당자 (계약직) | Service & Biz | (없음) |
| 인증 라이선스/플랫폼 기획 담당자 | Service & Biz | (없음) |
| 인증서비스 기획 어시스턴트 (체험형 인턴) | Service & Biz | (없음) |
| 정산 업무 담당자 (계약직) | Management | (없음) |
| 카카오뱅크 인재풀 등록 | 상시채용 | (없음) |

#### 라인 (`line`, custom) — 미분류 50건 / 전체 72건

| title | occupation | job |
|---|---|---|
| Billing Operation Specialist | Planning | Product Management |
| Board Secretary | Corporate | Business Management |
| Business Development Manager / Associate Manager - Merchant Partnerships & Project Management(EPI) | Business & Sales | Sales |
| CS representative(EPI) | Corporate | Customer Support |
| Commerce Platform Operations Assistant | Business & Sales | Business Development |
| Compliance Officer(EPI) | Corporate | Governance |
| Corporate Affairs_Risk Management & Resilience Manager | Corporate | (없음) |
| Corporate Business_Commercial PMO | Business & Sales | Sales |
| Engineering_Service QA | Engineering | QA/SET |
| HR Lead(EPI) | Corporate | Human Resources |
| Internal Audit Lead(EPI) | Corporate | Internal Audit |
| LINE Pay Product Designer (Promotion/Visual) | Design | Product Design |
| LINE Pay Product Designer (UI/UX) | Design | Product Design |
| LINE Pay Senior Brand Designer | Design | VX Design |
| LINE Pay 星種子業務代表 | Business & Sales | Sales |
| LINE Pay 정보보안 담당자 | Corporate | Security |
| LINE Taiwan_Communications Manager | Corporate | (없음) |
| LINE Taiwan_Corporate Business_Ads Product Planning_Product Manager | Planning | Sales |
| LINE Taiwan_Enterprise Business_Senior Performance Consulting Manager | Business & Sales | Sales |
| LINE Taiwan_Global TODAY_Product Manager | Planning | Product Management |
| LINE Taiwan_Product & Strategy_Senior Display Ad Product Manager | Business & Sales | Sales |
| LINE Taiwan_Product Manager (Messenger & OA Products) | Planning | Product Management |
| LINE Taiwan_Security Engineer | Engineering | Security Engineering |
| LINE Taiwan_Senior Strategic Business Development Manager  | Business & Sales | Business Development |
| LINE WEBTOON - Global Typesetting Project Manager | Planning | Product Management |
| LINE Webtoon_Assistant Marketing Manager - Content & Growth | (없음) | Marketing |
| Legal Counsel | Corporate | Legal |
| Network Engineer(EPI) | Engineering | System Engineering |
| Network Engineer_KR-TW | Engineering | (없음) |
| Product Planner | Planning | Product Management |
| QA Engineer | Engineering | QA/SET |
| QA Engineer(EPI) | Engineering | QA/SET |
| Risk Management Specialist(EPI) | Corporate | Risk Management |
| Senior Cloud Security Engineer | Engineering | Security Engineering |
| Senior Security Operations & Incident Response Engineer (SOC/CSIRT) | Engineering | Security Engineering |
| Service Planner(EPI) | Planning | Project Management |
| Stock Affairs Staff | Corporate | Communications & Corporate Affairs |
| System Engineer_KR-TW | Engineering | System Engineering |
| TEC_LINE GIFTSHOP_Senior Business Growth Strategy & Operation Director | (없음) | (없음) |
| Technical Product Manager | Engineering | Tech Management |
| WEBTOON - Localization Assistant Manager / Manager (Thai Language QA) | Planning | Business Strategy |
| [LINE Pay Taiwan] Branding Team Lead / Senior Manager | Marketing & CS | Marketing |
| [LINE Pay Taiwan] Chinese - Korean Interpreter 中韓專業口筆譯人員 | Corporate | Communications & Corporate Affairs |
| [LINE Pay Taiwan] Chinese - Korean Translator | Corporate | Support |
| [LINE Pay Taiwan] Marketing Manager | Marketing & CS | Marketing |
| [LINE Pay Taiwan] SNS Content Marketer | Marketing & CS | Contents Production |
| [LINE Pay Taiwan] Senior Account Manager | Business & Sales | Marketing |
| [LINE Pay Taiwan] Tap Reward Operations Specialist | Planning | Business Management |
| [LINE Pay Taiwan] Video Content Specialist | Marketing & CS | Contents Production |
| 일본어 전문 통번역 프리랜서  | Corporate | Support |

#### 당근 (`daangn`, custom) — 미분류 23건 / 전체 48건

| title | occupation | job |
|---|---|---|
| AD Sales Manager - 광고 (세일즈, Agency) | Business | Sales |
| AD Sales Manager - 광고 (세일즈, Client) | Business | Sales |
| Account Manager (인턴) - 로컬 잡스 D - 2 | Business | Business |
| B2B Content Designer (계약직) - 광고 | Design | Design |
| Brand Designer (계약직) - 브랜딩 (서비스 브랜딩 & UI) | Design | Design |
| Business Development Manager - 당근페이 | Business | Business |
| Character Designer, Illustrator - 브랜딩 | Design | Design |
| DBA (Database Administrator) - 인프라 (DB) | Tech | Database Engineer |
| Design Engineer - 디자인 시스템 | Tech | Design Engineer |
| ER Manager - 경영지원 (피플) | Corporate | HR |
| HRBP - 경영지원 (피플) | Corporate | HR |
| Lead Security Engineer - 인프라 (보안, Offensive Security) | Tech | Security |
| Merchandiser (계약직) - 커머스 (신선식품) | Business | Business |
| Network Engineer - 인프라 (네트워크, Cloud) | Tech | Network |
| Product Designer (인턴) - 로컬 잡스 (Trust & Safety) | Design | Design |
| Product Designer - Cross Product Growth (Engagement Part) | Design | Design |
| Product Designer - 부동산 | Design | Design |
| Product Manager - 광고 (광고 상품) | Product Management | Product Manager |
| Product Manager - 당근페이 (Offline Payment) | Product Management | Product Manager |
| Product Operations Manager - 중고거래 | Product Management | Service Operations |
| Security Engineer - 인프라 (보안, Detection & Response) | Tech | Security |
| Trust & Safety Manager - 로컬 잡스 | Product Management | Service Operations |
| Trust & Safety Manager - 부동산 | Product Management | Service Operations |

#### 티빙 (`tving`, custom) — 미분류 2건 / 전체 3건

| title | occupation | job |
|---|---|---|
| Agency Partner Team Lead | 일반직군 | (없음) |
| 자금담당자 | 일반직군 | (없음) |

#### 채널톡 (`channeltalk`, custom) — 미분류 37건 / 전체 43건

| title | occupation | job |
|---|---|---|
| Business Development Specialist | Sales / Business | (없음) |
| CEO Staff | Strategy / Business Ops | (없음) |
| CX Team Leader | Strategy / Business Ops | (없음) |
| Chief Information Security Officer | Corporate | (없음) |
| Customer Experience Specialist | Strategy / Business Ops | (없음) |
| DevOps Engineer | Engineering | (없음) |
| Engineering Team, 영상  PD | Engineering | (없음) |
| Enterprise, Sales Account Executive | Sales / Business | (없음) |
| Enterprise, Sales Manager (Team Lead) | Sales / Business | (없음) |
| FP&A Manager (Team Lead) | Talent Pool | (없음) |
| Forward Deployed Engineer | Engineering | (없음) |
| GTM Specialist (Founding Member), San Francisco | US - Business | (없음) |
| Growth Marketer | Sales / Business | (없음) |
| Lead Product Manager | Product / Design | (없음) |
| Machine Learning Engineer (Model Training) | Engineering | (없음) |
| Marketing Specialist | Sales / Business | (없음) |
| Mid-Market, Account Management Specialist | Sales / Business | (없음) |
| Mid-Market, Sales Account Executive | Sales / Business | (없음) |
| Mid-Market, Sales Development Representative | Sales / Business | (없음) |
| Product Designer | Product / Design | (없음) |
| Product Designer, Senior | Product / Design | (없음) |
| Product Designer, Staff | Product / Design | (없음) |
| Product Manager (PM) | Product / Design | (없음) |
| Recruiting Coordinator | Corporate | (없음) |
| SMB Account Executive | Sales / Business | (없음) |
| SMB Account Executive Manager, Team Lead | Sales / Business | (없음) |
| Sales Engineer | Engineering | (없음) |
| Sales Intern | Sales / Business | (없음) |
| Sales Manager (Team Lead) | Sales / Business | (없음) |
| Sales Operations Analyst | Strategy / Business Ops | (없음) |
| Sales Specialist (Public Sector) | Sales / Business | (없음) |
| Security Engineer | Engineering | (없음) |
| Senior Recruiter | Corporate | (없음) |
| Software Engineer | Engineering | (없음) |
| Software Engineer, Senior | Engineering | (없음) |
| Strategy Specialist | Strategy / Business Ops | (없음) |
| Treasury (Senior manager) | Talent Pool | (없음) |

#### 뱅크샐러드 (`banksalad`, custom) — 미분류 8건 / 전체 9건

| title | occupation | job |
|---|---|---|
| Contents Marketer (계약직) | 마케팅 | 마케팅 |
| Senior People & Culture Manager (인사 담당자) | 경영관리 | 경영관리 |
| [초기멤버] Insurance Solution Coach (보험 솔루션 팀 코치) | 보험 GA | 보험 GA |
| [초기멤버] Product Manager (프로덕트 매니저, 보험) | 제품기획 | 제품기획 |
| [초기멤버] [리더십] Product Lead (프로덕트 리드, 광고) | 제품기획 | 제품기획 |
| [최초채용] [리더십] Head of Business (사업총괄) | 세일즈 | 세일즈 |
| [최초채용] [리더십] Head of Product | 제품기획 | 제품기획 |
| [최초채용] [리더십] Platform Product Lead (플랫폼 프로덕트 리드) | 제품기획 | 제품기획 |

#### 하이퍼커넥트 (`hyperconnect`, custom) — 미분류 4건 / 전체 12건

| title | occupation | job |
|---|---|---|
| Accountant (1년 6개월 계약직) | Management | (없음) |
| Product Designer, International Growth (Tinder Seoul) | Tinder Seoul | (없음) |
| Product Manager (Azar) | PM | (없음) |
| Tinder Marketing Manager (2-year Contractor, 육아휴직 대체) | Tinder Seoul | (없음) |

#### 쏘카 (`socar`, custom) — 미분류 20건 / 전체 29건

| title | occupation | job |
|---|---|---|
| CS운영기획 매니저 | 서비스기획 | (없음) |
| HR Generalist (급여/인사운영) | 경영/전략 | (없음) |
| HRBP (HR Business Partner) | 경영/전략 | (없음) |
| IR 매니저 | 경영/전략 | (없음) |
| [계약직] 서비스 운영 매니저(쏘카구독) | 사업/운영 | (없음) |
| [계약직] 외국인 응대 현장 운영 | 사업/운영 | (없음) |
| [인턴] 제주사업팀  | 사업/운영 | (없음) |
| 고객센터 WFM 매니저 (Workforce Management) | 서비스기획 | (없음) |
| 그로스 마케터 (퍼포먼스/시니어) | 홍보/마케팅 | (없음) |
| 내부회계관리제도 운영 담당자 | 공통 | (없음) |
| 모두의주차장 PO(Product Owner) | 서비스기획 | (없음) |
| 사업기획자/시니어PO | 사업/운영 | (없음) |
| 상품기획 매니저(쏘카신구독) | 사업/운영 | (없음) |
| 정보보호 및 보안 엔지니어 | 경영/전략 | (없음) |
| 제주사업팀 사업운영 매니저 | 사업/운영 | (없음) |
| 차량 서비스 운영 매니저 | 사업/운영 | (없음) |
| 카셰어링 거점운영 (파트너십) 매니저 | 사업/운영 | (없음) |
| 카셰어링 사업개발 매니저 | 사업/운영 | (없음) |
| 프로덕트 디자이너 (PD) | 공통 | (없음) |
| 플릿 운영(fleet operation) 및 자산 관리 매니저 | 사업/운영 | (없음) |

#### 카카오 (`kakao`, custom) — 미분류 40건 / 전체 64건

| title | occupation | job |
|---|---|---|
| IR 매니저 (경력) | 스태프 | (없음) |
| Interaction Designer (경력) | 디자인 | (없음) |
| Shareholder Communication 매니저 (경력) | 스태프 | (없음) |
| [공동체] (계약직) 정보 협력 담당자 - 대외기관 정보 제공 지원 | 스태프 | (없음) |
| [공동체] 카카오게임즈 MMORPG 마케팅PM 영입 | 서비스비즈 | (없음) |
| [공동체] 카카오게임즈 게임 기술PM 영입 | 테크 | (없음) |
| [공동체] 카카오게임즈 서브컬처 마케팅PM 영입 | 서비스비즈 | (없음) |
| [공동체] 카카오모빌리티 QA 엔지니어 | 테크 | (없음) |
| [공동체] 카카오모빌리티 SLAM research scientist (R&D) | 테크 | (없음) |
| [공동체] 카카오모빌리티 공간정보 기획자 | 서비스비즈 | (없음) |
| [공동체] 카카오모빌리티 내비게이션 3D 지도 렌더링 엔진 개발자 | 테크 | (없음) |
| [공동체] 카카오모빌리티 사내 변호사 | 스태프 | (없음) |
| [공동체] 카카오모빌리티 사업 운영지원 담당자 | 서비스비즈 | (없음) |
| [공동체] 카카오모빌리티 자율주행 HW 테크니션 | 테크 | (없음) |
| [공동체] 카카오모빌리티 자율주행 SLAM 엔지니어 (R&D) | 테크 | (없음) |
| [공동체] 카카오모빌리티 자율주행 시스템 엔지니어 (R&D) | 테크 | (없음) |
| [공동체] 카카오모빌리티 자율주행 인증/규제 대응 담당자 | 서비스비즈 | (없음) |
| [공동체] 카카오페이 DevOps 엔지니어 - 클라우드 기반 블록체인 서비스 인프라 구축 & 운영 | 테크 | (없음) |
| [공동체] 카카오페이 사업 담당자 - 오프라인 결제 롱테일 채널 | 서비스비즈 | (없음) |
| [공동체] 카카오페이 사업 담당자 - 해외 온라인 결제 | 서비스비즈 | (없음) |
| [공동체] 카카오페이 프로덕트 매니저 - 결제 서비스 (시니어) | 서비스비즈 | (없음) |
| [공동체] 카카오페이 프로덕트 매니저 - 광고 수익화 및 혜택 서비스 그로스 | 서비스비즈 | (없음) |
| [공동체] 카카오페이 프로덕트 매니저 - 스테이블코인 & 월렛 프로덕트 | 서비스비즈 | (없음) |
| [공동체] 카카오페이 프로젝트 매니저 - 프로젝트 관리 | 서비스비즈 | (없음) |
| [공동체] 카카오페이손해보험 Business Operations (사업제휴) 담당자 | 서비스비즈 | (없음) |
| [공동체] 카카오페이손해보험 PR·콘텐츠 어시스턴트 | 서비스비즈 | (없음) |
| [공동체] 카카오페이손해보험 시스템 개발·운영 엔지니어 | 테크 | (없음) |
| 노사 전략 및 기획 담당자 (경력) | 스태프 | (없음) |
| 로컬임팩트 마케팅 운영_어시스턴트 | 스태프 | (없음) |
| 서비스/플랫폼 QA 담당자 (경력) | 테크 | QA |
| 인플루언서 제휴_어시스턴트 | 서비스비즈 | (없음) |
| 직매입 물류 기획 및 운영 관리자 (경력) | 서비스비즈 | (없음) |
| 직매입 수요예측 및 재고계획 관리자 (경력) | 서비스비즈 | (없음) |
| 카카오 교육 프로그램 운영 지원_어시스턴트 | 스태프 | (없음) |
| 카카오메이커스 MD_어시스턴트 | 서비스비즈 | (없음) |
| 카카오비즈니스 파트너 플랫폼 PM (경력) | 서비스비즈 | (없음) |
| 카카오톡 예약하기 서비스 마케팅 운영_어시스턴트 | 서비스비즈 | (없음) |
| 카카오프렌즈 공간디자인 VMD_어시스턴트 | 디자인 | (없음) |
| 커머스 식품 QA 담당자 (신입/경력) | 서비스비즈 | (없음) |
| 톡딜 뷰티CM_어시스턴트 | 서비스비즈 | (없음) |

#### 토스 (`toss`, custom) — 미분류 335건 / 전체 473건

| title | occupation | job |
|---|---|---|
|  Privacy Protection Team Leader | Information Security | (없음) |
| AIOps Platform Engineer | Infra | (없음) |
| AML Manager (STR 기획 및 운영) | AML | STR 기획 및 운영 |
| AML Monitoring Manager  | AML | (없음) |
| AML Operations Manager (Global) | AML | (없음) |
| AML Operations Specialist | AML | (없음) |
| AML Specialist | AML | (없음) |
| AML/CFT Manager (Gerente de PLD/FT, Toss Brazil) | AML | (없음) |
| Account Management Specialist | Sales Support | (없음) |
| Account Manager (FacePay) | Sales | FacePay |
| Account Manager (FacePay/Merchant Growth) | Sales | FacePay (Merchant Growth) |
| Account Manager (광고) | Sales | 광고 |
| Account Manager (플랫폼 제휴/사업개발) | Sales | Account Manger |
| Accounting Admin | Accounting | (없음) |
| Accounting Manager (연결) | Accounting | 연결 |
| Analyst | Securities | (없음) |
| Anti-Fraud Manager | Risk | (없음) |
| Banking Product Owner (SOHO 여신) | Product Ownership | SOHO 여신 |
| Barista | Community | (없음) |
| Barista Support | Community | (없음) |
| Brand Manager (Content) | Marketing | Content |
| Brand Manager (Event) | Marketing | Event |
| Brand Manager (Marketing) | Marketing | Content |
| Business Analyst | Sales Support | (없음) |
| Business Analyst | Strategy | (없음) |
| Business Content Marketing Manager | Marketing | 앱인토스 |
| Business Development Representative | Sales | (없음) |
| Business Enablement Manager | Sales Support | (없음) |
| Business FP&A Manager | Finance | (없음) |
| Business Marketing Manager (Field Marketer) | Marketing | (없음) |
| Business Marketing Specialist | Marketing | (없음) |
| Business Operations Assistant | Sales Support | (없음) |
| Business Operations Assistant (Internship) | (없음) | (없음) |
| Business Operations Manager | (없음) | (없음) |
| Business Operations Manager | (없음) | (없음) |
| Business Operations Specialist | Sales Support | (없음) |
| Business Partnership Manager | Sales | 공통 |
| Business Public Affairs Manager | PR | (없음) |
| CA Operations Manager (예금압류&추심) | (없음) | (없음) |
| CEO Staff | HR | (없음) |
| CS Risk Manager | Risk | (없음) |
| CX Planning Manager | Strategy | (없음) |
| Call Infra Engineer (IPCC, AICC) | Infra | (없음) |
| Call Sales Assistant | Sales Support | (없음) |
| Category MD (뷰티) | Sales | 쇼핑 MD |
| Category MD (생활 - 가구/홈데코/주방용품) | Sales | 쇼핑 MD |
| Category MD (신선식품 - 과일, 채소류) | Sales | 쇼핑 MD |
| Channel Sales Manager | Sales | 채널영업 |
| Client Solutions Manager | Sales Support | (없음) |
| Client Solutions Manager (AppInToss) | Sales Support | (없음) |
| Collections Manager | Finance | (없음) |
| Collections Manager (상각) | Bank | 상각 |
| Collections Specialist (대위변제) | Bank | 대위변제 |
| Commission Manager | Insurance | (없음) |
| Communications Manager | PR | (없음) |
| Community Operations Manager (Japan) | Product Operations | (없음) |
| Community Specialist | Community | (없음) |
| Compensation Manager (Planning) | Compensation & Benefit | (없음) |
| Compliance Manager | Compliance | (없음) |
| Compliance Manager (모니터링/점검) | Compliance | (없음) |
| Consumer Protection Manager (민원대응) | Customer | 민원대응 |
| Consumer Protection Manager (비예금상품) | Compliance | 비예금상품 |
| Consumer Protection Manager (정책/기획) | Compliance | 정책/기획 |
| Content Producer | Contents | (없음) |
| Content Specialist (Editing) | Marketing | (없음) |
| Core FP&A Manager | Finance | (없음) |
| Corp Legal Team Leader | Leadership | (없음) |
| Corporate Credit Rating Team Leader | Risk | (없음) |
| Corporate Development Manager | Corp.dev | (없음) |
| Corporate Development Team Leader  | Corp.dev | (없음) |
| Corporate Finance and IR Intern | IR | (없음) |
| Corporate Public Affairs Manager | PR | (없음) |
| Credit Rating Modeler | Risk | (없음) |
| Culture Business Partner | Culture | (없음) |
| Culture Coordinator | HR | (없음) |
| Customer Banking Specialist | Bank | 대면센터 |
| Customer Guider (기본 문의 응대 · 9 to 6 근무) | Customer | (없음) |
| Customer Guider (외국인 상담원 - 중국어/우즈베크어/베트남어) | Customer | (없음) |
| Customer Guider (토스인컴 전화/채팅상담) | Customer | (없음) |
| Customer Hero 페이먼츠 (평일 근무) | Customer | (없음) |
| Customer Hero 플랫폼/증권 (정착지원금 50만원) | Customer | (없음) |
| Customer Hero 플레이스 (9-6 고정근무 \| 입사축하금 50만원) | Customer | (없음) |
| Customer Protection Manager (FDS) | Compliance | FDS |
| Customer Protection Manager (소비자보호) | Compliance | (없음) |
| Customer Success Manager | Customer | (없음) |
| Customer Success Specialist | Customer | (없음) |
| Design Staff (Product Designer) | Product Design | 일반 |
| Design System Migration Assistant | Platform Design | 공통 |
| DevOps Engineer [산업기능요원/전문연구요원] | 병역특례 | (없음) |
| Developer Relations Manager | Technical Excellence | (없음) |
| Device Hardware Quality Engineer | QA | Manager |
| Device 관련 포지션 인재풀 등록 | Device | (없음) |
| Direct Sales Associate | Sales Support | (없음) |
| Direct Sales Manager | Sales | (없음) |
| Enterprise Marketing Manager | Marketing | (없음) |
| Equity Operations Manager (국내주식 운영관리) | Securities | (없음) |
| Executive Assistant | HR | CEO |
| Executive Assistant | HR | (없음) |
| Finance Manager (Accounting) | Finance | Accounting |
| Finance Manager(Tax) | Finance | Tax |
| Financial Compliance Manager (금융복합기업집단) | Finance | (없음) |
| Financial Systems Manager (SAP) | (없음) | SAP |
| GRC Manager (Global)  | Legal | (없음) |
| GRC Manager (금융복합기업집단)  | Legal | (없음) |
| General Affairs Assistant | GA | (없음) |
| General Affairs Assistant (신입/인턴) | GA | (없음) |
| General Affairs Manager | Finance | (없음) |
| General Affairs Manager | GA | 공통 |
| General Affairs Manager  | GA | 7년 이상 |
| General Affairs Specialist | GA | (없음) |
| General Affairs Specialist | GA | (없음) |
| General Affairs Specialist | GA | (없음) |
| General Affairs Specialist  | IT General Admin | (없음) |
| Global Beta Tester (Foreigner) | Product Operations | (없음) |
| Global Compensation Manager | Compensation & Benefit | (없음) |
| Global Finance Manager (Accounting) | Finance | Finance Execellence Manager |
| Global UX Researcher | UX | (없음) |
| HR Coordinator (보훈제한채용) | HR | (없음) |
| HR Operations Manager (BPO 사업 HR 체계·운영 담당) | HR | (없음) |
| HR Operations Manager (내부 조직 HR 체계·운영 담당) | HR | (없음) |
| HRBP | HR | (없음) |
| HRBP | HR | (없음) |
| HRBP | HR | (없음) |
| HRBP (Global) | HR | Global |
| IDC Assistant (단기계약직) | Infra | (없음) |
| IDC Infrastructure Engineer (Network & System)  | Infra | (없음) |
| IDC Manager | Infra | (없음) |
| IR Manager (공시/주총)  | IR | 공시/주총 |
| IR Operations Manager | Finance | (없음) |
| IT Assistant (단기계약직)(인재풀) | IT General Admin | (없음) |
| IT Assurance Manager | IT Planning | (없음) |
| IT Audit Manager | IT Planning | (없음) |
| IT Audit Manager | IT Planning | (없음) |
| IT Auditor | Compliance | (없음) |
| IT Governance Manager (BCP) | IT Planning | 거버넌스 |
| IT Manager | IT General Admin | (없음) |
| IT Manager | IT General Admin | (없음) |
| IT Manager (IT 및 콜 인프라 운영/IT 환경 기획) | IT General Admin | (없음) |
| IT Operations Specialist (Call Infra) | IT General Admin | (없음) |
| IT Planning Manager | IT Planning | 내부통제 |
| IT Planning Manager | IT Planning | PMO |
| IT Planning Manager (예산관리)  | IT Planning | 예산관리 |
| IT Planning Manager (자산관리)   | IT Planning | 자산관리 |
| IT Planning Team Leader | IT Planning | (없음) |
| IT SOX Manager | Finance | 내부회계 |
| IT Strategy Manager | IT Planning | (없음) |
| Information Security Manager (Global)  | Information Security | Global |
| Information Security Manager (보안 점검) | Information Security | 보안 점검 |
| Information Security Manager (보안정책) | Information Security | 보안정책 |
| Information Security Manager (정보보호 정책/기획 담당) | Information Security | 5년 미만 |
| Information Security Manager (정보보호 정책/기획 담당) | Information Security | 5년 이상 |
| Infrastructure Operations Engineer | Infra | (없음) |
| Internal Auditor (상시모니터링) | Compliance | 상시모니터링 |
| Internal Auditor (정보보호감사) | Compliance | 정보보호감사 |
| Internal Systems Engineer (MDM)  | IT General Admin | (없음) |
| KYC Operations Assistant | Customer | (없음) |
| KYC Specialist | Bank | (없음) |
| Leadership Talent Acquisition Manager | Recruiting | (없음) |
| Legal Counsel (Corporate)  | Legal | Corporate |
| Legal Counsel (Fintech) | Legal | Fintech |
| Legal Counsel (Global)  | Legal | Global |
| Legal Counsel (Platform) | Legal | Platform |
| Legal Counsel (공정거래) | Legal | 공정거래 |
| Legal Team Leader | Legal | (없음) |
| Loan Operations Manager | Bank | (없음) |
| Marketing Creative Assistant | Marketing | 공통 |
| Marketing Manager (B2B) | Marketing | B2B |
| Marketing Manager (Growth) | Marketing | Growth |
| Marketing Manager (Growth) | Marketing | Growth |
| Marketing Team Assistant (Internship) | Marketing | Operations |
| Merchant Onboarding Assistant (Internship) | Sales Support | 공통 |
| Merchant Onboarding Specialist  | Sales Support | 공통 |
| Network Engineer | Infra | Datacenter |
| Network Engineer | Infra | Cloud |
| Network Engineer (7년 이상) | Infra | (없음) |
| Network Engineer (Edge) | Infra | Edge |
| Network Security Engineer (5년 미만)  | Infra | 5년 미만 |
| Network Security Engineer (5년 이상) | Infra | 5년 이상 |
| Office Manager(부산) | GA | 공통 |
| Operations Enablement Assistant (Internship) | Sales | (없음) |
| Operations Enablement Specialist | Sales Support | 전담 운영 |
| Operations Manager (제품운영/인력운영) (인재풀) | Customer Service | 상시풀 운영 |
| Operations Manager (콘텐츠/제품운영) | Customer | (없음) |
| Operations Supporter (얼굴촬영/수집) | Customer | (없음) |
| Operations Supporter (인재풀) | Customer | 상시풀 운영 |
| Payment Software Engineer | Device | (없음) |
| People Systems Manager(Workday) | People System | (없음) |
| Platform Product Owner | Product Ownership | 공통 |
| Platform Product Owner | Product Ownership | 공통 |
| Platform Product Owner | Product Ownership | 공통 |
| Platform Product Owner (Blockchain) | Product Ownership | Blockchain |
| Platform Product Owner (Facepay) | Product Ownership | Facepay |
| Platform Product Owner (Global) | Product Ownership | 공통 |
| Privacy Manager | Information Security | 5년 미만 |
| Privacy Manager | Information Security | (없음) |
| Privacy Manager | Information Security | 5년 이상 |
| Privacy Manager | Information Security | 공통 |
| Privacy Manager (3년이하) | Information Security | 3년이하 |
| Privacy Manager (개인정보보호 담당자) | Information Security | 5년 이상 |
| Privacy Manager (개인정보보호 담당자) | Information Security | 5년 미만 |
| Privacy Manager(Global) | Information Security | Global |
| Privacy Operations Assistant | Information Security | (없음) |
| Privacy Operations Specialist | Information Security | (없음) |
| Product Design Assistant | Product Design | Product Design Assistant |
| Product Designer | Product Design | (없음) |
| Product Designer | Product Design | (없음) |
| Product Designer | Product Design | (없음) |
| Product Designer | Product Design | 일반 |
| Product Designer (Global)  | Product Design | Global |
| Product Designer (신입) | Product Design | (없음) |
| Product Excellence Manager (Strategy & Execution) | Product Ownership | (없음) |
| Product Manager | Product Ownership | 공통 |
| Product Manager (LLM) | Product Operations | (없음) |
| Product Operations Manager (Ads) | Product Ownership | Ads |
| Product Operations Manager (Growth) | Product Ownership | Growth |
| Product Owner | Product Ownership | 공통 |
| Product Owner | Product Ownership | 공통 |
| Product Owner | Product Ownership | 공통 |
| Product Owner (Global) | Product Ownership | 공통 |
| Product Owner (Growth) | Product Ownership | Growth |
| Product Owner (Growth) | Product Ownership | Growth |
| Product Owner (Vertical) | Product Ownership | Vertical |
| Product Owner (기업솔루션) | Product Ownership | 기업솔루션 |
| Product Owner (원장 Platform) | Product Ownership | 원장 Platform |
| Product Owner [Commerce] | Product Ownership | Product Owner |
| Project Staff (Product) | Product Ownership | (없음) |
| Project Staff (Tech) | Product Ownership | (없음) |
| Purchasing Manager | GA | 7년 이상 |
| QA Manager | QA | (없음) |
| QA Manager | QA | Manager |
| QA Manager | QA | Manager |
| QA Manager (10년 이상) | QA | Manager |
| QA Manager (5년 이상) | QA | (없음) |
| QA Manager (Product) | QA | Product |
| QA Manager(Platform) | QA | Platform |
| QA Team Leader | QA | Team Leader |
| Recruiting Assistant | Recruiting | (없음) |
| Recruiting Assistant | HR | (없음) |
| Recruiting Business Partner | Recruiting | (없음) |
| Recruiting Business Partner | Recruiting | (없음) |
| Recruiting Business Partner | Recruiting | (없음) |
| Recruiting Business Partner | Recruiting | (없음) |
| Recruiting Business Partner (BPO 사업 담당) | Recruiting | (없음) |
| Recruiting Partner Team Leader | Recruiting | (없음) |
| Retail Operations Manager (고객경험) | Customer | (없음) |
| Retail Operations Manager (금융사기방지) | Compliance | (없음) |
| Retail Operations Manager (연금) | Securities | (없음) |
| Retail Operations Manager (지점 업무 및 백오피스 운영) | Securities | (없음) |
| Risk Manager | (없음) | 공통 |
| Risk Manager | Risk | (없음) |
| SOX Manager  | Finance | 내부회계 |
| STR Monitoring Specialist | AML | (없음) |
| Sales Assistant (Internship) | Sales | 사무보조 |
| Sales Development Representative | Sales Support | (없음) |
| Sales Excellence Manager | Sales Support | 공통 |
| Sales Manager | Sales | 공통 |
| Sales Manager (Global) | Sales | Global |
| Sales Operations Specialist | Sales Support | 공통 |
| Sales Operations Specialist (Commerce) | Sales Support | (없음) |
| Sales Specialist (FacePay Merchant Growth) | Sales Support | (없음) |
| Sales Training Manager | Insurance | (없음) |
| Search Quality Operations Manager | Product Operations | (없음) |
| Search Quality Operations Team Leader | Product Operations | (없음) |
| Securities Settlement Manager (해외주식 - 3년 이상) | Securities | 해외주식 - 3년 이상 |
| Securities Settlement Manager (해외주식 - 주니어) | Securities | 해외주식 - 주니어 |
| Security Analyst | Security Engineering | (없음) |
| Security Audit Manager (정보보호 자체감사자) | Information Security | Security Audit Manager |
| Security Audit Manager (정보보호관리체계 및 기술 담당) | Information Security | Security Audit Manager |
| Security Audit Manager Team Leader (정보보호 자체감사자) | Information Security | Security Audit Manager |
| Security Engineer (네트워크 보안) | Security Engineering | (없음) |
| Security Engineer (시스템 보안) | Security Engineering | 시스템 보안 |
| Security Engineer (엔드포인트 보안) | Security Engineering | 엔드포인트 보안 |
| Security Engineer (이벤트 분석 / 사고 대응) | Security Engineering | (없음) |
| Security Engineer (이벤트 분석/사고 대응) | Security Engineering | (없음) |
| Security Engineer (클라우드 보안) | Security Engineering | (없음) |
| Security Engineer [산업기능요원/전문연구요원] | 병역특례 | (없음) |
| Security Engineer(보안 분석 플랫폼 운영) | Security Engineering | (없음) |
| Security Operations Specialist | Information Security | (없음) |
| Security Researcher | Security Engineering | 취약점 진단 & 모의해킹 |
| Security Researcher | Security Engineering | 오픈소스 보안 |
| Security Researcher (APT/인프라 모의해킹) | Security Engineering | (없음) |
| Security Researcher (모의해킹/취약점 분석) | Security Engineering | (없음) |
| Security Researcher [산업기능요원/전문연구요원] | 병역특례 | (없음) |
| Solution Account Manager | Sales | 솔루션 영업 |
| Strategic Account MD (패션) | Sales | 전략 MD |
| Strategic Finance Manager (FP&A / 10년 이상) | Finance | 10년 이상 |
| Strategic Finance Manager (FP&A) | Finance | FP&A |
| Strategy Manager | Strategy | (없음) |
| Strategy Manager  | Strategy | (없음) |
| Strategy Manager  | Strategy | 공통 |
| System Security Team Leader | Security Engineering | 시스템 보안 |
| Systems Engineer (GPU) | Infra | GPU |
| Systems Engineer (가상화) | Infra | (없음) |
| Talent Sourcer | Recruiting | (없음) |
| Tax Manager | Accounting | Tax |
| Technical Account Manager | Sales Support | (없음) |
| Technical Account Manager (Global) | Sales Support | Global |
| Technical Product Owner | Product Ownership | 공통 |
| Technical Product Owner (Commerce) | Product Ownership | Technical Product Owner |
| Technical Product Owner (공통) | Product Ownership | (없음) |
| Technical Product Owner [Search] | Product Ownership | Technical Product Owner |
| Technical Writer (Ads) | Technical Excellence | (없음) |
| UX Researcher | UX | 공통 |
| UX Researcher | UX | (없음) |
| UX Researcher | UX | (없음) |
| User Interview Assistant | UX | (없음) |
| User Interview Assistant | UX | (없음) |
| User Interview Assistant | UX | (없음) |
| Validation Manager (리스크 적합성 검증) | Risk | (없음) |
| Validation Manager (여신감리) | Risk | (없음) |
| Visual Designer | Brand Design | (없음) |
| Visual Designer | Brand Design | Graphic |
| Visual Designer | Brand Design | Brand |
| Visual Designer (Design System) | Platform Design | Design System |
| 계좌 도메인 운영 Manager  | Securities | (없음) |
| 금융거래정보 Assistant | Bank | (없음) |
| 금융사기대응 Specialist | Bank | (없음) |
| 법인영업 담당자 | Sales | 법인영업 |
| 보험업 관련 포지션 인재풀 등록 | Sales | (없음) |
| 보험총무(토스인슈어런스 직영)_인천 | Insurance | (없음) |
| 보훈특별채용 인재풀 등록 | All | (없음) |
| 부산센터 계약직 (상시 인재풀 운영) | Customer | 상시풀 운영 |
| 상담팀 리드 (외국인 상담 전담팀) | Customer Support | (없음) |
| 상담팀 리드 (토스플랫폼 전담팀) | Customer Support | (없음) |
| 수신 상품 Manager | Bank | (없음) |
| 안산 글로벌 라운지 세일즈 담당자 (Field Sales Specialist) | Sales Support | (없음) |
| 여신 상품 Manager (기업여신 심사) | Bank | 기업여신 심사 |
| 여신 제도 Manager | Bank | (없음) |
| 외환 상품 Manager (해외송금) | Product Ownership | 기업해외송금 |
| 이체/출납 도메인 운영 Manager  | Securities | (없음) |
| 자문 상품 운영 Manager (Wrap 운영) | Securities | (없음) |
| 토스인슈어런스 Product Designer 집중 채용 (~9/13) | Product Design | (없음) |
| 토스증권 Product Designer 집중 채용 (2년 이상) (~9/15) | Product Design | (없음) |
| 토스페이 청약심사 (팀원) | Customer | 청약심사_페이 |
| 토스페이먼츠 신사업 초기멤버 인재풀 등록 | All | (없음) |

### 1-2. 미분류 공고에 등장한 occupation 고유값 (빈도순)

| occupation | 건수 |
|---|---|
| (없음/None) | 167 |
| 마케팅 | 54 |
| IT | 32 |
| Product Ownership | 28 |
| Corporate | 23 |
| Sales | 23 |
| Engineering | 21 |
| 경영지원 | 21 |
| 서비스비즈 | 21 |
| Information Security | 20 |
| Sales Support | 20 |
| Business | 19 |
| Business & Sales | 19 |
| 디자인 | 19 |
| Customer | 18 |
| Service & Biz | 18 |
| 영업 | 18 |
| Marketing | 17 |
| Finance | 16 |
| Infra | 14 |
| 기술 | 14 |
| Design | 13 |
| Sales / Business | 13 |
| Security Engineering | 13 |
| HR | 12 |
| 물류 | 12 |
| Compliance | 11 |
| Bank | 10 |
| IT Planning | 10 |
| Product Design | 10 |
| 사업/운영 | 10 |
| 테크 | 10 |
| GA | 9 |
| Planning | 9 |
| QA | 9 |
| Recruiting | 9 |
| Securities | 9 |
| Tech | 9 |
| 디자인/컨텐츠 | 9 |
| 사업개발/기획 | 9 |
| Legal | 8 |
| 인재풀 | 8 |
| 프로덕트 | 8 |
| AML | 7 |
| IT General Admin | 7 |
| MD | 7 |
| Risk | 7 |
| Service & Business | 7 |
| UX | 7 |
| 보안 | 7 |
| 스태프 | 7 |
| Strategy | 6 |
| 스탭 | 6 |
| Product / Design | 5 |
| Product Management | 5 |
| Product Operations | 5 |
| Strategy / Business Ops | 5 |
| 경영지원(전략) | 5 |
| Customer Service | 4 |
| Marketing & CS | 4 |
| 경영/전략 | 4 |
| 경영지원(사업관리/재무) | 4 |
| 인사 | 4 |
| 제품기획 | 4 |
| Accounting | 3 |
| Brand Design | 3 |
| Community | 3 |
| EHS | 3 |
| FC기획 | 3 |
| Insurance | 3 |
| Management | 3 |
| PR | 3 |
| People | 3 |
| 기타/특수 | 3 |
| 병역특례 | 3 |
| 서비스기획 | 3 |
| 서비스사업 | 3 |
| 프로덕트 매니지먼트 | 3 |
| All | 2 |
| Compensation & Benefit | 2 |
| Corp.dev | 2 |
| Customer Support | 2 |
| Device | 2 |
| IR | 2 |
| PM | 2 |
| Platform Design | 2 |
| Product | 2 |
| Support | 2 |
| Talent Pool | 2 |
| Technical Excellence | 2 |
| Tinder Seoul | 2 |
| 경영지원(인사) | 2 |
| 공통 | 2 |
| 법무 | 2 |
| 비즈니스 | 2 |
| 일반직군 | 2 |
| 정보보안 | 2 |
| 제조 | 2 |
| Contents | 1 |
| Core Banking | 1 |
| Corporate Staff | 1 |
| Culture | 1 |
| Leadership | 1 |
| MKT & Brand | 1 |
| People System | 1 |
| Product (기획) | 1 |
| Program Manager | 1 |
| US - Business | 1 |
| 건설/개발 | 1 |
| 경영관리 | 1 |
| 고객서비스 | 1 |
| 고객지원 | 1 |
| 보험 GA | 1 |
| 상시채용 | 1 |
| 세일즈 | 1 |
| 영업(운영/지원) | 1 |
| 재무/회계 | 1 |
| 전체 직군 | 1 |
| 프로덕트 디자인 | 1 |
| 항공 | 1 |
| 홍보/마케팅 | 1 |

### 1-3. 미분류 공고에 등장한 job 고유값 (빈도순)

| job | 건수 |
|---|---|
| (없음/None) | 551 |
| Product Management | 40 |
| 공통 | 26 |
| MD | 15 |
| Brand Marketing | 10 |
| 마케팅 | 10 |
| Product Design | 9 |
| Sales | 9 |
| 글로벌마케팅 | 9 |
| Production Management | 8 |
| 개발 | 8 |
| Global | 7 |
| BM | 6 |
| Business Development | 6 |
| Content Planning | 6 |
| Design | 6 |
| 품질관리 | 6 |
| Growth | 5 |
| Growth Marketing | 5 |
| SCM | 5 |
| Security Engineering | 5 |
| 브랜드마케팅 | 5 |
| 5년 미만 | 4 |
| 5년 이상 | 4 |
| Ad Business | 4 |
| BPO | 4 |
| Manager | 4 |
| Marketing | 4 |
| On-Site Marketing | 4 |
| VMD | 4 |
| 사업전략 | 4 |
| 제품기획 | 4 |
| Business | 3 |
| FC운영 | 3 |
| HRM | 3 |
| Planning MD | 3 |
| Program Manager | 3 |
| QA/SET | 3 |
| Research | 3 |
| SW QA | 3 |
| Security | 3 |
| Security Audit Manager | 3 |
| Service Operations | 3 |
| System Engineering | 3 |
| 구매 | 3 |
| 브랜드디자인 | 3 |
| 상시풀 운영 | 3 |
| 쇼핑 MD | 3 |
| 전략기획 | 3 |
| 7년 이상 | 2 |
| Assistant | 2 |
| Business Management | 2 |
| CX | 2 |
| Communications & Corporate Affairs | 2 |
| Content | 2 |
| Contents Production | 2 |
| Engineering Manager | 2 |
| Fashion Design | 2 |
| HR | 2 |
| Human Resources | 2 |
| IT전략 | 2 |
| Logistics | 2 |
| MD스토어기획 | 2 |
| Off-Line Planning | 2 |
| Platform | 2 |
| Product Manager | 2 |
| QA | 2 |
| Risk Management | 2 |
| Support | 2 |
| Tax | 2 |
| Technical Product Owner | 2 |
| security policy | 2 |
| 내부회계 | 2 |
| 비주얼디자인 | 2 |
| 사업관리 | 2 |
| 사업기획및운영 | 2 |
| 시스템 보안 | 2 |
| 온사이트마케팅 | 2 |
| 인테리어 | 2 |
| 일반 | 2 |
| 자산관리 | 2 |
| 정보보안/개인정보보호 | 2 |
| 퍼포먼스마케팅 | 2 |
| 10년 이상 | 1 |
| 3년이하 | 1 |
| Account Manger | 1 |
| Accounting | 1 |
| Ads | 1 |
| B2B | 1 |
| Blockchain | 1 |
| Brand | 1 |
| Business Analysis | 1 |
| Business Strategy | 1 |
| CEO | 1 |
| Cloud | 1 |
| Content Design | 1 |
| Corporate | 1 |
| Customer Support | 1 |
| DBA | 1 |
| Database Engineer | 1 |
| Datacenter | 1 |
| Design Engineer | 1 |
| Design System | 1 |
| DevRel | 1 |
| Edge | 1 |
| Event | 1 |
| FDS | 1 |
| FP&A | 1 |
| FacePay | 1 |
| FacePay (Merchant Growth) | 1 |
| Facepay | 1 |
| Finance | 1 |
| Finance Execellence Manager | 1 |
| Financial Planning | 1 |
| Fintech | 1 |
| GPU | 1 |
| General Affair | 1 |
| Global Marketing | 1 |
| Global Software Engineering | 1 |
| Governance | 1 |
| Graphic | 1 |
| Hardware | 1 |
| IP | 1 |
| Internal Audit | 1 |
| Legal | 1 |
| MD운영지원 | 1 |
| Marketing Design | 1 |
| Merchant Growth 전략 기획 | 1 |
| Network | 1 |
| Off-Line Operation | 1 |
| Operation | 1 |
| Operation Management | 1 |
| Operations | 1 |
| PMO | 1 |
| PO | 1 |
| Package Design | 1 |
| Photographer | 1 |
| Product | 1 |
| Product Design Assistant | 1 |
| Product Development | 1 |
| Product Owner | 1 |
| Program Management | 1 |
| Project Management | 1 |
| SAP | 1 |
| SOHO 여신 | 1 |
| STR 기획 및 운영 | 1 |
| Sales Planning | 1 |
| Security Management | 1 |
| Strategic Communication | 1 |
| TPM | 1 |
| Team Leader | 1 |
| Tech Management | 1 |
| VX Design | 1 |
| Vertical | 1 |
| Video Production | 1 |
| 거버넌스 | 1 |
| 경영관리 | 1 |
| 공시/주총 | 1 |
| 공정거래 | 1 |
| 광고 | 1 |
| 구독멤버십 | 1 |
| 글로벌MD | 1 |
| 글로벌사업 | 1 |
| 글로벌사업관리 | 1 |
| 글로벌사업전략 | 1 |
| 글로벌온사이트마케팅 | 1 |
| 글로벌플랫폼운영 | 1 |
| 기업솔루션 | 1 |
| 기업여신 심사 | 1 |
| 기업해외송금 | 1 |
| 내부통제 | 1 |
| 대면센터 | 1 |
| 대위변제 | 1 |
| 마케팅커뮤니케이션 | 1 |
| 민원대응 | 1 |
| 법무 | 1 |
| 법인영업 | 1 |
| 보안 점검 | 1 |
| 보안정책 | 1 |
| 보험 GA | 1 |
| 브랜딩마케팅 | 1 |
| 비예금상품 | 1 |
| 사무보조 | 1 |
| 사무지원 | 1 |
| 상각 | 1 |
| 상권개발 | 1 |
| 상시모니터링 | 1 |
| 상품운영 | 1 |
| 서비스기획및운영 | 1 |
| 세일즈 | 1 |
| 소셜콘텐츠마케팅 | 1 |
| 솔루션 영업 | 1 |
| 앱인토스 | 1 |
| 어카운트/세일즈 | 1 |
| 엔드포인트 보안 | 1 |
| 연결 | 1 |
| 예산관리 | 1 |
| 오픈소스 보안 | 1 |
| 원장 Platform | 1 |
| 전담 운영 | 1 |
| 전략 MD | 1 |
| 정보보호감사 | 1 |
| 정책/기획 | 1 |
| 제휴마케팅 | 1 |
| 채널영업 | 1 |
| 청약심사_페이 | 1 |
| 취약점 진단 & 모의해킹 | 1 |
| 페이먼트 제휴 | 1 |
| 프로모션마케팅 | 1 |
| 해외주식 - 3년 이상 | 1 |
| 해외주식 - 주니어 | 1 |

### 1-4. 미분류 공고의 title 토큰 빈도 (2회 이상)

| 토큰 | 공고 수 |
|---|---|
| Manager | 257 |
| 담당자 | 177 |
| Product | 112 |
| 운영 | 67 |
| Engineer | 58 |
| 계약직 | 57 |
| Operations | 46 |
| 기획 | 44 |
| Designer | 43 |
| Business | 40 |
| Security | 40 |
| Specialist | 40 |
| Sales | 39 |
| 매니저 | 39 |
| Assistant | 37 |
| MD | 34 |
| Global | 31 |
| 마케터 | 31 |
| 및 | 31 |
| 글로벌 | 28 |
| Owner | 27 |
| LINE | 24 |
| 공동체 | 24 |
| 광고 | 24 |
| 년 | 24 |
| Growth | 23 |
| Marketer | 22 |
| Team | 22 |
| IT | 21 |
| 무신사 | 21 |
| Account | 20 |
| Lead | 20 |
| Marketing | 20 |
| PB | 20 |
| Platform | 20 |
| 마케팅 | 20 |
| B2B | 19 |
| QA | 19 |
| 사업 | 19 |
| 이상 | 19 |
| 인재풀 | 19 |
| 스탠다드 | 18 |
| 경력 | 17 |
| 영업 | 17 |
| Leader | 16 |
| Senior | 16 |
| Taiwan | 16 |
| 관리 | 16 |
| 디자이너 | 16 |
| 서비스 | 16 |
| 어시스턴트 | 16 |
| 지원 | 16 |
| 프로덕트 | 15 |
| Customer | 14 |
| Partner | 14 |
| 등록 | 14 |
| 상품 | 14 |
| 오프라인 | 14 |
| 인턴 | 14 |
| A | 13 |
| Affairs | 13 |
| Pay | 13 |
| Privacy | 13 |
| 전략 | 13 |
| 콘텐츠 | 13 |
| 프로모션 | 13 |
| Brand | 12 |
| Network | 12 |
| Technical | 12 |
| 개발 | 12 |
| 보안 | 12 |
| 뷰티 | 12 |
| 엔지니어 | 12 |
| 플랫폼 | 12 |
| CM | 11 |
| Researcher | 11 |
| Retail | 11 |
| Strategy | 11 |
| 담당 | 11 |
| 자율주행 | 11 |
| D | 10 |
| Development | 10 |
| NAVER | 10 |
| PM | 10 |
| Planning | 10 |
| Recruiting | 10 |
| 결제 | 10 |
| 실 | 10 |
| 인프라 | 10 |
| 카카오모빌리티 | 10 |
| AD | 9 |
| Corporate | 9 |
| EPI | 9 |
| General | 9 |
| HR | 9 |
| Management | 9 |
| 개월 | 9 |
| 소싱 | 9 |
| 시니어 | 9 |
| 업무 | 9 |
| 커머스 | 9 |
| Cloud | 8 |
| Commerce | 8 |
| Content | 8 |
| Finance | 8 |
| Legal | 8 |
| Merchant | 8 |
| Program | 8 |
| Staff | 8 |
| System | 8 |
| 글로벌몰 | 8 |
| 여신 | 8 |
| 제휴 | 8 |
| 카카오페이 | 8 |
| 팀장 | 8 |
| BM | 7 |
| BPO | 7 |
| Beauty | 7 |
| HRBP | 7 |
| Information | 7 |
| Strategic | 7 |
| T | 7 |
| 그로스 | 7 |
| 무신사로지스틱스 | 7 |
| 브랜드 | 7 |
| 사업개발 | 7 |
| 상품기획 | 7 |
| 생산관리 | 7 |
| 신사업 | 7 |
| 온라인 | 7 |
| 정규직 | 7 |
| 정보보호 | 7 |
| 채용 | 7 |
| 퍼포먼스 | 7 |
| 품질관리 | 7 |
| AML | 6 |
| Audit | 6 |
| BX | 6 |
| Compliance | 6 |
| Counsel | 6 |
| Design | 6 |
| DevOps | 6 |
| Enterprise | 6 |
| Executive | 6 |
| FP | 6 |
| IR | 6 |
| Internship | 6 |
| Project | 6 |
| Protection | 6 |
| R | 6 |
| SCM | 6 |
| UX | 6 |
| VMD | 6 |
| Visual | 6 |
| 기획자 | 6 |
| 리테일미디어 | 6 |
| 물류센터 | 6 |
| 분석 | 6 |
| 세일즈 | 6 |
| 스토어 | 6 |
| 시스템 | 6 |
| 정산 | 6 |
| 정책 | 6 |
| 클라우드 | 6 |
| 화장품 | 6 |
| Analyst | 5 |
| CRM | 5 |
| CX | 5 |
| Client | 5 |
| Contents | 5 |
| Core | 5 |
| Engineering | 5 |
| Payment | 5 |
| Risk | 5 |
| Search | 5 |
| Software | 5 |
| Systems | 5 |
| US | 5 |
| User | 5 |
| pool | 5 |
| 개인정보보호 | 5 |
| 관리자 | 5 |
| 기회 | 5 |
| 대응 | 5 |
| 리드 | 5 |
| 물류 | 5 |
| 사내 | 5 |
| 사업관리 | 5 |
| 사업기획 | 5 |
| 신입 | 5 |
| 온사이트 | 5 |
| 운영지원 | 5 |
| 이벤트 | 5 |
| 인재 | 5 |
| 전환 | 5 |
| 채널 | 5 |
| 초기멤버 | 5 |
| 컨텐츠 | 5 |
| 파트너 | 5 |
| Accounting | 4 |
| Auditor | 4 |
| IP | 4 |
| Internal | 4 |
| Media | 4 |
| Operation | 4 |
| Research | 4 |
| SLAM | 4 |
| SNS | 4 |
| Talent | 4 |
| Tech | 4 |
| 구매 | 4 |
| 구축 | 4 |
| 디자인 | 4 |
| 리더십 | 4 |
| 매장 | 4 |
| 모니터링 | 4 |
| 변호사 | 4 |
| 브랜딩 | 4 |
| 사업전략 | 4 |
| 정보 | 4 |
| 주니어 | 4 |
| 캠페인 | 4 |
| 패션 | 4 |
| Ads | 3 |
| Associate | 3 |
| B2C | 3 |
| CS | 3 |
| Call | 3 |
| Category | 3 |
| Chinese | 3 |
| Collections | 3 |
| Consumer | 3 |
| Coordinator | 3 |
| Culture | 3 |
| DBA | 3 |
| Developer | 3 |
| Discovery | 3 |
| E-Commerce | 3 |
| EHS | 3 |
| Enablement | 3 |
| FacePay | 3 |
| Fashion | 3 |
| GTM | 3 |
| Guider | 3 |
| Hero | 3 |
| IDC | 3 |
| Infra | 3 |
| Interview | 3 |
| Korean | 3 |
| Logistics | 3 |
| Mid-Market | 3 |
| PD | 3 |
| PO | 3 |
| People | 3 |
| Performance | 3 |
| Promotion | 3 |
| Public | 3 |
| Quality | 3 |
| Representative | 3 |
| SAP | 3 |
| STR | 3 |
| Safety | 3 |
| Service | 3 |
| Trust | 3 |
| UI | 3 |
| mall | 3 |
| 개발자 | 3 |
| 국내 | 3 |
| 근무 | 3 |
| 기술 | 3 |
| 네트워크 | 3 |
| 도메인 | 3 |
| 디지털 | 3 |
| 로컬 | 3 |
| 롱테일 | 3 |
| 리멤버 | 3 |
| 멤버십 | 3 |
| 모의해킹 | 3 |
| 무신사페이먼츠 | 3 |
| 미주 | 3 |
| 보호 | 3 |
| 부동산 | 3 |
| 산업기능요원 | 3 |
| 생활 | 3 |
| 소셜 | 3 |
| 식품 | 3 |
| 어필리에이트 | 3 |
| 에디터 | 3 |
| 영입 | 3 |
| 외국인 | 3 |
| 이커머스 | 3 |
| 인증 | 3 |
| 일본 | 3 |
| 잡스 | 3 |
| 잡화 | 3 |
| 전략기획 | 3 |
| 전문연구요원 | 3 |
| 집중채용 | 3 |
| 체계 | 3 |
| 체험형 | 3 |
| 최초채용 | 3 |
| 카카오게임즈 | 3 |
| 카카오페이손해보험 | 3 |
| 카테고리 | 3 |
| 팀 | 3 |
| 프로세스 | 3 |
| 프로젝트 | 3 |
| AICX | 2 |
| AMD | 2 |
| Acquisition | 2 |
| Ad | 2 |
| Administrator | 2 |
| Agency | 2 |
| B2G | 2 |
| BIOHEAL | 2 |
| BOH | 2 |
| Banking | 2 |
| Barista | 2 |
| Buying | 2 |
| CEO | 2 |
| Catalog | 2 |
| Communications | 2 |
| Community | 2 |
| Compensation | 2 |
| Contract | 2 |
| Credit | 2 |
| DMP | 2 |
| Device | 2 |
| Direct | 2 |
| Display | 2 |
| Excellence | 2 |
| Experience | 2 |
| FDS | 2 |
| Field | 2 |
| Financial | 2 |
| Footwear | 2 |
| GRC | 2 |
| Generalist | 2 |
| HW | 2 |
| Hardware | 2 |
| Head | 2 |
| IMC | 2 |
| Infrastructure | 2 |
| Intern | 2 |
| Interpreter | 2 |
| Japan | 2 |
| KR-TW | 2 |
| KYC | 2 |
| Language | 2 |
| Monitoring | 2 |
| Officer | 2 |
| On-Site | 2 |
| Onboarding | 2 |
| Order | 2 |
| PMO | 2 |
| Partnership | 2 |
| Pension | 2 |
| Photographer | 2 |
| Planner | 2 |
| Rating | 2 |
| Relations | 2 |
| Response | 2 |
| SMB | 2 |
| SNOW | 2 |
| SOX | 2 |
| Securities | 2 |
| Settlement | 2 |
| Social | 2 |
| Solution | 2 |
| Solutions | 2 |
| Success | 2 |
| Supporter | 2 |
| TPM | 2 |
| Tax | 2 |
| Tinder | 2 |
| Training | 2 |
| Translator | 2 |
| Validation | 2 |
| WEBTOON | 2 |
| of | 2 |
| research | 2 |
| scientist | 2 |
| 가계대출 | 2 |
| 개선 | 2 |
| 검사 | 2 |
| 경영지원 | 2 |
| 계약 | 2 |
| 공간디자인 | 2 |
| 공간정보 | 2 |
| 관련 | 2 |
| 교육 | 2 |
| 규제 | 2 |
| 금융복합기업집단 | 2 |
| 금융업무 | 2 |
| 기반 | 2 |
| 기초화장품 | 2 |
| 내부 | 2 |
| 내비게이션 | 2 |
| 네이버랩스 | 2 |
| 년차 | 2 |
| 단기계약직 | 2 |
| 당근페이 | 2 |
| 대외기관 | 2 |
| 라이선스 | 2 |
| 렌더링 | 2 |
| 리테일 | 2 |
| 마케팅본부 | 2 |
| 만원 | 2 |
| 미국 | 2 |
| 바이오힐 | 2 |
| 바이오힐보 | 2 |
| 법인 | 2 |
| 보 | 2 |
| 보조 | 2 |
| 보험 | 2 |
| 블록체인 | 2 |
| 비즈니스 | 2 |
| 사고 | 2 |
| 사업운영 | 2 |
| 상담팀 | 2 |
| 서울 | 2 |
| 설계 | 2 |
| 소재 | 2 |
| 솔루션 | 2 |
| 송파 | 2 |
| 수신 | 2 |
| 수익화 | 2 |
| 수출 | 2 |
| 스테이블코인 | 2 |
| 스토어기획 | 2 |
| 신선식품 | 2 |
| 실행 | 2 |
| 심사 | 2 |
| 안성 | 2 |
| 양지 | 2 |
| 엔진 | 2 |
| 우먼즈 | 2 |
| 월렛 | 2 |
| 웰니스실 | 2 |
| 응대 | 2 |
| 인천 | 2 |
| 인테리어 | 2 |
| 인플루언서 | 2 |
| 입 | 2 |
| 입출고 | 2 |
| 자금 | 2 |
| 자산 | 2 |
| 자체감사자 | 2 |
| 재무기획 | 2 |
| 전담팀 | 2 |
| 점검 | 2 |
| 정보보안실 | 2 |
| 제공 | 2 |
| 제도 | 2 |
| 제작 | 2 |
| 제주사업팀 | 2 |
| 제품운영 | 2 |
| 중국어 | 2 |
| 중화권 | 2 |
| 지도 | 2 |
| 직매입 | 2 |
| 진단 | 2 |
| 집중 | 2 |
| 총무 | 2 |
| 출고 | 2 |
| 카셰어링 | 2 |
| 커머스사업 | 2 |
| 컬래버 | 2 |
| 키즈 | 2 |
| 테크니션 | 2 |
| 토스인슈어런스 | 2 |
| 통번역 | 2 |
| 통합 | 2 |
| 통합소싱 | 2 |
| 팀원 | 2 |
| 포지션 | 2 |
| 피플 | 2 |
| 해외 | 2 |
| 해외주식 | 2 |
| 현장 | 2 |
| 협력 | 2 |
| 혜택 | 2 |
| 홈 | 2 |

---

## 2. 구조화 분류 실패 + 제목 오탐 사례 — 우선 검토 대상

아래 조건을 **모두** 만족하는 건이다.

1. `occupation` / `job` 구조화 필드로는 카테고리가 배정되지 않았다.
   (값이 `null`이거나, `기술` · `Tech` · `개발`처럼 스펙 카테고리와 매칭되지 않는 값)
2. 제목 키워드 fallback이 걸려서 카테고리가 배정됐다. (`category_source = "title"`)

그리팅 + 나인하이어 전체 `deploy=true` 1405건을 재검사한 결과 **112건**이다.

`매칭 키워드` 열은 제목에서 실제로 걸린 스펙 키워드다.

| company_id | ATS | title | occupation | job | 배정된 카테고리 | 매칭 키워드 |
|---|---|---|---|---|---|---|
| `banksalad` | custom | [Frontier] AI Native Server Engineer (AI 네이티브 서버 엔지니어) | 테크 | 테크 | 서버·백엔드 | `서버`, `Server` |
| `catchtable` | greeting | 인재풀 등록 - Data | 인재풀 | None | 데이터·AI | `Data` |
| `channeltalk` | custom | AI Product Owner | Strategy / Business Ops | (없음) | 데이터·AI | `AI` |
| `channeltalk` | custom | AI-BPO AX Business Operation, Senior | Strategy / Business Ops | (없음) | 데이터·AI | `AI` |
| `channeltalk` | custom | AI-BPO Business Development, Senior | Strategy / Business Ops | (없음) | 데이터·AI | `AI` |
| `channeltalk` | custom | Applied AI Engineer | Engineering | (없음) | 데이터·AI | `AI` |
| `channeltalk` | custom | Data Analyst | Strategy / Business Ops | (없음) | 데이터·AI | `Data` |
| `channeltalk` | custom | 음성 데이터 라벨링(단기 계약직) | Engineering | (없음) | 데이터·AI | `데이터` |
| `daangn` | custom | Security Engineer - 인프라 (보안, AI Security) | Tech | Security | 데이터·AI | `AI` |
| `daangn` | custom | Software Engineer - 테크코어 (AI Platform) | Tech | Software Engineer | 데이터·AI | `AI` |
| `hyperconnect` | custom | Data Analyst (Azar) | Engineering | (없음) | 데이터·AI | `Data` |
| `hyperconnect` | custom | Product Manager (Match Group AI) | PM | (없음) | 데이터·AI | `AI` |
| `hyperconnect` | custom | Senior Data & Analytics Engineer (Azar) | Engineering | (없음) | 데이터·AI | `Data` |
| `hyperconnect` | custom | Senior Software Engineer, Backend — Seoul Studios (Tinder Seoul) | Tinder Seoul | (없음) | 서버·백엔드 | `Backend` |
| `kakao` | custom | AI 데이터 라벨링_어시스턴트 | 스태프 | (없음) | 데이터·AI | `데이터`, `AI` |
| `kakao` | custom | Data Analytics Engineer (경력) | 테크 | 기타 | 데이터·AI | `Data` |
| `kakao` | custom | [공동체] 카카오모빌리티 머신러닝 research scientist (R&D) | 테크 | (없음) | 데이터·AI | `머신러닝` |
| `kakao` | custom | [공동체] 카카오모빌리티 물류 & 에이전트 개발실 백엔드 개발자 | 테크 | (없음) | 서버·백엔드 | `백엔드` |
| `kakao` | custom | [공동체] 카카오모빌리티 백엔드 개발자(내비 서비스) | 테크 | (없음) | 서버·백엔드 | `백엔드` |
| `kakao` | custom | [공동체] 카카오모빌리티 백엔드 개발자(주차 플랫폼 개발) | 테크 | (없음) | 서버·백엔드 | `백엔드` |
| `kakao` | custom | [공동체] 카카오모빌리티 자율주행 AI Perception 엔지니어 (R&D) | 테크 | (없음) | 데이터·AI | `AI` |
| `kakao` | custom | [공동체] 카카오모빌리티 자율주행 AI 엔지니어 (R&D) | 테크 | (없음) | 데이터·AI | `AI` |
| `kakao` | custom | [공동체] 카카오페이 데이터 기획자 - 데이터 거버넌스 정책/시스템 | 테크 | (없음) | 데이터·AI | `데이터` |
| `kakao` | custom | [공동체] 카카오페이 데이터 엔지니어 - 데이터 플랫폼 | 테크 | (없음) | 데이터·AI | `데이터` |
| `kakao` | custom | [공동체] 카카오페이 마케터 - 데이터 마케팅 전략/실행 | 서비스비즈 | (없음) | 데이터·AI | `데이터` |
| `kakao` | custom | [공동체] 카카오페이 서버 개발자 - 결제 서비스 | 테크 | (없음) | 서버·백엔드 | `서버` |
| `kakao` | custom | [공동체] 카카오페이 서버 개발자 - 대출 중개/신용관리 서비스 | 테크 | (없음) | 서버·백엔드 | `서버` |
| `kakao` | custom | [공동체] 카카오페이 서버 개발자 - 데이터 플랫폼 | 테크 | (없음) | 서버·백엔드 | `서버` |
| `kakao` | custom | [공동체] 카카오페이 서버 개발자 - 스테이블코인 발행 & 유통 | 테크 | (없음) | 서버·백엔드 | `서버` |
| `kakao` | custom | [공동체] 카카오페이 서버 개발자 - 시니어/미성년 사용자 전용 서비스 | 테크 | (없음) | 서버·백엔드 | `서버` |
| `kakao` | custom | [공동체] 카카오페이 프론트엔드 개발자 - 자산 서비스 | 테크 | (없음) | 웹 프론트엔드 | `프론트엔드` |
| `kakao` | custom | [공동체] 카카오헬스케어 AI Native EHR 개발 | 테크 | (없음) | 데이터·AI | `AI` |
| `kakao` | custom | [공동체] 카카오헬스케어 Data Engineer(Healthcare) | 테크 | (없음) | 데이터·AI | `Data` |
| `kakaobank` | custom | 서비스 기획자 - 대화형 AI 서비스 | Service & Biz | (없음) | 데이터·AI | `AI` |
| `kakaomobility` | greeting | 머신러닝 research scientist (R&D) | 기술 | 개발 | 데이터·AI | `머신러닝` |
| `kakaomobility` | greeting | 물류 & 에이전트 개발실 백엔드 개발자 | 기술 | 개발 | 서버·백엔드 | `백엔드` |
| `kakaomobility` | greeting | 백엔드 개발자(공간정보 시스템 개발) | 기술 | 개발 | 서버·백엔드 | `백엔드` |
| `kakaomobility` | greeting | 백엔드 개발자(내비 서비스) | 기술 | 개발 | 서버·백엔드 | `백엔드` |
| `kakaomobility` | greeting | 백엔드 개발자(주차 플랫폼 개발)  | 기술 | 개발 | 서버·백엔드 | `백엔드` |
| `kakaomobility` | greeting | 자율주행 AI Perception 엔지니어 (R&D) | 기술 | 개발 | 데이터·AI | `AI` |
| `kakaomobility` | greeting | 자율주행 AI 엔지니어 (R&D) | 기술 | 개발 | 데이터·AI | `AI` |
| `kakaopay` | greeting | [스테이블코인] 서버 개발자 - 스테이블코인 발행 & 유통 | 기술 | None | 서버·백엔드 | `서버` |
| `kakaopay` | greeting | 데이터 기획자 - 데이터 거버넌스 정책/시스템 | 기술 | None | 데이터·AI | `데이터` |
| `kakaopay` | greeting | 데이터 엔지니어 - 데이터 플랫폼 | 기술 | None | 데이터·AI | `데이터` |
| `kakaopay` | greeting | 마케터 - 데이터 마케팅 전략/실행 | 마케팅 | None | 데이터·AI | `데이터` |
| `kakaopay` | greeting | 서버 개발자 - 결제 서비스 | 기술 | None | 서버·백엔드 | `서버` |
| `kakaopay` | greeting | 서버 개발자 - 대출 중개/신용관리 서비스 | 기술 | None | 서버·백엔드 | `서버` |
| `kakaopay` | greeting | 서버 개발자 - 데이터 플랫폼 | 기술 | None | 서버·백엔드 | `서버` |
| `kakaopay` | greeting | 서버 개발자 - 시니어/미성년 사용자 전용 서비스 | 기술 | None | 서버·백엔드 | `서버` |
| `kakaopay` | greeting | 프론트엔드 개발자 - 자산 서비스 | 기술 | None | 웹 프론트엔드 | `프론트엔드` |
| `kurly` | greeting | AI·검색 운영지원 담당 (체험형 인턴) | 프로덕트 매니지먼트 | None | 데이터·AI | `AI` |
| `kurly` | greeting | 커머스 백엔드 개발자 (상품/주문/회원/파트너) | 개발 | None | 서버·백엔드 | `백엔드` |
| `kurly` | greeting | 커머스 시니어 백엔드 개발자(홈/전시/광고) | 개발 | None | 서버·백엔드 | `백엔드` |
| `kurly` | greeting | 커머스 시니어 프론트엔드 개발자 | 개발 | None | 웹 프론트엔드 | `프론트엔드` |
| `kurly` | greeting | 커머스 주니어 프론트엔드 개발자 | 개발 | None | 웹 프론트엔드 | `프론트엔드` |
| `kurly` | greeting | 풀필먼트 백엔드 개발자 | 개발 | None | 서버·백엔드 | `백엔드` |
| `kurly` | greeting | 풀필먼트 시니어 프론트엔드 개발자 | 개발 | None | 웹 프론트엔드 | `프론트엔드` |
| `kurly` | greeting | 풀필먼트 주니어 프론트엔드 개발자 | 개발 | None | 웹 프론트엔드 | `프론트엔드` |
| `kurly` | greeting | 핀테크 백엔드 개발자 (결제) | 개발 | None | 서버·백엔드 | `백엔드` |
| `kurly` | greeting | 핀테크 프론트엔드 개발자 (결제) | 개발 | None | 웹 프론트엔드 | `프론트엔드` |
| `line` | custom | AI Ad platform PM | Planning | Product Management | 데이터·AI | `AI` |
| `line` | custom | AI SaaS Sales & Business Development Manager | Business & Sales | Business Development | 데이터·AI | `AI` |
| `line` | custom | Engineering_Senior Android Engineer | Engineering | (없음) | 모바일 | `Android` |
| `line` | custom | LINE Taiwan_Senior Product Manager (AI Products) | Planning | Product Management | 데이터·AI | `AI` |
| `line` | custom | Platform Server QA Engineer | Engineering | QA/SET | 서버·백엔드 | `Server` |
| `naver` | custom | [NAVER Cloud] 네이버 클라우드 플랫폼(NCP) IaaS/AI Factory 상품 기획 (경력) | Service & Business | Product Development | 데이터·AI | `AI` |
| `naver` | custom | [네이버웹툰] AI 서비스 기획 (체험형 인턴) | Service & Business | Product Development | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] Ads Design 영상 디자이너 (계약직) | Design | Visual Comm. & Brand Design | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] Agency Partner (경력) | Service & Business | Business Development | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] Brand Marketing 영상 디자이너 (경력) | Design | Visual Comm. & Brand Design | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] Brand Media 콘텐츠 PD (계약직) | Design | Visual Comm. & Brand Design | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] Brand Media 콘텐츠 마케터 (체험형 인턴) | Design | Visual Comm. & Brand Design | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] Client Partner (경력) | Service & Business | Business Development | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] EN Webtoon Growth&Marketing (체험형 인턴) | Service & Business | Content Development | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] FR Platform Growth Manager (경력) | Service & Business | Business Development | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] HR Operations Assistant (체험형 인턴) | Corporate | Human Resources | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] IP 사업 운영 담당(IP Business Operations Associate) (계약직) | Service & Business | Business Development | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] KR Creative 영상 제작 지원 (체험형 인턴) | Design | Visual Comm. & Brand Design | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] KR Strategy Associate (계약직) | Service & Business | Business Development | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] KR Webtoon Marketing Manager (경력) | Service & Business | Business Development | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] KR Webtoon 콘텐츠 마케터 (체험형 인턴) | Service & Business | Business Development | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] UI/UX 프로덕트 디자이너 (UI/UX Product Designer) (경력) | Design | Product Design | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] US GAAP Consolidation (경력) | Corporate | 회계 | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] 글로벌 B2B 마케터 (Global B2B Marketer) (경력) | Service & Business | Business Development | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] 글로벌웹툰 콘텐츠 기획/운영 (체험형 인턴) | Service & Business | Content Development | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] 변호사 (경력) | Corporate | 법무 | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] 전략 기획 (경력) | Corporate | Corporate Strategy | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] 창작자 백엔드 시스템 정책/통제 (계약직) | Corporate | Risk Management | 서버·백엔드 | `백엔드` |
| `naver` | custom | [네이버웹툰] 컷츠 서비스 운영지원 (체험형 인턴) | Service & Business | Content Development | 웹 프론트엔드 | `웹` |
| `naver` | custom | [네이버웹툰] 플랫폼 그로스 매니저 (경력) | Service & Business | Business Development | 웹 프론트엔드 | `웹` |
| `oliveyoung` | greeting | Product Manager - AI | IT | Product Management | 데이터·AI | `AI` |
| `oliveyoung` | greeting | 데이터 사업 담당자 | None | None | 데이터·AI | `데이터` |
| `oliveyoung` | greeting | 데이터 콘텐츠 기획 담당자 | IT | IT기획 | 데이터·AI | `데이터` |
| `oliveyoung` | greeting | 리테일미디어 사업 기획/데이터분석 담당자 | None | None | 데이터·AI | `데이터` |
| `oliveyoung` | greeting | 웹디자이너_색조 (계약직) | None | None | 웹 프론트엔드 | `웹` |
| `remember` | ninehire | Frontend Software Engineer | Tech | (없음) | 웹 프론트엔드 | `Frontend` |
| `toss` | custom | Android Developer | App | (없음) | 모바일 | `Android` |
| `toss` | custom | Android Developer | App | (없음) | 모바일 | `Android` |
| `toss` | custom | Device Software Engineer (Android) | Device | (없음) | 모바일 | `Android` |
| `toss` | custom | Device Software Quality Engineer (Android) | Device | (없음) | 모바일 | `Android` |
| `toss` | custom | Financial Data Analyst (Accounting) | Finance | (없음) | 데이터·AI | `Data` |
| `toss` | custom | Frontend Developer [산업기능요원/전문연구요원] | 병역특례 | (없음) | 웹 프론트엔드 | `Frontend` |
| `toss` | custom | ML Engineer [전문연구요원] | 병역특례 | (없음) | 데이터·AI | `ML` |
| `toss` | custom | Security Audit Manager (개인정보 및 데이터관리 담당) | Information Security | (없음) | 데이터·AI | `데이터` |
| `toss` | custom | Server Developer [산업기능요원/전문연구요원] (Product) | 병역특례 | (없음) | 서버·백엔드 | `Server` |
| `toss` | custom | iOS Developer | App | (없음) | 모바일 | `iOS` |
| `toss` | custom | iOS Developer | App | (없음) | 모바일 | `iOS` |
| `toss` | custom | 토스쇼핑 음성 데이터 검수 스태프 (팀원) | Customer | 음성 클리핑 | 데이터·AI | `데이터` |
| `tving` | custom | Ad Tech Backend Engineer | 개발직군 | (없음) | 서버·백엔드 | `Backend` |
| `watcha` | greeting | 백엔드 개발자 - 미디어 플랫폼 | None | None | 서버·백엔드 | `백엔드` |
| `yeogieotdae` | greeting | Data Analyst [Business Insight]  | 기술 | None | 데이터·AI | `Data` |
| `yogiyo` | ninehire | [Security] Web & Application Security (5년 이상) | Tech | security engineering | 웹 프론트엔드 | `Web` |

### 2-1. 이 사례들에서 구조화 분류를 막은 occupation / job 값 (빈도순)

**occupation**

| occupation | 건수 |
|---|---|
| 테크 | 18 |
| 기술 | 16 |
| Service & Business | 14 |
| 개발 | 9 |
| Design | 6 |
| Engineering | 6 |
| Corporate | 5 |
| App | 4 |
| (없음/None) | 4 |
| Strategy / Business Ops | 4 |
| Tech | 4 |
| 병역특례 | 3 |
| Device | 2 |
| IT | 2 |
| Planning | 2 |
| Business & Sales | 1 |
| Customer | 1 |
| Finance | 1 |
| Information Security | 1 |
| PM | 1 |
| Service & Biz | 1 |
| Tinder Seoul | 1 |
| 개발직군 | 1 |
| 마케팅 | 1 |
| 서비스비즈 | 1 |
| 스태프 | 1 |
| 인재풀 | 1 |
| 프로덕트 매니지먼트 | 1 |

**job**

| job | 건수 |
|---|---|
| (없음/None) | 68 |
| Business Development | 10 |
| 개발 | 7 |
| Visual Comm. & Brand Design | 5 |
| Content Development | 3 |
| Product Management | 3 |
| Product Development | 2 |
| Corporate Strategy | 1 |
| Human Resources | 1 |
| IT기획 | 1 |
| Product Design | 1 |
| QA/SET | 1 |
| Risk Management | 1 |
| Security | 1 |
| Software Engineer | 1 |
| security engineering | 1 |
| 기타 | 1 |
| 법무 | 1 |
| 음성 클리핑 | 1 |
| 테크 | 1 |
| 회계 | 1 |

### 2-2. 배정된 카테고리별 건수

| 배정된 카테고리 | 건수 |
|---|---|
| 데이터·AI | 43 |
| 웹 프론트엔드 | 34 |
| 서버·백엔드 | 28 |
| 모바일 | 7 |

---

## 3. 부분일치 오탐 전수 — 우선 검토 대상

스펙 키워드가 **그 키워드가 아닌 더 긴 단어의 일부로** 걸린 사례다.
예: `웹`이 `웹툰`의 일부로 매칭.

판정 방법: 제목에서 키워드가 매칭된 구간을 같은 문자 종류(한글 / 영숫자)로
좌우 확장해 실제 단어를 구한 뒤, 그 단어가 키워드 자체와 다르면 부분일치로 본다.
매칭 규칙은 `job_classifier.py`와 동일하다.

전체 `deploy=true` 1405건을 검사한 결과 **35건**이다.

### 3-1. 키워드 × 걸린 단어별 건수

| 키워드 | 키워드가 속한 직무 | 실제로 걸린 단어 | 건수 | 이 매칭이 최종 카테고리를 결정한 건수 |
|---|---|---|---:|---:|
| `웹` | 웹 프론트엔드 | 네이버웹툰 | 27 | 23 |
| `데이터` | 데이터·AI | 금융데이터 | 3 | 0 |
| `데이터` | 데이터·AI | 데이터분석 | 1 | 1 |
| `데이터` | 데이터·AI | 데이터관리 | 1 | 1 |
| `모바일` | 모바일 | 모바일보안 | 1 | 0 |
| `웹` | 웹 프론트엔드 | 웹디자이너 | 1 | 1 |
| `웹` | 웹 프론트엔드 | 글로벌웹툰 | 1 | 1 |

### 3-2. 사례 전수

`최종 카테고리 결정` = 이 부분일치가 실제로 공고의 카테고리를 정했는지
(구조화 필드로 이미 분류된 건은 `아니오`).

| company_id | ATS | title | 키워드 | 걸린 단어 | 최종 카테고리 | 최종 카테고리 결정 |
|---|---|---|---|---|---|---|
| `naver` | custom | [네이버웹툰] AI 서비스 기획 (체험형 인턴) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] Ads Design 영상 디자이너 (계약직) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] Agency Partner (경력) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] Brand Marketing 영상 디자이너 (경력) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] Brand Media 콘텐츠 PD (계약직) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] Brand Media 콘텐츠 마케터 (체험형 인턴) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] Client Partner (경력) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] Data Product Engineer (경력) | `웹` | 네이버웹툰 | 데이터·AI | 아니오 |
| `naver` | custom | [네이버웹툰] Disney 디지털 코믹스 플랫폼 서버 개발 (경력) | `웹` | 네이버웹툰 | 서버·백엔드 | 아니오 |
| `naver` | custom | [네이버웹툰] EN Webtoon Growth&Marketing (체험형 인턴) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] FR Platform Growth Manager (경력) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] HR Operations Assistant (체험형 인턴) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] IP 사업 운영 담당(IP Business Operations Associate) (계약직) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] KR Creative 영상 제작 지원 (체험형 인턴) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] KR Strategy Associate (계약직) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] KR Webtoon Marketing Manager (경력) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] KR Webtoon 콘텐츠 마케터 (체험형 인턴) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] Search Intelligence Engineer (경력) | `웹` | 네이버웹툰 | 데이터·AI | 아니오 |
| `naver` | custom | [네이버웹툰] UI/UX 프로덕트 디자이너 (UI/UX Product Designer) (경력) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] US GAAP Consolidation (경력) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] 글로벌 B2B 마케터 (Global B2B Marketer) (경력) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] 글로벌웹툰 콘텐츠 기획/운영 (체험형 인턴) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] 글로벌웹툰 콘텐츠 기획/운영 (체험형 인턴) | `웹` | 글로벌웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] 변호사 (경력) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] 전략 기획 (경력) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] 창작자 백엔드 시스템 정책/통제 (계약직) | `웹` | 네이버웹툰 | 서버·백엔드 | 아니오 |
| `naver` | custom | [네이버웹툰] 컷츠 서비스 운영지원 (체험형 인턴) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `naver` | custom | [네이버웹툰] 플랫폼 그로스 매니저 (경력) | `웹` | 네이버웹툰 | 웹 프론트엔드 | 예 |
| `oliveyoung` | greeting | 리테일미디어 사업 기획/데이터분석 담당자 | `데이터` | 데이터분석 | 데이터·AI | 예 |
| `oliveyoung` | greeting | 웹디자이너_색조 (계약직) | `웹` | 웹디자이너 | 웹 프론트엔드 | 예 |
| `toss` | custom | Data Engineer (금융데이터/AI) | `데이터` | 금융데이터 | 데이터·AI | 아니오 |
| `toss` | custom | Data Engineer (금융데이터/자문) | `데이터` | 금융데이터 | 데이터·AI | 아니오 |
| `toss` | custom | Data Engineer (금융데이터/재무) | `데이터` | 금융데이터 | 데이터·AI | 아니오 |
| `toss` | custom | Security Audit Manager (개인정보 및 데이터관리 담당) | `데이터` | 데이터관리 | 데이터·AI | 예 |
| `toss` | custom | Security Researcher (모바일보안) | `모바일` | 모바일보안 | 모바일 | 아니오 |

### 3-3. 회사별 건수

| company_id | 건수 |
|---|---|
| naver | 28 |
| toss | 5 |
| oliveyoung | 2 |

### 3-4. 섹션 2와의 관계

- 섹션 2(제목 fallback으로 분류됨): 112건
- 그 중 이 섹션의 부분일치에 해당: 27건
- 부분일치가 아닌 채로 제목 fallback된 건: 85건
  (키워드가 제목에서 독립된 단어로 매칭된 경우. 예: 요기요
  `[Security] Web & Application Security`는 `Web`이 단독 단어로 걸렸으므로
  이 섹션이 아니라 섹션 2에만 해당한다.)

---

## 4. 단어 경계로 인한 역방향 미분류 — 우선 검토 대상

섹션 1(키워드 자체가 없어서 미분류)과는 성격이 다르다.
**스펙 키워드가 텍스트에 존재하고 의미상으로도 관련 있는데,**
**단어 경계(`\b`) 규칙 때문에 매칭되지 않은** 사례다.

분류기는 ASCII 키워드에만 단어 경계를 적용한다. 한글 키워드는 부분일치를 그대로
허용하므로 이 섹션에 해당하지 않는다.

판정 기준: 키워드를 품은 더 긴 영단어가 **그 키워드가 가리키는 기술 개념의**
**하위 개념이거나 합성어인가**. `Database`는 `Data`의 하위 개념이므로 해당하고,
`Webtoon`은 `Web`과 철자만 겹칠 뿐이므로 해당하지 않는다(그쪽은 섹션 3 성격).

`deploy=true` 1405건의 title · occupation · job을 모두 검사한 결과
단어 경계에 막힌 사례는 총 89건이고, 그 중 **의미상 관련 있는 것은 8건**이다.

### 4-1. 의미상 관련 있는 사례 (역방향 미분류)

| company_id | 필드 | 값 | 키워드 | 막은 단어 | 현재 최종 분류 |
|---|---|---|---|---|---|
| `daangn` | title | DBA (Database Administrator) - 인프라 (DB) | `Data` | Database | **미분류** |
| `daangn` | job | Database Engineer | `Data` | Database | **미분류** |
| `line` | title | Database Administrator (DBA)_KR-TW | `Data` | Database | 데이터·AI |
| `line` | title | Database Administrator Engineer(EPI) | `Data` | Database | 데이터·AI |
| `remember` | title | Database Engineer | `Data` | Database | 데이터·AI |
| `toss` | title | AIOps Platform Engineer | `AI` | AIOps | **미분류** |
| `toss` | title | DataOps Manager | `Data` | DataOps | 데이터·AI |
| `toss` | title | DataOps Manager | `Data` | DataOps | 데이터·AI |

### 4-2. 키워드별 집계

| 키워드 → 막은 단어 | 건수 |
|---|---|
| `Data` → Database | 5 |
| `Data` → DataOps | 2 |
| `AI` → AIOps | 1 |

### 4-3. 같은 규칙에 막혔지만 의미상 무관한 사례 (참고)

단어 경계 규칙이 **의도대로 오탐을 막아준** 경우다. 이 섹션의 판정 기준을
팀이 다시 검토할 때 비교 대상으로 쓰라고 함께 싣는다.

| 키워드 → 막은 단어 | 건수 |
|---|---|
| `AI` → Taiwan | 18 |
| `AI` → Affairs | 15 |
| `ML` → AML | 13 |
| `AI` → Retail | 11 |
| `Web` → Webtoon | 4 |
| `AI` → AICX | 2 |
| `AI` → Blockchain | 2 |
| `AI` → Brain | 2 |
| `AI` → Training | 2 |
| `Web` → WEBTOON | 2 |
| `AI` → AICC | 1 |
| `AI` → AIOC | 1 |
| `AI` → Affair | 1 |
| `AI` → Campaign | 1 |
| `AI` → Domain | 1 |
| `AI` → Thai | 1 |
| `AI` → Trainee | 1 |
| `AI` → training | 1 |
| `Data` → Datacenter | 1 |
| `iOS` → Studios | 1 |

---

## 5. 구조화 필드 자체 오탐 (occupation 오염) — 우선 검토 대상

섹션 1~4와 구분되는 유형이다. 구조화 필드가 **정상적으로 매칭됐는데**
결과가 의미상 틀린 경우다.

분류기는 `job`(세부 직무) → `occupation`(상위 직군) 순으로 본다.
`job`이 스펙 키워드에 걸리지 않으면 `occupation`으로 넘어가는데,
그 **직군 이름 자체에 스펙 키워드가 들어 있으면** 그 직군에 속한 무관한
업무까지 함께 분류된다. 쏘카의 `개발/데이터` 직군이 그 예로,
`데이터`가 occupation에 들어 있어 무관한 공고까지 데이터·AI로 간다.

검출 조건:

1. 구조화 분류이고, `job`이 아니라 `occupation`에서 매칭됐다
2. 그 `occupation` 문자열에 스펙 키워드가 포함된다
3. `job` 값도 `title`도 같은 카테고리를 뒷받침하지 않는다

`deploy=true` 1405건 전체에서 위 조건에 걸린 사례는 총 37건이다.

조건 3까지는 기계적으로 판정되지만, "의미상 무관한가"는 직군 이름과 실제
업무를 같이 봐야 갈린다. 판정은 `(company_id, occupation)` 단위로 하고
`scripts/build_keyword_audit.py`의 `OCCUPATION_BLEED_VERDICT`에 명시했다.
목록에 없는 새 조합은 `판정 보류`로 나온다.

판정 결과: **무관 9건** / 관련 4건 / 판정 보류 24건

### 5-1. 의미상 무관 (occupation 오염)

| company_id | occupation | 걸린 키워드 | job | title | 배정된 직무 |
|---|---|---|---|---|---|
| `kurly` | 인프라 | `인프라` | (없음) | IT 자산/라이선스 담당자 | 서버·백엔드 |
| `socar` | 개발/데이터 | `데이터` | (없음) | Product Engineer | 데이터·AI |
| `socar` | 개발/데이터 | `데이터` | (없음) | [쏘카일레클] Embedded Firmware Engineer | 데이터·AI |
| `socar` | 개발/데이터 | `데이터` | (없음) | [에이펙스 모빌리티] Applied Research Scientist | 데이터·AI |
| `socar` | 개발/데이터 | `데이터` | (없음) | [에이펙스 모빌리티] Product Engineer | 데이터·AI |
| `socar` | 개발/데이터 | `데이터` | (없음) | [에이펙스모빌리티] Embedded Platform SW Engineer (센서킷 플랫폼) | 데이터·AI |
| `socar` | 개발/데이터 | `데이터` | (없음) | [에이펙스모빌리티] Mechanical Design Engineer (센서킷 기구) | 데이터·AI |
| `socar` | 개발/데이터 | `데이터` | (없음) | [에이펙스모빌리티] Vehicle Integration Engineer (차량 전장·개조) | 데이터·AI |
| `socar` | 개발/데이터 | `데이터` | (없음) | 프로덕트 매니저 (PM) | 데이터·AI |

### 5-2. 같은 조건에 걸렸지만 의미상 관련 있는 사례 (참고)

직군 이름이 해당 카테고리 전용이고 실제 업무도 맞는 경우다. 5-1의 판정
기준을 팀이 다시 검토할 때 비교 대상으로 쓰라고 함께 싣는다.

| company_id | occupation | 걸린 키워드 | job | title | 배정된 직무 |
|---|---|---|---|---|---|
| `catchtable` | AI | `AI` | (없음) | AX Manager (6년차 이상) | 데이터·AI |
| `catchtable` | Data | `Data` | (없음) | Business Analyst | 데이터·AI |
| `hyperconnect` | AI/ML | `AI`, `ML` | (없음) | Staff, Machine Learning Research Scientist (Azar) | 데이터·AI |
| `remember` | Data | `Data` | (없음) | Database Engineer | 데이터·AI |

### 5-3. 판정 보류 (새로 등장한 조합)

| company_id | occupation | 걸린 키워드 | job | title | 배정된 직무 |
|---|---|---|---|---|---|
| `toss` | Data Engineering | `Data` | 공통 | DBA | 데이터·AI |
| `toss` | Data Engineering | `Data` | 공통 | DBA | 데이터·AI |
| `toss` | Data Engineering | `Data` | MySQL | DBA (MySQL) | 데이터·AI |
| `toss` | Data Engineering | `Data` | Oracle | DBA (Oracle) | 데이터·AI |
| `toss` | Data Managing | `Data` | Product | DataOps Manager | 데이터·AI |
| `toss` | Backend | `Backend` | 공통 | DevOps Engineer | 서버·백엔드 |
| `toss` | Backend | `Backend` | (없음) | DevOps Engineer | 서버·백엔드 |
| `toss` | Backend | `Backend` | (없음) | DevOps Engineer | 서버·백엔드 |
| `toss` | Backend | `Backend` | (없음) | DevOps Engineer | 서버·백엔드 |
| `toss` | Backend | `Backend` | (없음) | DevOps Engineer | 서버·백엔드 |
| `toss` | Frontend | `Frontend` | Platform | FE Platform Engineer | 웹 프론트엔드 |
| `toss` | Frontend | `Frontend` | (없음) | FE Platform Engineer | 웹 프론트엔드 |
| `toss` | Frontend | `Frontend` | Platform | FE Platform Engineer | 웹 프론트엔드 |
| `toss` | Frontend | `Frontend` | Platform | FE Platform Engineer | 웹 프론트엔드 |
| `toss` | Backend | `Backend` | (없음) | Network Software Engineer | 서버·백엔드 |
| `toss` | Backend | `Backend` | Operations | Node.js Developer | 서버·백엔드 |
| `toss` | Backend | `Backend` | Ads | Node.js Developer | 서버·백엔드 |
| `toss` | Backend | `Backend` | 공통 | Node.js Developer | 서버·백엔드 |
| `toss` | Backend | `Backend` | 자동화 | Node.js Developer | 서버·백엔드 |
| `toss` | Backend | `Backend` | 공통 | Site Reliability Engineer | 서버·백엔드 |
| `toss` | Backend | `Backend` | Commerce Domain | Site Reliability Engineer | 서버·백엔드 |
| `toss` | Backend | `Backend` | (없음) | Site Reliability Engineer | 서버·백엔드 |
| `toss` | Backend | `Backend` | (없음) | Site Reliability Engineer | 서버·백엔드 |
| `toss` | Frontend | `Frontend` | 공통 | Systems Engineer | 웹 프론트엔드 |

---

## 6. 회사별 occupation / job 필드 커버리지

`deploy=true` 기준. '없음'은 해당 공고의 모든 직무 항목에서 그 필드가 `null`인 경우다.

| company_id | 회사명 | ATS | 공고 수 | occupation 없음 | job 없음 |
|---|---|---|---:|---:|---:|
| `oliveyoung` | 올리브영 | greeting | 212 | 42 | 46 |
| `musinsa` | 무신사(+29CM) | greeting | 123 | 120 | 4 |
| `kurly` | 컬리 | greeting | 69 | 0 | 69 |
| `catchtable` | 캐치테이블 | greeting | 41 | 2 | 41 |
| `kakaopay` | 카카오페이 | greeting | 31 | 10 | 31 |
| `yeogieotdae` | 여기어때 | greeting | 26 | 1 | 26 |
| `kakaomobility` | 카카오모빌리티 | greeting | 22 | 0 | 0 |
| `watcha` | 왓챠 | greeting | 1 | 1 | 1 |
| `ssg` | SSG.COM | greeting | 0 | 0 | 0 |
| `devsisters` | 데브시스터즈 | greeting | 0 | 0 | 0 |
| `myrealtrip` | 마이리얼트립 | greeting | 21 | 1 | 21 |
| `remember` | 리멤버 | ninehire | 19 | 2 | 19 |
| `yogiyo` | 요기요 | ninehire | 12 | 0 | 0 |
| `naver` | 네이버 | custom | 42 | 0 | 0 |
| `kakaobank` | 카카오뱅크 | custom | 33 | 0 | 33 |
| `line` | 라인 | custom | 72 | 2 | 5 |
| `daangn` | 당근 | custom | 48 | 0 | 0 |
| `tving` | 티빙 | custom | 3 | 0 | 3 |
| `channeltalk` | 채널톡 | custom | 43 | 0 | 43 |
| `banksalad` | 뱅크샐러드 | custom | 9 | 0 | 0 |
| `hyperconnect` | 하이퍼커넥트 | custom | 12 | 0 | 12 |
| `socar` | 쏘카 | custom | 29 | 0 | 29 |
| `kakao` | 카카오 | custom | 64 | 0 | 57 |
| `toss` | 토스 | custom | 473 | 6 | 232 |

---

## 7. 회사별 title 고유값 전수 (빈도순)

### 올리브영 (`oliveyoung`, greeting) — 212건

| title | 건수 | 현재 분류 |
|---|---:|---|
| Data Scientist (광고) | 2 | 데이터·AI |
|  디지털 사업 전략 담당자 | 1 | **None** |
| AI Engineer (추천) | 1 | 데이터·AI |
| AI(ML) Engineer (광고) | 1 | 데이터·AI |
| AMD (정규직 전환형 계약직) | 1 | **None** |
| B2B 물류센터 운영 관리 담당자 (경산) | 1 | **None** |
| B2B 물류센터 운영 관리 담당자 (양지) | 1 | **None** |
| B2B 수출 운영 관리 담당자 (안성) | 1 | **None** |
| B2C 물류센터 운영 관리 담당자 (양지) | 1 | **None** |
| B2C 물류센터 운영 프로세스 기획 담당자 | 1 | **None** |
| BM 팀장 (색조사업부)  | 1 | **None** |
| BX 디자이너 | 1 | **None** |
| BX디자이너 (계약직)  | 1 | **None** |
| BX이벤트 전략/실행 담당자(시니어) | 1 | **None** |
| BX이벤트 전략/실행 담당자(주니어) | 1 | **None** |
| Back-end Engineer (광고/AD-Server) | 1 | 서버·백엔드 |
| Back-end Engineer (추천) | 1 | 서버·백엔드 |
| DBA | 1 | **None** |
| Data Analyst (분석) | 1 | 데이터·AI |
| Data Analytics Engineer | 1 | 데이터·AI |
| Data Analytics Engineer (광고/DMP) | 1 | 데이터·AI |
| Data Architect (시니어) | 1 | 데이터·AI |
| Data Architect (주니어) | 1 | 데이터·AI |
| Data Engineer | 1 | 데이터·AI |
| Data Engineer (광고/AD-Server) | 1 | 데이터·AI |
| Data Engineer (광고/DMP) | 1 | 데이터·AI |
| Data Scientist | 1 | 데이터·AI |
| Data Scientist (AI 추천) | 1 | 데이터·AI |
| Data Scientist (광고 플랫폼 사업) | 1 | 데이터·AI |
| Data Service Engineer | 1 | 데이터·AI |
| DevRel (Developer Relations) | 1 | **None** |
| Global Product Designer | 1 | **None** |
| Global Software Engineer-Backend (글로벌 개발) | 1 | 서버·백엔드 |
| Global Software Engineer-Frontend (글로벌 개발) | 1 | 웹 프론트엔드 |
| Global User Researcher  | 1 | **None** |
| IMC 마케터 | 1 | **None** |
| IP 콜라보 마케팅 기획 담당자 | 1 | **None** |
| IT 구매 담당자 | 1 | **None** |
| IT 인프라 기획 담당자 | 1 | **None** |
| IT기획 담당자 | 1 | **None** |
| Language Specialist (영어) | 1 | **None** |
| MD (PB 운영) | 1 | **None** |
| MD사업관리 담당자 | 1 | **None** |
| MD사업전략/개발 담당자 (시니어) | 1 | **None** |
| MD사업전략/개발 담당자 (주니어) | 1 | **None** |
| MD스토어기획 담당자 | 1 | **None** |
| Marketing Designer | 1 | **None** |
| Network RE | 1 | **None** |
| PB 글로벌 GTM 담당자 | 1 | **None** |
| PB 마케터 | 1 | **None** |
| PB 화장품 공급운영 관리 (SCM) | 1 | **None** |
| PB브랜드 콘텐츠 디자인 | 1 | **None** |
| PB화장품 구매 담당자 (소싱/조달) | 1 | **None** |
| PB화장품 구매 담당자(기초/바디/프래그런스) | 1 | **None** |
| PMO | 1 | **None** |
| Platform Designer (디자인시스템구축) | 1 | **None** |
| Platform Engineer | 1 | 데이터·AI |
| Product Data Analyst | 1 | 데이터·AI |
| Product Designer | 1 | **None** |
| Product Designer (B2B/광고플랫폼) | 1 | **None** |
| Product Designer (팀장급) | 1 | **None** |
| Product Manager - AI | 1 | 데이터·AI |
| Product Manager - Account & Membership (회원&멤버십) | 1 | **None** |
| Product Manager - Campaign Platform (캠페인) | 1 | **None** |
| Product Manager - Catalog & Listing (상품) | 1 | **None** |
| Product Manager - Commerce Display | 1 | **None** |
| Product Manager - Coupons & Promotions (쿠폰&증정) | 1 | **None** |
| Product Manager - Discovery (US mall) | 1 | **None** |
| Product Manager - Discovery (발견) | 1 | **None** |
| Product Manager - Fulfillment | 1 | **None** |
| Product Manager - Gift/Promotion (US mall) | 1 | **None** |
| Product Manager - Global E-Commerce | 1 | **None** |
| Product Manager - In-store Payment | 1 | **None** |
| Product Manager - Merchant Partner Platform (정산) | 1 | **None** |
| Product Manager - Merchant Platform (파트너플랫폼) | 1 | **None** |
| Product Manager - Omnichannel | 1 | **None** |
| Product Manager - Order/Payment/Point | 1 | **None** |
| Product Manager - PIS(파트너 인텔리전스 시스템) | 1 | **None** |
| Product Manager - Product (US mall) | 1 | **None** |
| Product Manager - Store Operations | 1 | **None** |
| Product Manager - 광고/DMP | 1 | **None** |
| Product Manager - 광고/DSP | 1 | **None** |
| Product Manager - 광고/SSP | 1 | **None** |
| Product Manager - 커머스 신사업(Review) | 1 | **None** |
| Product Strategist | 1 | **None** |
| QA Engineer (Domestic) | 1 | **None** |
| QA Engineer (Global) | 1 | **None** |
| QA Ops Engineer (Test Automation) | 1 | **None** |
| Research Specialist | 1 | **None** |
| SCM 사업관리/기획 담당자 | 1 | **None** |
| SCM 전략기획 담당자 | 1 | **None** |
| SRE | 1 | **None** |
| Staff Engineer (공통영역개선) | 1 | 서버·백엔드 |
| Staff Software Engineer (글로벌서비스 개발) | 1 | **None** |
| TPM (Tech. Project Management) | 1 | **None** |
| US E-Commerce 온사이트 마케터 | 1 | **None** |
| US E-Commerce 퍼포먼스/어필리에이트 마케터 | 1 | **None** |
| USE 온라인 플랫폼 사업관리/기획 담당자 | 1 | **None** |
| User Researcher | 1 | **None** |
| VMD 담당자 | 1 | **None** |
| Windows Application Engineer (POS 시스템) | 1 | 서버·백엔드 |
| 개발 BM (PB 식품) | 1 | **None** |
| 개발 BM (기초화장품, 헤어용품) | 1 | **None** |
| 개발 BM (미용소품/생활용품) | 1 | **None** |
| 검색 서비스 품질관리 담당자 (계약직) | 1 | **None** |
| 검색 플랫폼 개발자 (Back-end) | 1 | 서버·백엔드 |
| 검색 플랫폼 개발자 (Front-end) | 1 | 웹 프론트엔드 |
| 결제 제휴 및 프로모션 기획 담당자 | 1 | **None** |
| 공간디자인(인테리어) 담당자 | 1 | **None** |
| 공산품(잡화) 품질관리 담당자 | 1 | **None** |
| 광고 정산 및 운영 지원 담당자 (계약직) | 1 | **None** |
| 구매 담당자 | 1 | **None** |
| 국내 및 수출 입출고 품질관리 담당자 (안성) | 1 | **None** |
| 그로스마케터 | 1 | **None** |
| 글로벌 B2B SCM 팀장 | 1 | **None** |
| 글로벌 B2B 마케팅커뮤니케이션 마케터 (Estern) | 1 | **None** |
| 글로벌 CX체계 설계 담당자 | 1 | **None** |
| 글로벌 MD 통합 채용 | 1 | **None** |
| 글로벌 SCM 전략/물류거점 구축 PM | 1 | **None** |
| 글로벌 VMD 운영 Assistant (계약직) | 1 | **None** |
| 글로벌 VMD담당자 | 1 | **None** |
| 글로벌 개인정보보호 담당자 | 1 | **None** |
| 글로벌 리테일미디어 컨설턴트 | 1 | **None** |
| 글로벌 발주 프로세스 운영 담당자 | 1 | **None** |
| 글로벌 상품운영전략 | 1 | **None** |
| 글로벌 영업지원 담당자 (계약직) | 1 | **None** |
| 글로벌 이커머스 해외영업/운영 담당자(아마존/ 틱톡샵) | 1 | **None** |
| 글로벌 인허가 (RA) 지원 담당자 (계약직) | 1 | **None** |
| 글로벌 재고운영 및 정산지원 담당자(계약직) | 1 | **None** |
| 글로벌 품질관리 담당자 (식품/건강기능식품/잡화) | 1 | **None** |
| 글로벌 품질관리 담당자 (화장품/OTC/의료기기) | 1 | **None** |
| 글로벌몰 CRM 마케터 | 1 | **None** |
| 글로벌몰 Technical Program Manager (TPM) | 1 | **None** |
| 글로벌몰 마케팅 운영 Assistant (계약직) | 1 | **None** |
| 글로벌몰 멤버십 마케터 | 1 | **None** |
| 글로벌몰 시니어 그로스 마케터 | 1 | **None** |
| 글로벌몰 중화권 소셜/바이럴 마케터 (역직구 플랫폼) | 1 | **None** |
| 글로벌몰 퍼포먼스 마케터 | 1 | **None** |
| 글로벌몰 프로모션 마케터 | 1 | **None** |
| 글로벌커머스 일본 사업전략 담당자 | 1 | **None** |
| 글로벌콘텐츠커머스팀 팀장 | 1 | **None** |
| 기초화장품 BM | 1 | **None** |
| 노무관리/조직문화 담당자 | 1 | **None** |
| 데이터 사업 담당자 | 1 | 데이터·AI |
| 데이터 콘텐츠 기획 담당자 | 1 | 데이터·AI |
| 도심물류매장 MFC 운영(무기계약직) - 인천점 | 1 | **None** |
| 디지털 마케팅 전략 담당자 | 1 | **None** |
| 디지털플랫폼 사업전략 팀장 | 1 | **None** |
| 라이브커머스 PD | 1 | **None** |
| 리테일 사업관리 담당자 | 1 | **None** |
| 리테일미디어 DMP 상품 기획/사업 담당자 (BPO) | 1 | **None** |
| 리테일미디어 광고 사업 담당자 | 1 | **None** |
| 리테일미디어 광고 상품기획/사업 담당자 (BPO) | 1 | **None** |
| 리테일미디어 광고(AD) 퍼포먼스 마케터 | 1 | **None** |
| 리테일미디어 구좌형 광고 상품기획/운영 담당자 (BPO) | 1 | **None** |
| 리테일미디어 사업 기획/데이터분석 담당자 | 1 | 데이터·AI |
| 매장 자동발주 기획/관리 담당자 | 1 | **None** |
| 미국/웰니스 스토어기획 담당자 | 1 | **None** |
| 미주 글로벌 마케터 (컬러그램)  | 1 | **None** |
| 미주 마케팅 담당자 (바이오힐보) | 1 | **None** |
| 바이오힐 보 글로벌 퍼포먼스 마케터 (BIOHEAL BOH) | 1 | **None** |
| 바이오힐 보 동남아 마케터 (BIOHEAL BOH) | 1 | **None** |
| 바이오힐보 글로벌 채널 실적 전략 담당자 | 1 | **None** |
| 뷰티 카테고리 MD | 1 | **None** |
| 브랜드 디자이너 | 1 | **None** |
| 브랜드 마케터 (웨이크메이크)  | 1 | **None** |
| 비주얼 콘텐츠 기획자 (PB 브랜드) | 1 | **None** |
| 비주얼디자인 Assistant (계약직) | 1 | **None** |
| 상권개발 담당자 | 1 | **None** |
| 소셜 콘텐츠 제작 담당자 | 1 | **None** |
| 소셜커머스 사업기획 담당자(BPO) | 1 | **None** |
| 스토어 브랜딩 전략 담당자 | 1 | **None** |
| 안성물류센터 입/출고 검사 담당자 (계약직) | 1 | **None** |
| 양지물류센터 입/출고 검사 담당자 (계약직) | 1 | **None** |
| 양지센터 입출고 품질관리 담당자 | 1 | **None** |
| 어필리에이트 광고 사업 담당자 | 1 | **None** |
| 엔터프라이즈플랫폼유닛 Back-end 개발채용 | 1 | 서버·백엔드 |
| 엔터프라이즈플랫폼유닛 Front-end 개발채용 | 1 | 웹 프론트엔드 |
| 오늘드림 기획 운영 담당자 | 1 | **None** |
| 온라인 APP 온사이트 프로모션 | 1 | **None** |
| 온라인 프로모션 온사이트 마케팅 담당자 | 1 | **None** |
| 온사이트 마케팅 담당자 | 1 | **None** |
| 올리브영 PB브랜드 운영 지원 담당 (계약직) | 1 | **None** |
| 웹디자이너_색조 (계약직) | 1 | 웹 프론트엔드 |
| 이커머스 재고수불 관리 담당자 (계약직) | 1 | **None** |
| 인테리어 설계 및 시공 관리 담당자 | 1 | **None** |
| 일본 EC 영업 담당자 | 1 | **None** |
| 전사 캠페인/프로모션 담당자 | 1 | **None** |
| 정산담당자 (계약직) | 1 | **None** |
| 제휴 프로모션 운영 및 사업지원 담당자 (계약직) | 1 | **None** |
| 채용 코디네이터(계약직)  | 1 | **None** |
| 커머스 신사업 BPO | 1 | **None** |
| 커머스플랫폼유닛 Android 개발채용 | 1 | 모바일 |
| 커머스플랫폼유닛 Back-end 개발채용 | 1 | 서버·백엔드 |
| 커머스플랫폼유닛 Front-end 개발채용 | 1 | 웹 프론트엔드 |
| 커뮤니케이션 디자이너 | 1 | **None** |
| 컨텐츠 디자이너 | 1 | **None** |
| 코어플랫폼유닛 Back-end 개발채용 | 1 | 서버·백엔드 |
| 콘텐츠 디자이너 (계약직) | 1 | **None** |
| 콘텐츠 마케팅 담당자(시니어) | 1 | **None** |
| 콘텐츠커머스 마케터/전략기획 담당자 | 1 | **None** |
| 클라우드 인프라 보안 담당자 | 1 | **None** |
| 통번역 담당자 (계약직) | 1 | **None** |
| 통합 마케팅 전략 담당자 | 1 | **None** |
| 패키지 디자이너 | 1 | **None** |
| 플랫폼 전략기획 담당자 (PM) | 1 | **None** |
| 헬시라이프 카테고리 MD | 1 | **None** |
| 협력사발주 공급망 관리/기획 담당자 | 1 | **None** |
| 화장품 품질관리 담당자(계약직) | 1 | **None** |
| 화장품 품질보증 담당자 | 1 | **None** |
| 📌채용 마케팅 인턴 | 1 | **None** |

### 무신사(+29CM) (`musinsa`, greeting) — 123건

| title | 건수 | 현재 분류 |
|---|---:|---|
|  Brand & Contents Marketer (China) | 1 | **None** |
| 29CM HOME SNS 운영 담당자 | 1 | **None** |
| BM Lead (Beauty PB) | 1 | **None** |
| Backend Engineer (Catalog) | 1 | 서버·백엔드 |
| Backend Engineer (Core AI) | 1 | 서버·백엔드 |
| Backend Engineer (Foundation Platform)  | 1 | 서버·백엔드 |
| Backend Engineer (Platform Innovation) | 1 | 서버·백엔드 |
| Backend Engineer (SCM Platform) | 1 | 서버·백엔드 |
| Backend Engineer (Search&Recommendation) | 1 | 서버·백엔드 |
| Backend Engineer (무신사페이먼츠/결제) | 1 | 서버·백엔드 |
| Backend Engineer (무신사페이먼츠/선불) | 1 | 서버·백엔드 |
| Brand Marketer (Social Impact Manager) | 1 | **None** |
| Brand Marketer (글로벌 브랜드마케팅) | 1 | **None** |
| Buying MD (Footwear) | 1 | **None** |
| Buying MD (Sports / Outdoor) | 1 | **None** |
| CX Program Manager | 1 | **None** |
| Cloud Engineer (Foundation Platform) | 1 | 서버·백엔드 |
| Commerce PM Assistant | 1 | **None** |
| DBA (Foundation Platform) | 1 | **None** |
| Data Operations Lead | 1 | 데이터·AI |
| Engineering Manager (무신사페이먼츠/결제) | 1 | **None** |
| Engineering Manager (무신사페이먼츠/정산) | 1 | **None** |
| Engineering Manager (코어 파트너) | 1 | 서버·백엔드 |
| Engineering Manager(Infra Platform) | 1 | 서버·백엔드 |
| Fashion Designer (IP Business) | 1 | **None** |
| Fashion Designer (무신사 스탠다드/라이프웨어) | 1 | **None** |
| Fashion Designer (무신사 스탠다드/우먼즈) | 1 | **None** |
| FinOps Engineer | 1 | **None** |
| Global Brand Marketer | 1 | **None** |
| Global Brand Marketer (Beauty PB) | 1 | **None** |
| Global CX Specialist (Japan)  | 1 | **None** |
| Global Contents Marketer (Beauty PB) | 1 | **None** |
| Global Logistics 담당자 | 1 | **None** |
| Global Performance Marketer | 1 | **None** |
| Global Retail Manager (무신사 스탠다드) | 1 | **None** |
| Growth Marketer (CRM) | 1 | **None** |
| Growth Marketer (O4O 옴니채널) | 1 | **None** |
| Growth Marketing Lead | 1 | **None** |
| Growth Marketing Lead (글로벌 스토어) | 1 | **None** |
| HR Generalist (무신사로지스틱스) | 1 | **None** |
| IMC Marketer (무신사 스탠다드) | 1 | **None** |
| IP 컬래버 소싱 담당자 (무신사 스탠다드) | 1 | **None** |
| IT Service Administrator | 1 | **None** |
| Interpreter & Translator (Chinese - Korean) | 1 | **None** |
| MD (IP Business) | 1 | **None** |
| MD (남성패션) | 1 | **None** |
| Machine Learning Engineer (AI) | 1 | 데이터·AI |
| Machine Learning Engineer (AdTech/MarTech) | 1 | 데이터·AI |
| Network Security Engineer (SASE&CASB) | 1 | **None** |
| On-Site Marketer (전사캠페인) | 1 | **None** |
| On-Site Marketer (채널 기획) | 1 | **None** |
| Operations Assistant (리테일 상품 운영) | 1 | **None** |
| Operations Assistant (이벤트 운영) | 1 | **None** |
| Package Designer (Beauty PB) | 1 | **None** |
| Performance Marketer (Beauty PB) | 1 | **None** |
| Photographer (무신사로지스틱스) | 1 | **None** |
| Planning MD (Footwear) | 1 | **None** |
| Product Data Analyst (Data Intelligence) | 1 | 데이터·AI |
| Product Designer (Commerce) | 1 | **None** |
| Product Lead (Core Customer Growth) | 1 | **None** |
| Product Lead (물류) | 1 | **None** |
| Product Lead (유즈드) | 1 | **None** |
| Product Manager (29CM Order & Pricing) | 1 | **None** |
| Product Manager (Core Partner) | 1 | **None** |
| Product Manager (PDP/캠페인/콘텐츠) | 1 | **None** |
| Product Manager (SCM) | 1 | **None** |
| Product Manager (무신사페이먼츠/결제) | 1 | **None** |
| Product Manager (앱테크) | 1 | **None** |
| Product Manager(Core Catalog) | 1 | **None** |
| Program Manager (Commerce Platform) | 1 | **None** |
| Program Manager (글로벌) | 1 | **None** |
| Program Manager (커머스 정책 기획) | 1 | **None** |
| Program Manager (29CM 커머스) | 1 | **None** |
| Release & IT Operations Engineer (무신사페이먼츠) | 1 | 서버·백엔드 |
| Retail Marketer (무신사 스탠다드) | 1 | **None** |
| Retail Media Experience Manager | 1 | **None** |
| Retail Media Growth Lead | 1 | **None** |
| Retail Media Growth Manager | 1 | **None** |
| Retail Operation Manager (무신사 스탠다드) | 1 | **None** |
| SAP Engineer (MM) | 1 | **None** |
| SAP FI 개발·운영 (Platform Business Operation) | 1 | **None** |
| Security Compliance Manager | 1 | **None** |
| Security Engineer (접근제어/암호키관리 운영) | 1 | **None** |
| Senior MD (글로벌패션) | 1 | **None** |
| Senior Retail Media Growth Manager | 1 | **None** |
| Social Marketing Lead (무신사·29CM) | 1 | **None** |
| Technical Program Manager (Infra) | 1 | **None** |
| VMD (무신사동남아/중동) | 1 | **None** |
| Visual Retoucher (Beauty PB) | 1 | **None** |
| 다이마루 소싱/생산관리 담당자 (무신사 스탠다드) | 1 | **None** |
| 디지털/가전 MD (29CM) | 1 | **None** |
| 머천다이징 VMD (무신사 스탠다드) | 1 | **None** |
| 무신사 오프라인 스토어 SNS 운영 담당자 | 1 | **None** |
| 물류 Program Manager (무신사로지스틱스)  | 1 | **None** |
| 물류 운영 관리자 (무신사로지스틱스)  | 1 | **None** |
| 물류 전략 기획 담당자 (무신사로지스틱스)  | 1 | **None** |
| 물류센터 정산 담당자 (무신사로지스틱스) | 1 | **None** |
| 반품 공정 관리자 (무신사로지스틱스) | 1 | **None** |
| 뷰티 오프라인 MD | 1 | **None** |
| 브랜드 기획자 (29CM) | 1 | **None** |
| 상품컨트롤 MD (무신사 스탠다드) | 1 | **None** |
| 소싱/생산관리 담당자 (PB 브랜드) | 1 | **None** |
| 소싱/생산관리 담당자 (무신사 스탠다드) | 1 | **None** |
| 소재 소싱/생산관리 담당자 (무신사 스탠다드) | 1 | **None** |
| 소재 소싱/생산관리 담당자 (통합소싱) | 1 | **None** |
| 스킨케어 BM (Beauty PB) | 1 | **None** |
| 오프라인 뷰티 영업 관리 담당자 | 1 | **None** |
| 오프라인 커머스 마케팅 AMD | 1 | **None** |
| 오프라인 홈 MD (29CM) | 1 | **None** |
| 온사이트 채널 플래너 (29CM) | 1 | **None** |
| 우먼즈 상품기획 MD (무신사 스탠다드) | 1 | **None** |
| 우븐 소싱/생산관리 담당자 (무신사 스탠다드) | 1 | **None** |
| 유튜브 콘텐츠 기획/제작 매니저  | 1 | **None** |
| 잡화 소싱/생산관리 담당자 (통합소싱) | 1 | **None** |
| 재무기획 담당자 | 1 | **None** |
| 카테고리 마케터 (29CM)  | 1 | **None** |
| 컬래버 상품기획 MD (무신사 스탠다드) | 1 | **None** |
| 컬래버레이션 Marketer (무신사 스탠다드) | 1 | **None** |
| 콘텐츠 기획 담당자 (무신사 스탠다드) | 1 | **None** |
| 콘텐츠 에디터 (29CM)  | 1 | **None** |
| 키즈 MD  | 1 | **None** |
| 키즈 상품기획 MD (무신사 스탠다드) | 1 | **None** |
| 패션 오프라인 영업 담당자 (무신사 트레이딩) | 1 | **None** |

### 컬리 (`kurly`, greeting) — 69건

| title | 건수 | 현재 분류 |
|---|---:|---|
|  물류센터 자동화 설비 구축 Project Assistant Manager (계약직) | 1 | **None** |
| AI·검색 운영지원 담당 (체험형 인턴) | 1 | 데이터·AI |
| BX 디자이너 | 1 | **None** |
| CRM 마케팅 리드 | 1 | **None** |
| EHS 보건관리자 (김포) | 1 | **None** |
| EHS 안전관리자 | 1 | **None** |
| EHS 진단 Auditor | 1 | **None** |
| FC프로세스 개선 담당자 (송파) | 1 | **None** |
| HMR MD | 1 | **None** |
| HRBP(HR Business Partner) | 1 | **None** |
| HRIS 담당자 | 1 | **None** |
| IT 자산/라이선스 담당자 | 1 | 서버·백엔드 |
| Talent Acquisition Partner (5~8년) | 1 | **None** |
| 가공 MD | 1 | **None** |
| 개인정보보호 담당자 | 1 | **None** |
| 고객경험지원 담당자 | 1 | **None** |
| 광고 영업 담당자 (중대형 광고주 세일즈) | 1 | **None** |
| 국내 뷰티PB 마케터 (7년 이상) | 1 | **None** |
| 그로스 Product Manager (어필리에이트 제품) | 1 | **None** |
| 네트워크 보안 솔루션 운영 담당자 | 1 | **None** |
| 물류신사업 사업관리 담당자 | 1 | **None** |
| 미국 이커머스 마케터 | 1 | **None** |
| 뷰티 MD | 1 | **None** |
| 뷰티 MD 운영지원 담당자 (계약직) | 1 | **None** |
| 뷰티 PB상품기획 담당자 | 1 | **None** |
| 뷰티 에디터 | 1 | **None** |
| 뷰티/패션 프로모션 기획 마케터 (3년 이상) | 1 | **None** |
| 브랜드컨텐츠 기획 담당자 | 1 | **None** |
| 사내 변호사 (Compliance) | 1 | **None** |
| 사내 변호사 (개인정보 보호) | 1 | **None** |
| 상세페이지 컨텐츠 디자이너 | 1 | **None** |
| 생활 MD (주방/리빙) | 1 | **None** |
| 생활 MD 운영지원 (계약직) | 1 | **None** |
| 서버 엔지니어 | 1 | 서버·백엔드 |
| 소셜 미디어 마케터(SNS) | 1 | **None** |
| 시니어 그로스 마케터 | 1 | **None** |
| 시니어 데이터 엔지니어  | 1 | 데이터·AI |
| 오프라인 스토어 BX 디자이너 | 1 | **None** |
| 오프라인 스토어 마케팅기획 담당자 | 1 | **None** |
| 오프라인 스토어 영업기획 담당자 | 1 | **None** |
| 온라인 마케팅/프로모션 디자이너 | 1 | **None** |
| 유저마케팅 그로스 마케터 (CRM기획 및 운영) | 1 | **None** |
| 인사기획 담당자  | 1 | **None** |
| 재무기획 담당자 (Strategic Finance) | 1 | **None** |
| 정보보호 정책 담당자 | 1 | **None** |
| 주니어 뷰티 MD  | 1 | **None** |
| 캠페인 매니저(브랜딩/프로모션) | 1 | **None** |
| 커머스 Product Manager (상품) | 1 | **None** |
| 커머스 Product Manager (홈/전시) | 1 | **None** |
| 커머스 백엔드 개발자 (상품/주문/회원/파트너) | 1 | 서버·백엔드 |
| 커머스 시니어 백엔드 개발자(홈/전시/광고) | 1 | 서버·백엔드 |
| 커머스 시니어 프론트엔드 개발자 | 1 | 웹 프론트엔드 |
| 커머스 주니어 프론트엔드 개발자 | 1 | 웹 프론트엔드 |
| 커머스사업 B2G 영업 담당자 | 1 | **None** |
| 커머스사업 B2G 운영지원 담당자 (계약직) | 1 | **None** |
| 컨텐츠 디자이너 (계약직) | 1 | **None** |
| 패션 컨텐츠 디자이너 (계약직) | 1 | **None** |
| 퍼포먼스 마케터 | 1 | **None** |
| 퍼포먼스 마케터(UA프로모션 기획) | 1 | **None** |
| 포장기획 담당자 (송파) | 1 | **None** |
| 푸드 에디터 | 1 | **None** |
| 풀필먼트 백엔드 개발자 | 1 | 서버·백엔드 |
| 풀필먼트 시니어 프론트엔드 개발자 | 1 | 웹 프론트엔드 |
| 풀필먼트 주니어 프론트엔드 개발자 | 1 | 웹 프론트엔드 |
| 프로덕트 디자인 그룹장 | 1 | **None** |
| 프로모션 기획 마케터 (3년 이상) | 1 | **None** |
| 핀테크 백엔드 개발자 (결제) | 1 | 서버·백엔드 |
| 핀테크 정보보호 관리자 | 1 | **None** |
| 핀테크 프론트엔드 개발자 (결제) | 1 | 웹 프론트엔드 |

### 캐치테이블 (`catchtable`, greeting) — 41건

| title | 건수 | 현재 분류 |
|---|---:|---|
| AX Manager (6년차 이상) | 1 | 데이터·AI |
| B2B Front-end Developer | 1 | **None** |
| B2B 매장 영업 담당자 | 1 | **None** |
| B2B 매장 영업 담당자 (계약직/정규직 전환 기회) | 1 | **None** |
| B2B 매장 영업 인턴 (6개월/정규직 전환 기회) | 1 | **None** |
| B2B 오퍼레이션 매니저 (2년차 이상)  | 1 | **None** |
| B2B 온라인 세일즈 담당자 | 1 | **None** |
| B2C Product Manager (Search&Discovery-PM) | 1 | **None** |
| Brand Contents Assistant (6개월 인턴) | 1 | **None** |
| Business Analyst | 1 | 데이터·AI |
| Business Development Manager (사업기획/사업개발) | 1 | **None** |
| Business Owner (BO, 사업기획/관리) | 1 | **None** |
| FP&A(경영기획) 리소스 분석 인턴 (6개월) | 1 | **None** |
| Management Trainee - 운영 (채용연계형 인턴, 6개월) | 1 | **None** |
| Marketing Designer | 1 | **None** |
| Product Data Analyst (Data Analysis Part/5년이상) | 1 | 데이터·AI |
| Product Designer (Search&Discovery) | 1 | **None** |
| Recruiting Manager | 1 | **None** |
| Technical Operator (Global-Japan) | 1 | **None** |
| 광고 영업 담당자 | 1 | **None** |
| 광고 영업 담당자 (계약직/정규직 전환 기회) | 1 | **None** |
| 광고 영업 인턴 (6개월/정규직 전환 기회) | 1 | **None** |
| 사외 추천 | 1 | **None** |
| 인재풀 등록 - Business & Sales | 1 | **None** |
| 인재풀 등록 - Data | 1 | 데이터·AI |
| 인재풀 등록 - Design | 1 | **None** |
| 인재풀 등록 - Engineering | 1 | **None** |
| 인재풀 등록 - Marketing | 1 | **None** |
| 인재풀 등록 - People | 1 | **None** |
| 인재풀 등록 - Product | 1 | **None** |
| 인재풀 등록 - Strategy | 1 | **None** |
| 인재풀 등록 - 페이 서비스 기획 및 개발 | 1 | **None** |
| 일본 GTM TF 영업 | 1 | **None** |
| 자금 및 회계 담당자 (0~3년차) | 1 | **None** |
| 총무 담당자 (1년 계약직) | 1 | **None** |
| 총무 담당자 (6개월/정규직 전환 기회) | 1 | **None** |
| 캐치테이블페이_결제서비스팀 PM/PO 팀장 | 1 | **None** |
| 콘텐츠 마케터 | 1 | **None** |
| 프로모션 마케터 | 1 | **None** |
| 플랫폼 디자이너 (Platform Designer) | 1 | **None** |
| 필드세일즈 영업 지원 (6개월 인턴)  | 1 | **None** |

### 카카오페이 (`kakaopay`, greeting) — 31건

| title | 건수 | 현재 분류 |
|---|---:|---|
| [계약직] 정보 협력 담당자 - 대외기관 정보 제공 지원 | 1 | **None** |
| [디지털자산] DevOps 엔지니어 - 클라우드 기반 블록체인 서비스 인프라 구축 & 운영 | 1 | **None** |
| [스테이블코인] 서버 개발자 - 스테이블코인 발행 & 유통 | 1 | 서버·백엔드 |
| [스테이블코인] 프로덕트 매니저 - 스테이블코인 & 월렛 프로덕트 | 1 | **None** |
| [어시스턴트] 대출 마케팅 업무 운영 지원 | 1 | **None** |
| [어시스턴트] 오프라인 가맹점 심사 업무 지원  | 1 | **None** |
| [어시스턴트] 오프라인 결제 마케팅 업무 지원 | 1 | **None** |
| [어시스턴트] 오프라인 롱테일 결제환경 개선 프로젝트 현장 운영 담당 | 1 | **None** |
| [어시스턴트] 카카오페이 광고 운영 지원 | 1 | **None** |
| 내부 감사 담당자 | 1 | **None** |
| 데이터 기획자 - 데이터 거버넌스 정책/시스템 | 1 | 데이터·AI |
| 데이터 엔지니어 - 데이터 플랫폼 | 1 | 데이터·AI |
| 마케터 - 데이터 마케팅 전략/실행 | 1 | 데이터·AI |
| 사업 담당자 - 오프라인 결제 롱테일 채널 | 1 | **None** |
| 사업 담당자 - 해외 온라인 결제 | 1 | **None** |
| 서버 개발자 - 결제 서비스 | 1 | 서버·백엔드 |
| 서버 개발자 - 대출 중개/신용관리 서비스 | 1 | 서버·백엔드 |
| 서버 개발자 - 데이터 플랫폼 | 1 | 서버·백엔드 |
| 서버 개발자 - 시니어/미성년 사용자 전용 서비스 | 1 | 서버·백엔드 |
| 인재 pool - 기술 | 1 | **None** |
| 인재 pool - 디자인 | 1 | **None** |
| 인재 pool - 비즈니스 | 1 | **None** |
| 인재 pool - 스탭 | 1 | **None** |
| 인재 pool - 프로덕트 | 1 | **None** |
| 컴플라이언스 담당자 - 개인(신용)정보 보호 | 1 | **None** |
| 프로덕트 매니저 - 결제 서비스 (시니어) | 1 | **None** |
| 프로덕트 매니저 - 광고 수익화 및 혜택 서비스 그로스 | 1 | **None** |
| 프로덕트 매니저 - 광고 프로덕트 | 1 | **None** |
| 프로덕트 엔지니어 - 사내 생산성 플랫폼 | 1 | **None** |
| 프로젝트 매니저 - 프로젝트 관리 | 1 | **None** |
| 프론트엔드 개발자 - 자산 서비스 | 1 | 웹 프론트엔드 |

### 여기어때 (`yeogieotdae`, greeting) — 26건

| title | 건수 | 현재 분류 |
|---|---:|---|
| AD Sales Manager [강원지역] | 1 | **None** |
| AD Sales Manager [경남지역/계약직(1년)] | 1 | **None** |
| AD Sales Manager [경북지역] | 1 | **None** |
| AD Sales Manager [서울•인천•경기지역] | 1 | **None** |
| AD Sales Manager [제주지역] | 1 | **None** |
| AD Sales Manager [충청지역/계약직(1년)] | 1 | **None** |
| CRM Marketer | 1 | **None** |
| Cloud Security & Tech Leader | 1 | **None** |
| Contents Marketer | 1 | **None** |
| Data Analyst [Business Insight]  | 1 | 데이터·AI |
| DevOps Team Leader | 1 | **None** |
| Enterprise Sales Manager | 1 | **None** |
| Operations Manager [Enterprise Business] | 1 | **None** |
| Pension Sales Manager [강원 담당/서울 근무] | 1 | **None** |
| Photographer [Pension] | 1 | **None** |
| Privacy Team Leader | 1 | **None** |
| Product Owner [상품/연동] | 1 | **None** |
| Product Owner [정산·재무·회계시스템] | 1 | **None** |
| Promotion Marketer [Sales Promotion] | 1 | **None** |
| Security Engineer [모의해킹 및 취약점진단]  | 1 | **None** |
| Site Reliability Engineer | 1 | **None** |
| Strategic Planning Manager | 1 | **None** |
| Tech Strategy Leader | 1 | **None** |
| Technical Product Owner | 1 | **None** |
| UX Designer [Core UX] | 1 | **None** |
| ✈️ Talent Pool | 1 | **None** |

### 카카오모빌리티 (`kakaomobility`, greeting) — 22건

| title | 건수 | 현재 분류 |
|---|---:|---|
| QA 엔지니어 | 1 | **None** |
| SLAM research scientist (R&D) | 1 | **None** |
| [Assistant] POI서비스팀 업무 보조 | 1 | **None** |
| [Assistant] 영상콘텐츠팀 업무 보조 | 1 | **None** |
| [Contract] 사업 운영지원 담당자 | 1 | **None** |
| [Contract] 자율주행 HW 테크니션 | 1 | **None** |
| [집중채용] 자율주행 Research Engineer (Internship) | 1 | **None** |
| [집중채용] 자율주행 Research Engineer (MS) | 1 | **None** |
| [집중채용] 자율주행 Research Engineer (Ph.D) | 1 | **None** |
| 공간정보 기획자 | 1 | **None** |
| 내비게이션 3D 지도 렌더링 엔진 개발자 | 1 | **None** |
| 머신러닝 research scientist (R&D) | 1 | 데이터·AI |
| 물류 & 에이전트 개발실 백엔드 개발자 | 1 | 서버·백엔드 |
| 백엔드 개발자(공간정보 시스템 개발) | 1 | 서버·백엔드 |
| 백엔드 개발자(내비 서비스) | 1 | 서버·백엔드 |
| 백엔드 개발자(주차 플랫폼 개발)  | 1 | 서버·백엔드 |
| 사내 변호사 | 1 | **None** |
| 자율주행 AI Perception 엔지니어 (R&D) | 1 | 데이터·AI |
| 자율주행 AI 엔지니어 (R&D) | 1 | 데이터·AI |
| 자율주행 SLAM 엔지니어 (R&D) | 1 | **None** |
| 자율주행 시스템 엔지니어 (R&D) | 1 | **None** |
| 자율주행 인증/규제 대응 담당자 | 1 | **None** |

### 왓챠 (`watcha`, greeting) — 1건

| title | 건수 | 현재 분류 |
|---|---:|---|
| 백엔드 개발자 - 미디어 플랫폼 | 1 | 서버·백엔드 |

### SSG.COM (`ssg`, greeting) — 0건

(공고 없음)

### 데브시스터즈 (`devsisters`, greeting) — 0건

(공고 없음)

### 마이리얼트립 (`myrealtrip`, greeting) — 21건

| title | 건수 | 현재 분류 |
|---|---:|---|
| Flight실 항공사업팀 사업기획 매니저 | 1 | **None** |
| Global Stay실 Americas & EMEA팀 사업 개발 매니저 | 1 | **None** |
| Growth실 Ad Sales & Account Manager  | 1 | **None** |
| Growth실 인플루언서 마케팅 매니저(신입) | 1 | **None** |
| T&A실 글로벌 파트너 마케팅 매니저 | 1 | **None** |
| T&A실 글로벌 파트너 전략 매니저 (Global Partnership Strategy Manager) | 1 | **None** |
| T&A실 미주·대양주 사업개발 매니저 | 1 | **None** |
| T&A실 사업 개발 매니저(신입) | 1 | **None** |
| T&A실 유럽팀 사업개발 매니저 | 1 | **None** |
| T&A실 중화권 사업개발 매니저 (중국어 가능자 우대) | 1 | **None** |
| [AICX] 비항공지원팀 파트리더 (정규직)  | 1 | **None** |
| [AICX] 항공응대 매니저  | 1 | **None** |
| 국내 T&A팀 팀장 | 1 | **None** |
| 국내숙박실 국내사업 Account Manager | 1 | **None** |
| 웰니스실 메디컬팀 B2B 제휴 영업 매니저  | 1 | **None** |
| 웰니스실 뷰티웰니스팀 B2B 제휴 영업 매니저 | 1 | **None** |
| 인재풀 | 1 | **None** |
| 재무관리실 경영관리팀 IR Manager | 1 | **None** |
| 정보보안실 보안 분석&대응 매니저 | 1 | **None** |
| 정보보안실 보안취약점 진단 매니저 | 1 | **None** |
| 패키지실 신사업 팀장 (맞춤여행) | 1 | **None** |

### 리멤버 (`remember`, ninehire) — 19건

| title | 건수 | 현재 분류 |
|---|---:|---|
| <리멤버 인재풀 등록> | 1 | **None** |
| AI Agent Engineer | 1 | 데이터·AI |
| Brand Designer | 1 | **None** |
| Data Engineer | 1 | 데이터·AI |
| Database Engineer | 1 | 데이터·AI |
| Frontend Software Engineer | 1 | 웹 프론트엔드 |
| [리멤버 자회사] 이안손앤컴퍼니 Client Services Associate | 1 | **None** |
| 광고사업 B2B Sales Manager | 1 | **None** |
| 광고운영팀 운영 Manager | 1 | **None** |
| 교육 기획 및 운영 담당자(계약직) | 1 | **None** |
| 대학·공공기관 Sales Manager | 1 | **None** |
| 리멤버 직속 헤드헌팅 PM | 1 | **None** |
| 브랜드마케팅팀 팀장 | 1 | **None** |
| 영업 SDR 담당자 (B2B 영업대행 신사업 초기멤버) | 1 | **None** |
| 인재솔루션팀 Account Manager | 1 | **None** |
| 재무실 자금 담당자 | 1 | **None** |
| 정보 보호 담당자 | 1 | **None** |
| 채용사업 B2B Sales Manager | 1 | **None** |
| 채용사업실 Strategic Client Partner | 1 | **None** |

### 요기요 (`yogiyo`, ninehire) — 12건

| title | 건수 | 현재 분류 |
|---|---:|---|
| [Finance] 재무회계 팀원 (2년 이상) | 1 | **None** |
| [Logistics] Logistics 사업운영 담당자 (2년 이상) | 1 | **None** |
| [Logistics] 모니터링 운영 지원 담당자 (계약직, 6개월) | 1 | **None** |
| [Merchant Growth] MG전략 기획 담당자(3년 이상) | 1 | **None** |
| [Product] Customer Product Owner (3년 이상) | 1 | **None** |
| [Security] Information Security Manager (관리보안 담당자/5년 이상) | 1 | **None** |
| [Security] Privacy Manager (개인정보보호 담당자/5년 이상) | 1 | **None** |
| [Security] Web & Application Security (5년 이상) | 1 | 웹 프론트엔드 |
| [Tech] Business Intelligence Data Engineer (7년 이상) | 1 | 데이터·AI |
| [Tech] Data Governance Lead (10년 이상) | 1 | 데이터·AI |
| [마케팅본부] Payment 제휴 기획 담당자 (4년 이상) | 1 | **None** |
| [마케팅본부] 구독 멤버십 기획 및 운영 담당자 (4년 이상) | 1 | **None** |

### 네이버 (`naver`, custom) — 42건

| title | 건수 | 현재 분류 |
|---|---:|---|
| [NAVER Cloud] Global HR 운영 지원 (계약) | 1 | **None** |
| [NAVER Cloud] 글로벌 사업기획 및 개발 담당자 (경력) | 1 | **None** |
| [NAVER Cloud] 네이버 클라우드 플랫폼(NCP) IaaS/AI Factory 상품 기획 (경력) | 1 | 데이터·AI |
| [NAVER Cloud] 대외정책대응 및 분석개발 담당자 (경력) | 1 | **None** |
| [NAVER Cloud] 클라우드 비즈니스 사업/영업/파트너 관리 (경력) | 1 | **None** |
| [NAVER Cloud] 클라우드 사업개발/세일즈 분야 채용 (경력) | 1 | **None** |
| [NAVER I&S] 소프트웨어 자산·라이선스 운영·기획 담당 (경력) | 1 | **None** |
| [NAVER] N배송 WMS(Warehouse Management System) 기획 (경력) | 1 | **None** |
| [NAVER] 광고 프로덕트 기획 경력 채용 | 1 | **None** |
| [NAVER] 산업보건 담당 (경력) | 1 | **None** |
| [NAVER] 스마트스토어 판매자센터 운영 (계약) | 1 | **None** |
| [SNOW] UI/프로모션 디자이너 (계약직) | 1 | **None** |
| [SNOW] 남미(스페인어권) 컨텐츠 마케터 (계약직) | 1 | **None** |
| [네이버랩스] Embedded System Hardware Engineer | 1 | **None** |
| [네이버랩스] Robot System Software Engineer | 1 | **None** |
| [네이버웹툰] AI 서비스 기획 (체험형 인턴) | 1 | 웹 프론트엔드 |
| [네이버웹툰] Ads Design 영상 디자이너 (계약직) | 1 | 웹 프론트엔드 |
| [네이버웹툰] Agency Partner (경력) | 1 | 웹 프론트엔드 |
| [네이버웹툰] Brand Marketing 영상 디자이너 (경력) | 1 | 웹 프론트엔드 |
| [네이버웹툰] Brand Media 콘텐츠 PD (계약직) | 1 | 웹 프론트엔드 |
| [네이버웹툰] Brand Media 콘텐츠 마케터 (체험형 인턴) | 1 | 웹 프론트엔드 |
| [네이버웹툰] Client Partner (경력) | 1 | 웹 프론트엔드 |
| [네이버웹툰] Data Product Engineer (경력) | 1 | 데이터·AI |
| [네이버웹툰] Disney 디지털 코믹스 플랫폼 서버 개발 (경력) | 1 | 서버·백엔드 |
| [네이버웹툰] EN Webtoon Growth&Marketing (체험형 인턴) | 1 | 웹 프론트엔드 |
| [네이버웹툰] FR Platform Growth Manager (경력) | 1 | 웹 프론트엔드 |
| [네이버웹툰] HR Operations Assistant (체험형 인턴) | 1 | 웹 프론트엔드 |
| [네이버웹툰] IP 사업 운영 담당(IP Business Operations Associate) (계약직) | 1 | 웹 프론트엔드 |
| [네이버웹툰] KR Creative 영상 제작 지원 (체험형 인턴) | 1 | 웹 프론트엔드 |
| [네이버웹툰] KR Strategy Associate (계약직) | 1 | 웹 프론트엔드 |
| [네이버웹툰] KR Webtoon Marketing Manager (경력) | 1 | 웹 프론트엔드 |
| [네이버웹툰] KR Webtoon 콘텐츠 마케터 (체험형 인턴) | 1 | 웹 프론트엔드 |
| [네이버웹툰] Search Intelligence Engineer (경력) | 1 | 데이터·AI |
| [네이버웹툰] UI/UX 프로덕트 디자이너 (UI/UX Product Designer) (경력) | 1 | 웹 프론트엔드 |
| [네이버웹툰] US GAAP Consolidation (경력) | 1 | 웹 프론트엔드 |
| [네이버웹툰] 글로벌 B2B 마케터 (Global B2B Marketer) (경력) | 1 | 웹 프론트엔드 |
| [네이버웹툰] 글로벌웹툰 콘텐츠 기획/운영 (체험형 인턴) | 1 | 웹 프론트엔드 |
| [네이버웹툰] 변호사 (경력) | 1 | 웹 프론트엔드 |
| [네이버웹툰] 전략 기획 (경력) | 1 | 웹 프론트엔드 |
| [네이버웹툰] 창작자 백엔드 시스템 정책/통제 (계약직) | 1 | 서버·백엔드 |
| [네이버웹툰] 컷츠 서비스 운영지원 (체험형 인턴) | 1 | 웹 프론트엔드 |
| [네이버웹툰] 플랫폼 그로스 매니저 (경력) | 1 | 웹 프론트엔드 |

### 카카오뱅크 (`kakaobank`, custom) — 33건

| title | 건수 | 현재 분류 |
|---|---:|---|
| AI 엔지니어 | 1 | 데이터·AI |
| DevOps 엔지니어 | 1 | **None** |
| FDS 전기통신금융사기 모니터링 담당자 - 주간 (계약직) | 1 | **None** |
| SM 사업 관리 및 유지보수 담당자 (계약직) | 1 | **None** |
| STR 모니터링 담당자 (계약직) | 1 | **None** |
| Vision AI 엔지니어 | 1 | 데이터·AI |
| 가계대출 상품 기획 및 운영 담당자 | 1 | **None** |
| 가계대출 상품 기획 및 운영 담당자 (계약직) | 1 | **None** |
| 금융기술연구소 콘텐츠 담당자 (계약직) | 1 | **None** |
| 금융업무 지원 담당자 (계약직) | 1 | **None** |
| 금융업무 지원 담당자 - 국가보훈대상자 전형 (계약직) | 1 | **None** |
| 기술연구 사무 어시스턴트 (체험형 인턴) | 1 | **None** |
| 담보여신 운영 담당자 | 1 | **None** |
| 데이터 엔지니어 - Data Warehouse | 1 | 데이터·AI |
| 방카슈랑스 사업 기획 담당자 | 1 | **None** |
| 법인 여신 상품 기획 담당자 | 1 | **None** |
| 법인 여신 제도 기획 및 운영 담당자 | 1 | **None** |
| 부동산 감정평가 업무 담당자 | 1 | **None** |
| 사업 전략 및 제휴 담당자 - 투자 | 1 | **None** |
| 서비스 기획자 - 대화형 AI 서비스 | 1 | 데이터·AI |
| 서비스 기획자 - 신사업 | 1 | **None** |
| 서비스 기획자 - 여신 | 1 | **None** |
| 수신 상품/서비스 운영 담당자 (계약직) | 1 | **None** |
| 수신제도(정책) 담당자 | 1 | **None** |
| 신사업(서베이) 운영 및 기획 어시스턴트 (체험형 인턴) | 1 | **None** |
| 여신 운영 업무 지원 담당자 (계약직) | 1 | **None** |
| 여신 전자등기 운영 담당자 (계약직) | 1 | **None** |
| 여신업무 도메인 개발자 | 1 | **None** |
| 여신플랫폼사업 운영 담당자 (계약직) | 1 | **None** |
| 인증 라이선스/플랫폼 기획 담당자 | 1 | **None** |
| 인증서비스 기획 어시스턴트 (체험형 인턴) | 1 | **None** |
| 정산 업무 담당자 (계약직) | 1 | **None** |
| 카카오뱅크 인재풀 등록 | 1 | **None** |

### 라인 (`line`, custom) — 72건

| title | 건수 | 현재 분류 |
|---|---:|---|
| AI Ad platform PM | 1 | 데이터·AI |
| AI SaaS Sales & Business Development Manager | 1 | 데이터·AI |
| AI/Data Platform Engineer | 1 | 서버·백엔드 |
| Backend Software Engineer | 1 | 서버·백엔드 |
| Billing Operation Specialist | 1 | **None** |
| Board Secretary | 1 | **None** |
| Business Development Manager / Associate Manager - Merchant Partnerships & Project Management(EPI) | 1 | **None** |
| CS representative(EPI) | 1 | **None** |
| Commerce Platform Operations Assistant | 1 | **None** |
| Compliance Officer(EPI) | 1 | **None** |
| Corporate Affairs_Risk Management & Resilience Manager | 1 | **None** |
| Corporate Business_Commercial PMO | 1 | **None** |
| Database Administrator (DBA)_KR-TW | 1 | 데이터·AI |
| Database Administrator Engineer(EPI) | 1 | 데이터·AI |
| Engineering_Senior Android Engineer | 1 | 모바일 |
| Engineering_Server Side Engineer | 1 | 서버·백엔드 |
| Engineering_Service QA | 1 | **None** |
| Fintech Data Scientist/Engineer | 1 | 데이터·AI |
| Front End Engineer | 1 | 웹 프론트엔드 |
| Front-End Engineer(EPI) | 1 | 웹 프론트엔드 |
| Frontend Engineer | 1 | 웹 프론트엔드 |
| HR Lead(EPI) | 1 | **None** |
| Internal Audit Lead(EPI) | 1 | **None** |
| LINE Pay Frontend Engineer | 1 | 웹 프론트엔드 |
| LINE Pay Product Designer (Promotion/Visual) | 1 | **None** |
| LINE Pay Product Designer (UI/UX) | 1 | **None** |
| LINE Pay Senior Brand Designer | 1 | **None** |
| LINE Pay Server Engineer | 1 | 서버·백엔드 |
| LINE Pay 星種子業務代表 | 1 | **None** |
| LINE Pay 정보보안 담당자 | 1 | **None** |
| LINE Taiwan_Communications Manager | 1 | **None** |
| LINE Taiwan_Corporate Business_Ads Product Planning_Product Manager | 1 | **None** |
| LINE Taiwan_Enterprise Business_Senior Performance Consulting Manager | 1 | **None** |
| LINE Taiwan_Global TODAY_Product Manager | 1 | **None** |
| LINE Taiwan_Portal & Content_Product Engineering | 1 | 서버·백엔드 |
| LINE Taiwan_Product & Strategy_Senior Display Ad Product Manager | 1 | **None** |
| LINE Taiwan_Product Manager (Messenger & OA Products) | 1 | **None** |
| LINE Taiwan_Security Engineer | 1 | **None** |
| LINE Taiwan_Senior Product Manager (AI Products) | 1 | 데이터·AI |
| LINE Taiwan_Senior Strategic Business Development Manager  | 1 | **None** |
| LINE WEBTOON - Global Typesetting Project Manager | 1 | **None** |
| LINE Webtoon_Assistant Marketing Manager - Content & Growth | 1 | **None** |
| Legal Counsel | 1 | **None** |
| Network Engineer(EPI) | 1 | **None** |
| Network Engineer_KR-TW | 1 | **None** |
| Platform Server QA Engineer | 1 | 서버·백엔드 |
| Product Planner | 1 | **None** |
| QA Engineer | 1 | **None** |
| QA Engineer(EPI) | 1 | **None** |
| Risk Management Specialist(EPI) | 1 | **None** |
| Senior Cloud Security Engineer | 1 | **None** |
| Senior Security Operations & Incident Response Engineer (SOC/CSIRT) | 1 | **None** |
| Server Engineer(EPI) | 1 | 서버·백엔드 |
| Server-Side Engineer | 1 | 서버·백엔드 |
| Server-Side Engineer(EPI) | 1 | 서버·백엔드 |
| Service Planner(EPI) | 1 | **None** |
| Stock Affairs Staff | 1 | **None** |
| System Engineer_KR-TW | 1 | **None** |
| TEC_LINE GIFTSHOP_Senior Business Growth Strategy & Operation Director | 1 | **None** |
| Technical Product Manager | 1 | **None** |
| UIT - Markup Engineer | 1 | 웹 프론트엔드 |
| UIT - Markup Engineer(EPI) | 1 | 웹 프론트엔드 |
| WEBTOON - Localization Assistant Manager / Manager (Thai Language QA) | 1 | **None** |
| [LINE Pay Taiwan] Branding Team Lead / Senior Manager | 1 | **None** |
| [LINE Pay Taiwan] Chinese - Korean Interpreter 中韓專業口筆譯人員 | 1 | **None** |
| [LINE Pay Taiwan] Chinese - Korean Translator | 1 | **None** |
| [LINE Pay Taiwan] Marketing Manager | 1 | **None** |
| [LINE Pay Taiwan] SNS Content Marketer | 1 | **None** |
| [LINE Pay Taiwan] Senior Account Manager | 1 | **None** |
| [LINE Pay Taiwan] Tap Reward Operations Specialist | 1 | **None** |
| [LINE Pay Taiwan] Video Content Specialist | 1 | **None** |
| 일본어 전문 통번역 프리랜서  | 1 | **None** |

### 당근 (`daangn`, custom) — 48건

| title | 건수 | 현재 분류 |
|---|---:|---|
| AD Sales Manager - 광고 (세일즈, Agency) | 1 | **None** |
| AD Sales Manager - 광고 (세일즈, Client) | 1 | **None** |
| Account Manager (인턴) - 로컬 잡스 D - 2 | 1 | **None** |
| B2B Content Designer (계약직) - 광고 | 1 | **None** |
| Brand Designer (계약직) - 브랜딩 (서비스 브랜딩 & UI) | 1 | **None** |
| Business Development Manager - 당근페이 | 1 | **None** |
| Character Designer, Illustrator - 브랜딩 | 1 | **None** |
| DBA (Database Administrator) - 인프라 (DB) | 1 | **None** |
| Design Engineer - 디자인 시스템 | 1 | **None** |
| ER Manager - 경영지원 (피플) | 1 | **None** |
| HRBP - 경영지원 (피플) | 1 | **None** |
| Lead Security Engineer - 인프라 (보안, Offensive Security) | 1 | **None** |
| Merchandiser (계약직) - 커머스 (신선식품) | 1 | **None** |
| Network Engineer - 인프라 (네트워크, Cloud) | 1 | **None** |
| Product Designer (인턴) - 로컬 잡스 (Trust & Safety) | 1 | **None** |
| Product Designer - Cross Product Growth (Engagement Part) | 1 | **None** |
| Product Designer - 부동산 | 1 | **None** |
| Product Manager - 광고 (광고 상품) | 1 | **None** |
| Product Manager - 당근페이 (Offline Payment) | 1 | **None** |
| Product Operations Manager - 중고거래 | 1 | **None** |
| Security Engineer - 인프라 (보안, AI Security) | 1 | 데이터·AI |
| Security Engineer - 인프라 (보안, Detection & Response) | 1 | **None** |
| Software Engineer - 테크코어 (AI Platform) | 1 | 데이터·AI |
| Software Engineer, Android | 1 | 모바일 |
| Software Engineer, Android (인턴) | 1 | 모바일 |
| Software Engineer, Backend (경력) - 피드 (ML Data Platform) | 1 | 서버·백엔드 |
| Software Engineer, Backend (신입) - 피드 (ML Data Platform) | 1 | 서버·백엔드 |
| Software Engineer, Backend (인턴) - 나의당근 D - 2 | 1 | 서버·백엔드 |
| Software Engineer, Backend - 광고 | 1 | 서버·백엔드 |
| Software Engineer, Backend - 나의당근 | 1 | 서버·백엔드 |
| Software Engineer, Backend - 당근페이 | 1 | 서버·백엔드 |
| Software Engineer, Backend - 로컬 잡스 (레슨/과외 팀) 초기 빌더 | 1 | 서버·백엔드 |
| Software Engineer, Backend - 부동산 | 1 | 서버·백엔드 |
| Software Engineer, Backend - 서비스 코어 (Identity Service) | 1 | 서버·백엔드 |
| Software Engineer, Backend - 인프라 (공통 서비스 개발, 콘텐츠 서빙) | 1 | 서버·백엔드 |
| Software Engineer, Backend - 커뮤니티 (아파트) | 1 | 서버·백엔드 |
| Software Engineer, Backend - 피드 (피드 인프라) | 1 | 서버·백엔드 |
| Software Engineer, Frontend (인턴) - 커뮤니티 D - 2 | 1 | 웹 프론트엔드 |
| Software Engineer, Frontend - Cross Product Growth (Engagement Part) | 1 | 웹 프론트엔드 |
| Software Engineer, Frontend - 당근페이 | 1 | 웹 프론트엔드 |
| Software Engineer, Frontend - 로컬 잡스 | 1 | 웹 프론트엔드 |
| Software Engineer, Frontend - 커뮤니티 (모임) | 1 | 웹 프론트엔드 |
| Software Engineer, Machine Learning | 1 | 데이터·AI |
| Software Engineer, Machine Learning - ML 인프라 | 1 | 데이터·AI |
| Software Engineer, Machine Learning - 검색 (품질) | 1 | 데이터·AI |
| Software Engineer, iOS | 1 | 모바일 |
| Trust & Safety Manager - 로컬 잡스 | 1 | **None** |
| Trust & Safety Manager - 부동산 | 1 | **None** |

### 티빙 (`tving`, custom) — 3건

| title | 건수 | 현재 분류 |
|---|---:|---|
| Ad Tech Backend Engineer | 1 | 서버·백엔드 |
| Agency Partner Team Lead | 1 | **None** |
| 자금담당자 | 1 | **None** |

### 채널톡 (`channeltalk`, custom) — 43건

| title | 건수 | 현재 분류 |
|---|---:|---|
| AI Product Owner | 1 | 데이터·AI |
| AI-BPO AX Business Operation, Senior | 1 | 데이터·AI |
| AI-BPO Business Development, Senior | 1 | 데이터·AI |
| Applied AI Engineer | 1 | 데이터·AI |
| Business Development Specialist | 1 | **None** |
| CEO Staff | 1 | **None** |
| CX Team Leader | 1 | **None** |
| Chief Information Security Officer | 1 | **None** |
| Customer Experience Specialist | 1 | **None** |
| Data Analyst | 1 | 데이터·AI |
| DevOps Engineer | 1 | **None** |
| Engineering Team, 영상  PD | 1 | **None** |
| Enterprise, Sales Account Executive | 1 | **None** |
| Enterprise, Sales Manager (Team Lead) | 1 | **None** |
| FP&A Manager (Team Lead) | 1 | **None** |
| Forward Deployed Engineer | 1 | **None** |
| GTM Specialist (Founding Member), San Francisco | 1 | **None** |
| Growth Marketer | 1 | **None** |
| Lead Product Manager | 1 | **None** |
| Machine Learning Engineer (Model Training) | 1 | **None** |
| Marketing Specialist | 1 | **None** |
| Mid-Market, Account Management Specialist | 1 | **None** |
| Mid-Market, Sales Account Executive | 1 | **None** |
| Mid-Market, Sales Development Representative | 1 | **None** |
| Product Designer | 1 | **None** |
| Product Designer, Senior | 1 | **None** |
| Product Designer, Staff | 1 | **None** |
| Product Manager (PM) | 1 | **None** |
| Recruiting Coordinator | 1 | **None** |
| SMB Account Executive | 1 | **None** |
| SMB Account Executive Manager, Team Lead | 1 | **None** |
| Sales Engineer | 1 | **None** |
| Sales Intern | 1 | **None** |
| Sales Manager (Team Lead) | 1 | **None** |
| Sales Operations Analyst | 1 | **None** |
| Sales Specialist (Public Sector) | 1 | **None** |
| Security Engineer | 1 | **None** |
| Senior Recruiter | 1 | **None** |
| Software Engineer | 1 | **None** |
| Software Engineer, Senior | 1 | **None** |
| Strategy Specialist | 1 | **None** |
| Treasury (Senior manager) | 1 | **None** |
| 음성 데이터 라벨링(단기 계약직) | 1 | 데이터·AI |

### 뱅크샐러드 (`banksalad`, custom) — 9건

| title | 건수 | 현재 분류 |
|---|---:|---|
| Contents Marketer (계약직) | 1 | **None** |
| Senior People & Culture Manager (인사 담당자) | 1 | **None** |
| [Frontier] AI Native Server Engineer (AI 네이티브 서버 엔지니어) | 1 | 서버·백엔드 |
| [초기멤버] Insurance Solution Coach (보험 솔루션 팀 코치) | 1 | **None** |
| [초기멤버] Product Manager (프로덕트 매니저, 보험) | 1 | **None** |
| [초기멤버] [리더십] Product Lead (프로덕트 리드, 광고) | 1 | **None** |
| [최초채용] [리더십] Head of Business (사업총괄) | 1 | **None** |
| [최초채용] [리더십] Head of Product | 1 | **None** |
| [최초채용] [리더십] Platform Product Lead (플랫폼 프로덕트 리드) | 1 | **None** |

### 하이퍼커넥트 (`hyperconnect`, custom) — 12건

| title | 건수 | 현재 분류 |
|---|---:|---|
| Accountant (1년 6개월 계약직) | 1 | **None** |
| Data Analyst (Azar) | 1 | 데이터·AI |
| Machine Learning Engineer (Match Group AI) | 1 | 데이터·AI |
| Machine Learning Software Engineer (Match Group AI) | 1 | 데이터·AI |
| Product Designer, International Growth (Tinder Seoul) | 1 | **None** |
| Product Manager (Azar) | 1 | **None** |
| Product Manager (Match Group AI) | 1 | 데이터·AI |
| Senior Data & Analytics Engineer (Azar) | 1 | 데이터·AI |
| Senior Machine Learning Engineer (Match Group AI) | 1 | 데이터·AI |
| Senior Software Engineer, Backend — Seoul Studios (Tinder Seoul) | 1 | 서버·백엔드 |
| Staff, Machine Learning Research Scientist (Azar) | 1 | 데이터·AI |
| Tinder Marketing Manager (2-year Contractor, 육아휴직 대체) | 1 | **None** |

### 쏘카 (`socar`, custom) — 29건

| title | 건수 | 현재 분류 |
|---|---:|---|
| CS운영기획 매니저 | 1 | **None** |
| HR Generalist (급여/인사운영) | 1 | **None** |
| HRBP (HR Business Partner) | 1 | **None** |
| IR 매니저 | 1 | **None** |
| Product Engineer | 1 | 데이터·AI |
| [계약직] 서비스 운영 매니저(쏘카구독) | 1 | **None** |
| [계약직] 외국인 응대 현장 운영 | 1 | **None** |
| [쏘카일레클] Embedded Firmware Engineer | 1 | 데이터·AI |
| [에이펙스 모빌리티] Applied Research Scientist | 1 | 데이터·AI |
| [에이펙스 모빌리티] Product Engineer | 1 | 데이터·AI |
| [에이펙스모빌리티] Embedded Platform SW Engineer (센서킷 플랫폼) | 1 | 데이터·AI |
| [에이펙스모빌리티] Mechanical Design Engineer (센서킷 기구) | 1 | 데이터·AI |
| [에이펙스모빌리티] Vehicle Integration Engineer (차량 전장·개조) | 1 | 데이터·AI |
| [인턴] 제주사업팀  | 1 | **None** |
| 고객센터 WFM 매니저 (Workforce Management) | 1 | **None** |
| 그로스 마케터 (퍼포먼스/시니어) | 1 | **None** |
| 내부회계관리제도 운영 담당자 | 1 | **None** |
| 데이터 분석가 | 1 | 데이터·AI |
| 모두의주차장 PO(Product Owner) | 1 | **None** |
| 사업기획자/시니어PO | 1 | **None** |
| 상품기획 매니저(쏘카신구독) | 1 | **None** |
| 정보보호 및 보안 엔지니어 | 1 | **None** |
| 제주사업팀 사업운영 매니저 | 1 | **None** |
| 차량 서비스 운영 매니저 | 1 | **None** |
| 카셰어링 거점운영 (파트너십) 매니저 | 1 | **None** |
| 카셰어링 사업개발 매니저 | 1 | **None** |
| 프로덕트 디자이너 (PD) | 1 | **None** |
| 프로덕트 매니저 (PM) | 1 | 데이터·AI |
| 플릿 운영(fleet operation) 및 자산 관리 매니저 | 1 | **None** |

### 카카오 (`kakao`, custom) — 64건

| title | 건수 | 현재 분류 |
|---|---:|---|
| AI Platform 추론 최적화 Engineer(경력) | 1 | 서버·백엔드 |
| AI Research Engineer (Search & Agent) (경력) | 1 | 데이터·AI |
| AI 데이터 라벨링_어시스턴트 | 1 | 데이터·AI |
| Data Analytics Engineer (경력) | 1 | 데이터·AI |
| Data Scientist (경력) | 1 | 데이터·AI |
| IR 매니저 (경력) | 1 | **None** |
| Interaction Designer (경력) | 1 | **None** |
| LLM Research Engineer (Post-training) (신입/경력) | 1 | 데이터·AI |
| Multimodal LLM Research Engineer (경력) | 1 | 데이터·AI |
| Shareholder Communication 매니저 (경력) | 1 | **None** |
| [공동체] (계약직) 정보 협력 담당자 - 대외기관 정보 제공 지원 | 1 | **None** |
| [공동체] 카카오게임즈 MMORPG 마케팅PM 영입 | 1 | **None** |
| [공동체] 카카오게임즈 게임 기술PM 영입 | 1 | **None** |
| [공동체] 카카오게임즈 서브컬처 마케팅PM 영입 | 1 | **None** |
| [공동체] 카카오모빌리티 QA 엔지니어 | 1 | **None** |
| [공동체] 카카오모빌리티 SLAM research scientist (R&D) | 1 | **None** |
| [공동체] 카카오모빌리티 공간정보 기획자 | 1 | **None** |
| [공동체] 카카오모빌리티 내비게이션 3D 지도 렌더링 엔진 개발자 | 1 | **None** |
| [공동체] 카카오모빌리티 머신러닝 research scientist (R&D) | 1 | 데이터·AI |
| [공동체] 카카오모빌리티 물류 & 에이전트 개발실 백엔드 개발자 | 1 | 서버·백엔드 |
| [공동체] 카카오모빌리티 백엔드 개발자(내비 서비스) | 1 | 서버·백엔드 |
| [공동체] 카카오모빌리티 백엔드 개발자(주차 플랫폼 개발) | 1 | 서버·백엔드 |
| [공동체] 카카오모빌리티 사내 변호사 | 1 | **None** |
| [공동체] 카카오모빌리티 사업 운영지원 담당자 | 1 | **None** |
| [공동체] 카카오모빌리티 자율주행 AI Perception 엔지니어 (R&D) | 1 | 데이터·AI |
| [공동체] 카카오모빌리티 자율주행 AI 엔지니어 (R&D) | 1 | 데이터·AI |
| [공동체] 카카오모빌리티 자율주행 HW 테크니션 | 1 | **None** |
| [공동체] 카카오모빌리티 자율주행 SLAM 엔지니어 (R&D) | 1 | **None** |
| [공동체] 카카오모빌리티 자율주행 시스템 엔지니어 (R&D) | 1 | **None** |
| [공동체] 카카오모빌리티 자율주행 인증/규제 대응 담당자 | 1 | **None** |
| [공동체] 카카오페이 DevOps 엔지니어 - 클라우드 기반 블록체인 서비스 인프라 구축 & 운영 | 1 | **None** |
| [공동체] 카카오페이 데이터 기획자 - 데이터 거버넌스 정책/시스템 | 1 | 데이터·AI |
| [공동체] 카카오페이 데이터 엔지니어 - 데이터 플랫폼 | 1 | 데이터·AI |
| [공동체] 카카오페이 마케터 - 데이터 마케팅 전략/실행 | 1 | 데이터·AI |
| [공동체] 카카오페이 사업 담당자 - 오프라인 결제 롱테일 채널 | 1 | **None** |
| [공동체] 카카오페이 사업 담당자 - 해외 온라인 결제 | 1 | **None** |
| [공동체] 카카오페이 서버 개발자 - 결제 서비스 | 1 | 서버·백엔드 |
| [공동체] 카카오페이 서버 개발자 - 대출 중개/신용관리 서비스 | 1 | 서버·백엔드 |
| [공동체] 카카오페이 서버 개발자 - 데이터 플랫폼 | 1 | 서버·백엔드 |
| [공동체] 카카오페이 서버 개발자 - 스테이블코인 발행 & 유통 | 1 | 서버·백엔드 |
| [공동체] 카카오페이 서버 개발자 - 시니어/미성년 사용자 전용 서비스 | 1 | 서버·백엔드 |
| [공동체] 카카오페이 프로덕트 매니저 - 결제 서비스 (시니어) | 1 | **None** |
| [공동체] 카카오페이 프로덕트 매니저 - 광고 수익화 및 혜택 서비스 그로스 | 1 | **None** |
| [공동체] 카카오페이 프로덕트 매니저 - 스테이블코인 & 월렛 프로덕트 | 1 | **None** |
| [공동체] 카카오페이 프로젝트 매니저 - 프로젝트 관리 | 1 | **None** |
| [공동체] 카카오페이 프론트엔드 개발자 - 자산 서비스 | 1 | 웹 프론트엔드 |
| [공동체] 카카오페이손해보험 Business Operations (사업제휴) 담당자 | 1 | **None** |
| [공동체] 카카오페이손해보험 PR·콘텐츠 어시스턴트 | 1 | **None** |
| [공동체] 카카오페이손해보험 시스템 개발·운영 엔지니어 | 1 | **None** |
| [공동체] 카카오헬스케어 AI Native EHR 개발 | 1 | 데이터·AI |
| [공동체] 카카오헬스케어 Data Engineer(Healthcare) | 1 | 데이터·AI |
| 노사 전략 및 기획 담당자 (경력) | 1 | **None** |
| 로컬임팩트 마케팅 운영_어시스턴트 | 1 | **None** |
| 서비스/플랫폼 QA 담당자 (경력) | 1 | **None** |
| 인플루언서 제휴_어시스턴트 | 1 | **None** |
| 직매입 물류 기획 및 운영 관리자 (경력) | 1 | **None** |
| 직매입 수요예측 및 재고계획 관리자 (경력) | 1 | **None** |
| 카카오 교육 프로그램 운영 지원_어시스턴트 | 1 | **None** |
| 카카오메이커스 MD_어시스턴트 | 1 | **None** |
| 카카오비즈니스 파트너 플랫폼 PM (경력) | 1 | **None** |
| 카카오톡 예약하기 서비스 마케팅 운영_어시스턴트 | 1 | **None** |
| 카카오프렌즈 공간디자인 VMD_어시스턴트 | 1 | **None** |
| 커머스 식품 QA 담당자 (신입/경력) | 1 | **None** |
| 톡딜 뷰티CM_어시스턴트 | 1 | **None** |

### 토스 (`toss`, custom) — 473건

| title | 건수 | 현재 분류 |
|---|---:|---|
| DevOps Engineer | 5 | 서버·백엔드 |
| Server Developer (Product) | 5 | 서버·백엔드 |
| FE Platform Engineer | 4 | 웹 프론트엔드 |
| Node.js Developer | 4 | 서버·백엔드 |
| Privacy Manager | 4 | **None** |
| Product Designer | 4 | **None** |
| Recruiting Business Partner | 4 | **None** |
| Server Developer (Platform) | 4 | 서버·백엔드 |
| Site Reliability Engineer | 4 | 서버·백엔드 |
| Data Analytics Engineer | 3 | 데이터·AI |
| General Affairs Specialist | 3 | **None** |
| HRBP | 3 | **None** |
| Platform Product Owner | 3 | **None** |
| Product Owner | 3 | **None** |
| QA Manager | 3 | **None** |
| UX Researcher | 3 | **None** |
| User Interview Assistant | 3 | **None** |
| Visual Designer | 3 | **None** |
| Android Developer | 2 | 모바일 |
| Business Analyst | 2 | **None** |
| Business Operations Manager | 2 | **None** |
| DBA | 2 | 데이터·AI |
| Data Engineer | 2 | 데이터·AI |
| DataOps Manager | 2 | 데이터·AI |
| Executive Assistant | 2 | **None** |
| General Affairs Manager | 2 | **None** |
| IT Audit Manager | 2 | **None** |
| IT Manager | 2 | **None** |
| IT Planning Manager | 2 | **None** |
| Information Security Manager (정보보호 정책/기획 담당) | 2 | **None** |
| Marketing Manager (Growth) | 2 | **None** |
| Network Engineer | 2 | **None** |
| Privacy Manager (개인정보보호 담당자) | 2 | **None** |
| Product Owner (Growth) | 2 | **None** |
| Recruiting Assistant | 2 | **None** |
| Risk Manager | 2 | **None** |
| Security Engineer (이벤트 분석/사고 대응) | 2 | 데이터·AI |
| Security Researcher | 2 | **None** |
| Strategy Manager  | 2 | **None** |
| iOS Developer | 2 | 모바일 |
|  Data Analytics Engineer (Data Warehouse/Platform) | 1 | 데이터·AI |
|  Privacy Protection Team Leader | 1 | **None** |
| AI Engineer (Ads) | 1 | 데이터·AI |
| AI Engineer (Brain, AIOC) | 1 | 데이터·AI |
| AI Engineer (Commerce) | 1 | 데이터·AI |
| AI Engineer (Model) | 1 | 데이터·AI |
| AI Engineer (WM)  | 1 | 데이터·AI |
| AI Manager | 1 | 데이터·AI |
| AI Platform Engineer (Inference Pipeline) | 1 | 데이터·AI |
| AI Platform Engineer (Platform) | 1 | 데이터·AI |
| AI Platform Engineer (Serving) | 1 | 데이터·AI |
| AI Product Team Leader | 1 | 데이터·AI |
| AIOps Platform Engineer | 1 | **None** |
| AML Manager (STR 기획 및 운영) | 1 | **None** |
| AML Monitoring Manager  | 1 | **None** |
| AML Operations Manager (Global) | 1 | **None** |
| AML Operations Specialist | 1 | **None** |
| AML Specialist | 1 | **None** |
| AML/CFT Manager (Gerente de PLD/FT, Toss Brazil) | 1 | **None** |
| Account Management Specialist | 1 | **None** |
| Account Manager (FacePay) | 1 | **None** |
| Account Manager (FacePay/Merchant Growth) | 1 | **None** |
| Account Manager (광고) | 1 | **None** |
| Account Manager (플랫폼 제휴/사업개발) | 1 | **None** |
| Accounting Admin | 1 | **None** |
| Accounting Manager (연결) | 1 | **None** |
| Analyst | 1 | **None** |
| Anti-Fraud Manager | 1 | **None** |
| Banking Product Owner (SOHO 여신) | 1 | **None** |
| Barista | 1 | **None** |
| Barista Support | 1 | **None** |
| Brand Manager (Content) | 1 | **None** |
| Brand Manager (Event) | 1 | **None** |
| Brand Manager (Marketing) | 1 | **None** |
| Business Content Marketing Manager | 1 | **None** |
| Business Development Representative | 1 | **None** |
| Business Enablement Manager | 1 | **None** |
| Business FP&A Manager | 1 | **None** |
| Business Marketing Manager (Field Marketer) | 1 | **None** |
| Business Marketing Specialist | 1 | **None** |
| Business Operations Assistant | 1 | **None** |
| Business Operations Assistant (Internship) | 1 | **None** |
| Business Operations Specialist | 1 | **None** |
| Business Partnership Manager | 1 | **None** |
| Business Public Affairs Manager | 1 | **None** |
| CA Operations Manager (예금압류&추심) | 1 | **None** |
| CEO Staff | 1 | **None** |
| CS Risk Manager | 1 | **None** |
| CX Planning Manager | 1 | **None** |
| Call Infra Engineer (IPCC, AICC) | 1 | **None** |
| Call Sales Assistant | 1 | **None** |
| Category MD (뷰티) | 1 | **None** |
| Category MD (생활 - 가구/홈데코/주방용품) | 1 | **None** |
| Category MD (신선식품 - 과일, 채소류) | 1 | **None** |
| Channel Sales Manager | 1 | **None** |
| Client Solutions Manager | 1 | **None** |
| Client Solutions Manager (AppInToss) | 1 | **None** |
| Collections Manager | 1 | **None** |
| Collections Manager (상각) | 1 | **None** |
| Collections Specialist (대위변제) | 1 | **None** |
| Commission Manager | 1 | **None** |
| Communications Manager | 1 | **None** |
| Community Operations Manager (Japan) | 1 | **None** |
| Community Specialist | 1 | **None** |
| Compensation Manager (Planning) | 1 | **None** |
| Compliance Manager | 1 | **None** |
| Compliance Manager (모니터링/점검) | 1 | **None** |
| Consumer Protection Manager (민원대응) | 1 | **None** |
| Consumer Protection Manager (비예금상품) | 1 | **None** |
| Consumer Protection Manager (정책/기획) | 1 | **None** |
| Content Producer | 1 | **None** |
| Content Specialist (Editing) | 1 | **None** |
| Core FP&A Manager | 1 | **None** |
| Corp Legal Team Leader | 1 | **None** |
| Corporate Credit Rating Team Leader | 1 | **None** |
| Corporate Development Manager | 1 | **None** |
| Corporate Development Team Leader  | 1 | **None** |
| Corporate Finance and IR Intern | 1 | **None** |
| Corporate Public Affairs Manager | 1 | **None** |
| Credit Rating Modeler | 1 | **None** |
| Culture Business Partner | 1 | **None** |
| Culture Coordinator | 1 | **None** |
| Customer Banking Specialist | 1 | **None** |
| Customer Guider (기본 문의 응대 · 9 to 6 근무) | 1 | **None** |
| Customer Guider (외국인 상담원 - 중국어/우즈베크어/베트남어) | 1 | **None** |
| Customer Guider (토스인컴 전화/채팅상담) | 1 | **None** |
| Customer Hero 페이먼츠 (평일 근무) | 1 | **None** |
| Customer Hero 플랫폼/증권 (정착지원금 50만원) | 1 | **None** |
| Customer Hero 플레이스 (9-6 고정근무 \| 입사축하금 50만원) | 1 | **None** |
| Customer Protection Manager (FDS) | 1 | **None** |
| Customer Protection Manager (소비자보호) | 1 | **None** |
| Customer Success Manager | 1 | **None** |
| Customer Success Specialist | 1 | **None** |
| DBA (MySQL) | 1 | 데이터·AI |
| DBA (Oracle) | 1 | 데이터·AI |
| Data Analyst | 1 | 데이터·AI |
| Data Analyst (7년 미만) | 1 | 데이터·AI |
| Data Analyst (7년 이상) | 1 | 데이터·AI |
| Data Analyst (Commerce Ads Platform) | 1 | 데이터·AI |
| Data Analyst (Growth) | 1 | 데이터·AI |
| Data Analyst (Recommendation) | 1 | 데이터·AI |
| Data Analyst (광고) | 1 | 데이터·AI |
| Data Analyst (전사전략) | 1 | 데이터·AI |
| Data Analytics Engineer (DW) | 1 | 데이터·AI |
| Data Analytics Engineer (DW/Global) | 1 | 데이터·AI |
| Data Analytics Engineer (Data Warehouse/Mart) | 1 | 데이터·AI |
| Data Analytics Engineer (Platform) | 1 | 데이터·AI |
| Data Analytics Engineer (Product) | 1 | 데이터·AI |
| Data Analytics Specialist | 1 | 데이터·AI |
| Data Engineer (Data Service Platform) | 1 | 데이터·AI |
| Data Engineer (Finance) | 1 | 데이터·AI |
| Data Engineer (Global) | 1 | 데이터·AI |
| Data Engineer (Platform) | 1 | 데이터·AI |
| Data Engineer (Realtime) | 1 | 데이터·AI |
| Data Engineer (금융데이터/AI) | 1 | 데이터·AI |
| Data Engineer (금융데이터/자문) | 1 | 데이터·AI |
| Data Engineer (금융데이터/재무) | 1 | 데이터·AI |
| Data Governance Manager | 1 | 데이터·AI |
| Data Manager (Governance) | 1 | 데이터·AI |
| Data Platform Engineer (Streaming) | 1 | 데이터·AI |
| Data Product Manager (AI) | 1 | 데이터·AI |
| Data Product Manager (Log) | 1 | 데이터·AI |
| Data Product Manager (Mart) | 1 | 데이터·AI |
| Data Scientist (Commerce Signal) | 1 | 데이터·AI |
| Data Scientist (FDS) | 1 | 데이터·AI |
| Design Staff (Product Designer) | 1 | **None** |
| Design System Migration Assistant | 1 | **None** |
| DevOps Engineer [산업기능요원/전문연구요원] | 1 | **None** |
| Developer Relations Manager | 1 | **None** |
| Device Hardware Quality Engineer | 1 | **None** |
| Device Software Engineer (Android) | 1 | 모바일 |
| Device Software Quality Engineer (Android) | 1 | 모바일 |
| Device 관련 포지션 인재풀 등록 | 1 | **None** |
| Direct Sales Associate | 1 | **None** |
| Direct Sales Manager | 1 | **None** |
| Enterprise Marketing Manager | 1 | **None** |
| Equity Operations Manager (국내주식 운영관리) | 1 | **None** |
| Finance Data System Developer | 1 | 데이터·AI |
| Finance Manager (Accounting) | 1 | **None** |
| Finance Manager(Tax) | 1 | **None** |
| Financial Compliance Manager (금융복합기업집단) | 1 | **None** |
| Financial Data Analyst (Accounting) | 1 | 데이터·AI |
| Financial Data Analyst (FP&A) | 1 | 데이터·AI |
| Financial Systems Manager (SAP) | 1 | **None** |
| Frontend Developer | 1 | 웹 프론트엔드 |
| Frontend Developer (2026년 커뮤니티 대규모 채용) | 1 | 웹 프론트엔드 |
| Frontend Developer (Ads) | 1 | 웹 프론트엔드 |
| Frontend Developer (Product) | 1 | 웹 프론트엔드 |
| Frontend Developer (보훈특별채용) | 1 | 웹 프론트엔드 |
| Frontend Developer [산업기능요원/전문연구요원] | 1 | 웹 프론트엔드 |
| GRC Manager (Global)  | 1 | **None** |
| GRC Manager (금융복합기업집단)  | 1 | **None** |
| General Affairs Assistant | 1 | **None** |
| General Affairs Assistant (신입/인턴) | 1 | **None** |
| General Affairs Manager  | 1 | **None** |
| General Affairs Specialist  | 1 | **None** |
| Global Beta Tester (Foreigner) | 1 | **None** |
| Global Compensation Manager | 1 | **None** |
| Global Finance Manager (Accounting) | 1 | **None** |
| Global UX Researcher | 1 | **None** |
| HR Coordinator (보훈제한채용) | 1 | **None** |
| HR Operations Manager (BPO 사업 HR 체계·운영 담당) | 1 | **None** |
| HR Operations Manager (내부 조직 HR 체계·운영 담당) | 1 | **None** |
| HRBP (Global) | 1 | **None** |
| IDC Assistant (단기계약직) | 1 | **None** |
| IDC Infrastructure Engineer (Network & System)  | 1 | **None** |
| IDC Manager | 1 | **None** |
| IR Manager (공시/주총)  | 1 | **None** |
| IR Operations Manager | 1 | **None** |
| IT Assistant (단기계약직)(인재풀) | 1 | **None** |
| IT Assurance Manager | 1 | **None** |
| IT Auditor | 1 | **None** |
| IT Governance Manager (BCP) | 1 | **None** |
| IT Manager (IT 및 콜 인프라 운영/IT 환경 기획) | 1 | **None** |
| IT Operations Specialist (Call Infra) | 1 | **None** |
| IT Planning Manager (데이터 변경통제)  | 1 | 데이터·AI |
| IT Planning Manager (예산관리)  | 1 | **None** |
| IT Planning Manager (자산관리)   | 1 | **None** |
| IT Planning Team Leader | 1 | **None** |
| IT SOX Manager | 1 | **None** |
| IT Strategy Manager | 1 | **None** |
| Information Security Manager (Global)  | 1 | **None** |
| Information Security Manager (보안 점검) | 1 | **None** |
| Information Security Manager (보안정책) | 1 | **None** |
| Infrastructure Operations Engineer | 1 | **None** |
| Internal Auditor (상시모니터링) | 1 | **None** |
| Internal Auditor (정보보호감사) | 1 | **None** |
| Internal Systems Engineer (MDM)  | 1 | **None** |
| KYC Operations Assistant | 1 | **None** |
| KYC Specialist | 1 | **None** |
| Leadership Talent Acquisition Manager | 1 | **None** |
| Legal Counsel (Corporate)  | 1 | **None** |
| Legal Counsel (Fintech) | 1 | **None** |
| Legal Counsel (Global)  | 1 | **None** |
| Legal Counsel (Platform) | 1 | **None** |
| Legal Counsel (공정거래) | 1 | **None** |
| Legal Team Leader | 1 | **None** |
| Loan Operations Manager | 1 | **None** |
| ML Backend Engineer | 1 | 데이터·AI |
| ML Engineer (CSS) | 1 | 데이터·AI |
| ML Engineer (Commerce Ads) | 1 | 데이터·AI |
| ML Engineer (Commerce Data Graph) | 1 | 데이터·AI |
| ML Engineer (Data Pipeline) | 1 | 데이터·AI |
| ML Engineer (Infra) | 1 | 데이터·AI |
| ML Engineer (LLM) | 1 | 데이터·AI |
| ML Engineer (ML/LLM Ops) | 1 | 데이터·AI |
| ML Engineer (Platform) | 1 | 데이터·AI |
| ML Engineer (Product) | 1 | 데이터·AI |
| ML Engineer (검색 Conversion/Ranking) | 1 | 데이터·AI |
| ML Engineer (검색 Relevance) | 1 | 데이터·AI |
| ML Engineer (커뮤니티 추천) | 1 | 데이터·AI |
| ML Engineer [Commerce] | 1 | 데이터·AI |
| ML Engineer [전문연구요원] | 1 | 데이터·AI |
| Marketing Creative Assistant | 1 | **None** |
| Marketing Manager (B2B) | 1 | **None** |
| Marketing Team Assistant (Internship) | 1 | **None** |
| Merchant Onboarding Assistant (Internship) | 1 | **None** |
| Merchant Onboarding Specialist  | 1 | **None** |
| Network Engineer (7년 이상) | 1 | **None** |
| Network Engineer (Edge) | 1 | **None** |
| Network Security Engineer (5년 미만)  | 1 | **None** |
| Network Security Engineer (5년 이상) | 1 | **None** |
| Network Software Engineer | 1 | 서버·백엔드 |
| Office Manager(부산) | 1 | **None** |
| Operations Enablement Assistant (Internship) | 1 | **None** |
| Operations Enablement Specialist | 1 | **None** |
| Operations Manager (제품운영/인력운영) (인재풀) | 1 | **None** |
| Operations Manager (콘텐츠/제품운영) | 1 | **None** |
| Operations Supporter (얼굴촬영/수집) | 1 | **None** |
| Operations Supporter (인재풀) | 1 | **None** |
| Payment Software Engineer | 1 | **None** |
| People Systems Manager(Workday) | 1 | **None** |
| Platform Product Owner (Blockchain) | 1 | **None** |
| Platform Product Owner (Facepay) | 1 | **None** |
| Platform Product Owner (Global) | 1 | **None** |
| Privacy Manager (3년이하) | 1 | **None** |
| Privacy Manager (AI) | 1 | 데이터·AI |
| Privacy Manager(Global) | 1 | **None** |
| Privacy Operations Assistant | 1 | **None** |
| Privacy Operations Specialist | 1 | **None** |
| Product Design Assistant | 1 | **None** |
| Product Designer (Global)  | 1 | **None** |
| Product Designer (신입) | 1 | **None** |
| Product Excellence Manager (Strategy & Execution) | 1 | **None** |
| Product Manager | 1 | **None** |
| Product Manager (LLM) | 1 | **None** |
| Product Operations Manager (Ads) | 1 | **None** |
| Product Operations Manager (Growth) | 1 | **None** |
| Product Owner (Global) | 1 | **None** |
| Product Owner (User Journey) | 1 | 데이터·AI |
| Product Owner (Vertical) | 1 | **None** |
| Product Owner (기업솔루션) | 1 | **None** |
| Product Owner (원장 Platform) | 1 | **None** |
| Product Owner [Commerce] | 1 | **None** |
| Project Staff (Product) | 1 | **None** |
| Project Staff (Tech) | 1 | **None** |
| Purchasing Manager | 1 | **None** |
| QA Manager (10년 이상) | 1 | **None** |
| QA Manager (5년 이상) | 1 | **None** |
| QA Manager (Product) | 1 | **None** |
| QA Manager(Platform) | 1 | **None** |
| QA Team Leader | 1 | **None** |
| Recruiting Business Partner (BPO 사업 담당) | 1 | **None** |
| Recruiting Partner Team Leader | 1 | **None** |
| Retail Operations Manager (고객경험) | 1 | **None** |
| Retail Operations Manager (금융사기방지) | 1 | **None** |
| Retail Operations Manager (연금) | 1 | **None** |
| Retail Operations Manager (지점 업무 및 백오피스 운영) | 1 | **None** |
| SOX Manager  | 1 | **None** |
| STR Monitoring Specialist | 1 | **None** |
| Sales Assistant (Internship) | 1 | **None** |
| Sales Development Representative | 1 | **None** |
| Sales Excellence Manager | 1 | **None** |
| Sales Manager | 1 | **None** |
| Sales Manager (Global) | 1 | **None** |
| Sales Operations Specialist | 1 | **None** |
| Sales Operations Specialist (Commerce) | 1 | **None** |
| Sales Specialist (FacePay Merchant Growth) | 1 | **None** |
| Sales Training Manager | 1 | **None** |
| Search Quality Operations Manager | 1 | **None** |
| Search Quality Operations Team Leader | 1 | **None** |
| Securities Settlement Manager (해외주식 - 3년 이상) | 1 | **None** |
| Securities Settlement Manager (해외주식 - 주니어) | 1 | **None** |
| Security Analyst | 1 | **None** |
| Security Audit Manager (개인정보 및 데이터관리 담당) | 1 | 데이터·AI |
| Security Audit Manager (정보보호 자체감사자) | 1 | **None** |
| Security Audit Manager (정보보호관리체계 및 기술 담당) | 1 | **None** |
| Security Audit Manager Team Leader (정보보호 자체감사자) | 1 | **None** |
| Security Engineer (네트워크 보안) | 1 | **None** |
| Security Engineer (시스템 보안) | 1 | **None** |
| Security Engineer (엔드포인트 보안) | 1 | **None** |
| Security Engineer (이벤트 분석 / 사고 대응) | 1 | **None** |
| Security Engineer (클라우드 보안) | 1 | **None** |
| Security Engineer [산업기능요원/전문연구요원] | 1 | **None** |
| Security Engineer(보안 분석 플랫폼 운영) | 1 | **None** |
| Security Operations Specialist | 1 | **None** |
| Security Researcher (APT/인프라 모의해킹) | 1 | **None** |
| Security Researcher (모바일보안) | 1 | 모바일 |
| Security Researcher (모의해킹/취약점 분석) | 1 | **None** |
| Security Researcher [산업기능요원/전문연구요원] | 1 | **None** |
| Server Developer (3년 이상) | 1 | 서버·백엔드 |
| Server Developer (3년 이하) | 1 | 서버·백엔드 |
| Server Developer (AI Platform) | 1 | 데이터·AI |
| Server Developer (Finance) | 1 | 서버·백엔드 |
| Server Developer (Market Platform) | 1 | 서버·백엔드 |
| Server Developer (Platform/Product) | 1 | 서버·백엔드 |
| Server Developer (SRE)  | 1 | 서버·백엔드 |
| Server Developer (TCP·전문통신)    | 1 | 서버·백엔드 |
| Server Developer (계정계) | 1 | 서버·백엔드 |
| Server Developer (생산성) | 1 | 서버·백엔드 |
| Server Developer (여신) | 1 | 서버·백엔드 |
| Server Developer [산업기능요원/전문연구요원] (Product) | 1 | 서버·백엔드 |
| Server Development Specialist | 1 | 서버·백엔드 |
| Site Reliability Engineer (SRE Team) | 1 | 서버·백엔드 |
| Solution Account Manager | 1 | **None** |
| Strategic Account MD (패션) | 1 | **None** |
| Strategic Finance Manager (FP&A / 10년 이상) | 1 | **None** |
| Strategic Finance Manager (FP&A) | 1 | **None** |
| Strategy Manager | 1 | **None** |
| System Security Team Leader | 1 | **None** |
| Systems Engineer | 1 | 웹 프론트엔드 |
| Systems Engineer (GPU) | 1 | **None** |
| Systems Engineer (가상화) | 1 | **None** |
| Talent Sourcer | 1 | **None** |
| Tax Manager | 1 | **None** |
| Tech Lead (Server) | 1 | 서버·백엔드 |
| Technical Account Manager | 1 | **None** |
| Technical Account Manager (Global) | 1 | **None** |
| Technical Product Owner | 1 | **None** |
| Technical Product Owner (AI) | 1 | 데이터·AI |
| Technical Product Owner (Commerce) | 1 | **None** |
| Technical Product Owner (공통) | 1 | **None** |
| Technical Product Owner [Search] | 1 | **None** |
| Technical Writer (Ads) | 1 | **None** |
| Validation Manager (리스크 적합성 검증) | 1 | **None** |
| Validation Manager (여신감리) | 1 | **None** |
| Visual Designer (Design System) | 1 | **None** |
| [증권] Server Developer (Japan) | 1 | 서버·백엔드 |
| [코어] Data Analytics Engineer (Finops) | 1 | 데이터·AI |
| [코어] Data Analytics Engineer (Governance) | 1 | 데이터·AI |
| 계좌 도메인 운영 Manager  | 1 | **None** |
| 금융거래정보 Assistant | 1 | **None** |
| 금융사기대응 Specialist | 1 | **None** |
| 법인영업 담당자 | 1 | **None** |
| 보험업 관련 포지션 인재풀 등록 | 1 | **None** |
| 보험총무(토스인슈어런스 직영)_인천 | 1 | **None** |
| 보훈특별채용 인재풀 등록 | 1 | **None** |
| 부산센터 계약직 (상시 인재풀 운영) | 1 | **None** |
| 상담팀 리드 (외국인 상담 전담팀) | 1 | **None** |
| 상담팀 리드 (토스플랫폼 전담팀) | 1 | **None** |
| 수신 상품 Manager | 1 | **None** |
| 안산 글로벌 라운지 세일즈 담당자 (Field Sales Specialist) | 1 | **None** |
| 여신 상품 Manager (기업여신 심사) | 1 | **None** |
| 여신 제도 Manager | 1 | **None** |
| 외환 상품 Manager (해외송금) | 1 | **None** |
| 이체/출납 도메인 운영 Manager  | 1 | **None** |
| 자문 상품 운영 Manager (Wrap 운영) | 1 | **None** |
| 토스쇼핑 음성 데이터 검수 스태프 (팀원) | 1 | 데이터·AI |
| 토스인슈어런스 Product Designer 집중 채용 (~9/13) | 1 | **None** |
| 토스증권 Product Designer 집중 채용 (2년 이상) (~9/15) | 1 | **None** |
| 토스커뮤니티 Frontend Developer 대규모 채용 (~9/14) | 1 | 웹 프론트엔드 |
| 토스페이 청약심사 (팀원) | 1 | **None** |
| 토스페이먼츠 데이터 엔지니어 공개채용 (7년 이하) (~9/10) | 1 | 데이터·AI |
| 토스페이먼츠 신사업 초기멤버 인재풀 등록 | 1 | **None** |

## 8. 회사별 occupation 고유값 (빈도순)

### 올리브영 (`oliveyoung`, greeting)

| occupation | 건수 |
|---|---|
| IT | 66 |
| (없음/None) | 42 |
| 마케팅 | 37 |
| 경영지원 | 20 |
| 디자인 | 15 |
| 물류 | 12 |
| 경영지원(전략) | 5 |
| 경영지원(사업관리/재무) | 4 |
| 기타/특수 | 3 |
| 영업 | 3 |
| 경영지원(인사) | 2 |
| 제조 | 2 |
| 건설/개발 | 1 |

### 무신사(+29CM) (`musinsa`, greeting)

| occupation | 건수 |
|---|---|
| (없음/None) | 120 |
| Marketing | 1 |
| Product | 1 |
| Program Manager | 1 |

### 컬리 (`kurly`, greeting)

| occupation | 건수 |
|---|---|
| 마케팅 | 11 |
| 개발 | 9 |
| 디자인/컨텐츠 | 9 |
| MD | 7 |
| 영업 | 7 |
| 보안 | 4 |
| 인사 | 4 |
| 프로덕트 매니지먼트 | 4 |
| EHS | 3 |
| FC기획 | 3 |
| 법무 | 2 |
| 인프라 | 2 |
| Finance | 1 |
| 고객서비스 | 1 |
| 데이터 | 1 |
| 프로덕트 디자인 | 1 |

### 캐치테이블 (`catchtable`, greeting)

| occupation | 건수 |
|---|---|
| Business & Sales | 11 |
| 인재풀 | 9 |
| Design | 3 |
| Marketing | 3 |
| People | 3 |
| Customer | 2 |
| Data | 2 |
| Finance | 2 |
| (없음/None) | 2 |
| AI | 1 |
| Engineering | 1 |
| PM | 1 |
| Product (기획) | 1 |

### 카카오페이 (`kakaopay`, greeting)

| occupation | 건수 |
|---|---|
| (없음/None) | 10 |
| 기술 | 10 |
| 프로덕트 | 5 |
| 스탭 | 3 |
| 비즈니스 | 2 |
| 마케팅 | 1 |

### 여기어때 (`yeogieotdae`, greeting)

| occupation | 건수 |
|---|---|
| 영업 | 8 |
| 기술 | 4 |
| 마케팅 | 3 |
| 보안 | 3 |
| 프로덕트 | 3 |
| 디자인 | 2 |
| (없음/None) | 1 |
| 경영지원 | 1 |
| 영업(운영/지원) | 1 |

### 카카오모빌리티 (`kakaomobility`, greeting)

| occupation | 건수 |
|---|---|
| 기술 | 16 |
| 서비스사업 | 3 |
| 스탭 | 3 |

### 왓챠 (`watcha`, greeting)

| occupation | 건수 |
|---|---|
| (없음/None) | 1 |

### SSG.COM (`ssg`, greeting)

(공고 없음)

### 데브시스터즈 (`devsisters`, greeting)

(공고 없음)

### 마이리얼트립 (`myrealtrip`, greeting)

| occupation | 건수 |
|---|---|
| 사업개발/기획 | 9 |
| Sales | 4 |
| 마케팅 | 2 |
| 정보보안 | 2 |
| (없음/None) | 1 |
| 고객지원 | 1 |
| 재무/회계 | 1 |
| 항공 | 1 |

### 리멤버 (`remember`, ninehire)

| occupation | 건수 |
|---|---|
| Business | 9 |
| Data | 2 |
| (없음/None) | 2 |
| Support | 2 |
| AI | 1 |
| MKT & Brand | 1 |
| Tech | 1 |
| 전체 직군 | 1 |

### 요기요 (`yogiyo`, ninehire)

| occupation | 건수 |
|---|---|
| Business | 5 |
| Tech | 5 |
| Corporate Staff | 1 |
| Product | 1 |

### 네이버 (`naver`, custom)

| occupation | 건수 |
|---|---|
| Service & Business | 21 |
| Corporate | 9 |
| Design | 7 |
| Tech | 5 |

### 카카오뱅크 (`kakaobank`, custom)

| occupation | 건수 |
|---|---|
| Service & Biz | 19 |
| Customer Service | 3 |
| AI | 2 |
| Engineering | 2 |
| Management | 2 |
| Compliance | 1 |
| Core Banking | 1 |
| Data | 1 |
| Strategy | 1 |
| 상시채용 | 1 |

### 라인 (`line`, custom)

| occupation | 건수 |
|---|---|
| Engineering | 29 |
| Corporate | 14 |
| Planning | 11 |
| Business & Sales | 9 |
| Marketing & CS | 4 |
| Design | 3 |
| (없음/None) | 2 |

### 당근 (`daangn`, custom)

| occupation | 건수 |
|---|---|
| Tech | 30 |
| Design | 6 |
| Business | 5 |
| Product Management | 5 |
| Corporate | 2 |

### 티빙 (`tving`, custom)

| occupation | 건수 |
|---|---|
| 일반직군 | 2 |
| 개발직군 | 1 |

### 채널톡 (`channeltalk`, custom)

| occupation | 건수 |
|---|---|
| Sales / Business | 13 |
| Engineering | 10 |
| Strategy / Business Ops | 9 |
| Product / Design | 5 |
| Corporate | 3 |
| Talent Pool | 2 |
| US - Business | 1 |

### 뱅크샐러드 (`banksalad`, custom)

| occupation | 건수 |
|---|---|
| 제품기획 | 4 |
| 경영관리 | 1 |
| 마케팅 | 1 |
| 보험 GA | 1 |
| 세일즈 | 1 |
| 테크 | 1 |

### 하이퍼커넥트 (`hyperconnect`, custom)

| occupation | 건수 |
|---|---|
| AI/ML | 4 |
| Tinder Seoul | 3 |
| Engineering | 2 |
| PM | 2 |
| Management | 1 |

### 쏘카 (`socar`, custom)

| occupation | 건수 |
|---|---|
| 사업/운영 | 10 |
| 개발/데이터 | 9 |
| 경영/전략 | 4 |
| 서비스기획 | 3 |
| 공통 | 2 |
| 홍보/마케팅 | 1 |

### 카카오 (`kakao`, custom)

| occupation | 건수 |
|---|---|
| 테크 | 32 |
| 서비스비즈 | 22 |
| 스태프 | 8 |
| 디자인 | 2 |

### 토스 (`toss`, custom)

| occupation | 건수 |
|---|---|
| Backend | 38 |
| Product Ownership | 30 |
| Data Engineering | 28 |
| ML | 23 |
| Information Security | 22 |
| Sales Support | 20 |
| Sales | 19 |
| Customer | 17 |
| Security Engineering | 15 |
| Finance | 14 |
| Infra | 14 |
| Marketing | 13 |
| Data Analysis | 12 |
| HR | 12 |
| Frontend | 11 |
| IT Planning | 11 |
| Bank | 10 |
| Compliance | 10 |
| Product Design | 10 |
| GA | 9 |
| QA | 9 |
| Recruiting | 9 |
| Securities | 9 |
| Data Managing | 8 |
| Legal | 8 |
| AML | 7 |
| IT General Admin | 7 |
| Risk | 7 |
| UX | 7 |
| (없음/None) | 6 |
| 병역특례 | 6 |
| Product Operations | 5 |
| Strategy | 5 |
| App | 4 |
| Device | 4 |
| Accounting | 3 |
| Brand Design | 3 |
| Community | 3 |
| Insurance | 3 |
| PR | 3 |
| All | 2 |
| Compensation & Benefit | 2 |
| Corp.dev | 2 |
| Customer Support | 2 |
| IR | 2 |
| Platform Design | 2 |
| Technical Excellence | 2 |
| Contents | 1 |
| Culture | 1 |
| Customer Service | 1 |
| Leadership | 1 |
| People System | 1 |

## 9. 회사별 job 고유값 (빈도순)

### 올리브영 (`oliveyoung`, greeting)

| job | 건수 |
|---|---|
| (없음/None) | 46 |
| Product Management | 25 |
| Back-end Engineering | 9 |
| 글로벌마케팅 | 9 |
| 마케팅 | 9 |
| Data Engineering | 7 |
| 품질관리 | 6 |
| Data Scientist | 5 |
| Product Design | 5 |
| SCM | 5 |
| 브랜드마케팅 | 5 |
| BM | 4 |
| BPO | 4 |
| Front-end Engineering | 4 |
| 사업전략 | 4 |
| Research | 3 |
| SW QA | 3 |
| 구매 | 3 |
| 브랜드디자인 | 3 |
| 전략기획 | 3 |
| AI Engineering | 2 |
| Data Analyst | 2 |
| Data Architect | 2 |
| HRM | 2 |
| IT전략 | 2 |
| MD | 2 |
| MD스토어기획 | 2 |
| VMD | 2 |
| 비주얼디자인 | 2 |
| 사업관리 | 2 |
| 온사이트마케팅 | 2 |
| 인테리어 | 2 |
| 정보보안/개인정보보호 | 2 |
| 퍼포먼스마케팅 | 2 |
| Android App Engineering | 1 |
| DevRel | 1 |
| Global Software Engineering | 1 |
| IP | 1 |
| IT기획 | 1 |
| MD운영지원 | 1 |
| Marketing Design | 1 |
| TPM | 1 |
| 글로벌MD | 1 |
| 글로벌사업 | 1 |
| 글로벌사업관리 | 1 |
| 글로벌사업전략 | 1 |
| 글로벌온사이트마케팅 | 1 |
| 글로벌플랫폼운영 | 1 |
| 마케팅커뮤니케이션 | 1 |
| 브랜딩마케팅 | 1 |
| 사무지원 | 1 |
| 상권개발 | 1 |
| 상품운영 | 1 |
| 소셜콘텐츠마케팅 | 1 |
| 제휴마케팅 | 1 |
| 프로모션마케팅 | 1 |

### 무신사(+29CM) (`musinsa`, greeting)

| job | 건수 |
|---|---|
| MD | 13 |
| Product Management | 11 |
| Brand Marketing | 10 |
| Backend Engineering | 9 |
| Production Management | 8 |
| Content Planning | 6 |
| Growth Marketing | 5 |
| Ad Business | 4 |
| (없음/None) | 4 |
| On-Site Marketing | 4 |
| DevOps | 3 |
| FC운영 | 3 |
| Planning MD | 3 |
| Program Manager | 3 |
| BM | 2 |
| CX | 2 |
| Engineering Manager | 2 |
| Fashion Design | 2 |
| ML Engineer | 2 |
| Off-Line Planning | 2 |
| Security Engineering | 2 |
| VMD | 2 |
| AI Native Engineer | 1 |
| Business Analysis | 1 |
| Content Design | 1 |
| DBA | 1 |
| Data Analysis | 1 |
| Financial Planning | 1 |
| General Affair | 1 |
| Global Marketing | 1 |
| HRM | 1 |
| Off-Line Operation | 1 |
| Operation | 1 |
| Operation Management | 1 |
| Package Design | 1 |
| Photographer | 1 |
| Product Design | 1 |
| Program Management | 1 |
| Sales | 1 |
| Sales Planning | 1 |
| Security Management | 1 |
| System Engineering | 1 |
| Video Production | 1 |

### 컬리 (`kurly`, greeting)

| job | 건수 |
|---|---|
| (없음/None) | 69 |

### 캐치테이블 (`catchtable`, greeting)

| job | 건수 |
|---|---|
| (없음/None) | 41 |

### 카카오페이 (`kakaopay`, greeting)

| job | 건수 |
|---|---|
| (없음/None) | 31 |

### 여기어때 (`yeogieotdae`, greeting)

| job | 건수 |
|---|---|
| (없음/None) | 26 |

### 카카오모빌리티 (`kakaomobility`, greeting)

| job | 건수 |
|---|---|
| 개발 | 15 |
| Assistant | 2 |
| 사업기획및운영 | 2 |
| QA | 1 |
| 법무 | 1 |
| 서비스기획및운영 | 1 |

### 왓챠 (`watcha`, greeting)

| job | 건수 |
|---|---|
| (없음/None) | 1 |

### SSG.COM (`ssg`, greeting)

(공고 없음)

### 데브시스터즈 (`devsisters`, greeting)

(공고 없음)

### 마이리얼트립 (`myrealtrip`, greeting)

| job | 건수 |
|---|---|
| (없음/None) | 21 |

### 리멤버 (`remember`, ninehire)

| job | 건수 |
|---|---|
| (없음/None) | 19 |

### 요기요 (`yogiyo`, ninehire)

| job | 건수 |
|---|---|
| Data Engineer | 2 |
| Logistics | 2 |
| security policy | 2 |
| Finance | 1 |
| Merchant Growth 전략 기획 | 1 |
| PO | 1 |
| security engineering | 1 |
| 구독멤버십 | 1 |
| 페이먼트 제휴 | 1 |

### 네이버 (`naver`, custom)

| job | 건수 |
|---|---|
| Business Development | 13 |
| Visual Comm. & Brand Design | 5 |
| Content Development | 3 |
| Product Development | 3 |
| Human Resources | 2 |
| Product Design | 2 |
| Risk Management | 2 |
| 공통 | 2 |
| AI/ML | 1 |
| Backend | 1 |
| Corporate Strategy | 1 |
| Data Engineering | 1 |
| Hardware | 1 |
| Strategic Communication | 1 |
| 법무 | 1 |
| 어카운트/세일즈 | 1 |
| 자산관리 | 1 |
| 회계 | 1 |

### 카카오뱅크 (`kakaobank`, custom)

| job | 건수 |
|---|---|
| (없음/None) | 33 |

### 라인 (`line`, custom)

| job | 건수 |
|---|---|
| Server-side | 8 |
| Product Management | 7 |
| Sales | 6 |
| Web Development | 6 |
| (없음/None) | 5 |
| Marketing | 4 |
| QA/SET | 4 |
| Business Development | 3 |
| Data Engineering | 3 |
| Security Engineering | 3 |
| Business Management | 2 |
| Communications & Corporate Affairs | 2 |
| Contents Production | 2 |
| Product Design | 2 |
| Support | 2 |
| System Engineering | 2 |
| Business Strategy | 1 |
| Customer Support | 1 |
| Governance | 1 |
| Human Resources | 1 |
| Internal Audit | 1 |
| Legal | 1 |
| Project Management | 1 |
| Risk Management | 1 |
| Security | 1 |
| Tech Management | 1 |
| VX Design | 1 |

### 당근 (`daangn`, custom)

| job | 건수 |
|---|---|
| Software Engineer, Backend | 12 |
| Design | 6 |
| Software Engineer, Frontend | 5 |
| Business | 3 |
| Security | 3 |
| Service Operations | 3 |
| Software Engineer, Machine Learning | 3 |
| HR | 2 |
| Product Manager | 2 |
| Sales | 2 |
| Software Engineer, Android | 2 |
| Database Engineer | 1 |
| Design Engineer | 1 |
| Network | 1 |
| Software Engineer | 1 |
| Software Engineer, iOS | 1 |

### 티빙 (`tving`, custom)

| job | 건수 |
|---|---|
| (없음/None) | 3 |

### 채널톡 (`channeltalk`, custom)

| job | 건수 |
|---|---|
| (없음/None) | 43 |

### 뱅크샐러드 (`banksalad`, custom)

| job | 건수 |
|---|---|
| 제품기획 | 4 |
| 경영관리 | 1 |
| 마케팅 | 1 |
| 보험 GA | 1 |
| 세일즈 | 1 |
| 테크 | 1 |

### 하이퍼커넥트 (`hyperconnect`, custom)

| job | 건수 |
|---|---|
| (없음/None) | 12 |

### 쏘카 (`socar`, custom)

| job | 건수 |
|---|---|
| (없음/None) | 29 |

### 카카오 (`kakao`, custom)

| job | 건수 |
|---|---|
| (없음/None) | 57 |
| Algorithm/ML | 4 |
| QA | 1 |
| Server | 1 |
| 기타 | 1 |

### 토스 (`toss`, custom)

| job | 건수 |
|---|---|
| (없음/None) | 232 |
| 공통 | 36 |
| Platform | 13 |
| Product | 11 |
| Global | 8 |
| Growth | 6 |
| 5년 미만 | 4 |
| 5년 이상 | 4 |
| Ads | 4 |
| Manager | 4 |
| 7년 이상 | 3 |
| Security Audit Manager | 3 |
| 상시풀 운영 | 3 |
| 쇼핑 MD | 3 |
| AI | 2 |
| Content | 2 |
| Finance | 2 |
| Governance | 2 |
| Operations | 2 |
| Tax | 2 |
| Technical Product Owner | 2 |
| 내부회계 | 2 |
| 시스템 보안 | 2 |
| 일반 | 2 |
| 10년 이상 | 1 |
| 3년 이상 | 1 |
| 3년 이하 | 1 |
| 3년이하 | 1 |
| 7년 미만 | 1 |
| AI Platform | 1 |
| AI User Journey | 1 |
| ALM | 1 |
| Account Manger | 1 |
| Accounting | 1 |
| B2B | 1 |
| Blockchain | 1 |
| Brain | 1 |
| Brand | 1 |
| CEO | 1 |
| CSS | 1 |
| Cloud | 1 |
| Commerce | 1 |
| Commerce Ads | 1 |
| Commerce Ads Platform | 1 |
| Commerce Data Graph | 1 |
| Commerce Domain | 1 |
| Commerce Signal | 1 |
| Commerce 추천 | 1 |
| Corporate | 1 |
| DW | 1 |
| DW/Global | 1 |
| Data Pipeline | 1 |
| Data Value | 1 |
| Data Warehouse (Mart) | 1 |
| Data Warehouse (Platform) | 1 |
| Datacenter | 1 |
| Design System | 1 |
| Edge | 1 |
| Event | 1 |
| FDS | 1 |
| FP&A | 1 |
| FacePay | 1 |
| FacePay (Merchant Growth) | 1 |
| Facepay | 1 |
| Finance Execellence Manager | 1 |
| Finops | 1 |
| Fintech | 1 |
| GPU | 1 |
| Graphic | 1 |
| Inference Pipeline | 1 |
| Infra | 1 |
| LLM | 1 |
| ML/LLM Ops | 1 |
| Market Platform | 1 |
| Model | 1 |
| MySQL | 1 |
| Oracle | 1 |
| PMO | 1 |
| Plaform/Product | 1 |
| Product (Japan) | 1 |
| Product Design Assistant | 1 |
| Product Owner | 1 |
| Productivity | 1 |
| Realtime | 1 |
| Recommendation | 1 |
| SAP | 1 |
| SOHO 여신 | 1 |
| SRE | 1 |
| SRE Team | 1 |
| STR 기획 및 운영 | 1 |
| Serving | 1 |
| TCP·전문통신 | 1 |
| Team Leader | 1 |
| Vertical | 1 |
| WM | 1 |
| 거버넌스 | 1 |
| 검색 Conversion/Ranking | 1 |
| 검색 Relevance | 1 |
| 계정계 | 1 |
| 공시/주총 | 1 |
| 공정거래 | 1 |
| 광고 | 1 |
| 금융데이터 /  AI | 1 |
| 금융데이터/자문 | 1 |
| 금융데이터/재무 | 1 |
| 기업솔루션 | 1 |
| 기업여신 심사 | 1 |
| 기업해외송금 | 1 |
| 내부통제 | 1 |
| 대면센터 | 1 |
| 대위변제 | 1 |
| 데이터 변경통제 | 1 |
| 모바일보안 | 1 |
| 민원대응 | 1 |
| 법인영업 | 1 |
| 보안 점검 | 1 |
| 보안정책 | 1 |
| 비예금상품 | 1 |
| 사무보조 | 1 |
| 상각 | 1 |
| 상시모니터링 | 1 |
| 솔루션 영업 | 1 |
| 앱인토스 | 1 |
| 엔드포인트 보안 | 1 |
| 연결 | 1 |
| 예산관리 | 1 |
| 오픈소스 보안 | 1 |
| 원장 Platform | 1 |
| 음성 클리핑 | 1 |
| 이벤트 분석/사고 대응 | 1 |
| 자동화 | 1 |
| 자산관리 | 1 |
| 전담 운영 | 1 |
| 전략 MD | 1 |
| 전사전략 | 1 |
| 정보보호감사 | 1 |
| 정책/기획 | 1 |
| 채널영업 | 1 |
| 청약심사_페이 | 1 |
| 취약점 진단 & 모의해킹 | 1 |
| 커뮤니티 추천 | 1 |
| 해외주식 - 3년 이상 | 1 |
| 해외주식 - 주니어 | 1 |

## 10. 전체 title 토큰 빈도 (3회 이상)

| 토큰 | 공고 수 |
|---|---|
| Manager | 277 |
| Engineer | 216 |
| 담당자 | 181 |
| Product | 141 |
| Data | 78 |
| 운영 | 69 |
| 계약직 | 64 |
| Platform | 55 |
| Operations | 50 |
| 기획 | 50 |
| AI | 49 |
| Business | 47 |
| Security | 45 |
| Designer | 44 |
| Specialist | 42 |
| Developer | 41 |
| 공동체 | 41 |
| 매니저 | 41 |
| Sales | 40 |
| 경력 | 39 |
| Assistant | 38 |
| Software | 38 |
| Global | 36 |
| 마케터 | 36 |
| 광고 | 35 |
| MD | 34 |
| 개발자 | 34 |
| 년 | 33 |
| 및 | 32 |
| 글로벌 | 31 |
| 서비스 | 31 |
| Owner | 30 |
| Server | 29 |
| LINE | 28 |
| Growth | 27 |
| 네이버웹툰 | 27 |
| 인턴 | 26 |
| 플랫폼 | 26 |
| 엔지니어 | 25 |
| 이상 | 25 |
| Backend | 24 |
| IT | 24 |
| Team | 24 |
| Analyst | 23 |
| Lead | 23 |
| Marketer | 23 |
| Marketing | 23 |
| Senior | 23 |
| 사업 | 23 |
| 마케팅 | 22 |
| 무신사 | 21 |
| Account | 20 |
| B2B | 20 |
| PB | 20 |
| QA | 20 |
| 개발 | 20 |
| 인재풀 | 20 |
| ML | 19 |
| 디자이너 | 19 |
| 콘텐츠 | 19 |
| D | 18 |
| Taiwan | 18 |
| 데이터 | 18 |
| 스탠다드 | 18 |
| Leader | 17 |
| 어시스턴트 | 17 |
| 영업 | 17 |
| 지원 | 17 |
| 카카오페이 | 17 |
| 프로덕트 | 17 |
| Analytics | 16 |
| Partner | 16 |
| 관리 | 16 |
| 상품 | 16 |
| 시니어 | 16 |
| 전략 | 16 |
| 카카오모빌리티 | 16 |
| Brand | 15 |
| Frontend | 15 |
| Pay | 15 |
| 결제 | 15 |
| 등록 | 15 |
| 자율주행 | 15 |
| A | 14 |
| Commerce | 14 |
| Customer | 14 |
| EPI | 14 |
| Privacy | 14 |
| 담당 | 14 |
| 오프라인 | 14 |
| 인프라 | 14 |
| Affairs | 13 |
| Development | 13 |
| Network | 13 |
| Technical | 13 |
| 백엔드 | 13 |
| 보안 | 13 |
| 서버 | 13 |
| 커머스 | 13 |
| 프로모션 | 13 |
| PM | 12 |
| R | 12 |
| Researcher | 12 |
| Strategy | 12 |
| 뷰티 | 12 |
| 체험형 | 12 |
| CM | 11 |
| DevOps | 11 |
| Finance | 11 |
| NAVER | 11 |
| Planning | 11 |
| Retail | 11 |
| Scientist | 11 |
| 시스템 | 11 |
| Cloud | 10 |
| Engineering | 10 |
| HR | 10 |
| Learning | 10 |
| Machine | 10 |
| Recruiting | 10 |
| Staff | 10 |
| 실 | 10 |
| AD | 9 |
| Content | 9 |
| Corporate | 9 |
| General | 9 |
| Management | 9 |
| Research | 9 |
| System | 9 |
| 개월 | 9 |
| 기획자 | 9 |
| 소싱 | 9 |
| 업무 | 9 |
| 여신 | 9 |
| 정책 | 9 |
| 채용 | 9 |
| Ads | 8 |
| Android | 8 |
| DBA | 8 |
| Design | 8 |
| Legal | 8 |
| Merchant | 8 |
| Program | 8 |
| Search | 8 |
| Tech | 8 |
| 그로스 | 8 |
| 글로벌몰 | 8 |
| 분석 | 8 |
| 제휴 | 8 |
| 팀장 | 8 |
| Audit | 7 |
| BM | 7 |
| BPO | 7 |
| Beauty | 7 |
| FP | 7 |
| HRBP | 7 |
| Information | 7 |
| SCM | 7 |
| Strategic | 7 |
| T | 7 |
| UX | 7 |
| 검색 | 7 |
| 리테일미디어 | 7 |
| 무신사로지스틱스 | 7 |
| 물류 | 7 |
| 브랜드 | 7 |
| 사업개발 | 7 |
| 상품기획 | 7 |
| 생산관리 | 7 |
| 신사업 | 7 |
| 신입 | 7 |
| 온라인 | 7 |
| 운영지원 | 7 |
| 정규직 | 7 |
| 정보보호 | 7 |
| 주니어 | 7 |
| 클라우드 | 7 |
| 파트너 | 7 |
| 퍼포먼스 | 7 |
| 품질관리 | 7 |
| 프론트엔드 | 7 |
| AML | 6 |
| BX | 6 |
| Back-end | 6 |
| Client | 6 |
| Compliance | 6 |
| Core | 6 |
| Counsel | 6 |
| Enterprise | 6 |
| Executive | 6 |
| IR | 6 |
| Internship | 6 |
| Media | 6 |
| Project | 6 |
| Protection | 6 |
| Reliability | 6 |
| Service | 6 |
| Site | 6 |
| Systems | 6 |
| US | 6 |
| User | 6 |
| VMD | 6 |
| Visual | 6 |
| 개발채용 | 6 |
| 대응 | 6 |
| 무신사페이먼츠 | 6 |
| 물류센터 | 6 |
| 세일즈 | 6 |
| 스토어 | 6 |
| 이벤트 | 6 |
| 전문연구요원 | 6 |
| 정산 | 6 |
| 화장품 | 6 |
| Accounting | 5 |
| Associate | 5 |
| CRM | 5 |
| CX | 5 |
| Contents | 5 |
| Governance | 5 |
| IP | 5 |
| Infra | 5 |
| LLM | 5 |
| Operation | 5 |
| Payment | 5 |
| Risk | 5 |
| pool | 5 |
| 개인정보보호 | 5 |
| 관리자 | 5 |
| 기회 | 5 |
| 로컬 | 5 |
| 리드 | 5 |
| 변호사 | 5 |
| 사내 | 5 |
| 사업관리 | 5 |
| 사업기획 | 5 |
| 산업기능요원 | 5 |
| 온사이트 | 5 |
| 인재 | 5 |
| 자산 | 5 |
| 잡스 | 5 |
| 전환 | 5 |
| 채널 | 5 |
| 초기멤버 | 5 |
| 추천 | 5 |
| 커뮤니티 | 5 |
| 컨텐츠 | 5 |
| Ad | 4 |
| Administrator | 4 |
| Auditor | 4 |
| Azar | 4 |
| DMP | 4 |
| Database | 4 |
| Device | 4 |
| FE | 4 |
| Financial | 4 |
| Front-end | 4 |
| Group | 4 |
| Internal | 4 |
| KR | 4 |
| Match | 4 |
| Node | 4 |
| PD | 4 |
| Quality | 4 |
| SLAM | 4 |
| SNS | 4 |
| Talent | 4 |
| UI | 4 |
| Warehouse | 4 |
| Webtoon | 4 |
| js | 4 |
| research | 4 |
| scientist | 4 |
| 구매 | 4 |
| 구축 | 4 |
| 당근페이 | 4 |
| 디자인 | 4 |
| 디지털 | 4 |
| 리더십 | 4 |
| 매장 | 4 |
| 모니터링 | 4 |
| 부동산 | 4 |
| 브랜딩 | 4 |
| 사업전략 | 4 |
| 스테이블코인 | 4 |
| 실행 | 4 |
| 영상 | 4 |
| 정보 | 4 |
| 캠페인 | 4 |
| 코어 | 4 |
| 팀 | 4 |
| 패션 | 4 |
| Agency | 3 |
| B2C | 3 |
| CS | 3 |
| Call | 3 |
| Catalog | 3 |
| Category | 3 |
| Chinese | 3 |
| Collections | 3 |
| Consumer | 3 |
| Coordinator | 3 |
| Culture | 3 |
| Discovery | 3 |
| E-Commerce | 3 |
| EHS | 3 |
| Embedded | 3 |
| Enablement | 3 |
| FDS | 3 |
| FacePay | 3 |
| Fashion | 3 |
| Foundation | 3 |
| GTM | 3 |
| Guider | 3 |
| Hero | 3 |
| IDC | 3 |
| Intelligence | 3 |
| Interview | 3 |
| Japan | 3 |
| KR-TW | 3 |
| Korean | 3 |
| Logistics | 3 |
| Mid-Market | 3 |
| PO | 3 |
| Part | 3 |
| People | 3 |
| Performance | 3 |
| Promotion | 3 |
| Public | 3 |
| Representative | 3 |
| SAP | 3 |
| SRE | 3 |
| STR | 3 |
| Safety | 3 |
| Tinder | 3 |
| Trust | 3 |
| iOS | 3 |
| mall | 3 |
| 공간정보 | 3 |
| 국내 | 3 |
| 근무 | 3 |
| 금융데이터 | 3 |
| 기술 | 3 |
| 네트워크 | 3 |
| 년차 | 3 |
| 대출 | 3 |
| 도메인 | 3 |
| 라이선스 | 3 |
| 롱테일 | 3 |
| 리멤버 | 3 |
| 멤버십 | 3 |
| 모의해킹 | 3 |
| 미주 | 3 |
| 보호 | 3 |
| 사고 | 3 |
| 생활 | 3 |
| 소셜 | 3 |
| 식품 | 3 |
| 어필리에이트 | 3 |
| 에디터 | 3 |
| 에이펙스모빌리티 | 3 |
| 영입 | 3 |
| 외국인 | 3 |
| 이커머스 | 3 |
| 인증 | 3 |
| 일본 | 3 |
| 잡화 | 3 |
| 전략기획 | 3 |
| 제작 | 3 |
| 집중채용 | 3 |
| 체계 | 3 |
| 최초채용 | 3 |
| 카카오게임즈 | 3 |
| 카카오페이손해보험 | 3 |
| 카테고리 | 3 |
| 커머스플랫폼유닛 | 3 |
| 팀원 | 3 |
| 풀필먼트 | 3 |
| 프로세스 | 3 |
| 프로젝트 | 3 |
| 피드 | 3 |
| 핀테크 | 3 |
| 홈 | 3 |

