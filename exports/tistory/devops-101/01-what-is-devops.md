
# DevOps란 무엇인가?

> DevOps 101 시리즈 (1/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *개발팀* 과 *운영팀* 이 *서로를 탓하는* 회사는 어디서부터 잘못된 걸까요?

> DevOps는 *도구가 아니라 문화* 입니다. *함께 만들고 함께 책임지는* 일하는 방식입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *DevOps* 의 정의와 등장 배경
- *Dev* 와 *Ops* 가 분리된 시절의 *고통*
- DevOps의 *세 가지 원칙*
- 시작을 위한 *최소한의 도구*
- 흔한 함정 5가지

## 왜 중요한가

소프트웨어는 *만들기* 만 해서는 가치를 내지 못합니다. *배포* 되고 *운영* 되어야 사용자에게 닿습니다. *DevOps* 는 이 흐름을 *끊기지 않게* 만드는 일입니다.

> *빠른 배포* 와 *안정적 운영* 은 *상충하지 않습니다*. 함께 갑니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Code["코드 작성"] --> Build["빌드/테스트"]
    Build --> Deploy["배포"]
    Deploy --> Operate["운영/모니터링"]
    Operate --> Code
```

## 핵심 용어 정리

- **Dev**: *개발* (Development).
- **Ops**: *운영* (Operations).
- **CI**: 모든 커밋을 *자동 통합/검증*.
- **CD**: 검증된 코드를 *자동 배포*.
- **SRE**: *Site Reliability Engineering*. 운영을 *코드로* 다루는 직무.

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

## 실습: DevOps 시작 5단계

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

## 시니어 엔지니어는 이렇게 생각합니다

- *모든 수동 작업* 은 자동화 후보다.
- *배포 빈도* 는 *조직 건강* 의 지표다.
- *장애는 시스템의 학습 기회* 다.
- *Dev와 Ops* 는 *한 팀* 이다.
- *피드백 루프 길이* 가 모든 것을 결정한다.

## 체크리스트

- [ ] *모든 PR* 이 자동 테스트를 거친다.
- [ ] *main 머지* 가 *자동 배포* 로 이어진다.
- [ ] *기본 모니터링* 이 있다.
- [ ] *장애 회고* 가 정기적으로 열린다.

## 연습 문제

1. 본인 프로젝트의 *수동 배포 단계* 를 모두 적어보세요.
2. 그중 *3개* 를 자동화할 수 있는 후보로 표시하세요.
3. *마지막 장애* 의 회고를 *3문장* 으로 정리하세요.

## 정리 및 다음 단계

DevOps는 *문화의 변화* 입니다. 다음 글에서는 그 첫 단추인 *CI 파이프라인* 을 깊이 다룹니다.

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
## 참고 자료

- [The Phoenix Project (Gene Kim)](https://itrevolution.com/product/the-phoenix-project/)
- [Google SRE Book](https://sre.google/books/)
- [Atlassian DevOps Guide](https://www.atlassian.com/devops)
- [DORA State of DevOps](https://dora.dev/)

Tags: DevOps, Culture, CI, CD, Engineering

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
