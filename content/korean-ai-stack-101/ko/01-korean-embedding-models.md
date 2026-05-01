---
title: '한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar'
series: korean-ai-stack-101
episode: 1
language: ko
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

# 한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar

## 이 글에서 답할 질문

- 한국어 문장을 많이 다루는 팀이 영어 중심 임베딩만 쓰면 어디서 자주 틀어질까요?
- 모델 비교에서 코사인 유사도 한두 개보다 separation gap을 먼저 봐야 하는 이유는 무엇일까요?
- 한국어 문장과 영어 기술 용어가 섞인 데이터에서는 어떤 비교 축을 먼저 잡아야 할까요?
- 바로 돌려 볼 수 있는 기준선 모델과 한국어 특화 모델을 함께 놓고 보면 어떤 판단이 쉬워질까요?

> 임베딩 모델 비교는 절대 점수 자랑이 아니라, 비슷한 문장과 무관한 문장을 얼마나 안정적으로 벌려 놓는지 보는 작업입니다.

> 한국어 AI 스택 101 시리즈 (1/6)

예제 코드: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/ko/01-korean-embedding-models)

이번 글의 목표는 화려한 벤치마크 표를 다시 옮기는 데 있지 않습니다. 같은 문장 쌍을 두 모델에 통과시키고, 한국어 문장·영어 혼용 문장·무관한 문장이 어떤 간격으로 분리되는지 직접 보는 데 있습니다. 글 제목에는 KoSimCSE, BGE-M3, Solar가 함께 나오지만, 실행 예제는 재현성을 우선해 `all-MiniLM-L6-v2`와 `jhgan/ko-sbert-nli`를 비교합니다. 독자가 바로 `python main.py`로 돌릴 수 있어야 비교 기준이 손에 잡히기 때문입니다.

실무에서는 "어떤 모델이 제일 좋으냐"보다 "우리 데이터에서 어떤 실패를 덜 내느냐"가 더 중요합니다. 고객센터 FAQ처럼 짧은 한국어 문장이 많은지, 한국어 설명문 안에 영어 제품명이 자주 섞이는지, 코사인 점수를 임계값으로 잘라야 하는지에 따라 선택 기준이 달라집니다. 그래서 첫 글은 모델 소개보다 비교 프레임을 먼저 세웁니다.

---

## 핵심 흐름

![핵심 흐름](../../../assets/korean-ai-stack-101/01/01-01-core-flow.ko.png)
---

## 왜 재현 가능한 비교부터 시작할까

모델 비교 글이 실전에서 도움이 되려면 독자가 같은 코드를 돌려서 비슷한 경향을 확인할 수 있어야 합니다. API 전용 모델이나 사내 전용 평가셋만으로 비교하면 읽을 때는 그럴듯하지만, 다음 날 바로 다시 확인하기 어렵습니다.

이번 예제는 두 가지 관찰 포인트를 남깁니다. 첫째, 한국어 전용에 가까운 `ko-sbert-nli`는 유사 문장과 무관 문장을 더 크게 벌려 놓는 경향을 보입니다. 둘째, 범용 `all-MiniLM-L6-v2`는 영어 표현이 섞일 때 기준선으로는 유용하지만, 한국어만 놓고 보면 separation gap이 더 좁게 나올 수 있습니다. 이 차이를 알아두면 다음 글에서 KoSimCSE를 볼 때도 "한국어 문장끼리 더 잘 모이는가"를 같은 방식으로 확인할 수 있습니다.

---

## 최소 실행 예제

아래 코드는 두 모델을 같은 문장 쌍에 적용하고, `similar` 평균과 `unrelated` 평균을 비교합니다. 전체 실행 파일은 `main.py`에 있습니다.

