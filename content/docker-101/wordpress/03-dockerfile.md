---
title: "바이브코딩을 위한 Docker 기초 (3/10): Dockerfile 작성하기"
series: docker-101
episode: 3
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Docker
- AI코딩
- 컨테이너
seo_description: "바이브코딩 시대, AI가 만든 Dockerfile을 읽고 수정하려면 레이어 순서와 캐시 전략을 이해해야 합니다"
---

# 바이브코딩을 위한 Docker 기초 (3/10): Dockerfile 작성하기

이 글은 바이브코딩을 위한 Docker 기초 시리즈의 3번째 글입니다.

AI에게 "Dockerfile 만들어줘"라고 하면 금방 나옵니다. `FROM python:3.12-slim`으로 시작해서 `COPY`, `RUN`, `CMD`까지 그럴듯하게 채워 줍니다. 그런데 실제로 빌드해 보면 "왜 이렇게 오래 걸리지?" 또는 "코드 한 줄 바꿨는데 왜 패키지 설치를 처음부터 다시 하지?"라는 의문이 생깁니다. 반대로 AI가 생성해 준 Dockerfile이 보안 문제를 안고 있어도 알아채기가 어렵습니다.

AI가 만든 Dockerfile을 읽고 수정하려면 두 가지를 알면 충분합니다. 첫째, 각 명령의 역할. 둘째, 명령 순서가 빌드 속도에 영향을 주는 이유. 이 두 가지를 이해하면 "AI가 왜 이 순서로 작성했는지" 판단할 수 있고, 필요하면 수정도 할 수 있습니다.

Dockerfile의 핵심은 캐시입니다. Docker는 각 명령을 레이어로 만들고, 변경이 없는 레이어는 이전 빌드 결과를 재사용합니다. 그래서 자주 바뀌는 코드는 아래에, 잘 안 바뀌는 의존성은 위에 두는 것이 핵심입니다. AI가 항상 이 순서를 지켜 주진 않으므로, 직접 확인하는 것이 좋습니다.

> Dockerfile 빌드 속도의 차이는 명령 종류가 아니라 명령 순서에서 납니다. 자주 안 바뀌는 의존성을 먼저, 자주 바뀌는 소스를 나중에 두는 것만으로도 레이어 캐시가 살아납니다.

---

## 이 글에서 다룰 문제
- `FROM`, `RUN`, `COPY`, `CMD`는 각각 어떤 역할을 할까요?
- AI가 만든 Dockerfile에서 레이어 순서가 왜 중요할까요?
- `.dockerignore`는 왜 필요하고 AI가 빠뜨리면 어떤 일이 생길까요?
- non-root 실행 설정을 AI 결과물에 직접 추가하려면 어떻게 할까요?
- Dockerfile에서 비밀값이 노출되는 패턴은 무엇일까요?

## Dockerfile 핵심 명령 이해

Dockerfile은 이미지를 만드는 레시피입니다. 위에서 아래로 순서대로 실행되고, 각 명령이 하나의 레이어를 만듭니다.

- **FROM**: 베이스 이미지를 선택합니다. `python:3.12-slim`처럼 시작점이 됩니다.
- **RUN**: 빌드 시점에 명령을 실행합니다. 패키지 설치, 파일 생성 등에 사용합니다.
- **COPY**: 로컬 파일을 이미지 안으로 복사합니다.
- **CMD**: 컨테이너 시작 시 기본 실행 명령을 지정합니다.
- **ENTRYPOINT**: 항상 호출되는 고정 진입점입니다. CMD와 결합해 인자를 전달할 수 있습니다.

## Before / After

**Before**: AI가 만든 Dockerfile에 `COPY . .`가 맨 위에 있어서, 코드 한 줄 바뀔 때마다 의존성 설치(`pip install`)를 처음부터 다시 합니다. 빌드 한 번에 5분이 걸립니다.

**After**: requirements 파일을 먼저 복사하고 의존성을 설치한 뒤 소스를 복사하도록 순서를 바꾸면, 의존성이 변하지 않은 경우 캐시를 재사용해 빌드가 30초 안에 끝납니다.

