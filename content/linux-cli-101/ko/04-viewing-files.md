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

이 글은 Linux CLI 101 시리즈의 4번째 글입니다.

개발하다 보면 파일 내용을 확인하는 일이 수시로 발생합니다. 설정 파일의 값을 확인하고, 로그에서 에러를 찾고, CSV 데이터의 헤더를 봅니다. 에디터를 열면 무거운 파일은 몇 초씩 걸리고, 수정 모드로 들어가면 실수로 내용을 바꿀 위험도 있습니다.


![Linux CLI 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/04/04-01-big-picture.ko.png)
*Linux CLI 101 4장 흐름 개요*

## 먼저 던지는 질문

- 파일을 통째로 볼 때와 일부만 볼 때는 어떤 명령을 골라야 할까요?
- `less`가 단순 출력보다 더 안전한 이유는 무엇일까요?
- `head`와 `tail`은 로그 확인에서 어떻게 다르게 쓰일까요?

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

## 실무 시나리오: 파일 조회를 분석 루틴으로 바꾸기

파일 보기 명령은 단순히 내용을 읽는 행위가 아닙니다. 운영에서는 "문제 구간을 빠르게 찾고, 증거를 남기고, 다음 조치로 연결"하는 분석 루틴의 시작점입니다. 그래서 `cat`만 반복하는 습관보다, 목적에 맞는 조회 도구 조합을 익히는 편이 좋습니다.

### 전체 보기 전에 메타데이터부터 확인

```bash
ls -lh /var/log/my-app/app.log
stat /var/log/my-app/app.log

# 예상 출력 일부
# -rw-r----- 1 deploy deploy 142M May 21 14:10 /var/log/my-app/app.log
# Size: 148944001  Blocks: ...  Access: ...  Modify: 2026-05-21 14:10:03
```

파일 크기와 수정 시각을 먼저 보면 "지금 보고 있는 로그가 최신인지"를 빠르게 판단할 수 있습니다. 오래된 파일을 붙잡고 분석하는 실수를 줄여 줍니다.

### 구간 기반 조회로 시간 절약하기

```bash
# 처음 40줄: 포맷, 헤더, 초기화 로그 확인
head -n 40 /var/log/my-app/app.log

# 마지막 80줄: 현재 실패 징후 확인
tail -n 80 /var/log/my-app/app.log

# 실시간 추적
tail -f /var/log/my-app/app.log
```

실시간 추적 시에는 별도 터미널에서 요청을 재현하고, 로그 터미널은 증거 수집에 집중하는 방식이 효율적입니다.

### grep 정규식으로 실패 패턴 압축하기

```bash
grep -E 'ERROR|CRITICAL|Exception|timeout|5[0-9]{2}' /var/log/my-app/app.log   | tail -n 40

# 예상 출력
# 2026-05-21T14:12:03 ERROR Payment timeout after 3000ms
# 2026-05-21T14:12:04 CRITICAL Worker crashed pid=18312
```

`5[0-9]{2}` 같은 패턴은 HTTP 5xx를 포괄적으로 잡을 때 유용합니다. 텍스트를 읽는 대신 패턴으로 보는 습관이 분석 속도를 높입니다.

### 문맥 포함 조회로 원인 추적하기

```bash
grep -n -C 3 'Database connection pool exhausted' /var/log/my-app/app.log

# 예상 출력 일부
# 12931-... INFO checkout connection
# 12932-... WARN retrying request
# 12933:... ERROR Database connection pool exhausted
# 12934-... INFO queue depth=87
```

`-C 3`처럼 주변 문맥을 함께 보면 단일 오류 줄보다 원인 흐름을 이해하기 쉽습니다.

### less를 분석 도구처럼 사용하기

```bash
less /var/log/my-app/app.log
# /ERROR      -> 검색
# n / N       -> 다음/이전 결과
# g / G       -> 파일 처음/끝
# q           -> 종료
```

대용량 로그를 다룰 때 `less`는 단순 뷰어가 아니라 탐색기 역할을 합니다. 특히 검색 결과를 앞뒤로 오가며 패턴을 비교할 때 강력합니다.

### 파이프 체인으로 일자별 집계 만들기

```bash
grep -E 'ERROR|CRITICAL' /var/log/my-app/app.log   | awk '{print $1}'   | cut -d'T' -f1   | sort   | uniq -c

# 예상 출력
#   18 2026-05-19
#   24 2026-05-20
#   41 2026-05-21
```

오류량 추세를 빠르게 파악하면 "오늘만 급증했는지"를 즉시 판단할 수 있습니다.

### systemd 로그와 파일 로그를 연결해서 보기

