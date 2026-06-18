---
title: "바이브코딩을 위한 Linux CLI 기초 (8/10): 환경변수와 PATH"
series: linux-cli-101
episode: 8
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Linux
  - EnvironmentVariable
  - PATH
  - Shell
---

# 바이브코딩을 위한 Linux CLI 기초 (8/10): 환경변수와 PATH

이 글은 "바이브코딩을 위한 Linux CLI 기초" 시리즈의 8번째 글입니다.

---

바이브코딩에서 AI는 환경변수 설정 코드를 빠르게 만들어 줍니다. 그런데 "command not found" 오류가 나거나, 환경변수가 자식 프로세스에 전달되지 않거나, `.env` 파일이 실수로 Git에 올라가는 문제가 자주 발생합니다.

`python`을 입력하면 Shell이 Python 실행 파일을 찾아서 실행합니다. 어떻게 찾을까요? 모든 디렉터리를 뒤지는 것이 아니라, PATH에 등록된 디렉터리만 순서대로 확인합니다. PATH에 없으면 "command not found"입니다.

환경변수는 프로세스에 붙은 이름표이고, PATH는 Shell이 명령어를 찾아다니는 지도입니다. `export` 없이 설정한 변수는 현재 Shell에서만 유효하고 Python 스크립트 같은 자식 프로세스에는 전달되지 않습니다.

환경변수의 스코프, PATH 동작 원리, Shell 시작 파일의 역할, `.env` 보안을 중심으로 정리합니다.

> **핵심 인사이트:** `export` 없이 설정한 변수는 자식 프로세스(Python, Node.js 등)에 전달되지 않습니다. PATH는 `:` 구분자로 왼쪽이 우선합니다. `.env` 파일은 반드시 `.gitignore`에 추가해야 합니다.

## 이 글에서 다룰 문제

- 환경변수는 어떤 방식으로 프로세스에 전달될까요?
- `export`와 로컬 Shell 변수는 무엇이 다를까요?
- PATH는 명령 실행에서 어떤 검색 순서를 만들까요?
- Shell 시작 파일(.bashrc, .bash_profile)은 언제 읽힐까요?
- AI가 만든 환경변수 설정 코드에서 확인해야 할 것은 무엇인가요?

## 환경변수와 PATH 핵심 패턴

```bash
# 환경변수 확인
echo $HOME          # 홈 디렉터리
echo $PATH          # 명령어 검색 경로 (: 구분)
echo $PATH | tr ':' '\n'   # 한 줄씩 보기

# 로컬 변수 vs export
MY_VAR="hello"
bash -c 'echo $MY_VAR'    # (빈 문자열) — 자식 프로세스에 전달 안 됨

export MY_VAR             # 이후 자식 프로세스에 전달
bash -c 'echo $MY_VAR'    # hello

# PATH에 경로 추가 (기존 PATH 유지하며 앞에 추가)
export PATH="$HOME/.local/bin:$PATH"
```

```bash
# 영구 설정: ~/.bashrc에 추가
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
echo 'export EDITOR=vim' >> ~/.bashrc
source ~/.bashrc    # 즉시 적용

# .env 파일 로드 패턴
set -a              # 이후 변수를 자동 export
source .env
set +a
```

## 변경 전후 비교

**Before: PATH를 모를 때**
```text
- pip install httpie 후 http 명령 실행 → "command not found"
- export PATH="/my/path" → 기존 PATH 전체가 사라짐
- API 키를 .env에 저장 후 Git에 커밋 → 보안 사고
- 변수 설정 후 Python에서 os.environ 읽기 실패
```

