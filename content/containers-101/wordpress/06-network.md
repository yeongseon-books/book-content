---
series: containers-101
episode: 6
title: "바이브코딩을 위한 컨테이너 기초 (6/10): Network"
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Containers
- Docker
- Networking
- Bridge
language: ko
---

# 바이브코딩을 위한 컨테이너 기초 (6/10): Network

이 글은 **바이브코딩을 위한 컨테이너 기초** 시리즈의 여섯 번째 글입니다.

AI가 FastAPI 앱과 PostgreSQL을 포함한 `docker-compose.yml`을 만들어 줬습니다. 앱에서 DB 주소를 어떻게 설정해야 할까요? IP를 직접 넣으면 컨테이너 재시작 후 연결이 끊깁니다. 이름으로 연결하는 방법을 알아야 합니다.

---

## 오늘의 핵심 질문

AI가 만든 `docker-compose.yml`에서 FastAPI가 PostgreSQL에 접속하려면 DB 주소를 어떻게 써야 할까요? `172.17.0.3` 같은 IP를 쓰면 왜 나중에 문제가 생길까요?

> "Network의 핵심은 포트 번호가 아니라 어떤 네트워크 드라이버를 선택했고, 컨테이너 간 또는 호스트와의 통신이 어떤 경로로 흐르는지입니다."

---

## 이 글에서 다룰 문제

- 같은 `docker-compose.yml`에 있는 서비스들이 서로를 어떻게 찾을까요?
- IP 주소 대신 서비스 이름을 써야 하는 이유는 무엇일까요?
- `-p`로 포트를 여는 것과 내부 통신의 차이는 무엇일까요?
- 데이터베이스를 외부에 노출하지 않으려면 어떻게 해야 할까요?
- 바이브코딩 앱에서 네트워크 설정 실수는 어떤 결과를 낳을까요?

---

## 바이브코딩 관점에서 컨테이너 네트워크가 중요한 이유

AI가 `docker-compose.yml`을 만들 때 종종 이런 실수를 합니다:

```yaml
services:
  api:
    image: myorg/api:latest
    environment:
      DB_HOST: 172.17.0.3  # 위험: IP 하드코딩
```

컨테이너가 재시작되면 IP가 바뀝니다. 연결이 끊깁니다. 또 다른 실수:

```yaml
  db:
    image: postgres:16
    ports:
      - "5432:5432"  # 위험: DB가 인터넷에 노출됨
```

개발 편의를 위해 포트를 열었다가 운영 서버에 그대로 배포하면 PostgreSQL이 인터넷에 공개됩니다.

이런 실수를 피하려면 컨테이너 네트워크의 기본 원리를 알아야 합니다.

### DNS 기반 서비스 연결

Docker Compose는 각 서비스에 대해 서비스 이름을 DNS 이름으로 등록합니다.

```yaml
services:
  api:
    environment:
      DB_HOST: db  # 서비스 이름 = DNS 이름
  db:
    image: postgres:16
```

`DB_HOST: db`로 설정하면 Docker 내부 DNS가 `db`를 해당 컨테이너의 IP로 자동 변환합니다. 컨테이너가 재시작되어도 DNS가 새 IP를 알려줍니다.

**핵심 개념:**

- **bridge**: 기본 가상 네트워크. user-defined bridge를 만들면 컨테이너 이름 DNS 해석 지원
- **host**: 호스트 네트워크를 그대로 공유. 격리 없음
- **overlay**: 여러 호스트에 걸친 논리 네트워크
- **none**: 네트워크 비활성
- **expose**: Dockerfile에서 포트를 문서화. 외부 공개 아님
- **publish (-p)**: 호스트 포트와 컨테이너 포트를 실제로 매핑

---

## 적용 전후: IP 하드코딩 제거

**Before**: IP 하드코딩

```yaml
services:
  api:
    image: myorg/api:latest
    environment:
      DB_HOST: 172.17.0.3  # 컨테이너 재시작 시 변경됨
  db:
    image: postgres:16
    ports:
      - "5432:5432"  # DB가 외부에 노출됨
```

**After**: 서비스 이름 기반 DNS + 격리 네트워크

```yaml
services:
  api:
    image: myorg/api:latest
    environment:
      DB_HOST: db  # 서비스 이름 = DNS 이름
    ports:
      - "8080:8080"  # 앱만 외부 노출
    networks: [backend]
  db:
    image: postgres:16
    # ports 없음: 외부에서 접근 불가
    networks: [backend]
networks:
  backend: {}
```

