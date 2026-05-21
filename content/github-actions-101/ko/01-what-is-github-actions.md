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

처음 GitHub Actions를 보면 “GitHub 안에 CI가 하나 들어 있구나” 정도로 이해하기 쉽습니다. 출발점으로는 맞는 말입니다. 하지만 이 정도 설명만으로는 왜 어떤 팀은 배포 속도가 빨라지고, 어떤 팀은 YAML만 늘어나는데도 여전히 수동 작업에서 벗어나지 못하는지 설명되지 않습니다.

이 글은 GitHub Actions 101 시리즈의 첫 번째 글입니다. 여기서는 GitHub Actions를 단순한 자동화 버튼이 아니라, 코드 저장소 바로 옆에서 반복 작업을 실행하는 실행 플랫폼으로 이해해 보겠습니다.

## 먼저 던지는 질문

- GitHub Actions는 정확히 무엇이고 CI/CD에서 어디에 놓일까요?
- Workflow, Job, Step은 어떤 계층 구조로 이해해야 할까요?
- 첫 워크플로우는 어떤 최소 구성으로 시작하는 편이 좋을까요?

## 큰 그림

![GitHub Actions 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/01/01-01-diagram.ko.png)

*GitHub Actions 101 1장 흐름 개요*

## 왜 중요한가

CI/CD는 팀의 속도만이 아니라 신뢰의 기준을 만듭니다. 로컬에서만 테스트를 돌리는 팀은 “나는 통과했는데요”라는 문장에 자주 의존하게 됩니다. 반대로 저장소가 직접 테스트와 검증을 실행하는 팀은 “이 커밋은 같은 절차를 통과했다”는 공통 기반을 갖게 됩니다.

GitHub Actions가 강한 이유는 별도 서버를 운영하지 않아도 이 기준을 바로 만들 수 있기 때문입니다. 저장소에 `.github/workflows/*.yml` 파일을 추가하는 순간 자동화가 코드의 일부가 됩니다. 서버를 따로 붙들고 있지 않아도 되고, 작업 이력도 PR과 커밋 옆에 그대로 남습니다.

## 한눈에 보는 실행 흐름

이 그림에서 먼저 잡아야 할 감각은 단순합니다. 이벤트가 워크플로우를 깨우고, 워크플로우 안에서 잡이 돌고, 각 잡 안에서 스텝이 순서대로 실행됩니다. 실무에서 “어디를 고쳐야 하지?”라는 질문이 나올 때도 결국 이 계층을 따라가면 됩니다.

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

GitHub Actions는 워크플로 파일의 위치가 정확해야만 인식합니다. 첫 단계가 단순해 보여도, 실제로는 “자동화 파일도 저장소 규약 안에 둔다”는 규칙을 배우는 지점입니다.

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

여기서 중요한 점은 “성공했다”보다 “무슨 순서로 무슨 로그가 나왔는지 읽을 수 있다”입니다. 앞으로 CI가 깨질 때는 대부분 이 실행 로그에서 원인을 찾게 됩니다.

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

입문 단계에서는 “어차피 작은 프로젝트인데”라는 이유로 모든 것을 한 파일에 몰아넣기 쉽습니다. 하지만 처음부터 테스트 자동화와 배포 자동화를 같은 무게로 다루기 시작하면, 나중에 분리할 때 훨씬 고생합니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 test, lint, typecheck, build, deploy를 서로 다른 책임으로 분리합니다. 그리고 워크플로우 파일도 애플리케이션 코드와 똑같이 리뷰합니다. 저는 이 지점이 중요하다고 봅니다. YAML도 결국 운영 동작을 바꾸는 코드이기 때문입니다.

또 하나 기억할 점은 실행 시간입니다. 워크플로우가 길어질수록 개발자는 피드백을 덜 신뢰하게 됩니다. 자동화의 목적은 많이 돌리는 것이 아니라, 필요한 검사를 빠르고 일관되게 돌리는 것입니다.

## 체크리스트

- [ ] `.github/workflows/` 디렉터리가 있다.
- [ ] push와 PR 모두에서 트리거된다.
- [ ] 결과가 PR 체크로 보인다.
- [ ] 비밀값은 `secrets.*`로만 참조한다.

## 연습 문제

1. `Hello World`만 출력하는 가장 작은 워크플로우를 만들어 보세요.
2. Ubuntu와 macOS에서 모두 실행되는 매트릭스를 추가해 보세요.
3. 테스트를 일부러 깨뜨린 뒤 PR 체크가 어떻게 실패하는지 확인해 보세요.

## 정리

GitHub Actions는 코드 옆에 붙어 있는 자동화 실행기입니다. 저장소 이벤트를 받아 워크플로우를 깨우고, 워크플로우 안의 잡과 스텝이 실제 검증과 배포 절차를 수행합니다. 이 구조를 한 번 이해해 두면 뒤의 모든 주제는 결국 더 정교한 워크플로우 설계 문제로 연결됩니다.

다음 글에서는 워크플로우 안쪽 구조를 더 자세히 보겠습니다. 특히 잡을 어떻게 나누고, 어떤 작업을 병렬로 돌리며, 어떤 작업에는 순서를 강제해야 하는지를 다룹니다.


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

## 처음 질문으로 돌아가기

- **GitHub Actions는 정확히 무엇이고 CI/CD에서 어디에 놓일까요?**
  - 본문의 기준은 GitHub Actions란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Workflow, Job, Step은 어떤 계층 구조로 이해해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **첫 워크플로우는 어떤 최소 구성으로 시작하는 편이 좋을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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

Tags: GitHubActions, CICD, Automation, DevOps, Workflow
