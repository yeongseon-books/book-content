---
title: "Python 101 (4/10): list, tuple, set, dict"
series: python-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- list-and-tuple
- dict
- set
- mutability
- comprehensions
- hashable
last_reviewed: '2026-05-12'
seo_description: 네 자료구조는 "가변성, 순서, 중복 허용, 해시 가능성"이라는 네 축의 조합으로 구분되며, 자료구조를 고른다는 것은
  이 네 축에서 어떤…
---

# Python 101 (4/10): list, tuple, set, dict

list, tuple, set, dict는 비슷해 보여도 가변성, 순서, 중복 허용, 해시 가능성이라는 네 축에서 역할이 갈립니다. 자료구조 선택은 결국 이 네 축에서 무엇을 우선할지 정하는 일입니다.

이 글은 Python 101 시리즈의 네 번째 글입니다.


![Python 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-101/04/04-01-mental-model.ko.png)
*Python 101 4장 흐름 개요*
> list, tuple, set, dict의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- list를 `=`으로 "복사"한 뒤 한쪽을 바꿨는데 양쪽이 함께 바뀌는 alias 사고?
- 함수의 기본 인자로 `def f(items=[]):`를 썼다가, 호출이 누적될수록 리스트가 자라는 문제?
- dict에서 없는 키를 `d[key]`로 꺼내다가 `KeyError`로 멈추는 일?

## 멘탈 모델

> 네 자료구조는 "가변성, 순서, 중복 허용, 해시 가능성"이라는 네 축의 조합으로 구분되며, 자료구조를 고른다는 것은 이 네 축에서 어떤 보장을 받고 어떤 보장을 포기할지를 결정하는 일입니다.
네 자료구조를 가변성·순서·해시 가능성으로 묶으면 머릿속에 잘 박힙니다.

세 가지 핵심 규칙입니다.

1. **가변(list, dict, set)** 은 만든 뒤에 내용을 바꿀 수 있고, **불변(tuple, str, int)** 은 바꿀 수 없습니다.
2. **dict의 키와 set의 원소는 hashable해야** 합니다. tuple은 안에 들어 있는 값이 모두 hashable이면 자기도 hashable입니다.
3. **dict와 set은 평균 O(1)** 으로 키 검색이 끝나지만, list는 O(n)입니다. "이 값이 있나?"를 자주 묻는 자료라면 set이나 dict를 씁니다.

*자료구조 결정 트리: 위에서 아래로 네 질문을 따라가면 자연스럽게 하나가 남습니다.*

## 핵심 개념

### 1) list — 순서가 있고 가변

```text
>>> nums = [3, 1, 4, 1, 5]
>>> nums.append(9)
>>> nums
[3, 1, 4, 1, 5, 9]
>>> nums[0]
3
>>> nums[-1]
9
>>> nums[1:4]
[1, 4, 1]
>>> sorted(nums)
[1, 1, 3, 4, 5, 9]
>>> nums.sort()      # in place; returns None
>>> nums
[1, 1, 3, 4, 5, 9]
```

`sorted(nums)`는 **새 리스트**를 돌려주고, `nums.sort()`는 **제자리에서 정렬**합니다. `nums.sort()`의 반환값은 `None`이라는 점이 자주 잊힙니다.

`append`와 `extend`도 헷갈리기 쉽습니다.

```text
>>> a = [1, 2]
>>> a.append([3, 4])
>>> a
[1, 2, [3, 4]]            # the whole list is added as one element
>>> a = [1, 2]
>>> a.extend([3, 4])
>>> a
[1, 2, 3, 4]              # elements are added one by one
```

### 2) tuple — 순서가 있고 불변

```text
>>> point = (3, 4)
>>> x, y = point          # unpacking
>>> x, y
(3, 4)
>>> point[0] = 10
Traceback (most recent call last):
  ...
TypeError: 'tuple' object does not support item assignment
```

tuple은 "묶음의 정체성"을 표현할 때 좋습니다. 좌표 `(x, y)`, RGB 값 `(255, 0, 0)`, 데이터베이스의 한 행 같은 것입니다. 의미를 더 분명히 하려면 `collections.namedtuple`이나 `dataclasses.dataclass(frozen=True)`로 이름 붙은 튜플을 만들 수도 있습니다.

