---
series: software-engineering-101
episode: 7
title: "Software Engineering 101 (7/10): 문서화"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - SoftwareEngineering
  - Documentation
  - README
  - ADR
  - Knowledge
seo_description: README, ADR, docstring, runbook의 역할과 Diataxis 4분면을 짧게 정리합니다.
last_reviewed: '2026-05-15'
---

# Software Engineering 101 (7/10): 문서화

코드가 좋으면 문서는 없어도 된다는 말을 종종 듣습니다. 어느 정도는 맞는 말처럼 보입니다. 잘 이름 붙은 함수, 분리된 모듈, 읽기 쉬운 테스트가 있으면 많은 설명이 필요 없을 것 같습니다. 하지만 코드만으로는 “왜 이렇게 만들었는가”, “언제 이 절차를 따라야 하는가”, “새로 들어온 사람이 어디서부터 시작해야 하는가”를 설명하기 어렵습니다.

문서가 없을 때 생기는 가장 큰 문제는 정보가 특정 사람을 거쳐서만 이동한다는 점입니다. 그러면 질문은 늘 특정 사람에게 몰리고, 그 사람이 바쁜 시간대에는 팀 전체가 느려집니다. 문서화는 친절의 문제가 아니라 비동기 협업의 기반입니다.

이 글은 Software Engineering 101 시리즈의 일곱 번째 글입니다. 여기서는 README, ADR, docstring, 런북, 온보딩 문서의 역할과 Diataxis 4분면으로 문서를 분리하는 방법을 정리합니다.

## 먼저 던지는 질문

- 좋은 README는 최소한 어떤 블록을 가져야 할까요?
- ADR은 무엇을 남기고, 코드 주석과 어떻게 다를까요?
- docstring과 타입 힌트는 문서화에서 어떤 역할을 할까요?

## 큰 그림

![Software Engineering 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/software-engineering-101/07/07-01-concept-at-a-glance.ko.png)

*Software Engineering 101 7장 흐름 개요*

## 왜 중요한가

문서가 없으면 모든 질문은 누군가의 기억력에 의존합니다. 이 구조는 팀이 작을 때는 버틸 수 있어도 규모가 커질수록 병목이 됩니다. 특히 장애 대응, 신규 입사자 온보딩, 중요한 설계 변경처럼 시간이 촉박한 상황에서는 문서 부재 비용이 훨씬 크게 드러납니다.

또한 문서는 코드의 대체물이 아니라 보완물입니다. 함수 시그니처는 사용법의 절반을 말해 줄 수 있지만, 왜 그런 인터페이스를 선택했는지까지는 설명하지 못합니다. README와 ADR, 런북이 필요한 이유가 여기에 있습니다.

## 한눈에 보는 흐름

Diataxis는 문서를 작성자 기준이 아니라 독자의 목적 기준으로 나누게 해 줍니다.

## 핵심 용어

- **README**: 저장소의 첫 인상과 진입점입니다.
- **ADR**: 하나의 결정과 이유를 짧게 남기는 문서입니다.
- **docstring**: 함수나 클래스의 사용 계약을 설명하는 문자열입니다.
- 런북: 사고나 운영 작업을 단계별로 수행하는 절차서입니다.
- **Diataxis**: 튜토리얼, 하우투, 레퍼런스, 설명으로 문서를 구분하는 모델입니다.

## 전후 비교

**이전 — 하나의 거대한 위키**

```text
"It's all on the wiki" -> nobody knows where
```

**이후 — 목적별로 나뉜 문서 구조**

```text
docs/tutorials/  docs/how-to/  docs/reference/  docs/explanation/
```

문서가 많아지는 것이 문제가 아니라, 독자가 어디서 시작해야 할지 모르는 상태가 문제입니다.

## 단계별로 작은 문서 세트 만들기

### 1단계 — README 다섯 블록 만들기

```markdown
# 1_readme.md
## What — one-sentence description
## Why — why it exists
## Quick start — working in 60 seconds
## Configuration — env var table
## Links — go deeper
```

좋은 README는 처음 들어온 사람이 1분 안에 가치를 이해하고 다음 링크로 이동할 수 있게 만듭니다.

### 2단계 — 한 장짜리 ADR 남기기

```markdown
# 2_adr.md
# ADR 0012: introduce cache
- Context, Decision, Alternatives, Consequences
- Date, Owners
```

결정은 코드를 구현한 시점보다 오래 살아남습니다. 이유를 남기지 않으면 나중에 같은 토론을 반복하게 됩니다.

