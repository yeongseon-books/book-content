---
series: github-actions-101
episode: 1
title: "GitHub Actions 101 (1/10): GitHub Actions란 무엇인가?"
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
  - CICD
  - Automation
  - DevOps
  - Workflow
seo_description: GitHub Actions의 핵심 개념과 첫 워크플로우를 실무 관점에서 정리합니다.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (1/10): GitHub Actions란 무엇인가?

처음 GitHub Actions를 보면 "GitHub 안에 CI가 하나 들어 있구나" 정도로 이해하기 쉽습니다. 출발점으로는 맞는 말입니다. 하지만 이 정도 설명만으로는 왜 어떤 팀은 배포 속도가 빨라지고, 어떤 팀은 YAML만 늘어나는데도 여전히 수동 작업에서 벗어나지 못하는지 설명되지 않습니다.

이 글은 GitHub Actions 101 시리즈의 첫 번째 글입니다. 여기서는 GitHub Actions를 단순한 자동화 버튼이 아니라, 코드 저장소 바로 옆에서 반복 작업을 실행하는 실행 플랫폼으로 이해해 보겠습니다.


![GitHub Actions 실행 흐름](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/01/01-01-diagram.ko.png)
*이벤트가 워크플로우를 깨우고, 잡이 러너 위에서 스텝을 순서대로 실행하는 흐름*

> GitHub Actions는 'GitHub 안의 CI'가 아니라 코드 저장소 바로 옆에서 이벤트를 받아 작업을 실행하는 실행 플랫폼입니다 — 빌드·테스트뿐 아니라 라벨링·릴리스·문서 배포까지 같은 모델로 흡수된다는 점이 단순 CI 서비스와 다른 결정적 차이입니다.

## 먼저 던지는 질문

- GitHub Actions는 정확히 무엇이고 CI/CD에서 어디에 놓일까요?
- Workflow, Job, Step은 어떤 계층 구조로 이해해야 할까요?
- 첫 워크플로우는 어떤 최소 구성으로 시작하는 편이 좋을까요?

## 왜 중요한가

CI/CD는 팀의 속도만이 아니라 신뢰의 기준을 만듭니다. 로컬에서만 테스트를 돌리는 팀은 "나는 통과했는데요"라는 문장에 자주 의존하게 됩니다. 반대로 저장소가 직접 테스트와 검증을 실행하는 팀은 "이 커밋은 같은 절차를 통과했다"는 공통 기반을 갖게 됩니다.

GitHub Actions가 강한 이유는 별도 서버를 운영하지 않아도 이 기준을 바로 만들 수 있기 때문입니다. 저장소에 `.github/workflows/*.yml` 파일을 추가하는 순간 자동화가 코드의 일부가 됩니다. 서버를 따로 붙들고 있지 않아도 되고, 작업 이력도 PR과 커밋 옆에 그대로 남습니다.

## 한눈에 보는 실행 흐름

이 그림에서 먼저 잡아야 할 감각은 단순합니다. 이벤트가 워크플로우를 깨우고, 워크플로우 안에서 잡이 돌고, 각 잡 안에서 스텝이 순서대로 실행됩니다. 실무에서 "어디를 고쳐야 하지?"라는 질문이 나올 때도 결국 이 계층을 따라가면 됩니다.

## 핵심 용어를 먼저 정리하겠습니다

| 용어 | 뜻 | 운영에서 중요한 이유 |
| --- | --- | --- |
| 워크플로 | `.github/workflows/*.yml`에 있는 자동화 단위 | 자동화의 진입점과 범위를 결정합니다 |
| 이벤트 | 워크플로를 시작시키는 계기 | push, PR, schedule처럼 실행 시점을 정합니다 |
| 잡 | 워크플로 안의 실행 단위 | 기본적으로 병렬 실행되므로 속도와 구조를 좌우합니다 |
| 스텝 | 잡 안의 개별 명령 또는 액션 호출 | 실제 설치, 테스트, 빌드 작업이 여기서 일어납니다 |
| 러너 | 잡이 실행되는 머신 | ubuntu-latest 같은 실행 환경을 정합니다 |
| 액션 | 재사용 가능한 스텝 | `actions/checkout`처럼 반복되는 작업을 표준화합니다 |

