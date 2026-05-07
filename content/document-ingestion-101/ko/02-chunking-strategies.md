---
title: 청킹 전략 — 문서 유형별 최적화
series: document-ingestion-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- RAG
- Document Processing
- LangChain
- Python
last_reviewed: '2026-05-01'
seo_description: 청킹은 텍스트를 잘게 자르는 작업이 아니라 검색이 버틸 수 있는 문맥 단위를 설계하는 작업입니다.
---

# 청킹 전략 — 문서 유형별 최적화

<!-- a-grade-intro:begin -->
## 핵심 질문

문서 유형별 청킹을 어떻게 골라야 다운스트림 검색·생성 품질을 최대화할 수 있을까요?

이 글은 그 질문에 답하기 위해 청킹 전략의 핵심 결정과 운영 함정을 살펴봅니다.

<!-- a-grade-intro:end -->

## 이 글에서 답할 질문

- FAQ, 매뉴얼, 정책 문서에 같은 청크 크기를 써도 될까요?
- RecursiveCharacterTextSplitter는 어떤 구분자 순서로 문서를 자를까요?
- 청킹 결과를 임베딩 전에 어떤 통계로 빠르게 점검할 수 있을까요?

> 청킹은 텍스트를 잘게 자르는 작업이 아니라 검색이 버틸 수 있는 문맥 단위를 설계하는 작업입니다.

예제 코드: `/root/Github/document-ingestion-101/ko/02-chunking-strategies/main.py`

![이 글에서 답할 질문](../../../assets/document-ingestion-101/02/02-01-questions-this-post-answers.ko.png)

*이 글에서 답할 질문*
청킹을 한 번 잘못 잡으면 뒤 단계가 모두 비효율적이 됩니다. 너무 작으면 답변 맥락이 잘리고, 너무 크면 검색 결과에 잡음이 섞입니다.

이번 예제는 FAQ, 매뉴얼, 정책 문서 세 가지 텍스트를 같은 분할기로 돌려 보고, 문서 유형별 프리셋이 왜 필요한지 숫자로 보여줍니다.

## 문서 유형별 청킹 전략 흐름

![문서 유형별 청킹 전략 선택 흐름](../../../assets/document-ingestion-101/02/02-01-chunking-flow-by-document-type.ko.png)

*문서 유형별 청킹 전략 선택 흐름*
같은 분할기를 쓰더라도 문서 유형마다 경계와 겹침의 기본값을 다르게 잡아야 검색 잡음을 줄일 수 있습니다.

## 재귀 분할기 구분자 후퇴 순서

![재귀 분할기의 구분자 후퇴 흐름](../../../assets/document-ingestion-101/02/02-02-recursive-splitter-fallback-order.ko.png)

*재귀 분할기의 구분자 후퇴 흐름*
재귀 분할기의 장점은 의미 있는 큰 경계를 먼저 살려 보고, 안 되면 더 작은 경계로 천천히 내려간다는 점입니다.

## 실행 예제

```python
from __future__ import annotations

from statistics import mean

from langchain_text_splitters import RecursiveCharacterTextSplitter

SAMPLES = {
    'faq': 'Question: what is the upload limit? Answer: the default limit is 20MB and can be tuned. '
    'Question: how do we reprocess failed files? Answer: rerun only the failed documents in the incremental job. ' * 4,
    'manual': '# Deployment guide

1. Review the config file.
2. Validate sample documents before rollout.
3. Check logs and chunk counts after deployment.

'
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
        separators=['

', '
', '. ', ' '],
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

## 이 코드에서 봐야 할 것

### 청크 경계와 overlap 구조

![청크 경계와 겹침이 이어지는 구조](../../../assets/document-ingestion-101/02/02-01-how-chunk-overlap-preserves-context.ko.png)

*청크 경계와 겹침이 이어지는 구조*
겹침은 중복 저장이 아니라 앞 청크의 문맥 실마리를 다음 청크로 이어 주는 안전장치입니다.

- 예제는 `chunk_size`, `chunk_overlap`, `separators`만 바꿔도 결과가 크게 달라진다는 점을 보여줍니다.
- 평균 길이뿐 아니라 최소/최대 길이도 함께 출력해서 불균형한 청크를 바로 찾을 수 있습니다.
- 첫 번째 청크 미리보기를 같이 찍으면 헤더나 번호 목록이 예상대로 보존되는지 확인할 수 있습니다.

## 실무에서 헷갈리는 지점

### 청크 품질 점검 흐름

![청크 품질 지표를 확인하는 점검 흐름](../../../assets/document-ingestion-101/02/02-02-how-to-review-chunk-quality.ko.png)

*청크 품질 지표를 확인하는 점검 흐름*
청크 수만 보는 것으로는 부족하고 길이 분포와 첫 청크 미리보기까지 같이 봐야 경계 품질을 빠르게 판단할 수 있습니다.

- 좋은 청킹은 무조건 작은 청킹이 아닙니다. 검색 품질은 경계와 겹침이 함께 결정합니다.
- 문서 유형별 프리셋은 고정 규칙이 아니라 출발점입니다. 실제 운영에서는 검색 로그로 다시 조정해야 합니다.
- 문장 기준 분할이 항상 최고는 아닙니다. 매뉴얼처럼 구조가 뚜렷한 문서는 헤더 보존이 더 중요할 수 있습니다.

## 시니어 엔지니어는 이렇게 생각합니다

- **고정 크기는 baseline일 뿐** — 거의 항상 더 좋은 전략이 있습니다.
- **semantic chunking이 품질을 올린다** — 의미 단위 분할이 retrieval 정확도를 좌우합니다.
- **overlap이 컨텍스트 누락을 줄인다** — RAG에서 결정적 차이를 만듭니다.
- **문서 구조를 활용한다** — 헤딩·섹션이 자연 경계입니다.
- **청크와 metadata를 함께 저장** — 필터·복원에 필수입니다.

## 체크리스트

- [ ] 문서 유형별 프리셋을 최소 세 가지로 나눴다.
- [ ] 청크 수와 길이 분포를 숫자로 확인했다.
- [ ] 첫 번째 청크 미리보기로 구조 보존 여부를 확인했다.
- [ ] 임베딩 전에 너무 긴 청크와 너무 짧은 청크를 걸러낼 기준을 정했다.

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

- https://python.langchain.com/docs/how_to/recursive_text_splitter/

Tags: RAG, Document Processing, LangChain, Python
