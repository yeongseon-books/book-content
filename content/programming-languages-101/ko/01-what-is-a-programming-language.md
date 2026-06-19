---
series: programming-languages-101
episode: 1
title: "Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - Programming Languages
  - 언어
  - 패러다임
  - 추상화
  - 표현력
seo_description: 프로그래밍 언어가 제공하는 추상화 계층과 명령형, 객체지향, 함수형, 선언형 패러다임의 핵심 차이를 코드 예시와 함께 정리합니다.
last_reviewed: '2026-05-15'
---

# Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가?

Python을 쓰다 보면 언어를 그냥 도구처럼 여기기 쉽습니다. 그런데 같은 문제를 어셈블리로 풀 때와 Python으로 풀 때는 코드 길이만 달라지는 것이 아닙니다. 문제를 쪼개는 방식, 이름을 붙이는 방식, 상태를 다루는 방식까지 함께 달라집니다.

이 글은 Programming Languages 101 시리즈의 첫 번째 글입니다.

이 글에서는 프로그래밍 언어를 단순한 문법 집합이 아니라, 사람이 문제를 표현하는 틀로 보겠습니다. 같은 계산을 여러 패러다임으로 풀어 보면서 언어가 무엇을 감추고 무엇을 드러내는지부터 잡아 두겠습니다.

![Programming Languages 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/programming-languages-101/01/01-01-concept-at-a-glance.ko.png)
*Programming Languages 101 1장 흐름 개요*

> 프로그래밍 언어는 '컴퓨터에 명령하는 도구'이기 전에 '사람이 사람에게 의도를 전달하는 도구'입니다 — 같은 동작을 하는 코드도 어떤 추상화 / 타입 / 제어 흐름을 제공하는지에 따라 읽는 사람의 머릿속에 그려지는 모델이 달라집니다.

## 이 글에서 다룰 문제

- 왜 우리는 기계어 대신 고급 언어를 사용할까요?
- 프로그래밍 언어는 정확히 어떤 추상화를 제공할까요?
- 같은 문제를 명령형, 객체지향, 함수형, 선언형으로 풀면 무엇이 달라질까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

언어를 기능 목록으로만 보면 새 언어를 만날 때마다 처음부터 다시 배워야 한다는 느낌을 받습니다. 반대로 변수, 표현식, 제어 흐름, 함수, 타입 같은 공통 구조를 먼저 잡아 두면 새 언어는 낯선 대상이 아니라 익숙한 개념의 다른 표현으로 보입니다. 이 시리즈는 그 공통 구조를 하나씩 분해하는 흐름으로 이어집니다.

## 먼저 알아둘 용어

- **구문**: 어떤 문자 배열이 합법인지 정하는 규칙입니다.
- **의미**: 그 구문이 실행될 때 실제로 무엇을 하게 되는지입니다.
- **패러다임**: 문제를 푸는 기본 관점입니다. 명령형, 객체지향, 함수형, 선언형이 대표적입니다.
- **추상화**: 세부 사항을 감추고 더 큰 단위로 생각하게 해 주는 장치입니다.
- **번역기**: 소스 코드를 기계가 실행할 다른 형태로 바꾸는 프로그램입니다.

## 추상화 계층: 기계어에서 고급 언어까지

위로 갈수록 사람이 읽기 쉽고, 아래로 갈수록 CPU가 직접 이해하는 표현에 가까워집니다.

```text
고급 언어 (Python, Go, Rust)
    |  — 컴파일러 / 인터프리터
    v
중간 표현 (바이트코드, IR)
    |  — 가상 머신 / 어셈블러
    v
어셈블리 (x86-64, ARM)
    |  — 어셈블러
    v
기계어 (0과 1의 나열)
    |
    v
CPU 실행
```

프로그래밍 언어는 이 층위 어디에 설지 정하고, 그 위에서 이름, 함수, 타입, 모듈 같은 추상화를 제공합니다. Python 한 줄이 어셈블리 수십 줄로 풀리는 이유도 이 추상화 덕분입니다.

## 먼저 보는 예시

### 추상화가 낮을 때

