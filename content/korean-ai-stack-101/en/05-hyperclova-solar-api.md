---
title: 'Using HyperCLOVA X and Solar API'
series: korean-ai-stack-101
episode: 5
language: en
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- LLM
- Embeddings
- OCR
last_reviewed: '2026-05-01'
---

# Using HyperCLOVA X and Solar API

## Questions this post answers

- What API contract should you lock down before you start prompt tuning?
- What should you validate first when introducing Korean-first generation APIs such as HyperCLOVA X or Solar?
- Why does the runnable example use Groq llama-3.1-8b-instant as a stand-in?
- How should you separate Korean fluency from retrieval-grounded factual control?

> Switching generation providers is not just a model-name change. It also changes authentication, request shape, prompt contracts, and response validation.

> Korean AI Stack 101 (5/6)

Example code: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/en/05-hyperclova-solar-api)

The title points to HyperCLOVA X and Solar because they matter in the Korean model landscape, but the runnable example uses Groq's `llama-3.1-8b-instant`. The reason is practical: the repository example must run immediately in a reader's environment.

---

## Core flow

![Core flow](../../../assets/korean-ai-stack-101/05/05-01-core-flow.en.png)
---

## Why a provider-substitution exercise still helps

Readers do not always have HyperCLOVA X or Solar keys available. If the example cannot run, the prompt design lessons remain abstract. A stand-in provider still teaches the durable part of the workflow.

---

## Minimal runnable example

![Minimal runnable example](../../../assets/korean-ai-stack-101/05/05-01-minimal-runnable-example.en.png)
```python
import os
from groq import Groq

client = Groq(api_key=os.environ['GROQ_API_KEY'])
response = client.chat.completions.create(
    model='llama-3.1-8b-instant',
    temperature=0.3,
    max_completion_tokens=300,
    messages=[
        {'role': 'system', 'content': '당신은 한국어 제품 문서를 설명하는 시니어 개발자입니다.'},
        {'role': 'user', 'content': '벡터 검색과 키워드 검색의 차이를 한국어로 설명해 주세요.'},
    ],
)
print(response.choices[0].message.content)
```

---

## What to notice in this code

![What to notice in this code](../../../assets/korean-ai-stack-101/05/05-02-what-to-notice-in-this-code.en.png)
- The system message is already in Korean and already specific.
- A lower `temperature` keeps explanatory answers more stable.
- Constraining the output format makes downstream handling easier.
- Real systems also need retries, timeout handling, and masking rules.

---

## Where engineers get confused

![Where engineers get confused](../../../assets/korean-ai-stack-101/05/05-03-where-engineers-get-confused.en.png)
- Natural Korean phrasing does not automatically mean factual correctness.
- OpenAI-compatible does not mean every provider behaves the same.
- A detailed prompt is not a substitute for response validation.

---

## Checklist

- [ ] State the target reader and tone in the system message.
- [ ] Fix `temperature` and token limits before comparing outputs.
- [ ] Constrain the output format to bullets, JSON, or another explicit shape.
- [ ] Re-test authentication, error handling, and latency when switching providers.

---

## Summary

The main lesson here is how to operate a Korean generation API, not which provider logo appears in the call. Once the input and output contracts are stable, the final RAG pipeline becomes much easier to ground safely.

<!-- toc:begin -->
## In this series

- [Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Building sentence similarity search with KoSimCSE](./02-kosimcse-similarity.md)
- [BGE-M3 multilingual embedding in practice](./03-bge-m3-multilingual.md)
- [Document text extraction with CLOVA OCR API](./04-clova-ocr.md)
- **Using HyperCLOVA X and Solar API (current)**
- Assembling a Korean RAG pipeline (upcoming)

<!-- toc:end -->

---

## References

- [Groq Python library](https://github.com/groq/groq-python)
- [Groq API reference](https://console.groq.com/docs/api-reference)
- [Upstage Solar documentation](https://developers.upstage.ai/docs/getting-started/overview)

Tags: Korean NLP, LLM, Embeddings, OCR
