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

## 먼저 던지는 질문

- 왜 우리는 기계어 대신 고급 언어를 사용할까요?
- 프로그래밍 언어는 정확히 어떤 추상화를 제공할까요?
- 같은 문제를 명령형, 객체지향, 함수형, 선언형으로 풀면 무엇이 달라질까요?

## 왜 중요한가

언어를 기능 목록으로만 보면 새 언어를 만날 때마다 처음부터 다시 배워야 한다는 느낌을 받습니다. 반대로 변수, 표현식, 제어 흐름, 함수, 타입 같은 공통 구조를 먼저 잡아 두면 새 언어는 낯선 대상이 아니라 익숙한 개념의 다른 표현으로 보입니다. 이 시리즈는 그 공통 구조를 하나씩 분해하는 흐름으로 이어집니다.

## 핵심 개념 한눈에 보기

위로 갈수록 사람이 읽기 쉽고, 아래로 갈수록 CPU가 직접 이해하는 표현에 가까워집니다. 프로그래밍 언어는 이 층위 어디에 설지 정하고, 그 위에서 이름, 함수, 타입, 모듈 같은 추상화를 제공합니다. Python 한 줄이 어셈블리 수십 줄로 풀리는 이유도 이 추상화 덕분입니다.

## 먼저 알아둘 용어

- 구문: 어떤 문자 배열이 합법인지 정하는 규칙입니다.
- 의미: 그 구문이 실행될 때 실제로 무엇을 하게 되는지입니다.
- 패러다임: 문제를 푸는 기본 관점입니다. 명령형, 객체지향, 함수형, 선언형이 대표적입니다.
- 추상화: 세부 사항을 감추고 더 큰 단위로 생각하게 해 주는 장치입니다.
- 번역기: 소스 코드를 기계가 실행할 다른 형태로 바꾸는 프로그램입니다.

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

`total`이라는 이름이 생기고, `+`라는 익숙한 기호를 그대로 씁니다. 출력도 한 줄이면 충분합니다. 이것이 고급 언어가 주는 가장 현실적인 이점입니다. 기계 명령을 잊고 문제 구조에 집중하게 만든다는 점입니다.

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

여기서는 무엇을 원한다는 조건만 적고, 실제 실행 계획은 DBMS에 맡깁니다. 선언형의 핵심은 절차가 아니라 의도를 앞세운다는 점입니다.

### 5단계 — 네 가지 해법 비교하기

네 코드는 모두 24를 계산하지만, 강조점이 다릅니다. 명령형은 절차를, 객체지향은 책임을, 함수형은 데이터 흐름을, 선언형은 의도를 앞세웁니다. 중요한 질문은 어느 패러다임이 더 우월한가가 아니라, 어떤 문제와 어떤 팀에 더 자연스러운가입니다.

## 이 코드에서 먼저 볼 점

- 같은 결과도 패러다임에 따라 전혀 다른 모양의 코드가 됩니다.
- 한 언어가 하나의 패러다임만 강제하는 경우는 드뭅니다. Python처럼 여러 방식을 함께 지원하는 언어가 흔합니다.
- 언어를 고를 때는 속도만이 아니라 문제를 어떻게 표현하게 만드는지도 함께 봐야 합니다.

## 자주 하는 실수

1. 언어를 기능 목록으로만 봅니다. 같은 기능이 있어도 코드가 흘러가는 방식은 크게 다를 수 있습니다.
2. 새 언어를 만날 때마다 모든 것을 처음부터 다시 배워야 한다고 생각합니다. 공통 구조를 먼저 잡으면 부담이 줄어듭니다.
3. 언어 선택을 실행 속도 하나로만 결정합니다. 실제 병목은 I/O나 알고리즘인 경우가 많습니다.
4. 하나의 패러다임을 모든 문제에 밀어 넣습니다. 간단한 스크립트에 무거운 객체 구조를 씌우는 식의 과설계가 흔합니다.
5. 추상화 수준을 잘못 고릅니다. 다섯 줄짜리 작업에 지나치게 무거운 도구를 고르면 생산성이 떨어집니다.

## 실무에서는 이렇게 본다