```dockerfile
# Before (느림): 코드가 바뀔 때마다 pip install 재실행
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["python", "app.py"]

# After (빠름): 의존성 레이어와 코드 레이어를 분리
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `COPY .`를 requirements 설치 전에 둠 | 코드 수정마다 전체 의존성 재설치 | requirements 복사와 설치를 먼저, 코드 복사를 나중에 |
| `.dockerignore` 파일 없음 | `.git`, `.env` 등이 이미지에 포함될 수 있음 | `.dockerignore`에 `__pycache__`, `.env`, `.git` 추가 |
| `pip install` 뒤 캐시 정리 안 함 | 이미지가 불필요하게 커짐 | `--no-cache-dir` 옵션 추가 |
| root로 실행하는 기본값 방치 | 보안 취약점 노출 시 권한이 과도함 | `USER appuser` 추가 |
| 비밀값을 `ENV`에 직접 넣음 | 이미지 레이어에 영구적으로 박제됨 | 런타임 환경변수로 주입 |

## AI에게 Docker 관련 요청하는 팁

- "레이어 캐시를 최대화하도록 Dockerfile을 작성해줘"라고 명시적으로 요청하면 AI가 더 나은 순서로 작성합니다.
- "non-root 사용자로 실행하도록 USER 지시어를 추가해줘"라고 별도로 요청하는 것이 좋습니다. 기본적으로 AI가 빠뜨리는 경우가 많습니다.
- `.dockerignore`도 함께 만들어 달라고 하세요. "이 Dockerfile에 맞는 .dockerignore도 만들어줘"로 충분합니다.
- AI가 `ENV SECRET_KEY=abc123`처럼 비밀값을 Dockerfile에 넣어 주면 무조건 제거하고 런타임에 주입하도록 수정해야 합니다.

## 운영 체크리스트

- [ ] requirements 복사와 설치가 소스 코드 복사보다 위에 있습니다
- [ ] `.dockerignore`가 존재합니다
- [ ] 컨테이너가 non-root로 실행됩니다
- [ ] 비밀값이 Dockerfile에 하드코딩되어 있지 않습니다
- [ ] `docker history 이미지명`으로 레이어를 확인했습니다

## 처음 질문으로 돌아가기

AI가 만든 Dockerfile이 느리다면 `COPY . .`의 위치부터 확인하세요. requirements 파일 복사와 의존성 설치보다 소스 코드 복사가 먼저라면, 코드가 바뀔 때마다 의존성을 재설치합니다. 이 순서를 바꾸는 것만으로도 빌드 시간을 크게 줄일 수 있습니다.

## 정리

Dockerfile은 이미지를 만드는 레시피이면서 팀의 운영 문서입니다. AI가 만들어 준 Dockerfile을 그대로 쓰기보다, 레이어 순서가 캐시를 살리는지, `.dockerignore`가 있는지, 비밀값이 노출되어 있지 않은지를 한 번 확인하는 습관이 중요합니다. 다음 글에서는 데이터를 영구 저장하는 volume과 컨테이너 간 통신을 위한 network를 다룹니다.

## 참고 자료

### 공식 문서
- [Docker Documentation](https://docs.docker.com/)
- [Dockerfile reference](https://docs.docker.com/engine/reference/builder/)
- [Best practices for writing Dockerfiles](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)

### 관련 시리즈
- [Containers 101](../../containers-101/ko/)
- [Kubernetes 101](../../kubernetes-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 Docker 기초 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [바이브코딩을 위한 Docker 기초 (2/10): Image와 Container](./02-image-and-container.md)
- **바이브코딩을 위한 Docker 기초 (3/10): Dockerfile 작성하기 (현재 글)**
- [바이브코딩을 위한 Docker 기초 (4/10): Volume과 Network](./04-volume-and-network.md)
- [바이브코딩을 위한 Docker 기초 (5/10): Docker Compose](./05-docker-compose.md)
- [바이브코딩을 위한 Docker 기초 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [바이브코딩을 위한 Docker 기초 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [바이브코딩을 위한 Docker 기초 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [바이브코딩을 위한 Docker 기초 (9/10): Image 최적화](./09-image-optimization.md)
- [바이브코딩을 위한 Docker 기초 (10/10): 배포용 Docker 구성](./10-production-docker.md)
<!-- toc:end -->

Tags: 바이브코딩, Docker, AI코딩, 컨테이너
