---
title: "바이브코딩을 위한 Linux CLI 기초 (6/10): pipe와 redirection"
series: linux-cli-101
episode: 6
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
- 바이브코딩
- Linux
- pipe
- redirection
- stdin
- stdout
- CLI
last_reviewed: '2026-06-18'
seo_description: AI가 만든 서버의 로그를 분석하고 결과를 파일로 저장하려면 pipe와 redirection을 알아야 합니다. 명령어를 연결하고 입출력 방향을 바꾸는 법을 정리합니다.
---

# 바이브코딩을 위한 Linux CLI 기초 (6/10): pipe와 redirection

이 글은 **바이브코딩을 위한 Linux CLI 기초** 시리즈의 여섯 번째 글입니다. AI가 생성한 코드를 서버에서 실제로 실행하고 운영하려면 Linux 명령어를 알아야 합니다.

---

Linux의 철학은 "한 가지 일을 잘하는 작은 도구를 만들고, 조합하여 큰 일을 한다"입니다. `grep`은 검색만 하고, `sort`는 정렬만 하고, `wc`는 세기만 합니다. AI가 만든 서버의 로그를 분석할 때, 이 작은 도구들을 연결하는 접착제가 pipe와 redirection입니다.

> 명령어는 수도꼭지이고, pipe(`|`)는 수도관입니다. 물(데이터)은 왼쪽에서 오른쪽으로 흐릅니다. redirection(`>`)은 물줄기를 수도관 대신 물통(파일)으로 보내는 것입니다.

## 이 글에서 다룰 질문 5가지

1. 표준 입력, 표준 출력, 표준 오류는 왜 분리되어 있을까요?
2. `|`, `>`, `>>`, `2>`는 각각 어떤 흐름을 만들까요?
3. 중간 파일 없이 명령을 이어 붙이면 무엇이 좋아질까요?
4. 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
5. 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 바이브코딩 관점에서 왜 pipe인가?

AI가 만든 Python 서버의 로그를 분석합니다. 1GB 로그 파일에서 ERROR만 골라서, 날짜별로 집계하고, 결과를 파일로 저장해야 합니다. Python 스크립트를 새로 만들 수도 있지만, CLI 한 줄이면 충분합니다:

```bash
grep "ERROR" app.log | awk '{print $1}' | sort | uniq -c | sort -rn > error-summary.txt
```

이것이 Unix 철학의 핵심입니다. 작은 도구들을 `|`로 연결하면 강력한 분석 파이프라인이 됩니다.

## 핵심 기호 정리

| 기호 | 이름 | 역할 | 예시 |
|---|---|---|---|
| `\|` | pipe | 왼쪽 stdout → 오른쪽 stdin | `ls \| grep ".py"` |
| `>` | redirect (덮어쓰기) | stdout → 파일 (기존 내용 삭제) | `echo "hi" > out.txt` |
| `>>` | redirect (이어쓰기) | stdout → 파일 (기존 내용 유지) | `echo "hi" >> out.txt` |
| `<` | input redirect | 파일 → stdin | `sort < names.txt` |
| `2>` | stderr redirect | 에러만 파일로 | `cmd 2> error.log` |
| `2>&1` | stderr to stdout | 에러와 출력 합치기 | `cmd > all.log 2>&1` |

## Before / After: 중간 파일 vs pipe

**Before — 중간 파일을 수동으로 만들 때**

```bash
grep "ERROR" app.log > errors.txt
sort errors.txt > sorted.txt
uniq -c sorted.txt > counted.txt
sort -rn counted.txt > result.txt
cat result.txt
# 4 files created, cleanup needed
```

**After — pipe로 한 줄**

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
# 성공 요청만 보기
cat access.log | grep "200"

# IP별 요청 수
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

# 출력과 에러를 같은 파일에
ls /tmp /nonexistent > all.txt 2>&1
```

### 5단계. tee로 화면과 파일 동시 저장

```bash
# Save to file AND print to screen
grep "200" access.log | tee success.log | wc -l
# 6 (screen output) + success.log also saved

