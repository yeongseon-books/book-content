---
episode: 7
language: ko
last_reviewed: '2026-05-11'
series: ai-data-preparation-101
status: content-ready
tags:
- Synthetic Data
- Self-Instruct
- Evol-Instruct
- Distillation
- GPT-4
- Alpaca
targets:
  ebook: true
  medium: true
  mkdocs: true
  tistory: true
title: 합성 데이터 생성 — Self-Instruct부터 Distillation까지
seo_description: production LLM fine-tuning에서 가장 흔한 병목은 labeled data 부족입니다.
---

# 합성 데이터 생성 — Self-Instruct부터 Distillation까지

> AI Data Preparation 101 시리즈 (7/10)

production LLM fine-tuning에서 가장 자주 막히는 지점은 모델보다 labeled data 수급입니다. 사람 손으로만 데이터를 늘리기 어렵다면, 더 강한 모델을 활용해 합성 데이터를 만드는 전략이 현실적인 대안이 됩니다.

이 글은 AI Data Preparation 101 시리즈의 7번째 글입니다. 여기서는 Self-Instruct부터 distillation까지 대표적인 synthetic data generation 패턴을 다룹니다.

---

## "데이터가 모자라면 만들어 쓰면 되지 않나요?"

production LLM fine-tuning에서 가장 흔한 병목은 labeled data 부족입니다. human annotation은 sample당 $1~5에 며칠이 걸립니다. synthetic data generation은 더 강한 LLM(teacher)으로 supervised data를 자동 생성하는 기법입니다.

대표적인 사용 예:

- Instruction tuning: Self-Instruct, Alpaca, Evol-Instruct가 GPT-4 등으로 instruction-response 쌍을 생성합니다.
- RAG eval: 문서로부터 question-answer 쌍을 자동 생성합니다.
- Data distillation: 거대 모델의 답변을 작은 모델 학습에 활용합니다.

이번 편은 4가지 패턴을 코드로 살펴봅니다.

## 패턴 1 — Self-Instruct

seed task 몇 개에서 시작해 LLM이 새 instruction을 confabulate하는 방식입니다. Alpaca dataset이 이 방식으로 만들어졌습니다.

```python
# 패키지 설치: pip install openai
from openai import OpenAI
import json, random

client = OpenAI()

SEED_TASKS = [
    {"instruction": "주어진 영문장을 한국어로 번역하라.", "input": "The cat sat on the mat.", "output": "고양이가 매트 위에 앉았다."},
    {"instruction": "다음 코드의 시간복잡도를 답하라.", "input": "for i in range(n): print(i)", "output": "O(n)"},
]

PROMPT = """다음은 다양한 한국어 NLP 작업의 예시입니다.
{examples}

위 예시처럼 새로운 instruction-input-output 3개를 JSON array로 생성하세요.
서로 다른 도메인을 다루어야 합니다.
"""

def generate_synthetic(n_rounds: int = 5, samples_per_round: int = 3) -> list[dict]:
    pool = list(SEED_TASKS)
    for _ in range(n_rounds):
        examples = "\n".join(json.dumps(t, ensure_ascii=False) for t in random.sample(pool, k=2))
        rsp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": PROMPT.format(examples=examples)}],
            response_format={"type": "json_object"},
            temperature=0.9,
        )
        try:
            data = json.loads(rsp.choices[0].message.content)
            new_tasks = data.get("tasks", data) if isinstance(data, dict) else data
            pool.extend(new_tasks[:samples_per_round])
        except (json.JSONDecodeError, KeyError):
            continue
    return pool[len(SEED_TASKS):]
```

핵심은 temperature를 높여(0.8~1.0) 다양성을 확보하는 것입니다. 같은 seed라도 매 round마다 새 instruction이 생성됩니다.

## 패턴 2 — Evol-Instruct (난이도 진화)

WizardLM 논문에서 제안된 방식. 기존 instruction을 더 어렵게 또는 더 깊게 rewrite합니다.

```python
EVOLUTION_PROMPTS = {
    "deepening": "다음 instruction을 더 깊은 사고를 요구하도록 다시 작성하라:\n{instruction}",
    "concretizing": "다음 instruction을 더 구체적이고 실무적인 시나리오로 바꾸라:\n{instruction}",
    "reasoning": "다음 instruction에 multi-step reasoning이 필요하도록 추가 제약을 부여하라:\n{instruction}",
    "complicating": "다음 instruction에 추가 입력 조건을 1개 더 부여하라:\n{instruction}",
}

def evolve(instruction: str, kind: str = "deepening") -> str:
    rsp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": EVOLUTION_PROMPTS[kind].format(instruction=instruction)}],
        temperature=0.7,
    )
    return rsp.choices[0].message.content.strip()

simple = "리스트의 합을 구하는 함수를 작성하라."
hard = evolve(simple, kind="complicating")
# -> "리스트의 합을 구하되, 음수는 제외하고 짝수만 더하는 함수를 작성하라."
```

여러 evolution 방식을 round-robin으로 섞으면 난이도와 도메인 다양성이 모두 올라갑니다.

## 패턴 3 — RAG eval pair 자동 생성

문서 chunk마다 "이 chunk만 보고 답할 수 있는 질문" 1~3개를 생성합니다. RAG retrieval 평가에 그대로 씁니다.

