---
title: "Korean AI Stack 101 (5/6): Using HyperCLOVA X and Solar API"
series: korean-ai-stack-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- HyperCLOVA
- Solar
- LLM API
- Naver
- Upstage
last_reviewed: '2026-05-01'
seo_description: Learn to use HyperCLOVA X and Solar APIs for Korean LLM applications. Master API contracts, prompts, and response validation for production.
---

# Korean AI Stack 101 (5/6): Using HyperCLOVA X and Solar API

Once you introduce a Korean-first generation model, the hard part is not the model name. The hard part is locking down the call contract so authentication, prompting, output shape, and validation stay predictable in production.

This is the fifth post in the Korean AI Stack 101 series. Here, we map out safe calling patterns for Korean LLM APIs such as HyperCLOVA X and Solar.

![Korean AI Stack 101 chapter 5 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-01-core-flow.en.png)
*Korean AI Stack 101 chapter 5 flow overview*

> Choosing a Korean LLM API is not 'which model is smarter' — it is a four-axis decision over Korean fluency, price-per-1k-tokens, latency, and data-residency policy, and every production decision routes back through these four.

## Questions to Keep in Mind

- What API contract should you lock down before you start prompt tuning?
- What should you validate first when introducing Korean-first generation APIs such as HyperCLOVA X or Solar?
- Why does the runnable example use Groq `llama-3.1-8b-instant` as a stand-in?

## Why this matters

This post covers the patterns for safely calling Korean generation LLM APIs. Earlier posts cleaned the input data with embeddings (KoSimCSE, BGE-M3) and OCR (CLOVA). This post builds the answer on top. HyperCLOVA X (NAVER) and Solar (Upstage) are tuned for Korean fluency, but the real production problems live on the call-contract side: authentication, latency, error codes, token limits, prompt caching.

A separate post is justified because many teams expect that swapping in a Korean-tuned model is enough. If system messages, temperature, output format, and timeouts stay at defaults, the variance and refusal patterns persist. The most realistic learning path is two-stage: get fluent with the OpenAI-compatible interface using Groq's `llama-3.1-8b-instant`, then swap in HyperCLOVA / Solar at the end.

## Mental Model

Generation API calls factor into a 4-layer contract.

```text
[call contract]    auth, endpoint, rate limit, timeout, retry
     |
     v
[message contract] system / user / assistant roles, Korean system prompt
     |
     v
[sampling contract] temperature, top_p, max_tokens, stop sequences
     |
     v
[response contract] choices[0].message.content post-processing, JSON validation, safety filters
```

Three things matter most:

- **A model swap touches all four layers**: changing the model name is not the end of operationalization. Even one shifted layer changes the response distribution.
- **OpenAI-compatible is not a standard**: Groq, Solar, vLLM all advertise OpenAI compatibility, but timeout handling, rate-limit headers, and error codes differ.
- **Korean fluency is not factual correctness**: HyperCLOVA / Solar's natural Korean does not guarantee accuracy. Retrieval (next post) covers that gap.

Two more facts:

- HyperCLOVA X uses NAVER Cloud Platform auth; Solar uses an Upstage API key. The OpenAI SDK does not call HyperCLOVA directly — Solar mostly works via `base_url` swap.
- Groq is close to an OpenAI-compatible reference for learning purposes.

## Core concepts

| Item | Meaning |
| --- | --- |
| HyperCLOVA X | NAVER's Korean-centric LLM, served via NCP |
| Solar | Upstage's Korean/English LLM, with Solar Pro/Mini variants |
| Groq | LPU-based ultra low latency inference, OpenAI-compatible |
| `temperature` | Sampling randomness. 0.0 (deterministic) to 1.0+ (creative) |
| `max_completion_tokens` | Response token cap, output is truncated when exceeded |
| System prompt | First message that fixes persona, tone, language |
| Stop sequence | Token sequence that ends generation. Useful for JSON enforcement |
| Output validation | Post-processing: JSON schema, regex, length checks |

## Before vs. After

**Before** — Calling without a system message and an English user prompt makes the model mix English words into Korean responses, and the default temperature (often 1.0) returns a different answer to the same question every time.

**After** — A Korean system message and `temperature=0.3` stabilize behavior:

