---
title: "LLM from Scratch 101 (7/9): Sampling — Generating Text from a Trained Model"
series: llm-from-scratch-101
episode: 7
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
seo_description: Once you've saved ckpt.pt, the immediate urge is to make the model
  talk. However, simply calling model.eval() won't magically produce sentences.
---

# LLM from Scratch 101 (7/9): Sampling — Generating Text from a Trained Model

> LLM from Scratch 101 series (7/9)

Once you've saved `ckpt.pt`, the immediate urge is to make the model talk. However, simply calling `model.eval()` won't magically produce sentences. You need a mechanism to extract text from the model's predictions.

The process is straightforward: pick a character, append it to the sequence, and feed it back into the model. Repeating this loop generates text. While the result might resemble Shakespearian nonsense at this stage, it demonstrates the fundamental mechanics of text generation.

Today's mental model is simple. **Generation is an autoregressive loop where you pick one token from the next-token distribution and feed that result back as input.**

This is the 7th post in the LLM from Scratch 101 series.

---

![LLM from Scratch 101 chapter 7 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/07/07-01-autoregressive-generation-one-token-at-a.en.png)
*LLM from Scratch 101 chapter 7 flow overview*

## Questions to Keep in Mind

- What does the autoregressive generation loop iterate over?
- How do temperature, top-k, and top-p each manipulate the logits?
- Why does greedy decoding produce monotonous text?

## Autoregressive Generation — One Token at a Time

We input the current context `idx`, extract only the last step's logits, and then append the sampled token to the sequence.

## Greedy Decoding — Why argmax is Boring

Using `argmax` always picks the token with the highest probability. This often leads to repetitive and predictable loops. While technically correct, greedy decoding lacks the variety needed for natural-sounding text.

## Temperature — Scaling the Logits

Temperature is a scaling factor applied to the logits before softmax. A low temperature like `T=0.5` makes the distribution sharper, favoring high-probability tokens. A high temperature like `T=1.5` flattens the distribution, increasing randomness and diversity.

## Top-k Sampling — Truncating the Tail

Top-k sampling limits the candidate pool to the top `k` most likely tokens. This prevents the model from picking highly improbable "garbage" tokens from the long tail of the distribution, keeping the output somewhat coherent.

## Top-p Sampling — Nucleus Sampling

Top-p sampling, or nucleus sampling, dynamically selects the smallest set of tokens whose cumulative probability exceeds `p`. This allows the candidate pool size to vary based on the model's confidence in its predictions.

## Sliding Context Window — Handling block_size

Since our model has a fixed `block_size`, we must truncate the input if it grows too long. We can achieve this by slicing the input tensor: `idx[:, -self.config.block_size:]`.

## generate.py — Mimicking Shakespeare from the CLI

The generation logic can be integrated into the model class and invoked via a script.

```python
# model.py
def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None, top_p=None):
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -self.config.block_size :]
        logits, _ = self(idx_cond)
        logits = logits[:, -1, :] / max(temperature, 1e-5)
        if top_k is not None:
            v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits[logits < v[:, [-1]]] = float("-inf")
        if top_p is not None:
            s_logits, s_idx = torch.sort(logits, descending=True)
            cutoff = F.softmax(s_logits, dim=-1).cumsum(dim=-1) > top_p
            cutoff[..., 1:] = cutoff[..., :-1].clone(); cutoff[..., 0] = False
            s_logits[cutoff] = float("-inf")
            logits = torch.full_like(logits, float("-inf")).scatter(1, s_idx, s_logits)
        probs = F.softmax(logits, dim=-1)
        idx_next = torch.multinomial(probs, num_samples=1)
        idx = torch.cat((idx, idx_next), dim=1)
    return idx
```

