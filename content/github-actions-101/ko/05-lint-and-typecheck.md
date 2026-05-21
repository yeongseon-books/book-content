---
series: github-actions-101
episode: 5
title: "GitHub Actions 101 (5/10): Lint와 Type Check"
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
  - Lint
  - Ruff
  - Mypy
  - QualityGate
seo_description: ruff, mypy, pre-commit으로 코드 품질 게이트를 자동화하는 방법을 정리합니다.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (5/10): Lint와 Type Check

코드 리뷰가 늘 비슷한 지적에서 시작된다면 팀의 시간이 아깝게 쓰이고 있다는 뜻입니다. import 정렬, 줄 길이, 포매팅, 명백한 타입 오류까지 사람이 반복해서 잡고 있다면 리뷰어는 더 중요한 설계와 위험 신호에 집중하기 어렵습니다. 이런 일은 가능한 한 기계에게 넘기는 편이 맞습니다.

이 글은 GitHub Actions 101 시리즈의 5번째 글입니다. 여기서는 Ruff와 Mypy, pre-commit을 이용해 코드 품질 게이트를 만들고, PR 리뷰가 스타일 교정이 아니라 로직 검토에 집중되도록 하는 방법을 설명하겠습니다.

## 먼저 던지는 질문

- Ruff는 왜 여러 도구를 하나로 줄이는 데 유용할까요?
- Mypy는 어느 시점부터 엄격 모드로 가져가는 편이 좋을까요?
- pre-commit은 왜 CI와 짝을 이뤄야 할까요?

## 큰 그림

![GitHub Actions 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/05/05-01-diagram.ko.png)

*GitHub Actions 101 5장 흐름 개요*

## 왜 중요한가

린트와 타입 검사는 리뷰어가 가장 먼저 발견하는 항목입니다. 그런데 이 검사는 대부분 기계가 훨씬 더 빠르고 일관되게 할 수 있습니다. 품질 게이트를 자동화하면 리뷰어는 아키텍처, 예외 흐름, 성능, 운영 영향처럼 더 비싼 판단에 시간을 쓸 수 있습니다.

또 하나 중요한 점은 팀 기준의 통일입니다. 로컬에서는 통과했는데 CI에서는 실패하는 상황이 반복되면 개발자는 자동화를 귀찮은 장벽으로 느낍니다. 같은 명령을 로컬과 CI에서 똑같이 실행하게 만드는 것이 오래 가는 구조입니다.

## 한눈에 보는 품질 게이트

이 구조에서 핵심은 분명합니다. 코드가 들어오면 먼저 기계가 스타일과 정적 타입을 확인하고, 그 결과가 CI 게이트로 이어집니다. 사람의 리뷰는 그 다음입니다.

## 핵심 용어를 먼저 정리하겠습니다

| 용어 | 뜻 | 실무 포인트 |
| --- | --- | --- |
| 린터 | 스타일과 패턴 위반을 잡는 도구 | 반복적인 리뷰 지적을 줄여 줍니다 |
| 포매터 | 코드를 자동으로 정렬하고 맞추는 도구 | 팀 내 스타일 논쟁을 줄입니다 |
| 타입 체커 | 정적 타입 오류를 미리 찾는 도구 | 실행 전 경계 오류를 줄이는 데 유용합니다 |
| pre-commit | 커밋 전에 실행하는 훅 | CI에 가기 전 빠른 피드백을 줍니다 |
| 품질 게이트 | 실패 시 머지를 막는 규칙 | 기준을 문서가 아니라 동작으로 만듭니다 |

Ruff가 특히 매력적인 이유는 여러 도구를 단순화해 준다는 점입니다. flake8, isort, black을 따로 관리하던 복잡도를 줄여 주면 팀 전체 유지비가 확실히 낮아집니다.

## 자동화 전과 후를 비교해 보겠습니다

품질 게이트가 없으면 리뷰어는 같은 피드백을 반복합니다. import 순서, 사용하지 않는 변수, 줄 길이, 타입 누락 같은 항목이 매 PR마다 다시 등장합니다. 이 과정은 지치기 쉽고, 팀이 커질수록 기준이 사람마다 흔들립니다.

