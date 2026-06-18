---
title: "바이브코딩을 위한 Linux CLI 기초 (7/10): 프로세스 확인과 종료"
series: linux-cli-101
episode: 7
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
- 바이브코딩
- Linux
- Process
- ps
- kill
- Background
- CLI
last_reviewed: '2026-06-18'
seo_description: AI가 만든 서버가 포트를 이미 점유하고 있거나, 무한 루프에 빠졌을 때 프로세스를 확인하고 종료하는 법을 정리합니다.
---

# 바이브코딩을 위한 Linux CLI 기초 (7/10): 프로세스 확인과 종료

이 글은 **바이브코딩을 위한 Linux CLI 기초** 시리즈의 일곱 번째 글입니다. AI가 생성한 코드를 서버에서 실제로 실행하고 운영하려면 Linux 명령어를 알아야 합니다.

---

AI가 만든 FastAPI 서버를 재시작하려고 합니다. "Address already in use" 에러가 납니다. 이전에 실행한 서버가 아직 포트를 점유하고 있습니다. 어떤 프로세스인지 찾아서 종료해야 합니다.

> 프로그램은 레시피(코드 파일)이고, 프로세스는 그 레시피로 실제 요리하고 있는 요리사(실행 인스턴스)입니다. 같은 레시피로 요리사 3명이 동시에 요리할 수 있듯, 같은 프로그램에서 프로세스 3개가 동시에 실행될 수 있습니다.

## 이 글에서 다룰 질문 5가지

1. 프로세스와 프로그램은 무엇이 다를까요?
2. `ps`, `top`, `pgrep`, `kill`은 어떤 순서로 쓰면 좋을까요?
3. 백그라운드 작업과 작업 제어는 왜 서버 운영에서 자주 필요할까요?
4. 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
5. 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 바이브코딩 관점에서 왜 프로세스 관리인가?

AI가 만든 웹 서버를 배포하면서 이런 상황을 만납니다. 서버를 새로 시작하려는데 포트가 이미 사용 중입니다. 이전 버전 서버가 아직 실행 중입니다. 또는 AI가 만든 배치 스크립트가 무한 루프에 빠져서 CPU를 100% 사용합니다.

이런 상황을 해결하려면 어떤 프로세스가 문제인지 찾고, 안전하게 종료해야 합니다.

## 핵심 개념

| 용어 | 의미 | 명령어 |
|---|---|---|
| PID | Process ID, 프로세스 고유 번호 | `echo $$` (현재 shell PID) |
| 포그라운드 | 터미널을 점유하는 프로세스 | 기본 실행 방식 |
| 백그라운드 | 터미널을 점유하지 않는 프로세스 | `command &` |
| SIGTERM (15) | 정상 종료 요청 | `kill PID` |
| SIGKILL (9) | 강제 종료 | `kill -9 PID` |

## Before / After: 프로세스 관리를 모를 때

**Before — 프로세스 관리를 모를 때**

```text
"The server is stuck and I don't know what's wrong"
-> Close and reopen the terminal
-> Previous process remains as a zombie, causing port conflicts
```

**After — 프로세스를 이해할 때**

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

### 4단계. 포트 점유 프로세스 찾기

```bash
# 8000번 포트를 사용하는 프로세스 찾기
lsof -i :8000
# COMMAND  PID   USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# python  1234   user   3u  IPv4  12345      0t0  TCP *:8000 (LISTEN)

# 해당 포트 프로세스 종료
kill $(lsof -t -i :8000)
```

### 5단계. SSH 끊겨도 유지하기

```bash
# SSH가 끊겨도 계속 실행
nohup python long_task.py > task.log 2>&1 &
# [1] 34567
# Process continues even after SSH disconnection
# Output saved to task.log
```

## 자주 하는 실수 (바이브코딩 맥락)

| 실수 | 설명 | 올바른 방법 |
|---|---|---|
| kill -9 먼저 | 정리 작업 기회 없이 강제 종료 | `kill`(SIGTERM) 먼저, 안 되면 `kill -9` |
| 잘못된 PID 종료 | grep 결과에 grep 자신 포함 | `pgrep -f "python app.py"` |
| 포트 충돌 시 재부팅 | 서버 재부팅은 과잉 대응 | `lsof -i :PORT`로 점유 프로세스 찾아 종료 |
| SSH 끊기면 작업 소멸 | 포그라운드 프로세스는 SSH 종료 시 함께 종료 | `nohup` 또는 `tmux` 사용 |
| 좀비 프로세스 무시 | `Z` 상태 프로세스 누적 시 PID 고갈 | 부모 프로세스 점검 |

