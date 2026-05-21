---
title: "Linux CLI 101 (5/10): grep, find, xargs — 검색의 삼총사"
series: linux-cli-101
episode: 5
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
- grep
- find
- xargs
- Search
- CLI
last_reviewed: '2026-05-15'
seo_description: grep, find, xargs를 함께 써서 검색 작업을 이어 붙이는 법을 정리합니다.
---

# Linux CLI 101 (5/10): grep, find, xargs — 검색의 삼총사

이 글은 Linux CLI 101 시리즈의 5번째 글입니다.

프로젝트가 커지면 파일이 수백 개를 넘깁니다. "이 함수를 어디에서 호출하지?", "어제 수정된 파일이 뭐지?", "ERROR가 포함된 로그 줄만 보고 싶다" — 이 모든 질문에 답하는 것이 `grep`과 `find`입니다.


![Linux CLI 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/05/05-01-mental-model.ko.png)
*Linux CLI 101 5장 흐름 개요*

## 먼저 던지는 질문

- 파일 내용 검색과 파일 위치 검색은 왜 다른 문제일까요?
- `grep`, `find`, `xargs`는 어떤 순서로 연결하면 좋을까요?
- 검색 결과를 다음 명령으로 넘길 때 어떤 위험을 먼저 생각해야 할까요?

## 머릿속에 먼저 그릴 그림

> `grep`은 도서관에서 책 내용을 검색하는 전문 사서이고, `find`는 책꽂이에서 제목이나 크기로 책을 찾는 수색대입니다. `xargs`는 찾은 책 목록을 다른 사람에게 넘겨주는 전달자입니다.

```text
grep: "Find pages containing this word"     -> content search
find: "Find the red 200-page book"          -> file search
xargs: "Take the found books to the copier" -> results -> command
```

## 핵심 개념

| 명령어 | 검색 대상 | 주요 옵션 | 예시 |
|---|---|---|---|
| `grep` | 파일 내용(텍스트) | `-r`, `-n`, `-i`, `-l` | `grep -rn "TODO" src/` |
| `find` | 파일/디렉터리(메타데이터) | `-name`, `-type`, `-mtime`, `-size` | `find . -name "*.py"` |
| `xargs` | stdin을 인자로 변환 | `-I {}`, `-P` | `find . -name "*.log" \| xargs rm` |

## 전과 후

**Before (수동 검색)**

```text
1. Open files one by one in an editor
2. Ctrl+F to search
3. Open next file
4. Repeat for 30 files -> 20 minutes
```

**After (grep 한 줄)**

```bash
grep -rn "connection timeout" /var/log/app/
# /var/log/app/web.log:1523: 2026-05-04 ERROR database connection timeout
# /var/log/app/worker.log:89: 2026-05-04 ERROR database connection timeout
# All locations found in 1 second
```

## 단계별 실습

### 1단계. 실습 환경 준비

```bash
cd ~/practice/linux-cli
mkdir -p project/src project/tests project/docs
echo 'def hello():
    # TODO: add logging
    print("hello")' > project/src/app.py
echo 'def test_hello():
    # TODO: fix assertion
    assert hello() is None' > project/tests/test_app.py
echo '# Project README
TODO: write documentation' > project/docs/README.md
```

### 2단계. 내용 검색

```bash
grep "TODO" project/src/app.py           # Single file
# TODO: add logging

grep -rn "TODO" project/                  # Recursive + line numbers
# project/src/app.py:2:    # TODO: add logging
# project/tests/test_app.py:2:    # TODO: fix assertion
# project/docs/README.md:2:TODO: write documentation

grep -ri "todo" project/                  # Case insensitive
grep -rl "TODO" project/                  # File paths only
# project/src/app.py
# project/tests/test_app.py
# project/docs/README.md
```

### 3단계. 파일 찾기

```bash
find project/ -name "*.py"               # Find by name
# project/src/app.py
# project/tests/test_app.py

find project/ -type d                     # Directories only
find project/ -name "*.py" -newer project/docs/README.md   # Newer than a specific file
find /tmp -size +1M -mtime -7            # Over 1MB, modified within 7 days
```

### 4단계. 검색 결과를 다음 명령에 넘기기

