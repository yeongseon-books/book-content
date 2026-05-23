---
series: incident-response-101
episode: 6
title: "Incident Response 101 (6/10): Root Cause Analysis"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Incident
  - RCA
  - Postmortem
  - Analysis
  - Operations
seo_description: trigger와 root cause를 구분하고 5 Whys를 action item으로 잇는 RCA 방법을 설명합니다.
last_reviewed: '2026-05-15'
---

# Incident Response 101 (6/10): Root Cause Analysis

incident가 일어나면 누구나 빨리 원인을 찾고 싶어 합니다. 그런데 현장에서는 가장 먼저 눈에 보인 사건을 곧바로 근본 원인으로 받아들이는 경우가 많습니다.

배포 직후 장애가 났다면 배포가 원인처럼 보이고, 누군가 잘못된 명령을 실행했다면 그 사람이 원인처럼 보입니다. 하지만 그 한 단계 아래를 더 내려가 보면, 실제로는 보호 장치와 프로세스 빈틈이 함께 드러나는 경우가 대부분입니다.

이 글은 Incident Response 101 시리즈의 6번째 글입니다. 여기서는 trigger와 root cause를 구분하는 기준, 5 Whys를 운영 문서에 남기는 방법, 그리고 검증 가능한 action item으로 이어지는 RCA 흐름을 다룹니다.

![Incident Response 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/incident-response-101/06/06-01-diagram-at-a-glance.ko.png)
*Incident Response 101 6장 흐름 개요*
> RCA는 과거를 비난하는 게 아니라, 미래를 설계하는 일입니다. 인과관계를 추적하고 시스템 개선점을 찾습니다.

## 먼저 던지는 질문

- incident의 진짜 원인은 어떻게 찾아야 할까요?
- 왜 5 Whys가 여전히 유용할까요?
- trigger와 root cause는 어디서 갈릴까요?

## 왜 이 주제가 중요한가

trigger만 고치면 같은 root cause는 다음 incident에서 다시 터집니다. 예를 들어 특정 배포가 장애를 일으켰다고 해도, 실제 root cause는 보호 장치 없는 배포 프로세스, 부족한 검증, 취약한 기본값일 수 있습니다. 마지막 계기만 지우면 시스템은 여전히 같은 종류의 사고를 허용합니다.

RCA는 비난을 위한 절차가 아니라 재발 방지를 위한 분석입니다. 무엇이 가능 조건이었는지, 어떤 축에서 실패가 겹쳤는지, 어떤 후속 조치가 검증 가능해야 하는지를 분명히 해야 postmortem과 prevention 단계도 제대로 이어집니다.

## 한눈에 보는 구조

이 흐름에서 핵심은 한 번 더 묻는 습관입니다. 처음 눈에 보이는 설명에서 멈추지 않고, 왜 그 설명이 가능했는지 계속 내려가야 root cause에 가까워집니다.

## 핵심 용어

- **trigger**: incident를 직접 일으킨 계기입니다.
- **root cause**: 그 계기가 가능하도록 만든 조건입니다.
- **contributing factor**: incident를 키운 기여 요인입니다.
- **5 whys**: 왜를 여러 번 물어 깊이를 확보하는 기법입니다.
- **systems thinking**: 사람보다 시스템과 구조를 먼저 보는 관점입니다.

이 용어를 분리하면 RCA 문서가 훨씬 또렷해집니다. trigger는 사건의 마지막 스위치일 수 있지만, root cause는 더 깊은 곳에 있습니다. contributing factor는 한 축이 아니라 여러 축에서 함께 붙는 경우가 많습니다.

## 전후 비교

이전: trigger를 곧바로 root cause로 적습니다.

이후: 5 Whys와 기여 요인을 따라 구조적 조건까지 내려갑니다.

이후 상태의 장점은 사고 재발 가능성을 더 정확히 줄일 수 있다는 점입니다. 사람 한 명이나 마지막 이벤트 하나를 바꾸는 것보다, 사건을 가능하게 만든 구조를 바꾸는 편이 훨씬 오래 갑니다.

## 단계별 실습: 작은 RCA 워크북 만들기

