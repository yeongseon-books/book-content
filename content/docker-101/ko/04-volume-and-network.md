---
series: docker-101
episode: 4
title: "Docker 101 (4/10): Volume과 Network"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Docker
  - Volume
  - Network
  - Bind Mount
  - Bridge
seo_description: volume과 network로 데이터 영속성과 컨테이너 통신을 안전하게 다룹니다
last_reviewed: '2026-05-15'
---

# Docker 101 (4/10): Volume과 Network

컨테이너를 한두 개 실행할 때는 모든 것이 단순해 보입니다. 그런데 실제 애플리케이션은 금방 두 가지 문제를 만납니다. 하나는 데이터를 어디에 둘 것인가이고, 다른 하나는 컨테이너끼리 어떻게 통신하게 만들 것인가입니다. 이 두 문제를 제대로 다루지 못하면 재시작 한 번에 데이터가 사라지거나, 서비스가 서로를 찾지 못하는 일이 생깁니다.

이 글은 Docker 101 시리즈의 4번째 글입니다.

Docker에서 이 문제를 푸는 핵심 개념이 volume과 network입니다. volume은 상태의 수명을 결정하고, network는 컨테이너 간 통신 경로를 결정합니다. 결국 이 둘은 컨테이너 운영의 가장 기본적인 인프라입니다.

![Docker 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/04/04-01-concept-at-a-glance.ko.png)
*Docker 101 4장 흐름 개요*

> Volume과 Network는 부가 옵션이 아니라 컨테이너 운영의 두 기본 축입니다 — volume은 '상태의 수명을 컨테이너 수명에서 분리'하고, network는 '컨테이너가 서로를 어떻게 찾고 부르느냐'를 결정합니다. 이 둘 없이 컨테이너는 한 번 죽으면 자기 자리도 데이터도 잃습니다.

## 먼저 던지는 질문

- volume, bind mount, tmpfs는 각각 언제 써야 할까요?
- 컨테이너 데이터는 왜 기본적으로 휘발된다고 봐야 할까요?
- 브리지 네트워크는 어떻게 컨테이너 이름 기반 통신을 가능하게 할까요?

## 왜 이 글이 중요한가

컨테이너 운영에서 가장 흔한 사고는 화려한 분산 시스템 문제보다 훨씬 단순한 곳에서 시작합니다. 재시작했더니 데이터가 사라졌고, 앱 컨테이너가 DB 컨테이너에 접속하지 못하는 문제입니다. 둘 다 volume과 network 모델을 정확히 잡으면 예방 가능한 사고입니다.

특히 입문 단계에서는 컨테이너를 하나의 서버처럼 보고, 그 안에 파일을 저장하거나 `localhost`로 다른 컨테이너에 접근하려는 실수를 많이 합니다. 그러나 컨테이너는 버릴 수 있는 실행 단위이고, 통신도 명시적으로 연결해 주어야 합니다.

## 핵심 용어

- **Volume**: Docker가 관리하는 영구 저장소입니다.
- **Bind mount**: 호스트 경로를 컨테이너에 직접 연결하는 방식입니다.
- **tmpfs**: 메모리 기반의 일시적 저장소입니다.
- **Bridge network**: 한 호스트 안에서 컨테이너를 연결하는 기본 가상 네트워크입니다.
- **Service discovery**: 컨테이너 이름을 DNS처럼 해석해 주는 방식입니다.

이 다섯 가지 중 실무에서 가장 자주 쓰는 조합은 named volume과 user-defined bridge입니다. 하나는 상태를 보존하고, 다른 하나는 이름 기반 통신을 안정적으로 만들어 주기 때문입니다.

## 전과 후

**Before**: DB 데이터를 컨테이너 내부에 저장해 재시작 때마다 잃고, 다른 컨테이너를 `localhost`로 찾으려다 실패합니다.

**After**: named volume으로 데이터를 유지하고, user-defined bridge 위에서 컨테이너 이름으로 통신합니다.

이 차이는 작아 보여도 운영 감각을 완전히 바꿉니다. 상태는 외부화하고, 통신은 명시적 네트워크로 연결한다는 원칙이 생기기 때문입니다.

## 실습: volume과 network를 5단계로 익히기

### 1단계 — named volume 만들기

```bash
docker volume create app-data
docker run -d --name api -v app-data:/var/lib/data myapp
docker volume inspect app-data
```

