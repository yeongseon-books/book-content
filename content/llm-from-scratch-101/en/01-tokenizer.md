---
title: "LLM from Scratch 101 (1/9): Turning Text into Numbers"
series: llm-from-scratch-101
episode: 1
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
seo_description: The most jarring thing I noticed when first digging into LLM internals
  was that the model can't read at all.
---

# LLM from Scratch 101 (1/9): Turning Text into Numbers

> LLM from Scratch 101 series (1/9)

The most jarring thing I noticed when first digging into LLM internals was that the model can't read at all. When we type "Hello" into a prompt, it looks like the machine understands our words, but inside the model, it's just an array of numbers. What looks like a greeting to us is simply a sequence of integers like `[31495, ...]` to the neural network.

I've found that accepting this reality early on makes everything else much easier. If you skim over the tokenizer, concepts like embeddings, attention, and loss functions will feel like they're floating in mid-air. Once you realize it's just a matter of reliably slicing strings into integer sequences, the "magic" of LLMs starts to fade away.

In this series, we're building a small GPT model from scratch using TinyShakespeare. We'll set aside the heavy frameworks for a moment and go all the way with just PyTorch 2.x and a few Python files.

Today's mental model is simple: **The model doesn't read text. It reads integer sequences created by the tokenizer.**

This is the first post in the LLM from Scratch 101 series.

---

![LLM from Scratch 101 chapter 1 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/01/01-01-word-level-vs-subword-the-trade-off.en.png)
*LLM from Scratch 101 chapter 1 flow overview*

## Questions to Keep in Mind

- Why do models take integers instead of raw text?
- What are the trade-offs between character, word, and subword tokenization?
- How does BPE actually build a vocabulary step by step?

## Why Can't We Just Input Text?

Neural networks process tensors. You can't perform addition or matrix multiplication on a string. To process a line like "To be, or not to be," we first have to convert it into numbers. These numbers are called Token IDs.

There's one crucial point to keep in mind: Token IDs don't carry inherent meaning. They're just indices. There's no guarantee that token 5 is semantically close to token 6, and they aren't alphabetically ordered in a meaningful way. We just map them to integers for now, and later, during the embedding stage, we'll assign vector meanings to those integers.

Beginners often overlook this: if you change the tokenizer, the same sentence becomes a completely different sequence of IDs. This breaks compatibility with previously trained embeddings and checkpoints. While tokenization might look like a pre-processing step outside the model, it's more accurate to think of it as a part of the model itself.

## The Simplest Approach: Character-Level Tokenization

The easiest starting point is character-level tokenization. You build a vocabulary from the set of characters present in your text and assign a number to each. No complex exceptions, and debugging is straightforward.

```python
text = "hello world"
chars = sorted(set(text))
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}

def encode(s: str) -> list[int]:
    dropped = sorted({c for c in s if c not in stoi})
    if dropped:
        print(f"dropped unsupported characters: {dropped}")
    return [stoi[c] for c in s if c in stoi]

decode = lambda ids: "".join(itos[i] for i in ids)

ids = encode(text)
print(ids)
print(decode(ids))
```

Running this code gives you an immediate sense of how text moves back and forth between characters and numbers. One caveat is that a char-level tokenizer can only encode characters already present in its vocabulary, so unsupported input is dropped with a warning.

## Word-Level vs. Subword: The Trade-off

Character-level tokenization isn't always the answer. Word-level tokenization results in shorter sequences but causes the vocabulary size to explode and struggles with out-of-vocabulary (OOV) words. Subword tokenization aims for the middle ground.

This is why most production models use BPE (Byte Pair Encoding) variants. It provides a good balance between vocabulary size and representational power.

## Doing BPE by Hand — No Magic Involved

BPE might sound intimidating, but the idea is actually quite humble. You repeatedly merge the most frequent pairs of characters or character sequences. If you have words like `low`, `lower`, and `lowest`, you might merge `l + o`, then `lo + w`, gradually building longer pieces. Frequent patterns are essentially "promoted" to the vocabulary.

GPT-2 used a subword vocabulary of 50,257 tokens. It's not a black box; it's just a dictionary of text fragments optimized using statistics.

I usually describe BPE as something between compression and dictionary editing. Frequent patterns are reduced to a single short ID, while rare patterns are left as smaller pieces. Common words get shorter sequences, and the model never completely gives up on words it hasn't seen before.

