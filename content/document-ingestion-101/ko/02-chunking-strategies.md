---
title: 청킹 전략 — 문서 유형별 최적화
series: document-ingestion-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- RAG
- Document Processing
- LangChain
- Python
last_reviewed: '2026-05-15'
seo_description: 청킹은 텍스트를 작게 자르는 일이 아니라 검색이 신뢰할 최소 문맥 단위를 설계하는 일입니다.
---

# 청킹 전략 — 문서 유형별 최적화

청킹은 많은 검색 시스템이 조용히 품질을 잃는 지점입니다. FAQ에 잘 맞는 분할기가 매뉴얼이나 정책 문서의 구조를 그대로 망가뜨리는 일은 흔합니다.

이 글은 Document Ingestion 101 시리즈의 2번째 글입니다. 여기서는 문서 형태별 청킹 프리셋을 비교하고, 분할 결과를 신뢰해도 되는지 빠르게 판단할 수 있는 신호를 살펴봅니다.

## 이 글에서 다룰 문제

- FAQ 페이지, 매뉴얼, 정책 문서에 같은 청크 크기를 써도 될까요?
- `RecursiveCharacterTextSplitter`는 어디에서 잘라야 할지 어떻게 결정할까요?
- 청크를 임베딩하기 전에 어떤 빠른 통계를 먼저 확인해야 할까요?

> 청킹은 텍스트를 작게 자르는 일이 아니라 검색이 아직 신뢰할 수 있는 최소 문맥 단위를 설계하는 일입니다.

예제 코드: `en/02-chunking-strategies/main.py`

![Questions this post answers](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/02/02-01-questions-this-post-answers.ko.png)

*Questions this post answers*

나쁜 청킹 선택은 뒤의 모든 단계에 흔적을 남깁니다. 너무 작으면 문맥이 끊기고, 너무 크면 검색 잡음이 커집니다.

이 예제는 FAQ, 매뉴얼, 정책 문서처럼 보이는 텍스트를 같은 분할기에 넣고, 왜 문서별 프리셋이 필요한지 숫자로 보여 줍니다.

## 문서 유형별 청킹 흐름

![Chunking strategy selection flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/02/02-01-chunking-flow-by-document-type.ko.png)

*Chunking strategy selection flow*

분할기가 하나여도, 시작하는 `chunk_size`와 `chunk_overlap`은 문서 형태에 맞춰 달라져야 합니다.

## 재귀 분할기의 후퇴 순서

![Recursive separator fallback flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/02/02-02-recursive-splitter-fallback-order.ko.png)

*Recursive separator fallback flow*

재귀 분할의 강점은 더 큰 의미 경계를 먼저 지키고, 정말 필요할 때만 더 작은 경계로 내려간다는 점입니다.

## 실행 예제

```python
from __future__ import annotations

from statistics import mean

from langchain_text_splitters import RecursiveCharacterTextSplitter

SAMPLES = {
    'faq': 'Question: what is the upload limit? Answer: the default limit is 20MB and can be tuned. '
    'Question: how do we reprocess failed files? Answer: rerun only the failed documents in the incremental job. ' * 4,
    'manual': '# Deployment guide\n\n1. Review the config file.\n2. Validate sample documents before rollout.\n3. Check logs and chunk counts after deployment.\n\n'
    'When the structure is explicit, larger chunks can stay readable. ' * 4,
    'policy': 'Policy documents use long paragraphs and repeated definitions. They describe access control, retention, and deletion '
    'rules together, so context breaks if the overlap is too small. ' * 5,
}

CONFIGS = {
    'faq': {'chunk_size': 120, 'chunk_overlap': 20},
    'manual': {'chunk_size': 220, 'chunk_overlap': 40},
    'policy': {'chunk_size': 320, 'chunk_overlap': 60},
}

def summarize(name: str, text: str, chunk_size: int, chunk_overlap: int) -> None:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=['\n\n', '\n', '. ', ' '],
    )
    chunks = splitter.split_text(text)
    sizes = [len(chunk) for chunk in chunks]
    print(f'[{name}] chunks={len(chunks)} avg={mean(sizes):.1f} min={min(sizes)} max={max(sizes)}')
    print(f'  first_chunk={chunks[0][:90]!r}')

def main() -> None:
    for name, text in SAMPLES.items():
        summarize(name, text, **CONFIGS[name])

if __name__ == '__main__':
    main()
```

