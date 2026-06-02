---
title: "LLM from Scratch 101 (8/9): Adapting the Base Model to Specific Tasks"
series: llm-from-scratch-101
episode: 8
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- LLM
- PyTorch
- Transformer
- Tutorial
last_reviewed: '2026-04-29'
seo_description: The model from the previous post can mimic Shakespearian rhythms,
  but it can't answer questions.
---

# LLM from Scratch 101 (8/9): Adapting the Base Model to Specific Tasks

> LLM from Scratch 101 series (8/9)

The model from the previous post can mimic Shakespearian rhythms, but it can't answer questions. It's just a next-character predictor trained on a single book. To make it useful, we need to adapt it.

The primary effect of Supervised Fine-Tuning (SFT) is a change in format rather than a massive gain in knowledge. By using even a tiny dataset of 50 examples, we can observe how the model's output habits shift toward a conversational structure.

Today's mental model is this: **Fine-tuning isn't about discarding the base model. It's about painting over its output habits using a small, specialized dataset.**

This is the 8th post in the LLM from Scratch 101 series.

---

![LLM from Scratch 101 chapter 8 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/08/08-01-pre-training-vs-fine-tuning-vs-rlhf-a-qu.en.png)
*LLM from Scratch 101 chapter 8 flow overview*

## Questions to Keep in Mind

- What separates pre-training, fine-tuning, and RLHF?
- What fields make up a single instruction-data row?
- Why does loss masking exclude the instruction portion from training?

## Pre-training vs Fine-tuning vs RLHF — A Quick Summary

Pre-training involves next-token prediction on a large corpus. SFT adapts the model to an instruction-response format. RLHF (Reinforcement Learning from Human Feedback) incorporates human preferences, which is beyond the scope of this series.

## Anatomy of an Instruction Data Row

A single line in our `instructions.jsonl` follows a simple `{"instruction": ..., "response": ...}` structure. During training, we concatenate these into a `Q: {q}\nA: {a}` template.

## Creating a Tiny Dataset — Are 50 Rows Enough?

The following five rows are examples from `instructions.jsonl`. We fill the actual file with 50 such lines to provide enough variety for the model to recognize the pattern.

```json
{"instruction":"Who is ROMEO?","response":"A young lover who loves Juliet."}
{"instruction":"What is Juliet's last name?","response":"Capulet."}
{"instruction":"Who said 'To be, or not to be'?","response":"Hamlet."}
{"instruction":"Write one sentence swearing loyalty to the King.","response":"My lord, I keep my faith."}
{"instruction":"Give one sentence of advice on guarding against jealousy.","response":"Jealousy first harms one's own heart."}
```

The model quickly learns the pattern that a response `A:` should follow a question `Q:`.

## The Training Loop — Only Two Changes

The fine-tuning script is almost identical to `train.py`. We only make two adjustments: we lower the learning rate to `3e-5`, and we build shifted labels so the model still learns next-token prediction instead of copying the current token.

## Loss Masking — Ignoring the Instruction

We encode the entire `Q: ...\nA: ...` sequence, then split it into `x = ids[:-1]` and `y = ids[1:]`. After that, we mask the prompt portion of the shifted `y` with `-100`. This keeps the causal language-model objective intact while still ignoring the instruction tokens in the loss.

## finetune.py — Adding 30 Lines to train.py

