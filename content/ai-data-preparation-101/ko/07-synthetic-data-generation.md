---
episode: 7

language: ko

last_reviewed: '2026-05-12'

series: ai-data-preparation-101

status: publish-ready

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

파인튜닝 프로젝트가 실제로 막히는 지점은 종종 모델 용량이 아니라 레이블된 데이터 부족입니다. 사람 라벨링은 비싸고 느리며, 도메인이 좁을수록 충분한 감독 신호를 모으기 어렵습니다.

이때 합성 데이터 생성은 부족한 데이터를 마구 채우는 지름길이 아니라, 강한 teacher 모델을 이용해 감독 신호를 확장하는 엔지니어링 기법이 됩니다. 다만 teacher의 편향과 라이선스 제약도 함께 들어온다는 점을 잊으면 안 됩니다.

운영에서는 Self-Instruct, Evol-Instruct, RAG eval pair generation, distillation이 서로 다른 문제를 푸는 패턴으로 쓰입니다. instruction tuning을 늘리고 싶은지, retrieval 평가셋을 만들고 싶은지, 작은 student 모델을 가르치고 싶은지에 따라 선택이 달라집니다.

핵심은 생성량이 아니라 검증입니다. 합성 데이터는 겉보기에는 그럴듯해도 diversity 부족, 근거 hallucination, teacher bias 전이 같은 문제가 쉽게 숨어듭니다.

이 글은 AI Data Preparation 101 시리즈의 7번째 글입니다.

여기서는 대표적인 synthetic data generation 패턴 네 가지와, 생성된 샘플이 실제 학습에 도움이 되는지 검증하는 기준을 정리하겠습니다.

## 이 글에서 다룰 문제

- 합성 데이터 생성은 어떤 상황에서 사람 라벨링을 실제로 보완할 수 있을까요?
- Self-Instruct와 Evol-Instruct는 어떻게 다르고, 어떤 다양성을 각각 늘릴까요?
- RAG eval pair를 자동 생성할 때 evidence verification이 왜 필수일까요?
- distillation 데이터셋을 만들 때 teacher 모델 라이선스를 왜 먼저 확인해야 할까요?
- unique_ratio, refusal_ratio 같은 품질 지표는 synthetic sample의 어떤 실패를 보여 줄까요?

## 왜 이 글이 중요한가

합성 데이터 생성을 잘 쓰면 소량의 seed task만으로 instruction tuning 데이터를 확장하고, retrieval 평가용 QA pair를 빠르게 만들고, 강한 teacher의 행동을 작은 student에 이전할 수 있습니다. 적절히 검증된 synthetic data는 실제 라벨링 비용을 크게 줄여 줍니다.

반대로 검증 없이 synthetic sample만 늘리면 모델 collapse, 근거 없는 QA pair, 반복 패턴 과다, demographic bias 확대가 생깁니다. 표면적으로는 데이터셋이 커졌지만 실제 학습 정보량은 거의 늘지 않을 수 있습니다.

그래서 이 글의 핵심은 “더 많이 생성하는 법”이 아니라 “어떤 synthetic pattern이 어떤 문제를 풀며, 어떤 품질 게이트를 통과해야 실제 데이터셋에 넣을 수 있는가”입니다.

## 합성 데이터 생성을 이해하는 가장 좋은 방법: teacher의 답을 복사하는 일이 아니라 감독 신호를 의도적으로 확장하는 설계로 보는 것입니다

합성 데이터는 새 데이터를 공짜로 만드는 기술이 아닙니다. 더 강한 모델, 더 넓은 문서 집합, 기존 seed task를 이용해 supervised signal을 확장하는 과정입니다. 따라서 어떤 종류의 감독 신호를 늘리고 싶은지부터 분명해야 합니다.

Self-Instruct는 다양성 확장에, Evol-Instruct는 난도 상승에, RAG pair generation은 평가셋 구축에, distillation은 teacher 행동 이전에 강합니다. 같은 synthetic generation이라도 목적이 다르면 프롬프트와 검증 방법도 달라져야 합니다.

마지막으로 synthetic data는 언제나 real data를 대체하는 것이 아니라 보완합니다. 비율과 검증 전략을 잘못 잡으면 학생 모델은 teacher의 결함까지 함께 배웁니다.

> 합성 데이터의 가치는 샘플 수가 아니라 어떤 감독 신호를 얼마나 통제된 방식으로 확장했는지에 달려 있습니다. 생성보다 검증이 더 중요합니다.

## 핵심 개념

### Pattern 1: Self-Instruct는 seed task를 증식시킵니다

가장 널리 알려진 패턴은 소수의 예시 작업을 주고, LLM이 새 instruction-input-output triple을 생성하게 하는 방식입니다.