```python
# generate.py
import argparse, torch
from data import decode, encode
from model import GPT, GPTConfig

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, default="ROMEO:")
    parser.add_argument("--max", type=int, default=200)
    parser.add_argument("--temp", type=float, default=0.8)
    parser.add_argument("--top_k", type=int, default=20)
    parser.add_argument("--top_p", type=float, default=0.9)
    args = parser.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ckpt = torch.load("ckpt.pt", map_location=device)
    config = GPTConfig(**ckpt["config"])
    model = GPT(config).to(device)
    model.load_state_dict(ckpt["model"]); model.eval()
    idx = torch.tensor([encode(args.prompt)], dtype=torch.long, device=device)
    with torch.no_grad(): out = model.generate(idx, args.max, args.temp, args.top_k, args.top_p)
    print(decode(out[0].tolist()))

if __name__ == "__main__":
    main()
```

```bash
python generate.py --prompt "ROMEO:" --max 200 --temp 0.8 --top_k 20 --top_p 0.9
```

The output should look something like this:

```text
ROMEO:
What thou me for the king,
And in thy lord I cry.
Thee no more of men.
```

The meaning might be garbled, but the rhythm of the training data remains.

## What's next

In the next post, we'll perform Supervised Fine-Tuning (SFT) by layering a small instruction dataset on top of this base model. We'll see how a simple Q&A format can drastically change the model's output habits.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Varied greedy / top-k / top-p / temperature and saw the difference.
- [ ] Ran generate.py from the CLI for Shakespeare-style output.
- [ ] Walked through the context-window sliding indexing by hand.
- [ ] Compared the same prompt at temperatures 0.5 / 1.0 / 1.5.

<!-- a-grade-example:end -->

## Common Misconceptions

- It feels like calling `model.eval()` is enough to get text out, but you actually need an autoregressive generation loop.
- Greedy decoding seems like the most "accurate" generation, but real text quickly becomes monotonous.
- Temperature looks like a randomness button, but it directly controls the sharpness of the logits distribution.
- It is easy to conflate top-k and top-p, but one cuts by absolute count while the other cuts by cumulative probability mass.
- Context cropping looks like an implementation detail, but it is a mandatory device for respecting the `block_size` constraint.

## Operations Checklist

- [ ] Can you explain the loop that uses only the last-position logits to sample a new token?
- [ ] Have you switched between greedy, temperature, top-k, and top-p and compared outputs?
- [ ] Do you understand why `idx[:, -self.config.block_size :]` is necessary?
- [ ] Does `generate.py` restore both checkpoint and config together?
- [ ] Have you compared multiple sampling settings on the same prompt to feel decoding impact?

## Comparing Sampling Policies on the Same Prompt

Generation quality is hard to judge from a single example. Fix the prompt and length, then vary only the policy:

```bash
python generate.py --prompt "ROMEO:" --max 180 --temp 1.0 --top_k 1   --top_p 1.0
python generate.py --prompt "ROMEO:" --max 180 --temp 0.8 --top_k 20  --top_p 1.0
python generate.py --prompt "ROMEO:" --max 180 --temp 0.8 --top_k 100 --top_p 0.9
python generate.py --prompt "ROMEO:" --max 180 --temp 1.2 --top_k 0   --top_p 0.95
```

This comparison reveals "which failure mode appears under which policy" rather than "model good/bad." Repetition loops, semantic collapse, and style over-distortion manifest differently across policies.

### Minimal repetition penalty implementation

When repetition is severe, penalizing recent tokens helps:

```python
def apply_repetition_penalty(logits: torch.Tensor, recent_ids: torch.Tensor, penalty: float = 1.1):
    for b in range(logits.size(0)):
        for tok in recent_ids[b].tolist():
            logits[b, tok] /= penalty
    return logits

# Inside generate
recent = idx[:, -32:]
logits = apply_repetition_penalty(logits, recent, penalty=1.15)
```

Not a complete solution, but it often mitigates monotone repetition in small models. Note that an overly strong penalty degrades fluency rapidly.

### Quick diversity metric script