```asm
; x86-64 (simplified)
mov rax, 3
mov rbx, 4
add rax, rbx        ; rax = 7
```

여기서는 레지스터 이름과 명령어를 직접 다룹니다. 변수도 없고 함수도 없습니다. 계산 자체보다 계산을 어떻게 전달할지에 더 많은 주의를 써야 합니다.

### 추상화가 높을 때

```python
total = 3 + 4
print(total)  # 7
```

`total`이라는 이름이 생기고, `+`라는 익숙한 기호를 그대로 씁니다. 출력도 한 줄이면 충분합니다. 이것이 고급 언어가 주는 가장 현실적인 이점입니다. 기계 명령을 잊고 문제 구조에 집중하게 만든다는 사실입니다.

## 같은 문제를 네 가지 패러다임으로 풀기

정수 리스트에서 짝수만 골라 두 배로 만든 뒤 모두 더하는 문제를 보겠습니다.

### 1단계 — 명령형으로 풀기

```python
# 1_imperative.py
nums = [1, 2, 3, 4, 5, 6]
total = 0
for n in nums:
    if n % 2 == 0:
        total += n * 2
print(total)  # 24
```

루프와 변수로 계산 단계를 순서대로 적습니다. 가장 직접적이지만 단계가 길게 드러납니다.

### 2단계 — 객체지향으로 풀기

```python
# 2_oop.py
class EvenDoubler:
    def __init__(self, nums: list[int]) -> None:
        self.nums = nums

    def total(self) -> int:
        return sum(n * 2 for n in self.nums if n % 2 == 0)

print(EvenDoubler([1, 2, 3, 4, 5, 6]).total())  # 24
```

데이터와 동작을 한 객체 안에 묶었습니다. 작은 예제에서는 다소 무거워 보여도, 상태와 책임이 늘어나는 순간 이 장점이 바로 살아납니다.

### 3단계 — 함수형으로 풀기

```python
# 3_functional.py
from functools import reduce

nums = [1, 2, 3, 4, 5, 6]
result = reduce(
    lambda acc, n: acc + n * 2,
    filter(lambda n: n % 2 == 0, nums),
    0,
)
print(result)  # 24
```

데이터 흐름을 함수 조합으로 표현합니다. 값을 바꾸기보다 흘려보내는 쪽에 무게가 실립니다.

### 4단계 — 선언형으로 풀기

```python
# 4_declarative.py
import sqlite3
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE t (n INTEGER)")
db.executemany("INSERT INTO t VALUES (?)", [(i,) for i in [1,2,3,4,5,6]])
row = db.execute("SELECT SUM(n*2) FROM t WHERE n % 2 = 0").fetchone()
print(row[0])  # 24
```

여기서는 무엇을 원한다는 조건만 적고, 실제 실행 계획은 DBMS에 맡깁니다. 선언형의 핵심은 절차가 아니라 의도를 앞세운다는 사실입니다.

### 5단계 — 네 가지 해법 비교하기

네 코드는 모두 24를 계산하지만, 강조점이 다릅니다.

| 패러다임 | 강조점 | 특징 |
| --- | --- | --- |
| 명령형 | 절차 | 상태 변경 단계가 순서대로 드러남 |
| 객체지향 | 책임 | 데이터와 동작을 묶어 관리 |
| 함수형 | 데이터 흐름 | 값 변환의 파이프라인 |
| 선언형 | 의도 | 실행 계획을 시스템에 위임 |

중요한 질문은 어느 패러다임이 더 우월한가가 아니라, 어떤 문제와 어떤 팀에 더 자연스러운가입니다.

## 언어별 패러다임 지원 비교

같은 개념이 언어마다 어떻게 다르게 표현되는지 보면 패러다임의 감각이 빠르게 잡힙니다.

```python
# Python: 리스트 컴프리헨션 (함수형 + 명령형 혼합)
evens = [n * 2 for n in range(1, 7) if n % 2 == 0]
print(sum(evens))  # 24
```

```javascript
// JavaScript: 메서드 체이닝 (함수형 스타일)
const result = [1,2,3,4,5,6]
  .filter(n => n % 2 === 0)
  .map(n => n * 2)
  .reduce((acc, n) => acc + n, 0);
console.log(result);  // 24
```

