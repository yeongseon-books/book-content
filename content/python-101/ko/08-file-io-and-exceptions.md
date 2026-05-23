---
title: "Python 101 (8/10): 파일 I/O와 예외 처리"
series: python-101
episode: 8
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- file-io
- context-manager
- text-vs-binary
- exception-handling
- try-except-finally
- pathlib
last_reviewed: '2026-05-12'
seo_description: 파일은 "열고 → 쓰고/읽고 → 닫는다"는 세 단계의 자원이고, 예외는 "이 단계 중 어디에서 어떤 종류의 실패가 났는지"를
  분류하는…
---

# Python 101 (8/10): 파일 I/O와 예외 처리

파일은 열고, 읽거나 쓰고, 닫는 세 단계의 자원입니다. 예외는 그 과정에서 어느 단계가 어떤 이유로 실패했는지 구분해 주는 표지판입니다.

이 글은 Python 101 시리즈의 여덟 번째 글입니다.


![Python 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-101/08/08-01-mental-model.ko.png)
*Python 101 8장 흐름 개요*
> 파일 I/O와 예외 처리의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- 파일 I/O와 예외 처리를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?
- 파일 I/O와 예외 처리에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?
- 파일 I/O와 예외 처리를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?

## 멘탈 모델

> 파일은 "열고 → 쓰고/읽고 → 닫는다"는 세 단계의 자원이고, 예외는 "이 단계 중 어디에서 어떤 종류의 실패가 났는지"를 분류하는 라벨이라는 두 모델을 분리해 두면 `with`와 `try` 블록 설계가 자연스럽게 따라옵니다.
다음 그림은 파일을 열고 작업하는 동안 발생할 수 있는 흐름을 보여줍니다.

두 가지 핵심 아이디어가 있습니다.

- **`with`는 정상 종료 시에도, 예외가 발생했을 때에도 `__exit__`을 호출해 핸들을 닫아 줍니다.** 그래서 파일 처리에서는 `try`/`finally`로 직접 `close()`를 호출하는 일은 드뭅니다.
- **잡히지 않은 예외는 호출 스택을 따라 위로 전파됩니다.** `except`가 일치하지 않으면 함수는 그 자리에서 종료되고 호출자가 다시 그 예외를 만납니다. 이 흐름 덕분에 한 곳에서 일관된 에러 처리를 할 수 있습니다.

## 핵심 개념

### `open()`과 모드

`open(path, mode, encoding=...)`은 파일 객체를 돌려줍니다. 가장 자주 쓰는 모드는 다음과 같습니다.

- `"r"` — 읽기, 파일이 없으면 `FileNotFoundError`
- `"w"` — 쓰기, 파일이 있으면 내용을 비웁니다
- `"a"` — 추가 쓰기, 파일이 없으면 새로 만듭니다
- `"x"` — 새로 만들기, 이미 존재하면 `FileExistsError`
- `"b"` — 바이너리 모드 접미사 (`"rb"`, `"wb"`)

텍스트 모드에서는 `encoding`을 지정하지 않으면 플랫폼 기본값을 사용합니다. 운영체제마다 다를 수 있으므로, 텍스트 파일을 다룰 때에는 `encoding="utf-8"`을 명시하는 편이 안전합니다.

### `with` 문

`with`는 컨텍스트 매니저 프로토콜(`__enter__`/`__exit__`)을 사용하는 문법입니다. 파일은 이 프로토콜을 구현하고 있어서 `with` 블록을 빠져나가는 순간 핸들이 닫힙니다.

```python
with open("notes.txt", "r", encoding="utf-8") as f:
    text = f.read()
# 여기서 f는 이미 닫혀 있습니다
```

블록 안에서 예외가 발생해도 `__exit__`이 호출되므로, 핸들 누수를 걱정하지 않아도 됩니다.

### 읽기 방법 네 가지

- `f.read()` — 전체 내용을 한 문자열로 읽습니다. 작은 파일에 적합합니다.
- `f.readline()` — 한 줄을 읽고 다음 호출에서 다음 줄로 넘어갑니다.
- `f.readlines()` — 파일의 남은 줄을 리스트로 한꺼번에 읽습니다.
- `for line in f:` — 한 줄씩 순회합니다. 큰 파일에서도 메모리를 적게 씁니다.

