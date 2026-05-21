---
title: "Linux CLI 101 (3/10): 권한과 소유자 이해하기"
series: linux-cli-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
tags:
- Linux
- Permission
- chmod
- chown
- Security
- File System
last_reviewed: '2026-05-12'
seo_description: Linux 권한과 소유자, chmod와 chown의 기본 감각을 정리합니다.
---

# Linux CLI 101 (3/10): 권한과 소유자 이해하기

이 글은 Linux CLI 101 시리즈의 3번째 글입니다.

서버에서 스크립트를 실행하려고 `./deploy.sh`를 입력하면 "Permission denied"가 나옵니다. 파일은 분명 존재하는데 왜 실행이 안 될까요? 실행 권한(x)이 없기 때문입니다.


![Linux CLI 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/03/03-01-big-picture.ko.png)
*Linux CLI 101 3장 흐름 개요*

## 먼저 던지는 질문

- `r`, `w`, `x` 권한은 파일과 디렉터리에서 각각 어떻게 다르게 동작할까요?
- 소유자, 그룹, 그 외 사용자 구분을 왜 알아야 할까요?
- `chmod`와 `chown`은 각각 무엇을 바꾸는 명령일까요?

## 머릿속에 먼저 그릴 그림

> 파일 권한은 자물쇠 세 개가 달린 문입니다. 주인(owner)용, 같은 팀(group)용, 나머지(others)용 자물쇠가 각각 있고, 각 자물쇠에는 읽기(r), 쓰기(w), 실행(x) 세 가지 열쇠가 있습니다.

```text
-rwxr-xr--
│└┬┘└┬┘└┬┘
│ │  │  └── others: r-- (read only)
│ │  └── group:  r-x (read+execute)
│ └── owner:  rwx (read+write+execute)
└── file type (-: regular file, d: directory)
```

## 핵심 개념

| 기호 | 의미 | 숫자 | 파일 | 디렉터리 |
|---|---|---|---|---|
| r | 읽기 | 4 | 내용 읽기 | 목록 보기(ls) |
| w | 쓰기 | 2 | 내용 수정 | 파일 생성/삭제 |
| x | 실행 | 1 | 프로그램 실행 | 디렉터리 진입(cd) |
| - | 권한 없음 | 0 | — | — |

## 전과 후

**Before (권한을 모를 때)**

```bash
./deploy.sh
# bash: ./deploy.sh: Permission denied
chmod 777 deploy.sh    # "Just 777 if it doesn't work" — security hole
```

**After (권한을 이해할 때)**

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
ls -l secret.txt
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

## 이 코드에서 봐야 할 것

- `ls -l`의 첫 번째 열이 권한 문자열이고 10글자입니다(유형 1 + 권한 9)
- 숫자 방식은 전체를 한 번에 설정하고, 기호 방식은 부분만 변경합니다
- 디렉터리의 `x` 권한은 "실행"이 아니라 "진입"을 의미합니다
- `chown`은 보통 `sudo`가 필요합니다

## 자주 하는 실수

### 실수 1. 권한 문제를 과하게 열어서 해결한다

777은 모든 사용자에게 모든 권한을 주는 것입니다. 웹 서버 파일에 777을 주면 아무나 파일을 수정할 수 있는 보안 취약점이 됩니다. 최소 권한 원칙을 따르세요.

### 실수 2. 디렉터리 실행 권한의 의미를 놓친다

디렉터리에서 `x`는 "진입 허용"입니다. `r`만 있고 `x`가 없으면 `ls`로 목록은 보이지만 `cd`로 들어갈 수 없습니다. 파일에 접근하려면 경로상의 모든 디렉터리에 `x`가 있어야 합니다.

### 실수 3. 그룹 권한을 무시한다

혼자 작업하면 owner 권한만 신경 쓰지만, 팀 서버에서는 같은 그룹 소속 개발자가 파일을 읽거나 수정할 수 있어야 합니다. 적절한 group 설정이 없으면 동료가 파일을 열 수 없습니다.

