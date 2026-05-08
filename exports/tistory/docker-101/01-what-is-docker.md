
# Docker란 무엇인가?

> Docker 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *내 컴퓨터에서는 되는데* 라는 말을 *없애기 위해* Docker 는 무엇을 합니까?

> *Docker 는 *애플리케이션 + 의존성 + 실행 환경* 을 *하나의 단위* 로 묶어 *어디서나 동일하게* 실행되게 만듭니다.*

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *컨테이너* 와 *가상머신* 의 차이
- *Docker* 가 해결하는 *환경 표류* 문제
- *Image / Container / Registry* 의 큰 그림
- 첫 컨테이너 실행하기
- 흔한 함정 5가지

## 왜 중요한가

*환경 차이* 는 신입에게 가장 큰 좌절입니다. *Docker 한 줄* 로 *팀 전체가 같은 환경* 을 가지면, 디버깅 시간의 절반이 사라집니다.

> *환경 문제는 *개인의 실력 문제가 아니라 *시스템의 설계 문제* 입니다.*

## 개념 한눈에 보기

```mermaid
flowchart LR
    Code["내 코드"] --> Image["Docker Image"]
    Image --> Container["Container 실행"]
    Container --> Anywhere["로컬 / CI / 서버"]
```

## 핵심 용어 정리

- **Image**: *실행 가능한 패키지* (코드 + 라이브러리 + OS layer).
- **Container**: image 의 *실행 인스턴스*.
- **Registry**: image 보관 저장소 (Docker Hub, GHCR).
- **Daemon**: container 를 *생성/관리* 하는 백그라운드 프로세스.
- **Layer**: image 를 구성하는 *변경 단위*.

## Before/After

**Before**: "내 노트북에선 돌아가요." 새 팀원 셋업에 *반나절*.

**After**: `docker run myapp` 한 줄. *5분이면 동일 환경*.

## 실습: 첫 컨테이너 5단계

### 1단계 — Docker 설치 확인

```bash
docker --version
# Docker version 25.x.x
docker run hello-world
```

### 2단계 — 공식 image 실행

```bash
docker run -it --rm python:3.12-slim python -c "print('hi')"
```

### 3단계 — 백그라운드 실행

```bash
docker run -d --name web -p 8080:80 nginx
curl http://localhost:8080
```

### 4단계 — 상태 확인

```bash
docker ps              # 실행 중
docker logs web        # 로그
docker stop web && docker rm web
```

### 5단계 — Image 검색과 받기

```bash
docker pull redis:7-alpine
docker images
```

## 이 코드에서 주목할 점

- *image* 는 *실행 직전의 사진*, *container* 는 *살아 있는 프로세스*.
- *`-p 8080:80`* 은 *호스트:컨테이너* 포트 매핑.
- *`--rm`* 는 종료 후 자동 정리.

## 자주 하는 실수 5가지

1. **Docker 와 가상머신을 *동일시*.** 컨테이너는 *호스트 커널 공유*.
2. **`latest` tag 를 *프로덕션* 에 사용.** 어느 날 *조용히 깨짐*.
3. **`docker rm` 없이 컨테이너 *방치*.** 디스크가 *가득 찬다*.
4. **`-p` 없이 띄우고 *접속 안 됨* 으로 당황.** 포트 매핑이 필수.
5. **root 로 컨테이너 실행 후 *프로덕션* 으로 진출.** 보안 사고.

## 실무에서는 이렇게 쓰입니다

대부분의 회사가 *서비스 = container* 가정 위에 운영합니다. 로컬 개발, CI, 스테이징, 프로덕션이 *동일한 image* 를 씁니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *환경은 코드*, 위키 문서가 아니다.
- *Image 는 *불변*, container 는 *일회용*.
- *latest 는 데모용, 프로덕션은 *고정 tag*.
- *컨테이너는 *프로세스* 다. PID 1 을 의식한다.
- *호스트 커널 공유* 가 보안의 출발점.

## 체크리스트

- [ ] `docker run hello-world` 가 동작한다.
- [ ] *image* 와 *container* 의 차이를 설명할 수 있다.
- [ ] *포트 매핑* 의 의미를 안다.
- [ ] 컨테이너를 *정리* 할 수 있다.

## 연습 문제

1. `nginx` 를 띄워 *호스트 8080* 에서 접속해 보세요.
2. `python:3.12-slim` 으로 *대화형 셸* 을 띄워 보세요.
3. 실행 중 컨테이너의 *로그* 와 *상태* 를 확인해 보세요.

## 정리 및 다음 단계

Docker 는 *환경 표류* 를 없애는 가장 빠른 방법입니다. 다음 글에서는 *image 와 container* 의 내부를 더 깊이 봅니다.

- **Docker란 무엇인가? (현재 글)**
- Image와 Container (예정)
- Dockerfile 작성하기 (예정)
- Volume과 Network (예정)
- Docker Compose (예정)
- 환경변수와 설정 (예정)
- Python 앱 컨테이너화 (예정)
- 데이터베이스와 함께 실행하기 (예정)
- Image 최적화 (예정)
- 배포용 Docker 구성 (예정)
## 참고 자료

- [Docker overview](https://docs.docker.com/get-started/overview/)
- [Get Docker](https://docs.docker.com/get-docker/)
- [Docker Hub](https://hub.docker.com/)
- [What is a container?](https://www.docker.com/resources/what-container/)

Tags: Docker, Container, DevOps, Linux, Virtualization

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
