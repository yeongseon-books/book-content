---
title: 파일 I/O와 예외 처리
series: python-101
episode: 8
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- file-io
- context-manager
- text-vs-binary
- exception-handling
- try-except-finally
- pathlib
last_reviewed: '2026-05-03'
seo_description: 파일은 "열고 → 쓰고/읽고 → 닫는다"는 세 단계의 자원이고, 예외는 "이 단계 중 어디에서 어떤 종류의 실패가 났는지"를
  분류하는…
---

# 파일 I/O와 예외 처리

## 이 글에서 배울 것

이 글을 읽고 나면 다음을 할 수 있습니다.

- `open()` 함수와 `with` 문으로 파일을 안전하게 열고 닫을 수 있습니다.
- 텍스트 모드(`"r"`, `"w"`, `"a"`)와 바이너리 모드(`"rb"`, `"wb"`)의 차이를 구분해 사용할 수 있습니다.
- `read`, `readline`, `readlines`, 그리고 파일 객체 자체를 순회하는 방식의 차이를 한 문장씩으로 설명할 수 있습니다.
- `try`/`except`/`else`/`finally`의 네 블록 역할을 구분해 사용할 수 있습니다.
- `FileNotFoundError`, `PermissionError`처럼 좁은 예외를 골라 잡고, `except:` 같은 광범위한 catch는 피할 수 있습니다.
- `pathlib.Path`로 경로를 조작하고 `read_text` / `write_text`로 짧은 파일 작업을 처리할 수 있습니다.

## 이 글에서 답할 질문

- `open()`을 `with` 문과 함께 쓰는 것이 직접 `close()`를 호출하는 것보다 무엇을 보장해 주는가?
- 텍스트 모드와 바이너리 모드의 차이는 어떤 데이터에 적용되는 결정인가?
- `read`, `readline`, `readlines`, 파일 객체 순회는 각각 어떤 파일 크기·사용 패턴에 맞는가?
- `try`/`except`/`else`/`finally` 네 블록은 각각 어떤 책임을 맡는가?
- 광범위한 `except:` 대신 좁은 예외만 잡아야 하는 이유는 무엇인가?
- `pathlib.Path`의 `read_text`/`write_text`는 어떤 작업에서 가장 잘 들어맞는가?

## 왜 중요한가

파일 작업은 외부 자원을 다루는 코드입니다. 메모리 안의 변수와 달리, 파일 핸들은 운영체제가 발급한 한정된 자원이고 오류 가능성도 함께 따라옵니다. 디스크가 가득 찼을 수도 있고, 권한이 없을 수도 있고, 다른 프로세스가 잠가둔 파일일 수도 있습니다.

이런 상황을 무시하고 짠 코드는 평소에는 잘 동작하다가 운영 환경에서 갑자기 망가지는 편입니다. 핸들을 닫지 않으면 장시간 실행되는 서버에서 file descriptor가 누수되고, 예외를 무시하면 데이터가 절반만 쓰인 채 끝나기도 합니다. 반대로 예상 범위를 넘는 예외까지 `except:`로 한꺼번에 삼키면 진짜 버그가 조용히 숨어버립니다.

`with` 문과 좁은 `except` 절은 이 두 가지 함정을 피하는 가장 단순한 방법입니다. 이 글에서는 두 도구를 정확히 어디에 어떻게 쓰는지 살펴봅니다.

## Mental Model

> 파일은 "열고 → 쓰고/읽고 → 닫는다"는 세 단계의 자원이고, 예외는 "이 단계 중 어디에서 어떤 종류의 실패가 났는지"를 분류하는 라벨이라는 두 모델을 분리해 두면 `with`와 `try` 블록 설계가 자연스럽게 따라옵니다.
다음 그림은 파일을 열고 작업하는 동안 발생할 수 있는 흐름을 보여줍니다.

![Mental Model](../../../assets/python-101/08/08-01-mental-model.ko.png)
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

## Before-After

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
...     f.write("안녕\n")
...
3
>>> with open("hello.txt", "r", encoding="utf-8") as f:
...     print(f.read())
...
안녕
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
b'\xec\x95\x88\xeb'
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

## 자주 하는 실수

- **`with` 없이 `open()`** — 예외가 나면 핸들이 닫히지 않을 수 있습니다. 짧은 스크립트에서도 `with`를 기본으로 두는 편이 안전합니다.
- **`encoding`을 지정하지 않음** — 플랫폼 기본 인코딩에 의존하면 같은 코드가 환경에 따라 다른 결과를 냅니다. 텍스트 파일에는 `encoding="utf-8"`을 명시하세요.
- **`except:`로 예외를 넓게 잡기** — 진짜 버그까지 함께 삼켜집니다. 잡고 싶은 예외 클래스만 명시하세요.
- **예외 조용히 무시** — `except FileNotFoundError: pass`처럼 아무 일도 하지 않으면 디버깅이 어려워집니다. 최소한 로깅이라도 남기세요.
- **바이너리 파일을 텍스트 모드로 열기** — 디코딩 오류나 줄바꿈 변환으로 데이터가 망가질 수 있습니다. 이미지·압축·실행 파일은 `"rb"`/`"wb"`를 쓰세요.
- **문자열 `+`로 경로 합치기** — 운영체제마다 구분자가 다르고 중복 슬래시가 생기기 쉽습니다. `pathlib.Path`의 `/` 연산자나 `os.path.join`을 쓰세요.
- **큰 파일을 `read()`로 한꺼번에 읽기** — 메모리에 모두 올라갑니다. 줄 단위 순회(`for line in f:`)가 더 안전합니다.

