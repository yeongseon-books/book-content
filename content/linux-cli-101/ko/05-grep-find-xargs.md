---
title: "grep, find, xargs — 검색의 삼총사"
series: linux-cli-101
episode: 5
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
- grep
- find
- xargs
- Search
- CLI
last_reviewed: '2026-05-11'
seo_description: grep은 파일 내용에서 텍스트를 찾는 탐정이고, find는 파일 이름과 속성으로 파일을 찾는 수색대입니다.
---

# grep, find, xargs — 검색의 삼총사

> Linux CLI 101 시리즈 (5/10)

---


## 이 글에서 다룰 문제

프로젝트가 커지면 파일이 수백 개를 넘깁니다. "이 함수를 어디에서 호출하지?", "어제 수정된 파일이 뭐지?", "ERROR가 포함된 로그 줄만 보고 싶다" — 이 모든 질문에 답하는 것이 `grep`과 `find`입니다.

> 프로덕션 서버에서 "database connection timeout" 에러가 발생했습니다. 로그 파일이 30개이고 각각 수만 줄입니다. 어느 파일, 몇 번째 줄에서 발생하는지 찾아야 합니다.

에디터로 파일을 하나씩 여는 대신, `grep -rn "connection timeout" /var/log/app/`이면 전체 결과가 1초 안에 나옵니다.

## Mental Model

> `grep`은 도서관에서 책 내용을 검색하는 전문 사서이고, `find`는 책꽂이에서 제목이나 크기로 책을 찾는 수색대입니다. `xargs`는 찾은 책 목록을 다른 사람에게 넘겨주는 전달자입니다.

```text
grep: "이 단어가 적힌 페이지를 찾아줘"  → 내용 검색
find: "빨간 표지의 200페이지짜리 책을 찾아줘" → 파일 검색
xargs: "찾은 책을 모아서 복사기에 넣어줘" → 결과 → 명령어
```

## 핵심 개념

| 명령어 | 검색 대상 | 주요 옵션 | 예시 |
|---|---|---|---|
| `grep` | 파일 내용(텍스트) | `-r`, `-n`, `-i`, `-l` | `grep -rn "TODO" src/` |
| `find` | 파일/디렉터리(메타데이터) | `-name`, `-type`, `-mtime`, `-size` | `find . -name "*.py"` |
| `xargs` | stdin을 인자로 변환 | `-I {}`, `-P` | `find . -name "*.log" \| xargs rm` |

## Before / After

**Before (수동 검색)**

```text
1. 에디터로 파일을 하나씩 열기
2. Ctrl+F로 검색
3. 다음 파일 열기
4. 30개 파일 반복 → 20분 소요
```

**After (grep 한 줄)**

```bash
grep -rn "connection timeout" /var/log/app/
# /var/log/app/web.log:1523: 2026-05-04 ERROR database connection timeout
# /var/log/app/worker.log:89: 2026-05-04 ERROR database connection timeout
# 1초 만에 모든 위치 확인
```

## 단계별 실습

### Step 1. 실습 환경 준비

```bash
cd ~/practice/linux-cli
mkdir -p project/src project/tests project/docs
echo 'def hello():
    # 할 일: 로깅 추가
    print("hello")' > project/src/app.py
echo 'def test_hello():
    # 할 일: assertion 수정
    assert hello() is None' > project/tests/test_app.py
echo '# Project README
TODO: write documentation' > project/docs/README.md
```

### Step 2. grep으로 내용 검색

```bash
grep "TODO" project/src/app.py           # 단일 파일
# 할 일: 로깅 추가

grep -rn "TODO" project/                  # 재귀 + 줄번호
# project/src/app.py:2:    # TODO: add logging
# project/tests/test_app.py:2:    # TODO: fix assertion
# 문서 TODO: project/docs/README.md:2:TODO: write documentation

grep -ri "todo" project/                  # 대소문자 무시
grep -rl "TODO" project/                  # 파일 경로만 출력
# 일치 파일: project/src/app.py
# 일치 파일: project/tests/test_app.py
# 일치 파일: project/docs/README.md
```

### Step 3. find로 파일 찾기

```bash
find project/ -name "*.py"               # 이름으로 찾기
# 결과 파일: project/src/app.py
# 결과 파일: project/tests/test_app.py

find project/ -type d                     # 디렉터리만
find project/ -name "*.py" -newer project/docs/README.md   # 특정 파일보다 새로운 파일
find /tmp -size +1M -mtime -7            # 1MB 이상, 7일 이내
```

