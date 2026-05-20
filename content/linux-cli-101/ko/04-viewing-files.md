---
title: "Linux CLI 101 (4/10): cat, less, head, tail — 파일 내용 보기"
series: linux-cli-101
episode: 4
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
- cat
- less
- tail
- Log
last_reviewed: '2026-05-12'
seo_description: cat, less, head, tail로 파일 내용을 읽는 기본 흐름을 정리합니다.
---

# Linux CLI 101 (4/10): cat, less, head, tail — 파일 내용 보기

개발하다 보면 파일 내용을 확인하는 일이 수시로 발생합니다. 설정 파일의 값을 확인하고, 로그에서 에러를 찾고, CSV 데이터의 헤더를 봅니다. 에디터를 열면 무거운 파일은 몇 초씩 걸리고, 수정 모드로 들어가면 실수로 내용을 바꿀 위험도 있습니다.

이 글은 Linux CLI 101 시리즈의 4번째 글입니다.

## 먼저 던지는 질문

- 파일을 통째로 볼 때와 일부만 볼 때는 어떤 명령을 골라야 할까요?
- `less`가 단순 출력보다 더 안전한 이유는 무엇일까요?
- `head`와 `tail`은 로그 확인에서 어떻게 다르게 쓰일까요?

## 큰 그림

![Linux CLI 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/04/04-01-big-picture.ko.png)

*Linux CLI 101 4장 흐름 개요*

이 그림에서는 cat, less, head, tail — 파일 내용 보기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> cat, less, head, tail — 파일 내용 보기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 머릿속에 먼저 그릴 그림

> `cat`은 양동이를 한 번에 쏟는 것이고, `less`는 책을 한 페이지씩 넘기는 것입니다. `head`는 책의 첫 몇 페이지만 찢어보는 것이고, `tail`은 마지막 몇 페이지만 보는 것입니다.

```text
Small file     --> cat (print at once)
Large file     --> less (page navigation)
Need beginning --> head -n 20
Need end       --> tail -n 20
Real-time      --> tail -f
```

## 핵심 개념

| 명령어 | 용도 | 특징 |
|---|---|---|
| `cat` | 파일 전체 출력 | 짧은 파일에 적합, 파이프 입력으로도 사용 |
| `less` | 페이지 단위 탐색 | 검색, 이동 가능, 메모리 효율적 |
| `head` | 파일 앞부분 출력 | 기본 10줄, `-n`으로 조절 |
| `tail` | 파일 뒷부분 출력 | 기본 10줄, `-f`로 실시간 추적 |
| `wc` | 줄/단어/바이트 수 세기 | `wc -l`로 줄 수만 확인 |

## 전과 후

**Before (에디터로 모든 파일을 열 때)**

```text
vim /var/log/app/app.log    # 1GB file -> 30 seconds to load
# Accidentally press i -> edit mode -> risk of changing contents
# :q! to exit
```

**After (읽기 전용 명령어 사용)**

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
cat /etc/passwd > users.txt      # Copy system user list
```

### 2단계. 짧은 파일 보기

```bash
cat data.csv
# name,age
# Alice,30
# Bob,25
# Charlie,35

cat -n data.csv          # With line numbers
# 1  name,age
# 2  Alice,30
# 3  Bob,25
# 4  Charlie,35
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
less users.txt
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
# Terminal 1: monitor logs in real time
tail -f /tmp/test.log &

# Add log entries
echo "$(date) INFO: app started" >> /tmp/test.log
echo "$(date) ERROR: connection failed" >> /tmp/test.log