## Trying GPT-2 Tokenizer with tiktoken

Theory is one thing, but seeing it in action is better. You can experiment with actual GPT-2 style tokenization using the following code:

```python
import tiktoken

enc = tiktoken.get_encoding("gpt2")
text = "Hello, tokenizer!"

ids = enc.encode(text)
decoded = enc.decode(ids)

print(ids)
print(decoded)
```

Just `pip install tiktoken` and you're good to go. You'll notice the ID array looks completely different from the character-level version for the same sentence.

## Why We're Using Character-Level Tokenization

For this series, we're sticking with character-level tokenization. There are three reasons: the code is shorter, training is faster on small datasets like TinyShakespeare, and debugging is more intuitive. Since we only have about 65 characters, the final softmax layer is also lightweight.

While this isn't enough for a production-scale model, it's perfect for a 101 series focused on core principles. In these first three posts, transparency is more important than performance.

## Data Prep: Downloading and Encoding TinyShakespeare

Now we'll create the first code file of the series, `data.py`. This script downloads TinyShakespeare, builds a character vocabulary, and saves the training and validation sets as binary files.

```python
from pathlib import Path
from urllib.request import urlretrieve

import numpy as np

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

input_file = DATA_DIR / "tinyshakespeare.txt"
if not input_file.exists():
    urlretrieve(
        "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt",
        input_file,
    )

text = input_file.read_text(encoding="utf-8")
chars = sorted(set(text))
vocab_size = len(chars)

stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}

def encode(s: str) -> list[int]:
    dropped = sorted({c for c in s if c not in stoi})
    if dropped:
        print(f"dropped unsupported characters: {dropped}")
    return [stoi[c] for c in s if c in stoi]

def decode(ids: list[int]) -> str:
    return "".join(itos[i] for i in ids)

data = np.array(encode(text), dtype=np.uint16)
n = int(0.9 * len(data))
train_ids = data[:n]
val_ids = data[n:]

(DATA_DIR / "train.bin").write_bytes(train_ids.tobytes())
(DATA_DIR / "val.bin").write_bytes(val_ids.tobytes())

print(f"vocab_size={vocab_size}, train={len(train_ids)}, val={len(val_ids)}")
print(decode(train_ids[:80].tolist()))
```

Once you run this script, you'll be able to pull batches from the integer sequences for the next posts. I always keep the `decode()` function handy because debugging a model often involves turning numbers back into human-readable text.

## What's next

We have our integer sequences ready. In the next post, we'll assign vector meanings to these cold ID arrays. By combining token embeddings and positional embeddings, we'll create the first input tensor the model will actually read.

<!-- a-grade-example:begin -->

## Checklist

- [ ] Encoded TinyShakespeare into an integer sequence.
- [ ] Inspected vocabulary size against token count.
- [ ] Compared the same sentence under tiktoken's BPE.
- [ ] Can state the trade-off of character-level in one sentence.

<!-- a-grade-example:end -->

## Common misconceptions

- It is tempting to think token IDs carry meaning, but actual meaning is learned later in the embedding vectors.
- Tokenizers are often seen as mere preprocessing outside the model, but because they govern checkpoint compatibility, they are effectively part of the model.
- Character-level may seem outdated because it is simple, but it is extremely powerful for education and debugging.
- BPE feels like complex magic, but it is closer to a statistical procedure that repeatedly merges frequently co-occurring fragments.
- Ignoring out-of-vocab character handling seems harmless, but in production it leads directly to input loss and quality degradation.

## Operations checklist

- [ ] I can explain which tokenizer contract the current model was trained under.
- [ ] I have documented the out-of-vocab handling policy (drop, unknown, byte fallback, etc.).
- [ ] I have encoded the same sentence with char-level and BPE and compared the length difference.
- [ ] I maintain both `encode()` and `decode()` so numeric-to-character round-trip is verifiable.
- [ ] I have fixed the training dataset into reproducible artifacts like `train.bin` and `val.bin`.

## Tokenizer pinning for experiment reproducibility

One of the top reasons why the same code produces different results in LLM experiments is tokenizer mismatch. At a minimum, you should version the vocab file, special token definitions, and preprocessing rules together with each checkpoint.

Pinning the tokenizer makes training curve comparisons honest. You can separate "the effect of changing model architecture" from "the effect of changing input decomposition."

