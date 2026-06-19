---
title: "바이브코딩을 위한 Python 기초 (10/10): AI에게 시키기 전에 표준 라이브러리로 이미 되는지 먼저 확인"
series: python-101
episode: 10
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
- 표준라이브러리
- datetime
- pathlib
- collections
seo_description: "바이브코딩 시대, 외부 패키지 없이 표준 라이브러리로 해결하는 법. datetime, pathlib, json, Counter, itertools 완전 정리"
---

# 바이브코딩을 위한 Python 기초 (10/10): AI에게 시키기 전에 표준 라이브러리로 이미 되는지 먼저 확인

이 글은 바이브코딩을 위한 Python 기초 시리즈의 마지막 글입니다.

AI에게 "날짜 계산하는 코드 만들어줘"라고 하면 가끔 이런 코드가 돌아옵니다.

```bash
pip install arrow
```

```python
import arrow

now = arrow.now()
next_week = now.shift(weeks=1)
print(next_week.format("YYYY-MM-DD"))
```

`arrow`는 편리한 라이브러리지만, 이걸 쓰면 `requirements.txt`에 하나 더 생깁니다. 나중에 패키지 버전 충돌이 날 수도 있고, 배포 환경에서 설치가 안 될 수도 있습니다. 그런데 사실 이 정도는 표준 라이브러리의 `datetime`으로 충분히 됩니다.

```python
from datetime import date, timedelta

next_week = date.today() + timedelta(weeks=1)
print(next_week.strftime("%Y-%m-%d"))
```

바이브코딩을 잘 한다는 건 AI를 잘 쓴다는 것만이 아닙니다. "이건 굳이 AI 안 써도 되는데"를 알아보는 눈도 포함됩니다. 표준 라이브러리를 알면 AI에게 더 정확하게 물어볼 수 있고, AI가 불필요한 외부 패키지를 쓸 때 "표준 라이브러리로 바꿔줘"라고 요청할 수 있습니다.

표준 라이브러리의 핵심 모듈 다섯 개만 알아도 일상적인 바이브코딩 작업의 상당 부분을 커버할 수 있습니다.

> 외부 패키지를 설치하기 전에 항상 "표준 라이브러리로 되지 않나?"를 먼저 물어보세요.

---

## 이 글에서 다룰 문제

- 날짜 계산, 날짜 포맷 변환 — `datetime`이면 충분한가요?
- 파일 경로 처리에 `os.path.join()` 대신 더 좋은 방법이 있나요?
- JSON 파일을 읽고 쓰는 코드, AI 없이 짤 수 있나요?
- 리스트에서 빈도를 세거나 그룹을 묶을 때 `for` 루프 없이 되는 방법이 있나요?
- 여러 리스트를 합치거나 조합을 만들 때 표준 라이브러리로 가능한가요?

---

## AI에게 시키기 전에 먼저 알아야 할 다섯 모듈

### `datetime` — 날짜와 시간

날짜 계산, 포맷 변환, 날짜 차이 계산은 전부 `datetime`으로 됩니다.

```python
from datetime import date, datetime, timedelta

# 오늘 날짜
today = date.today()          # datetime.date(2026, 6, 17)

# 날짜 차이 계산
next_week = today + timedelta(weeks=1)
deadline = date(2026, 12, 31) - today
print(deadline.days)          # 몇 일 남았는지

# 포맷 변환
formatted = datetime.now().strftime("%Y년 %m월 %d일")
print(formatted)              # "2026년 06월 17일"

# 문자열 → datetime 객체
parsed = datetime.strptime("2026-06-17", "%Y-%m-%d")
```

**AI에게 물어볼 게 없는 경우:**
- "오늘부터 30일 후 날짜 구하기" → `date.today() + timedelta(days=30)`
- "날짜를 한국식 포맷으로 출력" → `strftime("%Y년 %m월 %d일")`
- "두 날짜 사이 일수 계산" → `(date2 - date1).days`

**AI에게 물어봐야 하는 경우:**
- 타임존 처리 (서울 시간 ↔ UTC 변환)
- 복잡한 날짜 패턴 파싱

### `pathlib` — 파일 경로

경로 처리의 모든 것입니다. `os.path.join()`보다 훨씬 직관적입니다.

```python
from pathlib import Path

# 경로 합치기
data_dir = Path("data")
input_file = data_dir / "input.csv"   # data/input.csv

# 현재 사용자 홈 디렉터리
home = Path.home()
config = home / ".myapp" / "config.json"

# 파일 정보
p = Path("report.csv")
print(p.name)     # "report.csv"
print(p.stem)     # "report"
print(p.suffix)   # ".csv"
print(p.parent)   # "."

# 파일 읽기/쓰기 (짧은 파일)
text = Path("notes.txt").read_text(encoding="utf-8")
Path("output.txt").write_text("결과\n", encoding="utf-8")

# 폴더 만들기
Path("logs/2026/06").mkdir(parents=True, exist_ok=True)

# 파일 목록
for csv_file in Path("data").glob("*.csv"):
    print(csv_file)
```