```python
# Three calls with the same question
'벡터 검색은 의미 유사도 기반, 키워드 검색은 문자 일치 기반입니다...'
'벡터 검색은 임베딩으로 의미를 비교하고, 키워드 검색은 토큰 매칭에 의존합니다...'
'벡터 검색은 의미를 벡터 공간에서 비교하고, 키워드 검색은 단어 단위 매칭입니다...'
```

What matters: (1) the same key concepts ("의미", "임베딩", "토큰") appear every time, (2) wording varies but facts stay consistent, (3) length stays predictable so post-processing cost is bounded.

## Why a provider-substitution exercise still helps

![Minimal runnable example](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-01-minimal-runnable-example.en.png)

*Minimal runnable example*

Readers do not always have HyperCLOVA X or Solar keys available. If the example cannot run, the prompt design lessons remain abstract. A stand-in provider still teaches the durable part of the workflow. At the final step, swapping the endpoint and auth header makes the same system message, sampling settings, and response handling reusable.

## Step-by-step practice

### Step 1 — Basic Groq call with a Korean system message

```python
import os
from groq import Groq

client = Groq(api_key=os.environ['GROQ_API_KEY'])
response = client.chat.completions.create(
    model='llama-3.1-8b-instant',
    temperature=0.3,
    max_completion_tokens=300,
    messages=[
        {'role': 'system', 'content': '당신은 한국어 제품 문서를 설명하는 시니어 개발자입니다. 항상 한국어로, 3~5문장으로 답합니다.'},
        {'role': 'user', 'content': '벡터 검색과 키워드 검색의 차이를 한국어로 설명해 주세요.'},
    ],
)
print(response.choices[0].message.content)
```

The point is to embed **language, role, and length** all into the system message. The user message stays clean.

### Step 2 — Constrain output format (force JSON)

![What to notice in this code](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-02-what-to-notice-in-this-code.en.png)

*What to notice in this code*

```python
import json

response = client.chat.completions.create(
    model='llama-3.1-8b-instant',
    temperature=0.0,
    max_completion_tokens=200,
    response_format={'type': 'json_object'},
    messages=[
        {'role': 'system', 'content': '당신은 한국어 답변을 JSON으로 반환합니다. {"summary": str, "keywords": [str]} 형태만 사용합니다.'},
        {'role': 'user', 'content': '벡터 검색의 핵심을 한 줄 요약과 키워드 3개로 정리해 주세요.'},
    ],
)
data = json.loads(response.choices[0].message.content)
assert 'summary' in data and 'keywords' in data
print(data)
```

`response_format='json_object'` and the explicit schema in the system message are a pair. Drop one and non-JSON answers leak through.

### Step 3 — Timeout and retry

```python
import time
from groq import Groq, APIConnectionError, RateLimitError

def call_with_retry(messages, max_retries=3):
    for attempt in range(max_retries):
        try:
            return client.chat.completions.create(
                model='llama-3.1-8b-instant',
                temperature=0.3,
                max_completion_tokens=300,
                messages=messages,
                timeout=10.0,
            )
        except (APIConnectionError, RateLimitError) as e:
            wait = 2 ** attempt
            print(f"retry {attempt+1}/{max_retries} after {wait}s: {e}")
            time.sleep(wait)
    raise RuntimeError('all retries failed')
```

Exponential backoff and timeout are a pair. Without a timeout, retries can wait forever on a hung call.

### Step 4 — Response validation and masking

```python
import re

def sanitize(text):
    text = re.sub(r'\b\d{2,3}-\d{3,4}-\d{4}\b', '[PHONE]', text)
    text = re.sub(r'\b\d{6}-\d{7}\b', '[RRN]', text)  # Korean resident number pattern
    return text

def validate(text, min_len=20, max_len=2000):
    if not (min_len <= len(text) <= max_len):
        raise ValueError(f'length out of range: {len(text)}')
    if any(bad in text for bad in ['죄송합니다, 제가', 'I cannot', 'As an AI']):
        raise ValueError('refusal-like response')
    return text

raw = response.choices[0].message.content
clean = sanitize(validate(raw))
```

Validation runs immediately after generation, before any user-facing surface. Masking runs once more before the response is logged or cached.

### Step 5 — Switching to HyperCLOVA / Solar (concept)

![Where engineers get confused](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/05/05-03-where-engineers-get-confused.en.png)

*Where engineers get confused*

