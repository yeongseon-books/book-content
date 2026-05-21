---
title: "Linux CLI 101 (1/10): CLI와 Shell이란 무엇인가?"
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

# Linux CLI 101 (1/10): CLI와 Shell이란 무엇인가?

처음 프로그래밍을 배울 때 대부분 GUI 에디터와 마우스 클릭으로 시작합니다. 파일을 더블클릭해서 열고, 메뉴에서 "실행"을 누릅니다. 이 방식은 처음에 직관적이지만, 서버 환경에 들어가는 순간 무력해집니다.

이 글은 Linux CLI 101 시리즈의 첫 번째 글입니다.

## 먼저 던지는 질문

- GUI 없이 컴퓨터를 다룬다는 말은 실제로 무엇을 뜻할까요?
- Terminal, Shell, CLI는 무엇이 다르고 어디서 헷갈릴까요?
- 개발자가 실무에서 CLI를 꼭 익혀야 하는 이유는 무엇일까요?

## 큰 그림

![Linux CLI 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/01/01-01-big-picture.ko.png)

*Linux CLI 101 1장 흐름 개요*

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


## 실전 CLI 운영 패턴

### 명령을 순서가 아니라 데이터 흐름으로 설계하기
CLI 작업이 길어질수록 핵심은 명령 개수보다 데이터 흐름입니다. 예를 들어 로그에서 오류 패턴을 찾고, 원인 프로세스를 좁히고, 마지막으로 자동 조치 후보를 만드는 과정은 하나의 파이프라인으로 보는 편이 안정적입니다. 다음 흐름은 실제 운영 환경에서 자주 쓰는 형태입니다.

```bash
journalctl -u my-api --since "10 min ago" \
  | grep -E "ERROR|CRITICAL" \
  | awk '{print $1" "$2" "$3" "$NF}' \
  | sort \
  | uniq -c \
  | sort -nr
```

이 파이프라인의 목적은 "원시 로그"를 "빈도 기반 우선순위 목록"으로 바꾸는 것입니다. 앞쪽 명령은 후보를 넓게 모으고, 뒤쪽 명령은 노이즈를 줄여 의사결정 가능한 형태로 압축합니다. 운영자가 먼저 이 구조를 머릿속에 그려두면, 중간에 도구를 바꿔도 전체 전략은 유지됩니다.

### 안전한 one-liner와 검증 루틴
한 줄 명령은 빠르지만 위험합니다. 삭제, 이동, 권한 변경처럼 되돌리기 어려운 작업은 항상 dry-run 단계를 먼저 둡니다.

```bash
find ./tmp-exports -type f -mtime +7 -print
find ./tmp-exports -type f -mtime +7 -print0 | xargs -0 rm -f
```

첫 줄은 영향 범위를 확인하는 단계이고, 둘째 줄은 실제 실행입니다. 이 두 단계를 분리하면 휴먼 에러를 크게 줄일 수 있습니다. 특히 공백이 있는 파일명을 다룰 때는 `-print0`와 `xargs -0` 조합을 기본값으로 두는 편이 안전합니다.

### 작은 셸 스크립트를 운영 도구로 키우기
반복 작업은 즉시 스크립트로 승격하는 것이 좋습니다. 아래 예시는 "서비스 상태 점검 + 이상 시 로그 추출"을 자동화한 최소 형태입니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

service_name="my-api"
window="5 min ago"

if systemctl is-active --quiet "$service_name"; then
  echo "[PASS] $service_name is active"
else
  echo "[FAIL] $service_name is not active"
  journalctl -u "$service_name" --since "$window" | tail -n 80
  exit 1
