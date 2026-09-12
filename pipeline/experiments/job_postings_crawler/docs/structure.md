# 프로젝트 구조

```
common/                 공통 (HTTP, 분류, 저장, 경로)
sources/greeting/       그리팅 11곳
sources/ninehire/       나인하이어 2곳 (요기요, 리멤버)
sources/custom/         자체구축 (네이버·카카오·토스 등)
scripts/                감사·집계·분류 진단
docs/                   이 폴더
```

저장소 루트 기준 산출물:

```
data/work/job_postings/raw/          수집 원본 (가공 금지, Git 제외)
data/work/job_postings/processed/    분류 결과 (Git 제외)
data/research/job_postings/keyword_audit.md
data/research/job_postings/team_decisions_needed.md
data/research/job_postings/step6_summary.md
```

## 분류

`common/job_classifier.py`

- 1순위: ATS 구조화 필드 (`occupation` / `job`) — `STRUCTURED_KEYWORDS`
- 2순위: 제목 — `JOB_KEYWORDS` (기능명세 스펙, 팀 논의 없이 수정하지 않음)
- ASCII 키워드는 `\b` 단어 경계, 한글은 부분일치

## 회사 목록 (24곳)

**그리팅:** 올리브영, 여기어때, 카카오페이, 컬리, 무신사(+29CM), SSG.COM, 왓챠, 캐치테이블, 카카오모빌리티, 데브시스터즈, 마이리얼트립

**나인하이어:** 요기요, 리멤버

**자체구축:** 네이버, 카카오뱅크, 라인, 당근, 티빙, 채널톡, 뱅크샐러드, 하이퍼커넥트, 쏘카, 카카오, 토스