**After: 환경변수 이해 후**
```text
- which http 또는 pip show httpie로 설치 위치 확인 후 PATH에 추가
- export PATH="$HOME/.local/bin:$PATH" → 기존 PATH 보존
- .gitignore에 .env 추가
- export 후 자식 프로세스에서 변수 참조 성공
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| export 없이 변수 설정 | 자식 프로세스(Python 등)에 전달 안 됨 | `export VAR=value` |
| `export PATH="/new/path"` | 기존 PATH 전체 덮어씀 | `export PATH="/new/path:$PATH"` |
| .env를 Git에 커밋 | API 키/비밀번호 공개 노출 | `.gitignore`에 `.env` 추가 |
| `${HOME}_backup` 대신 `$HOME_backup` | HOME_backup 변수를 찾음 | 중괄호 사용 `${HOME}_backup` |
| .bashrc와 .bash_profile 혼동 | SSH 접속 시 설정이 로드 안 됨 | .bash_profile에서 .bashrc를 source |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"Python 프로젝트에서 환경변수로 설정을 관리하는 코드를 만들어줘.
.env 파일 로드,
API_KEY, DB_HOST, DB_PORT 변수,
개발/운영 환경 구분,
.gitignore에 .env 추가 포함"

# AI 결과물 검증 체크포인트:
# - .env 파일이 .gitignore에 있는가?
# - 자식 프로세스에 전달이 필요한 변수에 export가 있는가?
# - PATH 변경 시 기존 PATH를 보존하는가?
# - Shell 시작 파일(.bashrc)에 영구 설정이 들어가 있는가?
# - 민감한 키가 코드에 하드코딩되지 않았는가?
```

## 운영 체크리스트

- [ ] `.env` 파일이 `.gitignore`에 등록되어 있다
- [ ] 자식 프로세스에서 읽어야 하는 변수에 `export`가 붙어 있다
- [ ] PATH 추가 시 기존 `$PATH`를 보존하는 패턴을 사용한다
- [ ] 영구 설정은 `~/.bashrc`에 저장하고 `source`로 적용했다
- [ ] CI/CD 환경변수가 코드가 아닌 플랫폼 비밀 저장소에 보관된다

## 처음 질문으로 돌아가기

- **export와 로컬 변수의 차이는?** `export` 없이 설정한 변수는 현재 Shell에만 존재하고 자식 프로세스(Python, Node.js 등)에 전달되지 않습니다. `export`가 있어야 `os.environ`으로 읽을 수 있습니다.
- **PATH 검색 순서는?** PATH는 `:` 구분자로 왼쪽부터 순서대로 검색합니다. 같은 이름의 명령이 여러 위치에 있으면 가장 왼쪽에 있는 것이 실행됩니다.
- **.bashrc와 .bash_profile의 차이는?** SSH 등 로그인 Shell은 `.bash_profile`을 읽고, 터미널 앱에서 여는 대화형 Shell은 `.bashrc`를 읽습니다. `.bash_profile`에서 `.bashrc`를 source하면 통일됩니다.

## 정리

바이브코딩에서 AI가 만들어 준 환경변수 코드에서 export 여부, PATH 보존 패턴, .env 보안을 반드시 확인하세요. 환경변수는 프로세스 간 설정 전달의 기본입니다. 다음 글에서는 Shell script를 다룹니다.

## 참고 자료

- [GNU Bash Manual — Shell Variables](https://www.gnu.org/software/bash/manual/bash.html#Shell-Variables)
- [12-Factor App — Config](https://12factor.net/config)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Linux CLI 기초 (1/10): Linux와 CLI란?
- 바이브코딩을 위한 Linux CLI 기초 (2/10): 파일 시스템 탐색
- 바이브코딩을 위한 Linux CLI 기초 (3/10): 파일 조작
- 바이브코딩을 위한 Linux CLI 기초 (4/10): 텍스트 처리
- 바이브코딩을 위한 Linux CLI 기초 (5/10): 프로세스 관리
- 바이브코딩을 위한 Linux CLI 기초 (6/10): 파일 권한과 소유자
- 바이브코딩을 위한 Linux CLI 기초 (7/10): 파이프와 리다이렉션
- **바이브코딩을 위한 Linux CLI 기초 (8/10): 환경변수와 PATH (현재 글)**
- 바이브코딩을 위한 Linux CLI 기초 (9/10): 간단한 Shell Script
- 바이브코딩을 위한 Linux CLI 기초 (10/10): SSH와 원격 서버 접속
<!-- toc:end -->

Tags: 바이브코딩, Linux, EnvironmentVariable, PATH, Shell
