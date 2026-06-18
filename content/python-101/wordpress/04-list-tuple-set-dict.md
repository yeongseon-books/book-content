---
title: "바이브코딩을 위한 Python 기초 (4/10): list, tuple, set, dict"
series: python-101
episode: 4
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- Python
- AI코딩
- 리스트
- 딕셔너리
- 자료구조선택
- comprehension
seo_description: "바이브코딩 시대, AI가 리스트를 줬는데 딕셔너리가 더 적합한 상황을 판단하려면 네 가지 자료구조의 차이를 알아야 합니다."
---

# 바이브코딩을 위한 Python 기초 (4/10): list, tuple, set, dict

이 글은 바이브코딩을 위한 Python 기초 시리즈의 4번째 글입니다.

AI에게 "사용자 ID 목록에서 중복 제거하고 특정 ID가 있는지 검사해줘"라고 했더니 이런 코드가 나왔습니다.

```python
user_ids = [1001, 1002, 1001, 1003, 1002]
unique_ids = []
for uid in user_ids:
    if uid not in unique_ids:
        unique_ids.append(uid)

if target_id in unique_ids:
    print("발견")
```

코드는 동작합니다. 그런데 사용자가 100만 명이라면 어떻게 될까요? `if uid not in unique_ids`가 매 반복마다 리스트 전체를 스캔하고, `if target_id in unique_ids`도 마찬가지입니다. `set`을 쓰면 두 줄로 끝나고 검색도 O(1)인데, AI는 리스트로 만들었습니다.

AI는 "동작하는 코드"를 만들지만, 자료구조 선택이 최적인지는 보장하지 않습니다. 특히 성능이 중요한 코드에서, 또는 AI가 리스트를 줬는데 딕셔너리가 더 적합한 상황을 판단하려면 네 자료구조의 차이를 알아야 합니다.

> 자료구조 선택은 "가변인가, 순서가 있는가, 중복을 허용하는가"라는 세 질문으로 결정됩니다.

---

## 이 글에서 다룰 문제

- AI가 리스트로 멤버십 검사를 만들었을 때, 언제 set으로 바꿔달라고 해야 할까?
- AI가 `=`로 리스트를 "복사"하는 코드를 만들었는데, 왜 양쪽이 같이 바뀌는 버그가 생기나?
- AI가 dict에서 키를 `d[key]`로 꺼내는 코드를 만들었을 때 KeyError를 막으려면?
- list, tuple, set, dict 중 어떤 것을 JSON으로 직렬화할 수 없나?
- AI에게 "카운팅 로직 만들어줘"라고 할 때 가장 Pythonic한 결과를 받는 방법은?

---

## 네 자료구조를 고르는 세 질문

AI가 자료구조를 선택할 때 항상 최적이 아닐 수 있습니다. 다음 세 질문으로 AI 코드를 검토할 수 있습니다.

**1. 순서가 필요한가?**
- 예 → list 또는 tuple (또는 dict, Python 3.7+에서 삽입 순서 보장)
- 아니오 → set 또는 dict (순서 무관)

**2. 변경이 필요한가?**
- 예 → list, dict, set
- 아니오 (한 번 만들면 고정) → tuple, frozenset

**3. 키-값 쌍인가, 단순 모음인가?**
- 키-값 쌍 → dict
- 단순 모음 → list, tuple, set

| 자료구조 | 순서 | 중복 | 변경 | 주용도 |
| --- | --- | --- | --- | --- |
| `list` | 있음 | 허용 | 가능 | 순서 있는 데이터, 스택/큐 |
| `tuple` | 있음 | 허용 | 불가 | 좌표, DB 행, 반환 다중값 |
| `set` | 없음 | 불가 | 가능 | 중복 제거, 빠른 멤버십 검사 |
| `dict` | 있음(삽입순) | 키 불가 | 가능 | 이름→값 매핑, 카운팅 |

## list: AI 코드에서 자주 보이는 두 가지 함정

**함정 1: 얕은 복사 vs 별칭**

```python
# AI가 생성한 코드 — 버그 가능성 있음
original = [1, 2, 3]
copy = original          # 이것은 복사가 아닙니다
copy.append(4)
print(original)          # [1, 2, 3, 4] — 원본도 바뀜!

# 올바른 얕은 복사
copy = original[:]       # 또는 list(original)
copy = original.copy()
```

`b = a`는 같은 객체에 이름표를 하나 더 붙입니다. AI가 이렇게 "복사"하는 코드를 만들었다면 즉시 `[:]` 또는 `list()`로 수정 요청을 보내세요.

**함정 2: `append` vs `extend`**

```python
a = [1, 2]
a.append([3, 4])    # [1, 2, [3, 4]] — 리스트가 하나의 원소로 추가됨
a = [1, 2]
a.extend([3, 4])    # [1, 2, 3, 4] — 원소들이 펼쳐져 추가됨
```

