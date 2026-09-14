# company_slugs.json

Area 파이프라인(`build_areas_per_company.py`, `manual_area_pipeline.py`)이
Area `id`를 만들 때 쓰는 회사명 → 영문 slug 매핑이다.

그룹2·4 16곳 결과(수기 필터 573건, `--output-suffix group24`)는
`data/research/tech_blog_engineering_focus_29/group24_areas.md` 다.
기존 6곳·그룹3 임베딩을 덮지 않으려면 suffix를 반드시 지정한다.

## Area id 스키마

`id = "{slug}-{순번:02d}"` (예: `oliveyoung-01`)

- `slug`는 이 파일에서 조회한다. 없는 회사면 스크립트가 바로 에러를
  내고 멈춘다 — 추측해서 slug를 만들지 않는다. `data/fixtures/index.json`에
  회사를 등록할 때 정한 slug와 반드시 같은 값을 여기도 추가해야 한다
  (웹 라우팅과 Area id가 같은 slug를 공유해야 나중에 둘을 연결할 수 있다).
- 순번은 area_name이 아니라 그 Area에 배정된 evidence 중 가장 작은
  `article_id`(콘텐츠 해시라 안정적)를 anchor로 정렬해서 매긴다.
  area_name은 LLM이 재실행마다 표현을 바꿀 수 있어서 id 기준으로 쓰지 않는다.

## 알려진 한계 (의도적으로 미해결)

같은 회사를 다시 돌렸을 때 Area 구성원(어떤 글이 그 Area에 배정되는지)
자체가 바뀌면 id도 재배정될 수 있다. 재실행 간 id를 강제로 유지시키는
registry(예: 이전 실행의 evidence 집합과 겹침을 비교해 같은 id를
재사용하는 방식)는 지금 만들지 않았다 — 아직 어디에도 Area id를
저장해서 참조하는 다운스트림 소비자가 없기 때문이다(웹 fixture는
domains가 빈 배열, Suggestion 생성 단계는 미구축). 실제로 누군가 이
id를 저장/참조하기 시작하면 그때 registry 방식을 별도 이슈로 설계한다.