### 1단계 — 5 Whys 체인 만들기

질문을 반복해 분석 깊이를 남기는 구조입니다. 중요한 것은 답 자체보다 왜가 몇 단계까지 내려갔는지를 보존하는 일입니다.

```python
def five_whys(start):
    chain = [start]
    for _ in range(5):
        chain.append(input(f"why? {chain[-1]} -> "))
    return chain
```

### 2단계 — 기여 요인 모으기

incident는 한 축에서만 생기지 않는 경우가 많습니다. 사람, 프로세스, 도구, 시스템처럼 여러 축을 함께 봐야 합니다.

```python
def factors():
    return {"people": [], "process": [], "tooling": [], "system": []}
```

### 3단계 — trigger와 root cause 구분하기

어떤 항목이 근본 원인인지 판단하려면 더 많은 근거가 필요합니다. 여기서는 증거 수로 간단히 구분합니다.

```python
def classify(item, evidence):
    return "root" if evidence >= 3 else "trigger"
```

### 4단계 — 후속 조치로 연결하기

RCA는 설명으로 끝나면 안 됩니다. root cause를 실제 수정 작업으로 옮겨야 합니다.

```python
def actions(root):
    return [{"root": root, "action": f"fix {root}"}]
```

### 5단계 — 검증 가능성 확인하기

좋은 action item은 검증할 수 있어야 합니다. 막연한 다짐보다 동사로 시작하는 구체 작업이 유리합니다.

```python
def is_actionable(action):
    return action["action"].startswith(("add ", "fix ", "remove ", "test "))
```

## 이 코드에서 먼저 볼 점

- 체인 구조가 있어야 분석 깊이를 잃지 않습니다.
- 기여 요인은 네 축으로 나눠 보는 편이 좋습니다.
- action item은 동사로 시작해야 실행 가능성이 높아집니다.

여기서 중요한 감각은 “누가 잘못했는가”보다 “왜 그런 실수가 incident로 이어질 수 있었는가”를 먼저 보는 것입니다. 개인의 실수는 자주 trigger일 수는 있어도, 반복 가능한 root cause는 대개 시스템과 프로세스 쪽에 남아 있습니다.

## RCA 기법 비교

RCA에는 여러 기법이 있으며, 사건의 성격에 따라 적합한 방법이 다릅니다. 각 기법의 특징과 적용 상황을 이해하면 분석 깊이를 더 효율적으로 확보할 수 있습니다.

| 기법 | 적합 상황 | 장점 | 단점 |
| --- | --- | --- | --- |
| 5 Whys | 단순한 인과관계 | 빠르고 직관적 | 복잡한 사건에는 부족 |
| Fishbone (Ishikawa) | 여러 축 요인 분석 | 기여 요인 시각화 | 원인 우선순위 불명확 |
| Fault Tree | 하드웨어·안전 사고 | 논리적 체계 | 작성 시간 소요 |
| Timeline | 시간순 복잡 사건 | 순서와 동시성 명확 | 인과보다 기록 중심 |

실무에서는 5 Whys로 시작해 깊이를 확보하고, Fishbone으로 기여 요인을 넓게 펼친 뒤, Timeline으로 순서를 정렬하는 흐름을 자주 씁니다. 한 기법만 고집하면 사각이 생길 수 있으므로, 사건 특성에 맞춰 조합하는 편이 안전합니다.

## 자주 하는 실수 5가지

1. 첫 답에서 바로 멈춥니다.
2. 사람을 root cause로 단정합니다.
3. trigger만 고치고 incident를 닫습니다.
4. action item이 지나치게 추상적입니다.
5. 검증할 수 없는 action item을 남깁니다.

가장 위험한 실수는 “원인을 찾았다”는 말로 분석을 너무 빨리 끝내는 일입니다. RCA가 짧게 끝났다면 root cause에 도달해서가 아니라 중간에서 멈췄을 가능성도 함께 의심해야 합니다.

## 실무에서는 이렇게 봅니다

실무에서는 postmortem 템플릿 안에 5 Whys 섹션과 contributing factors 표를 고정해 두는 경우가 많습니다. 이렇게 해야 incident마다 분석 깊이가 들쭉날쭉해지는 일을 줄일 수 있습니다.

