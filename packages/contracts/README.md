# Contracts

Next.js 웹과 Python 파이프라인이 함께 사용하는 데이터 계약을 관리합니다.

초기에는 JSON Schema를 계약의 기준으로 사용하고, 웹은 TypeScript 타입으로 읽으며 파이프라인은 같은 스키마로 출력 결과를 검증합니다.

예정된 계약은 다음과 같습니다.

- company: 회사와 직무 정보
- analysis: 조직 영역, 프로젝트 제안, 근거 연결
- personalization: 경험 입력과 개인화 결과

동일한 타입을 TypeScript와 Python에 각각 손으로 중복 정의하지 않는 것을 원칙으로 합니다.