AI가 두 메서드를 혼동하는 경우가 있습니다. 여러 원소를 "평탄하게" 추가하려면 `extend`, 하나의 컨테이너를 원소로 넣으려면 `append`입니다.

## set: AI가 놓치기 쉬운 성능 최적화

앞서 본 예시처럼 AI는 종종 멤버십 검사를 리스트로 처리합니다. 데이터 수가 적으면 문제없지만 수만 건 이상이 되면 성능 차이가 극적으로 납니다.

```python
# AI가 생성한 코드 — O(n) 검사
blocked_users = [1001, 1002, 1003, ...]  # 리스트

if user_id in blocked_users:   # 리스트 전체를 스캔
    ...

# 개선 — O(1) 검사
blocked_users = {1001, 1002, 1003, ...}  # set

if user_id in blocked_users:   # 해시로 즉시 검사
    ...
```

AI에게 "이 리스트가 멤버십 검사 용도라면 set으로 바꿔줘"라고 프롬프트를 보내면 됩니다.

set 사용 시 주의할 점 두 가지:
1. 빈 set은 `set()`이지 `{}`가 아닙니다. `{}`는 빈 dict입니다.
2. 순서가 보장되지 않아 출력 순서가 실행마다 다를 수 있습니다.

## dict: AI가 만든 누락 키 처리 패턴 개선

AI가 dict에서 값을 꺼낼 때 `d[key]` 방식을 쓰면 키가 없을 때 KeyError가 납니다.

```python
# AI가 생성한 코드 — KeyError 위험
user = {"name": "김철수", "age": 30}
print(user["email"])   # KeyError: 'email'

# 안전한 방법들
print(user.get("email"))           # None 반환
print(user.get("email", "없음"))   # 기본값 반환
```

AI에게 "키가 없을 수 있는 dict 접근은 .get() 사용해줘"라고 지시하세요.

**카운팅 패턴**

AI가 카운팅 코드를 만들 때 나오는 패턴별로 품질이 다릅니다.

```python
words = ["python", "AI", "python", "코딩", "AI", "python"]

# AI가 자주 생성하는 verbose 패턴
counts = {}
for word in words:
    if word in counts:
        counts[word] = counts[word] + 1
    else:
        counts[word] = 1

# 더 Pythonic한 패턴
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1

# 가장 Pythonic한 패턴
from collections import Counter
counts = Counter(words)
# Counter({'python': 3, 'AI': 2, '코딩': 1})
```

AI에게 카운팅 코드를 요청할 때 "collections.Counter 써줘"라고 명시하면 가장 깔끔한 결과를 받습니다.

## Before / After

**Before — AI가 처음 생성한 중복 제거 + 멤버십 검사 코드**

```python
# 중복 제거
user_ids = [1001, 1002, 1001, 1003, 1002]
unique_ids = []
for uid in user_ids:
    if uid not in unique_ids:   # O(n) 매 반복
        unique_ids.append(uid)

# 검사
target = 1002
found = False
for uid in unique_ids:          # O(n) 매 검사
    if uid == target:
        found = True
        break
```

**After — 자료구조를 올바르게 선택한 버전**

```python
user_ids = [1001, 1002, 1001, 1003, 1002]

# set으로 한 번에 중복 제거 + O(1) 검사
unique_ids = set(user_ids)      # {1001, 1002, 1003}

target = 1002
found = target in unique_ids    # True, O(1)
```

AI에게 이렇게 프롬프트를 보내세요: "이 코드에서 멤버십 검사가 반복되는 부분을 찾아서 list를 set으로 바꿔서 O(1)으로 최적화해줘."

## 바이브코딩할 때 자주 하는 실수

| 실수 패턴 | AI 코드 예시 | 문제 | 올바른 방향 |
| --- | --- | --- | --- |
| list로 멤버십 검사 반복 | `if x in my_list` (루프 안에서) | O(n) × 반복 횟수 | set으로 변환 후 검사 |
| `=`로 list "복사" | `b = a; b.append(1)` | 원본도 변경됨 | `b = a[:]` 또는 `list(a)` |
| `d[key]`로 dict 접근 | `user["email"]` | KeyError | `user.get("email")` |
| set 순서 가정 | `list(my_set)[0]` | 순서 비보장 | `sorted(my_set)[0]` |
| set에 list를 원소로 | `{[1, 2], [3, 4]}` | TypeError (unhashable) | `{(1, 2), (3, 4)}` |
| `json.dumps(set(...))` | JSON 직렬화 시도 | TypeError | `list(my_set)` 변환 후 직렬화 |

## AI에게 이 주제 관련 질문하는 팁

**자료구조 선택 유도**

나쁜 프롬프트: "빠르게 만들어줘"

좋은 프롬프트: "이 코드에서 멤버십 검사가 자주 일어나. 블랙리스트 조회는 O(1)이 되도록 적합한 자료구조 써줘."

**카운팅/그루핑**

