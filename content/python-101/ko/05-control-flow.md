---
title: "Python 101 (5/10): 제어 흐름: if, for, while, comprehension"
series: python-101
episode: 5
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- control-flow
- if-statement
- for-loop
- while-loop
- comprehensions
- enumerate-zip
last_reviewed: '2026-05-12'
seo_description: 제어 흐름을 짤 때는 "이 분기·반복이 무엇을 결정하느냐"를 truthy/falsy 한 단계와 종료 조건 한 단계로
  분리해 두면…
---

# Python 101 (5/10): 제어 흐름: if, for, while, comprehension

제어 흐름은 각 분기와 반복이 무엇을 결정하는지, 그리고 언제 끝나는지로 나눠 보면 훨씬 선명해집니다. truthy와 falsy, 종료 조건을 함께 보면 if와 loop가 한꺼번에 정리됩니다.

이 글은 Python 101 시리즈의 다섯 번째 글입니다.

## 먼저 던지는 질문

- 제어 흐름: if, for, while, comprehension를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?
- 제어 흐름: if, for, while, comprehension에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?
- 제어 흐름: if, for, while, comprehension를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?

## 큰 그림

![Python 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-101/05/05-01-mental-model.ko.png)

*Python 101 5장 흐름 개요*

이 그림에서는 제어 흐름: if, for, while, comprehension를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 제어 흐름: if, for, while, comprehension의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 멘탈 모델

> 제어 흐름을 짤 때는 "이 분기·반복이 무엇을 결정하느냐"를 truthy/falsy 한 단계와 종료 조건 한 단계로 분리해 두면, 컴프리헨션과 일반 루프 사이의 선택도 같은 잣대로 답이 나옵니다.
분기와 루프를 아래와 같이 한 장에 펼쳐 두면 코드를 읽을 때 다음 단계가 무엇인지 머릿속에 빠르게 떠오릅니다.

세 가지 핵심 규칙입니다.

1. **결정이 1회면 `if`, 같은 일을 반복하면 루프**입니다. `for`와 `while`은 같은 일을 반복하기 위한 두 가지 도구이며, 선택 기준은 "이미 순회할 대상이 있는가"입니다.
2. **순회할 대상(이터러블)이 있으면 `for`**가 자연스럽습니다. 길이가 없거나 조건이 만족될 때까지 돌아야 한다면 `while`을 씁니다. 이 경계가 흐려지면 무한 루프와 off-by-one이 늘어납니다.
3. **comprehension은 "입력 이터러블을 새 컬렉션으로 변환"하는 한정된 목적**의 표현식입니다. 부수효과(파일 쓰기, print, 외부 상태 변경)가 끼어드는 순간 일반 `for` 본문이 더 읽기 좋습니다.

이 규칙은 이후 모든 절의 기준이 됩니다.

*제어 흐름 결정 트리: 두 질문으로 if/for/while/comprehension 네 가지가 갈립니다.*

## 핵심 개념

### 1. truthy와 falsy

Python의 `if`는 조건을 `bool()`로 한 번 감싸 평가한다고 생각하면 됩니다. 다음 값들은 모두 falsy입니다.

- `False`, `None`
- 숫자형의 0: `0`, `0.0`, `0j`, `Decimal(0)`, `Fraction(0)`
- 빈 시퀀스/컬렉션: `""`, `b""`, `()`, `[]`, `{}`, `set()`, `range(0)`

그 외는 모두 truthy입니다. 이 규칙 덕분에 빈 리스트인지 검사할 때 `if not items:`처럼 짧게 쓸 수 있습니다. 다만 "값이 0이어도 처리해야 하는 경우"에는 truthy 검사로는 부족합니다. 예를 들어 사용자가 명시적으로 `0`을 입력했는지 확인하려면 `if value is None:` 또는 `if value == 0:`처럼 의도를 분명히 적습니다.

### 2. `if` / `elif` / `else`

분기 사다리는 짧을수록 읽기 쉽습니다. 같은 변수에 대해 가지를 늘리는 패턴이 반복된다면 dict 매핑이나 함수 디스패치로 평탄화할지 한 번 점검합니다.

```python
def label(score: int) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    else:
        return "F"
```

`elif`는 "위 조건이 모두 거짓일 때만" 평가됩니다. 그래서 위에서 아래로 읽었을 때 조건이 점점 좁아지도록 정렬하는 편이 안전합니다.

