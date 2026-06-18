---
series: computer-science-101
episode: 1
title: "바이브코딩을 위한 컴퓨터 과학 기초 (1/10): Computer Science란 무엇인가?"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Computer Science
  - 컴퓨터과학
  - CS 입문
  - 추상화
  - AI 코딩
seo_description: AI에게 코드를 시키기 전에 컴퓨터과학이 무엇을 연구하는지, 추상화가 왜 핵심 도구인지 큰 그림을 잡습니다.
language: ko
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 컴퓨터 과학 기초 (1/10): Computer Science란 무엇인가?

> 이 글은 **바이브코딩을 위한 컴퓨터 과학 기초** 시리즈의 첫 번째 글입니다. AI에게 코드를 시키려면 컴퓨터가 어떻게 동작하는지 기본은 알아야 합니다. 이 시리즈는 그 기초를 10편에 걸쳐 정리합니다.

---

AI 도구가 코드를 대신 써 주는 시대라도, "이 코드가 왜 느린지", "왜 메모리를 이렇게 쓰는지"를 설명하지 못하면 AI와의 대화는 막힙니다. 프롬프트로 원하는 코드를 끌어내려면 내가 먼저 문제를 정확히 말할 수 있어야 하고, 그러려면 컴퓨터과학의 언어를 조금은 알아야 합니다.

처음 컴퓨터과학을 접하면 프로그래밍 문법을 더 많이 아는 일이 곧 CS를 잘하는 일처럼 보이기 쉽습니다. 하지만 실무에서 오래 버티는 엔지니어를 가르는 기준은 언어 숙련도보다, 계산을 어떻게 모델링하고 추상화하며 한계를 어디까지 읽어 내는지에 더 가깝습니다.

여기서는 컴퓨터과학이 정확히 무엇을 다루는지, 왜 추상화가 이 분야의 공용 언어인지, 그리고 이후 글들이 어떤 지도를 따라 연결되는지 큰 그림부터 잡겠습니다.

> **바이브코딩 관점:** AI 코딩 도구를 쓸 때 "추상화 수준을 어떻게 설명하느냐"가 좋은 코드를 받느냐 나쁜 코드를 받느냐를 가릅니다. 이 글은 그 언어를 익히는 출발점입니다.

---

## 이 글에서 다룰 문제

- 컴퓨터과학은 프로그래밍과 어떻게 다르고, 정확히 무엇을 연구하는 학문일까요?
- 왜 추상화가 컴퓨터과학의 가장 중요한 도구로 반복해서 등장할까요?
- 알고리즘, 시스템, 응용 과목은 서로 어떤 계층 관계로 이어질까요?
- AI에게 코드를 맡길 때 CS 개념을 모르면 어떤 문제가 생길까요?
- 바이브코더가 CS를 배울 때 가장 자주 놓치는 포인트는 무엇일까요?

---

## 핵심 개념 한 줄 정리

> **CS = 계산의 원리, 한계, 그리고 응용을 연구하는 학문**

프로그래밍은 도구를 사용하는 기술이고, 컴퓨터과학은 도구가 작동하는 원리를 이해하는 학문입니다. 원리를 알면 AI에게 더 정확한 지시를 내릴 수 있고, AI가 내놓은 코드의 품질도 평가할 수 있습니다.

| 용어 | 설명 |
| --- | --- |
| Computation | 정해진 규칙에 따라 입력을 출력으로 바꾸는 과정 |
| Abstraction | 세부 구현을 감추고 필요한 인터페이스만 드러내는 방식 |
| Algorithm | 문제를 해결하기 위한 유한한 절차 |
| Complexity | 알고리즘이 사용하는 시간과 공간의 증가율 |
| Turing machine | 무엇이 계산 가능한지 정의하는 이론 모델 |

---

## Before / After: CS를 알기 전과 후

**Before — CS를 모를 때:**