반대로 PR에 `Lint passed`, `Type-check passed`가 자동으로 붙으면 리뷰 대화의 초점이 달라집니다. 이제 관심사는 “형식이 맞는가”보다 “이 설계가 맞는가”, “이 예외 처리가 충분한가”로 옮겨 갑니다. 저는 품질 게이트의 진짜 가치를 여기에 둡니다.

## 품질 게이트를 5단계로 구성해 보겠습니다

### 1단계 — Ruff로 기본 규칙 만들기

```yaml
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
  with:
    python-version: "3.11"
- run: pip install ruff
- run: ruff check .
- run: ruff format --check .
```

이 구성만으로도 상당수 스타일 문제를 자동으로 걸러낼 수 있습니다. 포매팅까지 검사하면 “이건 취향 아닌가요?”라는 논쟁도 크게 줄어듭니다.

### 2단계 — Mypy 추가하기

```yaml
- run: pip install mypy
- run: mypy src/
```

정적 타입 검사는 실행 전에 드러낼 수 있는 오류를 앞당겨 보여 줍니다. 특히 함수 경계와 데이터 구조가 많아질수록 효과가 커집니다.

### 3단계 — 설정을 한곳에 모으기

```toml
[tool.ruff]
line-length = 100
[tool.ruff.lint]
select = ["E", "F", "I", "N", "UP"]

[tool.mypy]
strict = true
```

설정 파일이 여러 곳에 흩어지면 어느 값이 기준인지 불분명해집니다. 저는 `pyproject.toml` 한곳을 중심으로 맞추는 방식을 선호합니다.

### 4단계 — pre-commit으로 로컬과 CI를 맞추기

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.0
    hooks: [{id: ruff}, {id: ruff-format}]
```

로컬에서 먼저 잡히는 오류는 CI 시간도 아껴 줍니다. 팀원이 커밋 전에 같은 규칙을 돌리면 PR에서 보는 실패 수도 자연스럽게 줄어듭니다.

### 5단계 — 변경분만 검사하기

```yaml
- run: |
    git fetch origin ${{ github.base_ref }}
    ruff check $(git diff --name-only origin/${{ github.base_ref }} | grep '\.py$') || true
