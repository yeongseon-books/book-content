---
title: '청킹 전략 — 문서 유형별 최적화'
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
---

# 청킹 전략 — 문서 유형별 최적화

## 이 글에서 답할 질문

- FAQ, 매뉴얼, 정책 문서에 같은 청크 크기를 써도 될까요?
- RecursiveCharacterTextSplitter는 어떤 구분자 순서로 문서를 자를까요?
- 청킹 결과를 임베딩 전에 어떤 통계로 빠르게 점검할 수 있을까요?

> 청킹은 텍스트를 잘게 자르는 작업이 아니라 검색이 버틸 수 있는 문맥 단위를 설계하는 작업입니다.

예제 코드: `/root/Github/document-ingestion-101/ko/02-chunking-strategies/main.py`

```mermaid
flowchart LR
    A[문서 유형 선택] --> B[청크 크기와 겹침 설정]
    B --> C[RecursiveCharacterTextSplitter 실행]
    C --> D[청크 수와 길이 분포 비교]
```

청킹을 한 번 잘못 잡으면 뒤 단계가 모두 비효율적이 됩니다. 너무 작으면 답변 맥락이 잘리고, 너무 크면 검색 결과에 잡음이 섞입니다.

이번 예제는 FAQ, 매뉴얼, 정책 문서 세 가지 텍스트를 같은 분할기로 돌려 보고, 문서 유형별 프리셋이 왜 필요한지 숫자로 보여줍니다.

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

- 예제는 `chunk_size`, `chunk_overlap`, `separators`만 바꿔도 결과가 크게 달라진다는 점을 보여줍니다.
- 평균 길이뿐 아니라 최소/최대 길이도 함께 출력해서 불균형한 청크를 바로 찾을 수 있습니다.
- 첫 번째 청크 미리보기를 같이 찍으면 헤더나 번호 목록이 예상대로 보존되는지 확인할 수 있습니다.

## 실무에서 헷갈리는 지점

- 좋은 청킹은 무조건 작은 청킹이 아닙니다. 검색 품질은 경계와 겹침이 함께 결정합니다.
- 문서 유형별 프리셋은 고정 규칙이 아니라 출발점입니다. 실제 운영에서는 검색 로그로 다시 조정해야 합니다.
- 문장 기준 분할이 항상 최고는 아닙니다. 매뉴얼처럼 구조가 뚜렷한 문서는 헤더 보존이 더 중요할 수 있습니다.

## 체크리스트

- [ ] 문서 유형별 프리셋을 최소 세 가지로 나눴다.
- [ ] 청크 수와 길이 분포를 숫자로 확인했다.
- [ ] 첫 번째 청크 미리보기로 구조 보존 여부를 확인했다.
- [ ] 임베딩 전에 너무 긴 청크와 너무 짧은 청크를 걸러낼 기준을 정했다.

<!-- blog-only:start -->

## 정리

청킹 전략은 문서 종류마다 달라야 하며, 숫자로 결과를 비교해 보는 습관이 가장 빠른 품질 점검법입니다.

다음 글에서는 이렇게 만든 청크에 어떤 메타데이터를 붙여야 검색 필터가 살아나는지 설명합니다.

<!-- blog-only:end -->

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
