---
title: 프로세스 확인과 종료
series: linux-cli-101
episode: 7
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
- Process
- ps
- kill
- Background
- CLI
last_reviewed: '2026-05-04'
seo_description: 프로세스는 실행 중인 프로그램의 인스턴스이며, 각각 고유한 PID를 가진 독립적인 작업자입니다.
---

# 프로세스 확인과 종료

> Linux CLI 101 시리즈 (7/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- 프로그램과 프로세스의 차이는 무엇일까요?
- 시스템에서 실행 중인 프로세스를 어떻게 확인할까요?
- 응답하지 않는 프로세스를 안전하게 종료하는 방법은 무엇일까요?
- 명령어를 백그라운드에서 실행하는 것은 왜 필요할까요?

> 프로세스는 실행 중인 프로그램의 인스턴스이며, 각각 고유한 PID를 가진 독립적인 작업자입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- `ps`, `top`으로 실행 중인 프로세스를 확인하는 법
- `kill`, `kill -9`으로 프로세스를 종료하는 법
- `&`, `bg`, `fg`, `jobs`로 백그라운드/포그라운드를 전환하는 법
- `nohup`으로 SSH 연결이 끊겨도 프로세스를 유지하는 법

## 왜 중요한가

서버에서 웹 서버가 CPU를 100% 쓰고 있거나, Python 스크립트가 무한 루프에 빠졌거나, 포트를 이미 다른 프로세스가 점유하고 있을 때 — 모두 프로세스를 확인하고 관리할 줄 알아야 해결됩니다.

> Flask 개발 서버를 실행했는데 "Address already in use" 에러가 납니다. 이전에 실행한 서버가 종료되지 않고 5000번 포트를 점유하고 있습니다. 어떤 프로세스가 차지하고 있는지 찾아서 종료해야 합니다.

## Mental Model

> 프로그램은 레시피(코드 파일)이고, 프로세스는 그 레시피로 실제 요리하고 있는 요리사(실행 인스턴스)입니다. 같은 레시피로 요리사 3명이 동시에 요리할 수 있듯, 같은 프로그램에서 프로세스 3개가 동시에 실행될 수 있습니다.

```text
프로그램(python)  →  프로세스 1 (PID 1234)  ← ps로 확인
                 →  프로세스 2 (PID 5678)  ← kill로 종료
                 →  프로세스 3 (PID 9012)  ← nohup으로 유지
```

## 핵심 개념

| 용어 | 의미 | 명령어 |
|---|---|---|
| PID | Process ID, 프로세스 고유 번호 | `echo $$` (현재 shell PID) |
| 포그라운드 | 터미널을 점유하는 프로세스 | 기본 실행 방식 |
| 백그라운드 | 터미널을 점유하지 않는 프로세스 | `command &` |
| SIGTERM (15) | 정상 종료 요청 | `kill PID` |
| SIGKILL (9) | 강제 종료 | `kill -9 PID` |

## Before / After

**Before (프로세스 관리를 모를 때)**

```text
"서버가 멈췄는데 뭐가 문제인지 모르겠다"
→ 터미널 닫고 다시 열기
→ 이전 프로세스가 좀비로 남아 포트 충돌
```

**After (프로세스를 이해할 때)**

```bash
lsof -i :5000                    # 5000번 포트 점유 프로세스 확인
kill $(lsof -t -i :5000)         # 해당 프로세스 종료
python app.py                     # 정상 실행
```

## 단계별 실습

### Step 1. 프로세스 확인

```bash
ps aux                           # 모든 프로세스 상세 보기
ps aux | grep python             # python 관련 프로세스만
ps -ef --forest                  # 부모-자식 관계를 트리로 표시
```

### Step 2. top으로 실시간 모니터링

```bash
top
# 조작법:
# q: 종료
# M: 메모리 순 정렬
# P: CPU 순 정렬
# k: 프로세스 종료 (PID 입력)
```

### Step 3. 프로세스 종료

```bash
# 실습용 프로세스 생성
sleep 300 &
# [1] 12345

ps aux | grep sleep
# user  12345  ... sleep 300

kill 12345                       # SIGTERM: 정상 종료 요청
# 종료되지 않으면:
kill -9 12345                    # SIGKILL: 강제 종료
```

### Step 4. 백그라운드 실행

```bash
sleep 100 &                      # 백그라운드에서 실행
# [1] 23456
jobs                             # 백그라운드 작업 목록
# [1]+  Running    sleep 100 &

fg %1                            # 포그라운드로 전환
# Ctrl+Z로 일시 정지
bg %1                            # 다시 백그라운드로
```

### Step 5. nohup으로 SSH 끊김에도 유지

```bash
nohup python long_task.py > task.log 2>&1 &
# [1] 34567
# SSH 연결을 끊어도 프로세스가 계속 실행됨
# 출력은 task.log에 저장
```

## 이 코드에서 봐야 할 것

- `ps aux`에서 `a`=모든 사용자, `u`=상세 정보, `x`=터미널 없는 프로세스 포함입니다
- `kill`은 기본적으로 SIGTERM(15)을 보냅니다. 프로그램이 정리 작업을 할 기회를 줍니다
- `kill -9`은 커널이 직접 프로세스를 죽입니다. 정리 작업 없이 즉시 종료됩니다
- `nohup`은 HUP(hangup) 시그널을 무시하게 하여 터미널 종료에도 살아남습니다

## 자주 하는 실수

### 실수 1. 바로 kill -9부터 쓴다

`kill -9`은 프로세스가 파일을 닫거나 임시 데이터를 저장할 기회를 주지 않습니다. 항상 `kill`(SIGTERM)을 먼저 시도하고, 5-10초 기다린 뒤에도 안 되면 `kill -9`을 씁니다.

### 실수 2. 잘못된 PID를 kill한다

```bash
ps aux | grep python
# 여러 줄이 나옴 — 어느 것이 내 프로세스인지 확인 필수
# 마지막 줄 "grep python"은 grep 자신이므로 무시
```

`pgrep -f "python app.py"`로 정확한 PID를 찾으세요.

### 실수 3. SSH 끊기면 프로세스도 죽는 것을 모른다

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

1. `sleep 600 &`으로 백그라운드 프로세스를 3개 만들고, `jobs`로 확인한 뒤, 하나를 `fg`로 포그라운드로 전환하여 `Ctrl+C`로 종료해보세요.
2. `ps aux | head -1`로 컬럼 헤더를 확인하고, PID, CPU%, MEM%, COMMAND 열의 의미를 설명해보세요.
3. `lsof -i :22`를 실행하여 SSH 데몬이 어떤 PID로 돌아가는지 확인해보세요.

## 정리 · 다음 글

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
- [cat, less, head, tail](./04-viewing-files.md)
- [grep, find, xargs](./05-grep-find-xargs.md)
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