```python
# Solar (Upstage) call — OpenAI SDK compatible
from openai import OpenAI

solar = OpenAI(
    api_key=os.environ['UPSTAGE_API_KEY'],
    base_url='https://api.upstage.ai/v1/solar',
)
response = solar.chat.completions.create(
    model='solar-mini',
    temperature=0.3,
    max_tokens=300,
    messages=[
        {'role': 'system', 'content': '당신은 한국어 제품 문서를 설명하는 시니어 개발자입니다.'},
        {'role': 'user', 'content': '벡터 검색과 키워드 검색의 차이를 설명해 주세요.'},
    ],
)
```

Solar requires only a `base_url` change, so most of the Groq example transfers as-is. HyperCLOVA X requires NCP-specific SDK or REST calls, but the message, sampling, and validation layers are identical.

## What to notice in this code

- A single system message line carrying **language, role, length** keeps the user message minimal.
- `temperature=0.3` is a strong starting point for explanatory Korean. Creative writing wants 0.7+.
- JSON enforcement needs **both** `response_format` and an explicit schema in the system message.
- Retry without timeout is dangerous. Always pair them.
- When you swap providers, the parts that change are endpoint and auth. The parts that stay are messages, validation, and masking.

## Common mistakes

- **No system message** — even at low temperature the persona drifts. A one-line system message is the highest leverage move.
- **Default temperature** — defaults vary by provider (0.7-1.0). Set it explicitly for cross-environment reproducibility.
- **No `max_tokens` cap** — Korean costs 1.3-1.5x more tokens than English. Without a cap, bills explode.
- **Assuming the OpenAI SDK reaches every Korean model** — Solar yes, HyperCLOVA X no. Verify before integration.
- **Surfacing raw response** — refusals ("죄송합니다, 제가 답할 수 없습니다") and PII can leak. Always validate and mask.
- **Confusing fluency for accuracy** — natural answers are not accurate by default. Accuracy is reinforced by RAG in the next post.

## Production application

- **Dual-provider operation**: Solar primary, HyperCLOVA X fallback. Share message code, swap endpoints.
- **Prompt caching**: long, repeated system messages benefit from OpenAI-compatible caching. Often 30%+ latency and cost savings.
- **Streaming**: responses over 200 tokens should stream. `stream=True` halves perceived latency.
- **Log masking**: never store raw prompts in production logs. Save only the `sanitize()` output.
- **Temperature/length A/B**: compare 0.3 vs 0.5, max_tokens 200 vs 400 against user satisfaction. Korean varies in length more than English.
- **Monitoring metrics**: TTFT, end-to-end latency, refusal rate, JSON parse failure rate, mean input/output tokens — these five form the LLM operations dashboard.

## Checklist

- [ ] Target reader, tone, and language are stated in the system message.
- [ ] `temperature` and token limits are fixed before comparing outputs.
- [ ] Output format is constrained to bullets, JSON, or another explicit shape.
- [ ] `timeout` and `retry` are paired.
- [ ] Validation and masking run once, immediately after generation.
- [ ] Auth, error handling, and latency are re-verified when switching providers.

## Exercises

1. Call the same system message with `temperature` 0.0, 0.3, 0.7 — five times each. Compare response length and key-term frequency.
2. Drop the schema from the JSON-forced call's system message and see how stable `response_format` alone is.
3. If you have a Solar (or HyperCLOVA) key, send the same messages and compare latency, refusal rate, and length against Groq in a small table.

## Summary · Next article

The core idea is operating Korean generation APIs as a 4-layer contract — call, message, sampling, response. Lock down system message, temperature, output format, and timeout once, and provider swaps or model upgrades become a one or two line edit. Korean fluency comes for free; factual control comes from retrieval, which is the next post.

The next article (episode 6, the final one) assembles a Korean RAG pipeline. We will combine BGE-M3 retrieval, CLOVA OCR text, and this post's LLM call into one flow that produces fact-grounded Korean responses — a minimum viable RAG, in code.

## HyperCLOVA X REST Call Example

The OpenAI-compatible interface is convenient for Solar and some providers, but HyperCLOVA X requires understanding NCP's proprietary REST contract for stable operation. Even when using an SDK wrapper, it is worth verifying the raw request/response format at least once.

