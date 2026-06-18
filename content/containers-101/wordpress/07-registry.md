---
series: containers-101
episode: 7
title: "바이브코딩을 위한 컨테이너 기초 (7/10): Registry"
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Containers
- Docker
- Registry
- GHCR
language: ko
---

# 바이브코딩을 위한 컨테이너 기초 (7/10): Registry

이 글은 **바이브코딩을 위한 컨테이너 기초** 시리즈의 일곱 번째 글입니다.

AI가 만든 앱을 컨테이너 이미지로 패키징했습니다. 이제 팀원에게 공유하거나 서버에 배포하려면 이미지를 어딘가에 올려야 합니다. USB로 전달하거나 `scp`로 복사하면 버전 추적이 불가능합니다. 레지스트리가 바로 그 "어딘가"입니다.

---

## 오늘의 핵심 질문

AI가 만든 앱 이미지를 팀원과 공유하고 싶습니다. 이미지를 파일로 내보내서 전달하면 될까요? 아니면 더 좋은 방법이 있을까요?

> "Registry의 핵심은 어디에 이미지가 보관되는가보다, tag와 digest로 어떻게 추적하고 어느 버전을 배포할지 결정하는 것입니다."

---

## 이 글에서 다룰 문제

- 컨테이너 이미지는 어디에 저장해야 할까요?
- Docker Hub, GHCR, ECR은 어떻게 다를까요?
- tag와 digest는 왜 구분해서 써야 할까요?
- 바이브코딩으로 만든 앱을 팀과 공유하는 최선의 방법은?
- 이미지를 잘못 관리하면 어떤 문제가 생길까요?

---

## 바이브코딩 관점에서 레지스트리가 중요한 이유

바이브코딩의 흐름을 생각해 봅니다:

1. AI가 앱 코드를 생성
2. 개발자가 테스트하고 수정
3. **팀원에게 공유하거나 서버에 배포**

3번 단계가 레지스트리 없이는 매우 번거롭습니다:

```bash
# 레지스트리 없이 공유하는 방법 (비효율적)
docker save myapp:latest | gzip > myapp.tar.gz
scp myapp.tar.gz teammate@server:/tmp/
ssh teammate@server 'docker load < /tmp/myapp.tar.gz'
# 문제: 버전 추적 불가, 100MB 파일 전송, 수동 과정
```

레지스트리를 쓰면:

```bash
# 레지스트리로 공유하는 방법
docker push ghcr.io/myteam/myapp:v1.0.0
# 팀원이 어디서든
docker pull ghcr.io/myteam/myapp:v1.0.0
```

### 주요 레지스트리 비교

| 레지스트리 | 특징 | 바이브코딩에 적합한 경우 |
|-----------|------|------------------------|
| Docker Hub | 공개 이미지 중심, 무료 tier 제한 | 오픈소스 프로젝트 |
| GHCR | GitHub 통합, Actions 연동 우수 | GitHub로 코드 관리할 때 |
| ECR | AWS IAM 통합 | AWS 배포 환경 |
| GCR | GCP IAM 통합 | GCP 배포 환경 |

**핵심 개념:**

- **repository**: 하나의 이미지 이름을 담는 단위 (`ghcr.io/myorg/myapp`)
- **tag**: 사람이 읽기 쉬운 버전 이름 (`v1.0.0`, `latest`). 가변적임
- **digest**: 이미지 내용의 SHA-256 해시. 불변. 재현성 보장
- **manifest**: 이미지 레이어 구성 정보

---

## 적용 전후: 이미지 공유와 배포

**Before**: 파일로 전달 (비효율)

```bash
docker save myapp:latest | gzip > myapp.tar.gz
# 100MB+ 파일 전송 필요, 버전 이력 없음
```

**After**: 레지스트리 사용

```bash
# CI/CD 또는 개발자가 push
docker tag myapp:latest ghcr.io/myteam/myapp:v1.0.0
docker push ghcr.io/myteam/myapp:v1.0.0

# 팀원이나 서버가 pull
docker pull ghcr.io/myteam/myapp:v1.0.0

# 운영 배포: digest로 정확한 버전 고정
docker pull ghcr.io/myteam/myapp@sha256:abc123...
```

**tag vs digest 이해:**

