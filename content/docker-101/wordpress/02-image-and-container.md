---
title: "바이브코딩을 위한 Docker 기초 (2/10): Image와 Container"
series: docker-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Docker
- AI코딩
- 컨테이너
seo_description: "바이브코딩 시대, AI가 만든 Docker 명령에서 image와 container 오류를 읽으려면 레이어 모델부터 이해해야 합니다"
---

# 바이브코딩을 위한 Docker 기초 (2/10): Image와 Container

이 글은 바이브코딩을 위한 Docker 기초 시리즈의 2번째 글입니다.

AI에게 "Dockerfile 만들어줘"라고 부탁하면 그럴듯한 파일이 나옵니다. `docker build -t myapp .`으로 빌드도 됩니다. 그런데 컨테이너 안에서 파일을 수정했더니 다음 날 다시 실행했을 때 바뀐 내용이 없어졌습니다. 또는 `docker rm mycontainer`를 했는데 이미지까지 지워진 줄 알고 당황했을 수도 있습니다.

이 혼동은 대부분 한 가지 오해에서 시작합니다. image와 container를 같은 것으로 보거나, 적어도 명확히 구분하지 않는 것입니다. AI가 만든 Docker 명령에서 오류 메시지를 읽으려면, 그 명령이 이미지에 작용하는지 컨테이너에 작용하는지를 구분할 수 있어야 합니다. 그렇지 않으면 오류 메시지를 봐도 무엇을 수정해야 할지 알 수 없습니다.

Image는 불변 스냅샷입니다. 한 번 만들어진 이미지는 바뀌지 않습니다. Container는 그 이미지를 실행한 인스턴스로, 위에 쓰기 가능한 레이어를 하나 더 올려서 동작합니다. 컨테이너를 삭제하면 그 쓰기 레이어도 함께 사라집니다. 그래서 컨테이너 안에서 무언가를 수정해도 재시작하면 원래 이미지 상태로 돌아갑니다.

> Image와 Container 혼동은 대부분 한 가지 사실에서 풀립니다. 이미지는 불변 snapshot이고, 컨테이너는 그 위에 만들어진 쓰기 가능 레이어와 실행 프로세스의 조합입니다. 그래서 컨테이너 안 변경은 기본적으로 일시적이고, 재시작 시 사라지는 것이 정상입니다.

---

## 이 글에서 다룰 문제
- image와 container는 정확히 무엇이 다를까요?
- 컨테이너를 삭제하면 이미지도 지워질까요?
- 컨테이너 안에서 파일을 바꿨는데 왜 재시작 후 사라질까요?
- AI가 만든 `docker rm`과 `docker rmi`는 각각 무엇을 지울까요?
- layer와 digest는 언제 중요해질까요?

## Image와 Container의 구조

컨테이너의 동작 방식을 이해하지 못하면 디버깅이 운에 가까워집니다. 파일이 사라진 이유, 변경이 남지 않는 이유를 설명하지 못하면 운영 이슈를 재현하기가 어려워집니다.

핵심 개념 정리:

- **Layer**: 이미지 내부를 구성하는 읽기 전용 파일시스템 조각입니다. Dockerfile의 각 명령이 레이어를 만듭니다.
- **Writable layer**: 컨테이너가 실행되면서 맨 위에 추가되는 쓰기 가능한 레이어입니다.
- **Lifecycle**: created → running → stopped → removed로 이어지는 수명 주기입니다.
- **Tag**: `nginx:1.27`처럼 이미지를 식별하는 버전 라벨입니다.
- **Digest**: 이미지 내용을 고정하는 불변 SHA256 식별자입니다.

## Before / After

**Before**: 컨테이너 안에서 `apt install`을 하고 재시작 뒤 변경이 사라져 당황합니다. `docker rm`과 `docker rmi`를 혼동해 필요한 이미지를 지웁니다.

