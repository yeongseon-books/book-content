# Oracle Content Review — llm-from-scratch-101

- **Session**: `ses_228f9531cffe0rMtKHc3W4yEhI`
- **Date**: 2026-04-29
- **Verdict**: **NOT SHIPPABLE** until P0 math/code fixes land
- **Effort**: Medium (1-2d)

## Per-article scores

| File | Score | Summary |
|---|---:|---|
| `en/01-tokenizer.md` | 4/5 | Clear; dataset source unpinned |
| `ko/01-tokenizer.md` | 4/5 | Natural Korean voice |
| `en/02-embedding.md` | 4/5 | Embedding + positional sum correct |
| `ko/02-embedding.md` | 4/5 | Solid |
| `en/03-attention.md` | 3/5 | **Math right, return contract sets up downstream crash** |
| `ko/03-attention.md` | 3/5 | Same |
| `en/04-transformer-block.md` | **2/5** | Pre-LN concept right, **block code not runnable** |
| `ko/04-transformer-block.md` | **2/5** | Same bug |
| `en/05-gpt-model.md` | **2/5** | Inherited block bug makes "ready for training" false |
| `ko/05-gpt-model.md` | **2/5** | Strong narrative, broken assembled code |
| `en/06-training-loop.md` | 4/5 | Mostly correct; thin reproducibility |
| `ko/06-training-loop.md` | 4/5 | Same |
| `en/07-inference.md` | 4/5 | Sampling sound |
| `ko/07-inference.md` | 4/5 | Same |
| `en/08-finetuning.md` | **1/5** | **Trains wrong target** |
| `ko/08-finetuning.md` | **1/5** | Same + **Hangul untokenizable** |
| `en/09-chatbot-wrapper.md` | **2/5** | OOV/streaming/history broken |
| `ko/09-chatbot-wrapper.md` | **1/5** | Korean chat impossible with English vocab |

## CRITICAL math/code correctness issues

### 1. Attention return contract breaks Transformer block (P0)
- `en|ko/03-attention.md:136-149` returns `out, wei`
- `en|ko/04-transformer-block.md:86-88` does `x = x + self.attn(self.ln1(x))`
- **Bug**: tensor + tuple → crash
- **Fix**: either `attn_out, _ = self.attn(self.ln1(x)); x = x + attn_out`, or make `CausalSelfAttention.forward()` return only `out`

### 2. Fine-tuning uses unshifted labels (P0)
- `en/08-finetuning.md:75-80,93-94`, `ko/08:77-82,95-96`
- **Bug**: `x` and `y` are same sequence with prompt masked. Removes 1-token shift used in causal LM training. **Optimizes token copying, not next-token prediction.**
- **Fix**: `ids = encode(full); x = ids[:-1]; y = ids[1:]`; apply mask on shifted `y`

### 3. Korean fine-tuning data cannot run with published tokenizer (P0)
- `ko/08-finetuning.md:47-52,80`
- **Bug**: dataset has Hangul; tokenizer built from TinyShakespeare English chars. `encode()` is raw `dict[c]` lookup → `KeyError` on Hangul.
- **Fix**: keep finetuning data in English charset OR rebuild tokenizer/vocab on mixed corpus

### 4. Chatbot input not robust to OOV; Korean examples impossible (P0)
- `en|ko/01-tokenizer.md:129-130` raw `stoi[c]` lookup
- `en|ko/09-chatbot-wrapper.md:108-123` passes arbitrary user text
- `ko/09:43-48` demonstrates Korean turns
- **Fix**: validate/reject unsupported chars OR change framing to "English-only char-level demo" OR switch tokenizer

### 5. Streaming endpoint drops conversation history (P1)
- `en|ko/09-chatbot-wrapper.md:113-123`
- **Bug**: `/chat` uses `body.history`; `/chat/stream` calls `build_prompt([], prompt)` — multi-turn claim false for streaming
- **Fix**: same history payload for both, or label streaming as single-turn

## PyTorch API stale items

- `scaled_dot_product_attention` only referenced (`en|ko/03-attention.md:192`) — no "we hand-roll for pedagogy, use SDPA in real code" note
- `torch.compile` never discussed
- Device handling cuda/cpu only (`en|ko/06:105`); `mps` absent
- Inference uses `torch.no_grad()`; should mention `torch.inference_mode()`
- No seed setting anywhere → not reproducible

## Top 5 quality issues (non-correctness)

1. Code continuity weaker than narrative (naming drift `token_embedding_table` vs `token_emb`, no canonical `model.py` snapshot)
2. Reproducibility underpowered (unpinned TinyShakespeare URL, hardcoded `vocab_size=65`, no seed)
3. ~720 LOC claim not well supported (assembled is in low hundreds)
4. Ep8 overclaims SFT on 50 rows demonstrates instruction following
5. English prose readable but templated ("When I first…", "Today's mental model…")

## Verdict: not-shippable

## Action list

1. **P0** Fix attention/block contract in ep3-ep5 (ko+en)
2. **P0** Rewrite ep8 SFT with shifted labels; regenerate before/after outputs
3. **P0** Remove Korean finetuning/chat inputs OR rebuild tokenizer
4. **P0** Add explicit OOV handling in ep9
5. **P1** Match streaming and non-streaming chat semantics
6. **P1** Add "PyTorch 2.x note" box (SDPA, `torch.compile`, `inference_mode`, `mps`)
7. **P1** Add reproducibility metadata (pin TinyShakespeare, seed block, derive `vocab_size` from tokenizer metadata)
8. **P1** Publish one canonical assembled code snapshot per phase
9. **P2** Rephrase or drop LOC claim
10. **P2** Tighten ep8 framing to "format steering demo"
11. **P2** Tone down production-adjacent framing in ep9
12. **P2** De-template English intros