```python
import numpy as np
from sentence_transformers import SentenceTransformer

MODEL_NAMES = {
    'all-MiniLM-L6-v2': 'sentence-transformers/all-MiniLM-L6-v2',
    'ko-sbert-nli': 'jhgan/ko-sbert-nli',
}

SENTENCE_PAIRS = [
    ('나는 오늘 점심으로 비빔밥을 먹었다.', '오늘 점심은 비빔밥이었다.', 'similar'),
    ('서울시청 앞에서 회의를 했다.', '회의는 서울 시청 앞에서 열렸다.', 'similar'),
    ('비가 와서 우산을 챙겼다.', 'GPU 메모리가 부족해 학습이 중단됐다.', 'unrelated'),
]

for label, name in MODEL_NAMES.items():
    model = SentenceTransformer(name)
    scores = []
    for sent_a, sent_b, expected in SENTENCE_PAIRS:
        emb = model.encode([sent_a, sent_b], normalize_embeddings=True)
        score = float(np.dot(emb[0], emb[1]))
        scores.append((expected, score))
    print(label, scores)
```

~~~
출력 결과
all-MiniLM-L6-v2 [('similar', 0.7876580953598022), ('similar', 0.9715070128440857), ('unrelated', 0.27471810579299927)]
ko-sbert-nli [('similar', 0.9112296104431152), ('similar', 0.8726195096969604), ('unrelated', 0.0983656570315361)]
~~~

---

## 이 코드에서 봐야 할 것

- 두 모델에 **같은 문장 쌍**을 넣습니다. 그래야 점수 차이가 데이터셋 차이가 아니라 모델 차이에서 왔는지 읽을 수 있습니다.
- `normalize_embeddings=True`를 켜 두면 내적이 곧 코사인 유사도가 됩니다. 실험 코드가 짧아지고, FAISS `IndexFlatIP`와도 연결하기 쉬워집니다.
- 개별 점수보다 `similar 평균 - unrelated 평균`을 같이 봐야 합니다. 운영에서는 이 간격이 넓을수록 임계값을 잡기가 편합니다.
- 한국어/영어 혼용 쌍을 하나 넣어 둔 이유는, 실제 문서가 완전한 단일 언어가 아닌 경우가 많기 때문입니다.

---

## 실무에서 헷갈리는 지점

- 한국어 특화 모델이 항상 모든 다국어 작업에서 우세한 것은 아닙니다. 영어가 많이 섞인 문서 검색이면 다국어 모델이 더 안정적일 수 있습니다.
- 코사인 점수 0.8이 "좋다"는 절대 기준은 아닙니다. 모델마다 분포가 다르므로, 상대적 간격과 실제 검색 결과를 함께 봐야 합니다.
- 벤치마크 리더보드 순위와 운영 체감 품질은 다를 수 있습니다. 짧은 질의, 오탈자, 띄어쓰기 흔들림 같은 한국어 실전 조건이 더 중요할 때가 많습니다.

---

## 체크리스트

- [ ] 우리 데이터가 한국어 단일 문장 중심인지, 한국어/영어 혼용인지 먼저 적어 본다.
- [ ] 유사 문장과 무관 문장을 함께 넣어 separation gap을 본다.
- [ ] 모델별 점수 분포를 확인한 뒤 임계값 후보를 정한다.
- [ ] 바로 다음 단계에서 FAISS나 벡터 DB로 이어질 수 있는지 확인한다.

---

## 마무리

첫 글에서 가져가야 할 핵심은 "모델 이름"이 아니라 "비교 방법"입니다. 같은 문장 쌍으로 간격을 보고, 그 간격이 실제 검색 품질로 이어지는지 확인해야 다음 선택이 쉬워집니다. 다음 글에서는 한국어 문장 유사도 검색을 더 직접적으로 보여 주는 KoSimCSE 예제로 넘어갑니다.

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

- [SentenceTransformers documentation](https://www.sbert.net/)
- [jhgan/ko-sbert-nli](https://huggingface.co/jhgan/ko-sbert-nli)
- [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

Tags: Korean NLP, LLM, Embeddings, OCR