좋은 프롬프트: "단어 빈도를 세는 코드야. collections.Counter 쓰고, 상위 5개를 most_common()으로 뽑아줘."

**dict 안전 접근**

좋은 프롬프트: "이 함수에서 dict 접근을 모두 .get()으로 바꾸고, 키가 없을 때 반환할 기본값도 적절히 설정해줘."

**JSON 직렬화 문제**

AI가 set을 포함한 데이터를 `json.dumps()`로 직렬화하는 코드를 만들면: "json.dumps가 set을 직렬화 못해. set을 sorted list로 변환하는 커스텀 serializer 추가해줘."

## 운영 체크리스트

- [ ] 루프 안에서 `in list` 패턴이 반복되면 set으로 변환 최적화 요청
- [ ] `b = a` 후 한쪽만 수정하려는 코드에서 `b = a[:]`로 수정
- [ ] dict 접근 코드에서 `d[key]` 대신 `d.get(key)` 패턴 확인
- [ ] set을 JSON으로 직렬화하려는 코드에서 `list()` 변환 확인
- [ ] 카운팅/그루핑 코드에 `Counter`/`defaultdict` 사용 유도
- [ ] list comprehension이 세 줄 이상 중첩되면 일반 for 루프로 풀어달라고 요청

## 처음 질문으로 돌아가기

**AI가 list로 멤버십 검사를 만들었을 때, 언제 set으로 바꿔야 할까?**
검사 대상 리스트가 수백 건 이상이거나 루프 안에서 반복 검사가 일어난다면 즉시 set으로 교체를 요청하세요. 검색 비용이 O(n)에서 O(1)으로 바뀝니다.

**`=`로 리스트를 "복사"할 때 양쪽이 같이 바뀌는 이유는?**
Python의 변수는 값을 담는 상자가 아니라 객체에 붙는 이름표입니다. `b = a`는 같은 리스트 객체에 이름표를 하나 더 붙이므로 한쪽 변경이 양쪽에 반영됩니다. 진짜 복사는 `b = a[:]`입니다.

**dict에서 KeyError를 막으려면?**
`d.get(key)` (없으면 None 반환) 또는 `d.get(key, 기본값)`을 씁니다. "없으면 만들어라" 패턴은 `d.setdefault(key, 기본값)` 또는 `defaultdict`가 어울립니다.

**JSON으로 직렬화할 수 없는 자료구조는?**
`set`은 `json.dumps()`가 직렬화하지 못합니다. `list(my_set)` 또는 `sorted(my_set)`으로 변환 후 직렬화하세요.

**가장 Pythonic한 카운팅 코드를 AI에게 받으려면?**
"collections.Counter 써줘"라고 명시하거나, "Counter와 most_common() 메서드로 상위 N개 뽑는 코드 만들어줘"라고 요청하세요.

## 정리

바이브코딩에서 AI는 보통 리스트를 기본값으로 선택합니다. 그러나 "멤버십 검사가 반복된다 → set", "키-값 매핑이 필요하다 → dict", "변경이 없는 묶음이다 → tuple" 이 세 판단을 할 수 있으면 AI 코드를 훨씬 빠르게 개선할 수 있습니다. 자료구조 선택이 맞으면 코드 길이와 버그 수가 동시에 줄어듭니다.

## 참고 자료

### 공식 문서
- [Python 공식 문서 (python.org)](https://docs.python.org/3/)
- [Python Tutorial (python.org)](https://docs.python.org/3/tutorial/)

### 관련 시리즈
- [Python DB-API 101](../../python-dbapi-101/ko/)
- [Pytest 101](../../pytest-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 Python 기초 (1/10): 왜 Python이고, 어떻게 설치할까?](./01-why-python-and-install.md)
- [바이브코딩을 위한 Python 기초 (2/10): 변수, 타입, 연산자](./02-variables-types-operators.md)
- [바이브코딩을 위한 Python 기초 (3/10): 문자열과 포매팅](./03-strings-and-formatting.md)
- **바이브코딩을 위한 Python 기초 (4/10): list, tuple, set, dict (현재 글)**
- [바이브코딩을 위한 Python 기초 (5/10): 제어 흐름](./05-control-flow.md)
- [바이브코딩을 위한 Python 기초 (6/10): 함수와 인자](./06-functions-and-arguments.md)
- [바이브코딩을 위한 Python 기초 (7/10): 모듈과 패키지](./07-modules-and-packages.md)
- [바이브코딩을 위한 Python 기초 (8/10): 파일 I/O와 예외 처리](./08-file-io-and-exceptions.md)
- [바이브코딩을 위한 Python 기초 (9/10): 클래스와 객체](./09-classes-and-objects.md)
- [바이브코딩을 위한 Python 기초 (10/10): 표준 라이브러리 투어](./10-standard-library-tour.md)

<!-- toc:end -->
Tags: 바이브코딩, Python, AI코딩, 리스트, 딕셔너리, 자료구조선택, comprehension
