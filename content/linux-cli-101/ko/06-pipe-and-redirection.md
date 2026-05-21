---
title: "Linux CLI 101 (6/10): pipe와 redirection"
series: linux-cli-101
episode: 6
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
- pipe
- redirection
- stdin
- stdout
- CLI
last_reviewed: '2026-05-15'
seo_description: 표준 입출력 개념을 파악하고 파이프와 리다이렉션을 활용해 명령어를 연결하거나 파일로 저장하는 실무 텍스트 처리 기법을 단계별 예제로 실습합니다.
---

# Linux CLI 101 (6/10): pipe와 redirection

이 글은 Linux CLI 101 시리즈의 6번째 글입니다.

Linux의 철학은 "한 가지 일을 잘하는 작은 도구를 만들고, 조합하여 큰 일을 한다"입니다. `grep`은 검색만 하고, `sort`는 정렬만 하고, `wc`는 세기만 합니다. 이 도구들을 연결하는 접착제가 pipe와 redirection입니다.


![Linux CLI 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/06/06-01-mental-model.ko.png)
*Linux CLI 101 6장 흐름 개요*

## 먼저 던지는 질문

- 표준 입력, 표준 출력, 표준 오류는 왜 분리되어 있을까요?
- `|`, `>`, `>>`, `2>`는 각각 어떤 흐름을 만들까요?
- 중간 파일 없이 명령을 이어 붙이면 무엇이 좋아질까요?

## 머릿속에 먼저 그릴 그림

> 명령어는 수도꼭지이고, pipe(`|`)는 수도관입니다. 물(데이터)은 왼쪽에서 오른쪽으로 흐릅니다. redirection(`>`)은 물줄기를 수도관 대신 물통(파일)으로 보내는 것입니다.

```text
[Command A] --stdout--|--stdin--> [Command B] --stdout--> screen
                                                          |
[Command A] --stdout--> file.txt    (overwrite)           |
[Command A] --stdout-->> file.txt   (append)              |
[Command A] <--stdin-- file.txt     (file as input)
```

## 핵심 개념

| 기호 | 이름 | 역할 | 예시 |
|---|---|---|---|
| `\|` | pipe | 왼쪽 stdout → 오른쪽 stdin | `ls \| grep ".py"` |
| `>` | redirect (덮어쓰기) | stdout → 파일 (기존 내용 삭제) | `echo "hi" > out.txt` |
| `>>` | redirect (이어쓰기) | stdout → 파일 (기존 내용 유지) | `echo "hi" >> out.txt` |
| `<` | input redirect | 파일 → stdin | `sort < names.txt` |
| `2>` | stderr redirect | 에러만 파일로 | `cmd 2> error.log` |
| `2>&1` | stderr to stdout | 에러와 출력 합치기 | `cmd > all.log 2>&1` |

## 전과 후

**Before (중간 파일을 수동으로 만들 때)**

```bash
grep "ERROR" app.log > errors.txt
sort errors.txt > sorted.txt
uniq -c sorted.txt > counted.txt
sort -rn counted.txt > result.txt
cat result.txt
# 4 files created, cleanup needed
```

**After (pipe로 한 줄)**

```bash
grep "ERROR" app.log | sort | uniq -c | sort -rn
# No intermediate files, result printed immediately
```

## 단계별 실습

### 1단계. 실습 데이터 준비

```bash
cd ~/practice/linux-cli
cat > access.log << 'EOF'
192.168.1.10 GET /index.html 200
10.0.0.5 GET /api/users 200
192.168.1.10 GET /style.css 200
10.0.0.5 POST /api/login 401
172.16.0.1 GET /index.html 200
192.168.1.10 GET /api/data 500
10.0.0.5 GET /index.html 200
172.16.0.1 GET /api/users 200
EOF
```

### 2단계. 명령어 연결

```bash
cat access.log | grep "200"             # Only successful requests
cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn
# 3 192.168.1.10
# 3 10.0.0.5
# 2 172.16.0.1
```

### 3단계. 파일로 저장하기

