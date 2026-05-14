---
title: CLI와 Shell이란 무엇인가?
series: linux-cli-101
episode: 1
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
- CLI
- Shell
- Terminal
- Bash
- Command Line
last_reviewed: '2026-05-15'
seo_description: CLI와 Shell, Terminal의 차이와 첫 명령 실행 흐름을 정리합니다.
---

# CLI와 Shell이란 무엇인가?

처음 프로그래밍을 배울 때 대부분 GUI 에디터와 마우스 클릭으로 시작합니다. 파일을 더블클릭해서 열고, 메뉴에서 "실행"을 누릅니다. 이 방식은 처음에 직관적이지만, 서버 환경에 들어가는 순간 무력해집니다.

이 글은 Linux CLI 101 시리즈의 첫 번째 글입니다.

## 이 글에서 다룰 문제

- GUI 없이 컴퓨터를 다룬다는 말은 실제로 무엇을 뜻할까요?
- Terminal, Shell, CLI는 무엇이 다르고 어디서 헷갈릴까요?
- 개발자가 실무에서 CLI를 꼭 익혀야 하는 이유는 무엇일까요?
- Bash, Zsh 같은 Shell은 어떤 기준으로 바라보면 될까요?

> CLI는 키보드만으로 컴퓨터를 조종하는 리모컨이고, Shell은 그 리모컨의 신호를 해석하는 통역사입니다.

## 머릿속에 먼저 그릴 그림

> CLI는 키보드만으로 컴퓨터를 조종하는 리모컨이고, Shell은 그 리모컨의 신호를 해석하는 통역사입니다.

TV 리모컨을 누르면 적외선 신호가 나가고 TV가 그 신호를 해석합니다. CLI도 같습니다. 사용자가 키보드로 명령을 입력하면(리모컨), Shell이 그 명령을 해석해서(통역사), 운영체제에 전달합니다. Terminal은 이 모든 것이 일어나는 화면, 즉 TV 화면에 해당합니다.

```text
[User] --typing--> [Terminal window] --passes--> [Shell (Bash)] --executes--> [OS]
                                                                                |
[User] <--display-- [Terminal window] <--result-- [Shell (Bash)] <--response-- [OS]
```

## 핵심 개념

| 용어 | 역할 | 예시 |
|---|---|---|
| CLI | 텍스트 명령으로 컴퓨터를 조작하는 인터페이스 | 명령어 입력 방식 전체 |
| Terminal | CLI를 사용하는 프로그램(창) | iTerm2, Windows Terminal, GNOME Terminal |
| Shell | 명령어를 해석하고 실행하는 프로그램 | Bash, Zsh, Fish |
| Prompt | Shell이 입력을 기다리는 표시 | `user@host:~$` |
| Command | 실행할 동작 | `ls`, `cd`, `echo` |

## 전과 후

**전 — GUI 방식**

```text
1. Open file explorer
2. Double-click Downloads folder
3. Right-click file → Rename
4. Type new name and press Enter
```

**후 — CLI 방식**

```bash
cd ~/Downloads
mv old-name.txt new-name.txt
```

2줄이면 끝납니다. 100개 파일 이름을 바꿔야 할 때 GUI는 100번 클릭이지만, CLI는 반복문 한 줄입니다.

## 단계별 실습

### 1단계. 터미널 열기

```bash
# macOS: Cmd + Space → search "Terminal"
# Ubuntu: Ctrl + Alt + T
# Windows: Install WSL, then open the "Ubuntu" app
```

Terminal을 열면 prompt가 나타납니다.

```text
user@hostname:~$
```

### 2단계. 첫 명령어 실행

```bash
echo "Hello, CLI!"
# Output: Hello, CLI!
```

`echo`는 뒤에 오는 텍스트를 화면에 출력하는 명령어입니다.

### 3단계. 명령어 구조 이해하기

```bash
ls -la /home
#  ^  ^^  ^
#  |  ||  └── argument: target path
#  |  |└── option: include hidden files
#  |  └── option: detailed information
#  └── command: list files
```

모든 명령어는 `command [options] [arguments]` 구조입니다.

### 4단계. 현재 셸 확인하기

```bash
echo $SHELL
# Example output: /bin/bash or /bin/zsh
```

### 5단계. 도움말 확인하기

```bash
ls --help    # Quick help
man ls       # Full manual (press q to exit)
```

## 이 코드에서 봐야 할 것

- `echo`는 가장 단순한 출력 명령이지만 디버깅과 스크립트에서 핵심 도구입니다
- `-la`는 `-l`과 `-a` 두 옵션을 합친 것이며 대부분의 명령어에서 이렇게 합칠 수 있습니다
- `$SHELL`은 환경변수이며 `$` 기호로 참조합니다 (Ep8에서 자세히 다룹니다)
- `man` 페이지는 인터넷 검색보다 정확한 공식 문서입니다

## 자주 하는 실수

### 실수 1. 터미널과 셸을 같은 것으로 혼동한다

Terminal은 화면(프로그램)이고 Shell은 명령어 해석기입니다. 하나의 Terminal에서 다른 Shell을 실행할 수 있습니다. `bash`를 쓰다가 `zsh`로 바꾸는 것은 같은 TV에서 채널을 바꾸는 것과 같습니다.

### 실수 2. 대소문자를 구분하지 않는다

Linux에서 `File.txt`와 `file.txt`는 완전히 다른 파일입니다. Windows와 달리 대소문자를 엄격하게 구분합니다.

### 실수 3. 공백 처리를 잘못한다

```bash
cd My Documents     # Error: interpreted as two arguments "My" and "Documents"
cd "My Documents"   # Correct: quotes wrap the path
cd My\ Documents    # Correct: backslash escapes the space
```

### 실수 4. 관리자 권한으로 모든 것을 실행한다

`sudo`를 습관적으로 붙이면 위험합니다. 시스템 파일을 실수로 삭제할 수 있습니다. 꼭 필요한 경우에만 `sudo`를 사용하세요.

### 실수 5. 자동 완성을 모른다

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

## 체크리스트

- [ ] Terminal, Shell, CLI의 차이를 한 문장씩 설명할 수 있다
- [ ] Terminal을 열고 `echo`, `ls` 명령어를 실행할 수 있다
- [ ] 명령어의 command, option, argument 구조를 구분할 수 있다
- [ ] 현재 사용 중인 Shell이 무엇인지 확인할 수 있다
- [ ] Tab 자동 완성과 man 페이지를 사용할 수 있다

## 연습 문제

1. 터미널을 열고 `whoami`, `hostname`, `date`, `pwd`를 순서대로 실행해 보세요. 각 명령이 무엇을 출력하는지 한 줄씩 적어 보세요.
2. `ls -la /etc`를 실행한 뒤 출력 각 열이 무엇을 뜻하는지 추측해 보세요. 정답의 핵심은 3편에서 다시 다룹니다.
3. `echo $SHELL`과 `echo $HOME`을 실행하고, 각 환경변수가 무엇을 가리키는지 설명해 보세요.

## 정리와 다음 글

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
- cat, less, head, tail — 파일 내용 보기 (예정)
- grep, find, xargs — 검색의 삼총사 (예정)
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