```python
# 모든 쌍을 비교해 중복 찾기 — O(n²)
def find_duplicates(items):
    duplicates = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            if items[i] == items[j] and items[i] not in duplicates:
                duplicates.append(items[i])
    return duplicates
```

AI에게 "중복 찾는 함수 만들어줘"라고 하면 이런 코드가 나올 수도 있습니다. 데이터가 10만 개면 100억 번 비교가 일어납니다.

**After — CS를 알 때:**

```python
# set을 사용해 O(n)으로 해결
def find_duplicates(items):
    seen = set()
    duplicates = set()
    for item in items:
        if item in seen:
            duplicates.add(item)
        seen.add(item)
    return list(duplicates)
```

CS를 알면 AI에게 "O(n) 복잡도로 set을 써서 중복을 찾아줘"라고 정확하게 요청할 수 있습니다.

---

## 핵심 내용: 바이브코딩 관점에서 보는 CS

### 계산이란 무엇인가

계산의 본질은 "입력을 받아 규칙에 따라 출력을 만드는 것"입니다. 모든 프로그램은 이 구조를 따릅니다. AI에게 코드를 요청할 때도 입력, 처리 규칙, 출력을 명확히 설명하면 훨씬 좋은 코드를 받을 수 있습니다.

```python
# 가장 단순한 계산: input -> process -> output
def is_even(n: int) -> bool:
    return n % 2 == 0
```

### 추상화의 힘

추상화는 CS의 가장 중요한 도구입니다. 운영체제는 하드웨어를, 프로그래밍 언어는 기계어를, 함수는 구현 세부를 추상화합니다.

```python
# 구현 세부사항은 숨기고 interface만 노출
class Stack:
    def __init__(self) -> None:
        self._items: list[int] = []

    def push(self, item: int) -> None:
        self._items.append(item)

    def pop(self) -> int:
        return self._items.pop()

    def is_empty(self) -> bool:
        return len(self._items) == 0

# 사용자는 내부에 list가 있는지 알 필요 없음
stack = Stack()
stack.push(1)
stack.push(2)
print(stack.pop())  # 2
```

바이브코딩에서 추상화는 핵심입니다. AI에게 "어떤 자료구조를 쓸지"보다 "어떤 동작이 필요한지"를 말하면 AI가 최적 구현을 선택합니다.

### CS의 계층 구조

```python
cs_layers = {
    "Applications": ["AI", "Data science", "Web", "Mobile"],
    "Software": ["Software engineering", "Programming languages"],
    "Systems": ["Operating systems", "Networks", "Databases"],
    "Hardware": ["Computer architecture", "Digital logic"],
    "Theory": ["Algorithms", "Complexity theory", "Computation theory"],
}

for layer, subjects in cs_layers.items():
    print(f"[{layer}] {', '.join(subjects)}")
```

이 계층 구조를 이해하면 AI가 만든 코드에서 어느 층의 문제인지 빠르게 파악할 수 있습니다.

---

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| CS = 프로그래밍이라고 생각 | AI 코드의 품질을 평가하지 못함 | CS는 계산의 원리를 연구하는 학문입니다 |
| 이론 과목을 건너뜀 | AI에게 정확한 요구사항을 전달하지 못함 | 알고리즘과 자료구조는 모든 과목의 기초입니다 |
| 한 과목만 깊이 파고듦 | AI 코드의 문제를 다른 층에서 못 찾음 | 먼저 넓게 보고 필요한 곳을 깊이 학습합니다 |
| 수학을 완전히 회피 | AI 코드의 성능 분석이 불가능 | 이산수학과 확률은 CS의 필수 도구입니다 |
| 실습 없이 이론만 학습 | AI 코드를 실제로 검증하지 못함 | 코드로 구현하며 개념을 확인합니다 |

---

## AI 코딩 팁

바이브코딩에서 CS 기초를 활용하는 방법:

