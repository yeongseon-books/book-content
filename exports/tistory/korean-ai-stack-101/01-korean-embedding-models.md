
# 한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar

한국어 임베딩 모델을 고를 때 중요한 일은 가장 예쁜 벤치마크 점수를 찾는 것이 아닙니다. 실제로는 한국어 FAQ, 한국어·영어 혼합 문서, 임계값 기반 검색처럼 우리 데이터가 흔히 만드는 조건에서 어떤 모델이 더 덜 흔들리는지 확인해야 합니다.

이 글은 Korean AI Stack 101 시리즈의 첫 번째 글입니다. 여기서는 이후 검색 설계의 기준선이 될 수 있도록, 한국어 임베딩 모델을 재현 가능하게 비교하는 프레임을 먼저 만듭니다.

## 이 글에서 다룰 문제

- 영어 중심 임베딩 모델은 한국어 비중이 높은 데이터에서 어디서 자주 무너질까요?
- 코사인 점수 하나보다 유사 쌍과 무관 쌍 사이의 간격이 왜 더 쓸모 있을까요?
- 한국어 텍스트에 영어 기술 용어가 자주 섞일 때는 무엇부터 시험해야 할까요?
- 범용 다국어 모델과 한국어 지향 모델 사이에서 재현 가능한 기준선이 왜 선택을 쉽게 만들까요?

> 임베딩 모델 비교는 리더보드 점수 자랑보다, 유사한 문장을 얼마나 안정적으로 끌어당기고 무관한 문장을 얼마나 멀리 밀어내는지 보는 일에 더 가깝습니다.

> Korean AI Stack 101 (1/6)

