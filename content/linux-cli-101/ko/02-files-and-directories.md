---
title: "Linux CLI 101 (2/10): 파일과 디렉터리 다루기"
series: linux-cli-101
episode: 2
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
- File System
- Directory
- ls
- cp
last_reviewed: '2026-05-12'
seo_description: 리눅스 트리 구조를 파악하고 cd, ls부터 cp, mv, rm까지 필수 명령어를 경로 개념과 함께 실습하며 안전한 파일 조작 습관을 익힙니다.
---

# Linux CLI 101 (2/10): 파일과 디렉터리 다루기

개발자의 일상은 파일을 만들고, 옮기고, 복사하고, 삭제하는 것의 연속입니다. 코드 파일을 정리하고, 설정 파일을 복사하고, 빌드 산출물을 삭제합니다. GUI에서는 드래그 앤 드롭으로 하지만, 서버에서는 모두 명령어입니다.

![Linux CLI 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/02/02-01-big-picture.ko.png)
*Linux CLI 101 2장 흐름 개요*

## 먼저 던지는 질문

- 절대 경로와 상대 경로는 언제 다르게 느껴질까요?
- `pwd`, `cd`, `ls`만으로 현재 위치를 어떻게 읽어야 할까요?
- `cp`, `mv`, `rm`은 각각 어떤 상황에서 쓰면 안전할까요?

## 머릿속에 먼저 그릴 그림

> Linux 파일 시스템은 하나의 뿌리(`/`)에서 시작하는 거대한 나무입니다. 모든 파일과 디렉터리는 이 나무의 가지입니다.

Windows는 `C:\`, `D:\`처럼 드라이브 문자가 여러 개이지만, Linux는 무조건 `/`(root) 하나에서 시작합니다. USB를 꽂아도, 네트워크 드라이브를 연결해도 모두 이 나무의 어딘가에 매달립니다.

```text
/                       <- root
├── home/               <- user home directories
│   └── user/           <- my workspace (~)
├── etc/                <- system configuration files
├── var/                <- logs, caches, variable data
├── tmp/                <- temporary files
└── usr/                <- user programs
    └── bin/            <- executables
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| 절대 경로 | `/`부터 시작하는 전체 경로 | `/home/user/project/main.py` |
| 상대 경로 | 현재 위치 기준 경로 | `./src/main.py`, `../config.yaml` |
| `.` | 현재 디렉터리 | `./run.sh` (현재 폴더의 run.sh) |
| `..` | 상위 디렉터리 | `cd ..` (한 단계 위로) |
| `~` | 홈 디렉터리 | `cd ~` = `cd /home/user` |

## 전과 후

**전 — 경로를 모를 때**

```text
"The file is somewhere... where was it?"
-> Click through folders one by one in the GUI
-> 5 minutes spent
```

**후 — 경로를 아는 CLI 사용자**

```bash
find /var/log -name "error*.log" -mtime -1
# Finds all error logs created since yesterday in 1 second
```

## 단계별 실습

### 1단계. 현재 위치 확인

```bash
pwd
# Example output: /home/user
```

`pwd`(print working directory)는 지금 내가 어디에 있는지 보여줍니다.

### 2단계. 디렉터리 이동

```bash
cd /tmp           # Move using an absolute path
cd ~              # Move to home
mkdir -p ~/practice/linux-cli   # Create a practice directory
cd ~/practice/linux-cli         # Move into it
pwd
# Output: /home/user/practice/linux-cli
```

### 3단계. 파일과 디렉터리 만들기

```bash
touch hello.txt               # Create an empty file
mkdir src                     # Create a directory
mkdir -p src/utils/helpers    # Create nested directories at once
ls -la
# hello.txt, src/ are visible
```

### 4단계. 복사, 이동, 이름 바꾸기

```bash
cp hello.txt hello-backup.txt          # Copy a file
mv hello-backup.txt src/               # Move a file
mv src/hello-backup.txt src/backup.txt # Rename
ls src/
# backup.txt  utils/
```