DB는 같은 네트워크 안에서 `db`라는 이름으로만 접근 가능합니다. 외부에서는 접근할 수 없습니다.

---

## 자주 하는 실수

| 실수 | 결과 | 해결 방법 |
|------|------|-----------|
| DB에 `-p 5432:5432` 추가 | DB가 인터넷에 노출 | DB는 내부 네트워크만 사용 |
| IP 하드코딩 | 재시작 시 연결 끊김 | 서비스 이름 사용 |
| 기본 bridge 그대로 사용 | DNS 이름 해석 안 됨 | user-defined network 사용 |
| host 모드 남용 | 포트 충돌, 격리 없음 | 필요할 때만 제한적 사용 |
| 미사용 네트워크 방치 | 리소스 낭비 | `docker network prune` 정기 실행 |

---

## AI 팁: 안전한 네트워크 설정 요청

AI에게 네트워크 설정을 포함한 `docker-compose.yml`을 요청하는 방법:

```
FastAPI 앱과 PostgreSQL을 포함한 docker-compose.yml을 만들어 주세요.

네트워크 요구사항:
1. FastAPI 앱은 외부에서 8080 포트로 접근 가능해야 합니다
2. PostgreSQL은 외부에서 접근 불가능해야 합니다 (보안)
3. FastAPI가 PostgreSQL에 접근할 때 IP가 아닌 서비스 이름을 사용해야 합니다
4. 컨테이너 재시작 후에도 연결이 유지되어야 합니다

내부 네트워크를 명시적으로 정의하고 각 서비스가 어떤 네트워크에 속하는지 표시해 주세요.
```

---

## 체크리스트

- [ ] `DB_HOST`에 IP 대신 서비스 이름을 사용합니다
- [ ] DB 서비스에 `-p` 옵션을 불필요하게 추가하지 않았습니다
- [ ] user-defined network를 명시적으로 정의했습니다
- [ ] `docker network inspect`로 네트워크 구성을 확인했습니다
- [ ] `expose`와 `ports(-p)`의 차이를 이해합니다

---

## 처음 질문으로 돌아가기

**FastAPI에서 PostgreSQL 주소를 `172.17.0.3`으로 쓰면 왜 나중에 문제가 생길까요?**

컨테이너는 재시작되거나 재생성될 때 새로운 IP를 받습니다. `172.17.0.3`이 오늘은 PostgreSQL이지만 내일은 다른 컨테이너가 될 수 있습니다. 서비스 이름 `db`를 사용하면 Docker 내부 DNS가 항상 올바른 컨테이너 IP를 알려줍니다.

---

## 정리

컨테이너 네트워킹의 핵심은 두 가지입니다. 첫째, 내부 서비스 간 통신은 서비스 이름(DNS)으로 합니다. 둘째, 외부 노출은 명시적으로 필요한 서비스만 `-p`로 엽니다.

이 원칙만 지키면 IP 변경 문제도 없고, 데이터베이스가 인터넷에 노출되는 사고도 방지할 수 있습니다.

다음 글에서는 완성된 이미지를 팀과 공유하고 배포하는 방법, 즉 Registry를 살펴봅니다.

---

## 참고 자료

- [Docker networking overview](https://docs.docker.com/network/)
- [Bridge networks](https://docs.docker.com/network/bridge/)
- [DNS in Docker](https://docs.docker.com/network/network-tutorial-standalone/)
- Containers 101 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/containers-101/ko

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 컨테이너 기초 (1/10): Container란 무엇인가?
- 바이브코딩을 위한 컨테이너 기초 (2/10): Image와 Layer
- 바이브코딩을 위한 컨테이너 기초 (3/10): Runtime
- 바이브코딩을 위한 컨테이너 기초 (4/10): Dockerfile
- 바이브코딩을 위한 컨테이너 기초 (5/10): Volume
- **바이브코딩을 위한 컨테이너 기초 (6/10): Network (현재 글)**
- 바이브코딩을 위한 컨테이너 기초 (7/10): Registry
- 바이브코딩을 위한 컨테이너 기초 (8/10): Container Security
- 바이브코딩을 위한 컨테이너 기초 (9/10): Containers vs VMs
- 바이브코딩을 위한 컨테이너 기초 (10/10): 실전 컨테이너 앱 만들기

<!-- toc:end -->

Tags: 바이브코딩, Containers, Docker, Networking, DevOps