큰 로그 파일을 다룬다면 마지막 방식이 가장 자연스럽습니다. 작은 설정 파일이라면 `read()`가 단순합니다.

### 쓰기

`write(s)`는 문자열을, `writelines(seq)`는 문자열 시퀀스를 차례로 씁니다. `writelines`는 줄바꿈을 자동으로 넣지 않으므로 필요하면 직접 붙여야 합니다.

```python
with open("out.txt", "w", encoding="utf-8") as f:
    f.write("first line\n")
    f.writelines(["a\n", "b\n", "c\n"])
```

### 텍스트 vs 바이너리

텍스트 모드는 문자열(`str`)을, 바이너리 모드는 바이트열(`bytes`)을 주고받습니다. 이미지, 압축 파일, 실행 파일은 바이너리 모드로 다뤄야 합니다. 텍스트 모드는 운영체제에 따라 줄바꿈을 변환할 수 있으므로, 줄바꿈을 그대로 보존해야 한다면 바이너리 모드를 쓰는 편이 안전합니다.

### `try`/`except`/`else`/`finally`

네 블록의 역할은 다음과 같습니다.

- `try` — 예외가 발생할 가능성이 있는 코드
- `except` — 특정 예외 종류에 대응하는 코드
- `else` — `try` 블록이 예외 없이 끝났을 때만 실행되는 코드
- `finally` — 예외 발생 여부와 무관하게 마지막에 실행되는 코드

`else`와 `finally`는 자주 쓰이지 않지만, 정상 경로와 정리 경로를 분리해 표현할 때 유용합니다.

### 좁은 예외 잡기

`except:` 또는 `except Exception:`처럼 광범위하게 잡으면 진짜 버그(타이포로 인한 `NameError` 등)도 함께 삼켜집니다. 예상되는 예외만 좁게 잡는 편이 디버깅에 도움이 됩니다.

```python
try:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()
except FileNotFoundError:
    return ""
except PermissionError:
    raise
```

### `pathlib.Path`

`pathlib.Path`는 경로를 객체로 다룹니다. `/` 연산자로 경로를 합치고, `read_text` / `write_text`로 짧은 파일 작업을 한 줄에 처리할 수 있습니다.

```python
from pathlib import Path

config_dir = Path.home() / ".myapp"
config_dir.mkdir(parents=True, exist_ok=True)
(config_dir / "config.txt").write_text("debug=true\n", encoding="utf-8")
```

문자열 `+`로 경로를 합치면 운영체제에 따라 구분자가 달라 문제가 생기기 쉽습니다. `pathlib`는 그런 잔실수를 줄여 줍니다.

## 전후 비교

다음은 설정 파일을 읽어 문자열로 돌려주는 함수입니다.

**Before**

```python
def load_config(path):
    f = open(path)
    try:
        return f.read()
    except:
        return ""
```

이 코드에는 세 가지 문제가 있습니다.

- `with` 없이 `open()`만 사용해서, `read()` 도중 예외가 나면 핸들이 새어 나갈 수 있습니다.
- `encoding`을 지정하지 않아 플랫폼마다 다른 결과를 줄 수 있습니다.
- `except:`가 예상하지 않은 예외까지 삼켜서, 파일 권한 문제든 코드 버그든 빈 문자열로 묻혀 버립니다.

**After**

```python
from pathlib import Path

def load_config(path):
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
```

세 가지 변화가 있습니다.

- `pathlib.Path.read_text`가 내부적으로 `with`를 사용하므로 핸들 관리를 직접 할 필요가 없습니다.
- `encoding="utf-8"`을 명시해 플랫폼 차이를 없앱니다.
- `FileNotFoundError`만 좁게 잡고, 다른 예외(권한 문제, 디스크 오류, 코드 버그)는 호출자에게 그대로 전파됩니다.

## 단계별 실습

