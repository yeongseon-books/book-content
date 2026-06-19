---
series: docker-101
episode: 2
title: "Docker 101 (2/10): Image와 Container"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/254"
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
  - Image
  - Container
  - Layer
  - Lifecycle
seo_description: image와 container의 수명 주기와 layer 모델을 실습으로 정리합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (2/10): Image와 Container

컨테이너의 동작 방식을 모르면 디버깅이 운에 가까워집니다. 파일이 사라진 이유, 변경이 남지 않는 이유, 어떤 명령은 이미지에 작용하고 어떤 명령은 컨테이너에 작용하는 이유를 설명하지 못하면 운영 이슈를 재현하기가 어려워집니다.

이 글은 Docker 101 시리즈의 2번째 글입니다.

Docker를 조금만 써 보면 가장 먼저 헷갈리는 지점이 image와 container입니다. 이미지를 받았는데 왜 실행해야 하는지, 컨테이너 안에서 파일을 만들었는데 왜 다시 없어지는지, 삭제한 것은 이미지인지 컨테이너인지가 섞이기 시작합니다. 이 구분이 흐려지면 디버깅도 같이 흐려집니다.

실무에서 발생하는 많은 컨테이너 문제는 복잡한 기술보다 기본 오해에서 출발합니다. 컨테이너 내부에서 뭔가를 바꿔 놓고 "왜 재시작했더니 사라졌지?"라고 묻는 장면이 대표적입니다. 이미지는 불변이고, 컨테이너의 변경은 일시적이라는 감각을 잡아야 Docker를 제대로 다룰 수 있습니다.

![Docker 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/02/02-01-concept-at-a-glance.ko.png)
*Docker 101 2장 흐름 개요*

> Image와 Container 혼동은 대부분 한 가지 사실에서 풀립니다 — 이미지는 불변 snapshot이고, 컨테이너는 그 위에 만들어진 '쓰기 가능 레이어 + 실행 프로세스'입니다. 그래서 컨테이너 안 변경은 기본적으로 일시적이고, 재시작·재생성 시 사라지는 것이 정상입니다.

## 이 글에서 다룰 문제

- image와 container는 정확히 무엇이 다를까요?
- layer와 copy-on-write는 왜 중요한 개념일까요?
- 컨테이너의 수명 주기는 어떤 흐름으로 흘러갈까요?
- 이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?
- 초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?

## 핵심 개념

반대로 lifecycle과 layer 개념을 이해하면 문제의 대부분이 예측 가능해집니다. "이건 컨테이너 상태가 날아간 문제다", "이건 이미지가 다시 빌드되어야 하는 문제다"처럼 원인을 훨씬 빨리 분리할 수 있습니다.

- **Layer**: 이미지 내부를 구성하는 읽기 전용 파일시스템 조각입니다. Dockerfile의 각 명령이 하나의 레이어를 만듭니다.
- **Writable layer**: 컨테이너가 실행되면서 맨 위에 추가되는 쓰기 가능한 레이어입니다. 컨테이너가 사라지면 이 레이어도 함께 사라집니다.
- **Lifecycle**: `created → running → stopped → removed`로 이어지는 수명 주기입니다.
- **Tag**: `nginx:1.27`처럼 이미지를 식별하는 버전 라벨입니다. 같은 태그가 다른 이미지를 가리킬 수 있습니다.
- **Digest**: 이미지 내용을 고정하는 불변 SHA256 식별자입니다. 프로덕션 배포 추적에 더 신뢰할 수 있습니다.

여기서 특히 중요한 것은 writable layer입니다. 컨테이너 내부에서 여러분이 만드는 모든 변경은 보통 이 쓰기 레이어에 쌓입니다. 그래서 컨테이너를 지우면 그 변경도 함께 사라집니다.

### 레이어 모델 시각화

