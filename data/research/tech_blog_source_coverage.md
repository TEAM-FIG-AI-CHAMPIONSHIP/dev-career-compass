# 기업별 기술블로그 수집 소스 커버리지

조사 시각: 2026-09-13T04:56:35.322230+00:00

우아한형제들에서 검증한 generic collector(RSS 우선 → sitemap fallback)를
올리브영, 네이버 D2, 토스, 당근에 그대로 적용한 결과입니다.
Area / embedding / clustering / LLM은 포함하지 않습니다.

본문 원문은 `data/work/tech_blog_source_coverage/`에만 있고 Git에 없습니다.

## 회사별 요약

| 회사명 | 블로그 URL | 플랫폼/형태 | RSS/Atom | Sitemap | 최근 12개월 수집 | 최근 12개월 게시글 수 | 본문 추출 성공 / 전체 | 수집 전략 | generic 실패 원인 | custom 필요 | 비고 |
| --- | --- | --- | --- | --- | --- | ---: | --- | --- | --- | --- | --- |
| 올리브영 | https://oliveyoung.tech/ | 자체 기술블로그 (oliveyoung.tech) | O | O | O | 48 | 48 / 48 (100.0%) | RSS | - | X | sitemap HTML 게시일 확인 실패 533건. 12개월 확정분은 RSS |
| 네이버 D2 | https://d2.naver.com/ | 자체 플랫폼 (d2.naver.com) | O | X | X | 20 | 0 / 20 (0.0%) | Custom | RSS가 최근 20건만 내려줌 (oldest=2026-06-15T10:51:03+00:00); sitemap에서 게시글 URL을 못 찾음 | O | Trafilatura 본문 추출 실패 20/20 |
| 토스 | https://toss.tech/ | 자체 기술블로그 (toss.tech, Next.js) | O | X | X | 20 | 20 / 20 (100.0%) | Custom | RSS가 최근 20건만 내려줌 (oldest=2026-06-23T02:01:00+00:00); sitemap에서 게시글 URL을 못 찾음 | O | - |
| 당근 | https://medium.com/daangn | Medium publication (medium.com/daangn) | O | X | X | 10 | 1 / 10 (10.0%) | Custom | RSS가 최근 10건만 내려줌 (oldest=2026-05-14T09:05:19+00:00); sitemap URL 111132개 중 blog_url 접두어 밖 111132개 | O | sitemap 전체 111132개 중 111132개는 blog_url 밖이라 generic 가드로 제외; Trafilatura 본문 추출 실패 9/10 |

## 해석

- `최근 12개월 수집`은 글이 한 건이라도 있다는 뜻이 아니다.
  RSS/sitemap으로 **12개월 전체를 닫을 수 있는지**를 본다.
  RSS oldest가 12개월보다 짧고 sitemap이 못 메우면 X다.
- custom 필요는 전용 크롤러를 지금 만들라는 뜻이 아니다.
  generic으로 12개월을 못 닫거나 본문을 거의 못 뽑은 곳에 O를 표시한다.
- sitemap URL이 blog_url 접두어 밖이면 회사 글로 세지 않았다.
  Medium처럼 호스트 단위 sitemap이 나오는 경우를 막기 위한 generic 가드이다.

### 회사별

- **올리브영:** RSS가 2020년까지 내려와 최근 12개월 48건을 확보했고
  Trafilatura 본문 추출은 48/48이다. sitemap URL은 더 많지만
  날짜를 못 읽는 페이지가 대부분이라 RSS만으로 충분하다.
- **네이버 D2:** `d2.atom`이 최신 20건만 주고 sitemap이 없다.
  확보한 20건도 Trafilatura가 본문을 하나도 못 뽑았다 (0/20).
  목록 페이지네이션과 JS 본문 처리가 필요하다.
- **토스:** `rss.xml`이 최신 20건만 주고 robots/sitemap이 없다.
  그 20건 본문은 20/20으로 뽑힌다. 12개월 전체를 쓰려면
  목록 archive/커스텀이 필요하다.
- **당근:** Medium RSS가 최신 10건만 주고, Medium 전역 sitemap
  약 11만 URL은 `medium.com/daangn` 밖이다. 본문은 1/10이다.
  Medium 피드·렌더를 별도로 봐야 한다.