현업에서는 한 회사가 하나의 언어만 쓰는 경우가 드뭅니다. 백엔드는 Python이나 Go, 프런트엔드는 JavaScript나 TypeScript, 데이터 쪽은 SQL과 Python, 시스템 쪽은 C나 Rust처럼 문제 영역에 따라 선택이 달라집니다. 언어를 고른다는 말은 사실 문제 영역에 맞는 추상화와 패러다임을 고른다는 뜻에 가깝습니다.

새 팀에 합류했을 때도 문법부터 외우기보다 그 팀이 어떤 패러다임을 선호하는지부터 보는 편이 빠릅니다. 코드 리뷰가 무엇을 칭찬하는지, 어떤 구조를 자연스럽다고 여기는지를 보면 언어의 성격이 훨씬 빨리 보입니다.

## 체크리스트

- [ ] 고급 언어에서 기계어까지 내려가는 추상화 계층을 한 문장으로 설명할 수 있는가?
- [ ] 명령형, 객체지향, 함수형, 선언형이 각각 무엇을 강조하는지 구분할 수 있는가?
- [ ] 같은 문제를 두 가지 이상 방식으로 풀어 본 적이 있는가?
- [ ] 새 언어를 배울 때 공통 구조부터 잡는 습관이 있는가?
- [ ] “어느 언어가 최고인가” 대신 “어느 언어가 이 문제에 맞는가”를 묻는가?

## 연습 문제

1. 가장 자주 쓰는 언어 하나를 골라, 그 언어가 어떤 패러다임을 특히 밀어 주는지 한 단락으로 정리해 보세요.
2. 위 네 가지 해법 가운데 가장 빠를 것 같은 것을 고르고, 그렇게 생각한 이유를 적어 보세요.
3. 선언형이 항상 최선이 아닌 상황을 두 가지 적어 보세요.

## 정리

프로그래밍 언어는 기계에 명령을 내리는 문법인 동시에, 사람이 문제를 구조화하는 틀입니다. 같은 계산도 패러다임에 따라 전혀 다른 코드가 되고, 그 차이가 팀의 설계 감각과 유지보수 방식까지 바꿉니다. 다음 글에서는 모든 언어의 두 축인 구문과 의미를 분리해서 보겠습니다.

## 심화 실전 노트: 타입, 스코프, 메모리 모델을 한 번에 연결하기

프로그래밍 언어를 실제로 운영 코드에 적용할 때는 문법 지식만으로 충분하지 않습니다. 타입 시스템이 어떤 오류를 언제 잡는지, 스코프 규칙이 상태 변경과 캡처를 어떻게 제한하는지, 메모리 모델이 동시성에서 어떤 가시성을 보장하는지를 한 묶음으로 이해해야 합니다. 이 세 축은 각각 독립 주제가 아니라, 코드 리뷰에서 같은 결함을 다른 이름으로 반복해서 만나게 만드는 공통 원인입니다.

### 타입 시스템 관점에서 보는 실패 패턴

다음 예시는 입력 파싱 이후 비즈니스 계층으로 전달되는 값의 타입이 느슨할 때 생기는 대표적인 문제를 보여줍니다.

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

핵심은 금액이 숫자라는 사실만으로 충분하지 않다는 점입니다. 정수인지, 소수점 정책이 무엇인지, 통화별 반올림 규칙이 무엇인지가 타입 설계에 반영되어야 합니다. 실무에서는 `int` 하나로 시작해 빠르게 배포한 뒤 정산 단계에서 누적 오차를 발견하는 일이 자주 발생합니다. 따라서 도메인 타입을 좁히는 전략이 필요합니다. 예를 들어 금액을 `Money` 값 객체로 감싸고, 생성 시점에 통화와 스케일을 강제하면 연산 단계를 통과하는 데이터 품질이 크게 올라갑니다.

### 스코프와 클로저를 리뷰할 때 보는 체크 포인트

클로저 자체는 강력한 도구이지만, 루프 변수 캡처와 가변 상태 결합이 만나면 예상과 다른 동작이 나옵니다.

```python
def make_handlers() -> list:
    handlers = []
    for i in range(3):
        handlers.append(lambda: i)
    return handlers

print([h() for h in make_handlers()])  # [2, 2, 2]
```

위 코드는 각 단계의 `i`를 복사하지 않고 같은 이름 해석 지점을 참조합니다. 의도한 결과가 `[0, 1, 2]`라면 기본 인자로 값을 고정해야 합니다.