REPL을 켜고 한 줄씩 따라가 보세요. 다음 블록은 `>>>` 표시가 붙은 REPL 전사이고, 그 외 코드 블록은 설명용 예시입니다.

### 1. 텍스트 파일 쓰고 다시 읽기

```text
>>> with open("hello.txt", "w", encoding="utf-8") as f:
...     f.write("hello\n")
...
6
>>> with open("hello.txt", "r", encoding="utf-8") as f:
...     print(f.read())
...
hello
```

`write`가 돌려주는 숫자는 기록한 문자 수입니다.

### 2. 없는 파일 안전하게 열기

```text
>>> try:
...     with open("missing.txt", "r", encoding="utf-8") as f:
...         data = f.read()
... except FileNotFoundError:
...     data = ""
...
>>> data
''
```

좁은 `except`로 한 가지 실패만 처리합니다. 다른 종류의 오류는 그대로 위로 올라갑니다.

### 3. 바이너리 모드로 첫 4바이트 보기

```text
>>> with open("hello.txt", "rb") as f:
...     header = f.read(4)
...
>>> header
b'hell'
```

같은 파일을 바이너리로 열면 UTF-8로 인코딩된 바이트열이 그대로 보입니다.

### 4. `pathlib`로 디렉터리 만들고 파일 쓰기

```text
>>> from pathlib import Path
>>> base = Path("scratch")
>>> base.mkdir(exist_ok=True)
>>> (base / "note.txt").write_text("hi\n", encoding="utf-8")
3
>>> (base / "note.txt").read_text(encoding="utf-8")
'hi\n'
```

### 5. `try`/`except`/`else`/`finally` 흐름 확인

```text
>>> def safe_read(p):
...     try:
...         text = Path(p).read_text(encoding="utf-8")
...     except FileNotFoundError:
...         print("missing")
...         return None
...     else:
...         print("ok")
...         return text
...     finally:
...         print("done")
...
>>> safe_read("scratch/note.txt")
ok
done
'hi\n'
>>> safe_read("scratch/none.txt")
missing
done
```

`else`는 예외가 없을 때만, `finally`는 어느 경우에든 실행되는 모습을 확인할 수 있습니다.

## 이 코드에서 주목할 점

- **`with open(...) as f:`** — 블록을 빠져나가는 순간 `__exit__`이 호출되어 핸들이 닫힙니다. 예외가 발생해도 동일하게 호출되므로 `try`/`finally`로 직접 `close()`를 호출할 필요가 없습니다.
- **`encoding="utf-8"` 명시** — 텍스트 모드에서 인코딩을 생략하면 운영체제 기본값을 사용합니다. 명시하는 한 줄로 환경 차이를 제거합니다.
- **`except FileNotFoundError:`** — 광범위한 `except:` 대신 한 가지 실패 종류만 좁게 잡습니다. 예상하지 못한 예외는 그대로 위로 전파됩니다.
- **`Path(path).read_text(...)`** — `pathlib`은 내부적으로 `with`를 사용하므로 짧은 파일 읽기는 한 줄로 줄어듭니다.
- **`else` 블록** — 예외 없이 끝났을 때만 실행되므로, 정상 경로의 후속 작업을 `try` 블록 바깥으로 분리해 의도를 명확히 할 수 있습니다.

## 자주 하는 실수

- **`with` 없이 `open()`** — 예외가 나면 핸들이 닫히지 않을 수 있습니다. 짧은 스크립트에서도 `with`를 기본으로 두는 편이 안전합니다.
- **`encoding`을 지정하지 않음** — 플랫폼 기본 인코딩에 의존하면 같은 코드가 환경에 따라 다른 결과를 냅니다. 텍스트 파일에는 `encoding="utf-8"`을 명시하세요.
- **`except:`로 예외를 넓게 잡기** — 진짜 버그까지 함께 삼켜집니다. 잡고 싶은 예외 클래스만 명시하세요.
- **예외 조용히 무시** — `except FileNotFoundError: pass`처럼 아무 일도 하지 않으면 디버깅이 어려워집니다. 최소한 로깅이라도 남기세요.
- **바이너리 파일을 텍스트 모드로 열기** — 디코딩 오류나 줄바꿈 변환으로 데이터가 망가질 수 있습니다. 이미지·압축·실행 파일은 `"rb"`/`"wb"`를 쓰세요.
- **문자열 `+`로 경로 합치기** — 운영체제마다 구분자가 다르고 중복 슬래시가 생기기 쉽습니다. `pathlib.Path`의 `/` 연산자나 `os.path.join`을 쓰세요.
- **큰 파일을 `read()`로 한꺼번에 읽기** — 메모리에 모두 올라갑니다. 줄 단위 순회(`for line in f:`)가 더 안전합니다.

