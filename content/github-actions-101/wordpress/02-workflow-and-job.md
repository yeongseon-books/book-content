---
title: "바이브코딩을 위한 GitHub Actions 기초 (2/10): Workflow와 Job 구조 이해하기"
series: github-actions-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- GitHubActions
- Workflow
- Job
- CICD
seo_description: "바이브코딩으로 만든 코드를 자동화하려면 Workflow, Job, Step의 관계와 병렬 실행 설계를 알아야 합니다."
---

# 바이브코딩을 위한 GitHub Actions 기초 (2/10): Workflow와 Job 구조 이해하기

이 글은 바이브코딩을 위한 GitHub Actions 기초 시리즈의 2번째 글입니다.

AI에게 CI 워크플로우를 만들어 달라고 하면 대부분 하나의 잡에 모든 것을 몰아 넣은 파일이 나옵니다. 린트, 테스트, 빌드, 배포가 전부 하나의 잡 안에 스텝으로 쭉 나열됩니다. 처음에는 단순해 보여서 좋습니다. 그런데 시간이 지나면서 린트 오류 하나 때문에 5분짜리 테스트를 기다려야 하고, 어디서 실패했는지 로그를 전부 뒤져야 하는 상황이 반복됩니다. 병렬로 돌릴 수 있는 검증들이 직렬로 묶여 있기 때문입니다.

Workflow, Job, Step의 계층 구조를 이해하면 이 문제가 해결됩니다. 린트는 30초 안에 피드백이 오고, 테스트는 2분 안에 오고, 배포는 둘 다 통과해야만 시작되는 구조를 만들 수 있습니다. AI가 만들어 준 파이프라인을 제대로 다듬으려면 이 설계 감각이 필요합니다.

> 잡을 어떻게 나누느냐가 CI 피드백 속도를 결정합니다. 모든 것을 한 잡에 넣으면 단순해 보여도, 실제로는 병렬 처리 가능성을 포기하는 선택입니다.

---

## 이 글에서 다룰 문제
- Workflow, Job, Step은 각각 어떤 역할을 맡을까요?
- 잡을 나누는 기준은 무엇이고, 언제 하나로 합쳐야 할까요?
- `needs`로 잡 사이에 순서를 만들면 어떤 효과가 있을까요?
- 매트릭스로 여러 환경을 동시에 테스트하면 비용이 어떻게 달라질까요?
- AI가 생성한 단일 잡 파이프라인을 어떻게 개선할 수 있을까요?

---

## 잡 분해가 왜 중요한가

바이브코딩 프로젝트에서 AI가 만들어 준 CI 파일을 그대로 쓰면 흔히 이런 구조가 됩니다.

```yaml
jobs:
  everything:
    runs-on: ubuntu-latest
    steps:
      - run: ruff check .       # 린트 (10초)
      - run: mypy src/          # 타입 검사 (30초)
      - run: pytest -q          # 테스트 (3분)
      - run: python -m build    # 빌드 (30초)
```

린트에서 오류가 나도 테스트가 끝날 때까지 기다려야 결과를 확인할 수 있습니다. 반대로 린트와 테스트를 분리하면 30초 안에 린트 피드백을 받고, 테스트도 병렬로 돌아갑니다.

### 핵심 용어 정리

| 용어 | 의미 | 설계 포인트 |
|------|------|------|
| 워크플로 | YAML 파일 하나에 담긴 자동화 단위 | 이벤트와 파이프라인의 경계를 정합니다 |
| 잡 | 워크플로 안의 실행 단위 | 기본값이 병렬 실행입니다 |
| 스텝 | 잡 안의 명령 또는 액션 호출 | 같은 잡 안에서 순서대로 실행됩니다 |
| `needs` | 잡 간 의존성 선언 | 실행 순서와 안전장치를 만듭니다 |
| `matrix` | 변수 조합으로 잡을 복제하는 기능 | 환경 조합을 넓히되 비용을 통제해야 합니다 |

---

## Before / After

**AI가 만든 단일 잡 파이프라인**

```yaml
jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: ruff check .
      - run: pytest -q
      - run: python -m build
```

**잡을 나눈 개선 버전**

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pip install ruff
      - run: ruff check .

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"
      - run: pip install -e ".[dev]"
      - run: pytest -q

  build:
    needs: [lint, test]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
