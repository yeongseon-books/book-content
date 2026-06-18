---
title: "바이브코딩을 위한 GitHub Actions 기초 (7/10): Docker 이미지 자동 빌드"
series: github-actions-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- GitHubActions
- Docker
- GHCR
- CICD
seo_description: "바이브코딩으로 만든 애플리케이션을 Docker 이미지로 자동 빌드하고 레지스트리에 올리는 방법을 설명합니다."
---

# 바이브코딩을 위한 GitHub Actions 기초 (7/10): Docker 이미지 자동 빌드

이 글은 바이브코딩을 위한 GitHub Actions 기초 시리즈의 7번째 글입니다.

AI로 웹 API나 서비스를 만들었다면 배포는 Docker 이미지 단위로 이루어지는 경우가 많습니다. 로컬에서 `docker build` 명령을 손으로 치고, 이미지를 직접 레지스트리에 올리고, 팀원에게 "내가 방금 올렸으니 배포해줘"라고 메시지를 보내는 패턴이 됩니다. 이 과정은 느리고, 누가 어떤 이미지를 올렸는지 추적하기 어렵고, 캐시 없이 매번 처음부터 빌드해서 시간도 많이 걸립니다.

GitHub Actions에서 Docker 빌드를 자동화하면 이 모든 것이 코드로 정의됩니다. PR이 열리면 이미지가 올바르게 빌드되는지 검증하고, main에 머지하면 SHA 태그와 함께 레지스트리에 자동으로 올라갑니다. 캐시를 활용하면 빌드 시간도 크게 줄어듭니다. 바이브코딩으로 만든 서비스를 컨테이너로 배포하는 팀이라면 이 자동화가 필수입니다.

> Docker 빌드 자동화는 `docker build`를 CI에 옮기는 것이 아닙니다. 캐시, 태그 전략, 권한 설정이 함께 설계되어야 빠르고 추적 가능한 이미지 파이프라인이 됩니다.

---

## 이 글에서 다룰 문제
- Buildx와 캐시 없이 Docker 빌드를 CI에 넣으면 어떤 문제가 생길까요?
- GHCR에 이미지를 올리려면 어떤 권한 설정이 필요할까요?
- `latest` 태그만 쓰면 왜 롤백이 어려워질까요?
- PR에서 이미지를 레지스트리에 올리지 않는 이유는 무엇일까요?
- Docker 빌드가 CI에서 느려지는 가장 흔한 원인은 무엇일까요?

---

## 캐시 없는 Docker 빌드의 현실

바이브코딩으로 만든 애플리케이션의 Dockerfile은 보통 의존성 설치 레이어가 포함됩니다.

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt  # 2-3분 소요
COPY src/ .
CMD ["python", "-m", "uvicorn", "main:app"]
```

캐시 없이 매 PR마다 이 Dockerfile을 빌드하면 `pip install` 단계가 매번 처음부터 실행됩니다. PR 하나에 3번 push하면 6-9분이 의존성 설치에 소비됩니다. Buildx와 `type=gha` 캐시를 쓰면 `requirements.txt`가 바뀌지 않는 한 이 레이어를 재사용합니다.

### 핵심 용어 정리

| 용어 | 뜻 | 실무 포인트 |
|------|------|------|
| Buildx | Docker 확장 빌더 | 캐시, 멀티 플랫폼, 최신 빌드 기능의 중심입니다 |
| gha 캐시 | GitHub Actions 캐시 백엔드 | 레이어 재사용으로 빌드 시간을 크게 줄입니다 |
| GHCR | GitHub Container Registry | GitHub 생태계 안에서 자연스럽게 쓸 수 있습니다 |
| `packages: write` | GHCR push에 필요한 권한 | 이 권한 없이 push하면 401 오류가 납니다 |
| SHA 태그 | 커밋 SHA 기반 이미지 태그 | 어떤 코드가 이 이미지에 담겼는지 추적합니다 |

---

## Before / After

**캐시 없는 단순 빌드**

```yaml
steps:
  - uses: actions/checkout@v6
  - run: docker build -t myapp .
  - run: docker push ghcr.io/myorg/myapp:latest
```

매번 전체 레이어를 새로 빌드하고, `latest` 태그만 있어서 이전 버전으로 돌아가기 어렵습니다.

**Buildx와 캐시를 활용한 표준 패턴**

```yaml
jobs:
  docker:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@v6

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: |
            ghcr.io/${{ github.repository }}:${{ github.sha }}
            ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

