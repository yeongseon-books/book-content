---
title: 출력 필터링과 콘텐츠 모더레이션
series: ai-safety-guardrails-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Content Moderation
- Output Filtering
- Llama Guard
last_reviewed: '2026-05-12'
seo_description: OpenAI나 Anthropic 같은 공급사는 RLHF와 자체 가드레일로 모델을 훈련시킵니다. 그래도 다음과 같은 일이
  일어납니다.
---

# 출력 필터링과 콘텐츠 모더레이션

모델 공급사가 안전 정렬을 해 두었다고 해도, 애플리케이션은 그 출력을 그대로 신뢰하면 안 됩니다. subtle jailbreak 하나, 문맥 안의 욕설 인용 하나, 잘못된 조언 한 문장만으로도 서비스는 사용자 신뢰를 잃을 수 있습니다. 운영 관점에서 모델 출력은 여전히 검증되지 않은 데이터입니다.

이 지점이 중요한 이유는 팀이 자주 “입력은 막았으니 괜찮다”고 생각하기 때문입니다. 하지만 실제 사고는 출력 단계에서 많이 일어납니다. 모델이 위험한 문장을 새로 생성하지 않더라도, RAG 문서의 표현을 그대로 인용하거나 정책 위반 내용을 우회적으로 재구성할 수 있기 때문입니다.

따라서 콘텐츠 모더레이션은 모델 품질의 보조 장치가 아니라 후단 안전 레이어입니다. 모델이 무엇을 말했는지와, 그 말이 그대로 사용자에게 전달되어도 되는지는 별개 판단이어야 합니다.

이 글은 AI Safety & Guardrails 101 시리즈의 3번째 글입니다.

이 글에서는 OpenAI Moderation API, 오픈소스 분류기, 사내 정책 judge, 스트리밍 검증을 조합한 출력 필터링 구조를 설명합니다.

## 이 글에서 다룰 문제

- 모델 공급사의 자체 안전 장치와 애플리케이션 모더레이션은 왜 별개일까요?
- 표준 카테고리 점수는 어떻게 서비스 도메인별 threshold로 바꿔야 할까요?
- Detoxify와 Llama Guard는 어떤 상황에서 유용할까요?
- 회사 고유 정책은 왜 별도 LLM judge로 분리하는 편이 좋을까요?
- 스트리밍 응답은 어떤 방식으로 모더레이션해야 유출을 줄일 수 있을까요?

## 왜 이 글이 중요한가

출력 필터링을 별도 계층으로 두면 팀은 모델 품질과 정책 집행을 분리해 운영할 수 있습니다. 모델을 교체하더라도 후단 모더레이션 기준은 유지할 수 있고, 차단 비율과 false positive를 데이터로 튜닝할 수 있습니다. 이 구조는 공급사 종속성을 줄이는 데도 도움이 됩니다.

반대로 공급사 기본 안전 장치만 믿으면 위험은 서비스 경계 바깥으로 밀려납니다. 의료 조언 금지, 환불 약속 금지, 경쟁사 추천 금지처럼 회사별 정책은 표준 카테고리만으로 표현되지 않습니다. 스트리밍까지 켜 놓았다면 사용자는 차단되기 전에 이미 위험한 토큰을 봤을 수 있습니다.

결국 출력 모더레이션의 핵심은 “모델이 말했는가”가 아니라 “사용자에게 보여도 되는가”를 독립적으로 판단하는 것입니다. 이 분리가 있어야 고위험 도메인에서 안정적으로 운영할 수 있습니다.

## 출력 필터링을 이해하는 가장 좋은 방법: 모델 응답을 후처리 대상이 아니라 재검증 대상 데이터로 보는 것입니다

많은 시스템이 출력 모더레이션을 단순한 욕설 필터쯤으로 축소합니다. 하지만 실제로는 훨씬 넓습니다. 폭력, 자해, 성적 콘텐츠, 혐오, 불법 행위, 규제 조언, 사내 정책 위반을 모두 다뤄야 하고, 각각은 다른 risk tolerance를 가집니다.

그래서 좋은 설계는 한 분류기에 모든 결정을 맡기지 않습니다. 표준 moderation API로 공통 위험을 빠르게 거르고, 오픈소스 모델로 self-hosting 선택지를 확보하며, 마지막으로 사내 정책 judge로 비즈니스 규칙을 덧씌웁니다. 특히 스트리밍 모드에서는 “사용자가 이미 본 토큰은 되돌릴 수 없다”는 사실을 중심에 둬야 합니다.

