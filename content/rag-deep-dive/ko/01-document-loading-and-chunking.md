---
title: "RAG Deep Dive (1/6): 문서 로딩과 청크 전략 — LangChain TextSplitter 내부"
series: rag-deep-dive
episode: 1
language: ko
status: published
published_to:
  tistory:
    url: "https://yeongseonchoe.tistory.com/83"
    published_at: '2026-05-14'
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- RAG
- LangChain
- Vector Search
- LLM
last_reviewed: '2026-05-15'
seo_description: PyPDFLoader와 RecursiveCharacterTextSplitter가 문서를 청크로 나누는 내부 동작을 예제와 함께 분해합니다.
---

# RAG Deep Dive (1/6): 문서 로딩과 청크 전략 — LangChain TextSplitter 내부

PyPDFLoader와 RecursiveCharacterTextSplitter는 문서를 청크로 나누는 방식에 따라 이후 retrieval 품질을 좌우합니다. 여기서는 그 내부 동작을 예제와 함께 분해합니다.

이 글은 RAG Deep Dive 시리즈의 첫 번째 글입니다.

![문서 로더별 메타데이터 전달 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/01/01-01-loader-metadata-flow.ko.png)
*문서 로더별 메타데이터 전달 흐름*
> 청킹은 텍스트를 잘게 자르는 작업이 아닙니다. 나중에 retrieval이 다시 회수하길 바라는 의미 경계를 지금 얼려 두는 작업입니다.

## 이 글에서 다룰 문제

- 유사도 검색이 시작되기 전, 로더와 splitter 경계는 왜 검색 품질을 좌우할까요?
- Character, Recursive, Token splitter는 같은 텍스트를 어떻게 다르게 자를까요?
- `chunk_overlap`이 설정값만큼 정확히 겹치지 않는 것처럼 보일 때 어디를 봐야 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 최소 실행 예제

예제 파일: `en/01-document-loading-and-chunking/main.py`

```bash
export GROQ_API_KEY=... && python main.py
```

```python
from langchain_text_splitters import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
)

TEXT = """# Incident runbook

## Retry policy
The worker retries a failed message three times.
After the final retry, the payload moves to the dead-letter queue.

## Operator action
The on-call engineer checks the exception chain and the original payload.
"""

def print_chunks(name: str, chunks: list[str]) -> None:
    print(f"\n=== {name} ({len(chunks)} chunks) ===")
    for index, chunk in enumerate(chunks, start=1):
        print(f"[{index}] {chunk!r}")

def main() -> None:
    character = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=90,
        chunk_overlap=10,
    )
    recursive = RecursiveCharacterTextSplitter(
        chunk_size=90,
        chunk_overlap=10,
    )
    token = TokenTextSplitter(
        encoding_name="cl100k_base",
        chunk_size=24,
        chunk_overlap=4,
    )

    print_chunks("CharacterTextSplitter", character.split_text(TEXT))
    print_chunks("RecursiveCharacterTextSplitter", recursive.split_text(TEXT))
    print_chunks("TokenTextSplitter", token.split_text(TEXT))

if __name__ == "__main__":
    main()
```

### 이 코드에서 봐야 할 것

- 같은 원문을 세 splitter에 넣어도 청크 수와 경계가 달라집니다.
- `RecursiveCharacterTextSplitter`는 문단과 줄바꿈을 최대한 살린 뒤 더 거친 분할로 내려갑니다.
- `TokenTextSplitter`는 모델 예산 기준으로 더 예측 가능한 창을 만듭니다.

### 실무에서 헷갈리는 지점

- `chunk_overlap=10`이 항상 정확히 10문자 겹침을 뜻하지는 않습니다.
- 재귀 분할은 구조 보존에 강하지만, 도메인별 경계를 자동으로 이해하는 것은 아닙니다.
- 문자 기준으로 안전해 보여도 토큰 기준 컨텍스트 한도는 초과할 수 있습니다.

### 검증 출력 예시

예제를 실행하면 정확한 문자열은 약간 달라도, 아래와 비슷한 형태가 나와야 합니다.

