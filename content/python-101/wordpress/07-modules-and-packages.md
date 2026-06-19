---
title: "바이브코딩을 위한 Python 기초 (7/10): AI가 import한 모듈, 내 프로젝트에 어떻게 넣나"
series: python-101
episode: 7
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
- import
- 모듈
- 패키지구조
seo_description: "바이브코딩 시대, AI가 생성한 import 코드의 의미와 내 프로젝트에 적용하는 법. 모듈, 패키지, sys.path 완전 정리"
---

# 바이브코딩을 위한 Python 기초 (7/10): AI가 import한 모듈, 내 프로젝트에 어떻게 넣나

이 글은 바이브코딩을 위한 Python 기초 시리즈의 7번째 글입니다.

AI에게 코드를 만들어달라고 하면 파일 맨 위에 이런 줄들이 붙어 옵니다.

```python
from .utils import clean_text
from ..config import Settings
import pandas as pd
from myapp.db import get_connection
```

이걸 복붙해서 실행하면 이런 에러가 납니다.

```
ModuleNotFoundError: No module named 'myapp'
ImportError: attempted relative import beyond top-level package
```

AI에게 다시 물어보면 "패키지 구조가 맞아야 한다"고 합니다. 근데 패키지 구조가 뭔지 모르면 또 막힙니다.

더 흔한 상황은 이겁니다. AI가 만들어준 여러 파일을 어떤 폴더에 넣어야 하는지 모르겠고, 파일끼리 서로 불러쓰려고 하면 계속 에러가 나는 것입니다. `from .sibling import foo` 같은 상대 경로 import는 특히 헷갈립니다.

모듈과 패키지를 이해하면 AI가 만든 파일들을 올바른 구조로 배치하고, import 에러가 났을 때 스스로 해결할 수 있게 됩니다. 코드를 재사용하거나 프로젝트를 확장할 때도 AI에게 정확한 지시를 내릴 수 있습니다.

> AI가 만든 import 문은 "이 파일들이 어떤 관계로 연결돼야 하는지"를 알려주는 지도입니다.

---

## 이 글에서 다룰 문제

- AI가 만든 코드에 `from .utils import foo`가 있는데, `.`이 뭘 가리키나요?
- `ModuleNotFoundError`가 나면 어디서 문제가 생긴 건가요?
- `__init__.py` 파일은 왜 만들어야 하고, 무엇을 넣어야 하나요?
- AI가 만든 파일들을 폴더에 어떻게 배치해야 서로 import가 되나요?
- `if __name__ == "__main__":` 이 패턴은 왜 쓰는 건가요?

---

## AI 코드를 읽으려면 이것을 알아야

### 모듈은 `.py` 파일 하나

`math.py` 파일을 만들면 그게 `math` 모듈입니다. `import math`로 불러씁니다. AI가 만들어준 파일 하나하나가 다 모듈입니다.

**중요한 것:** 모듈은 처음 import될 때 위에서 아래로 한 번 실행됩니다. 두 번째 import는 이미 실행된 결과를 재사용합니다. 그래서 `print("loaded")`가 들어있는 모듈을 두 번 import해도 한 번만 출력됩니다.

### 패키지는 `__init__.py`가 있는 폴더

AI가 "프로젝트 구조는 이렇게 만드세요"라고 줄 때 이런 형태를 자주 씁니다.

```text
myapp/
    __init__.py       <- 이게 있어야 패키지
    cli.py
    db/
        __init__.py   <- 하위 패키지도 마찬가지
        connection.py
        queries.py
```

`__init__.py`가 없으면 그냥 폴더입니다. 있으면 Python이 "이건 패키지구나"라고 인식합니다. 내용은 비어있어도 됩니다.

### import 형태 네 가지 읽는 법

```python
import math                     # math 전체를 math라는 이름으로
from math import sqrt           # sqrt만 꺼내서
import numpy as np              # numpy를 np라는 별명으로
from .sibling import foo        # 같은 패키지 안의 형제 파일에서
```

특히 `.`(점)이 들어간 import가 혼란스럽습니다.