### Step 4. xargs로 결과를 명령어에 전달

```bash
find project/ -name "*.py" | xargs wc -l
#  3 project/src/app.py
#  3 project/tests/test_app.py
#  6 total

grep -rl "TODO" project/ | xargs -I {} echo "Fix needed: {}"
# 수정 대상: project/src/app.py
# 수정 대상: project/tests/test_app.py
# 수정 대상: project/docs/README.md
```

### Step 5. 실전 조합

```bash
# 모든 Python 파일에서 "print" 호출 찾기
find project/ -name "*.py" | xargs grep -n "print"
# 검색 결과: project/src/app.py:3:    print("hello")

# 30일 이상 된 로그 파일 삭제
find /tmp -name "*.log" -mtime +30 -print | xargs rm -v
```

## 이 코드에서 봐야 할 것

- `grep -r`의 `-r`은 recursive(재귀)이며 하위 디렉터리까지 탐색합니다
- `grep -l`은 매칭된 줄 대신 파일 경로만 출력하여 파이프라인에 유리합니다
- `find`의 `-name` 패턴은 따옴표로 감싸야 Shell이 와일드카드를 먼저 확장하지 않습니다
- `xargs -I {}`는 `{}`를 찾은 항목으로 치환합니다

## 자주 하는 실수

### 실수 1. find 패턴에 따옴표를 빼먹는다

```bash
find . -name *.py          # Shell이 먼저 *.py를 확장 → 예상과 다른 결과
find . -name "*.py"        # 정상: find가 패턴을 직접 처리
```

### 실수 2. grep에서 정규표현식을 모르고 쓴다

`grep "error.log"`에서 `.`은 "아무 문자"입니다. `error.log`뿐 아니라 `errorXlog`도 매칭됩니다. 문자 그대로 찾으려면 `grep -F "error.log"` 또는 `grep "error\.log"`를 씁니다.

### 실수 3. xargs에 공백이 있는 파일 이름을 넘긴다

```bash
find . -name "*.txt" | xargs rm          # "My File.txt" → "My"와 "File.txt"로 분리
find . -name "*.txt" -print0 | xargs -0 rm  # null 구분자로 안전하게 처리
```

### 실수 4. find 결과를 for 루프로 처리한다

```bash
# 느리고 위험한 방법
for f in $(find . -name "*.log"); do rm "$f"; done

# 빠르고 안전한 방법
find . -name "*.log" -exec rm {} \;
# 또는
find . -name "*.log" -print0 | xargs -0 rm
```

### 실수 5. grep으로 바이너리 파일을 검색한다

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

## 체크리스트

- [ ] `grep -rn`으로 프로젝트 전체에서 문자열을 검색할 수 있다
- [ ] `find -name -type -mtime`으로 파일을 조건부로 찾을 수 있다
- [ ] `xargs`로 검색 결과를 다른 명령어에 전달할 수 있다
- [ ] 공백이 있는 파일 이름을 `-print0`과 `-0`으로 안전하게 처리할 수 있다
- [ ] `grep`의 `-i`, `-l`, `-c`, `-F` 옵션을 설명할 수 있다

## 정리 · 다음 글

- `grep`은 파일 내용에서 문자열을 검색하며, `-r`로 재귀, `-n`으로 줄번호를 표시합니다.
- `find`는 파일 이름, 유형, 크기, 수정 시간 등 메타데이터로 파일을 찾습니다.
- `xargs`는 표준 입력을 명령어 인자로 변환하며, `-0` 옵션으로 공백 문제를 방지합니다.
- 세 명령어의 조합은 수동 작업을 자동화하는 CLI의 핵심 패턴입니다.
- 기본 명령어를 먼저 익힌 뒤 `ripgrep`, `fd` 같은 대안 도구로 넘어가세요.

다음 글에서는 **pipe와 redirection** — 명령어를 연결하고 입출력 방향을 바꾸는 법을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [파일과 디렉터리 다루기](./02-files-and-directories.md)
- [권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- [cat, less, head, tail](./04-viewing-files.md)
- **grep, find, xargs (현재 글)**
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

Tags: Linux, grep, find, xargs, Search, CLI
