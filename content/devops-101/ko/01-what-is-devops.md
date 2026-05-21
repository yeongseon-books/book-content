---
series: devops-101
episode: 1
title: "DevOps 101 (1/10): DevOps란 무엇인가?"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - DevOps
  - Culture
  - CI
  - CD
  - Engineering
seo_description: 개발과 운영을 함께 책임지는 DevOps의 정의와 시작 방법을 정리합니다.
last_reviewed: '2026-05-12'
---

# DevOps 101 (1/10): DevOps란 무엇인가?

이 글은 DevOps 101 시리즈의 첫 번째 글입니다.

## 먼저 던지는 질문

- DevOps는 무엇이며, 왜 개발과 운영을 따로 보는 방식이 한계에 부딪혔을까요?
- DevOps를 도구가 아니라 문화라고 말하는 이유는 무엇일까요?
- CI, CD, SRE 같은 용어는 DevOps 흐름 안에서 어떤 역할을 할까요?

## 큰 그림

![DevOps 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/devops-101/01/01-01-diagram.ko.png)

*DevOps 101 1장 흐름 개요*

이 그림은 개발과 운영 조직 사이의 경계를 보여줍니다. DevOps는 이 경계를 낮추고, 둘이 함께 보고 배울 수 있도록 만드는 접근입니다.

> DevOps의 핵심은 속도나 도구가 아니라, 빠른 배포와 안정적인 운영을 상충하지 않는 같은 목표로 함께 추구하는 것입니다.

## 왜 중요한가

소프트웨어는 작성만으로 가치를 만들지 않습니다. 실제 사용자에게 도달하려면 빌드되고, 배포되고, 운영되어야 합니다. DevOps는 이 긴 흐름이 중간에서 끊기지 않도록 만드는 실무적 접근입니다.

많은 팀이 배포 속도와 운영 안정성을 서로 반대편에 놓고 생각합니다. 하지만 현장에서는 오히려 반대인 경우가 많습니다. 자주, 작게, 반복적으로 배포하는 팀이 문제를 더 빨리 발견하고 더 작게 되돌릴 수 있기 때문입니다.

> 빠른 배포와 안정적인 운영은 충돌하는 목표가 아닙니다. 같은 피드백 루프를 얼마나 짧게 돌릴 수 있는지가 둘을 함께 결정합니다.

## 한눈에 보는 개념

이 그림은 DevOps를 가장 단순하게 압축한 형태입니다. 코드를 작성하고, 검증하고, 배포하고, 운영하면서 얻은 신호가 다시 코드로 돌아와야 팀이 배웁니다. 이 루프가 끊기면 DevOps는 이름만 남고 실제 개선은 멈춥니다.

## 핵심 용어

- **Dev**: 소프트웨어를 설계하고 구현하는 개발 활동입니다.
- **Ops**: 서비스를 배포하고 운영하며 안정성을 유지하는 활동입니다.
- **CI**: 모든 커밋을 자동으로 통합하고 검증하는 흐름입니다.
- **CD**: 검증된 코드를 자동으로 배포 가능한 상태로 전달하는 흐름입니다.
- **SRE**: 운영을 코드와 시스템 설계 관점에서 다루는 엔지니어링 접근입니다.

용어 자체보다 중요한 것은 경계입니다. Dev와 Ops가 서로 책임을 넘기는 구조인지, 아니면 하나의 흐름을 함께 관리하는 구조인지에 따라 같은 도구를 써도 팀의 운영 품질은 크게 달라집니다.

## 전환 전후

## 데브옵스와 전통 운영 비교

DevOps를 처음 이해하려 할 때 가장 혼란스러운 부분은 이것이 기술이 아니라 문화 전환이라는 점입니다. 아래 표는 전통 운영과 DevOps가 같은 문제를 어떻게 다르게 풀어내는지 정리한 것입니다.