```bash
grep "500" access.log > errors.txt      # Save only 500 errors
cat errors.txt
# 192.168.1.10 GET /api/data 500

echo "new error" >> errors.txt          # Append
cat errors.txt
# 192.168.1.10 GET /api/data 500
# new error
```

### 4단계. 오류 출력 분리

```bash
ls /nonexistent 2> error.log            # Errors only to file
cat error.log
# ls: cannot access '/nonexistent': No such file or directory

ls /tmp /nonexistent > out.txt 2> err.txt  # Separate output and errors
ls /tmp /nonexistent > all.txt 2>&1        # Both to same file
```

### 5단계. 실전 파이프라인

```bash
# Top 3 IPs by request count
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -3

# Extract only 500-error IPs
grep "500" access.log | awk '{print $1}' | sort -u

# Save to file AND print to screen (tee)
grep "200" access.log | tee success.log | wc -l
# 6 (screen output) + success.log also saved
```

## 이 코드에서 봐야 할 것

- pipe는 중간 파일 없이 데이터를 흘려보내므로 디스크를 절약합니다
- `>`는 파일을 덮어쓰므로 기존 내용이 사라집니다. `>>`는 안전합니다
- `2>&1`에서 `&`는 "파일 디스크립터"를 의미합니다. `&` 없이 `2>1`이면 "1"이라는 파일로 보냅니다
- `tee`는 데이터를 화면과 파일 양쪽으로 보내는 T자 수도관입니다

## 자주 하는 실수

### 실수 1. `>`와 `>>`를 혼동하여 데이터를 날린다

```bash
echo "important" > data.txt    # Overwrites — existing contents deleted
echo "important" >> data.txt   # Appends — existing contents preserved
```

중요한 파일에는 `>>`를 쓰거나 백업 후 `>`를 씁니다.

### 실수 2. 같은 파일에서 읽고 쓴다

```bash
sort file.txt > file.txt    # File becomes empty!
# Shell empties file.txt with > before sort reads it
sort file.txt > sorted.txt && mv sorted.txt file.txt  # Safe
```

### 실수 3. 오류 출력을 무시한다

스크립트에서 에러를 잡지 않으면 에러 메시지가 화면에 섞여 나옵니다. `2>/dev/null`로 버리거나 `2>error.log`로 따로 저장하세요.

### 실수 4. 불필요한 중간 명령을 둔다

```bash
cat file.txt | grep "pattern"    # Useless Use of Cat
grep "pattern" file.txt          # grep reads the file directly — more efficient
```

### 실수 5. 명령어 연결 순서를 잘못 잡는다

데이터를 먼저 필터링(grep)하고 나서 정렬(sort)하는 것이 효율적입니다. 정렬 후 필터링하면 불필요한 줄까지 정렬하므로 느립니다.

## 실무 적용

- **로그 분석**: `grep "ERROR" app.log | awk '{print $5}' | sort | uniq -c | sort -rn`으로 에러 유형별 빈도를 분석합니다
- **빌드 로그**: `make 2>&1 | tee build.log`로 빌드 로그를 화면과 파일에 동시 저장합니다
- **배치 처리**: `find . -name "*.csv" | xargs -I {} sh -c 'process.py {} > {}.out'`
- **cron 작업**: `script.sh > /var/log/cron.log 2>&1`로 정기 작업 로그를 남깁니다
- **데이터 전처리**: `cut -d',' -f2 data.csv | sort | uniq -c | sort -rn | head`

## 실무에서는 이렇게 생각한다

pipe는 Unix 철학의 핵심입니다. 작은 도구를 조합하면 전용 프로그램을 만들지 않아도 대부분의 텍스트 처리를 해결할 수 있습니다. Python 스크립트를 작성하기 전에 "이걸 pipe 한 줄로 할 수 있지 않을까?"를 먼저 생각하는 습관이 CLI 숙련자의 특징입니다.