- `from .utils import foo` — 나와 같은 폴더의 `utils.py`에서 `foo`를 가져와
- `from ..config import Settings` — 한 폴더 위의 `config.py`에서 `Settings`를 가져와
- `from myapp.db import get_connection` — `myapp/db.py`에서 `get_connection`을 가져와

### `if __name__ == "__main__":` 이게 왜 있나

AI가 만든 파일 맨 아래에 자주 이 패턴이 있습니다.

```python
def main():
    print("실행됨")

if __name__ == "__main__":
    main()
```

이 파일을 `python myapp/cli.py`로 직접 실행하면 `main()`이 호출됩니다. 다른 파일에서 `import cli`로 불러올 때는 `main()`이 자동으로 실행되지 않습니다. 라이브러리 코드와 실행 코드를 한 파일에 함께 두는 표준 패턴입니다.

### AI가 만든 파일들, 어디에 놓아야 하나

AI가 이런 코드를 줬다고 가정합니다.

```python
# ai가 만든 파일 A
from .db import get_connection
from .tax import calculate_tax
```

`.db`와 `.tax`는 "나랑 같은 폴더에 있는 `db.py`와 `tax.py`"를 가리킵니다. 즉 이 파일들은 모두 같은 폴더 안에 있어야 하고, 그 폴더에는 `__init__.py`가 있어야 합니다.

```text
myapp/
    __init__.py    <- 없으면 relative import 에러
    cli.py         <- from .db import get_connection
    db.py
    tax.py
```

---

## Before / After

### AI가 만든 코드 — 한 파일에 다 몰아넣기

```python
# main.py — AI 초안
import sqlite3

def connect():
    return sqlite3.connect("app.db")

def calc_tax(amount):
    return round(amount * 0.1, 2)

def send_receipt(email, amount):
    print(f"receipt to {email}: {amount}")

def run():
    conn = connect()
    tax = calc_tax(100)
    send_receipt("a@b.c", 100 + tax)

if __name__ == "__main__":
    run()
```

이렇게 되면 나중에 세금 계산만 테스트하거나, DB 연결만 바꾸기가 어렵습니다.

### 바이브코딩으로 개선 — 책임별 모듈 분리

AI에게 이렇게 요청합니다: "이 코드를 역할별로 파일을 나눠줘. DB는 db.py, 세금 계산은 tax.py, 알림은 notify.py, 실행 진입점은 cli.py로."

```text
myapp/
    __init__.py
    cli.py
    db.py
    tax.py
    notify.py
```

```python
# myapp/tax.py
def calc_tax(amount: float) -> float:
    return round(amount * 0.1, 2)
```

```python
# myapp/cli.py
from .db import connect
from .tax import calc_tax
from .notify import send_receipt

def run():
    conn = connect()
    tax = calc_tax(100)
    send_receipt("a@b.c", 100 + tax)

if __name__ == "__main__":
    run()
```

`tax.py`는 DB와 전혀 무관하게 단독으로 테스트할 수 있습니다. 나중에 세금 계산 로직을 바꿔도 `tax.py`만 수정하면 됩니다.

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `__init__.py` 없이 relative import | `ImportError: attempted relative import` | 폴더에 빈 `__init__.py` 파일 만들기 |
| `python myapp/cli.py`로 실행하고 relative import | 패키지 컨텍스트 없이 실행돼 `.`이 동작 안 함 | `python -m myapp.cli`로 실행 |
| 파일 이름을 `json.py`, `math.py`로 지음 | 표준 라이브러리 모듈을 가려버림 | 표준 라이브러리와 겹치는 이름 피하기 |
| `from x import *` 사용 | 어디서 뭐가 들어왔는지 추적 불가 | 명시적으로 이름 나열하기 |
| 모듈 최상단에 무거운 작업 | import만 해도 시간이 걸림 | 함수 안으로 옮겨 필요할 때만 실행 |

---

## AI에게 이 주제 관련 질문하는 팁

