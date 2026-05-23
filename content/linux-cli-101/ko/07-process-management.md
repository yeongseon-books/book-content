---
title: "Linux CLI 101 (7/10): 프로세스 확인과 종료"
series: linux-cli-101
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
- Linux
- Process
- ps
- kill
- Background
- CLI
last_reviewed: '2026-05-15'
seo_description: 프로세스 조회, 종료, 백그라운드 실행 기법을 학습합니다. ps, top, kill 사용법과 nohup을 활용한 실무 관리 모델을 정리합니다.
---

# Linux CLI 101 (7/10): 프로세스 확인과 종료

서버에서 웹 서버가 CPU를 100% 쓰고 있거나, Python 스크립트가 무한 루프에 빠졌거나, 포트를 이미 다른 프로세스가 점유하고 있을 때 — 모두 프로세스를 확인하고 관리할 줄 알아야 해결됩니다.

![Linux CLI 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/07/07-01-mental-model.ko.png)
*Linux CLI 101 7장 흐름 개요*

## 먼저 던지는 질문

- 프로세스와 프로그램은 무엇이 다를까요?
- `ps`, `top`, `pgrep`, `kill`은 어떤 순서로 쓰면 좋을까요?
- 백그라운드 작업과 작업 제어는 왜 서버 운영에서 자주 필요할까요?

## 머릿속에 먼저 그릴 그림

> 프로그램은 레시피(코드 파일)이고, 프로세스는 그 레시피로 실제 요리하고 있는 요리사(실행 인스턴스)입니다. 같은 레시피로 요리사 3명이 동시에 요리할 수 있듯, 같은 프로그램에서 프로세스 3개가 동시에 실행될 수 있습니다.

```text
Program (python)  ->  Process 1 (PID 1234)  <- check with ps
                 ->  Process 2 (PID 5678)  <- terminate with kill
                 ->  Process 3 (PID 9012)  <- keep with nohup
```

## 핵심 개념

| 용어 | 의미 | 명령어 |
|---|---|---|
| PID | Process ID, 프로세스 고유 번호 | `echo $$` (현재 shell PID) |
| 포그라운드 | 터미널을 점유하는 프로세스 | 기본 실행 방식 |
| 백그라운드 | 터미널을 점유하지 않는 프로세스 | `command &` |
| SIGTERM (15) | 정상 종료 요청 | `kill PID` |
| SIGKILL (9) | 강제 종료 | `kill -9 PID` |

## 전과 후

**Before (프로세스 관리를 모를 때)**

```text
"The server is stuck and I don't know what's wrong"
-> Close and reopen the terminal
-> Previous process remains as a zombie, causing port conflicts
```

**After (프로세스를 이해할 때)**

```bash
lsof -i :5000                    # Find process holding port 5000
kill $(lsof -t -i :5000)         # Terminate it
python app.py                     # Start normally
```

## 단계별 실습

### 1단계. 프로세스 확인

```bash
ps aux                           # All processes in detail
ps aux | grep python             # Only python-related processes
ps -ef --forest                  # Parent-child tree view
```

### 2단계. 실시간으로 살펴보기

```bash
top
# Controls:
# q: quit
# M: sort by memory
# P: sort by CPU
# k: kill process (enter PID)
```

### 3단계. 프로세스 종료

```bash
# Create a practice process
sleep 300 &
# [1] 12345

ps aux | grep sleep
# user  12345  ... sleep 300

kill 12345                       # SIGTERM: graceful termination request
# If it doesn't stop:
kill -9 12345                    # SIGKILL: forced termination
```

### 4단계. 백그라운드 실행

```bash
sleep 100 &                      # Run in background
# [1] 23456
jobs                             # List background jobs
# [1]+  Running    sleep 100 &

fg %1                            # Bring to foreground
# Ctrl+Z to suspend
bg %1                            # Send back to background
```

### 5단계. 연결이 끊겨도 유지하기

```bash
nohup python long_task.py > task.log 2>&1 &
# [1] 34567
# Process continues even after SSH disconnection
# Output saved to task.log
```

## 이 코드에서 봐야 할 것

