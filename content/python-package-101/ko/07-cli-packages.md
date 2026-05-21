---
title: "Python Package 101 (7/10): CLI 패키지 만들기"
series: python-package-101
episode: 7
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- Python
- CLI
- Entry Point
- click
- argparse
- Command Line
last_reviewed: '2026-05-15'
seo_description: entry point와 click으로 pip install 후 바로 실행 가능한 CLI를 만드는 방법입니다.
---

# Python Package 101 (7/10): CLI 패키지 만들기

패키지는 import해서 쓰는 라이브러리로만 끝나지 않습니다. 잘 만든 패키지는 설치 직후 터미널 명령어로도 실행할 수 있습니다.

이 글은 Python Package 101 시리즈의 7번째 글입니다. 여기서는 `[project.scripts]` entry point가 어떻게 동작하는지, `argparse`와 `click`의 차이는 무엇인지, 그리고 실무에서 쓰기 좋은 CLI 구조를 어떻게 잡는지 정리하겠습니다.

![Python Package 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/python-package-101/07/07-01-mental-model.ko.png)
*Python Package 101 7장 흐름 개요*

## 먼저 던지는 질문

- `pip install` 후 바로 실행되는 명령어는 어떻게 만들까요?
- `[project.scripts]` entry point는 어떻게 동작할까요?
- `argparse`와 `click`은 무엇이 다를까요?

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

## 적용 전후 비교
**Before (스크립트 직접 실행)**

```bash
python /path/to/mylib/cli.py --name Alice
# must remember the path, must invoke python
```

**After (엔트리 포인트)**

```bash
pip install mylib
greet --name Alice
# runs anywhere, no python invocation needed
```

## 단계별 실습

### 단계 1. `argparse`로 기본 CLI 만들기

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

### 단계 2. `pyproject.toml`에 entry point 등록

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

### 단계 3. `click`으로 리팩터링

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

### 단계 4. 서브커맨드 구조 만들기

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

### 단계 5. 에러 처리와 종료 코드

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
# 잘못된 방법: 진입점이 스스로 인자를 전달할 수 없다
def main(name: str): ...

# 정답: argparse/click이 인수를 처리하도록 하세요.
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

## Entry Point 동작 원리

`[project.scripts]`에 등록한 entry point는 `pip install` 시 실행 가능한 래퍼 스크립트를 생성합니다.

### 설정과 생성되는 파일

```toml
# pyproject.toml
[project.scripts]
acme = "acme_utils.cli:main"
```

```bash
pip install -e .
which acme
# /home/user/.local/bin/acme (또는 .venv/bin/acme)
```

```python
# 생성되는 래퍼 스크립트 (자동 생성됨, 직접 수정 불필요)
# !/path/to/.venv/bin/python
from acme_utils.cli import main
import sys
sys.exit(main())
```

### entry point 종류

| 종류 | 설정 키 | 용도 |
|---|---|---|
| console_scripts | `[project.scripts]` | 터미널 명령 |
| gui_scripts | `[project.gui-scripts]` | GUI 앱 (Windows에서 콘솔 창 없음) |
| plugins | `[project.entry-points]` | 플러그인 확장 포인트 |

## Click으로 CLI 만들기

Click은 Python CLI 프레임워크 중 가장 널리 사용됩니다. 데코레이터 기반으로 명령, 옵션, 인자를 선언합니다.

### 기본 구조

```python
# src/acme_utils/cli.py
import click

@click.group()
@click.version_option()
def main():
    """Acme utility CLI."""
    pass

@main.command()
@click.argument("name")
@click.option("--greeting", "-g", default="Hello", help="Greeting message")
def hello(name: str, greeting: str):
    """Greet someone."""
    click.echo(f"{greeting}, {name}!")

@main.command()
@click.option("--format", "-f", type=click.Choice(["json", "yaml", "toml"]), default="json")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def config(format: str, output: str | None):
    """Generate configuration template."""
    import json
    template = {"name": "acme-app", "version": "1.0.0", "debug": False}
    
    result = json.dumps(template, indent=2)
    
    if output:
        with open(output, "w") as f:
            f.write(result)
        click.echo(f"Written to {output}")
    else:
        click.echo(result)
```