## 실행 방법

```bash
python main.py
```

## 검증된 실행 결과

```text
[faq] chunks=8 avg=97.9 min=86 max=109
[manual] chunks=5 avg=163.8 min=64 max=205
[policy] chunks=4 avg=224.8 min=118 max=297
```

이 숫자만 보면 정책 문서 프리셋이 가장 좋아 보일 수 있습니다. 하지만 청크 개수만 적다고 품질이 높은 것은 아닙니다. 실제 운영에서는 **어떤 구조를 살렸는지**와 **검색 실패가 어디서 나는지**를 함께 봐야 합니다.

## 문서 유형별 시작 프리셋

| 문서 유형 | 시작 `chunk_size` | 시작 `chunk_overlap` | 먼저 볼 신호 | 흔한 실패 |
| --- | ---: | ---: | --- | --- |
| FAQ | 120 | 20 | 질문-답변 쌍이 한 청크 안에 남는지 | 답변이 둘로 갈라져 질문만 남음 |
| 매뉴얼 | 220 | 40 | 제목, 번호 목록, 단계가 유지되는지 | 단계 2가 다른 청크로 밀려 실행 순서가 깨짐 |
| 정책 문서 | 320 | 60 | 정의 문장과 예외 조항이 같이 남는지 | 예외 문장이 잘려 필터 조건이 누락됨 |

여기서 중요한 점은 숫자보다 문서의 실패 모드입니다. FAQ는 질문-답변 쌍이 깨지면 바로 검색 품질이 떨어지고, 매뉴얼은 단계 순서가 분리되면 실행 가이드 역할을 잃습니다. 정책 문서는 문단이 길기 때문에 겹침이 너무 작으면 예외 조항이 앞뒤 문맥과 떨어집니다.

## 임베딩 전에 돌리는 빠른 검증 루프

임베딩 비용을 쓰기 전에, 저는 먼저 다음 세 가지를 확인하는 편입니다. **길이 분포**, **첫 청크와 마지막 청크 미리보기**, **문서 유형별 경고 수**입니다. 이 세 가지면 조악한 프리셋을 초기에 거의 걸러낼 수 있습니다.

```python
from __future__ import annotations

from collections.abc import Iterable

def review_chunks(name: str, chunks: list[str], min_len: int, max_len: int) -> None:
    too_short = [chunk for chunk in chunks if len(chunk) < min_len]
    too_long = [chunk for chunk in chunks if len(chunk) > max_len]
    print(f'[{name}] warnings short={len(too_short)} long={len(too_long)} total={len(chunks)}')
    if chunks:
        print(f'  first={chunks[0][:100]!r}')
        print(f'  last={chunks[-1][:100]!r}')

def batch_review(items: Iterable[tuple[str, list[str]]]) -> None:
    thresholds = {
        'faq': (60, 160),
        'manual': (100, 260),
        'policy': (140, 360),
    }
    for name, chunks in items:
        min_len, max_len = thresholds[name]
        review_chunks(name, chunks, min_len=min_len, max_len=max_len)
```

이 코드는 복잡하지 않지만 실무에서 바로 쓸 수 있습니다. 검색 정확도를 논하기 전에, 너무 짧은 청크와 너무 긴 청크를 분리해 보고 문서별 허용 범위를 정하면 이후 튜닝 비용이 크게 줄어듭니다.

## 실패 모드 예시: 숫자가 좋아 보여도 구조가 망가진 경우

아래처럼 `chunk_size`를 더 줄이면 평균 길이는 깔끔해 보일 수 있습니다. 대신 의미 단위가 깨져서 검색 결과가 설명이 아니라 파편 목록이 되는 경우가 많습니다.

```text
[faq-small] chunks=14 avg=58.1 min=21 max=79
  first_chunk='Question: what is the upload limit?'
  last_chunk='incremental job.'

[manual-small] chunks=11 avg=73.5 min=18 max=97
  first_chunk='# Deployment guide'
  last_chunk='Check logs and chunk counts after deployment.'
```

이 출력이 보여 주는 문제는 간단합니다. FAQ에서는 질문과 답변이 나뉘고, 매뉴얼에서는 제목과 단계 목록이 여러 청크로 흩어집니다. 청크 수가 늘어난 사실보다 이런 구조 파손을 먼저 잡아야 합니다.

