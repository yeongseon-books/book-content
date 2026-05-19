---
title: Model Serving
series: llm-finetuning-101
episode: 6
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Fine-tuning
- Serving
- FastAPI
- Inference
- Adapter
- Python
last_reviewed: '2026-05-01'
seo_description: Wrap your fine-tuned LLM in a FastAPI service by breaking the system into API and model layers for efficient inference and serving.
---

# Model Serving

Serving forces a different set of trade-offs than training. This article breaks the system into four layers so you can see where the API boundary ends, where inference begins, and why adapters change deployment options.

This is the final post in the LLM Fine-tuning 101 series.

## Questions this post answers

![Questions this post answers](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/06/06-01-questions-this-post-answers.en.png)

*Questions this post answers*

- What is the minimum structure for wrapping a fine-tuned small model behind a FastAPI endpoint?
- In serving code, where do you draw the line between training and inference?
- How can you validate the endpoint without opening a browser?
- What do you gain by deploying the LoRA adapter separately from the base model?

> Serving is not the step that makes the model smarter. It is the step that places an already-prepared model behind a predictable HTTP contract.

Example code: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/en/06-serving)

## Why this matters

The final article in the series puts the trained adapter behind an API. In production, training and serving are kept separate as a rule. For a demo, however, doing one small fine-tuning step and immediately wrapping the result in an endpoint helps you see the whole flow at once.

There is a clear reason to make serving its own stage. Training thinks in batches and epochs, but serving must think in **per-request latency and concurrency**. The same model under these two viewpoints needs different code structure, memory policy, and error handling. Episode 6 practices that switch in the smallest possible unit.

## Mental Model

A serving system decomposes into four layers.

```text
[client] -> HTTP -> [API layer] -> [model layer] -> [weights store]
                       |              |              |
                    FastAPI      tokenizer +     base model
                    Pydantic     model.generate  + adapter
```

- **API layer**: request/response serialization, validation, error handling, auth, observability
- **Model layer**: tokenizer, generation options, post-processing
- **Weights store**: base model (large file) + LoRA adapter (small file)

The key benefit of LoRA shows up in the weights store. Keep one base model in memory and swap adapters to serve multiple models from a single machine.

Two more facts to memorize:

- **Single-request latency** = tokenize + generate + decode. Generate accounts for over 90%.
- **Batching** raises throughput but also raises latency. The two are a trade-off.

## Core concepts

| Item | Meaning |
| --- | --- |
| `FastAPI` | A fast async Python web framework. Auto-validation via Pydantic |
| `TestClient` | A test tool that calls the app in memory without uvicorn |
| `/health` | A lightweight endpoint asking whether the service is alive. Used by load balancers |
| `/generate` | The endpoint that performs actual inference |
| `model.generate()` | A method that produces tokens autoregressively, one at a time |
| `max_new_tokens` | Upper bound on generation length. Essential to prevent infinite loops |
| Adapter merge | Optional: merge the LoRA adapter into the base to produce a single set of weights |
| Cold start | Time to load the model. Affects only the first request |

## Before vs. After

**Before** — Results are visible only on the laptop where you trained the model. Sharing with a colleague requires sending code every time.

**After** — Adopt the pattern in episode 6 and a colleague can call your model with one line:

```bash
curl -X POST http://localhost:8000/generate -d '{"prompt":"Python function example"}'
{"completion":"Python function example: def add(a, b): return a + b"}
```

What matters is (1) the model is behind an HTTP contract, (2) `TestClient` validates it in CI, and (3) swapping the adapter switches to a different model on the same infrastructure.

## What this demo isolates on purpose

![Separation of model preparation and HTTP contract](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/06/06-02-what-this-demo-isolates-on-purpose.en.png)

*Separation of model preparation and HTTP contract*

In production, model loading, request validation, generation options, response serialization, and observability logs are all separate responsibilities. This article's example shows only **model preparation** and the **HTTP contract** at minimum scale. Even in a small demo, separating health check and generate endpoints makes it easy to grow into production code.

![What this demo isolates on purpose](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/06/06-01-what-this-demo-isolates-on-purpose.en.png)

*What this demo isolates on purpose*

## Step-by-step practice

### Step 1 — FastAPI app skeleton

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
```

### Step 2 — Load the model (once at startup)

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

base = AutoModelForCausalLM.from_pretrained("sshleifer/tiny-gpt2")
model = PeftModel.from_pretrained(base, "artifacts/lora-adapter")
tokenizer = AutoTokenizer.from_pretrained("sshleifer/tiny-gpt2")
model.eval()
```

Forgetting `model.eval()` leaves dropout active and the same input produces different outputs. Never skip it in serving.

### Step 3 — `/generate` endpoint

```python
from pydantic import BaseModel

class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 32

@app.post("/generate")
def generate(req: GenerateRequest) -> dict:
    ids = tokenizer(req.prompt, return_tensors="pt").input_ids
    out = model.generate(ids, max_new_tokens=req.max_new_tokens)
    text = tokenizer.decode(out[0], skip_special_tokens=True)
    return {"completion": text}
```