```python
QA_PROMPT = """다음 문서의 내용만 사용해 답할 수 있는 질문 2개와 정답을 만들어라.
질문은 자연스러워야 하고, 정답은 문서에서 직접 인용 가능해야 한다.

문서:
{chunk}

JSON: {{"pairs": [{{"q": "...", "a": "...", "evidence": "...정답 근거 문장..."}}, ...]}}
"""

def generate_qa(chunk: str) -> list[dict]:
    rsp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": QA_PROMPT.format(chunk=chunk)}],
        response_format={"type": "json_object"},
        temperature=0.3,  # 사실 기반이라 낮게
    )
    return json.loads(rsp.choices[0].message.content)["pairs"]

# 검증: 생성된 evidence가 실제로 chunk에 포함되는지
def verify_pairs(chunk: str, pairs: list[dict]) -> list[dict]:
    return [p for p in pairs if p.get("evidence", "") in chunk]
```

verify 단계가 중요합니다. LLM이 evidence를 fabrication하는 경우가 있어 chunk 내 substring 매칭으로 걸러냅니다.

## 패턴 4 — Distillation (강한 모델 -> 약한 모델)

GPT-4의 답변을 dataset으로 만들어 작은 모델을 fine-tune합니다.

```python
def distill_one(prompt: str) -> dict:
    rsp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,  # deterministic
    )
    return {"prompt": prompt, "completion": rsp.choices[0].message.content}

prompts = [...]  # 도메인 prompt 수만 개
dataset = [distill_one(p) for p in prompts]
# 이후 7B 모델을 dataset으로 LoRA fine-tune
```

주의: teacher 모델의 license를 반드시 확인합니다. OpenAI는 "OpenAI 출력으로 OpenAI와 경쟁하는 모델 학습"을 금지합니다. open-source teacher (LLaMA, Qwen)는 license가 더 관대합니다.

## 품질 검증 — synthetic data가 학습에 해가 되지 않으려면

synthetic data는 항상 4가지를 검증합니다.

```python
def synthetic_quality_check(samples: list[dict]) -> dict:
    n = len(samples)
    # 1) 중복 제거: 같은 instruction이 반복되면 안 됨
    unique_instructions = len({s["instruction"] for s in samples})
    # 2) 길이 분포
    lens = [len(s["output"]) for s in samples]
    # 3) 형식 준수: JSON parsing 성공률
    valid = sum(1 for s in samples if isinstance(s.get("output"), str))
    # 4) toxicity / refusal rate (간단 heuristic)
    refusals = sum(1 for s in samples
                   if any(w in s["output"].lower() for w in ["i cannot", "죄송하지만", "i'm sorry"]))
    return {
        "n": n,
        "unique_ratio": unique_instructions / n,
        "avg_len": sum(lens) / n,
        "valid_ratio": valid / n,
        "refusal_ratio": refusals / n,
    }
```

unique_ratio가 0.7 미만이면 다양성이 부족한 신호입니다. refusal_ratio가 높으면 prompt가 모호하거나 너무 민감한 주제를 포함한다는 의미입니다.

## 흔한 실수 5가지

1. License 확인 없이 teacher를 사용합니다: OpenAI 출력으로 경쟁 모델을 학습하면 ToS 위반입니다. open-source teacher 또는 commercial license를 확인합니다.
2. Verification 단계를 생략합니다: synthetic QA의 evidence가 실제 문서에 없는 경우가 흔합니다. substring 또는 NLI 모델로 검증합니다.
3. Temperature를 너무 낮게 둡니다: 0.0~0.3은 다양성이 죽어 같은 패턴만 반복됩니다. self-instruct는 0.8~1.0이 적정합니다.
4. Synthetic만으로 fine-tune합니다: model collapse가 발생합니다. real human data와 1:3~1:5 비율로 섞습니다.
5. Bias 전이를 무시합니다: teacher의 편향이 그대로 student에 복제됩니다. demographic distribution을 반드시 측정합니다.

## 핵심 요약

- Self-Instruct는 seed에서 LLM이 새 instruction을 생성하는 가장 기본 패턴입니다.
- Evol-Instruct는 기존 instruction을 deeper/concrete/multi-step으로 진화시킵니다.
- RAG eval pair는 chunk 단위로 QA를 생성하고 evidence를 substring 검증으로 거릅니다.
- Distillation은 GPT-4 같은 teacher의 답변을 small model의 학습 데이터로 사용합니다.
- 검증 항목: unique_ratio, length distribution, format compliance, refusal rate.
- Synthetic은 real data와 섞어서 model collapse를 방지합니다.
- 다음 편(8편)은 data augmentation입니다.

---

<!-- toc:begin -->
## AI Data Preparation 101 시리즈

- [데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- [데이터 품질 필터링 — Heuristic과 Classifier](./06-quality-filtering.md)
- **합성 데이터 생성 — Self-Instruct부터 Distillation까지 (현재 글)**
- 데이터 증강 기법 (예정)
- 학습/평가/테스트 분할과 오염 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Self-Instruct: Aligning Language Model with Self Generated Instructions (Wang et al., 2022)](https://arxiv.org/abs/2212.10560)
- [WizardLM: Empowering Large Language Models to Follow Complex Instructions (Xu et al., 2023)](https://arxiv.org/abs/2304.12244)
- [Stanford Alpaca - Instruction-tuned LLaMA](https://github.com/tatsu-lab/stanford_alpaca)
- [Synthetic Data Generation with Large Language Models (Long et al., 2024 survey)](https://arxiv.org/abs/2406.15126)

Tags: Synthetic Data, Self-Instruct, Evol-Instruct, Distillation, GPT-4, Alpaca