요소가 하나인 튜플은 콤마가 필수입니다. `(1)`은 그냥 정수입니다.

```text
>>> type((1))
<class 'int'>
>>> type((1,))
<class 'tuple'>
```

### 3) set — 순서 없음, 중복 없음

set은 멤버십 검사와 중복 제거에 강합니다.

```text
>>> seen = {1, 2, 3}
>>> seen.add(2)             # already present; ignored
>>> seen
{1, 2, 3}
>>> 2 in seen
True
>>> {1, 2, 3} & {2, 3, 4}   # intersection
{2, 3}
>>> {1, 2, 3} | {2, 3, 4}   # union
{1, 2, 3, 4}
>>> {1, 2, 3} - {2}         # difference
{1, 3}
```

빈 set은 `set()`이지 `{}`이 아닙니다. `{}`은 빈 dict입니다.

```text
>>> type({})
<class 'dict'>
>>> type(set())
<class 'set'>
```

set의 반복 순서는 보장되지 않습니다. 출력을 비교하는 테스트라면 `sorted(seen)`처럼 정렬한 뒤 비교해야 합니다.

### 4) dict — 키→값 매핑, 가변, 키 유일

dict는 가장 자주 쓰는 자료구조입니다. Python 3.7부터 삽입 순서를 보존합니다.

```text
>>> user = {"name": "ada", "age": 30}
>>> user["name"]
'ada'
>>> user["email"] = "ada@example.com"
>>> user
{'name': 'ada', 'age': 30, 'email': 'ada@example.com'}
>>> "age" in user
True
>>> user.get("phone")          # missing → None
>>> user.get("phone", "N/A")
'N/A'
>>> list(user.keys())
['name', 'age', 'email']
>>> list(user.items())
[('name', 'ada'), ('age', 30), ('email', 'ada@example.com')]
```

없는 키를 `d[key]`로 꺼내면 `KeyError`가 납니다. "있을 수도, 없을 수도 있다"면 `get`을 씁니다.

### 5) hashable의 의미

dict의 키와 set의 원소는 **hashable**해야 합니다. 즉 한 번 만들어진 뒤 값이 변하지 않고, `__hash__`가 정의돼 있어야 합니다.

- hashable: `int`, `float`, `str`, `bool`, `bytes`, 모든 원소가 hashable인 `tuple`
- not hashable: `list`, `set`, `dict` (가변이라 hash 결과가 도중에 바뀔 수 있어서)

```text
>>> {(1, 2), (3, 4)}                    # tuples are hashable
{(1, 2), (3, 4)}
>>> {[1, 2], [3, 4]}
Traceback (most recent call last):
  ...
TypeError: unhashable type: 'list'
```

set 안에 set을 넣고 싶다면 `frozenset`을 씁니다.

### 6) Comprehension — 한 줄로 변형

list, set, dict 모두 comprehension 문법을 갖고 있습니다.

```text
>>> [n * n for n in range(5)]
[0, 1, 4, 9, 16]
>>> [n for n in range(10) if n % 2 == 0]
[0, 2, 4, 6, 8]
>>> {word.lower() for word in ["Python", "PYTHON", "python"]}
{'python'}
>>> {n: n * n for n in range(4)}
{0: 0, 1: 1, 2: 4, 3: 9}
```

comprehension은 짧지만, 조건이 두 개 이상으로 늘어나거나 중첩이 깊어지면 가독성이 떨어집니다. 그럴 때는 일반 `for` 루프로 풀어쓰는 편이 낫습니다.

## 전후 비교

같은 일을 어색한 방식과 자료구조를 잘 고른 방식으로 비교해 봅니다.

```python
# Before: list membership is O(n)
seen = []
duplicates = []
for x in stream:
    if x in seen:                # scans the whole list every time
        duplicates.append(x)
    else:
        seen.append(x)

# After: set membership is O(1) on average
seen = set()
duplicates = []
for x in stream:
    if x in seen:
        duplicates.append(x)
    else:
        seen.add(x)
```

dict의 누락 키 처리도 줄일 수 있습니다.

