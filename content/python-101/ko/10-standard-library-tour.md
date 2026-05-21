---
title: "Python 101 (10/10): 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools"
series: python-101
episode: 10
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- standard-library
- datetime-module
- pathlib-module
- json-module
- collections-module
- itertools-module
last_reviewed: '2026-05-12'
seo_description: 표준 라이브러리는 "자주 쓰는 일을 두 번 짜지 않게 하는 도구함"이며, 각 모듈은 한 가지 도메인(시간·경로·직렬화·집계·반복)에
  한정해…
---

# Python 101 (10/10): 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools

표준 라이브러리는 자주 쓰는 일을 두 번 짜지 않게 해 주는 도구함입니다. 각 모듈은 시간, 경로, 직렬화, 집계, 반복처럼 한 가지 도메인에 집중합니다.

이 글은 Python 101 시리즈의 마지막 글입니다.

## 먼저 던지는 질문

- 외부 의존성을 줄일 수 있습니다.** 작은 스크립트에 패키지를 추가하기 전에 표준 라이브러리부터 살펴보면, requirements 파일을 더 가볍게 유지할 수 있습니다?
- 코드가 짧고 익숙해집니다.** 다른 Python 개발자도 같은 도구를 알고 있으므로 리뷰가 빨라집니다?
- 버전 관리가 단순합니다.** Python 인터프리터 버전만 맞추면 동일한 동작을 기대할 수 있습니다?

## 큰 그림

![Python 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-101/10/10-01-mental-model.ko.png)

*Python 101 10장 흐름 개요*

이 그림에서는 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 멘탈 모델

> 표준 라이브러리는 "자주 쓰는 일을 두 번 짜지 않게 하는 도구함"이며, 각 모듈은 한 가지 도메인(시간·경로·직렬화·집계·반복)에 한정해 작은 어휘 세트를 제공합니다.
표준 라이브러리는 용도별로 나뉘어 있습니다. 시간과 날짜는 `datetime`, 파일 경로는 `pathlib`, 데이터 직렬화는 `json`, 더 풍부한 자료 구조는 `collections`, 반복 패턴은 `itertools`가 담당합니다.

각 모듈은 "특정 종류의 문제 한 가지"를 잘 풀도록 설계돼 있습니다. 모듈 이름만 봐도 어떤 문제를 다룰지 짐작할 수 있도록 명명돼 있는 점이 표준 라이브러리의 일관된 특징입니다.

## 핵심 개념

- **`datetime` 객체**: 날짜(`date`), 시간(`time`), 둘을 합친 `datetime`, 시간 간격(`timedelta`)을 표현합니다. `datetime`은 시간대(`tzinfo`)를 함께 가질 수 있습니다.
- **`pathlib.Path`**: 경로를 문자열이 아니라 객체로 다룹니다. `/` 연산자로 경로를 이어 붙이고, `.exists()`, `.read_text()`, `.glob()` 같은 메서드를 직접 호출합니다.
- **`json.dumps`/`json.loads`**: Python 객체와 JSON 문자열 사이를 변환합니다. dict, list, str, int, float, bool, None은 직접 변환되며, 그 외 타입은 직렬화 규칙을 직접 정해야 합니다.
- **`Counter`**: 요소의 출현 빈도를 세는 dict의 하위 클래스입니다.
- **`defaultdict`**: 키가 없을 때 호출할 기본값 팩토리를 미리 등록한 dict입니다.
- **`deque`**: 양쪽 끝에서 `O(1)`로 추가·제거가 가능한 자료 구조입니다.
- **`itertools`**: 반복 가능한 객체(iterable)를 변환·결합·잘라 주는 함수 모음입니다. 결과는 lazy한 이터레이터로 돌아옵니다.

## 전후 비교

다음은 단어 빈도를 세는 코드입니다.

**Before**

```python
def word_counts(words):
    counts = {}
    for w in words:
        if w in counts:
            counts[w] += 1
        else:
            counts[w] = 1
    return counts
```

직접 dict를 다루다 보면 키가 있는지 한 번씩 확인하는 분기가 필요합니다.

**After**

```python
from collections import Counter

def word_counts(words):
    return Counter(words)
```

세 가지 변화가 있습니다.

- 키 존재 여부를 검사하는 분기가 사라졌습니다.
- `Counter`는 `most_common(n)` 같은 메서드를 그대로 제공합니다.
- 결과 객체는 dict의 하위 클래스이므로 기존 dict 인터페이스와 호환됩니다.