```

lint와 test가 병렬로 실행되고, 둘 다 통과해야 build가 시작됩니다. 린트 실패는 30초 안에 피드백이 오고, 테스트는 같은 시간에 병렬로 돌아갑니다.

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| 모든 스텝을 한 잡에 몰아 넣음 | 병렬 처리 기회를 잃음 | 독립적인 검증은 잡으로 나눕니다 |
| `needs` 없이 의존성 가정 | 실행 순서가 보장되지 않음 | 의존 관계는 `needs`로 명시합니다 |
| 매트릭스를 과하게 넓힘 | 러너 비용이 기하급수로 늘어남 | 필수 조합만 선택합니다 |
| 잡을 너무 잘게 쪼갬 | 오케스트레이션 복잡도 증가 | 한 문장으로 설명 가능한 단위로 나눕니다 |
| 재실행 범위를 고려 안 함 | 배포 실패 시 전체를 다시 돌려야 함 | 배포 잡은 별도로 분리합니다 |

## AI 팁: 잡 분리 구조 요청 프롬프트

```
프롬프트 예시:
"GitHub Actions 워크플로우에서 lint, test, build를 별도 잡으로 분리해줘.
조건:
- lint와 test는 병렬 실행
- build는 lint와 test가 모두 성공해야 실행
- Python 3.11, 3.12 두 버전에서 test 실행 (matrix)
- 각 잡에 캐시 적용"
```

이렇게 요청하면 `needs`와 `matrix`가 포함된 구조를 받을 수 있습니다. 받은 후에는 매트릭스 크기가 비용 예산 안에 있는지 확인하세요.

## 운영 체크리스트
- [ ] 독립적으로 실행 가능한 검증은 잡으로 분리했는가?
- [ ] `needs`로 의존성이 명시되어 있는가?
- [ ] 매트릭스 크기가 합리적인가?
- [ ] 배포 잡은 검증 잡 이후에만 실행되는가?
- [ ] 각 잡을 한 문장으로 설명할 수 있는가?

## 처음 질문으로 돌아가기

- **잡을 나누는 기준은?**
  실패 원인이 다르거나, 실행 환경이 다르거나, 순서가 독립적인 작업은 잡으로 나눕니다. 반대로 항상 함께 실행되고 같은 상태가 필요한 작업은 같은 잡의 스텝으로 유지합니다.

- **`needs`는 왜 중요한가?**
  `needs` 없이는 잡 실행 순서가 보장되지 않습니다. "테스트 통과 후 배포"라는 규칙을 코드로 강제하려면 `needs`가 필수입니다.

- **AI가 만든 단일 잡을 어떻게 개선하나?**
  먼저 스텝 목록을 보고 독립적으로 실행 가능한 그룹을 찾습니다. 린트와 타입 체크, 테스트, 빌드는 보통 분리 가능합니다. 그런 다음 의존 관계에 따라 `needs`를 연결합니다.

## 정리

워크플로우 안에서 잡을 어떻게 설계하느냐가 CI 피드백 속도와 비용을 함께 결정합니다. 바이브코딩으로 빠르게 만든 코드를 AI에게 CI 파일로 만들어 달라고 했다면, 받은 파일을 그대로 쓰기보다 잡 분리와 `needs` 연결로 다듬어야 합니다. 다음 글에서는 이 잡들이 언제 실행되는지, 트리거 설계를 다룹니다.

## 참고 자료
### 공식 문서
- [Using jobs in a workflow](https://docs.github.com/actions/using-jobs/using-jobs-in-a-workflow)
- [Using a matrix for your jobs](https://docs.github.com/actions/using-jobs/using-a-matrix-for-your-jobs)
### 관련 시리즈
- [DevOps 101](../../devops-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 GitHub Actions 기초 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- **바이브코딩을 위한 GitHub Actions 기초 (2/10): Workflow와 Job 구조 이해하기 (현재 글)**
- [바이브코딩을 위한 GitHub Actions 기초 (3/10): 트리거로 실행 시점 제어하기](./03-triggers.md)
- [바이브코딩을 위한 GitHub Actions 기초 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (5/10): Lint와 Type Check 자동화](./05-lint-and-typecheck.md)
- [바이브코딩을 위한 GitHub Actions 기초 (6/10): 빌드 아티팩트 관리](./06-build-artifact.md)
- [바이브코딩을 위한 GitHub Actions 기초 (7/10): Docker 이미지 자동 빌드](./07-docker-build.md)
- [바이브코딩을 위한 GitHub Actions 기초 (8/10): 배포 자동화](./08-deploy-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (9/10): Secret 안전하게 관리하기](./09-secret-management.md)
- [바이브코딩을 위한 GitHub Actions 기초 (10/10): 실전 CI/CD 파이프라인 조립](./10-real-world-cicd-pipeline.md)
<!-- toc:end -->
Tags: 바이브코딩, GitHubActions, Workflow, Job, CICD
