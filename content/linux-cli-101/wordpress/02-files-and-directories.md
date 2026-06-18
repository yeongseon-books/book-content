---
title: "바이브코딩을 위한 Linux CLI 기초 (2/10): 파일과 디렉터리 다루기"
series: linux-cli-101
episode: 2
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
- 바이브코딩
- Linux
- CLI
- File System
- Directory
- ls
- cp
last_reviewed: '2026-06-18'
seo_description: AI가 만든 코드를 서버에 올리려면 파일과 디렉터리를 CLI로 다뤄야 합니다. ls, cd, mkdir, cp, mv, rm의 기본과 경로 개념을 익힙니다.
---

# 바이브코딩을 위한 Linux CLI 기초 (2/10): 파일과 디렉터리 다루기

이 글은 **바이브코딩을 위한 Linux CLI 기초** 시리즈의 두 번째 글입니다. AI가 생성한 코드를 서버에서 실제로 실행하고 운영하려면 Linux 명령어를 알아야 합니다.

---

AI가 프로젝트 구조를 만들어 줍니다. `src/`, `config/`, `logs/` 디렉터리를 만들고, 파일을 복사하고, 설정 파일을 이동하는 일은 배포할 때마다 반복됩니다. 서버에서 이 작업은 전부 명령어입니다.

> Linux 파일 시스템은 하나의 뿌리(`/`)에서 시작하는 거대한 나무입니다. 모든 파일과 디렉터리는 이 나무의 가지입니다.

## 이 글에서 다룰 질문 5가지

1. 절대 경로와 상대 경로는 언제 다르게 느껴질까요?
2. `pwd`, `cd`, `ls`만으로 현재 위치를 어떻게 읽어야 할까요?
3. `cp`, `mv`, `rm`은 각각 어떤 상황에서 쓰면 안전할까요?
4. 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
5. 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 바이브코딩 관점에서 왜 파일 다루기인가?

Claude가 FastAPI 앱을 만들어 주면 로컬에서 테스트합니다. 이제 서버에 올려야 합니다. 파일을 업로드하고, 디렉터리 구조를 맞추고, 설정 파일을 복사하고, 이전 버전을 백업하는 작업이 기다립니다. 이 모든 작업이 `cp`, `mv`, `mkdir`, `rm` 명령어입니다.

파일 작업을 CLI로 처리하면 스크립트로 자동화할 수 있습니다. 배포할 때마다 같은 파일을 같은 위치에 넣는 작업을 한 줄 명령으로 만들 수 있습니다.

## Linux 파일 시스템 구조

```text
/                       <- root
├── home/               <- user home directories
│   └── user/           <- my workspace (~)
├── etc/                <- system configuration files
├── var/                <- logs, caches, variable data
├── tmp/                <- temporary files
└── usr/                <- user programs
    └── bin/            <- executables
```