시니어 엔지니어는 RCA에서 사람보다 시스템을 먼저 의심합니다. 그리고 action item이 측정 가능하고 검증 가능한지까지 함께 봅니다. 설명만 길고 바뀌는 것이 없다면, 그 RCA는 기록은 될 수 있어도 예방 장치는 되기 어렵습니다.

## trigger와 root cause를 구분하는 예시

예를 들어 새 배포 직후 결제 장애가 났다고 가정해 보겠습니다. 이때 “배포가 원인”이라고 적는 것은 trigger 수준 설명에 가깝습니다. 조금 더 내려가 보면 이렇게 정리할 수 있습니다.

- trigger: 잘못된 timeout 설정이 포함된 배포
- contributing factor: staging 환경에 실제 결제 부하 테스트가 없음
- root cause: timeout 변경이 검증 없이 프로덕션에 들어갈 수 있는 배포 보호 장치 부재
- action item: timeout 변경 시 회귀 테스트와 배포 차단 규칙 추가

이렇게 쓰면 사람이나 마지막 이벤트를 탓하는 대신, 다음 incident를 막을 수 있는 변경점이 더 또렷해집니다.

## 근본 원인 vs 기여 요인

RCA에서 자주 혼동되는 개념은 근본 원인(root cause)과 기여 요인(contributing factor)의 경계입니다. 근본 원인은 제거하면 같은 사건이 재발하지 않는 조건이고, 기여 요인은 사건을 키웠지만 그 자체로는 사건을 일으키지 못하는 조건입니다.

예를 들어 앞서 결제 장애 사례를 다시 보면:

- 근본 원인: timeout 변경이 검증 없이 프로덕션에 들어갈 수 있는 배포 보호 장치 부재
- 기여 요인: staging 환경에 실제 결제 부하 테스트가 없음
- 기여 요인: timeout 기본값이 문서화되지 않음
- 기여 요인: 배포 당일 리뷰어가 한 명뿐이었음

근본 원인만 고치면 같은 방식의 재발은 막을 수 있지만, 기여 요인을 함께 개선해야 전체 시스템 강건성이 높아집니다. 그래서 실무에서는 action item을 root cause 수정 한 개와 contributing factor 개선 여러 개로 나눠 우선순위를 매기는 경우가 많습니다.

## 체크리스트

- [ ] RCA 템플릿 섹션이 미리 준비되어 있다.
- [ ] 사람, 프로세스, 도구, 시스템 네 축을 함께 봤다.
- [ ] action item을 동사로 시작하는 규칙을 적용했다.
- [ ] 각 action item의 검증 기준을 적었다.

## 연습 문제

1. trigger와 root cause의 차이를 한 문장으로 적어 보세요.
2. 5 Whys를 한 문장으로 정의해 보세요.
3. contributing factor를 한 문장으로 정의해 보세요.

## 장애 원인 그래프 예제

복잡한 사건에서는 여러 조건이 함께 만나 장애가 발생합니다. 이때 인과관계를 그래프로 시각화하면 어떤 경로가 가장 큰 영향을 줬는지 분석하기 쉬워집니다.

```python
def build_cause_graph():
    # 노드: 원인 요소
    # 엣지: 인과관계 (A → B = A가 B를 관계)
    graph = {
        "배포": ["잘못된 timeout"],
        "잘못된 timeout": ["결제 API 지연"],
        "staging 부하 테스트 부재": ["잘못된 timeout"],
        "배포 보호 장치 부재": ["잘못된 timeout"],
        "결제 API 지연": ["고객 영향"],
    }
    return graph

def find_root_paths(graph, target="고객 영향"):
    # 타겟 노드까지 이어지는 모든 경로를 찾습니다
    def backtrack(node, path):
        if node not in graph or not graph[node]:
            return [path]
        paths = []
        for parent in graph:
            if node in graph[parent]:
                paths.extend(backtrack(parent, [parent] + path))
        return paths

    return backtrack(target, [target])

# 분석 실행
g = build_cause_graph()
paths = find_root_paths(g)
for p in paths:
    print(" → ".join(p))
```

