---
title: "바이브코딩을 위한 pytest 기초 (9/10): CI와 GitHub Actions"
series: pytest-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - pytest
  - Testing
  - CI
  - GitHub Actions
---

# 바이브코딩을 위한 pytest 기초 (9/10): CI와 GitHub Actions

이 글은 "바이브코딩을 위한 pytest 기초" 시리즈의 9번째 글입니다.

---

바이브코딩에서 AI는 테스트 코드를 빠르게 만들어 줍니다. 그런데 로컬에서만 테스트를 실행하면 "내 환경에서는 됐는데"라는 문제가 반복됩니다. PR을 올리기 전에 테스트를 깜빡하거나, 특정 Python 버전에서만 발생하는 버그를 놓치거나, 팀원이 의존성을 다르게 설치한 환경에서 실패하는 경우가 생깁니다.

CI(Continuous Integration)는 코드가 저장소에 올라올 때마다 자동으로 테스트를 실행합니다. "테스트를 잊어버릴 수 없게" 만드는 구조입니다. GitHub Actions는 `.github/workflows/` 디렉터리에 YAML 파일을 두면 Push나 PR마다 자동으로 실행됩니다.

Python 프로젝트에서 중요한 것은 버전 매트릭스입니다. Python 3.10에서 잘 되던 코드가 3.12에서 타입 힌트 문법 차이로 실패할 수 있습니다. `strategy.matrix`로 여러 Python 버전을 한 번에 테스트하면 배포 전에 이를 발견할 수 있습니다.

AI가 만든 워크플로 파일에서는 커버리지 게이트, 의존성 캐싱, 버전 매트릭스 세 가지를 반드시 확인해야 합니다.

> **핵심 인사이트:** CI의 가치는 "자동으로 테스트를 실행한다"가 아니라 "테스트를 건너뛰는 것이 불가능한 구조를 만든다"입니다. PR 병합 전에 CI가 통과해야 한다는 규칙 하나가 테스트 문화를 만듭니다.

## 이 글에서 다룰 문제

- GitHub Actions 워크플로는 어떤 구조로 작성할까요?
- Python 버전 매트릭스는 왜 필요하고 어떻게 설정할까요?
- 의존성 캐싱은 CI 속도에 어떤 영향을 줄까요?
- 커버리지 게이트는 CI에서 어떻게 강제할까요?
- AI가 만든 워크플로 파일에서 확인해야 할 것은 무엇인가요?

## CI와 GitHub Actions 핵심 패턴

```yaml
# .github/workflows/test.yml
name: Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
      fail-fast: false   # 한 버전 실패해도 나머지 계속 실행

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Cache pip
        uses: actions/cache@v4
        with:
          path: ~/.cache/pip
          key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r requirements-dev.txt

      - name: Run tests with coverage
        run: |
          pytest --cov=src --cov-branch \
                 --cov-report=term-missing \
                 --cov-fail-under=80

      - name: Upload coverage report
        uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.12'
```

```yaml
# PR 병합 보호 설정 (GitHub Branch Protection Rules)
# Settings → Branches → Branch protection rules
# ✓ Require status checks to pass before merging
# ✓ test (3.10), test (3.11), test (3.12) 모두 필수
```

```ini
# pyproject.toml에 pytest 설정 통합
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
addopts = "--strict-markers"

[tool.coverage.run]
source = ["src"]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true
```

## 변경 전후 비교

**Before: 로컬에서만 테스트**
```text
- PR 전 테스트를 잊어버리는 경우 발생
- "내 환경에서는 됐는데" 반복
- 특정 Python 버전 호환성 문제 발견 못함
- 커버리지 게이트 없어서 점차 낮아짐
```

