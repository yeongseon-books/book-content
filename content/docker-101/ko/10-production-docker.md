---
series: docker-101
episode: 10
title: "Docker 101 (10/10): 배포용 Docker 구성"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Docker
  - Production
  - Security
  - Logging
  - Capstone
seo_description: 프로덕션용 Docker에서 태그, 서명, 보안, 로그, 메트릭의 기준을 정리합니다
last_reviewed: '2026-05-15'
---

# Docker 101 (10/10): 배포용 Docker 구성

시리즈 내내 이미지를 만들고, 컨테이너를 실행하고, 데이터와 네트워크를 다루고, 설정과 최적화까지 살펴봤습니다. 그런데 프로덕션은 이 모든 요소가 한꺼번에 검증되는 장소입니다. 이미지 태그 정책이 느슨하면 무엇이 배포됐는지 모르게 되고, 로그가 컨테이너 안 파일로 남아 있으면 수집이 깨지며, 런타임 보안이 약하면 운영 전체가 불안정해집니다.

즉, 프로덕션은 개별 기술 체크리스트의 합이 아니라 시스템입니다. 이미지를 어떻게 만들었는지, 어디에 저장하는지, 어떤 권한으로 실행하는지, 실패를 어떻게 관찰하는지가 동시에 맞물려야 합니다. 이 글은 그 마지막 기준선을 정리합니다.

이 글은 Docker 101 시리즈의 마지막 글입니다. 여기서는 시리즈에서 만든 모든 구성 요소를 프로덕션 기준으로 묶어, 태그 정책·이미지 서명·런타임 보안·로그·메트릭을 어떤 순서로 점검해야 하는지 정리합니다.

## 먼저 던지는 질문

- 프로덕션에서는 어떤 이미지 태그 정책을 가져가야 할까요?
- 레지스트리와 이미지 서명은 왜 공급망 신뢰의 일부일까요?
- read-only, capability 제한, non-root는 어떤 식으로 결합해야 할까요?

## 큰 그림

![Docker 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/docker-101/10/10-01-concept-at-a-glance.ko.png)

*Docker 101 10장 흐름 개요*

이 그림에서는 배포용 Docker 구성를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 배포용 Docker 구성의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

운영 환경에서는 이전에 배운 모든 결정이 한 번에 현실이 됩니다. 빌드 단계에서 남겨 둔 불필요한 도구는 공격 표면이 되고, `latest` 태그는 배포 추적을 어렵게 만들며, healthcheck와 재시작 정책이 없으면 죽은 컨테이너가 조용히 방치될 수 있습니다.

프로덕션을 어렵게 만드는 이유는 기술이 복잡해서만이 아닙니다. 각각의 작은 선택이 서로 연결되어 있다는 점 때문입니다. 따라서 프로덕션 컨테이너는 "돌아간다"보다 "추적 가능하고, 안전하고, 관측 가능하다"를 기준으로 평가해야 합니다.

## 한눈에 보는 개념

## 핵심 용어

- **Tag policy**: `semver`와 `git sha`를 함께 쓰는 이중 태깅 규칙입니다.
- **Cosign**: 이미지를 서명하는 도구입니다.
- **Read-only rootfs**: 컨테이너 루트 파일시스템을 읽기 전용으로 잠그는 방식입니다.
- **Capabilities**: Linux 권한을 세분화한 제어 단위입니다.
- **Logging driver**: stdout 로그를 어떻게 수집하고 전달할지 정하는 방식입니다.

이 용어들은 따로 떨어진 옵션처럼 보여도 실제로는 하나의 운영 모델을 이룹니다. 추적 가능한 이미지, 신뢰 가능한 공급망, 최소 권한 런타임, 표준 로그·메트릭 채널이 함께 있어야 MTTR을 줄일 수 있습니다.

## Before / After

**Before**: `latest`로 배포하고, root로 실행하고, 로그를 컨테이너 내부 파일에 씁니다.

**After**: `1.4.2`와 `sha-abc1234`를 함께 태깅하고, non-root + read-only로 실행하며, 로그는 stdout으로 보냅니다.

이 차이는 프로덕션 장애 대응 속도를 바꿉니다. 무엇이 배포됐는지, 어떤 권한으로 돌고 있는지, 장애 시 어디서 로그를 봐야 하는지를 즉시 설명할 수 있기 때문입니다.

## 실습: 프로덕션 구성을 5단계로 정리하기

### 1단계 — 태그 지정과 push

