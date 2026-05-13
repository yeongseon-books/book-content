---
title: 파일과 디렉터리 다루기
series: linux-cli-101
episode: 2
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
- CLI
- File System
- Directory
- ls
- cp
last_reviewed: '2026-05-12'
seo_description: 파일과 디렉터리 이동, 복사, 삭제를 경로 개념과 함께 정리합니다.
---

# 파일과 디렉터리 다루기

개발자의 일상은 파일을 만들고, 옮기고, 복사하고, 삭제하는 것의 연속입니다. 코드 파일을 정리하고, 설정 파일을 복사하고, 빌드 산출물을 삭제합니다. GUI에서는 드래그 앤 드롭으로 하지만, 서버에서는 모두 명령어입니다.

이 글은 Linux CLI 101 시리즈의 2번째 글입니다.

## 이 글에서 다룰 문제

- 절대 경로와 상대 경로는 언제 다르게 느껴질까요?
- `pwd`, `cd`, `ls`만으로 현재 위치를 어떻게 읽어야 할까요?
- `cp`, `mv`, `rm`은 각각 어떤 상황에서 쓰면 안전할까요?
- 서버에서 파일을 많이 다룰 때 왜 경로 감각이 먼저 필요할까요?

> Linux 파일 시스템은 하나의 뿌리(`/`)에서 시작하는 거대한 나무입니다. 모든 파일과 디렉터리는 이 나무의 가지입니다.

## 머릿속에 먼저 그릴 그림

> Linux 파일 시스템은 하나의 뿌리(`/`)에서 시작하는 거대한 나무입니다. 모든 파일과 디렉터리는 이 나무의 가지입니다.

Windows는 `C:\`, `D:\`처럼 드라이브 문자가 여러 개이지만, Linux는 무조건 `/`(root) 하나에서 시작합니다. USB를 꽂아도, 네트워크 드라이브를 연결해도 모두 이 나무의 어딘가에 매달립니다.

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

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| 절대 경로 | `/`부터 시작하는 전체 경로 | `/home/user/project/main.py` |
| 상대 경로 | 현재 위치 기준 경로 | `./src/main.py`, `../config.yaml` |
| `.` | 현재 디렉터리 | `./run.sh` (현재 폴더의 run.sh) |
| `..` | 상위 디렉터리 | `cd ..` (한 단계 위로) |
| `~` | 홈 디렉터리 | `cd ~` = `cd /home/user` |

## 전과 후

**전 — 경로를 모를 때**

```text
"The file is somewhere... where was it?"
-> Click through folders one by one in the GUI
-> 5 minutes spent
```

**후 — 경로를 아는 CLI 사용자**

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
ls src/
# (empty)
```

## 이 코드에서 봐야 할 것

- `mkdir -p`는 중간 디렉터리가 없어도 한 번에 만듭니다. `-p` 없이 하면 부모 디렉터리가 없을 때 오류가 납니다
- `mv`는 이동과 이름 변경 두 가지 역할을 합니다. 같은 디렉터리 내에서 `mv`하면 이름 변경입니다
- `rm -r`은 재귀적 삭제입니다. 휴지통이 없으므로 복구가 불가능합니다
- `cp`로 디렉터리를 복사할 때는 반드시 `-r` 옵션이 필요합니다

## 자주 하는 실수

### 실수 1. 루트 경로 삭제 명령을 함부로 실행한다

절대로 하면 안 됩니다. 시스템의 모든 파일이 삭제됩니다. 현대 시스템은 `--no-preserve-root` 없이는 거부하지만, `/home`이나 `/var`를 실수로 날릴 수 있습니다.

### 실수 2. 와일드카드 `*`를 확인 없이 쓴다

```bash
rm *.log        # Deletes only .log files — as intended
rm * .log       # Space causes deletion of ALL files, then tries to delete ".log" — disaster
```

삭제 전에 `ls *.log`로 대상을 먼저 확인하세요.

### 실수 3. 경로에 공백이 있는 파일을 따옴표 없이 쓴다

```bash
cp My File.txt backup/     # Error: interpreted as two files "My" and "File.txt"
cp "My File.txt" backup/   # Correct
```

### 실수 4. 상대 경로와 절대 경로를 혼동한다