입문자가 가장 많이 헷갈리는 부분은 워크플로와 잡을 같은 것으로 보는 것입니다. 워크플로는 상위 컨테이너이고, 잡은 그 안에서 돌아가는 작업 단위입니다. 이 구분을 잡고 시작하면 뒤에서 병렬 처리나 의존성 설정을 배울 때 훨씬 덜 흔들립니다.

## 자동화 전과 후를 비교해 보겠습니다

자동화가 없을 때는 PR마다 개발자가 로컬에서 테스트를 돌리고, 결과를 말로 공유하고, 누군가가 배포 여부를 수동으로 판단합니다. 이 구조는 작은 저장소에서는 버틸 수 있어 보여도 팀이 커지면 금방 불안정해집니다. 같은 테스트를 누군가는 돌리고, 누군가는 건너뛰며, 누군가는 오래된 가상환경에서 실행하기 때문입니다.

자동화가 붙으면 기준이 바뀝니다. PR을 열면 저장소가 동일한 환경에서 테스트를 실행하고, 결과가 체크로 남습니다. 사람이 기억해서 수행하던 절차가 저장소의 기본 동작으로 바뀌는 것입니다. 저는 GitHub Actions의 가치를 바로 이 전환에서 봅니다.

## 첫 워크플로우를 5단계로 만들어 보겠습니다

### 1단계 — 디렉터리 만들기

```bash
mkdir -p .github/workflows
```

GitHub Actions는 워크플로 파일의 위치가 정확해야만 인식합니다. 첫 단계가 단순해 보여도, 실제로는 "자동화 파일도 저장소 규약 안에 둔다"는 규칙을 배우는 지점입니다.

### 2단계 — 워크플로우 파일 작성

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

이 예제는 작지만 GitHub Actions의 최소 골격을 모두 보여 줍니다. `on:`은 언제 실행할지, `jobs:`는 무엇을 실행할지, `runs-on:`은 어디서 실행할지, `steps:`는 어떤 순서로 실행할지를 정의합니다.