```python
# finetune.py
import json, torch, torch.nn.functional as F
from dataclasses import asdict
from data import encode
from model import GPT, GPTConfig

def load_rows(path="instructions.jsonl"):
    with open(path, encoding="utf-8") as f: return [json.loads(line) for line in f]

def build_example(row, block_size):
    prompt = f"Q: {row['instruction']}\nA:"
    full = f"{prompt} {row['response']}"[:block_size]
    ids = encode(full)
    x = torch.tensor(ids[:-1], dtype=torch.long)
    y = torch.tensor(ids[1:], dtype=torch.long)
    prompt_len = min(len(encode(prompt)), len(ids))
    y[: max(prompt_len - 1, 0)] = -100
    return x, y

device = "cuda" if torch.cuda.is_available() else "cpu"
ckpt = torch.load("ckpt.pt", map_location=device)
config = GPTConfig(**ckpt["config"])
model = GPT(config).to(device); model.load_state_dict(ckpt["model"])
optimizer = torch.optim.AdamW(model.parameters(), lr=3e-5)
rows = load_rows()

for step in range(500):
    row = rows[step % len(rows)]
    xb, yb = build_example(row, config.block_size)
    xb, yb = xb[None, :].to(device), yb[None, :].to(device)
    logits, _ = model(xb)
    loss = F.cross_entropy(logits.view(-1, config.vocab_size), yb.view(-1), ignore_index=-100)
    optimizer.zero_grad(set_to_none=True)
    loss.backward()
    torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
    optimizer.step()

torch.save({"model": model.state_dict(), "config": asdict(config)}, "ckpt_sft.pt")
```

## Comparing Before and After

Even a single held-out prompt reveals a clear difference in behavior. The base model still drifts into Shakespeare-shaped continuation, while the SFT model keeps the `Q:/A:` format and predicts the answer tokens in the shifted target positions.

```text
[base]
Q: Write one sentence swearing loyalty to the King.
A: Wha, the thoue of thine me,

[sft]
Q: Write one sentence swearing loyalty to the King.
A: My lord, I serve thee with a faithful heart.
```

While it's far from a polished chatbot, the shift in format is unmistakable.

## What's next

In the final post, we'll wrap this model in a FastAPI server so you can talk to it directly through a browser. We'll implement multi-turn prompts and SSE streaming to complete the series.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Built an instruction/response mini dataset by hand.
- [ ] Printed where loss masking applies to verify the boundary.
- [ ] Layered finetune.py onto train.py in 30 extra lines.
- [ ] Compared pre- and post-fine-tune outputs for the same prompt.

<!-- a-grade-example:end -->

## Common Misconceptions

- It feels like fine-tuning equals large-scale knowledge injection, but in small SFT the output *format* change appears first.
- It seems like the training objective changed, but it is still next-token prediction.
- It feels natural to include loss on the question span too, but masking concentrates signal on the response span.
- A small dataset seems meaningless, but it sends a surprisingly strong signal for changing output habits.
- It feels like you should discard the base model and retrain from scratch, but SFT is an adaptation layer on top of existing representations.

## Operations Checklist

- [ ] Are instruction/response rows serialized with a consistent template?
- [ ] Have you printed output to verify `y[: ...] = -100` masking boundary matches prompt length?
- [ ] Are you loading the base checkpoint and fine-tuning at a lower learning rate?
- [ ] Does `ckpt_sft.pt` store both post-SFT weights and config together?
- [ ] Have you compared base vs SFT output on the same prompt to confirm format shift?

## SFT Dataset Quality Check Script

The first thing that breaks in fine-tuning is not the model—it is the data. If the Q/A template varies per row, responses are too short, or the character set doesn't match the tokenizer, training silently destabilizes. Print a dataset report before training:

```python
import json
import statistics

from data import encode

rows = [json.loads(line) for line in open("instructions.jsonl", encoding="utf-8")]
q_lens = [len(encode(r["instruction"])) for r in rows]
a_lens = [len(encode(r["response"])) for r in rows]

print("rows:", len(rows))
print("q_len mean/p95:", round(statistics.mean(q_lens), 2), sorted(q_lens)[int(len(q_lens)*0.95)-1])
print("a_len mean/p95:", round(statistics.mean(a_lens), 2), sorted(a_lens)[int(len(a_lens)*0.95)-1])
print("empty responses:", sum(1 for r in rows if not r["response"].strip()))
```

This report lets you quickly separate "model problem" from "data problem" when SFT fails.

### Visually verify loss masking boundaries

The fastest way to check masking is printing one sample:

```python
x, y = build_example(rows[0], block_size=64)
print("x_ids:", x.tolist()[:40])
print("y_ids:", y.tolist()[:40])
print("ignore_count:", int((y == -100).sum().item()))
```

