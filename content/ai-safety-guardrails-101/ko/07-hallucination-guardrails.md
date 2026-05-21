---
title: "AI Safety & Guardrails 101 (7/10): Hallucination Guardrail — Grounding 검증"
series: ai-safety-guardrails-101
episode: 7
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Hallucination
- RAG
- Grounding
last_reviewed: '2026-05-14'
seo_description: LLM이 "사실이 아닌 내용을 자신 있게 말하는" 현상을 hallucination이라고 부르지만, 운영에서 다루려면
  더 좁은 정의가 필요합니다.
---

# AI Safety & Guardrails 101 (7/10): Hallucination Guardrail — Grounding 검증

Hallucination이라는 말은 너무 넓게 쓰여서 운영 설계를 어렵게 만듭니다. 프로덕션에서 더 중요한 질문은 “이 답이 제공된 근거에 실제로 지지되는가”입니다. 특히 RAG 시스템에서는 사실 검증보다 grounding 검증이 훨씬 현실적인 첫 단계입니다.

이 문제가 중요한 이유는 사용자 피해가 단순한 오답으로 끝나지 않기 때문입니다. 인용 없이 단정적으로 말한 잘못된 답은 의사결정에 직접 영향을 주고, 근거가 붙어 있어 보여도 실제 문맥은 그 주장을 지지하지 않을 수 있습니다. 즉 citation, source, semantic 세 층을 모두 봐야 합니다.

그래서 이 글은 hallucination을 막연한 “헛소리”가 아니라 닫힌 문맥에서 검증 가능한 grounding 실패로 좁혀 다룹니다. 이 정의를 잡아야 측정과 차단, fallback 설계가 가능해집니다.

이 글은 AI Safety & Guardrails 101 시리즈의 7번째 글입니다.

이 글에서는 claim 추출, NLI entailment, judge 보강, citation 형식 강제, 회귀 지표를 묶어 grounding 검증 구조를 설명합니다.

## 먼저 던지는 질문

- Hallucination guardrail은 왜 답변 전체가 아니라 주장 단위로 봐야 할까요?
- claim extraction, entailment check, citation format은 각각 무엇을 검증할까요?
- 근거가 부족한 답변은 차단, 수정, 보류 중 어디로 보내야 할까요?

## 큰 그림

