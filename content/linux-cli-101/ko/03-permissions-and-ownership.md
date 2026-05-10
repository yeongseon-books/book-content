---
title: 권한과 소유자 이해하기
series: linux-cli-101
episode: 3
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
- Permission
- chmod
- chown
- Security
- File System
last_reviewed: '2026-05-04'
seo_description: Linux 파일 권한은 자물쇠 세 개가 달린 문과 같습니다. 주인, 같은 팀, 나머지 사람 각각에게 다른 열쇠를 줍니다.
---

# 권한과 소유자 이해하기

> Linux CLI 101 시리즈 (3/10)

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- `rwxr-xr--`는 무엇을 의미할까요?
- 파일의 소유자(owner)와 그룹(group)은 왜 구분할까요?
- `chmod 755`와 `chmod u+x`의 차이는 무엇일까요?
- "Permission denied" 에러가 나면 어떻게 진단할까요?

> 파일 권한은 자물쇠 세 개가 달린 문입니다. 주인, 같은 팀, 나머지 사람 각각에게 다른 열쇠를 줍니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- Linux 파일 권한의 3×3 구조(owner/group/others × read/write/execute)
- `ls -l` 출력에서 권한 문자열을 읽는 법
- `chmod`로 권한을 바꾸는 두 가지 방식(숫자, 기호)
- `chown`으로 소유자와 그룹을 변경하는 법

## 왜 중요한가

서버에서 스크립트를 실행하려고 `./deploy.sh`를 입력하면 "Permission denied"가 나옵니다. 파일은 분명 존재하는데 왜 실행이 안 될까요? 실행 권한(x)이 없기 때문입니다.

> 웹 서버가 설정 파일을 읽지 못해 502 에러를 반환합니다. 파일이 존재하는데도 "No such file" 비슷한 에러가 나옵니다. 원인은 디렉터리의 실행 권한(x)이 없어서 해당 경로에 진입 자체가 불가능한 것입니다.

권한 문제는 개발자가 서버에서 가장 자주 만나는 문제 중 하나이며, 이해하지 못하면 매번 `chmod 777`로 때우다가 보안 사고를 만듭니다.

## Mental Model

> 파일 권한은 자물쇠 세 개가 달린 문입니다. 주인(owner)용, 같은 팀(group)용, 나머지(others)용 자물쇠가 각각 있고, 각 자물쇠에는 읽기(r), 쓰기(w), 실행(x) 세 가지 열쇠가 있습니다.

```text
-rwxr-xr--
│└┬┘└┬┘└┬┘
│ │  │  └── others: r-- (읽기만)
│ │  └── group:  r-x (읽기+실행)
│ └── owner:  rwx (읽기+쓰기+실행)
└── 파일 유형 (-: 일반파일, d: 디렉터리)
```

## 핵심 개념

| 기호 | 의미 | 숫자 | 파일 | 디렉터리 |
|---|---|---|---|---|
| r | 읽기 | 4 | 내용 읽기 | 목록 보기(ls) |
| w | 쓰기 | 2 | 내용 수정 | 파일 생성/삭제 |
| x | 실행 | 1 | 프로그램 실행 | 디렉터리 진입(cd) |
| - | 권한 없음 | 0 | — | — |

## Before / After

**Before (권한을 모를 때)**

```bash
./deploy.sh
# bash: ./deploy.sh: Permission denied
chmod 777 deploy.sh    # "안 되면 777" — 보안 구멍
```

**After (권한을 이해할 때)**

```bash
ls -l deploy.sh
# -rw-r--r-- 1 user team 512 May 4 deploy.sh
# → 실행 권한(x)이 없음

chmod u+x deploy.sh   # owner에게만 실행 권한 추가
./deploy.sh            # 정상 실행
```

## 단계별 실습

### Step 1. 권한 확인하기

```bash
cd ~/practice/linux-cli
touch secret.txt
ls -l secret.txt
# -rw-r--r-- 1 user user 0 May  4 10:00 secret.txt
```

