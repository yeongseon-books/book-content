---
series: docker-101
episode: 1
title: "Docker 101 (1/10): Docker란 무엇인가?"
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
  - Container
  - DevOps
  - Linux
  - Virtualization
seo_description: Docker가 환경 차이를 어떻게 없애는지 첫 컨테이너 실습과 함께 설명합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (1/10): Docker란 무엇인가?

Docker를 처음 접하면 대개 이렇게 이해합니다. "개발 환경을 쉽게 맞춰 주는 도구구나." 맞는 말입니다. 하지만 이 설명만으로는 왜 팀들이 Docker를 표준처럼 쓰는지, 왜 컨테이너를 하나의 운영 단위로 보는지까지는 잘 보이지 않습니다. 진짜 핵심은 편의성보다 재현성에 있습니다. 누가 실행하든, 어디서 실행하든, 같은 이미지를 기준으로 같은 동작을 만들 수 있어야 한다는 문제를 Docker가 정면으로 다루기 때문입니다.

현업에서는 이 차이가 생각보다 큽니다. 개발자 노트북, CI, 스테이징, 운영 환경이 서로 조금씩 다르면 문제는 늘 애매하게 터집니다. 코드가 잘못된 것인지, 의존성이 다른 것인지, 운영 서버 설정이 다른 것인지 분간하는 데 시간을 다 써 버리기 쉽습니다. Docker는 바로 그 모호함을 줄이는 도구입니다.

이 글은 Docker 101 시리즈의 첫 번째 글입니다. 여기서는 Docker를 가상머신과 어떻게 다르게 봐야 하는지, image·container·registry가 어떤 관계로 맞물리는지, 그리고 첫 컨테이너 실습에서 무엇을 확인해야 하는지까지 한 번에 정리합니다.

## 먼저 던지는 질문

- Docker는 정확히 무엇을 해 주는 도구일까요?
- 컨테이너와 가상머신은 무엇이 다를까요?
- image, container, registry는 어떤 관계로 이해해야 할까요?

## 큰 그림

![Docker 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/01/01-01-concept-at-a-glance.ko.png)

*Docker 101 1장 흐름 개요*

## 왜 이 글이 중요한가

환경 차이는 입문자만 힘들게 하는 문제가 아닙니다. 숙련된 팀도 같은 문제로 시간을 잃습니다. 로컬에서는 되는데 CI에서만 실패하고, 어떤 개발자 노트북에서는 되는데 다른 노트북에서는 라이브러리 버전이 달라 오류가 나는 장면은 너무 흔합니다. 이런 문제는 개인 역량보다 시스템 설계의 문제에 가깝습니다.

Docker가 중요한 이유는 단순합니다. 코드만 공유하는 것이 아니라 실행 환경까지 함께 공유하게 만들기 때문입니다. 즉, 팀이 "어떻게 실행해야 하는가"를 위키 문서나 입소문이 아니라 이미지와 명령으로 표준화할 수 있습니다.

## 한눈에 보는 개념

## 핵심 용어

- **Image**: 코드, 라이브러리, 런타임을 포함한 실행 가능한 패키지입니다.
- **Container**: 이미지를 실제로 실행한 인스턴스입니다.
- **Registry**: 이미지를 저장하고 배포하는 저장소입니다. 예를 들어 Docker Hub, GHCR이 있습니다.
- **Daemon**: 컨테이너를 생성하고 관리하는 백그라운드 프로세스입니다.
- **Layer**: 이미지 내부에서 변경이 쌓이는 단위입니다.

이 용어는 처음엔 비슷해 보여도 역할이 분명히 다릅니다. 특히 image와 container를 분리해서 이해하지 못하면 이후 Dockerfile, volume, 배포 운영까지 전부 흐려집니다. 이미지는 배포 단위이고, 컨테이너는 실행 단위라는 구분부터 정확히 잡는 것이 좋습니다.

## Before / After

**Before**: "제 노트북에서는 돌아갑니다." 새 팀원 환경 구성에 반나절이 걸립니다.

**After**: `docker run myapp` 한 줄로 같은 환경을 바로 실행합니다.

이 변화가 중요한 이유는 설치 시간이 짧아져서가 아닙니다. 팀이 같은 문제를 같은 방식으로 재현할 수 있게 되기 때문입니다. 재현성이 생기면 디버깅이 쉬워지고, 디버깅이 쉬워지면 배포 속도와 운영 안정성도 함께 올라갑니다.

## 실습: 첫 컨테이너를 5단계로 실행해 보기

### 1단계 — 설치 확인

