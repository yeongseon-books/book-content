---
title: "바이브코딩을 위한 Docker 기초 (6/10): 환경변수와 설정"
series: docker-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Docker
- AI코딩
- 컨테이너
seo_description: "바이브코딩 시대, AI가 만든 Dockerfile에서 비밀값이 이미지에 박히는 위험을 막는 환경변수 분리 원칙을 설명합니다"
---

# 바이브코딩을 위한 Docker 기초 (6/10): 환경변수와 설정

이 글은 바이브코딩을 위한 Docker 기초 시리즈의 6번째 글입니다.

AI에게 "데이터베이스 연결 설정을 Dockerfile에 넣어줘"라고 하면, AI는 가끔 이런 코드를 생성합니다. `ENV DB_PASSWORD=mysecretpassword`. 로컬에서 바로 동작하니 편리합니다. 그런데 이 파일을 Git에 올리거나 이미지를 누군가에게 공유하는 순간, 비밀번호도 함께 배포됩니다. `docker history 이미지명`으로 레이어를 들여다보면 ENV에 넣은 값이 그대로 보입니다.

바이브코딩의 편리함이 보안 사고로 이어지는 가장 흔한 경로 중 하나가 바로 여기입니다. AI가 생성한 설정 코드를 그대로 쓰면 비밀값이 이미지에 박히거나 Git 저장소에 올라갑니다. 이 패턴을 알아채고 올바르게 수정하는 것이 이 글의 핵심입니다.

컨테이너 운영의 기본 원칙은 이미지와 환경을 분리하는 것입니다. 이미지는 어떤 환경에서 실행되든 동일한 불변 산출물이어야 하고, 환경별 차이와 비밀값은 실행 시점에 주입해야 합니다. 이 원칙을 지키면 하나의 이미지로 개발, 스테이징, 운영 환경을 모두 지원할 수 있습니다.

> 컨테이너 운영의 핵심 규칙은 이미지와 환경을 분리하는 것입니다. 환경마다 다른 이미지를 빌드하기 시작하면 재현성이 바로 무너지므로, 이미지는 불변 산출물로 유지하고 환경별 차이는 런타임 환경변수로 주입해야 합니다.

---

## 이 글에서 다룰 문제
- AI가 `ENV DB_PASSWORD=...`를 Dockerfile에 넣어줬을 때 왜 위험할까요?
- `ENV`와 `ARG`는 무엇이 다를까요?
- `.env` 파일을 어떻게 안전하게 관리할까요?
- 하나의 이미지로 개발, 스테이징, 운영을 지원하려면 어떻게 설정할까요?
- 비밀값이 이미지에 들어갔는지 확인하는 방법은 무엇일까요?

## ENV와 ARG의 차이

AI가 가장 많이 혼동하는 부분입니다.

- **ARG**: 빌드 시점에만 사용하는 변수입니다. 최종 이미지에 남지 않습니다.
- **ENV**: 최종 이미지와 실행 환경에 남는 변수입니다. `docker history`로 값이 보입니다.
- **`-e` 또는 `--env-file`**: 실행 시점에 값을 주입하는 방법입니다. 이미지에는 저장되지 않습니다.

비밀값은 반드시 실행 시점에 주입해야 합니다. `ENV DB_PASSWORD=비밀번호`는 절대 사용하면 안 됩니다.

## Before / After

**Before**: AI가 만든 Dockerfile에 `ENV DB_PASSWORD=dev123`이 들어 있습니다. 이미지를 빌드하면 비밀번호가 레이어에 박힙니다. Git에 Dockerfile을 올리면 비밀번호도 공개됩니다.

**After**: Dockerfile에는 `ENV DB_PASSWORD`만 선언하고 기본값 없이 둡니다. 실행 시 `--env-file .env`나 `-e DB_PASSWORD=값`으로 주입합니다. `.env`는 `.gitignore`에 추가합니다.

