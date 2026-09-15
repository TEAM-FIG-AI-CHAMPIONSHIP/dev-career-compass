# 재수집

`pipeline/experiments/job_postings_crawler`에서 실행합니다. 해당 회사의 `data/work/job_postings/raw/{id}.json`, `data/work/job_postings/processed/{id}.json`을 덮어씁니다.

다른 회사 raw는 건드리지 않습니다. 숫자를 보고서에 반영하려면 재수집 후 [aggregation.md](aggregation.md)를 다시 돌립니다.

## 그리팅 (16곳)

```bash
python3 sources/greeting/run.py
```

한 곳만:

```bash
python3 -c "
from sources.greeting.crawler import GREETING_COMPANIES, crawl_company
cid = 'kakaomobility'
name, url = GREETING_COMPANIES[cid]
print(crawl_company(cid, name, url))
"
```

`cid`: `oliveyoung` `yeogieotdae` `kakaopay` `kurly` `musinsa` `ssg` `watcha` `catchtable` `kakaomobility` `devsisters` `myrealtrip` `ahnlabcloudmate` `upstage` `kakaoenterprise` `hancom` `buzzvil`

목록 HTML의 `__NEXT_DATA__` `["openings"]`만 읽습니다. 지원 URL(`/o/*/apply`)은 요청하지 않습니다.

## 나인하이어 (4곳)

```bash
python3 sources/ninehire/run.py
```

`yogiyo`, `remember`는 sitemap → 상세 SSR. `megazone`, `rapportlabs`는 자체 도메인에서 `companyId`를 읽고 `api.ninehire.com`을 직접 호출합니다. `*.ninehire.site`와 `rapportlabs.kr`의 `/api`는 치지 않습니다.

## 리크루터 (2곳)

```bash
python3 sources/recruiter/run.py
```

`gsretail`, `com2us`. `api-recruiter.recruiter.co.kr`에 `prefix` 헤더로 POST. 본문 호스트의 `/app`·`/attachFile`은 치지 않습니다.

## 자체구축 (1곳씩)

```bash
python3 sources/custom/naver.py
python3 sources/custom/kakaobank.py
python3 sources/custom/line.py
python3 sources/custom/daangn.py
python3 sources/custom/tving.py
python3 sources/custom/channeltalk.py
python3 sources/custom/banksalad.py
python3 sources/custom/hyperconnect.py
python3 sources/custom/socar.py
python3 sources/custom/kakao.py          # Playwright + Chromium
python3 sources/custom/toss.py
python3 sources/custom/skcareers.py      # SK플래닛. corpCode만 바꿔 계열사 추가
python3 sources/custom/lgresearch.py     # LG AI연구원 공개 목록 API
python3 sources/custom/ktcloud.py        # 정적 HTML .jd__item
python3 sources/custom/nds.py            # NDS JSP 목록
python3 sources/custom/nhncloud.py       # /v1/job-postings, NHN Cloud만
python3 sources/custom/gabia.py          # 하이웍스 announces API
python3 sources/custom/goorm.py          # Playwright DOM
python3 sources/custom/samsung.py        # POST /hr/list.data
python3 sources/custom/samsungds.py      # 같은 목록 중 DS부문만
python3 sources/custom/imweb.py          # greetinghr jobs API
python3 sources/custom/inflab.py         # Playwright. inflearn /api 차단
python3 sources/custom/run_new.py        # 위 신규 10곳 + 라포랩스
```

배민(우아한형제들)·어피닛·넥스트리는 채용 목록이 없거나 `/w1/` 전체가 막혀 수집하지 않습니다.

카카오 raw에는 관계사(`[공동체]`)가 같이 들어갑니다. STEP 6은 본사(`group == 카카오`)만 카카오 몫으로 셉니다. 필터를 바꾸려면 집계 스크립트만 고칩니다.

토스 상세(`/career/job-detail?gh_jid=`)와 `toss.im/career/jobs?*`는 요청하지 않습니다. 목록 API만 씁니다.

## 새 사이트 구조 확인

```bash
python3 sources/custom/probe.py https://example.com/careers
```

robots · sitemap · 임베디드 JSON · API URL 흔적을 봅니다. `data/work/job_postings/probe/_probe_*.html`을 남길 수 있습니다. 집계에는 쓰이지 않으므로 확인 후 지워도 됩니다.