### 실수 4. 재귀 권한 변경에서 파일과 디렉터리를 구분하지 않는다

```bash
chmod -R 755 project/   # All files get execute permission — dangerous
# Correct approach:
find project/ -type d -exec chmod 755 {} \;   # Directories only
find project/ -type f -exec chmod 644 {} \;   # Files only
```

### 실수 5. 기본 권한 마스크를 모른 채 파일을 만든다

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

## 체크리스트

- [ ] `rwxr-xr--`를 보고 owner/group/others 권한을 말할 수 있다
- [ ] `chmod 755`가 어떤 권한인지 계산할 수 있다
- [ ] 기호 방식(`u+x`, `g-w`)으로 부분 변경을 할 수 있다
- [ ] 디렉터리의 `x` 권한이 "진입"을 의미한다는 것을 안다
- [ ] `chmod 777`을 쓰면 안 되는 이유를 설명할 수 있다

## 연습 문제

1. 빈 파일 하나를 만든 뒤 `ls -l`로 현재 권한을 확인하고, `chmod 600`, `chmod 644`, `chmod 755`를 차례로 적용해 차이를 기록해 보세요.
2. 디렉터리 하나를 만들고 `chmod 700`과 `chmod 755`를 바꿔 가며 접근 가능 범위를 설명해 보세요.
3. `chown`이 왜 보통 `sudo`와 함께 쓰이는지 한 문단으로 정리해 보세요.

## 정리와 다음 글

- Linux 파일 권한은 owner/group/others × r/w/x의 3×3 구조입니다.
- 숫자 방식(644, 755)은 전체를 설정하고, 기호 방식(u+x)은 부분을 변경합니다.
- 디렉터리의 x 권한은 진입 허용이며, 경로상 모든 디렉터리에 필요합니다.
- 최소 권한 원칙을 따르고, 777은 절대 쓰지 않습니다.
- `chown`으로 소유자를 바꾸려면 root 권한이 필요합니다.

다음 글에서는 **파일 내용을 확인하는 명령어** — `cat`, `less`, `head`, `tail`을 다룹니다.


## 실전 CLI 운영 패턴

### 명령을 순서가 아니라 데이터 흐름으로 설계하기
CLI 작업이 길어질수록 핵심은 명령 개수보다 데이터 흐름입니다. 예를 들어 로그에서 오류 패턴을 찾고, 원인 프로세스를 좁히고, 마지막으로 자동 조치 후보를 만드는 과정은 하나의 파이프라인으로 보는 편이 안정적입니다. 다음 흐름은 실제 운영 환경에서 자주 쓰는 형태입니다.

```bash
journalctl -u my-api --since "10 min ago" \
  | grep -E "ERROR|CRITICAL" \
  | awk '{print $1" "$2" "$3" "$NF}' \
  | sort \
  | uniq -c \
  | sort -nr
```

이 파이프라인의 목적은 "원시 로그"를 "빈도 기반 우선순위 목록"으로 바꾸는 것입니다. 앞쪽 명령은 후보를 넓게 모으고, 뒤쪽 명령은 노이즈를 줄여 의사결정 가능한 형태로 압축합니다. 운영자가 먼저 이 구조를 머릿속에 그려두면, 중간에 도구를 바꿔도 전체 전략은 유지됩니다.

### 안전한 one-liner와 검증 루틴
한 줄 명령은 빠르지만 위험합니다. 삭제, 이동, 권한 변경처럼 되돌리기 어려운 작업은 항상 dry-run 단계를 먼저 둡니다.

```bash
find ./tmp-exports -type f -mtime +7 -print
find ./tmp-exports -type f -mtime +7 -print0 | xargs -0 rm -f
```