### Step 2. 숫자 방식으로 권한 변경

```bash
chmod 644 secret.txt     # owner: rw-, group: r--, others: r--
chmod 755 secret.txt     # owner: rwx, group: r-x, others: r-x
chmod 600 secret.txt     # owner: rw-, group: ---, others: ---
ls -l secret.txt
# -rw------- 1 user user 0 May  4 10:00 secret.txt
```

숫자 계산: r=4, w=2, x=1을 더합니다. `755` = `rwx`(7) + `r-x`(5) + `r-x`(5).

### Step 3. 기호 방식으로 권한 변경

```bash
chmod u+x secret.txt     # owner에 실행 추가
chmod g-r secret.txt     # group에서 읽기 제거
chmod o=r secret.txt     # others를 읽기만으로 설정
chmod a+r secret.txt     # 모두(all)에게 읽기 추가
ls -l secret.txt
```

### Step 4. 디렉터리 권한

```bash
mkdir testdir
chmod 700 testdir        # owner만 접근 가능
ls -ld testdir
# drwx------ 2 user user 4096 May  4 10:00 testdir
```

### Step 5. 소유자 변경

```bash
# 소유자 변경은 root 권한이 필요합니다
sudo chown root:root secret.txt
ls -l secret.txt
# -rwxr--r-- 1 root root 0 May  4 10:00 secret.txt

sudo chown user:user secret.txt   # 원래대로 복원
```

## 이 코드에서 봐야 할 것

- `ls -l`의 첫 번째 열이 권한 문자열이고 10글자입니다(유형 1 + 권한 9)
- 숫자 방식은 전체를 한 번에 설정하고, 기호 방식은 부분만 변경합니다
- 디렉터리의 `x` 권한은 "실행"이 아니라 "진입"을 의미합니다
- `chown`은 보통 `sudo`가 필요합니다

## 자주 하는 실수

### 실수 1. "안 되면 chmod 777"로 해결한다

777은 모든 사용자에게 모든 권한을 주는 것입니다. 웹 서버 파일에 777을 주면 아무나 파일을 수정할 수 있는 보안 취약점이 됩니다. 최소 권한 원칙을 따르세요.

### 실수 2. 디렉터리의 x 권한을 간과한다

디렉터리에서 `x`는 "진입 허용"입니다. `r`만 있고 `x`가 없으면 `ls`로 목록은 보이지만 `cd`로 들어갈 수 없습니다. 파일에 접근하려면 경로상의 모든 디렉터리에 `x`가 있어야 합니다.

### 실수 3. 그룹 권한을 무시한다

혼자 작업하면 owner 권한만 신경 쓰지만, 팀 서버에서는 같은 그룹 소속 개발자가 파일을 읽거나 수정할 수 있어야 합니다. 적절한 group 설정이 없으면 동료가 파일을 열 수 없습니다.

### 실수 4. 재귀 권한 변경에서 파일과 디렉터리를 구분하지 않는다

```bash
chmod -R 755 project/   # 모든 파일에 실행 권한이 붙음 — 위험
# 올바른 방법:
find project/ -type d -exec chmod 755 {} \;   # 디렉터리만
find project/ -type f -exec chmod 644 {} \;   # 파일만
```

### 실수 5. umask를 모른 채 파일을 만든다

새 파일의 기본 권한은 `umask`로 결정됩니다. `umask 022`이면 파일은 644, 디렉터리는 755로 만들어집니다. `umask 077`이면 owner만 접근 가능합니다.

## 실무 적용

- **배포 스크립트**: `chmod u+x deploy.sh`로 실행 권한을 추가합니다
- **SSH 키**: `chmod 600 ~/.ssh/id_rsa`는 필수입니다. 권한이 느슨하면 SSH가 거부합니다
- **웹 서버**: HTML/CSS는 644, CGI/스크립트는 755, 설정 파일은 600이 일반적입니다
- **공유 디렉터리**: `chmod 2775 shared/`로 setgid를 설정하면 새 파일이 그룹을 상속합니다
- **Docker**: 컨테이너 내 파일 권한이 호스트와 다르면 volume mount에서 문제가 생깁니다

