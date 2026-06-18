---
title: "바이브코딩을 위한 Linux CLI 기초 (4/10): cat, less, head, tail — 파일 내용 보기"
series: linux-cli-101
episode: 4
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
- 바이브코딩
- Linux
- CLI
- cat
- less
- tail
- Log
last_reviewed: '2026-06-18'
seo_description: AI가 만든 서버에서 에러가 났을 때 로그를 어떻게 볼까요? cat, less, head, tail로 파일 내용을 읽는 기본 흐름을 정리합니다.
---

# 바이브코딩을 위한 Linux CLI 기초 (4/10): cat, less, head, tail — 파일 내용 보기

이 글은 **바이브코딩을 위한 Linux CLI 기초** 시리즈의 네 번째 글입니다. AI가 생성한 코드를 서버에서 실제로 실행하고 운영하려면 Linux 명령어를 알아야 합니다.

---

AI가 만든 FastAPI 서버를 배포했습니다. 요청을 보냈는데 500 에러가 납니다. 로그 파일을 열어봐야 합니다. 에디터로 열면 1GB 파일은 30초가 걸리고, 실수로 수정할 위험도 있습니다. `cat`, `less`, `tail`은 빠르고 안전하게 파일 내용을 확인하는 도구입니다.

> `cat`은 양동이를 한 번에 쏟는 것이고, `less`는 책을 한 페이지씩 넘기는 것입니다. `head`는 책의 첫 몇 페이지만 찢어보는 것이고, `tail`은 마지막 몇 페이지만 보는 것입니다.

## 이 글에서 다룰 질문 5가지

1. 파일을 통째로 볼 때와 일부만 볼 때는 어떤 명령을 골라야 할까요?
2. `less`가 단순 출력보다 더 안전한 이유는 무엇일까요?
3. `head`와 `tail`은 로그 확인에서 어떻게 다르게 쓰일까요?
4. 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
5. 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 바이브코딩 관점에서 왜 파일 보기인가?

AI가 만든 서버가 운영 중입니다. 에러 리포트가 들어옵니다. 첫 번째로 할 일은 로그 파일을 확인하는 것입니다. 하지만 로그 파일은 수백 메가바이트에서 수 기가바이트까지 커질 수 있습니다.

`tail -f`로 실시간 로그를 보면서 AI가 생성한 코드가 어떻게 동작하는지 확인하고, 문제가 생기면 즉시 발견할 수 있습니다. 이 도구를 모르면 에러가 나도 무엇이 문제인지 알 수 없습니다.

## 명령어 선택 기준

```text
Small file     --> cat (print at once)
Large file     --> less (page navigation)
Need beginning --> head -n 20
Need end       --> tail -n 20
Real-time      --> tail -f
```

| 명령어 | 용도 | 특징 |
|---|---|---|
| `cat` | 파일 전체 출력 | 짧은 파일에 적합, 파이프 입력으로도 사용 |
| `less` | 페이지 단위 탐색 | 검색, 이동 가능, 메모리 효율적 |
| `head` | 파일 앞부분 출력 | 기본 10줄, `-n`으로 조절 |
| `tail` | 파일 뒷부분 출력 | 기본 10줄, `-f`로 실시간 추적 |
| `wc` | 줄/단어/바이트 수 세기 | `wc -l`로 줄 수만 확인 |

## Before / After: 에디터 vs 조회 명령어

**Before — 에디터로 모든 파일을 열 때**

```text
vim /var/log/app/app.log    # 1GB file -> 30 seconds to load
# Accidentally press i -> edit mode -> risk of changing contents
# :q! to exit
```

**After — 읽기 전용 명령어 사용**

```bash
tail -n 50 /var/log/app/app.log    # Last 50 lines printed instantly
tail -f /var/log/app/app.log       # New log lines appear in real time
```

## 단계별 실습

### 1단계. 실습용 파일 만들기

```bash
cd ~/practice/linux-cli
seq 1 100 > numbers.txt          # Numbers 1 through 100
echo -e "name,age\nAlice,30\nBob,25\nCharlie,35" > data.csv
```

### 2단계. 짧은 파일 보기

```bash
cat data.csv
# name,age
# Alice,30
# Bob,25
# Charlie,35

cat -n data.csv          # With line numbers
```

### 3단계. 앞부분과 뒷부분 보기

```bash
head numbers.txt          # First 10 lines
head -n 5 numbers.txt     # First 5 lines

tail numbers.txt          # Last 10 lines
tail -n 3 numbers.txt     # Last 3 lines
# 98
# 99
# 100
```

### 4단계. 긴 파일 탐색하기

```bash
less /etc/passwd
# Controls:
# Space or f: next page
# b: previous page
# /keyword: search (n for next result)
# g: go to beginning
# G: go to end
# q: quit
```

### 5단계. 실시간 로그 보기

```bash
# 실시간 로그 모니터링
tail -f /var/log/syslog

# grep과 조합해서 에러만 보기
tail -f /var/log/app/app.log | grep --line-buffered ERROR
# Ctrl+C to stop
```

