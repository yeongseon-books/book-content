
# 출력 필터링과 콘텐츠 모더레이션

> AI Safety & Guardrails 101 시리즈 (3/10)

---
<!-- a-grade-intro:begin -->
## 핵심 질문

출력 필터링과 콘텐츠 모더레이션을 어떻게 설계해야 사고와 사용자 경험을 동시에 잡을 수 있을까요?

이 글은 그 질문에 답하기 위해 출력 필터링의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## Section 1

## 모델은 안전하다고 약속하지 않습니다

OpenAI나 Anthropic 같은 공급사는 RLHF와 자체 가드레일로 모델을 훈련시킵니다. 그래도 다음과 같은 일이 일어납니다.

- 미묘한 jailbreak에 넘어가서 폭력 묘사를 생성합니다.
- 사용자 친화적인 응답을 만들려다 부적절한 농담을 합니다.
- RAG 컨텍스트에 들어 있던 욕설을 그대로 인용합니다.
- 의학적 조언을 자제하라고 했는데도 처방을 추천합니다.

**모델 출력은 검증되지 않은 입력입니다.** 사용자에게 보내기 전에 별도 layer로 모더레이션해야 합니다. 이번 글에서는 OpenAI Moderation API, Detoxify, 그리고 자체 정책 분류기를 결합한 출력 필터링 패턴을 다룹니다.

이 글에서 다룰 것:

- OpenAI Moderation API 사용법과 카테고리
- Open-source 대안 (Detoxify, Llama Guard)
- 자체 정책 (회사별 금지 주제)을 LLM judge로 처리
- Streaming 응답에서의 모더레이션
- 차단된 응답을 사용자에게 어떻게 안내할지

---

## Section 1 — OpenAI Moderation API

가장 빠르게 시작하는 방법은 OpenAI Moderation API입니다. 무료이고 13개 카테고리를 분류합니다.

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

주요 카테고리:

| 카테고리 | 설명 |
| --- | --- |
| `harassment` / `harassment/threatening` | 괴롭힘, 위협 |
| `hate` / `hate/threatening` | 혐오, 차별 |
| `self-harm` / `self-harm/intent` / `self-harm/instructions` | 자해 |
| `sexual` / `sexual/minors` | 성적 콘텐츠 (미성년 별도) |
| `violence` / `violence/graphic` | 폭력 |
| `illicit` / `illicit/violent` | 불법 행위 |

실무 패턴: `flagged`만 보지 말고 `scores`에서 임계값을 자체 설정합니다. 도메인에 따라 같은 카테고리도 허용 수준이 다르기 때문입니다 (예: 의료 챗봇은 violence 점수 0.3에도 차단, 일반 챗봇은 0.7).

```python
THRESHOLDS = {
    "violence": 0.5,
    "self-harm": 0.3,  # 더 엄격
    "hate": 0.4,
    "sexual": 0.6,
}

def is_safe(scores: dict, thresholds: dict = THRESHOLDS) -> bool:
    for category, max_score in thresholds.items():
        if scores.get(category, 0) > max_score:
            return False
    return True
```

---

## Section 2 — Open-Source 대안

OpenAI에 의존하지 않거나 self-host가 필요한 경우 옵션이 있습니다.

### Detoxify (toxicity 전용)

```python
from detoxify import Detoxify

detox = Detoxify("original")  # or "multilingual"

def detox_score(text: str) -> dict:
    return detox.predict(text)  # {"toxicity": 0.02, "severe_toxicity": 0.001, ...}

scores = detox_score("You're an idiot")
# toxicity: 0.92
```

장점: self-hostable, GPU 없이도 동작 가능, 다국어 모델 있음. 단점: 카테고리가 toxicity 중심으로 좁음.

### Llama Guard

Meta의 Llama Guard는 LLM 기반 분류기로 정책을 자유롭게 정의할 수 있습니다.

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

Llama Guard는 정책 텍스트를 그대로 받아서 분류하므로 회사별 정책 (금융 자문 금지, 경쟁사 언급 금지 등)을 카테고리에 추가할 수 있습니다.

---

## Section 3 — 자체 정책을 LLM Judge로 처리

표준 카테고리에 안 잡히는 회사별 정책이 항상 있습니다.

- "환불 정책에 대한 약속을 하지 마세요"
- "특정 정치 이슈에 대해 의견을 내지 마세요"
- "경쟁사 제품을 추천하지 마세요"

이런 정책은 별도 LLM judge로 검증합니다.

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
\"\"\"
{response}
\"\"\""""

import json

def policy_judge(response: str) -> dict:
    out = small_llm.complete(POLICY_JUDGE_PROMPT.format(response=response))
    return json.loads(out)
```

여러 judge 호출을 병렬화하면 latency를 줄일 수 있습니다 (Moderation API + Detoxify + Policy judge를 동시에).

---

## Section 4 — Streaming 응답의 모더레이션

Streaming이면 토큰 단위로 응답이 나옵니다. 다 받은 뒤 검증하면 사용자가 이미 본 후입니다.

해결책 두 가지:

### 옵션 A: 청크 buffer + 정기 검증

```python
async def safe_stream(prompt: str):
    buffer = ""
    chunk_size = 50  # 50 토큰마다 검증
    async for token in llm.stream(prompt):
        buffer += token
        if len(buffer.split()) >= chunk_size:
            verdict = moderate(buffer)
            if verdict["flagged"]:
                yield "\n\n[응답이 정책 위반으로 중단되었습니다]"
                return
        yield token
    # 마지막 검증
    if moderate(buffer)["flagged"]:
        # 이미 사용자에게 보낸 부분이라 retraction 메시지만 가능
        yield "\n\n[위 응답을 무시해 주세요. 정책 위반이 감지되었습니다.]"