## 실무에서는 이렇게 생각한다

권한 설정의 원칙은 **최소 권한(Principle of Least Privilege)**입니다. 필요한 만큼만 주고, 나머지는 닫습니다. "일단 777로 열어두고 나중에 조이자"는 말은 현실에서 "나중에"가 오지 않기 때문에 위험합니다.

한편 권한이 너무 엄격하면 팀 협업이 막힙니다. 개발 서버에서는 그룹 권한을 적절히 열어두고, production 서버에서는 최소화하는 것이 균형점입니다. 권한 문제로 삽질한 시간을 기록해두면, 어떤 설정이 적절한지 패턴이 보입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **최소 권한** — chmod 777은 사실상 안티패턴입니다.
- **ACL/umask** — 기본 권한은 umask로 통제합니다.
- **setuid 주의** — setuid 사용은 보안 검토 후에만 허용합니다.
- **그룹 활용** — 공유 자원은 그룹과 sgid로 다룹니다.
- **감사 로그** — 권한 변경은 감사 로그에 남깁니다.

## 체크리스트

- [ ] `rwxr-xr--`를 보고 owner/group/others 권한을 말할 수 있다
- [ ] `chmod 755`가 어떤 권한인지 계산할 수 있다
- [ ] 기호 방식(`u+x`, `g-w`)으로 부분 변경을 할 수 있다
- [ ] 디렉터리의 `x` 권한이 "진입"을 의미한다는 것을 안다
- [ ] `chmod 777`을 쓰면 안 되는 이유를 설명할 수 있다

## 연습 문제

1. `test.sh` 파일을 만들고 `#!/bin/bash`와 `echo "Hello"`를 적은 뒤, 실행 권한을 추가하여 `./test.sh`로 실행해보세요.
2. `ls -l /etc/passwd`와 `ls -l /etc/shadow`의 권한 차이를 비교하고, 왜 그런지 추측해보세요.
3. `umask` 명령어를 실행하여 현재 값을 확인하고, `touch`로 새 파일을 만든 뒤 기본 권한이 umask와 어떻게 관련되는지 설명해보세요.

## 정리 · 다음 글

- Linux 파일 권한은 owner/group/others × r/w/x의 3×3 구조입니다.
- 숫자 방식(644, 755)은 전체를 설정하고, 기호 방식(u+x)은 부분을 변경합니다.
- 디렉터리의 x 권한은 진입 허용이며, 경로상 모든 디렉터리에 필요합니다.
- 최소 권한 원칙을 따르고, 777은 절대 쓰지 않습니다.
- `chown`으로 소유자를 바꾸려면 root 권한이 필요합니다.

다음 글에서는 **파일 내용을 확인하는 명령어** — `cat`, `less`, `head`, `tail`을 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [파일과 디렉터리 다루기](./02-files-and-directories.md)
- **권한과 소유자 이해하기 (현재 글)**
- cat, less, head, tail (예정)
- grep, find, xargs (예정)
- pipe와 redirection (예정)
- 프로세스 확인과 종료 (예정)
- 환경변수와 PATH (예정)
- 간단한 shell script (예정)
- SSH와 원격 서버 접속 (예정)

<!-- toc:end -->

## 참고 자료

- [Linux File Permissions Explained](https://www.redhat.com/sysadmin/linux-file-permissions-explained)
- [GNU Coreutils - chmod](https://www.gnu.org/software/coreutils/manual/html_node/chmod-invocation.html)
- [OWASP - Principle of Least Privilege](https://owasp.org/www-community/Access_Control)
- [Linux man page - chmod, chown](https://man7.org/linux/man-pages/)

Tags: Linux, Permission, chmod, chown, Security, File System
