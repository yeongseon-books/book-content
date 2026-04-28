# humanize-korean — 한글 AI 티 제거 룰 (이 repo 적용판)

이 디렉토리는 [`epoko77-ai/im-not-ai`](https://github.com/epoko77-ai/im-not-ai) v1.5.1 (MIT License) 의 분류 체계를 이 블로그 repo 한글 글 작성·검수 워크플로에 흡수한 미러본입니다.

## 출처와 라이선스

- 원본: <https://github.com/epoko77-ai/im-not-ai>
- 라이선스: MIT
- 미러 시점: v1.5.1 (2026-04-27)
- 미러 범위: `references/ai-tell-taxonomy.md`, `references/quick-rules.md` 두 파일만 (Claude Code 스킬 정의·에이전트 파일은 제외 — 이 repo는 OpenCode 환경)

## 이 repo에서의 적용 범위

1. **모든 `ko/*.md` (Tistory 발행본) + `ai-web-dev-101/*.md` + `llm-from-scratch-101/ko/*.md`** — 작성 단계부터 `quick-rules.md`의 S1 패턴을 처음부터 회피.
2. **`.sisyphus/style/check-ko.sh`** — 기존 `translation-smells.txt`에 본 분류 체계의 S1 핵심 패턴을 흡수해 자동 grep 검사.
3. **`en/*.md`, `medium/*.md`** — 영어이므로 비대상.

## 두 파일의 역할

| 파일 | 용도 |
|---|---|
| [`quick-rules.md`](./quick-rules.md) | 한 콜에서 자체검증까지 하는 슬림 룰북. **글 쓰기 직전·발행 직전 빠르게 점검**. |
| [`ai-tell-taxonomy.md`](./ai-tell-taxonomy.md) | 10대 카테고리 × 40+ 서브 패턴 전체 SSOT. **모호한 케이스를 분류·근거 인용**할 때 참조. |

## 작성·검수 워크플로

### 작성 시 (Pre-write)

`quick-rules.md`의 S1 표를 한 번 훑고 시작. 특히 다음 7개는 **첫 줄부터 회피**:

- A-1 "~에 대해" / A-2 "~를 통해" / A-3 "~에 있어서" / A-7 "가지고 있다" / A-8 이중 피동
- C-5 이모지 / C-10 콜론 부제 헤딩
- D-1~D-6 (결론적으로·시사하는 바·혁신적인·의인화 추상 주어·"~할 때입니다" 결말)
- H-1 문두 접속사 5회+ / H-3 메타 진입 ("이는·이 점에서")
- I-1 "~한 것이다" 결말 / I-4 "~해야 한다" 권고형 결말
- J-1 볼드 남발 / J-2 따옴표 5회+

### 검수 시 (Pre-commit)

```bash
.sisyphus/style/check-ko.sh
```

기존 `translation-smells.txt`에 본 분류 체계의 S1·핵심 S2 패턴이 흡수되어 있어 grep 단계에서 1차 자동 탐지. 출력이 0이 아니면 해당 라인을 `quick-rules.md` 처방에 따라 수정.

### 자체검증 (Post-write 5초 룰)

`quick-rules.md` 하단의 6항 체크리스트:

1. 고유명사·수치·날짜·인용 100% 보존
2. 변경률 30% 이하 (윤문 기준)
3. 장르 이탈 없음
4. register 보존
5. 잔존 S1 패턴 0건 (D-1~D-7, A-8, C-5, C-10, H-1, I-1, J-2)
6. 인공 표현 (없던 비유·수사) 추가 안 함

## 이 repo 룰과의 우선순위

- `AGENTS.md` (이 repo의 형식 룰) > `humanize-korean` (문체 룰)
- 문체와 형식이 충돌하면 형식 룰이 이김 (예: AGENTS.md가 요구하는 `## 참고 자료` 헤딩은 humanize-korean의 헤딩 처방과 무관하게 유지).
- humanize-korean의 `voice profile` (v1.2 기능)은 미적용 — 이 repo는 단일 작가 규약이므로 불필요.

## 주의

- 이 미러는 **분류 체계 문서만** 사용합니다. 원본 repo의 Claude Code 에이전트(`humanize-monolith`, `ai-tell-detector` 등)는 OpenCode 환경에서 실행 불가합니다.
- 자동 윤문이 필요하면 원본 repo를 별도 Claude Code 환경에서 사용하고, 결과만 이 repo에 commit 하세요.
- 분류 체계 자체 갱신은 원본 repo를 fetch 해서 두 파일을 재미러링 (수동).
