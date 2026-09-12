# 협업 컨벤션

이슈, 브랜치, PR, 리뷰의 최소 규칙을 정합니다. 해커톤 중에도 작업 단위와 완료 기준을 맞추기 위한 문서입니다.

## 작업 흐름

1. GitHub 이슈를 먼저 만듭니다.
2. `main`에서 브랜치를 분기해 작업합니다.
3. PR을 열고 이슈를 연결합니다.
4. 리뷰를 받은 뒤 `main`에 머지합니다. 머지된 원격 브랜치는 삭제합니다.

한 PR은 한 이슈의 완료 기준을 충족하는 범위로 유지합니다. 실험과 제품 코드를 한 PR에 섞지 않습니다.

## 타입

이슈 제목, 브랜치, PR 제목에 같은 타입을 사용합니다.

| 타입 | 용도 |
| --- | --- |
| `feat` | 기능 추가 |
| `fix` | 버그 수정 |
| `docs` | 문서 |
| `refactor` | 동작 유지 리팩터 |
| `test` | 테스트 |
| `chore` | 설정, 도구, 의존성 |
| `experiment` | 파이프라인 일회성 실험 |

## 이슈

이슈는 `.github/ISSUE_TEMPLATE`의 `작업 이슈` 템플릿을 사용합니다.

- 제목: `[type] 내용`
- 예: `[docs] API 요청·응답 명세 초안 작성`
- 완료 기준은 체크리스트로 작성합니다. 모호한 기준은 구현 전에 구체화합니다.

구현 이슈에는 무엇을 왜 하는지, 완료 상태를 어떻게 판단하는지 적습니다. 관련 설계 결정이나 테스트 방법이 있으면 참고 사항에 남깁니다.

## 브랜치

`main`에서 분기하고, 타입과 짧은 설명을 사용합니다.

    git switch main
    git pull
    git switch -c docs/api-contract-draft

규칙:

- `type/짧은-영문-설명`
- 소문자, 숫자, 하이픈만 사용합니다.
- 예: `feat/company-list`, `fix/broken-source-link`, `experiment/company-coverage`

파이프라인 실험은 `experiment/` 접두사와 `pipeline/experiments` 아래 주제별 디렉터리를 함께 사용합니다. 팀원이 같은 실험 파일을 수정하지 않도록 디렉터리를 나눕니다.

## 커밋

PR 제목과 같은 `type: 내용` 형식을 권장합니다.

    docs: API 요청·응답 명세 초안 작성

한 커밋은 한 가지 변경 이유를 담습니다. 완료 기준과 무관한 정리 작업은 분리합니다.

## Pull Request

PR은 `.github/pull_request_template.md`를 사용합니다.

- 제목: `type: 내용`
- 예: `docs: API 요청·응답 명세 초안 작성`
- 관련 이슈를 `Closes #번호`로 연결합니다. 닫지 않을 이슈는 `Related to #번호`를 사용합니다.

본문에는 변경 이유, 테스트 또는 확인 방법, 리뷰어가 볼 지점을 적습니다. 확인 사항 체크리스트를 채운 뒤 리뷰를 요청합니다.

`main`에 머지되면 해당 PR의 원격 브랜치는 삭제합니다. GitHub 저장소의 Automatically delete head branches 설정을 켜 두고, 로컬 브랜치는 각자 지우면 됩니다.

## 리뷰

- 리뷰어는 가능하면 로컬에서 실행하거나 관련 테스트를 돌립니다.
- 실행하지 못한 경우 PR 댓글에 남깁니다.
- 완료 기준과 데이터 정책을 함께 확인합니다.

승인은 완료 기준을 충족하고, 커밋하면 안 되는 파일이 없을 때 합니다.

## 영역별 작업 위치

| 영역 | 위치 | 확인 |
| --- | --- | --- |
| 웹 | `apps/web` | `npm run lint`, `npm run build` |
| 파이프라인 | `pipeline` | `python -m pytest`, `ruff check pipeline` |
| 데이터 계약 | `packages/contracts` | 웹과 파이프라인이 같은 스키마를 쓰는지 확인 |
| 게시 데이터 | `data/published` | 검증을 통과한 결과만 커밋 |
| 연구 요약 | `data/research` | 공유 가능한 통계와 요약만 커밋 |
| 문서 | `docs` | 구현과 검수에 쓰일 결정만 기록 |

반복되는 파이프라인 로직은 `pipeline/experiments`에 두지 않고 `pipeline/src/career_compass_pipeline`으로 옮긴 뒤 테스트를 추가합니다.

## 커밋하면 안 되는 것

다음 항목은 이슈, PR, 커밋에 포함하지 않습니다.

- API 키, 토큰, `.env` 실값
- 기술 블로그, 뉴스, 채용 공고 본문 전체
- 사용자가 입력한 경험 값
- GitHub README 원문
- `data/raw`, `data/work`, `data/intermediate`의 수집 원문과 임시 결과
- 가상환경, `node_modules`, 빌드 산출물

웹에는 검증된 구조화 결과와 출처 메타데이터만 제공합니다. 계약 타입은 TypeScript와 Python에 각각 손으로 중복 정의하지 않습니다.
