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

![Linux CLI 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/01/01-01-big-picture.ko.png)
*Linux CLI 101 1장 흐름 개요*

## 먼저 던지는 질문

- GUI 없이 컴퓨터를 다룬다는 말은 실제로 무엇을 뜻할까요?
- Terminal, Shell, CLI는 무엇이 다르고 어디서 헷갈릴까요?
- 개발자가 실무에서 CLI를 꼭 익혀야 하는 이유는 무엇일까요?

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

## 실무 시나리오: 장애 대응에서 CLI가 가지는 의미

처음 CLI를 배우는 단계에서는 `ls`, `cd`, `echo`처럼 작은 명령이 보통의 학습 단위입니다. 하지만 실무에서는 명령 하나보다 **문제 진단 흐름을 어떻게 구성하는지**가 더 중요합니다. 예를 들어 API 서버가 느려졌다는 신고를 받으면, 운영자는 GUI 대시보드만 보지 않고 즉시 SSH로 들어가 프로세스·디스크·로그를 함께 확인합니다. 이때 CLI는 단순 입력 도구가 아니라, 짧은 시간 안에 가설을 세우고 검증하는 실행 환경입니다.

```bash
# 1) 현재 접속한 서버와 사용자 컨텍스트 확인
whoami
hostname
pwd

# 예상 출력
# deploy
# prod-api-01
# /home/deploy
```

컨텍스트 확인을 먼저 하는 이유는 단순합니다. 잘못된 서버에 접속해 진단하거나 조치를 수행하는 사고를 막기 위해서입니다. 특히 운영/개발 서버가 비슷한 프롬프트를 쓰면, 첫 30초의 확인 습관이 전체 사고율을 줄입니다.

```bash
# 2) 시스템 상태를 한 번에 요약
uptime
free -h
df -h /

# 예상 출력
# 14:31:02 up 17 days,  3:12,  2 users,  load average: 1.82, 1.20, 0.98
#               total        used        free      shared  buff/cache   available
# Mem:           7.6Gi       4.1Gi       1.2Gi       210Mi       2.3Gi       2.8Gi
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/sda1        50G   29G   19G  61% /
```

위 세 명령은 각각 CPU 부하, 메모리 압박, 디스크 여유를 빠르게 보여줍니다. 이 값이 정상 범위를 벗어나면 애플리케이션 코드 문제인지 인프라 문제인지 분기할 수 있습니다. CLI 숙련도는 명령 암기가 아니라, 이런 분기를 빠르게 수행하는 능력에서 드러납니다.

### 파이프 체인으로 노이즈 줄이기

로그는 양이 많아서 원문 그대로 보면 판단이 늦어집니다. 운영에서는 파이프 체인을 통해 노이즈를 줄여 **판단 가능한 단위**로 압축합니다.

```bash
journalctl -u my-api --since '15 min ago'   | grep -E 'ERROR|CRITICAL|Timeout'   | sed -E 's/[0-9]{2}:[0-9]{2}:[0-9]{2}//'   | sort   | uniq -c   | sort -nr

# 예상 출력
#    37  Timeout while calling payment provider
#    12  ERROR Database connection pool exhausted
#     4  CRITICAL Worker process exited unexpectedly
```

핵심은 `grep -E`의 정규식입니다. `ERROR|CRITICAL|Timeout`처럼 OR 패턴을 쓰면 여러 실패 유형을 한 번에 잡을 수 있습니다. 이후 `uniq -c`로 빈도를 보면 가장 먼저 해결해야 할 항목이 자연스럽게 올라옵니다.

### 셸이 해석하는 순서를 이해하면 사고가 줄어듭니다

초보 구간에서 자주 발생하는 문제는 "명령은 맞는데 왜 다르게 실행되지?"입니다. 원인은 셸의 해석 순서를 놓치기 때문입니다. 변수 확장, 글로빙(`*`), 따옴표 처리, 파이프 분할이 먼저 일어나고 나서 실행됩니다.

```bash
name='api server'
echo $name
# api server

echo "$name"
# api server

echo '$name'
# $name
```

이 차이는 단순 문법이 아니라 보안·안정성과 직결됩니다. 자동화 스크립트에서 공백이 포함된 경로를 큰따옴표 없이 다루면 다른 파일이 대상이 될 수 있습니다. 그래서 실무에서는 변수를 넣을 때 기본값처럼 `"$var"`를 사용합니다.

### 프로세스와 서비스 단위를 구분해 보기

CLI 초급 글에서도 이 구분을 미리 알고 있으면 이후 학습이 쉬워집니다. `ps`는 프로세스 수준, `systemctl`은 서비스 단위 관리입니다.