### 3. `for`와 이터러블

`for`는 "이터러블을 한 번씩 꺼내 변수에 묶고 본문을 실행"합니다. 따라서 `range`, `list`, `tuple`, `set`, `dict`, 파일 객체, 제너레이터처럼 한 원소씩 내놓을 수 있는 모든 것이 대상이 됩니다.

```python
for item in ["ada", "bob", "carol"]:
    print(item)

for i in range(3):
    print(i)

for ch in "hi":
    print(ch)
```

`enumerate`, `zip`, `range`는 `for`의 표현력을 크게 끌어올립니다.

```python
names = ["ada", "bob", "carol"]
roles = ["engineer", "designer", "engineer"]

for idx, name in enumerate(names, start=1):
    print(idx, name)

for name, role in zip(names, roles):
    print(name, "->", role)
```

`enumerate`는 인덱스가 필요한 경우, `zip`은 두 개 이상의 시퀀스를 짝지어 돌고 싶은 경우에 씁니다. `zip`은 가장 짧은 시퀀스에 맞춰 멈춥니다. 길이가 다른 입력을 잡고 싶다면 `zip(..., strict=True)`를 사용해 의도를 명시합니다.

### 4. `while`과 탈출 조건

`while`은 "조건이 truthy인 동안 본문을 반복"합니다. 본문이 조건에 영향을 주는 어떤 변화를 만들지 못하면 무한 루프가 됩니다.

```python
remaining = 5
while remaining > 0:
    print("tick", remaining)
    remaining -= 1
```

명시적 종료 시점이 없는 작업, 예를 들어 사용자 입력을 받거나, 외부 큐에서 메시지를 빼오는 루프는 `while True` + `break` 조합이 더 읽기 좋습니다.

```python
while True:
    line = input("> ").strip()
    if line in {"quit", "exit"}:
        break
    print("echo:", line)
```

### 5. `break`, `continue`, 그리고 `for`-`else`

- `break`은 가장 안쪽 루프를 즉시 끝냅니다.
- `continue`는 본문의 나머지를 건너뛰고 다음 반복으로 넘어갑니다.
- 루프에 붙은 `else`는 "루프가 `break` 없이 끝났을 때만" 실행됩니다. 검색 패턴에서 가끔 유용하지만 가독성을 해친다면 `found = False` 플래그가 더 분명합니다.

```python
for n in [4, 6, 8, 9]:
    if n % 2 == 1:
        print("found odd:", n)
        break
else:
    print("no odd found")
```

### 6. comprehension

list/dict/set comprehension은 "입력 이터러블을 한 번에 새 컬렉션으로 변환"하는 표현식입니다.

```python
squares = [x * x for x in range(5)]
positives = [x for x in [-1, 2, -3, 4] if x > 0]
by_role = {name: role for name, role in zip(names, roles)}
unique_words = {w.lower() for w in "Hello hello world".split()}
```

조건도 붙일 수 있고, 두 단계로 중첩할 수도 있습니다. 다만 두 단계까지가 한계입니다. 그 이상이면 일반 `for`로 풀어 쓰는 편이 사람과 도구 모두에게 친절합니다.

generator expression(`(x * x for x in range(5))`)은 같은 문법을 메모리에 한꺼번에 들이지 않고 평가합니다. 큰 입력을 한 번에 합산하거나(`sum(x * x for x in range(10**6))`) 다음 한 개만 필요한 상황에 적합합니다.

## 전후 비교

같은 작업을 "장황한 루프" → "Pythonic 루프"로 다시 써 봅니다. 입력은 학생 점수 리스트와 이름 리스트입니다.

**Before — C 스타일 루프**

```python
names = ["ada", "bob", "carol", "dan"]
scores = [92, 71, 85, 58]

i = 0
result = []
while i < len(names):
    name = names[i]
    score = scores[i]
    if score >= 60:
        result.append(name + ":" + str(score))
    i += 1
print(result)
```

읽을 때 (a) 인덱스를 직접 굴리고, (b) 같은 인덱스를 두 번 사용해 양쪽 리스트를 따라가고, (c) 조건을 본문 안에서 다루고, (d) 누적 리스트를 별도 변수로 만든다는 네 단계를 각각 따라가야 합니다.

**After — `zip` + comprehension**

```python
names = ["ada", "bob", "carol", "dan"]
scores = [92, 71, 85, 58]

result = [f"{name}:{score}" for name, score in zip(names, scores) if score >= 60]
print(result)
```

