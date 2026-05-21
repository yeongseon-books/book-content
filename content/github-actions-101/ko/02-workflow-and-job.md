---
series: github-actions-101
episode: 2
title: "GitHub Actions 101 (2/10): Workflow와 Job"
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
  - Workflow
  - Job
  - Matrix
  - CICD
seo_description: Workflow, Job, Step의 관계와 의존성 설계를 실무 흐름으로 정리합니다.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (2/10): Workflow와 Job

GitHub Actions를 조금만 써 보면 금방 이런 고민이 생깁니다. “테스트와 린트를 같이 돌려도 될까?”, “배포는 테스트가 끝난 뒤에만 돌게 하려면 어떻게 써야 하지?”, “한 파일 안에 다 넣으면 되나, 잡을 나눠야 하나?” 이 질문들은 문법보다 구조 설계와 더 가깝습니다.

이 글은 GitHub Actions 101 시리즈의 2번째 글입니다. 여기서는 워크플로, 잡, 스텝이 어떻게 계층을 이루는지부터 시작해, 병렬성과 의존성을 어떤 기준으로 설계해야 하는지 정리해 보겠습니다.


![GitHub Actions 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/02/02-01-diagram.ko.png)
*GitHub Actions 101 2장 흐름 개요*

## 먼저 던지는 질문

- Workflow, Job, Step은 각각 무엇을 담당할까요?
- `needs`는 왜 단순한 옵션이 아니라 파이프라인 설계 도구일까요?
- `matrix`는 언제 유용하고 언제 비용 폭탄이 될까요?

## 왜 중요한가

모든 작업을 한 잡에 넣으면 이해는 쉬워 보여도 피드백이 느려집니다. 반대로 아무 기준 없이 잘게 쪼개면 의존성이 흐려지고, 어떤 순서로 무엇이 실행되는지 읽기 어려워집니다. 결국 좋은 CI는 “적당히 병렬적이고, 필요한 곳만 순차적인 구조”를 만들어야 합니다.

실무에서는 이 설계가 곧 개발자 경험으로 이어집니다. 린트 결과는 30초 안에 받고, 테스트는 2분 안에 받고, 배포는 그 이후에만 시작되게 만들 수 있다면 팀의 리듬이 달라집니다. 저는 Job 그래프를 잘 그리는 능력이 GitHub Actions 실력을 크게 갈라놓는다고 봅니다.

## 한눈에 보는 잡 그래프

이 그림은 단순하지만 핵심을 잘 보여 줍니다. lint와 test는 서로 독립이므로 병렬로 돌릴 수 있고, build는 그 둘이 성공한 뒤에만 시작하면 됩니다. deploy는 build가 끝난 뒤에만 허용해야 하므로 마지막에 놓입니다.

## 먼저 용어를 정확히 구분하겠습니다

| 용어 | 의미 | 설계 포인트 |
| --- | --- | --- |
| 워크플로 | YAML 파일 하나에 담긴 자동화 단위 | 어떤 이벤트에서 어떤 파이프라인이 시작되는지 정합니다 |
| 잡 | 워크플로 안의 실행 단위 | 기본값이 병렬 실행이라는 점이 중요합니다 |
| 스텝 | 잡 안의 명령 또는 액션 호출 | 같은 잡 안에서는 순서대로 실행됩니다 |
| `needs` | 잡 간 의존성 선언 | 실행 순서를 명시해 그래프를 만듭니다 |
| `matrix` | 변수 조합으로 잡을 복제하는 기능 | 환경 조합을 넓히되 비용을 통제해야 합니다 |
| `outputs` | 앞선 잡이 다음 잡으로 넘기는 값 | 문자열 위주로 단순하게 유지하는 편이 좋습니다 |

여기서 먼저 잡아야 할 감각은 이 구분입니다. 스텝은 한 잡 안에서 직렬 실행되고, 잡은 기본적으로 병렬 실행됩니다. 따라서 “같이 돌릴 수 있는가?”는 잡 경계를 묻는 질문이고, “반드시 이 다음에 돌아야 하는가?”는 `needs`를 묻는 질문입니다.

## 자동화 전과 후를 비교해 보겠습니다