```go
// Go: 명령형 (간결한 루프)
func evenDoubleSum(nums []int) int {
    total := 0
    for _, n := range nums {
        if n%2 == 0 {
            total += n * 2
        }
    }
    return total
}
```

```rust
// Rust: 이터레이터 체이닝 (함수형)
fn even_double_sum(nums: &[i32]) -> i32 {
    nums.iter()
        .filter(|&&n| n % 2 == 0)
        .map(|&n| n * 2)
        .sum()
}
```

Python과 JavaScript는 함수형을 자연스럽게 수용하지만, Go는 명령형을 기본으로 밀고, Rust는 이터레이터 체이닝으로 함수형을 표현합니다. 같은 결과를 향해 각 언어가 얼마나 다른 경로를 걷는지가 여기서 보입니다.

## 이 코드에서 먼저 볼 점

- 같은 결과도 패러다임에 따라 전혀 다른 모양의 코드가 됩니다.
- 한 언어가 하나의 패러다임만 강제하는 경우는 드뭅니다. Python처럼 여러 방식을 함께 지원하는 언어가 흔합니다.
- 언어를 고를 때는 속도만이 아니라 문제를 어떻게 표현하게 만드는지도 함께 봐야 합니다.

## 자주 하는 실수

| 실수 | 증상 | 올바른 접근 |
| --- | --- | --- |
| 언어를 기능 목록으로만 봄 | 같은 기능이 있어도 코드가 흘러가는 방식이 전혀 다른데 놓침 | 패러다임과 제어 흐름부터 파악 |
| 새 언어를 처음부터 배워야 한다는 생각 | 매번 과도한 학습 부담을 느낌 | 공통 구조(변수, 함수, 타입)를 먼저 연결 |
| 실행 속도만으로 언어 선택 | 실제 병목이 I/O나 알고리즘인데 언어 탓으로 돌림 | 프로파일링 후 병목 기준으로 선택 |
| 하나의 패러다임을 모든 문제에 적용 | 간단한 스크립트에 무거운 객체 구조를 씌우는 과설계 | 문제 성격에 맞는 가장 가벼운 표현 선택 |
| 추상화 수준을 잘못 고름 | 다섯 줄짜리 작업에 지나치게 무거운 도구 사용 | 팀이 유지보수할 수 있는 복잡도 기준으로 선택 |

## 실무에서는 이렇게 본다

현업에서는 한 회사가 하나의 언어만 쓰는 경우가 드뭅니다. 백엔드는 Python이나 Go, 프런트엔드는 JavaScript나 TypeScript, 데이터 쪽은 SQL과 Python, 시스템 쪽은 C나 Rust처럼 문제 영역에 따라 선택이 달라집니다. 언어를 고른다는 말은 사실 문제 영역에 맞는 추상화와 패러다임을 고른다는 뜻에 가깝습니다.

새 팀에 합류했을 때도 문법부터 외우기보다 그 팀이 어떤 패러다임을 선호하는지부터 보는 편이 빠릅니다. 코드 리뷰가 무엇을 칭찬하는지, 어떤 구조를 자연스럽다고 여기는지를 보면 언어의 성격이 훨씬 빨리 보입니다.

### 타입, 스코프, 메모리를 한 시야에서 보기

프로그래밍 언어를 실제로 운영 코드에 적용할 때는 문법 지식만으로 충분하지 않습니다. 타입 시스템이 어떤 오류를 언제 잡는지, 스코프 규칙이 상태 변경과 캡처를 어떻게 제한하는지, 메모리 모델이 동시성에서 어떤 가시성을 보장하는지를 한 묶음으로 이해해야 합니다.

다음은 입력 파싱 이후 비즈니스 계층으로 전달되는 값의 타입이 느슨할 때 생기는 대표적인 문제입니다.

```python
from typing import TypedDict, Literal

class PaymentCommand(TypedDict):
    order_id: str
    amount: int
    currency: Literal["KRW", "USD"]

def apply_discount(cmd: PaymentCommand) -> PaymentCommand:
    if cmd["currency"] == "KRW":
        cmd["amount"] = int(cmd["amount"] * 0.95)
    return cmd
```

