---
title: 간단한 shell script
series: linux-cli-101
episode: 9
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
tags:
- Linux
- Shell Script
- Bash
- Automation
- Scripting
- CLI
last_reviewed: '2026-05-12'
seo_description: Shell script로 반복 명령을 파일에 담아 자동화하는 기본을 정리합니다.
---

# 간단한 shell script

매일 아침 서버에 접속해서 같은 명령어 5개를 실행한다면, 그 5줄을 파일에 적어두고 한 번에 실행하면 됩니다. 그것이 shell script입니다.

이 글은 Linux CLI 101 시리즈의 9번째 글입니다.

## 이 글에서 다룰 문제

- 명령을 복붙하는 대신 스크립트 파일로 묶으면 무엇이 달라질까요?
- shebang, 실행 권한, 인자 처리는 왜 함께 배워야 할까요?
- 스크립트에서 변수와 조건문은 어디서 가장 자주 쓰일까요?
- 간단한 자동화라도 스크립트 형태로 남기는 이유는 무엇일까요?

> Shell script는 CLI 명령어를 레시피로 적어둔 파일입니다. 요리사가 레시피 없이 기억에 의존하면 실수하지만, 적어두면 누구든 같은 요리를 만들 수 있습니다.

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

<!-- toc:begin -->
## 시리즈 목차

- [CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [파일과 디렉터리 다루기](./02-files-and-directories.md)
- [권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- [cat, less, head, tail — 파일 내용 보기](./04-viewing-files.md)
- [grep, find, xargs — 검색의 삼총사](./05-grep-find-xargs.md)
- [pipe와 redirection](./06-pipe-and-redirection.md)
- [프로세스 확인과 종료](./07-process-management.md)
- [환경변수와 PATH](./08-environment-variables.md)
- **간단한 shell script (현재 글)**
- SSH와 원격 서버 접속 (예정)

<!-- toc:end -->

## 참고 자료

- [GNU Bash Manual - Shell Scripts](https://www.gnu.org/software/bash/manual/html_node/Shell-Scripts.html)
- [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- [ShellCheck - Shell script linter](https://www.shellcheck.net/)
- [The Missing Semester - Shell Scripting](https://missing.csail.mit.edu/2020/shell-tools/)

Tags: Linux, Shell Script, Bash, Automation, Scripting, CLI
