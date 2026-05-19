---
series: github-actions-101
episode: 4
title: Python 테스트 자동화
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - GitHubActions
  - Python
  - Pytest
  - Testing
  - CICD
seo_description: pytest, coverage, matrix 기반의 Python 테스트 자동화를 실무 흐름으로 정리합니다.
last_reviewed: '2026-05-15'
---

# Python 테스트 자동화

로컬에서만 `pytest`를 돌리는 팀은 결국 같은 문제를 반복해서 만납니다. 내 환경에서는 통과했는데 CI에서는 실패하고, 누군가는 테스트를 건너뛰고, 누군가는 다른 Python 버전에서만 깨지는 문제를 머지 뒤에 발견합니다. 테스트가 존재하는 것과 자동으로 실행되는 것은 전혀 다른 단계입니다.

이 글은 GitHub Actions 101 시리즈의 4번째 글입니다. 여기서는 GitHub Actions에서 Python 테스트를 자동화하는 기본 흐름을 정리하고, 캐시, 리포트, 커버리지, 매트릭스까지 어떤 기준으로 붙여야 하는지 설명하겠습니다.

## 이 글에서 다룰 문제

> 테스트는 작성하는 순간보다 자동으로 실행되는 순간부터 팀의 안전장치가 됩니다. PR마다 같은 환경에서 같은 명령이 돌아가야 테스트 결과를 신뢰할 수 있습니다.

- `setup-python`과 pip 캐시는 왜 함께 다뤄야 할까요?
- `pytest` 결과를 PR 체크와 리포트로 드러내려면 무엇이 필요할까요?
- 커버리지는 왜 숫자 자체보다 추세와 기준이 중요할까요?
- 여러 Python 버전은 어떤 경우에 매트릭스로 돌려야 할까요?
- 느린 테스트와 흔들리는 테스트는 어떻게 구분해야 할까요?

## 왜 중요한가

수동 테스트는 꼭 빠집니다. 일정이 급할수록 더 그렇습니다. 반대로 자동 테스트는 사람이 바쁘더라도 같은 절차를 반복합니다. 저는 CI의 핵심 가치를 “좋은 습관을 강제하는 것”이라고 생각합니다. 테스트 자동화가 붙는 순간, 품질 기준은 개인의 기억에서 저장소 규칙으로 옮겨 갑니다.

또 하나 중요한 점은 속도입니다. 테스트가 너무 느리면 팀은 CI를 덜 신뢰합니다. 느린 CI는 결국 건너뛰는 CI가 됩니다. 그래서 테스트 자동화는 많이 붙이는 것보다 빠르고 일관되게 붙이는 편이 더 중요합니다.

## 한눈에 보는 테스트 흐름

![PR이 열리면 Python 환경 준비, 의존성 설치, pytest, coverage 순서로 이어지는 테스트 흐름](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/04/04-01-diagram.ko.png)

*PR이 열리면 Python 환경 준비, 의존성 설치, pytest, coverage 순서로 이어지는 테스트 흐름*

이 흐름은 단순하지만 운영 감각을 잘 보여 줍니다. 실행 환경을 맞추고, 의존성을 설치하고, 테스트를 돌리고, 결과를 남깁니다. 어느 단계에서 시간이 오래 걸리는지 보는 것만으로도 개선 포인트가 드러납니다.

## 먼저 핵심 용어를 정리하겠습니다

| 용어 | 뜻 | 실무 포인트 |
| --- | --- | --- |
| `setup-python` | 러너에 Python을 설치하는 액션 | 버전 고정과 캐시 설정의 출발점입니다 |
| pip 캐시 | 의존성 설치 결과를 재사용하는 기능 | 설치 시간을 줄여 피드백을 빠르게 만듭니다 |
| `pytest` | Python 테스트 러너 | 가장 흔한 표준 조합입니다 |
| `junitxml` | 테스트 결과를 XML로 남기는 형식 | PR 리포트, 아티팩트와 연동하기 좋습니다 |
| coverage | 테스트가 닿은 코드 범위를 측정 | 목표 숫자보다 변화 추이를 보는 편이 중요합니다 |
| Codecov | 커버리지 리포팅 서비스 | PR에서 변화량을 보여 주는 데 유용합니다 |

## 자동화 전과 후를 비교해 보겠습니다

자동화가 없으면 `pytest`는 로컬에서만 돌아갑니다. 이 구조에서는 누가 어느 버전의 Python을 쓰는지, 가상환경이 깨끗한지, 테스트가 실제로 최신 코드 기준인지 확신하기 어렵습니다. “머지하고 나서 main이 깨졌다”는 사고가 자주 나는 이유도 여기에 있습니다.

자동화가 붙으면 PR마다 같은 절차가 실행됩니다. Python 3.10, 3.11, 3.12를 모두 통과해야 머지할 수 있게 만들 수도 있습니다. 이 순간부터 테스트는 개인의 습관이 아니라 저장소의 규칙이 됩니다.

## 테스트 자동화를 5단계로 구성해 보겠습니다

### 1단계 — Python과 캐시 설정하기

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.11"
    cache: "pip"
- run: pip install -r requirements.txt
```

이 설정의 핵심은 `cache: "pip"`입니다. 의존성 설치 시간을 매번 처음부터 내지 않게 해 주므로, 작은 한 줄이지만 체감 성능에 큰 차이를 만듭니다.

### 2단계 — 테스트 결과를 리포트로 남기기

```yaml
- run: pytest -q --junitxml=report.xml
- uses: actions/upload-artifact@v7
  if: always()
  with:
    name: pytest-report
    path: report.xml