핵심은 금액이 숫자라는 사실만으로 충분하지 않다는 점입니다. 정수인지, 소수점 정책이 무엇인지, 통화별 반올림 규칙이 무엇인지가 타입 설계에 반영되어야 합니다. 실무에서는 `int` 하나로 시작해 빠르게 배포한 뒤 정산 단계에서 누적 오차를 발견하는 일이 자주 발생합니다.

### 실전 시나리오: 입력 경계에서 도메인 객체로 변환하기

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class OrderEvent:
    event_id: str
    amount: int

def parse_event(raw: dict) -> OrderEvent:
    if "event_id" not in raw or "amount" not in raw:
        raise ValueError("missing required field")
    event_id = str(raw["event_id"]).strip()
    amount = int(raw["amount"])
    if amount < 0:
        raise ValueError("amount must be >= 0")
    return OrderEvent(event_id=event_id, amount=amount)
```

이 예시는 단순하지만 기준이 분명합니다. 입력을 받는 즉시 도메인 객체로 변환해 이후 단계의 가정을 안정화하고, `event_id`를 멱등 키로 사용해 중복 처리를 통제할 수 있습니다. 언어 기능 자체보다도, 타입 경계를 어디에서 확정하는지가 운영 안정성을 좌우합니다.

```text
$ python3
>>> from order_demo import parse_event
>>> parse_event({"event_id": "ev-1", "amount": "120"})
OrderEvent(event_id='ev-1', amount=120)
>>> parse_event({"event_id": "ev-2", "amount": -1})
ValueError: amount must be >= 0
```

## TypeScript로 보는 점진적 타입 도입

Python이 타입 힌트를 선택적으로 받아들이는 것처럼, TypeScript는 JavaScript 위에 정적 타입을 덧붙이는 방식으로 언어 설계의 점진적 도입을 보여 줍니다.

```typescript
// TypeScript: 점진적 타입 — 기존 JavaScript 생태계를 그대로 유지하면서 안전성 추가
function evenDoubleSum(nums: number[]): number {
    return nums
        .filter(n => n % 2 === 0)
        .map(n => n * 2)
        .reduce((acc, n) => acc + n, 0);
}

