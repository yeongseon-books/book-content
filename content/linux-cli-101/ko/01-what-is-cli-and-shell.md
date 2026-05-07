---
title: CLI와 Shell이란 무엇인가?
series: linux-cli-101
episode: 1
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
- CLI
- Shell
- Terminal
- Bash
- Command Line
last_reviewed: '2026-05-04'
seo_description: CLI는 키보드만으로 컴퓨터를 조종하는 리모컨이고, Shell은 그 리모컨의 신호를 해석하는 통역사입니다.
---

# CLI와 Shell이란 무엇인가?

> Linux CLI 101 시리즈 (1/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- GUI 없이 컴퓨터를 다룬다는 것은 구체적으로 무엇을 의미할까요?
- Terminal, Shell, CLI는 각각 어떤 역할을 하며 무엇이 다를까요?
- 개발자가 CLI를 배워야 하는 실무적 이유는 무엇일까요?
- Bash와 Zsh 같은 Shell은 어떤 기준으로 선택할까요?

> CLI는 키보드만으로 컴퓨터를 조종하는 리모컨이고, Shell은 그 리모컨의 신호를 해석하는 통역사입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- CLI, Shell, Terminal의 정확한 차이와 관계
- Bash shell에서 첫 명령어를 실행하는 방법
- 명령어의 구조(command, option, argument)를 읽는 법
- 개발자가 CLI를 쓰는 현실적인 이유와 장점

## 왜 중요한가

처음 프로그래밍을 배울 때 대부분 GUI 에디터와 마우스 클릭으로 시작합니다. 파일을 더블클릭해서 열고, 메뉴에서 "실행"을 누릅니다. 이 방식은 처음에 직관적이지만, 서버 환경에 들어가는 순간 무력해집니다.

> 배포 서버에 SSH로 접속했는데 화면에 검은 텍스트 창만 있습니다. 마우스도 안 먹히고, 어디를 클릭해야 할지 모릅니다. 로그 파일을 열려면 어떻게 해야 할까요?

이 상황이 CLI를 배워야 하는 이유입니다. 서버, Docker 컨테이너, CI/CD 파이프라인은 모두 CLI 환경에서 돌아갑니다. CLI를 모르면 개발은 할 수 있어도 운영은 할 수 없습니다.

## Mental Model

> CLI는 키보드만으로 컴퓨터를 조종하는 리모컨이고, Shell은 그 리모컨의 신호를 해석하는 통역사입니다.

TV 리모컨을 누르면 적외선 신호가 나가고 TV가 그 신호를 해석합니다. CLI도 같습니다. 사용자가 키보드로 명령을 입력하면(리모컨), Shell이 그 명령을 해석해서(통역사), 운영체제에 전달합니다. Terminal은 이 모든 것이 일어나는 화면, 즉 TV 화면에 해당합니다.

```text
[사용자] --타이핑--> [Terminal 창] --전달--> [Shell(Bash)] --실행--> [운영체제]
                                                                      |
[사용자] <--화면출력-- [Terminal 창] <--결과-- [Shell(Bash)] <--응답-- [운영체제]
```

## 핵심 개념

| 용어 | 역할 | 예시 |
|---|---|---|
| CLI | 텍스트 명령으로 컴퓨터를 조작하는 인터페이스 | 명령어 입력 방식 전체 |
| Terminal | CLI를 사용하는 프로그램(창) | iTerm2, Windows Terminal, GNOME Terminal |
| Shell | 명령어를 해석하고 실행하는 프로그램 | Bash, Zsh, Fish |
| Prompt | Shell이 입력을 기다리는 표시 | `user@host:~$` |
| Command | 실행할 동작 | `ls`, `cd`, `echo` |

## Before / After

**Before (GUI 방식)**

```text
1. 파일 탐색기를 연다
2. Downloads 폴더를 더블클릭한다
3. 파일을 찾아 우클릭 → 이름 바꾸기
4. 새 이름을 입력하고 Enter
```

**After (CLI 방식)**

```bash
cd ~/Downloads
mv old-name.txt new-name.txt
```

2줄이면 끝납니다. 100개 파일 이름을 바꿔야 할 때 GUI는 100번 클릭이지만, CLI는 반복문 한 줄입니다.

## 단계별 실습

### Step 1. Terminal 열기

```bash
# macOS: Cmd + Space → "Terminal" 검색
# Ubuntu: Ctrl + Alt + T
# Windows: WSL 설치 후 "Ubuntu" 앱 실행
```

Terminal을 열면 prompt가 나타납니다.

```text
user@hostname:~$
```

### Step 2. 첫 명령어 실행

```bash
echo "Hello, CLI!"
# 출력: Hello, CLI!
```

`echo`는 뒤에 오는 텍스트를 화면에 출력하는 명령어입니다.

### Step 3. 명령어 구조 이해하기

```bash
ls -la /home
#  ^  ^^  ^
#  |  ||  └── argument: 대상 경로
#  |  |└── option: 숨김 파일 포함
#  |  └── option: 자세한 정보
#  └── command: 파일 목록 보기
```

모든 명령어는 `command [options] [arguments]` 구조입니다.

### Step 4. Shell 확인하기

```bash
echo $SHELL
# 출력 예: /bin/bash 또는 /bin/zsh
```

### Step 5. 도움말 확인하기

```bash
ls --help    # 간단한 도움말
man ls       # 상세 매뉴얼 (q로 종료)
```

## 이 코드에서 봐야 할 것

- `echo`는 가장 단순한 출력 명령이지만 디버깅과 스크립트에서 핵심 도구입니다
- `-la`는 `-l`과 `-a` 두 옵션을 합친 것이며 대부분의 명령어에서 이렇게 합칠 수 있습니다
- `$SHELL`은 환경변수이며 `$` 기호로 참조합니다 (Ep8에서 자세히 다룹니다)
- `man` 페이지는 인터넷 검색보다 정확한 공식 문서입니다

## 자주 하는 실수

### 실수 1. Terminal과 Shell을 같은 것으로 혼동한다

Terminal은 화면(프로그램)이고 Shell은 명령어 해석기입니다. 하나의 Terminal에서 다른 Shell을 실행할 수 있습니다. `bash`를 쓰다가 `zsh`로 바꾸는 것은 같은 TV에서 채널을 바꾸는 것과 같습니다.

### 실수 2. 대소문자를 구분하지 않는다

Linux에서 `File.txt`와 `file.txt`는 완전히 다른 파일입니다. Windows와 달리 대소문자를 엄격하게 구분합니다.

### 실수 3. 공백 처리를 잘못한다

```bash
cd My Documents     # 오류: "My"와 "Documents" 두 인자로 해석
cd "My Documents"   # 정상: 따옴표로 감싸기
cd My\ Documents    # 정상: 백슬래시로 공백 이스케이프
```

### 실수 4. root 권한으로 모든 것을 실행한다

`sudo`를 습관적으로 붙이면 위험합니다. 시스템 파일을 실수로 삭제할 수 있습니다. 꼭 필요한 경우에만 `sudo`를 사용하세요.

### 실수 5. Tab 자동 완성을 모른다

파일 이름을 전부 타이핑할 필요 없습니다. 처음 몇 글자를 입력하고 Tab 키를 누르면 Shell이 자동으로 완성합니다. 두 번 누르면 후보 목록을 보여줍니다.

## 실무 적용

- **서버 디버깅**: SSH 접속 후 로그 확인, 프로세스 상태 점검은 모두 CLI입니다
- **Docker 컨테이너**: 컨테이너 내부에 GUI는 없습니다. `docker exec`로 들어가면 CLI뿐입니다
- **CI/CD 파이프라인**: GitHub Actions, Jenkins 등 모든 자동화 도구는 Shell 명령어로 동작합니다
- **스크립트 자동화**: 반복 작업을 Shell script로 묶으면 시간을 크게 절약합니다
- **원격 서버 관리**: 클라우드 서버(AWS EC2, Azure VM)는 CLI 접속이 기본입니다

## 실무에서는 이렇게 생각한다

"GUI가 있는데 왜 굳이 CLI를 쓰냐"는 질문을 받으면, 대답은 **재현성과 자동화**입니다. GUI로 한 작업은 기록이 남지 않습니다. 같은 작업을 내일 다시 해야 하면 처음부터 클릭해야 합니다. CLI 명령어는 히스토리에 남고, 스크립트로 저장하면 영원히 재현 가능합니다.

반면 모든 것을 CLI로 해야 하는 것은 아닙니다. 코드 편집은 VS Code 같은 GUI 에디터가 생산성이 높고, 파일 비교는 GUI diff 도구가 직관적입니다. 도구 선택의 기준은 "이 작업을 100번 반복한다면?"입니다. 반복이 잦은 작업일수록 CLI의 가치가 올라갑니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **Bash 표준** — 운영 스크립트는 bash로 통일해 이식성을 확보합니다.
- **set -euo pipefail** — 스크립트 시작에 안전 옵션을 강제합니다.
- **Quoting** — 변수는 항상 "$var"로 인용해 단어 분리를 막습니다.
- **PATH 인식** — 어떤 바이너리가 실행되는지 which로 확인합니다.
- **MANPAGE** — 옵션 추정 대신 man·--help를 우선 확인합니다.

## 체크리스트

- [ ] Terminal, Shell, CLI의 차이를 한 문장씩 설명할 수 있다
- [ ] Terminal을 열고 `echo`, `ls` 명령어를 실행할 수 있다
- [ ] 명령어의 command, option, argument 구조를 구분할 수 있다
- [ ] 현재 사용 중인 Shell이 무엇인지 확인할 수 있다
- [ ] Tab 자동 완성과 man 페이지를 사용할 수 있다

## 연습 문제

1. 터미널을 열고 `whoami`, `hostname`, `date`, `pwd` 명령어를 차례로 실행하세요. 각 명령어가 무엇을 출력하는지 한 줄로 정리해보세요.
2. `ls -la /etc` 명령어를 실행하고, 출력의 각 열(column)이 무엇을 의미하는지 추측해보세요. (Ep3에서 정답을 다룹니다.)
3. `echo $SHELL`과 `echo $HOME`을 실행해보세요. 두 환경변수가 각각 무엇을 가리키는지 설명해보세요.

## 정리 · 다음 글

- CLI는 텍스트 명령으로 컴퓨터를 다루는 인터페이스이며, GUI가 없는 서버 환경에서 필수입니다.
- Terminal은 화면, Shell은 명령어 해석기, CLI는 조작 방식 전체를 가리킵니다.
- 모든 명령어는 `command [options] [arguments]` 구조를 따릅니다.
- Tab 자동 완성과 man 페이지는 CLI 생산성의 핵심 도구입니다.
- CLI를 배우면 서버 관리, Docker, CI/CD, 자동화 스크립트를 직접 다룰 수 있습니다.

다음 글에서는 **파일과 디렉터리를 다루는 명령어** — `ls`, `cd`, `mkdir`, `cp`, `mv`, `rm`을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- **CLI와 Shell이란 무엇인가? (현재 글)**
- 파일과 디렉터리 다루기 (예정)
- 권한과 소유자 이해하기 (예정)
- cat, less, head, tail (예정)
- grep, find, xargs (예정)
- pipe와 redirection (예정)
- 프로세스 확인과 종료 (예정)
- 환경변수와 PATH (예정)
- 간단한 shell script (예정)
- SSH와 원격 서버 접속 (예정)

<!-- toc:end -->

## 참고 자료

- [GNU Bash Reference Manual](https://www.gnu.org/software/bash/manual/)
- [Linux man pages online](https://man7.org/linux/man-pages/)
- [The Missing Semester of Your CS Education - The Shell](https://missing.csail.mit.edu/2020/course-shell/)
- [ExplainShell - match command-line arguments to their help text](https://explainshell.com/)

Tags: Linux, CLI, Shell, Terminal, Bash, Command Line
