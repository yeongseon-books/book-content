---
title: "바이브코딩을 위한 Linux CLI 기초 (3/10): 권한과 소유자 이해하기"
series: linux-cli-101
episode: 3
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
- 바이브코딩
- Linux
- Permission
- chmod
- chown
- Security
- File System
last_reviewed: '2026-06-18'
seo_description: AI가 만든 배포 스크립트가 Permission denied로 실패할 때 어떻게 해야 할까요? chmod와 chown의 기본 감각을 정리합니다.
---

# 바이브코딩을 위한 Linux CLI 기초 (3/10): 권한과 소유자 이해하기

이 글은 **바이브코딩을 위한 Linux CLI 기초** 시리즈의 세 번째 글입니다. AI가 생성한 코드를 서버에서 실제로 실행하고 운영하려면 Linux 명령어를 알아야 합니다.

---

AI가 배포 스크립트를 만들어 줍니다. `./deploy.sh`를 실행하면 "Permission denied"가 납니다. 파일은 분명 존재하는데 왜 실행이 안 될까요? 실행 권한(x)이 없기 때문입니다. 권한을 이해해야 AI가 만든 스크립트를 서버에서 제대로 실행할 수 있습니다.

> 파일 권한은 자물쇠 세 개가 달린 문입니다. 주인(owner)용, 같은 팀(group)용, 나머지(others)용 자물쇠가 각각 있고, 각 자물쇠에는 읽기(r), 쓰기(w), 실행(x) 세 가지 열쇠가 있습니다.

## 이 글에서 다룰 질문 5가지

1. `r`, `w`, `x` 권한은 파일과 디렉터리에서 각각 어떻게 다르게 동작할까요?
2. 소유자, 그룹, 그 외 사용자 구분을 왜 알아야 할까요?
3. `chmod`와 `chown`은 각각 무엇을 바꾸는 명령일까요?
4. 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
5. 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 바이브코딩 관점에서 왜 권한인가?

Claude가 Python 웹 서버 코드와 함께 `start.sh` 스크립트를 만들어 줍니다. 서버에서 실행하려면 실행 권한이 필요합니다. SSH 키를 서버에 복사하면 권한이 맞지 않아 SSH가 거부합니다. 환경 설정 파일에 API 키가 들어 있으면 권한을 제한해서 보호해야 합니다.

바이브코딩으로 만든 시스템을 안전하게 운영하려면 최소 권한 원칙을 이해해야 합니다.

## 권한 구조 읽기

```text
-rwxr-xr--
│└┬┘└┬┘└┬┘
│ │  │  └── others: r-- (read only)
│ │  └── group:  r-x (read+execute)
│ └── owner:  rwx (read+write+execute)
└── file type (-: regular file, d: directory)
```

| 기호 | 의미 | 숫자 | 파일 | 디렉터리 |
|---|---|---|---|---|
| r | 읽기 | 4 | 내용 읽기 | 목록 보기(ls) |
| w | 쓰기 | 2 | 내용 수정 | 파일 생성/삭제 |
| x | 실행 | 1 | 프로그램 실행 | 디렉터리 진입(cd) |
| - | 권한 없음 | 0 | — | — |

## Before / After: 권한을 이해하면 달라지는 것

**Before — 권한을 모를 때**

```bash
./deploy.sh
# bash: ./deploy.sh: Permission denied
chmod 777 deploy.sh    # "Just 777 if it doesn't work" — security hole
```

**After — 권한을 이해할 때**

```bash
ls -l deploy.sh
# -rw-r--r-- 1 user team 512 May 4 deploy.sh
# -> execute permission (x) is missing

chmod u+x deploy.sh   # Add execute permission for owner only
./deploy.sh            # Runs successfully
```

## 단계별 실습

### 1단계. 권한 확인하기

```bash
cd ~/practice/linux-cli
touch secret.txt
ls -l secret.txt
# -rw-r--r-- 1 user user 0 May  4 10:00 secret.txt
```

### 2단계. 숫자 방식으로 권한 변경

```bash
chmod 644 secret.txt     # owner: rw-, group: r--, others: r--
chmod 755 secret.txt     # owner: rwx, group: r-x, others: r-x
chmod 600 secret.txt     # owner: rw-, group: ---, others: ---
ls -l secret.txt
# -rw------- 1 user user 0 May  4 10:00 secret.txt
```

숫자 계산: r=4, w=2, x=1을 더합니다. `755` = `rwx`(7) + `r-x`(5) + `r-x`(5).

### 3단계. 기호 방식으로 권한 변경

```bash
chmod u+x secret.txt     # Add execute for owner
chmod g-r secret.txt     # Remove read from group
chmod o=r secret.txt     # Set others to read only
chmod a+r secret.txt     # Add read for all
```

### 4단계. 디렉터리 권한

```bash
mkdir testdir
chmod 700 testdir        # Only owner can access
ls -ld testdir
# drwx------ 2 user user 4096 May  4 10:00 testdir
```

