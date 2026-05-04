---
title: Sampling — Generating Text from a Trained Model
series: llm-from-scratch-101
episode: 7
language: en
status: publish-ready
targets:
  tistory: true
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

# Sampling — Generating Text from a Trained Model

> LLM from Scratch 101 series (7/9)

Once you've saved `ckpt.pt`, the immediate urge is to make the model talk. However, simply calling `model.eval()` won't magically produce sentences. You need a mechanism to extract text from the model's predictions.

The process is straightforward: pick a character, append it to the sequence, and feed it back into the model. Repeating this loop generates text. While the result might resemble Shakespearian nonsense at this stage, it demonstrates the fundamental mechanics of text generation.

Today's mental model is simple. **Generation is an autoregressive loop where you pick one token from the next-token distribution and feed that result back as input.**

---

<!-- a-grade-intro:begin -->

## Key Questions

- What does the autoregressive generation loop iterate over?
- How do temperature, top-k, and top-p each manipulate the logits?
- Why does greedy decoding produce monotonous text?
- How should the model handle text longer than its context window?

<!-- a-grade-intro:end -->

## Autoregressive Generation — One Token at a Time

We input the current context `idx`, extract only the last step's logits, and then append the sampled token to the sequence.

![Autoregressive loop with token-by-token appends](../../../assets/llm-from-scratch-101/07/07-01-autoregressive-generation-one-token-at-a.en.png)

*Autoregressive loop with token-by-token appends*
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

<!-- toc:begin -->
## In this series

- [Turning Text into Numbers](./01-tokenizer.md)
- [From Integers to Vectors and Positions](./02-embedding.md)
- [Deciding Which Tokens to Focus On](./03-attention.md)
- [The Transformer Block: A Unit of Depth](./04-transformer-block.md)
- [Assembly: Completing the GPT Model Class](./05-gpt-model.md)
- [Learning via Gradients](./06-training-loop.md)
- **Sampling — Generating Text from a Trained Model (current)**
- Adapting the Base Model to Specific Tasks (upcoming)
- Turning Your LLM into a Chatbot — FastAPI + Streaming (upcoming)

<!-- toc:end -->

## References

- [The Curious Case of Neural Text Degeneration (arXiv:1904.09751)](https://arxiv.org/abs/1904.09751)
- [Hierarchical Neural Story Generation (arXiv:1805.04833)](https://arxiv.org/abs/1805.04833)
- [nanoGPT model.py generate (GitHub)](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [How to generate text: using different decoding methods for language generation with Transformers (Hugging Face)](https://huggingface.co/blog/how-to-generate)

Tags: LLM, PyTorch, Transformer, Tutorial