```bash
journalctl -u my-app --since '30 min ago' --no-pager   | grep -E 'Started|Stopped|Failed|OOM|ERROR'
```

애플리케이션 파일 로그와 시스템 로그를 함께 보면 재시작 시점, OOM 여부, 서비스 실패 이유를 더 정확히 파악할 수 있습니다.

### 조회 자동화를 위한 Bash 스니펫

```bash
#!/usr/bin/env bash
set -euo pipefail

log_file="/var/log/my-app/app.log"

printf '[INFO] file=%s size=%s
' "$log_file" "$(stat -c '%s' "$log_file")"

grep -E 'ERROR|CRITICAL|timeout|5[0-9]{2}' "$log_file"   | tail -n 60   | tee /tmp/my-app-errors-latest.txt

printf '[INFO] saved=/tmp/my-app-errors-latest.txt
'
```

핵심은 결과를 파일로 남기는 것입니다. 회의나 장애 리포트에서 같은 근거를 재사용할 수 있어 의사소통 비용이 줄어듭니다.

## 운영 점검 플레이북

실무에서 CLI 지식은 "명령을 외우는 능력"보다 "실수 가능성을 줄이는 절차"로 드러납니다. 아래 플레이북은 작업 전에 위험을 줄이고, 작업 후 검증을 빠뜨리지 않기 위한 최소 절차입니다.

### 1) 작업 전 컨텍스트 확인

```bash
whoami
hostname
pwd
date

# 예상 출력
# deploy
# prod-api-01
# /opt/my-app
# Thu May 21 15:24:18 KST 2026
```

같은 명령이라도 서버와 경로가 다르면 결과가 완전히 달라집니다. 컨텍스트 확인은 사소해 보이지만 잘못된 환경 조작을 막는 첫 방어선입니다.

### 2) 영향 범위 먼저 출력

```bash
# 예시: 후보만 확인
find ./target -type f -name '*.log' -mtime +7 -print
```

삭제·이동·권한 변경처럼 파괴적일 수 있는 작업은 항상 후보 목록 출력이 선행되어야 합니다. "실행 전에 눈으로 검토"가 자동화 품질의 핵심입니다.

### 3) 파이프 체인으로 증거를 압축

```bash
journalctl -u my-api --since '20 min ago' --no-pager   | grep -E 'ERROR|CRITICAL|timeout|5[0-9]{2}'   | awk '{print $1, $2, $3, $NF}'   | sort   | uniq -c   | sort -nr
```

`grep -E` 정규식은 노이즈를 줄이는 첫 단계입니다. 빈도 집계(`uniq -c`)까지 연결하면 우선순위를 빠르게 정할 수 있습니다.

### 4) systemd 상태와 애플리케이션 로그를 함께 확인

```bash
systemctl status my-api --no-pager | sed -n '1,15p'
journalctl -u my-api -n 80 --no-pager
```

프로세스가 살아 있어도 서비스가 실패 상태일 수 있고, 반대로 서비스는 active인데 내부 오류가 계속 발생할 수 있습니다. 두 관점을 동시에 봐야 원인 추적이 정확해집니다.

### 5) Bash 스크립트로 반복 점검 표준화

```bash
#!/usr/bin/env bash
set -euo pipefail

svc="my-api"
window='10 min ago'

printf '[INFO] host=%s user=%s time=%s
' "$(hostname)" "$(whoami)" "$(date '+%F %T')"

if systemctl is-active --quiet "$svc"; then
  echo '[PASS] service active'
else
  echo '[FAIL] service inactive'
fi

journalctl -u "$svc" --since "$window" --no-pager   | grep -E 'ERROR|CRITICAL|timeout|Failed' || true
```

자동화의 목적은 사람이 바뀌어도 같은 품질의 점검 결과를 얻는 것입니다. 이 원칙이 지켜지면 장애 대응 시간과 커뮤니케이션 비용이 함께 줄어듭니다.


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


### 운영 메모: 변경 후 검증 체크

권한/조회/환경값 변경 직후에는 기능 테스트만 하지 말고 시스템 레벨 검증을 함께 수행합니다.

```bash
whoami
hostname
systemctl is-active my-api
journalctl -u my-api -n 20 --no-pager
```

짧은 검증 루틴이라도 매번 남기면, 장애 발생 시 "무엇을 언제 바꿨는지"를 빠르게 복원할 수 있습니다.


운영에서는 이 검증 로그를 이슈 번호와 함께 저장해 두면 다음 대응 속도가 확실히 빨라집니다.

이 습관이 장기 운영 품질을 만듭니다.

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

- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko
Tags: Linux, CLI, cat, less, tail, Log
