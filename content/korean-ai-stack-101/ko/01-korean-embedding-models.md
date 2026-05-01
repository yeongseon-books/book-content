---
title: '한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar'
series: korean-ai-stack-101
episode: 1
language: ko
status: draft
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

# 한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar

> 한국어 AI 스택 101 시리즈 (1/6)

예제 코드: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/ko/01-korean-embedding-models)

영어 중심으로 설계된 임베딩 모델은 한국어 문장의 의미를 잘 잡아내지 못합니다. "나는 밥을 먹었다"와 "I had a meal"이 의미상 같다는 것을 알아채려면 한국어 문장 구조를 이해하는 모델이 필요합니다. 이번 글에서는 한국어에 특화된 세 가지 임베딩 모델을 비교합니다.

다룰 내용은 다음과 같습니다.

- 한국어 임베딩 모델을 따로 써야 하는 이유
- KoSimCSE, BGE-M3, Solar Embedding의 특징 비교
- 같은 문장 쌍으로 세 모델 유사도 비교
- 어느 상황에 어떤 모델을 선택할지 기준

---

## 한국어 임베딩 모델을 따로 써야 하는 이유

`sentence-transformers/all-MiniLM-L6-v2` 같은 다국어 모델도 한국어를 처리할 수 있습니다. 하지만 훈련 데이터의 대부분이 영어이기 때문에 한국어 표현, 조사, 어미 변화에 민감하지 않습니다.

예를 들어, "서울시청"과 "서울 시청"은 같은 의미지만 범용 모델은 두 표현을 멀리 배치할 수 있습니다. 한국어 전용 모델은 형태소 단위로 언어를 이해하도록 훈련되어 이런 문제를 줄입니다.

---

## 세 모델 개요

**KoSimCSE-RoBERTa** (`BM-K/KoSimCSE-roberta-multitask`): 카카오브레인과 HuggingFace 커뮤니티가 공개한 한국어 SimCSE 모델입니다. 한국어 문장 유사도 벤치마크에서 강한 성능을 보입니다. 768차원 벡터를 출력합니다. HuggingFace에서 무료로 사용할 수 있습니다.

**BGE-M3** (`BAAI/bge-m3`): 베이징 AI 연구소(BAAI)가 만든 다국어 모델입니다. 100개 이상의 언어를 지원하며 한국어 성능도 우수합니다. Dense, Sparse, Multi-vector 세 가지 검색 방식을 모두 지원해 하이브리드 검색에 강점이 있습니다. 1024차원 벡터를 출력합니다.

**Solar Embedding** (`upstage/solar-embedding-1-large-query`): 업스테이지가 만든 한국어/영어 이중 언어 모델입니다. 한국어 RAG에 최적화되어 있으며 API 형태로 제공됩니다. 4096차원 고차원 벡터를 사용해 미세한 의미 차이를 잘 구분합니다.

---

## 세 모델 비교 실험

```python
import numpy as np
from sentence_transformers import SentenceTransformer

# ── 모델 로드 ──────────────────────────────────────────────────────────────
print("모델 로딩 중...")

kosimcse = SentenceTransformer("BM-K/KoSimCSE-roberta-multitask")
bge_m3 = SentenceTransformer("BAAI/bge-m3")

print("모델 로딩 완료")

# ── 테스트 문장 쌍 ─────────────────────────────────────────────────────────
sentence_pairs = [
    # (문장A, 문장B, 예상 관계)
    ("나는 오늘 밥을 먹었다.", "나는 오늘 식사를 했다.", "유사"),
    ("서울 날씨가 맑다.", "부산 날씨가 흐리다.", "무관"),
    ("파이썬으로 웹 서버를 만들었다.", "Python을 이용해 웹 애플리케이션을 개발했다.", "유사"),
    ("고양이가 쥐를 잡았다.", "주식 시장이 하락했다.", "무관"),
    ("인공지능이 의료 진단을 돕는다.", "AI가 병원에서 환자 진단을 지원한다.", "유사"),
]

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def compare_models(pairs: list[tuple]) -> None:
    print(f"\n{'문장A':<30} {'문장B':<30} {'예상':^6} {'KoSimCSE':^10} {'BGE-M3':^10}")
    print("-" * 90)

    for sent_a, sent_b, expected in pairs:
        # KoSimCSE
        vec_a = kosimcse.encode(sent_a, normalize_embeddings=True)
        vec_b = kosimcse.encode(sent_b, normalize_embeddings=True)
        ko_sim = cosine_similarity(vec_a, vec_b)

        # BGE-M3
        vec_a = bge_m3.encode(sent_a, normalize_embeddings=True)
        vec_b = bge_m3.encode(sent_b, normalize_embeddings=True)
        bge_sim = cosine_similarity(vec_a, vec_b)

        a_display = sent_a[:28] + ".." if len(sent_a) > 30 else sent_a
        b_display = sent_b[:28] + ".." if len(sent_b) > 30 else sent_b
        print(f"{a_display:<30} {b_display:<30} {expected:^6} {ko_sim:^10.3f} {bge_sim:^10.3f}")

compare_models(sentence_pairs)
```

