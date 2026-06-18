---
series: containers-101
episode: 2
title: "바이브코딩을 위한 컨테이너 기초 (2/10): Image와 Layer"
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Containers
- Docker
- Image
- Layer
language: ko
---

# 바이브코딩을 위한 컨테이너 기초 (2/10): Image와 Layer

이 글은 **바이브코딩을 위한 컨테이너 기초** 시리즈의 두 번째 글입니다.

AI가 앱 코드를 만들어 줬고, 이제 그 앱을 컨테이너 이미지로 만들어야 합니다. 이미지는 파일 하나처럼 보이지만, 레이어 순서 하나가 빌드 시간과 전송 비용을 크게 바꿉니다. 같은 앱인데도 어떤 팀은 매번 5분이 걸리고, 어떤 팀은 8초 만에 끝나는 이유가 여기에 있습니다.

---

## 오늘의 핵심 질문

AI가 Python 앱을 만들어 줬고 Dockerfile도 작성해 줬습니다. 그런데 코드 한 줄 수정할 때마다 `pip install`이 다시 실행됩니다. 빌드가 왜 이렇게 느릴까요? 레이어를 이해하면 이 문제가 해결됩니다.

> "레이어는 단순한 저장 형식이 아니라 빌드 캐시, 전송 효율, 보안 표면을 동시에 결정하는 설계 단위입니다."

---

## 이 글에서 다룰 문제

- 컨테이너 이미지는 왜 굳이 여러 레이어로 나뉠까요?
- 레이어 하나는 정확히 어떤 역할을 할까요?
- OverlayFS는 이 레이어들을 어떻게 겹쳐 보이게 만들까요?
- 바이브코딩으로 만든 앱의 빌드를 어떻게 빠르게 할 수 있을까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

---

## 바이브코딩 관점에서 이미지 레이어가 중요한 이유

AI가 Dockerfile을 만들어 줄 때 종종 이런 순서로 작성합니다:

```dockerfile
FROM python:3.12-slim
COPY . .                  # 모든 파일 복사
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
```

이 순서가 문제입니다. 코드 한 줄만 바꿔도 `pip install`이 다시 실행됩니다. 하루에 10번 수정하면 10번 다시 설치합니다.

**왜 그럴까요?** Docker는 각 명령을 레이어로 만들고 캐시합니다. `COPY . .`가 바뀌면 그 이후 레이어는 모두 다시 빌드됩니다. `pip install`이 `COPY . .` 다음에 오면, 코드가 바뀔 때마다 의존성도 다시 설치됩니다.

레이어 순서를 바꾸면 AI가 생성한 앱의 빌드 시간을 극적으로 줄일 수 있습니다.

### 이미지와 레이어 구조

이미지는 읽기 전용 레이어들이 쌓인 구조입니다. 아래쪽은 운영 체제나 런타임 같은 공통 기반이고, 위쪽으로 갈수록 애플리케이션 고유 변경이 쌓입니다.

```bash
docker pull python:3.12-slim
docker image inspect python:3.12-slim --format '{{json .RootFS.Layers}}' | python3 -m json.tool
```

출력을 보면 4~5개의 sha256 해시가 배열로 나옵니다. 각 해시가 하나의 레이어이고, 이미지는 "이 레이어들을 순서대로 쌓아라"라는 선언입니다.

**핵심 용어:**

- **Layer**: 읽기 전용 변경 묶음입니다.
- **Base image**: 맨 아래에 놓이는 운영 체제 또는 런타임 기반 레이어입니다.
- **OverlayFS**: 여러 레이어를 하나의 파일시스템처럼 보이게 하는 방식입니다.
- **Manifest**: 이미지 구성 정보를 가리키는 메타데이터입니다.
- **Digest**: 이미지 내용을 식별하는 해시입니다. tag와 달리 불변입니다.

---

## 적용 전후: AI가 만든 Dockerfile 최적화

**Before**: AI가 생성한 기본 Dockerfile (느린 빌드)

```dockerfile
FROM python:3.12-slim
COPY . .                  # 소스 먼저 복사 → 문제의 원인
RUN pip install -r requirements.txt
CMD ["python", "main.py"]

# 결과: 코드 1줄 변경 → pip install 재실행 (~4분)
```

**After**: 레이어 순서를 최적화한 Dockerfile (빠른 빌드)

```dockerfile
FROM python:3.12-slim
COPY requirements.txt .   # 의존성 파일 먼저
RUN pip install -r requirements.txt
COPY . .                  # 소스는 마지막
CMD ["python", "main.py"]

# 결과: 코드 1줄 변경 → COPY 레이어만 재실행 (~8초)
```

