---
title: "바이브코딩을 위한 한국어 AI 스택 (6/6): 한국어 RAG 파이프라인 조합하기"
series: korean-ai-stack-101
episode: 6
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- Korean NLP
- RAG
- Pipeline
- LLM
---

# 바이브코딩을 위한 한국어 AI 스택 (6/6): 한국어 RAG 파이프라인 조합하기

이 글은 **바이브코딩을 위한 한국어 AI 스택** 시리즈의 마지막 글입니다. KoSimCSE/BGE-M3 임베딩, CLOVA OCR, HyperCLOVA X/Solar를 조합해 한국어 RAG 파이프라인을 완성합니다.

---

임베딩 모델, OCR, LLM을 각각 만들었습니다. 이제 연결해야 합니다. 한국어 RAG 파이프라인은 "한국어 문서를 읽어서 → 임베딩하고 → 검색해서 → 한국어로 답변"하는 흐름입니다. 각 단계에서 한국어에 맞는 컴포넌트를 선택해야 전체 품질이 올라갑니다.

바이브코딩으로 AI에게 "한국어 RAG 만들어줘"라고 하면 LangChain 기본 RAG가 나옵니다. 한국어 특화 컴포넌트를 어디에 어떻게 끼워넣는지 모르면, 각 단계에서 만든 것들이 연결되지 않습니다.

이 글에서는 지금까지 만든 컴포넌트를 엔드투엔드 파이프라인으로 통합합니다.

> "한국어 RAG는 한국어 특화 컴포넌트를 각 단계에 배치해야 합니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. RAG 파이프라인의 각 단계(문서 처리 → 임베딩 → 검색 → 생성)를 설명할 수 있나요?
2. 한국어 문서에 특화된 전처리가 필요한 이유가 무엇인가요?
3. 검색된 문서를 LLM에 전달하는 프롬프트 구조가 어떻게 되나요?
4. RAG 파이프라인의 품질을 측정하는 방법이 있나요?
5. 한국어 RAG에서 자주 발생하는 실패 패턴이 무엇인가요?

---

## 한국어 RAG 아키텍처

```
[문서 입력] → [CLOVA OCR / pypdf] → [한국어 청킹]
     → [KoSimCSE / BGE-M3 임베딩] → [FAISS 인덱스]
     → [질문 임베딩 + 검색] → [컨텍스트 구성]
     → [HyperCLOVA X / Solar 생성] → [답변]
```

## 한국어 청킹 설정

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

korean_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", ".", "，", ",", " ", ""],
)
```

## 통합 파이프라인

```python
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class KoreanRAGPipeline:
    def __init__(self, llm_client, embedding_model_name: str = "BM-K/KoSimCSE-roberta"):
        self.embedder = SentenceTransformer(embedding_model_name)
        self.llm = llm_client
        self.index = None
        self.chunks = []
        self.splitter = korean_splitter

    def index_documents(self, texts: list[str]):
        self.chunks = []
        for text in texts:
            self.chunks.extend(self.splitter.split_text(text))

        embeddings = self.embedder.encode(
            self.chunks,
            normalize_embeddings=True,
        ).astype("float32")

        dim = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dim)
        self.index.add(embeddings)

    def retrieve(self, query: str, k: int = 3) -> list[str]:
        if self.index is None:
            raise RuntimeError("인덱스가 없습니다. index_documents()를 먼저 실행하세요.")
        query_emb = self.embedder.encode([query], normalize_embeddings=True).astype("float32")
        D, I = self.index.search(query_emb, k)
        return [self.chunks[i] for i in I[0] if i != -1]

    def answer(self, query: str) -> str:
        context_chunks = self.retrieve(query)
        context = "\n\n---\n\n".join(context_chunks)

        messages = [
            {
                "role": "system",
                "content": "당신은 한국어 문서를 기반으로 정확하게 답변하는 AI 어시스턴트입니다. 제공된 컨텍스트에 없는 내용은 모른다고 답하세요.",
            },
            {
                "role": "user",
                "content": f"컨텍스트:\n{context}\n\n질문: {query}",
            },
        ]
        return self.llm.chat(messages)
