# 디자인 시스템

색·간격·글자 크기의 값은 `apps/web/src/app/globals.css` 에 정의되어 있으며,
원본은 `design/Tokens.dc.html` 아트보드입니다. 이 문서는 값이 아니라 값을
적용하는 규칙을 정의합니다.

## 색

색은 세 갈래로 구분해 사용합니다.

| 갈래 | 의미 | 토큰 |
|---|---|---|
| 중립 | 정보 표시 | `surface` `paper` `sunken` `line` `line-strong` `ink` `ink-soft` `ink-muted` |
| 강조 | 사용자가 수행할 수 있는 동작, 선택된 상태 | `accent` `accent-ink` `accent-tint` |
| 단계 | 역매칭 결과의 3단계 구분 | `stage-fit` `stage-step` `stage-far` |

- 강조색은 조작 가능한 요소와 선택 상태에만 사용합니다.
- 단계색은 역매칭 결과 화면에서만 사용합니다.
- 경고색 `warn` 은 입력 오류와 실패 안내에 사용합니다.
- 출처색 `src-blog` `src-job` 은 항상 텍스트 라벨과 함께 사용합니다.

## 카드

`components/ui/Card.tsx` 의 `Card`, `CardLink`, `cardStyle` 을 사용합니다.

| 종류 | 스타일 | 적용 대상 |
|---|---|---|
| `static` | 흰 배경, 실선 테두리, hover 없음 | 제안 카드, 이미 한 것, 저장소 입력 영역 |
| `action` | hover·선택 시 강조색 | 회사, 직무, 경험 항목, 진행 수준 |
| `cta` | 강조색 배경과 테두리 | 개인화 입력 유도 |
| `empty` | 점선 테두리, 흐린 텍스트 | 미선택 항목, 준비 중, 미구현 영역 |

- hover 효과는 조작 가능한 요소에만 적용합니다.
- 선택 상태는 hover 상태와 동일한 스타일을 사용합니다.
- `cta` 는 한 화면에 하나만 배치합니다.

## 버튼

`components/ui/Button.tsx` 의 `Button`, `ButtonLink`, `JobButton` 을 사용합니다.

| 종류 | 적용 대상 |
|---|---|
| `primary` | 해당 화면의 주 동작. 화면당 하나 |
| `secondary` | 보조 동작, 단계 이동 |
| `ghost` | 되돌리기, 삭제 등 낮은 강조가 필요한 동작 |

- 최소 높이는 44px 이며 화면 단위로 재정의하지 않습니다.
- 화면 전환은 `ButtonLink` 를 사용합니다.
- 하나의 버튼은 하나의 동작만 수행하며, 상태에 따라 라벨이 바뀌지 않습니다.

## 칩과 배지

`components/ui/Chip.tsx`, `components/ui/StageBadge.tsx` 를 사용합니다.

| 종류 | 스타일 | 적용 대상 |
|---|---|---|
| 분류 (`neutral`) | 흰 배경, 실선 테두리 | 조직이 반복하는 영역 |
| 값 (`accent`) | 강조색 테두리와 텍스트 | 저장소 분석 키워드 |
| 단계 배지 | 단계색 | 역매칭 결과 |

## 레이아웃

- 상단 바와 본문은 `components/ui/PageWidth.tsx` 를 사용합니다. 좌우 여백과
  최대 폭이 동일하므로 모든 화면에서 상단 바와 본문의 시작 위치가 일치합니다.
- 본문 텍스트와 입력 필드는 `max-w-3xl` 로 제한하고, 카드와 그리드는 전체 폭을
  사용합니다.
- 카드 그리드는 `grid-cols-1 sm:grid-cols-2`, 간격은 `gap-3` 입니다. 항목 수가
  많은 목록에 한해 `xl:grid-cols-3` 을 추가합니다.
- 배경 그라데이션은 랜딩 화면에 radial, 나머지 화면에 linear 20rem 을 적용합니다.

## 규격 외 요소

다음 요소는 위 분류에 포함되지 않습니다. 규칙이 필요한 시점에 이 문서에
추가합니다.

- 입력 필드 (`RepoField`, 검색 입력) — 테두리 `line-strong`, hover 중립색,
  focus 강조색
- 정사각형 아이콘 배지, 페이지네이션 버튼 — 별도 규격
- 오류 상자 (`state/Error`) — 경고색