```bash
find project/ -name "*.py" | xargs wc -l
#  3 project/src/app.py
#  3 project/tests/test_app.py
#  6 total

grep -rl "TODO" project/ | xargs -I {} echo "Fix needed: {}"
# Fix needed: project/src/app.py
# Fix needed: project/tests/test_app.py
# Fix needed: project/docs/README.md
```

### 5단계. 실전 조합

```bash
# Find "print" calls in all Python files
find project/ -name "*.py" | xargs grep -n "print"
# project/src/app.py:3:    print("hello")

# Delete log files older than 30 days
find /tmp -name "*.log" -mtime +30 -print | xargs rm -v
```

## 이 코드에서 봐야 할 것

- `grep -r`의 `-r`은 recursive(재귀)이며 하위 디렉터리까지 탐색합니다
- `grep -l`은 매칭된 줄 대신 파일 경로만 출력하여 파이프라인에 유리합니다
- `find`의 `-name` 패턴은 따옴표로 감싸야 Shell이 와일드카드를 먼저 확장하지 않습니다
- `xargs -I {}`는 `{}`를 찾은 항목으로 치환합니다

## 자주 하는 실수

### 실수 1. 검색 패턴에 따옴표를 빼먹는다

```bash
find . -name *.py          # Shell expands *.py first -> unexpected results
find . -name "*.py"        # Correct: find processes the pattern directly
```

### 실수 2. 정규표현식을 모르고 검색한다

`grep "error.log"`에서 `.`은 "아무 문자"입니다. `error.log`뿐 아니라 `errorXlog`도 매칭됩니다. 문자 그대로 찾으려면 `grep -F "error.log"` 또는 `grep "error\.log"`를 씁니다.

### 실수 3. 공백이 있는 파일 이름을 안전하게 넘기지 못한다

```bash
find . -name "*.txt" | xargs rm          # "My File.txt" splits into "My" and "File.txt"
find . -name "*.txt" -print0 | xargs -0 rm  # Null delimiter handles spaces safely
```

### 실수 4. 검색 결과를 비효율적으로 반복 처리한다

```bash
# Slow and unsafe
for f in $(find . -name "*.log"); do rm "$f"; done

# Fast and safe
find . -name "*.log" -exec rm {} \;
# or
find . -name "*.log" -print0 | xargs -0 rm
```

### 실수 5. 텍스트가 아닌 파일까지 같은 방식으로 검색한다

이미지, 실행 파일 등 바이너리 파일에 grep을 돌리면 깨진 문자가 출력됩니다. `grep --include="*.py" -r "pattern" .`으로 파일 유형을 제한하세요.

## 실무 적용

- **코드 검색**: `grep -rn "deprecated" src/`로 사용 중단된 API 호출을 찾습니다
- **로그 분석**: `grep -c "ERROR" app.log`로 에러 횟수를 셉니다
- **디스크 정리**: `find /tmp -mtime +30 -delete`로 오래된 임시 파일을 삭제합니다
- **빌드 산출물 정리**: `find . -name "__pycache__" -type d | xargs rm -rf`
- **코드 리뷰 준비**: `find . -name "*.py" -newer last-review.txt`로 리뷰 이후 변경된 파일을 찾습니다

## 실무에서는 이렇게 생각한다

`grep`과 `find`는 CLI 생활에서 가장 자주 쓰는 명령어입니다. IDE의 "프로젝트 전체 검색"이 내부적으로 하는 일이 `grep -r`이며, "파일 탐색기"가 하는 일이 `find`입니다. CLI에서 직접 쓰면 IDE보다 옵션이 유연하고, 파이프라인으로 후속 작업까지 자동화할 수 있습니다.

실무에서는 `grep`보다 빠른 `ripgrep(rg)`을 쓰는 팀이 많습니다. `find`보다 빠른 `fd`도 인기입니다. 하지만 기본 명령어를 먼저 익혀야 대안 도구의 장점을 체감할 수 있고, 기본 명령어는 모든 서버에 설치되어 있다는 확실한 장점이 있습니다.

## 문제가 생기면 먼저 이렇게 확인하세요