### 3단계 — docstring과 타입 힌트 쓰기

```python
# 3_docstring.py
def compute_invoice(amount: int, tax_rate: float) -> int:
    """세금을 포함한 금액을 센트 단위로 반환합니다.

    Raises:
        ValueError: amount가 음수일 때 발생합니다.
    """
```

함수 시그니처와 docstring은 가장 가까운 사용 계약입니다.

### 4단계 — 런북 만들기

```markdown
# 4_runbook.md
## Symptom
- 5xx error rate > 2% for 5 min
## Diagnose
1. Check Grafana dashboard X
2. Look at the latest deploy log
## Action
- Roll back immediately (`kubectl rollout undo ...`)
```

런북은 평온한 낮이 아니라 새벽 장애 상황에서도 그대로 따라갈 수 있어야 의미가 있습니다.

### 5단계 — 온보딩 체크리스트 두기

```markdown
# 5_onboarding.md
- [ ] Clone repo, run dev environment
- [ ] Land first PR (typo fix)
- [ ] Shadow first incident within a week
```

온보딩 문서는 새로 들어온 사람이 첫 30일 안에 무엇을 경험해야 하는지 명확하게 보여 줍니다.

## 문서 세트를 검증하는 방법

문서 품질은 양보다 찾기 쉬움과 재사용성에서 드러납니다. 실제 신규 입사자나 온콜 상황을 떠올리며 문서 세트를 따라가 보세요.

### 확인 절차

1. 저장소 README만 보고 개발 환경을 띄울 수 있는지 확인합니다.
2. 최근 큰 결정 하나가 ADR이나 RFC로 남아 있는지 찾습니다.
3. 사고 대응 절차를 런북 한 장으로 따라갈 수 있는지 검토합니다.

**예상 결과:**

- README가 좋으면 첫 5분 안에 프로젝트 목적과 실행 경로가 보입니다.
- ADR이 있으면 과거 결정을 다시 논쟁하는 횟수가 줄어듭니다.
- 런북이 있으면 새벽 장애에서도 확인 순서가 분명해집니다.

### 실패 신호

- "위키 어딘가에 있다"는 말만 있고 진입 문서가 없습니다.
- 문서 소유자나 마지막 검토 시점이 없어 신뢰하기 어렵습니다.
- 온보딩 질문이 늘 특정 사람에게만 몰립니다.

## 이 코드에서 먼저 봐야 할 점

- 독자의 목적별로 나누면 문서를 찾기 쉬워집니다.
- ADR은 결정의 이유를 회수 가능하게 만듭니다.
- 런북은 새벽 사고의 비용을 줄입니다.
- README는 사용 설명서이자 저장소의 얼굴입니다.

## 어디서 자주 헷갈릴까요?

첫 번째 오해는 자동 생성 문서만 있으면 충분하다는 생각입니다. API 레퍼런스는 필요하지만, 그것만으로는 왜 이런 구조를 택했는지 설명할 수 없습니다. 자동 생성 문서는 레퍼런스의 일부일 뿐입니다.

두 번째 오해는 모든 문서를 한 페이지 위키에 몰아넣는 것입니다. 정보는 많아 보이지만 실제로는 아무도 찾지 못합니다. 문서의 양보다 탐색 구조가 먼저 중요합니다.

세 번째 오해는 문서에 소유자가 없어도 된다고 보는 태도입니다. 마지막 검토 날짜와 책임자가 없으면 문서는 곧 믿기 어려운 정보가 됩니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 문서를 코드처럼 다룹니다. 저장소 안의 마크다운 파일로 관리하고, PR로 변경하고, CI에서 링크와 구조를 검사합니다. 새로운 기능은 RFC, 코드, 문서 업데이트가 한 흐름 안에 묶여 움직이는 경우가 많습니다.

시니어 엔지니어는 코드 리뷰만큼 문서 리뷰도 중요하게 봅니다. README가 약한 저장소는 대개 구조 설명이 약하고, 런북이 없는 시스템은 운영 복구성이 낮고, ADR이 없는 팀은 같은 설계 논쟁을 반복하는 경우가 많기 때문입니다.

## 체크리스트

- [ ] README에 다섯 개 기본 블록이 있나요?
- [ ] 큰 결정에 ADR이 있나요?
- [ ] docstring이 사용 계약을 설명하나요?
- [ ] 사고 대응용 런북이 있나요?
- [ ] 각 문서에 소유자와 검토 시점이 있나요?