첫 줄은 영향 범위를 확인하는 단계이고, 둘째 줄은 실제 실행입니다. 이 두 단계를 분리하면 휴먼 에러를 크게 줄일 수 있습니다. 특히 공백이 있는 파일명을 다룰 때는 `-print0`와 `xargs -0` 조합을 기본값으로 두는 편이 안전합니다.

### 작은 셸 스크립트를 운영 도구로 키우기
반복 작업은 즉시 스크립트로 승격하는 것이 좋습니다. 아래 예시는 "서비스 상태 점검 + 이상 시 로그 추출"을 자동화한 최소 형태입니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

service_name="my-api"
window="5 min ago"

if systemctl is-active --quiet "$service_name"; then
  echo "[PASS] $service_name is active"
else
  echo "[FAIL] $service_name is not active"
  journalctl -u "$service_name" --since "$window" | tail -n 80
  exit 1
fi
```

여기서 중요한 포인트는 세 가지입니다. 첫째, `set -euo pipefail`로 실패를 조기에 표면화합니다. 둘째, 하드코딩 값을 변수로 끌어올려 재사용성을 높입니다. 셋째, 실패 시 바로 조사 가능한 로그를 출력해 복구 시간을 줄입니다. 이런 작은 스크립트들이 쌓이면 팀의 운영 품질이 표준화됩니다.

### 파이프 결과를 파일과 결합해 재현성 확보하기
문제 분석은 재현 가능해야 합니다. 표준 출력으로만 보면 같은 분석을 다시 하기 어렵기 때문에 중간 결과를 파일로 남기는 습관이 유용합니다.

```bash
ps aux | grep "python" | grep -v grep | tee /tmp/python-proc.txt
cut -d' ' -f1-12 /tmp/python-proc.txt > /tmp/python-proc-compact.txt
```

`tee`는 화면 확인과 파일 저장을 동시에 처리하므로 탐색 속도와 재현성을 함께 확보합니다. 이후 팀원이 같은 파일을 기반으로 추가 분석을 이어갈 수 있어 협업 비용이 줄어듭니다.

## 자동화 품질을 높이는 셸 체크포인트

### 입력 검증과 종료 코드 계약
셸 스크립트가 팀 도구가 되려면 실패 방식이 예측 가능해야 합니다. 인자 검증과 종료 코드 계약을 명시하면 CI와 운영 스크립트가 안전하게 연동됩니다.

```bash
#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "usage: $0 <log_dir> <keyword>"
}

if [ "$#" -ne 2 ]; then
  usage
  exit 64
fi

log_dir="$1"
keyword="$2"

if [ ! -d "$log_dir" ]; then
  echo "directory not found: $log_dir"
  exit 66
fi

if grep -R --line-number "$keyword" "$log_dir" >/tmp/match.out; then
  echo "match found"
  exit 0
else
  echo "no match"
  exit 1
fi
```

여기서 `64`, `66` 같은 종료 코드는 호출자에게 실패 원인을 분류해 전달합니다. 사람이 읽는 메시지와 기계가 읽는 코드가 분리되어 있으면 자동화 파이프라인에서 분기 처리하기 쉽습니다.

### 파이프라인 병목 찾기
복잡한 파이프라인은 체감만으로 병목을 찾기 어렵습니다. 각 단계 앞뒤에 타임스탬프를 찍거나 임시 파일에 분리 저장해 어느 단계가 느린지 확인합니다.

```bash
time grep -R "ERROR" /var/log/myapp > /tmp/step1.txt
time cut -d' ' -f1-8 /tmp/step1.txt > /tmp/step2.txt
time sort /tmp/step2.txt | uniq -c | sort -nr > /tmp/step3.txt
```

이 방식은 단순하지만 효과가 큽니다. 어떤 단계가 CPU 중심인지 I/O 중심인지 빠르게 감을 잡을 수 있고, 이후 `awk` 대체, 병렬화, 입력 축소 같은 최적화 방향을 정하기 쉬워집니다.

### 재사용 가능한 함수형 스니펫
긴 스크립트에서도 기능 단위를 함수로 분리하면 테스트와 유지보수가 쉬워집니다.

```bash
collect_pids() {
  pgrep -f "$1" || true
}

