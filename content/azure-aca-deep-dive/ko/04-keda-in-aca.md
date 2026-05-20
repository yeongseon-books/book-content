---
title: "Azure Container Apps Deep Dive (4/6): ACA 안의 KEDA — Scale Rule이 만드는 것"
series: azure-aca-deep-dive
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- Container Apps
- KEDA
- Dapr
- Envoy
last_reviewed: '2026-05-15'
seo_description: ACA의 Scale Rule이 KEDA형 제어 루프로 어떻게 번역되고 scale-to-zero에 어떤 영향을 주는지 다룹니다.
---

# Azure Container Apps Deep Dive (4/6): ACA 안의 KEDA — Scale Rule이 만드는 것

Azure Container Apps의 스케일링 표면은 놀랄 만큼 짧습니다. `minReplicas`, `maxReplicas`, 그리고 HTTP·TCP·custom rule 몇 개만 설정하면 플랫폼이 나머지를 처리합니다. 사용 경험은 단순하지만, 실제 질문은 그다음부터 시작합니다. 이 설정이 어떻게 실제 replica 수로 바뀌는가입니다.

Microsoft 문서가 ACA scaling을 KEDA-powered라고 명시하는 이유도 여기에 있습니다. 사용자가 직접 `ScaledObject`나 HPA를 만들지는 않지만, 하위 제어 루프를 설명할 때는 KEDA가 가장 정확한 기준점이 되기 때문입니다. 제품 표면만 보고 있으면 스케일링이 “그냥 자동으로 되는 일”처럼 보이지만, 운영은 그렇게 단순하지 않습니다.

이 글은 Azure Container Apps Deep Dive 시리즈의 네 번째 글입니다. 여기서는 ACA의 scale rule이 보이지 않는 KEDA형 control loop로 어떻게 읽히는지, 그리고 왜 scale과 traffic을 서로 다른 mental bucket에 넣어야 하는지 설명하겠습니다.

이 글을 읽고 나면 HTTP concurrency, custom rule, scale-to-zero, cooldown 같은 용어가 각각 어디에 걸리는지 감이 생깁니다. 그리고 Replica 수 변화가 제품 마법이 아니라 KEDA형 번역과 제어 루프의 결과라는 점도 명확해집니다.

이제 ACA의 friendly Scale blade 뒤에 있는 KEDA형 구조를 보겠습니다.

## 먼저 던지는 질문

- ACA의 scale rule은 KEDA에서 어떤 형태의 제어 루프로 읽는 편이 가장 정확할까요?
- 왜 scale rule은 app-scope가 아니라 revision-scope에 속할까요?
- `minReplicas: 0`이 가능하다는 사실은 스케일 모델을 어떻게 바꿀까요?

## 큰 그림

![Azure Container Apps Deep Dive 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/04/04-01-the-short-version-a-scale-rule-is-not-th.ko.png)

*Azure Container Apps Deep Dive 4장 흐름 개요*

이 그림에서는 ACA 안의 KEDA — Scale Rule이 만드는 것를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> ACA 안의 KEDA — Scale Rule이 만드는 것의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

ACA 운영에서 트래픽 분할과 스케일링은 자주 같은 이야기처럼 섞입니다. 둘 다 Revision 주변에서 일어나기 때문입니다. 하지만 실제로는 완전히 다른 제어 루프입니다. 트래픽은 Ingress가 어디로 보낼지를 결정하고, 스케일은 선택된 Revision 뒤에 몇 개 replica를 둘지를 결정합니다. 이 둘을 섞는 순간 rollout과 capacity planning이 동시에 흐려집니다.

또한 scale rule은 성능 조절 기능이면서 비용 제어 기능입니다. `minReplicas`, `maxReplicas`, polling interval, cooldown, concurrency threshold를 어떻게 잡느냐에 따라 첫 요청 지연, burst 대응, downstream 부하, 운영 비용이 함께 달라집니다. 즉 스케일링은 “자동”이 아니라 “제약을 둔 자동”이어야 합니다.