모든 일을 한 잡에 넣은 파이프라인은 시작은 편합니다. 파일 수도 적고, 흐름도 한눈에 들어옵니다. 하지만 린트 한 줄 때문에 테스트와 빌드가 끝날 때까지 기다려야 하고, 중간 어느 지점에서 실패했는지 읽기도 불편합니다.

반대로 lint, test, build를 나누고, build에만 `needs: [lint, test]`를 걸면 피드백 시간이 달라집니다. 실패도 더 빨리 드러나고, 성공했을 때만 다음 단계로 넘어가는 구조가 자연스럽게 잡힙니다. 잡 분해는 단순한 YAML 꾸미기가 아니라 피드백 시간을 설계하는 일입니다.

## 잡 그래프를 5단계로 만들어 보겠습니다

### 1단계 — 잡을 나누기

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: ruff check .

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pytest -q
```

먼저 독립적으로 돌릴 수 있는 일을 나눕니다. 린트와 테스트는 대부분 서로 결과를 공유하지 않으므로 좋은 병렬 후보입니다.

### 2단계 — `needs`로 순서 만들기

```yaml
  build:
    runs-on: ubuntu-latest
    needs: [lint, test]
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
```

`needs`는 “이 잡이 어떤 성공을 전제로 시작되는가”를 드러냅니다. 문법은 짧지만, 사실상 파이프라인의 안전장치입니다.

### 3단계 — `matrix`로 환경을 늘리기

```yaml
  test:
    strategy:
      matrix:
        python: ["3.10", "3.11", "3.12"]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python }}
      - run: pytest -q
```

매트릭스는 같은 잡을 여러 환경에 복제합니다. 다만 Python 버전 세 개에 운영체제 두 개를 곱하는 순간 여섯 개 실행으로 늘어나므로, 필요 이상으로 크게 잡으면 곧 비용과 대기 시간이 커집니다.

### 4단계 — `outputs`로 값 넘기기

```yaml
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.v.outputs.version }}
    steps:
      - id: v
        run: echo "version=1.2.3" >> "$GITHUB_OUTPUT"

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - run: echo "deploy ${{ needs.build.outputs.version }}"
```

잡 사이 값 전달은 꼭 필요할 때만 작게 쓰는 편이 좋습니다. 문자열 한두 개는 깔끔하지만, 복잡한 객체를 억지로 넘기기 시작하면 파이프라인이 빠르게 지저분해집니다.

### 5단계 — 실패 정책 정하기

```yaml
  flaky:
    continue-on-error: true
    runs-on: ubuntu-latest
    steps:
      - run: pytest tests/flaky.py
