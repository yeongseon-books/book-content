---
series: docker-101
episode: 1
title: "Docker 101 (1/10): Docker란 무엇인가?"
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/253"
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
  - Container
  - DevOps
  - Linux
  - Virtualization
seo_description: Docker가 환경 차이를 어떻게 없애는지 첫 컨테이너 실습과 함께 설명합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (1/10): Docker란 무엇인가?

환경 차이는 입문자만 힘들게 하는 문제가 아닙니다. 숙련된 팀도 같은 문제로 시간을 잃습니다. 로컬에서는 되는데 CI에서만 실패하고, 어떤 개발자 노트북에서는 되는데 다른 노트북에서는 라이브러리 버전이 달라 오류가 나는 장면은 너무 흔합니다. 이런 문제는 개인 역량보다 시스템 설계의 문제에 가깝습니다.

이 글은 Docker 101 시리즈의 첫 번째 글입니다.

Docker를 처음 접하면 대개 이렇게 이해합니다. "개발 환경을 쉽게 맞춰 주는 도구구나." 맞는 말입니다. 하지만 이 설명만으로는 왜 팀들이 Docker를 표준처럼 쓰는지, 왜 컨테이너를 하나의 운영 단위로 보는지까지는 잘 보이지 않습니다. 진짜 핵심은 편의성보다 재현성에 있습니다. 누가 실행하든, 어디서 실행하든, 같은 이미지를 기준으로 같은 동작을 만들 수 있어야 한다는 문제를 Docker가 정면으로 다루기 때문입니다.

현업에서는 이 차이가 생각보다 큽니다. 개발자 노트북, CI, 스테이징, 운영 환경이 서로 조금씩 다르면 문제는 늘 애매하게 터집니다. 코드가 잘못된 것인지, 의존성이 다른 것인지, 운영 서버 설정이 다른 것인지 분간하는 데 시간을 다 써 버리기 쉽습니다. Docker는 바로 그 모호함을 줄이는 도구입니다.

![Docker 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/01/01-01-concept-at-a-glance.ko.png)
*Docker 101 1장 흐름 개요*

> Docker의 본질은 편의성이 아니라 재현성입니다 — '누가·어디서 실행하든 같은 이미지를 기준으로 같은 동작이 나온다'는 한 약속이, 개발자 노트북·CI·스테이징·운영의 미묘한 차이로 디버깅 시간을 다 써 버리던 문제를 정면으로 줄입니다.

## 이 글에서 다룰 문제

- Docker는 정확히 무엇을 해 주는 도구일까요?
- 컨테이너와 가상머신은 무엇이 다를까요?
- image, container, registry는 어떤 관계로 이해해야 할까요?
- 이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?
- 초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?

## 핵심 개념

Docker가 중요한 이유는 단순합니다. 코드만 공유하는 것이 아니라 실행 환경까지 함께 공유하게 만들기 때문입니다. 즉, 팀이 "어떻게 실행해야 하는가"를 위키 문서나 입소문이 아니라 이미지와 명령으로 표준화할 수 있습니다.

- **Image**: 코드, 라이브러리, 런타임을 포함한 실행 가능한 패키지입니다. 한 번 빌드되면 내용이 바뀌지 않습니다.
- **Container**: 이미지를 실제로 실행한 인스턴스입니다. 같은 이미지에서 여러 컨테이너를 동시에 실행할 수 있습니다.
- **Registry**: 이미지를 저장하고 배포하는 저장소입니다. Docker Hub, GHCR, ECR 등이 있습니다.
- **Daemon**: 컨테이너를 생성하고 관리하는 백그라운드 프로세스입니다.
- **Layer**: 이미지 내부에서 변경이 쌓이는 단위입니다. 레이어를 공유하면 저장 공간과 pull 시간이 절약됩니다.

이 용어는 처음엔 비슷해 보여도 역할이 분명히 다릅니다. 특히 image와 container를 분리해서 이해하지 못하면 이후 Dockerfile, volume, 배포 운영까지 전부 흐려집니다. 이미지는 배포 단위이고, 컨테이너는 실행 단위라는 구분부터 정확히 잡는 것이 좋습니다.

### 컨테이너 대 가상머신

