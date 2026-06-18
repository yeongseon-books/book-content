---
title: "바이브코딩을 위한 Docker 기초 (10/10): 배포용 Docker 구성"
series: docker-101
episode: 10
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Docker
- AI코딩
- 컨테이너
seo_description: "바이브코딩 시대, AI가 만든 Docker 설정을 실제 운영에 올리기 전에 확인해야 할 태그, 보안, 로그, 재시작 정책을 정리합니다"
---

# 바이브코딩을 위한 Docker 기초 (10/10): 배포용 Docker 구성

이 글은 바이브코딩을 위한 Docker 기초 시리즈의 10번째 글입니다.

AI로 빠르게 만든 앱을 처음으로 실제 서버에 배포하려고 합니다. Dockerfile, Compose, 환경변수, 데이터베이스 연동까지 모두 준비했습니다. 그런데 막상 운영 환경에 올리려니 불안합니다. "이 설정이 운영에서도 괜찮을까? 뭔가 빠진 것은 없을까?"

바이브코딩으로 만든 코드를 운영에 올릴 때 가장 흔하게 빠지는 것들이 있습니다. 이미지 태그를 `latest`로 그대로 두거나, 재시작 정책이 없어 컨테이너가 죽어도 아무 알림이 없거나, 로그가 컨테이너 안 파일에 쌓이거나, root로 실행되거나. 이것들은 개발 단계에서는 문제없어 보이지만 운영에서 장애가 나면 빠른 대응을 어렵게 만듭니다.

이 마지막 글에서는 AI가 만든 Docker 설정을 운영에 올리기 전에 확인해야 할 체크리스트를 정리합니다. 복잡한 이론보다 실용적인 확인 항목에 집중합니다.

> 프로덕션은 체크리스트의 합이 아니라 시스템입니다. 이미지 태그 정책, 실행 권한, 로그 수집, 재시작 정책이 동시에 맞물려야 무엇이 어디에 배포됐고, 실패했을 때 어떻게 알 수 있는가에 대한 답이 생깁니다.

---

## 이 글에서 다룰 문제
- `latest` 태그를 운영에 쓰면 어떤 문제가 생길까요?
- 재시작 정책이 없으면 컨테이너가 죽었을 때 어떻게 될까요?
- 로그를 컨테이너 안 파일에 쓰면 왜 문제가 될까요?
- AI가 만든 설정에서 운영 전 꼭 확인해야 할 것은 무엇일까요?
- read-only, cap-drop 같은 보안 설정은 어떻게 추가할까요?

## 운영 배포 전 핵심 확인 사항

**이미지 태그 정책**: `latest`는 어느 날 다른 이미지를 가리킬 수 있습니다. 운영에서는 `v1.4.2`나 `sha-abc1234`처럼 명시적 태그를 써야 무엇이 실행 중인지 추적할 수 있습니다.

**재시작 정책**: 컨테이너가 예기치 않게 종료될 때 자동으로 재시작되어야 합니다. `restart: on-failure` 또는 `restart: unless-stopped`를 추가하세요.

**로그 관리**: 컨테이너는 stdout으로 로그를 출력해야 합니다. 파일에 쓰면 컨테이너 재시작 시 사라지거나, 디스크를 가득 채울 수 있습니다.

**최소 권한 실행**: non-root, read-only filesystem, capability 제거는 보안의 기본값입니다.

## Before / After

**Before**: AI가 만든 설정에 `image: myapp:latest`, 재시작 정책 없음, 로그 설정 없음, root 실행. 서버에서 컨테이너가 크래시해도 자동 재시작이 안 되고, `docker logs`만 있으면 로그 관리가 어렵습니다.

**After**: 명시적 버전 태그, 재시작 정책, 로그 드라이버 설정, non-root + read-only 실행.

