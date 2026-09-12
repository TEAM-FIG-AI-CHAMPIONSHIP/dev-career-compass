# Dev Career Compass

기업 기술 블로그, 뉴스, 채용 공고를 분석해 개발자 취업 준비자가 다음 프로젝트 방향을 결정하도록 돕는 서비스입니다.

## Repository structure

- apps: 배포 가능한 애플리케이션
- data: 프론트용 fixture와 검증을 통과한 게시 데이터
- docs: 제품 요구사항, 화면 흐름, 아키텍처 결정 기록
- packages: 애플리케이션과 파이프라인이 공유하는 계약
- pipeline: 수집, 분석, 검증, 게시를 담당할 Python 파이프라인

## Web development

웹 애플리케이션은 apps/web에 있습니다.

    cd apps/web
    npm install
    npm run dev

코드 검사와 프로덕션 빌드는 다음 명령으로 확인합니다.

    npm run lint
    npm run build

## Deployment

현재 기본 Next.js 애플리케이션은 Vercel에 배포되어 있습니다.

- Production: https://dev-career-compass.vercel.app

## Data policy

수집한 원문, 사용자 경험 입력, GitHub README 원문은 저장소에 커밋하지 않습니다. 웹에는 검증된 구조화 결과와 출처 메타데이터만 제공합니다.