- `ps aux`에서 `a`=모든 사용자, `u`=상세 정보, `x`=터미널 없는 프로세스 포함입니다
- `kill`은 기본적으로 SIGTERM(15)을 보냅니다. 프로그램이 정리 작업을 할 기회를 줍니다
- `kill -9`은 커널이 직접 프로세스를 죽입니다. 정리 작업 없이 즉시 종료됩니다
- `nohup`은 HUP(hangup) 시그널을 무시하게 하여 터미널 종료에도 살아남습니다

## 자주 하는 실수

### 실수 1. 강제 종료부터 시도한다

`kill -9`은 프로세스가 파일을 닫거나 임시 데이터를 저장할 기회를 주지 않습니다. 항상 `kill`(SIGTERM)을 먼저 시도하고, 5-10초 기다린 뒤에도 안 되면 `kill -9`을 씁니다.

### 실수 2. 잘못된 프로세스를 종료한다

```bash
ps aux | grep python
# Multiple lines appear — verify which is your process
# The last line "grep python" is grep itself — ignore it
```

`pgrep -f "python app.py"`로 정확한 PID를 찾으세요.

### 실수 3. 연결이 끊길 때 작업이 함께 끝나는 것을 모른다

SSH 세션이 끊어지면 해당 세션에서 실행한 포그라운드 프로세스는 모두 종료됩니다. 오래 걸리는 작업은 반드시 `nohup` 또는 `tmux`/`screen`을 씁니다.

### 실수 4. 좀비 프로세스를 무시한다

`ps`에서 `Z`(zombie) 상태인 프로세스는 이미 종료되었지만 부모 프로세스가 종료 상태를 수거하지 않은 것입니다. 소수는 무해하지만 많으면 PID가 고갈됩니다.

### 실수 5. 포트 충돌을 재부팅으로 해결한다

포트가 점유되었다고 서버를 재부팅하는 것은 과잉 대응입니다. `lsof -i :PORT`로 점유 프로세스를 찾아 종료하면 됩니다.

## 실무 적용

- **포트 충돌 해결**: `lsof -i :8080 | grep LISTEN`으로 점유 프로세스를 찾습니다
- **메모리 누수 감시**: `top`에서 RSS(메모리) 열을 주기적으로 확인합니다
- **배치 작업 실행**: `nohup python etl.py > etl.log 2>&1 &`로 장시간 작업을 돌립니다
- **개발 서버 관리**: `Ctrl+C`로 종료하고, 종료가 안 되면 `kill`을 씁니다
- **도커 디버깅**: 컨테이너 안에서 `ps aux`로 실행 중인 서비스를 확인합니다

## 실무에서는 이렇게 생각한다

프로세스 관리는 "일단 실행하면 끝"이 아니라 "실행한 후 어떻게 관리할 것인가"까지 포함합니다. 운영 환경에서는 `systemd`, `supervisor`, `pm2` 같은 프로세스 매니저를 사용하여 크래시 시 자동 재시작, 로그 관리, 리소스 제한을 설정합니다.

개발 중에도 프로세스 감각이 중요합니다. "이 터미널을 닫으면 서버도 죽나?", "백그라운드에서 돌아가는 게 있나?" 같은 질문을 스스로 던지는 습관이, 나중에 프로덕션 장애를 예방합니다.

## 문제가 생기면 먼저 이렇게 확인하세요

- 포트 충돌이 나면 재부팅부터 하지 말고 `lsof -i :PORT`로 점유 프로세스를 찾으세요. PID와 COMMAND를 확인하면 잘못된 서버 인스턴스인지, 다른 서비스인지 바로 구분됩니다.
- `kill`을 보냈는데도 프로세스가 남아 있으면 `ps -p PID -o pid,stat,cmd`로 상태를 다시 봐야 합니다. `D` 상태나 좀비 상태처럼 시그널만으로 바로 안 정리되는 경우가 있습니다.
- `ps aux | grep python`에서 grep 자신이 같이 보이면 `pgrep -af "python app.py"`로 범위를 좁히세요. PID를 잘못 잡는 실수가 실제 장애보다 더 흔합니다.
- SSH가 끊긴 뒤 작업이 사라졌다면 포그라운드로 실행했는지부터 확인하세요. 장시간 작업은 `nohup`, `tmux`, `systemd-run` 중 하나를 기본 습관으로 두는 편이 안전합니다.