```

### 옵션 B: 전체 응답을 받아서 검증한 뒤 전송 (delayed delivery)

지연이 늘지만 안전합니다. 의료/법률처럼 위험이 큰 도메인에서 권장됩니다.

```python
async def safe_full(prompt: str) -> str:
    response = await llm.complete(prompt)  # 전체 받음
    if moderate(response)["flagged"]:
        return "죄송합니다. 적절한 응답을 생성하지 못했습니다."
    return response
```

기본 원칙: **사용자에게 보여 준 텍스트는 되돌릴 수 없다.** 위험이 클수록 옵션 B를 사용하세요.

---

## Section 5 — 차단된 응답 처리

응답을 차단했을 때 사용자에게 무엇을 보여 줄지가 UX의 핵심입니다.

```python
def fallback_message(category: str | None) -> str:
    base = "죄송합니다. 요청하신 내용에 대해 응답드리기 어렵습니다."
    suggestions = {
        "self-harm": " 위급한 상황이라면 정신건강 상담 전화 1577-0199로 연락 주세요.",
        "violence": " 다른 주제로 도와드릴 수 있습니다.",
        "policy": " 다른 방식으로 질문해 주세요.",
    }
    return base + suggestions.get(category, " 다른 방식으로 도와드릴 수 있습니다.")
```

원칙:

- **구체적인 차단 사유는 노출하지 않음** (우회 힌트가 됨)
- **카테고리별로 적절한 안내** (자해는 응급 연락처, 정책은 재시도 안내)
- **재시도가 가능함을 알림** (대화가 끝났다는 인상을 주지 않음)
- **로그에는 상세 사유 기록** (디버깅과 모니터링용)

---

## Section 6 — 가짜 양성 (False Positive) 모니터링

너무 엄격하면 정상 응답까지 차단해서 사용자 경험이 망가집니다. False positive rate를 추적해야 합니다.

```python
@dataclass
class ModerationLog:
    timestamp: datetime
    response_excerpt: str  # 처음 200자만
    flagged_category: str
    score: float
    user_complaint: bool = False  # 사용자가 "왜 차단됐는지 모르겠다"고 신고

def fp_rate(logs: list[ModerationLog], window_days: int = 7) -> float:
    cutoff = datetime.utcnow() - timedelta(days=window_days)
    recent = [l for l in logs if l.timestamp > cutoff]
    if not recent:
        return 0.0
    return sum(1 for l in recent if l.user_complaint) / len(recent)
```

False positive rate가 5%를 넘으면 임계값을 재조정하거나 카테고리 정책을 다시 보세요.

---

## 흔한 실수

1. **Moderation API의 `flagged`만 본다** — 카테고리별 임계값을 도메인에 맞게 조정하지 않으면 의료/금융 챗봇에 너무 느슨합니다.
2. **Streaming 응답을 검증하지 않는다** — 사용자가 다 본 뒤 알아챕니다. chunk buffer 또는 delayed delivery를 사용하세요.
3. **차단 사유를 그대로 노출한다** — 우회 힌트가 됩니다. 일반 메시지로 응답하세요.
4. **자체 정책을 표준 카테고리에 욱여넣는다** — "환불 약속 금지" 같은 회사 정책은 별도 LLM judge가 필요합니다.
5. **False positive를 측정하지 않는다** — 너무 엄격해도 신뢰를 잃습니다. 사용자 신고와 함께 추적하세요.

---

## 핵심 요약

- 모델 출력은 **검증되지 않은 입력**이므로 별도 모더레이션 layer가 필요합니다.
- **OpenAI Moderation API**가 빠른 시작이지만, 카테고리별 임계값을 도메인에 맞춰야 합니다.
- **Detoxify, Llama Guard** 등 self-hostable 대안이 있습니다.
- 회사별 정책은 **자체 LLM judge**로 검증합니다.
- **Streaming**은 chunk buffer 또는 delayed delivery로 처리합니다.
- 차단 메시지는 **카테고리별로 적절한 안내**를 제공하고, **false positive rate**를 모니터링하세요.

---

## 시니어 엔지니어는 이렇게 생각합니다

- **모더레이션 API가 1차 방어** — OpenAI·Azure·자체 분류기를 결합합니다.
- **카테고리별 임계값을 분리** — 모든 카테고리에 같은 기준은 위험합니다.
- **차단·재생성·경고의 흐름** — 단순 차단만으로는 UX가 무너집니다.
- **스트리밍 응답에서도 검증** — 끝까지 보지 않고 사고가 나갈 수 있습니다.
- **다국어 환경에서 정확도 차이** — 비영어권에서 false negative가 늘어납니다.

## AI Safety & Guardrails 101 시리즈

- [AI Safety가 왜 중요한가](./01-why-ai-safety-matters.md)
- [Prompt Injection 방어](./02-prompt-injection-defense.md)
- **출력 필터링과 콘텐츠 모더레이션 (현재 글)**
- PII 감지와 마스킹 (예정)
- Jailbreak 탐지 (예정)
- 독성과 편향 탐지 (예정)
- Hallucination Guardrail — Grounding 검증 (예정)
- Rate Limiting과 남용 방지 (예정)
- 감사 로깅과 컴플라이언스 (예정)
- 운영 가드레일 시스템 구축 (예정)
## 참고 자료

- [OpenAI Moderation API](https://platform.openai.com/docs/guides/moderation)
- [Meta Llama Guard](https://github.com/meta-llama/PurpleLlama/tree/main/Llama-Guard3)
- [Detoxify GitHub](https://github.com/unitaryai/detoxify)
- [Anthropic — Usage Policies](https://www.anthropic.com/legal/aup)

Tags: AI Safety, Content Moderation, Output Filtering, Llama Guard

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