## 연습 문제

1. 현재 저장소 README를 다섯 블록 구조로 다시 작성해 보세요.
2. 최근 결정 하나를 ADR 형식으로 바꿔 보세요.
3. 가장 최근 사고를 기준으로 한 장짜리 런북을 써 보세요.

## 정리

문서화는 코드가 부족해서 하는 일이 아닙니다. 사람이 없어도 지식이 움직이게 하기 위해 하는 일입니다. README, ADR, docstring, 런북, 온보딩 문서가 제자리에 있으면 팀은 특정 개인의 기억에 덜 의존하게 됩니다.

다음 글에서는 그 사람들 사이의 협업 자체를 다룹니다. RFC, 비동기 의사결정, 회의 최소화, 핸드오프 메모가 어떻게 팀 시간을 되돌려 주는지 이어서 보겠습니다.

## 엔지니어링 품질을 끌어올리는 추가 실무 프레임

기능 개발이 반복될수록 팀의 속도는 개인 역량보다 시스템화 수준에 더 크게 좌우됩니다. 특히 요구사항 명세, 리뷰 체크리스트, 테스트 전략이 분리되지 않으면 구현 품질은 우연에 기대게 됩니다. 아래 틀은 작은 팀에서도 바로 적용할 수 있는 최소 운영 단위입니다.

### 요구사항 명세 템플릿

요구사항은 "무엇을 만들지"보다 "완료를 어떻게 판단할지"까지 포함해야 합니다. 문장이 추상적이면 구현 범위가 확장되고, QA와 운영에서 해석이 갈립니다.

```text
[기능명] 장바구니 쿠폰 적용
- 배경: 재구매율 개선
- 사용자 시나리오: 로그인 사용자가 결제 전 쿠폰 코드를 입력한다
- 성공 조건:
  1) 유효 쿠폰이면 총액에서 할인 금액 차감
  2) 만료 쿠폰이면 400 + "coupon_expired" 반환
  3) 중복 적용 불가
- 비기능 요구:
  - p95 응답 시간 200ms 이하
  - 감사 로그에 coupon_id, user_id, trace_id 기록
- 제외 범위:
  - 관리자 쿠폰 생성 화면은 이번 범위에서 제외
```

이 형식의 장점은 구현 이전에 충돌 지점을 드러낸다는 점입니다. 예외 코드, 성능 기준, 제외 범위를 먼저 고정하면 개발 중간에 목표가 흔들리는 일을 줄일 수 있습니다.

### 코드 리뷰 체크리스트(필수 8항목)

```text
1. 요구사항의 성공 조건이 코드에서 추적 가능한가?
2. 에러 응답 형식과 상태 코드가 합의와 일치하는가?
3. 도메인 규칙이 컨트롤러/뷰 계층으로 새지 않았는가?
4. 신규 의존성이 보안/라이선스 정책과 충돌하지 않는가?
5. 테스트가 성공/실패/경계 케이스를 모두 포함하는가?
6. 로그에 민감정보가 기록되지 않는가?
7. 롤백 또는 feature flag 경로가 준비되어 있는가?
8. 문서(README, ADR, API 스펙)가 변경 내용을 반영하는가?
```

체크리스트의 목적은 리뷰 속도를 늦추는 것이 아니라, 리뷰 품질의 편차를 줄이는 것입니다. 팀원이 바뀌어도 같은 기준으로 위험을 잡아내야 릴리스 안정성이 유지됩니다.

### 테스트 전략: 피라미드 + 변경 위험 기반

```python
# tests/test_coupon_service.py
import pytest

@pytest.mark.unit
def test_apply_valid_coupon(coupon_service):
    total = coupon_service.apply(total_amount=20000, code="SAVE10")
    assert total == 18000

@pytest.mark.unit
def test_apply_expired_coupon(coupon_service):
    with pytest.raises(ValueError, match="coupon_expired"):
        coupon_service.apply(total_amount=20000, code="OLD10")
```

```text
권장 비율(시작점)
- Unit: 70%
- Integration: 20%
- E2E: 10%
```

Unit 테스트는 규칙 변경을 빠르게 검증하고, Integration 테스트는 DB/외부 API 경계의 계약을 검증하며, E2E 테스트는 사용자 핵심 경로만 보호합니다. 모든 것을 E2E로 막으려 하면 실행 시간이 늘고 실패 원인 분리가 어려워집니다.

### 릴리스 전 확인 절차