## 실무

실제 프로젝트에서 파일 I/O와 예외 처리는 주로 다음 자리에서 만납니다.

- **설정 로더**: `pathlib.Path.read_text`로 짧은 설정 파일을 한 번에 읽고, 없으면 기본값으로 떨어뜨립니다. 권한 오류는 일부러 전파해 빠르게 실패시키는 편이 안전합니다.
- **로그/리포트 쓰기**: 추가 모드(`"a"`)로 한 줄씩 기록합니다. 파일 핸들을 자주 여닫는 대신, 한 함수 안에서 `with`로 묶어 한 번에 처리합니다.
- **CSV/JSON 처리**: 줄 단위 스트리밍이 가능한 형식(CSV, JSONL)은 `for line in f:`로 처리하면 큰 파일도 메모리 부담 없이 다룰 수 있습니다.
- **임시 파일**: `tempfile.NamedTemporaryFile`을 `with`와 함께 쓰면, 작업이 끝나면 파일을 자동으로 정리할 수 있습니다.
- **재시도와 복구**: 일시적 오류(네트워크 파일 시스템의 잠깐의 끊김 등)는 좁은 예외로 잡아 재시도하고, 영구적 오류는 그대로 전파해 호출자가 결정하게 합니다.

핵심은 같습니다. 자원은 `with`로 닫고, 예외는 좁게 잡고, 모르는 오류는 위로 올려 보냅니다.

## 체크리스트

- [ ] `open()`을 기본적으로 `with`와 함께 사용할 수 있습니다.
- [ ] 텍스트 모드와 바이너리 모드의 차이, 그리고 `encoding`이 왜 필요한지 한 문장으로 설명할 수 있습니다.
- [ ] `read`, `readline`, `readlines`, `for line in f:`의 차이를 구분해 설명할 수 있습니다.
- [ ] `try`/`except`/`else`/`finally` 네 블록의 역할을 구분해 사용할 수 있습니다.
- [ ] `except:` 또는 `except Exception:`을 피하고 좁은 예외 클래스를 골라 잡을 수 있습니다.
- [ ] `pathlib.Path`로 경로를 합치고 `read_text` / `write_text`로 짧은 파일 작업을 처리할 수 있습니다.
- [ ] 큰 파일을 다룰 때 `for line in f:`로 줄 단위 순회를 선택할 수 있습니다.

## 연습 문제

1. `notes.txt`에 줄 단위로 메모를 추가하는 함수 `append_note(text)`를 작성하세요. 추가 모드(`"a"`)와 `with`를 사용하고, 줄바꿈을 직접 붙여 주세요.
2. `count_lines(path)` 함수를 작성하세요. 파일이 없으면 `0`을 돌려주고, 있으면 `for line in f:`로 줄 수를 세서 돌려줍니다.
3. `safe_copy(src, dst)` 함수를 작성하세요. `src`를 바이너리 모드로 읽어 `dst`에 그대로 씁니다. `src`가 없으면 `FileNotFoundError`를 그대로 전파합니다.
4. `pathlib`만 사용해 다음을 수행하는 스크립트를 작성하세요 — `data/` 디렉터리를 만들고, 그 안에 `hello.txt`를 쓰고, 다시 읽어 출력합니다. 디렉터리가 이미 있어도 오류가 나지 않게 하세요.

## 정리·다음 글

- 파일은 운영체제 자원이므로 `with`로 열어 자동으로 닫는 편이 안전합니다.
- 텍스트 모드는 `str`, 바이너리 모드는 `bytes`를 주고받고, 텍스트는 `encoding="utf-8"`을 명시하는 편이 좋습니다.
- 예외는 `try`/`except`/`else`/`finally` 네 블록으로 정상 경로와 복구·정리 경로를 나눠 표현합니다.
- 좁은 예외 클래스를 골라 잡고, 모르는 오류는 위로 전파해 호출자가 결정하게 합니다.
- `pathlib.Path`는 경로 조작과 짧은 파일 작업을 한 줄로 줄여 주는 표준 도구입니다.

다음 글에서는 클래스와 객체를 다룹니다. 지금까지 다뤄 온 함수와 모듈의 묶음을 한 단계 더 추상화해, 데이터와 동작을 함께 묶는 방법을 살펴봅니다.

<!-- toc:begin -->
<!-- toc:end -->

## 참고 자료

- [Python tutorial — Reading and writing files](https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files)
- [Python tutorial — Errors and exceptions](https://docs.python.org/3/tutorial/errors.html)
- [Python library — pathlib](https://docs.python.org/3/library/pathlib.html)
- [PEP 343 — The "with" statement](https://peps.python.org/pep-0343/)

Tags: file-io, context-manager, text-vs-binary, exception-handling, try-except-finally, pathlib
