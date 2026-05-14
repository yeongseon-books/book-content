---
title: SSH와 원격 서버 접속
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

# SSH와 원격 서버 접속

개발한 코드를 서버에 배포하고, 서버 로그를 확인하고, 데이터베이스에 접속하는 일은 모두 원격 접속에서 시작됩니다. SSH는 이 모든 원격 작업의 기반입니다.

이 글은 Linux CLI 101 시리즈의 마지막 글입니다.

## 이 글에서 다룰 문제

- SSH는 Telnet 대신 왜 기본 원격 접속 수단이 되었을까요?
- 비밀번호 인증과 키 기반 인증은 어떤 차이를 만들까요?
- `~/.ssh/config`는 접속 흐름을 어떻게 단순하게 만들까요?
- `scp`와 `rsync`는 각각 어떤 원격 파일 작업에 더 잘 맞을까요?

> SSH는 두 컴퓨터 사이에 암호화된 터널을 만드는 것입니다. 키 기반 인증은 비밀번호 대신 자물쇠(공개 키)와 열쇠(비밀 키) 쌍을 쓰는 방식입니다. 서버에 자물쇠를 달아두고, 내 컴퓨터의 열쇠로 열면 비밀번호 없이 접속됩니다.

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

<!-- toc:begin -->
## 시리즈 목차

- [CLI와 Shell이란 무엇인가?](./01-what-is-cli-and-shell.md)
- [파일과 디렉터리 다루기](./02-files-and-directories.md)
- [권한과 소유자 이해하기](./03-permissions-and-ownership.md)
- [cat, less, head, tail — 파일 내용 보기](./04-viewing-files.md)
- [grep, find, xargs — 검색의 삼총사](./05-grep-find-xargs.md)
- [pipe와 redirection](./06-pipe-and-redirection.md)
- [프로세스 확인과 종료](./07-process-management.md)
- [환경변수와 PATH](./08-environment-variables.md)
- [간단한 shell script](./09-shell-script-basics.md)
- **SSH와 원격 서버 접속 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [OpenSSH Manual Pages](https://www.openssh.com/manual.html)
- [SSH Academy - SSH Key Management](https://www.ssh.com/academy/ssh/keygen)
- [GitHub - Connecting with SSH](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [rsync man page](https://man7.org/linux/man-pages/man1/rsync.1.html)

Tags: Linux, SSH, Remote, scp, Security, Server