### 5단계. 소유자 변경

```bash
# Changing ownership requires root privileges
sudo chown root:root secret.txt
ls -l secret.txt
# -rwxr--r-- 1 root root 0 May  4 10:00 secret.txt

sudo chown user:user secret.txt   # Restore original
```

## 자주 하는 실수 (바이브코딩 맥락)

| 실수 | 설명 | 올바른 방법 |
|---|---|---|
| chmod 777 습관 | 모든 사람에게 모든 권한 — 보안 취약점 | 최소 권한 원칙 (`chmod u+x`) |
| 디렉터리 x 의미 오해 | `x`는 "실행"이 아니라 "진입 허용" | `cd` 하려면 `x` 권한 필요 |
| 그룹 권한 무시 | 팀 서버에서 동료가 파일에 접근 못 함 | 적절한 group 권한 설정 |
| 재귀 권한 남발 | `chmod -R 755 project/`는 모든 파일에 실행 권한 | `find`로 파일/디렉터리 구분 |
| SSH 키 권한 느슨 | 권한이 느슨하면 SSH가 키 거부 | `chmod 600 ~/.ssh/id_rsa` |

## AI 팁: 바이브코딩에서 권한 패턴

AI가 배포 스크립트를 생성하면 권한 설정 코드가 포함될 때가 많습니다:

```bash
# AI가 생성한 배포 스크립트 일부
chmod u+x /opt/myapp/bin/start.sh
chmod 640 /opt/myapp/conf/app.env
chmod 600 /opt/myapp/conf/secrets.env
```

이 명령들이 왜 이런 권한을 주는지 이해해야 합니다. `640`은 owner가 읽기/쓰기, group이 읽기만, others는 접근 불가입니다. 설정 파일에는 이 정도가 적절합니다.

## 운영 체크리스트

- [ ] `rwxr-xr--`를 보고 owner/group/others 권한을 말할 수 있다
- [ ] `chmod 755`가 어떤 권한인지 계산할 수 있다
- [ ] 기호 방식(`u+x`, `g-w`)으로 부분 변경을 할 수 있다
- [ ] 디렉터리의 `x` 권한이 "진입"을 의미한다는 것을 안다
- [ ] `chmod 777`을 쓰면 안 되는 이유를 설명할 수 있다

## 처음 질문으로 돌아가기

- **`r`, `w`, `x` 권한은 파일과 디렉터리에서 각각 어떻게 다르게 동작할까요?** 파일의 `x`는 실행, 디렉터리의 `x`는 진입입니다. 디렉터리에 `r`만 있으면 목록은 보이지만 들어갈 수 없습니다.
- **`chmod`와 `chown`은 각각 무엇을 바꾸는 명령일까요?** `chmod`는 권한(rwx)을, `chown`은 소유자(user:group)를 바꿉니다.

## 정리

- Linux 파일 권한은 owner/group/others × r/w/x의 3×3 구조입니다.
- 숫자 방식(644, 755)은 전체를 설정하고, 기호 방식(u+x)은 부분을 변경합니다.
- 디렉터리의 x 권한은 진입 허용이며, 경로상 모든 디렉터리에 필요합니다.
- 최소 권한 원칙을 따르고, 777은 절대 쓰지 않습니다.
- `chown`으로 소유자를 바꾸려면 root 권한이 필요합니다.

다음 글에서는 **파일 내용을 확인하는 명령어** — `cat`, `less`, `head`, `tail`을 다룹니다.

## 참고 자료

- [Linux File Permissions Explained](https://www.redhat.com/sysadmin/linux-file-permissions-explained)
- [GNU Coreutils - chmod](https://www.gnu.org/software/coreutils/manual/html_node/chmod-invocation.html)
- [OWASP - Principle of Least Privilege](https://owasp.org/www-community/Access_Control)
- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Linux CLI 기초 (1/10): CLI와 Shell이란 무엇인가?
- 바이브코딩을 위한 Linux CLI 기초 (2/10): 파일과 디렉터리 다루기
- **바이브코딩을 위한 Linux CLI 기초 (3/10): 권한과 소유자 이해하기 (현재 글)**
- 바이브코딩을 위한 Linux CLI 기초 (4/10): cat, less, head, tail — 파일 내용 보기
- 바이브코딩을 위한 Linux CLI 기초 (5/10): grep, find, xargs — 검색의 삼총사
- 바이브코딩을 위한 Linux CLI 기초 (6/10): pipe와 redirection
- 바이브코딩을 위한 Linux CLI 기초 (7/10): 프로세스 확인과 종료
- 바이브코딩을 위한 Linux CLI 기초 (8/10): 환경변수와 PATH
- 바이브코딩을 위한 Linux CLI 기초 (9/10): 간단한 shell script
- 바이브코딩을 위한 Linux CLI 기초 (10/10): SSH와 원격 서버 접속
<!-- toc:end -->

Tags: 바이브코딩, Linux, Permission, chmod, chown, Security, File System
