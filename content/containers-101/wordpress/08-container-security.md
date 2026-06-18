---
series: containers-101
episode: 8
title: "바이브코딩을 위한 컨테이너 기초 (8/10): Container Security"
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- Containers
- Security
- Docker
- DevOps
language: ko
---

# 바이브코딩을 위한 컨테이너 기초 (8/10): Container Security

이 글은 **바이브코딩을 위한 컨테이너 기초** 시리즈의 여덟 번째 글입니다.

AI가 만들어 준 Dockerfile은 기본적으로 root로 실행됩니다. 컨테이너 안에 있으니 괜찮을 것 같지만, 실제로는 호스트에 영향을 줄 수 있습니다. 바이브코딩으로 빠르게 만든 앱일수록 보안 기본값을 확인해야 합니다.

---

## 오늘의 핵심 질문

AI가 만든 Dockerfile을 확인하니 `USER` 명령이 없습니다. 컨테이너 안에서 root로 실행되는데 괜찮을까요? 왜 문제가 될 수 있으며, 어떻게 고쳐야 할까요?

> "Container Security의 핵심은 root로 실행하지 않는 것, 최소 권한 원칙, 그리고 격리는 완전하지 않다는 가정 아래 심층 방어(defense-in-depth)입니다."

---

## 이 글에서 다룰 문제

- 컨테이너 안에서 root로 실행하면 왜 위험할까요?
- non-root 실행은 어떻게 설정하나요?
- AI가 만든 앱에서 시크릿을 안전하게 다루는 방법은?
- 이미지 취약점 스캔은 왜 해야 할까요?
- 바이브코딩 프로젝트에서 보안 체크리스트는 어떻게 만들까요?

---

## 바이브코딩 관점에서 컨테이너 보안이 중요한 이유

AI가 빠르게 앱을 만들다 보면 보안 기본값이 소홀해집니다. 가장 흔한 세 가지 실수:

**1. root로 실행**

```dockerfile
# AI가 자주 생성하는 기본 Dockerfile
FROM python:3.12-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "main.py"]
# USER 명령 없음 = root로 실행
```

컨테이너 내부 취약점이 발견되면 공격자가 root 권한으로 컨테이너를 제어할 수 있습니다. 더 심각하게는 컨테이너 탈출 취약점과 결합되면 호스트 시스템도 위험해집니다.

**2. 시크릿을 환경 변수에 하드코딩**

```dockerfile
ENV DB_PASSWORD=supersecret  # 이미지 레이어에 영구 기록
```

`docker history`로 누구나 볼 수 있습니다. 이미지를 공개 레지스트리에 올리면 전 세계에 공개됩니다.

**3. 취약한 베이스 이미지 사용**

```dockerfile
FROM python:latest  # 알려진 취약점 포함 가능
```

### 보안 기본값 적용

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app

# 비root 사용자 생성 및 전환
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000
CMD ["python", "-m", "app.main"]
```

**Docker 실행 시 보안 옵션:**

```bash
docker run -d \
  --user 1000:1000 \
  --read-only \
  --tmpfs /tmp \
  --cap-drop=ALL \
  --security-opt no-new-privileges \
  myorg/api:latest
```

**핵심 개념:**

- **non-root**: UID 0(root)이 아닌 일반 사용자로 프로세스를 실행합니다
- **capability**: Linux 커널이 root 권한을 약 40개 조각으로 나눈 것. `--cap-drop=ALL`로 모두 제거 후 필요한 것만 추가
- **seccomp**: 컨테이너가 호출할 수 있는 시스템 콜을 제한
- **image scanning**: 이미지 레이어의 CVE를 검사하는 절차
- **read-only filesystem**: `--read-only`로 컨테이너 내부 파일 변경 방지

---

## 적용 전후: 보안 기본값 적용

**Before**: AI가 생성한 기본 설정 (보안 위험)

```bash
docker run -d \
  --privileged \
  -e DB_PASSWORD=supersecret \
  myorg/api:latest

docker exec <container> id
# uid=0(root) gid=0(root)
```

**After**: 보안 기본값 적용

```bash
docker run -d \
  --user 1000:1000 \
  --read-only \
  --tmpfs /tmp \
  --cap-drop=ALL \
  -v /run/secrets/db_pw:/run/secrets/db_pw:ro \
  myorg/api:latest