```bash
TAG=1.4.2
SHA=$(git rev-parse --short HEAD)
docker build -t ghcr.io/me/myapp:${TAG} -t ghcr.io/me/myapp:sha-${SHA} .
docker push ghcr.io/me/myapp:${TAG}
docker push ghcr.io/me/myapp:sha-${SHA}
```

semver 태그는 사람이 읽기 좋고, sha 태그는 변경 추적에 강합니다. 둘을 함께 두면 배포 기록과 사고 대응이 훨씬 단단해집니다.

### 2단계 — 이미지 서명

```bash
cosign sign --yes ghcr.io/me/myapp:${TAG}
cosign verify --certificate-identity-regexp '.*' \
              --certificate-oidc-issuer-regexp '.*' \
              ghcr.io/me/myapp:${TAG}
```

이미지 서명은 공급망 신뢰의 출발점입니다. 레지스트리에 올라가 있다는 사실만으로는 그 이미지가 정말 여러분이 만든 산출물인지 보장할 수 없습니다.

### 3단계 — 런타임 보안 옵션

```bash
docker run -d --name api \
  --read-only \
  --tmpfs /tmp \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  --user 1000:1000 \
  -p 8000:8000 \
  ghcr.io/me/myapp:${TAG}
```

이 명령은 운영 기본값을 바꾸는 좋은 예입니다. 쓰기 권한을 최소화하고, capability를 제거하고, 권한 상승을 막고, non-root로 실행합니다. 결국 프로덕션은 허용보다 차단이 기본이어야 합니다.

### 4단계 — Compose로 표현하기

```yaml
services:
  web:
    image: ghcr.io/me/myapp:1.4.2
    read_only: true
    tmpfs: ["/tmp"]
    cap_drop: ["ALL"]
    user: "1000:1000"
    deploy:
      restart_policy: { condition: on-failure }
    logging:
      driver: json-file
      options: { max-size: "10m", max-file: "5" }
```

Compose로도 같은 운영 기준을 선언할 수 있습니다. 보안 플래그와 로그 정책을 명시적으로 남기면, 로컬·스테이징·운영 환경 사이에서 설정 차이를 관리하기 쉬워집니다.

### 5단계 — 메트릭 노출

