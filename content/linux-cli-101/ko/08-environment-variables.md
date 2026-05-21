---
title: "Linux CLI 101 (8/10): 환경변수와 PATH"
series: linux-cli-101
episode: 8
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
- Environment Variable
- PATH
- bashrc
- Shell
- Configuration
last_reviewed: '2026-05-12'
seo_description: 환경변수와 PATH가 명령 실행과 설정 전달에 쓰이는 방식을 정리합니다.
---

# Linux CLI 101 (8/10): 환경변수와 PATH

이 글은 Linux CLI 101 시리즈의 8번째 글입니다.

`python`을 입력하면 Shell이 Python 실행 파일을 찾아서 실행합니다. 어떻게 찾을까요? 모든 디렉터리를 뒤지는 것이 아니라, PATH에 등록된 디렉터리만 순서대로 확인합니다. PATH에 없으면 "command not found"입니다.


## 먼저 던지는 질문

- 환경변수는 어떤 방식으로 프로세스에 전달될까요?
- `export`와 로컬 Shell 변수는 무엇이 다를까요?
- `PATH`는 명령 실행에서 어떤 검색 순서를 만들까요?

## 큰 그림

![Linux CLI 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/08/08-01-big-picture.ko.png)

*Linux CLI 101 8장 흐름 개요*

## 머릿속에 먼저 그릴 그림

> 환경변수는 프로세스에 붙은 이름표이고, PATH는 Shell이 명령어를 찾아다니는 지도입니다.

택배 기사가 배달할 때 주소록(PATH)을 순서대로 확인합니다. 주소록에 없는 곳은 가지 않습니다. 새 가게가 생기면 주소록에 추가해야 기사가 찾아갑니다.

```text
$ python
Shell searches PATH in order:
  /usr/local/bin/python  -> not found
  /usr/bin/python         -> found! -> execute
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| 환경변수 | 프로세스에 전달되는 key=value 쌍 | `HOME=/home/user` |
| PATH | 명령어 검색 경로 목록 (`:` 구분) | `/usr/local/bin:/usr/bin:/bin` |
| export | 자식 프로세스에도 변수를 전달 | `export API_KEY=abc123` |
| .bashrc | 대화형 bash shell 시작 시 실행 | `~/.bashrc` |
| .bash_profile | 로그인 shell 시작 시 실행 | `~/.bash_profile` |

## 전과 후

**Before (PATH를 모를 때)**

```bash
pip install httpie
http GET https://api.example.com
# bash: http: command not found
# "Why doesn't it work? I just installed it..."
```

**After (PATH를 이해할 때)**

```bash
pip install httpie
which http || pip show httpie | grep Location
# Location: /home/user/.local/lib/python3.11/site-packages
# -> check if ~/.local/bin is in PATH
echo $PATH | tr ':' '\n' | grep local
# If /home/user/.local/bin is missing:
export PATH="$HOME/.local/bin:$PATH"
http GET https://api.example.com   # Works
```

## 단계별 실습

### 1단계. 환경변수 확인

```bash
echo $HOME                    # Home directory
echo $USER                    # Current user
echo $SHELL                   # Current shell
echo $PATH                    # Command search paths

env                           # Print all environment variables
env | grep -i python          # Python-related variables only
```

### 2단계. 변수 설정과 내보내기

```bash
MY_VAR="hello"                # Shell variable (not passed to children)
echo $MY_VAR                  # hello

bash -c 'echo $MY_VAR'       # (empty) — not available in child process

export MY_VAR                 # export passes it to children
bash -c 'echo $MY_VAR'       # hello

export DB_HOST="localhost"    # Declare and export at once
```

### 3단계. 실행 경로 수정

```bash
echo $PATH | tr ':' '\n'     # View PATH one entry per line

# Temporary addition (current session only)
export PATH="$HOME/mytools:$PATH"

# Check command location
which python
which ls
```

### 4단계. 셸 시작 파일에 영구 설정

```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export EDITOR=vim' >> ~/.bashrc

source ~/.bashrc             # Apply immediately (or open a new terminal)
echo $EDITOR
# vim
```

### 5단계. 환경 파일 패턴

```bash
cat > ~/practice/linux-cli/.env << 'EOF'
DB_HOST=localhost
DB_PORT=5432
DB_NAME=myapp
API_KEY=secret-key-123
EOF