## 단계별 실습

REPL을 켜고 한 줄씩 따라가 보세요. `>>>`로 시작하는 블록은 REPL 전사이고, 그 외 코드 블록은 설명용 예시입니다.

### 1. `datetime`으로 오늘과 지금 다루기

```text
>>> from datetime import date, datetime, timedelta
>>> date.today()
datetime.date(2026, 5, 3)
>>> datetime.now()
datetime.datetime(2026, 5, 3, 14, 30, 0, 123456)
>>> date(2026, 12, 25) - date.today()
datetime.timedelta(days=236)
>>> (datetime(2026, 5, 3, 14, 30) + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")
'2026-05-03 16:30'
```

`strftime`으로 출력 형식을 정하고, 반대로 문자열을 객체로 바꿀 때는 `strptime`을 사용합니다. 사용자 입력은 형식이 바뀌기 쉬우므로 입력 단계에서 한 번 파싱한 뒤 객체로 다루는 편이 안전합니다.

### 2. `pathlib`로 경로 다루기

```text
>>> from pathlib import Path
>>> p = Path("docs") / "intro.md"
>>> p
PosixPath('docs/intro.md')
>>> p.suffix
'.md'
>>> p.stem
'intro'
>>> p.parent
PosixPath('docs')
```

`Path` 객체는 문자열과 다르게 운영체제 차이를 흡수합니다. `Path("a") / "b"`는 Linux에서는 `a/b`, Windows에서는 `a\b`로 만들어집니다. 그 결과 슬래시 처리 코드를 직접 짤 일이 줄어듭니다.

### 3. `json`으로 직렬화·역직렬화

```text
>>> import json
>>> data = {"name": "Ada", "tags": ["math", "logic"]}
>>> s = json.dumps(data, ensure_ascii=False)
>>> s
'{"name": "Ada", "tags": ["math", "logic"]}'
>>> json.loads(s) == data
True
```

`ensure_ascii=False`를 주면 한글처럼 비ASCII 문자가 그대로 보입니다. 파일에 직접 쓰고 싶다면 `json.dump(data, f)`, 읽을 때는 `json.load(f)`를 사용합니다.

### 4. `Counter`로 빈도 세기

```text
>>> from collections import Counter
>>> Counter("banana")
Counter({'a': 3, 'n': 2, 'b': 1})
>>> Counter(["red", "blue", "red", "green", "blue", "red"]).most_common(2)
[('red', 3), ('blue', 2)]
```

문자열을 넘기면 글자 단위로, 리스트를 넘기면 요소 단위로 셉니다. `most_common(n)`은 빈도가 높은 순서로 `n`개를 돌려줍니다.

### 5. `defaultdict`로 그룹 만들기

```text
>>> from collections import defaultdict
>>> groups = defaultdict(list)
>>> for word in ["ant", "ape", "bee", "bat"]:
...     groups[word[0]].append(word)
...
>>> dict(groups)
{'a': ['ant', 'ape'], 'b': ['bee', 'bat']}
```

키가 없을 때 자동으로 빈 리스트를 만들어 주므로 `if key not in d` 분기가 사라집니다.

### 6. `itertools`로 반복 압축하기

```text
>>> from itertools import chain, groupby, combinations
>>> list(chain([1, 2], [3, 4]))
[1, 2, 3, 4]
>>> [(k, list(g)) for k, g in groupby("aaabbc")]
[('a', ['a', 'a', 'a']), ('b', ['b', 'b']), ('c', ['c'])]
>>> list(combinations(["A", "B", "C"], 2))
[('A', 'B'), ('A', 'C'), ('B', 'C')]
```

`groupby`는 인접한 같은 값만 묶는다는 점에 주의해야 합니다. 정렬되지 않은 입력은 먼저 `sorted()`를 거쳐야 의도한 그룹이 만들어집니다.

## 이 코드에서 주목할 점

- **`Counter(words)`** — 한 줄로 빈도 집계가 끝납니다. 내부적으로 dict의 하위 클래스이므로 기존 dict 인터페이스(`d[k]`, `for k in d`)는 그대로 쓸 수 있습니다.
- **`Path("docs") / "intro.md"`** — `/` 연산자가 운영체제 구분자를 흡수합니다. Linux/Windows 차이를 직접 처리하지 않아도 동일하게 동작합니다.
- **`json.dumps(..., ensure_ascii=False)`** — 기본값은 비ASCII를 `\uXXXX`로 돌립니다. 한글을 그대로 보고 싶다면 이 옵션을 명시적으로 지정합니다.
- **`defaultdict(list)`** — 팔토리 자리에 `list`를 넓습니다(호출하지 않음). 키가 없을 때 빈 리스트를 자동 생성해 `if k not in d` 분기를 제거합니다.
- **`groupby` 앞의 정렬** — `groupby`는 인접한 같은 값만 묶습니다. 정렬되지 않은 입력은 `sorted()`를 먼저 거쳐야 의도한 그룹이 만들어집니다.

