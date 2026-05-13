---
series: containers-101
episode: 6
title: Network
status: publish-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Containers
  - Docker
  - Networking
  - Bridge
  - DevOps
seo_description: 컨테이너 네트워크 모드와 DNS 기반 연결 원리를 입문자 기준으로 설명합니다
last_reviewed: '2026-05-12'
---

# Network

이 글은 Containers 101 시리즈의 여섯 번째 글입니다.

## 이 글에서 다룰 문제

- bridge, host, overlay, none 모드는 무엇이 다를까요?
- 같은 호스트의 컨테이너는 이름으로 어떻게 서로를 찾을까요?
- `publish (-p)`와 `expose`는 어떻게 다를까요?
- user-defined network는 왜 기본 bridge보다 나을까요?
- 네트워크 설정에서 자주 터지는 실수는 무엇일까요?

> 컨테이너 네트워킹의 핵심은 두 가지입니다. 어떤 네트워크 모드를 선택할지, 그리고 컨테이너들이 DNS 이름으로 서로를 어떻게 찾게 만들지입니다.

## 왜 중요한가

Docker Compose와 Kubernetes는 모두 이 네트워크 추상화 위에 올라가 있습니다. 기본 원리를 이해하면 상위 도구가 바뀌어도 연결 모델은 훨씬 쉽게 읽힙니다.

많은 입문자가 컨테이너 통신을 IP 주소 관점에서만 봅니다. 하지만 컨테이너는 재시작과 재배치를 전제로 하는 실행 단위입니다. IP에 의존하면 금방 깨지고, 이름 기반 연결과 네트워크 모델을 이해해야 비로소 운영 가능한 구성이 됩니다.

## 한눈에 보는 개념

```mermaid
flowchart LR
    Host["host"] --> Bridge["bridge"]
    Bridge --> C1["web"]
    Bridge --> C2["db"]
    C1 -. dns .-> C2
```

핵심은 user-defined bridge 위에 컨테이너를 올리고, 서로를 IP가 아니라 이름으로 찾게 만드는 것입니다. 이 구조가 Compose의 기본 동작으로도 이어집니다.

## 핵심 용어

- **bridge**: 기본 가상 L2 네트워크입니다.
- **host**: 호스트의 네트워크 네임스페이스를 그대로 공유합니다.
- **overlay**: 여러 호스트에 걸쳐 네트워크를 확장합니다.
- **none**: 네트워크를 붙이지 않습니다.
- **expose**: 내부 포트를 문서화할 뿐, 외부에 공개하지는 않습니다.

특히 `expose`와 `-p`를 구분하는 감각이 중요합니다. 하나는 내부 통신 문맥이고, 다른 하나는 외부 노출 결정입니다.

## Before / After

**Before**: 컨테이너가 IP 주소로 서로 통신해서 재시작 때마다 깨집니다.

**After**: user-defined bridge 위에서 DNS 이름으로 통신하므로 재시작 후에도 연결 모델이 유지됩니다.

네트워킹의 목표는 단순 연결이 아니라 재시작 이후에도 유지되는 안정적 연결입니다.

## 실습: User-Defined Network 만들기

### Step 1 — Create

```python
import subprocess

def create_net(name):
    subprocess.run(["docker", "network", "create", name], check=True)
```

먼저 명시적으로 네트워크를 만듭니다. 기본 bridge를 그대로 쓰는 것보다 명확하고, DNS 기반 이름 해석도 더 잘 활용할 수 있습니다.

### Step 2 — Run DB

```python
def run_db(net):
    subprocess.run([
        "docker", "run", "-d", "--name", "db", "--network", net,
        "-e", "POSTGRES_PASSWORD=secret", "postgres:16",
    ], check=True)
```

데이터베이스를 같은 네트워크에 연결합니다. 이 시점부터 컨테이너 이름 `db`가 네트워크 내부 DNS 이름이 됩니다.

### Step 3 — Run app

```python
def run_app(net):
    subprocess.run([
        "docker", "run", "-d", "--name", "app", "--network", net,
        "-p", "8080:8080",
        "-e", "DB_HOST=db",
        "myorg/app:latest",
    ], check=True)
```

애플리케이션은 `DB_HOST=db`로 데이터베이스를 찾습니다. IP를 직접 넣지 않는다는 점이 운영 안정성의 핵심입니다.

### Step 4 — Inspect