```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

프로덕션에서는 로그만으로는 부족합니다. 상태를 계속 관찰하려면 메트릭이 필요합니다. 특히 요청 수, 지연 시간, 오류율은 운영에서 가장 먼저 보게 되는 신호입니다.

### 실행 뒤 바로 확인할 것

- push 뒤에는 semver 태그와 sha 태그가 둘 다 레지스트리에 올라가 있어야 하고, 서명 검증 명령이 성공해야 합니다.
- 런타임에서는 `/metrics` 엔드포인트가 열리고, 로그가 컨테이너 파일이 아니라 stdout으로 나오는지까지 확인합니다.

### 잘 안 될 때 먼저 볼 것

- `--read-only` 적용 뒤 앱이 실패하면 `/tmp` 같은 쓰기 경로를 tmpfs로 따로 열어 두었는지 먼저 확인합니다.
- 배포 추적이 흐리면 태그보다 digest 고정과 실제 배포 매니페스트가 일치하는지부터 확인합니다.

## 이 코드에서 먼저 봐야 할 점

- 이미지 서명은 공급망 신뢰를 추가합니다.
- read-only와 capability 제거는 런타임 권한을 크게 줄입니다.
- 로그와 메트릭은 stdout과 엔드포인트만으로도 충분한 표준 경로를 만들 수 있습니다.

여기서 중요한 것은 복잡한 기능을 많이 붙이는 것이 아닙니다. 운영 중 가장 자주 보는 신호와 가장 위험한 권한을 표준 방식으로 다루는 것입니다.

## 자주 하는 실수 다섯 가지

1. **`latest`를 그대로 배포합니다.** 어떤 버전이 실제로 떠 있는지 설명하기 어려워집니다.
2. **서명되지 않은 이미지를 사용합니다.** 공급망 공격 방어가 약해집니다.
3. **로그를 컨테이너 내부 파일에 씁니다.** 수집과 회전이 쉽게 깨집니다.
4. **`--privileged`를 습관처럼 사용합니다.** 보안 기본값이 무너집니다.
5. **healthcheck와 restart 정책을 두지 않습니다.** 죽은 컨테이너가 조용히 남을 수 있습니다.

이 다섯 가지는 모두 운영의 추적성과 복구 가능성을 떨어뜨립니다. 프로덕션 품질은 기능 수보다 실패를 얼마나 빨리 식별하고 복구할 수 있는가로 판단해야 합니다.

## 실무에서는 이렇게 이어집니다

실제 운영은 Kubernetes 위에서 이루어지는 경우가 많지만, 여기서 다룬 원칙은 거의 그대로 이어집니다. 태그와 digest 고정, 이미지 서명, read-only root filesystem, non-root 실행, 로그와 메트릭 분리는 Kubernetes manifest에서도 동일한 주제입니다.

즉, Docker 101에서 익힌 습관은 단순한 로컬 실습 기술이 아니라 더 큰 오케스트레이션 환경으로 넘어갈 때 그대로 가져갈 자산입니다.

## 시니어 엔지니어는 이렇게 생각합니다

- 프로덕션은 기본값을 허용에서 차단으로 뒤집는 곳입니다.
- 이미지 태그는 불변에 가깝게 관리하고, 실제 배포는 digest로 고정하는 편이 좋습니다.
- 로그는 stdout, 메트릭은 엔드포인트, 추적은 OTel 같은 표준 경로를 따릅니다.
- 서명되지 않은 이미지는 결국 출처가 불분명한 코드입니다.
- 모든 결정은 MTTR을 줄이는 방향으로 평가해야 합니다.

이 시리즈의 마지막 관점도 여기에 있습니다. Docker를 잘 쓴다는 말은 이미지를 잘 빌드하는 것에서 끝나지 않습니다. 운영에서 믿을 수 있는 단위로 만들고, 추적 가능하고, 안전하며, 관측 가능한 상태로 유지하는 것까지 포함합니다.

## 체크리스트

- [ ] semver와 sha 이중 태그를 사용합니다.
- [ ] 이미지를 서명하고 검증합니다.
- [ ] read-only, cap-drop, non-root를 적용합니다.
- [ ] 로그와 메트릭의 표준 채널이 있습니다.
- [ ] healthcheck와 restart 정책이 있습니다.

## 연습 문제

1. 이미지를 semver와 sha 태그로 함께 push해 보세요.
2. Cosign으로 서명하고 검증해 보세요.
3. read-only와 cap-drop을 적용한 컨테이너가 정상 동작하는지 확인해 보세요.

## 정리 및 다음 단계

여기까지 왔다면 Docker의 핵심 95%는 이미 다뤘다고 봐도 좋습니다. 이미지를 만들고, 컨테이너를 실행하고, 데이터와 네트워크를 분리하고, 설정을 외부화하고, 앱과 DB를 함께 운영하고, 이미지를 최적화하고, 마지막으로 프로덕션 기준까지 정리했습니다. 남는 과제는 이 감각을 더 큰 운영 환경으로 확장하는 것입니다.

다음 단계로는 Kubernetes 101에서 컨테이너 오케스트레이션을, SRE 101에서 운영 신뢰성을 이어서 보는 것이 좋습니다. Docker는 출발점이지만, 이미 충분히 실무적인 출발점입니다.

## 처음 질문으로 돌아가기

- **프로덕션에서는 어떤 이미지 태그 정책을 가져가야 할까요?**
  - 본문의 기준은 배포용 Docker 구성를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **레지스트리와 이미지 서명은 왜 공급망 신뢰의 일부일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **read-only, capability 제한, non-root는 어떤 식으로 결합해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Docker 101 (1/10): Docker란 무엇인가?](./01-what-is-docker.md)
- [Docker 101 (2/10): Image와 Container](./02-image-and-container.md)
- [Docker 101 (3/10): Dockerfile 작성하기](./03-dockerfile.md)
- [Docker 101 (4/10): Volume과 Network](./04-volume-and-network.md)
- [Docker 101 (5/10): Docker Compose](./05-docker-compose.md)
- [Docker 101 (6/10): 환경변수와 설정](./06-env-and-config.md)
- [Docker 101 (7/10): Python 앱 컨테이너화](./07-python-app-containerize.md)
- [Docker 101 (8/10): 데이터베이스와 함께 실행하기](./08-database-with-app.md)
- [Docker 101 (9/10): Image 최적화](./09-image-optimization.md)
- **배포용 Docker 구성 (현재 글)**

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Docker security](https://docs.docker.com/engine/security/)
- [Sigstore Cosign](https://docs.sigstore.dev/cosign/overview/)
- [Read-only filesystem](https://docs.docker.com/engine/reference/run/#read-only)
- [12-factor - logs](https://12factor.net/logs)

### 검증과 트러블슈팅

- [Image digests and immutable pulls](https://docs.docker.com/reference/cli/docker/image/pull/)

Tags: Docker, Production, Security, Logging, Capstone
