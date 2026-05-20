---
series: containers-101
episode: 7
title: "Containers 101 (7/10): Registry"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
- Containers
- Docker
- Registry
- ECR
- DevOps
seo_description: 레지스트리의 역할과 push, pull, digest, 서명 기본 원리를 설명합니다
last_reviewed: '2026-05-15'
---

# Containers 101 (7/10): Registry

이미지를 잘 빌드해도 어디엔가 안정적으로 올리고 다시 가져올 수 없다면 배포는 완성되지 않습니다. 배포 파이프라인이 흔들리는 팀을 보면 대개 tag와 digest를 구분하지 못하거나, 누가 push 권한을 가지는지 설계하지 못한 경우가 많습니다.

이 글은 Containers 101 시리즈의 일곱 번째 글입니다.

여기서는 레지스트리를 단순한 저장소가 아니라 배포 동일성을 보장하는 시스템으로 보고, push와 pull, digest pin, 서명 정책의 출발점을 함께 설명합니다.

## 먼저 던지는 질문

- 빌드한 이미지는 어디에 저장해 두어야 할까요?
- push와 pull 흐름은 배포에서 어떤 역할을 할까요?
- tag와 digest는 왜 구분해서 써야 할까요?

## 큰 그림

![Containers 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/07/07-01-concept-at-a-glance.ko.png)

*Containers 101 7장 흐름 개요*

registry는 단순한 이미지 저장소가 아니라 tag, digest, manifest, push/pull 정책이 모두 만나는 배포 계약 포인트입니다.

> Registry의 핵심은 어디에 이미지가 보관되는가보다, tag와 digest로 어떻게 추적하고 어느 버전을 배포할지 결정하는 것입니다.

## 왜 중요한가

이미지를 재현 가능하게 잘 만들었다고 해도, 어디선가 다시 가져올 수 없다면 배포는 성립하지 않습니다. 배포는 결국 레지스트리에서 시작합니다.

초기 학습 단계에서는 `docker build`까지만 해 보고 끝나는 경우가 많습니다. 하지만 팀 단위 운영으로 넘어가는 순간, 누가 이미지를 올리고 누가 가져오며 무엇을 기준으로 동일성을 보장할지 정해야 합니다. 그 기준이 바로 레지스트리와 digest입니다.

## 한눈에 보는 개념

개발 환경에서 만든 이미지는 레지스트리에 올라가고, 운영 환경은 다시 그 이미지를 당겨 옵니다. 이 흐름이 일관되어야 같은 아티팩트를 여러 환경에서 재사용할 수 있습니다.

## 핵심 용어

- **registry**: 이미지를 원격에 저장하는 서버입니다.
- **repository**: 하나의 이미지 이름을 담는 단위입니다.
- **tag**: 사람이 읽기 쉬운 버전 이름입니다.
- **digest**: 불변 내용을 식별하는 SHA 기반 식별자입니다.
- **signed image**: Cosign 같은 도구로 서명한 이미지입니다.

운영에서는 tag보다 digest가 진실에 가깝습니다. tag는 바뀔 수 있지만 digest는 이미지 내용이 바뀌지 않는 한 고정됩니다.

## Before / After

**Before**: 이미지를 USB나 `scp`로 옮겨 환경마다 결과가 어긋납니다.

**After**: 레지스트리와 digest pin을 사용해 같은 이미지를 정확히 재배포합니다.

즉, 레지스트리는 편의 기능이 아니라 배포 동일성을 확보하는 기반입니다.

## 실습: 이미지 Push 자동화하기

### Step 1 — Login

```python
import subprocess

def login(registry, user, password):
    subprocess.run(
        ["docker", "login", registry, "-u", user, "--password-stdin"],
        input=password.encode(), check=True,
    )
```

인증은 배포 흐름의 첫 단계입니다. 특히 `--password-stdin`을 써야 비밀값이 프로세스 목록이나 셸 기록에 덜 노출됩니다.

### Step 2 — Tag

```python
def tag(local, remote):
    subprocess.run(["docker", "tag", local, remote], check=True)
```

로컬 이미지에 원격 레지스트리용 이름을 붙입니다. 이때 tag는 사람을 위한 이름이지, 불변성을 보장하는 식별자는 아니라는 점이 중요합니다.

### Step 3 — Push

```python
def push(remote):
    subprocess.run(["docker", "push", remote], check=True)
```

이제 이미지를 레지스트리에 업로드합니다. 팀 운영에서는 보통 개발자 개인이 아니라 CI만 push 권한을 가지게 설계합니다.

### Step 4 — Read the digest

```python
def digest(remote):
    res = subprocess.run(
        ["docker", "inspect", "--format={{index .RepoDigests 0}}", remote],
        capture_output=True, text=True, check=True,
    )
    return res.stdout.strip()
```

업로드 후에는 digest를 읽습니다. 운영 배포가 tag 기준인지 digest 기준인지에 따라 재현성 수준이 크게 달라집니다.

### Step 5 — Verify with pull

```python
def verify_pull(remote_digest):
    subprocess.run(["docker", "pull", remote_digest], check=True)
```

digest 기준으로 다시 pull 해 보면 실제 배포가 어떤 대상을 가리키는지 분명해집니다. 같은 이름이 아니라 같은 내용을 가리키는 것입니다.

## 이 코드에서 먼저 봐야 할 점