**구조 요청:**
"이 기능들을 모듈로 분리해줘. 각 파일이 어떤 폴더에 있어야 하는지, `__init__.py`는 어디에 필요한지 폴더 구조도 보여줘."

**에러 해결:**
"이 에러가 났어: `ModuleNotFoundError: No module named 'myapp'`. 현재 프로젝트 구조는 이렇고, 실행 명령은 이거야. 뭐가 문제인지 설명해줘."

**import 설명 요청:**
"이 코드의 `from ..config import Settings`에서 `..`가 어떤 폴더를 가리키는지 현재 파일 위치를 기준으로 설명해줘."

**재사용 가능한 구조:**
"이 로직이 다른 프로젝트에서도 쓸 수 있게 패키지로 만들어줘. `pyproject.toml`도 같이 만들어줘."

---

## 운영 체크리스트

- [ ] AI가 만든 파일을 받으면 `from .xxx import` 패턴을 보고 폴더 구조를 짐작할 수 있다
- [ ] `__init__.py`가 필요한 위치를 파악해서 파일을 만들 수 있다
- [ ] `python -m myapp.cli` vs `python myapp/cli.py` 차이를 안다
- [ ] `ModuleNotFoundError`가 나면 `sys.path`와 파일 위치를 먼저 확인한다
- [ ] 파일 이름이 표준 라이브러리와 겹치는지 확인한다
- [ ] `if __name__ == "__main__":` 패턴이 있는 파일은 라이브러리이자 실행 스크립트임을 인식한다

---

## 처음 질문으로 돌아가기

**`from .utils import foo`의 `.`은 뭘 가리키나요?**
현재 파일이 속한 패키지 폴더입니다. `myapp/cli.py`에서 `from .utils import foo`라면 `myapp/utils.py`를 찾습니다.

**`ModuleNotFoundError`는 어디서 생긴 건가요?**
Python이 `sys.path`에 있는 폴더들을 순서대로 뒤지는데, 모듈이 거기 없는 겁니다. 실행 위치나 `__init__.py` 누락이 원인인 경우가 많습니다.

**`__init__.py`에는 뭘 넣어야 하나요?**
비어있어도 됩니다. 외부에서 쓸 함수를 `from .module import func` 형태로 모아두면 `from myapp import func`처럼 짧게 쓸 수 있어 편합니다.

**AI가 만든 파일들을 어떻게 배치하나요?**
`from .xxx import` 패턴을 보면 같은 폴더에 있어야 합니다. `from ..xxx import`면 한 단계 위 폴더입니다. 이걸 따라가면 폴더 구조가 나옵니다.

**`if __name__ == "__main__":`은 왜 쓰나요?**
직접 실행할 때는 코드가 실행되고, 다른 파일에서 import될 때는 실행되지 않게 하기 위해서입니다.

---

## 정리

모듈과 패키지를 이해하면 AI가 만든 파일들을 올바른 위치에 배치하고 서로 연결할 수 있습니다. `from .sibling import foo` 같은 패턴이 더 이상 무서운 주문이 아니라 "같은 폴더의 파일에서 가져와"라는 명확한 지시로 읽힙니다.

프로젝트가 커질수록 책임별로 파일을 나누는 구조가 중요해집니다. AI에게 처음부터 "역할별로 파일을 분리해줘"라고 요청하면 나중에 유지보수가 훨씬 쉬워집니다.

다음 편에서는 AI가 만든 파일 처리 코드에서 에러 핸들링이 빠져있을 때 어떻게 대처하는지를 다룹니다.

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
- **바이브코딩을 위한 Python 기초 (7/10): 모듈과 패키지 (현재 글)**
- [바이브코딩을 위한 Python 기초 (8/10): 파일 I/O와 예외 처리](./08-file-io-and-exceptions.md)
- [바이브코딩을 위한 Python 기초 (9/10): 클래스와 객체](./09-classes-and-objects.md)
- [바이브코딩을 위한 Python 기초 (10/10): 표준 라이브러리 투어](./10-standard-library-tour.md)

<!-- toc:end -->
Tags: 바이브코딩, Python, AI코딩, import, 모듈, 패키지구조