마지막으로 KEDA 모델을 이해하면 ACA의 닫힌 구현을 과장하지 않아도 됩니다. Microsoft가 공개한 제품 사실은 그대로 두고, 보이지 않는 하위 제어 루프는 pinned upstream KEDA 동작으로 제한적으로 설명할 수 있기 때문입니다. 이것이 가장 정확하고 실무적인 접근입니다.

## 핵심 관점

ACA의 스케일링을 한 문장으로 요약하면 이렇습니다. **scale rule은 scaler 그 자체가 아니라, 플랫폼이 KEDA형 autoscaling 동작으로 번역해야 하는 제품 설정**입니다. 사용자는 의도를 적고, 플랫폼이 그 의도를 숨은 control loop로 바꿉니다.

이 관점이 중요한 이유는 관찰 가능한 현상이 모두 번역 이후에 나타나기 때문입니다. 스케일링이 늦다, 0에서 깨어나는 첫 요청이 느리다, 여러 rule 중 하나만 충족해도 scale이 시작된다, 외부 지표 기반 scale이 밀리초 단위로 즉시 반응하지 않는다는 현상은 모두 KEDA형 polling·cooldown·activation 모델로 읽을 때 가장 자연스럽습니다.

그리고 이 설명은 ACA의 closed-source 성격과도 잘 맞습니다. 실제 `ScaledObject`나 HPA를 볼 수는 없지만, KEDA가 upstream에서 어떤 계약으로 동작하는지 알면 하위 루프의 모양을 과장 없이 설명할 수 있습니다.

> ACA의 scale rule은 사용자가 작성한 제품 설정이고, 실제 replica 수는 그 설정이 KEDA형 control loop로 해석된 뒤에야 결정됩니다.

## 핵심 개념

### scale rule은 scaler가 아니라 제품 설정입니다

ACA에서 사용자가 작성하는 rule은 runtime scaler object가 아닙니다. 플랫폼이 그 rule을 KEDA가 reconcile할 수 있는 형태의 숨은 구성으로 바꿔야 합니다. 보이지 않는다는 사실이 중요하지 않다는 뜻은 아닙니다. 오히려 보이지 않기 때문에 더 잘 이해해야 합니다.

직접 object를 보지는 못해도, 관찰되는 스케일 결과는 이 번역의 downstream입니다. 따라서 scale 이슈를 이해할 때는 rule 문법보다 “이 rule이 어떤 제어 루프를 만들었을까”를 먼저 생각해야 합니다.

### KEDA가 기준점인 이유는 계약이 명확하기 때문입니다

Upstream KEDA는 구조가 분명합니다. `ScaledObject`가 대상과 조건을 설명하고, operator가 이를 조정하며, HPA를 만들고, metrics adapter가 외부 지표 질의에 답합니다. ACA는 이 object를 드러내지 않지만, scaling이 KEDA-powered라는 문장은 이 구조를 기준점으로 삼아도 된다는 뜻입니다.

즉 ACA가 closed-source여도 스케일링 이야기를 허공에서 추측할 필요는 없습니다. pinned KEDA source가 control-loop의 형태를 설명하는 데 충분한 기준을 제공합니다.

### ACA가 노출하는 것과 KEDA가 필요한 것은 거의 대응됩니다

KEDA에는 scale target, trigger definition, limits가 필요합니다. ACA는 Revision template 안에 이미 그 개념을 갖고 있습니다. `minReplicas`, `maxReplicas`, HTTP/TCP/custom rule metadata, auth field가 그것입니다.

![ACA scale fields and KEDA inputs](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/04/04-02-what-aca-exposes-versus-what-keda-needs.ko.png)

*ACA scale fields and KEDA inputs*

그래서 사용자가 느끼는 scale rule과 보이지 않는 KEDA object 사이의 conceptual jump는 크지 않습니다. 제품은 object model을 감추지만, 의도는 거의 직접 대응됩니다.

### 스케일링은 App이 아니라 Revision 단위입니다

ACA에서 트래픽은 app-facing이지만, 스케일은 revision-facing입니다. scale rule을 바꾸면 새 Revision이 만들어지는 이유도 여기에 있습니다. scale은 metadata가 아니라 runtime behavior이기 때문입니다.