```bash
# 사용 예시
acme --version
# acme-utils, version 0.1.0

acme hello World
# Hello, World!

acme hello --greeting "Hi" Alice
# Hi, Alice!

acme config --format json --output config.json
# Written to config.json
```

### Click의 자동 도움말

```bash
acme --help
# Usage: acme [OPTIONS] COMMAND [ARGS]...
# 
#   Acme utility CLI.
# 
# Options:
#   --version  Show the version and exit.
#   --help     Show this message and exit.
# 
# Commands:
#   config  Generate configuration template.
#   hello   Greet someone.
```

## Typer: Click의 현대적 대안

Typer는 Click 위에 구축되었지만 타입 힌트를 활용하여 더 간결한 코드를 제공합니다.

```python
# src/acme_utils/cli.py
import typer
from typing import Annotated

app = typer.Typer(help="Acme utility CLI.")

@app.command()
def hello(
    name: str,
    greeting: Annotated[str, typer.Option("--greeting", "-g")] = "Hello",
):
    """Greet someone."""
    typer.echo(f"{greeting}, {name}!")

@app.command()
def init(
    project_name: str,
    force: Annotated[bool, typer.Option("--force", "-f")] = False,
):
    """Initialize a new project."""
    if force:
        typer.echo(f"Force creating {project_name}...")
    else:
        typer.echo(f"Creating {project_name}...")

def main():
    app()
```

### Click vs Typer 비교

| 항목 | Click | Typer |
|---|---|---|
| 타입 선언 | 데코레이터 매개변수 | Python 타입 힌트 |
| 학습 곡선 | 중간 | 낮음 |
| 생태계 | 매우 넓음 | Click 생태계 활용 |
| 자동 완성 | 별도 설정 | 내장 지원 |
| Python 최소 버전 | 3.7+ | 3.7+ |

## argparse: 표준 라이브러리 선택지

외부 의존성을 추가하고 싶지 않다면 `argparse`를 사용할 수 있습니다.

```python
# src/acme_utils/cli.py
import argparse
import sys

def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="acme",
        description="Acme utility CLI",
    )
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    
    subparsers = parser.add_subparsers(dest="command")
    
    # hello 서브커맨드
    hello_parser = subparsers.add_parser("hello", help="Greet someone")
    hello_parser.add_argument("name")
    hello_parser.add_argument("--greeting", "-g", default="Hello")
    
    # init 서브커맨드
    init_parser = subparsers.add_parser("init", help="Initialize project")
    init_parser.add_argument("project_name")
    init_parser.add_argument("--force", "-f", action="store_true")
    
    return parser

def main() -> int:
    parser = create_parser()
    args = parser.parse_args()
    
    if args.command == "hello":
        print(f"{args.greeting}, {args.name}!")
    elif args.command == "init":
        print(f"Creating {args.project_name}...")
    else:
        parser.print_help()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## CLI 테스트

### Click 테스트

```python
# tests/test_cli.py
from click.testing import CliRunner
from acme_utils.cli import main