```text
=== CharacterTextSplitter (2 chunks) ===
[1] '# Incident runbook\n\n## Retry policy\nThe worker retries ...'
[2] 'After the final retry, the payload moves ...'

=== RecursiveCharacterTextSplitter (2 chunks) ===
[1] '# Incident runbook\n\n## Retry policy\nThe worker retries ...'
[2] '## Operator action\nThe on-call engineer checks ...'

=== TokenTextSplitter (3 chunks) ===
[1] '# Incident runbook\n\n## Retry policy\nThe worker ...'
[2] 'three times. After the final retry ...'
[3] '## Operator action\nThe on-call engineer ...'
```

여기서 확인할 핵심은 세 가지입니다.

- 문자 분할은 먼저 선택한 구분자를 최대한 지키는지
- 재귀 분할은 일반 문자 분할보다 상위 구조를 더 오래 보존하는지
- 토큰 분할은 텍스트가 조밀해질수록 창 개수를 더 예측 가능하게 만드는지

## 운영 체크리스트

- [ ] 로더가 만든 기본 `Document` 경계를 먼저 확인했다.
- [ ] 문자 기준과 토큰 기준 분할 결과를 둘 다 비교했다.
- [ ] overlap이 조각 단위로 실현된다는 점을 로그로 검증했다.
- [ ] 프롬프트 직전 토큰 예산 점검이 따로 필요하다는 점을 이해했다.

## 소스 버전