```bash
# tag: 가변. 같은 이름이 다른 이미지를 가리킬 수 있음
docker pull ghcr.io/myteam/myapp:latest
# 오늘의 latest와 내일의 latest가 다를 수 있음

# digest: 불변. 항상 동일한 이미지
docker pull ghcr.io/myteam/myapp@sha256:abc123...
# 언제 pull 해도 동일한 이미지
```

---

## 자주 하는 실수

| 실수 | 결과 | 해결 방법 |
|------|------|-----------|
| 운영에서 `latest` 태그 사용 | 언제 무엇이 배포됐는지 추적 불가 | 버전 태그 또는 digest 사용 |
| 비공개 이미지를 public repo에 push | 내부 코드/시크릿 공개 노출 | private repo 사용 |
| 같은 tag를 계속 덮어씀 | 이전 버전으로 롤백 불가 | immutable tag 정책 설정 |
| 보존 정책 없음 | 스토리지 비용 증가 | 오래된 이미지 자동 삭제 정책 |
| push 권한을 모든 개발자에게 부여 | 의도치 않은 이미지 덮어씀 | CI만 push 권한 보유 |

---

## AI 팁: CI/CD 파이프라인에서 이미지 push 자동화

AI에게 GitHub Actions 파이프라인 생성을 요청하는 방법:

```
GitHub Actions에서 다음을 수행하는 워크플로를 만들어 주세요:
1. main 브랜치에 push될 때 실행
2. Docker 이미지 빌드
3. GHCR(GitHub Container Registry)에 push
4. 태그: git SHA 기반 (`git-<sha>` 형식)
5. push 후 digest를 출력해서 재현 가능하게 기록

GHCR 인증은 GITHUB_TOKEN을 사용합니다.
```

AI는 완전한 GitHub Actions 워크플로를 만들어 줍니다.

---

## 체크리스트

- [ ] 컨테이너 이미지를 레지스트리에 push해 봤습니다
- [ ] tag와 digest의 차이를 설명할 수 있습니다
- [ ] `latest` 태그가 가변적이라는 것을 이해합니다
- [ ] 팀원이 이미지를 pull할 수 있는 레지스트리를 설정했습니다
- [ ] push 후 `docker inspect`로 digest를 확인했습니다

---

## 처음 질문으로 돌아가기

**이미지를 파일로 전달하는 것보다 레지스트리를 사용하는 것이 왜 더 나을까요?**

레지스트리는 단순 저장소가 아니라 배포 동일성을 보장하는 시스템입니다. 파일 전달은 버전 추적이 불가능하고 무결성 검증도 어렵습니다. 레지스트리를 쓰면 digest로 정확히 어떤 이미지가 어디에 배포됐는지 추적할 수 있고, 팀 전체가 같은 이미지를 사용할 수 있습니다.

---

## 정리

레지스트리는 빌드 결과를 실제 배포 아티팩트로 전환하는 장소입니다. 바이브코딩으로 만든 앱을 팀과 공유하거나 서버에 배포하려면 레지스트리가 필수입니다.

실무에서 레지스트리를 올바르게 쓰려면 세 가지를 기억하세요: 태그 체계를 팀 표준으로 고정하고, 배포는 digest로 고정하며, push 권한은 CI로 제한합니다.

다음 글에서는 이 이미지를 어떻게 더 안전하게 실행할지, 즉 Container Security를 살펴봅니다.

---

## 참고 자료

- [Docker Hub](https://hub.docker.com/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/)
- Containers 101 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/containers-101/ko

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 컨테이너 기초 (1/10): Container란 무엇인가?
- 바이브코딩을 위한 컨테이너 기초 (2/10): Image와 Layer
- 바이브코딩을 위한 컨테이너 기초 (3/10): Runtime
- 바이브코딩을 위한 컨테이너 기초 (4/10): Dockerfile
- 바이브코딩을 위한 컨테이너 기초 (5/10): Volume
- 바이브코딩을 위한 컨테이너 기초 (6/10): Network
- **바이브코딩을 위한 컨테이너 기초 (7/10): Registry (현재 글)**
- 바이브코딩을 위한 컨테이너 기초 (8/10): Container Security
- 바이브코딩을 위한 컨테이너 기초 (9/10): Containers vs VMs
- 바이브코딩을 위한 컨테이너 기초 (10/10): 실전 컨테이너 앱 만들기

<!-- toc:end -->

Tags: 바이브코딩, Containers, Docker, Registry, DevOps