kill_gracefully() {
  local pid="$1"
  kill -TERM "$pid"
  sleep 2
  kill -0 "$pid" 2>/dev/null && kill -KILL "$pid" || true
}
```

함수 단위로 쪼개면 시나리오별 검증이 가능해집니다. 예를 들어 종료 신호가 정상 처리되는지, 남은 프로세스가 있는지, 재시작 로직이 중복 실행되는지 등을 독립적으로 점검할 수 있습니다.

## 실무 시나리오: 권한 사고를 예방하는 운영 기준

권한 문제는 "명령이 안 된다"에서 끝나지 않고, 서비스 장애와 보안 사고로 이어집니다. 실무에서는 파일 접근 실패를 기능 버그로 오해하는 경우가 많습니다. 그래서 운영자는 애플리케이션 로그를 보기 전에 권한 모델부터 확인합니다.

```bash
namei -l /opt/my-app/current/conf/app.env

# 예상 출력
# f: /opt/my-app/current/conf/app.env
# drwxr-xr-x root   root   /
# drwxr-xr-x root   root   opt
# drwxr-xr-x deploy deploy my-app
# lrwxrwxrwx deploy deploy current -> /opt/my-app/releases/prod-20260521
# drwxr-xr-x deploy deploy conf
# -rw-r----- deploy deploy app.env
```

경로 구성 요소 중 하나라도 실행 권한(`x`)이 없으면 파일에 접근할 수 없습니다. `namei -l`은 이 문제를 단계별로 보여주기 때문에 권한 디버깅에서 매우 효율적입니다.

### 숫자 권한과 의미를 연결하기

`chmod 640`, `750` 같은 숫자를 기계적으로 외우기보다 "누가 읽고, 누가 실행하는가"로 해석해야 합니다.

```bash
chmod 640 /opt/my-app/current/conf/app.env
chmod 750 /opt/my-app/current/bin/start.sh
ls -l /opt/my-app/current/conf/app.env /opt/my-app/current/bin/start.sh

# 예상 출력
# -rw-r----- 1 deploy deploy 512 May 21 13:22 /opt/my-app/current/conf/app.env
# -rwxr-x--- 1 deploy deploy 824 May 21 13:20 /opt/my-app/current/bin/start.sh
```

이 설정은 소유자에게 실행/읽기 권한을 주고, 그룹에는 필요한 최소 권한만 부여합니다. `others`를 닫아두면 실수로 민감 정보가 노출되는 경우를 줄일 수 있습니다.

### setuid/setgid/sticky bit를 운영 관점으로 이해하기

특수 비트는 시험 문제가 아니라 운영 정책과 직결됩니다.

```bash
# 공유 디렉터리에서 파일 소유 그룹을 고정
chmod 2775 /srv/shared

# /tmp 같은 공용 디렉터리 보호
chmod 1777 /tmp

ls -ld /srv/shared /tmp
# drwxrwsr-x 2 deploy ops 4096 May 21 13:30 /srv/shared
# drwxrwxrwt 20 root root 4096 May 21 12:00 /tmp
```

`2775`의 `2`는 setgid로, 해당 디렉터리에서 생성되는 파일이 디렉터리 그룹을 따르게 합니다. 팀 공동 작업에서 그룹 일관성을 유지할 때 유용합니다.

### ACL로 최소권한을 세밀하게 적용하기

기본 권한 비트만으로 부족하면 ACL을 사용합니다.

```bash
setfacl -m u:jenkins:rX /opt/my-app/current/conf
setfacl -m u:jenkins:r-- /opt/my-app/current/conf/app.env
getfacl /opt/my-app/current/conf/app.env