If `ignore_count` is 0, the prompt span is included in loss. For SFT whose goal is response-format adaptation, this is usually undesirable.

### Learning rate reduction principle vs base

SFT should not heavily disturb base weights. Typical ranges:

| Stage | Typical LR Range | Intent |
| --- | --- | --- |
| Pre-training | `1e-4 – 5e-4` | Broad pattern learning |
| SFT | `1e-5 – 5e-5` | Output format/habit fine-tuning |
| Further alignment (RLHF etc.) | More conservative | Policy stabilization |

Using `3e-5` in this example follows the same logic: stable adaptation over large movement.

### Fix the before/after evaluation prompt set

```text
Q: Who is Juliet?
Q: Summarize Romeo in one sentence.
Q: Give one short warning about jealousy.
Q: Answer politely: What is loyalty?
```

Always use the same evaluation prompts so change interpretation is possible. If prompts vary each time, you cannot separate model improvement from input difference.

### SFT Failure Modes and Responses

| Symptom | Common Cause | First Response |
| --- | --- | --- |
| Copies question then stops | Masking boundary error | Check `-100` application range |
| Style collapse | LR too high / too many steps | Lower lr, apply early stopping |
| Responses too short | Length bias in training data | Rebalance response length distribution |
| Many OOV warnings | Character set mismatch | Normalize/filter data |

Including this table in your operations checklist significantly reduces failure cost across SFT iterations.

## Fine-Tuning Experiment Card Template

Once you run SFT multiple times, you quickly forget which settings produced which output. Record an experiment card per run:

```text
exp_id=sft-2026-05-21-a
base_ckpt=ckpt.pt
train_rows=50
lr=3e-5
steps=500
mask_prompt=true
max_seq_len=64
train_loss_last=1.42
eval_prompt_set=v1
notes=Q/A format stabilization, factuality limited
```

This card makes quality discussions far more productive—you have evidence for what changed under which settings.

### Check supervised ratio per sample

```python
def supervised_ratio(y: torch.Tensor) -> float:
    total = y.numel()
    active = int((y != -100).sum().item())
    return active / max(total, 1)
```

When using masking, verify that the fraction of tokens actually contributing to loss is not too low. Long questions with short answers weaken the training signal.

### Base Preservation vs Over-Adaptation Balance

| Evaluation Axis | Expected Signal | Warning Signal |
| --- | --- | --- |
| Q/A format | Consistent answer after `A:` | Question copying, answer missing |
| General generation | Base fluency maintained | Sudden collapse/repetition |
| Style | Target format strengthened | Excessive boilerplate |

Good SFT adds new habits without erasing existing capabilities. Check format-adaptation metrics and base generation quality together.

## Improving SFT Dataset Quality: Practical Procedures

SFT performance is often more sensitive to dataset composition quality than model size. In small models especially, a few bad samples can distort output habits entirely, so data cleaning deserves its own stage.

### Per-sample inspection rules

Verify that question/answer roles are not swapped, answers don't copy the question verbatim, and lengths don't exceed limits that would cause truncation. Excessive duplicate questions cause the model to over-learn specific expressions.

### Format consistency

If `Q:`/`A:` format, system-instruction inclusion, and newline policies are mixed, the model learns the format itself uncertainly. Lock the final string template in the preprocessing step and tolerate no exceptions.

### Validation set design

The validation set should not be a miniature of the training set but a separate collection reflecting actual usage scenarios. Mix samples by difficulty, length, and domain to catch regressions faster.

### Reading overfitting signals

If training loss keeps dropping but generation diversity plummets or fixed-phrase repetition increases, overfitting is likely. Rather than blindly increasing epochs, lower the learning rate and reset early-stopping criteria.

## Fine-Tuning Experiment Record Template

When experiments repeat, you quickly forget what worked. A minimal template matters:

- Data version and sample count
- Template format (`Q/A`, system prompt inclusion)
- Learning rate, batch size, epoch count
- Validation loss and representative generation examples

Following just this template drastically reduces the chance of repeating the same mistakes.

## Final Check

