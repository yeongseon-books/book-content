---
series: docker-101
episode: 4
title: "Docker 101 (4/10): Volume과 Network"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/256"
    published_at: '2026-06-01'
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

## 이 글에서 다룰 문제

- volume, bind mount, tmpfs는 각각 언제 써야 할까요?
- 컨테이너 데이터는 왜 기본적으로 휘발된다고 봐야 할까요?
- 브리지 네트워크는 어떻게 컨테이너 이름 기반 통신을 가능하게 할까요?
- 이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?
- 초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?

## 핵심 개념

컨테이너 운영에서 가장 흔한 사고는 화려한 분산 시스템 문제보다 훨씬 단순한 곳에서 시작합니다. 재시작했더니 데이터가 사라졌고, 앱 컨테이너가 DB 컨테이너에 접속하지 못하는 문제입니다. 둘 다 volume과 network 모델을 정확히 잡으면 예방 가능한 사고입니다.

### 스토리지 유형 비교

| 유형 | 관리 주체 | 수명 | 주 용도 | 운영 적합도 |
|------|-----------|------|---------|------------|
| **Named volume** | Docker | 컨테이너와 독립 | DB 데이터, 영구 상태 | 운영 기본 |
| **Bind mount** | 호스트 OS | 호스트 파일 수명 | 개발 중 소스 코드 반영 | 개발 전용 |
| **tmpfs** | 메모리 | 컨테이너 수명 | 비밀값, 임시 파일 | 보안 데이터 |
| **Anonymous volume** | Docker | 컨테이너 수명 | 임시 데이터 | 비권장 |

### 네트워크 드라이버 비교

| 드라이버 | 설명 | 주 용도 |
|---------|------|---------|
| **bridge** | 한 호스트 내 컨테이너 연결 | 로컬 개발, 기본값 |
| **host** | 호스트 네트워크 직접 사용 | 고성능 필요 시 (보안 위험) |
| **overlay** | 여러 호스트 간 연결 | Docker Swarm, 분산 환경 |
| **none** | 네트워크 없음 | 완전 격리 필요 시 |
| **macvlan** | MAC 주소 부여 | 레거시 앱 통합 |

이 중에서 실무에서 가장 자주 쓰는 조합은 named volume과 user-defined bridge입니다. 하나는 상태를 보존하고, 다른 하나는 이름 기반 통신을 안정적으로 만들어 줍니다.

## 전과 후

**Before**: DB 데이터를 컨테이너 내부에 저장해 재시작 때마다 잃고, 다른 컨테이너를 `localhost`로 찾으려다 실패합니다.

**After**: named volume으로 데이터를 유지하고, user-defined bridge 위에서 컨테이너 이름으로 통신합니다.

이 차이는 작아 보여도 운영 감각을 완전히 바꿉니다. 상태는 외부화하고, 통신은 명시적 네트워크로 연결한다는 원칙이 생기기 때문입니다.

## 실습: volume과 network를 5단계로 익히기

### 1단계 — named volume 만들기

```bash
# volume 생성
docker volume create app-data

# volume을 마운트해 컨테이너 실행
docker run -d --name db \
  -v app-data:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=app \
  postgres:16

# volume 상세 정보 확인
docker volume inspect app-data
# Mountpoint를 보면 호스트 어디에 저장됐는지 알 수 있음

# volume 목록
docker volume ls
```

named volume은 컨테이너와 독립적으로 존재합니다. 컨테이너를 지웠다고 해서 데이터까지 곧바로 사라지지 않는 이유가 여기에 있습니다. `docker rm db`를 해도 `app-data` volume은 남아 있습니다.

### 2단계 — bind mount 사용하기

```bash
# 현재 디렉터리를 컨테이너 /app에 마운트 (개발용)
docker run --rm \
  -v "$PWD":/app \
  -w /app \
  python:3.12-slim \
  python app.py

# 로컬 소스 변경이 즉시 컨테이너에 반영됨
# 하지만 운영에서는 권한 이슈 주의
```

bind mount는 개발 환경에서 특히 유용합니다. 로컬 소스코드를 바로 컨테이너에 반영할 수 있기 때문입니다. 다만 운영에서는 호스트 의존성과 권한 이슈가 커지므로 신중해야 합니다.

bind mount 권한 문제가 자주 발생하는 이유는 호스트 파일 소유자와 컨테이너 내 실행 사용자 UID가 다를 때입니다. 개발에서는 `--user $(id -u):$(id -g)` 옵션으로 호스트 사용자 ID를 그대로 사용할 수 있습니다.

### 3단계 — user-defined bridge 만들기