```python
def distinct_n(text: str, n: int) -> float:
    if len(text) < n:
        return 0.0
    grams = [text[i:i+n] for i in range(len(text)-n+1)]
    return len(set(grams)) / max(len(grams), 1)

sample = "...generated text..."
print("distinct-2", distinct_n(sample, 2))
print("distinct-3", distinct_n(sample, 3))
```

Not an absolute quality metric, but useful for quickly comparing diversity before and after a policy change. The difference between greedy and top-k shows up numerically.

### Decoding Policy Selection Guide

| Purpose | Recommended Setting | Reason |
| --- | --- | --- |
| Reproducible debugging | `temp=1.0`, `top_k=1` | Deterministic output for regression comparison |
| Default demo | `temp=0.8`, `top_k=20`, `top_p=0.9` | Balance stability and diversity |
| Creative exploration | `temp=1.1–1.3`, `top_p=0.95` | Expand candidate diversity |
| Safe sentence completion | `temp=0.7`, `top_k=10` | Suppress excessive randomness |

At the generation stage, the goal is not finding "correct parameters" but managing failure cost per purpose. Production favors conservative settings; experiments favor wider ones.

## Operational Log Template for Generation Quality

As sampling experiments multiply, impressionistic evaluation ("looks good") makes decisions hard. Log at least the following to enable reproducible comparison when only the policy changes:

```text
run_id=infer-2026-05-21-01
checkpoint=ckpt.pt
prompt=ROMEO:
max_new_tokens=180
temperature=0.8
top_k=20
top_p=0.9
distinct_2=0.81
distinct_3=0.93
avg_token_logprob=-1.74
repetition_warning=false
```

`avg_token_logprob` and `distinct_n` together let you separate overly safe outputs from overly random ones. One metric alone distorts interpretation; two or three viewed together is more stable.

### Debug mode: per-token probability output

```python
def sample_one_step(logits: torch.Tensor, debug: bool = False):
    probs = F.softmax(logits, dim=-1)
    idx_next = torch.multinomial(probs, num_samples=1)
    if debug:
        topv, topi = torch.topk(probs, k=5, dim=-1)
        print("top5 ids:", topi[0].tolist())
        print("top5 probs:", [round(float(v), 4) for v in topv[0]])
    return idx_next
```

Useful for diagnosing why specific tokens repeat. If the top-1 probability stays above 0.7 consistently, raising temperature (not lowering it) often produces more natural output.

### Sliding window and the long-context illusion

A char-level model forgets content beyond `block_size` even if the generated text looks long. Printing the effective context length prevents misinterpretation:

```python
idx_cond = idx[:, -self.config.block_size :]
print("effective_context_len", idx_cond.size(1))
```

If this value is always pinned at `block_size`, the model is already blind to early content. This is why history summarization strategies become necessary at the chatbot stage.

## Sampling Policy Operations Guide

Even with the same checkpoint, changing the sampling policy completely alters output perception. So at inference time, "decoding policy version" must be managed as carefully as "model version."

### Principles for combining temperature, top-k, top-p

Temperature softens the entire distribution; top-k cuts candidates by absolute count; top-p cuts by cumulative probability mass. In practice, defining a few reference presets and comparing them is more stable than moving all three at once.

For QA-style text, low temperature and small top-k improve consistency. For creative text, medium temperature and top-p increase diversity. The key is not a "correct setting" but separating policies by purpose.

### Repetition prevention

Small models easily repeat the same phrases. Reducing this requires combining repetition penalty, n-gram blocking, max-length limits, and EOS-priority stopping. Shorter prompts increase repetition risk, so enforcing minimum context length at the service level is practical.

### Inference performance observation

In production, quality issues and latency issues appear together. Collect at minimum:

- Average generation time per token
- Time to first token
- Average generated tokens per request
- Early termination rate (EOS, length limit, user abort)

## Product-Level Generation Policy Presets

Real services don't apply the same sampling settings to all users. Purpose-based presets make quality discussions far clearer:

- Stable response: low temperature, small top-k
- Balanced: medium temperature, medium top-p
- Creative: high temperature, wide top-p

Naming presets transforms "the model is weird" feedback into "which symptom appears under which policy," accelerating improvement.

## Operational Tips

When changing generation policy, experiment with the highest user-impact parameter first. Typically temperature adjustment creates the most immediate change; top-k/top-p are finer follow-up tuning.

## Practice FAQ

### Should I follow these steps rigorously even for a tiny model?

Yes—smaller models benefit more from strict contracts. Low capacity magnifies input noise and implementation inconsistency. Establishing reproducible experiment units first accelerates quality improvements even before scaling model size.

### What if experiment speed and quality management conflict?

To go faster, reduce failure cost rather than increasing experiment count. Locking config files, standardizing logs, and storing checkpoint metadata let you run more *valid* experiments in the same time.

### What single thing is most worth recording?

The change rationale, expected effect, and observed result—briefly. Especially "why this value was chosen" lets you reconstruct decision context weeks later.

## Summary

This article implemented the autoregressive sampling loop that turns a trained GPT into an actual text generator. The core: read last-position logits, sample one token from that distribution, and append it back as input—repeated.

We also explored why temperature, top-k, top-p, and sliding context windows are necessary. If model weights are the foundation of generation, the sampling strategy is the policy that decides what character the output takes.

Next, we overlay instruction-response formatting on top of this base model via fine-tuning—shifting from a Shakespeare character predictor toward question-answer output habits.

## Answering the Opening Questions

- **What exactly does the generation loop repeat?**
  - Generation crops the current context with `idx_cond = idx[:, -self.config.block_size :]`, extracts the last-position logits, samples one new token, and appends it via `torch.cat((idx, idx_next), dim=1)`. It's not writing the entire sentence at once—it's an autoregressive loop that attaches one piece at a time from the next-token distribution.
- **Why does greedy decoding often produce boring, repetitive output?**
  - Greedy picks only the highest-probability token (`argmax`) at every step, so even slightly conservative models reinforce the same patterns. With a `ROMEO:` prompt, safe character sequences emerge fine but diversity vanishes and repetition grows.
- **How does temperature reshape the logits distribution?**
  - Dividing by temperature in `logits = logits[:, -1, :] / max(temperature, 1e-5)` before softmax makes large logits more dominant at `T < 1` and flattens the distribution at `T > 1`. Temperature is a knob that adjusts output conservatism/randomness without touching model weights.

<!-- toc:begin -->
## In this series

- [LLM from Scratch 101 (1/9): Turning Text into Numbers](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): From Integers to Vectors and Positions](./02-embedding.md)
- [LLM from Scratch 101 (3/9): Deciding Which Tokens to Focus On](./03-attention.md)
- [LLM from Scratch 101 (4/9): The Transformer Block: A Unit of Depth](./04-transformer-block.md)
- [LLM from Scratch 101 (5/9): Assembly: Completing the GPT Model Class](./05-gpt-model.md)
- [LLM from Scratch 101 (6/9): Learning via Gradients](./06-training-loop.md)
- **LLM from Scratch 101 (7/9): Sampling — Generating Text from a Trained Model (current)**
- LLM from Scratch 101 (8/9): Adapting the Base Model to Specific Tasks (upcoming)
- LLM from Scratch 101 (9/9): Turning Your LLM into a Chatbot — FastAPI + Streaming (upcoming)

<!-- toc:end -->

## References

- [The Curious Case of Neural Text Degeneration (arXiv:1904.09751)](https://arxiv.org/abs/1904.09751)
- [Hierarchical Neural Story Generation (arXiv:1805.04833)](https://arxiv.org/abs/1805.04833)
- [nanoGPT model.py generate (GitHub)](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [How to generate text: using different decoding methods for language generation with Transformers (Hugging Face)](https://huggingface.co/blog/how-to-generate)

Tags: LLM, PyTorch, Transformer, Tutorial