```bash
docker --version
# Docker version 25.x.x
docker run hello-world
```

가장 먼저 확인할 것은 Docker가 설치되었는가가 아니라, 실제로 이미지를 받아 컨테이너를 실행할 수 있는가입니다. `hello-world`는 바로 그 확인용으로 가장 적절합니다.

### 2단계 — 공식 이미지 실행

```bash
docker run -it --rm python:3.12-slim python -c "print('hi')"
```

이 명령은 Python이 로컬에 설치되어 있지 않아도, 이미지 안의 런타임으로 바로 명령을 실행할 수 있음을 보여 줍니다. 여기서 중요한 포인트는 "내 컴퓨터에 Python을 맞춰 깔았다"가 아니라 "필요한 런타임을 이미지가 이미 포함한다"는 점입니다.

### 3단계 — 백그라운드 실행

```bash
docker run -d --name web -p 8080:80 nginx
curl http://localhost:8080
```

웹 서버처럼 계속 살아 있어야 하는 프로세스는 보통 백그라운드로 실행합니다. 이 단계에서 함께 익혀야 할 것은 포트 매핑입니다. 컨테이너 안의 80 포트를 호스트의 8080 포트로 연결해야 브라우저나 `curl`로 접근할 수 있습니다.

### 4단계 — 상태 확인

```bash
docker ps              # running
docker logs web        # logs
docker stop web && docker rm web
```

컨테이너를 실행하는 것만큼 중요한 것이 관찰과 정리입니다. 어떤 컨테이너가 떠 있는지, 로그는 무엇인지, 다 쓴 컨테이너를 어떻게 내릴지를 일찍부터 익혀 두는 편이 좋습니다. 운영 습관은 이런 기본 명령에서 시작됩니다.

### 5단계 — 이미지 검색과 다운로드

```bash
docker pull redis:7-alpine
docker images
```

이미지는 보통 직접 만들기도 하지만, 공식 이미지를 가져와 출발점으로 쓰는 경우도 많습니다. 따라서 pull과 images는 이후 모든 실습의 기본 명령이 됩니다.

### 실행 뒤 바로 확인할 것

- `docker run hello-world` 뒤에는 Docker가 이미지를 내려받고 테스트 컨테이너를 실행했다는 성공 메시지가 보여야 합니다.
- `curl http://localhost:8080`은 nginx 기본 HTML을 반환해야 합니다. 빈 응답이나 연결 거부가 나오면 포트 매핑부터 다시 확인합니다.

### 잘 안 될 때 먼저 볼 것

- Docker Desktop이나 Docker daemon이 실제로 떠 있는지 먼저 확인합니다. 설치만 끝나고 엔진이 내려가 있는 경우가 흔합니다.
- `docker ps`에 컨테이너가 떠 있는데 접속이 안 되면 `-p 8080:80`처럼 호스트 포트와 컨테이너 포트를 뒤집지 않았는지 확인합니다.

## 이 코드에서 먼저 봐야 할 점

- image는 실행 직전의 정적 산출물이고, container는 실제로 동작하는 프로세스입니다.
- `-p 8080:80`은 호스트 포트와 컨테이너 포트를 연결합니다.
- `--rm`은 일회성 실행 뒤 흔적을 남기지 않도록 정리해 줍니다.

입문 단계에서 이 세 가지를 정확히 이해하면 뒤에서 나오는 Dockerfile, Compose, 운영 주제들이 훨씬 잘 이어집니다. 반대로 처음부터 Docker를 "가상머신 비슷한 것"으로 이해하면 파일시스템, 프로세스, 네트워크 개념이 모두 어긋나기 시작합니다.

## 자주 하는 실수 다섯 가지

1. **Docker를 가상머신처럼 생각합니다.** 컨테이너는 호스트 커널을 공유합니다.
2. **프로덕션에서 `latest` 태그를 그대로 씁니다.** 어느 날 조용히 다른 버전으로 바뀔 수 있습니다.
3. **컨테이너를 정리하지 않고 계속 쌓아 둡니다.** 디스크와 상태 확인이 금방 지저분해집니다.
4. **포트 매핑 없이 실행하고 접속이 안 된다고 판단합니다.** 서비스가 떠 있어도 외부에서는 보이지 않습니다.
5. **root 실행을 당연하게 여긴 채 운영까지 갑니다.** 초기에 방치한 습관이 나중에 보안 문제로 이어집니다.