| 비교 기준 | 전통 운영 | DevOps |
|---|---|---|
| 배포 주기 | 분기별 또는 월별 대규모 배포 | 하루 수십 회 작은 배포 |
| 책임 경계 | Dev는 기능 개발, Ops는 운영 | Dev와 Ops가 함께 전체 라이프사이클 책임 |
| 피드백 루프 | 장애 → 원인 조사 → 개선 제안 → 다음 배포 (수주 ~ 수개월) | 장애 → 즉시 로그/메트릭 확인 → 롤백 또는 수정 (수분 ~ 수시간) |
| 도구 | 수동 스크립트, 문서, 콘솔 클릭 | CI/CD 파이프라인, IaC, 모니터링 자동화 |

전통 운영이 나쁘다는 말이 아닙니다. 다만 소프트웨어 출시 주기가 빨라지면서 분기 배포 구조는 점점 더 비용이 큽니다. DevOps는 그 비용을 줄이는 방법론입니다.

## 데브옵스 문화의 핵심 원칙

DevOps는 도구보다 먼저 문화입니다. 이 문화를 다섯 가지 원칙으로 압축한 것이 CALMS 프레임워크입니다.

### Culture (문화)

개발과 운영을 별개 조직으로 나누면 자연스럽게 칸막이가 생깁니다. DevOps는 이 경계를 낮추고, 둘이 같은 목표와 같은 데이터를 보도록 만드는 문화 전환입니다.

### Automation (자동화)

수동 작업은 반복될 때마다 실수와 편차를 낳습니다. 자동화는 사람 손을 덜어 주는 것이 아니라, 팀 기준을 코드로 고정하는 방법입니다.

### Lean (린)

작고 빠르게 실패하는 쪽이, 크고 느리게 완벽을 추구하는 것보다 장기적으로 더 안전합니다. 린은 이 원칙을 배포 흐름에 적용하는 방법입니다.

### Measurement (측정)

배포 빈도, 장애 복구 시간(MTTR), 변경 실패율, 리드 타임 같은 지표는 팀이 나아지고 있는지 객관적으로 보여 줍니다.

### Sharing (공유)

장애 포스트모템, 런북, 메트릭 대시보드는 팀 지식이 특정 개인에게만 쌓이지 않게 만듭니다. 결국 운영 안정성은 공유된 지식에서 나옵니다.

## 파이썬 지속적 통합 스크립트 예제

CI는 거창한 플랫폼이 아니라 "PR마다 같은 검사를 자동으로 돌린다"는 원칙입니다. 아래는 GitHub Actions로 Python 프로젝트 CI를 구성하는 최소 예제입니다.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install ruff
      - run: ruff check .

  test:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -r requirements.txt
      - run: pytest

  build:
    runs-on: ubuntu-latest
    needs: test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install build
      - run: python -m build
