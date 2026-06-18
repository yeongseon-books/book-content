---
series: containers-101
episode: 4
title: "바이브코딩을 위한 컨테이너 기초 (4/10): Dockerfile"
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Containers
- Docker
- Dockerfile
- Build
language: ko
---

# 바이브코딩을 위한 컨테이너 기초 (4/10): Dockerfile

이 글은 **바이브코딩을 위한 컨테이너 기초** 시리즈의 네 번째 글입니다.

AI가 Dockerfile을 만들어 줍니다. 하지만 AI가 생성한 기본 Dockerfile은 동작은 하지만 운영에는 부족한 경우가 많습니다. 이미지가 900MB가 넘거나, 빌드할 때마다 의존성을 다시 설치하거나, root로 실행됩니다. Dockerfile을 직접 이해해야 AI가 만든 것을 검토하고 개선할 수 있습니다.

---

## 오늘의 핵심 질문

AI가 Dockerfile을 만들어 줬는데 빌드가 느리고 이미지가 900MB가 넘습니다. 어디서 문제가 생긴 걸까요? 그리고 어떻게 개선할 수 있을까요?

> "Dockerfile의 핵심은 명령 개수가 아니라 어느 명령까지 캐시할 수 있고, 어느 명령에서 캐시가 무효화되는지입니다."

---

## 이 글에서 다룰 문제

- Dockerfile의 명령 순서는 왜 그렇게 중요할까요?
- 캐시 친화적인 작성 방식은 빌드 시간을 어떻게 바꿀까요?
- multi-stage build는 어떤 문제를 해결할까요?
- AI가 생성한 Dockerfile의 전형적인 문제는 무엇일까요?
- 보안 기본값은 Dockerfile 어디에서 잡아야 할까요?

---

## 바이브코딩 관점에서 Dockerfile 최적화가 중요한 이유

AI에게 "Python FastAPI 앱 Dockerfile 만들어줘"라고 하면 동작하는 Dockerfile을 만들어 줍니다. 그런데 운영에 올리면 문제가 생깁니다:

1. **이미지가 너무 큼**: 개발 도구(gcc, make)가 최종 이미지에 남아 있습니다
2. **빌드가 느림**: 코드 한 줄 바꿀 때마다 `pip install`이 재실행됩니다
3. **보안 위험**: root로 실행됩니다
4. **재현성 없음**: 베이스 이미지를 `latest`로 씁니다

이 문제들은 Dockerfile 구조를 이해하면 모두 해결할 수 있습니다.

### AI가 자주 만드는 기본 Dockerfile과 그 문제

```dockerfile
# AI가 자주 생성하는 패턴 (문제 있음)
FROM python:3.12
COPY . /app
WORKDIR /app
RUN apt-get update && apt-get install -y gcc
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

문제점:
- 소스를 먼저 복사 → 코드 변경 시 의존성도 재설치
- gcc 등 빌드 도구가 최종 이미지에 남아 900MB 초과
- root로 실행

**개선된 multi-stage Dockerfile:**

```dockerfile
# Stage 1: 빌드
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt
COPY . .

# Stage 2: 실행
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --from=builder /build/app ./app
RUN useradd -m app && chown -R app:app /app
USER app
EXPOSE 8000
CMD ["python", "-m", "app.main"]
```

결과:
- 이미지 크기: 900MB → 80MB
- 빌드 시간: 코드 변경 시 캐시 활용
- 보안: non-root 실행

**핵심 Dockerfile 명령:**

- **FROM**: 베이스 이미지를 지정합니다.
- **WORKDIR**: 이후 명령이 실행될 작업 디렉터리를 정합니다.
- **COPY**: 파일을 이미지 안으로 복사합니다.
- **RUN**: 빌드 시점 명령을 실행합니다.
- **USER**: 실행 사용자를 변경합니다.
- **CMD/ENTRYPOINT**: 컨테이너 실행 시 기본 명령을 정의합니다.

---

## 적용 전후: AI 생성 Dockerfile 최적화

**Before**: AI가 생성한 단순 Dockerfile

```dockerfile
FROM python:3.12
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
# 이미지 크기: ~900MB, 매번 전체 재빌드
```

**After**: 캐시 최적화 + multi-stage

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt
COPY . .

FROM python:3.12-slim AS runtime
WORKDIR /app
COPY --from=builder /install /usr/local
COPY --from=builder /build/app /app
USER 1000:1000
CMD ["python", "main.py"]
# 이미지 크기: ~80MB, 코드 변경 시 캐시 활용
```

