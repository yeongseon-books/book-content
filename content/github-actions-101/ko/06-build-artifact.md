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


![GitHub Actions 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/github-actions-101/06/06-01-diagram.ko.png)
*GitHub Actions 101 6장 흐름 개요*

## 먼저 던지는 질문

- `upload-artifact`와 `download-artifact`는 각각 언제 쓰일까요?
- 잡 사이에서 결과물을 넘길 때 아티팩트가 왜 유용할까요?
- `retention-days`는 비용과 어떤 관계가 있을까요?

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


---

## 아티팩트의 생명 주기를 이해하겠습니다

아티팩트는 워크플로우 실행 안에서 생성되고, 설정된 보관 기간이 지나면 자동으로 삭제됩니다. 이 생명 주기를 이해하면 비용과 편의 사이의 균형을 잡을 수 있습니다.

| 시점 | 동작 | 비용 영향 |
| --- | --- | --- |
| 잡 실행 중 | upload-artifact로 저장 | 전송 시간 발생 |
| 같은 워크플로우 실행 내 | download-artifact로 다른 잡에서 가져오기 | 전송 시간 발생 |
| 실행 완료 후 | Actions UI에서 다운로드 가능 | 스토리지 비용 |
| retention-days 경과 | 자동 삭제 | 비용 해소 |

기본 보관 기간은 90일이지만, CI 용도로는 1-7일이면 충분합니다. 릴리스 아티팩트는 GitHub Release에 첨부하는 편이 보관과 접근성 모두 좋습니다.

### 아티팩트 크기 제한과 최적화

| 제한 | 값 |
| --- | --- |
| 단일 아티팩트 최대 크기 | 10 GB |
| 저장소당 총 아티팩트 용량 (Free) | 500 MB |
| 저장소당 총 아티팩트 용량 (Pro) | 2 GB |
| 업로드 동시성 | 파일당 병렬 청크 |