```

이 파이프라인은 린트 → 테스트 → 빌드 순서로 실행됩니다. 앞 단계가 실패하면 다음 단계는 건너뜁니다. 이 세 단계만으로도 코드 품질 합격선을 팀 시스템으로 고정할 수 있습니다.

**Before (분리된 조직)**

```text
- Dev team: "It works on my laptop"
- Ops team: "You broke it again"
- Deploys *once a quarter*, every time a *weekend overtime*
```

이 상태의 문제는 기술보다 구조에 있습니다. 개발팀은 기능을 넘기면 끝났다고 느끼고, 운영팀은 마지막 순간에 위험을 떠안습니다. 배포는 드물고 크며, 그래서 더 무서워집니다.

**After (DevOps)**

```text
- Every PR is merged after *passing CI*
- Capable of *dozens of deploys per day*
- Incidents are handled *together*; postmortems are run *together*
```

DevOps가 자리 잡은 팀은 개발과 운영을 조직도에서만 분리하지 않습니다. PR 단계에서부터 배포와 운영을 염두에 두고, 장애가 나도 같은 팀이 같은 데이터를 보며 대응합니다.

## 실전으로 시작하는 데브옵스 5단계

처음부터 거대한 플랫폼을 만들 필요는 없습니다. 작은 자동화 몇 개만 붙여도 팀의 피드백 속도는 눈에 띄게 달라집니다.

### 1단계 - Git 기반 협업

모든 변경이 같은 저장소와 같은 리뷰 흐름을 지나가야 합니다. DevOps의 출발점은 자동화보다 먼저, 변경 이력이 남고 함께 볼 수 있는 협업 구조입니다.

```bash
git checkout -b feat/login
# after changes
git commit -m "feat(auth): add login form"
git push origin feat/login
# open a PR
```

### 2단계 - CI 자동화

PR마다 같은 검사를 자동으로 돌리면 리뷰어의 감각이 아니라 팀의 기준이 코딩됩니다. 이 지점부터 "누가 확인했는가"보다 "무엇을 통과했는가"가 중요해집니다.

```yaml
# .github/workflows/ci.yml
on: [pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pytest
```

### 3단계 - 자동 배포 한 줄 추가

검증을 통과한 코드는 사람이 매번 기억으로 배포하는 대신, 일관된 절차로 흘러가야 합니다. 배포가 코드와 분리되어 있으면 운영은 계속 불안정해집니다.

```yaml
deploy:
  needs: test
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    - run: ./deploy.sh
```

### 4단계 - 모니터링 붙이기

배포를 자동화했다면 그다음은 상태를 읽는 눈이 필요합니다. 가장 작은 시작은 서비스가 살아 있는지 알려 주는 헬스 체크 하나입니다.

```python
# a one-line health check
@app.get("/health")
def health(): return {"status": "ok"}
```

### 5단계 - 장애 포스트모템 시작

문제가 발생했을 때 사람을 탓하는 대신 시스템과 절차를 고쳐야 루프가 닫힙니다. DevOps는 배포 자동화만이 아니라, 장애를 학습으로 바꾸는 문화까지 포함합니다.

```text
- What happened
- Why was the discovery late
- How will we know faster next time
```

## 이 코드에서 먼저 봐야 할 점

- 출발점은 거대한 전환이 아니라 작은 자동화입니다.
- 개발과 운영이 같은 저장소와 같은 변경 이력을 봅니다.
- 팀의 기준이 사람 머릿속이 아니라 코드와 설정으로 남습니다.

이 세 가지가 모이면 배포와 운영이 특정 개인의 경험에 덜 의존하게 됩니다. 결국 DevOps는 일을 더 복잡하게 만드는 것이 아니라, 반복되는 수작업과 기억 의존을 줄여 팀을 더 예측 가능하게 만드는 방식입니다.

## 자주 하는 실수 5가지

1. **DevOps를 부서 이름으로만 이해하는 실수**입니다. DevOps는 조직 라벨이 아니라 협업 방식입니다.
2. **도구만 도입하고 프로세스는 그대로 두는 실수**입니다. Jenkins를 설치해도 여전히 분기 배포라면 운영 방식은 거의 달라지지 않습니다.
3. **운영 책임을 특정 팀에만 떠넘기는 실수**입니다. 함께 만들었다면 함께 운영해야 합니다.
4. **자동화 자체에 과투자하는 실수**입니다. 한 번 하고 끝날 일을 위해 며칠짜리 자동화를 만드는 것은 좋은 DevOps가 아닙니다.
5. **장애 뒤에 사람을 탓하는 실수**입니다. 재발 방지는 사람 비난이 아니라 시스템 개선에서 나옵니다.

## 실무에서는 이렇게 이어집니다

성숙한 팀은 대개 작은 자동화에서 시작합니다. PR 테스트를 붙이고, main 머지 뒤 자동 배포를 연결하고, 기본 메트릭을 붙이고, 장애 회고를 정착시키는 식으로 반년 정도에 걸쳐 운영 습관을 바꿉니다.

중요한 점은 순서입니다. 처음부터 모든 것을 완벽하게 하려는 팀보다, 짧은 피드백 루프를 하나씩 실제 운영에 붙이는 팀이 더 오래 갑니다.

## 시니어 엔지니어는 이렇게 봅니다

- 모든 수작업은 자동화 후보입니다.
- 배포 빈도는 팀 건강도를 보여 주는 지표입니다.
- 장애는 시스템이 배우는 계기입니다.
- 개발과 운영은 하나의 팀으로 움직여야 합니다.
- 결국 모든 것은 피드백 루프의 길이가 결정합니다.

## 체크리스트

- [ ] 모든 PR에서 자동 테스트가 실행됩니다.
- [ ] main 머지가 자동 배포로 이어집니다.
- [ ] 기본 모니터링이 존재합니다.
- [ ] 장애 포스트모템이 정기적으로 운영됩니다.

## 연습 문제

1. 현재 프로젝트에서 사람이 직접 수행하는 배포 단계를 모두 적어 보세요.
2. 그중 자동화 후보 세 가지를 골라 보세요.
3. 가장 최근 장애를 세 문장으로 요약해 포스트모템 관점에서 다시 써 보세요.

## 정리 및 다음 단계

DevOps는 문화의 전환이자 피드백 루프의 설계입니다. 다음 글에서는 이 흐름의 첫 번째 지렛대인 CI 파이프라인을 더 구체적으로 다룹니다.

## 데브옵스 전환을 설계하는 실무 프레임

DevOps를 도구 목록으로 이해하면 팀은 빠르게 피로해집니다. Jenkins, GitHub Actions, Kubernetes, Terraform을 도입했는데도 릴리스가 느리고 장애는 반복되는 이유가 여기에 있습니다. 실무에서 효과가 나는 접근은 항상 동일합니다. 먼저 흐름을 나누고, 병목을 수치로 확인하고, 가장 작은 자동화부터 붙인 뒤, 운영 신호를 다시 개발 단계로 환류시키는 구조를 만듭니다. 이 순서를 지키면 DevOps는 유행어가 아니라 팀 운영 모델이 됩니다.

### DevOps와 전통 개발 운영 모델 비교

| 관점 | 전통 분리 모델 | DevOps 모델 | 실무 영향 |
| --- | --- | --- | --- |
| 책임 구조 | 개발 완료 후 운영 이관 | 개발부터 운영까지 공동 책임 | 장애 책임 공방 감소 |
| 배포 단위 | 큰 묶음, 저빈도 배포 | 작은 변경, 고빈도 배포 | 롤백 비용 축소 |
| 검증 방식 | 릴리스 직전 집중 검증 | PR 단계부터 연속 검증 | 결함 조기 발견 |
| 장애 대응 | 운영팀 단독 대응 | 서비스 팀 합동 대응 | MTTR 단축 |
| 개선 루프 | 분기 단위 회고 | 주간/일일 피드백 루프 | 학습 속도 향상 |

이 표에서 중요한 포인트는 도구가 아니라 책임 이동입니다. DevOps는 개발자가 운영자가 된다는 뜻이 아니라, 서비스 결과에 대한 책임 경계를 앞당긴다는 의미입니다. PR을 올리는 순간부터 배포와 관측성을 함께 고려하도록 팀 습관을 바꾸는 것이 핵심입니다.

### CALMS 프레임워크로 DevOps 성숙도 읽기

CALMS는 Culture, Automation, Lean, Measurement, Sharing 다섯 축으로 DevOps를 점검하는 프레임입니다. 팀이 어디서 막히는지 진단할 때 매우 유용합니다.

| 축 | 확인 질문 | 초기 팀의 흔한 상태 | 개선 방향 |
| --- | --- | --- | --- |
| Culture | 장애를 함께 복기하는가 | 팀 간 책임 분리 | 합동 포스트모템 |
| Automation | 수동 배포가 남아 있는가 | 특정 인력 의존 배포 | CI/CD 단계 자동화 |
| Lean | 대기 시간이 긴 단계는 어디인가 | 승인/리뷰 병목 | WIP 제한, 작은 PR |
| Measurement | 공통 지표가 있는가 | 감각 기반 판단 | DORA+SLO 측정 |
| Sharing | 운영 지식이 문서화되는가 | 개인 노하우 편중 | 런북/체크리스트 축적 |

CALMS는 성숙도 점수표가 아니라 대화 도구입니다. 예를 들어 자동화 수준이 높아도 Culture와 Sharing이 약하면 장애 시 대응 품질이 급격히 떨어집니다. 반대로 문화는 좋아도 Measurement가 없으면 개선 우선순위를 합의하기 어렵습니다. 다섯 축을 균형 있게 관리해야 실제 성능이 올라갑니다.

### 최소 실행 단위: 2주 DevOps 부트스트랩

첫 2주에 모든 체계를 갖출 필요는 없습니다. 아래처럼 작게 시작해도 효과가 큽니다.

```yaml
week_1:
  - pr_required_checks: [lint, test]
  - deployment: "main merge -> stage auto deploy"
  - observability: "health endpoint + basic error metric"
week_2:
  - runbook: "top 3 failure scenarios"
  - postmortem_template: "blameless + action owner"
  - weekly_review: "deploy count, failure count, lead time"
```

핵심은 도입 항목 수가 아니라 루프 길이입니다. 검증, 배포, 관측, 회고가 같은 주 안에서 한 번이라도 순환하면 팀은 즉시 학습을 시작합니다. 이후 도구 확장은 그다음 문제입니다.

### 도입 우선순위 결정 규칙

1. 장애 비용이 큰 구간부터 자동화합니다.
2. 배포 전 대기 시간을 만드는 단계를 먼저 줄입니다.
3. 사람이 기억으로 수행하는 절차는 모두 문서화 후 자동화 후보로 등록합니다.
4. 새 도구 도입 전, 기존 도구로 해결 가능한지 먼저 검토합니다.

이 규칙을 따르면 DevOps 전환이 도구 쇼핑이 되지 않습니다. 결국 좋은 DevOps는 기술 스택의 화려함이 아니라, 팀이 반복 가능하게 일하는 방식에 의해 결정됩니다.


## 운영 앵커: 배포, 인프라, 관측성, 대응을 한 장으로 연결하기

앞선 섹션에서 각 주제를 따로 설명했다면, 이 섹션은 실무에서 한 번에 연결해 쓰는 최소 구성 예시를 제공합니다. 핵심은 화려한 도구 조합이 아니라, 같은 기준으로 변경을 통과시키고 문제를 되돌릴 수 있는가입니다.

### CI/CD 파이프라인 공통 YAML

```yaml
name: delivery-flow
on:
  pull_request:
  push:
    branches: [main]

jobs:
  ci:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install -r requirements-dev.txt
      - run: ruff check .
      - run: pytest -q

  deploy-stage:
    needs: ci
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/deploy_stage.sh
      - run: ./scripts/smoke_test.sh https://stage.example.com

  deploy-prod-canary:
    needs: deploy-stage
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: ./scripts/deploy_prod.sh --strategy canary --percent 10
      - run: ./scripts/check_slo.sh --window 5m
      - run: ./scripts/promote_or_rollback.sh
```

이 흐름의 실전 포인트는 세 가지입니다. 첫째, CI 통과 전에는 어떤 배포도 시작하지 않습니다. 둘째, stage 통과 후에만 production으로 승격합니다. 셋째, production 승격은 canary 관찰 통과를 조건으로 강제합니다.

### Terraform과 Ansible 역할 분리 예시

```hcl
# infra/main.tf
resource "aws_security_group" "api" {
  name        = "api-sg"
  description = "api security group"
}

resource "aws_instance" "api" {
  ami           = var.ami
  instance_type = "t3.small"
  tags = {
    service = "api"
    env     = var.env
  }
}
```

```yaml
# ops/playbooks/hardening.yml
- hosts: api
  become: true
  tasks:
    - name: Install security updates
      apt:
        update_cache: true
        upgrade: dist

    - name: Ensure auditd is installed
      apt:
        name: auditd
        state: present

    - name: Ensure ssh root login is disabled
      lineinfile:
        path: /etc/ssh/sshd_config
        regexp: '^PermitRootLogin'
        line: 'PermitRootLogin no'
```

Terraform은 "무엇을 만들 것인가"를 선언하고, Ansible은 "만들어진 시스템을 어떤 상태로 유지할 것인가"를 담당합니다. 두 도구를 구분하면 변경 리뷰 범위가 명확해지고, 장애 시 원인 추적도 빨라집니다.

### 모니터링/알림 설정 예시

```yaml
# monitoring/alerts.yml
groups:
  - name: api-slo
    rules:
      - alert: ApiHighErrorRate
        expr: rate(http_requests_total{service="api",status=~"5.."}[5m]) / rate(http_requests_total{service="api"}[5m]) > 0.01
        for: 5m
        labels:
          severity: page
        annotations:
          summary: "API 5xx 비율 1% 초과"
          runbook: "https://internal/wiki/runbooks/api-high-error-rate"

      - alert: ApiHighLatencyP95
        expr: histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket{service="api"}[5m])) by (le)) > 0.35
        for: 10m
        labels:
          severity: warning
