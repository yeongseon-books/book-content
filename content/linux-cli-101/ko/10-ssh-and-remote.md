---
title: "Linux CLI 101 (10/10): SSH와 원격 서버 접속"
series: linux-cli-101
episode: 10
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
- SSH
- Remote
- scp
- Security
- Server
last_reviewed: '2026-05-15'
seo_description: SSH 접속, 키 인증, scp와 rsync를 통한 원격 작업의 기본을 정리합니다.
---

# Linux CLI 101 (10/10): SSH와 원격 서버 접속

개발한 코드를 서버에 배포하고, 서버 로그를 확인하고, 데이터베이스에 접속하는 일은 모두 원격 접속에서 시작됩니다. SSH는 이 모든 원격 작업의 기반입니다.

![Linux CLI 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/linux-cli-101/10/10-01-big-picture.ko.png)
*Linux CLI 101 10장 흐름 개요*

## 먼저 던지는 질문

- SSH는 Telnet 대신 왜 기본 원격 접속 수단이 되었을까요?
- 비밀번호 인증과 키 기반 인증은 어떤 차이를 만들까요?
- `~/.ssh/config`는 접속 흐름을 어떻게 단순하게 만들까요?

## 머릿속에 먼저 그릴 그림

> SSH는 두 컴퓨터 사이에 암호화된 터널을 만드는 것입니다. 키 기반 인증은 비밀번호 대신 자물쇠(공개 키)와 열쇠(비밀 키) 쌍을 쓰는 방식입니다. 서버에 자물쇠를 달아두고, 내 컴퓨터의 열쇠로 열면 비밀번호 없이 접속됩니다.

```text
[My Computer]                       [Server]
 Private key (~/.ssh/id_ed25519) <-> Public key (~/.ssh/authorized_keys)
          |                              |
    "Open with this key"          "Lock matches — access granted"
          └──── Encrypted SSH tunnel ────┘
```

## 핵심 개념

| 용어 | 설명 | 위치 |
|---|---|---|
| 공개 키 | 서버에 등록하는 자물쇠 | `~/.ssh/id_ed25519.pub` |
| 비밀 키 | 내 컴퓨터에 보관하는 열쇠 | `~/.ssh/id_ed25519` |
| authorized_keys | 서버가 허용하는 공개 키 목록 | `~/.ssh/authorized_keys` |
| ssh-agent | 비밀 키를 메모리에 캐시하여 비밀번호 재입력 방지 | 프로세스 |
| known_hosts | 접속한 서버의 지문(fingerprint) 기록 | `~/.ssh/known_hosts` |

## 전과 후

**전 — 비밀번호 인증**

```bash
ssh user@192.168.1.100
# Type password every time
# Vulnerable to brute-force attacks
# Cannot automate (putting passwords in scripts is a security incident)
```

**후 — 키 기반 인증 + config**

```bash
ssh prod-server
# Instant login without a password
# Automatable (CI/CD deploys over SSH)
# Brute-force impossible
```

## 단계별 실습

### 1단계. 원격 접속용 키 만들기

```bash
ssh-keygen -t ed25519 -C "user@example.com"
# Enter file: (press Enter for default path)
# Enter passphrase: (recommended for security)

ls -la ~/.ssh/
# id_ed25519        <- Private key (never share)
# id_ed25519.pub    <- Public key (register on server)
```

### 2단계. 서버에 공개 키 등록

```bash
# Method 1: ssh-copy-id (easiest)
ssh-copy-id user@192.168.1.100

# Method 2: manual copy
cat ~/.ssh/id_ed25519.pub | ssh user@192.168.1.100 \
    'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'

# Now you can connect without a password
ssh user@192.168.1.100
```

### 3단계. 접속 별칭 설정

```bash
cat > ~/.ssh/config << 'EOF'
Host dev-server
    HostName 192.168.1.100
    User developer
    Port 22
    IdentityFile ~/.ssh/id_ed25519

Host prod-server
    HostName 10.0.1.50
    User deploy
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
EOF

chmod 600 ~/.ssh/config

# Connect using aliases
ssh dev-server          # = ssh developer@192.168.1.100
ssh prod-server         # = ssh deploy@10.0.1.50 -p 2222
```

### 4단계. 파일 전송

```bash
# scp: copy single files or directories
scp app.tar.gz dev-server:/opt/releases/          # Upload
scp dev-server:/var/log/app.log ./                 # Download
scp -r project/ dev-server:/home/developer/        # Copy directory

# rsync: incremental sync (transfers only changes)
rsync -avz project/ dev-server:/home/developer/project/
# -a: archive (preserves permissions, timestamps)
# -v: verbose
# -z: compressed transfer
```