# 예상 출력 일부
# user::rw-
# user:jenkins:r--
# group::r--
# mask::r--
# other::---
```

CI 계정에 필요한 읽기 권한만 주면 배포 자동화는 유지하면서 보안 노출을 줄일 수 있습니다.

### 권한 변경 자동화 스크립트 예시

```bash
#!/usr/bin/env bash
set -euo pipefail

target="/opt/my-app/releases/prod-20260521"

chown -R deploy:deploy "$target"
find "$target" -type d -exec chmod 755 {} \;
find "$target" -type f -name '*.sh' -exec chmod 750 {} \;
find "$target" -type f ! -name '*.sh' -exec chmod 640 {} \;

# 비밀 파일은 더 엄격하게
chmod 600 "$target/conf/secrets.env"
```

이 스크립트의 목적은 "권한을 잘 맞춘다"가 아니라, **항상 같은 규칙을 재현**하는 것입니다. 수동 변경을 줄이면 환경 간 차이가 줄고, 장애 원인 추적이 빨라집니다.

### systemd 서비스 계정과 권한 일치시키기

서비스가 어떤 사용자로 실행되는지와 파일 권한이 맞지 않으면 시작 직후 실패합니다.

```ini
# /etc/systemd/system/my-app.service
[Service]
User=deploy
Group=deploy
WorkingDirectory=/opt/my-app/current
ExecStart=/opt/my-app/current/bin/start.sh
EnvironmentFile=/opt/my-app/current/conf/app.env
```

설정 후에는 아래처럼 로그를 확인합니다.

```bash
systemctl daemon-reload
systemctl restart my-app
journalctl -u my-app -n 20 --no-pager
```

여기서 `Permission denied`가 보이면 코드보다 먼저 권한 체계를 확인하는 것이 맞습니다.

## 운영 점검 플레이북

실무에서 CLI 지식은 "명령을 외우는 능력"보다 "실수 가능성을 줄이는 절차"로 드러납니다. 아래 플레이북은 작업 전에 위험을 줄이고, 작업 후 검증을 빠뜨리지 않기 위한 최소 절차입니다.

### 1) 작업 전 컨텍스트 확인

```bash
whoami
hostname
pwd
date

# 예상 출력
# deploy
# prod-api-01
# /opt/my-app
# Thu May 21 15:24:18 KST 2026
```

같은 명령이라도 서버와 경로가 다르면 결과가 완전히 달라집니다. 컨텍스트 확인은 사소해 보이지만 잘못된 환경 조작을 막는 첫 방어선입니다.

### 2) 영향 범위 먼저 출력

```bash
# 예시: 후보만 확인
find ./target -type f -name '*.log' -mtime +7 -print
```

삭제·이동·권한 변경처럼 파괴적일 수 있는 작업은 항상 후보 목록 출력이 선행되어야 합니다. "실행 전에 눈으로 검토"가 자동화 품질의 핵심입니다.

### 3) 파이프 체인으로 증거를 압축

```bash
journalctl -u my-api --since '20 min ago' --no-pager   | grep -E 'ERROR|CRITICAL|timeout|5[0-9]{2}'   | awk '{print $1, $2, $3, $NF}'   | sort   | uniq -c   | sort -nr
```

`grep -E` 정규식은 노이즈를 줄이는 첫 단계입니다. 빈도 집계(`uniq -c`)까지 연결하면 우선순위를 빠르게 정할 수 있습니다.

### 4) systemd 상태와 애플리케이션 로그를 함께 확인

```bash
systemctl status my-api --no-pager | sed -n '1,15p'
journalctl -u my-api -n 80 --no-pager
```

프로세스가 살아 있어도 서비스가 실패 상태일 수 있고, 반대로 서비스는 active인데 내부 오류가 계속 발생할 수 있습니다. 두 관점을 동시에 봐야 원인 추적이 정확해집니다.

### 5) Bash 스크립트로 반복 점검 표준화

```bash
#!/usr/bin/env bash
set -euo pipefail

svc="my-api"
window='10 min ago'

printf '[INFO] host=%s user=%s time=%s
' "$(hostname)" "$(whoami)" "$(date '+%F %T')"

