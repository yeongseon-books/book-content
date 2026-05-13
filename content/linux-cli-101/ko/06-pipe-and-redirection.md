---
title: pipe와 redirection
series: linux-cli-101
episode: 6
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
- pipe
- redirection
- stdin
- stdout
- CLI
last_reviewed: '2026-05-12'
seo_description: 파이프와 리다이렉션으로 명령 출력을 연결하고 저장하는 법을 정리합니다.
---

# pipe와 redirection

Linux의 철학은 "한 가지 일을 잘하는 작은 도구를 만들고, 조합하여 큰 일을 한다"입니다. `grep`은 검색만 하고, `sort`는 정렬만 하고, `wc`는 세기만 합니다. 이 도구들을 연결하는 접착제가 pipe와 redirection입니다.

이 글은 Linux CLI 101 시리즈의 6번째 글입니다.

## 이 글에서 다룰 문제

- 표준 입력, 표준 출력, 표준 오류는 왜 분리되어 있을까요?
- `|`, `>`, `>>`, `2>`는 각각 어떤 흐름을 만들까요?
- 중간 파일 없이 명령을 이어 붙이면 무엇이 좋아질까요?
- 로그 분석에서 파이프를 읽는 감각이 왜 중요한가요?

> 명령어는 수도꼭지이고, pipe(`|`)는 수도관입니다. 물(데이터)은 왼쪽에서 오른쪽으로 흐릅니다. redirection(`>`)은 물줄기를 수도관 대신 물통(파일)으로 보내는 것입니다.

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

<!-- toc:begin -->
## 시리즈 목차

- [CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [파일과 디렉터리 다루기](./02-files-and-directories.md)
- [권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- [cat, less, head, tail — 파일 내용 보기](./04-viewing-files.md)
- [grep, find, xargs — 검색의 삼총사](./05-grep-find-xargs.md)
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

Tags: Linux, pipe, redirection, stdin, stdout, CLI