```python
# Before: explicit existence check every time
counts = {}
for word in words:
    if word in counts:
        counts[word] = counts[word] + 1
    else:
        counts[word] = 1

# After: dict.get or defaultdict
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1

# After (shortest): collections.Counter
from collections import Counter
counts = Counter(words)
```

## 단계별 실습

로그 줄 리스트에서 IP 주소별 접근 횟수와 첫 접근 시간을 모아 봅니다. dict, set, tuple, comprehension을 모두 씁니다.

1. **샘플 데이터 준비.**

   ```python
   logs = [
       ("10.0.0.1", "2026-05-03 09:00:01"),
       ("10.0.0.2", "2026-05-03 09:00:02"),
       ("10.0.0.1", "2026-05-03 09:00:05"),
       ("10.0.0.3", "2026-05-03 09:00:07"),
       ("10.0.0.2", "2026-05-03 09:00:10"),
   ]
   ```

2. **유일 IP 추출.** set comprehension으로 한 줄에 끝납니다.

   ```python
   unique_ips = {ip for ip, _ in logs}
   # {'10.0.0.1', '10.0.0.2', '10.0.0.3'}
   ```

3. **IP별 접근 횟수.** `dict.get`을 활용합니다.

   ```python
   counts = {}
   for ip, _ in logs:
       counts[ip] = counts.get(ip, 0) + 1
   # {'10.0.0.1': 2, '10.0.0.2': 2, '10.0.0.3': 1}
   ```

4. **IP별 첫 접근 시간.** `dict.setdefault`로 한 번에 처리합니다.

   ```python
   first_seen = {}
   for ip, ts in logs:
       first_seen.setdefault(ip, ts)
   # {'10.0.0.1': '2026-05-03 09:00:01', '10.0.0.2': '...', '10.0.0.3': '...'}
   ```

5. **결과 정렬.** dict는 정렬을 직접 하지 않으므로 `sorted`로 새 리스트를 만듭니다.

   ```python
   ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
   # [('10.0.0.1', 2), ('10.0.0.2', 2), ('10.0.0.3', 1)]
   ```

`Counter`를 알고 있다면 2번과 3번은 한 줄로 줄어듭니다. 다음 글의 함수와 합쳐 재사용 가능한 형태로 빼면 더 깔끔해집니다.

## 이 코드에서 주목할 점

- **set comprehension으로 유일 IP 추출** — `{ip for ip, _ in logs}` 한 줄이 빈 set 초기화·루프·중복 검사를 모두 대신합니다. 의도가 "유일 원소 모음"임을 자료구조 자체가 말해 줍니다.
- **`dict.get(key, 0)` 누락 키 패턴** — `if key in d` 검사를 없애고 "없으면 0"을 한 표현식에 담습니다. 카운팅·누적 코드의 기본기입니다.
- **`setdefault`로 첫 값 보존** — 두 번째 호출부터는 무시되므로 "첫 등장 시간" 같은 first-write-wins 의미가 자연스럽게 표현됩니다.
- **`sorted(items, key=lambda kv: kv[1], reverse=True)`** — dict는 정렬 자료구조가 아니므로 새 list를 만들어 정렬합니다. 키 함수로 값 기준 정렬을 명시합니다.
- **tuple 언패킹 `for ip, ts in logs`** — 인덱스 `[0]`, `[1]` 대신 의미 있는 이름을 즉시 부여해 다음 줄의 가독성이 올라갑니다.

## 자주 하는 실수

1. **`b = a`로 list를 "복사"한다.**
   `b = a`는 같은 객체에 이름표를 하나 더 붙일 뿐입니다. 한쪽을 바꾸면 양쪽이 바뀝니다. 얕은 복사가 필요하면 `b = a[:]`이나 `b = list(a)`, 중첩까지 복사하려면 `copy.deepcopy(a)`를 씁니다.

2. **mutable 기본 인자.**
   `def f(items=[]):`는 함수 정의 시점에 리스트를 한 번 만들고, 호출 사이에 그 리스트를 공유합니다. 호출이 누적될수록 리스트가 자랍니다. 기본값이 빈 리스트여야 한다면 `def f(items=None): items = items if items is not None else []`로 작성합니다.

