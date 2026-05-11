---
title: CLI 패키지 만들기
series: python-package-101
episode: 7
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Python
- CLI
- Entry Point
- click
- argparse
- Command Line
last_reviewed: '2026-05-04'
seo_description: entry point와 click으로 pip install 후 바로 실행 가능한 CLI를 만드는 방법입니다.
---

# CLI 패키지 만들기

> Python Package 101 시리즈 (7/10)

---


## 이 글에서 다룰 문제

Python 스크립트를 `python my_script.py`로 실행하는 것보다 `mytool`로 바로 실행하는 것이 편합니다. 패키지에 entry point를 설정하면 `pip install` 후 바로 터미널 명령어로 쓸 수 있습니다.

> 팀에서 데이터 변환 스크립트를 `python /opt/scripts/convert.py --input data.csv`로 실행합니다. 경로를 기억해야 하고, Python을 직접 호출해야 합니다.

`pip install mytools` 후 `convert --input data.csv`로 실행하면 훨씬 간결합니다.

## Mental Model

> Entry point는 앱스토어에서 앱을 설치하면 바탕화면에 아이콘이 생기는 것과 같습니다. `pip install`이 설치이고, entry point가 아이콘입니다. 아이콘을 클릭하면(명령어를 입력하면) 앱(Python 함수)이 실행됩니다.

```text
pyproject.toml                     터미널
─────────────                     ──────
[project.scripts]                 $ greet Alice
greet = "mylib.cli:main"    →    Hello, Alice!
         ↓
   mylib/cli.py의 main() 함수 실행
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| entry point | 패키지 설치 시 등록되는 실행 가능 명령어 | `greet = "mylib.cli:main"` |
| [project.scripts] | pyproject.toml의 CLI entry point 섹션 | 위 예시 |
| argparse | Python 내장 CLI 인자 파서 | `parser.add_argument('--name')` |
| click | 데코레이터 기반 CLI 프레임워크 | `@click.command()` |
| subcommand | 명령어 아래의 하위 명령어 | `git commit`, `git push` |

## Before / After

**Before (스크립트 직접 실행)**

```bash
python /path/to/mylib/cli.py --name Alice
# 경로를 기억해야 함, python을 직접 호출
```

**After (entry point)**

```bash
pip install mylib
greet --name Alice
# 어디서든 실행 가능, python 호출 불필요
```

## 단계별 실습

### Step 1. argparse로 기본 CLI 만들기

```python
# src/mylib/cli.py
import argparse

def main():
    parser = argparse.ArgumentParser(description="Greet someone")
    parser.add_argument("name", help="Name to greet")
    parser.add_argument("--count", type=int, default=1, help="Number of greetings")
    args = parser.parse_args()

    for i in range(args.count):
        print(f"[{i+1}] Hello, {args.name}!")

if __name__ == "__main__":
    main()
```

### Step 2. pyproject.toml에 entry point 등록

```toml
[project.scripts]
greet = "mylib.cli:main"
```

```bash
pip install -e .
greet Alice
# [1] Hello, Alice!

greet Alice --count 3
# [1] Hello, Alice!
# [2] Hello, Alice!
# [3] Hello, Alice!
```

### Step 3. click으로 리팩터링

```python
# src/mylib/cli.py
import click

@click.command()
@click.argument("name")
@click.option("--count", default=1, help="Number of greetings")
def main(name: str, count: int):
    """Greet someone."""
    for i in range(count):
        click.echo(f"[{i+1}] Hello, {name}!")

if __name__ == "__main__":
    main()
```

```toml
# pyproject.toml에 click 의존성 추가
[project]
dependencies = ["click>=8.0"]
```

```bash
pip install -e .
greet Alice --count 3
greet --help
# Usage: greet [OPTIONS] NAME
#   Greet someone.
# Options:
#   --count INTEGER  Number of greetings
#   --help           Show this message and exit.
```

### Step 4. 서브커맨드 구조

```python
# src/mylib/cli.py
import click

@click.group()
def main():
    """mylib CLI tool."""
    pass

@main.command()
@click.argument("name")
def greet(name: str):
    """Greet someone."""
    click.echo(f"Hello, {name}!")

@main.command()
@click.argument("path", type=click.Path(exists=True))
def check(path: str):
    """파일을 검사합니다."""
    click.echo(f"Checking: {path}")
```

```bash
pip install -e .
greet                    # Usage 출력
greet greet Alice        # Hello, Alice!
greet check README.md    # Checking: README.md
```

### Step 5. 에러 처리와 종료 코드

```python
import sys
import click

@click.command()
@click.argument("path", type=click.Path())
def main(path: str):
    """파일을 처리합니다."""
    try:
        with open(path) as f:
            lines = f.readlines()
        click.echo(f"Processed {len(lines)} lines")
    except FileNotFoundError:
        click.echo(f"Error: {path} not found", err=True)
        sys.exit(1)
