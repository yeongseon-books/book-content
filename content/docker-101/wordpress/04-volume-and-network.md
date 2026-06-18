---
title: "바이브코딩을 위한 Docker 기초 (4/10): Volume과 Network"
series: docker-101
episode: 4
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Docker
- AI코딩
- 컨테이너
seo_description: "바이브코딩 시대, AI가 만든 docker-compose에서 volume과 network 설정을 읽고 수정하는 방법을 설명합니다"
---

# 바이브코딩을 위한 Docker 기초 (4/10): Volume과 Network

이 글은 바이브코딩을 위한 Docker 기초 시리즈의 4번째 글입니다.

AI에게 "웹 앱과 데이터베이스를 Docker로 실행하게 해줘"라고 요청하면, `docker run` 명령 두 개 또는 `docker-compose.yml` 파일이 나옵니다. 처음 실행할 때는 잘 됩니다. 그런데 다음 날 다시 실행하면 데이터베이스가 비어 있습니다. 또는 앱 컨테이너에서 DB 컨테이너에 접속하려고 `localhost`를 쓰면 연결이 실패합니다.

이 두 가지 문제가 volume과 network를 이해해야 하는 이유입니다. AI가 만들어 준 설정에 volume이 빠져 있으면 재시작 시 데이터가 사라집니다. 네트워크 설정이 없거나 `localhost`로 컨테이너 간 통신을 시도하면 연결이 안 됩니다. 이 설정들은 AI가 빠뜨리거나 잘못 생성하는 경우가 있어서, 결과물을 읽을 수 있어야 합니다.

Volume은 컨테이너 수명과 독립적으로 데이터를 보존하는 방법입니다. Network는 컨테이너끼리 이름으로 서로를 찾을 수 있게 해 줍니다. 이 두 가지가 있어야 재시작해도 데이터가 남고, 컨테이너들이 서로 통신할 수 있습니다.

> Volume과 Network는 부가 옵션이 아니라 컨테이너 운영의 두 기본 축입니다. Volume은 상태의 수명을 컨테이너 수명에서 분리하고, Network는 컨테이너가 서로를 이름으로 찾을 수 있게 해 줍니다.

---

## 이 글에서 다룰 문제
- 컨테이너를 재시작했는데 왜 데이터가 사라질까요?
- volume, bind mount는 각각 언제 써야 할까요?
- 앱 컨테이너에서 DB 컨테이너에 접속할 때 왜 `localhost`가 안 될까요?
- AI가 만든 네트워크 설정에서 무엇을 확인해야 할까요?
- volume 백업은 어떻게 할까요?

## Volume과 Network 개념 정리

- **Volume**: Docker가 관리하는 영구 저장소입니다. 컨테이너를 삭제해도 데이터가 남습니다.
- **Bind mount**: 호스트의 특정 폴더를 컨테이너에 연결합니다. 개발 중 소스코드 실시간 반영에 유용합니다.
- **Bridge network**: 같은 호스트 안에서 컨테이너들을 연결하는 기본 가상 네트워크입니다.
- **Service discovery**: 같은 네트워크 안의 컨테이너는 이름으로 서로를 찾을 수 있습니다. `db`라는 컨테이너 이름이 곧 접속 주소가 됩니다.

## Before / After

**Before**: AI가 만든 설정에 volume이 없어 DB 컨테이너를 재시작할 때마다 데이터가 사라집니다. 앱 컨테이너에서 `DB_HOST=localhost`로 설정했더니 연결이 안 됩니다.

**After**: named volume으로 DB 데이터를 영구 보존하고, `DB_HOST=db`처럼 컨테이너 이름을 호스트 주소로 사용해 통신합니다.

