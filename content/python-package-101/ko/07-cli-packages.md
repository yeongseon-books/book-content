---
title: CLI 패키지 만들기
series: python-package-101
episode: 7
language: ko
status: publish-ready
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
last_reviewed: '2026-05-12'
seo_description: entry point와 click으로 pip install 후 바로 실행 가능한 CLI를 만드는 방법입니다.
---

# CLI 패키지 만들기

패키지는 import해서 쓰는 라이브러리로만 끝나지 않습니다. 잘 만든 패키지는 설치 직후 터미널 명령어로도 실행할 수 있습니다. 이 글은 Python Package 101 시리즈의 7번째 글입니다. 여기서는 `[project.scripts]` entry point가 어떻게 동작하는지, `argparse`와 `click`의 차이는 무엇인지, 그리고 실무에서 쓰기 좋은 CLI 구조를 어떻게 잡는지 정리하겠습니다.

## 이 글에서 다룰 문제

- `pip install` 후 바로 실행되는 명령어는 어떻게 만들까요?
- `[project.scripts]` entry point는 어떻게 동작할까요?
- `argparse`와 `click`은 무엇이 다를까요?
- 서브커맨드 구조는 어떻게 설계할까요?

## 이 글에서 배우는 내용

- `[project.scripts]`로 CLI entry point를 등록하는 방법
- `argparse`로 기본 CLI를 만드는 방법
- `click`으로 선언형 CLI를 만드는 방법
- 서브커맨드 구조를 설계하는 방법

## 왜 중요한가

사용자는 `python my_script.py`보다 `mytool`처럼 바로 실행되는 명령어를 더 편하게 받아들입니다. 패키지에 entry point를 등록해 두면 설치 직후 터미널에서 명령어를 바로 사용할 수 있어 배포 경험이 크게 좋아집니다.

> 팀에서 데이터 변환 스크립트를 `python /opt/scripts/convert.py --input data.csv`로 실행하고 있다고 가정해 보겠습니다. 경로를 외워야 하고, Python 실행기까지 직접 호출해야 합니다.

`pip install mytools` 뒤에 `convert --input data.csv`만 실행하면 사용성과 배포 일관성이 훨씬 좋아집니다.

## 멘탈 모델

entry point는 앱스토어에서 앱을 설치하면 홈 화면에 아이콘이 생기는 것과 비슷합니다. `pip install`이 설치 과정이고, entry point는 생성된 아이콘입니다. 사용자가 명령어를 입력하면 그 아이콘이 눌린 셈이고, 결국 Python 함수가 실행됩니다.

```text
pyproject.toml                     Terminal
─────────────                     ──────
[project.scripts]                 $ greet Alice
greet = "mylib.cli:main"    →    Hello, Alice!
         ↓
   runs the main() function in mylib/cli.py
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| entry point | 패키지 설치 시 등록되는 실행 명령 | `greet = "mylib.cli:main"` |
| [project.scripts] | CLI entry point를 적는 `pyproject.toml` 섹션 | 위 예시 |
| argparse | Python 내장 CLI 인자 파서 | `parser.add_argument('--name')` |
| click | 데코레이터 기반 CLI 프레임워크 | `@click.command()` |
| subcommand | 부모 명령 아래에 붙는 하위 명령 | `git commit`, `git push` |

## Before / After

**Before (run script directly)**

```bash
python /path/to/mylib/cli.py --name Alice
# must remember the path, must invoke python
```

**After (entry point)**

```bash
pip install mylib
greet --name Alice
# runs anywhere, no python invocation needed
```

## 단계별 실습

### Step 1. `argparse`로 기본 CLI 만들기

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

### Step 2. `pyproject.toml`에 entry point 등록

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

### Step 3. `click`으로 리팩터링

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
# Add click dependency to pyproject.toml
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

### Step 4. 서브커맨드 구조 만들기

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
    """Check a file."""
    click.echo(f"Checking: {path}")
```

```bash
pip install -e .
greet                    # prints usage
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
    """Process a file."""
    try:
        with open(path) as f:
            lines = f.readlines()
        click.echo(f"Processed {len(lines)} lines")
    except FileNotFoundError:
        click.echo(f"Error: {path} not found", err=True)
        sys.exit(1)
```

## 이 코드에서 눈여겨볼 점

