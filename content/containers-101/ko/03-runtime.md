---
series: containers-101
episode: 3
title: "Containers 101 (3/10): Runtime"
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
- Runtime
- containerd
- runc
- DevOps
seo_description: Docker, containerd, runc, CRI의 역할 차이를 계층 구조로 설명합니다
last_reviewed: '2026-05-15'
---

# Containers 101 (3/10): Runtime

컨테이너 문제를 만났을 때 Docker CLI만 보면 답이 나올 것처럼 느껴질 때가 많습니다. 하지만 운영 환경으로 가면 Docker, containerd, runc, CRI가 서로 다른 계층으로 분리되어 있어 어디를 보고 있는지부터 구분해야 합니다.

이 글은 Containers 101 시리즈의 세 번째 글입니다.

여기서는 사용자 도구, 런타임 데몬, 저수준 실행기, Kubernetes 인터페이스를 각각 어떤 책임으로 나눠 이해해야 하는지 살펴봅니다.

## 먼저 던지는 질문

- Docker, containerd, runc는 왜 따로 존재할까요?
- 고수준 런타임과 저수준 런타임은 무엇이 다를까요?
- Docker → containerd → runc 흐름은 어떻게 이어질까요?

## 큰 그림

![Containers 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/03/03-01-concept-at-a-glance.ko.png)

*Containers 101 3장 흐름 개요*

이 그림에서는 Runtime이 Docker, containerd, runc 세 계층으로 어떻게 나뉘며, 각 계층이 어떤 책임을 가지는지 봅니다. 중요한 것은 자신이 어느 계층을 다루고 있는지 파악하는 것입니다.

> Runtime의 핵심은 '더 빠르고 작다'는 게 아니라, 어디서 디버깅하고 어디서 스케일링을 제어할지 아는 것입니다.

## 왜 중요한가

Kubernetes 1.24에서 `dockershim`이 제거된 뒤로는 런타임 계층을 모르면 노드 디버깅이 매우 어려워졌습니다. 예전처럼 “컨테이너 문제니까 docker CLI를 보면 되겠지”라는 접근이 항상 통하지 않기 때문입니다.

실무에서 장애를 만났을 때는 누가 이미지를 내려받고, 누가 컨테이너 메타데이터를 관리하며, 누가 최종 프로세스를 띄우는지 구분할 수 있어야 합니다. 이 구분이 없으면 문제를 잘못된 계층에서 찾게 됩니다.

## 한눈에 보는 개념

사용자나 Kubernetes는 직접 프로세스를 실행하지 않습니다. 요청은 인터페이스와 데몬을 거쳐 최종 실행기까지 단계적으로 내려갑니다.

## 핵심 용어

- **Docker**: 사용자가 가장 자주 만나는 고수준 CLI와 데몬 조합입니다.
- **containerd**: 컨테이너 생명주기를 관리하는 데몬입니다.
- **runc**: OCI 표준에 맞춰 컨테이너를 실제로 실행하는 저수준 실행기입니다.
- **CRI**: Kubernetes가 런타임과 통신할 때 사용하는 인터페이스입니다.
- **OCI**: 컨테이너 이미지와 런타임 호환성의 기반이 되는 표준입니다.

특히 Docker와 containerd의 관계를 모르면 노드 운영에서 자주 막힙니다. Docker는 편한 사용자 도구이고, containerd는 운영 계층에서 더 직접적으로 다뤄지는 런타임 데몬입니다.

## Before / After

**Before**: Docker가 컨테이너의 전부라고 생각합니다.

**After**: containerd, runc, CRI의 책임을 분리해서 이해합니다.

이 전환이 중요합니다. 그래야 Kubernetes 환경에서 어떤 도구를 써야 하는지 판단할 수 있습니다.

## 실습: containerd 직접 보기

### Step 1 — Client (illustrative)

```python
import subprocess

def ctr_version():
    res = subprocess.run(["ctr", "version"], capture_output=True, text=True)
    return res.stdout
```

`ctr`는 containerd를 직접 들여다볼 때 쓰는 디버깅용 CLI입니다. 일상적인 개발 도구라기보다 운영 도구에 가깝습니다.

### Step 2 — Pull

```python
def ctr_pull(image):
    subprocess.run(["ctr", "image", "pull", image], check=True)
```

이미지를 직접 내려받아 보면 Docker가 없어도 런타임 계층이 독립적으로 동작한다는 점을 실감할 수 있습니다.

### Step 3 — Run

```python
def ctr_run(image, name):
    subprocess.run(
        ["ctr", "run", "-d", image, name],
        check=True,
    )
```

컨테이너 실행도 별도 계층에서 이뤄집니다. Docker가 편한 UX를 제공할 뿐, 실행의 본질이 Docker 하나 안에 갇혀 있는 것은 아닙니다.

### Step 4 — List

```python
def ctr_list():
    res = subprocess.run(["ctr", "containers", "ls"], capture_output=True, text=True)
    return res.stdout
```

컨테이너 메타데이터를 확인합니다. 운영에서는 이 목록을 통해 실제 관리 대상이 무엇인지 구분하게 됩니다.

### Step 5 — Cleanup

```python
def ctr_kill(name):
    subprocess.run(["ctr", "task", "kill", name])
    subprocess.run(["ctr", "container", "rm", name])
```

`task`와 `container`를 분리해서 다룬다는 점이 여기서 드러납니다. 메타데이터와 실행 중인 작업은 같은 개념이 아닙니다.

## 이 코드에서 먼저 봐야 할 점

- `ctr`는 containerd 디버깅용 CLI입니다.
- `task`와 `container`는 서로 다른 개념입니다.
- Kubernetes 노드에서는 보통 `docker`가 아니라 `crictl`을 사용합니다.

