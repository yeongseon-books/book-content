---
series: docker-101
episode: 6
title: "Docker 101 (6/10): 환경변수와 설정"
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
  - Config
  - EnvVar
  - Secret
  - 12Factor
seo_description: 하나의 이미지에 환경별 설정과 비밀값을 안전하게 주입하는 원칙을 설명합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (6/10): 환경변수와 설정

이 글은 Docker 101 시리즈의 6번째 글입니다.

컨테이너를 만들기 시작하면 곧 이런 요구가 생깁니다. 개발 환경에서는 디버그 로그를 켜고 싶고, 스테이징과 운영에서는 다른 데이터베이스 주소를 써야 하며, 비밀번호와 토큰은 코드나 이미지 안에 넣고 싶지 않습니다. 그런데 이때 환경마다 다른 이미지를 따로 빌드하기 시작하면 재현성은 금방 무너집니다.

좋은 컨테이너 운영의 핵심은 이미지와 환경을 분리하는 것입니다. 이미지는 불변 산출물로 유지하고, 환경별 차이는 런타임 설정으로 주입해야 합니다. 이 원칙이 바로 Twelve-Factor의 config 원칙과도 맞닿아 있습니다.

![Docker 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/06/06-01-concept-at-a-glance.ko.png)
*Docker 101 6장 흐름 개요*

## 먼저 던지는 질문

- 하나의 이미지로 여러 환경을 어떻게 지원할 수 있을까요?
- `ENV`와 `ARG`는 무엇이 다를까요?
- 환경변수, 설정 파일, secret은 어떻게 구분하는 편이 좋을까요?

## 왜 이 글이 중요한가

컨테이너가 재현 가능하려면 dev, staging, prod를 거치면서도 이미지 자체는 바뀌지 않아야 합니다. 환경별 차이를 코드에 하드코딩하거나, 환경마다 다른 이미지를 다시 빌드하면 "같은 애플리케이션"이라는 전제가 사라집니다.

또한 secret을 어디에 두는지는 단순한 편의 문제가 아니라 보안 문제입니다. 이미지 안에 비밀번호가 들어간 순간, 그 이미지를 받은 모든 곳에 비밀값도 함께 복제됩니다. 한번 새어 나간 secret은 되돌릴 수 없습니다.

## 한눈에 보는 개념

## 핵심 용어

- **ENV**: Dockerfile 안에 정의하는 기본 환경변수입니다.
- **ARG**: 빌드 시점에만 사용하는 변수입니다.
- **`-e` / `--env-file`**: 실행 시점에 값을 주입하는 방법입니다.
- **Config volume**: 설정 파일을 마운트해 전달하는 방식입니다.
- **Secret store**: Vault, Doppler 같은 외부 비밀값 저장소입니다.

여기서 가장 많이 헷갈리는 것은 `ENV`와 `ARG`입니다. `ARG`는 빌드 단계에만 쓰이고, `ENV`는 최종 이미지와 실행 환경에 남습니다. 따라서 secret을 `ENV`에 넣는 실수는 특히 치명적입니다.

## 전과 후

**Before**: dev용 이미지와 prod용 이미지를 따로 빌드해 각각 운영합니다.

**After**: 이미지는 하나만 유지하고, 환경별 차이는 환경변수와 외부 설정으로 주입합니다.

이 차이는 팀 운영에서 매우 큽니다. 하나의 이미지가 여러 환경을 그대로 통과해야, 스테이징에서 검증한 결과를 운영에서도 믿을 수 있기 때문입니다.

## 실습: 환경변수와 설정을 5단계로 정리하기

### 1단계 — Dockerfile의 ENV와 ARG

```dockerfile
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION} \
    LOG_LEVEL=INFO
```

`ARG`는 빌드 시 값을 바꾸는 데 쓰고, `ENV`는 컨테이너 실행 시 기본값으로 남깁니다. 둘의 역할을 분리해 두어야 어떤 값이 빌드 산출물에 들어가고, 어떤 값이 런타임에만 결정되는지 명확해집니다.

### 2단계 — 런타임 주입

```bash
docker run --rm \
  -e LOG_LEVEL=DEBUG \
  -e DB_URL=postgres://user:pass@db:5432/app \
  myapp:1.0
```

환경별 차이는 가능한 한 실행 시점에 주입하는 편이 좋습니다. 그래야 이미지를 다시 빌드하지 않고도 같은 산출물을 여러 환경에서 재사용할 수 있습니다.

