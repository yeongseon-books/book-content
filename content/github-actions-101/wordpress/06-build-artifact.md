---
title: "바이브코딩을 위한 GitHub Actions 기초 (6/10): 빌드 아티팩트 관리"
series: github-actions-101
episode: 6
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- GitHubActions
- Artifact
- Build
- CICD
seo_description: "바이브코딩 프로젝트에서 빌드 결과물을 저장하고 잡 사이에서 전달하며 릴리스까지 연결하는 방법을 설명합니다."
---

# 바이브코딩을 위한 GitHub Actions 기초 (6/10): 빌드 아티팩트 관리

이 글은 바이브코딩을 위한 GitHub Actions 기초 시리즈의 6번째 글입니다.

AI의 도움으로 Python 패키지를 만들었습니다. CI에서 빌드도 성공했습니다. 그런데 다음 단계인 배포 잡에서 "파일이 없다"는 오류가 납니다. 빌드 잡에서 만든 `dist/*.whl` 파일이 배포 잡에는 없기 때문입니다. GitHub Actions의 각 잡은 독립된 가상 머신에서 실행됩니다. 한 잡이 끝나면 그 머신은 사라지고, 안에 있던 파일도 함께 사라집니다.

아티팩트는 이 문제를 해결하는 도구입니다. 빌드 잡이 결과물을 `upload-artifact`로 저장하고, 배포 잡이 `download-artifact`로 가져옵니다. 같은 파일이 잡 경계를 넘어서 이어집니다. 바이브코딩으로 만든 코드를 빌드하고 배포하는 파이프라인을 제대로 연결하려면 아티팩트 사용법을 알아야 합니다.

> 아티팩트는 빌드 결과물을 저장하는 옵션이 아닙니다. 빌드 잡과 배포 잡을 분리하면서도 "같은 파일"을 넘겨주는 인터페이스입니다.

---

## 이 글에서 다룰 문제
- `upload-artifact`와 `download-artifact`는 각각 언제 필요한가요?
- 빌드 결과를 배포 잡에 전달할 때 아티팩트가 왜 필요한가요?
- `retention-days`를 설정하지 않으면 스토리지 비용이 어떻게 쌓이나요?
- 테스트 리포트, 커버리지 결과도 아티팩트로 남겨야 하는 이유는 무엇일까요?
- 태그 push 시 GitHub Release를 자동으로 만들려면 어떻게 해야 할까요?

---

## 잡이 끝나면 파일은 사라진다

GitHub Actions 러너는 잡이 시작될 때 깨끗한 가상 머신을 받고, 잡이 끝나면 그 머신이 사라집니다. 이는 재현성 측면에서 좋은 구조이지만, "앞 잡에서 만든 파일을 뒤 잡에서 쓴다"는 패턴이 불가능하다는 의미이기도 합니다.

```text
build 잡 → dist/app-1.0.0.whl 생성 → 잡 종료 → 파일 소멸
deploy 잡 → dist/app-1.0.0.whl 없음 → 실패
```

아티팩트로 저장하면 이 연결이 가능해집니다.

### 핵심 용어 정리

| 용어 | 뜻 | 실무 포인트 |
|------|------|------|
| 아티팩트 | 워크플로우가 저장한 파일 묶음 | 잡 경계를 넘어 결과물을 전달합니다 |
| `upload-artifact` | 파일을 GitHub 스토리지에 업로드 | 잡 종료 후에도 파일을 유지합니다 |
| `download-artifact` | 같은 워크플로우 내 아티팩트 내려받기 | 재빌드 없이 앞 잡의 결과물을 씁니다 |
| `retention-days` | 아티팩트 보관 기간 | 기본 90일, CI 용도는 7일 이하로 충분합니다 |
| Release | GitHub 공식 배포 페이지 | 외부에 패키지를 공개할 때 씁니다 |

---

## Before / After

**아티팩트 없이 배포 잡이 다시 빌드하는 패턴**

```yaml
jobs:
  build:
    steps:
      - run: python -m build  # dist/ 생성

  deploy:
    needs: build
    steps:
      - run: python -m build  # 또 빌드 — 같은 결과인지 보장 안 됨
      - run: twine upload dist/*
```

build 잡과 deploy 잡에서 빌드가 두 번 실행됩니다. 환경이 미묘하게 다르면 결과물도 달라질 수 있습니다.

