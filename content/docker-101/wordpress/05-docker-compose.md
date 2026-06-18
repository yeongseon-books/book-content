---
title: "바이브코딩을 위한 Docker 기초 (5/10): Docker Compose"
series: docker-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Docker
- AI코딩
- 컨테이너
seo_description: "바이브코딩 시대, AI가 만든 docker-compose.yml을 읽고 수정하려면 depends_on과 healthcheck의 관계를 알아야 합니다"
---

# 바이브코딩을 위한 Docker 기초 (5/10): Docker Compose

이 글은 바이브코딩을 위한 Docker 기초 시리즈의 5번째 글입니다.

AI에게 "웹 앱, DB, 캐시를 한 번에 실행하는 설정 만들어줘"라고 요청하면 `docker-compose.yml` 파일이 생성됩니다. `docker compose up` 한 줄로 모든 서비스가 올라오는 것처럼 보입니다. 그런데 실행하면 앱이 DB에 연결하지 못하고 바로 종료됩니다. AI가 `depends_on: db`를 넣어 줬는데도요.

이 현상은 바이브코딩할 때 Compose에서 가장 많이 만나는 문제입니다. `depends_on`만으로는 DB가 실제로 요청을 받을 준비가 되었는지 보장하지 않습니다. 컨테이너가 시작됐다는 것과, 그 안의 서비스가 연결을 받을 준비가 됐다는 것은 다른 이야기입니다. AI가 만든 Compose 파일에서 이 차이를 알아채고 수정할 수 있어야 합니다.

Compose는 여러 컨테이너를 하나의 YAML 파일로 선언하는 도구입니다. 서비스, 네트워크, 볼륨, 의존 관계를 함께 정의하면 팀 전체가 같은 환경을 `docker compose up` 한 줄로 재현할 수 있습니다. 많은 팀에서 Compose는 첫 번째 인프라 코드입니다.

> Compose는 docker run의 편의 래퍼가 아니라 팀의 첫 번째 인프라 코드입니다. 서비스, 네트워크, 볼륨, 의존 관계를 YAML로 선언하면 사람의 기억이 아니라 파일로 환경이 재현 가능해집니다.

---

## 이 글에서 다룰 문제
- `depends_on`만 있는데 왜 앱이 DB에 연결하지 못할까요?
- healthcheck와 `depends_on`은 어떻게 함께 써야 할까요?
- AI가 만든 Compose 파일에서 무엇을 먼저 확인해야 할까요?
- `.env` 파일은 왜 Git에 올리면 안 될까요?
- `docker compose down`과 `docker compose down -v`는 무엇이 다를까요?

## Compose 핵심 구조 이해

- **Service**: 하나의 이미지에서 만들어지는 컨테이너입니다.
- **depends_on**: 시작 순서를 정의하지만, 서비스 준비 상태는 보장하지 않습니다.
- **healthcheck**: 서비스가 실제로 요청을 받을 준비가 됐는지 확인하는 기준입니다.
- **condition: service_healthy**: healthcheck가 통과된 후에 다음 서비스를 시작합니다.
- **volumes / networks**: 볼륨과 네트워크를 Compose 레벨에서 선언해 관리합니다.

## Before / After

**Before**: AI가 만든 Compose 파일에 `depends_on: db`만 있어서 앱이 DB보다 조금 빨리 시작해 연결 오류로 죽습니다.

**After**: DB에 healthcheck를 추가하고, 앱의 `depends_on`에 `condition: service_healthy`를 넣으면 DB가 준비된 후에만 앱이 시작됩니다.