```bash
ps -ef | grep my-api | grep -v grep
systemctl status my-api --no-pager

# 예상 출력 일부
# deploy   18231     1  1 14:10 ?  00:00:08 /usr/bin/python3 /opt/my-api/app.py
# Active: active (running) since Thu 2026-05-21 14:09:52 KST; 21min ago
```

프로세스는 떠 있는데 서비스 상태가 `failed`인 경우도 있고, 반대 상황도 나올 수 있습니다. 이 차이를 이해하면 7편(프로세스)과 systemd 운영 패턴을 더 빠르게 연결할 수 있습니다.

### 미니 Bash 스크립트로 점검 루틴 고정하기

반복 점검은 스크립트로 고정하는 편이 안전합니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

svc="my-api"

printf '[INFO] host=%s user=%s
' "$(hostname)" "$(whoami)"
systemctl is-active --quiet "$svc" && echo '[PASS] service active' || echo '[FAIL] service inactive'

journalctl -u "$svc" --since '5 min ago'   | grep -E 'ERROR|CRITICAL|Timeout' || true
```

이런 스크립트는 팀 내에서 같은 방식으로 상황을 재현하게 해 줍니다. 결국 CLI 역량의 목적은 "내가 빨라지는 것"을 넘어서 "팀의 진단 품질을 표준화하는 것"입니다.

## 실전 점검 로그 예시

아래 예시는 실제 운영에서 자주 보는 "점검 출력 형태"를 축약한 것입니다. 중요한 것은 특정 명령을 그대로 복사하는 것이 아니라, 출력을 근거로 다음 판단을 연결하는 습관입니다.

```bash
# 서비스 상태 + 최근 오류를 한 번에 수집
systemctl is-active my-api
journalctl -u my-api --since '5 min ago' --no-pager   | grep -E 'ERROR|CRITICAL|timeout|Failed'   | tail -n 20

# 예상 출력
# active
# 2026-05-21 15:31:10 ERROR timeout while calling payment API
# 2026-05-21 15:31:12 CRITICAL worker exited unexpectedly
```

```bash
# 프로세스/포트/파일 핸들 점검
ps -ef | grep -E 'my-api|gunicorn' | grep -v grep
ss -lntp | grep -E ':8080|:80|:443'
lsof -p "$(pgrep -f my-api | head -n 1)" | wc -l

# 예상 출력 예시
# deploy 18231 1  ... /opt/my-api/current/bin/start.sh
# LISTEN 0 4096 0.0.0.0:8080 ... users:(("python3",pid=18231,fd=12))
# 412
```

이런 출력들을 시계열로 저장해 두면 재발 시 비교가 쉬워지고, "지금이 평소와 어떻게 다른가"를 빠르게 설명할 수 있습니다. 결국 CLI 실무 역량은 명령 자체보다 **증거 기반 판단 루틴**을 안정적으로 반복하는 능력입니다.

## 처음 질문으로 돌아가기

- **GUI 없이 컴퓨터를 다룬다는 말은 실제로 무엇을 뜻할까요?**
  - 키보드로 `echo "Hello, CLI!"`, `ls -la /home`, `cd ~/Downloads` 같은 명령을 직접 입력해 운영체제에 일을 시키는 방식입니다. Terminal은 화면이고 Shell은 그 명령을 해석하는 프로그램이므로, 서버나 Docker 컨테이너처럼 GUI가 없는 환경에서도 같은 흐름으로 작업할 수 있습니다.
- **Terminal, Shell, CLI는 무엇이 다르고 어디서 헷갈릴까요?**
  - 글의 그림처럼 Terminal은 입력과 결과를 보여 주는 창이고, Shell은 `command [options] [arguments]` 구조를 해석해 OS에 전달하는 실행기이며, CLI는 이 전체 상호작용 방식입니다. `echo $SHELL`로 현재 셸을 확인할 수 있고, 같은 Terminal 안에서 Bash나 Zsh를 바꿔 쓸 수 있다는 점이 둘을 구분하는 가장 쉬운 기준입니다.
- **개발자가 실무에서 CLI를 꼭 익혀야 하는 이유는 무엇일까요?**
  - CLI 명령은 히스토리와 스크립트로 남아서 재현성과 자동화를 만들 수 있기 때문입니다. SSH로 접속한 서버 점검, `journalctl | grep` 같은 로그 확인, CI/CD 실행, 반복 작업 스크립트화까지 모두 CLI를 기반으로 돌아가므로 실무 범위가 바로 넓어집니다.

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

- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko
Tags: Linux, CLI, Shell, Terminal, Bash, Command Line