Windows는 `C:\`, `D:\`처럼 드라이브가 여러 개이지만, Linux는 무조건 `/`(root) 하나에서 시작합니다.

| 용어 | 설명 | 예시 |
|---|---|---|
| 절대 경로 | `/`부터 시작하는 전체 경로 | `/home/user/project/main.py` |
| 상대 경로 | 현재 위치 기준 경로 | `./src/main.py`, `../config.yaml` |
| `.` | 현재 디렉터리 | `./run.sh` (현재 폴더의 run.sh) |
| `..` | 상위 디렉터리 | `cd ..` (한 단계 위로) |
| `~` | 홈 디렉터리 | `cd ~` = `cd /home/user` |

## Before / After: 경로를 알면 달라지는 것

**Before — 경로를 모를 때**

```text
"The file is somewhere... where was it?"
-> Click through folders one by one in the GUI
-> 5 minutes spent
```

**After — 경로를 아는 CLI 사용자**

```bash
find /var/log -name "error*.log" -mtime -1
# Finds all error logs created since yesterday in 1 second
```

## 단계별 실습

### 1단계. 현재 위치 확인

```bash
pwd
# Example output: /home/user
```

`pwd`(print working directory)는 지금 내가 어디에 있는지 보여줍니다.

### 2단계. 디렉터리 이동

```bash
cd /tmp           # Move using an absolute path
cd ~              # Move to home
mkdir -p ~/practice/linux-cli   # Create a practice directory
cd ~/practice/linux-cli         # Move into it
pwd
# Output: /home/user/practice/linux-cli
```

### 3단계. 파일과 디렉터리 만들기

```bash
touch hello.txt               # Create an empty file
mkdir src                     # Create a directory
mkdir -p src/utils/helpers    # Create nested directories at once
ls -la
# hello.txt, src/ are visible
```

### 4단계. 복사, 이동, 이름 바꾸기

```bash
cp hello.txt hello-backup.txt          # Copy a file
mv hello-backup.txt src/               # Move a file
mv src/hello-backup.txt src/backup.txt # Rename
ls src/
# backup.txt  utils/
```

### 5단계. 삭제

```bash
rm src/backup.txt              # Delete a file
rmdir src/utils/helpers        # Delete an empty directory
rm -r src/utils                # Delete a directory and its contents
```

## 자주 하는 실수 (바이브코딩 맥락)

| 실수 | 설명 | 올바른 방법 |
|---|---|---|
| 루트 경로 삭제 | `/`를 실수로 삭제하면 시스템 전체 손실 | 항상 대상 확인 후 삭제 |
| 와일드카드 미확인 | `rm * .log`는 ALL 파일 삭제 | 삭제 전 `ls *.log`로 확인 |
| 공백 있는 경로 | `cp My File.txt`는 에러 | `cp "My File.txt"`로 따옴표 |
| 경로 혼동 | `cd practice`는 현재 위치 의존 | 어디서든 `cd ~/practice` |
| 디렉터리 복사 누락 | `cp src/ backup/`은 에러 | `cp -r src/ backup/`로 `-r` 추가 |

## AI 팁: 배포 자동화에서 파일 작업

AI가 배포 스크립트를 생성할 때 이런 패턴이 자주 나옵니다:

```bash
# AI가 생성한 배포 패턴
mkdir -p /opt/myapp/releases/$(date +%Y%m%d)
cp -r ./dist/* /opt/myapp/releases/$(date +%Y%m%d)/
ln -sfn /opt/myapp/releases/$(date +%Y%m%d) /opt/myapp/current
```

이 명령들이 무엇을 하는지 이해해야 AI가 만든 배포 스크립트를 신뢰하고 실행할 수 있습니다.

## 운영 체크리스트

- [ ] `pwd`로 현재 위치를 확인하고 `cd`로 이동할 수 있다
- [ ] 절대 경로와 상대 경로의 차이를 설명할 수 있다
- [ ] `mkdir -p`로 중첩 디렉터리를 한 번에 만들 수 있다
- [ ] `cp`, `mv`, `rm`의 차이와 `-r` 옵션의 필요성을 안다
- [ ] 와일드카드 `*` 사용 전 `ls`로 대상을 확인하는 습관이 있다

## 처음 질문으로 돌아가기

- **절대 경로와 상대 경로는 언제 다르게 느껴질까요?** 스크립트에서는 항상 절대 경로가 안전합니다. `~/` 또는 `/home/user/`처럼 시작하면 어디서 실행해도 같은 결과입니다.
- **`cp`, `mv`, `rm`은 각각 어떤 상황에서 쓰면 안전할까요?** 삭제는 되돌릴 수 없으므로 항상 `ls`로 대상 확인 후 실행합니다. 중요한 파일은 `cp`로 백업 후 작업합니다.

## 정리

- Linux 파일 시스템은 `/`(root)에서 시작하는 단일 트리 구조입니다.
- `pwd`, `cd`, `ls`로 현재 위치를 파악하고 이동합니다.
- `mkdir`, `touch`, `cp`, `mv`, `rm`으로 파일과 디렉터리를 조작합니다.
- 삭제는 되돌릴 수 없으므로 항상 대상을 확인한 후 실행합니다.
- 절대 경로는 어디서든 동작하고, 상대 경로는 현재 위치에 의존합니다.

다음 글에서는 **파일 권한과 소유자** — `chmod`, `chown`, `rwx`의 의미를 다룹니다.

## 참고 자료

- [Linux Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html)
- [GNU Coreutils Manual](https://www.gnu.org/software/coreutils/manual/)
- [The Missing Semester - Navigating the Shell](https://missing.csail.mit.edu/2020/course-shell/)
- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Linux CLI 기초 (1/10): CLI와 Shell이란 무엇인가?
- **바이브코딩을 위한 Linux CLI 기초 (2/10): 파일과 디렉터리 다루기 (현재 글)**
- 바이브코딩을 위한 Linux CLI 기초 (3/10): 권한과 소유자 이해하기
- 바이브코딩을 위한 Linux CLI 기초 (4/10): cat, less, head, tail — 파일 내용 보기
- 바이브코딩을 위한 Linux CLI 기초 (5/10): grep, find, xargs — 검색의 삼총사
- 바이브코딩을 위한 Linux CLI 기초 (6/10): pipe와 redirection
- 바이브코딩을 위한 Linux CLI 기초 (7/10): 프로세스 확인과 종료
- 바이브코딩을 위한 Linux CLI 기초 (8/10): 환경변수와 PATH
- 바이브코딩을 위한 Linux CLI 기초 (9/10): 간단한 shell script
- 바이브코딩을 위한 Linux CLI 기초 (10/10): SSH와 원격 서버 접속
<!-- toc:end -->

Tags: 바이브코딩, Linux, CLI, File System, Directory, ls, cp