### 3단계 — push로 실행시키기

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add first workflow"
git push
```

자동화는 파일만 써 두고 끝나는 기능이 아닙니다. 저장소에 반영되어 실제 이벤트가 발생해야 비로소 살아납니다. 그래서 첫 워크플로우를 배울 때는 반드시 한 번 직접 push해서 실행 로그를 보는 편이 좋습니다.

### 4단계 — Actions 탭에서 결과 확인

```text
Repo > Actions tab
- The workflow run log appears.
- Each step prints its output and time.
```

여기서 중요한 점은 "성공했다"보다 "무슨 순서로 무슨 로그가 나왔는지 읽을 수 있다"입니다. 앞으로 CI가 깨질 때는 대부분 이 실행 로그에서 원인을 찾게 됩니다.

### 5단계 — PR 체크로 연결하기

```text
In branch protection, enable "Require status checks to pass."
A failed test now blocks merge.
```

이 단계까지 와야 GitHub Actions가 단순한 실행기가 아니라 팀 규칙의 일부가 됩니다. 실패한 테스트가 머지를 막기 시작하면, 자동화는 권고가 아니라 품질 게이트로 작동합니다.

## 이 코드에서 먼저 봐야 할 점

- YAML 파일 하나가 자동화 전체를 정의합니다.
- `actions/checkout`은 거의 모든 워크플로우의 첫 단계입니다.
- `runs-on`은 실행 환경 선택이므로 속도, 호환성, 비용과 연결됩니다.

특히 `checkout`을 빼먹는 실수는 아주 흔합니다. 러너에는 기본적으로 여러분 저장소 코드가 없기 때문에, 코드를 먼저 가져오지 않으면 뒤의 설치나 테스트 단계가 모두 실패합니다.

## 자주 하는 실수 다섯 가지

1. 워크플로 파일을 `.github/workflows/` 밖에 둡니다.
2. `on:`을 빼먹어서 아무 이벤트에도 반응하지 않게 만듭니다.
3. `actions/checkout` 없이 바로 명령을 실행합니다.
4. 무거운 빌드나 배포까지 모든 PR에서 한꺼번에 실행합니다.
5. 비밀값을 YAML에 직접 적습니다.

입문 단계에서는 "어차피 작은 프로젝트인데"라는 이유로 모든 것을 한 파일에 몰아넣기 쉽습니다. 하지만 처음부터 테스트 자동화와 배포 자동화를 같은 무게로 다루기 시작하면, 나중에 분리할 때 훨씬 고생합니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 test, lint, typecheck, build, deploy를 서로 다른 책임으로 분리합니다. 그리고 워크플로우 파일도 애플리케이션 코드와 똑같이 리뷰합니다. 저는 이 지점이 중요하다고 봅니다. YAML도 결국 운영 동작을 바꾸는 코드이기 때문입니다.

또 하나 기억할 점은 실행 시간입니다. 워크플로우가 길어질수록 개발자는 피드백을 덜 신뢰하게 됩니다. 자동화의 목적은 많이 돌리는 것이 아니라, 필요한 검사를 빠르고 일관되게 돌리는 것입니다.

---

## GitHub Actions가 CI/CD 생태계에서 놓이는 위치

GitHub Actions를 처음 접할 때 흔히 Jenkins, GitLab CI, CircleCI 같은 기존 도구와 비교합니다. 차이를 몇 가지로 정리하면 아래와 같습니다.

| 비교 기준 | Jenkins | GitLab CI | GitHub Actions |
| --- | --- | --- | --- |
| 실행 인프라 | 자체 서버 운영 | GitLab Runner 설치 | GitHub-hosted 러너 기본 제공 |
| 설정 위치 | Jenkins UI + Jenkinsfile | `.gitlab-ci.yml` | `.github/workflows/*.yml` |
| 마켓플레이스 | 플러그인 중심 | 제한적 | 20,000개 이상의 공개 액션 |
| 코드 저장소 통합 | 별도 연결 | GitLab 내장 | GitHub 내장 |
| 과금 단위 | 서버 비용 | 분당 과금(SaaS) | 분당 과금(public repo 무료) |

핵심 차이는 통합 밀도입니다. GitHub Actions는 PR 체크, 이슈 자동화, 패키지 배포, 릴리스, 의존성 업데이트까지 하나의 플랫폼 안에서 이어집니다. 별도 서비스를 붙이는 비용이 줄어드는 대신, GitHub 생태계에 더 깊이 묶이는 구조입니다.

이 점을 이해하면 "언제 GitHub Actions가 맞고, 언제 다른 도구가 나은가"를 판단하기 쉬워집니다. 자체 호스팅이 반드시 필요하거나, 멀티 VCS를 써야 하거나, 빌드 캐시 공유 요구가 극도로 복잡한 경우에는 다른 도구가 여전히 유리할 수 있습니다. 하지만 대부분의 팀에서 GitHub을 이미 쓰고 있다면, Actions가 초기 진입 비용이 가장 낮은 선택지입니다.

---

## 러너의 동작 방식을 이해해야 비용이 보입니다

GitHub-hosted 러너는 잡이 시작될 때 깨끗한 가상머신을 할당받고, 잡이 끝나면 그 머신은 사라집니다. 이 구조는 격리와 재현성 측면에서 강하지만, 몇 가지 운영 감각을 요구합니다.

첫째, 러너는 영속 상태를 가지지 않습니다. 이전 실행에서 설치한 패키지, 생성한 파일, 캐시는 기본적으로 남지 않습니다. 그래서 의존성 설치 시간이 매번 들고, 이를 줄이려면 `actions/cache`나 `setup-python`의 캐시 옵션을 의식적으로 설정해야 합니다.

```yaml
- uses: actions/setup-python@v6
  with:
    python-version: "3.11"
    cache: "pip"
```

둘째, 러너 선택은 비용과 직결됩니다. `ubuntu-latest`는 가장 빠르고 저렴한 선택인 경우가 많고, `macos-latest`는 분당 비용이 10배입니다. 매트릭스에 macOS를 넣을 때는 실제로 필요한 테스트인지 한 번 더 생각하는 편이 좋습니다.

```yaml
strategy:
  matrix:
    os: [ubuntu-latest]
    # macos-latest는 iOS/macOS 타겟이 있을 때만
```

셋째, self-hosted 러너라는 선택지가 있습니다. 보안 정책이 엄격하거나, GPU가 필요하거나, 빌드가 매우 무거운 경우에는 자체 머신을 러너로 등록할 수 있습니다. 하지만 그만큼 러너 관리 부담도 함께 옵니다.

---

## 워크플로우 파일 구조를 더 자세히 보겠습니다

앞에서 최소 예제를 보았으니, 이번에는 실무에서 자주 보는 조금 더 풍부한 구조를 봅니다.

```yaml
name: ci

on:
  push:
    branches: [main]
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"
  pull_request:
    paths:
      - "src/**"
      - "tests/**"
      - "pyproject.toml"

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"

      - name: 의존성 설치
        run: pip install -e ".[dev]"

      - name: 테스트 실행
        run: pytest -q --junitxml=report.xml

      - name: 테스트 리포트 업로드
        uses: actions/upload-artifact@v7
        if: always()
        with:
          name: test-report-${{ matrix.python-version }}
          path: report.xml
          retention-days: 7
```

이 파일에서 추가된 요소를 하나씩 짚어 보겠습니다.

**`paths` 필터**: 문서나 설정 파일만 바뀌었을 때는 테스트를 돌리지 않습니다. 불필요한 실행을 줄여 러너 비용과 대기 시간을 함께 절약합니다.

**`concurrency`**: 같은 PR에 연속으로 push가 들어오면 앞선 실행을 취소합니다. 결과를 기다리지 않을 실행이 대기열에 쌓이는 낭비를 막아 줍니다.

**`matrix`**: Python 3.11과 3.12에서 동시에 테스트를 돌립니다. 호환성을 확인하면서도 병렬 실행 덕분에 전체 시간은 크게 늘지 않습니다.

**아티팩트 업로드**: 테스트 결과를 XML로 남기면 나중에 실패 원인을 추적하기 훨씬 쉬워집니다. `if: always()`가 없으면 실패한 실행에서는 리포트가 올라가지 않으므로 주의해야 합니다.

---

## 액션의 구조와 버전 관리

`uses: actions/checkout@v6`처럼 액션을 호출할 때 `@v6`이 버전 핀입니다. 이 버전 핀이 왜 중요한지 실무에서는 금방 느끼게 됩니다.

```yaml
# 권장: 메이저 버전 핀
- uses: actions/setup-python@v6

# 더 안전: 커밋 SHA 핀
- uses: actions/setup-python@8d9ed867ee42ba1c3be538356b8e3e90c3aef03a  # v6.0.0

# 위험: 브랜치 직접 참조
- uses: actions/setup-python@main
```

메이저 버전 핀(`@v6`)은 하위 호환 업데이트만 자동으로 따라가므로 대부분의 경우 적절합니다. 보안이 민감한 환경이라면 커밋 SHA를 직접 적고, Dependabot이 자동으로 업데이트 PR을 올리게 하는 조합이 가장 안정적입니다.

액션의 소스는 결국 GitHub 저장소입니다. `actions/checkout` 저장소에 가면 `action.yml`이라는 메타데이터 파일이 있고, 여기에 입력, 출력, 실행 방식이 정의돼 있습니다. 나중에 직접 액션을 만들 때도 이 구조를 따르게 됩니다.

---

## 실행 로그를 읽는 감각

워크플로우를 만든 뒤 가장 먼저 익혀야 할 기술은 실행 로그 읽기입니다. Actions 탭에서 실행 기록을 열면 잡별, 스텝별로 접힌 로그를 볼 수 있습니다.

```text
Run pytest -q --junitxml=report.xml
...
FAILED tests/test_auth.py::test_login_expired_token
  assert response.status_code == 401
  AssertionError: assert 500 == 401
...
1 failed, 42 passed in 3.21s
Error: Process completed with exit code 1.
```

이 로그에서 봐야 할 순서는 명확합니다.

1. 어떤 스텝에서 실패했는가 — 스텝 이름이 접혀 있으므로 빨간색 표시를 먼저 찾습니다.
2. 어떤 명령이 실패했는가 — `Run` 다음에 나오는 명령을 확인합니다.
3. 종료 코드는 무엇인가 — `exit code 1`은 일반적인 실패, `exit code 137`은 메모리 초과를 의미하는 경우가 많습니다.

실행 시간도 중요한 정보입니다. 의존성 설치가 2분을 넘기면 캐시를 점검해야 하고, 테스트 자체가 5분을 넘기면 병렬화나 테스트 분리를 고려해야 합니다. 이 감각은 로그를 자주 읽어야 붙습니다.

---

## 워크플로우 디버깅 기본 기법

워크플로우가 예상대로 동작하지 않을 때 쓸 수 있는 기본 기법을 정리하겠습니다.

```yaml
# 컨텍스트 값을 출력해서 확인하기
- name: 디버그 컨텍스트 출력
  run: |
    echo "event_name: ${{ github.event_name }}"
    echo "ref: ${{ github.ref }}"
    echo "sha: ${{ github.sha }}"
    echo "actor: ${{ github.actor }}"
```

`github` 컨텍스트에는 이벤트 종류, 브랜치, 커밋 SHA, 실행자 정보가 들어 있습니다. 조건문(`if:`)이 예상대로 동작하지 않을 때는 이 값들을 먼저 출력해 보는 편이 빠릅니다.

```yaml
# 러너 환경 확인
- name: 러너 정보
  run: |
    uname -a
    python --version
    pip --version
    df -h
    free -m
```

러너의 OS 버전, 디스크 공간, 메모리를 확인하면 "왜 로컬에서는 되는데 CI에서는 안 되지?"라는 질문에 대한 실마리를 찾을 수 있습니다.

또 하나 유용한 기법은 `act`라는 로컬 실행 도구입니다. Docker 기반으로 워크플로우를 로컬에서 시뮬레이션할 수 있어, push 전에 YAML 문법이나 기본 흐름을 미리 확인하기 좋습니다. 다만 GitHub 컨텍스트나 secret은 완벽히 재현되지 않으므로 보조 도구로 활용하는 편이 맞습니다.

---

## 비용과 한도를 미리 알아 두면 좋습니다

GitHub Actions는 public 저장소에서 무료이고, private 저장소에서는 플랜별 무료 분수가 다릅니다. 주요 한도를 정리하면 아래와 같습니다.

| 항목 | 한도 |
| --- | --- |
| 워크플로우 실행 시간 | 잡당 최대 6시간 |
| 동시 잡 수 (Free) | 20개 |
| 동시 잡 수 (Team/Enterprise) | 60~180개 |
| 아티팩트 보관 기간 | 기본 90일, 설정 가능 |
| 로그 보관 기간 | 400일 |

비용을 줄이는 가장 확실한 방법은 불필요한 실행을 줄이는 것입니다. `paths` 필터, `concurrency`, 매트릭스 범위 제한이 여기에 해당합니다. 비용을 모니터링하려면 Settings > Billing에서 Actions 사용량을 정기적으로 확인하는 습관이 필요합니다.

---


---

## 보안 기본 원칙을 처음부터 잡아야 합니다

워크플로우는 저장소 코드에 접근할 수 있으므로, 잘못 설정하면 비밀값 노출이나 권한 남용으로 이어질 수 있습니다. 처음부터 알아 두면 좋은 보안 기본 원칙을 정리하겠습니다.

첫째, 워크플로우 권한은 최소 권한 원칙을 따릅니다. GitHub은 기본적으로 `GITHUB_TOKEN`에 넓은 권한을 부여하지만, 저장소 설정에서 기본 권한을 `read`로 낮추고, 필요한 잡에서만 `permissions`를 명시적으로 올리는 편이 안전합니다.

```yaml
permissions:
  contents: read
  pull-requests: write

jobs:
  label:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/labeler@v5
```

둘째, fork에서 오는 PR은 특별히 주의해야 합니다. 외부 기여자의 PR에서는 기본적으로 secret이 주입되지 않고, `GITHUB_TOKEN` 권한도 제한됩니다. 이는 의도된 안전장치이므로, 이를 우회하려는 설정은 신중하게 판단해야 합니다.

셋째, 서드파티 액션을 사용할 때는 출처를 확인합니다. `actions/` 공식 네임스페이스가 아닌 액션은 코드를 한 번 읽어 보거나, 최소한 커밋 SHA로 핀해서 예고 없는 변경을 막는 편이 좋습니다.

```yaml
# 서드파티 액션은 SHA 핀 권장
- uses: slackapi/slack-github-action@485a9d42d3a73031f12ec201c457e2162c45d02d  # v2.0.0
```

넷째, `pull_request_target` 이벤트는 신중하게 사용합니다. 이 이벤트는 base 브랜치의 워크플로우를 실행하면서도 PR의 코드에 접근할 수 있어, 잘못 쓰면 악의적인 PR이 secret을 탈취할 수 있습니다. 꼭 필요한 경우가 아니면 `pull_request`를 사용하는 편이 안전합니다.

이 네 가지 원칙은 뒤에서 다룰 Secret 관리(9장)의 기초가 됩니다. 처음 워크플로우를 만들 때부터 이 감각을 가지고 있으면 나중에 보안 사고를 크게 줄일 수 있습니다.

마지막으로, 워크플로우 파일 자체의 변경도 리뷰 대상입니다. CODEOWNERS 파일에 `.github/workflows/` 경로를 등록해 두면, 워크플로우 변경 시 반드시 지정된 리뷰어의 승인을 받게 할 수 있습니다. 이는 실수로 권한을 넓히거나 위험한 트리거를 추가하는 상황을 팀 차원에서 막아 줍니다.

## 체크리스트

- [ ] `.github/workflows/` 디렉터리가 있다.
- [ ] push와 PR 모두에서 트리거된다.
- [ ] 결과가 PR 체크로 보인다.
- [ ] 비밀값은 `secrets.*`로만 참조한다.
- [ ] 캐시 설정으로 의존성 설치 시간을 줄였다.
- [ ] `concurrency`로 중복 실행을 제한했다.

## 연습 문제

1. `Hello World`만 출력하는 가장 작은 워크플로우를 만들어 보세요.
2. Ubuntu와 macOS에서 모두 실행되는 매트릭스를 추가해 보세요.
3. 테스트를 일부러 깨뜨린 뒤 PR 체크가 어떻게 실패하는지 확인해 보세요.
4. `concurrency`를 추가하고 연속 push 시 앞선 실행이 취소되는지 확인해 보세요.

## 정리

GitHub Actions는 코드 옆에 붙어 있는 자동화 실행기입니다. 저장소 이벤트를 받아 워크플로우를 깨우고, 워크플로우 안의 잡과 스텝이 실제 검증과 배포 절차를 수행합니다. 이 구조를 한 번 이해해 두면 뒤의 모든 주제는 결국 더 정교한 워크플로우 설계 문제로 연결됩니다.

다음 글에서는 워크플로우 안쪽 구조를 더 자세히 보겠습니다. 특히 잡을 어떻게 나누고, 어떤 작업을 병렬로 돌리며, 어떤 작업에는 순서를 강제해야 하는지를 다룹니다.

## 처음 질문으로 돌아가기

- **GitHub Actions는 정확히 무엇이고 CI/CD에서 어디에 놓일까요?**
  - GitHub Actions는 저장소 이벤트에 반응해 워크플로우를 실행하는 플랫폼입니다. Jenkins처럼 별도 서버를 운영할 필요 없이, `.github/workflows/` 안의 YAML 파일이 CI/CD 파이프라인이 됩니다. GitHub 생태계와의 통합 밀도가 핵심 차별점이며, PR 체크, 릴리스, 패키지 배포까지 하나의 플랫폼에서 이어집니다.
- **Workflow, Job, Step은 어떤 계층 구조로 이해해야 할까요?**
  - Workflow는 자동화의 바깥 틀이고, Job은 병렬 실행되는 작업 단위이며, Step은 Job 안에서 순서대로 실행되는 명령입니다. "어디서 실패했는가"를 좁힐 때 이 세 계층을 따라가면 됩니다. Job 사이에는 `needs`로 순서를 강제할 수 있고, Step 사이에는 `if` 조건으로 실행을 제어합니다.
- **첫 워크플로우는 어떤 최소 구성으로 시작하는 편이 좋을까요?**
  - `on: [push, pull_request]`로 트리거를 열고, 단일 잡에 checkout, setup, test 세 스텝을 두는 것이 최소 구성입니다. 여기에 `cache`, `paths` 필터, `concurrency`를 하나씩 붙여 가면 자연스럽게 실무 수준으로 발전합니다. 처음부터 완벽한 파이프라인을 만들기보다 작게 시작해서 점진적으로 키우는 편이 학습 효율이 높습니다.

<!-- toc:begin -->
## 시리즈 목차

- **GitHub Actions란 무엇인가? (현재 글)**
- Workflow와 Job (예정)
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

- [GitHub Actions Documentation](https://docs.github.com/actions)
- [Workflow syntax](https://docs.github.com/actions/using-workflows/workflow-syntax-for-github-actions)
- [Awesome Actions](https://github.com/sdras/awesome-actions)
- [Actions Marketplace](https://github.com/marketplace?type=actions)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/github-actions-101/ko)

Tags: GitHubActions, CICD, Automation, DevOps, Workflow