```

이 옵션은 실패를 무시하는 도구가 아니라, 어떤 실패를 경고 수준으로 다룰지 결정하는 정책입니다. 저는 이 값을 남용하기보다, 꼭 필요한 경우에만 이유를 문서화해서 쓰는 편을 권합니다.

## 이 코드에서 먼저 봐야 할 점

- `needs`는 잡 사이에 방향을 가진 그래프를 만듭니다.
- `matrix`는 편리하지만 조합이 커질수록 비용이 기하급수적으로 늘어납니다.
- `outputs`는 단순한 문자열 전달에 가장 잘 맞습니다.

즉, 잡 설계는 “얼마나 많이 나눌까”보다 “무엇을 독립 실행 가능한 단위로 볼까”를 묻는 작업입니다. 이 기준이 흔들리면 YAML만 길어지고 읽기는 더 어려워집니다.

## 자주 하는 실수 다섯 가지

1. 모든 스텝을 한 잡에 몰아넣어 병렬성을 잃습니다.
2. `needs`를 생략해 의존성을 암묵적으로 만듭니다.
3. 매트릭스를 지나치게 크게 잡아 실행 비용을 키웁니다.
4. `outputs`에 복잡한 구조를 넣어 직렬화 문제를 만듭니다.
5. `if:` 조건 없이 불필요한 잡을 매번 실행합니다.

특히 세 번째와 다섯 번째는 비용과 직접 연결됩니다. 잡 그래프를 잘못 그리면 느리기만 한 것이 아니라, 러너 사용량도 빠르게 불어납니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 PR에서 빠른 lint와 test만 돌리고, main push에서 더 넓은 matrix와 build를 실행하는 식으로 두 층 구조를 만듭니다. 이는 GitHub Actions 문법만 아는 수준을 넘어, 피드백과 비용을 구분해서 설계한다는 이야기입니다.

또한 `needs`는 기술적 의존성만이 아니라 비즈니스 의도를 표현하는 도구이기도 합니다. 예를 들어 “보안 검사 통과 전에는 배포 금지”라는 규칙도 결국 잡 그래프에 녹여 내야 지속됩니다.

## 체크리스트

- [ ] lint, test, build가 분리돼 있다.
- [ ] `needs`로 의존성이 명시돼 있다.
- [ ] `matrix` 크기가 비용을 고려해 정해졌다.
- [ ] `outputs`는 단순한 문자열 위주로 쓴다.

## 연습 문제

1. lint, test, build로 이루어진 3개 잡 그래프를 직접 만들어 보세요.
2. Python 3.11과 3.12를 테스트하는 매트릭스를 추가해 보세요.
3. build 잡이 만든 버전 문자열을 deploy 잡에서 읽어 보세요.

## 정리

워크플로는 자동화의 바깥 틀이고, 잡 그래프가 파이프라인의 실제 뼈대입니다. 무엇을 병렬로 돌릴지, 무엇에 순서를 걸지, 어떤 값만 다음 단계로 넘길지 정하는 일이 곧 좋은 CI 설계입니다.

다음 글에서는 이 그래프가 언제 실행돼야 하는지, 즉 트리거 설계를 다룹니다. 좋은 잡 구조도 적절한 시점에만 실행될 때 비로소 가치가 있습니다.


---

## 잡 분해 기준을 구체적으로 세워 보겠습니다

"잡을 어떻게 나눌까?"는 직관만으로는 답이 나오지 않습니다. 실무에서는 다음 네 가지 기준이 유용합니다.

**기준 1 — 실패 격리**: 린트 실패와 테스트 실패는 원인이 다릅니다. 한 잡에 넣으면 "어디서 깨졌는지"를 로그에서 찾아야 하고, 나누면 실패한 잡 이름만으로 원인을 좁힐 수 있습니다.

**기준 2 — 실행 환경**: 린트는 Python만 있으면 되지만 빌드는 Docker가 필요할 수 있습니다. 실행 환경이 다르면 잡을 분리하는 편이 자연스럽습니다.

**기준 3 — 병렬화 가능성**: 서로 결과를 공유하지 않는 작업은 병렬로 돌릴 수 있습니다. 잡을 나누면 GitHub Actions가 자동으로 병렬 실행하므로 전체 시간이 줄어듭니다.

**기준 4 — 재실행 범위**: 잡 단위로 재실행이 가능합니다. 테스트는 통과했는데 배포만 실패했다면, 배포 잡만 다시 돌릴 수 있습니다. 하나의 잡에 모든 것이 들어 있으면 처음부터 다시 실행해야 합니다.

이 기준을 표로 정리하면 아래와 같습니다.

| 분리 기준 | 한 잡 유지 | 분리 추천 |
| --- | --- | --- |
| 실패 원인 | 같은 종류 | 다른 종류 |
| 실행 환경 | 동일 | 다름 |
| 병렬화 | 순서 의존 있음 | 독립적 |
| 재실행 | 항상 함께 재실행 OK | 부분 재실행 필요 |

---

## `needs`로 만드는 잡 그래프의 실전 패턴

단순한 직렬 체인(`A → B → C`)은 이해하기 쉽지만, 실무에서는 더 복잡한 패턴이 필요합니다. 자주 보이는 세 가지 패턴을 정리하겠습니다.

### 팬아웃 / 팬인 패턴

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: ruff check .

  test-unit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pytest tests/unit -q

  test-integration:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pytest tests/integration -q

  build:
    needs: [lint, test-unit, test-integration]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
```

세 개의 검증 잡이 병렬로 실행되고(팬아웃), 모두 성공해야 빌드가 시작됩니다(팬인). 이 패턴은 검증 종류를 늘려도 전체 실행 시간이 가장 긴 잡에 맞춰지므로, 개별 잡 시간만 관리하면 됩니다.