이 다섯 가지는 전부 작은 오해에서 시작합니다. 하지만 컨테이너 수가 늘고 팀이 커질수록 이런 오해는 디버깅 비용, 보안 위험, 운영 혼선으로 바로 이어집니다. 처음부터 멘탈 모델을 바르게 잡는 이유가 여기에 있습니다.

## 실무에서는 이렇게 이어집니다

현업에서는 서비스 하나를 하나의 컨테이너로 패키징하고, 같은 이미지를 로컬 개발, CI, 스테이징, 운영 환경에 반복해서 사용합니다. 즉, Docker는 단순한 로컬 개발 도구라기보다 "배포 가능한 실행 단위"를 표준화하는 기반입니다.

그래서 많은 팀이 애플리케이션 코드를 검토할 때만큼이나 이미지 태그, 베이스 이미지, 실행 사용자, 포트, 헬스체크를 함께 검토합니다. Docker를 도입한다는 말은 개발 환경만 편해진다는 뜻이 아니라, 실행 방식 자체를 코드로 관리한다는 뜻에 가깝습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 환경은 문서가 아니라 코드와 이미지로 관리해야 합니다.
- 이미지는 불변 산출물이고, 컨테이너는 언제든 버릴 수 있어야 합니다.
- `latest`는 데모에는 편하지만 운영 기본값이 되어서는 안 됩니다.
- 컨테이너는 결국 하나의 프로세스라는 감각을 놓치면 안 됩니다.
- 호스트 커널을 공유한다는 사실이 성능과 보안의 출발점입니다.

이 관점은 앞으로 시리즈 전반을 읽는 기준이 됩니다. Dockerfile은 이미지를 만드는 방법을 다루고, volume은 상태를 어떻게 분리할지 다루며, production 주제는 이 불변성과 격리 모델을 어떻게 안전하게 운영할지로 이어집니다.

## 체크리스트

- [ ] `docker run hello-world`가 정상 동작합니다.
- [ ] image와 container의 차이를 설명할 수 있습니다.
- [ ] 포트 매핑의 의미를 이해했습니다.
- [ ] 실행한 컨테이너를 정리할 수 있습니다.

## 연습 문제

1. `nginx`를 실행하고 호스트 8080 포트로 접속해 보세요.
2. `python:3.12-slim`으로 대화형 셸을 열어 보세요.
3. 실행 중인 컨테이너의 로그와 상태를 각각 확인해 보세요.

## 정리 및 다음 단계

Docker는 환경 차이를 없애는 가장 빠른 출발점입니다. 이 글에서 가장 먼저 가져가야 할 핵심은 세 가지입니다. 첫째, Docker는 실행 환경을 이미지라는 산출물로 묶습니다. 둘째, 컨테이너는 그 이미지를 실제로 실행한 프로세스입니다. 셋째, 재현성이 생기면 디버깅과 배포가 모두 쉬워집니다.

다음 글에서는 image와 container를 더 깊게 분리해서 살펴보겠습니다. 어디까지가 불변이고, 어디서 상태가 생기며, 왜 컨테이너를 언제든 버릴 수 있게 설계해야 하는지를 본격적으로 다룹니다.


## 실전 설계 확장: Dockerfile, Compose, 멀티 스테이지

Docker를 팀 표준으로 쓰려면 단순 실행 명령을 넘어서 이미지 빌드 규칙과 서비스 조합 규칙을 함께 정의해야 합니다. 특히 Dockerfile 계층 설계, docker-compose.yml 환경 분리, 멀티 스테이지 빌드 전략은 개발 속도와 보안 품질을 동시에 좌우합니다. 같은 애플리케이션 코드라도 이 세 가지를 어떻게 설계하느냐에 따라 이미지 크기, 빌드 시간, 취약점 노출 범위가 크게 달라집니다.

### Dockerfile을 재현 가능한 빌드 문서로 다루기

좋은 Dockerfile은 "동작한다"보다 "같은 입력에서 같은 산출물이 나온다"를 목표로 합니다. 베이스 이미지 태그를 고정하고, 의존성 설치 순서를 안정적으로 분리하고, 런타임 사용자 권한을 낮춰야 합니다.

```dockerfile
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1     PYTHONUNBUFFERED=1

WORKDIR /app

RUN useradd -m appuser

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER appuser
CMD ["python", "main.py"]
```

위 구조에서 중요한 점은 의존성 설치 계층과 소스 복사 계층을 분리해 캐시 효율을 확보하는 것입니다. `requirements.txt`가 바뀌지 않으면 패키지 설치 레이어를 재사용할 수 있어 빌드 시간이 크게 줄어듭니다.

### docker-compose.yml은 서비스 경계를 코드로 남긴다