### 5단계. 삭제

```bash
rm src/backup.txt              # Delete a file
rmdir src/utils/helpers        # Delete an empty directory
rm -r src/utils                # Delete a directory and its contents
ls src/
# (empty)
```

## 이 코드에서 봐야 할 것

- `mkdir -p`는 중간 디렉터리가 없어도 한 번에 만듭니다. `-p` 없이 하면 부모 디렉터리가 없을 때 오류가 납니다
- `mv`는 이동과 이름 변경 두 가지 역할을 합니다. 같은 디렉터리 내에서 `mv`하면 이름 변경입니다
- `rm -r`은 재귀적 삭제입니다. 휴지통이 없으므로 복구가 불가능합니다
- `cp`로 디렉터리를 복사할 때는 반드시 `-r` 옵션이 필요합니다

## 자주 하는 실수

### 실수 1. 루트 경로 삭제 명령을 함부로 실행한다

절대로 하면 안 됩니다. 시스템의 모든 파일이 삭제됩니다. 현대 시스템은 `--no-preserve-root` 없이는 거부하지만, `/home`이나 `/var`를 실수로 날릴 수 있습니다.

### 실수 2. 와일드카드 `*`를 확인 없이 쓴다

```bash
rm *.log        # Deletes only .log files — as intended
rm * .log       # Space causes deletion of ALL files, then tries to delete ".log" — disaster
```

삭제 전에 `ls *.log`로 대상을 먼저 확인하세요.

### 실수 3. 경로에 공백이 있는 파일을 따옴표 없이 쓴다

```bash
cp My File.txt backup/     # Error: interpreted as two files "My" and "File.txt"
cp "My File.txt" backup/   # Correct
```

### 실수 4. 상대 경로와 절대 경로를 혼동한다

`cd practice`는 현재 디렉터리에 `practice`가 있을 때만 동작합니다. 어디서든 동작하려면 `cd ~/practice`처럼 절대 경로나 `~`을 씁니다.

### 실수 5. 디렉터리 복사에 재귀 옵션을 빼먹는다

```bash
cp src/ backup/         # Error: "src/ is a directory"
cp -r src/ backup/      # Correct: recursive copy
```

## 실무 적용

- **프로젝트 초기화**: `mkdir -p`로 디렉터리 구조를 한 번에 생성합니다
- **로그 백업**: `cp -r /var/log/app/ /backup/$(date +%F)/`로 날짜별 백업을 만듭니다
- **빌드 정리**: `rm -rf dist/ build/`로 이전 빌드 산출물을 정리합니다
- **설정 복사**: `cp config.yaml config.yaml.bak`으로 변경 전 백업을 둡니다
- **배포 준비**: `mv app-v2.0.tar.gz /opt/releases/`로 릴리스 파일을 이동합니다

## 실무에서는 이렇게 생각한다

파일 조작 명령어는 단순해 보이지만, **삭제는 되돌릴 수 없다**는 점이 핵심입니다. Git으로 관리되는 코드는 복구 가능하지만, 로그 파일이나 데이터베이스 덤프처럼 Git 밖의 파일은 한 번 지우면 끝입니다.

팀에서는 위험한 명령어에 안전장치를 겁니다. `.bashrc`에 `alias rm='rm -i'`를 넣어 삭제 전 확인을 받거나, `trash-cli` 같은 휴지통 도구를 씁니다. 서버에서는 `rm` 대신 `mv`로 임시 폴더에 옮긴 뒤, 일정 기간 후 정리하는 패턴이 안전합니다.

## 체크리스트

- [ ] `pwd`로 현재 위치를 확인하고 `cd`로 이동할 수 있다
- [ ] 절대 경로와 상대 경로의 차이를 설명할 수 있다
- [ ] `mkdir -p`로 중첩 디렉터리를 한 번에 만들 수 있다
- [ ] `cp`, `mv`, `rm`의 차이와 `-r` 옵션의 필요성을 안다
- [ ] 와일드카드 `*` 사용 전 `ls`로 대상을 확인하는 습관이 있다