```python
def make_handlers() -> list:
    handlers = []
    for i in range(3):
        handlers.append(lambda i=i: i)
    return handlers
```

이 차이는 단순 문법 이슈가 아니라 스코프 체계의 본질입니다. 변수의 "값"을 캡처하는지, "이름 해석 규칙"을 캡처하는지 구분하지 못하면 비동기 콜백, 이벤트 핸들러, 지연 실행 코드에서 재현 어려운 버그가 생깁니다.

### 메모리 모델을 읽는 최소 다이어그램

동시성 코드를 검토할 때는 아래처럼 책임 경계를 먼저 그려 두면 문제 재현과 해결 속도가 빨라집니다.

```text
[Thread A] write shared_flag=True
      |
      |  (reorder 가능성, 캐시 지연)
      v
[Memory Visibility Boundary]
      |
      v
[Thread B] read shared_flag
```

언어와 런타임은 이 경계에서 서로 다른 규칙을 제공합니다. 어떤 언어는 메모리 장벽이나 원자 연산을 명시적으로 요구하고, 어떤 언어는 메시지 전달 모델로 공유 메모리 자체를 줄입니다. 따라서 "동작한다"는 테스트 한 번으로 안전성을 결론 내리면 안 됩니다. 스레드 스케줄이 바뀌어도 같은 결과가 유지되는지, happens-before 관계가 코드 구조에 드러나는지 확인해야 합니다.

### 통합 적용 예시: 타입 + 스코프 + 메모리

작은 작업 큐 소비자를 예로 들면, 메시지 스키마를 엄격히 정의하고, 핸들러 생성 시 캡처 대상을 고정하고, 상태 공유를 최소화하는 세 가지를 함께 적용해야 안정성이 올라갑니다. 이 세 가지 중 하나만 빠져도 나머지 두 가지가 문제를 완전히 막아주지 못합니다. 결국 좋은 언어 사용 습관은 "문법 숙련"보다 "오류를 설계 단계에서 조기 차단하는 구조"에 가깝습니다.

### 추가 사례: 언어 설계 선택이 유지보수 비용에 미치는 영향

실무에서 타입, 스코프, 메모리 모델은 장애 보고서에서 따로 등장하지 않고 함께 엮여 나타납니다. 예를 들어 이벤트 소비자가 `dict[str, Any]`를 그대로 전달하면 타입 경계가 무너지고, 지연 실행 콜백이 외부 가변 상태를 캡처하면 스코프 결함이 생기며, 여러 워커가 같은 캐시 객체를 잠금 없이 접근하면 메모리 가시성 문제가 겹칩니다. 이런 결함은 단위 테스트 한두 개로는 쉽게 드러나지 않습니다.

그래서 언어 기능 선택을 할 때는 "지금 빨리 쓰기 쉬운가"보다 "오류를 조기에 막는가"를 기준으로 삼아야 합니다. 타입 힌트를 강제하고, 클로저 캡처 규칙을 리뷰 체크리스트에 넣고, 공유 상태 대신 메시지 전달을 우선하면 코드가 길어지더라도 운영 리스크가 크게 줄어듭니다. 결과적으로 좋은 설계는 문법의 화려함이 아니라, 팀이 반복 실수 없이 같은 문제를 안정적으로 푸는 능력으로 측정됩니다.

### 보강 메모: 리뷰에서 바로 쓰는 질문

이 코드는 타입 오류를 실행 전에 막는가, 클로저 캡처가 의도한 값 기준으로 고정되는가, 공유 상태 접근이 동시성 규칙을 만족하는가를 한 번에 점검해야 합니다. 세 질문 중 하나라도 답하지 못하면 기능이 맞아도 운영 위험이 남습니다.

언어 선택은 생산성 취향이 아니라 오류 모델 선택입니다. 팀이 자주 겪는 실패 유형을 먼저 정의하고 그 실패를 가장 빨리 드러내는 언어 기능을 고르는 방식이 실무에서 가장 안전합니다.


## 실무 앵커: 개념을 코드와 런타임으로 고정하기

이 장에서 다룬 개념을 실무에서 재사용하려면, 문장 설명을 코드와 실행 흔적으로 고정해야 합니다. 아래 예시는 같은 문제를 여러 언어와 실행 맥락으로 비교해 개념 경계를 분명히 만드는 목적입니다.

### 언어 비교 코드: Python, JavaScript, Go, Rust

