---
series: containers-101
episode: 6
title: "Containers 101 (6/10): Network"
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
- Networking
- Bridge
- DevOps
seo_description: 컨테이너 네트워크 모드와 DNS 기반 연결 원리를 입문자 기준으로 설명합니다
last_reviewed: '2026-05-15'
---

# Containers 101 (6/10): Network

컨테이너 네트워크는 처음에는 포트를 열고 IP를 확인하는 문제처럼 보입니다. 하지만 실제 운영에서는 컨테이너가 재시작되고 다시 배치되기 때문에, 어떤 네트워크 모드 위에서 어떤 이름 체계로 서로를 찾게 만들지부터 잡아야 연결 모델이 오래 갑니다.

이 글은 Containers 101 시리즈의 여섯 번째 글입니다.

여기서는 bridge, host, overlay, none의 역할 차이와 함께, user-defined network와 DNS 이름 기반 연결이 왜 Compose와 Kubernetes의 공통 출발점인지 정리합니다.

## 먼저 던지는 질문

- bridge, host, overlay, none 모드는 무엇이 다를까요?
- 같은 호스트의 컨테이너는 이름으로 어떻게 서로를 찾을까요?
- `publish (-p)`와 `expose`는 어떻게 다를까요?

## 큰 그림

![Containers 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/06/06-01-concept-at-a-glance.ko.png)

*Containers 101 6장 흐름 개요*

컨테이너 네트워킹은 bridge, host, overlay 같은 드라이버별로 나뉘며, 각 드라이버는 다른 격리 수준과 성능 특성을 가집니다.

> Network의 핵심은 포트 번호가 아니라 어떤 네트워크 드라이버를 선택했고, 컨테이너 간 또는 호스트와의 통신이 어떤 경로로 흐르는지입니다.

## 왜 중요한가

Docker Compose와 Kubernetes는 모두 이 네트워크 추상화 위에 올라가 있습니다. 기본 원리를 이해하면 상위 도구가 바뀌어도 연결 모델은 훨씬 쉽게 읽힙니다.

많은 입문자가 컨테이너 통신을 IP 주소 관점에서만 봅니다. 하지만 컨테이너는 재시작과 재배치를 전제로 하는 실행 단위입니다. IP에 의존하면 금방 깨지고, 이름 기반 연결과 네트워크 모델을 이해해야 비로소 운영 가능한 구성이 됩니다.

## 한눈에 보는 개념

핵심은 사용자 정의 bridge 위에 컨테이너를 올리고, 서로를 IP가 아니라 이름으로 찾게 만드는 것입니다. 이 구조가 Compose의 기본 동작으로도 이어집니다.

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

## 빠른 검증과 장애 신호

```bash
docker network create app-net
docker run -d --name db --network app-net -e POSTGRES_PASSWORD=secret postgres:16
docker run --rm --network app-net busybox nslookup db
docker network inspect app-net
```

**Expected output:**
- `nslookup db`가 네트워크 내부 DNS 이름을 해석합니다.
- `docker network inspect`에 연결된 컨테이너가 보입니다.

**먼저 확인할 것:**
- 이름 해석이 안 되면 같은 네트워크에 붙었는지 먼저 확인합니다.
- 외부 접속 문제는 `-p` 노출 여부와 앱 바인딩 주소를 함께 봅니다.
- host 모드라면 포트 충돌과 방화벽 정책을 점검합니다.

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


## 심화: 네트워크 모드 비교와 포트 매핑 운영 패턴

컨테이너 네트워크는 기능이 아니라 경계 설계입니다. 특히 "통신만 되면 된다"는 기준으로 구성하면, 외부 노출 범위가 불분명해지고 장애 시 원인 분리가 어려워집니다. 실무에서는 네트워크 모드 선택, 이름 해석 전략, 포트 공개 정책을 함께 다뤄야 합니다.

다음 비교표를 기준으로 기본값을 정하면 운영 실수가 크게 줄어듭니다.

| 항목 | bridge | host | overlay | none |
| --- | --- | --- | --- | --- |
| 호스트 간 통신 | 제한적(단일 호스트) | 단일 호스트 | 가능(멀티호스트) | 불가 |
| 격리 수준 | 보통 | 낮음 | 보통 | 매우 높음(통신 없음) |
| 포트 매핑 필요 | 예 | 아니오 | 상황 의존 | 해당 없음 |
| DNS 이름 해석 | user-defined에서 우수 | 호스트 기준 | 오케스트레이터 의존 | 없음 |
| 대표 사용처 | 일반 앱, Compose | 성능 민감 에이전트 | 분산 서비스 | 보안 테스트 |

## 포트 매핑 원칙

- 외부 사용자 트래픽을 받는 서비스만 `-p`를 사용합니다.
- 내부 서비스(DB, 캐시)는 같은 네트워크에서 이름으로 접근합니다.
- 관리 포트는 `127.0.0.1` 바인딩을 우선 검토합니다.

예시:

```bash
docker network create app-net
docker run -d --name db --network app-net postgres:16
docker run -d --name api --network app-net -p 127.0.0.1:8080:8080 myorg/api:1.0.0
```

이 구성은 DB를 외부에 노출하지 않으면서 API만 로컬 접근으로 열어 두는 안전한 기본 패턴입니다.

## Compose에서 서비스 의존성과 DNS