**After**: 변경은 Dockerfile에 코드로 남기고, 컨테이너는 언제든 버릴 수 있는 실행 단위로 다룹니다. `rm`은 컨테이너, `rmi`는 이미지라는 구분이 명확해집니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 컨테이너 안에서 파일을 직접 수정 | 재시작 시 변경이 사라짐 | 변경 사항은 Dockerfile에 반영 |
| `docker rm`으로 이미지까지 지워진 줄 앎 | `docker rm`은 컨테이너만 제거, 이미지는 `docker rmi` | 명령 구분 숙지 |
| `docker commit`으로 이미지를 관리하려 함 | 재현하기 어려운 산출물이 됨 | Dockerfile로 이미지 빌드 |
| `latest`만 믿고 어떤 코드인지 모름 | 언제든 다른 이미지를 가리킬 수 있음 | 명시적 버전 태그 또는 digest 사용 |
| 멈춘 컨테이너를 방치 | `docker ps -a`가 금방 관리하기 어려워짐 | `docker rm` 또는 `--rm` 옵션 |

## AI에게 Docker 관련 요청하는 팁

- AI에게 "컨테이너 안에서 패키지를 설치하게 해줘"라고 하지 말고, "Dockerfile에서 패키지를 설치하도록 RUN 명령 추가해줘"라고 요청하세요.
- AI가 `docker exec -it 컨테이너명 bash`를 제안하면, 이것은 실행 중인 컨테이너 안으로 들어가는 것이지 이미지를 바꾸는 것이 아님을 기억하세요.
- `docker ps`는 실행 중인 컨테이너만, `docker ps -a`는 멈춘 컨테이너까지 보여줍니다. AI가 컨테이너를 찾지 못한다면 어느 명령을 써야 하는지 확인하세요.

## 운영 체크리스트

- [ ] image와 container의 차이를 설명할 수 있습니다
- [ ] 컨테이너 내부 변경이 재시작 시 사라진다는 점을 이해했습니다
- [ ] `docker rm`과 `docker rmi`의 차이를 압니다
- [ ] 멈춘 컨테이너를 `docker ps -a`로 확인할 수 있습니다
- [ ] layer와 writable layer의 개념을 이해했습니다

## 처음 질문으로 돌아가기

컨테이너 안에서 수정한 내용이 사라진 이유는 간단합니다. 컨테이너는 이미지 위에 임시 쓰기 레이어를 올려 동작하기 때문입니다. 컨테이너가 사라지면 그 쓰기 레이어도 함께 사라집니다. AI에게 "이 변경을 영구적으로 만들어달라"고 할 때는 "Dockerfile에 반영해줘"라고 해야 이미지 레이어에 남게 됩니다.

## 정리

이미지는 불변 산출물이고, 컨테이너는 그 위에 잠깐 올라가는 실행 상태입니다. AI가 만든 Docker 명령에서 오류가 났을 때 이 구분을 기억하면, 이미지 문제인지 컨테이너 상태 문제인지를 훨씬 빨리 구분할 수 있습니다. 다음 글에서는 Dockerfile을 직접 작성하는 방법을 봅니다.

## 참고 자료

### 공식 문서
- [Docker Documentation](https://docs.docker.com/)
- [Storage drivers and layers](https://docs.docker.com/storage/storagedriver/)

### 관련 시리즈
- [Containers 101](../../containers-101/ko/)
- [Kubernetes 101](../../kubernetes-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 Docker 기초 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- **바이브코딩을 위한 Docker 기초 (2/10): Image와 Container (현재 글)**
- [바이브코딩을 위한 Docker 기초 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [바이브코딩을 위한 Docker 기초 (4/10): Volume과 Network](./04-volume-and-network.md)
- [바이브코딩을 위한 Docker 기초 (5/10): Docker Compose](./05-docker-compose.md)
- [바이브코딩을 위한 Docker 기초 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [바이브코딩을 위한 Docker 기초 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [바이브코딩을 위한 Docker 기초 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [바이브코딩을 위한 Docker 기초 (9/10): Image 최적화](./09-image-optimization.md)
- [바이브코딩을 위한 Docker 기초 (10/10): 배포용 Docker 구성](./10-production-docker.md)
<!-- toc:end -->

Tags: 바이브코딩, Docker, AI코딩, 컨테이너