3. **dict의 없는 키를 `d[key]`로 꺼낸다.**
   `KeyError`가 발생합니다. "있을 수도, 없을 수도"라면 `d.get(key)` 또는 `d.get(key, default)`를 씁니다. "없으면 만들어라"는 패턴은 `setdefault`나 `defaultdict`가 어울립니다.

4. **set의 순서를 신뢰한다.**
   set은 순서를 보장하지 않습니다. 출력 순서를 비교하는 테스트라면 `sorted(...)`로 정렬한 뒤 비교합니다. dict는 3.7부터 삽입 순서를 보장하지만, 그 보장을 set으로 끌어들이지 않습니다.

5. **list를 set이나 dict 키로 쓰려고 한다.**
   `TypeError: unhashable type: 'list'`을 만납니다. 키로 써야 하면 `tuple(seq)`으로 변환합니다.

6. **`dict.keys()`, `dict.values()`를 list로 가정한다.**
   둘 다 view 객체입니다. dict가 바뀌면 view도 같이 바뀝니다. 고정된 스냅샷이 필요하면 `list(d.keys())`처럼 명시적으로 변환합니다.

## 실무에서는 이렇게 생각합니다

- **카운팅·그루핑.** `Counter`, `defaultdict(list)`는 직접 짜는 dict 누락 키 패턴을 줄여 줍니다. 본인이 짠 코드에 `if key not in d: d[key] = []`이 반복된다면 `defaultdict`로 바꿉니다.
- **순서 있는 dict.** Python 3.7+에서는 dict 자체가 삽입 순서를 보존합니다. `OrderedDict`는 끝에서 꺼내거나 다시 정렬하는 등의 dict에는 없는 기능을 위한 용도로 남겨 둡니다.
- **불변 묶음.** 함수 사이로 전달되는 "이 묶음은 바꾸지 마세요" 신호는 tuple, `frozenset`, `dataclass(frozen=True)`로 표현합니다. 타입만 보고도 의도가 드러납니다.
- **JSON 직렬화.** `json.dumps`는 set을 직접 직렬화하지 못합니다. 보내기 직전에 `list(my_set)`이나 `sorted(my_set)`으로 변환합니다.
- **대량 멤버십 검사.** "10만 개의 차단 사용자 ID"가 list라면 검사마다 O(n)입니다. set으로 한 번 변환해 두고 검사를 반복합니다.

## 체크리스트

- [ ] list, tuple, set, dict의 가변성·순서·중복·해시 가능성을 표로 그릴 수 있다
- [ ] `=`로는 list가 복사되지 않는다는 사실을 안다
- [ ] mutable 기본 인자의 함정과 회피 패턴을 안다
- [ ] `dict.get`, `setdefault`, `defaultdict`, `Counter`를 적절히 골라 쓸 수 있다
- [ ] hashable이라는 단어를 한 줄로 설명할 수 있다
- [ ] list/set/dict comprehension을 한 번씩 짜 봤다
- [ ] set의 순서가 보장되지 않는다는 점을 잊지 않는다
- [ ] tuple과 namedtuple/dataclass(frozen=True)가 어떤 자리에 어울리는지 안다

## 정리·다음 글

- list/tuple은 순서 있는 묶음, set은 해시 기반의 유일 원소 모음, dict는 키→값 매핑입니다.
- 가변(list, set, dict)과 불변(tuple)을 의식적으로 골라야 의도가 분명해집니다.
- dict 키와 set 원소는 hashable해야 하며, list는 hashable이 아닙니다.
- `b = a`는 복사가 아니라 alias입니다. 복사가 필요하면 `list(a)` 또는 `copy.deepcopy(a)`를 씁니다.
- 누락 키 처리는 `dict.get`, `setdefault`, `defaultdict`, `Counter`로 짧게 마무리합니다.

다음 글에서는 제어 흐름을 다룹니다. `if`/`for`/`while`을 정리하고, comprehension과 `enumerate`/`zip`/`range`를 함께 이어 읽기 좋은 루프를 짜는 법을 짚습니다.

## 실전 앵커: 자료구조 선택을 감이 아니라 근거로 결정하기

리스트, 튜플, 셋, 딕셔너리는 모두 자주 쓰이지만 목적이 다릅니다. 아래 표를 실무 의사결정의 기본 템플릿으로 기억해 두면 좋습니다.