![Per-revision independent scaling behavior](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/04/04-03-the-first-key-behavior-scaling-is-per-re.ko.png)

*Per-revision independent scaling behavior*

여러 Revision이 동시에 active라면 각 Revision은 서로 다른 scaling behavior를 가질 수 있습니다. 이 때문에 rollout math와 scaling math를 절대 같은 개념으로 합쳐서는 안 됩니다.

### KEDA는 HPA를 대체하는 것이 아니라 HPA 동작을 관리합니다

이 부분은 자주 오해됩니다. KEDA는 HPA와 완전히 별개인 마법 시스템이 아닙니다. upstream KEDA는 `ScaledObject`를 reconcile하고 HPA spec을 만들고 업데이트합니다. 즉 HPA-style decision loop를 관리하고 feeding하는 쪽에 가깝습니다.

![ScaledObject and HPA control relationship](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/04/04-04-a-scaledobject-creates-hpa-behavior-not.ko.png)

*ScaledObject and HPA control relationship*

ACA에서도 같은 큰 그림을 가정하는 편이 정확합니다. 제품 표면은 KEDA가 Revision에 대한 HPA류 결정을 만들 수 있을 만큼 충분한 정보를 제공합니다.

### `minReplicas: 0`은 scale-to-zero의 문을 엽니다

ACA가 `minReplicas: 0`을 허용한다는 사실은 중요한 의미를 가집니다. 이제 스케일링은 단순한 비율 조정이 아니라, event-driven activation까지 포함하는 모델이 됩니다. 전통적인 HPA-only mental model보다 KEDA mental model이 더 적합한 이유가 바로 여기 있습니다.

![minReplicas zero and scale-to-zero activation path](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/04/04-05-minreplicas-can-be-zero-and-that-changes.ko.png)

*minReplicas zero and scale-to-zero activation path*

문서가 cooldown이 마지막 replica를 0으로 내릴 때 특히 중요하다고 설명하는 것도 같은 맥락입니다. 1에서 0으로 가는 마지막 단계는 event-driven activation 모델에서 특별한 운영 의미를 가집니다.

### custom rule은 가장 KEDA다운 부분입니다

custom rule은 KEDA scaler와의 대응이 가장 선명한 영역입니다. ACA 문서도 KEDA scaler metadata와 authentication 개념을 ACA field로 옮기는 방법을 설명합니다. 사실상 “여기는 KEDA식으로 생각하라”는 힌트에 가깝습니다.

![Custom rule to replica control loop](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/04/04-06-the-control-loop-how-a-custom-rule-becom.ko.png)

*Custom rule to replica control loop*

외부 event source를 보고 activation을 판단하고, polling과 cooldown을 거쳐 replica 수를 늘리거나 줄이는 흐름은 보이지 않는 Kubernetes object를 몰라도 충분히 설명 가능합니다.

### HTTP scaling은 built-in이지만 KEDA형 사고와 닮아 있습니다

ACA는 HTTP concurrency 기반 built-in scaling을 제공합니다. 문서는 concurrent requests와 15초 측정 창을 설명합니다. 여기서 중요한 것은 정확한 선 긋기입니다. ACA HTTP scaling이 upstream `kedacore/http-add-on`과 동일하다고 말하면 과장입니다. 하지만 event-driven autoscaling 사고방식과 trigger input이 request concurrency라는 점은 분명합니다.

![HTTP concurrency in a KEDA-shaped loop](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/04/04-07-http-scaling-is-built-in-but-the-shape-s.ko.png)

*HTTP concurrency in a KEDA-shaped loop*

정확한 표현은 이렇습니다. ACA는 HTTP scaling을 built-in product feature로 제공하고, 그 scaling model은 KEDA형 제어 루프와 개념적으로 정렬되어 있습니다.

### TCP scaling도 같은 큰 패턴을 따릅니다

TCP scaling 역시 동시 연결 수 기준을 정하고, 측정 창에서 수요를 보고, 임계값을 넘으면 replica를 늘린다는 큰 구조를 가집니다. 플랫폼 구현은 제품이 소유하지만, trigger state를 replica 변화로 바꾸는 패턴은 여전히 KEDA형 autoscaling loop로 읽는 편이 맞습니다.