## 자주 하는 실수

- **`datetime.now()`와 `utcnow()`를 섞어 쓰기** — 둘 다 시간대 정보가 없는 naive 객체를 돌려줍니다. 시간대를 신경 써야 한다면 `datetime.now(timezone.utc)`처럼 `tzinfo`를 명시하세요.
- **`pathlib.Path`를 문자열 인자에 그대로 넘기기** — 일부 외부 API는 문자열만 받습니다. `str(path)`로 명시적으로 변환하면 디버깅이 쉬워집니다.
- **`json.dumps`로 한글이 `\uXXXX`로 보임** — `ensure_ascii=False`를 깜빡한 경우입니다. 파일이나 로그에 그대로 보고 싶다면 옵션을 켜 두세요.
- **`Counter`의 결과를 dict로 가정해 키 순서에 의존** — `most_common()`을 거치지 않은 결과는 빈도순 정렬이 보장되지 않습니다. 정렬이 필요하면 `most_common()`을 사용하세요.
- **`defaultdict`의 팩토리 함수에 `()`를 붙이기** — `defaultdict(list)`가 맞는 형태입니다. `defaultdict(list())`라고 쓰면 빈 리스트 한 개가 팩토리 자리에 들어가 `TypeError`가 납니다.
- **`groupby`에 정렬 안 된 입력을 그대로 넘기기** — 인접한 값만 묶이므로 같은 키가 여러 그룹으로 쪼개집니다.
- **`itertools` 결과를 두 번 순회하기** — 이터레이터는 한 번 소비되면 비어 버립니다. 두 번 보고 싶다면 `list(...)`로 먼저 모아 두세요.

## 실무에서는 이렇게 생각합니다

표준 라이브러리는 작은 도우미가 많아 자주 쓰이는 자리도 함께 알아 두면 좋습니다.

- **로그 파일 정리**: `pathlib`로 디렉터리를 순회하고, `datetime`으로 파일명에 들어 있는 날짜를 파싱한 뒤, 오래된 파일을 분리합니다.
- **간단한 설정 파일**: 외부 의존성 없이 설정을 저장할 때 `json` 파일이면 충분합니다. 사람이 직접 손으로 수정할 일이 잦다면 주석을 지원하는 다른 형식(YAML 등)을 검토할 수 있습니다.
- **로그 분석**: `Counter`로 상위 에러 메시지를, `defaultdict(list)`로 사용자별 요청을 묶어 보는 식으로 빠르게 통계를 뽑을 수 있습니다.
- **중복 작업 큐**: `deque`로 양쪽 끝에서 빠르게 넣고 빼며 작업을 처리합니다. `popleft()`는 list의 `pop(0)`보다 큰 입력에서 빠릅니다.
- **데이터 페어링**: `itertools.combinations`나 `product`로 후보 쌍을 만들어 테스트 케이스를 자동으로 펼치는 식으로 활용합니다.

표준 라이브러리에 손이 익을수록 작은 스크립트의 분량이 짧아집니다. 동시에 읽는 사람도 같은 모듈에 익숙하므로 리뷰 시간이 줄어듭니다.

## 체크리스트

- [ ] `datetime`, `date`, `timedelta`로 날짜 계산을 한 줄로 표현할 수 있습니다.
- [ ] `pathlib.Path`의 `/` 연산자, `.suffix`, `.stem`, `.parent`를 사용할 수 있습니다.
- [ ] `json.dumps`/`loads`와 `json.dump`/`load`의 차이를 설명할 수 있습니다.
- [ ] `Counter`, `defaultdict(list)`, `deque`를 적절한 상황에 골라 쓸 수 있습니다.
- [ ] `itertools.chain`, `groupby`, `combinations`의 동작을 한 문장씩으로 설명할 수 있습니다.
- [ ] 이터레이터가 한 번만 소비된다는 사실을 코드에서 의식할 수 있습니다.

## 정리·다음 글