```

전체 저장소를 한 번에 엄격하게 바꾸기 어려운 레거시 프로젝트에서는 이 방식이 유용할 수 있습니다. 다만 임시 전략인지 장기 전략인지 팀 안에서 분명히 정하는 편이 좋습니다.

## 이 코드에서 먼저 봐야 할 점

- Ruff 하나로 여러 품질 도구를 단순화할 수 있습니다.
- Mypy는 가능하면 초기에 엄격하게 가져가는 편이 전환 비용이 낮습니다.
- pre-commit은 CI 전에 문제를 줄여 주는 빠른 방파제 역할을 합니다.

도구 수를 늘리는 일은 본질이 아닙니다. 기준을 선명하게 만드는 편이 훨씬 중요합니다. 기준이 선명하면 실패도 덜 억울하고 수정도 더 빨라집니다.

## 자주 하는 실수 다섯 가지

1. CI에서만 돌리고 로컬에는 같은 도구를 설치하지 않습니다.
2. 규칙을 자꾸 완화하다가 사실상 의미 없는 수준으로 만듭니다.
3. Mypy를 일부 모듈에만 어정쩡하게 적용합니다.
4. `ruff format` 결과를 PR마다 자동 커밋하게 만들어 충돌을 늘립니다.
5. 설정 파일을 여러 곳에 흩어 놓습니다.

특히 두 번째 실수는 흔합니다. 경고를 줄이는 대신 기준을 낮추면 단기적으로는 편하지만, 장기적으로는 품질 게이트 자체를 신뢰하지 않게 됩니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 Ruff, Mypy, pre-commit 조합을 표준 템플릿으로 묶습니다. 저장소마다 제각각 다른 규칙을 두기보다, 템플릿 저장소나 공통 설정으로 팀의 기준을 일관되게 만드는 편이 유지보수에 유리합니다.

또한 자동 수정과 자동 커밋을 구분해서 봐야 합니다. 자동 수정 자체는 좋지만, CI가 PR마다 코드를 다시 커밋하기 시작하면 리뷰와 충돌 관리가 오히려 복잡해질 수 있습니다. 저는 보통 로컬 자동 수정, CI 검증 분리를 선호합니다.

## 체크리스트

- [ ] `ruff check`와 `ruff format --check`가 CI에서 돈다.
- [ ] `mypy strict` 기준이 켜져 있다.
- [ ] 팀이 pre-commit을 설치해 사용한다.
- [ ] 설정이 `pyproject.toml`에 모여 있다.

## 연습 문제

1. Ruff와 Mypy를 함께 실행하는 워크플로우를 추가해 보세요.
2. 세 개 이상의 훅으로 pre-commit 구성을 만들어 보세요.
3. strict mypy를 켠 뒤 나타나는 오류를 범주별로 분류해 보세요.

## 정리

린트와 타입 검사는 사람이 반복해서 볼 가치가 낮은 오류를 미리 걷어 내는 게이트입니다. Ruff로 스타일과 포맷을 통일하고, Mypy로 타입 경계를 점검하고, pre-commit으로 로컬과 CI의 기준을 맞추면 리뷰의 밀도가 높아집니다.

다음 글에서는 빌드 아티팩트를 다룹니다. 코드 품질을 검증했다면, 이제 그 결과물인 빌드 산출물을 어떻게 저장하고 다음 단계로 넘길지 살펴볼 차례입니다.


## 워크플로 설계를 코드로 구체화하기

워크플로우 품질은 "한 번 돌아간다"가 아니라 "변경이 누적돼도 의도를 유지한다"로 판단해야 합니다. 아래 예시는 테스트, 린트, 빌드를 분리해 실패 지점을 빠르게 찾는 구성입니다.

```yaml
name: ci
on:
  pull_request:
  push:
    branches: [main]

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

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pip install ruff
      - run: ruff check .

  build:
    runs-on: ubuntu-latest
    needs: [test, lint]
    steps:
      - uses: actions/checkout@v6
      - run: docker build -t app:${{ github.sha }} .