```

## 이 코드에서 봐야 할 것

- entry point의 `"mylib.cli:main"`은 `mylib/cli.py` 모듈의 `main` 함수를 가리킵니다
- `click`의 `@click.command()` 데코레이터가 함수를 CLI 명령어로 변환합니다
- `click.echo`는 `print`보다 유니코드와 파이프 처리에 안전합니다
- `err=True`로 에러 메시지를 stderr로 보냅니다

## 자주 하는 실수

### 실수 1. entry point를 수정한 후 재설치하지 않는다

`[project.scripts]`를 수정하면 `pip install -e .`를 다시 실행해야 합니다. editable install도 entry point는 재설치가 필요합니다.

### 실수 2. main() 함수에 인자를 넣는다

```python
# 잘못: entry point에서 호출할 때 인자를 전달할 수 없음
def main(name: str): ...

# 올바름: argparse/click이 인자를 처리
def main():
    parser = argparse.ArgumentParser()
    ...
```

### 실수 3. if __name__ == "__main__"을 entry point 함수 안에 넣는다

`if __name__ == "__main__": main()`은 파일 끝에 두어야 합니다. entry point와 `python -m` 실행을 모두 지원하기 위한 것입니다.

### 실수 4. 종료 코드를 반환하지 않는다

CLI 도구는 성공 시 0, 실패 시 1 이상의 종료 코드를 반환해야 합니다. 파이프라인에서 다음 단계 실행 여부를 결정합니다.

### 실수 5. --help 출력을 확인하지 않는다

`--help`는 사용자가 가장 먼저 보는 문서입니다. 설명이 없거나 부정확하면 사용자가 혼란스럽습니다.

## 실무 적용

- **개발 도구**: `ruff`, `black`, `pytest`는 모두 entry point로 등록된 CLI 패키지입니다
- **데이터 파이프라인**: CSV 변환, API 호출 등을 CLI 도구로 만들어 cron에서 실행합니다
- **DevOps 도구**: 배포, 모니터링, 설정 관리 CLI를 사내 패키지로 배포합니다
- **프로토타이핑**: `click`으로 빠르게 CLI를 만들고, 나중에 웹 UI를 추가합니다
- **테스트**: `click.testing.CliRunner`로 CLI 출력을 프로그래밍으로 검증합니다

## 실무에서는 이렇게 생각한다

CLI를 만들 때 가장 중요한 것은 **일관된 인터페이스**입니다. `--verbose`, `--output`, `--format` 같은 공통 옵션의 이름과 동작을 통일하면 사용자가 직관적으로 씁니다.

`argparse`는 외부 의존성이 없어 가볍지만, `click`은 서브커맨드, 프롬프트, 색상 출력, 테스트 러너를 내장하여 실무에서 더 생산적입니다. 라이브러리라면 `argparse`, 독립 CLI 도구라면 `click`이 적합합니다.

## 체크리스트

- [ ] `[project.scripts]`로 entry point를 등록할 수 있다
- [ ] `argparse`로 기본 CLI를 만들 수 있다
- [ ] `click`으로 데코레이터 기반 CLI를 만들 수 있다
- [ ] 서브커맨드 구조를 `click.group`으로 구현할 수 있다
- [ ] CLI의 종료 코드와 stderr 출력을 올바르게 처리할 수 있다

## 정리 · 다음 글

- `[project.scripts]`로 `pip install` 후 바로 쓸 수 있는 CLI 명령어를 등록합니다.
- entry point는 `"모듈:함수"` 형식으로 실행할 함수를 지정합니다.
- `argparse`는 내장, `click`은 데코레이터 기반의 더 생산적인 CLI 프레임워크입니다.
- `click.group()`으로 서브커맨드 구조를 만듭니다.
- CLI는 성공 시 0, 실패 시 1 이상의 종료 코드를 반환해야 합니다.

다음 글에서는 **타입 힌트와 정적 검사** — mypy, py.typed, 타입 안전한 패키지를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- [패키지 빌드하기 — wheel과 sdist](./04-building-packages.md)
- [PyPI에 배포하기 — TestPyPI부터 실제 배포까지](./05-publishing-to-pypi.md)
- [버전 관리와 릴리스](./06-versioning-and-releases.md)
- **CLI 패키지 만들기 (현재 글)**
- 타입 힌트와 정적 검사 (예정)
- 문서화 — README, MkDocs, API Reference (예정)
- 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Python Packaging - Entry Points](https://packaging.python.org/en/latest/specifications/entry-points/)
- [click documentation](https://click.palletsprojects.com/)
- [argparse documentation](https://docs.python.org/3/library/argparse.html)
- [Real Python - Python CLI with Click](https://realpython.com/python-click/)