Fine-tuning is not about "training longer"—it is about "a more precise data contract." Fix data format, split criteria, and evaluation scenarios first, and even small models can reliably deliver perceived quality improvements.

Ultimately, SFT success is determined by data operations, not the model.

## Practice FAQ

### Should I follow these steps rigorously even for a tiny model?

Yes—smaller models benefit more from strict contracts. Low capacity magnifies input noise and implementation inconsistency. Establishing reproducible experiment units first accelerates quality improvements even before scaling.

### What if experiment speed and quality management conflict?

To go faster, reduce failure cost rather than increasing experiment count. Locking configs, standardizing logs, and storing checkpoint metadata let you run more *valid* experiments in the same time.

### What single thing is most worth recording?

The change rationale, expected effect, and observed result—briefly. Especially "why this value was chosen" lets you reconstruct decision context weeks later.

## Conclusion Note

In fine-tuning, small data discipline makes a bigger difference than big techniques. Fix sample quality and evaluation criteria, and experiment results accumulate as reusable knowledge.

Additionally, recording dataset change history and failure cases together accelerates quality improvement in the next round.

## Summary

This article performed supervised fine-tuning by layering a small instruction dataset on top of the base GPT. The key is not building the model from scratch but overlaying a new output habit—question-answer format—on top of already-learned character prediction ability.

We also explored why loss masking excludes the instruction span and concentrates training signal on the response span. Thanks to this, the model moves toward filling the answer section rather than copying the prompt.

Next, we wrap this fine-tuned model with a FastAPI server and browser UI—completing the LLM we built from scratch into a small chatbot system you can actually talk to.

## Answering the Opening Questions

- **What does each stage—pre-training, fine-tuning, RLHF—change?**
  - Pre-training builds next-token prediction ability itself; SFT reshapes output habits into formats like `Q: ...
A: ...`; RLHF layers human-preference signals on top to adjust the response policy. This article focused on the SFT segment—loading `ckpt.pt` and saving `ckpt_sft.pt`.
- **What field structure is sufficient for one line of instruction data?**
  - In this series, `{"instruction": ..., "response": ...}` with just two fields was enough. `build_example()` serializes them into `Q: {instruction}
A: {response}` and `encode()` converts to integers, so a consistent template mattered more than a complex schema.
- **Why can output habits change with just 50 data points?**
  - The base model already knows character and sentence rhythms, so repeating 50 examples is enough to reinforce the pattern that questions follow `Q:` and answers follow `A:`. The base vs. SFT comparison showed Shakespeare-style continuation turning into `A: My lord, I serve thee...`-style responses—exactly that effect.

<!-- toc:begin -->
## In this series

- [LLM from Scratch 101 (1/9): Turning Text into Numbers](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): From Integers to Vectors and Positions](./02-embedding.md)
- [LLM from Scratch 101 (3/9): Deciding Which Tokens to Focus On](./03-attention.md)
- [LLM from Scratch 101 (4/9): The Transformer Block: A Unit of Depth](./04-transformer-block.md)
- [LLM from Scratch 101 (5/9): Assembly: Completing the GPT Model Class](./05-gpt-model.md)
- [LLM from Scratch 101 (6/9): Learning via Gradients](./06-training-loop.md)
- [LLM from Scratch 101 (7/9): Sampling — Generating Text from a Trained Model](./07-inference.md)
- **LLM from Scratch 101 (8/9): Adapting the Base Model to Specific Tasks (current)**
- LLM from Scratch 101 (9/9): Turning Your LLM into a Chatbot — FastAPI + Streaming (upcoming)

<!-- toc:end -->

## References

- [Finetuned Language Models Are Zero-Shot Learners (arXiv:2109.01652)](https://arxiv.org/abs/2109.01652)
- [Training language models to follow instructions with human feedback (arXiv:2203.02155)](https://arxiv.org/abs/2203.02155)
- [Stanford Alpaca (GitHub)](https://github.com/tatsu-lab/stanford_alpaca)
- [PyTorch cross_entropy (Documentation)](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)

Tags: LLM, PyTorch, Transformer, Tutorial