named volume은 컨테이너와 독립적으로 존재합니다. 컨테이너를 지웠다고 해서 데이터까지 곧바로 사라지지 않는 이유가 여기에 있습니다.

### 2단계 — bind mount 사용하기

```bash
docker run --rm -v "$PWD":/app -w /app python:3.12-slim python app.py
```

bind mount는 개발 환경에서 특히 유용합니다. 로컬 소스코드를 바로 컨테이너에 반영할 수 있기 때문입니다. 다만 운영에서는 호스트 의존성과 권한 이슈가 커지므로 신중해야 합니다.

### 3단계 — user-defined bridge 만들기

```bash
docker network create app-net
docker run -d --network app-net --name db postgres:16
docker run -d --network app-net --name api -e DB_HOST=db myapp
# api can reach the host 'db'
```

이 단계의 핵심은 `db`라는 이름이 곧 접속 대상이 된다는 사실입니다. user-defined bridge는 컨테이너 이름 기반 DNS를 제공하므로, IP 주소를 직접 관리할 필요가 없습니다.

### 4단계 — 통신 확인하기

```bash
docker exec api ping -c 1 db
docker exec api curl http://db:5432
```

컨테이너 네트워크 문제는 감으로 해결하기 어렵습니다. 따라서 실제로 이름 해석이 되는지, 포트에 도달하는지, 어느 단계에서 막히는지 확인하는 습관이 중요합니다.

### 5단계 — volume 백업하기

```bash
docker run --rm \
  -v app-data:/data \
  -v "$PWD":/backup \
  alpine tar czf /backup/data.tgz -C /data .
```

volume이 영구적이라고 해서 안전한 것은 아닙니다. 삭제, 손상, 잘못된 마이그레이션은 언제든 일어날 수 있습니다. 그래서 영속성 다음 단계는 항상 백업입니다.

### 실행 뒤 바로 확인할 것

- `docker volume inspect app-data`는 volume이 독립적으로 생성되었음을 보여 주어야 하고, `docker exec api ping -c 1 db`는 이름 해석이 성공해야 합니다.
- 백업 명령을 실행했다면 현재 디렉터리에 `data.tgz`가 생겼는지까지 확인해 둡니다.

### 잘 안 될 때 먼저 볼 것

- 컨테이너가 `localhost`로 DB를 찾으려 한다면 네트워크가 아니라 환경변수 값이 잘못된 경우가 많습니다. `DB_HOST=db`처럼 서비스 이름을 확인합니다.
- bind mount 권한 오류가 나면 호스트 파일 소유자와 컨테이너 사용자 ID가 맞는지부터 살펴봅니다.

## 이 코드에서 먼저 봐야 할 점

- named volume은 컨테이너와 독립적으로 살아 있습니다.
- user-defined bridge는 이름 기반 DNS를 자동으로 제공합니다.
- bind mount는 편하지만 권한 문제를 자주 동반합니다.

입문 단계에서는 bind mount가 가장 익숙해서 모든 문제를 그것으로 해결하고 싶어집니다. 하지만 운영에서는 named volume이 기본이고, bind mount는 개발 편의성 도구에 가깝다는 감각을 가지는 편이 좋습니다.

## 자주 하는 실수 다섯 가지

1. **컨테이너 내부 경로에 직접 저장합니다.** 재시작이나 재생성 시 데이터가 사라질 수 있습니다.
2. **default bridge를 그대로 씁니다.** 이름 해석과 격리 측면에서 한계가 있습니다.
3. **bind mount 권한을 무시합니다.** 호스트와 컨테이너 사이에서 수정 충돌이 납니다.
4. **volume을 백업하지 않습니다.** 사고가 나면 복구 경로가 없습니다.
5. **`--network host`를 남용합니다.** 보안과 포트 충돌 위험이 커집니다.

이 실수들은 모두 컨테이너를 단순한 프로세스 격리 도구로만 볼 때 생깁니다. 실제로는 상태와 통신 모델까지 설계해야 운영 가능한 시스템이 됩니다.

## 실무에서는 이렇게 이어집니다

Kubernetes로 가더라도 개념은 크게 바뀌지 않습니다. volume은 PersistentVolume 같은 영속 저장 개념으로 이어지고, network와 이름 기반 통신은 Service DNS로 이어집니다. Docker에서 이 멘탈 모델을 먼저 익혀 두면 이후 전환이 훨씬 자연스럽습니다.