이 글의 모든 코드 인용은 [`langchain-ai/langchain @ v0.2.17`](https://github.com/langchain-ai/langchain/tree/langchain==0.2.17) 기준입니다.

RAG 파이프라인이 실패할 때 많은 팀이 제일 먼저 의심하는 곳은 인덱스나 retriever입니다. 하지만 실제 운영에서 더 자주 먼저 무너지는 지점은 그 앞단입니다. 문서를 어떤 단위로 읽고, 어떤 경계에서 자르고, 어떤 메타데이터를 남겼는가가 틀어지면 뒤의 모든 단계가 그 왜곡을 충실하게 확대합니다. 벡터 인덱스는 이미 잘못 잘린 조각을 저장할 뿐이고, retriever는 그중 가장 가까운 조각을 성실하게 가져올 뿐입니다. 질문에 대한 답이 문서에 있었는데도 못 찾는 경우를 추적해 보면, 원인은 "검색을 못 했다"보다 "애초에 답이 들어 있던 문맥을 우리가 잘라서 잃어버렸다"인 경우가 훨씬 많습니다.

이번 글은 그 실패 지점을 LangChain 소스 수준에서 확인합니다. 범위는 `langchain_community.document_loaders`의 로더들, `langchain_text_splitters`의 `CharacterTextSplitter`, `RecursiveCharacterTextSplitter`, `TokenTextSplitter`입니다. 특히 `TextSplitter`의 기본 병합 로직인 `_merge_splits()`가 왜 `chunk_overlap`을 생각보다 다르게 느끼게 만드는지, `RecursiveCharacterTextSplitter`가 왜 기본 선택으로 굳어졌는지, 문자 수와 토큰 수의 차이가 언제 실제 장애로 이어지는지를 차례로 보겠습니다.

---

## 청킹은 왜 RAG의 첫 번째 실패 지점인가

RAG에서 검색 품질은 임베딩 모델 하나로 결정되지 않습니다. 더 앞에서 이미 두 가지 결정이 내려집니다. 첫째, 로더가 무엇을 한 덩어리의 `Document`로 만들었는가입니다. 둘째, splitter가 그 덩어리를 어떤 경계에서 다시 나눴는가입니다. 이 두 단계가 잘못되면 retriever는 "질문과 가장 가까운 벡터"를 찾아도 사용자가 원하는 문맥 전체를 못 가져옵니다.

예를 들어 계약서 PDF에서 면책 조항이 한 페이지 끝과 다음 페이지 시작에 걸쳐 있다고 해보겠습니다. 로더가 페이지별 문서를 만들고 splitter가 페이지 내부에서만 잘랐다면, 실제로 의미 단위는 둘로 찢어집니다. FAQ 문서에서는 제목과 답변 본문이 다른 청크로 떨어질 수 있습니다. 소스 코드는 함수 시그니처와 예외 처리 블록이 분리되면 검색은 되더라도 답변에 필요한 조건 문맥이 사라집니다. 이런 문제는 retriever 튜닝으로 뒤늦게 복구하기 어렵습니다. 없는 문맥은 다시 검색할 수 없기 때문입니다.

이 글의 관점은 단순합니다. **chunking은 저장 최적화가 아니라 의미 보존 문제**입니다. 이제 그 보존이 실제 코드에서 어떻게 구현되는지부터 보겠습니다.

---

## 1. 문서 로더는 무엇을 읽고 무엇을 남기는가

LangChain에서 로더의 첫 책임은 파일을 읽는 일이고, 두 번째 책임은 그 결과를 `Document(page_content=..., metadata=...)` 형태로 만드는 일입니다. 이 두 번째가 중요합니다. 이후 splitter와 vector store는 대부분 이 `Document`의 `page_content`와 `metadata`를 그대로 이어받기 때문입니다.

가장 단순한 `TextLoader`는 파일을 `open()`으로 읽고 `metadata = {"source": str(self.file_path)}`를 만들어 단 하나의 `Document`를 yield 합니다. `PDFMinerLoader`는 `concatenate_pages=True`면 전체 PDF를 하나의 텍스트로 합치고, `concatenate_pages=False`면 페이지마다 `metadata={"source": blob.source, "page": str(i)}`가 붙은 `Document`가 나옵니다. 같은 PDF라도 이 설정 하나로 이후 청킹의 시작점이 완전히 달라집니다.

```python
from pathlib import Path

from langchain_community.document_loaders import (
    PDFMinerLoader,
    TextLoader,
)


def load_corpus(base_dir: Path):
    docs = []

    docs.extend(
        TextLoader(
            base_dir / "announcements" / "release-note.txt",
            encoding="utf-8",
            autodetect_encoding=True,
        ).load()
    )

    docs.extend(
        PDFMinerLoader(
            str(base_dir / "manuals" / "oncall-runbook.pdf"),
            concatenate_pages=False,
        ).load()
    )

    for doc in docs[:5]:
        print(doc.metadata)

    return docs


if __name__ == "__main__":
    corpus = load_corpus(Path("sample_data"))
    print(f"loaded documents: {len(corpus)}")
```

운영 관점에서 이 섹션의 핵심은 하나입니다. **splitter를 바꾸기 전에 로더가 만든 기본 문서 단위를 먼저 봐야 합니다.** `chunk_size`를 아무리 조절해도, 로더가 이미 제목과 본문을 분리했거나 페이지 경계를 고정해 버렸다면 그 위에서 얻는 청크의 성질도 제한됩니다.

---

## 2. `TextSplitter` 내부에서 실제 청크가 만들어지는 방식

많은 설명이 `CharacterTextSplitter`를 "구분자로 자른다" 수준에서 멈추지만, 실제로 중요한 부분은 자른 뒤 다시 합치는 병합 단계입니다. `CharacterTextSplitter.split_text()`는 먼저 `_split_text_with_regex()`로 원문을 작은 조각들로 나눈 다음, 최종 결과는 `TextSplitter._merge_splits()`에 맡깁니다. 이 함수가 `chunk_size`, `chunk_overlap`, `length_function`의 상호작용을 결정합니다.

![문자 분할 뒤 병합 창 이동 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/01/01-02-character-splitter-merge-window.ko.png)

*문자 분할 뒤 병합 창 이동 흐름*

`chunk_overlap`은 "청크마다 정확히 N자를 겹치게 한다"는 뜻이 아닙니다. `_merge_splits()`는 `splits`를 순서대로 쌓다가 `chunk_size`를 넘는 순간 현재 묶음을 확정한 뒤 슬라이딩 윈도를 만듭니다. 겹침이 조각 단위로 계산되기 때문에 실제 overlap 길이는 구분자 구조에 따라 들쭉날쭉합니다.

```python
from langchain_text_splitters import CharacterTextSplitter

text = """Incident summary

The payment worker retries a failed task three times.
If all retries fail, the message moves to the dead-letter queue.
Operators must inspect the original payload and the exception chain.
"""

splitter = CharacterTextSplitter(
    separator="\n",
    chunk_size=80,
    chunk_overlap=20,
    length_function=len,
    add_start_index=True,
)

documents = splitter.create_documents([text], metadatas=[{"source": "runbook"}])

for index, doc in enumerate(documents, start=1):
    print(f"chunk {index}")
    print(doc.metadata)
    print(doc.page_content)
    print("-" * 40)
```

이 예시를 직접 돌려 보면 overlap이 항상 정확히 20문자가 아니라, 줄 단위 조각을 얼마나 오래 유지했는지에 따라 바뀌는 것을 확인할 수 있습니다.

---

## 3. `RecursiveCharacterTextSplitter`가 기본 선택이 된 이유

`RecursiveCharacterTextSplitter`가 널리 쓰이는 이유는 정교해서가 아니라, 실패 방식이 비교적 온건하기 때문입니다. 기본 `separators`는 `["\n\n", "\n", " ", ""]`입니다. 문단, 줄, 공백, 마지막으로 문자 단위까지 단계적으로 후퇴합니다.

![재귀 분할의 구분자 우선순위 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/01/01-03-recursive-separator-fallback.ko.png)

*재귀 분할의 구분자 우선순위 흐름*

핵심 메서드인 `_split_text()`는 현재 텍스트에 실제로 등장하는 첫 번째 separator를 찾아 분할하고, 조각이 `chunk_size`보다 작으면 병합 목록에 모아 확정합니다. 아직도 큰 조각이 남으면 남은 separator로 재귀 호출합니다. 이 구현은 "문단 경계가 있으면 최대한 문단을 살리고, 그게 안 될 때만 줄 단위로 내려간다"는 보수적 전략을 구현합니다.

또 `keep_separator=True`가 기본값이라는 사실도 중요합니다. 구분자를 보존하는 쪽이 기본이므로 제목과 본문 사이의 문맥 신호가 덜 사라집니다.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

markdown_text = """# Service policy

## Password reset
Users can reset passwords from the account settings page.
The reset link expires after 15 minutes.

## API rate limit
The public API allows 120 requests per minute per API key.
Burst requests above the limit receive HTTP 429 responses.
"""

splitter = RecursiveCharacterTextSplitter(
    chunk_size=120,
    chunk_overlap=30,
)

chunks = splitter.split_text(markdown_text)

for index, chunk in enumerate(chunks, start=1):
    print(f"chunk {index}\n{chunk}\n")
```

---

## 4. 토큰 기준 분할이 필요한 순간

문자 수와 토큰 수는 다릅니다. LLM의 컨텍스트 윈도는 토큰 기준인데, 많은 파이프라인은 여전히 문자 기준 splitter로 ingest를 끝냅니다. 그러면 인덱싱 때는 멀쩡해 보여도, 검색 후 여러 chunk를 프롬프트에 조립하는 단계에서 토큰 예산이 갑자기 넘칩니다.

![문자 수와 토큰 수의 어긋남 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/01/01-04-token-aware-splitting.ko.png)

*문자 수와 토큰 수의 어긋남 흐름*

`TokenTextSplitter`는 내부에서 문자열을 토큰 ID 리스트로 바꾼 뒤 고정 폭 슬라이딩 윈도를 이동합니다. overlap이 조각 단위가 아니라 토큰 단위로 직접 적용되므로 예측 가능성이 높습니다.

```python
import tiktoken
from langchain_text_splitters import CharacterTextSplitter, TokenTextSplitter

text = "고객 ID 18423의 결제 실패 원인은 HTTP 429 응답이 아니라, 백오프 없이 재시도한 내부 배치 작업이었습니다."

encoding = tiktoken.get_encoding("cl100k_base")

char_splitter = CharacterTextSplitter(
    separator=" ",
    chunk_size=30,
    chunk_overlap=5,
)
token_splitter = TokenTextSplitter(
    encoding_name="cl100k_base",
    chunk_size=18,
    chunk_overlap=4,
)

char_chunks = char_splitter.split_text(text)
token_chunks = token_splitter.split_text(text)

print("character-based")
for chunk in char_chunks:
    print(len(chunk), len(encoding.encode(chunk)), chunk)

print("token-based")
for chunk in token_chunks:
    print(len(chunk), len(encoding.encode(chunk)), chunk)
```

한국어, 숫자, 영문 식별자, 구두점이 섞인 운영 로그나 에러 리포트에서는 이 차이가 더 벌어집니다. 문자 500자면 충분할 거라고 가정했는데 토큰 900개가 나오는 식입니다. `top_k=6`을 유지하고 싶다면 ingest 단계의 chunk 크기부터 토큰 예산과 맞춰야 합니다.

---

## 5. 실무에서는 chunk 크기를 어떻게 고를까

정답 숫자는 없습니다. 대신 틀린 접근은 분명합니다. 문서 종류가 다른데도 모든 코퍼스에 `chunk_size=1000, chunk_overlap=200`을 일괄 적용하는 방식입니다.

![청크 품질 측정과 조정 순환 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-deep-dive/01/01-05-chunk-quality-feedback-loop.ko.png)

*청크 품질 측정과 조정 순환 흐름*

실무에서는 보통 세 축을 같이 봅니다. 첫째, 한 chunk가 답변 근거로 자급자족할 수 있는가. 둘째, retriever가 너무 넓은 chunk 때문에 비슷한 주제를 모두 같은 벡터로 뭉개지 않는가. 셋째, overlap이 실제로 문맥 보존에 기여하는가입니다.

```python
from statistics import mean

import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter


def measure_chunks(texts):
    chunk_size = 700
    chunk_overlap = 120
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )
    encoding = tiktoken.get_encoding("cl100k_base")

    chunks = []
    for text in texts:
        chunks.extend(splitter.split_text(text))

    token_lengths = [len(encoding.encode(chunk)) for chunk in chunks]
    overlap_ratio = chunk_overlap / chunk_size

    print(f"chunks: {len(chunks)}")
    print(f"configured overlap ratio: {overlap_ratio:.2f}")
    print(f"avg tokens per chunk: {mean(token_lengths):.1f}")
    print(f"max tokens per chunk: {max(token_lengths)}")
    print(f"min tokens per chunk: {min(token_lengths)}")