## 체크리스트

- [ ] `ps aux`로 시스템의 모든 프로세스를 확인할 수 있다
- [ ] `kill`과 `kill -9`의 차이를 설명할 수 있다
- [ ] `&`로 백그라운드 실행하고 `fg`/`bg`로 전환할 수 있다
- [ ] `nohup`으로 SSH 끊김에도 프로세스를 유지할 수 있다
- [ ] `lsof -i :PORT`로 포트를 점유하는 프로세스를 찾을 수 있다

## 연습 문제

1. `sleep 300`을 백그라운드로 실행하고 `ps`, `jobs`, `kill`로 상태 변화를 확인해 보세요.
2. `top` 또는 `htop`에서 CPU 정렬과 메모리 정렬을 바꿔 보며 어떤 차이가 보이는지 적어 보세요.
3. `nohup`이 SSH 연결 종료 이후에도 작업을 계속 살려 두는 이유를 한 문단으로 설명해 보세요.

## 정리와 다음 글

- 프로세스는 실행 중인 프로그램 인스턴스이며 고유 PID를 가집니다.
- `ps`, `top`으로 프로세스 상태를 확인하고, `kill`로 종료합니다.
- `kill`(SIGTERM) → 기다림 → `kill -9`(SIGKILL) 순서로 종료합니다.
- `&`, `bg`, `fg`로 백그라운드/포그라운드를 전환합니다.
- `nohup` 또는 `tmux`로 SSH 끊김에도 프로세스를 유지합니다.

다음 글에서는 **환경변수와 PATH** — Shell이 명령어를 찾는 방법과 설정 관리를 다룹니다.

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

## 실무 시나리오: 프로세스 관리와 서비스 복구 절차

프로세스 관리는 단순히 `kill` 명령을 아는 수준에서 끝나지 않습니다. 실무에서는 "어떤 프로세스가 왜 자원을 쓰는지"를 먼저 파악하고, 안전한 복구 절차로 연결해야 합니다.

### 기본 상태 점검 루틴

```bash
ps -eo pid,ppid,user,%cpu,%mem,etime,cmd --sort=-%cpu | head -n 15

# 예상 출력 일부
#   PID  PPID USER   %CPU %MEM     ELAPSED CMD
# 18231     1 deploy 92.3 12.1     00:43:21 /usr/bin/python3 /opt/my-api/app.py
```

CPU/메모리 상위 프로세스를 먼저 보면 병목 가설을 빠르게 세울 수 있습니다.

### 특정 프로세스 정밀 조회

```bash
pgrep -af 'my-api|gunicorn|uvicorn'

# 예상 출력
# 18231 /usr/bin/python3 /opt/my-api/app.py
# 18242 /usr/bin/python3 /opt/my-api/worker.py
```

`pgrep -af`는 PID와 전체 명령행을 함께 보여주므로 유사 이름 프로세스를 구분하기 좋습니다.

### 신호 기반 종료 전략

```bash
# 1) 정상 종료 요청
kill -TERM 18231

# 2) 종료 대기 후 강제 종료
sleep 5
kill -KILL 18231
```

실무 기본은 `TERM`입니다. 바로 `KILL`을 사용하면 정리 작업(파일 flush, 연결 종료)이 생략되어 데이터 불일치가 생길 수 있습니다.

### 우선순위 조정(nice/renice)

```bash
nice -n 10 /opt/my-api/bin/heavy-batch.sh
renice -n 5 -p 18242
```

배치 작업 우선순위를 낮춰 API 응답성을 지키는 전략으로 자주 사용합니다.

### 백그라운드 작업과 세션 분리

```bash
nohup /opt/my-api/bin/report.sh > /tmp/report.out 2>&1 &
disown
jobs -l
```

세션이 끊겨도 작업이 유지되어야 하는 상황에서 유용합니다. 다만 장기적으로는 systemd 서비스/타이머로 승격하는 편이 안정적입니다.

### systemd 중심 운영 패턴

```bash
systemctl status my-api --no-pager
systemctl restart my-api
systemctl is-failed my-api && journalctl -u my-api -n 80 --no-pager
```