## 실무에서는 이렇게 생각합니다

실제 프로젝트에서 파일 I/O와 예외 처리는 주로 다음 자리에서 만납니다.

- **설정 로더**: `pathlib.Path.read_text`로 짧은 설정 파일을 한 번에 읽고, 없으면 기본값으로 떨어뜨립니다. 권한 오류는 일부러 전파해 빠르게 실패시키는 편이 안전합니다.
- **로그/리포트 쓰기**: 추가 모드(`"a"`)로 한 줄씩 기록합니다. 파일 핸들을 자주 여닫는 대신, 한 함수 안에서 `with`로 묶어 한 번에 처리합니다.
- **CSV/JSON 처리**: 줄 단위 스트리밍이 가능한 형식(CSV, JSONL)은 `for line in f:`로 처리하면 큰 파일도 메모리 부담 없이 다룰 수 있습니다.
- **임시 파일**: `tempfile.NamedTemporaryFile`을 `with`와 함께 쓰면, 작업이 끝나면 파일을 자동으로 정리할 수 있습니다.
- **재시도와 복구**: 일시적 오류(네트워크 파일 시스템의 잠깐의 끊김 등)는 좁은 예외로 잡아 재시도하고, 영구적 오류는 그대로 전파해 호출자가 결정하게 합니다.

요지는 같습니다. 자원은 `with`로 닫고, 예외는 좁게 잡고, 모르는 오류는 위로 올려 보냅니다.

## 체크리스트

- [ ] `open()`을 기본적으로 `with`와 함께 사용할 수 있습니다.
- [ ] 텍스트 모드와 바이너리 모드의 차이, 그리고 `encoding`이 왜 필요한지 한 문장으로 설명할 수 있습니다.
- [ ] `read`, `readline`, `readlines`, `for line in f:`의 차이를 구분해 설명할 수 있습니다.
- [ ] `try`/`except`/`else`/`finally` 네 블록의 역할을 구분해 사용할 수 있습니다.
- [ ] `except:` 또는 `except Exception:`을 피하고 좁은 예외 클래스를 골라 잡을 수 있습니다.
- [ ] `pathlib.Path`로 경로를 합치고 `read_text` / `write_text`로 짧은 파일 작업을 처리할 수 있습니다.
- [ ] 큰 파일을 다룰 때 `for line in f:`로 줄 단위 순회를 선택할 수 있습니다.

## 정리·다음 글

- 파일은 운영체제 자원이므로 `with`로 열어 자동으로 닫는 편이 안전합니다.
- 텍스트 모드는 `str`, 바이너리 모드는 `bytes`를 주고받고, 텍스트는 `encoding="utf-8"`을 명시하는 편이 좋습니다.
- 예외는 `try`/`except`/`else`/`finally` 네 블록으로 정상 경로와 복구·정리 경로를 나눠 표현합니다.
- 좁은 예외 클래스를 골라 잡고, 모르는 오류는 위로 전파해 호출자가 결정하게 합니다.
- `pathlib.Path`는 경로 조작과 짧은 파일 작업을 한 줄로 줄여 주는 표준 도구입니다.

다음 글에서는 클래스와 객체를 다룹니다. 지금까지 다뤄 온 함수와 모듈의 묶음을 한 단계 더 추상화해, 데이터와 동작을 함께 묶는 방법을 살펴봅니다.

## 실전 앵커: 파일 처리 신뢰성과 예외 설계