```yaml
# volume과 network를 명시한 docker-compose.yml 예시
services:
  web:
    image: myapp
    environment:
      DB_HOST: db    # localhost가 아니라 컨테이너 이름
    networks:
      - app-net

  db:
    image: postgres:16
    volumes:
      - pgdata:/var/lib/postgresql/data    # named volume으로 영구 보존
    networks:
      - app-net

volumes:
  pgdata:    # 컨테이너 삭제 후에도 데이터 유지

networks:
  app-net:    # 이 네트워크 안에서 이름으로 통신 가능
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| DB 컨테이너에 volume 없이 실행 | 재시작 또는 `docker-compose down` 시 데이터 삭제 | named volume 선언 및 마운트 |
| 앱에서 `DB_HOST=localhost` 사용 | 각 컨테이너는 독립된 네트워크 네임스페이스를 가짐 | `DB_HOST=db`처럼 컨테이너 이름 사용 |
| `docker-compose down -v` 실행 | `-v` 옵션은 volume까지 삭제함 | 데이터 삭제가 의도된 경우에만 사용 |
| bind mount 권한 오류 | 호스트 파일 소유자와 컨테이너 사용자 ID 불일치 | UID 맞추거나 volume으로 전환 |
| `--network host` 남용 | 보안 격리가 깨지고 포트 충돌 가능성 증가 | user-defined bridge 사용 |

## AI에게 Docker 관련 요청하는 팁

- "DB 데이터가 컨테이너 재시작 후에도 유지되게 해줘"라고 명시적으로 요청해야 AI가 volume을 추가합니다.
- "앱과 DB가 서로 통신할 수 있도록 네트워크 설정을 포함해줘"라고 하면 AI가 같은 네트워크에 배치해 줍니다.
- AI가 `DB_HOST=localhost`로 설정해 줬다면, 컨테이너 이름으로 바꿔야 합니다. `docker-compose.yml`에서 DB 서비스 이름을 찾아 그 이름을 호스트로 사용하세요.
- volume 백업 방법도 AI에게 "이 volume을 백업하는 명령을 알려줘"라고 요청할 수 있습니다.

## 운영 체크리스트

- [ ] DB 데이터가 named volume에 저장됩니다
- [ ] 앱이 `localhost`가 아닌 컨테이너 이름으로 DB에 접속합니다
- [ ] 컨테이너들이 같은 user-defined network에 있습니다
- [ ] `docker-compose down -v`의 의미를 이해하고 사용합니다
- [ ] volume 백업 방법을 알고 있습니다

## 처음 질문으로 돌아가기

컨테이너를 재시작했을 때 데이터가 사라졌다면 volume이 없기 때문입니다. AI가 만든 설정에서 `volumes:` 섹션을 찾아 DB 컨테이너에 마운트되어 있는지 확인하세요. 앱에서 DB에 연결이 안 된다면 `DB_HOST` 값이 `localhost`인지 확인하고, 같은 `docker-compose.yml` 안에 있는 DB 서비스 이름으로 바꾸세요.

## 정리

Volume은 데이터를 컨테이너와 독립적으로 보존하고, Network는 컨테이너들이 이름으로 서로를 찾게 해 줍니다. AI가 만든 Docker 설정에서 이 두 가지를 확인하는 것만으로도 가장 흔한 데이터 손실과 연결 오류를 예방할 수 있습니다. 다음 글에서는 여러 컨테이너를 하나의 파일로 관리하는 Docker Compose를 다룹니다.

## 참고 자료

### 공식 문서
- [Docker Documentation](https://docs.docker.com/)
- [Manage data in Docker - Volumes](https://docs.docker.com/storage/volumes/)
- [Networking overview](https://docs.docker.com/network/)

### 관련 시리즈
- [Containers 101](../../containers-101/ko/)
- [Kubernetes 101](../../kubernetes-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- [바이브코딩을 위한 Docker 기초 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [바이브코딩을 위한 Docker 기초 (2/10): Image와 Container](./02-image-and-container.md)
- [바이브코딩을 위한 Docker 기초 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- **바이브코딩을 위한 Docker 기초 (4/10): Volume과 Network (현재 글)**
- [바이브코딩을 위한 Docker 기초 (5/10): Docker Compose](./05-docker-compose.md)
- [바이브코딩을 위한 Docker 기초 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [바이브코딩을 위한 Docker 기초 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [바이브코딩을 위한 Docker 기초 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [바이브코딩을 위한 Docker 기초 (9/10): Image 최적화](./09-image-optimization.md)
- [바이브코딩을 위한 Docker 기초 (10/10): 배포용 Docker 구성](./10-production-docker.md)
<!-- toc:end -->

Tags: 바이브코딩, Docker, AI코딩, 컨테이너
