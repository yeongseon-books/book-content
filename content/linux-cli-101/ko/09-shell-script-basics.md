---
title: "Linux CLI 101 (9/10): 간단한 shell script"
series: linux-cli-101
episode: 9
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
- Shell Script
- Bash
- Automation
- Scripting
- CLI
last_reviewed: '2026-05-15'
seo_description: Shell script로 반복 명령을 파일에 담아 자동화하는 기본을 정리합니다.
---

# Linux CLI 101 (9/10): 간단한 shell script

매일 아침 서버에 접속해서 같은 명령어 5개를 실행한다면, 그 5줄을 파일에 적어두고 한 번에 실행하면 됩니다. 그것이 shell script입니다.

이 글은 Linux CLI 101 시리즈의 9번째 글입니다.

## 먼저 던지는 질문

- 명령을 복붙하는 대신 스크립트 파일로 묶으면 무엇이 달라질까요?
- shebang, 실행 권한, 인자 처리는 왜 함께 배워야 할까요?
- 스크립트에서 변수와 조건문은 어디서 가장 자주 쓰일까요?

## 큰 그림

![Linux CLI 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/09/09-01-big-picture.ko.png)

*Linux CLI 101 9장 흐름 개요*

## 머릿속에 먼저 그릴 그림

> Shell script는 CLI 명령어를 레시피로 적어둔 파일입니다. 요리사가 레시피 없이 기억에 의존하면 실수하지만, 적어두면 누구든 같은 요리를 만들 수 있습니다.

```text
Manual execution              Shell script
─────────────                 ──────────────
$ git pull                    #!/bin/bash
$ python -m pytest            git pull
$ docker build -t app .       python -m pytest
$ docker push app             docker build -t app .
                              docker push app
→ Type 4 lines every time     → ./deploy.sh once
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| shebang | 스크립트를 실행할 인터프리터 지정 | `#!/bin/bash` |
| `$1`, `$2` | 스크립트에 전달된 인자 | `./script.sh hello` → `$1`=hello |
| `$#` | 인자 개수 | 2개 전달 시 `$#`=2 |
| `$?` | 직전 명령어의 종료 코드 | 0=성공, 그 외=실패 |
| `set -e` | 에러 발생 시 즉시 중단 | 스크립트 첫 줄에 권장 |

## 전과 후

**Before (수동 배포)**

```text
1. SSH in
2. cd /opt/app
3. git pull
4. pip install -r requirements.txt
5. sudo systemctl restart app
# → Skipped step 3, old version keeps running
```

**After (스크립트 배포)**

```bash
#!/bin/bash
set -e
cd /opt/app
git pull
pip install -r requirements.txt
sudo systemctl restart app
echo "Deploy complete at $(date)"
```

## 단계별 실습

### 1단계. 첫 스크립트 만들기

```bash
cd ~/practice/linux-cli
cat > hello.sh << 'EOF'
#!/bin/bash
echo "Hello, $(whoami)!"
echo "Today is $(date +%Y-%m-%d)"
echo "Current directory: $(pwd)"
EOF

chmod u+x hello.sh
./hello.sh
# Hello, user!
# Today is 2026-05-04
# Current directory: /home/user/practice/linux-cli
```

### 2단계. 변수와 인자

```bash
cat > greet.sh << 'EOF'
#!/bin/bash
NAME=${1:-"World"}          # First argument, default "World"
COUNT=${2:-1}               # Second argument, default 1

echo "Arguments count: $#"
for i in $(seq 1 "$COUNT"); do
    echo "[$i] Hello, $NAME!"
done
EOF

chmod u+x greet.sh
./greet.sh                  # Hello, World! (1 time)
./greet.sh Alice 3          # Hello, Alice! (3 times)
```

### 3단계. 조건문

```bash
cat > check-file.sh << 'EOF'
#!/bin/bash
set -e

FILE=${1:?"Usage: $0 <filename>"}

if [ -f "$FILE" ]; then
    echo "File exists: $FILE"
    echo "Size: $(wc -c < "$FILE") bytes"
    echo "Lines: $(wc -l < "$FILE")"
elif [ -d "$FILE" ]; then
    echo "Directory exists: $FILE"
    echo "Contents: $(ls "$FILE" | wc -l) items"
else
    echo "Not found: $FILE"
    exit 1
fi
EOF

chmod u+x check-file.sh
./check-file.sh hello.sh         # File exists: hello.sh
./check-file.sh /tmp              # Directory exists: /tmp
./check-file.sh nonexistent       # Not found: nonexistent
```