출력 예시:

```text
배포 보호 장치 부재 → 잘못된 timeout → 결제 API 지연 → 고객 영향
staging 부하 테스트 부재 → 잘못된 timeout → 결제 API 지연 → 고객 영향
배포 → 잘못된 timeout → 결제 API 지연 → 고객 영향
```

이 그래프에서는 "잘못된 timeout"이 공통 중간 노드로 드러나고, 그 위로 세 가지 조건이 함께 연결됩니다. 이 구조를 보면 배포 보호 장치와 staging 부하 테스트 둘 다 개선해야 재발 가능성이 낮아진다는 점이 명확해집니다.

실무에서는 이런 그래프를 Graphviz나 Mermaid로 그려 postmortem 문서에 첨부하기도 합니다. 시각화가 있으면 팀원들이 인과관계를 훨씬 빠르게 이해할 수 있습니다.
## 정리와 다음 글

RCA의 목적은 마지막 계기를 찾는 데서 끝나지 않습니다. trigger와 root cause를 구분하고, 여러 기여 요인을 함께 보고, 검증 가능한 action item으로 이어져야 incident가 다시 반복되는 일을 줄일 수 있습니다.

다음 글에서는 피해를 멈추는 mitigation과 원인을 제거하는 resolution을 어떻게 구분하고 운영할지 다루겠습니다.

## RCA 심화: 5 Whys 사례와 피시본 다이어그램 해설

RCA 품질은 질문의 깊이와 근거의 분리에서 결정됩니다. "무엇이 터졌는가"는 trigger에 가깝고, "왜 그 상태가 가능했는가"가 root cause에 가깝습니다. 실무에서는 이 둘을 분리하지 못해 같은 유형 incident가 반복됩니다.

### 5 Whys 예시

사례: 결제 API timeout 급증으로 SEV2 incident 발생

1. 왜 결제가 실패했는가?  
   - API timeout이 급증했기 때문입니다.
2. 왜 timeout이 급증했는가?  
   - 새 릴리스에서 외부 결제 게이트웨이 재시도 횟수가 증가했기 때문입니다.
3. 왜 재시도 증가가 프로덕션에 반영됐는가?  
   - 성능 회귀 테스트가 해당 경로를 포함하지 않았기 때문입니다.
4. 왜 테스트가 경로를 포함하지 않았는가?  
   - 테스트 시나리오 소유자가 명확하지 않았고, 릴리스 체크리스트가 불완전했기 때문입니다.
5. 왜 소유자와 체크리스트가 불완전했는가?  
   - 결제 경로 변경에 대한 배포 가드레일 정책이 문서화/자동화되지 않았기 때문입니다.

이 체인에서 trigger는 "재시도 증가 릴리스"이고 root cause는 "가드레일 부재"입니다. 사람 실수는 보통 단일 원인이라기보다 시스템 결함을 드러내는 신호로 봐야 합니다.

### 피시본(Fishbone) 축 정리

피시본 다이어그램은 원인을 축별로 분리해 인과관계 누락을 줄입니다. incident RCA에서는 보통 다음 다섯 축이 유효합니다.

- People: 역할/인수인계/교육
- Process: 체크리스트/승인/릴리스 절차
- Tooling: 모니터링/알림/배포 도구
- System: 아키텍처/의존성/리소스 한계
- Environment: 트래픽 패턴/외부 서비스/시간대 이벤트

한 축만 보면 빠르게 결론이 나오는 대신 재발 가능성이 높아집니다. 최소 세 축 이상에서 근거를 모아야 균형 잡힌 RCA가 됩니다.

## action item 작성 규칙

좋은 action item은 동사로 시작하고, owner/due/검증 지표를 포함합니다.

```text
나쁜 예: 모니터링을 개선한다.
좋은 예: checkout timeout p95가 800ms를 5분 연속 초과하면 SEV2 페이지가 열리도록 alert rule을 추가한다. Owner: sre-platform, Due: 2026-06-05, Verify: staging fault injection test pass
```