PR에서는 빌드만 하고 push는 하지 않습니다(`push: ${{ github.event_name != 'pull_request' }}`). main push 시에는 SHA 태그와 latest 두 개를 올립니다.

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `permissions: packages: write` 누락 | push 단계에서 401 오류 발생 | 잡에 권한을 명시합니다 |
| `latest` 태그만 사용 | 롤백 기준 이미지를 찾기 어려움 | SHA 또는 버전 태그를 함께 씁니다 |
| 캐시 없이 모든 레이어 재빌드 | PR마다 3-5분이 낭비됨 | `cache-from/to: type=gha`를 추가합니다 |
| PR에서도 이미지를 push | 검증 안 된 이미지가 레지스트리에 쌓임 | PR에서는 push를 false로 설정합니다 |
| 이미지 이름에 대문자 포함 | GHCR은 소문자만 허용 | `${{ github.repository }}`를 소문자로 변환합니다 |

## AI 팁: Docker 빌드 워크플로우 요청 프롬프트

```
프롬프트 예시:
"GitHub Actions에서 Docker 이미지를 빌드하고 GHCR에 push하는 워크플로우를 만들어줘.
조건:
- docker/setup-buildx-action과 docker/build-push-action 사용
- GitHub Actions Cache로 레이어 캐시 (cache-from/to: type=gha,mode=max)
- PR에서는 빌드만 (push: false), main push에서는 SHA 태그와 latest를 push
- permissions에 packages: write 포함
- 이미지 이름 소문자 처리"
```

받은 후에는 `permissions` 블록이 잡 레벨에 있는지 확인하세요. 워크플로우 레벨 permissions와 다릅니다.

## 운영 체크리스트
- [ ] `permissions: packages: write`가 잡에 선언됐는가?
- [ ] Buildx와 gha 캐시가 설정됐는가?
- [ ] PR에서는 push가 false인가?
- [ ] SHA 태그가 포함돼 있는가?
- [ ] 이미지 이름이 소문자인가?

## 처음 질문으로 돌아가기

- **PR에서 이미지를 push하지 않는 이유는?**
  PR은 아직 머지되지 않은 코드입니다. 검증 안 된 이미지가 레지스트리에 쌓이면 어떤 이미지가 배포 가능한 상태인지 불명확해집니다. PR에서는 빌드만 해서 오류가 없는지 확인합니다.

- **`latest` 태그만 쓰면 왜 위험한가?**
  `latest`는 덮어쓰입니다. 배포 후 문제가 생겼을 때 "이전 latest"로 돌아가기가 불가능합니다. SHA 태그를 함께 올리면 `ghcr.io/myorg/app:a1b2c3d`처럼 특정 버전으로 롤백할 수 있습니다.

- **캐시로 얼마나 시간이 줄어드나?**
  의존성 레이어가 캐시되면 `pip install`이 포함된 빌드가 3분 → 30초로 줄어드는 경우도 있습니다. Dockerfile에서 `COPY requirements.txt`를 소스 코드 복사보다 앞에 두면 캐시 효율이 높아집니다.

## 정리

Docker 빌드를 CI에서 자동화하면 "누가 언제 어떤 이미지를 올렸는지"가 워크플로우 로그에 남습니다. Buildx 캐시로 빌드 시간을 줄이고, SHA 태그로 추적성을 확보하고, PR에서는 빌드만 하는 구조를 갖추면 바이브코딩으로 만든 서비스의 이미지 파이프라인이 완성됩니다. 다음 글에서는 이 이미지를 실제 서버에 배포하는 자동화를 다룹니다.

## 참고 자료
### 공식 문서
- [docker/build-push-action](https://github.com/docker/build-push-action)
- [GHCR documentation](https://docs.github.com/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
### 관련 시리즈
- [Docker 101](../../docker-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 GitHub Actions 기초 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [바이브코딩을 위한 GitHub Actions 기초 (2/10): Workflow와 Job 구조 이해하기](./02-workflow-and-job.md)
- [바이브코딩을 위한 GitHub Actions 기초 (3/10): 트리거로 실행 시점 제어하기](./03-triggers.md)
- [바이브코딩을 위한 GitHub Actions 기초 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (5/10): Lint와 Type Check 자동화](./05-lint-and-typecheck.md)
- [바이브코딩을 위한 GitHub Actions 기초 (6/10): 빌드 아티팩트 관리](./06-build-artifact.md)
- **바이브코딩을 위한 GitHub Actions 기초 (7/10): Docker 이미지 자동 빌드 (현재 글)**
- [바이브코딩을 위한 GitHub Actions 기초 (8/10): 배포 자동화](./08-deploy-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (9/10): Secret 안전하게 관리하기](./09-secret-management.md)
- [바이브코딩을 위한 GitHub Actions 기초 (10/10): 실전 CI/CD 파이프라인 조립](./10-real-world-cicd-pipeline.md)
<!-- toc:end -->
Tags: 바이브코딩, GitHubActions, Docker, GHCR, CICD