### 3단계 — `--env-file`

```bash
# .env.staging
LOG_LEVEL=INFO
DB_URL=postgres://user:pass@stg-db:5432/app

docker run --rm --env-file .env.staging myapp:1.0
```

파일 기반 주입은 환경별 구성을 분리하는 데 유용합니다. 특히 로컬 개발, 스테이징처럼 반복 실행 환경에서는 `--env-file`이 가장 단순한 운영 단위가 되기도 합니다.

### 4단계 — Compose에서 변수 사용

```yaml
services:
  web:
    image: myapp:1.0
    env_file: .env.${ENV:-dev}
    environment:
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
```

기본값 문법까지 함께 쓰면 누락된 값을 어느 정도 방어할 수 있습니다. 다만 기본값이 있다고 해서 모든 문제가 해결되는 것은 아닙니다. 필수값은 별도로 검증해야 합니다.

### 5단계 — secret 외부화

```bash
# Doppler
doppler run -- docker compose up -d
# Vault (envconsul)
envconsul -secret secret/app -- docker compose up -d
```

이 단계가 실제 운영 품질을 가릅니다. secret을 Compose 파일이나 Dockerfile에 직접 넣지 않고, 외부 secret 제공자를 통해 런타임에 주입해야 노출 면적을 줄일 수 있습니다.

### 실행 뒤 바로 확인할 것

- `docker run --env-file .env.staging myapp:1.0`로 실행했을 때 로그나 진단 엔드포인트에서 `LOG_LEVEL`, `DB_URL` 같은 값이 의도한 환경으로 들어왔는지 확인합니다.
- 필수 변수를 비워 실행해 보면 애플리케이션이 조용히 진행하지 않고 빠르게 실패해야 합니다.

### 잘 안 될 때 먼저 볼 것

- 값이 비어 들어가면 `${VAR:-default}` 기본값 문법보다 `.env` 파일 경로와 shell export 상태를 먼저 확인합니다.
- secret이 이미지에 남았는지 의심되면 `docker history`와 Dockerfile의 `ENV` 사용 위치를 다시 봅니다.

## 이 코드에서 먼저 봐야 할 점

- `${VAR:-default}` 같은 기본값은 값 누락을 완화해 줍니다.
- `.env.dev`, `.env.staging`처럼 환경별 파일을 나누면 차이가 명시적으로 드러납니다.
- secret은 Compose나 이미지 안에 두지 않고 외부 시스템에서 주입해야 합니다.

결국 설정의 핵심은 "어디에 값을 둘 것인가"보다 "무엇을 이미지 밖으로 밀어낼 것인가"에 있습니다. 비밀값과 환경별 차이는 가능하면 모두 런타임 문맥으로 남겨 두는 편이 좋습니다.

## 자주 하는 실수 다섯 가지

1. **secret을 Dockerfile `ENV`에 넣습니다.** 이미지 안에 영구적으로 박제됩니다.
2. **`.env`를 Git에 커밋합니다.** 유출 사고로 이어집니다.
3. **환경마다 별도 이미지를 다시 빌드합니다.** 재현성이 깨집니다.
4. **필수 변수가 비어 있어도 그냥 실행되게 둡니다.** 런타임 사고가 늦게 드러납니다.
5. **로그에 환경변수 전체를 출력합니다.** secret 노출로 이어질 수 있습니다.

이 다섯 가지는 처음엔 편해 보일 수 있습니다. 하지만 운영에서 문제를 만나면 모두 추적성과 보안을 동시에 악화시킵니다. 설정을 외부화하는 습관은 초반부터 강하게 들이는 편이 좋습니다.

## 실무에서는 이렇게 이어집니다

성숙한 팀은 Vault, Doppler, 1Password 같은 시스템을 런타임 secret 제공자로 사용하고, 코드 저장소에는 변수 이름과 예시값만 남깁니다. 즉, 저장소는 계약을 설명하고, 실제 값은 환경이 책임지게 만드는 구조입니다.