이 차이를 이해하면 노드 문제를 디버깅할 때 도구 선택이 훨씬 정확해집니다. 잘못된 CLI를 붙잡고 한참 헤매는 일이 줄어듭니다.

## 빠른 검증과 장애 신호

```bash
ctr version
ctr image pull docker.io/library/nginx:1.27-alpine
ctr images ls | grep nginx
crictl info
```

**Expected output:**
- `ctr version`에서 client/server 버전이 보입니다.
- `ctr images ls`에 방금 받은 이미지가 등록됩니다.
- Kubernetes 노드라면 `crictl info`에서 CRI 엔드포인트를 확인할 수 있습니다.

**먼저 확인할 것:**
- `ctr`가 없으면 Docker-only 개발 환경인지 실제 containerd 노드인지 먼저 구분합니다.
- `crictl info`가 실패하면 CRI socket 경로를 점검합니다.
- pull 실패 시 레지스트리 접근 정책과 프록시 설정을 확인합니다.

## 자주 하는 실수 5가지

1. **Docker만 배우고 containerd를 완전히 건너뜁니다.**
2. **Kubernetes 노드를 `docker` CLI로 디버깅하려고 합니다.**
3. **호스트마다 런타임 버전 차이를 방치합니다.**
4. **rootless 런타임 옵션을 검토하지 않습니다.**
5. **`runc`의 기본 seccomp 프로필 영향을 무시합니다.**

이 실수들은 모두 컨테이너 실행 계층을 하나로 뭉뚱그려 볼 때 생깁니다. 실제 운영에서는 계층 분리가 곧 문제 해결 속도입니다.

## 운영에서는 이렇게 나타납니다

Kubernetes 노드는 주로 containerd를 사용하고, 운영자는 `crictl` 같은 도구로 상태를 확인합니다. 반면 로컬 개발은 여전히 Docker Desktop을 많이 사용합니다. 또 일부 임베디드나 서버리스 환경에서는 `podman`이나 다른 런타임 구성이 등장하기도 합니다.

즉, 같은 컨테이너라도 환경에 따라 앞단 도구는 달라질 수 있습니다. 그러나 OCI와 런타임 계층 구조는 계속 공통 기반으로 남습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 런타임 계층을 이해하면 절반의 장애는 더 빨리 풀립니다.
- Docker는 사용자 도구이고, containerd는 운영 도구에 더 가깝습니다.
- OCI 표준이 호환성의 핵심입니다.
- 가능하면 rootless 옵션을 먼저 검토합니다.
- 런타임 업그레이드는 클러스터 전체 동작에 영향을 준다고 봅니다.

시니어 엔지니어는 “무슨 CLI를 쓰는가”보다 “지금 어느 계층을 보고 있는가”를 먼저 묻습니다. 그 질문이 정확해야 로그와 증상도 올바르게 해석할 수 있기 때문입니다.

## 체크리스트

- [ ] containerd와 runc의 차이를 설명할 수 있습니다.
- [ ] CRI의 역할을 이해합니다.
- [ ] 디버깅 시 `crictl`이 필요한 상황을 알고 있습니다.
- [ ] OCI 표준의 의미를 이해합니다.

## 연습 문제

1. runc와 containerd의 책임 차이를 한 줄로 설명해 보세요.
2. Kubernetes가 `dockershim`을 제거한 이유를 하나 들어 보세요.
3. `crictl`을 언제 써야 하는지 한 줄로 적어 보세요.

## 정리와 다음 글

컨테이너 실행은 Docker 하나가 모두 맡는 단일 구조가 아닙니다. 사용자 경험, 생명주기 관리, 저수준 실행이 계층으로 나뉘어 있고, Kubernetes는 그 위에 CRI를 통해 올라탑니다. 이 구조를 이해해야 컨테이너 운영이 비로소 선명해집니다.

다음 글에서는 이렇게 실행할 이미지를 실제로 어떻게 작성하는지, 즉 Dockerfile을 살펴보겠습니다.

## 처음 질문으로 돌아가기
- **Docker, containerd, runc는 왜 따로 존재할까요?**
  - 각 계층의 책임은 따로 분리되어 있습니다. Docker는 개발자 경험, containerd는 호스트 데몬, runc는 저수준 프로세스 실행입니다.
- **고수준 런타임과 저수준 런타임은 무엇이 다를까요?**
  - 고수준 런타임(Docker, containerd)은 이미지 관리와 스토리지 처리를 합니다. 저수준 런타임(runc)은 받은 파일시스템으로 프로세스만 생성합니다.
- **Docker → containerd → runc 흐름은 어떻게 이어질까요?**
  - Docker CLI는 containerd에 지시를 보내고, containerd는 runc에게 프로세스를 실행하라고 합니다. Kubernetes는 containerd나 runc를 직접 호출해서 Docker를 건너뜁니다.

<!-- toc:begin -->
## 시리즈 목차

- [Containers 101 (1/10): Container란 무엇인가?](./01-what-is-a-container.md)
- [Containers 101 (2/10): Image와 Layer](./02-image-and-layer.md)
- **Runtime (현재 글)**
- Dockerfile (예정)
- Volume (예정)
- Network (예정)
- Registry (예정)
- Container Security (예정)
- Containers vs VMs (예정)
- 실전 컨테이너 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [containerd 공식 문서](https://containerd.io/docs/)
- [runc 저장소](https://github.com/opencontainers/runc)
- [Kubernetes CRI](https://kubernetes.io/docs/concepts/architecture/cri/)
- [OCI 표준](https://opencontainers.org/)

Tags: Containers, Docker, Kubernetes, DevOps
