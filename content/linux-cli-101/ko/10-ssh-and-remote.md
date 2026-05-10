---
title: SSH와 원격 서버 접속
series: linux-cli-101
episode: 10
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
- SSH
- Remote
- scp
- Security
- Server
last_reviewed: '2026-05-04'
seo_description: SSH는 네트워크를 통해 다른 컴퓨터의 터미널을 원격으로 여는 것이며, 키 기반 인증은 비밀번호 대신 자물쇠와 열쇠 쌍을 쓰는 방식입니다.
---

# SSH와 원격 서버 접속

> Linux CLI 101 시리즈 (10/10)

---


## 이 글에서 다룰 문제

개발한 코드를 서버에 배포하고, 서버 로그를 확인하고, 데이터베이스에 접속하는 일은 모두 원격 접속에서 시작됩니다. SSH는 이 모든 원격 작업의 기반입니다.

> AWS EC2 인스턴스를 생성했습니다. 공개 IP 주소를 받았는데, 어떻게 접속해서 코드를 배포할까요? 웹 브라우저로는 서버 터미널을 열 수 없습니다.

`ssh user@ip-address` 한 줄이면 서버의 터미널이 내 화면에 열립니다.

## Mental Model

> SSH는 두 컴퓨터 사이에 암호화된 터널을 만드는 것입니다. 키 기반 인증은 비밀번호 대신 자물쇠(공개 키)와 열쇠(비밀 키) 쌍을 쓰는 방식입니다. 서버에 자물쇠를 달아두고, 내 컴퓨터의 열쇠로 열면 비밀번호 없이 접속됩니다.

```text
[내 컴퓨터]                        [서버]
 비밀 키(~/.ssh/id_ed25519)  ←→  공개 키(~/.ssh/authorized_keys)
          ↓                            ↓
    "이 열쇠로 열어줘"          "자물쇠에 맞으니 통과"
          └──── 암호화된 SSH 터널 ────┘
```

## 핵심 개념

| 용어 | 설명 | 위치 |
|---|---|---|
| 공개 키 | 서버에 등록하는 자물쇠 | `~/.ssh/id_ed25519.pub` |
| 비밀 키 | 내 컴퓨터에 보관하는 열쇠 | `~/.ssh/id_ed25519` |
| authorized_keys | 서버가 허용하는 공개 키 목록 | `~/.ssh/authorized_keys` |
| ssh-agent | 비밀 키를 메모리에 캐시하여 비밀번호 재입력 방지 | 프로세스 |
| known_hosts | 접속한 서버의 지문(fingerprint) 기록 | `~/.ssh/known_hosts` |

## Before / After

**Before (비밀번호 인증)**

```bash
ssh user@192.168.1.100
# 매번 비밀번호 입력
# 브루트포스 공격에 취약
# 자동화 불가 (비밀번호를 스크립트에 넣으면 보안 사고)
```

**After (키 기반 인증 + config)**

```bash
ssh prod-server
# 비밀번호 없이 즉시 접속
# 자동화 가능 (CI/CD에서 SSH 배포)
# 브루트포스 불가능
```

## 단계별 실습

### Step 1. SSH 키 생성

```bash
ssh-keygen -t ed25519 -C "user@example.com"
# Enter file: (Enter로 기본 경로)
# Enter passphrase: (보안을 위해 설정 권장)

ls -la ~/.ssh/
# id_ed25519        ← 비밀 키 (절대 공유 금지)
# id_ed25519.pub    ← 공개 키 (서버에 등록)
```

### Step 2. 서버에 공개 키 등록

```bash
# 방법 1: ssh-copy-id (가장 간편)
ssh-copy-id user@192.168.1.100

# 방법 2: 수동 복사
cat ~/.ssh/id_ed25519.pub | ssh user@192.168.1.100 \
    'mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys'

# 이제 비밀번호 없이 접속 가능
ssh user@192.168.1.100
```

### Step 3. SSH config 설정

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

# 이제 별칭으로 접속
ssh dev-server          # = ssh developer@192.168.1.100
ssh prod-server         # = ssh deploy@10.0.1.50 -p 2222
```

### Step 4. 파일 전송 (scp, rsync)

```bash
# scp: 단일 파일/디렉터리 복사
scp app.tar.gz dev-server:/opt/releases/          # 업로드
scp dev-server:/var/log/app.log ./                 # 다운로드
scp -r project/ dev-server:/home/developer/        # 디렉터리 복사

# rsync: 증분 동기화 (변경분만 전송)
rsync -avz project/ dev-server:/home/developer/project/
# -a: archive (권한, 시간 유지)
# -v: verbose
# -z: 압축 전송
```

### Step 5. 원격 명령 실행

```bash
# 접속 없이 원격 명령 실행
ssh dev-server 'df -h'                        # 디스크 용량 확인
ssh dev-server 'tail -5 /var/log/app.log'     # 로그 마지막 5줄

# 여러 명령 실행
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

### 실수 1. 비밀 키를 공유하거나 Git에 커밋한다

비밀 키(`id_ed25519`)는 절대 다른 사람에게 보내거나 Git에 올리면 안 됩니다. 공유하는 것은 공개 키(`.pub`)뿐입니다.

### 실수 2. SSH 키 파일 권한이 느슨하다

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 ~/.ssh/config
# 권한이 이보다 느슨하면 SSH가 키 사용을 거부합니다
```

### 실수 3. known_hosts 경고를 무시한다

"WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED" 메시지가 나오면, 서버가 바뀌었거나 중간자 공격일 수 있습니다. 서버를 확인한 후 `ssh-keygen -R hostname`으로 이전 지문을 삭제합니다.

### 실수 4. 비밀번호 인증을 비활성화하지 않는다

키 기반 인증을 설정한 후에도 비밀번호 인증이 켜져 있으면 브루트포스 공격에 노출됩니다. `/etc/ssh/sshd_config`에서 `PasswordAuthentication no`를 설정하세요.

### 실수 5. SSH config를 쓰지 않는다

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

## 체크리스트

- [ ] SSH 키 쌍을 생성하고 서버에 공개 키를 등록할 수 있다
- [ ] `~/.ssh/config`에 별칭을 만들어 접속을 간소화할 수 있다
- [ ] `scp`로 파일을 업로드/다운로드할 수 있다
- [ ] `rsync`로 디렉터리를 증분 동기화할 수 있다
- [ ] SSH 키 파일의 적절한 권한(600, 700)을 알고 있다

## 정리 · 다음 글

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
- [cat, less, head, tail](./04-viewing-files.md)
- [grep, find, xargs](./05-grep-find-xargs.md)
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
