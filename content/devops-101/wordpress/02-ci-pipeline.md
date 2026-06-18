---
title: "바이브코딩을 위한 DevOps 기초 (2/10): CI 파이프라인"
series: devops-101
episode: 2
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- DevOps
- AI코딩
seo_description: "바이브코딩으로 만든 코드를 팀이 함께 쓰려면 CI가 필수입니다. AI가 짠 코드도 자동으로 검증되는 CI 파이프라인 설계 원칙을 정리합니다."
---

# 바이브코딩을 위한 DevOps 기초 (2/10): CI 파이프라인

이 글은 바이브코딩을 위한 DevOps 기초 시리즈의 2번째 글입니다.

AI 코딩 도구로 빠르게 코드를 만들다 보면 이런 상황이 생깁니다. 어제 AI가 짜준 코드가 오늘 동료가 추가한 코드와 충돌합니다. 또는 로컬에서는 잘 되는데 서버에 올리면 에러가 납니다. AI가 코드를 빠르게 만들어 줄수록, 그 코드가 실제로 괜찮은지 자동으로 확인하는 장치가 더 중요해집니다.

CI(Continuous Integration)는 코드가 저장소에 들어올 때마다 자동으로 품질을 확인하는 흐름입니다. 린트, 타입 검사, 테스트, 보안 스캔이 사람이 기억하지 않아도 자동으로 돌아갑니다. AI가 짜준 코드도, 직접 짠 코드도, 이 관문을 통과해야 합니다.

AI에게 "GitHub Actions 파이프라인 만들어줘"라고 요청할 수 있습니다. 하지만 어떤 단계가 왜 필요한지 모르면, AI가 만들어준 파이프라인에서 무언가 빠졌을 때 알아채지 못합니다. CI 파이프라인은 단순한 자동화 스크립트가 아니라 팀의 코드 품질 기준을 코드로 고정한 것입니다.

> CI 없는 PR은 아직 검증되지 않은 가정에 가깝습니다.

---

## 이 글에서 다룰 문제
- CI 파이프라인은 단순한 테스트 자동화와 어떻게 다를까요?
- lint, test, build, scan 단계는 왜 한 흐름으로 묶여야 할까요?
- 빠른 피드백을 주는 파이프라인은 어떤 순서로 설계해야 할까요?
- AI가 만들어준 CI 설정에서 자주 빠지는 것은 무엇일까요?
- 파이프라인이 느리면 팀에 어떤 문제가 생길까요?

## CI 파이프라인이 없을 때 어떤 일이 생기는가

CI 없이 바이브코딩으로 빠르게 작업하다 보면 이런 패턴이 반복됩니다. 로컬에서 잘 되던 코드가 배포 후 에러를 냅니다. 리뷰어가 코드 스타일을 지적하는 데 시간이 소비됩니다. main에 들어간 코드가 기존 기능을 깨뜨립니다. CI는 이런 문제를 PR 단계에서 자동으로 잡아냅니다.

| 단계 | 역할 | 바이브코딩에서의 중요성 |
|---|---|---|
| Lint | 코드 스타일, 불필요한 변수 등 확인 | AI가 짠 코드도 스타일이 다를 수 있음 |
| Type check | 타입 오류 조기 발견 | AI 생성 코드의 타입 불일치를 빠르게 발견 |
| Test | 기능이 의도대로 작동하는지 확인 | AI가 만든 코드가 엣지 케이스를 처리하는지 검증 |
| Security scan | 의존성 취약점, 코드 보안 이슈 확인 | AI가 오래된 라이브러리를 추천할 수 있음 |

## CI 파이프라인을 설계하는 원칙

가장 빠르고 가장 저렴한 검사를 먼저 두어야 합니다. 문법 오류가 있는 코드를 10분짜리 테스트 끝까지 돌리는 것은 낭비입니다.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ruff mypy
      - run: ruff check .
      - run: mypy src/

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt pytest
      - run: pytest -q