## 자주 하는 실수 (바이브코딩 맥락)

| 실수 | 설명 | 올바른 방법 |
|---|---|---|
| 큰 파일을 cat으로 출력 | 1GB 파일이 터미널을 몇 분 동안 스크롤 | `less` 또는 `tail -n 100` 사용 |
| less에서 나가는 법 모름 | `Ctrl+C`는 작동 안 함 | `q`를 눌러서 종료 |
| tail -f 미종료 | 끝나지 않는 명령 | `Ctrl+C`로 명시적 종료 |
| 기본 줄 수 오해 | `head file.txt`는 기본 10줄 | 5줄만 보려면 `head -n 5` |
| cat의 원래 용도 오해 | cat은 "concatenate" 파일 연결이 본래 목적 | `cat header.csv data.csv > combined.csv` |

## AI 팁: 장애 대응에서 로그 확인

AI가 만든 서버에서 에러가 났을 때 첫 번째 단계는 로그 확인입니다. 이런 패턴을 기억하세요:

```bash
# 최근 에러만 빠르게 확인
tail -n 100 /var/log/myapp/app.log | grep ERROR

# 실시간으로 에러 모니터링하면서 재현
tail -f /var/log/myapp/app.log | grep --line-buffered -E 'ERROR|CRITICAL'

# 파일 크기와 마지막 수정 시각 확인
ls -lh /var/log/myapp/app.log
```

AI에게 "이 로그를 분석해줘"라고 붙여넣기 전에, 먼저 자신이 최근 100줄 정도를 빠르게 훑어보는 습관을 갖는 것이 좋습니다.

## 운영 체크리스트

- [ ] `cat`, `less`, `head`, `tail`의 용도를 구분할 수 있다
- [ ] `less`에서 검색(`/`)과 종료(`q`)를 할 수 있다
- [ ] `head -n N`과 `tail -n N`으로 원하는 줄 수만 볼 수 있다
- [ ] `tail -f`로 실시간 로그를 모니터링할 수 있다
- [ ] 파일 크기에 따라 적절한 명령어를 선택할 수 있다

## 처음 질문으로 돌아가기

- **파일을 통째로 볼 때와 일부만 볼 때는 어떤 명령을 골라야 할까요?** 수십 줄이면 `cat`, 수백 줄 이상이면 `less`, 앞뒤만 보면 `head`/`tail`입니다.
- **`less`가 단순 출력보다 더 안전한 이유는?** 파일을 메모리에 전부 올리지 않아서 거대한 파일도 즉시 열립니다. 수정 모드도 없어서 내용을 실수로 바꿀 위험이 없습니다.
- **`head`와 `tail`은 로그 확인에서 어떻게 다르게 쓰일까요?** `head`는 로그 포맷과 초기화 메시지 확인, `tail -f`는 실시간 에러 모니터링에 씁니다.

## 정리

- `cat`은 짧은 파일을 한 번에 출력하거나 파일을 연결할 때 씁니다.
- `less`는 큰 파일을 메모리 효율적으로 페이지 단위로 탐색합니다.
- `head`/`tail`은 파일의 앞뒤 일부만 빠르게 확인합니다.
- `tail -f`는 실시간 로그 모니터링의 핵심 도구입니다.
- 파일 크기와 목적에 따라 적절한 명령어를 선택하는 것이 CLI 숙련도입니다.

다음 글에서는 **텍스트 검색과 파일 찾기** — `grep`, `find`, `xargs`를 다룹니다.

## 참고 자료

- [GNU Coreutils - cat, head, tail](https://www.gnu.org/software/coreutils/manual/)
- [less man page](https://man7.org/linux/man-pages/man1/less.1.html)
- [The Missing Semester - Data Wrangling](https://missing.csail.mit.edu/2020/data-wrangling/)
- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Linux CLI 기초 (1/10): CLI와 Shell이란 무엇인가?
- 바이브코딩을 위한 Linux CLI 기초 (2/10): 파일과 디렉터리 다루기
- 바이브코딩을 위한 Linux CLI 기초 (3/10): 권한과 소유자 이해하기
- **바이브코딩을 위한 Linux CLI 기초 (4/10): cat, less, head, tail — 파일 내용 보기 (현재 글)**
- 바이브코딩을 위한 Linux CLI 기초 (5/10): grep, find, xargs — 검색의 삼총사
- 바이브코딩을 위한 Linux CLI 기초 (6/10): pipe와 redirection
- 바이브코딩을 위한 Linux CLI 기초 (7/10): 프로세스 확인과 종료
- 바이브코딩을 위한 Linux CLI 기초 (8/10): 환경변수와 PATH
- 바이브코딩을 위한 Linux CLI 기초 (9/10): 간단한 shell script
- 바이브코딩을 위한 Linux CLI 기초 (10/10): SSH와 원격 서버 접속
<!-- toc:end -->

Tags: 바이브코딩, Linux, CLI, cat, less, tail, Log