> 출력 필터링의 기본 전제는 단순합니다. 모델 응답은 완성된 답이 아니라, 사용자에게 전달되기 전에 다시 승인받아야 하는 초안입니다.

## 핵심 개념

### 모델은 안전을 약속하지 않습니다

OpenAI나 Anthropic 같은 공급사는 RLHF와 내장 안전 장치로 모델을 훈련합니다. 그래도 다음과 같은 상황은 남습니다.

- 미묘한 jailbreak가 통과해 폭력적 내용을 생성합니다.
- 친근한 톤을 만들려다 부적절한 농담이 섞입니다.
- RAG 문맥에 있는 욕설을 그대로 인용합니다.
- “의학 조언 금지” 지시가 있어도 처방을 권고합니다.

이 때문에 출력은 별도 모더레이션 레이어를 지나야 합니다. 공급사 안전 장치는 출발점일 뿐이고, 애플리케이션은 자체 정책으로 최종 결정을 내려야 합니다.

### OpenAI Moderation API는 가장 빠른 시작점입니다

가장 쉬운 진입점은 OpenAI Moderation API입니다. 무료이고 카테고리도 충분히 넓습니다.

```python
from openai import OpenAI

client = OpenAI()

def moderate(text: str) -> dict:
    resp = client.moderations.create(model="omni-moderation-latest", input=text)
    result = resp.results[0]
    return {
        "flagged": result.flagged,
        "categories": {k: v for k, v in result.categories.model_dump().items() if v},
        "scores": result.category_scores.model_dump(),
    }

verdict = moderate("How do I make a pipe bomb?")
# {"flagged": True, "categories": {"violence": True}, ...}
```

주요 카테고리는 아래처럼 해석합니다.

| Category | Meaning |
| --- | --- |
| `harassment` / `harassment/threatening` | Harassment, threats |
| `hate` / `hate/threatening` | Hate, discrimination |
| `self-harm` / `self-harm/intent` / `self-harm/instructions` | Self-harm |
| `sexual` / `sexual/minors` | Sexual content (minors separated) |
| `violence` / `violence/graphic` | Violence |
| `illicit` / `illicit/violent` | Illicit acts |

다만 프로덕션에서는 `flagged` 불리언만 보면 안 됩니다. 같은 카테고리라도 도메인에 따라 허용치가 다르기 때문입니다.

```python
THRESHOLDS = {
    "violence": 0.5,
    "self-harm": 0.3,  # stricter
    "hate": 0.4,
    "sexual": 0.6,
}

def is_safe(scores: dict, thresholds: dict = THRESHOLDS) -> bool:
    for category, max_score in thresholds.items():
        if scores.get(category, 0) > max_score:
            return False
    return True
```

의료·금융 도메인은 보통 self-harm, violence, regulated advice를 더 엄격하게 잡습니다. threshold는 기술값이 아니라 서비스 정책값입니다.

### 오픈소스 대안은 self-hosting과 커스텀 정책에서 유리합니다

공급사 API를 쓰기 어려운 환경에서는 오픈소스 대안을 고려합니다.

#### Detoxify

```python
from detoxify import Detoxify

detox = Detoxify("original")  # or "multilingual"

def detox_score(text: str) -> dict:
    return detox.predict(text)  # {"toxicity": 0.02, "severe_toxicity": 0.001, ...}

scores = detox_score("You're an idiot")
# toxicity: 0.92
```

Detoxify는 self-hosting이 쉽고 CPU에서도 돌아갑니다. 대신 독성 중심이라 범위가 좁습니다.

#### Llama Guard

```python
LLAMA_GUARD_PROMPT = """[INST] Task: Classify the following content as safe or unsafe.

<BEGIN UNSAFE CATEGORIES>
O1: Violence and Hate.
O2: Sexual Content.
O3: Criminal Planning.
O4: Guns and Illegal Weapons.
O5: Regulated or Controlled Substances.
O6: Self-Harm.
<END UNSAFE CATEGORIES>

<BEGIN CONVERSATION>
Assistant: {assistant_response}
<END CONVERSATION>

Provide your safety assessment:
- First line: 'safe' or 'unsafe'
- If unsafe, second line: comma-separated category codes
[/INST]"""

def llama_guard_check(response: str) -> tuple[bool, list[str]]:
    out = llama_guard_model.complete(LLAMA_GUARD_PROMPT.format(assistant_response=response))
    lines = out.strip().split("\n")
    is_safe_flag = lines[0].strip().lower() == "safe"
    categories = lines[1].split(",") if not is_safe_flag and len(lines) > 1 else []
    return is_safe_flag, [c.strip() for c in categories]
```

