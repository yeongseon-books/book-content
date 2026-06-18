---
title: "바이브코딩을 위한 Docker 기초 (7/10): Python 앱 컨테이너화"
series: docker-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Docker
- AI코딩
- 컨테이너
seo_description: "바이브코딩 시대, AI가 만든 Python 앱 Dockerfile에서 PID 1, healthcheck, non-root를 올바르게 설정하는 방법을 설명합니다"
---

# 바이브코딩을 위한 Docker 기초 (7/10): Python 앱 컨테이너화

이 글은 바이브코딩을 위한 Docker 기초 시리즈의 7번째 글입니다.

AI에게 "FastAPI 앱을 Docker로 실행하게 해줘"라고 요청하면 Dockerfile이 나옵니다. `python app.py`를 직접 실행하거나 `uvicorn app:app`으로 시작하는 간단한 형태입니다. 로컬에서는 잘 됩니다. 그런데 실제 서버에 올렸을 때 배포 중에 기존 요청이 갑자기 끊기거나, 로드 밸런서가 컨테이너가 준비됐는지 알 수 없다는 오류가 납니다.

"컨테이너 안에서 뜬다"와 "운영에 올려도 된다"는 다른 말입니다. AI가 생성한 기본 Python 컨테이너화 코드는 동작은 하지만, 운영에서 중요한 몇 가지가 빠져 있습니다. PID 1 처리, graceful shutdown, healthcheck, non-root 실행입니다. 이것들이 없으면 배포 중 요청 손실이나 보안 취약점이 생깁니다.

이 글에서는 AI가 생성해 준 Python 앱 Dockerfile을 운영 수준으로 개선하는 방법을 봅니다. 복잡한 것은 없습니다. 핵심은 네 가지 운영 조건을 체크리스트로 확인하는 것입니다.

> '컨테이너 안에서 뜬다'와 '운영에 올려도 된다'는 다른 말입니다. Python 웹앱 컨테이너화의 진짜 관문은 코드가 아니라 PID 1, 종료 신호 처리, healthcheck, non-root 같은 운영 조건입니다.

---

## 이 글에서 다룰 문제
- AI가 만든 `python app.py` 방식의 실행에 어떤 문제가 있을까요?
- PID 1과 SIGTERM은 왜 컨테이너 종료 시 중요할까요?
- healthcheck는 어떻게 추가해야 할까요?
- non-root 실행을 AI 결과물에 추가하는 방법은 무엇일까요?
- FastAPI와 uvicorn의 조합에서 graceful shutdown을 어떻게 확인할까요?

## 운영 조건 네 가지 이해

- **PID 1**: 컨테이너 안에서 가장 먼저 실행되는 프로세스입니다. 신호 처리와 좀비 프로세스 정리를 담당합니다. `python app.py`가 직접 PID 1이 되면 신호 처리가 불안정해질 수 있습니다.
- **SIGTERM / graceful shutdown**: `docker stop`은 SIGTERM을 보냅니다. 앱이 이를 받아 진행 중인 요청을 마무리하고 종료해야 합니다. 이를 무시하면 진행 중인 요청이 강제 종료됩니다.
- **healthcheck**: 컨테이너가 떴다는 것과 요청을 받을 준비가 됐다는 것은 다릅니다. healthcheck 엔드포인트가 있어야 오케스트레이터나 Compose가 준비 상태를 알 수 있습니다.
- **non-root**: 기본적으로 Docker 컨테이너는 root로 실행됩니다. 보안 사고 시 권한이 과도합니다.

## Before / After

**Before**: AI가 만든 Dockerfile이 `CMD ["python", "app.py"]`로 끝납니다. root로 실행되고, healthcheck가 없으며, `docker stop` 시 요청이 강제 종료됩니다.

**After**: `tini`를 init 프로세스로 두고, uvicorn이 graceful shutdown을 처리하며, `/healthz` 엔드포인트와 Dockerfile의 `HEALTHCHECK`가 연결됩니다. `USER appuser`로 non-root 실행합니다.

