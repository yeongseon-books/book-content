---
series: containers-101
episode: 4
title: Dockerfile
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
- Containers
- Docker
- Dockerfile
- Build
- DevOps
seo_description: Dockerfile 작성 순서, 캐시 활용, 보안 기본값을 실전 감각으로 설명합니다
last_reviewed: '2026-05-15'
---

# Dockerfile

Dockerfile은 단순히 이미지가 빌드되도록 만드는 텍스트 파일이 아닙니다. 명령 순서 하나가 캐시 적중률을 바꾸고, 베이스 이미지 선택 하나가 취약점 수와 전송 크기를 바꾸며, 실행 사용자 설정 하나가 기본 보안 수준을 바꿉니다.

이 글은 Containers 101 시리즈의 네 번째 글입니다.

여기서는 캐시 친화적인 작성 순서, multi-stage build, 비root 실행, 비밀값 처리 같은 운영 기본값을 실제 Dockerfile 설계 관점에서 정리합니다.

## 이 글에서 다룰 문제

- Dockerfile의 명령 순서는 왜 그렇게 중요할까요?
- 캐시 친화적인 작성 방식은 빌드 시간을 어떻게 바꿀까요?
- multi-stage build는 어떤 문제를 해결할까요?
- 보안 기본값은 Dockerfile에서 어디서부터 잡아야 할까요?
- 초보 Dockerfile이 자주 만드는 실수는 무엇일까요?

> Dockerfile은 단순한 설정 파일이 아니라 이미지 품질을 결정하는 빌드 설계도입니다. 명령 순서, 캐시 전략, multi-stage, 비root 실행이 결과를 완전히 바꿉니다.

## 왜 중요한가

Dockerfile 하나가 팀의 생산성과 보안 수준을 동시에 좌우합니다. 한 번 제대로 작성해 두면 빌드 시간, 이미지 크기, 취약점 노출 면적, 온보딩 비용까지 장기간 영향을 받습니다.

같은 애플리케이션이라도 Dockerfile이 다르면 결과는 크게 달라집니다. 어떤 이미지는 900MB가 넘고 빌드도 느리지만, 어떤 이미지는 slim 베이스와 multi-stage 덕분에 100MB 아래로 작아지고 훨씬 빨리 빌드됩니다. 이 차이는 애플리케이션 코드보다 Dockerfile 구조에서 먼저 나옵니다.

## 한눈에 보는 개념

![빌더 스테이지와 런타임 스테이지 분리 흐름](../../../assets/containers-101/04/04-01-concept-at-a-glance.ko.png)

*빌더 스테이지와 런타임 스테이지 분리 흐름*
빌드용 스테이지와 실행용 스테이지를 분리하면, 최종 이미지는 필요한 결과물만 포함하고 불필요한 도구는 버릴 수 있습니다.

## 핵심 용어

- **FROM**: 베이스 이미지를 지정합니다.
- **WORKDIR**: 이후 명령이 실행될 작업 디렉터리를 정합니다.
- **COPY/ADD**: 파일을 이미지 안으로 복사합니다.
- **RUN**: 빌드 시점 명령을 실행합니다.
- **CMD/ENTRYPOINT**: 컨테이너 실행 시 기본 명령을 정의합니다.

이 명령들은 문법만 외우는 것으로 끝나지 않습니다. 어느 순서에 놓는지가 캐시 효율과 이미지 구조를 결정합니다.

## Before / After

**Before**: single-stage build 하나로 900MB짜리 이미지를 만듭니다.

**After**: multi-stage와 slim 베이스를 조합해 80MB 안팎으로 줄입니다.

결국 Dockerfile 최적화는 취향 문제가 아니라 빌드 시간과 배포 비용을 줄이는 구조적 개선입니다.

## 실습: Python 앱 Dockerfile 구성하기

### Step 1 — Base

```python
def base_stage():
    return [
        "FROM python:3.12-slim AS builder",
        "WORKDIR /app",
    ]
```

빌드 스테이지의 출발점을 정의합니다. 어떤 베이스 이미지를 고르느냐가 최종 이미지 크기와 취약점 표면에 직접 영향을 줍니다.

### Step 2 — Dependencies first

```python
def deps_stage():
    return [
        "COPY requirements.txt .",
        "RUN pip install --user -r requirements.txt",
    ]
```

의존성 파일을 코드보다 먼저 복사하는 이유는 캐시를 최대한 살리기 위해서입니다. 실제 현업에서 빌드 시간을 줄이는 가장 기본적인 패턴입니다.

### Step 3 — Code

```python
def code_stage():
    return [
        "COPY . .",
    ]
```

의존성 설치가 끝난 뒤에야 애플리케이션 코드를 복사합니다. 자주 바뀌는 레이어를 위로 올리는 전형적인 캐시 전략입니다.

### Step 4 — Runtime stage

```python
def runtime_stage():
    return [
        "FROM python:3.12-slim",
        "WORKDIR /app",
        "COPY --from=builder /root/.local /root/.local",
        "COPY --from=builder /app .",
        "ENV PATH=/root/.local/bin:$PATH",
    ]
```