```
이미지 레이어 (읽기 전용)
┌──────────────────────────────┐
│  Layer 4: COPY app.py        │  ← 가장 최근 레이어
├──────────────────────────────┤
│  Layer 3: RUN pip install    │
├──────────────────────────────┤
│  Layer 2: COPY requirements  │
├──────────────────────────────┤
│  Layer 1: FROM python:3.12   │  ← 베이스 이미지
└──────────────────────────────┘
          ↓ 실행 시
┌──────────────────────────────┐
│  Writable Layer (컨테이너)    │  ← 변경사항이 여기에 쌓임
└──────────────────────────────┘
```

컨테이너가 삭제되면 writable layer만 사라지고, 이미지 레이어는 그대로 남습니다.

## 전과 후

**Before**: 컨테이너 안에서 `apt install`을 하고 재시작 뒤 변경이 사라져 당황합니다. 이미지와 컨테이너를 같은 개념으로 보기 때문에 생기는 오해입니다.

**After**: 변경은 Dockerfile에 코드로 남기고, 컨테이너는 언제든 버릴 수 있는 실행 단위로 다룹니다. 재현성과 추적 가능성이 생깁니다.

이 차이는 단순히 습관의 문제가 아닙니다. 재현 가능한 운영을 만들 수 있느냐의 문제입니다. 손으로 바꾼 컨테이너는 설명하기 어렵고, 다시 만들기도 어렵습니다.

## 실습: image와 container를 5단계로 구분해 보기

### 1단계 — 이미지 살펴보기

```bash
# 이미지 다운로드
docker pull nginx:1.27

# 레이어 구조 확인
docker image inspect nginx:1.27 | jq '.[0].RootFS.Layers'

# 빌드 히스토리 (각 레이어가 어떤 명령으로 생겼는지)
docker history nginx:1.27

# 이미지 크기 확인
docker images nginx:1.27
```

`docker history`는 이미지가 어떤 레이어로 쌓였는지 보여 줍니다. 처음에는 단순한 정보처럼 보이지만, 이미지 크기와 빌드 시간을 이해하는 데 아주 중요한 단서가 됩니다.

### 2단계 — 컨테이너 생성과 실행 (분리)

```bash
# 생성만 (실행 안 함)
docker create --name web nginx:1.27

# 상태 확인 — "Created" 상태
docker ps -a

# 실행
docker start web

# 이제 Running 상태
docker ps
```

이 단계는 create와 start가 분리될 수 있다는 점을 보여 줍니다. 즉, 이미지는 실행 준비물이고, 컨테이너는 실제 실행 상태라는 구분이 명령 수준에서도 드러납니다. 보통은 `docker run`이 두 단계를 합쳐서 실행합니다.

### 3단계 — 내부로 들어가 보기

```bash
# 실행 중인 컨테이너 안으로 진입
docker exec -it web bash
# bash가 없는 이미지는: docker exec -it web sh

# 컨테이너 내부에서
ls /etc/nginx
cat /etc/nginx/nginx.conf
whoami    # root인지 확인
exit
```

컨테이너 안으로 직접 들어가 보면 파일시스템이 진짜 서버처럼 보입니다. 많은 입문자가 여기서 착각합니다. 눈에 보인다고 해서 영구적이라는 뜻은 아닙니다.

### 4단계 — 변경은 일시적입니다

```bash
# 컨테이너 안에 파일 생성
docker exec web touch /tmp/hello
docker exec web ls /tmp/hello
# /tmp/hello 존재 확인

# 컨테이너 삭제
docker stop web && docker rm web

# 새 컨테이너 실행
docker run -d --name web2 nginx:1.27

# 이전 파일 없음
docker exec web2 ls /tmp/hello
# ls: cannot access '/tmp/hello': No such file or directory
```

이 단계가 핵심입니다. 컨테이너 내부에 만든 파일이 다음 컨테이너에서는 보이지 않는 이유는 변경이 이미지에 반영된 것이 아니라, 이전 컨테이너의 writable layer에만 있었기 때문입니다.

### 5단계 — 이미지와 컨테이너 정리