```dockerfile
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# 의존성 레이어 분리 (캐시 최적화)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드
COPY . .

# non-root 사용자 생성
RUN useradd -m -u 1000 appuser
USER appuser

EXPOSE 8000

# 컨테이너 준비 상태 확인
HEALTHCHECK --interval=10s --timeout=3s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz').read()" || exit 1

# tini: PID 1 init, SIGTERM을 uvicorn에 올바르게 전달
ENTRYPOINT ["tini", "--"]
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `python app.py`를 직접 PID 1로 실행 | SIGTERM 처리 불안정, 좀비 프로세스 가능성 | `tini --` 또는 uvicorn이 직접 PID 1이 되도록 구성 |
| healthcheck 없음 | 로드 밸런서나 Compose가 준비 상태를 모름 | `/healthz` 엔드포인트 추가, Dockerfile에 `HEALTHCHECK` 추가 |
| root로 실행 | 보안 사고 시 권한 과도 | `useradd` 후 `USER appuser` 추가 |
| healthcheck에서 DB 연결 검사 | DB 장애 시 앱 healthcheck까지 실패하는 false negative 발생 | healthcheck는 앱 자체의 준비 상태만 확인 |
| workers 수를 과도하게 설정 | 메모리 사용량이 급증 | 부하 테스트로 적정값 결정 |

## AI에게 Docker 관련 요청하는 팁

- "tini를 사용해 PID 1 신호 처리를 올바르게 설정해줘"라고 요청하세요. AI가 `tini` 설치와 `ENTRYPOINT` 설정을 함께 만들어 줍니다.
- "앱의 준비 상태를 알리는 `/healthz` 엔드포인트와 Dockerfile HEALTHCHECK를 추가해줘"라고 함께 요청하세요.
- AI가 만든 Dockerfile에 `USER`가 없다면 "non-root 사용자로 실행하도록 USER 지시어를 추가해줘"라고 요청하세요.
- `docker stop 컨테이너명` 후 `docker logs 컨테이너명 | tail`을 실행해 정상 종료가 되는지 확인하세요.

## 운영 체크리스트

- [ ] `tini` 또는 동등한 init 프로세스를 사용합니다
- [ ] `/healthz` 엔드포인트가 있고 Dockerfile에 `HEALTHCHECK`가 있습니다
- [ ] 컨테이너가 non-root로 실행됩니다
- [ ] `docker stop` 시 진행 중 요청이 안전하게 종료되는지 확인했습니다
- [ ] `docker exec 컨테이너명 id`로 non-root 확인을 했습니다

## 처음 질문으로 돌아가기

AI가 만든 Python 컨테이너 Dockerfile을 받으면 네 가지를 확인하세요. 첫째, `ENTRYPOINT`나 `CMD`에 `tini`가 있는가. 둘째, `/healthz` 같은 healthcheck 엔드포인트와 Dockerfile의 `HEALTHCHECK`가 있는가. 셋째, `USER`로 non-root 실행이 설정되어 있는가. 넷째, `ENV` 등에 비밀값이 없는가. 이 네 가지 체크만으로 운영 수준의 컨테이너가 됩니다.

## 정리

Python 앱 컨테이너화에서 AI가 놓치기 쉬운 것들은 PID 1 처리, healthcheck, non-root 실행입니다. 이 세 가지를 체크리스트로 확인하고 없으면 추가 요청을 하면, AI가 만든 코드를 운영 수준으로 끌어올릴 수 있습니다. 다음 글에서는 데이터베이스와 앱을 함께 운영하는 구성을 다룹니다.

## 참고 자료

### 공식 문서
- [Docker Documentation](https://docs.docker.com/)
- [FastAPI in containers](https://fastapi.tiangolo.com/deployment/docker/)
- [tini - a tiny init for containers](https://github.com/krallin/tini)
- [Dockerfile HEALTHCHECK](https://docs.docker.com/engine/reference/builder/#healthcheck)

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
- **바이브코딩을 위한 Docker 기초 (7/10): Python 앱 컨테이너화 (현재 글)**
- [바이브코딩을 위한 Docker 기초 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [바이브코딩을 위한 Docker 기초 (9/10): Image 최적화](./09-image-optimization.md)
- [바이브코딩을 위한 Docker 기초 (10/10): 배포용 Docker 구성](./10-production-docker.md)
<!-- toc:end -->

Tags: 바이브코딩, Docker, AI코딩, 컨테이너
