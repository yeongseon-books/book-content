---
title: "바이브코딩을 위한 GitHub Actions 기초 (1/10): GitHub Actions란 무엇인가?"
series: github-actions-101
episode: 1
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- GitHubActions
- CICD
- Automation
- DevOps
seo_description: "바이브코딩 시대, AI가 만든 코드를 자동으로 테스트하고 배포하려면 GitHub Actions부터 이해해야 합니다."
---

# 바이브코딩을 위한 GitHub Actions 기초 (1/10): GitHub Actions란 무엇인가?

이 글은 바이브코딩을 위한 GitHub Actions 기초 시리즈의 1번째 글입니다.

AI에게 코드를 만들어 달라고 하면 빠르게 동작하는 코드가 나옵니다. 그런데 그 코드를 서버에 올리고, 버그가 없는지 확인하고, 팀원과 같이 쓰는 시점이 되면 문제가 생깁니다. "내 로컬에서는 됐는데 서버에서 왜 에러가 나지?", "방금 머지했더니 main이 깨졌는데 누가 확인해?", "배포하려면 누가 손으로 서버에 명령을 쳐야 하나?" — 이런 상황들이 반복됩니다. 바이브코딩으로 만든 코드도 결국 자동화 없이는 팀 단위에서 쓰기 어렵습니다.

GitHub Actions는 코드 저장소 바로 옆에서 이런 반복 작업을 자동으로 처리해 주는 플랫폼입니다. PR을 열면 테스트가 돌고, main에 머지하면 서버에 배포되고, 매일 밤 취약점 스캔이 실행됩니다. 이 모든 것이 `.github/workflows/` 폴더 안의 YAML 파일 하나로 정의됩니다. 별도 서버를 운영할 필요도 없고, CI 툴을 따로 설치할 필요도 없습니다.

> AI가 만든 코드를 자동으로 테스트하고 배포하려면 CI/CD가 필요합니다. GitHub Actions는 저장소 안에 자동화를 코드로 정의하는 가장 빠른 방법입니다.

---

## 이 글에서 다룰 문제
- GitHub Actions는 정확히 무엇이고, 바이브코딩 워크플로에서 어디에 필요할까요?
- Workflow, Job, Step, Runner는 어떤 관계로 동작할까요?
- 첫 워크플로우를 가장 작은 구성으로 만들어 보려면 어떻게 해야 할까요?
- CI 없이 바이브코딩하면 어떤 문제가 반복될까요?
- 초보자가 처음 워크플로우를 만들 때 가장 자주 빠지는 함정은 무엇일까요?

---

## 바이브코딩 시대에 GitHub Actions가 필요한 이유

AI로 코드를 빠르게 만드는 것은 이제 어렵지 않습니다. 문제는 그 다음입니다. AI가 생성한 코드를 팀 저장소에 올리는 순간, 다른 사람의 코드와 충돌하거나 예상치 못한 버그가 섞일 수 있습니다. 수동으로 테스트를 돌리는 사람도 있고, 건너뛰는 사람도 생깁니다. 배포는 "아는 사람"이 수동으로 하게 됩니다.

GitHub Actions는 이 반복적인 수작업을 저장소 이벤트에 연결된 자동 절차로 바꿉니다. PR이 열리면 테스트가 자동 실행되고, 테스트를 통과해야만 머지할 수 있게 만들 수 있습니다. 배포 명령도 특정 조건에서 자동으로 실행됩니다. 바이브코딩으로 빠르게 만든 코드를 팀이 신뢰할 수 있는 상태로 유지하는 데 CI/CD는 필수입니다.

### 핵심 용어 정리

| 용어 | 뜻 | 실무 포인트 |
|------|------|------|
| 워크플로 | `.github/workflows/*.yml`에 정의된 자동화 단위 | 자동화의 시작점이자 범위입니다 |
| 이벤트 | 워크플로를 실행시키는 계기 | push, PR, schedule 등이 있습니다 |
| 잡 | 워크플로 안의 실행 단위 | 기본적으로 병렬 실행됩니다 |
| 스텝 | 잡 안의 개별 명령 또는 액션 호출 | 실제 테스트, 빌드가 여기서 일어납니다 |
| 러너 | 잡이 실행되는 가상 머신 | ubuntu-latest가 가장 흔히 쓰입니다 |
| 액션 | 재사용 가능한 스텝 | `actions/checkout`처럼 공개 액션을 가져다 씁니다 |

---

## Before / After

**GitHub Actions 없을 때**

```text
개발자 A: "방금 머지했는데 테스트 돌렸어요?"
개발자 B: "아, 로컬에서 main 기준으로 안 돌렸는데..."
배포 담당자: (터미널 열고 수동으로 명령 실행)
```

**GitHub Actions 도입 후**

```yaml
# .github/workflows/ci.yml
name: ci
on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: pytest -q
```