def test_hello():
    runner = CliRunner()
    result = runner.invoke(main, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.output

def test_hello_with_greeting():
    runner = CliRunner()
    result = runner.invoke(main, ["hello", "--greeting", "Hi", "Alice"])
    assert result.exit_code == 0
    assert "Hi, Alice!" in result.output

def test_version():
    runner = CliRunner()
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert "version" in result.output
```

### Typer 테스트

```python
from typer.testing import CliRunner
from acme_utils.cli import app

runner = CliRunner()

def test_hello():
    result = runner.invoke(app, ["hello", "World"])
    assert result.exit_code == 0
    assert "Hello, World!" in result.output
```

## 종료 코드 관리

CLI 도구는 적절한 종료 코드를 반환해야 스크립트와 CI에서 올바르게 동작합니다.

```python
import sys
import click

@click.command()
@click.argument("path", type=click.Path(exists=True))
def lint(path: str):
    """Lint Python files."""
    errors = run_linter(path)
    
    if errors:
        for err in errors:
            click.echo(f"ERROR: {err}", err=True)
        sys.exit(1)  # 실패: 비정상 종료 코드
    
    click.echo("All checks passed!")
    sys.exit(0)  # 성공
```

```text
종료 코드 규칙:
0   - 성공
1   - 일반 에러
2   - CLI 사용법 에러 (잘못된 인자)
130 - Ctrl+C로 중단됨 (128 + SIGINT)
```

## Rich를 활용한 터미널 출력

```python
from rich.console import Console
from rich.table import Table
from rich.progress import track
import time

console = Console()

def show_packages():
    table = Table(title="Installed Packages")
    table.add_column("Name", style="cyan")
    table.add_column("Version", style="green")
    table.add_column("Location")
    
    table.add_row("httpx", "0.27.2", "site-packages/httpx")
    table.add_row("pydantic", "2.8.2", "site-packages/pydantic")
    
    console.print(table)

def process_files(files: list[str]):
    for file in track(files, description="Processing..."):
        time.sleep(0.1)  # 실제 작업
    console.print("[green]Done![/green]")
```

## 셸 자동 완성 설정

### Click 자동 완성

```bash
# Bash
_ACME_COMPLETE=bash_source acme > ~/.acme-complete.bash
echo '. ~/.acme-complete.bash' >> ~/.bashrc

# Zsh
_ACME_COMPLETE=zsh_source acme > ~/.acme-complete.zsh
echo '. ~/.acme-complete.zsh' >> ~/.zshrc

# Fish
_ACME_COMPLETE=fish_source acme > ~/.config/fish/completions/acme.fish
```

### Typer 자동 완성

```bash
# Typer는 내장 지원
acme --install-completion
# 자동으로 셸에 맞는 완성 스크립트 설치
```

## CLI 패키지 배포 구조

CLI 패키지의 전체 프로젝트 구조와 pyproject.toml을 정리합니다.

```text
acme-cli/
├── src/
│   └── acme_cli/
│       ├── __init__.py
│       ├── __main__.py      # python -m acme_cli 지원
│       ├── cli.py           # Click/Typer 앱 정의
│       ├── commands/        # 서브커맨드 모듈
│       │   ├── __init__.py
│       │   ├── init.py
│       │   ├── build.py
│       │   └── deploy.py
│       └── utils.py         # 공용 헬퍼
├── tests/
│   ├── test_cli.py
│   └── test_commands/
├── pyproject.toml
└── README.md
```

### `__main__.py`: `python -m` 지원

```python
# src/acme_cli/__main__.py
from .cli import main

if __name__ == "__main__":
    main()
```

```bash
# 두 가지 실행 방법 모두 지원
acme --help                # entry point
python -m acme_cli --help  # __main__.py
```

### pyproject.toml 전체 설정

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "acme-cli"
version = "0.1.0"
description = "Command-line tools for Acme platform"
requires-python = ">=3.10"
dependencies = [
    "click>=8.1",
    "rich>=13.0",
    "httpx>=0.27",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-cov>=5.0",
]

[project.scripts]
acme = "acme_cli.cli:main"

[tool.hatch.build.targets.wheel]
packages = ["src/acme_cli"]
```

## 설정 파일 관리

CLI 도구는 사용자 설정을 파일로 저장하는 경우가 많습니다.

```python
# src/acme_cli/config.py
from pathlib import Path
import tomllib  # Python 3.11+

def get_config_dir() -> Path:
    """XDG Base Directory 규칙에 따른 설정 디렉터리."""
    xdg = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    config_dir = xdg / "acme"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir

def load_config() -> dict:
    config_path = get_config_dir() / "config.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            return tomllib.load(f)
    return {}
```

```toml
# ~/.config/acme/config.toml
[defaults]
output_format = "json"
verbose = false

[auth]
api_url = "https://api.acme.dev"
```

## 환경 변수와 CLI 옵션 우선순위

CLI 도구의 설정 값은 여러 출처에서 올 수 있습니다. 일반적인 우선순위는 다음과 같습니다.

```text
우선순위 (높음 → 낮음):
1. CLI 옵션 (--format json)
2. 환경 변수 (ACME_FORMAT=json)
3. 설정 파일 (~/.config/acme/config.toml)
4. 기본값 (코드에 하드코딩)
```

```python
@click.command()
@click.option(
    "--api-url",
    envvar="ACME_API_URL",       # 환경 변수에서도 읽기
    default="https://api.acme.dev",
    help="API endpoint URL",
)
def deploy(api_url: str):
    """Deploy to Acme platform."""
    click.echo(f"Deploying to {api_url}...")
```

```bash
# 세 가지 방법 모두 동일하게 동작
acme deploy --api-url https://staging.acme.dev
ACME_API_URL=https://staging.acme.dev acme deploy
# 또는 config.toml에 설정
```

이 우선순위 체계를 잘 설계하면 사용자는 반복적인 옵션 입력 없이도 CLI를 편리하게 사용할 수 있고, 필요할 때만 명시적으로 값을 재정의할 수 있습니다. 대부분의 성숙한 CLI 도구(`aws`, `gh`, `docker`)가 이 패턴을 따릅니다.

## 처음 질문으로 돌아가기

- **`pip install` 후 바로 실행되는 명령어는 어떻게 만들까요?**
  - `pyproject.toml`의 `[project.scripts]`에 `명령이름 = "패키지.모듈:함수"` 형식으로 entry point를 등록합니다. `pip install` 시 해당 함수를 호출하는 래퍼 스크립트가 `bin/` 디렉터리에 자동 생성되어 터미널에서 바로 실행할 수 있게 됩니다.

- **`[project.scripts]` entry point는 어떻게 동작할까요?**
  - pip은 설치 시 `site-packages`의 `.dist-info/entry_points.txt`에 매핑을 기록하고, `bin/` 디렉터리에 Python 래퍼 스크립트를 생성합니다. 이 스크립트는 지정된 모듈을 import하고 지정된 함수를 호출하며, 함수의 반환값을 `sys.exit()`에 전달합니다.

- **CLI 프레임워크는 어떤 것을 선택해야 할까요?**
  - 외부 의존성을 원하지 않으면 `argparse`, 풍부한 생태계와 플러그인이 필요하면 `click`, 타입 힌트 기반 간결한 코드를 원하면 `typer`를 선택합니다. `typer`는 내부적으로 `click`을 사용하므로 click의 기능을 그대로 쓸 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Python Package 101 (1/10): Python Package란 무엇인가?](./01-what-is-a-python-package.md)
