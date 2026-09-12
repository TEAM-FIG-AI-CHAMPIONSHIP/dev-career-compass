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

## 개발 환경 준비

Python 3.11 이상이 필요합니다. 각 팀원은 저장소를 clone한 뒤 자신의 로컬 가상환경을 생성합니다.

저장소 루트에서 먼저 Python 버전을 확인합니다.

    python3 --version

3.11 이상인 경우 다음 명령을 실행합니다.

    python3 -m venv pipeline/.venv
    source pipeline/.venv/bin/activate
    python -m pip install --upgrade pip
    python -m pip install -e "./pipeline[dev]"

설치 후 다음 명령으로 환경을 확인합니다.

    python --version
    python -m pytest
    ruff check pipeline

가상환경과 Python 패키지 빌드 산출물은 Git에 포함되지 않습니다.

## 실험 작업 방식

각 실험은 별도 브랜치와 별도 디렉터리에서 작업합니다.

    git switch -c experiment/company-coverage

실험 코드는 pipeline/experiments 아래에 주제별 디렉터리를 만들어 배치합니다. 여러 실험에서 반복되는 로직은 pipeline/src/career_compass_pipeline으로 옮기고 테스트를 추가합니다.

공유 가능한 통계와 요약 결과만 data/research에 저장합니다. 수집 원문과 임시 결과는 Git에서 제외되는 data/work에 저장합니다.