# 배포 로그를 화면에서 보면서 파일에도 저장
./deploy.sh 2>&1 | tee deploy-$(date +%Y%m%d).log
```

## 자주 하는 실수 (바이브코딩 맥락)

| 실수 | 설명 | 올바른 방법 |
|---|---|---|
| `>`와 `>>`혼동 | `>`는 기존 내용 삭제 | 중요 파일은 `>>`로 이어쓰기 |
| 같은 파일 읽고 쓰기 | `sort file.txt > file.txt`는 파일이 비어버림 | 임시 파일 사용 후 `mv` |
| 에러 출력 무시 | 스크립트 에러가 화면에 섞여 나옴 | `2>/dev/null` 또는 `2>error.log` |
| 불필요한 cat | `cat file.txt \| grep "pattern"` | `grep "pattern" file.txt` |
| 잘못된 연결 순서 | 정렬 후 필터링은 비효율 | 먼저 필터링(grep) 후 정렬(sort) |

## AI 팁: pipe로 로그 분석을 AI에게 넘기기

AI에게 로그 분석을 요청할 때 pipe로 전처리하면 토큰을 절약하고 더 정확한 답을 받을 수 있습니다:

```bash
# 오늘 에러만 추출
grep "ERROR" /var/log/myapp/app.log \
  | grep "$(date +%Y-%m-%d)" \
  | sort | uniq -c | sort -rn \
  | head -20 \
  | tee /tmp/today-errors.txt

# /tmp/today-errors.txt 내용을 AI에게 붙여넣기
```

이렇게 하면 수백 MB 로그 파일 전체 대신 핵심 20줄만 AI에게 전달할 수 있습니다.

## 운영 체크리스트

- [ ] `|`로 두 명령어의 출력/입력을 연결할 수 있다
- [ ] `>`(덮어쓰기)와 `>>`(이어쓰기)의 차이를 안다
- [ ] stdout(1)과 stderr(2)가 분리된 이유를 설명할 수 있다
- [ ] `2>&1`로 에러와 출력을 합칠 수 있다
- [ ] `tee`로 화면 출력과 파일 저장을 동시에 할 수 있다

## 처음 질문으로 돌아가기

- **표준 입력, 표준 출력, 표준 오류는 왜 분리되어 있을까요?** 정상 출력과 에러를 분리하면 파이프라인에서 에러를 별도로 처리할 수 있습니다. `cmd > out.txt 2> err.txt`처럼 각각 다른 파일로 보낼 수 있습니다.
- **중간 파일 없이 명령을 이어 붙이면 무엇이 좋아질까요?** 디스크 I/O가 줄고, 정리해야 할 임시 파일이 없으며, 파이프라인 전체가 메모리 효율적으로 처리됩니다.

## 정리

- pipe(`|`)는 명령어의 stdout을 다음 명령어의 stdin으로 연결합니다.
- `>`는 덮어쓰기, `>>`는 이어쓰기로 출력을 파일에 저장합니다.
- stdout(1)과 stderr(2)는 독립적이며, `2>&1`로 합칠 수 있습니다.
- `tee`는 화면과 파일에 동시에 출력합니다.
- pipe 체인이 복잡해지면 스크립트로 옮기는 것이 유지보수에 유리합니다.

다음 글에서는 **프로세스 확인과 종료** — `ps`, `top`, `kill`, 백그라운드 실행을 다룹니다.

## 참고 자료

- [GNU Bash Manual - Redirections](https://www.gnu.org/software/bash/manual/html_node/Redirections.html)
- [The Missing Semester - Data Wrangling](https://missing.csail.mit.edu/2020/data-wrangling/)
- [Linux Documentation - I/O Redirection](https://tldp.org/LDP/abs/html/io-redirection.html)
- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Linux CLI 기초 (1/10): CLI와 Shell이란 무엇인가?
- 바이브코딩을 위한 Linux CLI 기초 (2/10): 파일과 디렉터리 다루기
- 바이브코딩을 위한 Linux CLI 기초 (3/10): 권한과 소유자 이해하기
- 바이브코딩을 위한 Linux CLI 기초 (4/10): cat, less, head, tail — 파일 내용 보기
- 바이브코딩을 위한 Linux CLI 기초 (5/10): grep, find, xargs — 검색의 삼총사
- **바이브코딩을 위한 Linux CLI 기초 (6/10): pipe와 redirection (현재 글)**
- 바이브코딩을 위한 Linux CLI 기초 (7/10): 프로세스 확인과 종료
- 바이브코딩을 위한 Linux CLI 기초 (8/10): 환경변수와 PATH
- 바이브코딩을 위한 Linux CLI 기초 (9/10): 간단한 shell script
- 바이브코딩을 위한 Linux CLI 기초 (10/10): SSH와 원격 서버 접속
<!-- toc:end -->

Tags: 바이브코딩, Linux, pipe, redirection, stdin, stdout, CLI