### 4단계. 반복문

```bash
cat > backup.sh << 'EOF'
#!/bin/bash
set -e

BACKUP_DIR="/tmp/backup-$(date +%Y%m%d)"
mkdir -p "$BACKUP_DIR"

for file in *.sh; do
    if [ -f "$file" ]; then
        cp "$file" "$BACKUP_DIR/"
        echo "Backed up: $file"
    fi
done

echo "All scripts backed up to $BACKUP_DIR"
ls "$BACKUP_DIR"
EOF

chmod u+x backup.sh
./backup.sh
# Backed up: hello.sh
# Backed up: greet.sh
# ...
```

### 5단계. 종료 코드 활용

```bash
cat > deploy-check.sh << 'EOF'
#!/bin/bash
set -e

echo "Running tests..."
python -m pytest tests/ 2>/dev/null
if [ $? -eq 0 ]; then
    echo "Tests passed. Proceeding with deploy."
else
    echo "Tests failed. Aborting deploy."
    exit 1
fi

echo "Building..."
echo "Deploying..."
echo "Done!"
EOF

chmod u+x deploy-check.sh
```

## 이 코드에서 봐야 할 것

- `#!/bin/bash`가 없으면 시스템의 기본 Shell로 실행되어 문법 차이로 오류가 날 수 있습니다
- `set -e`는 어떤 명령이든 실패하면 즉시 스크립트를 중단합니다. 실수를 방지하는 안전장치입니다
- `${1:-"default"}`는 인자가 없을 때 기본값을 쓰는 패턴이고, `${1:?"message"}`는 필수 인자가 없으면 에러를 발생시킵니다
- `$(command)`는 명령어의 출력을 문자열로 캡처합니다

## 자주 하는 실수

### 실수 1. 해시뱅을 빼먹는다

```bash
# Without a shebang, sh may run instead of bash
# sh lacks bash features like arrays and [[ ]], causing errors
```

항상 `#!/bin/bash`를 첫 줄에 씁니다.

### 실수 2. 변수에 공백을 넣고 따옴표를 안 쓴다

```bash
FILE=my file.txt              # Error: tries to execute "my"
FILE="my file.txt"            # Correct

rm $FILE                      # Tries to delete "my" and "file.txt" separately
rm "$FILE"                    # Deletes "my file.txt" as one file
```

변수를 쓸 때는 항상 `"$VAR"`로 따옴표를 감쌉니다.

### 실수 3. 중간 오류를 무시한 채 실행한다

`set -e`가 없으면 중간 명령이 실패해도 다음 줄이 계속 실행됩니다. 테스트가 실패했는데 배포가 진행되는 사고가 발생합니다.

### 실수 4. 절대 경로를 쓰지 않는다

스크립트 안에서 `cd` 없이 상대 경로를 쓰면, 스크립트를 어디서 실행하느냐에 따라 결과가 달라집니다. 중요한 경로는 절대 경로로 쓰거나 `cd "$(dirname "$0")"` 패턴을 씁니다.

### 실수 5. 오류 메시지를 표준 오류로 보내지 않는다

```bash
echo "Error: file not found" >&2   # stderr — correct
echo "Error: file not found"       # stdout — gets mixed in pipes
```

## 실무 적용

- **배포 스크립트**: 테스트 → 빌드 → 백업 → 배포 → 헬스체크를 한 파일로 관리합니다
- **CI/CD**: GitHub Actions의 `run:` 블록은 shell script입니다
- **cron 작업**: 정기적인 백업, 로그 정리를 스크립트로 자동화합니다
- **개발 환경 설정**: 새 팀원이 `./setup.sh` 하나로 환경을 구축합니다
- **데이터 파이프라인**: CSV 전처리, 파일 이동 등 간단한 ETL을 스크립트로 합니다

## 실무에서는 이렇게 생각한다

Shell script의 강점은 **CLI 명령어를 그대로 쓸 수 있다**는 것입니다. `git`, `docker`, `kubectl` 같은 CLI 도구를 조합하는 글루 코드(glue code)로 최적입니다. Python으로 `subprocess.run(["git", "pull"])`을 쓰는 것보다 `git pull` 한 줄이 명확합니다.

반면 복잡한 로직(JSON 파싱, API 호출, 에러 핸들링)은 Python이 훨씬 낫습니다. 기준은 "이 스크립트가 50줄을 넘을까?"입니다. 넘을 것 같으면 Python으로 쓰세요. Shell script는 "50줄 이하의 명령어 조합"에서 가장 빛납니다.

