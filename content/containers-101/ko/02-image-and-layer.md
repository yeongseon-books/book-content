---
series: containers-101
episode: 2
title: "Containers 101 (2/10): Image와 Layer"
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
- Image
- Layer
- DevOps
seo_description: 이미지와 레이어 구조, 캐시, OverlayFS의 역할을 입문자 기준으로 설명합니다
last_reviewed: '2026-05-15'
---

# Containers 101 (2/10): Image와 Layer

이미지는 파일 하나처럼 보이지만, 레이어 순서 하나가 빌드 시간과 전송 비용, 취약점 표면까지 바꿉니다. 같은 앱인데도 어떤 팀은 캐시를 거의 못 쓰고, 어떤 팀은 바뀐 부분만 다시 만들어 빠르게 배포하는 이유가 여기서 갈립니다.

이 글은 Containers 101 시리즈의 두 번째 글입니다.

여기서는 이미지가 왜 레이어 스택으로 설계되는지, OverlayFS와 캐시, digest 기반 재현성이 왜 이 구조에서 나오는지 설명합니다.

## 먼저 던지는 질문

- 컨테이너 이미지는 왜 굳이 여러 레이어로 나뉠까요?
- 레이어 하나는 정확히 어떤 역할을 할까요?
- OverlayFS는 이 레이어들을 어떻게 겹쳐 보이게 만들까요?

## 큰 그림

![Containers 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/containers-101/02/02-01-concept-at-a-glance.ko.png)

*Containers 101 2장 흐름 개요*

이 그림에서는 Image와 Layer를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Image와 Layer의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

레이어를 이해하지 못하면 Dockerfile을 제대로 최적화할 수 없습니다. 같은 애플리케이션인데도 어떤 팀은 빌드에 30초가 걸리고, 어떤 팀은 5분이 걸리는 이유가 대부분 여기에 있습니다.

입문자에게 이미지는 하나의 파일처럼 보이기 쉽습니다. 하지만 실제 이미지는 읽기 전용 변경 묶음인 레이어들이 쌓인 구조입니다. 이 구조 덕분에 베이스 이미지를 재사용하고, 변경된 부분만 다시 빌드하고, 네트워크로는 달라진 부분만 전송할 수 있습니다.

## 한눈에 보는 개념

아래쪽은 운영 체제나 런타임 같은 공통 기반이고, 위쪽으로 갈수록 애플리케이션 고유 변경이 쌓입니다. 실행 시에는 여기에 쓰기 가능한 컨테이너 레이어가 하나 더 붙습니다.

## 핵심 용어

- **Layer**: 읽기 전용 변경 묶음입니다.
- **Base image**: 맨 아래에 놓이는 운영 체제 또는 런타임 기반 레이어입니다.
- **OverlayFS**: 여러 레이어를 하나의 파일시스템처럼 보이게 하는 방식입니다.
- **Manifest**: 이미지 구성 정보를 가리키는 메타데이터입니다.
- **Digest**: 이미지 내용을 식별하는 해시입니다.

여기서 digest와 tag를 구분하는 감각이 특히 중요합니다. tag는 사람이 붙인 이름이고, digest는 실제 내용의 동일성을 보장하는 식별자입니다.

## Before / After

**Before**: 소스 코드 한 줄만 바뀌어도 이미지 전체를 다시 빌드합니다.

**After**: 위쪽 레이어만 다시 빌드하므로 몇 초 안에 끝날 수 있습니다.

즉, 레이어는 단순한 저장 형식이 아니라 빌드 속도와 배포 효율을 좌우하는 핵심 메커니즘입니다.

## 실습: 이미지 내부 들여다보기

### Step 1 — Pull and inspect

```python
import subprocess, json

def inspect(image):
    res = subprocess.run(
        ["docker", "image", "inspect", image],
        capture_output=True, text=True, check=True,
    )
    return json.loads(res.stdout)
```

이미지 메타데이터를 읽어서 구조를 확인합니다. 실무에서는 문제를 감으로 추측하기보다 `inspect` 출력부터 보는 습관이 중요합니다.

### Step 2 — History

```python
def history(image):
    res = subprocess.run(
        ["docker", "history", "--no-trunc", image],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

각 레이어가 어떤 명령에서 만들어졌는지 추적합니다. Dockerfile 수정이 이미지 크기와 캐시에 어떤 영향을 주는지 읽을 수 있는 출발점입니다.

### Step 3 — Layer hashes

```python
def layer_sizes(image):
    data = inspect(image)
    return [layer for layer in data[0]["RootFS"]["Layers"]]
```

실제 레이어 해시 목록을 확인합니다. 이미지가 말 그대로 여러 레이어의 스택이라는 사실이 여기서 분명해집니다.

### Step 4 — Digest

```python
def digest(image):
    return inspect(image)[0]["Id"]
```

이미지의 내용 식별자를 확인합니다. 운영에서는 tag보다 digest를 기준으로 재현성을 확보하는 경우가 많습니다.

### Step 5 — Compare two builds

```python
def diff(a, b):
    return set(layer_sizes(a)) ^ set(layer_sizes(b))