```

`needs`를 통해 의존 관계를 명시하면 "테스트 실패인데 빌드는 왜 돌았는가" 같은 혼선을 줄일 수 있습니다. 또한 잡을 분리하면 병렬 실행이 가능해 전체 피드백 시간이 짧아집니다.

## Job Matrix로 중복을 줄이기

동일한 작업을 여러 런타임에서 반복해야 한다면 matrix가 가장 실용적입니다. 아래 구성은 Python 버전과 운영체제를 조합해 호환성을 검증합니다.

```yaml
jobs:
  test-matrix:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest]
        python-version: ["3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -r requirements.txt
      - run: pytest -q
```

`fail-fast: false`를 켜면 한 조합이 실패해도 나머지 조합 결과를 끝까지 수집할 수 있습니다. 라이브러리 호환성 이슈를 찾는 단계에서는 이 설정이 원인 파악 속도를 높입니다.

## Secret 처리 원칙

비밀값은 YAML 본문에 직접 넣지 않고 GitHub Secrets나 OIDC 기반 임시 자격 증명을 사용해야 합니다. 고정 토큰을 코드에 넣으면 회전, 감사, 권한 축소가 모두 어려워집니다.

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    permissions:
      id-token: write
      contents: read
    steps:
      - uses: actions/checkout@v6
      - name: Login to cloud with OIDC
        run: ./scripts/oidc-login.sh
      - name: Deploy
        env:
          API_BASE_URL: ${{ secrets.API_BASE_URL }}
        run: ./scripts/deploy.sh
```

실무에서는 다음 기준을 함께 둡니다.

- secret 이름은 목적 중심으로 명명해 누가 봐도 용도를 파악할 수 있게 합니다.
- PR from fork에서는 secret이 기본적으로 주입되지 않으므로, 배포 잡을 분리하거나 조건문으로 차단합니다.
- 로그에 비밀값이 노출되지 않도록 `set -x` 사용 구간을 제한하고, 민감 출력은 마스킹합니다.
- 회전 주기를 문서화하고, 사용하지 않는 secret은 즉시 폐기합니다.

## 운영 안정성을 높이는 추가 패턴

- `concurrency`를 사용해 같은 브랜치의 중복 배포를 자동 취소하면 롤백 리스크를 줄일 수 있습니다.
- 캐시 키는 잠금 파일(`poetry.lock`, `requirements.txt`) 해시와 연결해 오염된 캐시 재사용을 막습니다.
- 배포 잡은 `environment` 보호 규칙과 reviewer 승인을 함께 걸어 사고 범위를 줄입니다.
- 실패 알림은 채널 하나에 몰지 말고, 서비스 소유 팀 라우팅 기준으로 분리해야 대응 시간이 짧아집니다.

이 구조를 먼저 잡아 두면 워크플로 파일이 길어져도 책임 경계가 무너지지 않고, CI/CD 품질을 지속적으로 개선하기 쉬워집니다.


## 운영 체크포인트 보강

워크플로를 길게 쓰는 것보다 더 중요한 것은 실패 원인을 빠르게 고립하는 구조입니다. 테스트 잡에서는 의존성 설치 시간을 측정하고, 배포 잡에서는 릴리스 노트와 커밋 SHA를 함께 남겨 추적성을 확보해야 합니다. 또한 `if: github.event_name == "pull_request"` 같은 조건식을 사용해 PR 검증과 main 배포를 분리하면 권한 오남용과 불필요한 실행 시간을 동시에 줄일 수 있습니다.

```yaml
- name: Record build metadata
  run: |
    echo "sha=${GITHUB_SHA}" >> build-info.txt
    echo "ref=${GITHUB_REF}" >> build-info.txt
```

메타데이터 파일을 아티팩트로 보존해 두면 장애 회고에서 "어떤 실행 결과가 어느 커밋과 연결되는가"를 빠르게 확인할 수 있습니다.


## 실패 분석 루틴

테스트 자동화와 정적 검사는 "돌린다"보다 "실패를 재현한다"가 핵심입니다. 실패한 런에서는 로그 일부만 복사하지 말고, 실행한 Python 버전, 의존성 잠금 파일 해시, 실패 테스트 식별자(`-k`)를 함께 남겨야 다음 사람이 같은 조건으로 다시 실행할 수 있습니다. CI에서 실패한 테스트를 로컬에서 재현할 수 있어야 원인 분리가 빨라지고, flaky 테스트와 실제 회귀를 구분할 수 있습니다.

```bash
pytest -q -k "failing_test_name" --maxfail=1
python -V
pip freeze | sha256sum
```

이 정보를 PR 코멘트 템플릿에 포함시키면 리뷰 과정에서 추측성 토론이 줄고, 수정 범위를 더 정확히 결정할 수 있습니다.

## 처음 질문으로 돌아가기

- **Ruff는 왜 여러 도구를 하나로 줄이는 데 유용할까요?**
  - 본문의 기준은 Lint와 Type Check를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Mypy는 어느 시점부터 엄격 모드로 가져가는 편이 좋을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **pre-commit은 왜 CI와 짝을 이뤄야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [GitHub Actions 101 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflow와 Job](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Trigger 이해하기](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- **Lint와 Type Check (현재 글)**
- 빌드 아티팩트 (예정)
- Docker 빌드 (예정)
- 배포 자동화 (예정)
- Secret 관리 (예정)
- 실전 CI/CD 파이프라인 (예정)

<!-- toc:end -->

## 참고 자료

- [Ruff documentation](https://docs.astral.sh/ruff/)
- [Mypy documentation](https://mypy.readthedocs.io/)
- [pre-commit](https://pre-commit.com/)
- [astral-sh/ruff-pre-commit](https://github.com/astral-sh/ruff-pre-commit)

Tags: GitHubActions, Lint, Ruff, Mypy, QualityGate