핵심은 **자주 바뀌는 것을 위로** 올리는 것입니다. `requirements.txt`는 거의 안 바뀌지만 소스 코드는 자주 바뀝니다. 자주 안 바뀌는 것을 아래에 두면 캐시가 살아남습니다.

---

## 자주 하는 실수

| 실수 | 결과 | 해결 방법 |
|------|------|-----------|
| `COPY .`를 의존성 설치 전에 배치 | 소스 변경 시 의존성 재설치 | 의존성 파일 먼저 COPY |
| `apt update`와 `apt install` 분리 | 오래된 캐시로 설치 실패 | 한 `RUN`에서 update+install+정리 |
| 빌드 도구를 최종 이미지에 남김 | 이미지 비대화, 취약점 증가 | multi-stage build 사용 |
| `.dockerignore` 없음 | 불필요 파일 전송 | `.git`, `node_modules` 등 제외 |
| `latest` 태그 의존 | 재현성 없는 빌드 | digest 또는 버전 고정 |

---

## AI 팁: Dockerfile 레이어 최적화 요청

AI가 생성한 Dockerfile이 느리다면 이렇게 요청하세요:

```
현재 Dockerfile:
[Dockerfile 내용 붙여넣기]

이 Dockerfile의 빌드 캐시가 자주 깨집니다.
의존성 설치 레이어가 소스 코드 변경에 영향받지 않도록
레이어 순서를 최적화해 주세요.
multi-stage build도 적용해 최종 이미지 크기를 줄여주세요.
```

AI는 레이어 순서를 재배치하고 multi-stage build를 적용해서 훨씬 빠른 Dockerfile을 만들어 줍니다.

---

## 체크리스트

- [ ] `docker history <이미지>` 명령으로 레이어 구조를 확인했습니다
- [ ] 의존성 파일(`requirements.txt`)이 소스 코드보다 먼저 복사됩니다
- [ ] `.dockerignore` 파일을 작성했습니다
- [ ] multi-stage build의 개념을 이해합니다
- [ ] tag와 digest의 차이를 설명할 수 있습니다

---

## 처음 질문으로 돌아가기

**AI가 만든 Dockerfile에서 코드 한 줄 수정할 때마다 `pip install`이 재실행되는 이유는?**

Docker는 각 명령을 레이어로 캐시합니다. `COPY . .`가 소스 변경을 감지하면 그 이후 레이어는 모두 무효화됩니다. `pip install`이 `COPY . .` 다음에 있으면 소스가 바뀔 때마다 의존성도 다시 설치됩니다. 의존성 파일을 먼저 복사하는 순서로 바꾸면 이 문제가 해결됩니다.

---

## 정리

이미지는 여러 레이어가 쌓여 만들어지는 정적 아티팩트입니다. 레이어 순서를 이해하면 Dockerfile을 왜 특정 순서로 써야 하는지, 왜 캐시가 깨지는지, 왜 multi-stage build가 필요한지가 자연스럽게 연결됩니다.

다음 글에서는 이렇게 준비된 이미지를 실제로 누가 어떻게 실행하는지, 즉 Runtime 계층을 살펴봅니다.

---

## 참고 자료

- [Docker — about storage drivers](https://docs.docker.com/storage/storagedriver/)
- [Multi-stage builds](https://docs.docker.com/build/building/multi-stage/)
- [OCI Image Spec — manifest](https://github.com/opencontainers/image-spec/blob/main/manifest.md)
- Containers 101 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/containers-101/ko

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 컨테이너 기초 (1/10): Container란 무엇인가?
- **바이브코딩을 위한 컨테이너 기초 (2/10): Image와 Layer (현재 글)**
- 바이브코딩을 위한 컨테이너 기초 (3/10): Runtime
- 바이브코딩을 위한 컨테이너 기초 (4/10): Dockerfile
- 바이브코딩을 위한 컨테이너 기초 (5/10): Volume
- 바이브코딩을 위한 컨테이너 기초 (6/10): Network
- 바이브코딩을 위한 컨테이너 기초 (7/10): Registry
- 바이브코딩을 위한 컨테이너 기초 (8/10): Container Security
- 바이브코딩을 위한 컨테이너 기초 (9/10): Containers vs VMs
- 바이브코딩을 위한 컨테이너 기초 (10/10): 실전 컨테이너 앱 만들기

<!-- toc:end -->

Tags: 바이브코딩, Containers, Docker, DevOps