규칙을 지키면 postmortem 이후 "무엇이 바뀌었는가"를 추적할 수 있습니다.

## 간단한 RCA 모델 코드

```python
def classify_cause(evidence_count: int, repeated: bool) -> str:
    if evidence_count >= 3 and repeated:
        return "root_cause"
    if evidence_count >= 1:
        return "trigger_or_factor"
    return "unknown"

def actionable(text: str) -> bool:
    verbs = ("add ", "fix ", "remove ", "test ", "enforce ")
    return text.startswith(verbs)
```

코드 자체보다 중요한 것은 기준의 명시화입니다. 기준이 명시되면 팀 간 리뷰에서 품질 논의를 구체적으로 할 수 있습니다.

## RCA 리뷰 체크리스트

- trigger, root cause, contributing factors가 분리되어 있는가?
- 각 주장에 근거 로그/지표/타임라인 링크가 있는가?
- action item이 검증 가능하게 작성되었는가?
- 30일 뒤 재확인 일정이 잡혀 있는가?

이 체크리스트를 통과한 RCA는 단순 회고를 넘어 재발 방지 설계 문서로 기능합니다.

## RCA 출력 포맷: 원인 지도와 실행 항목

좋은 RCA는 결론 문장보다 구조가 먼저 보입니다. 아래 포맷은 trigger, root cause, 기여 요인, 검증 가능한 조치를 분리해 남기기 위한 예시입니다.

```text
[rca-output]
- trigger:
- root_cause:
- contributing_factors:
  - people:
  - process:
  - tooling:
  - system:
- corrective_actions:
  - action:
    owner:
    due:
    verify:
```

이 구조를 고정하면 "분석은 길었는데 조치가 없다"는 문제를 줄일 수 있습니다. RCA는 설명 문서가 아니라 다음 변경의 입력 문서여야 하기 때문입니다.

## 원인 우선순위 매트릭스

| 항목 | 재발 가능성 | 영향도 | 우선순위 |
| --- | --- | --- | --- |
| 배포 가드레일 부재 | 높음 | 높음 | 즉시 |
| 관측 지표 부족 | 중간 | 높음 | 높음 |
| 운영 절차 문서 누락 | 중간 | 중간 | 중간 |

원인 우선순위를 정하면 action item이 현실적인 순서로 배치됩니다. 모든 원인을 동시에 고치려 하면 결국 아무것도 끝내지 못하는 경우가 많습니다.

## 운영 부록: RCA 회의 템플릿

```text
[rca-meeting]
- incident_id:
- facilitator:
- 참석자:
- trigger 확인:
- root cause 후보:
- evidence 링크:
- 기여 요인 분류(people/process/tooling/system):
- action item 초안:
- 검증 계획:
```

회의 템플릿을 고정하면 분석 깊이 편차를 줄일 수 있습니다.

## 운영 부록: 근거 등급 규칙

| 등급 | 기준 | 예시 |
| --- | --- | --- |
| A | 로그/메트릭/배포 이력 3개 이상 일치 | 원인 확정 가능 |
| B | 근거 2개 일치, 일부 불확실성 | 보강 조사 필요 |
| C | 가설 수준, 근거 부족 | root cause로 채택 금지 |

근거 등급 규칙은 "느낌 RCA"를 줄이는 데 효과적입니다.

## 운영 부록: 조치 검증 문장 예시

- 배포 가드레일 추가 후 staging fault injection 테스트를 통과한다.
- timeout 기본값 변경 후 p95 지연이 2주간 임계값 내 유지된다.
- 경보 규칙 개정 후 동일 유형 장애에서 MTTA가 5분 이하로 유지된다.

RCA 품질은 원인 문장보다 검증 문장에서 더 잘 드러납니다.

## RCA 운영 추가 점검 항목

아래 항목은 실무에서 바로 점검할 수 있는 추가 체크포인트입니다.

- 체크포인트 1: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 2: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 3: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 4: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.
- 체크포인트 5: incident 운영에서 재현 가능한 품질을 만들려면 기준 문서, 실행 템플릿, 검증 루프가 하나로 연결되어야 합니다. 대응자는 판단 근거를 수치로 남기고, 커뮤니케이션은 정시로 발행하며, 종료 후에는 action item을 추적 가능한 티켓으로 전환해야 합니다. 이 원칙을 반복 적용하면 개인 경험에 의존하던 대응이 팀 시스템으로 바뀝니다.