```bash
# 실행 중인 컨테이너 정리
docker stop web2 && docker rm web2

# 모든 중지된 컨테이너 정리
docker container prune -f

# dangling 이미지 제거 (태그 없는 이미지)
docker image prune -f

# 특정 이미지 삭제
docker image rm nginx:1.27

# 모두 정리 (이미지, 컨테이너, 볼륨, 네트워크)
docker system prune -af
```

정리 명령도 구분해서 이해해야 합니다. 컨테이너 정리와 이미지 정리는 다른 작업입니다. `docker system prune -af`는 모든 것을 지우므로 주의해서 사용합니다.

### 실행 뒤 바로 확인할 것

- `docker history nginx:1.27`는 레이어 목록을 보여 주어야 합니다.
- 4단계에서 `docker exec web2 ls /tmp/hello`가 "No such file or directory" 오류를 반환해야 합니다. 이 두 결과가 함께 나와야 image와 container 상태가 분리된다는 사실을 눈으로 확인한 셈입니다.

### 트러블슈팅

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| `docker exec -it web bash`가 실패 | 이미지에 bash 없음 | `docker exec -it web sh` 시도 |
| 이미지 삭제 실패 (`image is being used`) | 실행 중이거나 멈춘 컨테이너가 이미지를 사용 중 | `docker ps -a`로 확인 후 컨테이너 먼저 삭제 |
| `docker commit`으로 만든 이미지가 무거움 | 불필요한 파일, 레이어가 많음 | Dockerfile로 다시 빌드 |
| 컨테이너 내 변경이 사라짐 | writable layer의 정상 동작 | volume이나 bind mount 사용 |

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| 컨테이너 안에 파일을 영구 저장 | 재시작·재생성 시 사라짐 | volume이나 bind mount 사용 |
| `docker commit`으로 이미지 생성 | 재현하기 어렵고 레이어가 지저분해짐 | Dockerfile로 빌드 |
| 멈춘 컨테이너를 계속 쌓아 둠 | `docker ps -a`가 복잡해짐 | `docker container prune` 정기 실행 |
| `latest` 태그만 사용 | 어느 날 다른 이미지가 같은 태그를 가리킬 수 있음 | 고정 태그나 digest 사용 |
| 레이어가 지나치게 많은 이미지 | 빌드와 pull이 느려짐 | RUN 명령 합치기, 멀티스테이지 사용 |

## 컨테이너 수명 주기

```
         docker create
created ────────────────→ created
         docker start
created ────────────────→ running
         docker run (create + start 합산)
         docker pause
running ────────────────→ paused
         docker unpause
paused  ────────────────→ running
         docker stop
running ────────────────→ stopped (exited)
         docker start
stopped ────────────────→ running
         docker kill
running ────────────────→ stopped (즉시 종료)
         docker rm
stopped ────────────────→ (삭제됨)
```

`docker stop`은 SIGTERM을 보낸 뒤 10초 대기 후 SIGKILL합니다. `docker kill`은 즉시 SIGKILL입니다. 운영에서는 graceful shutdown을 위해 `docker stop`을 사용합니다.

## 실무에서는 이렇게 이어집니다

CI 파이프라인은 이미지 빌드 결과를 digest 기준으로 고정하고, 운영에서는 어떤 digest가 배포되었는지 로그와 메트릭 시스템과 연결해 추적합니다. 사고 분석에서도 "어떤 코드가 배포됐나"만큼이나 "어떤 이미지가 실제로 실행됐나"가 중요합니다.

결국 image와 container를 분리해서 보는 습관은 단순한 개념 학습이 아니라 변경 이력을 추적할 수 있는 운영 습관으로 이어집니다.

## 운영 체크리스트

- [ ] image와 container의 차이를 설명할 수 있습니다.
- [ ] 컨테이너 내부 변경이 휘발된다는 점을 이해했습니다.
- [ ] `docker history`로 레이어 구조를 볼 수 있습니다.
- [ ] layer와 digest가 왜 중요한지 설명할 수 있습니다.
- [ ] 멈춘 컨테이너를 `container prune`으로 정리할 수 있습니다.
- [ ] 컨테이너 수명 주기 (`created → running → stopped → removed`)를 설명할 수 있습니다.