```

## 품질 평가

```python
def evaluate_rag(pipeline: KoreanRAGPipeline, test_cases: list[dict]) -> dict:
    """
    test_cases: [{"question": "...", "expected_keywords": ["키워드1", "키워드2"]}, ...]
    """
    results = []
    for case in test_cases:
        answer = pipeline.answer(case["question"])
        keywords_found = [kw for kw in case["expected_keywords"] if kw in answer]
        results.append({
            "question": case["question"],
            "keyword_coverage": len(keywords_found) / len(case["expected_keywords"]),
        })
    avg_coverage = sum(r["keyword_coverage"] for r in results) / len(results)
    return {"avg_keyword_coverage": avg_coverage, "details": results}
```

---

## Before / After

| 항목 | Before (영어 RAG 그대로) | After (한국어 특화 RAG) |
|------|------------------------|-----------------------|
| 임베딩 | text-embedding-ada-002 | KoSimCSE / BGE-M3 |
| LLM | GPT-4 | HyperCLOVA X / Solar |
| 청킹 구분자 | 영어 기준 | 한국어 구분자 추가 |
| OCR | pytesseract | CLOVA OCR |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 영어 구분자만 사용 | 청크 경계 오류 | 한국어 구분자(。, ，) 추가 |
| 컨텍스트 과다 주입 | 응답 품질 저하 | k=3으로 제한 |
| "모른다" 처리 없음 | 환각 응답 | 시스템 프롬프트에 명시 |
| 품질 측정 없음 | 개선 방향 불명 | 키워드 커버리지 평가 |

---

## AI 활용 팁

```
한국어 RAG 파이프라인을 만들어줘.
임베딩은 KoSimCSE, 검색은 FAISS IndexFlatIP, 생성은 Solar API를 사용해줘.
청킹 구분자에 한국어 구분자(。, ，, \n)를 포함하고, 컨텍스트는 최대 3개 청크로 제한해줘.
키워드 커버리지로 RAG 품질을 평가하는 함수도 만들어줘.
```

---

## 체크리스트

- [ ] KoreanRAGPipeline 클래스 구현
- [ ] 한국어 청킹 구분자 설정
- [ ] FAISS IndexFlatIP로 검색
- [ ] 시스템 프롬프트에 "모른다" 처리 포함
- [ ] 키워드 커버리지 평가 함수
- [ ] 엔드투엔드 테스트 실행

---

## 처음 질문으로 돌아가기

"LangChain RAG를 쓰면 되는 거 아닌가요?" — LangChain으로 시작할 수 있습니다. 하지만 한국어 특화 컴포넌트를 각 단계에 배치해야 품질이 올라갑니다. KoSimCSE/BGE-M3 임베딩, 한국어 청킹, HyperCLOVA X/Solar 생성 — 이 조합이 한국어 RAG의 기초입니다.

---

## 정리

- 한국어 RAG는 임베딩(KoSimCSE/BGE-M3), 검색(FAISS), 생성(HyperCLOVA X/Solar)을 한국어 특화로 구성한다
- 청킹 구분자에 한국어 구분자를 추가한다
- 시스템 프롬프트에 "컨텍스트에 없으면 모른다"를 명시해 환각을 방지한다
- 키워드 커버리지로 RAG 품질을 정량 평가한다

---

## 참고 자료

- [LangChain RAG 가이드](https://python.langchain.com/docs/use_cases/question_answering/)
- [KoSimCSE GitHub](https://github.com/BM-K/Sentence-Embedding-is-all-you-need)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 한국어 RAG 아키텍처
- 한국어 청킹 설정
- 통합 파이프라인
- 품질 평가
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, Korean NLP, RAG, Pipeline, LLM