# tail -f prints new lines immediately
# Ctrl+C to stop
kill %1 2>/dev/null
```

## 이 코드에서 봐야 할 것

- `seq 1 100 > numbers.txt`에서 `>`은 출력을 파일로 보내는 redirection입니다 (Ep6에서 자세히)
- `cat -n`은 디버깅할 때 줄 번호가 필요할 때 유용합니다
- `less`는 파일을 메모리에 전부 올리지 않아서 거대한 파일도 즉시 열립니다
- `tail -f`의 `f`는 "follow"입니다. 파일 끝을 계속 추적합니다

## 자주 하는 실수

### 실수 1. 큰 파일을 한꺼번에 출력한다

```bash
cat access.log    # 1GB file -> terminal scrolls for minutes
# Ctrl+C stops it, but the terminal buffer is already flooded
```

`less`를 쓰거나, `tail -n 100`으로 필요한 부분만 봅니다.

### 실수 2. 파일 보기 도구에서 나가는 법을 모른다

`q`를 누르면 됩니다. `less` 안에서 `Ctrl+C`는 동작하지 않습니다. `less`는 vim과 달리 `:q`가 아니라 `q` 하나입니다.

### 실수 3. 실시간 감시를 종료하지 않고 다른 작업을 한다

`tail -f`는 끝나지 않는 명령입니다. `Ctrl+C`로 명시적으로 종료해야 합니다. 백그라운드로 두면 리소스를 계속 사용합니다.

### 실수 4. 기본 출력 줄 수를 모른다

`head file.txt`는 기본 10줄입니다. 5줄만 보고 싶으면 반드시 `-n 5`를 써야 합니다.

### 실수 5. 파일 연결 명령의 원래 용도를 모른다

`cat`은 concatenate(연결)의 약자입니다. 파일 여러 개를 이어붙이는 것이 본래 용도입니다.

```bash
cat header.csv data1.csv data2.csv > combined.csv
```

## 실무 적용

- **로그 모니터링**: `tail -f /var/log/nginx/error.log`로 실시간 에러를 봅니다
- **CSV 헤더 확인**: `head -n 1 data.csv`로 컬럼 이름만 빠르게 확인합니다
- **설정 확인**: `cat config.yaml`로 짧은 설정 파일을 봅니다
- **줄 수 세기**: `wc -l access.log`로 요청 수를 빠르게 파악합니다
- **로그 필터링**: `tail -n 1000 app.log | grep ERROR`로 최근 에러만 뽑습니다

## 실무에서는 이렇게 생각한다

"어떤 명령어로 파일을 볼까"의 판단 기준은 **파일 크기와 목적**입니다. 수십 줄이면 `cat`, 수백 줄 이상이면 `less`, 앞뒤만 보면 `head`/`tail`입니다. 이 선택이 자동으로 되면 CLI 작업 속도가 눈에 띄게 빨라집니다.

운영 환경에서 가장 많이 쓰는 조합은 `tail -f` + `grep`입니다. `tail -f app.log | grep --line-buffered ERROR`를 띄워두면 에러가 발생하는 즉시 화면에 나타납니다. 장애 대응 시 이 조합을 모르면 "로그 파일을 에디터로 열어서 새로고침"하는 비효율에 빠집니다.

## 체크리스트

- [ ] `cat`, `less`, `head`, `tail`의 용도를 구분할 수 있다
- [ ] `less`에서 검색(`/`)과 종료(`q`)를 할 수 있다
- [ ] `head -n N`과 `tail -n N`으로 원하는 줄 수만 볼 수 있다
- [ ] `tail -f`로 실시간 로그를 모니터링할 수 있다
- [ ] 파일 크기에 따라 적절한 명령어를 선택할 수 있다

## 연습 문제

1. CSV 파일 하나를 만들고 `cat`, `head -n 2`, `tail -n 2`, `nl -ba`로 각각 어떤 정보를 빠르게 확인할 수 있는지 비교해 보세요.
2. 100줄짜리 텍스트 파일을 만든 뒤 `less`에서 검색(`/keyword`)과 처음·끝 이동(`g`, `G`)을 직접 해 보세요.
3. `tail -f`가 로그 모니터링에 적합한 이유를 실무 상황 하나와 함께 설명해 보세요.

## 정리와 다음 글

- `cat`은 짧은 파일을 한 번에 출력하거나 파일을 연결할 때 씁니다.
- `less`는 큰 파일을 메모리 효율적으로 페이지 단위로 탐색합니다.
- `head`/`tail`은 파일의 앞뒤 일부만 빠르게 확인합니다.
- `tail -f`는 실시간 로그 모니터링의 핵심 도구입니다.
- 파일 크기와 목적에 따라 적절한 명령어를 선택하는 것이 CLI 숙련도입니다.

다음 글에서는 **텍스트 검색과 파일 찾기** — `grep`, `find`, `xargs`를 다룹니다.

## 처음 질문으로 돌아가기

- **파일을 통째로 볼 때와 일부만 볼 때는 어떤 명령을 골라야 할까요?**
  - 본문의 기준은 cat, less, head, tail — 파일 내용 보기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`less`가 단순 출력보다 더 안전한 이유는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`head`와 `tail`은 로그 확인에서 어떻게 다르게 쓰일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linux CLI 101 (1/10): CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): 파일과 디렉터리 다루기](./02-files-and-directories.md)
- [Linux CLI 101 (3/10): 권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- **cat, less, head, tail — 파일 내용 보기 (현재 글)**
- grep, find, xargs — 검색의 삼총사 (예정)
- pipe와 redirection (예정)
- 프로세스 확인과 종료 (예정)
- 환경변수와 PATH (예정)
- 간단한 shell script (예정)
- SSH와 원격 서버 접속 (예정)

<!-- toc:end -->

## 참고 자료

- [GNU Coreutils - cat, head, tail](https://www.gnu.org/software/coreutils/manual/)
- [less man page](https://man7.org/linux/man-pages/man1/less.1.html)
- [The Missing Semester - Data Wrangling](https://missing.csail.mit.edu/2020/data-wrangling/)
- [Linux Journal - tail -f and friends](https://www.linuxjournal.com/content/tail-f-and-friends)

Tags: Linux, CLI, cat, less, tail, Log