Compose는 "여러 컨테이너를 한 번에 띄운다"가 전부가 아닙니다. 각 서비스의 책임 경계, 네트워크 연결, 볼륨 지속성, 헬스체크 기준을 파일로 고정하는 역할이 더 큽니다.

```yaml
version: "3.9"
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - APP_ENV=local
      - DATABASE_URL=postgresql://app:app@db:5432/appdb
    depends_on:
      db:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 3s
      retries: 5

  db:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=app
      - POSTGRES_DB=appdb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app -d appdb"]
      interval: 5s
      timeout: 3s
      retries: 10

volumes:
  pgdata:
```

이 파일 하나로 새 팀원은 로컬 환경을 재현하고, CI는 같은 토폴로지를 사용해 통합 테스트를 수행할 수 있습니다. Compose를 문서 대신 코드로 다루는 이유가 여기에 있습니다.

### 멀티 스테이지 빌드로 런타임 이미지를 가볍게 유지하기

빌드 도구와 런타임이 섞이면 이미지가 불필요하게 커지고 공격 표면도 넓어집니다. 멀티 스테이지는 빌드에 필요한 것과 실행에 필요한 것을 분리해 이 문제를 해결합니다.

```dockerfile
FROM node:22-alpine AS build
WORKDIR /src
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS runtime
COPY --from=build /src/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

이 방식의 장점은 명확합니다.

- 최종 이미지는 정적 파일과 최소 런타임만 포함합니다.
- 빌드 도구 체인 취약점이 운영 이미지로 전파될 가능성을 줄입니다.
- 배포 전 전송량이 줄어 레지스트리 푸시/풀 시간이 단축됩니다.

### 운영 기준으로 보는 체크포인트

- 이미지 태그는 `latest` 대신 버전+커밋 해시를 사용합니다.
- 기본 사용자로 root를 피하고 최소 권한 사용자로 실행합니다.
- 헬스체크를 통해 readiness 판단을 자동화합니다.
- `.dockerignore`로 불필요한 파일 유입을 차단합니다.
- Secret은 이미지에 bake-in 하지 않고 런타임 주입으로 관리합니다.

### 빌드 파이프라인 예시

```bash
docker build -t ghcr.io/acme/app:1.4.2-3f2a9d1 .
docker run --rm ghcr.io/acme/app:1.4.2-3f2a9d1 python -m pytest -q
docker push ghcr.io/acme/app:1.4.2-3f2a9d1
```

위처럼 테스트 통과 이미지만 푸시하도록 규칙화하면 "코드는 통과했는데 이미지가 깨졌다" 같은 불일치를 줄일 수 있습니다. 컨테이너 운영의 핵심은 코드와 실행 단위를 같은 검증 루프로 묶는 데 있습니다.

### 장애 대응 관점에서 Compose와 Dockerfile을 함께 본다

운영 이슈가 발생하면 단일 파일만 봐서는 원인이 잘 드러나지 않습니다. 예를 들어 앱 컨테이너가 재시작 루프에 빠졌다면 Dockerfile의 엔트리포인트, Compose의 환경변수, 의존 서비스 헬스체크를 한 번에 확인해야 합니다. 따라서 리뷰 단계에서 "Dockerfile 단독 리뷰"가 아니라 "Dockerfile + Compose + 실행 로그"를 묶어 검토하는 습관이 필요합니다.

이 관점을 유지하면 컨테이너는 단순 포장 기술이 아니라 신뢰 가능한 배포 단위로 자리잡습니다.


## 처음 질문으로 돌아가기

- **Docker는 정확히 무엇을 해 주는 도구일까요?**
  - 본문의 기준은 Docker란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **컨테이너와 가상머신은 무엇이 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **image, container, registry는 어떤 관계로 이해해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Docker란 무엇인가? (현재 글)**
- Image와 Container (예정)
- Dockerfile 작성하기 (예정)
- Volume과 Network (예정)
- Docker Compose (예정)
- 환경변수와 설정 (예정)
- Python 앱 컨테이너화 (예정)
- 데이터베이스와 함께 실행하기 (예정)
- Image 최적화 (예정)
- 배포용 Docker 구성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Docker overview](https://docs.docker.com/get-started/overview/)
- [Get Docker](https://docs.docker.com/get-docker/)
- [Docker Hub](https://hub.docker.com/)
- [What is a container?](https://www.docker.com/resources/what-container/)

### 검증과 트러블슈팅

- [docker run reference](https://docs.docker.com/engine/reference/run/)

Tags: Docker, Container, DevOps, Linux, Virtualization
