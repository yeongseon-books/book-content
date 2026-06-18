---
title: "바이브코딩을 위한 GitHub Actions 기초 (4/10): Python 테스트 자동화"
series: github-actions-101
episode: 4
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- GitHubActions
- Python
- Pytest
- CICD
seo_description: "바이브코딩으로 만든 Python 코드를 GitHub Actions에서 자동으로 테스트하는 방법을 설명합니다."
---

# 바이브코딩을 위한 GitHub Actions 기초 (4/10): Python 테스트 자동화

이 글은 바이브코딩을 위한 GitHub Actions 기초 시리즈의 4번째 글입니다.

AI에게 Python 코드를 만들어 달라고 하면 테스트 코드도 함께 만들어 줍니다. "pytest로 단위 테스트도 작성해줘"라고 하면 꽤 그럴싸한 테스트가 나옵니다. 문제는 그 테스트가 로컬에서만 돌아간다는 점입니다. CI에 올리면 "가상환경이 없다", "패키지 버전이 다르다", "환경 변수가 없다"는 이유로 실패하거나, 아예 테스트를 돌리는 단계가 워크플로우에 없습니다. 바이브코딩으로 테스트를 만들었다면 그 테스트가 PR마다 자동으로 돌아야 의미가 있습니다.

CI에서 Python 테스트를 제대로 실행하려면 환경 설정, 캐시, 결과 보관까지 연결해야 합니다. `setup-python`으로 Python 버전을 고정하고, pip 캐시로 설치 시간을 줄이고, `--junitxml`로 결과를 남기면 "PR마다 같은 환경에서 같은 명령이 실행되는" 상태가 됩니다. 이 상태가 되어야 바이브코딩으로 만든 코드의 품질 기준이 개인 로컬이 아닌 저장소 규칙으로 바뀝니다.

> 테스트 파일이 있는 것과 테스트가 자동으로 실행되는 것은 다른 단계입니다. CI에서 테스트가 돌아야 PR마다 품질이 보장됩니다.

---

## 이 글에서 다룰 문제
- `setup-python`과 pip 캐시를 함께 설정하면 어떤 효과가 있을까요?
- `pytest` 결과를 PR에서 바로 볼 수 있게 만들려면 무엇이 필요할까요?
- 커버리지는 어떻게 측정하고 PR에 표시할 수 있을까요?
- 여러 Python 버전에서 동시에 테스트를 돌리면 비용이 어떻게 달라질까요?
- 바이브코딩으로 만든 테스트에서 CI가 자주 실패하는 이유는 무엇일까요?

---

## 왜 로컬에서 되는데 CI에서 실패하나

바이브코딩으로 만든 테스트가 로컬에서는 통과하는데 CI에서 실패하는 가장 흔한 이유입니다.

1. **환경 변수 누락**: 로컬에 설정된 `.env` 파일이 CI에는 없습니다.
2. **Python 버전 불일치**: 로컬은 3.12인데 CI는 다른 버전을 씁니다.
3. **의존성 불완전**: 로컬 가상환경에는 있는데 `requirements.txt`에 빠진 패키지가 있습니다.
4. **외부 서비스 의존**: 실제 DB나 API에 연결하는 테스트를 목(mock) 없이 CI에서 돌립니다.

`setup-python`으로 버전을 고정하고 `pip install -e ".[dev]"`로 의존성을 명확히 설치하면 1, 2, 3번이 해결됩니다.

### 핵심 용어 정리

| 용어 | 뜻 | 실무 포인트 |
|------|------|------|
| `setup-python` | 러너에 Python을 설치하는 액션 | 버전 고정과 캐시 설정의 출발점입니다 |
| pip 캐시 | 의존성 설치 결과를 재사용하는 기능 | 설치 시간을 50-80% 줄입니다 |
| `junitxml` | 테스트 결과를 XML로 저장하는 형식 | PR 체크와 아티팩트에서 활용합니다 |
| coverage | 테스트가 닿은 코드 범위 측정 | 목표 숫자보다 추이를 보는 편이 중요합니다 |
| `if: always()` | 이전 스텝 실패 여부와 무관하게 실행 | 실패 시에도 리포트를 남기려면 필수입니다 |

---

## Before / After

**AI가 만든 기본 테스트 스텝**

```yaml
steps:
  - uses: actions/checkout@v6
  - run: pip install pytest
  - run: pytest
```

Python 버전이 고정되지 않고, 캐시도 없고, 결과도 남지 않습니다.

**실무 수준의 테스트 워크플로우**

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-python@v6
        with:
          python-version: "3.12"
          cache: "pip"

      - name: 의존성 설치
        run: pip install -e ".[dev]"

      - name: 테스트 실행
        run: pytest -q --junitxml=report.xml --cov=src --cov-report=xml

      - name: 테스트 리포트 업로드
        uses: actions/upload-artifact@v7
        if: always()
        with:
          name: pytest-report
          path: |
            report.xml
            coverage.xml
          retention-days: 7