if systemctl is-active --quiet "$svc"; then
  echo '[PASS] service active'
else
  echo '[FAIL] service inactive'
fi

journalctl -u "$svc" --since "$window" --no-pager   | grep -E 'ERROR|CRITICAL|timeout|Failed' || true
```

자동화의 목적은 사람이 바뀌어도 같은 품질의 점검 결과를 얻는 것입니다. 이 원칙이 지켜지면 장애 대응 시간과 커뮤니케이션 비용이 함께 줄어듭니다.


## 실전 점검 로그 예시

아래 예시는 실제 운영에서 자주 보는 "점검 출력 형태"를 축약한 것입니다. 중요한 것은 특정 명령을 그대로 복사하는 것이 아니라, 출력을 근거로 다음 판단을 연결하는 습관입니다.

```bash
# 서비스 상태 + 최근 오류를 한 번에 수집
systemctl is-active my-api
journalctl -u my-api --since '5 min ago' --no-pager   | grep -E 'ERROR|CRITICAL|timeout|Failed'   | tail -n 20

# 예상 출력
# active
# 2026-05-21 15:31:10 ERROR timeout while calling payment API
# 2026-05-21 15:31:12 CRITICAL worker exited unexpectedly
```

```bash
# 프로세스/포트/파일 핸들 점검
ps -ef | grep -E 'my-api|gunicorn' | grep -v grep
ss -lntp | grep -E ':8080|:80|:443'
lsof -p "$(pgrep -f my-api | head -n 1)" | wc -l

# 예상 출력 예시
# deploy 18231 1  ... /opt/my-api/current/bin/start.sh
# LISTEN 0 4096 0.0.0.0:8080 ... users:(("python3",pid=18231,fd=12))
# 412
```

이런 출력들을 시계열로 저장해 두면 재발 시 비교가 쉬워지고, "지금이 평소와 어떻게 다른가"를 빠르게 설명할 수 있습니다. 결국 CLI 실무 역량은 명령 자체보다 **증거 기반 판단 루틴**을 안정적으로 반복하는 능력입니다.


### 운영 메모: 실패 후 복구 순서

실패가 발생했을 때는 "원인 추정 -> 즉시 재시작"보다 "상태 확인 -> 증거 수집 -> 최소 조치" 순서가 안전합니다.

```bash
systemctl status my-api --no-pager | sed -n '1,12p'
journalctl -u my-api -n 50 --no-pager | grep -E 'ERROR|CRITICAL|timeout|Failed' || true
```

상태와 로그를 먼저 남겨 두면, 재시작 후 증거가 사라져도 회고와 재발 방지 작업을 진행할 수 있습니다.


### 운영 메모: 변경 후 검증 체크

권한/조회/환경값 변경 직후에는 기능 테스트만 하지 말고 시스템 레벨 검증을 함께 수행합니다.

```bash
whoami
hostname
systemctl is-active my-api
journalctl -u my-api -n 20 --no-pager
```

짧은 검증 루틴이라도 매번 남기면, 장애 발생 시 "무엇을 언제 바꿨는지"를 빠르게 복원할 수 있습니다.


## 처음 질문으로 돌아가기

- **`r`, `w`, `x` 권한은 파일과 디렉터리에서 각각 어떻게 다르게 동작할까요?**
  - 본문의 기준은 권한과 소유자 이해하기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **소유자, 그룹, 그 외 사용자 구분을 왜 알아야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`chmod`와 `chown`은 각각 무엇을 바꾸는 명령일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linux CLI 101 (1/10): CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): 파일과 디렉터리 다루기](./02-files-and-directories.md)
- **권한과 소유자 이해하기 (현재 글)**
- cat, less, head, tail — 파일 내용 보기 (예정)
- grep, find, xargs — 검색의 삼총사 (예정)
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

- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko
Tags: Linux, Permission, chmod, chown, Security, File System