또한 운영 사고 대응에서도 같은 감각이 필요합니다. 데이터 손실은 storage 문제인지, 접속 실패는 network 문제인지 먼저 구분해야 원인 분석이 빨라집니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 상태는 volume에 두고, 통신은 network로 푼다는 원칙을 분리합니다.
- user-defined bridge를 기본값으로 봅니다.
- 백업 없는 volume은 아직 운영 준비가 끝난 것이 아닙니다.
- bind mount는 개발용이고, 운영은 named volume 중심으로 설계합니다.
- 필요한 포트만 최소한으로 노출합니다.

이 기준을 가지고 다음 글의 Compose를 보면 왜 services, volumes, networks를 한 파일에서 함께 정의하는지 더 잘 이해할 수 있습니다.

## 체크리스트

- [ ] 데이터가 named volume에 저장됩니다.
- [ ] 컨테이너가 user-defined bridge에서 실행됩니다.
- [ ] 컨테이너 이름으로 서로 통신할 수 있습니다.
- [ ] volume 백업 절차가 있습니다.

## 연습 문제

1. PostgreSQL 데이터를 named volume에 영속화해 보세요.
2. 두 컨테이너를 user-defined bridge에 연결하고 이름으로 통신하게 해 보세요.
3. `tar`를 사용해 volume 내용을 백업해 보세요.

## 정리 및 다음 단계

데이터와 네트워크는 컨테이너 운영의 기초 체력입니다. image와 container를 이해했다면, 이제 상태를 어디에 둘지와 컨테이너가 서로를 어떻게 찾을지를 함께 설계해야 합니다. volume은 영속성을, network는 연결 가능성을 담당합니다.

다음 글에서는 Docker Compose를 봅니다. 지금까지 개별 명령으로 다룬 컨테이너, 네트워크, 볼륨을 하나의 YAML로 묶어 반복 가능한 환경으로 만드는 단계입니다.

## 처음 질문으로 돌아가기

- **volume, bind mount, tmpfs는 각각 언제 써야 할까요?**
  - 본문 비교 예시처럼 named volume은 Docker가 관리하는 영구 저장소라 DB 데이터처럼 컨테이너 수명과 분리된 데이터에 적합하고, bind mount는 호스트 경로를 그대로 연결하므로 개발 중 소스 핫리로드 같은 시나리오에 어울리며, tmpfs는 메모리에만 살기 때문에 단기 비밀이나 임시 캐시에 씁니다.
- **컨테이너 데이터는 왜 기본적으로 휘발된다고 봐야 할까요?**
  - 컨테이너의 writable layer는 컨테이너가 사라지면 함께 폐기되도록 설계됐기 때문에, 본문에서 강조했듯이 `docker rm` 한 번에 모든 데이터가 같이 날아갑니다. 그래서 영속이 필요한 모든 데이터는 명시적으로 volume이나 bind mount로 컨테이너 바깥에 보관해야 합니다.
- **브리지 네트워크는 어떻게 컨테이너 이름 기반 통신을 가능하게 할까요?**
  - 본문에서 본 것처럼 user-defined bridge에 같이 붙은 컨테이너들은 Docker 내장 DNS 덕분에 IP가 아닌 컨테이너 이름·서비스 이름으로 서로를 찾을 수 있습니다. 기본 `bridge`와 달리 자동 service discovery가 켜진다는 점이 user-defined bridge를 권장하는 이유입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- [Docker 101 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- **Volume과 Network (현재 글)**
- Docker Compose (예정)
- 환경변수와 설정 (예정)
- Python 앱 컨테이너화 (예정)
- 데이터베이스와 함께 실행하기 (예정)
- Image 최적화 (예정)
- 배포용 Docker 구성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Manage data in Docker - Volumes](https://docs.docker.com/storage/volumes/)
- [Bind mounts](https://docs.docker.com/storage/bind-mounts/)
- [Networking overview](https://docs.docker.com/network/)
- [Use bridge networks](https://docs.docker.com/network/bridge/)

### 검증과 트러블슈팅

- [docker volume inspect reference](https://docs.docker.com/reference/cli/docker/volume/inspect/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/docker-101/ko)

Tags: Docker, Volume, Network, BindMount, Bridge