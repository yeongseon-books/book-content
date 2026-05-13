---
title: 프로세스 확인과 종료
series: linux-cli-101
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
- Linux
- Process
- ps
- kill
- Background
- CLI
last_reviewed: '2026-05-12'
seo_description: 프로세스 조회, 종료, 백그라운드 실행의 기본 흐름을 정리합니다.
---

# 프로세스 확인과 종료

서버에서 웹 서버가 CPU를 100% 쓰고 있거나, Python 스크립트가 무한 루프에 빠졌거나, 포트를 이미 다른 프로세스가 점유하고 있을 때 — 모두 프로세스를 확인하고 관리할 줄 알아야 해결됩니다.

이 글은 Linux CLI 101 시리즈의 7번째 글입니다.

## 이 글에서 다룰 문제

- 프로세스와 프로그램은 무엇이 다를까요?
- `ps`, `top`, `pgrep`, `kill`은 어떤 순서로 쓰면 좋을까요?
- 백그라운드 작업과 작업 제어는 왜 서버 운영에서 자주 필요할까요?
- 문제가 생긴 프로세스를 무조건 `kill -9`로 끝내면 왜 안 될까요?

> 프로그램은 레시피(코드 파일)이고, 프로세스는 그 레시피로 실제 요리하고 있는 요리사(실행 인스턴스)입니다. 같은 레시피로 요리사 3명이 동시에 요리할 수 있듯, 같은 프로그램에서 프로세스 3개가 동시에 실행될 수 있습니다.

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

<!-- toc:begin -->
## 시리즈 목차

- [CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [파일과 디렉터리 다루기](./02-files-and-directories.md)
- [권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- [cat, less, head, tail — 파일 내용 보기](./04-viewing-files.md)
- [grep, find, xargs — 검색의 삼총사](./05-grep-find-xargs.md)
- [pipe와 redirection](./06-pipe-and-redirection.md)
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

Tags: Linux, Process, ps, kill, Background, CLI