```

Python 3.12로 고정되고, pip 캐시가 활성화됩니다. 실패해도 `if: always()` 덕분에 리포트가 아티팩트로 올라갑니다.

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `setup-python` 없이 pytest 실행 | Python 버전이 러너 기본값에 의존함 | 항상 버전을 명시합니다 |
| pip 캐시 없이 매번 전체 설치 | PR마다 2-3분이 의존성 설치에 소비됨 | `cache: "pip"` 한 줄이 시간을 줄입니다 |
| `if: always()` 없는 리포트 업로드 | 테스트 실패 시 리포트가 올라가지 않음 | 실패 원인을 볼 수 없게 됩니다 |
| 외부 API를 직접 호출하는 테스트 | 네트워크 상태에 따라 흔들리는 CI가 됨 | mock 또는 서비스 컨테이너를 씁니다 |
| 커버리지를 숫자 목표로만 추적 | 중요한 경로가 빠졌는지 모르고 수치만 봄 | diff 커버리지로 변화를 봅니다 |

## AI 팁: 테스트 워크플로우 요청 프롬프트

```
프롬프트 예시:
"Python pytest 테스트를 GitHub Actions에서 실행하는 워크플로우를 만들어줘.
조건:
- Python 3.12, pip 캐시 활성화
- pip install -e '.[dev]'로 의존성 설치
- pytest 결과를 JUnit XML로 저장, 항상 아티팩트로 업로드
- 커버리지 측정 후 XML 저장
- retention-days는 7일"
```

이렇게 요청하면 `if: always()` 처리를 포함한 워크플로우를 받을 수 있습니다. 받은 후에는 `cache-dependency-path`에 의존성 파일이 모두 포함됐는지 확인하세요.

## 운영 체크리스트
- [ ] `setup-python`으로 Python 버전이 고정됐는가?
- [ ] pip 캐시가 활성화됐는가?
- [ ] `junitxml` 결과를 아티팩트로 올리는가?
- [ ] `if: always()`로 실패해도 리포트가 남는가?
- [ ] 외부 서비스에 의존하는 테스트가 격리됐는가?

## 처음 질문으로 돌아가기

- **로컬에서 되는데 CI에서 실패하는 이유는?**
  가장 흔한 원인은 환경 변수 누락, Python 버전 불일치, 의존성 파일 불완전입니다. `setup-python`으로 버전을 고정하고 `pyproject.toml` 기반 설치를 쓰면 대부분 해결됩니다.

- **커버리지를 측정하는 것이 왜 유용한가?**
  AI가 테스트를 만들어 줘도 중요한 분기를 빠뜨릴 수 있습니다. 커버리지 숫자 자체보다 PR마다 커버리지가 낮아지는 변화를 잡는 것이 더 실용적입니다.

- **CI 테스트가 흔들릴 때 어떻게 하나?**
  외부 네트워크에 의존하는 테스트가 있는지 먼저 확인합니다. 있다면 mock으로 격리하거나 `services:`로 로컬 컨테이너를 띄웁니다.

## 정리

Python 테스트 자동화의 핵심은 "같은 환경에서 같은 명령을 반복 실행하게 만드는 것"입니다. `setup-python`, 캐시, `junitxml`, `if: always()` 네 가지 요소가 갖춰지면 바이브코딩으로 만든 테스트도 PR마다 신뢰할 수 있는 검증 게이트가 됩니다. 다음 글에서는 Lint와 타입 체크를 자동화해서 AI가 만든 코드의 스타일 문제를 PR 단계에서 잡는 방법을 다룹니다.

## 참고 자료
### 공식 문서
- [actions/setup-python](https://github.com/actions/setup-python)
- [pytest documentation](https://docs.pytest.org/)
### 관련 시리즈
- [Testing 101](../../testing-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 GitHub Actions 기초 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [바이브코딩을 위한 GitHub Actions 기초 (2/10): Workflow와 Job 구조 이해하기](./02-workflow-and-job.md)
- [바이브코딩을 위한 GitHub Actions 기초 (3/10): 트리거로 실행 시점 제어하기](./03-triggers.md)
- **바이브코딩을 위한 GitHub Actions 기초 (4/10): Python 테스트 자동화 (현재 글)**
- [바이브코딩을 위한 GitHub Actions 기초 (5/10): Lint와 Type Check 자동화](./05-lint-and-typecheck.md)
- [바이브코딩을 위한 GitHub Actions 기초 (6/10): 빌드 아티팩트 관리](./06-build-artifact.md)
- [바이브코딩을 위한 GitHub Actions 기초 (7/10): Docker 이미지 자동 빌드](./07-docker-build.md)
- [바이브코딩을 위한 GitHub Actions 기초 (8/10): 배포 자동화](./08-deploy-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (9/10): Secret 안전하게 관리하기](./09-secret-management.md)
- [바이브코딩을 위한 GitHub Actions 기초 (10/10): 실전 CI/CD 파이프라인 조립](./10-real-world-cicd-pipeline.md)
<!-- toc:end -->
Tags: 바이브코딩, GitHubActions, Python, Pytest, CICD