// 타입이 없어도 동작하지만, 타입이 있으면 오류를 조기에 잡음
const result: number = evenDoubleSum([1, 2, 3, 4, 5, 6]);
console.log(result);  // 24
```

TypeScript의 접근 방식은 "안전성을 강제하지 않고 선택하게 한다"는 점에서 설계 철학을 잘 보여 줍니다. 기존 JavaScript 코드는 수정 없이 TypeScript 프로젝트에 포함될 수 있고, 팀이 준비됐을 때 타입을 추가하면 됩니다.

## 언어를 고를 때 실제로 보는 것들

이론적인 패러다임 분류 외에, 현업에서 언어를 선택할 때 고려하는 현실적인 요인들도 있습니다.

| 고려 요인 | 내용 | 대표 사례 |
| --- | --- | --- |
| 생태계 | 필요한 라이브러리와 도구의 풍부함 | Python의 데이터 과학 생태계 |
| 학습 곡선 | 팀이 익숙해지는 데 필요한 시간 | Go의 낮은 학습 곡선 |
| 배포 단순성 | 바이너리 하나로 배포 가능한가 | Go, Rust의 단일 바이너리 |
| 커뮤니티 활동성 | 오류를 만났을 때 도움을 구할 수 있는가 | Stack Overflow 답변 수 |
| 타입 시스템 강도 | 얼마나 일찍 오류를 잡아 주는가 | Rust > TypeScript > Python |
| 런타임 성능 | 지연 시간과 처리량 요구사항 | Rust/C++ > Go/Java > Python |

이 표의 어떤 행도 단독으로 언어를 결정하지 않습니다. 팀의 현재 상황, 프로젝트 수명, 성능 요구사항, 채용 환경이 모두 조합돼 최종 선택을 만듭니다.

## 운영 체크리스트

- [ ] 고급 언어에서 기계어까지 내려가는 추상화 계층을 한 문장으로 설명할 수 있는가?
- [ ] 명령형, 객체지향, 함수형, 선언형이 각각 무엇을 강조하는지 구분할 수 있는가?
- [ ] 같은 문제를 두 가지 이상 방식으로 풀어 본 적이 있는가?
- [ ] 새 언어를 배울 때 공통 구조부터 잡는 습관이 있는가?
- [ ] "어느 언어가 최고인가" 대신 "어느 언어가 이 문제에 맞는가"를 묻는가?

## 연습 문제

1. 가장 자주 쓰는 언어 하나를 골라, 그 언어가 어떤 패러다임을 특히 밀어 주는지 한 단락으로 정리해 보세요.
2. 위 네 가지 해법 가운데 가장 빠를 것 같은 것을 고르고, 그렇게 생각한 이유를 적어 보세요.
3. 선언형이 항상 최선이 아닌 상황을 두 가지 적어 보세요.

## 정리

프로그래밍 언어는 기계에 명령을 내리는 문법인 동시에, 사람이 문제를 구조화하는 틀입니다. 같은 계산도 패러다임에 따라 전혀 다른 코드가 되고, 그 차이가 팀의 설계 감각과 유지보수 방식까지 바꿉니다.

## 처음 질문으로 돌아가기

- **왜 우리는 기계어 대신 고급 언어를 사용할까요?**
  - 고급 언어는 기계 명령을 감추고 이름, 함수, 타입이라는 추상화를 제공합니다. 같은 계산이 어셈블리로는 수십 줄이 될 일이 Python 한 줄로 줄어드는 이유가 바로 이 추상화 덕분입니다.
- **프로그래밍 언어는 정확히 어떤 추상화를 제공할까요?**
  - 변수(이름-값 연결), 함수(행동 단위), 타입(값의 성질 제약), 모듈(코드 경계)이 핵심 추상화입니다. 언어마다 이 중 어느 것을 더 강하게 표현하는지가 설계 성격을 결정합니다.
- **같은 문제를 명령형, 객체지향, 함수형, 선언형으로 풀면 무엇이 달라질까요?**
  - 결과는 같아도 강조점이 다릅니다. 명령형은 절차, 객체지향은 책임, 함수형은 데이터 흐름, 선언형은 의도를 앞세웁니다. 이 감각이 언어를 고르는 기준이 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- **Programming Languages 101 (1/10): 프로그래밍 언어란 무엇인가? (현재 글)**
- [Programming Languages 101 (2/10): 구문과 의미](./02-syntax-and-semantics.md)
- [Programming Languages 101 (3/10): 타입 시스템](./03-type-system.md)
- [Programming Languages 101 (4/10): 스코프와 바인딩](./04-scope-and-binding.md)
- [Programming Languages 101 (5/10): 함수와 클로저](./05-functions-and-closures.md)
- [Programming Languages 101 (6/10): 객체와 프로토타입](./06-objects-and-prototypes.md)
- [Programming Languages 101 (7/10): 메모리 관리](./07-memory-management.md)
- [Programming Languages 101 (8/10): 인터프리터와 컴파일러](./08-interpreter-and-compiler.md)
- [Programming Languages 101 (9/10): 정적 언어와 동적 언어](./09-static-vs-dynamic.md)
- [Programming Languages 101 (10/10): 좋은 언어 설계란 무엇인가?](./10-what-makes-good-language-design.md)

<!-- toc:end -->

## 참고 자료

- [Programming Language Pragmatics (Scott)](https://www.elsevier.com/books/programming-language-pragmatics/scott/978-0-12-410409-9)
- [Structure and Interpretation of Computer Programs](https://mitpress.mit.edu/sites/default/files/sicp/index.html)
- [Concepts, Techniques, and Models of Computer Programming](https://www.info.ucl.ac.be/~pvr/book.html)
- [Python Documentation — The Python Tutorial](https://docs.python.org/3/tutorial/)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, 언어, 패러다임, 추상화, 표현력