같은 동작이지만 "두 시퀀스를 짝지어 돌면서, 60점 이상인 이름·점수를 모은다"는 의도가 한 줄로 보입니다. 인덱스가 사라졌고, 누적 리스트가 별도 변수일 필요도 없어졌습니다.

다만 만약 "60점 미만일 때 로그를 남기고, 60점 이상일 때 결과에 모은다"처럼 부수효과가 끼어들면 일반 `for`로 돌아갑니다.

```python
result = []
for name, score in zip(names, scores):
    if score < 60:
        log_low(name, score)
        continue
    result.append(f"{name}:{score}")
```

이 두 형태를 자유롭게 오갈 수 있다면 분기·루프 코드를 훨씬 더 읽기 쉬게 정리할 수 있습니다.

## 단계별 실습

REPL 또는 짧은 스크립트에서 차례대로 실행해 봅니다. 아래 `>>>`가 붙은 줄은 REPL 입력, 그 아래 줄은 출력입니다.

1. **truthy·falsy를 직접 확인합니다.**

```text
>>> for v in [0, 1, "", "x", [], [0], None, {"a": 1}]:
...     print(repr(v), bool(v))
0 False
1 True
'' False
'x' True
[] False
[0] True
None False
{'a': 1} True
```

`[0]`은 길이가 1이라서 truthy임을 확인합니다. "원소가 0이라도 컨테이너가 비어 있지 않으면 truthy"라는 점이 핵심입니다.

2. **`enumerate`와 `zip`을 결합합니다.**

```text
>>> names = ["ada", "bob", "carol"]
>>> roles = ["engineer", "designer", "engineer"]
>>> for idx, (name, role) in enumerate(zip(names, roles), start=1):
...     print(idx, name, "->", role)
1 ada -> engineer
2 bob -> designer
3 carol -> engineer
```

`enumerate(zip(...))` 패턴은 "두 시퀀스를 짝지으면서 1부터 번호를 붙이고 싶을 때" 자주 등장합니다.

3. **`for`-`else`로 검색 결과를 분기합니다.**

```text
>>> def find_first_negative(nums):
...     for n in nums:
...         if n < 0:
...             return n
...     return None
>>> find_first_negative([1, 2, 3])
>>> find_first_negative([1, -2, 3])
-2
```

같은 일을 `for`-`else`로 쓰면 다음과 같습니다. 둘 중 어느 쪽이 더 읽기 쉬운지 판단해 봅니다.

```text
>>> def find_first_negative_v2(nums):
...     for n in nums:
...         if n < 0:
...             return n
...     else:
...         return None
```

이 경우는 함수의 마지막 `return None`이 자연스럽기 때문에 `for`-`else`가 큰 이득을 주지 않습니다. 검색 후에 "찾지 못했다"는 것을 한 번에 처리해야 할 때만 쓰면 충분합니다.

4. **comprehension과 일반 루프 사이를 옮겨 다닙니다.**

```text
>>> nums = list(range(10))
>>> [x * x for x in nums if x % 2 == 0]
[0, 4, 16, 36, 64]
>>> {x: x * x for x in nums if x % 2 == 0}
{0: 0, 2: 4, 4: 16, 6: 36, 8: 64}
>>> sum(x * x for x in nums if x % 2 == 0)  # generator expression
120
```

세 형태가 모두 같은 "짝수 제곱"을 만들지만 결과 컨테이너는 list, dict, 그리고 단일 합계로 다릅니다.

## 이 코드에서 주목할 점

- **`zip(names, scores)`로 인덱스 제거** — `i = 0`, `i += 1`, `len(names)` 세 가지가 한 번에 사라집니다. "두 시퀀스를 짝지어 돌자"는 의도가 타입으로 드러납니다.
- **comprehension에 조건절 `if score >= 60`** — 필터링을 별도 if 블록으로 다시 쓰지 않고 한 줄 안에 놓습니다. "필터 + 변환"이 하나의 관용구처럼 읽힙니다.
- **부수효과가 끼어들면 일반 `for`로 돌아감** — `log_low(...)` 호출이 생기는 순간 comprehension을 포기하는 판단이 중요합니다. "짧은 코드"가 아니라 "의도가 드러나는 코드"가 목표입니다.
- **`continue`로 가드 절절** — `if score < 60: log_low(); continue`로 "조기 탈출" 팅컴 다음 줄의 주로섭이 온전히 "정상 케이스"임이 분명해집니다.
- **f-string 안에 이름과 점수를 동시에 메움** — `name + ":" + str(score)` 같은 레거시 패턴 대신 타입 변환이 필요 없는 f-string이 표준입니다.