- 검색 결과가 하나도 안 나오면 범위부터 줄여 보세요. `grep -n "TODO" file.txt`처럼 단일 파일에서 먼저 확인한 뒤 `-r`을 붙이면 패턴 문제인지 경로 문제인지 빨리 구분됩니다.
- `find . -name *.py`처럼 따옴표를 빼먹으면 셸이 먼저 `*.py`를 확장해 엉뚱한 결과가 나옵니다. 패턴은 항상 `"*.py"`처럼 감싸 두는 편이 안전합니다.
- 공백이 들어간 파일 이름을 `xargs`에 넘길 때 명령이 깨지면 `-print0`과 `xargs -0` 조합부터 적용하세요. 삭제나 이동 작업은 이 단계가 빠지면 실수 비용이 큽니다.
- `grep`이 바이너리 파일까지 뒤져서 출력이 지저분하면 `--include="*.py"`나 `--exclude-dir=.git`처럼 대상을 먼저 제한하세요. 실무에서는 속도보다 범위 제어가 먼저입니다.

## 체크리스트

- [ ] `grep -rn`으로 프로젝트 전체에서 문자열을 검색할 수 있다
- [ ] `find -name -type -mtime`으로 파일을 조건부로 찾을 수 있다
- [ ] `xargs`로 검색 결과를 다른 명령어에 전달할 수 있다
- [ ] 공백이 있는 파일 이름을 `-print0`과 `-0`으로 안전하게 처리할 수 있다
- [ ] `grep`의 `-i`, `-l`, `-c`, `-F` 옵션을 설명할 수 있다

## 연습 문제

1. 연습용 디렉터리를 만든 뒤 `TODO` 문자열이 들어 있는 파일만 `grep -R`로 찾아 보세요.
2. `find`로 `.py` 파일만 골라 `xargs`로 `wc -l`을 실행해 보고, 각 명령의 역할을 한 줄씩 적어 보세요.
3. 공백이 있는 파일 이름이 있을 때 `xargs`가 위험해지는 이유와 `-print0` / `-0` 조합의 의미를 설명해 보세요.

## 정리와 다음 글

- `grep`은 파일 내용에서 문자열을 검색하며, `-r`로 재귀, `-n`으로 줄번호를 표시합니다.
- `find`는 파일 이름, 유형, 크기, 수정 시간 등 메타데이터로 파일을 찾습니다.
- `xargs`는 표준 입력을 명령어 인자로 변환하며, `-0` 옵션으로 공백 문제를 방지합니다.
- 세 명령어의 조합은 수동 작업을 자동화하는 CLI의 핵심 패턴입니다.
- 기본 명령어를 먼저 익힌 뒤 `ripgrep`, `fd` 같은 대안 도구로 넘어가세요.

다음 글에서는 **pipe와 redirection** — 명령어를 연결하고 입출력 방향을 바꾸는 법을 다룹니다.


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

## 실무 시나리오: 대량 파일 처리 파이프라인 설계

`grep`, `find`, `xargs`는 "많은 파일 중 필요한 대상만 골라 안전하게 처리"하는 핵심 조합입니다. 운영에서는 이 세 도구를 단일 명령이 아니라 파이프라인으로 다뤄야 합니다.

### 1단계: 검색 조건을 먼저 검증

```bash
find /var/log/my-app -type f -name '*.log' -mtime -2 -print

# 예상 출력
# /var/log/my-app/app.log
# /var/log/my-app/worker.log
# /var/log/my-app/batch.log
```

처음부터 `-exec rm` 같은 파괴적 동작을 붙이지 않고, 후보 목록 출력부터 시작해야 합니다.

### 2단계: 정규식으로 노이즈 줄이기

```bash
grep -R -n -E 'ERROR|CRITICAL|timeout|HTTP/1\.1" 5[0-9]{2}' /var/log/my-app

# 예상 출력 일부
# /var/log/my-app/app.log:1203:... ERROR payment timeout
# /var/log/my-app/access.log:9312:... "GET /api/pay" 502
```

여기서 `HTTP/1\.1" 5[0-9]{2}` 패턴은 access 로그의 5xx 응답을 추출할 때 자주 씁니다.