---

## 자주 하는 실수

| 실수 | 결과 | 해결 방법 |
|------|------|-----------|
| `COPY .`를 너무 먼저 배치 | 캐시 무효화로 의존성 재설치 | 의존성 파일 먼저 복사 |
| `apt update` 분리 실행 | 오래된 캐시로 설치 실패 | `update && install && 정리`를 한 RUN에 |
| root로 실행 | 보안 위험 | `USER` 명령으로 비root 전환 |
| 비밀값을 `ENV`에 직접 | `docker history`에 노출 | BuildKit secret 또는 런타임 주입 |
| 베이스 이미지 `latest` 사용 | 재현성 없는 빌드 | 버전 고정 (`python:3.12.3-slim`) |

---

## AI 팁: Dockerfile 보안 검토 요청

AI에게 Dockerfile 보안 검토를 요청하는 방법:

```
다음 Dockerfile을 검토해 주세요:
[Dockerfile 내용]

다음 항목을 점검하고 개선해 주세요:
1. root로 실행되는 부분
2. 비밀값이 이미지 레이어에 남는 부분
3. 불필요한 패키지가 최종 이미지에 포함된 부분
4. 캐시가 불필요하게 깨지는 레이어 순서
5. multi-stage build 적용 가능성
```

AI는 각 항목별로 문제를 찾아내고 구체적인 수정 코드를 제안합니다.

---

## 체크리스트

- [ ] AI가 생성한 Dockerfile에서 `COPY .`의 위치를 확인했습니다
- [ ] multi-stage build로 빌드 도구와 런타임을 분리했습니다
- [ ] `USER` 명령으로 non-root 실행을 설정했습니다
- [ ] `.dockerignore` 파일을 작성했습니다
- [ ] 베이스 이미지 버전을 고정했습니다

---

## 처음 질문으로 돌아가기

**AI가 만든 Dockerfile의 이미지가 900MB를 넘는 이유와 해결 방법은?**

AI가 만든 기본 Dockerfile은 빌드 도구(gcc, make, pip wheel 등)를 최종 이미지에 그대로 남깁니다. multi-stage build를 적용하면 빌드 단계에서만 도구를 사용하고 최종 이미지에는 실행에 필요한 결과물만 복사합니다. 900MB가 80MB로 줄어들 수 있습니다.

---

## 정리

Dockerfile은 이미지 빌드 결과를 규정하는 핵심 설계 문서입니다. 명령 순서, 캐시 전략, multi-stage build, non-root 실행이라는 네 가지 축을 잡으면 AI가 만든 앱도 훨씬 운영 친화적으로 만들 수 있습니다.

다음 글에서는 이미지가 아니라 상태를 어디에 둘 것인지, 즉 Volume 설계를 살펴봅니다.

---

## 참고 자료

- [Dockerfile 레퍼런스](https://docs.docker.com/engine/reference/builder/)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Dockerfile 모범 사례](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- Containers 101 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/containers-101/ko

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 컨테이너 기초 (1/10): Container란 무엇인가?
- 바이브코딩을 위한 컨테이너 기초 (2/10): Image와 Layer
- 바이브코딩을 위한 컨테이너 기초 (3/10): Runtime
- **바이브코딩을 위한 컨테이너 기초 (4/10): Dockerfile (현재 글)**
- 바이브코딩을 위한 컨테이너 기초 (5/10): Volume
- 바이브코딩을 위한 컨테이너 기초 (6/10): Network
- 바이브코딩을 위한 컨테이너 기초 (7/10): Registry
- 바이브코딩을 위한 컨테이너 기초 (8/10): Container Security
- 바이브코딩을 위한 컨테이너 기초 (9/10): Containers vs VMs
- 바이브코딩을 위한 컨테이너 기초 (10/10): 실전 컨테이너 앱 만들기

<!-- toc:end -->

Tags: 바이브코딩, Containers, Docker, Dockerfile, DevOps
