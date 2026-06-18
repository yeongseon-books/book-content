---
title: "바이브코딩을 위한 Docker 기초 (9/10): Image 최적화"
series: docker-101
episode: 9
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Docker
- AI코딩
- 컨테이너
seo_description: "바이브코딩 시대, AI가 만든 Dockerfile을 멀티스테이지와 BuildKit으로 개선해 이미지 크기와 빌드 시간을 줄이는 방법을 설명합니다"
---

# 바이브코딩을 위한 Docker 기초 (9/10): Image 최적화

이 글은 바이브코딩을 위한 Docker 기초 시리즈의 9번째 글입니다.

AI에게 Dockerfile을 생성해 달라고 하면 동작하는 결과물이 나옵니다. 그런데 빌드하면 이미지 크기가 1GB를 넘거나, 코드 한 줄 바꿀 때마다 5분씩 빌드를 기다려야 합니다. CI에서는 매번 모든 의존성을 다시 다운로드합니다. 처음엔 "어쩔 수 없나 보다"고 넘어가지만, 하루에 수십 번 빌드하다 보면 이 시간이 쌓입니다.

이미지 최적화는 어렵지 않습니다. 핵심은 두 가지입니다. 첫째, 멀티스테이지 빌드로 빌드 도구와 런타임 환경을 분리합니다. 둘째, 레이어 캐시를 잘 활용합니다. AI가 만든 기본 Dockerfile에 이 두 가지를 추가하면 이미지 크기와 빌드 시간을 크게 줄일 수 있습니다.

이미지 크기는 미적 취향이 아닙니다. 배포 시간, CI 속도, 보안 표면에 직접 영향을 줍니다. AI가 만들어 준 Dockerfile에 멀티스테이지를 적용하는 방법을 알면, 바이브코딩의 빠른 개발 사이클을 유지하면서도 운영에 적합한 이미지를 만들 수 있습니다.

> 이미지 크기는 미적 취향이 아니라 운영 지표입니다. 배포 시간, CI 속도, 보안 표면이 모두 함께 움직이기 때문에, 베이스 이미지 선택, 멀티스테이지 빌드, 캐시 전략은 같은 목표의 세 축입니다.

---

## 이 글에서 다룰 문제
- AI가 만든 Dockerfile의 이미지가 왜 이렇게 클까요?
- 멀티스테이지 빌드는 어떻게 이미지를 줄일까요?
- BuildKit cache mount를 추가하면 얼마나 빨라질까요?
- `slim`, `alpine`, `distroless` 중 무엇을 선택해야 할까요?
- AI 결과물을 멀티스테이지로 개선하는 최소한의 변경은 무엇일까요?

## 최적화 세 가지 핵심

- **멀티스테이지 빌드**: 빌드에 필요한 도구(`gcc`, `pip wheel` 등)는 builder 스테이지에만 두고, 최종 이미지(runtime 스테이지)에는 실행 결과물만 복사합니다. 컴파일러와 빌드 도구가 최종 이미지에 남지 않습니다.
- **레이어 캐시**: 자주 바뀌지 않는 것(의존성)을 위에, 자주 바뀌는 것(소스 코드)을 아래에 두면 재빌드 시 의존성 레이어를 재사용합니다.
- **BuildKit cache mount**: `--mount=type=cache`를 사용하면 `pip` 캐시를 빌드 간에 공유해 의존성 다운로드 시간을 줄입니다.

## Before / After

**Before**: AI가 만든 단일 스테이지 Dockerfile. 빌드 도구가 최종 이미지에 남아 크기가 1.2GB. 코드 수정 시 pip install이 매번 재실행.

**After**: 멀티스테이지 + BuildKit cache mount 적용. 최종 이미지 80MB. 캐시 적중 시 빌드 5초.