**아티팩트로 연결한 패턴**

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
          retention-days: 7

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v7
        with:
          name: dist
          path: dist/
      - run: twine upload dist/*
        env:
          TWINE_TOKEN: ${{ secrets.PYPI_TOKEN }}
```

빌드는 한 번만 하고, 그 결과물을 배포 잡이 그대로 씁니다.

---

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| `retention-days` 없이 기본값 사용 | 90일 × 잦은 빌드 = 스토리지 누적 | CI 용도는 3-7일로 짧게 설정합니다 |
| 배포 잡에서 다시 빌드 | 두 빌드 결과물이 달라질 수 있음 | 아티팩트로 한 번 빌드한 결과를 전달합니다 |
| 민감한 파일을 아티팩트에 포함 | `.env`가 공개 저장소에 올라갈 수 있음 | `!` 패턴으로 민감 파일을 제외합니다 |
| 매트릭스 아티팩트에 같은 이름 사용 | 덮어쓰기로 일부 결과가 사라짐 | 이름에 `${{ matrix.os }}`를 포함합니다 |
| `if-no-files-found` 기본값 방치 | 빌드 실패로 파일 없어도 잡이 성공 | `error`로 설정합니다 |

## AI 팁: 아티팩트 연결 요청 프롬프트

```
프롬프트 예시:
"GitHub Actions에서 build 잡과 deploy 잡을 아티팩트로 연결해줘.
조건:
- build 잡: python -m build 후 dist/ 를 아티팩트로 업로드, retention-days 7
- deploy 잡: build 완료 후 아티팩트 다운로드, twine upload
- 태그 push 시에만 deploy 잡 실행
- if-no-files-found는 error로 설정"
```

아티팩트 이름에 버전이나 SHA를 포함하면 나중에 어떤 빌드인지 추적하기 좋습니다.

## 운영 체크리스트
- [ ] 빌드 결과물이 아티팩트로 저장되는가?
- [ ] `retention-days`가 적절하게 설정됐는가?
- [ ] 배포 잡이 아티팩트를 내려받아 사용하는가?
- [ ] `if-no-files-found: error`로 설정됐는가?
- [ ] 민감한 파일이 아티팩트에 포함되지 않는가?

## 처음 질문으로 돌아가기

- **아티팩트가 필요한 이유는?**
  각 잡은 독립된 가상 머신에서 실행되고, 잡이 끝나면 그 머신과 파일이 사라집니다. 잡 사이에 파일을 전달하려면 아티팩트가 유일한 방법입니다.

- **`retention-days`를 왜 짧게 설정해야 하나?**
  기본값은 90일이고, 저장소 무료 스토리지 한도(500MB)를 빠르게 소진합니다. CI 검증용 아티팩트는 7일이면 충분합니다. 영구 보관이 필요한 빌드 결과물은 GitHub Release에 첨부하세요.

- **테스트 리포트도 아티팩트로 올려야 하나?**
  네. 테스트가 실패했을 때 원인을 추적하려면 리포트가 필요합니다. `if: always()`를 달아야 실패 시에도 리포트가 올라갑니다.

## 정리

아티팩트는 잡 경계를 넘어서 결과물을 전달하는 핵심 연결 고리입니다. 빌드를 한 번만 하고 그 결과를 이후 잡에서 재사용하면 파이프라인의 신뢰성이 올라갑니다. 다음 글에서는 Docker 이미지를 빌드하고 레지스트리에 올리는 방법을 다룹니다.

## 참고 자료
### 공식 문서
- [actions/upload-artifact](https://github.com/actions/upload-artifact)
- [actions/download-artifact](https://github.com/actions/download-artifact)
### 관련 시리즈
- [Docker 101](../../docker-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 GitHub Actions 기초 (1/10): GitHub Actions란 무엇인가?](./01-what-is-github-actions.md)
- [바이브코딩을 위한 GitHub Actions 기초 (2/10): Workflow와 Job 구조 이해하기](./02-workflow-and-job.md)
- [바이브코딩을 위한 GitHub Actions 기초 (3/10): 트리거로 실행 시점 제어하기](./03-triggers.md)
- [바이브코딩을 위한 GitHub Actions 기초 (4/10): Python 테스트 자동화](./04-python-test-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (5/10): Lint와 Type Check 자동화](./05-lint-and-typecheck.md)
- **바이브코딩을 위한 GitHub Actions 기초 (6/10): 빌드 아티팩트 관리 (현재 글)**
- [바이브코딩을 위한 GitHub Actions 기초 (7/10): Docker 이미지 자동 빌드](./07-docker-build.md)
- [바이브코딩을 위한 GitHub Actions 기초 (8/10): 배포 자동화](./08-deploy-automation.md)
- [바이브코딩을 위한 GitHub Actions 기초 (9/10): Secret 안전하게 관리하기](./09-secret-management.md)
- [바이브코딩을 위한 GitHub Actions 기초 (10/10): 실전 CI/CD 파이프라인 조립](./10-real-world-cicd-pipeline.md)
<!-- toc:end -->
Tags: 바이브코딩, GitHubActions, Artifact, Build, CICD