- `datetime`은 날짜·시간 계산을 객체 단위로 다루게 해 줍니다. 시간대 처리는 따로 신경 쓸 부분이 많습니다.
- `pathlib`은 경로를 문자열이 아닌 객체로 다루어, OS 차이와 슬래시 처리 부담을 줄여 줍니다.
- `json`은 dict 중심의 데이터를 외부에 보관할 때 가장 가볍게 쓰는 직렬화 방식입니다.
- `collections`의 `Counter`, `defaultdict`, `deque`는 dict와 list의 빈자리를 채워 줍니다.
- `itertools`는 반복 패턴을 짧게 표현하지만, 결과가 lazy 이터레이터라는 점을 의식해야 합니다.

이번 글로 Python 101 시리즈가 마무리됩니다. 여기서 다룬 함수, 모듈, 클래스, 표준 라이브러리는 이후 다른 시리즈(예: `python-dbapi-101`, `sqlalchemy-101`)에서 그대로 다시 쓰입니다. 다음 시리즈에서는 표준 라이브러리에서 시작해, 외부 패키지로 자연스럽게 영역을 넓혀 갑니다.

## 실전 앵커: 표준 라이브러리 조합으로 작은 도구 만들기

표준 라이브러리의 진짜 가치는 "각 모듈을 아는 것"보다 "여러 모듈을 묶어 문제를 끝내는 것"입니다. 여기서는 로그 파일 요약 도구를 예시로 모듈 조합을 보겠습니다.

```python
from pathlib import Path
from collections import Counter
import csv
import json

root = Path('logs')
counter = Counter()

for file in root.glob('*.csv'):
    with file.open(encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            counter[row['level']] += 1

summary = {'total': sum(counter.values()), 'by_level': dict(counter)}
Path('summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
```

`pathlib + csv + collections + json`만으로도 운영에 바로 쓸 수 있는 수준의 유틸리티가 나옵니다.

날짜/시간은 `datetime`과 `zoneinfo`를 같이 쓰는 습관을 들이는 편이 좋습니다.

```python
from datetime import datetime
from zoneinfo import ZoneInfo

now = datetime.now(ZoneInfo('Asia/Seoul'))
print(now.isoformat())
```

타임존 없는 naive datetime을 남기면 로그 상관 분석이 매우 어려워집니다.

정규식은 최소한의 안전장치를 붙여 사용합니다.

```python
import re

pat = re.compile(r'^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$')
print(bool(pat.match('dev@example.com')))
```

`subprocess`를 쓸 때는 쉘 문자열 결합보다 리스트 인자 전달을 기본으로 둡니다.

```python
import subprocess

result = subprocess.run(['python', '--version'], capture_output=True, text=True, check=True)
print(result.stdout.strip())
```

보안과 이식성 모두에서 더 안전합니다.

벤치마크 예시도 하나 넣겠습니다.

```python
import timeit

sort_t = timeit.timeit('sorted(data)', setup='import random; data=[random.randint(1,1000000) for _ in range(10000)]', number=300)
heap_t = timeit.timeit('import heapq; h=data[:]; heapq.heapify(h); [heapq.heappop(h) for _ in range(10000)]', setup='import random; data=[random.randint(1,1000000) for _ in range(10000)]', number=300)
print(sort_t, heap_t)
```

전체 정렬이 필요한지, 상위 K개만 필요한지에 따라 선택이 달라진다는 사실을 체감할 수 있습니다.

패키징 관점의 마무리 예시로 `argparse` 기반 CLI 스켈레톤을 보면 표준 라이브러리만으로 배포 가능한 도구를 만들 수 있습니다.

```python
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True)
    args = parser.parse_args()
    print('input:', args.input)

if __name__ == '__main__':
    main()
```

`pyproject.toml`에 console script 엔트리를 추가하면 팀 내부 유틸리티를 일관된 방식으로 실행할 수 있습니다.

```toml
[project.scripts]
log-summary = "myapp.cli:main"
```

표준 라이브러리 학습은 "외부 라이브러리 없이 어디까지 가능한가"를 체험하는 과정입니다. 이 감각을 가져가면 의존성 선택도 훨씬 보수적이고 안정적으로 할 수 있습니다.

### 추가 실습: 표준 라이브러리만으로 만드는 진단 CLI

외부 의존성 없이도 진단 도구를 충분히 만들 수 있습니다. 예를 들어 디렉터리의 파일 수와 총 바이트를 계산하는 CLI는 `argparse`와 `pathlib`만으로 구현됩니다.

