---
title: 환경변수와 PATH
series: linux-cli-101
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
- Linux
- Environment Variable
- PATH
- bashrc
- Shell
- Configuration
last_reviewed: '2026-05-12'
seo_description: 환경변수와 PATH가 명령 실행과 설정 전달에 쓰이는 방식을 정리합니다.
---

# 환경변수와 PATH

`python`을 입력하면 Shell이 Python 실행 파일을 찾아서 실행합니다. 어떻게 찾을까요? 모든 디렉터리를 뒤지는 것이 아니라, PATH에 등록된 디렉터리만 순서대로 확인합니다. PATH에 없으면 "command not found"입니다.

이 글은 Linux CLI 101 시리즈의 8번째 글입니다.

## 이 글에서 다룰 문제

- 환경변수는 어떤 방식으로 프로세스에 전달될까요?
- `export`와 로컬 Shell 변수는 무엇이 다를까요?
- `PATH`는 명령 실행에서 어떤 검색 순서를 만들까요?
- 도구를 설치했는데 command not found가 뜨면 무엇부터 봐야 할까요?

> 환경변수는 프로세스에 붙은 이름표이고, PATH는 Shell이 명령어를 찾아다니는 지도입니다.

## 머릿속에 먼저 그릴 그림

> 환경변수는 프로세스에 붙은 이름표이고, PATH는 Shell이 명령어를 찾아다니는 지도입니다.

택배 기사가 배달할 때 주소록(PATH)을 순서대로 확인합니다. 주소록에 없는 곳은 가지 않습니다. 새 가게가 생기면 주소록에 추가해야 기사가 찾아갑니다.

```text
$ python
Shell searches PATH in order:
  /usr/local/bin/python  -> not found
  /usr/bin/python         -> found! -> execute
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| 환경변수 | 프로세스에 전달되는 key=value 쌍 | `HOME=/home/user` |
| PATH | 명령어 검색 경로 목록 (`:` 구분) | `/usr/local/bin:/usr/bin:/bin` |
| export | 자식 프로세스에도 변수를 전달 | `export API_KEY=abc123` |
| .bashrc | 대화형 bash shell 시작 시 실행 | `~/.bashrc` |
| .bash_profile | 로그인 shell 시작 시 실행 | `~/.bash_profile` |

## 전과 후

**Before (PATH를 모를 때)**

```bash
pip install httpie
http GET https://api.example.com
# bash: http: command not found
# "Why doesn't it work? I just installed it..."
```

**After (PATH를 이해할 때)**

```bash
pip install httpie
which http || pip show httpie | grep Location
# Location: /home/user/.local/lib/python3.11/site-packages
# -> check if ~/.local/bin is in PATH
echo $PATH | tr ':' '\n' | grep local
# If /home/user/.local/bin is missing:
export PATH="$HOME/.local/bin:$PATH"
http GET https://api.example.com   # Works
```

## 단계별 실습

### 1단계. 환경변수 확인

```bash
echo $HOME                    # Home directory
echo $USER                    # Current user
echo $SHELL                   # Current shell
echo $PATH                    # Command search paths

env                           # Print all environment variables
env | grep -i python          # Python-related variables only
```

### 2단계. 변수 설정과 내보내기

```bash
MY_VAR="hello"                # Shell variable (not passed to children)
echo $MY_VAR                  # hello

bash -c 'echo $MY_VAR'       # (empty) — not available in child process

export MY_VAR                 # export passes it to children
bash -c 'echo $MY_VAR'       # hello

export DB_HOST="localhost"    # Declare and export at once
```

### 3단계. 실행 경로 수정

```bash
echo $PATH | tr ':' '\n'     # View PATH one entry per line

# Temporary addition (current session only)
export PATH="$HOME/mytools:$PATH"

# Check command location
which python
which ls
```

### 4단계. 셸 시작 파일에 영구 설정

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export EDITOR=vim' >> ~/.bashrc

source ~/.bashrc             # Apply immediately (or open a new terminal)
echo $EDITOR
# vim
```

### 5단계. 환경 파일 패턴

```bash
cat > ~/practice/linux-cli/.env << 'EOF'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
API_KEY=secret-key-123
EOF

# Load .env file in Shell
set -a                        # Auto-export subsequent variables
source ~/practice/linux-cli/.env
set +a
echo $DB_HOST                 # localhost
```

## 이 코드에서 봐야 할 것

- `export` 없이 설정한 변수는 현재 Shell에서만 유효하고 자식 프로세스에 전달되지 않습니다
- PATH는 `:` 구분자로 여러 경로를 나열하며, 왼쪽이 우선합니다
- `source ~/.bashrc`는 현재 Shell에서 파일을 실행합니다. `.`도 같은 의미입니다
- `.env` 파일은 Git에 커밋하면 안 됩니다 (API 키 등 민감 정보 포함)

## 자주 하는 실수

### 실수 1. 실행 경로를 덮어쓴다

```bash
export PATH="/my/new/path"              # Entire existing PATH is gone!
export PATH="/my/new/path:$PATH"        # Appends to existing PATH — safe
```

### 실수 2. 시작 파일 역할을 혼동한다