## 연습 문제

1. `~/practice/linux-cli` 아래에 `logs`, `src`, `backup` 디렉터리를 만들고 `pwd`, `ls -la`로 결과를 확인해 보세요.
2. `notes.txt` 파일을 만든 뒤 복사본을 `backup/`으로 옮기고 이름을 `notes.bak`으로 바꿔 보세요.
3. `rm`, `rmdir`, `rm -r`가 각각 언제 필요한지 실제 예시를 한 줄씩 적어 보세요.

## 정리와 다음 글

- Linux 파일 시스템은 `/`(root)에서 시작하는 단일 트리 구조입니다.
- `pwd`, `cd`, `ls`로 현재 위치를 파악하고 이동합니다.
- `mkdir`, `touch`, `cp`, `mv`, `rm`으로 파일과 디렉터리를 조작합니다.
- 삭제는 되돌릴 수 없으므로 항상 대상을 확인한 후 실행합니다.
- 절대 경로는 어디서든 동작하고, 상대 경로는 현재 위치에 의존합니다.

다음 글에서는 **파일 권한과 소유자** — `chmod`, `chown`, `rwx`의 의미를 다룹니다.

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

## 실무 시나리오: 파일 작업을 안전하게 자동화하기

파일과 디렉터리 명령은 단순해 보이지만, 운영 사고의 상당수가 여기서 시작됩니다. 예를 들어 로그 정리 작업에서 경로 하나를 잘못 쓰면 필요한 파일을 삭제할 수 있습니다. 그래서 실무에서는 "작업 전 확인 -> 영향 범위 출력 -> 실제 실행"의 3단계를 습관화합니다.

```bash
# 1) 현재 위치와 대상 확인
pwd
ls -la ./releases

# 예상 출력
# /opt/my-app
# drwxr-xr-x  8 deploy deploy 4096 May 21 13:00 .
# drwxr-xr-x  5 deploy deploy 4096 May 21 09:11 ..
# drwxr-xr-x  2 deploy deploy 4096 May 14 10:00 20260514
```

### 이름 규칙을 먼저 만들고 생성하기

디렉터리 구조는 처음 설계가 중요합니다. 운영에서는 날짜와 환경 이름을 포함한 규칙을 두면 사고 추적이 쉬워집니다.

```bash
env_name="prod"
release_date="$(date +%Y%m%d)"
base_dir="/opt/my-app/releases/${env_name}-${release_date}"

mkdir -p "$base_dir"/{bin,conf,logs,tmp}
find "$base_dir" -maxdepth 2 -type d | sort

# 예상 출력
# /opt/my-app/releases/prod-20260521
# /opt/my-app/releases/prod-20260521/bin
# /opt/my-app/releases/prod-20260521/conf
# /opt/my-app/releases/prod-20260521/logs
# /opt/my-app/releases/prod-20260521/tmp
```

### 복사와 이동: 원자성 관점으로 보기

`cp`는 원본을 남기고, `mv`는 위치를 바꿉니다. 배포에서는 임시 디렉터리에 준비한 뒤 심볼릭 링크를 바꾸는 방식이 안전합니다.

```bash
cp -a ./build/. "$base_dir/bin/"
ln -sfn "$base_dir" /opt/my-app/current
ls -la /opt/my-app/current

# 예상 출력
# lrwxrwxrwx 1 deploy deploy 34 May 21 13:12 /opt/my-app/current -> /opt/my-app/releases/prod-20260521
```

`ln -sfn`은 기존 링크를 덮어써서 전환을 짧게 만들 수 있습니다. 다만 링크 대상 검증 없이 실행하면 잘못된 릴리스로 전환될 수 있으므로, 전환 직전 파일 수와 체크섬을 확인하는 절차를 두는 편이 좋습니다.

### 삭제는 항상 후보 출력부터 시작하기