```dockerfile
# 멀티스테이지 Dockerfile (AI 결과물을 이렇게 개선)
# syntax=docker/dockerfile:1.7

# 빌드 스테이지: wheel 생성 (빌드 도구 포함)
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip wheel --wheel-dir /wheels -r requirements.txt

# 런타임 스테이지: 실행 결과물만 복사 (빌드 도구 제외)
FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /wheels /wheels
RUN pip install --no-index --find-links=/wheels /wheels/*.whl && rm -rf /wheels
COPY . .
RUN useradd -m -u 1000 appuser
USER appuser
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 단일 스테이지에 빌드 도구 그대로 | 이미지에 컴파일러 등 불필요한 도구 포함 | 멀티스테이지로 builder/runtime 분리 |
| alpine을 무조건 선택 | C 확장 사용 패키지(numpy 등)에서 musl 호환 오류 발생 | 먼저 `slim`으로 시작, 문제없으면 alpine 시도 |
| `apt-get install` 후 캐시 정리 없음 | 이미지가 수십 MB씩 불필요하게 커짐 | `&& rm -rf /var/lib/apt/lists/*` 같은 줄에 추가 |
| `.dockerignore` 없이 `COPY . .` | node_modules, .git 등 거대한 디렉터리가 컨텍스트에 포함 | `.dockerignore`에 불필요한 디렉터리 추가 |
| 빌드 도구를 런타임에 남김 | 공격 표면 증가, 이미지 크기 낭비 | 멀티스테이지로 runtime 스테이지에는 복사 안 함 |

## AI에게 Docker 관련 요청하는 팁

- "멀티스테이지 빌드를 사용해서 최종 이미지에는 빌드 도구가 남지 않도록 Dockerfile을 개선해줘"라고 요청하세요.
- "BuildKit cache mount를 사용해 pip 캐시를 재사용하도록 해줘"라고 함께 요청하면 빌드 시간도 줄어듭니다.
- "현재 이미지 크기가 1GB인데 최대한 줄여줘"라고 요청하면 AI가 멀티스테이지와 베이스 이미지 선택을 함께 개선해 줍니다.
- `docker images 이미지명`으로 최적화 전후 크기를 직접 비교하세요.

## 운영 체크리스트

- [ ] 멀티스테이지로 build와 runtime 스테이지가 분리되어 있습니다
- [ ] 최종 이미지에 빌드 도구가 남아 있지 않습니다
- [ ] `.dockerignore`로 빌드 컨텍스트를 줄였습니다
- [ ] 이미지 크기가 이전보다 크게 줄었습니다
- [ ] 코드만 바꿀 때 의존성 레이어가 캐시에서 재사용되는지 확인했습니다

## 처음 질문으로 돌아가기

AI가 만든 Dockerfile 이미지가 너무 크다면, 멀티스테이지를 추가하는 것이 가장 빠른 해결책입니다. `FROM ... AS builder`로 빌드 스테이지를 나누고, `FROM ... AS runtime`에서 `COPY --from=builder`로 결과물만 가져오는 패턴을 AI에게 다시 요청하면 됩니다. 빌드가 느리다면 `--mount=type=cache`를 추가하도록 요청하세요.

## 정리

이미지 최적화는 어렵지 않습니다. AI가 만든 Dockerfile에 멀티스테이지를 추가하고, 레이어 순서를 캐시에 유리하게 조정하면 대부분의 경우 이미지 크기와 빌드 시간을 크게 줄일 수 있습니다. 다음 글에서는 시리즈 마지막으로 실제 운영 배포 시 고려해야 할 설정을 정리합니다.

## 참고 자료

### 공식 문서
- [Docker Documentation](https://docs.docker.com/)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [BuildKit cache mounts](https://docs.docker.com/build/cache/optimize/)

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
- [바이브코딩을 위한 Docker 기초 (5/10): Docker Compose](./05-docker-compose.md)
- [바이브코딩을 위한 Docker 기초 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [바이브코딩을 위한 Docker 기초 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [바이브코딩을 위한 Docker 기초 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- **바이브코딩을 위한 Docker 기초 (9/10): Image 최적화 (현재 글)**
- [바이브코딩을 위한 Docker 기초 (10/10): 배포용 Docker 구성](./10-production-docker.md)
<!-- toc:end -->

Tags: 바이브코딩, Docker, AI코딩, 컨테이너
