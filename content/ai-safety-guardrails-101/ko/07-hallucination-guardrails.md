---
title: Hallucination Guardrail — Grounding 검증
series: ai-safety-guardrails-101
episode: 7
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- Hallucination
- RAG
- Grounding
last_reviewed: '2026-05-03'
---

# Hallucination Guardrail — Grounding 검증

> AI Safety & Guardrails 101 시리즈 (7/10)

---
## Section 1

## Hallucination이라는 용어의 함정

LLM이 "사실이 아닌 내용을 자신 있게 말하는" 현상을 hallucination이라고 부르지만, 운영에서 다루려면 더 좁은 정의가 필요합니다.

- **Closed-domain hallucination**: RAG처럼 명시된 출처(컨텍스트)가 있고, 출력이 그 출처에서 지지되지 않는 경우입니다. 검증이 가능합니다.
- **Open-domain hallucination**: 출처 없이 모델 지식만으로 답할 때 발생하는 사실 오류입니다. 외부 사실 검증이 필요해 비용이 큽니다.

이 글에서는 **closed-domain**을 중심으로 다룹니다. 대부분의 production guardrail은 RAG 기반이고, grounding 검증이 가장 안정적인 방법이기 때문입니다.

## Grounding이 무엇을 의미하는가

Grounding은 모델 출력의 모든 사실 주장(claim)이 제공된 컨텍스트 내에서 entailment(수반)되는 상태를 말합니다. 세 가지 수준으로 분리합니다.

| 수준 | 의미 | 검증 방법 |
| --- | --- | --- |
| Citation grounding | 모든 사실 주장에 인용 표시가 붙어 있음 | 정규식 + 길이 |
| Source grounding | 인용된 chunk가 실제로 검색 결과에 포함됨 | chunk ID 매칭 |
| Semantic grounding | 인용된 chunk가 그 주장을 실제로 지지함 | NLI 모델 또는 LLM judge |

세 수준은 모두 통과해야 합니다. 인용은 있지만 chunk가 다른 내용이거나, chunk는 맞지만 주장과 무관한 경우가 흔합니다.

## Claim 추출

문장 수준이 아니라 claim(원자적 사실 주장) 수준에서 검증해야 정확합니다. 한 문장에 검증 가능한 claim이 두세 개 들어가는 경우가 많습니다.

```python
import json

CLAIM_PROMPT = """Decompose the answer below into atomic factual claims.
Each claim must be a single declarative sentence that can be verified independently.
Return JSON: {"claims": [{"id": 1, "text": "..."}, ...]}.

ANSWER:
\"\"\"{answer}\"\"\""""

def extract_claims(answer: str) -> list[dict]:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": CLAIM_PROMPT.format(answer=answer)}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)["claims"]
```

claim이 너무 잘게 쪼개지면 후속 NLI 비용이 커지므로 sentence boundary 기준으로 합치는 후처리를 둡니다.

## NLI 기반 entailment 검증

각 claim이 검색된 chunk에 의해 entail되는지 자연어 추론(NLI) 모델로 판정합니다. `roberta-large-mnli`나 `deberta-v3-large-mnli`가 표준입니다.

```python
from transformers import pipeline

nli = pipeline(
    "text-classification",
    model="cross-encoder/nli-deberta-v3-large",
    return_all_scores=True,
)

def entails(premise: str, hypothesis: str) -> float:
    """0~1 사이의 entailment 확률을 반환합니다."""
    pairs = [{"text": premise, "text_pair": hypothesis}]
    out = nli(pairs)[0]
    return next(s["score"] for s in out if s["label"] == "ENTAILMENT")
```

각 claim에 대해 retrieved chunk 전체와 entailment를 계산하고, 최댓값이 임계치(예: 0.7) 미만이면 hallucination으로 판정합니다.

```python
def grounded(claims: list[dict], chunks: list[str], threshold: float = 0.7) -> dict:
    failures = []
    for c in claims:
        best = max(entails(chunk, c["text"]) for chunk in chunks)
        if best < threshold:
            failures.append({"claim": c["text"], "score": best})
    return {"ok": not failures, "failures": failures}
```

## LLM judge로 보강

NLI 모델은 짧은 문장에 강하지만 긴 다단계 추론이 필요한 claim에는 약합니다. 이때 LLM judge를 보조로 사용합니다.

```python
JUDGE_PROMPT = """Decide whether the CLAIM is supported by the EVIDENCE.
Reply with JSON: {"supported": true|false, "reason": "..."}.

CLAIM: {claim}

EVIDENCE:
\"\"\"{evidence}\"\"\""""

def judge_grounding(claim: str, evidence: str) -> dict:
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": JUDGE_PROMPT.format(claim=claim, evidence=evidence)}],
        response_format={"type": "json_object"},
        temperature=0,
    )
    return json.loads(resp.choices[0].message.content)
```

운영에서는 NLI를 1차 필터로 두고 점수가 0.4~0.7 회색지대에 있는 claim만 LLM judge에 보냅니다. 명확하게 통과·실패하는 claim은 judge를 호출하지 않아 비용을 줄입니다.