```

테스트는 통과 여부만 보는 것으로 끝나지 않습니다. 실패했을 때 어떤 테스트가 어떻게 깨졌는지 남겨야 이후 분석이 쉬워집니다. `if: always()`가 중요한 이유도 여기에 있습니다.

### 3단계 — 커버리지 측정하기

```yaml
- run: pytest --cov=src --cov-report=xml
- uses: codecov/codecov-action@v4
  with:
    files: coverage.xml
```

커버리지는 숫자를 모으는 게임이 아닙니다. 어떤 PR이 중요한 경로를 빠뜨렸는지, 시간이 지나며 품질 기준이 낮아지고 있는지 읽기 위한 신호에 가깝습니다.

### 4단계 — 여러 Python 버전에서 검증하기

```yaml
strategy:
  matrix:
    python: ["3.10", "3.11", "3.12"]
steps:
  - uses: actions/setup-python@v6
    with:
      python-version: ${{ matrix.python }}
```

라이브러리나 SDK처럼 호환성이 중요한 프로젝트라면 매트릭스가 큰 가치가 있습니다. 반대로 사내 서비스처럼 실제 운영 버전이 하나로 고정돼 있다면, 매트릭스는 꼭 필요한 범위로만 두는 편이 좋습니다.

### 5단계 — 실패 시 로그 남기기

```yaml
- name: dump logs on failure
  if: failure()
  run: |
    cat pytest.log || true
```

테스트가 흔들릴 때 가장 아쉬운 것은 재현 재료가 없는 상황입니다. 실패 시점의 로그를 남기면 다시 돌렸을 때 사라지는 문제도 어느 정도 추적할 수 있습니다.

## 이 코드에서 먼저 봐야 할 점

- `cache: "pip"` 한 줄이 설치 시간을 크게 줄일 수 있습니다.
- `junitxml`은 사람이 읽는 로그와 별개로 도구가 읽을 결과물을 만듭니다.
- `if: always()` 덕분에 실패한 실행에서도 아티팩트를 남길 수 있습니다.

즉, 테스트 자동화는 “테스트를 돌린다”에서 끝나지 않습니다. 결과를 남기고, 실패를 읽을 수 있게 만들고, 반복 실행 비용을 낮추는 것까지 포함해야 실무에서 오래 갑니다.

## 자주 하는 실수 다섯 가지

1. pip 캐시 없이 매번 전체 의존성을 다시 설치합니다.
2. CI에서 `pytest -v`를 남발해 로그만 과도하게 키웁니다.
3. 외부 네트워크에 의존하는 테스트를 그대로 넣어 흔들리는 CI를 만듭니다.
4. `junitxml` 없이 통과 여부만 남깁니다.
5. 커버리지를 목표 없이 측정해 숫자만 쌓습니다.

특히 세 번째는 운영에서 자주 문제를 만듭니다. 네트워크 상태, 외부 서비스 레이트 리밋, 테스트 데이터 오염이 겹치면 CI 신뢰가 빠르게 무너집니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 빠른 단위 테스트와 느린 통합 테스트를 분리합니다. PR에서는 빠른 테스트만 돌리고, 야간이나 main push에서는 더 무거운 검증을 붙이는 방식이 흔합니다. 또 흔들리는 테스트는 그냥 두지 않고 격리하거나 재실행 정책을 둡니다.

커버리지도 같은 기준으로 봅니다. 100%를 목표로 세우기보다, 핵심 경로를 빠뜨리지 않았는지, 중요한 모듈이 지속적으로 빈약해지지 않는지 보는 편이 훨씬 실용적입니다.

## 체크리스트

- [ ] pip 캐시가 켜져 있다.
- [ ] `junit XML` 결과를 업로드한다.
- [ ] 커버리지를 측정한다.
- [ ] 매트릭스 범위가 실제 필요에 맞는다.

## 연습 문제

1. 현재 프로젝트에 `pytest` 워크플로우를 추가해 보세요.
2. Python 3.11과 3.12 매트릭스를 붙여 보세요.
3. 커버리지가 80% 아래로 떨어지면 PR을 실패시키도록 바꿔 보세요.

## 정리

Python 테스트 자동화의 핵심은 같은 환경에서 같은 명령을 반복 실행하게 만드는 것입니다. 캐시로 피드백 시간을 줄이고, 리포트와 커버리지로 결과를 남기고, 필요할 때만 매트릭스로 검증 범위를 넓히면 됩니다.

다음 글에서는 lint와 type check를 다룹니다. 테스트가 동작을 검증한다면, 그다음 단계는 스타일과 정적 타입 규칙을 자동으로 막는 품질 게이트를 세우는 일입니다.

<!-- toc:begin -->
- [GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [Workflow와 Job](./02-workflow-and-job.md)
- [Trigger 이해하기](./03-triggers.md)
- **Python 테스트 자동화 (현재 글)**
- Lint와 Type Check (예정)
- 빌드 아티팩트 (예정)
- Docker 빌드 (예정)
- 배포 자동화 (예정)
- Secret 관리 (예정)
- 실전 CI/CD 파이프라인 (예정)
<!-- toc:end -->

## 참고 자료

- [actions/setup-python](https://github.com/actions/setup-python)
- [pytest documentation](https://docs.pytest.org/)
- [coverage.py](https://coverage.readthedocs.io/)
- [Codecov GitHub Action](https://github.com/codecov/codecov-action)

Tags: GitHubActions, Python, Pytest, Testing, CICD