### 인증도 번역 경계입니다

Upstream KEDA는 `TriggerAuthentication`이나 identity 구성을 자주 씁니다. ACA는 그 raw object를 노출하지 않고, secrets와 managed identity 같은 제품 표면으로 같은 의도를 표현하게 합니다. 즉 auth도 또 하나의 translation boundary입니다.

![Scale rule auth and product translation boundary](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/04/04-09-authentication-for-scale-rules-is-anothe.ko.png)

*Scale rule auth and product translation boundary*

모양은 recognizable하지만 resource model은 productized되어 있습니다. 이것이 ACA가 KEDA를 감추는 방식입니다.

### metrics adapter를 몰라도 그 결과는 계속 보게 됩니다

Upstream KEDA는 HPA가 external metric 질의에 답을 받을 수 있도록 metrics adapter를 둡니다. ACA에서는 사용자가 adapter를 직접 설정하지 않지만, 외부 이벤트나 concurrency가 replica 수를 바꾸는 모든 순간 이 숨은 고리가 작동하고 있다고 봐야 합니다.

![HPA queries and metrics adapter path](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/04/04-10-why-the-metrics-adapter-matters-even-whe.ko.png)

*HPA queries and metrics adapter path*

그래서 metric이 사라지거나 activation이 기대와 다르게 느릴 때는 제품 표면만 보지 말고, “metric answer path에서 어떤 신호가 비었는가”라는 질문도 함께 해야 합니다.

### 기본 polling·cooldown 값이 운영 체감을 만듭니다

문서가 custom rule의 default polling, cooldown 값을 따로 언급하는 이유가 있습니다. scale 변화는 밀리초 단위 연속 곡선이 아닙니다. 특히 1에서 0으로 내려갈 때는 cooldown의 존재감이 훨씬 강하게 드러납니다. 또 0에서 깨어나는 activation은 이미 떠 있는 Revision의 steady-state scaling과 체감이 다릅니다.

이런 차이는 제품 quirks가 아니라 event-driven autoscaling loop의 자연스러운 결과입니다. 운영에서 보이는 scale 지연, scale-in 보수성, 0→1 특수성은 대부분 여기서 설명됩니다.

### 여러 rule은 평균이 아니라 여러 활성화 경로입니다

ACA 문서는 여러 scale rule이 있을 때 첫 번째 조건을 만족한 rule부터 스케일이 시작될 수 있다고 설명합니다. 즉 여러 rule을 거대한 단일 평균 임계값으로 합치는 식으로 이해하면 안 됩니다.

![Multiple scale rules with separate activation paths](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/04/04-11-one-rule-can-wake-the-revision-up.ko.png)

*Multiple scale rules with separate activation paths*

깊이 들어가면, 여러 trigger는 하나의 scaling target을 깨울 수 있는 여러 activation path입니다. 이 관점을 알아야 rule stack을 설계할 때 우선순위와 downstream 영향도를 함께 볼 수 있습니다.

### scale rule이 revision template에 붙는 이유

ACA가 scale rule을 revision-scope로 둔 것은 우연이 아닙니다. canary Revision은 stable Revision과 다른 concurrency threshold나 max replica를 필요로 할 수 있고, 새 버전은 요청 처리 효율이 달라서 같은 임계값이 맞지 않을 수 있습니다.