## 자주 하는 실수

1. **순회 중인 리스트를 수정합니다.**
   `for item in items: ...` 본문에서 `items.remove(...)`나 `items.append(...)`를 호출하면 인덱스가 어긋나 원소를 건너뛰거나 무한 루프에 빠집니다. 새로운 리스트로 모으거나(`items = [x for x in items if cond(x)]`) 사본을 순회(`for item in items[:]`)합니다.

2. **`while True` 안에서 종료 조건을 잊습니다.**
   탈출 조건이 본문 어딘가에서 반드시 truthy로 바뀌도록 만들어야 합니다. 외부 신호(`KeyboardInterrupt`, 큐 메시지)에 의존한다면 `try/except`나 `break`을 명시적으로 둡니다.

3. **falsy 검사로 "값이 0인지"를 본다.**
   `if value:`는 `value`가 `0`, `""`, `[]`이면 모두 거짓입니다. "값이 명시적으로 주어지지 않은 경우"를 가리키고 싶다면 `if value is None:`을 씁니다. 두 검사는 의미가 다릅니다.

4. **comprehension에 부수효과를 넣습니다.**
   `[print(x) for x in nums]`는 list를 만들면서 그 안에 `None`을 채워 넣는 어색한 코드가 됩니다. `for` 본문에서 `print`를 호출하는 편이 의도가 분명합니다.

5. **`zip`이 짧은 쪽에 맞춰 끝나는 것을 잊습니다.**
   길이가 다른 두 시퀀스를 `zip`으로 묶으면 짧은 쪽 길이만큼만 결과가 나옵니다. 그게 의도가 아니라면 `zip(a, b, strict=True)`로 길이가 다를 때 즉시 `ValueError`를 일으키게 합니다.

6. **`==`와 `is`를 혼동합니다.**
   `is`는 두 변수가 같은 객체를 가리키는지 검사합니다. 값을 비교하고 싶다면 `==`을 씁니다. `is`는 `None`, `True`, `False`처럼 싱글턴을 비교할 때만 자연스럽습니다.

## 실무에서는 이렇게 생각합니다

실무에서는 한 번에 여러 단계를 도는 루프, 입력이 길거나 끝이 정해지지 않은 루프가 자주 등장합니다. 두 가지 패턴을 짚어 둡니다.

**(1) 큰 파일을 줄 단위로 처리합니다.**

```python
total = 0
with open("access.log", encoding="utf-8") as f:
    for line in f:
        if line.startswith("GET "):
            total += 1
print(total)
```

파일 객체는 한 줄씩 내놓는 이터러블이라서 `for line in f:` 한 줄로 충분합니다. `f.readlines()`처럼 한 번에 전부 읽으면 큰 파일에서 메모리 낭비가 큽니다.

**(2) 외부 호출 결과를 모읍니다.**

```python
def fetch_users(ids):
    results = {}
    for user_id in ids:
        try:
            user = api.get_user(user_id)
        except NotFound:
            continue
        results[user_id] = user
    return results
```

루프 안에서 `try/except`로 한 호출만 격리하면 한 사용자가 실패해도 나머지가 계속 진행됩니다. 이때는 comprehension보다 `for`가 적합합니다.

이 두 패턴은 다음 글의 함수 인자 설계, 그 다음 글의 파일 I/O와 예외 처리에서 다시 활용됩니다.

## 체크리스트

- [ ] `if value:`와 `if value is None:`의 차이를 한 줄로 설명할 수 있다.
- [ ] `for`와 `while` 중 어느 쪽을 쓸지 "이터러블이 있는가"로 판단할 수 있다.
- [ ] `enumerate`, `zip`, `range`를 본문에서 직접 호출해 보았다.
- [ ] list/dict/set comprehension을 부수효과 없이 한 번씩 작성해 보았다.
- [ ] `zip`이 짧은 쪽에 맞춰 끝난다는 것을 알고, `strict=True` 옵션을 안다.
- [ ] 순회 중 시퀀스를 수정하지 않는 패턴(`items[:]`, comprehension)을 안다.