### 3단계: xargs로 병렬 처리

```bash
find ./images -type f -name '*.png' -print0   | xargs -0 -n 1 -P 4 optipng -quiet
```

`-P 4`는 4개 작업을 병렬 실행합니다. CPU 집약 작업에서 처리 시간을 줄일 수 있지만, I/O 경쟁이나 시스템 부하를 고려해 적절한 병렬도를 선택해야 합니다.

### 파일명 안전성: -print0 / -0를 기본값으로

```bash
find ./reports -type f -name '*.csv' -print0   | xargs -0 -I {} sh -c 'wc -l "$1"' _ {}
```

공백, 따옴표, 줄바꿈이 포함된 파일명도 안전하게 처리하려면 이 조합이 필수입니다.

### grep 결과를 후속 처리에 연결

```bash
grep -R -l -E 'TODO|FIXME|HACK' ./src   | xargs -n 1 -I {} sh -c 'echo "--- {} ---"; sed -n "1,5p" "{}"'
```

`-l`은 파일 경로만 출력하므로 후속 파이프라인과 결합하기 좋습니다.

### 삭제 자동화 예시: dry-run 포함

```bash
# dry-run
find /tmp/cache -type f -name '*.tmp' -mtime +3 -print

# execute
find /tmp/cache -type f -name '*.tmp' -mtime +3 -print0   | xargs -0 rm -f
```

dry-run 없이 바로 삭제하면 사고 가능성이 큽니다. 자동화 스크립트에도 같은 단계 분리를 유지해야 합니다.

### systemd 타이머와 연결해 정기 실행

```ini
# /etc/systemd/system/cache-cleanup.service
[Unit]
Description=Cleanup old temp cache files

[Service]
Type=oneshot
ExecStart=/usr/local/bin/cache-cleanup.sh

# /etc/systemd/system/cache-cleanup.timer
[Unit]
Description=Run cache cleanup daily

[Timer]
OnCalendar=*-*-* 03:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

`find/xargs` 스크립트를 타이머에 연결하면 수동 작업을 제거할 수 있습니다. 단, 첫 배포 전에는 반드시 dry-run 로그를 남겨 영향 범위를 확인해야 합니다.

### Bash 점검 스크립트 예시

```bash
#!/usr/bin/env bash
set -euo pipefail

target="/var/log/my-app"
pattern='ERROR|CRITICAL|timeout'

count=$(grep -R -E "$pattern" "$target" | wc -l)
printf '[INFO] pattern_count=%s
' "$count"

if [ "$count" -gt 200 ]; then
  printf '[WARN] high error volume detected
'
fi
```

이 스크립트처럼 기준값을 두면 단순 검색을 운영 알림으로 확장할 수 있습니다.

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


## 처음 질문으로 돌아가기

- **파일 내용 검색과 파일 위치 검색은 왜 다른 문제일까요?**
  - 본문의 기준은 grep, find, xargs — 검색의 삼총사를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`grep`, `find`, `xargs`는 어떤 순서로 연결하면 좋을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **검색 결과를 다음 명령으로 넘길 때 어떤 위험을 먼저 생각해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linux CLI 101 (1/10): CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): 파일과 디렉터리 다루기](./02-files-and-directories.md)
- [Linux CLI 101 (3/10): 권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- [Linux CLI 101 (4/10): cat, less, head, tail — 파일 내용 보기](./04-viewing-files.md)
- **grep, find, xargs — 검색의 삼총사 (현재 글)**
- pipe와 redirection (예정)
- 프로세스 확인과 종료 (예정)
- 환경변수와 PATH (예정)
- 간단한 shell script (예정)
- SSH와 원격 서버 접속 (예정)

<!-- toc:end -->

## 참고 자료

- [GNU grep Manual](https://www.gnu.org/software/grep/manual/)
- [GNU find Manual](https://www.gnu.org/software/findutils/manual/html_node/find_html/)
- [The Missing Semester - Data Wrangling](https://missing.csail.mit.edu/2020/data-wrangling/)
- [ripgrep - a faster grep alternative](https://github.com/BurntSushi/ripgrep)

- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko
Tags: Linux, grep, find, xargs, Search, CLI