용량을 줄이는 실용적인 방법입니다.

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: dist
    path: |
      dist/*.whl
      dist/*.tar.gz
    # 불필요한 파일 제외
    if-no-files-found: error
    retention-days: 3
    compression-level: 6
```

`if-no-files-found: error`는 빌드가 실패해서 파일이 생성되지 않았을 때 명시적으로 실패하게 합니다. 기본값인 `warn`은 빈 아티팩트가 올라가도 잡이 성공으로 끝나서, 다음 잡에서 다운로드 실패로 이어질 수 있습니다.

---

## Python 패키지 빌드 전략

Python 프로젝트의 빌드 아티팩트는 보통 wheel(.whl)과 source distribution(.tar.gz)입니다.

### pyproject.toml 기반 빌드

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"

      - name: 빌드 도구 설치
        run: pip install build

      - name: 패키지 빌드
        run: python -m build

      - name: 빌드 결과 확인
        run: |
          ls -la dist/
          pip install twine
          twine check dist/*

      - uses: actions/upload-artifact@v7
        with:
          name: dist-${{ github.sha }}
          path: dist/
          retention-days: 7
```

`twine check`는 패키지 메타데이터가 올바른지 검증합니다. PyPI에 업로드하기 전에 이 검사를 통과해야 업로드 실패를 방지할 수 있습니다.

### 버전 관리와 아티팩트 이름

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.value }}
    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0  # git describe에 필요

      - id: version
        run: |
          VERSION=$(python -c "import tomllib; print(tomllib.load(open('pyproject.toml','rb'))['project']['version'])")
          echo "value=${VERSION}" >> "$GITHUB_OUTPUT"

      - run: python -m build

      - uses: actions/upload-artifact@v7
        with:
          name: myapp-${{ steps.version.outputs.value }}
          path: dist/
```

아티팩트 이름에 버전을 포함하면 나중에 어떤 빌드가 어떤 버전인지 즉시 파악할 수 있습니다.

---

## 잡 간 아티팩트 전달 패턴

빌드 결과를 다음 잡(테스트, 배포)에서 사용하는 패턴입니다.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: python -m build
      - uses: actions/upload-artifact@v7
        with:
          name: dist
          path: dist/

  test-install:
    needs: build
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python-version }}

      - uses: actions/download-artifact@v7
        with:
          name: dist
          path: dist/

      - name: wheel 설치 테스트
        run: |
          pip install dist/*.whl
          python -c "import myapp; print(myapp.__version__)"

  publish:
    needs: [build, test-install]
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    permissions:
      id-token: write  # PyPI trusted publishing
    steps:
      - uses: actions/download-artifact@v7
        with:
          name: dist
          path: dist/

      - name: PyPI 배포
        uses: pypa/gh-action-pypi-publish@release/v1
```

이 워크플로우의 흐름입니다.

1. **build**: 한 번만 빌드해서 아티팩트를 저장합니다.
2. **test-install**: 여러 환경에서 wheel 설치를 검증합니다. 빌드된 패키지가 실제로 설치 가능한지 확인하는 단계입니다.
3. **publish**: 태그 push일 때만 PyPI에 배포합니다. Trusted publishing으로 토큰 없이 배포합니다.

핵심은 "한 번 빌드, 여러 번 검증, 한 번 배포"입니다. 매 잡에서 다시 빌드하면 환경 차이로 결과가 달라질 수 있습니다.

---

## GitHub Release와 아티팩트 연결

아티팩트는 임시 저장소이고, 영구 보관이 필요한 빌드 결과물은 GitHub Release에 첨부하는 편이 좋습니다.

```yaml
jobs:
  release:
    if: startsWith(github.ref, 'refs/tags/v')
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: python -m build

      - name: Release 생성
        uses: softprops/action-gh-release@v2
        with:
          files: |
            dist/*.whl
            dist/*.tar.gz
          generate_release_notes: true
          draft: false
          prerelease: ${{ contains(github.ref, 'rc') || contains(github.ref, 'beta') }}
```

`generate_release_notes: true`는 이전 릴리스 이후의 커밋과 PR을 자동으로 릴리스 노트에 포함합니다. `prerelease` 플래그는 태그에 `rc`나 `beta`가 포함되면 자동으로 프리릴리스로 표시합니다.

---

## 멀티 플랫폼 빌드와 아티팩트 병합

C 확장이 있는 Python 패키지나 바이너리를 배포해야 할 때는 여러 OS에서 빌드한 결과를 하나로 모아야 합니다.

```yaml
jobs:
  build-wheels:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
      - run: pip install build
      - run: python -m build --wheel

      - uses: actions/upload-artifact@v7
        with:
          name: wheel-${{ matrix.os }}
          path: dist/*.whl

  merge-and-publish:
    needs: build-wheels
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v7
        with:
          path: all-wheels/
          pattern: wheel-*
          merge-multiple: true

      - run: ls -la all-wheels/
      # 모든 플랫폼의 wheel이 한 디렉터리에 모입니다
```

`merge-multiple: true`는 여러 아티팩트를 하나의 디렉터리로 병합합니다. 매트릭스에서 각 OS별로 업로드한 wheel을 한 곳에 모아 릴리스에 첨부하거나 PyPI에 업로드할 수 있습니다.

---

## 빌드 캐시 전략

빌드 시간을 줄이는 또 다른 방법은 중간 결과물을 캐시하는 것입니다.

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      .mypy_cache
      .ruff_cache
      .pytest_cache
    key: build-${{ runner.os }}-${{ hashFiles('pyproject.toml', 'requirements*.txt') }}
    restore-keys: |
      build-${{ runner.os }}-
```

캐시와 아티팩트의 차이를 명확히 이해해야 합니다.

| 구분 | 캐시 | 아티팩트 |
| --- | --- | --- |
| 목적 | 실행 속도 향상 | 잡 간 결과물 전달 |
| 접근 범위 | 같은 저장소의 모든 워크플로우 | 같은 워크플로우 실행 내 |
| 키 | 해시 기반 매칭 | 이름 기반 |
| 보관 기간 | 7일 미사용 시 제거 | retention-days 설정 |
| UI 다운로드 | 불가 | 가능 |

캐시는 "같은 작업을 빠르게 반복"할 때, 아티팩트는 "결과물을 다음 단계로 넘길 때" 사용합니다.

---

## 아티팩트 보안 고려사항

아티팩트에 민감한 정보가 포함되지 않도록 주의해야 합니다.

1. **환경 변수나 시크릿이 빌드 결과물에 포함되지 않았는지 확인합니다.** `.env` 파일이나 설정 파일이 아티팩트에 섞이면 다른 잡이나 UI 다운로드를 통해 노출될 수 있습니다.
2. **아티팩트 접근 권한을 이해합니다.** 같은 워크플로우 실행 내의 모든 잡이 아티팩트를 다운로드할 수 있습니다. fork에서 온 PR의 워크플로우에서 생성된 아티팩트도 원본 저장소에서 접근 가능합니다.
3. **retention을 최소한으로 설정합니다.** 필요한 기간만큼만 보관하면 노출 위험과 스토리지 비용을 동시에 줄입니다.

```yaml
- uses: actions/upload-artifact@v7
  with:
    name: build-output
    path: |
      dist/
      !dist/**/*.env
      !dist/**/config.local.*
    retention-days: 1
```

`!` 패턴으로 민감할 수 있는 파일을 명시적으로 제외하면 실수를 방지할 수 있습니다.


---

## 아티팩트 다운로드 자동화와 워크플로우 간 공유

같은 워크플로우 실행 내에서는 `download-artifact`로 간단히 공유할 수 있지만, 다른 워크플로우에서 생성된 아티팩트를 가져와야 할 때는 추가 설정이 필요합니다.

### workflow_run을 활용한 워크플로우 간 아티팩트 전달

```yaml
# .github/workflows/deploy.yml
name: deploy
on:
  workflow_run:
    workflows: ["build"]
    types: [completed]
    branches: [main]