동일한 입력에서 짝수 값만 두 배로 만들고 합계를 계산하는 예시입니다. 핵심은 문법 차이가 아니라, 오류를 어디서 얼마나 일찍 막는지입니다.

```python
def sum_even_doubled(nums: list[int]) -> int:
    return sum(n * 2 for n in nums if n % 2 == 0)

print(sum_even_doubled([1, 2, 3, 4, 5, 6]))  # 24
```

```javascript
function sumEvenDoubled(nums) {
  return nums.filter((n) => n % 2 === 0).map((n) => n * 2).reduce((a, b) => a + b, 0);
}

console.log(sumEvenDoubled([1, 2, 3, 4, 5, 6])); // 24
```

```go
package main

import "fmt"

func sumEvenDoubled(nums []int) int {
    total := 0
    for _, n := range nums {
        if n%2 == 0 {
            total += n * 2
        }
    }
    return total
}

func main() {
    fmt.Println(sumEvenDoubled([]int{1, 2, 3, 4, 5, 6})) // 24
}
```

```rust
fn sum_even_doubled(nums: &[i32]) -> i32 {
    nums.iter()
        .filter(|n| *n % 2 == 0)
        .map(|n| n * 2)
        .sum()
}

fn main() {
    println!("{}", sum_even_doubled(&[1, 2, 3, 4, 5, 6])); // 24
}
```

네 언어 모두 같은 답을 내지만, 타입 선언 강도, 표준 라이브러리 관용구, 에러 처리 문화가 다릅니다. 팀 기준을 세울 때는 성능 벤치마크보다 먼저, 리뷰 단계에서 실수를 드러내는 신호가 충분한지 확인하는 편이 안전합니다.

### 타입 시스템 앵커: 실패를 어디서 잡는가

아래 상황은 실무에서 자주 발생합니다. 문자열 숫자와 정수 숫자가 섞여 들어올 때, 파이프라인 초입에서 명시적으로 정규화하지 않으면 나중 단계에서 장애가 커집니다.

```python
from typing import Iterable

def normalize(values: Iterable[str]) -> list[int]:
    result: list[int] = []
    for v in values:
        result.append(int(v))
    return result

print(normalize(["1", "2", "3"]))
```

```typescript
function normalize(values: string[]): number[] {
  return values.map((v) => Number.parseInt(v, 10));
}

console.log(normalize(["1", "2", "3"]));
```

정적 타입 언어에서는 함수 경계에서 계약을 강하게 걸 수 있고, 동적 타입 언어에서는 런타임 검증 코드를 명시적으로 두는 습관이 중요합니다. 결론은 어느 쪽이 우월하냐가 아니라, 실패 지점을 팀이 의도적으로 앞당겼는가입니다.

### 메모리 모델 다이어그램: 공유 상태의 책임 경계

```text
[Producer Goroutine/Thread]
  write task -> queue
       |
       | happens-before 보장 지점
       v
[Queue Synchronization Boundary]
       |
       v
[Consumer Goroutine/Thread]
  read task -> process
```

동시성 결함 대부분은 계산 로직보다 경계 정의가 흐릴 때 생깁니다. 어떤 자료구조가 동기화 책임을 가지는지, 어느 호출 지점에서 메모리 가시성이 확보되는지를 코드 리뷰 항목으로 고정해야 재현 어려운 버그를 줄일 수 있습니다.

### 간단 파서 구현 앵커: 구문과 의미를 분리하기

토큰 배열을 받아 산술식 `NUM (+ NUM)*`를 계산하는 최소 파서 예시입니다.

```python
def parse_addition(tokens: list[str]) -> int:
    if not tokens:
        raise ValueError("empty")
    total = int(tokens[0])
    i = 1
    while i < len(tokens):
        op = tokens[i]
        rhs = int(tokens[i + 1])
        if op != "+":
            raise ValueError(f"unexpected operator: {op}")
        total += rhs
        i += 2
    return total

print(parse_addition(["10", "+", "20", "+", "7"]))  # 37
```

이 구조의 핵심은 두 단계 분리입니다. 먼저 구문 오류를 검사하고, 그다음 의미 계산을 수행합니다. 이 원칙을 지키면 오류 메시지가 명확해지고, 연산자 우선순위나 괄호 지원 같은 확장을 추가하기 쉬워집니다.

