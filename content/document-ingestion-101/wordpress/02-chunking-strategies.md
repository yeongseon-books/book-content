---
title: "바이브코딩을 위한 문서 수집 파이프라인 (2/6): 청킹 전략 — 문서 유형별 최적화"
series: document-ingestion-101
episode: 2
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG
- Chunking
- LangChain
- Python
---

# 바이브코딩을 위한 문서 수집 파이프라인 (2/6): 청킹 전략 — 문서 유형별 최적화

이 글은 **바이브코딩을 위한 문서 수집 파이프라인** 시리즈의 두 번째 글입니다. 파싱된 텍스트를 어떻게 쪼개야 검색이 잘 되는지, 문서 유형별 청킹 전략을 다룹니다.

---

PDF 파싱에 성공했습니다. 텍스트가 나옵니다. 이제 청킹을 해야 합니다. "500자씩 자르면 되지 않나요?"라고 생각했다가, 실제 검색 결과를 보면 절반이 맥락이 잘린 조각입니다. FAQ 문서에서 질문과 답변이 다른 청크로 나뉘거나, 정책 문서에서 한 조항이 두 개로 쪼개져 각각 다른 의미를 갖게 됩니다.

바이브코딩으로 AI에게 "청킹 코드 만들어줘"라고 하면 `RecursiveCharacterTextSplitter(chunk_size=500)`을 줍니다. 그게 시작점이지 끝점이 아닙니다. 문서 유형에 맞는 청킹 전략이 없으면, 좋은 파서 위에 나쁜 청크가 쌓입니다.

이 글에서는 문서 유형별 청킹 프리셋을 설계하고, 청크 품질을 검토하는 방법을 코드와 함께 설명합니다.

> "청크 경계가 의미 경계와 일치할 때 검색 정확도가 올라갑니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. `chunk_size`와 `chunk_overlap`의 적절한 비율을 알고 있나요?
2. FAQ 문서와 기술 매뉴얼에 다른 청킹 전략이 필요한 이유를 설명할 수 있나요?
3. `RecursiveCharacterTextSplitter`의 구분자 우선순위가 어떻게 작동하는지 아나요?
4. 청크 품질을 측정하는 지표가 있나요?
5. 너무 짧은 청크와 너무 긴 청크가 각각 어떤 문제를 만드나요?

---

## RecursiveCharacterTextSplitter 기본

LangChain의 `RecursiveCharacterTextSplitter`는 구분자 우선순위를 지정할 수 있어 유연합니다.

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", "。", ".", " ", ""],
)
```

구분자는 왼쪽부터 시도하고, 너무 크면 다음 구분자로 이동합니다.

## 문서 유형별 프리셋

문서 유형에 따라 최적 청킹 파라미터가 다릅니다.

```python
CHUNKING_PRESETS = {
    "faq": {
        "chunk_size": 300,
        "chunk_overlap": 0,
        "separators": ["\n\n## ", "\n\n", "\n"],
    },
    "manual": {
        "chunk_size": 800,
        "chunk_overlap": 100,
        "separators": ["\n## ", "\n### ", "\n\n", "\n"],
    },
    "policy": {
        "chunk_size": 600,
        "chunk_overlap": 80,
        "separators": ["\n제", "\n조", "\n\n", "\n"],
    },
}

def get_splitter(doc_type: str) -> RecursiveCharacterTextSplitter:
    preset = CHUNKING_PRESETS.get(doc_type, CHUNKING_PRESETS["manual"])
    return RecursiveCharacterTextSplitter(**preset)
```

## 청크 품질 검토

청크를 만들고 품질을 측정하세요.

```python
def review_chunks(chunks: list[str]) -> dict:
    lengths = [len(c) for c in chunks]
    too_short = sum(1 for l in lengths if l < 50)
    too_long = sum(1 for l in lengths if l > 1000)
    return {
        "total": len(chunks),
        "avg_length": sum(lengths) / len(lengths) if lengths else 0,
        "too_short": too_short,
        "too_long": too_long,
        "passed": too_short == 0 and too_long == 0,
    }
```

`too_short`가 많으면 `chunk_size`를 늘리거나 구분자를 조정합니다.

---

## Before / After

| 항목 | Before (고정 500자) | After (유형별 프리셋) |
|------|--------------------|--------------------|
| FAQ 문서 | Q·A가 다른 청크로 분리 | Q·A가 한 청크로 유지 |
| 정책 문서 | 조항 중간에서 절단 | 조항 경계에서 분리 |
| 기술 매뉴얼 | 코드 블록 파괴 | 코드 블록 보존 |
| 품질 검토 | 없음 | 자동 측정 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 모든 문서에 동일 청크 크기 | 유형별 맥락 손실 | 문서 유형 감지 후 프리셋 적용 |
| overlap 없음 | 경계 맥락 손실 | 10~15% overlap 설정 |
| 빈 청크 통과 | 노이즈 적재 | 최소 길이 필터 |
| 코드 블록 무시 | 코드 파괴 | ` ``` ` 구분자 우선 처리 |

---

## AI 활용 팁

```
문서 유형(faq/manual/policy)을 파라미터로 받아 적합한 청킹 프리셋을 적용하는 함수를 만들어줘.
각 청크에 {doc_type, chunk_index, char_count} 메타데이터를 붙여줘.
품질 검토 함수도 포함해서 too_short/too_long 청크 개수를 반환해줘.
```

---

## 체크리스트

- [ ] 문서 유형별 청킹 프리셋 정의
- [ ] `RecursiveCharacterTextSplitter`에 한국어 구분자 추가
- [ ] 청크 품질 검토 함수 구현
- [ ] 너무 짧은 청크(< 50자) 필터
- [ ] 청크에 메타데이터(유형, 인덱스) 포함

---

## 처음 질문으로 돌아가기

"500자씩 자르면 되지 않나요?" — 문서 유형이 하나라면 그럴 수 있습니다. 하지만 FAQ, 매뉴얼, 정책 문서가 섞이는 순간 단일 크기 청킹은 맥락을 파괴합니다. 유형별 프리셋과 품질 검토가 있어야 청킹이 검색 품질의 기초가 됩니다.

---

## 정리

- 문서 유형(FAQ/매뉴얼/정책)에 따라 청킹 파라미터를 다르게 설정한다
- `RecursiveCharacterTextSplitter`의 구분자 우선순위로 의미 경계를 보존한다
- 청크 품질(너무 짧음/너무 긴 청크)을 자동으로 측정한다
- 청크에 문서 유형과 인덱스 메타데이터를 포함시킨다

---

## 참고 자료

- [LangChain TextSplitter 문서](https://python.langchain.com/docs/modules/data_connection/document_transformers/)
- [RecursiveCharacterTextSplitter API](https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- RecursiveCharacterTextSplitter 기본
- 문서 유형별 프리셋
- 청크 품질 검토
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, RAG, Chunking, LangChain, Python
