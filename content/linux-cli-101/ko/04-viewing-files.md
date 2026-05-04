---
title: "cat, less, head, tail — 파일 내용 보기"
series: linux-cli-101
episode: 4
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
- CLI
- cat
- less
- tail
- Log
last_reviewed: '2026-05-04'
seo_description: cat은 파일을 통째로 쏟아내는 양동이이고, less는 한 페이지씩 넘기는 책입니다.
---

# cat, less, head, tail — 파일 내용 보기

> Linux CLI 101 시리즈 (4/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- 파일 내용을 확인하는 명령어가 왜 여러 개 필요할까요?
- 1GB 로그 파일을 열 때 `cat`을 쓰면 어떻게 될까요?
- `tail -f`는 어떤 상황에서 쓸까요?
- 파일의 처음 10줄만, 마지막 20줄만 보려면 어떻게 할까요?

> cat은 파일을 통째로 쏟아내는 양동이이고, less는 한 페이지씩 넘기는 책입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- `cat`으로 짧은 파일을 빠르게 확인하는 법
- `less`로 긴 파일을 페이지 단위로 탐색하는 법
- `head`와 `tail`로 파일의 앞뒤를 잘라 보는 법
- `tail -f`로 실시간 로그를 모니터링하는 법

## 왜 중요한가

개발하다 보면 파일 내용을 확인하는 일이 수시로 발생합니다. 설정 파일의 값을 확인하고, 로그에서 에러를 찾고, CSV 데이터의 헤더를 봅니다. 에디터를 열면 무거운 파일은 몇 초씩 걸리고, 수정 모드로 들어가면 실수로 내용을 바꿀 위험도 있습니다.

> 서버에서 1GB짜리 로그 파일의 마지막 에러를 확인해야 합니다. vim으로 열면 메모리를 다 쓰고, cat으로 출력하면 터미널이 몇 분간 스크롤됩니다.

읽기 전용 명령어를 용도에 맞게 쓰면 이 문제를 깔끔하게 해결합니다.

## Mental Model

> `cat`은 양동이를 한 번에 쏟는 것이고, `less`는 책을 한 페이지씩 넘기는 것입니다. `head`는 책의 첫 몇 페이지만 찢어보는 것이고, `tail`은 마지막 몇 페이지만 보는 것입니다.

```text
파일 크기 작다 ──→ cat (한 번에 출력)
파일 크기 크다 ──→ less (페이지 탐색)
앞부분만 필요 ──→ head -n 20
뒷부분만 필요 ──→ tail -n 20
실시간 추적  ──→ tail -f
```

## 핵심 개념

| 명령어 | 용도 | 특징 |
|---|---|---|
| `cat` | 파일 전체 출력 | 짧은 파일에 적합, 파이프 입력으로도 사용 |
| `less` | 페이지 단위 탐색 | 검색, 이동 가능, 메모리 효율적 |
| `head` | 파일 앞부분 출력 | 기본 10줄, `-n`으로 조절 |
| `tail` | 파일 뒷부분 출력 | 기본 10줄, `-f`로 실시간 추적 |
| `wc` | 줄/단어/바이트 수 세기 | `wc -l`로 줄 수만 확인 |

## Before / After

**Before (에디터로 모든 파일을 열 때)**

```text
vim /var/log/app/app.log    # 1GB 파일 → 30초 로딩
# 실수로 i 눌러 편집 모드 → 내용 변경 위험
# :q!로 나가기
```

**After (읽기 전용 명령어 사용)**

```bash
tail -n 50 /var/log/app/app.log    # 마지막 50줄만 즉시 출력
tail -f /var/log/app/app.log       # 새 로그가 쌓이면 실시간으로 표시
```

## 단계별 실습

### Step 1. 실습용 파일 만들기

```bash
cd ~/practice/linux-cli
seq 1 100 > numbers.txt          # 1부터 100까지 숫자 파일
echo -e "name,age\nAlice,30\nBob,25\nCharlie,35" > data.csv
cat /etc/passwd > users.txt      # 시스템 사용자 목록 복사
```

### Step 2. cat으로 짧은 파일 보기

```bash
cat data.csv
# name,age
# Alice,30
# Bob,25
# Charlie,35

cat -n data.csv          # 줄 번호 포함
# 1  name,age
# 2  Alice,30
# 3  Bob,25
# 4  Charlie,35
```

### Step 3. head와 tail

```bash
head numbers.txt          # 처음 10줄
head -n 5 numbers.txt     # 처음 5줄

tail numbers.txt          # 마지막 10줄
tail -n 3 numbers.txt     # 마지막 3줄
# 98
# 99
# 100
```

### Step 4. less로 긴 파일 탐색

```bash
less users.txt
# 조작법:
# Space 또는 f: 다음 페이지
# b: 이전 페이지
# /keyword: 검색 (n으로 다음 결과)
# g: 파일 처음으로
# G: 파일 끝으로
# q: 종료
```

### Step 5. tail -f로 실시간 로그 보기

```bash
# 터미널 1: 로그를 실시간으로 감시
tail -f /tmp/test.log &

# 터미널에서 로그 추가
echo "$(date) INFO: app started" >> /tmp/test.log
echo "$(date) ERROR: connection failed" >> /tmp/test.log

# tail -f가 새 줄을 즉시 출력
# Ctrl+C로 종료
kill %1 2>/dev/null
```

## 이 코드에서 봐야 할 것

- `seq 1 100 > numbers.txt`에서 `>`은 출력을 파일로 보내는 redirection입니다 (Ep6에서 자세히)
- `cat -n`은 디버깅할 때 줄 번호가 필요할 때 유용합니다
- `less`는 파일을 메모리에 전부 올리지 않아서 거대한 파일도 즉시 열립니다
- `tail -f`의 `f`는 "follow"입니다. 파일 끝을 계속 추적합니다

## 자주 하는 실수

### 실수 1. 큰 파일에 cat을 쓴다

```bash
cat access.log    # 1GB 파일 → 터미널이 몇 분간 출력
# Ctrl+C로 중단은 되지만, 이미 터미널 버퍼가 가득 참
```

`less`를 쓰거나, `tail -n 100`으로 필요한 부분만 봅니다.

### 실수 2. less에서 나가는 법을 모른다

`q`를 누르면 됩니다. `less` 안에서 `Ctrl+C`는 동작하지 않습니다. `less`는 vim과 달리 `:q`가 아니라 `q` 하나입니다.

### 실수 3. tail -f를 종료하지 않고 다른 작업을 한다

`tail -f`는 끝나지 않는 명령입니다. `Ctrl+C`로 명시적으로 종료해야 합니다. 백그라운드로 두면 리소스를 계속 사용합니다.

### 실수 4. head/tail의 기본값(10줄)을 모른다

`head file.txt`는 기본 10줄입니다. 5줄만 보고 싶으면 반드시 `-n 5`를 써야 합니다.

### 실수 5. cat으로 파일을 연결하는 원래 용도를 모른다

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

1. `/etc/passwd` 파일의 줄 수를 `wc -l`로 확인하고, 처음 5줄과 마지막 5줄을 각각 출력해보세요.
2. `seq 1 10000 > big.txt`로 만든 파일을 `less`로 열고, `/5000`으로 검색하여 해당 줄로 이동해보세요.
3. `tail -f /tmp/live.log`를 실행한 상태에서, 다른 터미널에서 `echo "test" >> /tmp/live.log`를 입력하여 실시간 출력을 확인해보세요.

## 정리 · 다음 글

- `cat`은 짧은 파일을 한 번에 출력하거나 파일을 연결할 때 씁니다.
- `less`는 큰 파일을 메모리 효율적으로 페이지 단위로 탐색합니다.
- `head`/`tail`은 파일의 앞뒤 일부만 빠르게 확인합니다.
- `tail -f`는 실시간 로그 모니터링의 핵심 도구입니다.
- 파일 크기와 목적에 따라 적절한 명령어를 선택하는 것이 CLI 숙련도입니다.

다음 글에서는 **텍스트 검색과 파일 찾기** — `grep`, `find`, `xargs`를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [파일과 디렉터리 다루기](./02-files-and-directories.md)
- [권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- **cat, less, head, tail (현재 글)**
- grep, find, xargs (예정)
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