`cd practice`는 현재 디렉터리에 `practice`가 있을 때만 동작합니다. 어디서든 동작하려면 `cd ~/practice`처럼 절대 경로나 `~`을 씁니다.

### 실수 5. 디렉터리 복사에 재귀 옵션을 빼먹는다

```bash
cp src/ backup/         # Error: "src/ is a directory"
cp -r src/ backup/      # Correct: recursive copy
```

## 실무 적용

- **프로젝트 초기화**: `mkdir -p`로 디렉터리 구조를 한 번에 생성합니다
- **로그 백업**: `cp -r /var/log/app/ /backup/$(date +%F)/`로 날짜별 백업을 만듭니다
- **빌드 정리**: `rm -rf dist/ build/`로 이전 빌드 산출물을 정리합니다
- **설정 복사**: `cp config.yaml config.yaml.bak`으로 변경 전 백업을 둡니다
- **배포 준비**: `mv app-v2.0.tar.gz /opt/releases/`로 릴리스 파일을 이동합니다

## 실무에서는 이렇게 생각한다

파일 조작 명령어는 단순해 보이지만, **삭제는 되돌릴 수 없다**는 점이 핵심입니다. Git으로 관리되는 코드는 복구 가능하지만, 로그 파일이나 데이터베이스 덤프처럼 Git 밖의 파일은 한 번 지우면 끝입니다.

팀에서는 위험한 명령어에 안전장치를 겁니다. `.bashrc`에 `alias rm='rm -i'`를 넣어 삭제 전 확인을 받거나, `trash-cli` 같은 휴지통 도구를 씁니다. 서버에서는 `rm` 대신 `mv`로 임시 폴더에 옮긴 뒤, 일정 기간 후 정리하는 패턴이 안전합니다.

## 체크리스트

- [ ] `pwd`로 현재 위치를 확인하고 `cd`로 이동할 수 있다
- [ ] 절대 경로와 상대 경로의 차이를 설명할 수 있다
- [ ] `mkdir -p`로 중첩 디렉터리를 한 번에 만들 수 있다
- [ ] `cp`, `mv`, `rm`의 차이와 `-r` 옵션의 필요성을 안다
- [ ] 와일드카드 `*` 사용 전 `ls`로 대상을 확인하는 습관이 있다

## 연습 문제

1. `~/practice/linux-cli` 아래에 `logs`, `src`, `backup` 디렉터리를 만들고 `pwd`, `ls -la`로 결과를 확인해 보세요.
2. `notes.txt` 파일을 만든 뒤 복사본을 `backup/`으로 옮기고 이름을 `notes.bak`으로 바꿔 보세요.
3. `rm`, `rmdir`, `rm -r`가 각각 언제 필요한지 실제 예시를 한 줄씩 적어 보세요.

## 정리와 다음 글

- Linux 파일 시스템은 `/`(root)에서 시작하는 단일 트리 구조입니다.
- `pwd`, `cd`, `ls`로 현재 위치를 파악하고 이동합니다.
- `mkdir`, `touch`, `cp`, `mv`, `rm`으로 파일과 디렉터리를 조작합니다.
- 삭제는 되돌릴 수 없으므로 항상 대상을 확인한 후 실행합니다.
- 절대 경로는 어디서든 동작하고, 상대 경로는 현재 위치에 의존합니다.

다음 글에서는 **파일 권한과 소유자** — `chmod`, `chown`, `rwx`의 의미를 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- [CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- **파일과 디렉터리 다루기 (현재 글)**
- 권한과 소유자 이해하기 (예정)
- cat, less, head, tail — 파일 내용 보기 (예정)
- grep, find, xargs — 검색의 삼총사 (예정)
- pipe와 redirection (예정)
- 프로세스 확인과 종료 (예정)
- 환경변수와 PATH (예정)
- 간단한 shell script (예정)
- SSH와 원격 서버 접속 (예정)

<!-- toc:end -->

## 참고 자료

- [Linux Filesystem Hierarchy Standard](https://refspecs.linuxfoundation.org/FHS_3.0/fhs/index.html)
- [GNU Coreutils Manual](https://www.gnu.org/software/coreutils/manual/)
- [The Missing Semester - Navigating the Shell](https://missing.csail.mit.edu/2020/course-shell/)
- [Linux man page - cp, mv, rm](https://man7.org/linux/man-pages/)

Tags: Linux, CLI, File System, Directory, ls, cp