파일 I/O는 정상 경로보다 실패 경로 설계가 중요합니다. 파일이 없거나, 인코딩이 다르거나, 권한이 없거나, 중간에 프로세스가 중단되는 상황을 먼저 가정해야 합니다.

```python
from pathlib import Path

path = Path('data/input.txt')
if not path.exists():
    raise FileNotFoundError(path)

text = path.read_text(encoding='utf-8')
print(text[:40])
```

파일 쓰기는 원자성(atomicity) 관점에서 임시 파일 + 교체 패턴을 쓰면 안전합니다.

```python
from pathlib import Path

final = Path('result.json')
tmp = final.with_suffix('.tmp')
tmp.write_text('{"ok": true}
', encoding='utf-8')
tmp.replace(final)
```

중간 실패가 발생해도 손상된 결과 파일을 남길 가능성이 줄어듭니다.

예외 처리에서는 폭넓은 `except Exception:`을 먼저 쓰지 않는 것이 중요합니다. 예상 가능한 예외를 좁게 잡고, 복구 불가능한 예외는 다시 올려야 합니다.

```python
try:
    value = int('42a')
except ValueError as e:
    print('숫자 파싱 실패:', e)
```

체이닝도 꼭 알아두어야 합니다.

```python
try:
    raise ValueError('bad format')
except ValueError as e:
    raise RuntimeError('사용자 입력 검증 실패') from e
```

`from e`를 쓰면 원인 예외가 traceback에 보존되어 운영 디버깅이 쉬워집니다.

`pdb`로 파일 처리 코드를 추적하는 예시는 다음이 기본입니다.

```python
import pdb
from pathlib import Path

def load_config(path):
    pdb.set_trace()
    return Path(path).read_text(encoding='utf-8')
```

`p path`, `n`, `p Path(path).exists()` 순서로 보면 실패 지점을 빠르게 찾을 수 있습니다.

성능 측정도 간단히 해 봅니다.

```python
import timeit

line_t = timeit.timeit("sum(1 for _ in open('big.txt', encoding='utf-8'))", number=10)
all_t = timeit.timeit("len(open('big.txt', encoding='utf-8').read().splitlines())", number=10)
print(line_t, all_t)
```

대용량 파일은 스트리밍 처리가 메모리 안정성 면에서 유리합니다.

표준 라이브러리 예시를 더하면 다음 조합이 실무에서 자주 쓰입니다.

- `pathlib`: 경로 조작의 가독성 향상
- `csv`: 구분자/인용부호 처리 자동화
- `json`: API/설정 파일 직렬화
- `tempfile`: 임시 파일 안전 생성

예외 처리는 "모든 오류를 숨기는 기술"이 아니라 "오류를 예측 가능하게 노출하는 설계"입니다. 이 관점을 잡아야 운영에서 원인 분석 시간이 줄어듭니다.

### 추가 실습: 예외 로깅과 재시도 경계 설정

예외를 처리할 때는 복구 가능한 오류와 즉시 실패해야 하는 오류를 구분해야 합니다. 파일 잠금, 일시적 네트워크 오류는 재시도 가능하지만 데이터 포맷 오류는 재시도로 해결되지 않습니다.

```python
import time

def retry_read(read_fn, retries=3):
    for attempt in range(1, retries + 1):
        try:
            return read_fn()
        except OSError as e:
            if attempt == retries:
                raise
            time.sleep(0.2 * attempt)
```

또한 로깅 시 traceback을 반드시 남겨야 사후 분석이 가능합니다.

```python
import logging

logger = logging.getLogger(__name__)

try:
    1 / 0
except ZeroDivisionError:
    logger.exception('계산 실패')
```

`logger.exception`은 현재 예외 스택을 자동으로 붙여 주므로 운영 장애 대응에 유리합니다.

텍스트 파일 처리에서는 newline 정책도 명확히 해야 합니다. CSV는 `newline=''`를 권장하고, 일반 텍스트는 기본 newline 정규화를 사용하되 플랫폼 간 결과를 테스트로 고정하는 편이 안전합니다.

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

## 처음 질문으로 돌아가기