# Load .env file in Shell
set -a                        # Auto-export subsequent variables
source ~/practice/linux-cli/.env
set +a
echo $DB_HOST                 # localhost
```

## 이 코드에서 봐야 할 것

- `export` 없이 설정한 변수는 현재 Shell에서만 유효하고 자식 프로세스에 전달되지 않습니다
- PATH는 `:` 구분자로 여러 경로를 나열하며, 왼쪽이 우선합니다
- `source ~/.bashrc`는 현재 Shell에서 파일을 실행합니다. `.`도 같은 의미입니다
- `.env` 파일은 Git에 커밋하면 안 됩니다 (API 키 등 민감 정보 포함)

## 자주 하는 실수

### 실수 1. 실행 경로를 덮어쓴다

```bash
export PATH="/my/new/path"              # Entire existing PATH is gone!
export PATH="/my/new/path:$PATH"        # Appends to existing PATH — safe
```

### 실수 2. 시작 파일 역할을 혼동한다

로그인 셸(SSH 접속)은 `.bash_profile`을 읽고, 비로그인 대화형 셸(터미널 앱)은 `.bashrc`를 읽습니다. 보통 `.bash_profile`에서 `.bashrc`를 source하여 통일합니다.

### 실수 3. 변수 참조 시 중괄호를 생략한다

```bash
echo "$HOME_backup"           # Looks for a variable named HOME_backup
echo "${HOME}_backup"         # HOME variable + "_backup" string
```

### 실수 4. 환경 파일을 저장소에 커밋한다

API 키, 비밀번호가 포함된 `.env`가 공개 저장소에 올라가면 보안 사고입니다. `.gitignore`에 반드시 `.env`를 추가하세요.

### 실수 5. 내보내기를 빼먹고 변수 전달이 안 된다고 생각한다

Python 스크립트에서 `os.environ["MY_VAR"]`를 읽으려면, Shell에서 `export`로 내보내야 합니다. `MY_VAR=hello`만으로는 자식 프로세스인 Python이 볼 수 없습니다.

## 실무 적용

- **12-Factor App**: 설정을 코드가 아닌 환경변수로 관리합니다 (DB 접속 정보, API 키 등)
- **가상환경 활성화**: `source venv/bin/activate`는 PATH 앞에 venv의 bin/을 추가합니다
- **CI/CD 변수**: GitHub Actions의 `env:`는 환경변수를 설정하는 것입니다
- **Docker**: `docker run -e DB_HOST=db`로 컨테이너에 환경변수를 전달합니다
- 디버깅: `env | sort`로 현재 환경을 덤프하여 문제를 진단합니다

## 실무에서는 이렇게 생각한다

환경변수는 "코드 밖의 설정"을 관리하는 표준 방법입니다. 같은 코드를 개발/스테이징/프로덕션에서 돌릴 때, 코드를 바꾸는 대신 `DB_HOST` 환경변수만 바꾸면 됩니다. 이것이 12-Factor App 방법론의 핵심이며, Docker, Kubernetes 환경에서 설정을 주입하는 기본 방식입니다.

반면 환경변수가 너무 많아지면 관리가 어려워집니다. 이때는 `.env` 파일을 환경별로 관리하거나, AWS Parameter Store, HashiCorp Vault 같은 시크릿 관리 도구로 넘어갑니다. 하지만 모든 것의 출발점은 `export`와 `$PATH`를 이해하는 것입니다.

## 체크리스트

- [ ] `echo $PATH`의 출력을 읽고 명령어 검색 순서를 설명할 수 있다
- [ ] `export`와 단순 변수 대입의 차이를 안다
- [ ] `.bashrc`에 PATH를 영구적으로 추가할 수 있다
- [ ] `.env` 파일을 만들고 `source`로 로드할 수 있다
- [ ] `.env` 파일을 `.gitignore`에 추가하는 이유를 안다

## 연습 문제

1. `MY_NAME=linux-cli`와 `export MY_NAME=linux-cli`를 각각 실행한 뒤 하위 Shell에서 보이는 차이를 확인해 보세요.
2. `echo $PATH` 결과를 줄마다 나눠 보고, 자주 쓰는 명령이 어느 디렉터리에서 오는지 `which`로 확인해 보세요.
3. 가상의 `.env` 파일을 하나 만들고 Shell에서 읽어 오는 흐름을 직접 연습해 보세요.

## 정리와 다음 글

- 환경변수는 프로세스에 전달되는 key=value 설정이며 `export`로 자식에게 상속됩니다.
- PATH는 Shell이 명령어를 찾는 디렉터리 목록이며 `:` 구분, 왼쪽 우선입니다.
- `.bashrc`에 설정을 추가하면 새 Shell마다 자동 적용됩니다.
- `.env` 파일은 애플리케이션 설정 관리에 유용하지만 Git에 커밋하면 안 됩니다.
- `export`를 빼먹으면 자식 프로세스(Python, Docker 등)가 변수를 볼 수 없습니다.

다음 글에서는 **간단한 shell script** — 반복 작업을 자동화하는 스크립트 작성법을 다룹니다.


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

## 실무 시나리오: 환경변수를 배포 계약으로 관리하기

환경변수는 "값을 저장하는 기술"이 아니라 배포 계약입니다. 코드와 환경의 경계를 명확히 하면 동일한 바이너리를 개발·스테이징·운영에서 재사용할 수 있습니다. 반대로 환경변수 관리가 느슨하면 배포마다 다른 동작이 나와 장애 원인이 됩니다.

### 필수 변수 목록을 문서화하기

```bash
cat > /opt/my-api/current/.env.example << 'EOF'
APP_ENV=production
APP_PORT=8080
DB_HOST=127.0.0.1
DB_PORT=5432
LOG_LEVEL=INFO
EOF
```

`.env.example`은 실제 비밀값을 담지 않고, 필요한 키 목록과 형식을 공유하는 문서 역할을 합니다.

### 현재 셸 변수 확인과 필터링

```bash
env | sort | grep -E '^(APP_|DB_|LOG_)'