```yaml
# AI가 자주 생성하는 패턴 (문제 있음)
services:
  web:
    depends_on:
      - db    # 컨테이너 시작 순서만 보장, 준비 상태 미보장

# 수정된 패턴 (올바름)
services:
  db:
    image: postgres:16
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  web:
    depends_on:
      db:
        condition: service_healthy    # DB healthcheck 통과 후 시작
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `depends_on`만 쓰고 healthcheck 없음 | DB 컨테이너가 시작했어도 아직 연결 불가 상태일 수 있음 | DB에 healthcheck 추가, `condition: service_healthy` 사용 |
| `.env` 파일을 Git에 커밋 | 비밀값 유출 | `.gitignore`에 `.env` 추가, `.env.example`만 커밋 |
| `docker compose down -v` 사용 | volume까지 삭제되어 DB 데이터 손실 | 데이터 삭제가 의도된 경우에만 사용 |
| 여러 프로젝트가 같은 포트 사용 | 포트 충돌로 두 번째 프로젝트가 실행 안 됨 | 프로젝트별로 포트 분리 또는 `.env`로 포트 변수화 |
| `up`만 반복하고 `down` 없이 재시작 | 이전 컨테이너 상태가 남아 예측하기 어려운 동작 | `down` 후 `up` 습관 또는 `--force-recreate` 사용 |

## AI에게 Docker 관련 요청하는 팁

- "DB healthcheck와 `condition: service_healthy`를 포함한 Compose 파일을 만들어줘"라고 명시적으로 요청하면 올바른 시작 순서 보장이 됩니다.
- "포트와 비밀번호 등 환경변수를 `.env` 파일로 분리해줘"라고 함께 요청하세요.
- AI가 만든 Compose 파일을 받으면, DB 서비스에 `healthcheck`가 있는지, 앱 서비스의 `depends_on`에 `condition`이 있는지 먼저 확인하세요.
- "이 Compose 파일에 `.env.example`도 만들어줘"라고 하면 팀원들이 필요한 환경변수를 파악할 수 있습니다.

## 운영 체크리스트

- [ ] DB 서비스에 healthcheck가 있습니다
- [ ] 앱 서비스의 `depends_on`에 `condition: service_healthy`가 있습니다
- [ ] `.env`가 `.gitignore`에 포함되어 있습니다
- [ ] `.env.example`이 존재합니다
- [ ] `docker compose down -v`의 의미를 이해하고 사용합니다

## 처음 질문으로 돌아가기

AI가 만든 Compose 파일에서 앱이 DB 연결 오류로 죽는다면, DB 서비스에 `healthcheck`가 있는지, 앱의 `depends_on`이 단순히 서비스 이름만 나열하는지 확인하세요. `condition: service_healthy`가 없다면 추가해야 합니다. 이 한 줄이 cold start 실패의 가장 흔한 원인을 해결합니다.

## 정리

Compose는 팀이 처음으로 갖게 되는 환경 코드입니다. AI가 만들어 준 Compose 파일을 그대로 쓰기 전에, healthcheck와 `depends_on` 조합이 올바른지, `.env`가 Git에 올라가지 않는지 확인하는 습관이 중요합니다. 다음 글에서는 환경변수와 설정 분리를 다룹니다.

## 참고 자료

### 공식 문서
- [Docker Documentation](https://docs.docker.com/)
- [Compose specification](https://docs.docker.com/compose/compose-file/)
- [Compose startup order](https://docs.docker.com/compose/how-tos/startup-order/)

### 관련 시리즈
- [Containers 101](../../containers-101/ko/)
- [Kubernetes 101](../../kubernetes-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 Docker 기초 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [바이브코딩을 위한 Docker 기초 (2/10): Image와 Container](./02-image-and-container.md)
- [바이브코딩을 위한 Docker 기초 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [바이브코딩을 위한 Docker 기초 (4/10): Volume과 Network](./04-volume-and-network.md)
- **바이브코딩을 위한 Docker 기초 (5/10): Docker Compose (현재 글)**
- [바이브코딩을 위한 Docker 기초 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [바이브코딩을 위한 Docker 기초 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [바이브코딩을 위한 Docker 기초 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [바이브코딩을 위한 Docker 기초 (9/10): Image 최적화](./09-image-optimization.md)
- [바이브코딩을 위한 Docker 기초 (10/10): 배포용 Docker 구성](./10-production-docker.md)
<!-- toc:end -->

Tags: 바이브코딩, Docker, AI코딩, 컨테이너
