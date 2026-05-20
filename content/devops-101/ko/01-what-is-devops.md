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

## Before/After

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

## 실전으로 시작하는 DevOps 5단계

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

Tags: DevOps, Culture, CI, CD, Engineering
