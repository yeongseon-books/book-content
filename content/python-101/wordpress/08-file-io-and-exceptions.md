---
title: "바이브코딩을 위한 Python 기초 (8/10): AI가 만든 파일 처리 코드, 에러 핸들링이 빠져있을 때"
series: python-101
episode: 8
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
- 파일처리
- 예외처리
- pathlib
seo_description: "바이브코딩 시대, AI가 만든 파일 I/O 코드에서 에러 핸들링을 추가하는 법. with문, try/except, pathlib 완전 정리"
---

# 바이브코딩을 위한 Python 기초 (8/10): AI가 만든 파일 처리 코드, 에러 핸들링이 빠져있을 때

이 글은 바이브코딩을 위한 Python 기초 시리즈의 8번째 글입니다.

AI에게 "CSV 파일 읽어서 처리하는 코드 만들어줘"라고 하면 이런 코드가 나옵니다.

```python
def process_file(path):
    f = open(path)
    data = f.read()
    f.close()
    return parse(data)
```

이 코드를 실제로 쓰다 보면 몇 가지 문제가 생깁니다. 파일이 없으면 프로그램이 죽습니다. `parse(data)`에서 에러가 나면 `f.close()`가 안 불려서 파일 핸들이 누수됩니다. `encoding`이 안 맞으면 한글이 깨집니다.

AI는 "동작하는 최소 코드"를 먼저 만들어줍니다. 에러 핸들링은 요청하지 않으면 빠지는 경우가 많습니다. 그래서 바이브코더라면 AI가 만든 파일 처리 코드를 받았을 때 "이 코드에 에러 핸들링이 충분한가"를 점검하는 눈이 필요합니다.

더 중요한 것은 코드가 실제 운영에서 어떻게 실패할 수 있는지를 알아야 AI에게 제대로 보강 요청을 할 수 있다는 점입니다. "에러 처리 추가해줘"보다 "파일이 없을 때 빈 결과를 반환하고, 권한 에러는 그대로 위로 올려줘"가 훨씬 정확한 요청입니다.

> AI가 만든 파일 처리 코드는 정상 경로만 다루는 경우가 많습니다. 실패 경로를 설계하는 것은 바이브코더의 몫입니다.

---

## 이 글에서 다룰 문제

- AI가 만든 코드에 `with` 없이 `open()`이 있는데, 이게 왜 위험한가요?
- `except:` 하나로 모든 에러를 잡는 코드, 어떻게 개선해야 하나요?
- 파일이 없을 때, 권한이 없을 때, 인코딩이 틀렸을 때 각각 어떻게 처리해야 하나요?
- `pathlib`를 쓰면 뭐가 좋아지나요?
- 큰 파일을 통째로 읽는 AI 코드, 메모리 문제 없이 고치려면?

---

## AI 코드를 읽으려면 이것을 알아야

### `with`가 없으면 핸들이 샌다

```python
# 위험한 패턴
f = open("data.txt")
data = f.read()  # 여기서 에러 나면 f.close() 안 불림
f.close()
```

`f.read()` 도중 에러가 나면 `f.close()`가 실행되지 않습니다. 파일 핸들이 계속 열려있게 됩니다. 작은 스크립트에서는 티가 잘 안 나지만, 서버에서 돌아가는 코드에서는 파일 핸들이 고갈돼 시스템이 멈출 수 있습니다.

```python
# 안전한 패턴
with open("data.txt", encoding="utf-8") as f:
    data = f.read()
# 블록을 나가는 순간 에러가 났어도 f가 닫힘
```

`with`는 블록을 빠져나갈 때 — 정상이든 에러든 — 자동으로 파일을 닫아줍니다.

### `encoding`을 명시해야 한글이 안 깨진다

AI가 `encoding`을 빠뜨리는 경우가 자주 있습니다. 빠뜨리면 플랫폼 기본값을 씁니다. Windows는 `cp949`, macOS/Linux는 `utf-8`이 기본입니다. 같은 코드가 환경마다 다르게 동작합니다. 한글 파일이라면 항상 `encoding="utf-8"`을 명시하세요.

### 예외 클래스는 종류가 있다

```python
# 나쁜 패턴 — 모든 에러를 잡아버림
try:
    with open(path) as f:
        return f.read()
except:
    return ""  # 버그가 있어도 ""가 반환돼 문제를 숨김
```