## AI 팁: 바이브코딩 서버 운영 패턴

AI가 만든 서버를 운영할 때 가장 자주 쓰는 프로세스 관리 패턴입니다:

```bash
# 1. AI가 만든 FastAPI 서버 시작 (백그라운드)
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
echo "PID: $!"

# 2. 서버 상태 확인
ps aux | grep uvicorn | grep -v grep

# 3. 포트 확인
lsof -i :8000

# 4. 로그 실시간 확인
tail -f app.log

# 5. 서버 재시작 (AI가 코드를 수정했을 때)
kill $(lsof -t -i :8000)
sleep 2
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > app.log 2>&1 &
```

이 패턴을 반복하다 보면 systemd 서비스로 관리하는 것이 훨씬 낫다는 걸 느끼게 됩니다. 하지만 그 전에 프로세스 기본부터 이해해야 합니다.

## 운영 체크리스트

- [ ] `ps aux`로 시스템의 모든 프로세스를 확인할 수 있다
- [ ] `kill`과 `kill -9`의 차이를 설명할 수 있다
- [ ] `&`로 백그라운드 실행하고 `fg`/`bg`로 전환할 수 있다
- [ ] `nohup`으로 SSH 끊김에도 프로세스를 유지할 수 있다
- [ ] `lsof -i :PORT`로 포트를 점유하는 프로세스를 찾을 수 있다

## 처음 질문으로 돌아가기

- **프로세스와 프로그램은 무엇이 다를까요?** 프로그램은 디스크에 있는 코드 파일이고, 프로세스는 메모리에 로드되어 실행 중인 인스턴스입니다. 같은 Python 파일을 두 번 실행하면 프로세스가 두 개 생깁니다.
- **백그라운드 작업은 왜 서버 운영에서 필요할까요?** SSH 세션이 끊어지면 포그라운드 프로세스는 종료됩니다. 서버는 24시간 실행되어야 하므로 백그라운드 실행이 필수입니다.

## 정리

- 프로세스는 실행 중인 프로그램 인스턴스이며 고유 PID를 가집니다.
- `ps`, `top`으로 프로세스 상태를 확인하고, `kill`로 종료합니다.
- `kill`(SIGTERM) → 기다림 → `kill -9`(SIGKILL) 순서로 종료합니다.
- `&`, `bg`, `fg`로 백그라운드/포그라운드를 전환합니다.
- `nohup` 또는 `tmux`로 SSH 끊김에도 프로세스를 유지합니다.

다음 글에서는 **환경변수와 PATH** — Shell이 명령어를 찾는 방법과 설정 관리를 다룹니다.

## 참고 자료

- [Linux man page - ps](https://man7.org/linux/man-pages/man1/ps.1.html)
- [Linux man page - kill, signal](https://man7.org/linux/man-pages/man1/kill.1.html)
- [The Missing Semester - Job Control](https://missing.csail.mit.edu/2020/command-line/)
- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Linux CLI 기초 (1/10): CLI와 Shell이란 무엇인가?
- 바이브코딩을 위한 Linux CLI 기초 (2/10): 파일과 디렉터리 다루기
- 바이브코딩을 위한 Linux CLI 기초 (3/10): 권한과 소유자 이해하기
- 바이브코딩을 위한 Linux CLI 기초 (4/10): cat, less, head, tail — 파일 내용 보기
- 바이브코딩을 위한 Linux CLI 기초 (5/10): grep, find, xargs — 검색의 삼총사
- 바이브코딩을 위한 Linux CLI 기초 (6/10): pipe와 redirection
- **바이브코딩을 위한 Linux CLI 기초 (7/10): 프로세스 확인과 종료 (현재 글)**
- 바이브코딩을 위한 Linux CLI 기초 (8/10): 환경변수와 PATH
- 바이브코딩을 위한 Linux CLI 기초 (9/10): 간단한 shell script
- 바이브코딩을 위한 Linux CLI 기초 (10/10): SSH와 원격 서버 접속
<!-- toc:end -->

Tags: 바이브코딩, Linux, Process, ps, kill, Background, CLI