또한 애플리케이션 시작 시점에 필수 환경변수를 검증해, 값이 없으면 빠르게 실패하게 만듭니다. 조용히 빈 문자열로 실행되는 시스템은 언젠가 더 비싼 장애로 돌아옵니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 이미지는 환경에 중립적이어야 하고, 환경 차이는 변수로 표현해야 합니다.
- 이미지 안에 들어간 secret은 이미 유출된 것으로 봐야 합니다.
- 필수 변수는 시작 시 검증하고 빠르게 실패해야 합니다.
- 기본값은 편의보다 안전한 방향으로 두는 편이 좋습니다.
- `.env.example`은 항상 함께 관리해야 합니다.

이 감각을 잡고 나면 다음 글의 Python 앱 컨테이너화에서 왜 healthcheck, 포트, 데이터베이스 주소를 모두 런타임 문맥으로 다루는지 자연스럽게 연결됩니다.

## 체크리스트

- [ ] 이미지는 환경에 중립적입니다.
- [ ] secret은 외부 저장소에서 주입됩니다.
- [ ] `.env.example`이 존재합니다.
- [ ] 시작 시 필수 변수 검증이 있습니다.

## 연습 문제

1. 같은 이미지를 dev와 staging에서 각각 실행해 보세요.
2. `--env-file`로 환경별 설정을 분리해 보세요.
3. 필수 환경변수가 없으면 시작에 실패하는 검증 코드를 추가해 보세요.

## 정리 및 다음 단계

설정 분리는 프로덕션 안정성의 절반입니다. 이미지는 하나로 유지하고, 환경별 차이와 비밀값은 런타임에 주입해야 재현성과 보안을 동시에 지킬 수 있습니다. 컨테이너를 잘 만든다는 것은 Dockerfile만 잘 쓰는 것이 아니라, 무엇을 이미지 밖에 남겨 둘지까지 결정하는 일입니다.

다음 글에서는 Python 앱을 실제로 컨테이너화합니다. 설정 원칙을 바탕으로 FastAPI 앱을 production-grade 수준으로 묶을 때 어떤 점을 챙겨야 하는지 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **하나의 이미지로 여러 환경을 어떻게 지원할 수 있을까요?**
  - 본문에서 강조했듯이 환경별 값(API 엔드포인트, DB 호스트 등)을 이미지 안에 박지 말고, 컨테이너 시작 시점에 환경 변수나 외부 설정 파일로 주입하면 됩니다. 이렇게 하면 dev·staging·prod가 모두 같은 이미지를 쓰면서 각자 다른 설정으로 동작해 "이미지 = 코드, 환경 = 설정"이라는 12-factor 원칙이 자연스럽게 지켜집니다.
- **`ENV`와 `ARG`는 무엇이 다를까요?**
  - 본문 예시처럼 `ARG`는 빌드 시점에만 살아 있는 변수로 이미지에 흔적을 남기지 않고, `ENV`는 이미지에 함께 구워져 컨테이너 실행 중에도 그대로 보입니다. 그래서 빌드 토큰 같은 일회성 값은 `ARG`로, 앱이 런타임에 읽어야 하는 값은 `ENV`로 분리해야 비밀이 이미지에 새지 않습니다.
- **환경변수, 설정 파일, secret은 어떻게 구분하는 편이 좋을까요?**
  - 본문에서 본 것처럼 변경이 잦은 짧은 값은 환경변수가 편하고, 길거나 구조가 있는 값은 마운트된 설정 파일이 낫고, 토큰·키 같은 민감 데이터는 docker secret이나 외부 vault에 두어 이미지·로그·`docker inspect`에 노출되지 않게 해야 합니다. 즉 "민감도 + 형태"에 따라 저장소를 다르게 골라야 운영 안전성이 유지됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- [Docker 101 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [Docker 101 (4/10): Volume과 Network](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- **환경변수와 설정 (현재 글)**
- Python 앱 컨테이너화 (예정)
- 데이터베이스와 함께 실행하기 (예정)
- Image 최적화 (예정)
- 배포용 Docker 구성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [The Twelve-Factor App - Config](https://12factor.net/config)
- [Set environment variables in containers](https://docs.docker.com/engine/reference/commandline/run/#env)
- [Compose - environment variables](https://docs.docker.com/compose/environment-variables/)
- [Manage secrets with Docker](https://docs.docker.com/engine/swarm/secrets/)

### 검증과 트러블슈팅

- [Environment variables in Compose](https://docs.docker.com/compose/how-tos/environment-variables/set-environment-variables/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/docker-101/ko)

Tags: Docker, Config, EnvVar, Secret, 12Factor