```yaml
services:
  web:
    image: myapp:1.4.2    # latest 대신 명시적 버전 태그
    read_only: true         # 파일시스템 읽기 전용
    tmpfs: ["/tmp"]         # /tmp만 쓰기 허용
    cap_drop: ["ALL"]       # 모든 Linux capability 제거
    user: "1000:1000"       # non-root 실행
    restart: on-failure     # 크래시 시 자동 재시작
    deploy:
      restart_policy:
        condition: on-failure
    logging:
      driver: json-file
      options:
        max-size: "10m"     # 로그 파일 크기 제한
        max-file: "5"       # 로그 파일 개수 제한
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/healthz"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `latest` 태그로 배포 | 어떤 버전이 실행 중인지 알 수 없음, 예기치 않은 업데이트 | 명시적 버전 태그 사용 (`v1.4.2`, `sha-abc123`) |
| 재시작 정책 없음 | 크래시 시 수동으로 재시작해야 함 | `restart: on-failure` 추가 |
| 로그를 컨테이너 내부 파일에 기록 | 재시작 시 손실, 디스크 고갈 위험 | stdout으로 출력, 로그 드라이버 설정 |
| healthcheck와 재시작 정책 모두 없음 | 죽은 컨테이너가 조용히 방치됨 | 둘 다 추가 |
| `--privileged` 또는 과도한 capability | 보안 사고 시 권한 과도 | `cap_drop: ALL`에서 필요한 것만 `cap_add` |

## AI에게 Docker 관련 요청하는 팁

- "이 Compose 파일을 운영 배포에 적합하게 개선해줘. 명시적 버전 태그, 재시작 정책, 로그 제한, non-root 실행을 포함해줘"라고 요청하세요.
- "read-only filesystem과 cap-drop을 적용해줘"라고 별도로 요청하면 AI가 보안 설정을 추가합니다.
- AI가 `latest` 태그를 계속 사용한다면 "latest 대신 특정 버전 태그를 사용해줘"라고 명시하세요.
- 배포 전 "이 Docker 설정에서 운영 보안 관점에서 문제가 될 수 있는 부분을 찾아줘"라고 AI에게 리뷰를 요청할 수도 있습니다.

## 운영 체크리스트

- [ ] `latest` 대신 명시적 버전 태그를 사용합니다
- [ ] 재시작 정책이 설정되어 있습니다
- [ ] 로그 드라이버와 크기 제한이 있습니다
- [ ] healthcheck가 있습니다
- [ ] non-root 실행이 설정되어 있습니다
- [ ] 비밀값이 `.env`로 분리되어 있습니다

## 처음 질문으로 돌아가기

AI가 만든 Docker 설정을 운영에 올리기 전에 이 여섯 가지를 순서대로 확인하세요. 태그가 `latest`이면 명시적 버전으로 바꾸고, 재시작 정책이 없으면 추가하고, 로그 설정이 없으면 드라이버를 지정하고, healthcheck가 없으면 추가하고, root 실행이면 `user`를 지정하고, 비밀값이 코드에 있으면 `.env`로 분리합니다. 이 여섯 가지만 챙기면 운영에서 가장 흔한 문제들을 예방할 수 있습니다.

## 정리

바이브코딩으로 빠르게 만든 Docker 설정은 대개 개발에는 충분하지만 운영에는 조금 더 손이 필요합니다. 이 시리즈에서 배운 것들을 요약하면 이렇습니다. 이미지는 불변 산출물로, 환경은 외부에서 주입하고, 데이터는 volume에, 통신은 network로, 시작 순서는 healthcheck로 보장하고, 이미지는 최적화하고, 운영에서는 최소 권한과 재시작 정책을 챙깁니다. AI와 함께 Docker를 사용한다면 이 체크리스트가 AI 결과물을 검토하는 기준이 됩니다.

## 참고 자료

### 공식 문서
- [Docker Documentation](https://docs.docker.com/)
- [Docker security](https://docs.docker.com/engine/security/)
- [Logging drivers](https://docs.docker.com/config/containers/logging/configure/)
- [Restart policies](https://docs.docker.com/config/containers/start-containers-automatically/)

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
- [바이브코딩을 위한 Docker 기초 (9/10): Image 최적화](./09-image-optimization.md)
- **바이브코딩을 위한 Docker 기초 (10/10): 배포용 Docker 구성 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, Docker, AI코딩, 컨테이너
