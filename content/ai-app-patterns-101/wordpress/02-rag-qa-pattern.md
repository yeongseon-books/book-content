---
title: "바이브코딩을 위한 AI 앱 패턴 (2/6): RAG QA 패턴"
series: ai-app-patterns-101
episode: 2
language: ko
tags:
- RAG
- Retrieval Augmented Generation
- Vector Search
- 바이브코딩
- Vibe Coding
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 앱 패턴 (2/6): RAG QA 패턴

이 글은 **바이브코딩을 위한 AI 앱 패턴** 시리즈의 두 번째 글입니다.

---

바이브코딩으로 AI 앱을 만들다 보면 "LLM에게 우리 회사 문서를 기반으로 답변하게 하고 싶다"는 요구가 생깁니다. 하지만 모든 문서를 프롬프트에 넣을 수는 없습니다. 문서가 수백 개라면 컨텍스트 윈도우를 초과하고, 비용도 폭증합니다.

RAG(Retrieval Augmented Generation)는 이 문제를 해결합니다. 질문이 들어오면 관련 문서 조각만 검색해 LLM에 전달하고, LLM은 그 맥락을 바탕으로 답변을 생성합니다. 이때 핵심은 두 가지입니다. **오프라인 인덱싱**(문서를 미리 분할하고 벡터화하는 단계)과 **온라인 QA**(질문이 왔을 때 관련 문서를 검색해 답변하는 단계).

> "RAG는 LLM에게 책 전체를 외우게 하는 대신, 필요한 페이지를 찾아 읽게 하는 방식입니다."

## 이 글에서 다룰 질문

1. RAG의 오프라인 인덱싱과 온라인 QA 파이프라인은 어떻게 구성되나요?
2. 문서를 어떻게 분할해야 검색 품질이 높아지나요?
3. 출처 표시(Source Attribution)는 왜 중요하고 어떻게 구현하나요?
4. hit@k와 MRR로 검색 품질을 어떻게 평가하나요?
5. 검색 결과의 관련성을 검증하는 방법은 무엇인가요?

---

## RAG 파이프라인 구조

| 단계 | 작업 | 실행 시점 |
|------|------|----------|
| 오프라인: 분할 | 문서를 청크로 나누기 | 문서 업로드 시 1회 |
| 오프라인: 임베딩 | 청크를 벡터로 변환 | 문서 업로드 시 1회 |
| 오프라인: 인덱싱 | 벡터 DB에 저장 | 문서 업로드 시 1회 |
| 온라인: 검색 | 질문과 유사한 청크 찾기 | 질문마다 실행 |
| 온라인: 생성 | 검색 결과 + 질문으로 답변 | 질문마다 실행 |

## Before / After: RAG 도입 효과

**Before (전체 문서를 프롬프트에 포함)**
```python
docs = load_all_documents()  # 수백 개 문서
response = llm.chat(f"다음 문서를 참고해 답변하세요:\n{docs}\n\n질문: {question}")
# 문제: 토큰 초과, 비용 폭증, 관련 없는 문서로 인한 정확도 하락
```

**After (RAG로 관련 문서만 검색)**
```python
# 오프라인 (1회 실행)
def index_document(doc_id: str, text: str, chunk_size: int = 500) -> list[str]:
    chunks = chunk_text(text, chunk_size)
    for i, chunk in enumerate(chunks):
        embedding = embed(chunk)
        vector_db.upsert(f"{doc_id}-{i}", embedding, {"text": chunk, "doc_id": doc_id})
    return chunks

# 온라인 (질문마다)
def answer_with_sources(question: str, top_k: int = 5) -> dict:
    q_embedding = embed(question)
    results = vector_db.search(q_embedding, top_k=top_k)
    context = "\n\n".join([r["text"] for r in results])

    answer = llm.chat(f"""다음 문서를 참고해 답변하세요.
    답변에 사용한 문서 출처를 반드시 포함하세요.

    문서:
    {context}

    질문: {question}""")

    return {
        "answer": answer,
        "sources": [r["doc_id"] for r in results]
    }
```

## 청크 분할 전략

```python
def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """오버랩이 있는 청크로 텍스트를 분할합니다."""
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += chunk_size - overlap  # 오버랩으로 맥락 연결

    return chunks
```

오버랩(중복 구간)을 두는 이유는 청크 경계에서 맥락이 끊기는 것을 방지하기 위해서입니다.

## 검색 관련성 검증

```python
def validate_relevance(question: str, chunk: str) -> bool:
    """LLM으로 검색된 청크의 관련성을 검증합니다."""
    result = llm.chat(f"""다음 문서 조각이 질문에 답하는 데 관련이 있는지 판단하세요.
    관련 있으면 YES, 없으면 NO만 답하세요.

    질문: {question}
    문서: {chunk}""")

    return "YES" in result.upper()
```