## 연습 문제

1. `nginx:1.27`의 레이어 개수를 `docker history`로 확인해 보세요.
2. 컨테이너 안에 `echo hello > /tmp/test.txt`로 파일을 만든 뒤 컨테이너를 삭제하고 새로 실행해서 파일이 사라지는지 확인해 보세요.
3. `docker image prune`으로 사용하지 않는 이미지를 정리하고 `docker system df`로 용량 변화를 확인해 보세요.
4. `docker inspect <container>`에서 `State.Status`와 `NetworkSettings.IPAddress`를 찾아보세요.

## 처음 질문으로 돌아가기

- **image와 container는 정확히 무엇이 다를까요?**
  - image는 읽기 전용 레이어들의 집합으로, 실행 가능한 불변 패키지입니다. container는 그 이미지 위에 쓰기 가능한 레이어를 추가해 실제로 실행 중인 프로세스입니다. 같은 이미지에서 여러 컨테이너를 동시에 실행할 수 있지만, 각 컨테이너의 변경은 서로 독립적입니다.

- **layer와 copy-on-write는 왜 중요한 개념일까요?**
  - 레이어 공유 덕분에 같은 베이스 이미지를 쓰는 여러 이미지가 디스크 공간을 절약합니다. copy-on-write는 컨테이너가 이미지 레이어를 복사하지 않고, 변경이 발생할 때만 복사하는 방식으로 메모리와 공간을 아낍니다.

- **컨테이너의 수명 주기는 어떤 흐름으로 흘러갈까요?**
  - `created → running → stopped → removed` 순서입니다. `docker run`은 create와 start를 합친 명령이고, `docker stop`은 graceful shutdown(SIGTERM), `docker kill`은 즉시 종료(SIGKILL)입니다.

- **이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?**
  - `docker commit`으로 만든 이미지는 내부가 불투명해 보안 감사가 어렵습니다. 항상 Dockerfile로 빌드해야 하고, `docker exec`으로 운영 컨테이너를 직접 수정하는 것은 피해야 합니다. 수정이 필요하면 Dockerfile을 고치고 다시 빌드해야 합니다.

- **초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?**
  - 컨테이너 안에 저장한 파일이 재시작 후 사라지는 현상입니다. 이는 버그가 아니라 writable layer의 정상 동작입니다. 데이터를 유지하려면 volume을 사용해야 합니다.

## 정리

Docker의 기본기는 image와 container를 분리해서 이해하는 데서 시작합니다. image는 불변 산출물이고, container는 그 위에 잠깐 올라가는 실행 상태입니다. 이 관점을 놓치지 않으면 상태 손실, 재현성, 디버깅 문제 대부분을 훨씬 빨리 설명할 수 있습니다.

다음 글에서는 Dockerfile을 직접 작성하면서 이 불변 산출물을 어떻게 만드는지 봅니다. 결국 컨테이너 운영의 품질은 이미지를 얼마나 재현 가능하게 빌드하느냐에서 시작합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- **Docker 101 (2/10): Image와 Container (현재 글)**
- [Docker 101 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [Docker 101 (4/10): Volume과 Network](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- [Docker 101 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [Docker 101 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [Docker 101 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [Docker 101 (9/10): Image 최적화](./09-image-optimization.md)
- [배포용 Docker 구성](./10-production-docker.md)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Docker images](https://docs.docker.com/engine/reference/commandline/image/)
- [Docker container lifecycle](https://docs.docker.com/engine/reference/commandline/container/)
- [Storage drivers and layers](https://docs.docker.com/storage/storagedriver/)
- [Image digests](https://docs.docker.com/engine/reference/commandline/pull/#pull-an-image-by-digest-immutable-identifier)

### 검증과 트러블슈팅

- [docker exec reference](https://docs.docker.com/engine/reference/commandline/exec/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/docker-101/ko)

Tags: Docker, Image, Container, Layer, Lifecycle