```bash
# 사용자 정의 네트워크 생성
docker network create app-net

# 네트워크 상세 정보
docker network inspect app-net

# DB 컨테이너를 네트워크에 연결
docker run -d \
  --network app-net \
  --name db \
  -e POSTGRES_PASSWORD=dev \
  -e POSTGRES_DB=app \
  postgres:16

# 앱 컨테이너를 같은 네트워크에 연결
# DB_HOST=db → 컨테이너 이름으로 접속 가능
docker run -d \
  --network app-net \
  --name api \
  -e DB_HOST=db \
  -e DB_PORT=5432 \
  -p 8000:8000 \
  myapp:1.0
```

이 단계의 핵심은 `db`라는 이름이 곧 접속 대상이 된다는 사실입니다. user-defined bridge는 컨테이너 이름 기반 DNS를 자동으로 제공하므로, IP 주소를 직접 관리할 필요가 없습니다.

### 4단계 — 통신 확인하기

```bash
# api 컨테이너에서 db로 ping
docker exec api ping -c 3 db

# api 컨테이너에서 db로 TCP 연결 확인
docker exec api nc -zv db 5432

# api에서 직접 DB 쿼리 실행
docker exec db psql -U postgres -d app -c "SELECT 1"

# 네트워크 내 컨테이너 목록 확인
docker network inspect app-net | jq '.[0].Containers'
```

컨테이너 네트워크 문제는 감으로 해결하기 어렵습니다. 따라서 실제로 이름 해석이 되는지, 포트에 도달하는지, 어느 단계에서 막히는지 확인하는 습관이 중요합니다.

### 5단계 — volume 백업과 복구

```bash
# volume 백업: app-data의 내용을 현재 디렉터리에 tar로 저장
docker run --rm \
  -v app-data:/data \
  -v "$PWD":/backup \
  alpine \
  tar czf /backup/data-$(date +%Y%m%d).tgz -C /data .

# 백업 확인
ls -lh data-*.tgz

# volume 복구: 새 volume에 백업 파일 복원
docker volume create app-data-restored
docker run --rm \
  -v app-data-restored:/data \
  -v "$PWD":/backup \
  alpine \
  tar xzf /backup/data-*.tgz -C /data
```

volume이 영구적이라고 해서 안전한 것은 아닙니다. 삭제, 손상, 잘못된 마이그레이션은 언제든 일어날 수 있습니다. 그래서 영속성 다음 단계는 항상 백업입니다.

### 실행 뒤 바로 확인할 것

- `docker volume inspect app-data`에서 `Mountpoint`가 존재하고, 컨테이너를 삭제해도 volume이 남아 있는지 확인합니다.
- `docker exec api ping -c 1 db`가 성공하면 이름 기반 DNS가 정상 동작하는 것입니다.
- 백업 명령을 실행했다면 현재 디렉터리에 `.tgz` 파일이 생겼는지까지 확인합니다.

### 트러블슈팅

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| `localhost`로 DB 접속 실패 | 다른 컨테이너는 localhost가 자기 자신 | 컨테이너 이름(`db`)을 DB_HOST로 사용 |
| bind mount 권한 오류 | 호스트 UID와 컨테이너 사용자 불일치 | `--user $(id -u):$(id -g)` 옵션 추가 |
| `ping: db: Name or service not known` | 같은 네트워크에 없음 | `--network app-net` 플래그 확인 |
| volume 삭제 후 데이터 분실 | `docker volume rm` 또는 `docker compose down -v` 실수 | 삭제 전 백업 필수 |
| default bridge에서 이름 해석 안 됨 | default bridge는 DNS 미지원 | user-defined bridge 사용 |

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| 컨테이너 내부 경로에 직접 저장 | 재시작·재생성 시 데이터 소실 | named volume 또는 bind mount 사용 |
| default bridge 그대로 사용 | 이름 해석 불가, 격리 한계 | user-defined bridge 생성 후 사용 |
| bind mount 권한 무시 | 수정 충돌, `permission denied` 오류 | UID 일치 확인, `--user` 옵션 사용 |
| volume 백업 안 함 | 사고 시 복구 경로 없음 | 정기 백업 스크립트 구성 |
| `--network host` 남용 | 포트 충돌, 보안 격리 약화 | 필요한 포트만 `-p`로 노출 |

## 네트워크 진단 명령

```bash
# 모든 네트워크 목록
docker network ls

# 특정 네트워크 상세 정보
docker network inspect app-net

# 컨테이너가 어떤 네트워크에 연결됐는지
docker inspect api | jq '.[0].NetworkSettings.Networks'

# 실행 중인 컨테이너에 네트워크 추가 연결
docker network connect another-net api

# 컨테이너에서 네트워크 연결 해제
docker network disconnect app-net api

# 사용하지 않는 네트워크 정리
docker network prune -f
```