## 문제가 생기면 먼저 이렇게 확인하세요

- 스크립트가 `Permission denied`로 시작조차 안 되면 `chmod u+x script.sh`와 shebang 존재 여부를 먼저 확인하세요. 실행 권한과 인터프리터 지정이 빠지면 내용이 맞아도 실행되지 않습니다.
- Bash 문법이 맞는데도 이상한 오류가 나면 어떤 셸로 실행됐는지 보세요. `sh script.sh`로 실행하면 Bash 전용 문법이 깨질 수 있으니 `./script.sh` 또는 `bash script.sh`로 재현해 보는 편이 정확합니다.
- 특정 파일을 못 찾는다면 현재 작업 디렉터리부터 확인해야 합니다. `pwd`, `dirname "$0"`, `set -x`를 조합하면 상대 경로 실수를 빠르게 찾을 수 있습니다.
- 배포 스크립트가 중간 실패 후에도 계속 진행되면 `set -e`와 명시적 종료 코드 처리가 있는지 보세요. 자동화에서 가장 위험한 실패는 조용히 지나가는 실패입니다.

## 체크리스트

- [ ] shebang(`#!/bin/bash`)의 역할을 알고 항상 추가한다
- [ ] `$1`, `$#`, `$?`로 인자와 종료 코드를 다룰 수 있다
- [ ] `if/else`와 `for` 루프를 Bash 문법으로 작성할 수 있다
- [ ] `set -e`를 써서 에러 시 스크립트를 중단할 수 있다
- [ ] 변수를 쓸 때 항상 따옴표(`"$VAR"`)를 감싸는 습관이 있다

## 연습 문제

1. `hello.sh` 스크립트를 만들고 인자 하나를 받아 인사하도록 수정해 보세요.
2. 백업 대상 파일 목록을 받아 반복문으로 복사하는 작은 스크립트를 작성해 보세요.
3. shebang이 없을 때와 있을 때 실행 결과가 왜 달라질 수 있는지 `bash`와 `sh` 관점에서 설명해 보세요.

## 정리와 다음 글

- Shell script는 CLI 명령어를 파일에 적어 자동화하는 가장 직접적인 방법입니다.
- `#!/bin/bash`와 `set -e`는 모든 스크립트의 필수 시작점입니다.
- `$1`, `$#`, `$?`로 인자와 종료 코드를 다루고, `if/for`로 흐름을 제어합니다.
- 변수는 항상 따옴표로 감싸고, 에러는 stderr로 보냅니다.
- 50줄 이하의 명령어 조합에 최적이며, 복잡해지면 Python으로 넘어갑니다.

다음 글에서는 **SSH와 원격 서버 접속** — 키 기반 인증, scp, ssh config를 다룹니다.


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

## 처음 질문으로 돌아가기

- **명령을 복붙하는 대신 스크립트 파일로 묶으면 무엇이 달라질까요?**
  - 본문의 기준은 간단한 shell script를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **shebang, 실행 권한, 인자 처리는 왜 함께 배워야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **스크립트에서 변수와 조건문은 어디서 가장 자주 쓰일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linux CLI 101 (1/10): CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): 파일과 디렉터리 다루기](./02-files-and-directories.md)
- [Linux CLI 101 (3/10): 권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- [Linux CLI 101 (4/10): cat, less, head, tail — 파일 내용 보기](./04-viewing-files.md)
- [Linux CLI 101 (5/10): grep, find, xargs — 검색의 삼총사](./05-grep-find-xargs.md)
- [Linux CLI 101 (6/10): pipe와 redirection](./06-pipe-and-redirection.md)
- [Linux CLI 101 (7/10): 프로세스 확인과 종료](./07-process-management.md)
- [Linux CLI 101 (8/10): 환경변수와 PATH](./08-environment-variables.md)
- **간단한 shell script (현재 글)**
- SSH와 원격 서버 접속 (예정)

<!-- toc:end -->

## 참고 자료

- [GNU Bash Manual - Shell Scripts](https://www.gnu.org/software/bash/manual/html_node/Shell-Scripts.html)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- [ShellCheck - Shell script linter](https://www.shellcheck.net/)
- [The Missing Semester - Shell Scripting](https://missing.csail.mit.edu/2020/shell-tools/)

Tags: Linux, Shell Script, Bash, Automation, Scripting, CLI