```

알림은 많이 울리는 것이 목표가 아닙니다. 운영자가 실제로 행동할 수 있는 신호만 남기고, 모든 page 알림에 runbook 링크를 붙여 대응 시작 시간을 줄여야 합니다.

### 블루그린/카나리 승격 절차 예시

```bash
# blue-green switch
./scripts/deploy_blue.sh
./scripts/smoke_test.sh https://blue.example.com
./scripts/switch_traffic.sh --from green --to blue

# canary rollout
./scripts/deploy_canary.sh --percent 10
./scripts/check_metrics.sh --window 5m
./scripts/promote_canary.sh --to 50
./scripts/promote_canary.sh --to 100
```

블루그린은 즉시 전환과 즉시 롤백에 유리하고, 카나리는 위험을 작게 나눠 검증하는 데 유리합니다. 서비스 특성과 팀 역량에 따라 전략을 고르되, 승격/철수 명령을 반드시 런북과 자동화 스크립트로 함께 유지해야 합니다.

### 인시던트 대응 런북 예시

```markdown
# Runbook: API 5xx 급증

## 0-5분
1. SEV 판정 (SEV1/SEV2)
2. incident 채널 개설
3. 최근 배포 커밋 확인

## 5-10분
1. canary/최근 릴리스 롤백 시도
2. 에러율, p95, DB 연결수 확인
3. 고객 영향 범위 요약 공지

