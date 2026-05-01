---
title: '청킹 전략 — 문서 유형별 최적화'
series: document-ingestion-101
episode: 2
language: ko
status: draft
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

> 문서 수집과 인덱싱 101 시리즈 (2/6)

예제 코드: [github.com/yeongseon-books/document-ingestion-101](https://github.com/yeongseon-books/document-ingestion-101/tree/main/ko/02-chunking-strategies)

청킹은 문서를 임베딩 가능한 작은 단위로 나누는 과정입니다. 청크 크기가 너무 크면 검색된 청크가 관련 없는 내용을 많이 포함합니다. 너무 작으면 맥락 정보가 부족해서 LLM이 좋은 답변을 생성하지 못합니다. 최적의 청크 크기는 문서 유형에 따라 다릅니다.

다룰 내용은 다음과 같습니다.

- 고정 크기 청킹과 의미 단위 청킹
- RecursiveCharacterTextSplitter 심화
- 문서 유형별 청킹 파라미터
- 청크 품질 평가 방법

---

<!-- ebook-only:start -->

이 장의 핵심: **청킹 전략은 문서 유형에 따라 달라진다.** 연속된 산문·섹션 구조·테이블·코드는 각각 다른 분할 기준이 필요하다.

## 이 장의 위치

이 글은 시리즈 6편 중 2번째 장입니다.
앞 장에서는 **PDF 파싱과 텍스트 추출**을 다뤘습니다.
이 장을 마치면 다음 장에서 **메타데이터 설계와 필터링**으로 이어집니다.
<!-- ebook-only:end -->

## 고정 크기 vs 의미 단위 청킹

**고정 크기 청킹**: 지정한 글자 수마다 자릅니다. 빠르고 예측 가능하지만, 문장이나 단락 중간에서 잘릴 수 있습니다.

**의미 단위 청킹**: 문단, 문장, 헤딩 같은 자연스러운 경계에서 자릅니다. 더 나은 맥락을 보존하지만 청크 크기가 불균일합니다.

LangChain의 `RecursiveCharacterTextSplitter`는 두 방식의 절충안입니다. 지정한 구분자 목록을 순서대로 시도하면서 청크 크기 목표에 맞게 자릅니다.

---

## RecursiveCharacterTextSplitter 심화

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

def analyze_chunks(text: str, chunk_size: int, chunk_overlap: int, separators: list[str]) -> dict:
    """청킹 파라미터별 통계를 반환합니다."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
    )
    chunks = splitter.split_text(text)

    sizes = [len(c) for c in chunks]
    return {
        "chunk_count": len(chunks),
        "avg_size": sum(sizes) / len(sizes) if sizes else 0,
        "min_size": min(sizes) if sizes else 0,
        "max_size": max(sizes) if sizes else 0,
        "chunks": chunks,
    }

# 샘플 기술 문서
tech_doc = """
# 파이썬 비동기 프로그래밍

## asyncio 소개

asyncio는 파이썬 표준 라이브러리의 비동기 I/O 프레임워크입니다.
단일 스레드에서 여러 I/O 작업을 동시에 처리할 수 있도록 합니다.
CPU 작업이 아닌 네트워크 요청, 파일 읽기 같은 I/O 대기 시간을 활용합니다.

## 핵심 개념

코루틴(Coroutine)은 async def로 정의하는 특수 함수입니다.
await 키워드로 다른 코루틴의 완료를 기다립니다.
이벤트 루프(Event Loop)가 코루틴의 실행을 관리합니다.

## 기본 패턴

단순한 비동기 함수:

```python
import asyncio

async def fetch_data(url: str) -> str:
    await asyncio.sleep(1)  # 실제로는 HTTP 요청
    return f"데이터: {url}"

async def main():
    result = await fetch_data("https://example.com")
    print(result)

asyncio.run(main())
```

## 병렬 실행

asyncio.gather()로 여러 코루틴을 동시에 실행합니다.
순차 실행에 비해 실행 시간이 크게 줄어듭니다.
"""

# 세 가지 청킹 설정 비교
configs = [
    {"chunk_size": 100, "chunk_overlap": 20, "desc": "소형 (100자)"},
    {"chunk_size": 300, "chunk_overlap": 50, "desc": "중형 (300자)"},
    {"chunk_size": 600, "chunk_overlap": 100, "desc": "대형 (600자)"},
]

for config in configs:
    stats = analyze_chunks(
        text=tech_doc,
        chunk_size=config["chunk_size"],
        chunk_overlap=config["chunk_overlap"],
        separators=["\n\n", "\n", "。", ". ", " "],
    )
    print(f"\n{config['desc']}:")
    print(f"  청크 수: {stats['chunk_count']}")
    print(f"  평균 크기: {stats['avg_size']:.0f}자")
    print(f"  범위: {stats['min_size']}~{stats['max_size']}자")
```

---

## 문서 유형별 최적 파라미터

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

CHUNKING_PRESETS = {
    "legal": {
        # 법령: 조항 단위 보존 중요
        "chunk_size": 800,
        "chunk_overlap": 150,
        "separators": ["\n\n", "\n", "。", ". "],
        "reason": "조항 번호와 내용이 분리되지 않도록 크게 설정",
    },
    "news": {
        # 뉴스: 짧고 자기완결적인 단락
        "chunk_size": 300,
        "chunk_overlap": 30,
        "separators": ["\n\n", "\n", ". "],
        "reason": "뉴스 단락은 보통 200~400자로 자기완결적",
    },
    "technical": {
        # 기술 문서: 코드 블록 경계 보존
        "chunk_size": 500,
        "chunk_overlap": 100,
        "separators": ["\n\n", "\n", "```", ". ", " "],
        "reason": "코드 블록이 청크 중간에 잘리지 않도록",
    },
    "academic": {
        # 논문: 섹션 단위 보존
        "chunk_size": 600,
        "chunk_overlap": 120,
        "separators": ["\n\n\n", "\n\n", "\n", ". "],
        "reason": "논문 섹션과 단락 구조 보존",
    },
    "faq": {
        # FAQ: Q&A 쌍이 분리되지 않도록
        "chunk_size": 400,
        "chunk_overlap": 0,    # FAQ는 overlap이 오히려 해가 됨
        "separators": ["\n\n", "Q:", "A:"],
        "reason": "질문과 답변이 같은 청크에 있도록",
    },
}

def get_splitter(doc_type: str) -> RecursiveCharacterTextSplitter:
    """문서 유형에 맞는 RecursiveCharacterTextSplitter를 반환합니다."""
    preset = CHUNKING_PRESETS.get(doc_type, CHUNKING_PRESETS["technical"])
    return RecursiveCharacterTextSplitter(
        chunk_size=preset["chunk_size"],
        chunk_overlap=preset["chunk_overlap"],
        separators=preset["separators"],
    )

# 법령 문서 예시
legal_text = """
제1조 (목적)
이 법은 개인정보의 처리 및 보호에 관한 사항을 정함으로써 개인의 자유와 권리를 보호하고, 나아가 개인의 존엄과 가치를 구현함을 목적으로 한다.

제2조 (정의)
이 법에서 사용하는 용어의 뜻은 다음과 같다.
1. "개인정보"란 살아 있는 개인에 관한 정보로서 성명, 주민등록번호 및 영상 등을 통하여 개인을 알아볼 수 있는 정보를 말한다.
2. "처리"란 개인정보의 수집, 생성, 연계, 연동, 기록, 저장, 보유, 가공, 편집, 검색, 출력, 정정, 복구, 이용, 제공, 공개, 파기, 그 밖에 이와 유사한 행위를 말한다.

제3조 (개인정보 보호 원칙)
개인정보처리자는 개인정보의 처리 목적을 명확하게 하여야 하고 그 목적에 필요한 범위에서 최소한의 개인정보만을 적법하고 정당하게 수집하여야 한다.
"""

legal_splitter = get_splitter("legal")
legal_chunks = legal_splitter.split_text(legal_text)
print(f"법령 문서 청크 수: {len(legal_chunks)}")
for i, chunk in enumerate(legal_chunks, start=1):
    print(f"  [{i}] {chunk[:80]}...")
```

---

## 헤딩 기반 청킹

마크다운 문서처럼 헤딩 구조가 있는 경우, 헤딩 경계에서 자르면 맥락이 더 잘 보존됩니다.

```python
import re
from dataclasses import dataclass

@dataclass
class Section:
    heading: str
    level: int
    content: str

def split_by_headings(markdown_text: str) -> list[Section]:
    """마크다운 헤딩을 기준으로 섹션을 분리합니다."""
    pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
    matches = list(pattern.finditer(markdown_text))

    sections = []
    for i, match in enumerate(matches):
        level = len(match.group(1))
        heading = match.group(2)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown_text)
        content = markdown_text[start:end].strip()

        if content:
            sections.append(Section(heading=heading, level=level, content=content))

    return sections

def heading_aware_chunks(
    markdown_text: str,
    max_chunk_size: int = 500,
) -> list[dict]:
    """헤딩 구조를 보존하면서 청킹합니다."""
    sections = split_by_headings(markdown_text)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=max_chunk_size,
        chunk_overlap=50,
        separators=["\n\n", "\n", ". "],
    )

    chunks = []
    for section in sections:
        # 섹션이 청크 크기보다 크면 추가 분할
        if len(section.content) > max_chunk_size:
            sub_chunks = splitter.split_text(section.content)
            for sub in sub_chunks:
                chunks.append({
                    "heading": section.heading,
                    "level": section.level,
                    "text": sub,
                })
        else:
            chunks.append({
                "heading": section.heading,
                "level": section.level,
                "text": section.content,
            })

    return chunks

sample_md = """
# 클라우드 아키텍처 설계 원칙

## 확장성

수평 확장(Scale-out)을 기본으로 설계합니다.
상태는 외부 저장소(Redis, DB)에 보관하고 서버는 무상태(stateless)로 유지합니다.
로드 밸런서로 트래픽을 여러 인스턴스에 분산합니다.

## 고가용성

단일 장애점(SPOF)을 제거합니다.
여러 가용 영역(AZ)에 걸쳐 배포합니다.
헬스체크와 자동 장애 복구를 구성합니다.

## 보안

최소 권한 원칙을 적용합니다.
전송 중과 저장 중 데이터를 암호화합니다.
접근 로그를 기록하고 이상 징후를 모니터링합니다.
"""

heading_chunks = heading_aware_chunks(sample_md)
print(f"헤딩 기반 청크 수: {len(heading_chunks)}")
for chunk in heading_chunks:
    print(f"\n  [H{chunk['level']}: {chunk['heading']}]")
    print(f"  {chunk['text'][:100]}...")
```

---

## 마무리

문서 유형을 먼저 파악하고 그에 맞는 청킹 전략을 선택하는 것이 검색 품질의 기반입니다. 법령이나 FAQ처럼 구조가 중요한 문서는 그 구조를 보존하는 방식으로 청킹하세요. 다음 글에서는 청크에 메타데이터를 붙이고 이를 필터링에 활용하는 방법을 다룹니다.

<!-- blog-only:start -->
다음 글: [메타데이터 설계와 필터링](./03-metadata-filtering.md)
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

---

## 참고 자료

- [LangChain TextSplitter](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [청킹 전략 비교 (Pinecone)](https://www.pinecone.io/learn/chunking-strategies/)
- [RecursiveCharacterTextSplitter 가이드](https://python.langchain.com/docs/modules/data_connection/document_transformers/recursive_text_splitter/)

Tags: RAG, Document Processing, LangChain, Python