```text
[quick-audit]
- declaration_latency_minutes:
- first_update_latency_minutes:
- mitigation_started_minutes:
- recovery_verification_metrics:
- postmortem_linked: true/false
```

## 운영 메모: 점검 루프

운영 문서는 작성으로 끝나지 않습니다. 월간 점검 루프를 통해 선언 기준, 역할 분리, 공지 주기, 후속 조치 추적이 실제 incident에서 유지되는지 확인해야 합니다. 점검 결과는 다음 리허설 시나리오와 runbook 개정 항목으로 바로 연결하는 편이 좋습니다.

## 처음 질문으로 돌아가기

- **incident의 진짜 원인은 어떻게 찾아야 할까요?**
  - 본문에서 강조했듯이 "장애가 난 컴포넌트"에서 멈추지 말고, 그 컴포넌트가 그 시점에 그렇게 동작한 이유를 묻는 식으로 한 단계씩 거슬러 올라가야 합니다. 보통은 코드 한 줄이 아니라 검증되지 않은 가정, 빠진 알람, 누락된 운영 절차 같은 시스템 수준의 약점에 도달했을 때 더 이상 새로운 답이 나오지 않는 지점이 진짜 root cause입니다.
- **왜 5 Whys가 여전히 유용할까요?**
  - 본문에서 본 것처럼 5 Whys는 도구가 단순해서 누구나 즉시 쓸 수 있고, "왜?"를 반복하는 동안 책임을 사람에서 시스템·프로세스로 자연스럽게 옮겨 줍니다. 다섯 번이 절대 숫자는 아니지만, 두세 번에서 멈추면 표면 원인에 머물고, 너무 깊게 가면 답이 추상화되기 때문에 약 다섯 번이 실무에서 합리적인 깊이라는 경험적 지점입니다.
- **trigger와 root cause는 어디서 갈릴까요?**
  - 본문 구분처럼 trigger는 "사건을 그 순간 터뜨린 직접적인 자극"(특정 배포, 트래픽 스파이크, 특정 입력)이고, root cause는 "그 trigger가 들어왔을 때 시스템이 견디지 못하게 만든 구조적 약점"입니다. 같은 trigger라도 다른 시스템에서는 incident가 안 되기 때문에, trigger만 막는 대응은 같은 종류의 다른 trigger에 그대로 다시 터집니다.
  - 근본 원인 하나가 아니라 여러 원인이 함께 작용한 경우가 대부분입니다.
<!-- toc:begin -->
## 시리즈 목차

- [Incident Response 101 (1/10): Incident란 무엇인가?](./01-what-is-incident.md)
- [Incident Response 101 (2/10): Severity 분류](./02-severity.md)
- [Incident Response 101 (3/10): 초기 대응](./03-initial-response.md)
- [Incident Response 101 (4/10): Communication](./04-communication.md)
- [Incident Response 101 (5/10): Timeline 작성](./05-timeline.md)
- **Root Cause Analysis (현재 글)**
- Mitigation과 Resolution (예정)
- Postmortem (예정)
- 재발 방지 (예정)
- Incident Runbook 만들기 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Root cause analysis - PagerDuty](https://response.pagerduty.com/after/root_cause_analysis/)
- [Postmortem Culture - Google SRE Book](https://sre.google/sre-book/postmortem-culture/)
- [Postmortem templates - Atlassian](https://www.atlassian.com/incident-management/postmortem/templates)
- [NIST SP 800-61 Rev. 2 Computer Security Incident Handling Guide](https://csrc.nist.gov/pubs/sp/800/61/r2/final)

### 예제 소스
- [incident-response-101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/incident-response-101/ko)
- [incident-response-101 canonical source in book-content](https://github.com/yeongseon-books/book-content/tree/main/content/incident-response-101)

Tags: Incident, RCA, Postmortem, Analysis, Operations
