---
series: github-actions-101
episode: 6
title: "GitHub Actions 101 (6/10): 빌드 아티팩트"
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
  - Artifact
  - Build
  - Release
  - CICD
seo_description: 빌드 결과물을 업로드하고 다음 잡과 릴리스까지 연결하는 방법을 정리합니다.
last_reviewed: '2026-05-15'
---

# GitHub Actions 101 (6/10): 빌드 아티팩트

CI를 돌려서 빌드까지 성공했는데 결과물이 그대로 사라진다면, 그 파이프라인은 절반만 완성된 셈입니다. 테스트는 통과했지만 어떤 wheel이 만들어졌는지 남지 않고, 배포 잡은 다시 빌드를 반복하고, 며칠 뒤에는 어떤 산출물이 실제로 배포됐는지도 추적하기 어려워집니다. 빌드 결과를 남기는 일은 생각보다 중요합니다.

이 글은 GitHub Actions 101 시리즈의 6번째 글입니다. 여기서는 artifact를 이용해 빌드 산출물을 보관하고, 잡 사이에 전달하고, 필요하면 Release까지 연결하는 기본 패턴을 정리하겠습니다.

## 먼저 던지는 질문

- `upload-artifact`와 `download-artifact`는 각각 언제 쓰일까요?
- 잡 사이에서 결과물을 넘길 때 아티팩트가 왜 유용할까요?
- `retention-days`는 비용과 어떤 관계가 있을까요?

## 큰 그림

![GitHub Actions 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/06/06-01-diagram.ko.png)

*GitHub Actions 101 6장 흐름 개요*

## 왜 중요한가

러너는 영구 서버가 아닙니다. 빌드 잡이 끝나면 그 안에 있던 `dist/` 디렉터리도 함께 사라집니다. 따라서 결과물을 따로 보관하지 않으면 성공한 빌드조차 재사용할 수 없습니다. 배포 잡이 다음 단계에서 같은 빌드를 반복해야 한다면 시간도 늘고, 무엇이 실제 배포본인지 식별하기도 어려워집니다.

저는 아티팩트를 “빌드의 영수증”이라고 생각합니다. 어떤 입력으로 어떤 결과가 나왔는지 남겨 두는 기록이 있어야 공급망 보안, 릴리스 재현, 롤백 기준 같은 운영 작업도 안정적으로 굴러갑니다.

## 한눈에 보는 아티팩트 흐름

이 흐름이 중요한 이유는 빌드와 배포를 같은 러너에 묶지 않아도 된다는 점입니다. 저장된 산출물을 다음 잡이 읽기만 하면 되므로, 파이프라인 구조가 훨씬 유연해집니다.

## 핵심 용어를 먼저 정리하겠습니다

| 용어 | 뜻 | 실무 포인트 |
| --- | --- | --- |
| 아티팩트 | 워크플로우가 만든 파일 묶음 | 빌드 결과, 리포트, 로그를 남기는 수단입니다 |
| `upload-artifact` | 파일을 GitHub 스토리지에 업로드하는 액션 | 잡 종료 후에도 결과물을 유지합니다 |
| `download-artifact` | 같은 워크플로우 안의 아티팩트를 내려받는 액션 | 다음 잡에서 재빌드 없이 재사용합니다 |
| `retention-days` | 보관 기간 | 비용과 보관 정책을 함께 결정합니다 |
| Release | GitHub의 공식 배포 페이지 | 외부 사용자에게 산출물을 공개하기 좋습니다 |

## 자동화 전과 후를 비교해 보겠습니다

아티팩트가 없는 파이프라인에서는 build 잡이 끝나는 순간 결과물이 사실상 사라집니다. 로그에는 성공이라고 남지만, 실제 `dist/*.whl` 파일은 다음 잡이 접근할 수 없습니다. 그래서 deploy 잡이 다시 빌드를 하거나, 사람이 로컬에서 따로 파일을 만들어 업로드하는 우회가 생깁니다.

반대로 build 잡이 결과물을 업로드하고 deploy 잡이 그것을 내려받는 구조를 만들면, “검증한 바로 그 결과물”을 그대로 다음 단계에 넘길 수 있습니다. 이 차이가 작아 보여도 파이프라인의 신뢰도는 크게 달라집니다.

## 아티팩트를 5단계로 다뤄 보겠습니다

### 1단계 — 빌드 결과 업로드하기

```yaml
- run: python -m build
- uses: actions/upload-artifact@v7
  with:
    name: dist
    path: dist/*
    retention-days: 14
```

이 단계의 핵심은 결과물을 파일 시스템 밖으로 꺼내는 것입니다. 빌드가 끝난 뒤에도 남게 해야 다음 작업이 이를 참조할 수 있습니다.

### 2단계 — 다음 잡에서 내려받기

```yaml
deploy:
  needs: build
  runs-on: ubuntu-latest
  steps:
    - uses: actions/download-artifact@v8
      with:
        name: dist
        path: dist/
    - run: ls dist/
```

잡이 달라도 같은 워크플로우 안이라면 이 방식으로 산출물을 이어받을 수 있습니다. 배포 단계에서 다시 빌드하지 않아도 된다는 점이 중요합니다.