로그인 셸(SSH 접속)은 `.bash_profile`을 읽고, 비로그인 대화형 셸(터미널 앱)은 `.bashrc`를 읽습니다. 보통 `.bash_profile`에서 `.bashrc`를 source하여 통일합니다.

### 실수 3. 변수 참조 시 중괄호를 생략한다

```bash
echo "$HOME_backup"           # Looks for a variable named HOME_backup
echo "${HOME}_backup"         # HOME variable + "_backup" string
```

### 실수 4. 환경 파일을 저장소에 커밋한다

API 키, 비밀번호가 포함된 `.env`가 공개 저장소에 올라가면 보안 사고입니다. `.gitignore`에 반드시 `.env`를 추가하세요.

### 실수 5. 내보내기를 빼먹고 변수 전달이 안 된다고 생각한다

Python 스크립트에서 `os.environ["MY_VAR"]`를 읽으려면, Shell에서 `export`로 내보내야 합니다. `MY_VAR=hello`만으로는 자식 프로세스인 Python이 볼 수 없습니다.

## 실무 적용

- **12-Factor App**: 설정을 코드가 아닌 환경변수로 관리합니다 (DB 접속 정보, API 키 등)
- **가상환경 활성화**: `source venv/bin/activate`는 PATH 앞에 venv의 bin/을 추가합니다
- **CI/CD 변수**: GitHub Actions의 `env:`는 환경변수를 설정하는 것입니다
- **Docker**: `docker run -e DB_HOST=db`로 컨테이너에 환경변수를 전달합니다
- 디버깅: `env | sort`로 현재 환경을 덤프하여 문제를 진단합니다

## 실무에서는 이렇게 생각한다

환경변수는 "코드 밖의 설정"을 관리하는 표준 방법입니다. 같은 코드를 개발/스테이징/프로덕션에서 돌릴 때, 코드를 바꾸는 대신 `DB_HOST` 환경변수만 바꾸면 됩니다. 이것이 12-Factor App 방법론의 핵심이며, Docker, Kubernetes 환경에서 설정을 주입하는 기본 방식입니다.

반면 환경변수가 너무 많아지면 관리가 어려워집니다. 이때는 `.env` 파일을 환경별로 관리하거나, AWS Parameter Store, HashiCorp Vault 같은 시크릿 관리 도구로 넘어갑니다. 하지만 모든 것의 출발점은 `export`와 `$PATH`를 이해하는 것입니다.

## 체크리스트

- [ ] `echo $PATH`의 출력을 읽고 명령어 검색 순서를 설명할 수 있다
- [ ] `export`와 단순 변수 대입의 차이를 안다
- [ ] `.bashrc`에 PATH를 영구적으로 추가할 수 있다
- [ ] `.env` 파일을 만들고 `source`로 로드할 수 있다
- [ ] `.env` 파일을 `.gitignore`에 추가하는 이유를 안다

## 연습 문제

1. `MY_NAME=linux-cli`와 `export MY_NAME=linux-cli`를 각각 실행한 뒤 하위 Shell에서 보이는 차이를 확인해 보세요.
2. `echo $PATH` 결과를 줄마다 나눠 보고, 자주 쓰는 명령이 어느 디렉터리에서 오는지 `which`로 확인해 보세요.
3. 가상의 `.env` 파일을 하나 만들고 Shell에서 읽어 오는 흐름을 직접 연습해 보세요.

## 정리와 다음 글

- 환경변수는 프로세스에 전달되는 key=value 설정이며 `export`로 자식에게 상속됩니다.
- PATH는 Shell이 명령어를 찾는 디렉터리 목록이며 `:` 구분, 왼쪽 우선입니다.
- `.bashrc`에 설정을 추가하면 새 Shell마다 자동 적용됩니다.
- `.env` 파일은 애플리케이션 설정 관리에 유용하지만 Git에 커밋하면 안 됩니다.
- `export`를 빼먹으면 자식 프로세스(Python, Docker 등)가 변수를 볼 수 없습니다.

다음 글에서는 **간단한 shell script** — 반복 작업을 자동화하는 스크립트 작성법을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [파일과 디렉터리 다루기](./02-files-and-directories.md)
- [권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- [cat, less, head, tail — 파일 내용 보기](./04-viewing-files.md)
- [grep, find, xargs — 검색의 삼총사](./05-grep-find-xargs.md)
- [pipe와 redirection](./06-pipe-and-redirection.md)
- [프로세스 확인과 종료](./07-process-management.md)
- **환경변수와 PATH (현재 글)**
- 간단한 shell script (예정)
- SSH와 원격 서버 접속 (예정)

<!-- toc:end -->

## 참고 자료

- [GNU Bash Manual - Shell Variables](https://www.gnu.org/software/bash/manual/html_node/Shell-Variables.html)
- [The Twelve-Factor App - Config](https://12factor.net/config)
- [Linux man page - environ](https://man7.org/linux/man-pages/man7/environ.7.html)
- [dotenv pattern - Best practices](https://github.com/motdotla/dotenv)

Tags: Linux, Environment Variable, PATH, bashrc, Shell, Configuration