| 구조 | 순서 보장 | 중복 허용 | 변경 가능 | 주 사용 목적 |
|---|---|---|---|---|
| `list` | 예 | 예 | 예 | 순차 데이터, 인덱싱 |
| `tuple` | 예 | 예 | 아니오 | 불변 레코드, 해시 키 구성 요소 |
| `set` | 아니오 | 아니오 | 예 | 빠른 포함 검사, 집합 연산 |
| `dict` | 예(삽입 순서) | 키 중복 불가 | 예 | 키-값 매핑, 인덱스 |

입문자가 가장 자주 묻는 질문은 "왜 이 경우 리스트가 아니라 셋인가요"입니다. 답은 포함 검사 비용입니다.

```python
import timeit

list_t = timeit.timeit('99999 in data', setup='data=list(range(100000))', number=10000)
set_t = timeit.timeit('99999 in data', setup='data=set(range(100000))', number=10000)
print(list_t, set_t)
```

예시 출력:

```text
7.889102
0.002614
```

데이터 구조 선택이 알고리즘 복잡도를 바꾼다는 사실이 숫자로 드러납니다. 이 한 번의 체험이 이후 코드를 크게 바꿉니다.

공유 참조 함정도 반드시 짚어야 합니다. 다음 코드는 2차원 배열 초기화에서 반복적으로 나타나는 버그입니다.

```python
matrix = [[0] * 3] * 2
matrix[0][1] = 9
print(matrix)
```

출력:

```text
[[0, 9, 0], [0, 9, 0]]
```

내부 리스트가 같은 객체를 가리키기 때문입니다. 안전한 방식은 컴프리헨션입니다.

```python
matrix = [[0] * 3 for _ in range(2)]
```

딕셔너리는 `get`, `setdefault`, `defaultdict`를 상황별로 나눠서 쓰는 감각이 중요합니다.

```python
from collections import defaultdict

words = ['py', 'py', 'code']
counter = defaultdict(int)
for w in words:
    counter[w] += 1
print(counter)
```

가독성과 안정성을 동시에 챙기려면, 누적/그룹화는 `defaultdict`를 기본 후보에 두는 편이 좋습니다.

튜플은 불변이라 안전하다는 장점이 있지만 내부에 가변 객체가 들어가면 완전 불변이 아닙니다.

```pycon
>>> t = (1, [2, 3])
>>> t[1].append(4)
>>> t
(1, [2, 3, 4])
```

이 사례는 "튜플이면 다 안전하다"는 오해를 바로잡아 줍니다.

디버깅은 `pdb`에서 객체 id를 확인하면 빠릅니다.

```python
import pdb

a = [1, 2]
b = a
pdb.set_trace()
```

`p id(a)`, `p id(b)`, `p a is b`를 순서대로 찍으면 얕은 복사/참조 공유 여부를 즉시 확인할 수 있습니다.

표준 라이브러리 예시도 함께 묶어 보겠습니다.

- `collections.deque`: 양쪽 끝 삽입/삭제가 많은 큐
- `heapq`: 우선순위 큐
- `bisect`: 정렬 리스트에 이진 탐색 삽입

자료구조 파트에서 이 세 모듈을 같이 기억하면 문제 풀이에서 실무 코드로 넘어갈 때 훨씬 자연스럽습니다.

### 추가 실습: 자료구조 선택 실수 사례 복기

실무에서 자주 보는 실수는 "순서가 중요하지 않은데 리스트를 기본값으로 쓰는 것"입니다. 중복 제거가 필요하다면 처음부터 셋으로 모으는 편이 간단하고 빠릅니다.

```python
emails = ['a@x.com', 'b@x.com', 'a@x.com']
unique = set(emails)
print(unique)
```

딕셔너리 병합 문법도 알아두면 코드가 많이 짧아집니다.

```python
a = {'host': 'localhost', 'port': 5432}
b = {'port': 5433, 'debug': True}
merged = a | b
print(merged)
```

출력:

```text
{'host': 'localhost', 'port': 5433, 'debug': True}
```

튜플은 언패킹과 함께 쓰면 가독성이 좋아집니다.