반면 pipe 체인이 5단계 이상 복잡해지면, 유지보수성이 떨어집니다. 이 시점에서는 Python이나 셸 스크립트로 옮기는 것이 맞습니다. pipe는 "일회성 분석"에 최적이고, "반복적으로 실행하는 로직"은 스크립트로 남기는 것이 팀 협업에 유리합니다.

## 문제가 생기면 먼저 이렇게 확인하세요

- 파이프라인 결과가 비어 있으면 왼쪽부터 한 단계씩 떼어 내세요. `grep "ERROR" app.log` → `grep "ERROR" app.log | sort`처럼 확인하면 어느 단계에서 데이터가 사라지는지 바로 보입니다.
- 원본 파일이 갑자기 비었다면 `sort file.txt > file.txt`처럼 같은 파일을 읽고 쓴 흔적이 있는지 먼저 봐야 합니다. 이런 경우는 중간 파일을 쓰거나 `sponge` 같은 도구가 필요합니다.
- 에러 메시지가 안 보이거나 로그 파일에 안 남으면 stdout과 stderr를 분리했는지 확인하세요. 빌드 로그처럼 실패 원인을 남겨야 할 때는 `2>&1 | tee build.log`가 기본값에 가깝습니다.
- `>`를 써서 덮어쓸지 `>>`로 이어쓸지 헷갈리면 먼저 임시 파일에 저장해 비교하세요. 운영 로그나 보고서 파일은 한 번 덮어쓰면 되돌리기 어렵습니다.

## 체크리스트

- [ ] `|`로 두 명령어의 출력/입력을 연결할 수 있다
- [ ] `>`(덮어쓰기)와 `>>`(이어쓰기)의 차이를 안다
- [ ] stdout(1)과 stderr(2)가 분리된 이유를 설명할 수 있다
- [ ] `2>&1`로 에러와 출력을 합칠 수 있다
- [ ] `tee`로 화면 출력과 파일 저장을 동시에 할 수 있다

## 연습 문제

1. 텍스트 파일 하나를 만든 뒤 `cat`, `grep`, `sort`, `uniq -c`를 파이프로 연결해 빈도표를 만들어 보세요.
2. `>`, `>>`, `2>`를 각각 한 번씩 써 보고 어떤 파일이 어떻게 달라지는지 직접 확인해 보세요.
3. `tee`가 화면 출력과 파일 저장을 동시에 처리할 때 왜 유용한지 배포 로그 예시와 함께 설명해 보세요.

## 정리와 다음 글

- pipe(`|`)는 명령어의 stdout을 다음 명령어의 stdin으로 연결합니다.
- `>`는 덮어쓰기, `>>`는 이어쓰기로 출력을 파일에 저장합니다.
- stdout(1)과 stderr(2)는 독립적이며, `2>&1`로 합칠 수 있습니다.
- `tee`는 화면과 파일에 동시에 출력합니다.
- pipe 체인이 복잡해지면 스크립트로 옮기는 것이 유지보수에 유리합니다.

다음 글에서는 **프로세스 확인과 종료** — `ps`, `top`, `kill`, 백그라운드 실행을 다룹니다.


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

## 실무 시나리오: 파이프와 리다이렉션으로 분석 흐름 고정하기

파이프와 리다이렉션은 CLI 자동화의 중심입니다. 핵심은 출력 포맷을 예쁘게 만드는 것이 아니라, **다음 단계가 소비할 수 있는 형태로 변환**하는 것입니다.

### 표준 스트림을 먼저 분리해 이해하기

```bash
python3 app.py > /tmp/app.out 2> /tmp/app.err

# 예상 결과
# /tmp/app.out : 정상 출력
# /tmp/app.err : 오류 출력
```

문제 분석에서 stdout과 stderr를 분리하면 원인 추적이 빨라집니다.

### tee로 화면 출력과 파일 저장 동시 처리

```bash
journalctl -u my-api --since '20 min ago'   | grep -E 'ERROR|CRITICAL|timeout'   | tee /tmp/my-api-errors.txt
```

`tee`는 "지금 보고" + "나중에 재사용"을 동시에 만족합니다.

### 파이프 체인 설계 예시: 접근 로그 요약