docker exec <container> id
# uid=1000 gid=1000
```

**시크릿 관리 (환경 변수 대신 파일 마운트):**

```yaml
# docker-compose.yml
services:
  api:
    image: myorg/api:latest
    secrets:
      - db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt
```

---

## 자주 하는 실수

| 실수 | 결과 | 해결 방법 |
|------|------|-----------|
| `USER` 없이 root로 실행 | 취약점 악용 시 root 권한 | Dockerfile에 `USER` 추가 |
| 시크릿을 `ENV`에 하드코딩 | 이미지 레이어에 영구 노출 | 파일 마운트 또는 시크릿 매니저 |
| 스캔 없이 운영 배포 | 알려진 취약점 포함 이미지 운영 | CI에 `trivy image` 추가 |
| `--privileged` 남용 | 호스트와 거의 동일한 권한 | 필요한 capability만 추가 |
| 서명 검증 생략 | 의도치 않은 이미지 실행 위험 | digest 기반 pull 또는 cosign |

---

## AI 팁: Dockerfile 보안 강화 요청

AI에게 보안이 강화된 Dockerfile 생성을 요청하는 방법:

```
다음 조건을 만족하는 Python FastAPI 앱용 Dockerfile을 만들어 주세요:

보안 요구사항:
1. non-root 사용자로 실행 (UID 1000)
2. 읽기 전용 파일시스템 지원 (임시 파일은 /tmp에만 쓰기 허용)
3. 불필요한 패키지 최소화 (slim 베이스 이미지 사용)
4. 비밀번호, API 키를 Dockerfile이나 이미지에 포함하지 않음
5. HEALTHCHECK 추가

추가로 이 이미지를 trivy로 스캔하는 명령도 알려주세요.
```

---

## 체크리스트

- [ ] Dockerfile에 `USER` 명령을 추가해 non-root로 실행합니다
- [ ] 시크릿을 `ENV`나 Dockerfile에 직접 쓰지 않습니다
- [ ] `trivy image` 또는 유사 도구로 이미지를 스캔했습니다
- [ ] `--privileged` 없이 필요한 capability만 추가합니다
- [ ] `HEALTHCHECK`를 Dockerfile에 정의했습니다

---

## 처음 질문으로 돌아가기

**컨테이너 안에서 root로 실행되는 것이 왜 문제가 될까요?**

컨테이너 격리는 완전하지 않습니다. 컨테이너 내부 취약점이 발견되면 공격자는 root 권한으로 컨테이너를 제어할 수 있습니다. 컨테이너 탈출 취약점과 결합되면 호스트 시스템의 root 권한까지 얻을 수 있습니다. non-root 사용자로 실행하면 이 공격 경로를 막을 수 있습니다.

---

## 정리

컨테이너 보안은 복잡한 도구가 필요하지 않습니다. Dockerfile에 `USER` 추가, 시크릿을 환경 변수 대신 파일로 전달, CI에 이미지 스캔 추가, 이 세 가지만으로도 대부분의 기본 위험을 줄일 수 있습니다.

바이브코딩으로 빠르게 만든 앱일수록 이 보안 기본값을 반드시 확인해야 합니다.

다음 글에서는 컨테이너와 VM의 차이를 비교하며, AI가 만든 앱을 어떤 격리 환경에서 실행해야 하는지 살펴봅니다.

---

## 참고 자료

- [Docker security](https://docs.docker.com/engine/security/)
- [Trivy](https://aquasecurity.github.io/trivy/)
- [Kubernetes Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- Containers 101 예제 코드: https://github.com/yeongseon-books/book-examples/tree/main/containers-101/ko

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 컨테이너 기초 (1/10): Container란 무엇인가?
- 바이브코딩을 위한 컨테이너 기초 (2/10): Image와 Layer
- 바이브코딩을 위한 컨테이너 기초 (3/10): Runtime
- 바이브코딩을 위한 컨테이너 기초 (4/10): Dockerfile
- 바이브코딩을 위한 컨테이너 기초 (5/10): Volume
- 바이브코딩을 위한 컨테이너 기초 (6/10): Network
- 바이브코딩을 위한 컨테이너 기초 (7/10): Registry
- **바이브코딩을 위한 컨테이너 기초 (8/10): Container Security (현재 글)**
- 바이브코딩을 위한 컨테이너 기초 (9/10): Containers vs VMs
- 바이브코딩을 위한 컨테이너 기초 (10/10): 실전 컨테이너 앱 만들기

<!-- toc:end -->

Tags: 바이브코딩, Containers, Security, Docker, DevOps