```python
from pathlib import Path
import argparse

def scan(root: Path):
    files = [p for p in root.rglob('*') if p.is_file()]
    total = sum(p.stat().st_size for p in files)
    return len(files), total

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('root')
    args = parser.parse_args()
    count, total = scan(Path(args.root))
    print(f'files={count} bytes={total}')

if __name__ == '__main__':
    main()
```

출력 예시:

```text
files=128 bytes=4092312
```

운영 자동화에서는 `shutil`, `zipfile`, `tempfile`도 자주 같이 사용됩니다.

- `shutil.copytree`: 디렉터리 복사
- `zipfile.ZipFile`: 압축/해제
- `tempfile.TemporaryDirectory`: 임시 작업공간 관리

이 조합은 배포 아티팩트 정리, 로그 번들링, 백업 스크립트 작성에서 바로 활용할 수 있습니다.

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

표준 라이브러리 학습의 마지막 기준은 간단합니다. 새로운 의존성을 추가하기 전에, 먼저 표준 라이브러리로 문제를 해결할 수 있는지 확인합니다. 이 습관이 프로젝트의 장기 유지보수 비용을 크게 낮춥니다.

추가 팁: 팀 내 스크립트는 표준 라이브러리 우선 원칙을 두고, 외부 패키지는 명확한 필요가 생길 때만 도입하면 배포·보안·업그레이드 부담을 크게 낮출 수 있습니다.

## 처음 질문으로 돌아가기

- **외부 의존성을 줄일 수 있습니다.** 작은 스크립트에 패키지를 추가하기 전에 표준 라이브러리부터 살펴보면, requirements 파일을 더 가볍게 유지할 수 있습니다?**
  - 본문의 기준은 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **코드가 짧고 익숙해집니다.** 다른 Python 개발자도 같은 도구를 알고 있으므로 리뷰가 빨라집니다?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **버전 관리가 단순합니다.** Python 인터프리터 버전만 맞추면 동일한 동작을 기대할 수 있습니다?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python 101 (1/10): 왜 Python인가, 그리고 설치와 venv](./01-why-python-and-install.md)
- [Python 101 (2/10): 변수, 타입, 연산자](./02-variables-types-operators.md)
- [Python 101 (3/10): 문자열과 포매팅](./03-strings-and-formatting.md)
- [Python 101 (4/10): list, tuple, set, dict](./04-list-tuple-set-dict.md)
- [Python 101 (5/10): 제어 흐름: if, for, while, comprehension](./05-control-flow.md)
- [Python 101 (6/10): 함수와 인자: def, args, kwargs, default, lambda](./06-functions-and-arguments.md)
- [Python 101 (7/10): 모듈과 패키지: import, __init__, __name__](./07-modules-and-packages.md)
- [Python 101 (8/10): 파일 I/O와 예외 처리](./08-file-io-and-exceptions.md)
- [Python 101 (9/10): 클래스와 객체: 데이터와 동작을 함께 묶기](./09-classes-and-objects.md)
- **표준 라이브러리 투어: datetime, pathlib, json, collections, itertools (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Python 튜토리얼 — Brief Tour of the Standard Library](https://docs.python.org/3/tutorial/stdlib.html) — 표준 라이브러리의 “batteries included” 철학과 모듈 선택 감각을 잡게 해 줍니다.
- [Python 공식 문서 — `datetime`](https://docs.python.org/3/library/datetime.html) — 날짜·시간 객체, `timedelta`, `strftime`/`strptime` 사용의 기준 문서입니다.
- [Python 공식 문서 — `pathlib`](https://docs.python.org/3/library/pathlib.html) — 경로를 문자열 대신 객체로 다루는 API와 파일 조작 메서드를 설명합니다.
- [Python 공식 문서 — `json`](https://docs.python.org/3/library/json.html) — `dump`/`load`/`dumps`/`loads`와 JSON 인코딩 제약을 다룹니다.
- [Python 공식 문서 — `collections`](https://docs.python.org/3/library/collections.html) — `Counter`, `defaultdict`, `deque` 같은 보강 자료구조의 핵심 동작을 확인할 수 있습니다.
- [Python 공식 문서 — `itertools`](https://docs.python.org/3/library/itertools.html) — lazy iterator 도구들의 의도와 조합 방식을 설명합니다.

Tags: standard-library, datetime-module, pathlib-module, json-module, collections-module, itertools-module