**AI에게 `os.path` 대신 `pathlib`를 요청할 수 있습니다:**
"이 코드의 경로 처리를 `os.path.join()` 대신 `pathlib.Path`를 써서 다시 작성해줘."

### `json` — 직렬화와 역직렬화

설정 파일 읽기, API 응답 처리, 데이터 저장 — 다 `json`으로 됩니다.

```python
import json

# dict → JSON 문자열
data = {"name": "Ada", "score": 95, "tags": ["python", "ai"]}
json_str = json.dumps(data, ensure_ascii=False, indent=2)
print(json_str)
# {
#   "name": "Ada",
#   "score": 95,
#   "tags": ["python", "ai"]
# }

# JSON 문자열 → dict
loaded = json.loads(json_str)
print(loaded["name"])  # "Ada"

# 파일에 쓰기
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

# 파일에서 읽기
with open("data.json", encoding="utf-8") as f:
    config = json.load(f)
```

**주의:** `ensure_ascii=False`를 빠뜨리면 한글이 `\uD55C\uAE00` 형태로 저장됩니다.

**AI 코드에서 자주 보는 패턴:**

```python
import json
from pathlib import Path

# 한 줄로 설정 파일 읽기
config = json.loads(Path("config.json").read_text(encoding="utf-8"))
```

### `collections` — 더 강력한 컨테이너

반복문을 줄여주는 세 가지 도구입니다.

**Counter — 빈도 세기**

```python
from collections import Counter

words = ["apple", "banana", "apple", "cherry", "banana", "apple"]
counts = Counter(words)
print(counts)              # Counter({'apple': 3, 'banana': 2, 'cherry': 1})
print(counts.most_common(2))  # [('apple', 3), ('banana', 2)]

# 에러 로그 분석
errors = ["TimeoutError", "ConnectionError", "TimeoutError", "ValueError"]
print(Counter(errors).most_common())
```

**defaultdict — 키 없을 때 기본값 자동 생성**

```python
from collections import defaultdict

# 카테고리별 그룹핑
items = [("python", "book"), ("ai", "course"), ("python", "video"), ("ai", "book")]
grouped = defaultdict(list)
for category, item in items:
    grouped[category].append(item)

print(dict(grouped))
# {'python': ['book', 'video'], 'ai': ['course', 'book']}
```

**deque — 빠른 양방향 큐**

```python
from collections import deque

# 최근 N개만 유지
recent = deque(maxlen=5)
for i in range(10):
    recent.append(i)
print(list(recent))  # [5, 6, 7, 8, 9]
```

### `itertools` — 반복 패턴 압축

복잡한 반복 로직을 한 줄로 만들어줍니다.

```python
from itertools import chain, combinations, product, groupby

# 여러 리스트 합치기
list1 = [1, 2, 3]
list2 = [4, 5, 6]
combined = list(chain(list1, list2))  # [1, 2, 3, 4, 5, 6]

# 조합 만들기
teams = list(combinations(["A", "B", "C", "D"], 2))
# [('A','B'), ('A','C'), ('A','D'), ('B','C'), ('B','D'), ('C','D')]

# 경우의 수 (데카르트 곱)
sizes = ["S", "M", "L"]
colors = ["red", "blue"]
variants = list(product(sizes, colors))
# [('S','red'), ('S','blue'), ('M','red'), ...]

# 그룹핑 (정렬 후 사용 필수)
data = sorted([("A", 1), ("B", 2), ("A", 3)], key=lambda x: x[0])
for key, group in groupby(data, key=lambda x: x[0]):
    print(key, list(group))
```

---

## Before / After

### AI가 외부 패키지로 짠 코드

```bash
# AI 초안 — 외부 패키지 3개 필요
pip install pandas numpy tabulate
```

```python
import pandas as pd
import numpy as np
from tabulate import tabulate

words = ["apple", "banana", "apple", "cherry"]
df = pd.Series(words).value_counts().reset_index()
df.columns = ["word", "count"]
print(tabulate(df, headers="keys"))
```

### 표준 라이브러리만으로

```python
from collections import Counter

words = ["apple", "banana", "apple", "cherry"]
counts = Counter(words)
print(f"{'단어':<10} {'빈도':>5}")
print("-" * 16)
for word, count in counts.most_common():
    print(f"{word:<10} {count:>5}")
```

AI에게 요청: "이 코드를 pandas 없이 표준 라이브러리만 써서 다시 작성해줘."

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `ensure_ascii=False` 빠뜨리기 | 한글이 유니코드 escape로 저장 | `json.dumps(data, ensure_ascii=False)` |
| `datetime.now()` 시간대 무시 | 서버-클라이언트 시간 불일치 | `datetime.now(timezone.utc)` 사용 |
| `groupby` 정렬 없이 사용 | 같은 키가 여러 그룹으로 분리 | `sorted()` 후 `groupby` 사용 |
| `itertools` 결과 두 번 순회 | 이터레이터는 한 번만 소비됨 | `list(...)` 로 먼저 변환 |
| `defaultdict(list())` — `()` 붙이기 | `TypeError` 발생 | `defaultdict(list)` — 함수 참조만 전달 |