## 정리·다음 글

- 분기·루프는 "결정 1회인가, 반복인가" → "이터러블이 있는가"의 두 단계로 자연스럽게 갈립니다.
- `if`는 truthy·falsy를 평가합니다. 빈 컨테이너와 `0`이 모두 falsy라는 점을 의식해야 합니다.
- `for`는 이터러블 위에서 돌고, `while`은 조건이 truthy인 동안 반복됩니다. `enumerate`/`zip`/`range`로 표현력을 키웁니다.
- comprehension은 "변환만" 하는 한정 도구입니다. 부수효과가 끼어드는 순간 일반 `for`로 돌아옵니다.
- `for`-`else`, `zip(..., strict=True)`, `items[:]` 같은 작은 도구들이 자주 쓰는 함정을 정리해 줍니다.

다음 글에서는 함수와 인자를 다룹니다. `def`, `*args`/`**kwargs`, default, lambda를 정리해 분기·루프 본문을 함수 단위로 묶는 법을 살핍니다.

## 실전 앵커: 제어 흐름을 안전하게 다루는 패턴과 함정

조건문과 반복문은 문법보다 경계 조건이 핵심입니다. 특히 `if/elif/else`가 길어질수록 누락된 분기를 찾기 어려워집니다. 이럴 때는 매핑 테이블로 표현하면 버그 면적이 줄어듭니다.

```python
def fee(level):
    table = {
        'basic': 0,
        'pro': 10000,
        'enterprise': 50000,
    }
    return table.get(level, -1)
```

반복문에서는 `for-else`의 의미를 정확히 아는 것이 중요합니다. `else`는 루프가 `break` 없이 끝났을 때 실행됩니다.

```python
nums = [2, 4, 6, 9]
for n in nums:
    if n % 2 == 1:
        print('홀수 발견:', n)
        break
else:
    print('홀수가 없습니다')
```

처음 보는 사람은 `if-else`로 오해하기 쉽기 때문에, 팀 코드에서는 주석이나 함수명으로 의도를 분명히 드러내는 편이 좋습니다.

무한 루프 방지는 시간 조건과 카운터 조건을 동시에 두면 안전합니다.

```python
import time

start = time.time()
retry = 0
while True:
    retry += 1
    if retry >= 5:
        break
    if time.time() - start > 10:
        break
```

성능 측면에서는 리스트 컴프리헨션과 명시적 루프의 차이를 경험해 두면 좋습니다.

```python
import timeit

loop_t = timeit.timeit('out=[]
for x in range(10000):
    out.append(x*x)', number=500)
comp_t = timeit.timeit('[x*x for x in range(10000)]', number=500)
print(loop_t, comp_t)
```

예시 출력:

```text
0.487201
0.311778
```

모든 경우에 컴프리헨션이 정답은 아니지만, 단순 변환이라면 더 읽기 쉽고 빠른 경우가 많습니다.

디버깅 예시로는 분기 추적이 효과적입니다.

```python
import pdb

def classify(score):
    pdb.set_trace()
    if score >= 90:
        return 'A'
    if score >= 80:
        return 'B'
    return 'C'

classify(85)
```

`n`으로 한 줄씩 진행하면서 조건 평가를 확인하면 논리 누락을 빠르게 찾습니다.

또 하나 자주 발생하는 함정은 `continue` 때문에 중요한 후처리가 건너뛰는 경우입니다. 파일 핸들 정리, 카운트 증가, 로깅은 분기 아래가 아니라 루프 구조 바깥에서 관리하는 것이 안전합니다.

제어 흐름 파트의 목표는 문법 암기가 아니라, 예외 상황에서도 코드가 예측 가능하게 움직이도록 만드는 것입니다.

### 추가 실습: 분기 누락 방지와 테스트 가능한 흐름

제어 흐름은 테스트 케이스 설계와 같이 움직여야 합니다. 예를 들어 등급 판정 함수는 경계값(89, 90, 79, 80)을 별도 테스트로 고정해야 회귀를 막을 수 있습니다.

```python
def grade(s):
    if s >= 90:
        return 'A'
    if s >= 80:
        return 'B'
    return 'C'
```

테스트 관점 입력 목록:

```text
89 -> B
90 -> A
79 -> C
80 -> B
```

`match-case`를 사용하는 경우에도 기본 분기(`case _`)를 항상 두는 습관이 필요합니다. 알 수 없는 값이 들어왔을 때 조용히 실패하지 않게 하기 위해서입니다.