fi
```

여기서 중요한 포인트는 세 가지입니다. 첫째, `set -euo pipefail`로 실패를 조기에 표면화합니다. 둘째, 하드코딩 값을 변수로 끌어올려 재사용성을 높입니다. 셋째, 실패 시 바로 조사 가능한 로그를 출력해 복구 시간을 줄입니다. 이런 작은 스크립트들이 쌓이면 팀의 운영 품질이 표준화됩니다.

### 파이프 결과를 파일과 결합해 재현성 확보하기
문제 분석은 재현 가능해야 합니다. 표준 출력으로만 보면 같은 분석을 다시 하기 어렵기 때문에 중간 결과를 파일로 남기는 습관이 유용합니다.

```bash
ps aux | grep "python" | grep -v grep | tee /tmp/python-proc.txt
cut -d' ' -f1-12 /tmp/python-proc.txt > /tmp/python-proc-compact.txt
```

`tee`는 화면 확인과 파일 저장을 동시에 처리하므로 탐색 속도와 재현성을 함께 확보합니다. 이후 팀원이 같은 파일을 기반으로 추가 분석을 이어갈 수 있어 협업 비용이 줄어듭니다.

## 자동화 품질을 높이는 셸 체크포인트

### 입력 검증과 종료 코드 계약
셸 스크립트가 팀 도구가 되려면 실패 방식이 예측 가능해야 합니다. 인자 검증과 종료 코드 계약을 명시하면 CI와 운영 스크립트가 안전하게 연동됩니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 <log_dir> <keyword>"
}

if [ "$#" -ne 2 ]; then
  usage
  exit 64
fi

log_dir="$1"
keyword="$2"

if [ ! -d "$log_dir" ]; then
  echo "directory not found: $log_dir"
  exit 66
fi

if grep -R --line-number "$keyword" "$log_dir" >/tmp/match.out; then
  echo "match found"
  exit 0
else
  echo "no match"
  exit 1
fi
```

여기서 `64`, `66` 같은 종료 코드는 호출자에게 실패 원인을 분류해 전달합니다. 사람이 읽는 메시지와 기계가 읽는 코드가 분리되어 있으면 자동화 파이프라인에서 분기 처리하기 쉽습니다.

### 파이프라인 병목 찾기
복잡한 파이프라인은 체감만으로 병목을 찾기 어렵습니다. 각 단계 앞뒤에 타임스탬프를 찍거나 임시 파일에 분리 저장해 어느 단계가 느린지 확인합니다.

```bash
time grep -R "ERROR" /var/log/myapp > /tmp/step1.txt
time cut -d' ' -f1-8 /tmp/step1.txt > /tmp/step2.txt
time sort /tmp/step2.txt | uniq -c | sort -nr > /tmp/step3.txt
```

이 방식은 단순하지만 효과가 큽니다. 어떤 단계가 CPU 중심인지 I/O 중심인지 빠르게 감을 잡을 수 있고, 이후 `awk` 대체, 병렬화, 입력 축소 같은 최적화 방향을 정하기 쉬워집니다.

### 재사용 가능한 함수형 스니펫
긴 스크립트에서도 기능 단위를 함수로 분리하면 테스트와 유지보수가 쉬워집니다.

```bash
collect_pids() {
  pgrep -f "$1" || true
}

kill_gracefully() {
  local pid="$1"
  kill -TERM "$pid"
  sleep 2
  kill -0 "$pid" 2>/dev/null && kill -KILL "$pid" || true
}
```

함수 단위로 쪼개면 시나리오별 검증이 가능해집니다. 예를 들어 종료 신호가 정상 처리되는지, 남은 프로세스가 있는지, 재시작 로직이 중복 실행되는지 등을 독립적으로 점검할 수 있습니다.

## 처음 질문으로 돌아가기

- **GUI 없이 컴퓨터를 다룬다는 말은 실제로 무엇을 뜻할까요?**
  - 본문의 기준은 CLI와 Shell이란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Terminal, Shell, CLI는 무엇이 다르고 어디서 헷갈릴까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **개발자가 실무에서 CLI를 꼭 익혀야 하는 이유는 무엇일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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