if __name__ == "__main__":
    documents = [
        "Service owners must rotate secrets every 90 days. Emergency exceptions require security approval.",
        "API clients that exceed the quota receive HTTP 429 and should retry with exponential backoff.",
    ]
    measure_chunks(documents)
```

---

## 자주 하는 실수

| 실수 | 이유 | 올바른 접근 |
|------|------|------------|
| 모든 문서에 동일한 `chunk_size=1000, chunk_overlap=200` 일괄 적용 | 문서 종류마다 의미 단위가 달라 정책이 맞지 않음 | 문서 유형별로 chunk 크기를 별도로 설계하고, 샘플 질문 세트로 검증 |
| `chunk_overlap`이 설정값과 정확히 같을 것으로 기대 | LangChain은 조각 단위로 병합하므로 실제 overlap은 구분자 구조에 따라 달라짐 | 실제 청크 출력을 찍어 인접 청크 간 중복 토큰 비율을 직접 측정 |
| 문자 수 기준으로 chunk를 설계하고 토큰 한도는 나중에 확인 | 한국어+영문+코드가 혼합된 텍스트에서 문자 수와 토큰 수 차이가 크게 벌어짐 | `TokenTextSplitter`로 토큰 기준 상한을 먼저 잡고, 구조 보존은 재귀 분할로 처리 |
| 로더가 만든 문서 경계를 확인하지 않고 splitter만 튜닝 | 로더가 페이지별 분리를 이미 고정했다면 splitter 조정은 효과가 제한됨 | splitter 변경 전 로더 출력의 `page_content` 경계와 `metadata`를 먼저 출력해 확인 |
| retrieval 실패를 retriever 탓으로 먼저 귀결 | 답이 청크 경계에서 잘렸다면 retriever는 이미 왜곡된 데이터를 성실히 검색할 뿐 | 로더 경계 확인 → 청크 출력 확인 → 토큰 길이 측정 순서로 앞단부터 진단 |

## 정리

RAG 파이프라인의 앞단은 생각보다 단순한 코드로 이루어져 있습니다. `TextLoader`는 파일 경로를 `source`에 담아 한 개 문서를 만들고, `PDFMinerLoader`는 페이지 결합 여부에 따라 문서 경계를 바꿉니다. 그 위에서 `CharacterTextSplitter`와 `RecursiveCharacterTextSplitter`는 먼저 자르고 나중에 병합하는 방식으로 chunk를 만들고, `TokenTextSplitter`는 모델 토큰 기준으로 그 창을 다시 정의합니다.

이 기준선을 잡아 두면 다음 화의 임베딩과 인덱스 논의가 훨씬 선명해집니다. 벡터 인덱스는 결코 중립적인 저장소가 아닙니다. 로더와 splitter가 만든 문서 단위를 그대로 기하학으로 바꾸는 장치입니다. 2화에서는 그 기하학이 실제로 어떻게 검색 동작으로 이어지는지, FAISS의 `IndexFlatL2`를 기준으로 이어서 보겠습니다.

## 처음 질문으로 돌아가기

- **유사도 검색이 시작되기 전, 로더와 splitter 경계는 왜 검색 품질을 좌우할까요?**
  - retriever는 벡터 인덱스에 저장된 청크 중에서 가장 가까운 것을 찾습니다. 그 청크가 이미 의미 경계에서 잘못 잘려 있다면, retriever가 아무리 잘 작동해도 답변에 필요한 문맥이 없는 청크를 가져옵니다. 로더가 무엇을 `Document`로 만들었는지, splitter가 그것을 어떤 경계에서 다시 나눴는지가 벡터 인덱스의 내용을 결정합니다.

- **Character, Recursive, Token splitter는 같은 텍스트를 어떻게 다르게 자를까요?**
  - `CharacterTextSplitter`는 지정한 구분자(예: `\n\n`)로 먼저 나누고 크기 한도에서 병합합니다. `RecursiveCharacterTextSplitter`는 `["\n\n", "\n", " ", ""]` 순서로 단계적으로 후퇴하며 상위 구조를 가능한 한 보존합니다. `TokenTextSplitter`는 문자 단위가 아니라 모델 토큰 단위로 고정 폭 슬라이딩 윈도를 만들어 컨텍스트 예산 기준으로 더 예측 가능한 청크를 생성합니다.

- **`chunk_overlap`이 설정값만큼 정확히 겹치지 않는 것처럼 보일 때 어디를 봐야 할까요?**
  - LangChain의 `_merge_splits()`는 조각 단위로 슬라이딩 윈도를 이동합니다. 겹침이 정확한 문자 수가 아니라 조각 경계 단위로 결정되기 때문에, 실제 overlap 길이는 구분자 구조와 조각 크기에 따라 들쭉날쭉합니다. 인접 청크 간 중복 토큰 비율을 직접 측정해 설정 의도와 실제 결과가 얼마나 다른지 확인해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- **RAG Deep Dive (1/6): 문서 로딩과 청크 전략 — LangChain TextSplitter 내부 (현재 글)**
- [RAG Deep Dive (2/6): 임베딩과 벡터 인덱스 — FAISS IndexFlatL2 동작 원리](./02-embeddings-and-vector-index.md)
- [RAG Deep Dive (3/6): Retriever 설계 — VectorStoreRetriever와 MMR](./03-retriever-design.md)
- [RAG Deep Dive (4/6): 프롬프트 구성과 컨텍스트 주입 — PromptTemplate 내부](./04-prompt-construction-and-context-injection.md)
- [RAG Deep Dive (5/6): RAG Chain 조립 — RetrievalQA vs LCEL](./05-rag-chain-assembly.md)
- [RAG Deep Dive (6/6): 평가와 품질 게이트 — RAGAS 메트릭과 Faithfulness](./06-evaluation-and-quality-gates.md)

<!-- toc:end -->

---

## 참고 자료

- [LangChain `TextSplitter` base source](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/text-splitters/langchain_text_splitters/base.py)
- [LangChain `CharacterTextSplitter` and `RecursiveCharacterTextSplitter` source](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/text-splitters/langchain_text_splitters/character.py)
- [LangChain `TextLoader` source](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/community/langchain_community/document_loaders/text.py)
- [LangChain PDF loader source](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/community/langchain_community/document_loaders/pdf.py)
- [LangChain `Document` base type](https://github.com/langchain-ai/langchain/blob/langchain==0.2.17/libs/core/langchain_core/documents/base.py)
- [Lewis et al., Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks](https://doi.org/10.48550/arXiv.2005.11401)

### 관련 시리즈

- [Vector Search 101](../../vector-search-101/ko/01-what-is-embedding.md) — RAG가 검색 결과를 그대로 받아 쓰는 그 "벡터 검색"을 직접 다룹니다. ANN 인덱스(FAISS, HNSW)나 임베딩 모델 선택 때문에 검색 품질이 흔들리면 이 시리즈로 한 단계 내려가 디버깅하기를 권장합니다.

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/rag-deep-dive/ko)

Tags: RAG, LangChain, Vector Search, LLM