- entry point 문자열 `"mylib.cli:main"`은 `mylib/cli.py`의 `main` 함수를 가리킵니다.
- `@click.command()` 데코레이터는 함수를 CLI 명령으로 바꿉니다.
- `click.echo`는 유니코드와 파이프 처리 측면에서 `print`보다 안전합니다.
- `err=True`를 주면 에러 메시지가 stdout이 아니라 stderr로 나갑니다.

## 자주 하는 실수

### 실수 1. entry point를 바꿨는데 재설치하지 않는다

`[project.scripts]`를 수정하면 editable install 상태에서도 `pip install -e .`을 다시 실행해야 합니다. entry point는 설치 시점에 생성되기 때문입니다.

### 실수 2. `main()` 함수 시그니처에 인자를 직접 넣는다

```python
# Wrong: entry point cannot pass arguments on its own
def main(name: str): ...

# Correct: let argparse/click handle arguments
def main():
    parser = argparse.ArgumentParser()
    ...
```

### 실수 3. `if __name__ == "__main__"`를 함수 안에 넣는다

이 구문은 파일 끝에 두어야 entry point 실행과 `python -m` 실행을 모두 자연스럽게 지원할 수 있습니다.

### 실수 4. 종료 코드를 제대로 반환하지 않는다

CLI 도구는 성공 시 0, 실패 시 1 이상을 반환해야 합니다. 셸 스크립트와 CI 파이프라인은 이 값을 보고 다음 단계를 이어갈지 결정합니다.

### 실수 5. `--help` 출력을 점검하지 않는다

사용자가 가장 먼저 보는 문서는 거의 항상 `--help`입니다. 설명이 비어 있거나 부정확하면 CLI 전체의 신뢰도가 떨어집니다.

## 실무 적용

- **개발 도구**: `ruff`, `black`, `pytest`는 모두 entry point로 등록된 CLI 패키지입니다.
- **데이터 파이프라인**: CSV 변환, API 호출 같은 작업을 CLI로 만들어 cron과 함께 돌릴 수 있습니다.
- **DevOps 도구**: 배포, 모니터링, 설정 관리 CLI를 사내 패키지로 배포할 수 있습니다.
- **프로토타이핑**: 먼저 `click`으로 CLI를 만들고 이후 웹 UI를 붙일 수 있습니다.
- **테스트 자동화**: `click.testing.CliRunner`로 CLI 출력과 종료 코드를 검증할 수 있습니다.

## 실무에서는 이렇게 생각합니다

CLI에서 가장 중요한 것은 기능 수보다 **일관된 인터페이스**입니다. `--verbose`, `--output`, `--format` 같은 공통 옵션의 이름과 동작을 일관되게 유지해야 사용자가 빠르게 익힐 수 있습니다.

`argparse`는 외부 의존성이 없어 가볍고 기본기 위주로 쓰기 좋습니다. 반면 `click`은 서브커맨드, 프롬프트, 컬러 출력, 테스트 러너까지 갖추고 있어 독립 CLI 패키지에서는 생산성이 더 높습니다.

## 체크리스트

- [ ] `[project.scripts]`로 entry point를 등록할 수 있다
- [ ] `argparse`로 기본 CLI를 만들 수 있다
- [ ] `click`으로 데코레이터 기반 CLI를 만들 수 있다
- [ ] `click.group`으로 서브커맨드 구조를 구현할 수 있다
- [ ] 종료 코드와 stderr 출력을 올바르게 처리할 수 있다

## 연습 문제

1. 두 숫자를 받아 사칙연산을 수행하는 `argparse` 기반 CLI를 만들어 보세요. 예: `calc add 3 5`, `calc mul 2 4`.
2. 같은 CLI를 `click`으로 다시 구현하고 `--help` 출력이 어떻게 달라지는지 비교해 보세요.
3. `click.testing.CliRunner`를 사용해 CLI 출력을 검증하는 pytest를 작성해 보세요.

## 정리 · 다음 글

- `[project.scripts]`는 `pip install` 직후 사용할 수 있는 CLI 명령을 등록합니다.
- entry point는 `"module:function"` 형식으로 실행할 함수를 지정합니다.
- `argparse`는 내장 도구이고, `click`은 더 생산적인 데코레이터 기반 프레임워크입니다.
- `click.group()`으로 서브커맨드 구조를 만들 수 있습니다.
- CLI는 성공 시 0, 실패 시 1 이상을 반환해야 합니다.

다음 글에서는 **타입 힌트와 정적 검사** — mypy, `py.typed`, 타입 안전한 패키지를 다룹니다.

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

Tags: Python, CLI, Entry Point, click, argparse, Command Line