### 5단계. 원격 명령 실행

```bash
# Run a command remotely without opening a session
ssh dev-server 'df -h'                        # Check disk usage
ssh dev-server 'tail -5 /var/log/app.log'     # Last 5 log lines

# Run multiple commands
ssh dev-server << 'EOF'
cd /opt/app
git pull
sudo systemctl restart app
echo "Deploy done"
EOF
```

## 이 코드에서 봐야 할 것

- `ssh-keygen -t ed25519`에서 ed25519는 현재 권장되는 알고리즘입니다. RSA보다 짧고 빠릅니다
- `~/.ssh/` 디렉터리와 키 파일의 권한이 중요합니다. 느슨하면 SSH가 거부합니다
- `rsync`는 `scp`와 달리 변경분만 전송하여 대용량 디렉터리 동기화에 효율적입니다
- SSH config의 `Host`는 별칭이며, `HostName`이 실제 주소입니다

## 자주 하는 실수

### 실수 1. 비밀 키를 공유하거나 저장소에 커밋한다

비밀 키(`id_ed25519`)는 절대 다른 사람에게 보내거나 Git에 올리면 안 됩니다. 공유하는 것은 공개 키(`.pub`)뿐입니다.

### 실수 2. 접속용 키 파일 권한이 느슨하다

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 ~/.ssh/config
# Looser permissions cause SSH to reject the key
```

### 실수 3. 호스트 지문 경고를 무시한다

"WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED" 메시지가 나오면, 서버가 바뀌었거나 중간자 공격일 수 있습니다. 서버를 확인한 후 `ssh-keygen -R hostname`으로 이전 지문을 삭제합니다.

### 실수 4. 비밀번호 인증을 비활성화하지 않는다

키 기반 인증을 설정한 후에도 비밀번호 인증이 켜져 있으면 브루트포스 공격에 노출됩니다. `/etc/ssh/sshd_config`에서 `PasswordAuthentication no`를 설정하세요.

### 실수 5. 접속 설정 파일을 쓰지 않는다

매번 `ssh -i ~/.ssh/mykey -p 2222 user@long-hostname.example.com`을 타이핑하는 것은 비효율적이고 실수를 유발합니다. config에 별칭을 만드세요.

## 실무 적용

- **서버 배포**: `ssh prod 'cd /opt/app && git pull && sudo systemctl restart app'`
- **CI/CD**: GitHub Actions에서 SSH 키로 서버에 자동 배포합니다
- **포트 포워딩**: `ssh -L 5432:localhost:5432 db-server`로 원격 DB에 로컬처럼 접속합니다
- **파일 동기화**: `rsync -avz dist/ prod:/var/www/html/`로 웹 배포합니다
- **점프 호스트**: `ssh -J bastion internal-server`로 방화벽 뒤 서버에 접근합니다

## 실무에서는 이렇게 생각한다

SSH는 서버 관리의 기본이지만, 직접 SSH로 서버에 들어가서 작업하는 횟수가 적을수록 인프라가 성숙한 것입니다. 좋은 팀은 CI/CD 파이프라인으로 배포하고, 모니터링 도구로 로그를 보고, Infrastructure as Code로 서버를 관리합니다.

그렇더라도 SSH를 모르면 안 됩니다. CI/CD가 실패했을 때, 모니터링이 안 잡는 문제가 생겼을 때, 결국 "서버에 직접 들어가서 확인"하는 것이 마지막 수단이기 때문입니다. SSH는 평소에는 쓰지 않되, 긴급 상황에서 반드시 쓸 줄 알아야 하는 기술입니다.

## 문제가 생기면 먼저 이렇게 확인하세요

- `Permission denied (publickey)`가 나오면 서버 방화벽보다 키 경로와 권한부터 보세요. `chmod 700 ~/.ssh`, `chmod 600 ~/.ssh/id_ed25519`, `ssh -v host` 조합으로 확인하면 원인이 빨리 드러납니다.
- `WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED`를 무시하지 말고 서버가 실제로 교체됐는지 먼저 검증하세요. 확인 후 `ssh-keygen -R host`로 예전 지문을 지우는 순서가 안전합니다.
- `scp`나 `rsync`가 안 되면 SSH 별칭에 포트와 사용자 정보가 맞는지 확인하세요. 특히 운영 서버는 22번이 아닌 포트를 쓰는 경우가 많아 연결 실패를 파일 경로 문제로 오해하기 쉽습니다.
- 원격 명령이 절반만 실행되면 셸 초기화 파일이나 `sudo` 프롬프트가 중간에 끼어든 경우가 많습니다. 자동화 경로에서는 비대화형 실행을 전제로 명령을 다시 나누어 보는 편이 좋습니다.

## 체크리스트

- [ ] SSH 키 쌍을 생성하고 서버에 공개 키를 등록할 수 있다
- [ ] `~/.ssh/config`에 별칭을 만들어 접속을 간소화할 수 있다
- [ ] `scp`로 파일을 업로드/다운로드할 수 있다
- [ ] `rsync`로 디렉터리를 증분 동기화할 수 있다
- [ ] SSH 키 파일의 적절한 권한(600, 700)을 알고 있다

## 연습 문제

1. `ssh-keygen -t ed25519`로 키 쌍을 만들고 공개 키 파일(`~/.ssh/id_ed25519.pub`) 내용을 직접 확인해 보세요.
2. 가상의 서버를 기준으로 `Host`, `HostName`, `User`, `Port`, `IdentityFile` 다섯 필드를 모두 포함한 `~/.ssh/config` 예시를 작성해 보세요.
3. localhost를 원격 호스트라고 가정하고, 로컬 파일 하나를 `/tmp/`로 복사하는 `scp` 명령을 써 보세요.

## 정리와 다음 글

- SSH는 암호화된 원격 접속 프로토콜이며, 키 기반 인증이 비밀번호보다 안전합니다.
- `ssh-keygen`으로 키를 만들고, `ssh-copy-id`로 서버에 등록합니다.
- `~/.ssh/config`로 접속 정보를 별칭으로 관리하면 생산성이 올라갑니다.
- `scp`는 단일 복사, `rsync`는 증분 동기화에 적합합니다.
- SSH 키 파일의 권한 관리와 비밀번호 인증 비활성화는 보안의 기본입니다.

이것으로 Linux CLI 101 시리즈가 끝났습니다. CLI의 기본기를 익혔으니, 이제 서버에 접속하고, 로그를 분석하고, 배포를 자동화하는 실무에 자신감을 가지셔도 됩니다.

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

## 실무 시나리오: SSH 운영 표준과 자동화 접점

SSH를 "원격 접속 명령"으로만 이해하면 운영 자동화와 보안 정책이 분리됩니다. 실무에서는 SSH를 인증, 접속 제어, 파일 전송, 원격 실행, 감사 가능한 기록 체계로 함께 봐야 합니다.

### 접속 전 기본 점검

```bash
ssh -V
ls -ld ~/.ssh
ls -l ~/.ssh