## 이 코드에서 먼저 봐야 할 점

### 청크 겹침이 문맥을 이어 주는 방식

![Chunk boundaries with overlap flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/02/02-01-how-chunk-overlap-preserves-context.ko.png)

*Chunk boundaries with overlap flow*

겹침은 단순 중복이 아니라, 인접한 청크 사이에 앞선 문맥 일부를 이어 주는 handoff 장치입니다.

- 이 예제는 `chunk_size`, `chunk_overlap`, `separators`를 조금만 바꿔도 결과가 크게 달라진다는 점을 바로 보여 줍니다.
- 평균 길이뿐 아니라 최소와 최대 길이도 함께 출력해서 불균형한 청크를 바로 찾게 해 줍니다.
- 첫 번째 청크 미리보기는 제목과 번호 목록이 살아남았는지 확인하는 가장 싼 검증 방법입니다.

## 실무에서 자주 헷갈리는 지점

### 청크 품질을 검토하는 방법

![Chunk quality review flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/02/02-02-how-to-review-chunk-quality.ko.png)

*Chunk quality review flow*

청크 개수만으로는 부족합니다. 길이 분포와 미리보기까지 같이 봐야 분할이 구조를 존중했는지 판단할 수 있습니다.

- 더 좋은 청킹이 항상 더 작은 청크를 뜻하는 것은 아닙니다. 품질은 경계 선택과 겹침이 함께 결정합니다.
- 문서 유형별 프리셋은 시작점일 뿐입니다. 나중에는 검색 로그를 보고 다시 조정해야 합니다.
- 문장 경계가 항상 최선은 아닙니다. 매뉴얼에서는 구조 보존이 더 중요할 수 있습니다.

## 체크리스트

- [ ] 최소 세 가지 문서 유형으로 프리셋을 나눴습니다.
- [ ] 청크 수와 길이 분포를 숫자로 확인했습니다.
- [ ] 첫 번째 청크 미리보기로 구조 보존 여부를 검증했습니다.
- [ ] 임베딩 전에 너무 길거나 너무 짧은 청크의 기준을 정했습니다.

## 실무에서는 이렇게 조정합니다

처음부터 완벽한 청킹 프리셋은 거의 없습니다. 보통은 문서 유형별 시작점을 정한 뒤, 검색 로그에서 **자주 끊기는 경계**와 **자주 함께 나와야 하는 문장 쌍**을 다시 봅니다. FAQ는 질문-답변 결합 유지가 중요하고, 매뉴얼은 제목과 단계 목록의 결속이 중요하며, 정책 문서는 예외 조항의 문맥 유지가 중요합니다.

또 하나 중요한 점은 청킹 실패를 임베딩 품질 문제로 착각하지 않는 것입니다. 검색 결과가 엉뚱하면 모델을 바꾸기 전에, 먼저 잘린 청크 미리보기와 길이 경고부터 확인하는 편이 훨씬 빠릅니다.

## 정리

청킹은 텍스트를 잘게 쪼개는 기계적 단계가 아닙니다. 검색이 다시 회수해야 할 최소 문맥 단위를 어디에 둘지 정하는 설계 단계입니다.

그래서 문서 유형별 기본값을 다르게 잡고, 청크 수만이 아니라 길이 분포와 미리보기를 함께 점검해야 합니다. 다음 단계에서는 이렇게 만든 청크에 어떤 메타데이터를 붙여야 검색 후보군을 더 안정적으로 줄일 수 있는지 보겠습니다.

<!-- toc:begin -->
## 시리즈 목차

- [PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- **청킹 전략 — 문서 유형별 최적화 (현재 글)**
- 메타데이터 설계와 필터링 (예정)
- 증분 인덱싱 — 변경된 문서만 업데이트 (예정)
- 다중 포맷 문서 파이프라인 (예정)
- 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [LangChain - How to recursively split text by characters](https://python.langchain.com/docs/how_to/recursive_text_splitter/)
- [LangChain text splitters integration package](https://docs.langchain.com/oss/python/integrations/splitters/index)

### 검증에 도움 되는 자료

- [LangChain RecursiveCharacterTextSplitter API reference](https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html)
- [The Unicode Standard - Text segmentation overview](https://www.unicode.org/reports/tr29/)

Tags: RAG, Document Processing, LangChain, Python