```dockerfile
# 잘못된 패턴 (AI가 자주 생성)
ENV DB_PASSWORD=mysecretpassword

# 올바른 패턴: 이미지에는 변수 이름만, 값은 런타임에 주입
ENV LOG_LEVEL=INFO
# DB_PASSWORD는 Dockerfile에서 선언하지 않음
```

```bash
# 실행 시 주입
docker run --env-file .env.dev myapp:1.0
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 비밀값을 Dockerfile `ENV`에 넣음 | `docker history`로 값이 노출, 이미지 배포 시 유출 | 런타임에 `-e` 또는 `--env-file`로 주입 |
| `.env` 파일을 Git에 커밋 | 비밀값이 저장소에 공개됨 | `.gitignore`에 `.env` 추가 |
| 환경마다 다른 이미지를 빌드 | "같은 앱"이라는 전제가 사라져 재현성이 깨짐 | 이미지 하나로 유지, 환경별 차이는 변수로 분리 |
| 필수 변수가 없어도 조용히 실행됨 | 런타임에 예상치 못한 오류가 늦게 드러남 | 앱 시작 시 필수 변수 검증 후 없으면 즉시 실패 |
| 로그에 환경변수 전체를 출력 | 비밀값이 로그에 노출될 수 있음 | 민감한 변수는 로그에서 마스킹 |

## AI에게 Docker 관련 요청하는 팁

- "비밀값이나 DB 비밀번호는 Dockerfile에 넣지 말고 런타임에 주입하도록 해줘"라고 명시적으로 요청하세요.
- AI가 만든 Dockerfile에 `ENV`로 비밀값이 들어 있다면 즉시 제거하고, `.env` 파일과 `--env-file` 옵션으로 분리하세요.
- "이 설정을 `.env.example` 파일로도 만들어줘"라고 하면, 팀원들이 필요한 변수 목록을 파악할 수 있습니다.
- `docker history 이미지명`을 실행해서 ENV 레이어에 비밀값이 노출되어 있지 않은지 확인하세요.

## 운영 체크리스트

- [ ] Dockerfile에 비밀값이 직접 들어 있지 않습니다
- [ ] `.env` 파일이 `.gitignore`에 포함되어 있습니다
- [ ] `.env.example`이 존재합니다
- [ ] 같은 이미지를 환경별로 다시 빌드하지 않습니다
- [ ] `docker history 이미지명`으로 ENV 레이어를 확인했습니다

## 처음 질문으로 돌아가기

AI가 Dockerfile에 비밀값을 넣어 줬다면, `docker history 이미지명`으로 ENV 레이어에 비밀값이 보이는지 확인하세요. 보인다면 이미 이미지에 박힌 것입니다. 이미지를 다시 빌드해야 합니다. 이번에는 Dockerfile에서 비밀값 있는 `ENV` 줄을 제거하고, `.env` 파일로 분리해 실행 시 `--env-file`로 주입하세요.

## 정리

이미지와 환경을 분리하는 원칙은 간단합니다. 이미지에는 코드와 구조만, 비밀값과 환경별 차이는 실행 시점에 주입합니다. AI가 만든 설정 파일에서 비밀값이 코드에 하드코딩되어 있는지 확인하는 것만으로도 가장 흔한 보안 실수를 막을 수 있습니다. 다음 글에서는 Python 앱을 실제로 컨테이너화하는 방법을 다룹니다.

## 참고 자료

### 공식 문서
- [Docker Documentation](https://docs.docker.com/)
- [The Twelve-Factor App - Config](https://12factor.net/config)
- [Set environment variables in containers](https://docs.docker.com/engine/reference/commandline/run/#env)

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
- **바이브코딩을 위한 Docker 기초 (6/10): 환경변수와 설정 (현재 글)**
- [바이브코딩을 위한 Docker 기초 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [바이브코딩을 위한 Docker 기초 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [바이브코딩을 위한 Docker 기초 (9/10): Image 최적화](./09-image-optimization.md)
- [바이브코딩을 위한 Docker 기초 (10/10): 배포용 Docker 구성](./10-production-docker.md)
<!-- toc:end -->

Tags: 바이브코딩, Docker, AI코딩, 컨테이너