```

두 빌드 사이에서 어떤 레이어가 달라졌는지 비교합니다. 캐시가 왜 깨졌는지 추적할 때 유용한 접근입니다.

## 이 코드에서 먼저 봐야 할 점

- `RootFS.Layers`에는 실제 레이어 해시가 들어 있습니다.
- `history`는 각 레이어를 만든 명령을 보여 줍니다.
- digest는 이미지 내용이 같은지를 보장합니다.

이 세 가지를 함께 보면 “왜 이번 빌드가 느렸는가”, “왜 이미지가 갑자기 커졌는가”, “왜 같은 tag인데 결과가 다르게 보이는가” 같은 질문에 훨씬 빨리 답할 수 있습니다.

## 빠른 검증과 장애 신호

```bash
docker pull python:3.12-slim
docker image inspect python:3.12-slim --format "{{json .RootFS.Layers}}"
docker history python:3.12-slim
docker inspect --format "{{index .RepoDigests 0}}" python:3.12-slim
```

**Expected output:**
- `RootFS.Layers`에 여러 레이어 해시가 배열로 출력됩니다.
- `docker history`에 각 레이어의 명령과 크기가 보입니다.
- push된 이미지라면 `RepoDigests`로 불변 식별자를 확인할 수 있습니다.

**먼저 확인할 것:**
- 레이어 수가 과하면 Dockerfile의 `RUN` 분리를 먼저 점검합니다.
- digest가 비어 있으면 아직 로컬 전용 이미지인지 확인합니다.
- 이미지가 크면 build context와 multi-stage 사용 여부를 봅니다.

## 자주 하는 실수 5가지

1. **RUN 명령을 지나치게 잘게 쪼개 레이어를 불필요하게 늘립니다.**
2. **`COPY .`로 필요 없는 파일까지 이미지에 넣습니다.**
3. **`apt update`와 `apt install`을 분리해 캐시를 어색하게 만듭니다.**
4. **빌드 산출물을 최종 이미지에 그대로 남겨 이미지가 커집니다.**
5. **`latest` 태그만 믿고 재현성을 잃습니다.**

이 실수들은 모두 레이어를 “보이지 않는 내부 구현”으로만 볼 때 나옵니다. 레이어는 운영 비용에 직접 연결되는 설계 요소입니다.

## 운영에서는 이렇게 나타납니다

실무에서는 multi-stage build로 빌드 도구와 런타임을 분리하고, `.dockerignore`로 build context를 줄이며, 배포 시에는 digest pin으로 재현성을 고정합니다. 즉, 레이어 이해가 곧 운영 품질로 이어집니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 자주 바뀌지 않는 명령과 자주 바뀌는 명령의 순서를 구분합니다.
- multi-stage build를 기본 패턴으로 봅니다.
- `latest`는 편의용 이름이지 운영 기준이 아니라고 봅니다.
- `.dockerignore`도 Dockerfile만큼 중요하게 다룹니다.
- 이미지 크기는 곧 공격 표면이라고 생각합니다.

시니어 엔지니어는 레이어를 단지 빌드 속도 관점에서만 보지 않습니다. 보안, 전송 비용, 캐시 효율, 재현성까지 한 번에 연결해서 봅니다.

## 체크리스트

- [ ] multi-stage build를 사용하고 있습니다.
- [ ] `.dockerignore`를 작성했습니다.
- [ ] 운영 환경에서는 digest pin을 사용합니다.
- [ ] 이미지 스캔을 활성화했습니다.

## 연습 문제

1. 레이어 캐시가 깨지는 가장 흔한 이유를 한 줄로 적어 보세요.
2. multi-stage build가 특히 유리한 상황을 하나 들어 보세요.
3. tag와 digest의 차이를 한 줄로 설명해 보세요.

## 정리와 다음 글

이미지는 여러 레이어가 쌓여 만들어지는 정적 아티팩트입니다. 이 구조를 이해하면 Dockerfile을 왜 특정 순서로 써야 하는지, 왜 캐시가 깨지는지, 왜 운영에서 digest를 중요하게 보는지가 자연스럽게 연결됩니다.

다음 글에서는 이렇게 준비된 이미지를 실제로 누가 어떻게 실행하는지, 즉 Runtime 계층을 살펴보겠습니다.

## 처음 질문으로 돌아가기

- **컨테이너 이미지는 왜 굳이 여러 레이어로 나뉠까요?**
  - 본문의 기준은 Image와 Layer를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **레이어 하나는 정확히 어떤 역할을 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **OverlayFS는 이 레이어들을 어떻게 겹쳐 보이게 만들까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Containers 101 (1/10): Container란 무엇인가?](./01-what-is-a-container.md)
- **Image와 Layer (현재 글)**
- Runtime (예정)
- Dockerfile (예정)
- Volume (예정)
- Network (예정)
- Registry (예정)
- Container Security (예정)
- Containers vs VMs (예정)
- 실전 컨테이너 앱 만들기 (예정)

<!-- toc:end -->

## 참고 자료

- [Docker — about storage drivers](https://docs.docker.com/storage/storagedriver/)
- [OverlayFS](https://docs.kernel.org/filesystems/overlayfs.html)
- [OCI Image Spec — manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)

Tags: Containers, Docker, Kubernetes, DevOps