---

## AI에게 이 주제 관련 질문하는 팁

**외부 패키지 대체 요청:**
"이 코드를 `requests` 없이 `urllib.request`로 바꿔줘." / "pandas 없이 표준 라이브러리만 써서 CSV를 처리하는 코드로 바꿔줘."

**표준 라이브러리 추천 요청:**
"단어 빈도를 세야 하는데 표준 라이브러리 중 뭘 쓰면 좋을지 추천해줘."

**복잡한 표준 라이브러리 활용:**
"로그 파일에서 에러 종류별 빈도를 세고 JSON으로 저장하는 코드를 `pathlib`, `collections.Counter`, `json`만 써서 만들어줘."

**날짜 처리:**
"`arrow` 없이 `datetime`만으로 한국 시간 기준으로 오늘 자정을 구하는 코드 만들어줘."

---

## 운영 체크리스트

- [ ] 날짜 계산이 필요하면 `datetime + timedelta`를 먼저 떠올린다
- [ ] 경로 합치기에 문자열 `+` 대신 `pathlib.Path / "subdir"` 패턴을 쓴다
- [ ] JSON 읽기/쓰기는 `json.load(f)` / `json.dump(data, f)` 형태를 안다
- [ ] 빈도 세기는 `Counter()`, 그룹핑은 `defaultdict(list)`, 큐는 `deque`를 쓴다
- [ ] AI가 외부 패키지를 쓰면 "표준 라이브러리로 대체 가능한지" 먼저 확인한다
- [ ] `itertools` 결과는 한 번만 소비되는 이터레이터임을 안다

---

## 처음 질문으로 돌아가기

**날짜 계산에 `arrow` 같은 패키지 없이 되나요?**
대부분의 날짜 계산은 `datetime` + `timedelta`로 됩니다. 타임존이 복잡한 경우에만 추가 패키지를 고려하면 됩니다.

**`os.path.join()` 대신 더 좋은 방법은?**
`pathlib.Path`의 `/` 연산자입니다. `Path("data") / "input.csv"`처럼 씁니다. 운영체제 구분자를 자동 처리하고, `read_text()`, `write_text()` 같은 편의 메서드도 씁니다.

**빈도를 세려면 `for` 루프를 써야 하나요?**
`Counter(리스트)`로 한 줄에 됩니다. `most_common(n)`으로 상위 N개도 바로 뽑을 수 있습니다.

**여러 리스트 합치기 — `+` 말고 다른 방법이 있나요?**
`list(chain(list1, list2, list3))`로 됩니다. `+`는 새 리스트를 매번 만들지만 `chain`은 이터레이터라 메모리 효율적입니다.

---

## 정리

표준 라이브러리는 설치 없이 즉시 쓸 수 있고, Python 버전만 맞으면 동일하게 동작합니다. 외부 패키지 의존성이 없으니 배포도 단순합니다.

바이브코딩에서 AI를 잘 쓰는 것과 더불어, "이건 AI 없이도 표준 라이브러리로 되는 것"을 알아보는 눈이 생기면 더 가볍고 유지보수하기 쉬운 코드를 만들 수 있습니다.

`datetime`으로 날짜 계산, `pathlib`로 경로 처리, `json`으로 직렬화, `Counter`로 빈도 세기, `defaultdict`로 그룹핑. 이 다섯 가지 패턴을 손에 익혀두면 일상적인 바이브코딩 작업의 절반은 AI 없이도 금방 짤 수 있습니다.

Python 기초 시리즈를 마칩니다. 함수, 모듈, 파일 처리, 클래스, 표준 라이브러리. 이 다섯 편에서 다룬 내용이 앞으로 AI와 함께 Python으로 무언가를 만들 때의 기반이 됩니다.

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
- [바이브코딩을 위한 Python 기초 (4/10): list, tuple, set, dict](./04-list-tuple-set-dict.md)
- [바이브코딩을 위한 Python 기초 (5/10): 제어 흐름](./05-control-flow.md)
- [바이브코딩을 위한 Python 기초 (6/10): 함수와 인자](./06-functions-and-arguments.md)
- [바이브코딩을 위한 Python 기초 (7/10): 모듈과 패키지](./07-modules-and-packages.md)
- [바이브코딩을 위한 Python 기초 (8/10): 파일 I/O와 예외 처리](./08-file-io-and-exceptions.md)
- [바이브코딩을 위한 Python 기초 (9/10): 클래스와 객체](./09-classes-and-objects.md)
- **바이브코딩을 위한 Python 기초 (10/10): 표준 라이브러리 투어 (현재 글)**

<!-- toc:end -->
Tags: 바이브코딩, Python, AI코딩, 표준라이브러리, datetime, pathlib, collections
