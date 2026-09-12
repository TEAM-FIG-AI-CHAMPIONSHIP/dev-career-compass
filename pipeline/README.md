# Pipeline

기업 자료를 수집하고 분석해 data/published에 게시 가능한 결과를 생성하는 Python 파이프라인 영역입니다.

예정된 처리 단계는 다음과 같습니다.

1. collect: 기업 블로그, 뉴스, 승인된 채용 데이터 수집
2. normalize: 문서 날짜, 출처, URL 형식 통일
3. extract: 회사와 직무별 기술 영역 추출
4. aggregate: 일반 코드로 근거 빈도 집계
5. recommend: 근거 문서에 연결된 프로젝트 제안 생성
6. validate: 링크, 근거 ID, 데이터 스키마 검증
7. publish: 검증을 통과한 결과만 data/published에 출력

수집 원문과 사용자 데이터는 Git에 커밋하지 않습니다. LLM은 영역 추출과 제안 생성에 제한적으로 사용하고, 빈도 계산과 링크 검증은 결정적인 코드로 처리합니다.