- 운영에서는 tag가 아니라 digest로 고정하는 편이 안전합니다.
- `password-stdin`은 비밀값 노출을 줄입니다.
- push 권한은 역할 분리 이후에만 주는 편이 좋습니다.

이 세 가지를 놓치면 배포 동일성과 공급망 보안이 동시에 흔들릴 수 있습니다.

## 빠른 검증과 장애 신호

```bash
docker login ghcr.io -u "$GITHUB_USER" --password-stdin
docker tag myapp:dev ghcr.io/example/myapp:1.0.0
docker push ghcr.io/example/myapp:1.0.0
docker inspect --format "{{index .RepoDigests 0}}" ghcr.io/example/myapp:1.0.0
```

**Expected output:**
- push 이후 `RepoDigests`에 `@sha256:` 형태 digest가 생깁니다.
- 같은 digest로 pull 하면 어떤 환경에서도 같은 내용을 다시 받습니다.

**먼저 확인할 것:**
- 인증 실패 시 토큰 권한을 먼저 점검합니다.
- digest가 기대와 다르면 push 직전 tag 대상이 맞는지 봅니다.
- 운영 배포에서는 `latest`만 남기지 말고 digest를 기록합니다.

## 자주 하는 실수 5가지

1. **운영에서 `latest`를 사용합니다.**
2. **digest pin 없이 재배포합니다.**
3. **비공개 이미지를 공개 저장소에 올립니다.**
4. **같은 tag를 덮어써 이력을 잃습니다.**
5. **서명 검증을 생략합니다.**

레지스트리 관련 사고는 대개 “그 정도는 괜찮겠지”라는 편의주의에서 시작합니다. 하지만 운영에서는 그 작은 편의가 큰 추적 불가능성으로 돌아옵니다.

## 운영에서는 이렇게 나타납니다

실무에서는 GitHub Actions가 이미지를 빌드해 GHCR이나 ECR로 push하고, Argo CD 같은 배포 시스템이 digest 변화를 감지해 롤아웃하기도 합니다. 즉, 레지스트리는 CI와 CD 사이를 잇는 중심축입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 진실의 기준은 digest라고 봅니다.
- tag는 단지 사람이 읽기 쉬운 이름일 뿐이라고 생각합니다.
- 레지스트리 자체도 백업 대상이라고 봅니다.
- 서명은 공급망 신뢰의 시작이라고 생각합니다.
- push 권한 분리가 보안의 첫 단계라고 봅니다.

시니어 엔지니어는 “이미지를 어디에 두는가”보다 “누가 어떤 권한으로 어떤 식별자를 배포하는가”를 더 중요하게 봅니다. 그 기준이 있어야 운영 이력과 사고 추적이 가능해집니다.

## 체크리스트

- [ ] 운영 배포는 digest로 고정합니다.
- [ ] push 권한을 CI로 제한했습니다.
- [ ] 이미지 서명 정책을 적용했습니다.
- [ ] 보존 정책을 설정했습니다.

## 연습 문제

1. tag와 digest의 차이를 한 줄로 설명해 보세요.
2. GHCR의 장점 하나를 적어 보세요.
3. 서명 검증이 왜 중요한지 한 줄로 설명해 보세요.

## 정리와 다음 글

레지스트리는 빌드 결과를 실제 배포 아티팩트로 전환하는 장소입니다. push, pull, digest, 서명을 함께 이해해야 비로소 같은 이미지를 안전하게 여러 환경으로 전달할 수 있습니다.

다음 글에서는 이 이미지를 어떻게 더 안전하게 실행할지, 즉 Container Security를 살펴보겠습니다.

## 처음 질문으로 돌아가기
- **tag와 digest의 차이는 뭘까요?**
  - tag는 사람이 붙인 이름(v1.0, latest), digest는 내용 기반 해시(sha256:abcd...)입니다. 같은 tag는 바뀔 수 있지만, digest는 절대 바뀌지 않습니다.
- **private registry와 public registry의 보안 차이는 뭘까요?**
  - private registry는 인증된 사용자만 push/pull할 수 있고, 네트워크도 제어할 수 있습니다. public registry는 누구나 받을 수 있으므로 이미지 내용과 보안 검사가 더 중요합니다.
- **registry 미러링은 왜 하고, 어떻게 동작할까요?**
  - 네트워크 대역폭을 절약하고 배포 속도를 올리기 위해 local 미러를 씁니다. 첫 pull은 upstream에서 받고, 이후 pull은 로컬 미러에서 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Containers 101 (1/10): Container란 무엇인가?](./01-what-is-a-container.md)
- [Containers 101 (2/10): Image와 Layer](./02-image-and-layer.md)
- [Containers 101 (3/10): Runtime](./03-runtime.md)
- [Containers 101 (4/10): Dockerfile](./04-dockerfile.md)
- [Containers 101 (5/10): Volume](./05-volume.md)
- [Containers 101 (6/10): Network](./06-network.md)
- **Registry (현재 글)**
- Container Security (예정)
- Containers vs VMs (예정)
- 실전 컨테이너 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Docker Hub](https://hub.docker.com/)
- [Amazon ECR](https://docs.aws.amazon.com/AmazonECR/latest/userguide/)
- [GitHub Container Registry](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [Cosign](https://docs.sigstore.dev/cosign/overview/)

Tags: Containers, Docker, Kubernetes, DevOps