`except:` 하나로 잡으면 파일 없음, 권한 없음, 코드 버그(NameError, TypeError 등)가 모두 같은 처리를 받습니다. 실제 버그가 숨겨집니다.

```python
# 좋은 패턴 — 예상한 에러만 좁게 잡기
try:
    with open(path, encoding="utf-8") as f:
        return f.read()
except FileNotFoundError:
    return ""        # 파일 없음 → 기본값 반환
except PermissionError:
    raise            # 권한 없음 → 위로 전달 (호출자가 결정)
```

### 네 개의 블록: try / except / else / finally

```python
from pathlib import Path

def safe_read(path):
    try:
        text = Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print("파일 없음")
        return None
    else:
        print("읽기 성공")  # 에러 없이 끝났을 때만 실행
        return text
    finally:
        print("항상 실행")  # 에러 여부 관계없이 마지막에 실행
```

`else`는 "try가 에러 없이 끝났을 때", `finally`는 "무조건 마지막에"입니다. AI가 만든 코드에 `finally`가 있으면 "자원 정리를 여기서 한다"는 의미입니다.

### `pathlib`로 경로를 다루면 짧아진다

AI가 최근엔 `pathlib`를 자주 씁니다.

```python
from pathlib import Path

# 문자열 더하기 대신
config_path = "/home/user/" + ".config" + "/app.json"  # 위험

# Path 객체로
config_path = Path.home() / ".config" / "app.json"  # 안전

# 짧은 파일 읽기
content = Path("data.txt").read_text(encoding="utf-8")

# 짧은 파일 쓰기
Path("output.txt").write_text("결과\n", encoding="utf-8")
```