### REPL 세션 앵커: 실행 관찰 습관

```text
$ python3
>>> from demo import parse_addition
>>> parse_addition(["2", "+", "3"])
5
>>> parse_addition(["2", "*", "3"])
Traceback (most recent call last):
  ...
ValueError: unexpected operator: *
```

REPL은 작은 단위 가설을 빠르게 검증하는 도구입니다. 문서로 정리한 개념과 실제 런타임 동작이 어긋나지 않는지 확인할 때, 테스트 코드 작성 전 첫 관찰 지점으로 활용하면 품질이 안정적으로 올라갑니다.

### 적용 체크리스트

- 입력 경계에서 타입과 형식을 정규화했는가
- 공유 상태보다 메시지 경계가 먼저 보이도록 설계했는가
- 파서/검증/실행 단계를 분리해 오류 원인을 즉시 설명할 수 있는가
- REPL 또는 단위 테스트로 실패 사례를 먼저 고정했는가

이 체크리스트는 특정 언어 문법보다 오래 갑니다. 새 언어를 배우더라도 같은 질문으로 코드를 점검하면, 기능 개발 속도를 유지하면서도 운영 안정성을 함께 끌어올릴 수 있습니다.


## 실전 시나리오: 장애를 줄이는 언어 설계 점검

현업에서 언어 개념을 배울 때 가장 빠른 방법은 장애 시나리오를 기준으로 역추적하는 것입니다. 아래는 주문 이벤트 처리 파이프라인을 가정한 점검 예시입니다. 핵심은 기능 구현보다 경계 확인입니다.

```text
입력(JSON) -> 역직렬화 -> 타입 검증 -> 규칙 실행 -> 상태 반영 -> 로그/메트릭
```

각 단계에서 질문을 고정하면 품질이 크게 올라갑니다. 역직렬화 단계에서는 필수 필드 누락을 즉시 중단하는가, 타입 검증 단계에서는 문자열/숫자 혼합을 허용하지 않는가, 규칙 실행 단계에서는 부수효과를 최소화했는가, 상태 반영 단계에서는 재시도 시 멱등성이 보장되는가를 확인해야 합니다.

### 미니 구현: 입력 검증과 멱등 키

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

### REPL 확인

```text
$ python3
>>> from order_demo import parse_event
>>> parse_event({"event_id": "ev-1", "amount": "120"})
OrderEvent(event_id='ev-1', amount=120)
>>> parse_event({"event_id": "ev-2", "amount": -1})
Traceback (most recent call last):
  ...
ValueError: amount must be >= 0
```

짧은 REPL 검증을 반복하면 설계 문서의 문장이 실제 런타임에서 유지되는지 빠르게 확인할 수 있습니다. 이 습관이 쌓이면 언어를 바꿔도 문제 분석 속도와 리뷰 품질이 함께 유지됩니다.

## 처음 질문으로 돌아가기

- **왜 우리는 기계어 대신 고급 언어를 사용할까요?**
  - 본문의 기준은 프로그래밍 언어란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **프로그래밍 언어는 정확히 어떤 추상화를 제공할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **같은 문제를 명령형, 객체지향, 함수형, 선언형으로 풀면 무엇이 달라질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **프로그래밍 언어란 무엇인가? (현재 글)**
- 구문과 의미 (예정)
- 타입 시스템 (예정)
- 스코프와 바인딩 (예정)
- 함수와 클로저 (예정)
- 객체와 프로토타입 (예정)
- 메모리 관리 (예정)
- 인터프리터와 컴파일러 (예정)
- 정적 언어와 동적 언어 (예정)
- 좋은 언어 설계란 무엇인가? (예정)

<!-- toc:end -->

## 참고 자료

- [Programming Language Pragmatics (Scott)](https://www.elsevier.com/books/programming-language-pragmatics/scott/978-0-12-410409-9)
- [Structure and Interpretation of Computer Programs](https://mitpress.mit.edu/sites/default/files/sicp/index.html)
- [Concepts, Techniques, and Models of Computer Programming](https://www.info.ucl.ac.be/~pvr/book.html)
- [Python Documentation — The Python Tutorial](https://docs.python.org/3/tutorial/)

- [Programming Languages 101 실습 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/programming-languages-101/ko)

Tags: Computer Science, Programming Languages, 언어, 패러다임, 추상화, 표현력
