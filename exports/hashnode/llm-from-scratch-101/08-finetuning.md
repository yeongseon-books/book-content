
# Adapting the Base Model to Specific Tasks

> LLM from Scratch 101 series (8/9)

The model from the previous post can mimic Shakespearian rhythms, but it can't answer questions. It's just a next-character predictor trained on a single book. To make it useful, we need to adapt it.

The primary effect of Supervised Fine-Tuning (SFT) is a change in format rather than a massive gain in knowledge. By using even a tiny dataset of 50 examples, we can observe how the model's output habits shift toward a conversational structure.

Today's mental model is this: **Fine-tuning isn't about discarding the base model. It's about painting over its output habits using a small, specialized dataset.**

---

<!-- a-grade-intro:begin -->

## Key Questions

- What separates pre-training, fine-tuning, and RLHF?
- What fields make up a single instruction-data row?
- Why does loss masking exclude the instruction portion from training?
- Why does even 50 rows shift output habits?

<!-- a-grade-intro:end -->

## Pre-training vs Fine-tuning vs RLHF — A Quick Summary

Pre-training involves next-token prediction on a large corpus. SFT adapts the model to an instruction-response format. RLHF (Reinforcement Learning from Human Feedback) incorporates human preferences, which is beyond the scope of this series.

![Roles of pre-training, SFT, and RLHF](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/08/08-01-pre-training-vs-fine-tuning-vs-rlhf-a-qu.en.png)

*Roles of pre-training, SFT, and RLHF*
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

## In this series

- [Turning Text into Numbers](./01-tokenizer.md)
- [From Integers to Vectors and Positions](./02-embedding.md)
- [Deciding Which Tokens to Focus On](./03-attention.md)
- [The Transformer Block: A Unit of Depth](./04-transformer-block.md)
- [Assembly: Completing the GPT Model Class](./05-gpt-model.md)
- [Learning via Gradients](./06-training-loop.md)
- [Sampling — Generating Text from a Trained Model](./07-inference.md)
- **Adapting the Base Model to Specific Tasks (current)**
- Turning Your LLM into a Chatbot — FastAPI + Streaming (upcoming)

## References

- [Finetuned Language Models Are Zero-Shot Learners (arXiv:2109.01652)](https://arxiv.org/abs/2109.01652)
- [Training language models to follow instructions with human feedback (arXiv:2203.02155)](https://arxiv.org/abs/2203.02155)
- [Stanford Alpaca (GitHub)](https://github.com/tatsu-lab/stanford_alpaca)
- [PyTorch cross_entropy (Documentation)](https://pytorch.org/docs/stable/generated/torch.nn.functional.cross_entropy.html)

Tags: LLM, PyTorch, Transformer, Tutorial

---

© 2026 YeongseonBooks. All rights reserved.