![Hallucination guardrail의 핵심: 답변을 주장 단위로 분해해 근거와 대조](https://yeongseon-books.github.io/book-public-assets/assets/ai-safety-guardrails-101/07/07-01-hallucination-guardrail.ko.png)

*Hallucination guardrail의 핵심: 답변을 주장 단위로 분해해 근거와 대조*

이 그림에서는 답변을 주장 단위로 분해하고 각 주장을 근거와 대조해 통과 여부를 판단하는 흐름을 봅니다. Hallucination guardrail은 답변의 말투가 아니라 주장과 근거의 관계를 검증해야 합니다.

> Hallucination을 줄이려면 답변을 문장 덩어리가 아니라 검증 가능한 주장 집합으로 봐야 합니다.

## 왜 이 글이 중요한가

grounding 검증을 별도 레이어로 두면 팀은 “모델이 틀릴 수 있다”는 추상적 두려움을 구체적 체크리스트로 바꿀 수 있습니다. 인용 여부, 출처 존재, 의미적 지지 여부를 순서대로 검사하면 어떤 단계에서 실패했는지 명확해지고, 회귀 세트로 precision과 recall을 수치화할 수 있습니다.

반대로 citation만 강제하면 겉보기 신뢰성만 올라갑니다. 모델은 plausible-looking citation을 붙일 수 있고, 검색된 chunk가 존재해도 실제 주장을 지지하지 않을 수 있습니다. 그래서 semantic grounding이 빠지면 사용자는 “근거가 있다”는 형식만 보고 잘못된 정보를 더 쉽게 믿게 됩니다.

결국 hallucination guardrail의 핵심은 정답 생성이 아니라 증거 검증입니다. 무엇을 알았는지가 아니라, 어떤 근거로 말했는지를 기계적으로 확인할 수 있어야 합니다.

## 핵심 관점

RAG 응답 한 문장에는 둘 이상의 사실 주장이 섞여 있는 경우가 많습니다. 문장 전체를 한 번에 참·거짓으로 판단하면 부분 오류를 놓치기 쉽습니다. 그래서 먼저 answer를 atomic claim으로 쪼개고, 각 claim이 어떤 chunk에 의해 지지되는지 확인해야 합니다.

이 과정을 세 단계로 나누면 운영이 단순해집니다. citation grounding은 형식 검증, source grounding은 chunk-ID 매칭, semantic grounding은 실제 지지 여부 확인입니다. 비용이 낮은 검사부터 실행하고, 회색 지대만 judge로 보내는 방식이 가장 현실적입니다.

> hallucination 검증의 핵심은 답변 전체를 한 번에 믿거나 버리는 것이 아닙니다. 답변을 주장 단위로 쪼개고, 각 주장에 대해 근거를 확인하는 것입니다.

## 핵심 개념

### 닫힌 문맥 hallucination에 집중해야 합니다

- **Closed-domain hallucination**: in RAG-style systems with explicit context, an output that is not supported by that context. This is verifiable.
- **Open-domain hallucination**: a factual error in answers generated from model knowledge alone, with no source. Verifying it requires external fact-checking and is expensive.

프로덕션 guardrail은 보통 전자에 먼저 집중합니다. RAG 시스템은 이미 문맥이 있으므로, 그 문맥이 답을 지지하는지만 봐도 큰 위험을 줄일 수 있기 때문입니다.

### grounding은 세 단계로 봐야 합니다

| Level | Meaning | Check |
| --- | --- | --- |
| Citation grounding | Every factual sentence carries a citation marker | Regex + length |
| Source grounding | The cited chunk actually appears in retrieved results | Chunk-ID match |
| Semantic grounding | The cited chunk really supports the claim | NLI model or LLM judge |

이 세 단계는 서로 대체 관계가 아닙니다. citation만 있으면 형식만 맞고, source만 맞으면 내용이 틀릴 수 있습니다. semantic grounding까지 가야 실제 검증이 됩니다.

### claim 추출이 첫 단계입니다

```python
import json

CLAIM_PROMPT = """Decompose the answer below into atomic factual claims.
Each claim must be a single declarative sentence that can be verified independently.
Return JSON: {"claims": [{"id": 1, "text": "..."}, ...]}.

ANSWER:
\"\"\"{answer}\"\"\"
"""

def extract_claims(answer: str) -> list[dict]:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": CLAIM_PROMPT.format(answer=answer)}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)["claims"]
```

claim이 너무 잘게 쪼개지면 비용이 폭증하므로, 후처리에서 문장 경계 기준으로 병합하는 전략도 함께 고려해야 합니다.

### NLI는 semantic grounding의 첫 필터입니다

```python
from transformers import pipeline

nli = pipeline(
    "text-classification",
    model="cross-encoder/nli-deberta-v3-large",
    return_all_scores=True,
)

def entails(premise: str, hypothesis: str) -> float:
    """Return entailment probability between 0 and 1."""
    pairs = [{"text": premise, "text_pair": hypothesis}]
    out = nli(pairs)[0]
    return next(s["score"] for s in out if s["label"] == "ENTAILMENT")
```

```python
def grounded(claims: list[dict], chunks: list[str], threshold: float = 0.7) -> dict:
    failures = []
    for c in claims:
        best = max(entails(chunk, c["text"]) for chunk in chunks)
        if best < threshold:
            failures.append({"claim": c["text"], "score": best})
    return {"ok": not failures, "failures": failures}
```

NLI는 빠르고 일관되지만 다단계 추론이 필요한 claim에서는 약할 수 있습니다. 그래서 회색 구간만 judge로 보냅니다.

### judge는 회색 지대를 재판정합니다

```python
JUDGE_PROMPT = """Decide whether the CLAIM is supported by the EVIDENCE.
Reply with JSON: {"supported": true|false, "reason": "..."}.

CLAIM: {claim}

EVIDENCE:
\"\"\"{evidence}\"\"\"
"""

def judge_grounding(claim: str, evidence: str) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(claim=claim, evidence=evidence)}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)
```

NLI score가 0.4~0.7 정도인 회색 구간만 judge로 보내면 비용을 많이 줄일 수 있습니다.

### citation 형식을 강제해야 자동 검증이 쉬워집니다

```text
Seoul is the capital of South Korea, with a population of about 9.7 million [chunk-3]. ...
```

```python
import re

CITE_RE = re.compile(r"\[chunk-(\d+)\]")

def citation_check(answer: str, retrieved_ids: set[int]) -> dict:
    cited = {int(m.group(1)) for m in CITE_RE.finditer(answer)}
    missing = cited - retrieved_ids
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", answer) if s.strip()]
    uncited = [s for s in sentences if not CITE_RE.search(s)]
    return {"missing_chunks": missing, "uncited_sentences": uncited}
```

citation 형식이 강제되면 source grounding은 자동화가 쉬워집니다. uncited sentence는 근거 없는 주장 가능성이 높습니다.

### 전체 파이프라인은 세 레이어를 묶습니다

```python
def verify_grounding(answer: str, chunks: list[dict]) -> dict:
    chunk_texts = [c["text"] for c in chunks]
    chunk_ids = {c["id"] for c in chunks}

    cite = citation_check(answer, chunk_ids)
    if cite["missing_chunks"] or cite["uncited_sentences"]:
        return {"ok": False, "stage": "citation", "detail": cite}

    claims = extract_claims(answer)
    nli_result = grounded(claims, chunk_texts)
    if not nli_result["ok"]:
        rechecked = []
        for f in nli_result["failures"]:
            best_chunk = max(chunk_texts, key=lambda ch: entails(ch, f["claim"]))
            verdict = judge_grounding(f["claim"], best_chunk)
            if not verdict["supported"]:
                rechecked.append(f["claim"])
        if rechecked:
            return {"ok": False, "stage": "semantic", "claims": rechecked}

    return {"ok": True}
```

실패 시 무조건 차단할 필요는 없습니다. 부분 경고, 재검색, 미검증 문장 제거 같은 fallback이 더 나은 UX를 만들 수 있습니다.

### 지표는 claim 단위로 관리해야 합니다

- **TruthfulQA, FEVER, HaluEval**: public grounding evaluation sets
- **Internal set**: 200 to 500 (question, context, answer, label) tuples sampled from real RAG traffic
- **Metrics**: claim-level precision and recall, average verification latency, cost per claim

정확도와 비용은 항상 trade-off입니다. claim recall, precision, latency를 같이 봐야 합니다.

## claim-level 검증에서 자주 놓치는 구현 포인트

grounding 검증은 코드가 돌아가는 것과 지표가 신뢰되는 것이 다릅니다. 아래 세 가지를 반드시 분리해서 기록해야 합니다.

- `citation_present`: 인용 마커가 있는가
- `source_exists`: 인용한 chunk가 실제 retrieval 결과에 있는가
- `semantic_support`: 인용 chunk가 주장을 실제로 지지하는가

```python
def verify_claim(claim: str, cited_chunk_ids: list[int], retrieved: dict[int, str]) -> dict:
    missing = [cid for cid in cited_chunk_ids if cid not in retrieved]
    if missing:
        return {"ok": False, "stage": "source_exists", "missing": missing}
    scores = {cid: entails(retrieved[cid], claim) for cid in cited_chunk_ids}
    best_cid = max(scores, key=scores.get)
    return {
        "ok": scores[best_cid] >= 0.7,
        "stage": "semantic_support",
        "best_chunk": best_cid,
        "score": scores[best_cid],
    }
```

## 공격/방어 시나리오: 그럴듯한 가짜 인용

| 공격 패턴 | 예시 | 방어 |
| --- | --- | --- |
| 존재하지 않는 chunk 인용 | `[chunk-99]` | source grounding 실패로 즉시 차단 |
| 다른 문서의 문장 왜곡 인용 | 사실과 반대 의미 재서술 | NLI entailment + judge |
| 숫자 조작 | 날짜/수치만 바꿔 단정 | structured fact check 규칙 |

### 숫자 사실 검증 보조 규칙

```python
import re

NUM_RE = re.compile(r"\d+(?:\.\d+)?")

def numeric_consistency(claim: str, evidence: str) -> bool:
    claim_nums = set(NUM_RE.findall(claim))
    ev_nums = set(NUM_RE.findall(evidence))
    return claim_nums.issubset(ev_nums) if claim_nums else True
```

NLI 점수가 높아도 숫자 일관성이 깨지면 경고를 올리는 식으로 보강합니다.

## fallback 정책 표준

| 실패 단계 | 기본 동작 | 사용자 경험 |
| --- | --- | --- |
| citation 실패 | 재생성 1회 | "근거를 다시 확인 중입니다" |
| semantic 실패(일부 claim) | 실패 claim 제거 후 전달 | "일부 문장을 검증하지 못했습니다" |
| semantic 실패(핵심 claim) | 차단 또는 사람 검토 | 안전한 대체 답변 |

이 기준을 미리 고정해야 운영자가 케이스마다 임의 판단하지 않습니다.

## Grounding 검증의 운영 비용 최적화

claim 단위 검증은 정확하지만 비쌉니다. 그래서 모든 claim에 동일한 검사를 적용하면 지연과 비용이 급증합니다.

| 단계 | 저비용 검사 | 고비용 검사 |
| --- | --- | --- |
| claim 생성 | 규칙 기반 분할 | LLM 기반 claim 추출 |
| 의미 검증 | bi-encoder 유사도 | cross-encoder NLI |
| 회색 구간 처리 | 규칙 경고 | LLM judge 재판정 |

### 2단계 점수 기반 라우팅

```python
def route_claim(score: float) -> str:
    if score >= 0.85:
        return "pass"
    if score < 0.45:
        return "fail"
    return "judge"
```

이렇게 라우팅하면 judge 호출량을 크게 줄이면서도 recall을 유지할 수 있습니다.

## 검증 실패 응답 정책

```python
def grounding_fallback(level: str) -> str:
    if level == "minor":
        return "일부 근거를 확인하지 못해 검증된 범위만 요약합니다."
    if level == "major":
        return "현재 근거를 확인할 수 없어 답변을 보류합니다."
    return "근거 확인 중입니다."
```

고위험 도메인에서는 `major`를 기본 차단으로 두는 편이 안전합니다.

## 운영 지표 추가

- claim당 평균 검증 비용
- claim당 평균 검증 지연
- 검증 실패 후 사용자 재질문 전환율
- 재검색(re-retrieval) 성공률

이 지표를 보면 단순 정확도 외에 사용자 흐름까지 개선할 수 있습니다.

## 운영 부록: 검증 질문

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

### 운영 검증 질문 세트

- 질문: 이 레이어가 실패했을 때 사용자에게 노출되는 최악의 결과는 무엇인가
- 답변 기록: 실패 모드별 `fail-open`/`fail-closed` 정책과 책임 팀을 runbook에 남깁니다.
- 질문: 우회 시도가 반복될 때 자동으로 강화되는 제재 단계가 있는가
- 답변 기록: 경고, 완화, CAPTCHA, 임시 정지, 영구 차단의 단계와 기준값을 명시합니다.
- 질문: 차단된 요청을 사람이 재검토할 수 있는 근거가 충분한가
- 답변 기록: request id, 정책 버전, 점수, 입력 해시, 출력 해시, 시간 정보를 함께 남깁니다.
- 질문: 정책을 변경했을 때 어떤 지표가 좋아지고 나빠졌는지 확인 가능한가
- 답변 기록: 변경 전후 7일 기준 차단율, FP율, 지연, 비용을 비교합니다.

## 흔히 헷갈리는 지점

- citation만 있으면 grounding이 끝났다고 생각하기 쉽습니다.
- 문장 단위 검사만으로 충분하다고 생각하기 쉽지만, 부분 hallucination을 놓칩니다.
- NLI threshold 하나로 모든 회색 지대를 처리하려 하면 false positive가 폭증합니다.
- 실패 시 무조건 차단하는 것이 안전하다고 보기 쉽지만, UX는 금방 무너집니다.

## 운영 체크리스트

- [ ] RAG 응답은 citation 형식을 강제하고 chunk-ID를 유지합니다.
- [ ] answer를 claim 단위로 분해한 뒤 entailment를 계산합니다.
- [ ] 회색 구간만 LLM judge로 보내 비용을 통제합니다.
- [ ] 실패 시 block, warning, re-retrieval 중 어떤 fallback을 쓸지 사전에 정합니다.
- [ ] claim precision, recall, latency를 회귀 세트로 지속 측정합니다.

## 정리

Hallucination guardrail의 핵심은 모델을 더 똑똑하게 만드는 것이 아니라, 모델이 한 주장에 대해 어떤 근거를 갖고 있는지 검증하는 것입니다. 특히 RAG 시스템에서는 이 문제가 닫힌 문맥 안에서 비교적 잘 정의됩니다.

운영적으로는 citation, source, semantic grounding을 분리하고, claim 단위로 검증하는 방식이 가장 실용적입니다. 이 구조가 있어야 어떤 부분이 실패했는지 설명할 수 있고, 지표로 튜닝할 수 있습니다.

여기서 더 중요한 것은 자신감 있는 문장이 아니라 실제로 지지되는 문장입니다.

## 처음 질문으로 돌아가기

- **Hallucination guardrail은 왜 답변 전체가 아니라 주장 단위로 봐야 할까요?**
  - 하나의 답변 안에서도 어떤 주장은 근거가 있고 어떤 주장은 없을 수 있어 claim 단위로 나눠야 정확히 고칠 수 있습니다.
- **claim extraction, entailment check, citation format은 각각 무엇을 검증할까요?**
  - claim extraction은 검증할 문장을 뽑고, entailment는 근거가 주장을 지지하는지 보며, citation format은 사용자가 근거를 추적할 수 있게 합니다.
- **근거가 부족한 답변은 차단, 수정, 보류 중 어디로 보내야 할까요?**
  - 안전·법적 위험이 크면 차단하고, 근거는 있으나 표현이 과하면 수정하며, 근거가 애매하면 보류하거나 사람 검토로 보냅니다.
<!-- toc:begin -->
## 시리즈 목차

- [AI Safety & Guardrails 101 (1/10): AI Safety가 왜 중요한가](./01-why-ai-safety-matters.md)
- [AI Safety & Guardrails 101 (2/10): Prompt Injection 방어](./02-prompt-injection-defense.md)
- [AI Safety & Guardrails 101 (3/10): 출력 필터링과 콘텐츠 모더레이션](./03-output-filtering.md)
- [AI Safety & Guardrails 101 (4/10): PII 감지와 마스킹](./04-pii-detection-redaction.md)
- [AI Safety & Guardrails 101 (5/10): Jailbreak 탐지](./05-jailbreak-detection.md)
- [AI Safety & Guardrails 101 (6/10): 독성과 편향 탐지](./06-toxicity-bias-detection.md)
- **AI Safety & Guardrails 101 (7/10): Hallucination Guardrail — Grounding 검증 (현재 글)**
- AI Safety & Guardrails 101 (8/10): Rate Limiting과 남용 방지 (예정)
- AI Safety & Guardrails 101 (9/10): 감사 로깅과 컴플라이언스 (예정)
- AI Safety & Guardrails 101 (10/10): 운영 가드레일 시스템 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [TruthfulQA: Measuring How Models Mimic Human Falsehoods](https://arxiv.org/abs/2109.07958)
- [FEVER - Fact Extraction and VERification](https://fever.ai/)
- [HaluEval - A Large-Scale Hallucination Evaluation Benchmark](https://arxiv.org/abs/2305.11747)
- [Cross-Encoder NLI - DeBERTa v3 large](https://huggingface.co/cross-encoder/nli-deberta-v3-large)

### 관련 시리즈

- [출력 필터링과 콘텐츠 모더레이션](./03-output-filtering.md)
- [운영 가드레일 시스템 구축](./10-production-guardrail-system.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-safety-guardrails-101/ko/07-hallucination-guardrails)

Tags: AI Safety, Hallucination, RAG, Grounding