예제 코드: [github.com/yeongseon-books/korean-ai-stack-101](https://github.com/yeongseon-books/korean-ai-stack-101/tree/main/en/01-korean-embedding-models)

이 글은 로컬에서 다시 돌려 볼 수 있는 비교 프레임부터 시작합니다. 제목에는 KoSimCSE, BGE-M3, Solar가 들어가지만, 실행 예제는 `all-MiniLM-L6-v2`와 `jhgan/ko-sbert-nli`를 비교합니다. 이유는 단순합니다. 독자가 바로 `python main.py`를 실행하지 못하면 비교는 끝까지 추상적으로 남기 쉽기 때문입니다.

실무에서 진짜 질문은 “어떤 모델이 벤치마크에서 이겼는가?”가 아닙니다. “우리 데이터에서 어떤 모델이 덜 자주 실패하는가?”가 더 중요합니다. 한국어만 있는 FAQ, 영어 제품명이 섞인 한국어 문장, 임계값 기반 검색은 모델마다 전혀 다른 압박을 줍니다. 그래서 첫 글은 한국어 중심 검색으로 더 깊게 들어가기 전에, 반복 가능한 비교 방법부터 다룹니다.

---

## 핵심 흐름

![Core flow](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-01-core-flow.ko.png)

*Core flow*

---

## 왜 재현 가능한 비교부터 시작할까

![Why start with a reproducible comparison](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-01-why-start-with-a-reproducible-comparison.ko.png)

*Why start with a reproducible comparison*

모델 비교는 독자가 자기 환경에서 비슷한 경향을 다시 확인할 수 있을 때만 실전 가치가 있습니다. API 전용 모델이나 비공개 평가셋은 그럴듯해 보일 수 있지만, 다음 날 다시 돌려 보면서 감을 쌓는 데는 거의 도움이 되지 않습니다.

이 예제는 실무에서 유용한 두 가지 관찰점을 남깁니다. 첫째, `ko-sbert-nli`는 유사한 한국어 문장과 무관한 문장 사이에 더 넓은 간격을 만드는 경향이 있습니다. 둘째, `all-MiniLM-L6-v2`는 한국어 문장에 영어가 섞일 때 여전히 쓸 만한 기준선입니다. 한국어 전용 분리력은 더 좁을 수 있지만, 혼합 데이터에서는 해석 가능한 출발점이 됩니다. 이 관점이 있어야 다음 글에서 비교를 실제 검색으로 자연스럽게 이어 갈 수 있습니다.

> 멘탈 모델은 간단합니다. 임베딩 비교는 “누가 1등인가”를 가리는 시험이 아니라, “어떤 모델이 우리 데이터에서 더 안정적인 간격을 만드는가”를 확인하는 계측 작업입니다.

---

## 최소 실행 예제

![Minimal runnable example](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-02-minimal-runnable-example.ko.png)

*Minimal runnable example*

아래 예제는 같은 문장 쌍을 두 모델에 넣고 `similar` 쌍 평균 점수와 `unrelated` 쌍 평균 점수를 비교합니다. 전체 버전은 `main.py`에 있습니다.

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

---

## 이 코드에서 먼저 봐야 할 점

![What to notice in this code](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-03-what-to-notice-in-this-code.ko.png)

*What to notice in this code*

- 두 모델 모두 **같은 문장 쌍**을 봅니다. 그래야 숨겨진 데이터 차이가 아니라 모델 차이만 비교할 수 있습니다.
- `normalize_embeddings=True`는 내적을 코사인 유사도로 바꿔 주고, 같은 벡터를 FAISS에 재사용하기 쉽게 만듭니다.
- 중요한 신호는 높은 점수 하나가 아닙니다. `similar` 평균과 `unrelated` 평균 사이의 간격입니다.
- 한국어 실무 데이터에는 영어 UI 문자열, 제품명, 로그가 자주 섞이므로, 교차 언어 쌍 하나를 일부러 넣어 두는 편이 좋습니다.

---

## 어디서 자주 헷갈릴까요?

![Where engineers get confused](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/01/01-04-where-engineers-get-confused.ko.png)

*Where engineers get confused*

- 한국어 특화 모델이 모든 다국어 워크로드에서 자동으로 이기지는 않습니다. 코퍼스에 한국어와 영어가 많이 섞여 있으면 다국어 모델이 더 안전한 기준선일 수 있습니다.
- 코사인 점수 0.8 같은 숫자는 품질의 절대 기준이 아닙니다. 모델마다 점수 분포가 다릅니다.
- 공개 벤치마크 순위가 운영 품질과 꼭 일치하지는 않습니다. 한국어 띄어쓰기 오류, 오탈자, 짧은 사용자 질의가 리더보드보다 더 큰 영향을 줄 때가 많습니다.

---

## 체크리스트

- [ ] 코퍼스가 한국어 전용인지, 한국어+영어 혼합인지 먼저 적었습니다.
- [ ] 비교에 유사 쌍과 무관 쌍을 모두 넣었습니다.
- [ ] 임계값을 정하기 전에 모델별 점수 분포를 확인했습니다.
- [ ] 다음 검색 단계에 별도 접착 코드 없이 벡터를 바로 넘길 수 있는지 확인했습니다.

---

## 정리

첫 글의 핵심은 특정 모델을 좋아하는 태도가 아니라, 비교를 다루는 규율입니다. 우리 데이터에서 분리 간격을 직접 측정할 수 있어야 이후 설계 선택도 덜 흔들립니다. 다음 글에서는 이 비교를 실제 한국어 문장 유사도 검색 루프로 옮겨 가며 KoSimCSE를 본격적으로 다룹니다.

## 시리즈 목차

- **한국어 임베딩 모델 비교 — KoSimCSE, BGE-M3, Solar (현재 글)**
- KoSimCSE로 문장 유사도 구현하기 (예정)
- BGE-M3 다국어 임베딩 실전 (예정)
- CLOVA OCR API로 문서 텍스트 추출 (예정)
- HyperCLOVA X와 Solar API 사용하기 (예정)
- 한국어 RAG 파이프라인 조합하기 (예정)

## 참고 자료

- [SentenceTransformers documentation](https://www.sbert.net/)
- [jhgan/ko-sbert-nli](https://huggingface.co/jhgan/ko-sbert-nli)
- [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2)

Tags: Korean NLP, LLM, Embeddings, OCR

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