컨테이너와 가상머신(VM)은 둘 다 격리된 실행 환경을 제공하지만, 방식이 다릅니다.

| 항목 | 가상머신(VM) | 컨테이너 |
|------|-------------|----------|
| 커널 | 각자 별도 OS | 호스트 커널 공유 |
| 시작 시간 | 수십 초 ~ 수 분 | 수백 밀리초 ~ 수 초 |
| 이미지 크기 | GB 수준 | MB ~ 수백 MB |
| 격리 수준 | 강함 (하이퍼바이저) | 중간 (네임스페이스 + cgroup) |
| 사용 사례 | 완전한 OS 격리 필요 시 | 애플리케이션 실행 환경 표준화 |

컨테이너는 VM과 달리 호스트 OS 커널을 공유합니다. 이 덕분에 가볍고 빠르지만, 보안 격리 수준은 VM보다 낮습니다. 따라서 프로덕션에서는 non-root 실행, capability 제한, read-only rootfs 같은 추가 보안 설정이 필요합니다.

## 전과 후

**Before**: "제 노트북에서는 돌아갑니다." 새 팀원 환경 구성에 반나절이 걸립니다. 라이브러리 버전 충돌로 서로 다른 결과가 나옵니다.

**After**: `docker run myapp` 한 줄로 같은 환경을 바로 실행합니다. 어떤 머신에서든 동일한 결과가 보장됩니다.

이 변화가 중요한 이유는 설치 시간이 짧아져서가 아닙니다. 팀이 같은 문제를 같은 방식으로 재현할 수 있게 되기 때문입니다. 재현성이 생기면 디버깅이 쉬워지고, 디버깅이 쉬워지면 배포 속도와 운영 안정성도 함께 올라갑니다.

## 실습: 첫 컨테이너를 5단계로 실행해 보기

### 1단계 — 설치 확인

```bash
docker --version
# Docker version 25.x.x
docker info
docker run hello-world
```

가장 먼저 확인할 것은 Docker가 설치되었는가가 아니라, 실제로 이미지를 받아 컨테이너를 실행할 수 있는가입니다. `hello-world`는 바로 그 확인용으로 가장 적절합니다. `docker info`는 데몬 상태와 전체 설정을 보여 줍니다.

### 2단계 — 공식 이미지 실행

```bash
# Python이 로컬에 없어도 실행 가능
docker run -it --rm python:3.12-slim python -c "import sys; print(sys.version)"

# Node.js도 동일하게
docker run -it --rm node:20-slim node -e "console.log('hello from node', process.version)"
```

이 명령은 Python이 로컬에 설치되어 있지 않아도, 이미지 안의 런타임으로 바로 명령을 실행할 수 있음을 보여 줍니다. 여기서 중요한 포인트는 "내 컴퓨터에 Python을 맞춰 깔았다"가 아니라 "필요한 런타임을 이미지가 이미 포함한다"는 점입니다.

- `-it`: 대화형 터미널 연결
- `--rm`: 실행 완료 후 컨테이너 자동 삭제

### 3단계 — 백그라운드 실행과 포트 매핑

```bash
# nginx 웹서버를 백그라운드로 실행, 호스트 8080 → 컨테이너 80
docker run -d --name web -p 8080:80 nginx:1.27-alpine

# 접속 확인
curl http://localhost:8080
# 또는 브라우저에서 http://localhost:8080
```

웹 서버처럼 계속 살아 있어야 하는 프로세스는 보통 백그라운드로 실행합니다. 포트 매핑(`-p 8080:80`)을 이해하는 것이 핵심입니다. 형식은 `호스트포트:컨테이너포트`입니다.

### 4단계 — 상태 확인과 정리

```bash
# 실행 중인 컨테이너 목록
docker ps

# 로그 확인
docker logs web
docker logs -f web    # 실시간 스트림

# 상태 확인
docker inspect web | jq '.[0].State'

# 정리
docker stop web && docker rm web

# 한 번에 정리 (실행 중이더라도)
docker rm -f web
```

컨테이너를 실행하는 것만큼 중요한 것이 관찰과 정리입니다. 어떤 컨테이너가 떠 있는지, 로그는 무엇인지, 다 쓴 컨테이너를 어떻게 내릴지를 일찍부터 익혀 두는 편이 좋습니다.

