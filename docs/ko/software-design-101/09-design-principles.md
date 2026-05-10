---
series: software-design-101
episode: 9
title: 설계 원칙 모음
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - SoftwareDesign
  - SOLID
  - KISS
  - YAGNI
  - Principles
seo_description: SOLID, KISS, YAGNI, DRY, 디미터 법칙을 한 자리에서 정리하고 언제 적용할지 보여줍니다.
last_reviewed: '2026-05-04'
---

# 설계 원칙 모음

> Software Design 101 시리즈 (9/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: SOLID, KISS, YAGNI… 모두 외울 가치가 있나요?

> 외울 게 아니라 *언제* 떠올릴지를 압니다. 각 원칙은 코드 냄새에 대한 응답입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- SOLID 다섯 가지 핵심 정리
- KISS와 YAGNI의 자리
- DRY의 함정
- 디미터의 법칙
- 원칙을 *언제* 꺼내야 하는가

## 왜 중요한가

원칙은 정답이 아니라 진단 도구입니다. 코드 냄새가 나면 어떤 원칙이 깨졌는지 가리키고, 어떻게 고칠지 힌트를 줍니다.

> 원칙은 "왜"를 묻게 한다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    S["Smell"] --> P["Principle"]
    P --> R["Refactor"]
    R --> C["Cleaner code"]
```

냄새 → 원칙 → 리팩토링.

## 핵심 용어 정리

- **SRP**: 모듈은 변경 이유가 하나여야 한다.
- **OCP**: 확장에 열리고 수정에 닫혀 있어야 한다.
- **LSP**: 하위 타입은 상위 타입을 대체할 수 있어야 한다.
- **ISP**: 사용자는 쓰지 않는 인터페이스에 의존하지 않는다.
- **DIP**: 구체에 의존하지 말고 추상에 의존한다.
- **KISS / YAGNI / DRY / Law of Demeter**: 보조 원칙 — 단순하게, 미리 만들지 말고, 반복을 의심하고, 친구의 친구와 말하지 마라.

## Before/After

**Before**

```python
class UserService:
    def signup(self, payload):
        # 검증 + 저장 + 이메일 + 통계 + 로깅 + 결제까지
        ...
```

**After**

```python
class SignupValidator: ...
class UserRepo: ...
class WelcomeMailer: ...
class SignupService:
    def __init__(self, validator, repo, mailer): ...
    def run(self, payload): ...
```

SRP를 적용해 협력하는 작은 단위로.

## 실습: 원칙을 꺼내는 5가지 상황

### 1단계 — "이 클래스 왜 이렇게 큼?" → SRP

```python
# 1_srp.py
# 변경 이유 두 개 이상이면 분리.
```

### 2단계 — "또 if-elif 체인" → OCP

```python
# 2_ocp.py
# 분기를 다형성/등록표로.
```

### 3단계 — "하위 클래스가 예외" → LSP

```python
# 3_lsp.py
# 상속 계층을 의심.
```

### 4단계 — "쓰지도 않는 메서드 강요" → ISP

```python
# 4_isp.py
# 인터페이스를 쪼갠다.
```

### 5단계 — "도메인이 DB를 안다" → DIP

```python
# 5_dip.py
# 추상을 도메인 쪽에.
```

## 이 코드에서 주목할 점

- 각 원칙이 다른 종류의 냄새를 가리킵니다.
- 원칙은 *코드를* 고치게 만듭니다, 만 하지 않게.
- 한 번에 한 원칙만 적용하면 가독성이 유지됩니다.

## 자주 하는 실수 5가지

1. **DRY 과잉.** 우연히 비슷한 코드를 무리하게 합치고 결합 폭발.
2. **YAGNI 무시.** 미래의 가정으로 추상화 미리 추가.
3. **SOLID 강박.** 작은 스크립트도 5계층 분리.
4. **KISS를 게으름의 변명으로.** 단순함이 아니라 회피.
5. **원칙을 규칙처럼 적용.** 맥락을 잊는다.

## 실무에서는 이렇게 쓰입니다

코드 리뷰의 공통 언어가 됩니다. "이건 SRP가 깨진 것 같아"라고 말하면 동료가 같은 그림을 떠올립니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 원칙을 진단 도구로 쓴다.
- 한 번에 한 가지만 적용한다.
- DRY보다 결합도를 먼저 본다.
- YAGNI를 기억하며 추상화를 미룬다.
- 시스템 크기에 맞는 원칙 강도를 고른다.

## 체크리스트

- [ ] 변경 이유가 하나로 모이나? (SRP)
- [ ] 새 기능 추가가 기존 코드 수정 없이 가능한가? (OCP)
- [ ] 하위 타입이 약속을 깨지 않는가? (LSP)
- [ ] 인터페이스가 사용자별로 적절한가? (ISP)
- [ ] 도메인이 추상에만 의존하는가? (DIP)

## 연습 문제

1. 본인 코드의 가장 큰 클래스에서 SRP 위반을 1개 찾아 분리해 보세요.
2. if-elif 체인을 OCP 관점에서 다시 써 보세요.
3. 작년에 만든 추상화 중 YAGNI에 걸리는 것을 1개 정리해 보세요.

## 정리 및 다음 단계

원칙은 길잡이입니다. 마지막 글에서는 이 시리즈의 모든 도구를 — 작은 프로젝트 — 에 적용해 봅니다.

<!-- toc:begin -->
- [소프트웨어 설계란 무엇인가?](./01-what-is-software-design.md)
- [관심사 분리](./02-separation-of-concerns.md)
- [모듈과 경계](./03-modules-and-boundaries.md)
- [의존성 방향](./04-dependency-direction.md)
- [인터페이스와 추상화](./05-interfaces-and-abstraction.md)
- [계층 아키텍처](./06-layered-architecture.md)
- [데이터 흐름 설계](./07-data-flow-design.md)
- [변경 영향 줄이기](./08-reducing-change-impact.md)
- **설계 원칙 모음 (현재 글)**
- 작은 프로젝트로 설계 연습 (예정)
<!-- toc:end -->

## 참고 자료

- [SOLID Principles (Robert C. Martin)](https://web.archive.org/web/20151010224057/http://www.objectmentor.com/resources/articles/Principles_and_Patterns.pdf)
- [Law of Demeter](https://en.wikipedia.org/wiki/Law_of_Demeter)
- [The Wrong Abstraction (Sandi Metz)](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)
- [YAGNI (Martin Fowler)](https://martinfowler.com/bliki/Yagni.html)