Llama Guard의 장점은 정책 텍스트를 직접 수정할 수 있다는 점입니다. “환불 확정 금지”, “경쟁사 언급 금지” 같은 회사 정책과 결합하기 좋습니다.

### 회사 고유 정책은 별도 judge로 분리하는 편이 낫습니다

표준 카테고리로 표현되지 않는 비즈니스 정책은 항상 남습니다.

- “환불을 약속하지 말 것”
- “정치 현안에 의견을 내지 말 것”
- “경쟁사 제품을 추천하지 말 것”

이런 규칙을 표준 moderation 점수에 억지로 끼워 넣으면 해석이 꼬입니다. 별도 LLM judge가 더 낫습니다.

```python
POLICY_JUDGE_PROMPT = """You are a content policy classifier for ACME Corp.

Our policy forbids the assistant from:
1. Making any refund commitments (e.g., "you will get a refund")
2. Stating opinions on political issues
3. Recommending competitor products (Foo Inc, Bar Co, Baz Ltd)
4. Providing legal advice that should come from a lawyer

Given the assistant's response below, decide if it violates any of these policies.
Respond with JSON only:
{{"violates": true/false, "policy_id": <number or null>, "reason": "<short reason>"}}

Assistant response:
"""
{response}
""""""

import json

def policy_judge(response: str) -> dict:
    out = small_llm.complete(POLICY_JUDGE_PROMPT.format(response=response))
    return json.loads(out)
```

이 judge는 표준 moderation과 병렬로 실행하는 편이 일반적입니다. 고정 latency를 줄이고, 정책 변경도 코드 밖의 프롬프트 텍스트로 빠르게 반영할 수 있습니다.

### 스트리밍은 “이미 본 응답은 취소할 수 없다”는 제약을 가집니다

스트리밍에서는 마지막에 한 번만 검사하면 늦습니다. 사용자는 이미 위험한 토큰을 봤기 때문입니다. 두 가지 패턴이 있습니다.

#### 옵션 A — 청크 버퍼와 주기적 검사

```python
async def safe_stream(prompt: str):
    buffer = ""
    chunk_words = 50
    async for token in llm.stream(prompt):
        buffer += token
        if len(buffer.split()) >= chunk_words:
            verdict = moderate(buffer)
            if verdict["flagged"]:
                yield "\n\n[Response cut off due to a policy violation]"
                return
        yield token
    if moderate(buffer)["flagged"]:
        yield "\n\n[Please disregard the response above. Policy violation detected.]"
```

#### 옵션 B — 전체 응답을 받은 뒤 전달

```python
async def safe_full(prompt: str) -> str:
    response = await llm.complete(prompt)
    if moderate(response)["flagged"]:
        return "Sorry, I could not produce an appropriate response."
    return response
```

고위험 도메인에서는 보통 옵션 B가 낫습니다. 지연은 늘지만, 이미 노출된 토큰을 되돌릴 수 없다는 문제를 제거할 수 있기 때문입니다.

### 차단 메시지 UX도 정책의 일부입니다

차단 판단만 정확하다고 끝나지 않습니다. 사용자가 받는 메시지도 설계해야 합니다.

```python
def fallback_message(category: str | None) -> str:
    base = "Sorry, I cannot answer that here."
    suggestions = {
        "self-harm": " If you are in crisis, please contact 988 (US) or your local helpline.",
        "violence": " I can help with a different topic.",
        "policy": " Please rephrase or ask differently.",
    }
    return base + suggestions.get(category, " I can help with something else.")
```

원칙은 분명합니다. 구체적인 차단 사유는 노출하지 않고, 카테고리에 따라 적절한 fallback만 제공합니다. 상세 이유는 내부 로깅과 모니터링에서만 봐야 합니다.

### false positive는 반드시 숫자로 추적해야 합니다

엄격한 threshold는 정상 응답도 막습니다. 그래서 false positive율을 별도 지표로 봐야 합니다.