```python
point = (10, 20)
x, y = point
print(x, y)
```

그리고 정렬이 필요한 딕셔너리 뷰는 `sorted(d.items(), key=...)` 패턴을 익혀 두면 분석용 코드 작성 속도가 빨라집니다.

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

### 보강 메모: 실수 줄이는 운영 습관

학습 단계에서 만든 코드를 실제 프로젝트에 옮길 때는 세 가지를 같이 점검하는 편이 좋습니다. 첫째, 입력 검증 경계가 함수 시작 지점에 있는지 확인합니다. 둘째, 실패 시 사용자에게 보여 줄 메시지와 로그 메시지를 분리합니다. 셋째, 성능 판단은 추측이 아니라 `timeit` 또는 샘플 벤치마크로 남깁니다.

간단한 템플릿은 다음과 같습니다.

```python
def safe_run(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except Exception as e:
        # 학습 단계에서는 원인 관찰을 우선
        raise RuntimeError(f'실행 실패: {fn.__name__}') from e
```

또한 표준 라이브러리 문서를 읽을 때는 "모듈 개요 -> 대표 함수 3개 -> 예외 종류" 순서로 훑는 습관을 들이면 기억이 오래갑니다. 기능을 전부 외우는 것보다, 어떤 상황에서 어떤 모듈을 열어봐야 하는지 아는 것이 더 중요합니다.

실무에서는 "먼저 올바른 자료구조를 고르고, 그다음 구현을 단순화한다"는 순서가 중요합니다. 자료구조 선택이 맞으면 코드 길이와 버그 수가 동시에 줄어듭니다.

## 처음 질문으로 돌아가기

- **list를 `=`으로 "복사"한 뒤 한쪽을 바꿨는데 양쪽이 함께 바뀌는 alias 사고?**
  - 본문의 기준은 list, tuple, set, dict를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **함수의 기본 인자로 `def f(items=[]):`를 썼다가, 호출이 누적될수록 리스트가 자라는 문제?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **dict에서 없는 키를 `d[key]`로 꺼내다가 `KeyError`로 멈추는 일?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python 101 (1/10): 왜 Python인가, 그리고 설치와 venv](./01-why-python-and-install.md)
- [Python 101 (2/10): 변수, 타입, 연산자](./02-variables-types-operators.md)
- [Python 101 (3/10): 문자열과 포매팅](./03-strings-and-formatting.md)
- **list, tuple, set, dict (현재 글)**
- 제어 흐름: if, for, while, comprehension (예정)
- 함수와 인자: def, args, kwargs, default, lambda (예정)
- 모듈과 패키지: import, __init__, __name__ (예정)
- 파일 I/O와 예외 처리 (예정)
- 클래스와 객체: 데이터와 동작을 함께 묶기 (예정)
- 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools (예정)

<!-- toc:end -->

## 참고 자료

- [Python 공식 문서 — Built-in Types](https://docs.python.org/3/library/stdtypes.html) — list, tuple, set, dict의 공식 동작과 해시 가능성 제약을 한곳에서 확인할 수 있습니다.
- [Python 튜토리얼 — Data Structures](https://docs.python.org/3/tutorial/datastructures.html) — list 메서드, tuple, set, dict, comprehension을 입문 수준 예제로 설명합니다.
- [PEP 274 — Dict Comprehensions](https://peps.python.org/pep-0274/) — dict comprehension 문법과 의도를 직접 확인할 수 있습니다.
- [Python Wiki — TimeComplexity](https://wiki.python.org/moin/TimeComplexity) — list의 선형 탐색과 dict/set의 평균 O(1) 조회를 비교할 때 참고할 수 있습니다.
- [Python 공식 문서 — `collections`](https://docs.python.org/3/library/collections.html) — `namedtuple`, `deque` 같은 표준 보조 자료구조를 소개해 자료구조 선택 기준을 넓혀 줍니다.
- [Python 공식 문서 — Data Model](https://docs.python.org/3/reference/datamodel.html) — 변경 가능 객체와 불변 객체의 차이를 언어 모델 차원에서 보강합니다.

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/python-101/ko)
Tags: list-and-tuple, dict, set, mutability, comprehensions, hashable