### 3단계 — 여러 파일을 묶어 보관하기

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: reports
    path: |
      coverage.xml
      report.xml
      logs/*.log
```

아티팩트는 wheel이나 바이너리만 담는 용도가 아닙니다. 테스트 리포트, 커버리지 결과, 장애 로그처럼 나중에 다시 봐야 할 모든 실행 흔적을 묶을 수 있습니다.

### 4단계 — Release 자동 발행하기

```yaml
- uses: softprops/action-gh-release@v2
  if: startsWith(github.ref, 'refs/tags/')
  with:
    files: dist/*
    generate_release_notes: true
```

내부 파이프라인 재사용을 넘어서 외부 배포 채널까지 연결하고 싶다면 Release가 자연스러운 다음 단계입니다. 태그 푸시와 묶으면 릴리스 절차도 코드화할 수 있습니다.

### 5단계 — 보관 정책 정하기

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: nightly-build
    path: dist/
    retention-days: 7
```

보관 기간을 정하지 않으면 기본값이 누적됩니다. 빌드가 자주 도는 저장소일수록 이 설정은 비용과 직결됩니다.

## 이 코드에서 먼저 봐야 할 점

- `retention-days`는 스토리지 비용과 보관 정책을 함께 제어합니다.
- `generate_release_notes`는 릴리스 설명 작성 비용을 줄여 줍니다.
- `download-artifact`는 같은 워크플로우 안에서만 동작합니다.

즉, 아티팩트는 단순한 저장 기능이 아니라 빌드 결과물의 수명주기를 설계하는 도구입니다.

## 자주 하는 실수 다섯 가지

1. `upload-artifact@v3` 같은 오래된 버전을 그대로 씁니다.
2. 필요 없는 파일까지 전부 업로드해 비용을 키웁니다.
3. `retention-days`를 빼먹어 기본 보관 기간이 계속 누적됩니다.
4. 같은 이름의 아티팩트를 반복 업로드해 오류를 냅니다.
5. Release에 체크섬이나 서명을 붙이지 않습니다.

특히 마지막 실수는 공급망 보안 관점에서 중요합니다. 릴리스 파일이 있다면 무결성을 함께 보여 줄 수 있어야 신뢰가 생깁니다.

## 실무에서는 이렇게 생각합니다

성숙한 팀은 빌드 산출물만 저장하지 않습니다. checksum, SBOM, 테스트 리포트, 커버리지 결과까지 함께 남겨 두고, 필요하면 릴리스 파일에 서명도 붙입니다. 이렇게 해야 나중에 “무엇을 만들었고, 무엇을 배포했고, 어떤 검증을 통과했는가”를 한 번에 설명할 수 있습니다.

또한 아티팩트 이름도 대충 짓지 않습니다. `dist`, `reports`, `nightly-build`처럼 목적이 드러나는 이름을 쓰면, 실행 기록이 쌓였을 때도 읽기가 훨씬 쉽습니다.

## 체크리스트

- [ ] `upload-artifact@v7`를 사용한다.
- [ ] 보관 기간을 명시했다.
- [ ] 태그 푸시 시 Release 발행 흐름이 있다.
- [ ] 체크섬이나 서명 같은 무결성 정보가 붙는다.

## 연습 문제

1. `pytest` 리포트와 커버리지 파일을 하나의 아티팩트로 올려 보세요.
2. build 잡이 만든 결과를 deploy 잡에서 내려받아 사용해 보세요.
3. 태그 푸시 시 Release가 자동 발행되도록 구성해 보세요.

## 정리

아티팩트는 빌드 결과를 잡 사이에 전달하고, 실행 흔적을 남기고, 릴리스로 이어 주는 핵심 연결 고리입니다. 빌드 성공만으로 끝내지 말고, 무엇이 만들어졌는지 남기는 습관까지 파이프라인에 넣어야 실무에서 재현 가능성이 생깁니다.

다음 글에서는 Docker 빌드를 다룹니다. 아티팩트로 일반 파일 산출물을 다뤘다면, 이제 컨테이너 이미지를 어떻게 효율적으로 빌드하고 레지스트리에 올릴지 살펴볼 차례입니다.


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

- **`upload-artifact`와 `download-artifact`는 각각 언제 쓰일까요?**
  - 본문의 기준은 빌드 아티팩트를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **잡 사이에서 결과물을 넘길 때 아티팩트가 왜 유용할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`retention-days`는 비용과 어떤 관계가 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [GitHub Actions 101 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [GitHub Actions 101 (2/10): Workflow와 Job](./02-workflow-and-job.md)
- [GitHub Actions 101 (3/10): Trigger 이해하기](./03-triggers.md)
- [GitHub Actions 101 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- [GitHub Actions 101 (5/10): Lint와 Type Check](./05-lint-and-typecheck.md)
- **빌드 아티팩트 (현재 글)**
- Docker 빌드 (예정)
- 배포 자동화 (예정)
- Secret 관리 (예정)
- 실전 CI/CD 파이프라인 (예정)

<!-- toc:end -->

## 참고 자료

- [actions/upload-artifact](https://github.com/actions/upload-artifact)
- [actions/download-artifact](https://github.com/actions/download-artifact)
- [softprops/action-gh-release](https://github.com/softprops/action-gh-release)
- [About artifacts](https://docs.github.com/actions/using-workflows/storing-workflow-data-as-artifacts)

Tags: GitHubActions, Artifact, Build, Release, CICD