## 10-20분
1. 임시 완화 조치 적용
2. 영구 수정 owner 지정
3. postmortem 일정 예약
```

운영에서는 "잘 아는 사람"보다 "같은 순서를 따르는 팀"이 더 빠르게 복구합니다. 그래서 runbook은 설명 문서가 아니라 실행 문서여야 하며, 경보에서 한 번에 열 수 있어야 합니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

### 운영 메모

운영 품질을 높이려면 변경 단위를 작게 유지하고, 실패 신호를 빠르게 드러내고, 되돌림 경로를 배포 설계에 포함해야 합니다. 또한 지표 해석과 대응 절차를 팀 공통 언어로 문서화해 개인 경험 의존도를 줄여야 합니다. 이 원칙이 지켜질 때 배포 속도와 안정성을 함께 올릴 수 있습니다.

## 처음 질문으로 돌아가기

- **DevOps는 무엇이며, 왜 개발과 운영을 따로 보는 방식이 한계에 부딪혔을까요?**
  - 본문의 기준은 DevOps란 무엇인가?를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **DevOps를 도구가 아니라 문화라고 말하는 이유는 무엇일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **CI, CD, SRE 같은 용어는 DevOps 흐름 안에서 어떤 역할을 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **DevOps란 무엇인가? (현재 글)**
- CI 파이프라인 (예정)
- CD와 배포 전략 (예정)
- 환경 분리와 설정 관리 (예정)
- Infrastructure as Code (예정)
- 컨테이너와 빌드 (예정)
- 모니터링과 알림 (예정)
- 로그 수집과 분석 (예정)
- 장애 대응과 on-call (예정)
- 운영 가능한 DevOps 흐름 (예정)

<!-- toc:end -->

## 참고 자료

- [The Phoenix Project (Gene Kim)](https://itrevolution.com/product/the-phoenix-project/)
- [Google SRE Book](https://sre.google/books/)
- [Atlassian DevOps Guide](https://www.atlassian.com/devops)
- [DORA State of DevOps](https://dora.dev/)

- [이 시리즈의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/devops-101/ko)

Tags: DevOps, Culture, CI, CD, Engineering