프로세스를 직접 띄우는 방식보다 systemd 단위로 관리하면 재시작 정책과 로그 수집을 일관되게 적용할 수 있습니다.

```ini
# /etc/systemd/system/my-api.service
[Unit]
Description=My API Service
After=network.target

[Service]
Type=simple
User=deploy
WorkingDirectory=/opt/my-api/current
ExecStart=/opt/my-api/current/bin/start.sh
Restart=on-failure
RestartSec=2
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target
```

### 프로세스 누수 탐지를 위한 정규식 필터

```bash
ps -ef   | grep -E 'python3 .*my-api|gunicorn .*my-api'   | grep -v grep
```

배포 후 이전 버전 프로세스가 남아 있는지 점검할 때 유용합니다.

### 복구 자동화 Bash 스크립트

```bash
#!/usr/bin/env bash
set -euo pipefail

svc="my-api"

if ! systemctl is-active --quiet "$svc"; then
  echo "[WARN] $svc inactive, restarting"
  systemctl restart "$svc"
  sleep 2
fi

systemctl status "$svc" --no-pager | sed -n '1,12p'
journalctl -u "$svc" -n 40 --no-pager | grep -E 'ERROR|CRITICAL|Failed' || true
```

중요한 점은 "자동 복구 + 근거 출력"을 함께 수행하는 것입니다. 단순 재시작만 하면 재발 분석이 어려워집니다.

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

- **프로세스와 프로그램은 무엇이 다를까요?**
  - 프로그램은 디스크에 있는 코드나 실행 파일이고, 프로세스는 그것이 메모리에서 실제로 돌고 있는 인스턴스입니다. 같은 Python 앱이라도 `pgrep -af 'my-api|gunicorn|uvicorn'` 결과처럼 PID가 다른 여러 프로세스로 동시에 존재할 수 있다는 점이 핵심입니다.
- **`ps`, `top`, `pgrep`, `kill`은 어떤 순서로 쓰면 좋을까요?**
  - 먼저 `ps -eo ... --sort=-%cpu`나 `top`으로 자원 사용 상위를 보고, 이어서 `pgrep -af`로 정확한 프로세스를 특정한 뒤, 마지막에 `kill -TERM`으로 정상 종료를 시도하는 순서가 안전합니다. 그래도 남아 있으면 잠시 기다린 뒤 `kill -KILL`을 쓰는 흐름을 글에서 명확히 제시했습니다.
- **백그라운드 작업과 작업 제어는 왜 서버 운영에서 자주 필요할까요?**
  - SSH 세션이 끊겨도 오래 걸리는 배치나 점검 스크립트가 계속 돌아가야 하는 경우가 많기 때문입니다. `sleep 100 &`, `jobs`, `fg`, `bg` 같은 기본 제어와 `nohup ... > task.log 2>&1 &`, `disown` 패턴을 익혀 두면 세션과 작업을 분리해 안정적으로 운영할 수 있습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linux CLI 101 (1/10): CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): 파일과 디렉터리 다루기](./02-files-and-directories.md)
- [Linux CLI 101 (3/10): 권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- [Linux CLI 101 (4/10): cat, less, head, tail — 파일 내용 보기](./04-viewing-files.md)
- [Linux CLI 101 (5/10): grep, find, xargs — 검색의 삼총사](./05-grep-find-xargs.md)
- [Linux CLI 101 (6/10): pipe와 redirection](./06-pipe-and-redirection.md)
- **프로세스 확인과 종료 (현재 글)**
- 환경변수와 PATH (예정)
- 간단한 shell script (예정)
- SSH와 원격 서버 접속 (예정)

<!-- toc:end -->

## 참고 자료

- [Linux man page - ps](https://man7.org/linux/man-pages/man1/ps.1.html)
- [Linux man page - kill, signal](https://man7.org/linux/man-pages/man1/kill.1.html)
- [The Missing Semester - Job Control](https://missing.csail.mit.edu/2020/command-line/)
- [systemd for Developers](https://www.freedesktop.org/software/systemd/man/systemd.html)

- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko
Tags: Linux, Process, ps, kill, Background, CLI