최종 스테이지는 실행에 필요한 결과만 가져옵니다. 빌드 도구를 남기지 않는 것이 multi-stage의 핵심입니다.

### Step 5 — Non-root and run

```python
def finalize():
    return [
        "RUN useradd -m app && chown -R app:app /app",
        "USER app",
        "CMD [\"python\", \"main.py\"]",
    ]
```

마지막 단계에서 비root 사용자로 전환합니다. 보안은 나중에 덧붙이는 옵션이 아니라 Dockerfile 안에서 기본값으로 잡아야 합니다.

## 이 코드에서 먼저 봐야 할 점

- `requirements.txt`를 코드보다 먼저 복사해야 캐시가 살아납니다.
- `--from=builder`는 이전 스테이지의 결과만 가져옵니다.
- `USER app`은 root 실행을 피하게 해 줍니다.

이 세 가지를 이해하면 작은 Dockerfile에서도 성능, 크기, 보안을 함께 개선할 수 있습니다. 실무에서는 이 세 지점이 리뷰의 기본 체크포인트가 됩니다.

## 빠른 검증과 장애 신호

```bash
docker build -t demo-app:dev .
docker image inspect demo-app:dev --format "user={{.Config.User}} size={{.Size}}"
```

**Expected output:**
- 의존성 레이어가 소스 코드 레이어보다 먼저 배치됩니다.
- `Config.User`가 비어 있지 않으면 비root 기본값이 들어간 상태입니다.

**먼저 확인할 것:**
- 의존성이 매번 다시 깔리면 `COPY requirements.txt` 위치를 먼저 봅니다.
- root로 뜨면 `USER`가 최종 스테이지에 있는지 확인합니다.
- 이미지가 크면 빌드 도구가 최종 스테이지에 남았는지 점검합니다.

## 자주 하는 실수 5가지

1. **`COPY .`를 너무 먼저 써서 캐시를 죽입니다.**
2. **`apt update`를 따로 실행해 오래된 캐시를 남깁니다.**
3. **컨테이너를 root로 실행합니다.**
4. **비밀값을 `ENV`에 직접 넣습니다.**
5. **베이스 이미지를 `latest`로 둡니다.**

이 다섯 가지는 초반에는 사소해 보여도 운영에서는 반복 비용으로 돌아옵니다. 느린 빌드, 큰 이미지, 취약점 노출, 재현성 저하가 모두 여기서 시작됩니다.

## 운영에서는 이렇게 나타납니다

운영 환경에서는 multi-stage로 빌드 도구를 분리하고, `.dockerignore`로 build context를 줄이며, digest pin으로 재현성을 확보합니다. 컨테이너는 비root 사용자로 실행되고, 이미지 스캔은 CI 파이프라인의 일부가 됩니다.

즉, 좋은 Dockerfile은 개발 편의를 넘어서 운영 기본 정책을 담는 문서입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- Dockerfile도 애플리케이션 코드처럼 리뷰합니다.
- 캐시 친화적인 순서는 곧 팀 생산성이라고 봅니다.
- 비밀값은 ENV가 아니라 build arg나 BuildKit secret 같은 별도 경로로 다룹니다.
- 베이스 이미지는 작고 검증된 것을 선택합니다.
- 이미지 스캔은 선택이 아니라 CI 기본 단계로 봅니다.

시니어 엔지니어는 Dockerfile을 “빌드가 되면 끝”으로 보지 않습니다. 시간이 지나도 빠르고 안전하게 유지되는가를 기준으로 봅니다.

## 체크리스트

- [ ] multi-stage build를 사용합니다.
- [ ] `.dockerignore`를 작성했습니다.
- [ ] 비root 사용자로 실행합니다.
- [ ] 운영에서는 digest pin을 사용합니다.

## 연습 문제

1. 왜 `COPY requirements.txt`가 `COPY .`보다 먼저 와야 하는지 한 줄로 설명해 보세요.
2. multi-stage build의 대표 장점을 하나 적어 보세요.
3. Dockerfile에서 비밀값을 안전하게 다루는 방법 하나를 제안해 보세요.

## 정리와 다음 글

Dockerfile은 이미지 빌드 결과를 규정하는 핵심 설계 문서입니다. 명령 순서, 캐시 전략, multi-stage, 비root 실행이라는 네 가지 축을 잡으면 작은 앱도 훨씬 더 운영 친화적으로 만들 수 있습니다.

다음 글에서는 이미지가 아니라 상태를 어디에 둘 것인지, 즉 Volume 설계를 살펴보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [Container란 무엇인가?](./01-what-is-a-container.md)
- [Image와 Layer](./02-image-and-layer.md)
- [Runtime](./03-runtime.md)
- **Dockerfile (현재 글)**
- Volume (예정)
- Network (예정)
- Registry (예정)
- Container Security (예정)
- Containers vs VMs (예정)
- 실전 컨테이너 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Dockerfile 레퍼런스](https://docs.docker.com/engine/reference/builder/)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [Dockerfile 모범 사례](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [BuildKit secrets](https://docs.docker.com/build/building/secrets/)

Tags: Containers, Docker, Kubernetes, DevOps
