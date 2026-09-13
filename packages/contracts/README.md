# Contracts

Next.js 웹과 Python 파이프라인이 함께 사용하는 데이터 계약의 기준입니다.
계약의 원본은 `schemas/`의 JSON Schema이며, 웹과 파이프라인 타입은 이 스키마에서
생성하는 것을 원칙으로 합니다. 같은 계약을 TypeScript와 Python에 각각 손으로
중복 정의하지 않습니다.

## 현재 계약

| 스키마 | 책임 |
|---|---|
| `role-catalog.schema.json` | 상위 직무와 내부 세부 트랙 |
| `experience-catalog.schema.json` | 회사 연결에 쓰는 표준 경험과 GitHub 검증 정책 |
| `company-project.schema.json` | 회사 프로젝트와 진입·연결 경험 ID |

`examples/`는 스키마 구조를 검증하기 위한 예시일 뿐 게시 데이터가 아닙니다.
예시의 직무, 세부 트랙과 경험 항목을 제품의 확정 목록으로 사용하지 않습니다.

## 버전

각 문서에는 두 버전이 있습니다.

- `schemaVersion`: JSON 문서의 필드 구조 버전
- `version`: 카탈로그 또는 산출물 내용 버전

필드의 의미나 필수 여부가 바뀌면 `schemaVersion`을 올립니다. 항목을 추가, 수정,
폐기하면 `version`을 올립니다. 한 번 게시한 ID는 다른 의미로 재사용하지 않고,
더 이상 쓰지 않는 항목은 삭제 대신 `deprecated`로 전환합니다.

## 상태

- `draft`: 조사·검증 중이며 사용자 화면과 매칭에 사용하지 않음
- `published`: 검증을 통과해 제품에서 사용 가능
- `deprecated`: 새 분석에는 사용하지 않지만 과거 데이터 해석을 위해 ID를 보존

LLM에는 `published` 경험만 전달합니다. 회사 수 집계와 매칭에도 `published`
직무·세부 트랙·프로젝트만 사용합니다.

## 계약 사이의 불변 조건

JSON Schema만으로 다른 파일의 ID 존재 여부까지 검증할 수 없으므로 게시
파이프라인은 다음 조건을 추가로 검사해야 합니다.

1. 경험의 `roleIds`는 직무 카탈로그에 존재합니다.
2. 경험의 `trackIds`는 `roleIds` 중 하나에 속합니다.
3. 회사 프로젝트의 `roleId`와 `trackIds`는 직무 카탈로그에 존재합니다.
4. 프로젝트의 `entryExperienceIds`와 `bridgeExperienceIds`는 게시된 경험입니다.
5. 한 프로젝트에서 진입 경험과 연결 경험은 겹치지 않습니다.
6. 게시된 프로젝트에는 하나 이상의 진입·연결 경험과 하나 이상의 근거가 있습니다.

이 교차 계약 검증은 회사 조사 산출물이 정해질 때 파이프라인의 정식 검증 단계에
추가합니다.

## 관련 설계

- `docs/superpowers/specs/2026-09-13-github-experience-company-matching-design.md`
