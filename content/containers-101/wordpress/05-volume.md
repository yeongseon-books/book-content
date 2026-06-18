---
series: containers-101
episode: 5
title: "바이브코딩을 위한 컨테이너 기초 (5/10): Volume"
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Containers
- Docker
- Volume
- Storage
language: ko
---

# 바이브코딩을 위한 컨테이너 기초 (5/10): Volume

이 글은 **바이브코딩을 위한 컨테이너 기초** 시리즈의 다섯 번째 글입니다.

AI가 데이터베이스가 포함된 앱을 만들어 줬습니다. 컨테이너를 재시작했더니 데이터가 모두 사라졌습니다. 컨테이너는 기본적으로 상태를 저장하지 않습니다. 데이터를 영구적으로 보존하려면 Volume을 이해해야 합니다.

---

## 오늘의 핵심 질문

AI가 PostgreSQL을 포함한 앱을 만들어 줬습니다. 테스트 데이터를 열심히 넣었는데 `docker restart` 후 모두 사라졌습니다. 데이터를 어떻게 보존할 수 있을까요?

> "Volume의 핵심은 컨테이너를 지워도 데이터를 남기는 메커니즘입니다. 비상태 컨테이너와 상태를 가진 데이터 저장소를 분리하는 것이 설계의 출발점입니다."

---

## 이 글에서 다룰 문제

- volume, bind mount, tmpfs는 무엇이 다를까요?
- 컨테이너를 지워도 데이터를 남기려면 어떤 선택을 해야 할까요?
- 바이브코딩으로 만든 앱에서 데이터베이스 데이터는 어디에 둬야 할까요?
- 개발 중 소스 코드를 컨테이너에 실시간으로 반영하려면?
- 백업과 복구는 어떻게 접근해야 할까요?

---

## 바이브코딩 관점에서 Volume이 중요한 이유

AI가 `docker-compose.yml`을 만들어 줄 때 volume 설정을 빠뜨리는 경우가 있습니다. 또는 올바른 volume 설정이 있어도 개발자가 `docker compose down -v`를 실행해서 데이터를 날리기도 합니다.

바이브코딩으로 만든 앱에서 데이터 관련 시나리오:

1. **PostgreSQL 데이터**: 컨테이너 재시작/업데이트 후에도 보존 필요
2. **사용자 업로드 파일**: 컨테이너와 별도로 관리 필요
3. **개발 중 소스 코드**: 코드 변경이 컨테이너에 즉시 반영되어야 함
4. **임시 세션 토큰**: 컨테이너 종료 후 사라져야 함

각 시나리오마다 다른 저장 방식이 필요합니다.

### 세 가지 저장 방식

```text
[ named volume ]
  Docker가 경로를 관리 → /var/lib/docker/volumes/<name>/_data
  컨테이너 삭제해도 데이터 유지
  예: DB 데이터, 업로드 파일

[ bind mount ]
  호스트 절대 경로를 직접 연결 → -v /home/user/src:/app
  개발 중 소스 코드 실시간 동기
  예: 바이브코딩 중 코드 변경 확인

[ tmpfs ]
  메모리에만 존재 → 컨테이너 종료 시 소멸
  예: 임시 토큰, 세션 파일
```

---

## 적용 전후: 데이터베이스 데이터 보존

**Before**: volume 없이 DB 실행

```bash
docker run -d --name pg -e POSTGRES_PASSWORD=secret postgres:16
# 컨테이너 삭제 시 데이터 전체 유실
docker rm -f pg
# → 모든 데이터 사라짐
```

**After**: named volume으로 데이터 분리

```bash
docker volume create pgdata
docker run -d --name pg \
  -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  postgres:16

# 컨테이너를 삭제해도 데이터는 그대로
docker rm -f pg

# 새 컨테이너로 같은 데이터 재연결
docker run -d --name pg \
  -v pgdata:/var/lib/postgresql/data \
  -e POSTGRES_PASSWORD=secret \
  postgres:16
# → 기존 데이터 모두 살아있음
```

**개발 중 코드 실시간 반영 (bind mount):**

```bash
docker run --rm -it \
  -v "$PWD":/app \
  -w /app \
  python:3.12-slim python -m app.main
# → 로컬 파일 수정이 컨테이너에 즉시 반영
```

---

## 자주 하는 실수