---

## 차원과 검색 성능의 관계

임베딩 차원이 높을수록 더 미세한 의미 차이를 담을 수 있지만, 저장 공간과 검색 시간도 늘어납니다.

```python
import numpy as np
import time
import faiss
from sentence_transformers import SentenceTransformer

# 모델별 차원
# KoSimCSE: 768차원
# BGE-M3: 1024차원
# Solar (API): 4096차원

# BGE-M3로 차원 vs 검색 속도 실험
bge_m3 = SentenceTransformer("BAAI/bge-m3")

documents = [
    "파이썬 웹 개발 프레임워크 비교",
    "머신러닝 모델 훈련 방법",
    "한국어 자연어 처리 기술",
    "데이터베이스 인덱스 최적화",
    "클라우드 서비스 아키텍처 설계",
    "딥러닝 이미지 분류 모델",
    "API 보안과 인증 방법",
    "도커 컨테이너 배포 전략",
] * 100  # 800개 문서

print(f"문서 수: {len(documents)}")

# 임베딩 생성
start = time.time()
embeddings = bge_m3.encode(documents, normalize_embeddings=True, show_progress_bar=True)
embed_time = time.time() - start
print(f"임베딩 시간: {embed_time:.2f}초")
print(f"임베딩 차원: {embeddings.shape[1]}")
print(f"저장 공간: {embeddings.nbytes / 1024:.1f} KB")

# FAISS 인덱스 구성
embeddings_f32 = embeddings.astype(np.float32)
index = faiss.IndexFlatIP(embeddings.shape[1])
index.add(embeddings_f32)

# 검색 속도 측정
query = "자연어 처리를 위한 딥러닝 모델"
query_vec = bge_m3.encode([query], normalize_embeddings=True).astype(np.float32)

start = time.time()
for _ in range(100):
    distances, indices = index.search(query_vec, k=5)
search_time = (time.time() - start) / 100 * 1000
print(f"\n검색 속도: {search_time:.3f}ms (100회 평균)")
print(f"상위 5개 결과:")
for i, idx in enumerate(indices[0]):
    print(f"  {i+1}. [{distances[0][i]:.3f}] {documents[idx]}")
```

---

## 모델 선택 기준

**한국어 전용, 무료, 가벼운 모델이 필요할 때**: KoSimCSE를 선택합니다. 768차원으로 저장 부담이 적고, HuggingFace에서 바로 사용할 수 있습니다. 한국어 문장 유사도 태스크에서 검증된 성능을 보입니다.

**한국어/영어 혼용 문서를 다룰 때**: BGE-M3를 선택합니다. 기술 문서, 학술 자료처럼 영어가 섞인 한국어 텍스트에 강합니다. Dense + Sparse 하이브리드 검색도 지원합니다.

**최고 품질의 한국어 RAG가 필요하고 API 비용을 감당할 수 있을 때**: Solar Embedding을 선택합니다. 4096차원 고차원 벡터로 미세한 의미 차이를 잘 잡아내며, 업스테이지가 한국어에 특화해서 훈련했습니다.

---

## 마무리

한국어 임베딩 모델 선택은 요구사항에 따라 달라집니다. 비용 없이 시작하려면 KoSimCSE나 BGE-M3로 충분합니다. 다음 글에서는 KoSimCSE를 실제로 사용해서 문장 유사도 검색 시스템을 만듭니다.

<!-- blog-only:start -->
다음 글: [KoSimCSE로 문장 유사도 구현하기](./02-kosimcse-similarity.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- **한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar (현재 글)**
- KoSimCSE로 문장 유사도 구현하기 (예정)
- BGE-M3 다국어 임베딩 실전 (예정)
- CLOVA OCR API로 문서 텍스트 추출 (예정)
- HyperCLOVA X와 Solar API 사용하기 (예정)
- 한국어 RAG 파이프라인 조합하기 (예정)

<!-- toc:end -->

---

## 참고 자료

- [KoSimCSE 논문 (Kim et al., 2021)](https://arxiv.org/abs/2109.12145)
- [BGE-M3 HuggingFace 페이지](https://huggingface.co/BAAI/bge-m3)
- [Upstage Solar Embedding](https://developers.upstage.ai/docs/apis/embeddings)
- [SentenceTransformers 라이브러리](https://www.sbert.net/)

Tags: Korean NLP, LLM, Embeddings, OCR