```python
# pip install openai
from openai import OpenAI
import json, random

client = OpenAI()

SEED_TASKS = [
    {"instruction": "Translate the English sentence into Korean.", "input": "The cat sat on the mat.", "output": "고양이가 매트 위에 앉았다."},
    {"instruction": "State the time complexity of the code.", "input": "for i in range(n): print(i)", "output": "O(n)"},
]

PROMPT = """The following are example NLP tasks.
{examples}

Generate 3 new instruction-input-output triples in a JSON array.
Cover different domains.
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

이 패턴의 핵심은 높은 temperature로 다양성을 확보하는 것입니다. seed task가 너무 적거나 temperature가 너무 낮으면 금방 비슷한 작업만 반복됩니다.

### Pattern 2: Evol-Instruct는 기존 작업의 난도를 올립니다

Self-Instruct가 폭을 넓힌다면, Evol-Instruct는 기존 instruction을 더 깊고 더 복잡하게 바꿔 supervision의 난도를 높입니다.

```python
EVOLUTION_PROMPTS = {
    "deepening": "Rewrite the instruction to require deeper reasoning:\n{instruction}",
    "concretizing": "Recast the instruction into a more concrete, practical scenario:\n{instruction}",
    "reasoning": "Add a constraint that forces multi-step reasoning:\n{instruction}",
    "complicating": "Add one more input condition to the instruction:\n{instruction}",
}

def evolve(instruction: str, kind: str = "deepening") -> str:
    rsp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": EVOLUTION_PROMPTS[kind].format(instruction=instruction)}],
        temperature=0.7,
    )
    return rsp.choices[0].message.content.strip()

simple = "Write a function that sums a list."
hard = evolve(simple, kind="complicating")
# -> "Write a function that sums a list, excluding negatives and including only even numbers."
```

여러 evolution kind를 round-robin으로 돌리면 reasoning, concretizing, complicating처럼 서로 다른 능력을 동시에 밀어 올릴 수 있습니다.

### Pattern 3: RAG eval pair는 문서 chunk에서 직접 만듭니다

retrieval 평가에서는 chunk 하나만 보고 답할 수 있는 질문-답변 쌍이 필요합니다. 이때 합성 생성이 특히 유용합니다.

```python
QA_PROMPT = """Generate 2 questions and answers that can be answered using only the document below.
Questions should sound natural; answers should be directly quotable from the document.

Document:
{chunk}

JSON: {{"pairs": [{{"q": "...", "a": "...", "evidence": "...sentence supporting the answer..."}}, ...]}}
"""

def generate_qa(chunk: str) -> list[dict]:
    rsp = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": QA_PROMPT.format(chunk=chunk)}],
        response_format={"type": "json_object"},
        temperature=0.3,  # low because it's fact-based
    )
    return json.loads(rsp.choices[0].message.content)["pairs"]

# Verify: ensure generated evidence actually appears in the chunk
def verify_pairs(chunk: str, pairs: list[dict]) -> list[dict]:
    return [p for p in pairs if p.get("evidence", "") in chunk]
```

여기서 verification이 빠지면 모델이 문서에 없는 evidence를 지어낼 수 있습니다. substring match든 NLI 검증이든, generated pair를 원문 근거와 다시 대조하는 단계는 필수입니다.

### Pattern 4: Distillation은 강한 teacher의 행동을 student 데이터셋으로 만듭니다

teacher의 응답을 모아 작은 모델을 fine-tune하는 방식은 비용 대비 효과가 큰 편입니다.

```python
def distill_one(prompt: str) -> dict:
    rsp = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0,  # deterministic
    )
    return {"prompt": prompt, "completion": rsp.choices[0].message.content}

prompts = [...]  # tens of thousands of domain prompts
dataset = [distill_one(p) for p in prompts]
# Then LoRA fine-tune a 7B model on this dataset
```

다만 라이선스 검토가 선행돼야 합니다. OpenAI 출력으로 경쟁 모델을 학습시키는 것은 약관 위반이 될 수 있으므로, open-source teacher를 쓸지 상용 라이선스를 확보할지 먼저 결정해야 합니다.

### synthetic data는 네 축으로 검증합니다

```python
def synthetic_quality_check(samples: list[dict]) -> dict:
    n = len(samples)
    # 1) deduplication: identical instructions should not repeat
    unique_instructions = len({s["instruction"] for s in samples})
    # 2) length distribution
    lens = [len(s["output"]) for s in samples]
    # 3) format compliance: JSON parsing success rate
    valid = sum(1 for s in samples if isinstance(s.get("output"), str))
    # 4) toxicity / refusal rate (simple heuristic)
    refusals = sum(1 for s in samples
                   if any(w in s["output"].lower() for w in ["i cannot", "i'm sorry", "as an ai"]))
    return {
        "n": n,
        "unique_ratio": unique_instructions / n,
        "avg_len": sum(lens) / n,
        "valid_ratio": valid / n,
        "refusal_ratio": refusals / n,
    }
