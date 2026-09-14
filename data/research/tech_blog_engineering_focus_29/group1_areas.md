# group1_areas: 그룹1 회사 Area 생성 결과 (수동 프롬프팅, 진행 중)

engineering_focus -> v4 embedding -> clustering(complete linkage) -> LLM 병합 -> deterministic membership -> 키워드 태깅 전체 파이프라인을 그룹1(#58) 회사에 독립적으로 적용한 결과다 (LLM 두 단계는 claude.ai 수동 프롬프팅으로 수행).

그룹1은 삼성반도체·여기어때·쏘카·카카오 4곳이다. 이 파일은 완료된 회사만
담는다 — 현재 쏘카 1곳만 완료, 나머지 3곳은 engineering_focus 단계(#58)가
아직 안 끝나서 Area 대상이 아니다.

각 Area는 안정적인 `id`(예: `socar-01`)를 갖는다. 스키마와 한계는
`../../../pipeline/experiments/tech_blog_engineering_focus_29/config/README.md` 참고.

## 알려진 한계

- 쏘카는 `tech.socar.kr/sitemap.xml`의 lastmod 기준으로 최근 12개월치를
  직접 재검증했다 — 9건이 실제로 전체 개수가 맞다(월 1회 정도 페이스,
  RSS 상한으로 인한 과소집계가 아님).

## 쏘카 (9개 글)

| Area | 근거 수 | 키워드 |
|---|---:|---|
| 디자인 시스템과 크로스플랫폼 앱 프레임워크 설계 | 4 | Figma Code Connect, Slot 기반 합성 컴포넌트, 정책 객체 + Hook 어댑터, 트리쉐이킹 번들 구조, Figma Plugin 토큰 PR, BluetoothSpec / BluetoothHandle 분리 |
| 배포·종료 동작과 레거시 코드베이스 정리 | 3 | CloudFront invalidation 범위, ChunkLoadError, Graceful shutdown (SIGTERM), dumb-init (PID 1), terminationGracePeriodSeconds, 무중단 스키마 변경 절차 |
| LLM 에이전트의 판단 신뢰성 확보 | 2 | 지식 그래프 (Neo4j), 사람 정의 시드, LLM 신뢰도 점수 임계값, structured output 스키마, 안전한 기본값 폴백 |

unassigned: 0