```python
import os
import requests

def call_hyperclova_x(prompt: str) -> str:
    host = os.environ['NCP_APIGW_HOST']
    endpoint = '/testapp/v1/chat-completions/HCX-005'
    url = f'https://{host}{endpoint}'

    headers = {
        'Content-Type': 'application/json; charset=utf-8',
        'X-NCP-CLOVASTUDIO-API-KEY': os.environ['NCP_CLOVA_API_KEY'],
        'X-NCP-APIGW-API-KEY': os.environ['NCP_APIGW_API_KEY'],
        'X-NCP-CLOVASTUDIO-REQUEST-ID': 'korean-ai-stack-101-ep05',
    }

    payload = {
        'messages': [
            {'role': 'system', 'content': '당신은 한국어 기술 문서를 설명하는 시니어 개발자입니다.'},
            {'role': 'user', 'content': prompt},
        ],
        'topP': 0.8,
        'topK': 0,
        'temperature': 0.3,
        'maxTokens': 320,
        'repeatPenalty': 1.1,
        'includeAiFilters': True,
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=12)
    resp.raise_for_status()
    data = resp.json()
    return data['result']['message']['content']
```

The key point is the header contract, not the model name. A large portion of production issues start from key name typos, missing request IDs, or unset timeouts.

## A Small Benchmark for Korean Response Quality

To separate fluency from accuracy, you need an evaluation set — even a very small one. Here are the minimum metrics commonly used for Korean technical Q&A baselines.

| Metric | Definition | Initial baseline example |
| --- | --- | --- |
| Format pass rate | Parse success ratio when JSON response is enforced | 0.98+ |
| Refusal precision | Ratio of rule compliance on unanswerable questions | 0.95+ |
| Citation presence rate | Ratio of responses containing a source line | 0.99+ |
| Korean consistency | Ratio maintaining Korean style without English mixing | 0.97+ |

A simple automated check function like this catches regressions quickly before deployment.

```python
import json
import re

def check_generation_contract(raw_text: str):
    result = {
        'len_ok': 20 <= len(raw_text) <= 2000,
        'has_sources': '[sources:' in raw_text,
        'no_ai_slop': not any(
            bad in raw_text for bad in ['As an AI', 'I cannot', '저는 AI']
        ),
        'mostly_korean': bool(re.search(r'[가-힣]', raw_text)),
    }
    return result

sample = '결제 동기화 지연을 먼저 확인하세요. [sources: 0,1]'
print(json.dumps(check_generation_contract(sample), ensure_ascii=False))
```

## Production Config Example: Dual-Provider Routing

For Korean-language services, it is safer to prepare a primary/fallback route in advance rather than locking in a single provider. This lets you reroute quickly during latency spikes or temporary outages.

```yaml
llm_router:
  primary: solar-mini
  fallback: hyperclova-x
  timeout_ms: 10000
  max_retries: 2

providers:
  solar:
    base_url: https://api.upstage.ai/v1/solar
    model: solar-mini
    temperature: 0.3
    max_tokens: 320

  hyperclova:
    host_env: NCP_APIGW_HOST
    endpoint: /testapp/v1/chat-completions/HCX-005
    temperature: 0.3
    max_tokens: 320

guardrails:
  require_citation: true
  reject_if_no_json_when_required: true
  pii_mask_before_log: true
```

Keeping this configuration separate from code means a provider switch is a single PR, and temperature/length tuning history stays clear in version control.

## Error Code Classification and Retry Policy

Blindly retrying every API call failure can make things worse. It is better to define per-status-code responses up front.

| Status code | Meaning | Recommended response |
| --- | --- | --- |
| 400 | Request format error | Fail immediately, no retry |
| 401/403 | Auth/permission issue | Key rotation alert, no retry |
| 429 | Rate limit | Exponential backoff, limited retries |
| 500/502/503 | Transient server error | Short backoff retry, then fallback switch |
| timeout | Network/latency | Prefer request reduction and fallback over increasing timeout |

```python
def should_retry(status_code: int) -> bool:
    return status_code in (429, 500, 502, 503)
```

Embedding this rule at the router level keeps operational policy consistent even when per-model SDKs differ.

## Korean System Prompt Template Example

Prompt quality depends on the contract, not length. For Korean technical document answers, a template like this is usually sufficient.