### 조건부 잡 패턴

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: pytest -q

  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: ./scripts/deploy.sh staging

  deploy-production:
    needs: deploy-staging
    if: github.event_name == 'push' && startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6
      - run: ./scripts/deploy.sh production
```

`if:` 조건은 잡 그래프의 분기를 만듭니다. PR에서는 테스트만 돌고, main push에서는 스테이징까지, 태그 push에서만 프로덕션 배포가 실행됩니다. 같은 워크플로우 파일 하나로 여러 시나리오를 처리할 수 있습니다.

### 매트릭스 + needs 조합 패턴

```yaml
jobs:
  test:
    strategy:
      matrix:
        python: ["3.11", "3.12"]
        os: [ubuntu-latest, macos-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python }}
      - run: pytest -q

  publish:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
      - run: twine upload dist/*
```

`needs: test`는 매트릭스의 모든 조합이 성공해야 다음 잡이 시작된다는 뜻입니다. 4개 조합 중 하나라도 실패하면 publish는 실행되지 않습니다. 이 동작은 매트릭스를 안전장치로 쓸 수 있게 해 줍니다.

---

## `outputs`를 활용한 잡 간 데이터 전달 심화

잡 사이에 값을 넘길 때 자주 만나는 패턴과 주의점을 정리하겠습니다.

```yaml
jobs:
  version:
    runs-on: ubuntu-latest
    outputs:
      tag: ${{ steps.get-tag.outputs.tag }}
      should-deploy: ${{ steps.check.outputs.deploy }}
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0

      - id: get-tag
        run: |
          TAG=$(git describe --tags --abbrev=0 2>/dev/null || echo "v0.0.0")
          echo "tag=${TAG}" >> "$GITHUB_OUTPUT"

      - id: check
        run: |
          if [[ "${{ github.ref }}" == refs/tags/v* ]]; then
            echo "deploy=true" >> "$GITHUB_OUTPUT"
          else
            echo "deploy=false" >> "$GITHUB_OUTPUT"
          fi

  build:
    needs: version
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: |
          echo "Building version: ${{ needs.version.outputs.tag }}"
          docker build -t app:${{ needs.version.outputs.tag }} .

  deploy:
    needs: [version, build]
    if: needs.version.outputs.should-deploy == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying ${{ needs.version.outputs.tag }}"
```

이 패턴에서 주의할 점 세 가지입니다.

1. **outputs는 항상 문자열입니다.** 불리언처럼 보이는 `'true'`도 실제로는 문자열이므로, `if:` 조건에서 `== 'true'`로 비교해야 합니다.
2. **한 잡의 outputs는 `needs`로 연결된 잡에서만 접근 가능합니다.** `needs`에 명시하지 않은 잡에서는 다른 잡의 outputs를 읽을 수 없습니다.
3. **큰 데이터는 아티팩트로 넘깁니다.** outputs는 짧은 문자열에 적합하고, 빌드 결과물이나 리포트는 `actions/upload-artifact`와 `actions/download-artifact`를 사용해야 합니다.

---

## 매트릭스 비용 통제 전략

매트릭스는 강력하지만 조합이 커지면 비용이 빠르게 불어납니다. 실무에서 비용을 통제하는 방법을 정리하겠습니다.

```yaml
strategy:
  fail-fast: true
  matrix:
    python: ["3.11", "3.12"]
    os: [ubuntu-latest]
    include:
      - python: "3.12"
        os: macos-latest
    exclude:
      - python: "3.10"
        os: macos-latest
```

**`fail-fast: true`**: 하나가 실패하면 나머지를 즉시 취소합니다. 비용을 줄이는 가장 직접적인 방법입니다. 다만 호환성 매트릭스에서는 모든 결과를 보고 싶을 수 있으므로 `false`가 나을 때도 있습니다.

**`include`와 `exclude`**: 전체 조합 대신 필요한 조합만 추가하거나 불필요한 조합을 제거합니다. macOS 테스트가 특정 버전에서만 필요하다면 `include`로 한 조합만 추가하는 편이 효율적입니다.

**PR vs main 분리**: PR에서는 최소 매트릭스(최신 Python + Ubuntu만)로 빠른 피드백을 주고, main push에서 전체 매트릭스를 실행하는 이중 구조가 일반적입니다.

```yaml
strategy:
  matrix:
    python: ${{ github.event_name == 'pull_request' && fromJSON('["3.12"]') || fromJSON('["3.10", "3.11", "3.12"]') }}
```

이 표현식은 PR에서는 Python 3.12만, push에서는 세 버전 모두를 테스트합니다. 동적 매트릭스는 복잡해 보이지만, 비용과 피드백 속도를 동시에 잡는 실무 기법입니다.

---

## 잡 간 아티팩트 전달

outputs가 문자열에 적합하다면, 빌드 결과물이나 테스트 리포트 같은 파일은 아티팩트로 전달해야 합니다.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: python -m build
      - uses: actions/upload-artifact@v7
        with:
          name: dist
          path: dist/
          retention-days: 3

  publish:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v7
        with:
          name: dist
          path: dist/
      - run: twine upload dist/*
```

아티팩트 사용 시 알아 두면 좋은 점입니다.

- `retention-days`를 짧게 잡으면 스토리지 비용을 줄일 수 있습니다. CI 용도로는 1-3일이면 충분합니다.
- 같은 워크플로우 실행 안에서만 아티팩트를 공유할 수 있습니다. 다른 워크플로우에서 가져오려면 `workflow_run` 이벤트를 사용해야 합니다.
- 아티팩트 이름은 매트릭스에서 고유해야 합니다. `name: dist-${{ matrix.python }}`처럼 변수를 포함시켜야 덮어쓰기를 방지합니다.

---

## `concurrency`로 중복 실행 방지

같은 PR에 빠르게 여러 커밋을 push하면 워크플로우가 여러 번 실행됩니다. 결과를 기다리지 않을 앞선 실행이 리소스를 차지하는 낭비를 `concurrency`로 막을 수 있습니다.

```yaml
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

이 설정은 같은 브랜치(또는 PR)에서 새 실행이 시작되면 이전 실행을 자동 취소합니다. 배포 잡에서는 `cancel-in-progress: false`를 써서 진행 중인 배포가 취소되지 않게 보호하는 편이 안전합니다.

```yaml
jobs:
  deploy:
    concurrency:
      group: deploy-production
      cancel-in-progress: false
    runs-on: ubuntu-latest
    steps:
      - run: ./scripts/deploy.sh
```

잡 수준에서 `concurrency`를 걸면 워크플로우 전체가 아니라 특정 잡만 직렬화할 수 있습니다. 테스트는 병렬로 돌되, 배포만 한 번에 하나씩 실행하는 구조가 가능합니다.

---

## 워크플로우 파일 구조화 패턴

워크플로우 파일이 길어지면 관리가 어려워집니다. 실무에서 쓰는 구조화 패턴을 정리하겠습니다.

**패턴 1 — 역할별 파일 분리**

```text
.github/workflows/
├── ci.yml          # 테스트, 린트, 타입체크
├── build.yml       # 빌드, 패키징
├── deploy.yml      # 배포
└── maintenance.yml # 의존성 업데이트, 정리 작업
```

**패턴 2 — Reusable workflow로 공통 로직 추출**

```yaml
# .github/workflows/reusable-test.yml
on:
  workflow_call:
    inputs:
      python-version:
        required: true
        type: string

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ inputs.python-version }}
      - run: pytest -q
```

```yaml
# .github/workflows/ci.yml
jobs:
  test-311:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: "3.11"

  test-312:
    uses: ./.github/workflows/reusable-test.yml
    with:
      python-version: "3.12"
```

Reusable workflow는 잡 그래프 설계와 직접 연결됩니다. 공통 검증 로직을 한 곳에서 관리하면서도, 호출하는 쪽에서 `needs`로 의존성을 걸 수 있습니다. 이 패턴은 시리즈 후반부(10장)에서 더 자세히 다룹니다.

---

## 잡 실행 시간 최적화

잡 그래프가 올바르게 설계됐더라도 개별 잡 실행 시간이 길면 전체 피드백이 느려집니다. 자주 쓰는 최적화 기법을 정리하겠습니다.

| 기법 | 효과 | 적용 시점 |
| --- | --- | --- |
| 의존성 캐시 | 설치 시간 50-80% 절감 | 항상 |
| checkout fetch-depth: 1 | clone 시간 단축 | git 이력 불필요 시 |
| 매트릭스 최소화 | 잡 수 감소 | PR 검증 |
| 조건부 스킵 | 불필요 실행 방지 | paths 필터 |
| 병렬 테스트 | 테스트 시간 단축 | 테스트 수 많을 때 |

```yaml
- uses: actions/checkout@v6
  with:
    fetch-depth: 1  # shallow clone

- uses: actions/setup-python@v6
  with:
    python-version: "3.12"
    cache: "pip"

- run: pytest -q -n auto  # pytest-xdist 병렬 실행
```

`fetch-depth: 1`은 가장 쉬운 최적화입니다. 대부분의 CI 잡에서는 최신 커밋만 있으면 되므로, 전체 이력을 가져올 필요가 없습니다. 다만 `git describe`나 changelog 생성처럼 이력이 필요한 잡에서는 `fetch-depth: 0`을 써야 합니다.


## 처음 질문으로 돌아가기

- **Workflow, Job, Step은 각각 무엇을 담당할까요?**
  - Workflow는 자동화의 바깥 틀로 "어떤 이벤트에서 무엇이 시작되는가"를 정합니다. Job은 병렬 실행되는 작업 단위로 실패 격리와 병렬성의 경계입니다. Step은 Job 안에서 순서대로 실행되는 개별 명령입니다. 설계할 때는 "이 작업이 독립 실행 가능한가"를 기준으로 Job 경계를 잡고, "이 명령이 앞 결과에 의존하는가"를 기준으로 Step 순서를 정하면 됩니다.
- **`needs`는 왜 단순한 옵션이 아니라 파이프라인 설계 도구일까요?**
  - `needs`는 잡 사이에 방향 있는 그래프를 만들어, "무엇이 성공해야 다음이 시작되는가"라는 비즈니스 규칙을 코드로 표현합니다. 팬아웃/팬인, 조건부 배포, 매트릭스 게이트 같은 실무 패턴이 모두 `needs` 위에서 동작합니다. 잘못 설계하면 불필요한 직렬화로 시간이 낭비되고, 생략하면 실패한 검증 위에 배포가 올라가는 사고가 납니다.
- **`matrix`는 언제 유용하고 언제 비용 폭탄이 될까요?**
  - 매트릭스는 호환성 검증(여러 Python 버전, 여러 OS)에서 유용합니다. 비용 폭탄이 되는 순간은 조합을 무분별하게 곱할 때입니다. Python 3개 × OS 3개 × DB 2개 = 18개 잡이 동시에 돌면 비용도 18배입니다. PR에서는 최소 조합, main에서 전체 조합을 돌리는 이중 구조와 `fail-fast`, `include`/`exclude`로 범위를 통제하는 것이 실무 기본입니다.

<!-- toc:begin -->
## 시리즈 목차

- [GitHub Actions 101 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- **Workflow와 Job (현재 글)**
- Trigger 이해하기 (예정)
- Python 테스트 자동화 (예정)
- Lint와 Type Check (예정)
- 빌드 아티팩트 (예정)
- Docker 빌드 (예정)
- 배포 자동화 (예정)
- Secret 관리 (예정)
- 실전 CI/CD 파이프라인 (예정)

<!-- toc:end -->

## 참고 자료

- [Workflow syntax](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
- [Using jobs in a workflow](https://docs.github.com/actions/using-jobs/using-jobs-in-a-workflow)
- [Using a matrix for jobs](https://docs.github.com/actions/using-jobs/using-a-matrix-for-your-jobs)
- [Defining outputs for jobs](https://docs.github.com/actions/using-jobs/defining-outputs-for-jobs)
- [Reusing workflows](https://docs.github.com/actions/using-workflows/reusing-workflows)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/github-actions-101/ko)

Tags: GitHubActions, Workflow, Job, Matrix, CICD