# 예상 출력
# APP_ENV=production
# APP_PORT=8080
# DB_HOST=10.0.2.7
# DB_PORT=5432
# LOG_LEVEL=INFO
```

정규식 앵커(`^`)를 사용하면 접두사 기준으로 안전하게 추출할 수 있습니다.

### 일시 설정과 영구 설정 구분

```bash
# 현재 세션에서만 유효
export APP_ENV=staging

# 새 셸에도 유지
printf '
export APP_ENV=staging
' >> ~/.bashrc
source ~/.bashrc
```

운영 자동화에서는 세션 의존 설정보다 systemd `EnvironmentFile`이나 배포 시스템 변수 주입을 선호합니다.

### systemd 유닛에서 환경변수 주입

```ini
# /etc/systemd/system/my-api.service
[Service]
Environment="APP_ENV=production"
Environment="LOG_LEVEL=INFO"
EnvironmentFile=/opt/my-api/current/conf/app.env
ExecStart=/opt/my-api/current/bin/start.sh
```

```bash
systemctl daemon-reload
systemctl restart my-api
systemctl show my-api --property=Environment
```

서비스 단위에서 설정하면 로그인 셸 상태와 무관하게 일관된 실행 환경을 유지할 수 있습니다.

### 비밀값 노출 방지

```bash
# 잘못된 예시: 비밀값이 히스토리에 남음
# export DB_PASSWORD=super-secret

# 권장: 보안 저장소/권한 파일/CI secret 사용
chmod 600 /opt/my-api/current/conf/app.env
```

환경변수는 편하지만, 프로세스 목록과 크래시 덤프에 노출될 수 있습니다. 민감 정보는 주입 경로와 권한을 함께 설계해야 합니다.

### Bash에서 기본값/필수값 처리

```bash
#!/usr/bin/env bash
set -euo pipefail

: "${APP_ENV:=development}"
: "${APP_PORT:=8000}"
: "${DB_HOST:?DB_HOST is required}"

printf 'APP_ENV=%s APP_PORT=%s DB_HOST=%s
' "$APP_ENV" "$APP_PORT" "$DB_HOST"
```

`${VAR:?message}` 패턴은 필수 변수 누락을 즉시 실패시켜, 조용한 오동작을 방지합니다.

### 로그에서 변수 문제 추적하기

```bash
journalctl -u my-api -n 100 --no-pager   | grep -E 'missing env|invalid config|DB_HOST|APP_PORT'
```

환경변수 문제는 보통 시작 직후 로그에 힌트가 남습니다. 배포 실패 분석에서 가장 먼저 확인할 가치가 큽니다.

### 환경별 템플릿 비교

```bash
diff -u conf/app.env.staging conf/app.env.production

# 예상 출력 일부
# -APP_ENV=staging
# +APP_ENV=production
# -LOG_LEVEL=DEBUG
# +LOG_LEVEL=INFO
```

명시적 diff는 "무엇이 달라서 동작이 달라졌는지"를 빠르게 보여줍니다.

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

## 처음 질문으로 돌아가기

- **환경변수는 어떤 방식으로 프로세스에 전달될까요?**
  - 본문의 기준은 환경변수와 PATH를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **`export`와 로컬 Shell 변수는 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`PATH`는 명령 실행에서 어떤 검색 순서를 만들까요?**
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
- **환경변수와 PATH (현재 글)**
- 간단한 shell script (예정)
- SSH와 원격 서버 접속 (예정)

<!-- toc:end -->

## 참고 자료

- [GNU Bash Manual - Shell Variables](https://www.gnu.org/software/bash/manual/html_node/Shell-Variables.html)
- [The Twelve-Factor App - Config](https://12factor.net/config)
- [Linux man page - environ](https://man7.org/linux/man-pages/man7/environ.7.html)
- [dotenv pattern - Best practices](https://github.com/motdotla/dotenv)

- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko
Tags: Linux, Environment Variable, PATH, bashrc, Shell, Configuration
