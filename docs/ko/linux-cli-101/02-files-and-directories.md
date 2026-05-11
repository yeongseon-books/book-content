---
title: 파일과 디렉터리 다루기
series: linux-cli-101
episode: 2
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
- CLI
- File System
- Directory
- ls
- cp
last_reviewed: '2026-05-04'
seo_description: Linux 파일 시스템은 하나의 뿌리(/)에서 시작하는 거대한 나무입니다. 모든 파일과 디렉터리는 이 나무의 가지입니다.
---

# 파일과 디렉터리 다루기

> Linux CLI 101 시리즈 (2/10)

---


## 이 글에서 다룰 문제

개발자의 일상은 파일을 만들고, 옮기고, 복사하고, 삭제하는 것의 연속입니다. 코드 파일을 정리하고, 설정 파일을 복사하고, 빌드 산출물을 삭제합니다. GUI에서는 드래그 앤 드롭으로 하지만, 서버에서는 모두 명령어입니다.

> 배포 서버에서 로그 파일을 백업하라는 요청을 받았습니다. `/var/log/app/` 안에 있는 파일 50개를 `/backup/2026-05-04/`로 복사해야 합니다. 마우스는 없습니다.

이 작업을 `cp -r`로 3초 만에 끝내려면, 파일 시스템 구조와 기본 명령어를 알아야 합니다.

## Mental Model

> Linux 파일 시스템은 하나의 뿌리(`/`)에서 시작하는 거대한 나무입니다. 모든 파일과 디렉터리는 이 나무의 가지입니다.

Windows는 `C:\`, `D:\`처럼 드라이브 문자가 여러 개이지만, Linux는 무조건 `/`(root) 하나에서 시작합니다. USB를 꽂아도, 네트워크 드라이브를 연결해도 모두 이 나무의 어딘가에 매달립니다.

```text
/                       ← 뿌리(root)
├── home/               ← 사용자 홈 디렉터리
│   └── user/           ← 내 작업 공간 (~)
├── etc/                ← 시스템 설정 파일
├── var/                ← 로그, 캐시 등 가변 데이터
├── tmp/                ← 임시 파일
└── usr/                ← 사용자 프로그램
    └── bin/            ← 실행 파일
```

## 핵심 개념

| 용어 | 설명 | 예시 |
|---|---|---|
| 절대 경로 | `/`부터 시작하는 전체 경로 | `/home/user/project/main.py` |
| 상대 경로 | 현재 위치 기준 경로 | `./src/main.py`, `../config.yaml` |
| `.` | 현재 디렉터리 | `./run.sh` (현재 폴더의 run.sh) |
| `..` | 상위 디렉터리 | `cd ..` (한 단계 위로) |
| `~` | 홈 디렉터리 | `cd ~` = `cd /home/user` |

## Before / After

**Before (경로를 모를 때)**

```text
"파일이 어딘가에 있는데... 어디였지?"
→ GUI에서 폴더를 하나씩 클릭하며 찾기
→ 5분 소요
```

**After (경로를 아는 CLI 사용자)**

```bash
find /var/log -name "error*.log" -mtime -1
# 1초 만에 어제 이후 생성된 에러 로그를 전부 찾음
```

## 단계별 실습

### Step 1. 현재 위치 확인

```bash
pwd
# 출력 예: /home/user
```

`pwd`(print working directory)는 지금 내가 어디에 있는지 보여줍니다.

### Step 2. 디렉터리 이동

```bash
cd /tmp           # 절대 경로로 이동
cd ~              # 홈으로 이동
mkdir -p ~/practice/linux-cli   # 연습 디렉터리 생성
cd ~/practice/linux-cli         # 연습 디렉터리로 이동
pwd
# 출력: /home/user/practice/linux-cli
```

### Step 3. 파일과 디렉터리 만들기

```bash
touch hello.txt               # 빈 파일 생성
mkdir src                     # 디렉터리 생성
mkdir -p src/utils/helpers    # 중간 경로까지 한 번에 생성
ls -la
# hello.txt, src/ 가 보임
```

### Step 4. 복사, 이동, 이름 바꾸기

```bash
cp hello.txt hello-backup.txt          # 파일 복사
mv hello-backup.txt src/               # 파일 이동
mv src/hello-backup.txt src/backup.txt # 이름 변경
ls src/
# backup.txt  utils/
```

### Step 5. 삭제

```bash
rm src/backup.txt              # 파일 삭제
rmdir src/utils/helpers        # 빈 디렉터리 삭제
rm -r src/utils                # 디렉터리와 내용물 삭제
ls src/
# (비어 있음)
```

## 이 코드에서 봐야 할 것

- `mkdir -p`는 중간 디렉터리가 없어도 한 번에 만듭니다. `-p` 없이 하면 부모 디렉터리가 없을 때 오류가 납니다
- `mv`는 이동과 이름 변경 두 가지 역할을 합니다. 같은 디렉터리 내에서 `mv`하면 이름 변경입니다
- `rm -r`은 재귀적 삭제입니다. 휴지통이 없으므로 복구가 불가능합니다
- `cp`로 디렉터리를 복사할 때는 반드시 `-r` 옵션이 필요합니다

## 자주 하는 실수

### 실수 1. `rm -rf /`를 실행한다

절대로 하면 안 됩니다. 시스템의 모든 파일이 삭제됩니다. 현대 시스템은 `--no-preserve-root` 없이는 거부하지만, `/home`이나 `/var`를 실수로 날릴 수 있습니다.

### 실수 2. 와일드카드 `*`를 확인 없이 쓴다

```bash
rm *.log        # .log 파일만 삭제 — 의도대로
rm * .log       # 공백 때문에 모든 파일 삭제 후 ".log" 삭제 시도 — 재앙
```

삭제 전에 `ls *.log`로 대상을 먼저 확인하세요.

### 실수 3. 경로에 공백이 있는 파일을 따옴표 없이 쓴다

```bash
cp My File.txt backup/     # 오류: "My"와 "File.txt" 두 파일로 해석
cp "My File.txt" backup/   # 정상
```

### 실수 4. 상대 경로와 절대 경로를 혼동한다

`cd practice`는 현재 디렉터리에 `practice`가 있을 때만 동작합니다. 어디서든 동작하려면 `cd ~/practice`처럼 절대 경로나 `~`을 씁니다.

### 실수 5. `cp`로 디렉터리를 복사할 때 `-r`을 빼먹는다

```bash
cp src/ backup/         # 오류: "src/는 디렉터리입니다"
cp -r src/ backup/      # 정상: 재귀 복사
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

## 정리 · 다음 글

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
- cat, less, head, tail (예정)
- grep, find, xargs (예정)
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