- 요구사항 문서의 성공 조건과 테스트 케이스 ID를 매핑합니다.
- 리뷰 체크리스트 미충족 항목이 있으면 머지 전 해결 또는 위험 수용 근거를 남깁니다.
- 배포 직후 확인할 지표(p95, 에러율, 결제 성공률)를 사전에 합의합니다.
- 장애 시 되돌림 절차와 커뮤니케이션 채널을 지정합니다.

엔지니어링의 핵심은 "잘 만드는 기술"과 "같은 품질을 반복하는 시스템"을 동시에 갖추는 것입니다. 위 세 축이 고정되면 팀 규모가 커져도 의사결정의 품질이 유지되고, 기능 추가 속도와 운영 안정성을 함께 확보할 수 있습니다.

## 요구사항-리뷰-테스트 연결표

엔지니어링에서 자주 놓치는 지점은 세 문서가 따로 움직이는 상황입니다. 요구사항 문서는 목표만 말하고, 리뷰는 스타일 중심으로 흘러가고, 테스트는 구현 이후에 뒤따라옵니다. 이렇게 분리되면 기능은 동작해도 품질 기준이 흐려집니다. 아래처럼 연결표를 두면 변경 영향이 추적됩니다.

```text
REQ-12: 만료 쿠폰 거부
- Review check: 상태 코드 400 + error_code=coupon_expired 확인
- Test case: test_apply_expired_coupon
- Metric: coupon_expired 발생 비율
```

연결표를 유지하면 "무엇을 만들었는가"가 아니라 "어떤 기준을 만족했는가"로 대화가 바뀝니다. 회고 시점에도 장애 원인을 요구사항 해석, 리뷰 누락, 테스트 공백 중 어디서 시작됐는지 빠르게 찾을 수 있습니다.

### 운영 전환 체크

- 배포 노트에 요구사항 ID와 PR 링크를 함께 남깁니다.
- 온콜 핸드오프 문서에 새 기능의 실패 시그널을 명시합니다.
- 첫 24시간 관찰 지표와 임계치를 릴리스 전에 고정합니다.

이 작은 연결 장치가 있으면 팀 규모가 커져도 품질 기준이 개인 기억에 의존하지 않습니다.

## 실무 적용 메모

아래 항목은 실제 팀 운영에서 즉시 적용 가능한 최소 기준입니다.

- 요구사항 ID를 브랜치 이름과 PR 제목에 포함해 추적성을 높입니다.
- 코드 리뷰에서 "변경 위험" 항목을 별도로 두고, 장애 반경을 한 줄로 남깁니다.
- 테스트 결과는 성공 여부만 기록하지 않고 실패 시 복구 절차 링크를 같이 둡니다.
- 배포 후 모니터링 대시보드 URL을 릴리스 노트에 고정합니다.

작은 기록 규칙이 누적되면 협업 비용이 줄고, 동일한 문제를 반복해서 조사하는 시간을 크게 줄일 수 있습니다.

## 처음 질문으로 돌아가기

- **좋은 README는 최소한 어떤 블록을 가져야 할까요?**
  - 본문의 기준은 문서화를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **ADR은 무엇을 남기고, 코드 주석과 어떻게 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **docstring과 타입 힌트는 문서화에서 어떤 역할을 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Software Engineering 101 (1/10): 소프트웨어 엔지니어링이란 무엇인가?](./01-what-is-software-engineering.md)
- [Software Engineering 101 (2/10): 요구사항 이해하기](./02-understanding-requirements.md)
- [Software Engineering 101 (3/10): 설계와 구현의 차이](./03-design-vs-implementation.md)
- [Software Engineering 101 (4/10): 코드 리뷰](./04-code-review.md)
- [Software Engineering 101 (5/10): 테스트 전략](./05-testing-strategy.md)
- [Software Engineering 101 (6/10): 버전 관리와 릴리스](./06-version-control-and-release.md)
- **문서화 (현재 글)**
- 협업 프로세스 (예정)
- 유지보수와 기술부채 (예정)
- 좋은 소프트웨어의 기준 (예정)

<!-- toc:end -->

## 참고 자료

- [Diataxis Framework](https://diataxis.fr/)
- [The Documentation System — Daniele Procida](https://documentation.divio.com/)
- [Write the Docs — Documentation Guide](https://www.writethedocs.org/guide/)
- [Google — Documentation Best Practices](https://google.github.io/styleguide/docguide/best_practices.html)

Tags: Computer Science, SoftwareEngineering, Documentation, README, ADR, Knowledge