## What changes when you keep a tokenizer training script

Even when using char-level as the default for education, in real projects it is safer to leave "how the vocabulary was built" as code. The most common choice is a BPE training script. The key is not a complex library but **fixing the reproducibility path so the same input always produces the same vocab/merge files**.

```python
from pathlib import Path

from tokenizers import Tokenizer, models, normalizers, pre_tokenizers, trainers

def train_bpe_tokenizer(corpus_path: str, out_dir: str, vocab_size: int = 8000) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    tokenizer = Tokenizer(models.BPE(unk_token="<unk>"))
    tokenizer.normalizer = normalizers.Sequence([
        normalizers.NFKC(),
        normalizers.StripAccents(),
    ])
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)

    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=2,
        special_tokens=["<pad>", "<unk>", "<bos>", "<eos>"],
    )
    tokenizer.train([corpus_path], trainer)

    tokenizer.model.save(str(out), "tokenizer")
    tokenizer.save(str(out / "tokenizer.json"))

train_bpe_tokenizer("data/tinyshakespeare.txt", "artifacts/tokenizer", vocab_size=2000)
```

This code is not an example for improving training performance — it is an example for ensuring tokenizer changes do not contaminate experiment results. In particular, changing `special_tokens` order shifts ID mappings, and from that moment the existing checkpoint becomes incompatible. So tokenizer artifacts should be treated as part of the same release unit as `ckpt.pt`.

Recording "tokenizer metadata" alongside makes later regression analysis easier:

```json
{
  "tokenizer_type": "char",
  "vocab_size": 65,
  "normalization": "none",
  "special_tokens": [],
  "train_corpus_sha256": "8d1f...",
  "created_at": "2026-05-21T11:10:00Z"
}
```

With this metadata, when you encounter "the model suddenly went wrong," you can check input contract changes before investigating model architecture. This is one of the habits that most dramatically reduces debugging time in practice.

### Token length distribution reveals training bottlenecks early

Tokenizer choice ultimately changes the sequence length distribution. Longer sequences increase attention computation as `T^2`, forcing smaller batch sizes on the same GPU memory. Printing length distribution at the tokenizer stage lets you set training parameters more rationally later.

```python
import numpy as np

samples = [
    "To be, or not to be, that is the question.",
    "What light through yonder window breaks?",
    "O Romeo, Romeo! wherefore art thou Romeo?",
]

lengths = [len(encode(s)) for s in samples]
print("lengths:", lengths)
print("mean:", float(np.mean(lengths)))
print("p95:", float(np.percentile(lengths, 95)))
```

With char-level, average lengths are longer but debugging visibility is higher. Conversely, subword shortens lengths for training efficiency but makes encoding results harder for humans to read intuitively. You must verify this trade-off numerically to explain "why this tokenizer" end-to-end.

| Choice | Advantage | Cost |
| --- | --- | --- |
| char-level | simple implementation/debugging, full visibility | long sequences, slower training |
| BPE/subword | short sequences, practical efficiency | complex training pipeline, reduced visibility |
| byte-level | OOV robustness | post-processing/readability burden |

This is why the series fixes char-level early on. Securing the experience of visually tracking input contracts before pursuing absolute performance ensures your judgment stays stable when reading attention patterns and loss curves later.

## Operational checkpoints when changing tokenizers

A tokenizer change looks like a single-file code change, but in reality it simultaneously changes the interpretation rules for training data and model weights. Even small changes should be treated like a schema migration from an operational perspective. Checking the following four points in advance significantly reduces training restarts and inference mismatches.

### Vocabulary size and special token policy

`<pad>`, `<bos>`, `<eos>`, `<unk>` — their presence and ID assignment propagate throughout the model. Changing special token order mid-training makes checkpoint reuse difficult and immediately alters decoding results. Fix a special token table per tokenizer version as a permanent document.

### Normalization rules and invertibility

Lowercasing, whitespace cleanup, and Unicode normalization can create data loss. For example, excessive normalization on a Korean+English mixed corpus can break domain terminology. Before training, always create `encode -> decode` round-trip samples to verify that meaning loss is within acceptable bounds.

### Tokenizer synchronization across training/inference paths

If the training script and serving inference code reference different tokenizer files, the model interprets "inputs seen during training" and "real service inputs" differently. This problem manifests only as accuracy degradation, so discovery comes late. Storing the tokenizer file hash in checkpoint metadata catches this mismatch early.