- [Python Package 101 (2/10): 프로젝트 구조 잡기 — src layout과 pyproject.toml](./02-project-structure.md)
- [Python Package 101 (3/10): 의존성 관리 — venv, pip, uv, requirements](./03-dependency-management.md)
- [Python Package 101 (4/10): 패키지 빌드하기 — wheel과 sdist](./04-building-packages.md)
- [Python Package 101 (5/10): PyPI에 배포하기 — TestPyPI부터 실제 배포까지](./05-publishing-to-pypi.md)
- [Python Package 101 (6/10): 버전 관리와 릴리스](./06-versioning-and-releases.md)
- **Python Package 101 (7/10): CLI 패키지 만들기 (현재 글)**
- Python Package 101 (8/10): 타입 힌트와 정적 검사 (예정)
- Python Package 101 (9/10): 문서화 — README, MkDocs, API Reference (예정)
- Python Package 101 (10/10): 실전 패키지 템플릿 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/python-package-101/ko)
- [Python Packaging - Entry Points](https://packaging.python.org/en/latest/specifications/entry-points/)
- [click documentation](https://click.palletsprojects.com/)
- [argparse documentation](https://docs.python.org/3/library/argparse.html)
- [Real Python - Python CLI with Click](https://realpython.com/python-click/)

Tags: Python, Packaging, PyPI, pyproject.toml
