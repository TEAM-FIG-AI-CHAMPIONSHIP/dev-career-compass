# Experiments

제품 범위와 데이터 수집 가능성을 검증하기 위한 일회성 Python 실험 코드를 둡니다.

반복해서 사용하는 로직은 src/career_compass_pipeline 아래의 정식 모듈로 옮깁니다.

팀원끼리 같은 파일을 수정하지 않도록 주제별 디렉터리를 사용합니다.

    experiments/
    ├── job_postings_crawler/
    │   └── README.md
    ├── tech_blog_source_coverage/
    │   └── README.md
    ├── tech_blog_company_role_census/
    │   └── README.md
    ├── tech_blog_engineering_focus_29/
    │   └── config/README.md
    ├── company_coverage/
    │   └── main.py
    ├── role_coverage/
    │   └── main.py
    └── llm_comparison/
        └── main.py

실험 디렉터리에는 목적, 실행 방법, 입력과 출력 위치를 설명하는 README를 함께 둡니다. API 키와 수집 원문은 커밋하지 않습니다.