### Data distribution and token length monitoring

After a tokenizer change, average token length and upper percentile lengths can shift significantly. Longer lengths reduce information capacity within the same context window and increase training cost. Conversely, excessively short lengths can fragment meaning units, making pattern learning harder for the model.

## Quick validation with small experiments

A tokenizer change can reduce failure probability with a small validation before rerunning full training. For example, fixing 100 sample sentences and comparing `token count`, `rare token ratio`, and `round-trip restoration rate` quickly characterizes the nature of the change. Automating this check at the PR stage makes it easy to block model quality degradation proactively.

## One-line conclusion

A tokenizer is not a preprocessing tool but the model's character system. The moment you pin it and version-control it, experiment quality in all subsequent stages stabilizes.

## Frequently asked questions in practice

### Should I follow this discipline even for small models?

Yes — in fact, smaller models require stricter adherence to basic contracts. The smaller the model capacity, the more it is affected by input noise and implementation mismatches. Securing reproducible experiment units first improves quality improvement velocity even before scaling model size.

### What do I do when experiment speed and quality control conflict?

To increase speed, the goal is not more experiments but lower failure cost. Introducing config file pinning, log standardization, and checkpoint metadata storage first lets you run more "valid" experiments in the same time.

### What's the single most useful thing to record?

Record the reason for the change, expected effect, and actual observed result briefly. Especially recording "why this value was chosen" lets you reconstruct decision context even weeks later.

Even short validations, when automated, significantly reduce tokenizer change risk.

## Summary

This article established the most important starting point: models do not read text directly but receive integer sequences produced by the tokenizer as input. This single perspective makes LLM internals feel far less mysterious.

We also examined what character-level, word-level, and subword tokenization trade off against each other. Char-level is long but transparent; subword is efficient but structurally more complex. The series chose char-level precisely for this transparency.

Moving to the next article, these integer IDs will receive vector meanings. That is, the number sequences produced by the tokenizer will pass through embeddings and enter the representation space the model can actually operate on.

## Answering the Opening Questions

- **Why must the model receive integer sequences instead of raw strings?**
  - Neural networks operate as matrix-multiplication and tensor engines, so they cannot compute on strings directly—they need the integer array produced by `encode()` first. This article's `stoi`, `itos`, `train.bin`, and `val.bin` are exactly the result of converting human-readable text into a numeric contract the model can consume.
- **What does each tokenization granularity—character, word, subword—gain and lose?**
  - Character-level has a tiny vocab and easy `decode()` tracing but long sequences; word-level is short but suffers OOV and vocabulary explosion. Subword compromises between length and vocab size. This series chose char-level for transparency over performance.
- **How does BPE actually grow its vocabulary incrementally?**
  - BPE starts with character fragments then repeatedly merges frequently co-occurring pairs—`l + o`, `lo + w`—promoting them to new tokens. So a production tokenizer like `tiktoken.get_encoding("gpt2")` represents common patterns as shorter ID sequences.

<!-- toc:begin -->
## In this series

- **LLM from Scratch 101 (1/9): Turning Text into Numbers (current)**
- LLM from Scratch 101 (2/9): From Integers to Vectors and Positions (upcoming)
- LLM from Scratch 101 (3/9): Deciding Which Tokens to Focus On (upcoming)
- LLM from Scratch 101 (4/9): The Transformer Block: A Unit of Depth (upcoming)
- LLM from Scratch 101 (5/9): Assembly: Completing the GPT Model Class (upcoming)
- LLM from Scratch 101 (6/9): Learning via Gradients (upcoming)
- LLM from Scratch 101 (7/9): Sampling — Generating Text from a Trained Model (upcoming)
- LLM from Scratch 101 (8/9): Adapting the Base Model to Specific Tasks (upcoming)
- LLM from Scratch 101 (9/9): Turning Your LLM into a Chatbot — FastAPI + Streaming (upcoming)

<!-- toc:end -->

## References

- [Karpathy minBPE](https://github.com/karpathy/minbpe)
- [OpenAI tiktoken](https://github.com/openai/tiktoken)
- [Language Models are Unsupervised Multitask Learners (GPT-2)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
- [Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909)

Tags: LLM, PyTorch, Transformer, Tutorial