**After: CI로 자동 검증**
```text
- Push/PR 때마다 자동으로 테스트 실행
- Python 3.10/3.11/3.12 모두 병렬 테스트
- 커버리지 80% 미만이면 CI 실패
- PR 병합 전 CI 통과 필수로 강제
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| `fail-fast: true` (기본값) | 한 버전 실패 시 나머지 취소, 정보 손실 | `fail-fast: false` 설정 |
| 의존성 캐싱 없음 | CI 실행마다 패키지 재설치, 느림 | `actions/cache` 사용 |
| 커버리지 게이트 없음 | 커버리지가 점진적으로 낮아짐 | `--cov-fail-under=80` 추가 |
| main 브랜치만 CI 실행 | PR 시 검증 안 됨 | `pull_request` 트리거 추가 |
| Branch Protection 없음 | CI 실패해도 병합 가능 | GitHub Branch Protection 설정 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"Python 프로젝트를 위한 GitHub Actions 워크플로를 만들어줘.
Python 3.10/3.11/3.12 버전 매트릭스,
pytest-cov로 커버리지 80% 게이트,
pip 캐싱 포함,
PR과 main 브랜치 push 시 실행"

# AI 결과물 검증 체크포인트:
# - python-version matrix가 3개 이상 버전을 포함하는가?
# - fail-fast: false가 설정되어 있는가?
# - actions/cache로 pip 캐싱이 설정되어 있는가?
# - --cov-fail-under로 커버리지 게이트가 있는가?
# - pull_request 트리거가 포함되어 있는가?
```

## 운영 체크리스트

- [ ] `.github/workflows/test.yml`이 push와 pull_request에 모두 트리거된다
- [ ] Python 버전 매트릭스가 지원 범위를 커버한다
- [ ] `fail-fast: false`로 설정되어 있다
- [ ] `actions/cache`로 pip 의존성 캐싱이 설정되어 있다
- [ ] GitHub Branch Protection으로 CI 통과 전 PR 병합이 차단된다

## 처음 질문으로 돌아가기

- **CI와 로컬 테스트의 차이는?** 로컬은 개발자가 기억해야 실행합니다. CI는 코드가 올라올 때마다 자동으로 실행됩니다. "잊어버릴 수 없다"는 구조 차이가 팀 전체 테스트 습관을 만듭니다.
- **버전 매트릭스가 필요한 이유는?** Python 3.10의 `match` 문법, 3.12의 타입 힌트 변경 등 버전마다 동작이 다릅니다. 지원하는 Python 버전 전체를 CI에서 테스트해야 배포 후 버전 충돌을 피할 수 있습니다.
- **`fail-fast: false`는 언제 필요한가?** 기본값 `true`는 한 버전이 실패하면 나머지를 중단합니다. 버전 간 호환성 문제를 모두 파악하려면 `false`로 설정해 모든 버전의 결과를 봐야 합니다.

## 정리

바이브코딩에서 AI가 만들어 준 워크플로 파일에서 버전 매트릭스, `fail-fast: false`, 커버리지 게이트, pip 캐싱을 반드시 확인하세요. CI는 테스트를 "건너뛸 수 없는 구조"로 만드는 도구입니다. GitHub Branch Protection으로 CI 통과 전 PR 병합을 막으면 팀 전체의 테스트 문화가 자연스럽게 형성됩니다. 다음 글에서는 테스트하기 좋은 코드 설계를 다룹니다.

## 참고 자료

- [GitHub Actions — Python 공식 예시](https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-python)
- [actions/setup-python](https://github.com/actions/setup-python)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/pytest-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 pytest 기초 (1/10): pytest란 무엇인가?
- 바이브코딩을 위한 pytest 기초 (2/10): 첫 번째 테스트 작성
- 바이브코딩을 위한 pytest 기초 (3/10): assert와 예외 테스트
- 바이브코딩을 위한 pytest 기초 (4/10): 픽스처
- 바이브코딩을 위한 pytest 기초 (5/10): 파라미터화 테스트
- 바이브코딩을 위한 pytest 기초 (6/10): Mock과 패치
- 바이브코딩을 위한 pytest 기초 (7/10): 파일, 환경변수, 시간 테스트
- 바이브코딩을 위한 pytest 기초 (8/10): 커버리지
- **바이브코딩을 위한 pytest 기초 (9/10): CI와 GitHub Actions (현재 글)**
- 바이브코딩을 위한 pytest 기초 (10/10): 테스트하기 좋은 코드
<!-- toc:end -->

Tags: 바이브코딩, pytest, Testing, CI, GitHub Actions
