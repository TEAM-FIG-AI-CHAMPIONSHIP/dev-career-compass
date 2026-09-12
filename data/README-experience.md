# data/experience.json 은 임시입니다

경험 체크 항목이 아직 확정되지 않아, F-05 경험 입력 화면에 쓰는 값을 넣어 둔
상태입니다. 화면과 개인화를 먼저 완주시키려는 임시값이며 그대로 제출할 값이
아닙니다.

현재 `version` 은 2입니다. 프로젝트 종류 6개, 직무별 경험 4개 그룹
(`backend`, `frontend`, `data-ai`, `mobile`), 진행 수준 3단계입니다.

## 바꿀 때 지킬 것

- 항목을 **추가·삭제·수정하면 `version` 을 올립니다.** 브라우저에 저장된 입력값은
  `catalogVersion` 이 다르면 버려집니다. 안 올리면 사라진 항목 id 가 남아
  엉뚱한 개인화가 나갑니다.
- **한 번 쓴 `id` 는 재사용하지 않습니다.** 뜻이 바뀌면 새 id 를 만듭니다.
- `backend` 그룹처럼 직무별 항목은 `appliesTo` 에 직무 슬러그를 적습니다.
  비워 두면 모든 직무에 보입니다.
- 직무 슬러그는 게시 데이터와 맞춥니다: `backend`, `frontend`, `data-ai`,
  `mobile`.

모양은 `apps/web/src/types/data.ts` 의 `ExperienceCatalog` 입니다.

## README 키워드와 초기 체크

2단계는 경험 카드 id 가 아니라 표준 기술 키워드 배열을
`sessionStorage` (`repositoryKeywords`) 에 남깁니다. 3단계는
`apps/web/src/lib/keyword-experience.ts` 에서 그 키워드를 카탈로그 id 로
옮긴 뒤, 저장된 선택이 없을 때만 섹션 1·2 초기 체크에 씁니다. 사용자는
자동 선택 항목도 자유롭게 고칠 수 있습니다.