# 예상 출력 일부
# OpenSSH_9.6p1, OpenSSL 3.0.13
# drwx------ 2 user user 4096 May 21 12:01 /home/user/.ssh
# -rw------- 1 user user  411 May 21 12:01 id_ed25519
```

권한이 느슨하면 SSH가 키 사용을 거부하므로, 연결 문제를 네트워크 탓으로 보기 전에 파일 권한부터 확인해야 합니다.

### 접속 디버깅: verbose 로그 활용

```bash
ssh -v prod-server

# 출력에서 확인할 포인트
# debug1: Offering public key: /home/user/.ssh/id_ed25519
# debug1: Server accepts key: /home/user/.ssh/id_ed25519
# debug1: Authentication succeeded (publickey).
```

`Permission denied (publickey)` 상황에서 가장 빠른 진단 방법입니다.

### ~/.ssh/config를 정책 문서처럼 쓰기

```sshconfig
Host prod-server
    HostName 10.0.1.50
    User deploy
    Port 2222
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 3

Host bastion
    HostName 203.0.113.10
    User jump

Host internal-api
    HostName 10.10.2.15
    User deploy
    ProxyJump bastion
```

설정 파일은 편의 기능을 넘어, 팀의 접속 방식을 표준화하는 문서 역할을 합니다.

### 원격 명령과 파이프 체인

```bash
ssh prod-server "journalctl -u my-api --since '10 min ago' --no-pager"   | grep -E 'ERROR|CRITICAL|timeout|5[0-9]{2}'   | tee /tmp/prod-api-errors.txt
```

원격 출력도 로컬 파이프라인에 결합할 수 있어, 중앙 분석 스크립트를 만들기 좋습니다.

### 파일 동기화 전략: scp vs rsync

```bash
# 단일 파일 전송
scp dist/app.tar.gz prod-server:/opt/releases/