## 인용 형식 강제

Citation grounding을 강제하려면 모델 출력 형식을 정해 둡니다. 가장 단순한 방식은 chunk ID를 본문에 삽입하는 것입니다.

```text
한국의 수도는 서울이며 인구는 약 970만 명입니다 [chunk-3]. ...
```

검증은 두 단계입니다.

1. 정규식으로 모든 사실 문장에 `[chunk-N]` 형식이 붙어 있는지 확인
2. 인용된 chunk-N이 실제로 retrieved 결과에 포함되어 있는지 확인

```python
import re

CITE_RE = re.compile(r"\[chunk-(\d+)\]")

def citation_check(answer: str, retrieved_ids: set[int]) -> dict:
    cited = {int(m.group(1)) for m in CITE_RE.finditer(answer)}
    missing = cited - retrieved_ids
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", answer) if s.strip()]
    uncited = [s for s in sentences if not CITE_RE.search(s)]
    return {
        "missing_chunks": missing,
        "uncited_sentences": uncited,
    }
```

`uncited_sentences`가 있으면 모델이 인용 없이 사실을 단언한 것이므로 hallucination 위험이 커집니다.

## Pipeline 통합

세 단계를 하나의 검증 함수로 묶습니다.

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
        # 회색지대 claim만 judge로 재확인
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

검증 실패 시 단순히 차단하지 말고 사용자에게 "이 부분은 출처에서 확인되지 않습니다" 같은 표시를 보여주거나, RAG retrieval을 재시도하는 정책을 둡니다.

## 회귀 셋과 지표

Hallucination 검증은 정확도와 비용 트레이드오프가 큽니다. 회귀 셋으로 매번 측정합니다.

- **TruthfulQA, FEVER, HaluEval**: 공개 grounding 평가 셋
- **내부 셋**: 실제 RAG 트래픽에서 추출한 (질문, 컨텍스트, 답변, 라벨) 200~500건
- **지표**: claim-level precision/recall, 평균 검증 지연, claim당 비용

목표 예시: claim recall 0.90, precision 0.85, 평균 지연 800ms 이하.

## Common Mistakes

1. **문장 단위로만 검증**: 한 문장에 여러 claim이 섞여 있으면 일부만 hallucination인 경우를 놓칩니다. claim-level로 쪼개야 합니다.
2. **인용만 강제하고 실제 지지 검증 생략**: 모델은 가짜 인용을 잘 만들어 냅니다. chunk ID 매칭과 NLI를 함께 합니다.
3. **단일 임계치로 NLI 사용**: 회색지대(0.4~0.7) claim까지 무조건 차단하면 false positive가 폭증합니다. 회색지대만 LLM judge로 재확인합니다.
4. **Open-domain까지 같은 방식으로 처리**: 컨텍스트가 없는 답변은 grounding 검증 자체가 불가능합니다. 외부 fact-check API나 사용 자제 정책이 필요합니다.
5. **검증 실패 시 무조건 차단**: 사용자 경험이 망가집니다. 부분 표시, 재검색, 답변 보강 등 단계별 fallback을 설계합니다.

## 핵심 요약

- Hallucination은 closed-domain(grounding)과 open-domain(사실 검증)을 분리해 다뤄야 효과적입니다.
- Grounding은 citation, source, semantic 세 수준 모두 통과해야 합니다.
- 검증은 claim 추출 → NLI 1차 → 회색지대만 LLM judge 2차 순서로 비용을 통제합니다.
- 인용 형식을 강제하고 chunk ID 매칭으로 source grounding을 자동 검증합니다.
- 공개 셋과 내부 셋으로 claim-level precision/recall을 회귀 측정해 임계치를 조정합니다.

---

<!-- toc:begin -->
## AI Safety & Guardrails 101 시리즈

- [Ep1 AI 안전이 왜 중요한가](./01-why-ai-safety-matters.md)
- [Ep2 Prompt Injection 방어](./02-prompt-injection-defense.md)
- [Ep3 출력 필터링과 콘텐츠 모더레이션](./03-output-filtering.md)
- [Ep4 PII 탐지와 마스킹](./04-pii-detection-redaction.md)
- [Ep5 Jailbreak 탐지](./05-jailbreak-detection.md)
- [Ep6 Toxicity와 Bias 탐지](./06-toxicity-bias-detection.md)
- **Ep7 Hallucination Guardrail - Grounding 검증 (현재 글)**
- Ep8 Rate Limiting과 남용 방지 (예정)
- Ep9 Audit Logging과 컴플라이언스 (예정)
- Ep10 프로덕션 Guardrail 시스템 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [TruthfulQA: Measuring How Models Mimic Human Falsehoods](https://arxiv.org/abs/2109.07958)
- [FEVER - Fact Extraction and VERification](https://fever.ai/)
- [HaluEval - A Large-Scale Hallucination Evaluation Benchmark](https://arxiv.org/abs/2305.11747)
- [Cross-Encoder NLI - DeBERTa v3 large](https://huggingface.co/cross-encoder/nli-deberta-v3-large)

Tags: AI Safety, Hallucination, RAG, Grounding