jobs:
  deploy:
    if: github.event.workflow_run.conclusion == 'success'
    runs-on: ubuntu-latest
    steps:
      - name: 빌드 아티팩트 다운로드
        uses: actions/download-artifact@v7
        with:
          name: dist
          path: dist/
          github-token: ${{ secrets.GITHUB_TOKEN }}
          run-id: ${{ github.event.workflow_run.id }}

      - name: 배포
        run: ./scripts/deploy.sh
```

`workflow_run` 이벤트는 다른 워크플로우가 완료된 후에 실행됩니다. `run-id`를 지정하면 해당 실행의 아티팩트를 가져올 수 있습니다. 이 패턴은 빌드와 배포를 완전히 분리하면서도 아티팩트를 공유할 수 있어, 보안과 관심사 분리 모두에 유리합니다.

### API를 통한 아티팩트 접근

프로그래밍 방식으로 아티팩트에 접근해야 할 때는 GitHub REST API를 사용합니다.

```yaml
- name: 최근 성공 빌드의 아티팩트 다운로드
  run: |
    ARTIFACT_URL=$(gh api repos/${{ github.repository }}/actions/artifacts \
      --jq '.artifacts[] | select(.name == "dist") | .archive_download_url' \
      | head -1)
    
    curl -L -H "Authorization: token ${{ secrets.GITHUB_TOKEN }}" \
      "$ARTIFACT_URL" -o artifact.zip
    unzip artifact.zip -d dist/
```

이 방법은 유연하지만 복잡하므로, 가능하면 `download-artifact` 액션이나 `workflow_run` 패턴을 우선 사용하는 편이 좋습니다.

---

## 빌드 재현성 보장

"로컬에서는 빌드되는데 CI에서는 안 된다"는 문제를 방지하려면 빌드 재현성을 의식적으로 관리해야 합니다.

```yaml
- name: 빌드 환경 기록
  run: |
    python --version >> build-env.txt
    pip --version >> build-env.txt
    pip freeze >> build-env.txt
    echo "OS: $(uname -a)" >> build-env.txt
    echo "Date: $(date -u)" >> build-env.txt

- uses: actions/upload-artifact@v7
  with:
    name: build-env-${{ github.sha }}
    path: build-env.txt
    retention-days: 30
```

빌드 환경 정보를 아티팩트로 남기면 나중에 "이 빌드는 어떤 환경에서 만들어졌는가"를 추적할 수 있습니다. 장애 회고에서 유용합니다.

재현성을 높이는 추가 방법입니다.

- **잠금 파일 사용**: `pip-compile`로 생성한 `requirements.lock`을 CI에서 사용합니다.
- **Python 버전 고정**: `"3.12"`가 아니라 `"3.12.4"`처럼 패치 버전까지 고정합니다.
- **빌드 도구 버전 고정**: `pip install build==1.2.1`처럼 빌드 도구도 버전을 고정합니다.


## 처음 질문으로 돌아가기

- **`upload-artifact`와 `download-artifact`는 각각 언제 쓰일까요?**
  - `upload-artifact`는 잡이 생성한 결과물(빌드 산출물, 테스트 리포트, 로그)을 워크플로우 실행에 저장할 때 씁니다. `download-artifact`는 이전 잡이 저장한 아티팩트를 다음 잡에서 가져올 때 씁니다. "한 번 빌드, 여러 번 검증"이라는 패턴이 이 두 액션 위에서 동작합니다.
- **잡 사이에서 결과물을 넘길 때 아티팩트가 왜 유용할까요?**
  - 잡은 서로 다른 러너에서 실행되므로 파일시스템을 공유하지 않습니다. `outputs`는 짧은 문자열만 전달할 수 있고, 빌드된 wheel이나 테스트 리포트 같은 파일은 아티팩트로만 넘길 수 있습니다. 매 잡에서 다시 빌드하면 환경 차이로 결과가 달라질 위험도 있으므로, 한 번 빌드한 결과를 아티팩트로 공유하는 편이 안정적입니다.
- **`retention-days`는 비용과 어떤 관계가 있을까요?**
  - 아티팩트는 보관 기간 동안 스토리지를 차지하고, Free 플랜에서는 500MB, Pro에서는 2GB가 한도입니다. retention-days를 90일(기본값)로 두면 며칠 분의 빌드 아티팩트가 누적되어 한도에 금방 도달합니다. CI 용도로는 1-3일, 릴리스는 GitHub Release에 별도 첨부하는 구조가 비용을 합리적으로 유지합니다.

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
- [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/)
- [book-examples 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/github-actions-101/ko)

Tags: GitHubActions, Artifact, Build, Release, CICD