```python
def action(cmd):
    match cmd:
        case 'start':
            return 1
        case 'stop':
            return 2
        case _:
            raise ValueError(f'unknown cmd: {cmd}')
```

### 부록: 로컬 실습 로그 템플릿

아래 템플릿은 학습 단계에서 직접 실험한 결과를 남길 때 유용합니다. 중요한 점은 "코드 + 실행 환경 + 출력"을 한 세트로 기록하는 것입니다. 이렇게 남긴 로그는 나중에 문제가 다시 발생했을 때 가장 신뢰할 수 있는 재현 자료가 됩니다.

```text
[환경]
python: 3.12.x
platform: macOS/Linux
venv: .venv

[실험]
목표: 동작 확인 또는 성능 비교
입력: 샘플 데이터 1,000건
실행 명령: python script.py

[출력]
성공/실패 여부
핵심 숫자(timeit, 처리 건수, 예외 메시지)
```

실무 코드 리뷰에서는 결과 숫자만 공유하는 경우가 많지만, 학습 단계에서는 중간 가정까지 함께 적는 편이 더 효과적입니다. 예를 들어 "셋 포함 검사가 빠를 것이다"라는 가정이 맞았는지, "f-string이 항상 더 읽기 쉽다"라는 판단이 팀 컨벤션과 맞는지까지 기록하면 다음 의사결정이 빨라집니다.

디버깅 기록도 같은 형식을 쓰면 좋습니다.

1) 증상: 어떤 입력에서 실패했는가
2) 가설: 어떤 조건문/자료구조/경로가 원인인가
3) 검증: `pdb`, `print`, `timeit`, 단위 테스트 중 무엇으로 확인했는가
4) 결론: 수정 전후 동작 차이가 무엇인가

이 습관은 초급 단계에서는 다소 느리게 느껴질 수 있습니다. 하지만 프로젝트 규모가 커질수록 "정확한 기록"이 가장 빠른 길이 됩니다. Python 문법을 익히는 것과 별개로, 실험을 재현 가능한 형태로 남기는 역량은 개발자로서의 성장 속도를 결정합니다.

## 처음 질문으로 돌아가기

- **제어 흐름: if, for, while, comprehension를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?**
  - 본문의 기준은 제어 흐름: if, for, while, comprehension를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **제어 흐름: if, for, while, comprehension에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **제어 흐름: if, for, while, comprehension를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python 101 (1/10): 왜 Python인가, 그리고 설치와 venv](./01-why-python-and-install.md)
- [Python 101 (2/10): 변수, 타입, 연산자](./02-variables-types-operators.md)
- [Python 101 (3/10): 문자열과 포매팅](./03-strings-and-formatting.md)
- [Python 101 (4/10): list, tuple, set, dict](./04-list-tuple-set-dict.md)
- **제어 흐름: if, for, while, comprehension (현재 글)**
- 함수와 인자: def, args, kwargs, default, lambda (예정)
- 모듈과 패키지: import, __init__, __name__ (예정)
- 파일 I/O와 예외 처리 (예정)
- 클래스와 객체: 데이터와 동작을 함께 묶기 (예정)
- 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 튜토리얼 — More Control Flow Tools](https://docs.python.org/3/tutorial/controlflow.html) — `if`, `for`, `while`, `break`, `continue`, `else`, comprehension까지 이 장의 핵심 구문을 모두 다룹니다.
- [Python 공식 문서 — Built-in Types](https://docs.python.org/3/library/stdtypes.html) — truthy/falsy, short-circuit, 비교 연쇄의 기준 규칙이 모여 있습니다.
- [Python 공식 문서 — Built-in Functions](https://docs.python.org/3/library/functions.html) — `range`, `enumerate`, `zip`의 시그니처와 동작을 함께 확인할 수 있습니다.
- [PEP 202 — List Comprehensions](https://peps.python.org/pep-0202/) — comprehension이 반복/필터링을 어떻게 표현식으로 압축하는지 보여 주는 원문입니다.
- [Python 공식 문서 — Compound Statements](https://docs.python.org/3/reference/compound_stmts.html) — `if`, `while`, `for`의 정확한 문법과 `else` 의미를 언어 명세 수준에서 확인할 수 있습니다.

Tags: control-flow, if-statement, for-loop, while-loop, comprehensions, enumerate-zip