Validating the request with a Pydantic model prevents bad payloads from reaching the model layer.

### Step 4 — Self-validate with `TestClient`

```python
from fastapi.testclient import TestClient

client = TestClient(app)
assert client.get("/health").json() == {"status": "ok"}
print(client.post("/generate", json={"prompt": "Python function example"}).json())
```

`TestClient` calls the app in memory without spawning uvicorn. It drops straight into CI.

### Step 5 — Run the real server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

You can now call from another machine with `curl` or test in Postman.

## What to notice in this code

![FastAPI inference request and endpoint branching flow](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/06/06-03-what-to-notice-in-this-code.en.png)

*FastAPI inference request and endpoint branching flow*

- Model loading runs only once at app startup. Loading per request increases latency by tens of times.
- Separating `/health` and `/generate` makes it easy to distinguish model state from inference failure causes.
- `TestClient` validates the endpoint contract without uvicorn, which is CI-friendly.
- Pydantic validation is the lightest possible defense against garbage-in.

## Common mistakes

![Latency vs. quality decision criteria for serving](https://yeongseon-books.github.io/book-public-assets/assets/llm-finetuning-101/06/06-04-where-engineers-get-confused.en.png)

*Latency vs. quality decision criteria for serving*

- **Loading the model per request** — every cold start adds seconds of latency. Load once at app startup.
- **Not specifying `max_new_tokens`** — relying on the default produces unintentionally long responses and latency spikes.
- **Forgetting `model.eval()`** — active dropout produces nondeterministic output. Hard to debug.
- **Exposing raw errors** — leaking stack traces to the client is a security risk. Wrap in `HTTPException`.
- **No timeout** — a 30-second request ties up an entire worker. Set timeouts on both client and server.
- **No GPU memory monitoring** — silent OOMs kill workers while the health check still passes. Expose `torch.cuda.memory_allocated()` as a metric.

## Production application

- **Separate training and serving code**: even within one repository, isolate the directories. Serving code should not import training dependencies (`datasets`, `wandb`).
- **Adapter multi-tenancy**: one base model + N adapters serve multiple models from a single machine. `PeftModel.set_adapter()` allows runtime switching.
- **Batching**: serving engines like vLLM or TGI provide automatic dynamic batching. With raw FastAPI, implement micro-batching with `asyncio.Queue`.
- **Streaming responses**: long outputs feel much faster when sent token-by-token via `StreamingResponse`.
- **Observability**: log per-request prompt token count, completion token count, total latency, and GPU memory. Prometheus + Grafana is the common combination.
- **Canary deployment**: send 1% of traffic to a new adapter first. Increase gradually as perplexity and latency stabilize.

## Checklist

- [ ] I can distinguish model preparation responsibility from HTTP endpoint responsibility.
- [ ] I validated `/health` and `/generate` with `TestClient`.
- [ ] I understand the difference between a tiny model demo and real production serving.
- [ ] I can explain what improves when LoRA adapters are deployed separately from the base.
- [ ] I can connect the flow from episode 1 through episode 6 in one continuous arc.

## Exercises

1. Add `temperature` and `top_p` parameters to `/generate` and observe how the same prompt produces different outputs.
2. Measure single-request latency with `time.perf_counter()` and compare how it changes as `max_new_tokens` varies between 8 / 32 / 128.
3. Prepare two adapters and write code to switch them at runtime via a `?adapter=A` query parameter on `/generate`.

## Summary · Series wrap-up

The minimum end-to-end path of the fine-tuning series is now complete. You built intuition with formulas (ep 1), prepared data (ep 2), attached LoRA (ep 3), trained one step (ep 4), evaluated (ep 5), and finally wired up an HTTP endpoint (ep 6).

The next step is leaving the series and repeating this same flow on your own domain data. 100-1000 examples, LoRA rank 8-16, 1 epoch, perplexity + golden-set evaluation, FastAPI serving — once this one-line recipe is in your hands, you can ship any small model into a service.

<!-- toc:begin -->
## In this series

- [LLM Fine-tuning Primer](./01-intro.md)
- [Dataset Preparation and Preprocessing](./02-dataset.md)
- [Configuring LoRA Adapters](./03-lora.md)
- [Training Loop and Hyperparameters](./04-training.md)
- [Model Evaluation](./05-evaluation.md)
- **Model Serving (current)**

<!-- toc:end -->

---

## References

- [Example repository — llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101)
- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Starlette TestClient reference](https://www.starlette.io/testclient/)
- [PEFT — Multiple adapters](https://huggingface.co/docs/peft/main/en/developer_guides/lora#multiple-adapters)
- [vLLM — high-throughput LLM serving](https://github.com/vllm-project/vllm)

Tags: Fine-tuning, LoRA, LLM, Python
