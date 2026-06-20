---
title: "바이브코딩을 위한 한국어 AI 스택 (2/6): KoSimCSE로 문장 유사도 구현하기"
series: korean-ai-stack-101
episode: 2
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- Korean NLP
- KoSimCSE
- FAISS
- SemanticSearch
---

# 바이브코딩을 위한 한국어 AI 스택 (2/6): KoSimCSE로 문장 유사도 구현하기

이 글은 **바이브코딩을 위한 한국어 AI 스택** 시리즈의 두 번째 글입니다. KoSimCSE를 사용해 한국어 문장 유사도를 측정하고 FAISS 기반 의미 검색을 구현합니다.

---

"비슷한 내용의 FAQ를 묶고 싶어요", "고객 질문과 유사한 기존 답변을 찾고 싶어요" — 이런 요구사항은 키워드 검색으로 해결하기 어렵습니다. "반품"과 "환불"은 다른 단어지만 같은 의미입니다. 의미 기반 검색이 필요합니다.

바이브코딩으로 AI에게 "한국어 의미 검색 만들어줘"라고 하면 코드가 나옵니다. 그런데 임베딩 결과를 어떻게 측정하는지, 유사도가 높다는 게 실제로 의미가 있는지 검증하는 방법을 모르면 코드가 맞는지 틀린지 알 수 없습니다.

이 글에서는 KoSimCSE로 임베딩을 생성하고, 코사인 유사도로 검색하고, FAISS로 대용량을 처리하는 전체 흐름을 설명합니다.

> "의미 검색은 단어가 아닌 뜻으로 찾습니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 코사인 유사도가 무엇인지 설명할 수 있나요?
2. 임베딩 정규화(normalize)가 왜 필요한가요?
3. FAISS IndexFlatIP와 IndexFlatL2의 차이를 알고 있나요?
4. 의미 검색 결과의 품질을 어떻게 평가하나요?
5. 임베딩 배치 처리가 왜 중요한가요?

---

## KoSimCSE 임베딩 생성

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("BM-K/KoSimCSE-roberta")

def embed_sentences(sentences: list[str]) -> np.ndarray:
    embeddings = model.encode(
        sentences,
        normalize_embeddings=True,  # 코사인 유사도를 위한 정규화
        batch_size=32,
        show_progress_bar=len(sentences) > 100,
    )
    return embeddings.astype("float32")
```

## 코사인 유사도 계산

```python
def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))  # 정규화된 벡터는 내적 = 코사인 유사도

def find_similar(query: str, corpus: list[str], top_k: int = 5) -> list[tuple[str, float]]:
    query_emb = embed_sentences([query])[0]
    corpus_emb = embed_sentences(corpus)

    scores = [cosine_similarity(query_emb, c) for c in corpus_emb]
    ranked = sorted(zip(corpus, scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]
```

## FAISS 의미 검색

```python
import faiss

def build_faiss_index(sentences: list[str]) -> tuple[faiss.Index, list[str]]:
    embeddings = embed_sentences(sentences)
    dim = embeddings.shape[1]

    index = faiss.IndexFlatIP(dim)  # Inner Product = 코사인 유사도(정규화 후)
    index.add(embeddings)

    return index, sentences

def search_faiss(query: str, index: faiss.Index, sentences: list[str], k: int = 5):
    query_emb = embed_sentences([query])
    D, I = index.search(query_emb, k)
    return [(sentences[i], float(D[0][j])) for j, i in enumerate(I[0]) if i != -1]
```

## 품질 검증

```python
def evaluate_similarity(test_pairs: list[tuple[str, str, bool]]) -> dict:
    """
    test_pairs: [(문장1, 문장2, 유사여부), ...]
    """
    correct = 0
    for s1, s2, expected_similar in test_pairs:
        e1 = embed_sentences([s1])[0]
        e2 = embed_sentences([s2])[0]
        score = cosine_similarity(e1, e2)
        predicted_similar = score > 0.75
        if predicted_similar == expected_similar:
            correct += 1
    return {"accuracy": correct / len(test_pairs)}
```

---

## Before / After

| 항목 | Before (키워드 검색) | After (KoSimCSE 의미 검색) |
|------|--------------------|-----------------------------|
| "반품" 검색 | "환불" 문서 누락 | "환불" 문서 포함 |
| 동의어 처리 | 별도 동의어 사전 필요 | 자동 의미 유사도 |
| 다의어 처리 | 어려움 | 문맥 기반 임베딩 |
| 대용량 처리 | 선형 탐색 | FAISS O(log n) |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| normalize 없음 | 코사인 유사도 오류 | normalize_embeddings=True |
| IndexFlatL2로 코사인 유사도 | 잘못된 점수 | IndexFlatIP 사용 |
| 배치 처리 없음 | 메모리 부족 | batch_size 설정 |
| 임계값 미설정 | 관련 없는 결과 포함 | score > 0.75 필터 |

---

## AI 활용 팁

```
KoSimCSE로 한국어 FAQ를 의미 검색하는 시스템을 만들어줘.
임베딩은 normalize_embeddings=True로 정규화하고, FAISS IndexFlatIP를 사용해.
검색 결과에 유사도 점수를 포함하고, 0.75 미만은 제외해줘.
테스트 쌍으로 검색 품질을 평가하는 함수도 만들어줘.
```

---

## 체크리스트

- [ ] KoSimCSE 모델 로드
- [ ] normalize_embeddings=True 설정
- [ ] FAISS IndexFlatIP 인덱스 구성
- [ ] 코사인 유사도 임계값 설정(기본 0.75)
- [ ] 배치 처리(batch_size=32)
- [ ] 유사도 평가 함수로 품질 검증

---

## 처음 질문으로 돌아가기

"'반품'을 검색했는데 '환불' 문서가 왜 안 나오나요?" — 키워드 검색은 단어를 매칭합니다. 의미 검색은 뜻을 매칭합니다. KoSimCSE로 임베딩을 생성하고 FAISS로 검색하면 "반품"과 "환불"이 같은 의미임을 자동으로 인식합니다.

---

## 정리

- KoSimCSE는 한국어 문장 유사도에 특화된 모델이다
- normalize_embeddings=True로 정규화하면 내적이 코사인 유사도와 같아진다
- FAISS IndexFlatIP로 대용량 고속 검색이 가능하다
- 유사도 임계값(0.75)으로 관련 없는 결과를 필터링한다

---

## 참고 자료

- [KoSimCSE 논문](https://arxiv.org/abs/2109.12027)
- [FAISS IndexFlatIP](https://faiss.ai/cpp_api/struct/structfaiss_1_1IndexFlatIP.html)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- KoSimCSE 임베딩 생성
- 코사인 유사도 계산
- FAISS 의미 검색
- 품질 검증
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, Korean NLP, KoSimCSE, FAISS, SemanticSearch