```text
당신은 한국어 기술 문서를 설명하는 시니어 개발자입니다.
규칙:
1) 반드시 한국어로 답합니다.
2) 제공된 문맥에 없는 내용은 추측하지 말고 '문맥에서 확인하지 못했습니다.'라고 답합니다.
3) 답변 마지막 줄에 [sources: ...] 형식으로 출처 번호를 적습니다.
4) 불필요한 사과문, 자기소개, 모델 언급을 하지 않습니다.
```

Fixing this template means style and safety rules persist even when you swap models — the product feels less shaky to users.

## Operations Table: Managing Cost and Latency Together

In LLM API operations, cost and latency matter as much as quality. Tracking per-request input/output tokens and p95 latency in a single table accelerates decision-making.

| Profile | temperature | max_tokens | Avg input tokens | Avg output tokens | p95 latency (ms) | Cost per request (relative) |
| --- | --- | --- | --- | --- | --- | --- |
| concise-support | 0.2 | 180 | 420 | 120 | 820 | 1.0x |
| default-explain | 0.3 | 320 | 530 | 210 | 1210 | 1.6x |
| long-report | 0.4 | 700 | 760 | 520 | 2480 | 3.1x |

The operations team should split profiles by product feature using this table. Applying the same token limit to every feature causes cost and latency to destabilize quickly.

## Production Code Example: Provider Abstraction Interface

To make provider swaps safe, wrap call code behind an interface.

```python
from dataclasses import dataclass

@dataclass
class LLMRequest:
    system: str
    user: str
    temperature: float = 0.3
    max_tokens: int = 320

class LLMProvider:
    def generate(self, req: LLMRequest) -> str:
        raise NotImplementedError

class SolarProvider(LLMProvider):
    def __init__(self, client, model='solar-mini'):
        self.client = client
        self.model = model

    def generate(self, req: LLMRequest) -> str:
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=req.temperature,
            max_tokens=req.max_tokens,
            messages=[
                {'role': 'system', 'content': req.system},
                {'role': 'user', 'content': req.user},
            ],
        )
        return resp.choices[0].message.content
```

With this structure, you can use Solar during experimentation and swap to HyperCLOVA in environments requiring regulatory or contractual compliance — all through the same interface.

## Answering the Opening Questions

- **What API contracts must you lock down before prompt tuning?**
  - Lock the call contract, message contract, sampling contract, and response contract first: authentication and endpoint, system/user message structure, `temperature` and token ceiling, JSON validation and masking—bundled as one set. Only with this frame fixed can you read what actually changed quality when you revise prompt wording.
- **When adopting a Korean generation API like HyperCLOVA X or Solar, what should you verify first?**
  - Before Korean fluency, verify that authentication, timeout, retry, output format, refusal handling, and PII masking are stable. This article covered JSON enforcement, length validation, forbidden-phrase checks, and status-code-based retry policy first. In production, calls break more often from contract instability than from insufficient expressiveness.
- **Why does the runnable example use Groq `llama-3.1-8b-instant` as a stand-in model?**
  - So readers without HyperCLOVA X or Solar keys can immediately practice durable patterns—system messages, sampling, JSON response validation. The structure learned on Groq transfers to Solar with just a `base_url` change, and to HyperCLOVA X with header and endpoint swaps. The stand-in model is not a diluting detour but a device for building a provider-independent baseline.

<!-- toc:begin -->
## In this series

- [Korean AI Stack 101 (1/6): Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Korean AI Stack 101 (2/6): Building sentence similarity search with KoSimCSE](./02-kosimcse-similarity.md)
- [Korean AI Stack 101 (3/6): BGE-M3 multilingual embedding in practice](./03-bge-m3-multilingual.md)
- [Korean AI Stack 101 (4/6): Document text extraction with CLOVA OCR API](./04-clova-ocr.md)
- **Korean AI Stack 101 (5/6): Using HyperCLOVA X and Solar API (current)**
- Korean AI Stack 101 (6/6): Assembling a Korean RAG pipeline (upcoming)

<!-- toc:end -->

---

## References

- [Groq Python library](https://github.com/groq/groq-python)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Upstage Solar documentation](https://developers.upstage.ai/docs/getting-started/overview)
- [NAVER Cloud HyperCLOVA X overview](https://www.ncloud.com/product/aiService/clovaStudio)

Tags: Korean NLP, LLM, Embeddings, OCR