Compose에서는 서비스명이 곧 DNS 이름입니다. 따라서 `DB_HOST=db`처럼 고정하면 컨테이너 재시작 후에도 연결 모델이 유지됩니다. 반대로 IP를 하드코딩하면 재생성 시 바로 깨집니다.

```yaml
services:
  api:
    image: myorg/api:1.0.0
    environment:
      DB_HOST: db
    depends_on:
      db:
        condition: service_healthy
  db:
    image: postgres:16
```

## 네트워크 장애 디버깅 순서

1. 같은 네트워크에 붙었는지 확인합니다.
2. DNS 이름 해석이 되는지 확인합니다.
3. 대상 컨테이너가 해당 포트에서 리스닝 중인지 확인합니다.
4. 외부 노출 경로(`-p`, 방화벽, 바인딩 주소)를 확인합니다.

```bash
docker network inspect app-net
docker run --rm --network app-net busybox nslookup db
docker exec -it api sh -c "nc -zv db 5432"
```

## 운영 체크리스트

- 네트워크 모드 선택 기준 문서화
- 외부 공개 포트 목록 관리
- 내부 서비스 비공개 원칙 준수
- 서비스 이름 기반 연결 사용
- 불필요한 네트워크 리소스 정리 자동화

이 기준이 있으면 Compose에서 Kubernetes로 확장할 때도 연결 개념을 거의 그대로 가져갈 수 있습니다.


## 추가 실무 노트: 서비스 경계와 네트워크 정책

네트워크는 기능 연결보다 경계 정의가 먼저입니다. 특히 내부 서비스와 외부 진입점(API Gateway, Ingress)을 분리하지 않으면 보안 사고 확률이 높아집니다.

권장 원칙은 다음과 같습니다.

- 외부 공개 계층은 최소 1개 진입점으로 제한
- 내부 서비스는 사설 네트워크에서만 통신
- 관리 포트와 데이터 포트를 분리

```bash
docker run -d --name admin --network app-net -p 127.0.0.1:9000:9000 myorg/admin:1.0.0
```

위 예시는 관리 포트를 로컬 루프백에만 바인딩해 노출 범위를 줄이는 패턴입니다.


## 추가 정리: 운영 적용 전 최종 점검 질문

아래 질문은 도구 지식이 아니라 운영 준비도를 확인하기 위한 질문입니다. 각 질문에 문서와 명령으로 답할 수 있어야 실제 팀 운영에서 반복 가능한 품질을 만들 수 있습니다.

1. 이 구성은 새 팀원이 같은 절차로 재현할 수 있는가?
2. 실패했을 때 어디서 원인을 확인해야 하는지 런북이 있는가?
3. 보안 기본값(root 금지, 최소 권한, 시크릿 분리)이 강제되는가?
4. 버전과 아티팩트 동일성(digest, lock file)이 보장되는가?
5. 데이터/네트워크/권한 경계가 문서로 정의되어 있는가?

다음은 공통 점검 명령 예시입니다.

```bash
# 아티팩트 동일성
docker inspect --format '{{index .RepoDigests 0}}' <image>

# 실행 상태
docker ps --format 'table {{.Names}}	{{.Status}}	{{.Ports}}'

# 로그 관측
docker logs --tail 100 <container>

# 네트워크/볼륨 구조
docker network ls
docker volume ls
```

이 명령 자체가 중요한 것이 아니라, 팀이 같은 순서로 문제를 좁혀 가는 절차를 공유한다는 점이 중요합니다. 컨테이너 운영의 성숙도는 개인의 숙련도보다 팀의 표준화 수준에서 결정됩니다. 따라서 시리즈 학습의 최종 목표는 기능 이해가 아니라 운영 계약의 명문화입니다.

## 처음 질문으로 돌아가기
- **bridge, host, overlay 네트워크는 언제 어떻게 쓸까요?**
  - bridge는 로컬 개발, host는 성능이 중요할 때, overlay는 여러 호스트의 컨테이너 간 통신이 필요할 때입니다.
- **포트 매핑과 포트 발행의 차이는 뭘까요?**
  - -p 플래그로 매핑하면 호스트 포트가 컨테이너 포트로 들어옵니다. EXPOSE는 문서화 목적이고 실제 통신을 제어하지 않습니다.
- **컨테이너 간 통신은 DNS로 어떻게 이루어질까요?**
  - 같은 docker network에 속한 컨테이너는 서비스 이름으로 서로를 호출할 수 있습니다. Docker 내장 DNS가 동적으로 IP를 이름에 매핑합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Containers 101 (1/10): Container란 무엇인가?](./01-what-is-a-container.md)
- [Containers 101 (2/10): Image와 Layer](./02-image-and-layer.md)
- [Containers 101 (3/10): Runtime](./03-runtime.md)
- [Containers 101 (4/10): Dockerfile](./04-dockerfile.md)
- [Containers 101 (5/10): Volume](./05-volume.md)
- **Network (현재 글)**
- Registry (예정)
- Container Security (예정)
- Containers vs VMs (예정)
- 실전 컨테이너 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Docker networking overview](https://docs.docker.com/network/)
- [Bridge networks](https://docs.docker.com/network/bridge/)
- [Overlay networks](https://docs.docker.com/network/overlay/)
- [DNS in Docker](https://docs.docker.com/network/network-tutorial-standalone/)

Tags: Containers, Docker, Kubernetes, DevOps