PR을 열면 이 워크플로우가 자동 실행됩니다. 테스트를 통과해야만 머지 버튼이 활성화됩니다. 사람이 "테스트 돌렸어요?"를 물을 필요가 없어집니다.

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 워크플로 파일을 `.github/workflows/` 밖에 둠 | GitHub이 인식하지 못함 | 경로를 정확히 지켜야 합니다 |
| `actions/checkout` 없이 바로 명령 실행 | 러너에 저장소 코드가 없음 | 첫 스텝은 항상 checkout입니다 |
| 비밀값을 YAML에 직접 작성 | 저장소 공개 시 노출 | `secrets.*`로만 참조합니다 |
| `on:` 없이 파일 작성 | 어떤 이벤트에도 반응 안 함 | 트리거를 반드시 선언합니다 |
| 모든 작업을 한 파일에 몰아 넣음 | 나중에 분리하기 어려움 | 역할별로 파일을 나눕니다 |

## AI 팁: GitHub Actions 워크플로우 요청 프롬프트

```
프롬프트 예시:
"GitHub Actions로 Python 프로젝트 CI 워크플로우를 만들어줘.
조건:
- Python 3.11 기준
- PR과 main push 양쪽에서 실행
- pip install 후 pytest 실행
- 캐시를 활용해서 의존성 설치 시간 단축
- actions/checkout과 setup-python 최신 버전 사용"
```

이렇게 요청하면 바로 사용 가능한 수준의 워크플로우를 얻을 수 있습니다. 받은 뒤에는 `on:` 트리거와 `actions/checkout` 스텝이 빠지지 않았는지 반드시 확인하세요.

## 운영 체크리스트
- [ ] `.github/workflows/` 디렉터리가 올바른 위치에 있는가?
- [ ] `on:` 트리거가 선언돼 있는가?
- [ ] 첫 스텝에 `actions/checkout`이 있는가?
- [ ] 비밀값이 YAML에 직접 노출되지 않았는가?
- [ ] PR 체크에서 결과가 보이는가?

## 처음 질문으로 돌아가기

- **GitHub Actions는 바이브코딩 워크플로에서 어디에 필요할까요?**
  AI가 만든 코드를 저장소에 올리는 순간부터 테스트, 빌드, 배포까지의 반복 작업을 자동화해 줍니다. 팀 단위로 코드를 관리하면서 품질 기준을 유지하려면 CI/CD는 선택이 아닙니다.

- **Workflow, Job, Step, Runner의 관계는?**
  이벤트가 워크플로우를 깨우고, 워크플로우 안에서 잡이 병렬로 실행되고, 각 잡 안에서 스텝이 순서대로 실행됩니다. 잡은 러너라는 가상 머신 위에서 돌아갑니다.

- **초보자가 가장 자주 빠지는 함정은?**
  `actions/checkout`을 빠뜨리는 것입니다. 러너는 깨끗한 환경이라 저장소 코드가 없습니다. checkout 없이 pytest를 돌리면 당연히 코드를 찾지 못해 실패합니다.

## 정리

GitHub Actions는 코드 저장소 바로 옆에서 반복 작업을 자동화하는 플랫폼입니다. 바이브코딩으로 빠르게 만든 코드도 PR마다 테스트가 자동으로 돌고, 통과해야만 머지되고, 배포까지 이어지는 구조를 갖추면 팀 전체의 신뢰 기반이 달라집니다. 다음 글에서는 워크플로우와 잡의 내부 구조, 병렬 실행과 의존성 설계를 다룹니다.

## 참고 자료
### 공식 문서
- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Workflow syntax](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
### 관련 시리즈
- [DevOps 101](../../devops-101/ko/)
- [Git & GitHub 101](../../git-github-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- **바이브코딩을 위한 GitHub Actions 기초 (1/10): GitHub Actions란 무엇인가? (현재 글)**
- [바이브코딩을 위한 GitHub Actions 기초 (2/10): Workflow와 Job 구조 이해하기](./02-workflow-and-job.md)
- [바이브코딩을 위한 GitHub Actions 기초 (3/10): 트리거로 실행 시점 제어하기](./03-triggers.md)
- [바이브코딩을 위한 GitHub Actions 기초 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (5/10): Lint와 Type Check 자동화](./05-lint-and-typecheck.md)
- [바이브코딩을 위한 GitHub Actions 기초 (6/10): 빌드 아티팩트 관리](./06-build-artifact.md)
- [바이브코딩을 위한 GitHub Actions 기초 (7/10): Docker 이미지 자동 빌드](./07-docker-build.md)
- [바이브코딩을 위한 GitHub Actions 기초 (8/10): 배포 자동화](./08-deploy-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (9/10): Secret 안전하게 관리하기](./09-secret-management.md)
- [바이브코딩을 위한 GitHub Actions 기초 (10/10): 실전 CI/CD 파이프라인 조립](./10-real-world-cicd-pipeline.md)
<!-- toc:end -->
Tags: 바이브코딩, GitHubActions, CICD, Automation, DevOps
