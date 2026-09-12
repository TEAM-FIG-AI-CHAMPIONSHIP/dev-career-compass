# 디자인 캔버스

`.dc.html` 아트보드 8개와 배치 정보(`canvas.json`)가 원본입니다.

| 파일 | 내용 |
| --- | --- |
| `Tokens.dc.html` | 색·타이포·간격·라운드 토큰. `apps/web/src/app/globals.css` 의 출처 |
| `Components.dc.html` | 버튼, 칩, 제안 카드, 근거 타임라인, 체크 항목, 상태 |
| `Main.dc.html` | S1 랜딩 |
| `S2Result.dc.html` | S2 결과 |
| `S3Experience.dc.html` | S3 경험 입력 |
| `S4Personalized.dc.html` | S4 개인화 결과 |
| `S5Reverse.dc.html` | S5 역매칭 직무 선택 |
| `S6ReverseResult.dc.html` | S6 역매칭 결과 |

## 커밋하지 않는 것

`design/refactor-me-design-system.html` 은 위 파일들을 묶어 만든 게시용
생성물이며 편집기 코드가 통째로 들어 있어 2.5MB 입니다. `.gitignore` 에
있습니다.

## 구현과의 관계

토큰 값이 어긋나면 `.dc.html` 쪽을 먼저 고치고 `globals.css` 에 옮깁니다.
화면 아트보드는 시안이며, 실제 동작은 `apps/web` 이 기준입니다.
