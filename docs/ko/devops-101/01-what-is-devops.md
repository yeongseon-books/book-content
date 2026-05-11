---
series: devops-101
episode: 1
title: DevOps란 무엇인가?
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - DevOps
  - Culture
  - CI
  - CD
  - Engineering
seo_description: 개발과 운영을 잇는 DevOps의 정의, 원칙, 그리고 실무에서 시작하는 첫걸음.
last_reviewed: '2026-05-04'
---

# DevOps란 무엇인가?

> DevOps 101 시리즈 (1/10)


## 이 글에서 다룰 문제

소프트웨어는 *만들기* 만 해서는 가치를 내지 못합니다. *배포* 되고 *운영* 되어야 사용자에게 닿습니다. *DevOps* 는 이 흐름을 *끊기지 않게* 만드는 일입니다.

> *빠른 배포* 와 *안정적 운영* 은 *상충하지 않습니다*. 함께 갑니다.

## 전체 흐름
```mermaid
flowchart LR
    Code["코드 작성"] --> Build["빌드/테스트"]
    Build --> Deploy["배포"]
    Deploy --> Operate["운영/모니터링"]
    Operate --> Code
```

## Before/After

**Before (분리된 조직)**

```text
- 개발팀: "내 노트북에서는 잘 돼요"
- 운영팀: "또 너희가 망가뜨렸네"
- 배포는 *분기에 한 번*, 매번 *주말 야근*
```

**After (DevOps)**

```text
- 모든 PR이 *CI 통과* 후 머지
- *하루 수십 번* 배포 가능
- 장애는 *함께* 대응, 회고도 *함께*
```

## DevOps 시작 5단계

### 1단계 — Git 기반 협업

```bash
git checkout -b feat/login
# 변경 후
git commit -m "feat(auth): add login form"
git push origin feat/login
# PR 생성
```

### 2단계 — CI 자동화

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

### 3단계 — 자동 배포 한 줄 추가

```yaml
deploy:
  needs: test
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    - run: ./deploy.sh
```

### 4단계 — 모니터링 붙이기

```python
# 헬스체크 한 줄
@app.get("/health")
def health(): return {"status": "ok"}
```

### 5단계 — 장애 회고 시작

```text
- 무엇이 일어났나
- 왜 발견이 늦었나
- 다음에 어떻게 빨리 알 것인가
```

## 이 코드에서 주목할 점

- *작은 자동화* 부터 시작합니다. 큰 변혁이 아닙니다.
- *Dev와 Ops* 가 *같은 저장소* 를 봅니다.
- 모든 것이 *코드* 로 표현됩니다.

## 자주 하는 실수 5가지

1. **DevOps를 *부서 이름* 으로 만들기.** *문화* 이지 *조직도* 가 아닙니다.
2. **도구만 도입하고 *프로세스* 는 그대로.** Jenkins 깔아도 분기 배포면 의미 없습니다.
3. **운영팀에게 *책임만 떠넘김*.** *함께* 책임집니다.
4. **자동화에 *과투자*.** 한 번 쓸 일에 *3일짜리 자동화* 를 만들지 마세요.
5. **장애 후 *사람을 탓함*.** *시스템* 을 탓해야 합니다.

## 실무에서는 이렇게 쓰입니다

성공하는 팀은 *작은 단계* 부터 시작합니다. PR 자동 테스트 → 자동 배포 → 모니터링 → 회고 문화 순으로 *6개월* 에 걸쳐 정착합니다.

## 체크리스트

- [ ] *모든 PR* 이 자동 테스트를 거친다.
- [ ] *main 머지* 가 *자동 배포* 로 이어진다.
- [ ] *기본 모니터링* 이 있다.
- [ ] *장애 회고* 가 정기적으로 열린다.

## 정리 및 다음 단계

DevOps는 *문화의 변화* 입니다. 다음 글에서는 그 첫 단추인 *CI 파이프라인* 을 깊이 다룹니다.

<!-- toc:begin -->
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