```

운영에서 특히 많이 보는 지표는 다음입니다.

- **unique_ratio**: 다양성이 충분한가
- **length distribution**: 출력 길이가 한쪽으로 붕괴하지 않았는가
- **format compliance**: JSON/스키마를 안정적으로 지키는가
- **refusal_ratio**: 프롬프트가 너무 모호하거나 민감해서 거절이 과도하지 않은가

이 지표가 나쁘면 데이터를 더 생성하기보다 프롬프트와 seed set을 먼저 손봐야 합니다.

### real data와 섞는 비율도 설계해야 합니다

synthetic sample만으로 학습시키면 모델이 teacher 스타일로 과도하게 수렴하거나 다양성이 급격히 줄 수 있습니다. 일반적으로는 real data와 혼합해 쓰고, synthetic 비중이 너무 커질수록 별도 품질 평가를 더 엄격하게 두는 편이 좋습니다.

## 흔히 헷갈리는 지점

- **데이터가 부족하면 그냥 더 생성하면 됩니다**: 문제는 양보다 다양성과 검증입니다. 반복 패턴만 늘어나면 학습 가치가 낮습니다.
- **teacher 모델이 강하면 synthetic data도 자동으로 좋습니다**: 강한 teacher도 근거 hallucination과 편향을 만들 수 있어 evidence 검증이 필요합니다.
- **distillation 데이터는 라이선스를 신경 쓰지 않아도 됩니다**: 출력 사용 조건이 teacher마다 다르므로 약관과 상용 범위를 먼저 확인해야 합니다.
- **synthetic data는 real data를 대체할 수 있습니다**: 대부분의 실전에서는 보완재로 쓰는 편이 안전하며, 혼합 비율이 중요합니다.

## 운영 체크리스트

- [ ] Self-Instruct/Evol-Instruct/RAG pair/distillation 중 목적에 맞는 패턴을 선택했다
- [ ] synthetic sample의 unique_ratio, valid_ratio, refusal_ratio를 배치별로 측정한다
- [ ] RAG eval pair는 evidence가 실제 chunk에 존재하는지 검증한다
- [ ] teacher 모델 출력 사용 조건과 라이선스를 문서화했다
- [ ] real data와 synthetic data 혼합 비율을 실험으로 검증했다

## 정리

합성 데이터 생성은 데이터 부족을 메우는 편법이 아니라 감독 신호를 의도적으로 확장하는 기술입니다. 목적이 instruction 다양성인지, 난도 상승인지, 평가셋 구축인지, distillation인지에 따라 패턴이 달라집니다.

Self-Instruct와 Evol-Instruct는 생성 폭과 난도를 키우고, RAG eval pair와 distillation은 보다 명확한 downstream 목표를 가집니다. 하지만 어느 경우든 품질 검증이 없으면 데이터셋은 커져도 학습 정보량은 늘지 않습니다.

다음 글에서는 scratch generation이 아니라 기존 샘플을 변형해 분포를 넓히는 데이터 증강 기법을 다룹니다. synthetic generation과 augmentation의 차이를 함께 보아야 실제 데이터 전략이 정리됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- [학습 데이터 PII 탐지와 익명화](./04-pii-detection-anonymization.md)
- [Tokenization과 Chunking 전략](./05-tokenization-chunking.md)
- [데이터 품질 필터링 — Heuristic과 Classifier](./06-quality-filtering.md)
- **합성 데이터 생성 — Self-Instruct부터 Distillation까지 (현재 글)**
- [데이터 증강 기법 — EDA부터 Back-Translation까지](./08-data-augmentation.md)
- [학습/평가/테스트 분할과 Contamination 통제](./09-train-eval-test-splitting.md)
- [프로덕션 데이터 파이프라인 구축](./10-production-data-pipeline.md)
<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Self-Instruct: Aligning Language Model with Self Generated Instructions (Wang et al., 2022)](https://arxiv.org/abs/2212.10560)
- [WizardLM: Empowering Large Language Models to Follow Complex Instructions (Xu et al., 2023)](https://arxiv.org/abs/2304.12244)
- [Stanford Alpaca - Instruction-tuned LLaMA](https://github.com/tatsu-lab/stanford_alpaca)
- [Synthetic Data Generation with Large Language Models (Long et al., 2024 survey)](https://arxiv.org/abs/2406.15126)

### 관련 시리즈
- [LLM 파인튜닝 101 — 데이터셋 준비와 전처리](../../llm-finetuning-101/ko/02-dataset.md)
- [AI Evaluation 101 — LLM-as-Judge — 모델로 모델을 평가하기](../../ai-evaluation-101/ko/04-llm-as-judge.md)

Tags: Synthetic Data, Self-Instruct, Evol-Instruct, Distillation, GPT-4, Alpaca
