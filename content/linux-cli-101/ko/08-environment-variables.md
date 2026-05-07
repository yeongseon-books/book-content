---
title: 환경변수와 PATH
series: linux-cli-101
episode: 8
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Linux
- Environment Variable
- PATH
- bashrc
- Shell
- Configuration
last_reviewed: '2026-05-04'
seo_description: 환경변수는 프로세스에 붙은 이름표이고, PATH는 Shell이 명령어를 찾아다니는 지도입니다.
---

# 환경변수와 PATH

> Linux CLI 101 시리즈 (8/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- 환경변수란 무엇이고 왜 필요할까요?
- `echo $PATH`의 출력은 무엇을 의미할까요?
- `export`와 단순 변수 대입의 차이는 무엇일까요?
- `.bashrc`, `.bash_profile`, `.profile`은 각각 언제 실행될까요?

> 환경변수는 프로세스에 붙은 이름표이고, PATH는 Shell이 명령어를 찾아다니는 지도입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 환경변수의 개념과 `echo`, `env`, `export`로 확인/설정하는 법
- PATH가 명령어 검색에 작동하는 원리
- `.bashrc`, `.bash_profile`에 영구 설정을 추가하는 법
- `.env` 파일로 애플리케이션 설정을 관리하는 법

## 왜 중요한가

`python`을 입력하면 Shell이 Python 실행 파일을 찾아서 실행합니다. 어떻게 찾을까요? 모든 디렉터리를 뒤지는 것이 아니라, PATH에 등록된 디렉터리만 순서대로 확인합니다. PATH에 없으면 "command not found"입니다.

> `pip install`로 패키지를 설치했는데 `mycommand`를 입력하면 "command not found"가 뜹니다. 패키지는 설치되었는데 왜 실행이 안 될까요? 설치 경로가 PATH에 없기 때문입니다.

## Mental Model

> 환경변수는 프로세스에 붙은 이름표이고, PATH는 Shell이 명령어를 찾아다니는 지도입니다.

택배 기사가 배달할 때 주소록(PATH)을 순서대로 확인합니다. 주소록에 없는 곳은 가지 않습니다. 새 가게가 생기면 주소록에 추가해야 기사가 찾아갑니다.

```text
$ python
Shell이 PATH를 순서대로 탐색:
  /usr/local/bin/python  → 없음
  /usr/bin/python         → 있음! → 실행
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| 환경변수 | 프로세스에 전달되는 key=value 쌍 | `HOME=/home/user` |
| PATH | 명령어 검색 경로 목록 (`:` 구분) | `/usr/local/bin:/usr/bin:/bin` |
| export | 자식 프로세스에도 변수를 전달 | `export API_KEY=abc123` |
| .bashrc | 대화형 bash shell 시작 시 실행 | `~/.bashrc` |
| .bash_profile | 로그인 shell 시작 시 실행 | `~/.bash_profile` |

## Before / After

**Before (PATH를 모를 때)**

```bash
pip install httpie
http GET https://api.example.com
# bash: http: command not found
# "왜 안 되지? 분명 설치했는데..."
```

**After (PATH를 이해할 때)**

```bash
pip install httpie
which http || pip show httpie | grep Location
# Location: /home/user/.local/lib/python3.11/site-packages
# → ~/.local/bin이 PATH에 있는지 확인
echo $PATH | tr ':' '\n' | grep local
# /home/user/.local/bin이 없으면:
export PATH="$HOME/.local/bin:$PATH"
http GET https://api.example.com   # 정상 실행
```

## 단계별 실습

### Step 1. 환경변수 확인

```bash
echo $HOME                    # 홈 디렉터리
echo $USER                    # 현재 사용자
echo $SHELL                   # 사용 중인 Shell
echo $PATH                    # 명령어 검색 경로

env                           # 모든 환경변수 출력
env | grep -i python          # python 관련 변수만
```

### Step 2. 변수 설정과 export

```bash
MY_VAR="hello"                # Shell 변수 (자식에게 안 전달됨)
echo $MY_VAR                  # hello

bash -c 'echo $MY_VAR'       # (빈 출력) — 자식 프로세스에 없음

export MY_VAR                 # export하면 자식에게 전달
bash -c 'echo $MY_VAR'       # hello

export DB_HOST="localhost"    # 선언과 export 동시에
```

### Step 3. PATH 수정

```bash
echo $PATH | tr ':' '\n'     # PATH를 줄 단위로 보기

# 임시 추가 (현재 세션만)
export PATH="$HOME/mytools:$PATH"

# which로 명령어 위치 확인
which python
which ls
```

### Step 4. .bashrc에 영구 설정

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export EDITOR=vim' >> ~/.bashrc

source ~/.bashrc             # 즉시 적용 (또는 새 터미널 열기)
echo $EDITOR
# vim
```

### Step 5. .env 파일 패턴

```bash
cat > ~/practice/linux-cli/.env << 'EOF'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
API_KEY=secret-key-123
EOF

# Shell에서 .env 파일 로드
set -a                        # 이후 변수를 자동 export
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

### 실수 1. PATH를 덮어쓴다

```bash
export PATH="/my/new/path"              # 기존 PATH가 전부 사라짐!
export PATH="/my/new/path:$PATH"        # 기존 PATH 뒤에 추가 — 안전
```

### 실수 2. .bashrc와 .bash_profile을 혼동한다

로그인 셸(SSH 접속)은 `.bash_profile`을 읽고, 비로그인 대화형 셸(터미널 앱)은 `.bashrc`를 읽습니다. 보통 `.bash_profile`에서 `.bashrc`를 source하여 통일합니다.

### 실수 3. 변수 참조 시 중괄호를 생략한다

```bash
echo "$HOME_backup"           # HOME_backup이라는 변수를 참조
echo "${HOME}_backup"         # HOME 변수 + "_backup" 문자열
```

### 실수 4. .env 파일을 Git에 커밋한다

API 키, 비밀번호가 포함된 `.env`가 공개 저장소에 올라가면 보안 사고입니다. `.gitignore`에 반드시 `.env`를 추가하세요.

### 실수 5. export를 빼먹고 "변수가 안 먹힌다"고 한다

Python 스크립트에서 `os.environ["MY_VAR"]`를 읽으려면, Shell에서 `export`로 내보내야 합니다. `MY_VAR=hello`만으로는 자식 프로세스인 Python이 볼 수 없습니다.

## 실무 적용

- **12-Factor App**: 설정을 코드가 아닌 환경변수로 관리합니다 (DB 접속 정보, API 키 등)
- **가상환경 활성화**: `source venv/bin/activate`는 PATH 앞에 venv의 bin/을 추가합니다
- **CI/CD 변수**: GitHub Actions의 `env:`는 환경변수를 설정하는 것입니다
- **Docker**: `docker run -e DB_HOST=db`로 컨테이너에 환경변수를 전달합니다
- **디버깅**: `env | sort`로 현재 환경을 덤프하여 문제를 진단합니다

## 실무에서는 이렇게 생각한다

환경변수는 "코드 밖의 설정"을 관리하는 표준 방법입니다. 같은 코드를 개발/스테이징/프로덕션에서 돌릴 때, 코드를 바꾸는 대신 `DB_HOST` 환경변수만 바꾸면 됩니다. 이것이 12-Factor App 방법론의 핵심이며, Docker, Kubernetes 환경에서 설정을 주입하는 기본 방식입니다.

반면 환경변수가 너무 많아지면 관리가 어려워집니다. 이때는 `.env` 파일을 환경별로 관리하거나, AWS Parameter Store, HashiCorp Vault 같은 시크릿 관리 도구로 넘어갑니다. 하지만 모든 것의 출발점은 `export`와 `$PATH`를 이해하는 것입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **Secret 격리** — 환경변수에 비밀값은 두지 말고 secret manager로 갑니다.
- **PATH 위험** — 현재 디렉터리(.)를 PATH에 두지 않습니다.
- **export 범위** — 변수는 명시 export 시에만 자식 프로세스에 전달됩니다.
- **Locale** — LC_ALL·LANG 차이가 정렬·정규식을 바꿉니다.
- **스크립트 의존** — 스크립트 시작에 필요한 환경 변수의 존재를 검증합니다.

## 체크리스트

- [ ] `echo $PATH`의 출력을 읽고 명령어 검색 순서를 설명할 수 있다
- [ ] `export`와 단순 변수 대입의 차이를 안다
- [ ] `.bashrc`에 PATH를 영구적으로 추가할 수 있다
- [ ] `.env` 파일을 만들고 `source`로 로드할 수 있다
- [ ] `.env` 파일을 `.gitignore`에 추가하는 이유를 안다

## 연습 문제

1. `echo $PATH | tr ':' '\n' | nl`로 PATH의 검색 순서를 번호와 함께 확인해보세요.
2. `MY_SECRET=hello`와 `export MY_SECRET=hello` 후 각각 `bash -c 'echo $MY_SECRET'`를 실행하여 차이를 확인해보세요.
3. `.bashrc`에 `alias ll='ls -la'`를 추가하고, `source ~/.bashrc` 후 `ll`이 동작하는지 확인해보세요.

## 정리 · 다음 글

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
- [cat, less, head, tail](./04-viewing-files.md)
- [grep, find, xargs](./05-grep-find-xargs.md)
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