# 변경분만 동기화
rsync -avz --delete dist/ prod-server:/opt/my-api/current/
```

`--delete`는 원격의 불필요 파일을 정리해 상태를 맞추지만, 잘못된 경로에서 실행하면 큰 사고가 납니다. dry-run(`--dry-run`)으로 먼저 검증하세요.

### SSH 터널로 내부 서비스 접근

```bash
# 원격 DB를 로컬 5432로 포워딩
ssh -L 5432:127.0.0.1:5432 prod-server

# 다른 터미널에서 접속
psql -h 127.0.0.1 -p 5432 -U appuser appdb
```

운영망 DB를 직접 공개하지 않고도 안전하게 점검할 수 있습니다.

### server-side sshd 설정 핵심

```text
# /etc/ssh/sshd_config 주요 예시
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
AllowUsers deploy ops
```

설정 변경 후에는 반드시 서비스 재시작과 로그 확인이 필요합니다.

```bash
sudo systemctl restart sshd
sudo systemctl status sshd --no-pager
sudo journalctl -u sshd -n 40 --no-pager
```

### 원격 운영 스크립트 예시

```bash
#!/usr/bin/env bash
set -euo pipefail

host="prod-server"
svc="my-api"

ssh "$host" "systemctl is-active --quiet $svc"
ssh "$host" "systemctl status $svc --no-pager | sed -n '1,10p'"
ssh "$host" "journalctl -u $svc -n 50 --no-pager | grep -E 'ERROR|CRITICAL|Failed' || true"
```

이 방식은 사람이 직접 SSH에 들어가 수동 점검하는 시간을 줄이고, 점검 결과 형식을 표준화합니다.

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

## 처음 질문으로 돌아가기

- **SSH는 Telnet 대신 왜 기본 원격 접속 수단이 되었을까요?**
  - SSH는 원격 명령과 파일 전송을 암호화된 터널 위에서 처리하므로 평문으로 오가는 Telnet보다 훨씬 안전합니다. 서버 배포, `ssh prod-server 'df -h'` 같은 점검, `scp`와 `rsync` 전송까지 같은 보안 채널로 묶을 수 있어 실무 기본 수단이 되었습니다.
- **비밀번호 인증과 키 기반 인증은 어떤 차이를 만들까요?**
  - 비밀번호 인증은 매번 입력이 필요하고 자동화에 약하지만, `ssh-keygen -t ed25519`로 만든 키를 `authorized_keys`에 등록하면 비밀번호 없이도 안전하게 접속할 수 있습니다. `Permission denied (publickey)`가 날 때는 `chmod 700 ~/.ssh`, `chmod 600 ~/.ssh/id_ed25519`, `ssh -v prod-server`처럼 권한과 인증 과정을 먼저 점검해야 합니다.
- **`~/.ssh/config`는 접속 흐름을 어떻게 단순하게 만들까요?**
  - `Host`, `HostName`, `User`, `Port`, `IdentityFile`을 미리 적어 두면 긴 접속 문자열을 외우지 않고 `ssh prod-server` 같은 별칭으로 바로 접속할 수 있습니다. 글의 `ProxyJump bastion`, `ServerAliveInterval 30` 예시처럼 팀의 접속 정책과 중계 호스트 경로까지 설정 파일에 표준화할 수 있다는 점도 큽니다.

<!-- toc:begin -->
## 시리즈 목차

- [Linux CLI 101 (1/10): CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [Linux CLI 101 (2/10): 파일과 디렉터리 다루기](./02-files-and-directories.md)
- [Linux CLI 101 (3/10): 권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- [Linux CLI 101 (4/10): cat, less, head, tail — 파일 내용 보기](./04-viewing-files.md)
- [Linux CLI 101 (5/10): grep, find, xargs — 검색의 삼총사](./05-grep-find-xargs.md)
- [Linux CLI 101 (6/10): pipe와 redirection](./06-pipe-and-redirection.md)
- [Linux CLI 101 (7/10): 프로세스 확인과 종료](./07-process-management.md)
- [Linux CLI 101 (8/10): 환경변수와 PATH](./08-environment-variables.md)
- [Linux CLI 101 (9/10): 간단한 shell script](./09-shell-script-basics.md)
- **SSH와 원격 서버 접속 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [OpenSSH Manual Pages](https://www.openssh.com/manual.html)
- [SSH Academy - SSH Key Management](https://www.ssh.com/academy/ssh/keygen)
- [GitHub - Connecting with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [rsync man page](https://man7.org/linux/man-pages/man1/rsync.1.html)

- book-examples (linux-cli-101): https://github.com/yeongseon-books/book-examples/tree/main/linux-cli-101/ko
Tags: Linux, SSH, Remote, scp, Security, Server