## 실무에서는 이렇게 이어집니다

Kubernetes로 가더라도 개념은 크게 바뀌지 않습니다. volume은 PersistentVolume 같은 영속 저장 개념으로 이어지고, network와 이름 기반 통신은 Service DNS로 이어집니다. Docker에서 이 멘탈 모델을 먼저 익혀 두면 이후 전환이 훨씬 자연스럽습니다.

또한 운영 사고 대응에서도 같은 감각이 필요합니다. 데이터 손실은 storage 문제인지, 접속 실패는 network 문제인지 먼저 구분해야 원인 분석이 빨라집니다.

## 운영 체크리스트

- [ ] DB 데이터가 named volume에 저장됩니다.
- [ ] 컨테이너들이 user-defined bridge 네트워크를 사용합니다.
- [ ] 컨테이너 이름으로 서로 통신할 수 있습니다.
- [ ] volume 백업 절차가 문서화되어 있습니다.
- [ ] bind mount는 개발 환경에서만 사용합니다.
- [ ] `--network host`를 운영에서 쓰지 않습니다.

## 연습 문제

1. PostgreSQL 컨테이너를 named volume과 함께 실행하고, 컨테이너를 삭제 후 재생성해도 데이터가 유지되는지 확인해 보세요.
2. 두 컨테이너를 user-defined bridge에 연결하고 이름(`ping db`)으로 통신하게 해 보세요.
3. `tar`를 사용해 volume 내용을 백업하고 새 volume에 복구해 보세요.
4. `docker network inspect`를 사용해 컨테이너의 IP 주소와 연결된 네트워크를 확인해 보세요.

## 처음 질문으로 돌아가기

- **volume, bind mount, tmpfs는 각각 언제 써야 할까요?**
  - named volume은 운영 기본으로 DB 데이터나 영구 상태를 저장합니다. bind mount는 개발 중 소스 코드 변경을 즉시 반영할 때 씁니다. tmpfs는 메모리에만 저장되어 컨테이너 종료 시 사라지므로, 비밀값이나 임시 캐시에 적합합니다.

- **컨테이너 데이터는 왜 기본적으로 휘발된다고 봐야 할까요?**
  - 컨테이너 내부의 파일시스템은 writable layer로 구현되고, 이 레이어는 컨테이너가 삭제될 때 함께 사라집니다. 데이터를 유지하려면 반드시 컨테이너 외부(volume 또는 bind mount)에 저장해야 합니다.

- **브리지 네트워크는 어떻게 컨테이너 이름 기반 통신을 가능하게 할까요?**
  - user-defined bridge 네트워크는 내장 DNS 서버를 통해 컨테이너 이름을 IP로 자동 해석합니다. 따라서 `DB_HOST=db`처럼 컨테이너 이름을 그대로 호스트명으로 사용할 수 있습니다. default bridge 네트워크에서는 이 기능이 없습니다.

- **이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?**
  - `--network host`는 호스트 네트워크를 그대로 노출하므로 보안 격리가 깨집니다. bind mount는 호스트 파일시스템에 직접 접근하므로 경로 선택에 신중해야 합니다. volume 백업 없이는 사고 복구가 불가능합니다.

- **초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?**
  - 다른 컨테이너를 `localhost`로 접근하려다 실패하는 경우가 가장 많습니다. 각 컨테이너에서 `localhost`는 자기 자신을 가리킵니다. 컨테이너 이름(예: `db`)을 호스트명으로 사용하고, user-defined bridge 네트워크에 함께 연결해야 합니다.

## 정리

데이터와 네트워크는 컨테이너 운영의 기초 체력입니다. image와 container를 이해했다면, 이제 상태를 어디에 둘지와 컨테이너가 서로를 어떻게 찾을지를 함께 설계해야 합니다. volume은 영속성을, network는 연결 가능성을 담당합니다.

다음 글에서는 Docker Compose를 봅니다. 지금까지 개별 명령으로 다룬 컨테이너, 네트워크, 볼륨을 하나의 YAML로 묶어 반복 가능한 환경으로 만드는 단계입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- [Docker 101 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- **Docker 101 (4/10): Volume과 Network (현재 글)**
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- [Docker 101 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [Docker 101 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [Docker 101 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [Docker 101 (9/10): Image 최적화](./09-image-optimization.md)
- [배포용 Docker 구성](./10-production-docker.md)

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
