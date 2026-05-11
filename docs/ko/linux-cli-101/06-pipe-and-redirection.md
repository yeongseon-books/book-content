---
title: pipe와 redirection
series: linux-cli-101
episode: 6
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
- pipe
- redirection
- stdin
- stdout
- CLI
last_reviewed: '2026-05-04'
seo_description: pipe는 명령어를 수도관으로 연결하는 것이고, redirection은 물줄기의 방향을 파일로 바꾸는 것입니다.
---

# pipe와 redirection

> Linux CLI 101 시리즈 (6/10)

---


## 이 글에서 다룰 문제

Linux의 철학은 "한 가지 일을 잘하는 작은 도구를 만들고, 조합하여 큰 일을 한다"입니다. `grep`은 검색만 하고, `sort`는 정렬만 하고, `wc`는 세기만 합니다. 이 도구들을 연결하는 접착제가 pipe와 redirection입니다.

> 웹 서버 로그에서 오늘 가장 많이 접속한 IP 상위 5개를 알고 싶습니다. 에디터에서 수만 줄을 눈으로 세는 것은 불가능합니다.

```bash
cat access.log | grep "2026-05-04" | awk '{print $1}' | sort | uniq -c | sort -rn | head -5
```

이 한 줄이 분석가가 스프레드시트에서 30분 걸릴 작업을 3초에 끝냅니다.

## Mental Model

> 명령어는 수도꼭지이고, pipe(`|`)는 수도관입니다. 물(데이터)은 왼쪽에서 오른쪽으로 흐릅니다. redirection(`>`)은 물줄기를 수도관 대신 물통(파일)으로 보내는 것입니다.

```text
[명령어A] ──stdout──|──stdin──> [명령어B] ──stdout──> 화면
                                                      |
[명령어A] ──stdout──> file.txt    (덮어쓰기)          |
[명령어A] ──stdout──>> file.txt   (이어쓰기)          |
[명령어A] <──stdin── file.txt     (파일을 입력으로)
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

## Before / After

**Before (중간 파일을 수동으로 만들 때)**

```bash
grep "ERROR" app.log > errors.txt
sort errors.txt > sorted.txt
uniq -c sorted.txt > counted.txt
sort -rn counted.txt > result.txt
cat result.txt
# 파일 4개 생성, 정리도 필요
```

**After (pipe로 한 줄)**

```bash
grep "ERROR" app.log | sort | uniq -c | sort -rn
# 중간 파일 없이 결과 즉시 출력
```

## 단계별 실습

### Step 1. 실습 데이터 준비

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

### Step 2. pipe로 명령어 연결

```bash
cat access.log | grep "200"             # 성공 요청만
cat access.log | awk '{print $1}' | sort | uniq -c | sort -rn
# 3 192.168.1.10
# 3 10.0.0.5
# 2 172.16.0.1
```

### Step 3. redirection으로 파일 저장

```bash
grep "500" access.log > errors.txt      # 500 에러만 저장
cat errors.txt
# 192.168.1.10 GET /api/data 500

echo "new error" >> errors.txt          # 이어쓰기
cat errors.txt
# 192.168.1.10 GET /api/data 500
# new error
```

### Step 4. stderr 분리

```bash
ls /nonexistent 2> error.log            # 에러만 파일로
cat error.log
# ls: cannot access '/nonexistent': No such file or directory

ls /tmp /nonexistent > out.txt 2> err.txt  # 출력과 에러 분리
ls /tmp /nonexistent > all.txt 2>&1        # 둘 다 같은 파일로
```

### Step 5. 실전 파이프라인

```bash
# 접속 로그에서 IP별 요청 수 상위 3개
awk '{print $1}' access.log | sort | uniq -c | sort -rn | head -3

# 500 에러 IP만 추출
grep "500" access.log | awk '{print $1}' | sort -u

# 결과를 파일에 저장하면서 화면에도 출력 (tee)
grep "200" access.log | tee success.log | wc -l
# 6 (화면 출력) + success.log에도 저장
```

## 이 코드에서 봐야 할 것

- pipe는 중간 파일 없이 데이터를 흘려보내므로 디스크를 절약합니다
- `>`는 파일을 덮어쓰므로 기존 내용이 사라집니다. `>>`는 안전합니다
- `2>&1`에서 `&`는 "파일 디스크립터"를 의미합니다. `&` 없이 `2>1`이면 "1"이라는 파일로 보냅니다
- `tee`는 데이터를 화면과 파일 양쪽으로 보내는 T자 수도관입니다

## 자주 하는 실수

### 실수 1. `>`와 `>>`를 혼동하여 데이터를 날린다

```bash
echo "important" > data.txt    # 기존 내용 삭제하고 덮어쓰기
echo "important" >> data.txt   # 기존 내용 뒤에 추가
```

중요한 파일에는 `>>`를 쓰거나 백업 후 `>`를 씁니다.

### 실수 2. 같은 파일에서 읽고 쓴다

```bash
sort file.txt > file.txt    # 파일이 비어버림!
# Shell이 먼저 > file.txt로 파일을 비운 뒤 sort를 실행하기 때문
sort file.txt > sorted.txt && mv sorted.txt file.txt  # 안전
```

### 실수 3. stderr를 무시한다

스크립트에서 에러를 잡지 않으면 에러 메시지가 화면에 섞여 나옵니다. `2>/dev/null`로 버리거나 `2>error.log`로 따로 저장하세요.

### 실수 4. 불필요한 cat을 쓴다 (UUOC)

```bash
cat file.txt | grep "pattern"    # Useless Use of Cat
grep "pattern" file.txt          # grep이 직접 파일을 읽음 — 더 효율적
```

### 실수 5. pipe 순서를 잘못 잡는다

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

## 정리 · 다음 글

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
- [cat, less, head, tail](./04-viewing-files.md)
- [grep, find, xargs](./05-grep-find-xargs.md)
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