`/` 연산자가 경로 구분자를 자동으로 처리합니다. Windows(`\`)와 Linux(`/`) 차이를 신경 쓰지 않아도 됩니다.

### 큰 파일은 줄 단위로 읽어야 한다

```python
# AI가 자주 쓰는 패턴 — 작은 파일엔 OK, 큰 파일엔 위험
with open("big.log") as f:
    data = f.read()  # 전체를 메모리에 올림

# 큰 파일은 이렇게
with open("big.log", encoding="utf-8") as f:
    for line in f:  # 한 줄씩 읽음, 메모리 효율적
        process(line.rstrip())
```

로그 파일이 1GB라면 `f.read()`는 1GB를 통째로 메모리에 올립니다. `for line in f:`는 한 줄씩 처리합니다.

---

## Before / After

### AI가 만든 초안

```python
def load_config(path):
    f = open(path)
    try:
        return f.read()
    except:
        return ""
```

세 가지 문제가 있습니다. `with` 없이 `open()` → 핸들 누수 가능. `encoding` 없음 → 플랫폼마다 다른 결과. `except:` → 모든 에러를 빈 문자열로 묻어버림.

### 바이브코딩으로 개선

```python
from pathlib import Path

def load_config(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    # 다른 에러(권한, 디스크 오류)는 그대로 위로 전달
```

AI에게 이렇게 요청하면 됩니다: "이 함수에서 `with`를 쓰고, `encoding='utf-8'`을 명시하고, 파일이 없을 때만 빈 문자열을 반환하고, 다른 에러는 위로 전달하도록 수정해줘."

### 원자적 파일 쓰기 (AI가 자주 빠뜨리는 것)

```python
from pathlib import Path

def save_result(data: str, output_path: str) -> None:
    final = Path(output_path)
    tmp = final.with_suffix(".tmp")
    try:
        tmp.write_text(data, encoding="utf-8")
        tmp.replace(final)  # 성공하면 교체
    except Exception:
        tmp.unlink(missing_ok=True)  # 실패하면 임시 파일 삭제
        raise
```

중간에 실패해도 손상된 파일을 남기지 않습니다. AI에게 "파일 쓰기를 원자적으로 만들어줘. 임시 파일에 쓰고 성공하면 교체하는 방식으로."라고 요청하면 됩니다.

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `open()` without `with` | 에러 시 핸들 누수 | 항상 `with open(...) as f:` 사용 |
| `encoding` 생략 | 플랫폼마다 다른 결과, 한글 깨짐 | `encoding="utf-8"` 명시 |
| `except:` 광범위 | 실제 버그를 숨김 | 예상한 예외 클래스만 좁게 잡기 |
| `except SomeError: pass` | 에러를 완전히 무시 | 최소한 로그라도 남기기 |
| 큰 파일 `f.read()` | 전체를 메모리에 올림 | `for line in f:` 줄 단위 처리 |
| 문자열 `+`로 경로 합치기 | OS별 구분자 문제 | `pathlib.Path` / 연산자 사용 |

---

## AI에게 이 주제 관련 질문하는 팁

**에러 핸들링 보강 요청:**
"이 파일 처리 코드에 에러 핸들링을 추가해줘. 파일이 없으면 기본값을 반환하고, 권한 에러는 위로 전달하고, 인코딩 에러는 로그를 남겨줘."

**pathlib 변환:**
"이 코드의 파일 경로 처리를 `pathlib.Path`를 써서 다시 작성해줘."

**메모리 효율 개선:**
"이 코드가 큰 파일을 처리할 때 메모리 문제가 있을 것 같아. 줄 단위 스트리밍으로 바꿔줘."

**원자적 쓰기:**
"파일 쓰기가 중간에 실패해도 기존 파일이 손상되지 않게 임시 파일 패턴으로 수정해줘."

---

## 운영 체크리스트

- [ ] AI 코드에서 `open()` 앞에 `with`가 있는지 확인한다
- [ ] 텍스트 파일 처리에 `encoding="utf-8"`이 명시돼 있는지 확인한다
- [ ] `except:` 또는 `except Exception:` 광범위한 예외 처리가 있으면 좁혀야 한다고 인식한다
- [ ] 큰 파일 처리 코드에서 `f.read()`가 있으면 `for line in f:`로 대체를 고려한다
- [ ] 파일 경로를 문자열 `+`로 합치는 코드를 보면 `pathlib`로 개선할 수 있음을 안다
- [ ] 중요한 파일 쓰기엔 임시 파일 → 교체 패턴이 있어야 함을 안다

---

## 처음 질문으로 돌아가기

**`with` 없이 `open()`이 왜 위험한가요?**
에러가 났을 때 `f.close()`가 보장되지 않아 파일 핸들이 계속 열려있게 됩니다. `with`는 정상이든 에러든 블록 탈출 시 자동으로 닫아줍니다.

**`except:` 하나로 잡는 코드를 어떻게 개선하나요?**
`except FileNotFoundError:`, `except PermissionError:` 처럼 예상하는 에러 클래스를 명시합니다. 예상 못 한 에러는 그대로 위로 올라가야 버그를 발견할 수 있습니다.

**`pathlib`를 쓰면 뭐가 좋아지나요?**
경로를 객체로 다루므로 OS별 구분자 문제가 없어지고, `read_text()`/`write_text()` 같은 편의 메서드로 `with open()` 코드를 한 줄로 줄일 수 있습니다.

**큰 파일을 통째로 읽는 코드, 어떻게 고치나요?**
`f.read()` 대신 `for line in f:`로 줄 단위 처리로 바꿉니다. AI에게 "스트리밍 방식으로 수정해줘"라고 요청하면 됩니다.

---

## 정리

AI가 만든 파일 처리 코드는 정상 경로에 집중하고 실패 경로를 빠뜨리는 경우가 많습니다. `with` 여부, `encoding` 명시, 예외 클래스의 구체성, 파일 크기 고려. 이 네 가지를 점검하는 습관이 생기면 AI 코드를 운영에 바로 투입할 수 있는 품질로 다듬을 수 있습니다.

"에러 처리를 추가해줘"보다 구체적인 요청이 더 좋은 코드를 만들어냅니다. 어떤 에러가 생길 수 있는지 알아야 구체적으로 요청할 수 있고, 이 글이 그 출발점이 됩니다.

다음 편에서는 AI가 클래스를 만들어줬는데 왜 이렇게 짰는지 이해하는 방법을 다룹니다.

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
- **바이브코딩을 위한 Python 기초 (8/10): 파일 I/O와 예외 처리 (현재 글)**
- [바이브코딩을 위한 Python 기초 (9/10): 클래스와 객체](./09-classes-and-objects.md)
- [바이브코딩을 위한 Python 기초 (10/10): 표준 라이브러리 투어](./10-standard-library-tour.md)

<!-- toc:end -->
Tags: 바이브코딩, Python, AI코딩, 파일처리, 예외처리, pathlib