| 실수 | 결과 | 해결 방법 |
|------|------|-----------|
| DB 데이터를 컨테이너 내부에 저장 | 컨테이너 삭제 시 데이터 유실 | named volume 사용 |
| `docker compose down -v` 실수 | volume까지 삭제 | 운영 환경에서 `-v` 옵션 금지 |
| bind mount 권한 충돌 | 컨테이너 내부 쓰기 실패 | UID/GID 맞추기 |
| volume 백업 없음 | 장애 시 데이터 복구 불가 | 정기 백업 자동화 |
| 영속 데이터에 tmpfs 사용 | 재시작 시 데이터 소멸 | 목적에 맞는 저장소 선택 |

---

## AI 팁: Volume 설정 요청

AI에게 올바른 volume 설정을 포함한 `docker-compose.yml`을 요청하는 방법:

```
다음 서비스들을 docker-compose.yml로 만들어 주세요:
- FastAPI 앱
- PostgreSQL 데이터베이스

요구사항:
1. PostgreSQL 데이터가 컨테이너 재시작 후에도 보존되어야 합니다
2. 개발 중 FastAPI 코드 변경이 실시간으로 반영되어야 합니다
3. 비밀번호는 환경 변수로 주입합니다

volume 설정과 bind mount를 적절히 사용해 주세요.
```

AI는 named volume으로 DB 데이터를 보존하고 bind mount로 코드를 실시간 동기하는 설정을 만들어 줍니다.

---

## 체크리스트

- [ ] 데이터베이스 데이터를 named volume에 저장합니다
- [ ] `docker volume ls`와 `docker volume inspect`로 volume을 확인했습니다
- [ ] 개발 환경에서 bind mount로 코드를 실시간 동기합니다
- [ ] `docker compose down`에서 `-v` 옵션의 의미를 이해합니다
- [ ] 최소 한 번 백업과 복구 과정을 테스트해 봤습니다

---

## 처음 질문으로 돌아가기

**`docker restart` 후 데이터가 사라지는 이유와 해결 방법은?**

컨테이너의 쓰기 가능한 레이어는 컨테이너와 생명주기를 같이 합니다. 컨테이너가 삭제되면 그 안에 저장된 데이터도 함께 사라집니다. named volume을 사용하면 Docker가 별도 위치에 데이터를 저장하므로 컨테이너를 삭제해도 데이터가 보존됩니다.

---

## 정리

컨테이너는 상태를 담는 곳이 아니라 상태를 연결하는 실행 단위입니다. volume, bind mount, tmpfs를 목적에 맞게 구분해서 써야 데이터 보존과 개발 편의성을 함께 잡을 수 있습니다.

바이브코딩으로 만든 앱을 컨테이너로 패키징할 때 가장 먼저 해야 할 질문은 "이 데이터가 사라지면 안 되는가?"입니다. 대답이 "예"라면 named volume이 필요합니다.

다음 글에서는 데이터가 아니라 통신 관점으로 넘어가, 컨테이너들이 서로를 어떻게 찾고 연결하는지 Network를 살펴봅니다.

---

## 참고 자료

- [Docker volumes](https://docs.docker.com/storage/volumes/)
- [Bind mounts](https://docs.docker.com/storage/bind-mounts/)
- [tmpfs](https://docs.docker.com/storage/tmpfs/)
- Containers 101 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/containers-101/ko

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 컨테이너 기초 (1/10): Container란 무엇인가?
- 바이브코딩을 위한 컨테이너 기초 (2/10): Image와 Layer
- 바이브코딩을 위한 컨테이너 기초 (3/10): Runtime
- 바이브코딩을 위한 컨테이너 기초 (4/10): Dockerfile
- **바이브코딩을 위한 컨테이너 기초 (5/10): Volume (현재 글)**
- 바이브코딩을 위한 컨테이너 기초 (6/10): Network
- 바이브코딩을 위한 컨테이너 기초 (7/10): Registry
- 바이브코딩을 위한 컨테이너 기초 (8/10): Container Security
- 바이브코딩을 위한 컨테이너 기초 (9/10): Containers vs VMs
- 바이브코딩을 위한 컨테이너 기초 (10/10): 실전 컨테이너 앱 만들기

<!-- toc:end -->

Tags: 바이브코딩, Containers, Docker, Volume, DevOps