- **파일 I/O와 예외 처리를 운영 관점에서 볼 때 먼저 어떤 경계를 확인해야 할까요?**
  - 먼저 파일을 여는 단계, 읽거나 쓰는 단계, 닫는 단계를 분리해서 봐야 합니다. 그래서 `with open(..., encoding="utf-8") as f:`나 `Path(path).read_text(encoding="utf-8")`처럼 자원 정리와 인코딩을 초반에 고정하고, 어떤 예외를 여기서 처리하고 어떤 예외를 호출자에게 올릴지 경계를 정하는 편이 안전합니다.
- **파일 I/O와 예외 처리에서 예제나 다이어그램으로 검증해야 할 핵심 신호는 무엇일까요?**
  - 본문 예제에서는 `write("hello\n")`가 6을 돌려주는지, `open("hello.txt", "rb")`에서 `b'hell'`처럼 바이트가 읽히는지, `safe_read("scratch/note.txt")`에서는 `ok`와 `done`이, 없는 파일에서는 `missing`과 `done`이 출력되는지가 핵심 신호입니다. 이런 출력이 있어야 `with`, 텍스트/바이너리 모드, `try`/`except`/`else`/`finally`의 역할이 실제 흐름으로 확인됩니다.
- **파일 I/O와 예외 처리를 실제 시스템에 적용할 때 어떤 실패를 먼저 막아야 할까요?**
  - 가장 먼저 막아야 할 실패는 `with` 없이 파일을 열어 핸들을 새는 경우와, `except:`로 모든 오류를 삼켜 진짜 원인을 잃는 경우입니다. 여기에 인코딩 미지정으로 플랫폼마다 다른 결과가 나오는 문제, 큰 파일을 `read()`로 한꺼번에 읽는 문제, 최종 파일에 바로 써서 중간 실패 때 손상된 결과를 남기는 문제까지 같이 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python 101 (1/10): 왜 Python인가, 그리고 설치와 venv](./01-why-python-and-install.md)
- [Python 101 (2/10): 변수, 타입, 연산자](./02-variables-types-operators.md)
- [Python 101 (3/10): 문자열과 포매팅](./03-strings-and-formatting.md)
- [Python 101 (4/10): list, tuple, set, dict](./04-list-tuple-set-dict.md)
- [Python 101 (5/10): 제어 흐름: if, for, while, comprehension](./05-control-flow.md)
- [Python 101 (6/10): 함수와 인자: def, args, kwargs, default, lambda](./06-functions-and-arguments.md)
- [Python 101 (7/10): 모듈과 패키지: import, __init__, __name__](./07-modules-and-packages.md)
- **파일 I/O와 예외 처리 (현재 글)**
- 클래스와 객체: 데이터와 동작을 함께 묶기 (예정)
- 표준 라이브러리 투어: datetime, pathlib, json, collections, itertools (예정)

<!-- toc:end -->

## 참고 자료

- [Python 튜토리얼 — Input and Output](https://docs.python.org/3/tutorial/inputoutput.html) — `open()`, 읽기/쓰기 메서드, 텍스트 vs 바이너리 모드의 기본 흐름을 설명합니다.
- [Python 튜토리얼 — Errors and Exceptions](https://docs.python.org/3/tutorial/errors.html) — `try`/`except`/`else`/`finally`, 예외 전파, 좁은 예외 처리의 예시를 제공합니다.
- [Python 공식 문서 — `open()`](https://docs.python.org/3/library/functions.html#open) — mode, encoding, text/binary 구분의 세부 규칙을 확인할 수 있습니다.
- [Python 공식 문서 — `pathlib`](https://docs.python.org/3/library/pathlib.html) — `Path`, `/` 연산자, `read_text()`/`write_text()` 같은 경로 기반 API를 다룹니다.
- [PEP 343 — The "with" Statement](https://peps.python.org/pep-0343/) — 컨텍스트 매니저와 `with` 문이 자원 정리를 어떻게 표준화했는지 설명합니다.

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/python-101/ko)
Tags: file-io, context-manager, text-vs-binary, exception-handling, try-except-finally, pathlib