삭제 작업에서 안전장치가 없으면 복구 비용이 큽니다.

```bash
# 삭제 후보 확인
find /opt/my-app/releases -maxdepth 1 -type d -name 'prod-*' -mtime +14 -print

# 실제 삭제
find /opt/my-app/releases -maxdepth 1 -type d -name 'prod-*' -mtime +14 -print0   | xargs -0 rm -rf
```

공백·특수문자 대응을 위해 `-print0`와 `xargs -0`를 조합합니다. 이 패턴은 파일 작업 자동화의 기본 안전장치입니다.

### 권한과 소유자를 함께 검증하기

파일이 있어도 권한이 맞지 않으면 서비스가 실패합니다.

```bash
chown -R deploy:deploy "$base_dir"
find "$base_dir" -type d -exec chmod 755 {} \;
find "$base_dir" -type f -name '*.sh' -exec chmod 750 {} \;

# 점검
find "$base_dir" -maxdepth 2 -printf '%M %u:%g %p
' | head -n 8
```

여기서 핵심은 실행 파일(`*.sh`)과 일반 파일의 권한을 분리하는 것입니다. 모든 파일에 `chmod 777`을 주는 방식은 편해 보여도 보안과 감사 관점에서 바로 문제가 됩니다.

### 파일 패턴 추출에 정규식 결합하기

정리 작업에서는 파일명 패턴 필터링이 자주 필요합니다.

```bash
ls -1 /var/log/my-app   | grep -E '^app-[0-9]{4}-[0-9]{2}-[0-9]{2}\.log(\.[0-9]+)?$'   | sort

# 예상 출력
# app-2026-05-19.log
# app-2026-05-20.log
# app-2026-05-20.log.1
```

정규식을 명확히 써 두면 의도하지 않은 파일을 건드릴 확률이 줄어듭니다.

### systemd 유닛과 디렉터리 구조 연결

서비스가 참조하는 경로를 유닛 파일과 맞춰 두면 운영이 안정됩니다.

```ini
# /etc/systemd/system/my-app.service
[Unit]
Description=My App Service
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/my-app/current
ExecStart=/opt/my-app/current/bin/start.sh
Restart=on-failure
RestartSec=3

[Install]
WantedBy=multi-user.target
```

이 구조의 장점은 명확합니다. 새 릴리스를 준비한 뒤 `current` 링크만 바꾸면 유닛 파일은 건드리지 않아도 됩니다. 결과적으로 배포 변경점이 작아지고, 롤백도 빠르게 수행할 수 있습니다.

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

### 운영 메모: 실패 후 복구 순서

실패가 발생했을 때는 "원인 추정 -> 즉시 재시작"보다 "상태 확인 -> 증거 수집 -> 최소 조치" 순서가 안전합니다.

```bash
systemctl status my-api --no-pager | sed -n '1,12p'
journalctl -u my-api -n 50 --no-pager | grep -E 'ERROR|CRITICAL|timeout|Failed' || true
```

상태와 로그를 먼저 남겨 두면, 재시작 후 증거가 사라져도 회고와 재발 방지 작업을 진행할 수 있습니다.

## 처음 질문으로 돌아가기

- **절대 경로와 상대 경로는 언제 다르게 느껴질까요?**
  - 본문의 기준은 파일과 디렉터리 다루기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`pwd`, `cd`, `ls`만으로 현재 위치를 어떻게 읽어야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`cp`, `mv`, `rm`은 각각 어떤 상황에서 쓰면 안전할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linux CLI 101 (1/10): CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- **파일과 디렉터리 다루기 (현재 글)**
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

- [Linux Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html)
- [GNU Coreutils Manual](https://www.gnu.org/software/coreutils/manual/)
- [The Missing Semester - Navigating the Shell](https://missing.csail.mit.edu/2020/course-shell/)
- [Linux man page - cp, mv, rm](https://man7.org/linux/man-pages/)

- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko
Tags: Linux, CLI, File System, Directory, ls, cp