모든 검색 결과를 LLM에 전달하지 말고, 관련성 검증으로 실제로 유용한 청크만 선별하면 답변 품질이 높아집니다.

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 청크가 너무 작음 | 맥락 없는 단편적 정보 | 500-1000 토큰 청크 권장 |
| 청크가 너무 큼 | 관련 없는 내용 포함, 비용 증가 | 적절한 크기 + 오버랩 |
| 출처 표시 없음 | 사용자가 신뢰하기 어려움 | 모든 답변에 source 포함 |
| 검색 결과 검증 없음 | 관련 없는 문서로 답변 품질 저하 | 관련성 검증 단계 추가 |

## AI 팁

hit@k와 MRR(Mean Reciprocal Rank)로 검색 품질을 측정하세요.

```python
def evaluate_retrieval(test_cases: list[dict], k: int = 5) -> dict:
    """검색 품질을 hit@k와 MRR로 평가합니다."""
    hits = 0
    reciprocal_ranks = []

    for case in test_cases:
        results = retrieve_chunks(case["question"], top_k=k)
        retrieved_ids = [r["doc_id"] for r in results]
        expected_id = case["expected_doc_id"]

        if expected_id in retrieved_ids:
            hits += 1
            rank = retrieved_ids.index(expected_id) + 1
            reciprocal_ranks.append(1.0 / rank)
        else:
            reciprocal_ranks.append(0.0)

    return {
        f"hit@{k}": hits / len(test_cases),
        "mrr": sum(reciprocal_ranks) / len(reciprocal_ranks)
    }
```

hit@5가 0.8이면 80%의 경우 상위 5개 결과에 정답 문서가 포함된다는 의미입니다.

## 체크리스트

- [ ] 오프라인 인덱싱과 온라인 QA 파이프라인을 분리했다
- [ ] 청크 크기와 오버랩을 실험해 최적값을 찾았다
- [ ] 모든 답변에 출처 문서를 포함한다
- [ ] hit@k와 MRR로 검색 품질을 평가했다
- [ ] 관련성 검증으로 부적절한 청크를 필터링한다

## 처음 질문으로 돌아가기

**오프라인 인덱싱과 온라인 QA 파이프라인 구조는?** 오프라인에서는 문서를 청크로 분할하고 벡터로 변환해 DB에 저장합니다. 온라인에서는 질문을 벡터로 변환해 유사한 청크를 검색하고, 검색 결과를 컨텍스트로 LLM에 전달해 답변을 생성합니다.

**청크 분할 방법은?** 500-1000 토큰 크기로 분할하되, 50-100 토큰의 오버랩을 두어 경계에서 맥락이 끊기는 것을 방지합니다.

**출처 표시가 중요한 이유는?** 사용자가 답변의 근거를 확인할 수 있어 신뢰도가 높아지고, 오류 발생 시 원본 문서를 확인해 수정할 수 있습니다.

**hit@k와 MRR이란?** hit@k는 상위 k개 결과 안에 정답 문서가 있는 비율, MRR은 정답 문서의 평균 역순위입니다. 둘 다 높을수록 검색 품질이 좋습니다.

**관련성 검증 방법은?** 검색된 청크를 LLM으로 다시 검증해 실제로 질문과 관련 있는 것만 선별합니다. 비용이 추가되지만 답변 품질이 크게 향상됩니다.

## 정리

RAG는 LLM이 모든 문서를 기억하는 대신 필요한 정보만 찾아 답변하는 패턴입니다. 오프라인 인덱싱과 온라인 QA 파이프라인을 분리하고, 출처를 표시하며, 검색 품질을 지속적으로 측정하는 것이 핵심입니다.

다음 글에서는 긴 문서를 요약하고 정보를 추출하는 **문서 어시스턴트** 패턴을 다룹니다.

## 참고 자료

- [AI 앱 패턴 원문: RAG QA 패턴](../ko/02-rag-qa-pattern.md)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 앱 패턴 (1/6): 챗봇 패턴](./01-chatbot-pattern.md)
2. **바이브코딩을 위한 AI 앱 패턴 (2/6): RAG QA 패턴 (현재 글)**
3. [바이브코딩을 위한 AI 앱 패턴 (3/6): 문서 어시스턴트](./03-document-assistant.md)
4. [바이브코딩을 위한 AI 앱 패턴 (4/6): 에이전트 도구 패턴](./04-agent-tool-pattern.md)
5. [바이브코딩을 위한 AI 앱 패턴 (5/6): 워크플로우 자동화](./05-workflow-automation.md)
6. [바이브코딩을 위한 AI 앱 패턴 (6/6): Human-in-the-Loop](./06-human-in-the-loop.md)
<!-- toc:end -->

Tags: RAG, Retrieval Augmented Generation, Vector Search, 바이브코딩, Vibe Coding