```

`needs: lint`는 린트가 실패하면 테스트를 돌리지 않습니다. 가장 싼 실패를 먼저 확인하는 설계입니다.

## Before / After

**Before**: "AI가 짜준 코드를 그냥 main에 푸시했더니 기존 기능이 깨졌다. 누가 어디서 깨뜨렸는지 찾느라 1시간을 썼다."

**After**: "PR을 올리면 자동으로 린트, 타입 검사, 테스트가 돌아간다. AI가 생성한 코드가 기존 테스트를 깨뜨리면 PR 단계에서 바로 표시된다."

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|---|---|---|
| Required check를 설정하지 않는 실수 | 빨간 파이프라인인데도 머지가 가능해 CI 의미가 없어짐 | GitHub에서 Branch protection → Required status checks 설정 |
| 모든 단계를 직렬로 돌리는 실수 | 불필요하게 느려짐 | 독립적인 단계는 병렬로 실행 |
| CI가 로컬에서 재현 안 되는 실수 | 에러 원인을 찾으려면 CI를 계속 푸시해야 함 | act 같은 로컬 CI 실행 도구 활용 |
| 파이프라인이 20분 넘는 실수 | 개발자가 기다리다 다른 작업을 시작하고 피드백을 놓침 | 5분 내 피드백을 목표로 단계 최적화 |
| AI가 만든 설정을 검토 없이 사용 | 불필요한 권한, 시크릿 노출, 보안 이슈가 숨어 있을 수 있음 | AI 생성 CI 설정도 코드 리뷰 필수 |

## AI에게 CI 관련 질문하는 팁

CI 파이프라인을 AI에게 요청할 때 이 정보를 포함하면 더 정확한 결과를 받을 수 있습니다:

```
언어/프레임워크: [Python 3.12, FastAPI 등]
테스트 도구: [pytest, coverage 등]
원하는 단계: [lint, type check, test, security scan]
목표 피드백 시간: [5분 이내]
브랜치 정책: [main PR에만 실행]
```

AI가 만든 파이프라인을 받았다면 반드시 확인할 것: 단계 순서가 빠른 실패 원칙을 따르는지, Required check가 설명되어 있는지, 시크릿을 환경 변수로 안전하게 처리하는지.

## 운영 체크리스트

- [ ] PR이 올라가면 자동으로 lint와 test가 실행됩니다
- [ ] Required check가 설정되어 실패 시 머지를 막습니다
- [ ] 파이프라인 피드백 시간이 5분 이내입니다
- [ ] CI 실행 환경이 로컬에서 재현 가능합니다
- [ ] 보안 스캔 단계가 포함되어 있습니다

## 처음 질문으로 돌아가기

"AI가 코드를 짜주는데 CI 파이프라인이 왜 필요한가요?"

AI가 짜준 코드도 실수가 있을 수 있습니다. 타입이 맞지 않거나, 기존 기능을 깨뜨리거나, 보안 취약점이 있는 라이브러리를 쓸 수 있습니다. CI는 이런 문제를 사람이 기억하지 않아도 자동으로 잡아주는 안전망입니다. 바이브코딩으로 코드 생산 속도가 빨라질수록 이 안전망의 중요성도 함께 커집니다.

## 정리

CI 파이프라인은 팀의 코드 품질 기준을 자동화된 흐름으로 고정하는 장치입니다. AI가 코드를 빠르게 생성할수록 이 자동 검증 체계가 더 중요합니다. 다음 글에서는 CI를 통과한 코드를 안전하게 배포하는 CD와 배포 전략을 다룹니다.

## 참고 자료
### 공식 문서
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Martin Fowler — Continuous Integration](https://martinfowler.com/articles/continuousIntegration.html)
- [Trivy](https://trivy.dev/)
### 관련 시리즈
- [바이브코딩을 위한 DevOps 기초 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- [바이브코딩을 위한 소프트웨어 설계 기초](../../software-design-101/wordpress/)

---

<!-- toc:begin -->
## 시리즈 목차
- [바이브코딩을 위한 DevOps 기초 (1/10): DevOps란 무엇인가?](./01-what-is-devops.md)
- **바이브코딩을 위한 DevOps 기초 (2/10): CI 파이프라인 (현재 글)**
- [바이브코딩을 위한 DevOps 기초 (3/10): CD와 배포 전략](./03-cd-and-deployment.md)
- [바이브코딩을 위한 DevOps 기초 (4/10): 환경 분리와 설정 관리](./04-environments-and-config.md)
- [바이브코딩을 위한 DevOps 기초 (5/10): Infrastructure as Code](./05-infrastructure-as-code.md)
- [바이브코딩을 위한 DevOps 기초 (6/10): 컨테이너와 빌드](./06-containers-and-build.md)
- [바이브코딩을 위한 DevOps 기초 (7/10): 모니터링과 알림](./07-monitoring-and-alerting.md)
- [바이브코딩을 위한 DevOps 기초 (8/10): 로그 수집과 분석](./08-logging-and-analysis.md)
- [바이브코딩을 위한 DevOps 기초 (9/10): 장애 대응과 on-call](./09-incident-and-oncall.md)
- [바이브코딩을 위한 DevOps 기초 (10/10): 운영 가능한 DevOps 흐름](./10-operable-devops-flow.md)
<!-- toc:end -->

Tags: 바이브코딩, DevOps, AI코딩, CI, Pipeline
