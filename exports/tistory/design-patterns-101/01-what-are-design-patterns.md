
# 디자인 패턴이란 무엇인가?

> Design Patterns 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 디자인 패턴이 왜 필요한가요?

> 같은 문제를 매번 새로 풀기 싫기 때문입니다. 패턴은 검증된 풀이의 이름표입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 디자인 패턴의 정의
- GoF 23개 패턴의 분류
- 패턴이 진짜로 해결하는 문제
- 패턴을 배우는 올바른 순서
- 패턴이 해가 되는 순간

## 왜 중요한가

패턴은 정답이 아니라 어휘입니다. "Strategy로 빼자"라는 한 마디에 동료가 같은 그림을 떠올릴 수 있다는 것 — 이것이 패턴의 가장 큰 가치입니다.

> 패턴은 코드보다 대화에서 먼저 빛난다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    P["Problem"] --> N["Pattern Name"]
    N --> S["Solution structure"]
    S --> T["Tradeoffs"]
```

이름이 곧 풀이를 부른다.

## 핵심 용어 정리

- **Design pattern**: 자주 발생하는 설계 문제의 검증된 해법.
- **GoF**: Gang of Four — 4명의 저자가 정리한 23개 패턴.
- **Creational / Structural / Behavioral**: 패턴의 세 가지 분류.
- **Antipattern**: 자주 보이지만 해로운 풀이.
- **Idiom**: 특정 언어에 어울리는 작은 패턴.

## Before/After

**Before**

```python
# "if 종류로 분기" 가 곳곳에 흩어진다
if kind == "credit": process_credit(...)
elif kind == "paypal": process_paypal(...)
```

**After**

```python
# Strategy 패턴 한 줄로 정리
processor = PROCESSORS[kind]
processor.charge(...)
```

이름이 붙은 풀이로 의도를 표현.

## 실습: 패턴을 익히는 5단계

### 1단계 — 문제 인식

```python
# 1_problem.py
# 같은 분기/같은 객체 생성/같은 알림 흐름이 반복?
# 패턴이 등장할 무대.
```

문제부터 정의합니다.

### 2단계 — 패턴 이름 떠올리기

```python
# 2_name.py
# 분기? Strategy. 생성? Factory. 알림? Observer.
```

이름이 풀이를 끌어옵니다.

### 3단계 — 구조 그리기

```python
# 3_structure.py
# 클래스 다이어그램으로 한 번 그려본 뒤 코드.
```

구조를 먼저, 코드는 나중에.

### 4단계 — 작게 적용

```python
# 4_small.py
# 시스템 전체에 적용하지 말고 한 모듈에서.
```

작게 시도하고 효과를 검증.

### 5단계 — 트레이드오프 적기

```python
# 5_tradeoff.md
# - 얻은 것: 분기 제거, 확장 용이
# - 잃은 것: 클래스 수 증가
```

패턴은 항상 거래입니다.

## 이 코드에서 주목할 점

- 패턴은 코드를 바꾸기 전 *대화*를 바꿉니다.
- 모든 패턴은 트레이드오프를 가집니다.
- 적용 단위는 보통 작습니다.

## 자주 하는 실수 5가지

1. **모든 곳에 패턴 적용.** 단순 코드가 복잡해진다.
2. **이름만 외우고 문제는 모름.** 적용 시점을 놓친다.
3. **언어 특성 무시.** Python에서 Singleton을 강박적으로 만듦.
4. **트레이드오프 무시.** 클래스 폭발만 남음.
5. **패턴이 곧 정답이라 믿기.** 더 단순한 해법을 놓친다.

## 실무에서는 이렇게 쓰입니다

코드 리뷰의 공통 어휘로 가장 자주 쓰입니다 — "여기 Adapter 하나 두자", "Strategy로 빼자". 이름이 곧 합의입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 패턴을 어휘로 다룬다.
- 문제부터 식별하고 이름을 붙인다.
- 적용 범위는 작게 시작한다.
- 트레이드오프를 의식한다.
- 더 단순한 해법이 있는지 마지막에 한 번 더 묻는다.

## 체크리스트

- [ ] 어떤 문제를 푸는지 한 줄로 적었는가?
- [ ] 어울리는 패턴 이름이 떠오르는가?
- [ ] 구조를 그림으로 그려봤는가?
- [ ] 트레이드오프를 적었는가?
- [ ] 더 단순한 해법은 없는가?

## 연습 문제

1. 본인 코드에서 같은 분기 구조가 3번 이상 반복되는 곳을 찾아 보세요.
2. 그 자리에 어울리는 패턴 이름을 1개 떠올려 보세요.
3. 패턴 적용 후 트레이드오프 2개를 적어 보세요.

## 정리 및 다음 단계

패턴은 어휘입니다. 다음 글부터 GoF 23개를 세 그룹 — Creational, Structural, Behavioral — 으로 묶어 살펴봅니다.

- **디자인 패턴이란 무엇인가? (현재 글)**
- Creational 패턴 (예정)
- Structural 패턴 (예정)
- Behavioral 패턴 (예정)
- Strategy 패턴 (예정)
- Adapter 패턴 (예정)
- Observer 패턴 (예정)
- Factory와 의존성 주입 (예정)
- 패턴을 남용하지 않는 법 (예정)
- Python에 어울리는 패턴 (예정)
## 참고 자료

- [Design Patterns: Elements of Reusable Object-Oriented Software (GoF)](https://en.wikipedia.org/wiki/Design_Patterns)
- [refactoring.guru — Design Patterns](https://refactoring.guru/design-patterns)
- [Patterns of Enterprise Application Architecture](https://martinfowler.com/eaaCatalog/)
- [Head First Design Patterns](https://www.oreilly.com/library/view/head-first-design/9781492077992/)

Tags: Computer Science, DesignPatterns, SoftwareDesign, GoF, Architecture, Foundations

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