```bash
cat /var/log/nginx/access.log   | awk '{print $1, $7, $9}'   | grep -E ' 5[0-9]{2}$'   | sort   | uniq -c   | sort -nr   | head -n 20

# 예상 출력
#   87 10.10.1.2 /api/pay 502
#   41 10.10.1.5 /api/order 504
```

이 흐름은 "원문 로그"를 "우선 조치 대상 목록"으로 바꾸는 전형적인 패턴입니다.

### 여기문서와 리다이렉션으로 설정 파일 생성

```bash
cat > /tmp/my-api.env << 'EOF'
APP_ENV=production
LOG_LEVEL=INFO
WORKER_COUNT=4
EOF

cat /tmp/my-api.env
```

자동화 스크립트에서 설정 파일을 만들 때 유용하지만, 비밀값은 평문으로 남지 않도록 별도 비밀 관리 체계를 사용해야 합니다.

### stderr 합치기와 분리 전략

```bash
# stdout + stderr 모두 파일로
./deploy.sh > /tmp/deploy.log 2>&1

# stderr만 별도 파일
./deploy.sh 2> /tmp/deploy.err
```

운영에서는 "실패 로그만 모아 보기"가 중요하므로 stderr 파일 분리가 자주 쓰입니다.

### xargs와 파이프 결합으로 대량 실행

```bash
printf '%s
' api worker scheduler   | xargs -n 1 -I {} sh -c 'systemctl status my-{} --no-pager | sed -n "1,5p"'
```

서비스 다수를 빠르게 점검할 때 효과적입니다.

### systemd 로그와 리다이렉션 결합

```bash
journalctl -u my-api --since '1 hour ago' --no-pager   > /tmp/my-api-journal.txt

grep -E 'ERROR|CRITICAL|timeout|OOM' /tmp/my-api-journal.txt
```

실시간 조회만으로 끝내지 않고 파일로 남기면 팀 리뷰와 회고에 재사용할 수 있습니다.

### Bash 파이프라인 스크립트 예시

```bash
#!/usr/bin/env bash
set -euo pipefail

service="my-api"
out="/tmp/${service}-incident-$(date +%Y%m%d-%H%M%S).log"

journalctl -u "$service" --since '30 min ago' --no-pager   | grep -E 'ERROR|CRITICAL|timeout|OOM'   | tee "$out"

printf '[INFO] saved=%s
' "$out"
```

이런 스크립트는 장애 시 "누가 실행해도 같은 결과"를 만들기 때문에 운영 품질을 안정화합니다.

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


## 처음 질문으로 돌아가기

- **표준 입력, 표준 출력, 표준 오류는 왜 분리되어 있을까요?**
  - 본문의 기준은 pipe와 redirection를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`|`, `>`, `>>`, `2>`는 각각 어떤 흐름을 만들까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **중간 파일 없이 명령을 이어 붙이면 무엇이 좋아질까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linux CLI 101 (1/10): CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): 파일과 디렉터리 다루기](./02-files-and-directories.md)
- [Linux CLI 101 (3/10): 권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- [Linux CLI 101 (4/10): cat, less, head, tail — 파일 내용 보기](./04-viewing-files.md)
- [Linux CLI 101 (5/10): grep, find, xargs — 검색의 삼총사](./05-grep-find-xargs.md)
- **pipe와 redirection (현재 글)**
- 프로세스 확인과 종료 (예정)
- 환경변수와 PATH (예정)
- 간단한 shell script (예정)
- SSH와 원격 서버 접속 (예정)

<!-- toc:end -->

## 참고 자료

- [GNU Bash Manual - Redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html)
- [The Missing Semester - Data Wrangling](https://missing.csail.mit.edu/2020/data-wrangling/)
- [Linux Documentation - I/O Redirection](https://tldp.org/LDP/abs/html/io-redirection.html)
- [Useless Use of Cat Award](https://porkmail.org/era/unix/award)

- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko
Tags: Linux, pipe, redirection, stdin, stdout, CLI