### 5단계 — 이미지 검색과 관리

```bash
# Docker Hub에서 검색
docker search postgres

# 공식 이미지 다운로드
docker pull redis:7-alpine
docker pull postgres:16

# 로컬 이미지 목록
docker images

# 이미지 상세 정보
docker image inspect redis:7-alpine

# 사용하지 않는 이미지 정리
docker image prune -f
```

이미지는 보통 직접 만들기도 하지만, 공식 이미지를 가져와 출발점으로 쓰는 경우도 많습니다. 따라서 pull과 images는 이후 모든 실습의 기본 명령이 됩니다.

### 실행 뒤 바로 확인할 것

- `docker run hello-world` 뒤에는 "Hello from Docker!"라는 성공 메시지가 보여야 합니다.
- `curl http://localhost:8080`은 nginx 기본 HTML을 반환해야 합니다. 빈 응답이나 연결 거부가 나오면 포트 매핑부터 다시 확인합니다.
- `docker ps`에서 컨테이너 상태가 `Up X seconds`로 보여야 합니다.

### 트러블슈팅

| 증상 | 원인 | 해결 방법 |
|------|------|-----------|
| `Cannot connect to the Docker daemon` | Docker 데몬이 꺼져 있음 | Docker Desktop 시작 또는 `sudo systemctl start docker` |
| `Port is already allocated` | 호스트 포트 충돌 | 다른 포트 번호 사용: `-p 8081:80` |
| `curl` 연결 거부 | 포트 매핑 누락 | `-p 8080:80` 플래그 추가 여부 확인 |
| `docker: command not found` | Docker 미설치 | [docs.docker.com/get-docker](https://docs.docker.com/get-docker/) 참고 |
| 컨테이너가 바로 종료됨 | 포그라운드 프로세스 없음 | `-d` 플래그 또는 `tail -f /dev/null` 추가 |

## 자주 하는 실수

| 실수 | 문제점 | 올바른 방법 |
|------|--------|-------------|
| Docker를 가상머신처럼 생각 | 커널 공유, 격리 모델 오해 | 컨테이너는 프로세스 격리임을 이해 |
| `latest` 태그를 프로덕션에서 사용 | 언제든 다른 버전으로 바뀔 수 있음 | `nginx:1.27-alpine`처럼 고정 태그 사용 |
| 컨테이너를 정리하지 않고 쌓아 둠 | 디스크 공간 낭비, 관리 복잡 | `docker rm -f`, `docker system prune` 활용 |
| 포트 매핑 없이 접속 시도 | 서비스가 떠 있어도 외부 접근 불가 | `-p 호스트포트:컨테이너포트` 필수 |
| root 실행을 당연하게 여김 | 보안 취약, 운영에서 위험 | `--user` 또는 Dockerfile에서 `USER` 지정 |

## Docker가 해결하는 근본 문제

Docker 이전에는 이런 문제들이 당연하게 여겨졌습니다.

```
# 흔한 상황들

"제 노트북에서는 Python 3.9인데, CI는 3.11이라 오류가 납니다."
"새 팀원 환경 구성에 반나절이 걸렸습니다. README가 안 맞습니다."
"운영 서버에 어떤 패키지가 깔려 있는지 아무도 정확히 모릅니다."
"스테이징에서는 됐는데 운영에서만 오류가 납니다."
```

Docker는 이 문제들을 "이미지"라는 단 하나의 개념으로 해결합니다.

```bash
# 팀원 모두가 같은 환경에서 시작
docker pull ghcr.io/myteam/myapp:1.2.3
docker run -d -p 8000:8000 ghcr.io/myteam/myapp:1.2.3
# 누가 어디서 실행해도 동일한 결과
```

### Docker가 하는 일 vs 하지 않는 일

| Docker가 하는 일 | Docker가 하지 않는 일 |
|-----------------|----------------------|
| 실행 환경을 이미지로 패키징 | 코드 자체를 더 좋게 만들기 |
| 환경 차이 제거 | 네트워크 지연 해결 |
| 빠른 시작/종료 | VM 수준의 보안 격리 |
| 재현 가능한 빌드 | 데이터 영속성 자동 보장 |
| 레지스트리로 배포 | 부하 분산, 자동 확장 |

## 실무에서는 이렇게 이어집니다

현업에서는 서비스 하나를 하나의 컨테이너로 패키징하고, 같은 이미지를 로컬 개발, CI, 스테이징, 운영 환경에 반복해서 사용합니다. 즉, Docker는 단순한 로컬 개발 도구라기보다 "배포 가능한 실행 단위"를 표준화하는 기반입니다.

그래서 많은 팀이 애플리케이션 코드를 검토할 때만큼이나 이미지 태그, 베이스 이미지, 실행 사용자, 포트, 헬스체크를 함께 검토합니다. Docker를 도입한다는 말은 개발 환경만 편해진다는 뜻이 아니라, 실행 방식 자체를 코드로 관리한다는 뜻에 가깝습니다.

## 자주 쓰는 명령 모음

```bash
# ── 이미지 관련 ─────────────────────────────────────────────
docker pull nginx:1.27-alpine          # 이미지 다운로드
docker images                          # 로컬 이미지 목록
docker image rm nginx:1.27-alpine      # 이미지 삭제
docker image prune -f                  # dangling 이미지 정리

# ── 컨테이너 실행 ────────────────────────────────────────────
docker run -d --name web -p 8080:80 nginx   # 백그라운드 실행
docker run -it --rm python:3.12-slim sh     # 대화형, 종료 후 삭제
docker run --rm -v "$PWD":/app -w /app \    # 현재 디렉터리 마운트
  python:3.12-slim python app.py

# ── 컨테이너 관리 ────────────────────────────────────────────
docker ps                    # 실행 중인 컨테이너
docker ps -a                 # 전체 컨테이너 (멈춘 것 포함)
docker logs web              # 로그 확인
docker logs -f web           # 실시간 로그
docker exec -it web bash     # 컨테이너 안으로 진입
docker stop web              # 정상 종료 (SIGTERM)
docker rm -f web             # 강제 삭제

# ── 전체 정리 ────────────────────────────────────────────────
docker system prune -af      # 모든 미사용 리소스 삭제
docker system df             # 사용 중인 디스크 공간 확인
```

## Docker를 배우는 순서

Docker 101 시리즈는 아래 흐름으로 진행됩니다. 각 글이 이전 글 위에 쌓이는 구조입니다.

```
1. Docker란 무엇인가?     ← 지금 여기
   image, container, registry 기본 이해

2. Image와 Container
   layer, lifecycle, writable layer

3. Dockerfile 작성하기
   명령 순서, 캐시 전략, 보안

4. Volume과 Network
   영속성, 서비스 간 통신

5. Docker Compose
   멀티 컨테이너 선언, healthcheck

6. 환경변수와 설정
   12-Factor App, secret 관리

7. Python 앱 컨테이너화
   PID 1, signal, healthcheck

8. DB와 함께 실행하기
   migration, seed, 준비 상태

9. Image 최적화
   멀티스테이지, BuildKit 캐시

10. 배포용 Docker 구성
    태그 정책, 서명, 런타임 보안
```

각 글은 독립적으로 읽을 수 있지만, 순서대로 읽으면 개념이 자연스럽게 쌓입니다. 처음 읽는다면 1→2→3 순서로 진행하는 것을 권장합니다.

## 운영 체크리스트

- [ ] `docker run hello-world`가 정상 동작합니다.
- [ ] image와 container의 차이를 설명할 수 있습니다.
- [ ] `-p 8080:80` 포트 매핑의 의미를 이해했습니다.
- [ ] 실행한 컨테이너를 `docker stop`과 `docker rm`으로 정리할 수 있습니다.
- [ ] `docker logs`로 컨테이너 출력을 확인할 수 있습니다.
- [ ] `latest` 태그를 프로덕션에서 쓰지 않는 이유를 설명할 수 있습니다.

## Docker 설치 확인과 환경 점검

처음 시작하는 분을 위해 Docker가 올바르게 설치되었는지 확인하는 방법입니다.

```bash
# Docker 버전 확인
docker --version
# Docker version 25.0.x, build abc123

# Docker 데몬 상태 확인
docker info
# 출력에 "Server:" 섹션이 보이면 데몬이 실행 중

# 가장 빠른 동작 확인
docker run hello-world

# 컨테이너 실행 가능 여부 확인 (권한 없으면 sudo 필요)
docker ps

# Linux에서 sudo 없이 실행하려면
sudo usermod -aG docker $USER
# 로그아웃 후 재로그인 필요
```

**플랫폼별 설치:**
- **Mac**: Docker Desktop (https://docs.docker.com/desktop/install/mac-install/)
- **Windows**: Docker Desktop + WSL2 (https://docs.docker.com/desktop/install/windows-install/)
- **Linux**: Docker Engine (https://docs.docker.com/engine/install/)

## 연습 문제

1. `nginx:1.27-alpine`을 실행하고 호스트 8080 포트로 접속해 보세요. 그리고 `docker logs`로 접속 로그를 확인해 보세요.
2. `python:3.12-slim`으로 대화형 셸을 열어 `import platform; print(platform.python_version())`를 실행해 보세요.
3. `docker ps -a`로 멈춘 컨테이너를 확인하고 `docker rm`으로 전부 정리해 보세요.
4. `docker image inspect nginx:1.27-alpine`에서 레이어 수와 생성 시각을 찾아보세요.

## 처음 질문으로 돌아가기

- **Docker는 정확히 무엇을 해 주는 도구일까요?**
  - 실행 환경을 이미지라는 불변 산출물로 묶어, 누가 어디서 실행하든 같은 동작을 만들어 줍니다. 코드만 공유하는 것이 아니라 런타임, 라이브러리, 설정까지 함께 묶어 배포 단위로 만들기 때문입니다.

- **컨테이너와 가상머신은 무엇이 다를까요?**
  - VM은 각자 별도 OS 커널을 갖지만, 컨테이너는 호스트 커널을 공유합니다. 그래서 컨테이너는 수백 밀리초 안에 시작되고, 이미지 크기도 MB 단위입니다. 대신 커널 수준 격리는 VM이 더 강합니다.

- **image, container, registry는 어떤 관계로 이해해야 할까요?**
  - image는 불변 설계도, container는 그 설계도를 실제로 실행한 인스턴스, registry는 이미지를 저장하고 배포하는 창고입니다. 코드 관점으로 보면 image는 클래스, container는 인스턴스, registry는 패키지 저장소에 가깝습니다.

- **이 기능을 프로덕션에서 쓸 때 보안 관점에서 주의할 점은 무엇일까요?**
  - 컨테이너를 root로 실행하지 않아야 하고, `latest` 태그 대신 고정 태그나 digest를 사용해야 합니다. 호스트 커널을 공유하므로 VM처럼 완전히 격리되지 않는다는 점도 기억해야 합니다.

- **초보자가 이 기능에서 가장 자주 겪는 오류는 무엇일까요?**
  - 포트 매핑 없이 접속을 시도하거나, Docker 데몬이 꺼진 상태에서 명령을 실행하는 경우가 가장 많습니다. 또한 컨테이너를 정리하지 않아 디스크가 차거나 이름 충돌이 나는 경우도 흔합니다.

## 정리

Docker는 환경 차이를 없애는 가장 빠른 출발점입니다. 이 글에서 가장 먼저 가져가야 할 핵심은 세 가지입니다. 첫째, Docker는 실행 환경을 이미지라는 산출물로 묶습니다. 둘째, 컨테이너는 그 이미지를 실제로 실행한 프로세스입니다. 셋째, 재현성이 생기면 디버깅과 배포가 모두 쉬워집니다.

다음 글에서는 image와 container를 더 깊게 분리해서 봅니다. 어디까지가 불변이고, 어디서 상태가 생기며, 왜 컨테이너를 언제든 버릴 수 있게 설계해야 하는지를 본격적으로 다룹니다.

<!-- toc:begin -->
## 시리즈 목차

- **Docker 101 (1/10): Docker란 무엇인가? (현재 글)**
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
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

- [Docker overview](https://docs.docker.com/get-started/overview/)
- [Get Docker](https://docs.docker.com/get-docker/)
- [Docker Hub](https://hub.docker.com/)
- [What is a container?](https://www.docker.com/resources/what-container/)

### 검증과 트러블슈팅

- [docker run reference](https://docs.docker.com/engine/reference/run/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/docker-101/ko)

Tags: Docker, Container, DevOps, Linux, Virtualization
