---
title: "바이브코딩을 위한 Linux CLI 기초 (10/10): SSH와 원격 서버 접속"
series: linux-cli-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Linux
  - SSH
  - Remote
  - Security
---

# 바이브코딩을 위한 Linux CLI 기초 (10/10): SSH와 원격 서버 접속

이 글은 "바이브코딩을 위한 Linux CLI 기초" 시리즈의 마지막 글입니다.

---

바이브코딩에서 AI는 SSH 설정 코드를 빠르게 만들어 줍니다. 개발한 코드를 서버에 배포하고, 서버 로그를 확인하고, 데이터베이스에 접속하는 일은 모두 원격 접속에서 시작됩니다. 하지만 비밀 키를 Git에 올리거나, 비밀번호 인증을 비활성화하지 않거나, 키 파일 권한이 느슨해 SSH가 거부하는 문제가 자주 발생합니다.

SSH는 두 컴퓨터 사이에 암호화된 터널을 만드는 것입니다. 키 기반 인증은 비밀번호 대신 자물쇠(공개 키)와 열쇠(비밀 키) 쌍을 쓰는 방식입니다. 서버에 자물쇠를 달아두고, 내 컴퓨터의 열쇠로 열면 비밀번호 없이 접속됩니다.

비밀번호 인증이 켜져 있으면 브루트포스 공격에 노출됩니다. 키 기반 인증 설정 후에는 반드시 비밀번호 인증을 비활성화해야 합니다.

키 생성, 공개 키 등록, `~/.ssh/config`, `scp`/`rsync` 파일 전송을 중심으로 정리합니다.

> **핵심 인사이트:** 비밀 키(`id_ed25519`)는 절대 공유하거나 Git에 올리면 안 됩니다. 공유하는 것은 공개 키(`.pub`)뿐입니다. 키 파일 권한이 느슨하면 SSH 자체가 키 사용을 거부합니다(`chmod 600 ~/.ssh/id_ed25519`).

## 이 글에서 다룰 문제

- SSH는 Telnet 대신 왜 기본 원격 접속 수단이 되었을까요?
- 비밀번호 인증과 키 기반 인증은 어떤 차이를 만들까요?
- `~/.ssh/config`는 접속 흐름을 어떻게 단순하게 만들까요?
- scp와 rsync는 어떻게 다를까요?
- AI가 만든 SSH 설정에서 확인해야 할 것은 무엇인가요?

## SSH 핵심 패턴

```bash
# 1. 키 생성 (ed25519 권장)
ssh-keygen -t ed25519 -C "user@example.com"
# ~/.ssh/id_ed25519      ← 비밀 키 (절대 공유 금지)
# ~/.ssh/id_ed25519.pub  ← 공개 키 (서버에 등록)

# 2. 공개 키 서버에 등록
ssh-copy-id user@192.168.1.100

# 3. 키 파일 권한 설정 (느슨하면 SSH가 거부)
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 ~/.ssh/config
```

```bash
# ~/.ssh/config: 접속 별칭 설정
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

ssh dev-server           # = ssh developer@192.168.1.100

# 파일 전송
scp app.tar.gz dev-server:/opt/releases/    # 단일 파일 업로드
rsync -avz project/ dev-server:/home/developer/project/  # 변경분만 동기화
```

## 변경 전후 비교

**Before: 비밀번호 인증**
```text
- 매번 비밀번호 입력
- 브루트포스 공격에 노출
- 스크립트 자동화 불가 (비밀번호를 스크립트에 넣으면 보안 사고)
- 긴 호스트명을 매번 타이핑
```

**After: 키 기반 인증 + config**
```text
- 비밀번호 없이 즉시 접속
- 브루트포스 공격 원천 차단
- CI/CD 파이프라인에서 자동 배포 가능
- ssh prod-server 한 단어로 접속
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 비밀 키를 Git에 커밋 | 서버 접근권이 영구 노출 | 공개 키(.pub)만 공유, .gitignore에 키 추가 |
| 키 파일 권한이 느슨 | SSH가 키 사용을 거부 | `chmod 600 ~/.ssh/id_ed25519` |
| 비밀번호 인증 비활성화 안 함 | 키 설정해도 브루트포스 가능 | sshd_config에서 `PasswordAuthentication no` |
| 호스트 지문 경고 무시 | 중간자 공격 가능 | 서버 확인 후 `ssh-keygen -R hostname` |
| config 없이 긴 명령 타이핑 | 실수 유발, 비효율 | `~/.ssh/config`에 별칭 등록 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"SSH 키 기반 인증 설정 가이드를 만들어줘.
ed25519 키 생성,
~/.ssh/config에 dev/prod 서버 별칭,
비밀번호 인증 비활성화,
GitHub Actions CI/CD에서 SSH 배포까지 포함"

# AI 결과물 검증 체크포인트:
# - 비밀 키가 아닌 공개 키(.pub)만 서버에 등록하는가?
# - 키 파일 권한(chmod 600)이 명시되어 있는가?
# - 비밀번호 인증 비활성화 단계가 포함되어 있는가?
# - ~/.ssh/config로 별칭을 사용하는가?
# - CI/CD에서 비밀 키가 환경변수/시크릿으로 안전하게 전달되는가?
```

## 운영 체크리스트

- [ ] ed25519 키로 생성하고 비밀번호 없이 접속된다
- [ ] 키 파일 권한이 올바르다 (`chmod 600 ~/.ssh/id_ed25519`)
- [ ] 서버에서 비밀번호 인증이 비활성화되어 있다
- [ ] `~/.ssh/config`에 자주 접속하는 서버 별칭이 등록되어 있다
- [ ] 비밀 키가 Git 저장소나 공유 채널에 노출되지 않았다

## 처음 질문으로 돌아가기

- **키 기반 인증이 비밀번호보다 안전한 이유는?** 비밀번호는 추측 공격이 가능하지만, 비밀 키는 수학적으로 역산이 불가능합니다. 비밀번호 인증을 비활성화하면 브루트포스 공격이 원천 차단됩니다.
- **scp와 rsync의 차이는?** `scp`는 전체 파일을 복사하고, `rsync`는 변경된 부분만 전송합니다. 대용량 디렉터리 동기화에는 `rsync -avz`가 효율적입니다.
- **호스트 지문 경고가 뜨면?** "WARNING: REMOTE HOST IDENTIFICATION HAS CHANGED"는 서버가 바뀌었거나 중간자 공격일 수 있습니다. 서버를 먼저 확인한 후 `ssh-keygen -R hostname`으로 이전 지문을 삭제합니다.

## 정리

바이브코딩에서 AI가 만들어 준 SSH 설정에서 비밀 키 보안, 키 파일 권한, 비밀번호 인증 비활성화를 반드시 확인하세요. SSH는 원격 작업의 기반입니다. Linux CLI 101 시리즈를 통해 파일 시스템부터 프로세스 관리, 환경변수, Shell script, SSH까지 Linux 기초를 갖추셨기를 바랍니다.

## 참고 자료

- [OpenSSH Manual](https://www.openssh.com/manual.html)
- [SSH Key Management Best Practices](https://www.ssh.com/academy/ssh/keygen)
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
- 바이브코딩을 위한 Linux CLI 기초 (8/10): 환경변수와 PATH
- 바이브코딩을 위한 Linux CLI 기초 (9/10): 간단한 Shell Script
- **바이브코딩을 위한 Linux CLI 기초 (10/10): SSH와 원격 서버 접속 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, Linux, SSH, Remote, Security