1. **추상화 수준을 명시하세요.** "리스트로 구현해줘"보다 "빠른 삽입 삭제가 필요한 자료구조로 구현해줘"가 더 좋은 결과를 냅니다.
2. **복잡도를 요구사항에 포함하세요.** "O(n log n) 이하로 정렬해줘"처럼 성능 요구사항을 명시하면 AI가 적합한 알고리즘을 선택합니다.
3. **AI 코드를 검토할 때 계층을 확인하세요.** 애플리케이션 로직에 시스템 코드가 섞이지 않았는지, 추상화가 적절한지 봅니다.

---

## 체크리스트

- [ ] 컴퓨터과학의 정의를 자신의 말로 설명할 수 있는가
- [ ] 추상화가 CS에서 왜 중요한지 이해했는가
- [ ] CS 주요 과목들의 계층 관계를 파악했는가
- [ ] 알고리즘 효율성이 왜 중요한지 체감했는가
- [ ] AI에게 CS 용어로 요구사항을 전달할 수 있는가

---

## 처음 질문으로 돌아가기

- **컴퓨터과학은 프로그래밍과 어떻게 다를까요?**
  프로그래밍은 도구 사용 기술, CS는 그 도구의 원리를 이해하는 학문입니다. AI에게 코드를 시키려면 원리를 알아야 올바른 코드를 판별할 수 있습니다.

- **왜 추상화가 CS의 가장 중요한 도구일까요?**
  복잡한 시스템을 관리 가능한 단위로 나누기 때문입니다. 바이브코딩에서도 어느 수준의 추상화로 AI에게 요청하느냐가 코드 품질을 좌우합니다.

- **알고리즘, 시스템, 응용은 어떤 계층 관계일까요?**
  이론 → 하드웨어 → 시스템 → 소프트웨어 → 응용의 순서로 쌓입니다. 아래 계층이 위 계층의 기반이 됩니다.

---

## 정리

컴퓨터과학은 계산의 원리, 한계, 응용을 연구하는 학문입니다. 추상화를 핵심 도구로 사용하며, 이론부터 응용까지 계층 구조로 연결됩니다. 바이브코딩 시대에도 CS 기초가 탄탄할수록 AI와 더 효과적으로 협업할 수 있습니다.

다음 글에서는 "계산이란 무엇인가"를 더 깊이 살펴보고, 프로그래밍 패러다임이 AI 코드 요청에 어떤 영향을 주는지 봅니다.

---

## 참고 자료

- [CS50 — Introduction to Computer Science (Harvard)](https://cs50.harvard.edu/)
- [Structure and Interpretation of Computer Programs (MIT)](https://mitpress.mit.edu/sites/default/files/sicp/full-text/book/book.html)
- [Computer Science Distilled — Wladston Ferreira Filho](https://code.energy/computer-science-distilled/)

---

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 컴퓨터 과학 기초 (1/10): Computer Science란 무엇인가? (현재 글)**
- 바이브코딩을 위한 컴퓨터 과학 기초 (2/10): 계산과 프로그램
- 바이브코딩을 위한 컴퓨터 과학 기초 (3/10): 데이터 표현
- 바이브코딩을 위한 컴퓨터 과학 기초 (4/10): 알고리즘과 복잡도
- 바이브코딩을 위한 컴퓨터 과학 기초 (5/10): 컴퓨터 구조
- 바이브코딩을 위한 컴퓨터 과학 기초 (6/10): 운영체제
- 바이브코딩을 위한 컴퓨터 과학 기초 (7/10): 네트워크
- 바이브코딩을 위한 컴퓨터 과학 기초 (8/10): 데이터베이스
- 바이브코딩을 위한 컴퓨터 과학 기초 (9/10): 소프트웨어 엔지니어링
- 바이브코딩을 위한 컴퓨터 과학 기초 (10/10): AI와 데이터사이언스까지의 연결
<!-- toc:end -->

Tags: 바이브코딩, Computer Science, 컴퓨터과학, CS 입문, 추상화, AI 코딩