```python
def inspect(net):
    res = subprocess.run(
        ["docker", "network", "inspect", net],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

네트워크 구성을 확인하면 어떤 컨테이너가 붙어 있는지, DNS 이름이 어떻게 연결되는지 읽을 수 있습니다.

### Step 5 — Cleanup

```python
def cleanup(net):
    subprocess.run(["docker", "rm", "-f", "app", "db"])
    subprocess.run(["docker", "network", "rm", net])
```

네트워크도 상태입니다. 쓰지 않는 리소스를 지우는 습관까지 포함해야 실습이 끝납니다.

## 이 코드에서 먼저 봐야 할 점

- `DB_HOST=db`는 IP가 아니라 DNS 이름을 사용합니다.
- user-defined network가 기본 bridge보다 실전적입니다.
- `-p`는 정말 외부 노출이 필요할 때만 써야 합니다.

이 세 가지를 놓치면 내부 통신과 외부 공개를 뒤섞기 쉽습니다. 운영 사고는 대개 이 경계가 흐릴 때 시작됩니다.

## 자주 하는 실수 5가지

1. **기본 bridge를 그대로 써서 DNS 이점을 놓칩니다.**
2. **DB까지 `-p`로 외부에 공개합니다.**
3. **overlay와 bridge의 역할을 혼동합니다.**
4. **host 모드를 남용해 포트 충돌을 만듭니다.**
5. **사용하지 않는 네트워크를 계속 쌓아 둡니다.**

이 실수들은 모두 “연결된다”만 보고 “어디에 드러나는가”를 놓칠 때 발생합니다. 네트워크는 기능이 아니라 경계 설계입니다.

## 운영에서는 이렇게 나타납니다

Compose는 프로젝트마다 user-defined network를 자동으로 만들고, Kubernetes는 CNI를 통해 각 Pod에 L3 연결성을 제공합니다. 구현은 달라도 원리는 같습니다. 서비스가 이름으로 서로를 찾고, 외부 노출은 별도 계층에서 명시적으로 결정합니다.

## 시니어 엔지니어는 이렇게 생각합니다

- DNS가 연결 모델의 기본이라고 봅니다.
- 외부 노출은 명시적인 결정으로 다룹니다.
- 네트워크 모드 선택은 보안 결정이기도 합니다.
- 네트워크 리소스도 상태이므로 정리 대상이라고 봅니다.
- Compose와 Kubernetes가 추상화하더라도 원리는 같다고 생각합니다.

시니어 엔지니어는 “통신이 되느냐”보다 “이 통신이 어떤 경계와 이름 체계 위에서 성립하느냐”를 먼저 봅니다. 그래야 환경이 바뀌어도 구조를 유지할 수 있습니다.

## 체크리스트

- [ ] user-defined network를 사용합니다.
- [ ] DB를 외부에 공개하지 않았습니다.
- [ ] DNS 이름으로 통신합니다.
- [ ] 사용하지 않는 네트워크를 정리합니다.

## 연습 문제

1. 기본 bridge의 대표 한계를 한 줄로 설명해 보세요.
2. overlay network가 적합한 전형적 사례를 하나 적어 보세요.
3. `expose`와 `publish (-p)`의 차이를 한 줄로 설명해 보세요.

## 정리와 다음 글

컨테이너 네트워킹은 복잡한 기능 묶음처럼 보이지만, 실제로는 모드 선택과 이름 기반 연결이라는 두 축으로 정리됩니다. 이 기본만 잡아도 Compose와 Kubernetes의 네트워크 동작을 훨씬 더 쉽게 읽을 수 있습니다.

다음 글에서는 실행할 이미지를 어디에 저장하고 어떻게 다시 가져오는지, 즉 Registry를 살펴보겠습니다.

<!-- toc:begin -->
- [Container란 무엇인가?](./01-what-is-a-container.md)
- [Image와 Layer](./02-image-and-layer.md)
- [Runtime](./03-runtime.md)
- [Dockerfile](./04-dockerfile.md)
- [Volume](./05-volume.md)
- **Network (현재 글)**
- Registry (예정)
- Container Security (예정)
- Container와 VM 차이 (예정)
- 실전 컨테이너 앱 만들기 (예정)
<!-- toc:end -->

## 참고 자료

- [Docker networking overview](https://docs.docker.com/network/)
- [Bridge networks](https://docs.docker.com/network/bridge/)
- [Overlay networks](https://docs.docker.com/network/overlay/)
- [DNS in Docker](https://docs.docker.com/network/network-tutorial-standalone/)

Tags: Containers, Docker, Networking, Bridge, DevOps