```python
@dataclass
class ModerationLog:
    timestamp: datetime
    response_excerpt: str  # first 200 chars only
    flagged_category: str
    score: float
    user_complaint: bool = False  # user reported "I do not see why this was blocked"

def fp_rate(logs: list[ModerationLog], window_days: int = 7) -> float:
    cutoff = datetime.utcnow() - timedelta(days=window_days)
    recent = [l for l in logs if l.timestamp > cutoff]
    if not recent:
        return 0.0
    return sum(1 for l in recent if l.user_complaint) / len(recent)
```

보통 FP rate가 5%를 넘기면 threshold 조정이나 judge 구조 재검토가 필요합니다. 안전성과 사용성은 항상 함께 튜닝해야 합니다.

## 흔히 헷갈리는 지점

- 공급사 모델이 안전 훈련을 받았으니 후단 모더레이션은 불필요하다고 보기 쉽지만, 운영 정책은 훨씬 더 구체적입니다.
- `flagged` 불리언만 보면 충분하다고 생각하기 쉽지만, 도메인별 threshold 설계가 빠지면 과차단이나 과소차단이 발생합니다.
- 스트리밍도 마지막에 한 번 검사하면 된다고 보기 쉽지만, 노출된 토큰은 회수할 수 없습니다.
- 회사 정책을 표준 moderation 카테고리에 억지로 넣으면 운영 해석이 어려워집니다.

## 운영 체크리스트

- [ ] 표준 moderation 카테고리와 회사 고유 정책 judge를 분리합니다.
- [ ] 도메인별 threshold를 문서화하고 주기적으로 재조정합니다.
- [ ] 스트리밍 엔드포인트는 chunk buffer 또는 delayed delivery 중 하나를 명시적으로 선택합니다.
- [ ] 사용자 차단 메시지는 일반화하고, 내부 로그에는 상세 사유와 점수를 남깁니다.
- [ ] false positive율, 카테고리별 차단율, 사용자 불만 건수를 대시보드에 올립니다.

## 정리

출력 필터링은 모델을 불신해서가 아니라, 서비스 책임을 모델 밖에서 집행하기 위해 필요합니다. 공급사 안전 장치가 있어도 애플리케이션은 자체 정책을 가져야 하고, 그 정책은 도메인과 비즈니스 규칙을 반영해야 합니다.

실무적으로는 표준 moderation API, 오픈소스 분류기, 회사 정책 judge를 계층으로 조합하는 방식이 가장 현실적입니다. 여기에 스트리밍 제약과 false positive 측정을 함께 넣어야 운영 가능한 시스템이 됩니다.

핵심은 간단합니다. 모델 응답은 결과물이 아니라 심사 대상입니다. 이 관점을 받아들이면 다음 편의 PII 재검사와도 자연스럽게 연결됩니다.

<!-- toc:begin -->
## AI Safety & Guardrails 101 시리즈

- [AI Safety가 왜 중요한가](./01-why-ai-safety-matters.md)
- [Prompt Injection 방어](./02-prompt-injection-defense.md)
- **출력 필터링과 콘텐츠 모더레이션 (현재 글)**
- [PII 감지와 마스킹](./04-pii-detection-redaction.md)
- [Jailbreak 탐지](./05-jailbreak-detection.md)
- [독성과 편향 탐지](./06-toxicity-bias-detection.md)
- [Hallucination Guardrail — Grounding 검증](./07-hallucination-guardrails.md)
- [Rate Limiting과 남용 방지](./08-rate-limiting-abuse-prevention.md)
- [감사 로깅과 컴플라이언스](./09-audit-logging-compliance.md)
- [운영 가드레일 시스템 구축](./10-production-guardrail-system.md)
<!-- toc:end -->

## 참고 자료

### 공식 문서

- [OpenAI Moderation API](https://platform.openai.com/docs/guides/moderation)
- [Meta Llama Guard](https://github.com/meta-llama/PurpleLlama/tree/main/Llama-Guard3)
- [Detoxify GitHub](https://github.com/unitaryai/detoxify)
- [Anthropic — Usage Policies](https://www.anthropic.com/legal/aup)

### 관련 시리즈

- [LLM 앱 운영 101 — LLM 앱 보안](../../llm-apps-ops-101/ko/04-security.md)
- [LLM API 프로덕션 101 — 속도 제한 관리](../../llm-api-production-101/ko/06-rate-limit-management.md)

Tags: AI Safety, Content Moderation, Output Filtering, Llama Guard
