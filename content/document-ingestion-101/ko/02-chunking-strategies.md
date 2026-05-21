---
title: "Document Ingestion 101 (2/6): 청킹 전략 — 문서 유형별 최적화"
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

# Document Ingestion 101 (2/6): 청킹 전략 — 문서 유형별 최적화

청킹은 많은 검색 시스템이 조용히 품질을 잃는 지점입니다. FAQ에 잘 맞는 분할기가 매뉴얼이나 정책 문서의 구조를 그대로 망가뜨리는 일은 흔합니다.

이 글은 Document Ingestion 101 시리즈의 두 번째 글입니다.

여기서는 문서 형태별 청킹 프리셋을 비교하고, 분할 결과를 신뢰해도 되는지 빠르게 판단할 수 있는 신호를 살펴봅니다.

## 먼저 던지는 질문

- 모든 문서에 같은 chunk_size를 쓰면 왜 검색 품질이 흔들릴까요?
- Recursive splitter는 어떤 순서로 경계를 포기하며 텍스트를 나눌까요?
- 임베딩 전에 청크 품질을 빠르게 검토하려면 무엇을 봐야 할까요?

## 큰 그림

![Chunking strategy selection flow](https://yeongseon-books.github.io/book-public-assets/assets/document-ingestion-101/02/02-01-chunking-flow-by-document-type.ko.png)

*Chunking strategy selection flow*

이 그림에서는 문서 유형마다 다른 구조를 가진 원문이 splitter 설정을 거쳐 검색 가능한 청크로 바뀌는 흐름을 봅니다. 좋은 청킹은 크기 하나를 고르는 일이 아니라 문서 구조와 검색 질문을 함께 맞추는 일입니다.

> 청킹은 텍스트를 작게 자르는 일이 아니라 검색이 아직 신뢰할 수 있는 최소 문맥 단위를 설계하는 일입니다.

## 문서 유형별 청킹 흐름

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

### Recursive splitter 설정을 코드로 고정하는 방법

실험을 반복하다 보면 separator 순서가 자주 바뀌는데, 이 변경이 기록되지 않으면 같은 문서를 다시 청킹해도 결과가 달라집니다. 그래서 프리셋을 코드 상수로 두고 문서 유형별 정책을 명시적으로 분리하는 편이 운영에 유리합니다.

```python
from __future__ import annotations

from dataclasses import dataclass

from langchain_text_splitters import RecursiveCharacterTextSplitter

@dataclass(frozen=True)
class SplitterPreset:
    chunk_size: int
    chunk_overlap: int
    separators: list[str]

PRESETS: dict[str, SplitterPreset] = {
    'faq': SplitterPreset(120, 24, ['\n\n', '\n', '? ', '. ', ' ']),
    'manual': SplitterPreset(240, 48, ['\n## ', '\n\n', '\n', '. ', ' ']),
    'policy': SplitterPreset(320, 72, ['\n\n', '\n', '; ', '. ', ' ']),
}

def build_splitter(doc_type: str) -> RecursiveCharacterTextSplitter:
    preset = PRESETS[doc_type]
    return RecursiveCharacterTextSplitter(
        chunk_size=preset.chunk_size,
        chunk_overlap=preset.chunk_overlap,
        separators=preset.separators,
    )
```

이 패턴의 장점은 `doc_type`만으로 분할 정책이 완전히 결정된다는 점입니다. 나중에 검색 회귀가 발생했을 때도, 어떤 문서군에 어떤 separator 순서를 적용했는지 곧바로 추적할 수 있습니다.

### overlap 튜닝을 자동 비교하는 최소 루프

겹침 값을 감으로 올리면 청크 수와 중복 토큰 비용이 빠르게 증가합니다. 반대로 너무 낮추면 질문의 앞부분과 답변의 뒷부분이 서로 다른 청크로 갈라집니다. 아래처럼 후보 overlap을 한 번에 비교하면, 비용과 문맥 보존 사이의 균형점을 찾기 쉽습니다.

```python
from __future__ import annotations

from statistics import mean

def tune_overlap(text: str, chunk_size: int, overlaps: list[int]) -> None:
    for overlap in overlaps:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap,
            separators=['\n\n', '\n', '. ', ' '],
        )
        chunks = splitter.split_text(text)
        lengths = [len(chunk) for chunk in chunks]
        duplicated = max(0, overlap) * max(0, len(chunks) - 1)
        print(
            f'overlap={overlap:>2} chunks={len(chunks):>2} '
            f'avg={mean(lengths):>6.1f} duplicate_chars~={duplicated:>4}'
        )

sample_text = ' '.join(
    [
        '질문과 답변이 교차하는 FAQ 문단입니다.',
        '겹침이 부족하면 질문과 답변이 분리됩니다.',
        '겹침이 과하면 중복 비용이 커집니다.',
    ]
    * 20
)
tune_overlap(sample_text, chunk_size=180, overlaps=[0, 12, 24, 36, 48])
```

출력에서 `duplicate_chars`가 급증하는 지점을 먼저 찾고, 그 직전 값을 시작점으로 삼으면 과도한 중복 없이 문맥 연결을 확보할 수 있습니다. 이런 식으로 튜닝 과정을 숫자로 기록해 두면, 나중에 임베딩 모델을 바꿔도 청킹 정책을 독립적으로 유지할 수 있습니다.

## 실무 확장: 청킹 알고리즘 선택과 검색 회귀 방지

청킹 전략은 한 번 정하고 끝내는 설정이 아닙니다. 문서 유형이 늘어나면 동일한 splitter라도 실패 패턴이 달라집니다. 그래서 운영에서는 문서군별 알고리즘을 분리하고, 검색 회귀를 숫자로 감지하는 루프를 반드시 둡니다.

### 구조 기반 청킹과 길이 기반 청킹을 병행하는 패턴

매뉴얼 문서는 제목 경계를 먼저 지키고, 정책 문서는 문단 길이를 우선 맞추는 식으로 알고리즘을 병행하면 안정성이 좋아집니다.

```python
from __future__ import annotations

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

def chunk_manual(markdown_text: str) -> list[str]:
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[('#', 'h1'), ('##', 'h2'), ('###', 'h3')]
    )
    docs = header_splitter.split_text(markdown_text)
    body_splitter = RecursiveCharacterTextSplitter(
        chunk_size=280,
        chunk_overlap=48,
        separators=['

', '
', '. ', ' '],
    )
    chunks: list[str] = []
    for doc in docs:
        chunks.extend(body_splitter.split_text(doc.page_content))
    return chunks

def chunk_policy(long_text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=360,
        chunk_overlap=72,
        separators=['

', '; ', '. ', ' '],
    )
    return splitter.split_text(long_text)
```

핵심은 모든 문서를 하나의 분할기로 몰아넣지 않는 것입니다. 구조가 뚜렷한 문서는 구조 우선, 장문 정책 문서는 길이 우선으로 처리해야 검색 질문이 요구하는 문맥 단위를 유지할 수 있습니다.

### 청킹 회귀를 탐지하는 오프라인 평가 루프

프리셋 변경 후 검색 품질이 떨어졌는지 확인하려면 최소한 고정 질의 세트를 두고 정답 포함 여부를 추적해야 합니다.

```python
from __future__ import annotations

from dataclasses import dataclass

@dataclass(frozen=True)
class RetrievalCase:
    query: str
    expected_source: str

def evaluate_chunk_regression(retriever, cases: list[RetrievalCase], k: int = 5) -> None:
    hit = 0
    for case in cases:
        docs = retriever.invoke(case.query)
        topk = docs[:k]
        if any(doc.metadata.get('source') == case.expected_source for doc in topk):
            hit += 1
    recall_at_k = hit / len(cases) if cases else 0.0
    print(f'recall_at_{k}={recall_at_k:.3f} cases={len(cases)}')
```

이 점수는 완벽한 품질 지표는 아니지만, 청킹 변경이 검색을 악화시키는지 빠르게 확인하는 데 충분합니다. 운영에서는 `recall_at_k`가 기준 아래로 떨어지면 새 프리셋을 배포하지 않는 식으로 게이트를 걸 수 있습니다.

### 청크 메타데이터를 벡터 DB 필터와 맞추는 이유

청크를 만들 때 `doc_type`, `section`, `chunk_order`를 함께 저장해 두면 벡터 검색 결과를 설명하기 쉬워집니다.

```python
chunk.metadata.update(
    {
        'doc_type': 'manual',
        'section': 'deployment-checklist',
        'chunk_order': 17,
        'chunk_size_policy': 'manual-v2',
    }
)
```

이 정보는 나중에 "왜 이 청크가 선택되었는가"를 해석하는 근거가 됩니다. 검색 실패를 모델 문제로 오해하지 않으려면, 청킹 단계의 의사결정 흔적을 메타데이터로 남겨야 합니다.

## 운영 노트: 청크 정책을 버전으로 관리하기

청킹 설정은 코드 한 줄이 아니라 검색 품질 계약입니다. 그래서 운영에서는 `chunk-policy-v1`, `chunk-policy-v2`처럼 정책 버전을 메타데이터에 함께 저장합니다.

```python
chunk.metadata.update(
    {
        'chunk_policy_version': 'chunk-policy-v2',
        'chunk_size': 240,
        'chunk_overlap': 48,
        'separator_profile': 'manual-headers-first',
    }
)
```

이 정보가 있으면 검색 회귀가 발생했을 때 "어떤 정책으로 만들어진 청크에서 문제가 나는지"를 바로 좁힐 수 있습니다. 반대로 정책 버전을 남기지 않으면 인덱스에 서로 다른 규칙이 섞였는지 확인하기 어렵습니다.

추가로, 정책 변경 직후에는 상위 질의 20~50개를 고정해 `recall@k`와 `source diversity`를 비교하는 습관을 권장합니다. 청크 수가 예쁘게 나와도 실제 질의 회수율이 떨어지면 변경을 되돌리는 편이 맞습니다.

## 실전 점검 체크리스트 확장

아래 체크리스트는 배포 직전 10분 점검용으로 자주 사용합니다. 문서 수집 파이프라인은 기능이 아니라 경계 검증으로 안정성이 결정되므로, 매 실행에서 같은 항목을 반복 확인하는 습관이 중요합니다.

- 입력 파일 수가 평소 범위에서 크게 벗어나지 않는지 확인합니다.
- 실패 문서 비율이 임계치(예: 3%)를 넘지 않는지 확인합니다.
- 샘플 문서 3건 이상에 대해 source, page, chunk_id 추적이 가능한지 확인합니다.
- 메타데이터 필드 누락(`source`, `format`, `doc_type`)이 0건인지 확인합니다.
- 벡터 검색 샘플 질의에서 기대 출처가 상위 결과에 포함되는지 확인합니다.

```python
def quick_health_report(stats: dict[str, int | float]) -> None:
    print(f"files_total={stats['files_total']}")
    print(f"failed_total={stats['failed_total']}")
    print(f"chunks_total={stats['chunks_total']}")
    print(f"metadata_missing={stats['metadata_missing']}")
    print(f"smoke_passed={stats['smoke_passed']}")
```

이 정도 점검만 자동화해도 "돌아갔다"와 "운영 가능한 상태로 끝났다"를 구분할 수 있습니다. 장기적으로는 이 리포트를 누적해 주간 추세를 보고, 특정 단계에서 실패율이 증가하는 패턴을 조기에 잡는 것이 좋습니다.

## 마무리 운영 기준

문서 수집 파이프라인은 새 기능보다 기준 유지가 더 중요합니다. 그래서 팀 단위 운영에서는 아래 네 가지를 주간 기준으로 고정해 두는 편이 좋습니다.

- 파싱 품질 지표(평균 문자 수, OCR 비율, 재처리 비율)
- 청킹 품질 지표(평균 길이, 극단 길이 비율, 정책 버전 분포)
- 메타데이터 품질 지표(필수 필드 누락률, 정규화 실패 건수)
- 검색 검증 지표(샘플 질의 recall@k, 출처 회수율)

이 네 축을 함께 보면 어느 경계에서 품질이 떨어지는지 빠르게 확인할 수 있습니다. 결국 안정적인 ingestion은 화려한 모델 선택보다, 입력 품질과 단계 계약을 지속적으로 측정하는 운영 루틴에서 만들어집니다.

## 임베딩 모델 토큰 제한과 청킹 크기의 관계

청킹 크기를 정할 때 임베딩 모델의 최대 입력 토큰 수를 함께 고려해야 합니다. 예를 들어 `text-embedding-3-small`은 8191 토큰까지 받지만, 실제로 512 토큰 이하에서 가장 안정적인 유사도를 보이는 경우가 많습니다. 그래서 `chunk_size`를 문자 수로 설정하더라도, 최종 청크의 토큰 수가 모델 sweet spot을 넘지 않는지 확인하는 검증 단계를 추가하는 편이 좋습니다.

```python
from __future__ import annotations

import tiktoken

def estimate_tokens(text: str, model: str = 'cl100k_base') -> int:
    enc = tiktoken.get_encoding(model)
    return len(enc.encode(text))

def flag_over_limit(chunks: list[str], max_tokens: int = 512) -> list[int]:
    return [i for i, chunk in enumerate(chunks) if estimate_tokens(chunk) > max_tokens]
```

이 검증은 임베딩 호출 전에 넣어야 합니다. 토큰 초과 청크는 truncation되거나 의미가 잘릴 수 있기 때문입니다. 초과 비율이 높으면 `chunk_size`를 줄이거나 separator를 더 세밀하게 조정하라는 신호입니다.

## 처음 질문으로 돌아가기

- **모든 문서에 같은 chunk_size를 쓰면 왜 검색 품질이 흔들릴까요?**
  정책 문서, FAQ, 코드, 표는 의미 경계가 다르므로 같은 크기로 자르면 어떤 문서는 맥락이 끊기고 어떤 문서는 잡음이 섞입니다.

- **Recursive splitter는 어떤 순서로 경계를 포기하며 텍스트를 나눌까요?**
  Recursive splitter는 보통 큰 구분자부터 시도하고 실패하면 더 작은 구분자로 내려가며 마지막에는 문자 단위에 가까워집니다.

- **임베딩 전에 청크 품질을 빠르게 검토하려면 무엇을 봐야 할까요?**
  청크 길이 분포, overlap 실현 여부, 제목·본문 분리, 너무 짧거나 긴 청크, 원문 위치 메타데이터를 확인해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Document Ingestion 101 (1/6): PDF 파싱과 텍스트 추출](./01-pdf-parsing.md)
- **Document Ingestion 101 (2/6): 청킹 전략 — 문서 유형별 최적화 (현재 글)**
- Document Ingestion 101 (3/6): 메타데이터 설계와 필터링 (예정)
- Document Ingestion 101 (4/6): 증분 인덱싱 — 변경된 문서만 업데이트 (예정)
- Document Ingestion 101 (5/6): 다중 포맷 문서 파이프라인 (예정)
- Document Ingestion 101 (6/6): 문서 수집 파이프라인 완성 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [LangChain - How to recursively split text by characters](https://python.langchain.com/docs/how_to/recursive_text_splitter/)
- [LangChain text splitters integration package](https://docs.langchain.com/oss/python/integrations/splitters/index)

### 검증에 도움 되는 자료

- [LangChain RecursiveCharacterTextSplitter API reference](https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html)
- [The Unicode Standard - Text segmentation overview](https://www.unicode.org/reports/tr29/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/document-ingestion-101/ko)

Tags: RAG, Document Processing, LangChain, Python