![Scale rules attached to revision templates](https://yeongseon-books.github.io/book-public-assets/assets/azure-aca-deep-dive/04/04-12-scale-rules-belong-to-the-revision-templ.ko.png)

*Scale rules attached to revision templates*

scale이 runtime behavior라는 점을 생각하면, revision template에 붙는 것이 가장 자연스럽습니다. 그래야 rollout 실험과 scaling 실험을 함께 하지만 서로 섞지 않을 수 있습니다.

### 여러 scaler를 쌓을수록 downstream 보호가 더 중요해집니다

scale rule을 추가하는 일은 처리량을 늘리는 일처럼 보이지만, 동시에 downstream pressure를 증폭시키는 일입니다. queue scaler, HTTP concurrency scaler, 외부 metric scaler가 같은 Revision을 깨울 수 있다면, 앱 뒤의 DB connection pool, rate-limited API, 메시지 브로커가 버틸 수 있는지까지 함께 계산해야 합니다.

이 점이 중요한 이유는 ACA가 “잘” 확장될수록 뒤 시스템에는 더 빨리 부담을 줄 수 있기 때문입니다. KEDA형 autoscaling loop는 애플리케이션 앞단의 demand를 읽는 데는 능숙하지만, downstream이 같은 속도로 커진다고 가정하지는 않습니다. 따라서 max replica와 concurrency threshold는 성능 knob이면서 동시에 보호 장치입니다.

### scale 변화가 즉시 연속적이지 않은 이유

운영에서 자주 듣는 질문이 있습니다. “왜 요청이 늘었는데 바로바로 replica가 늘지 않죠?” 이때는 제품이 둔한 것이 아니라, control loop가 polling과 cooldown을 가진다는 사실을 먼저 떠올리는 편이 맞습니다. event-driven autoscaling은 본질적으로 measurement window, threshold, polling cadence 위에서 움직입니다.

즉 scale change는 매 밀리초마다 끊김 없이 따라붙는 연속 함수가 아닙니다. 이 특성을 이해하고 나면 burst 대응 전략도 현실적으로 바뀝니다. 아주 짧고 급한 스파이크는 warm baseline이나 higher min replica가 더 맞을 수 있고, 길고 명확한 이벤트 증가는 aggressive scaler가 더 맞을 수 있습니다.

### 관찰 포인트를 KEDA형 모델에 맞춰 잡아야 합니다

ACA에서 보이지 않는 object를 직접 볼 수는 없지만, 관찰 포인트는 분명히 잡을 수 있습니다. 첫째, trigger input이 실제로 들어오고 있는가를 봐야 합니다. 둘째, activation 이후 replica count가 기대 방향으로 움직이는가를 봐야 합니다. 셋째, 움직인 replica가 downstream 오류율과 latency에 어떤 영향을 주는지 봐야 합니다.

이 세 단계를 나누면 scale 문제를 훨씬 덜 추상적으로 다룰 수 있습니다. “스케일이 이상하다”는 막연한 말 대신, 입력 신호 문제인지, control loop 반응 문제인지, downstream 용량 문제인지를 각각 따로 검토할 수 있기 때문입니다.

### 운영자가 바로 적용해 볼 명령

아래 예시는 queue-based scale rule을 정의하는 가장 직접적인 ACA 표면입니다.

```bash
az containerapp update -n my-app -g my-rg \
  --min-replicas 0 --max-replicas 30 \
  --scale-rule-name queue-rule \
  --scale-rule-type azure-queue \
  --scale-rule-metadata queueName=jobs queueLength=5 \
  --scale-rule-auth connection=queue-conn
```

보이는 것은 몇 개 필드뿐이지만, 이 명령은 결국 trigger metadata, activation path, auth, replica limit가 숨은 KEDA형 control loop로 번역되도록 요청하는 것입니다.

설정이 실제 Revision 상태와 어떻게 연결되는지도 바로 확인해 두는 편이 좋습니다.

```bash
az containerapp show -n my-app -g my-rg \
  --query "properties.template.scale"

az containerapp revision list -n my-app -g my-rg -o table
```

**Expected output:**

- 첫 번째 명령에서 현재 Revision template에 붙은 `minReplicas`, `maxReplicas`, `rules`를 확인합니다.
- 두 번째 명령에서 scale rule 변경이 새 Revision 생성으로 이어졌는지 확인합니다.
- traffic 비율은 그대로여도 Revision 목록이 바뀔 수 있다는 점을 함께 확인합니다.

이 검증이 중요한 이유는 스케일링을 앱 전역 설정으로 착각하지 않기 위해서입니다. 같은 앱 URL을 쓰더라도, 실제 replica 제어는 언제나 특정 Revision template 뒤에서 일어납니다.

## 흔히 헷갈리는 지점

- **scale rule은 scaler object 자체가 아닙니다.** 제품 설정이며, 플랫폼이 하위 루프로 번역합니다.
- **KEDA는 HPA를 대체하는 완전히 별도 시스템이 아닙니다.** HPA-style behavior를 관리하고 feeding합니다.
- **HTTP scaling을 upstream KEDA HTTP add-on과 1:1로 단정하면 안 됩니다.** 개념적으로 닮았을 뿐입니다.
- **traffic 비율과 replica 비율은 같은 수치가 아닙니다.** 하나는 ingress policy, 하나는 autoscaling 결과입니다.
- **여러 rule은 평균 임계값이 아닙니다.** 여러 activation path로 이해하는 편이 맞습니다.

## 운영 체크리스트

- [ ] SLA 기준으로 scale-to-zero 허용 여부를 명시적으로 결정했습니다.
- [ ] 워크로드 스파이크 형태에 맞춰 polling interval과 cooldown을 조정했습니다.
- [ ] max replicas가 downstream(DB 연결 수, API quota)를 깨지 않는지 확인했습니다.
- [ ] 여러 scaler를 겹칠 때 우선순위와 aggregation 방식을 문서화했습니다.
- [ ] KEDA형 metric 변화와 실제 replica 수가 일치하는지 모니터링 체계를 만들었습니다.

## 정리

ACA의 스케일링은 단순한 제품 편의 기능이 아닙니다. 사용자가 적은 scale rule을 플랫폼이 KEDA형 autoscaling behavior로 번역하고, 그 결과가 Revision 단위 replica 수로 나타나는 구조입니다. 따라서 scale 이슈를 읽을 때는 rule 문법보다 control loop를 먼저 생각해야 합니다.

또한 scale은 Revision 범위의 런타임 행동입니다. 그래서 트래픽 분할과 같은 app-scope 정책과 분리해서 봐야 하며, canary나 blue-green 운영에서도 별도 조절 레버로 취급해야 합니다. `minReplicas: 0`, polling, cooldown, multi-rule activation은 모두 이 분리 위에서 의미를 가집니다.

다음 글에서는 replica 옆에 실제로 붙는 또 다른 런타임, Dapr sidecar를 보겠습니다. Dapr enablement가 단순 메타데이터가 아니라 어떻게 실제 `daprd` 프로세스를 붙이는지 따라가 보겠습니다.

## 처음 질문으로 돌아가기

- **ACA의 scale rule은 KEDA에서 어떤 형태의 제어 루프로 읽는 편이 가장 정확할까요?**
  - 본문의 기준은 ACA 안의 KEDA — Scale Rule이 만드는 것를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **왜 scale rule은 app-scope가 아니라 revision-scope에 속할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **`minReplicas: 0`이 가능하다는 사실은 스케일 모델을 어떻게 바꿀까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Azure Container Apps Deep Dive (1/6): ACA 아키텍처 — 사용자에게 보이지 않는 Kubernetes 위에 얹은 것](./01-aca-architecture.md)
- [Azure Container Apps Deep Dive (2/6): Environment 내부 — 네트워크·관측·Dapr 스코프의 경계](./02-environment-internals.md)
- [Azure Container Apps Deep Dive (3/6): Revision과 트래픽 분할 — Envoy 가중치는 어디에서 오는가](./03-revision-and-traffic-split.md)
- **Azure Container Apps Deep Dive (4/6): ACA 안의 KEDA — Scale Rule이 만드는 것 (현재 글)**
- Azure Container Apps Deep Dive (5/6): Dapr 사이드카 내부 — 컨테이너 옆에 뜨는 Go 프로세스 (예정)
- Azure Container Apps Deep Dive (6/6): Envoy Ingress 경로 — 첫 요청이 사용자 컨테이너에 닿기까지 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Scaling in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/scale-app)
- [Update and deploy changes in Azure Container Apps](https://learn.microsoft.com/en-us/azure/container-apps/revisions)

### 관련 시리즈
- [Azure Container Apps 101](../../azure-aca-101/ko/)
- [Azure AKS Deep Dive](../../azure-aks-deep-dive/ko/)
- [Azure Functions Deep Dive](../../azure-functions-deep-dive/ko/)

Tags: Container Apps, KEDA, Dapr, Envoy
