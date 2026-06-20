---
title: "바이브코딩을 위한 문서 수집 파이프라인 (3/6): 메타데이터 설계와 필터링"
series: document-ingestion-101
episode: 3
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG
- Metadata
- FAISS
- Python
---

# 바이브코딩을 위한 문서 수집 파이프라인 (3/6): 메타데이터 설계와 필터링

이 글은 **바이브코딩을 위한 문서 수집 파이프라인** 시리즈의 세 번째 글입니다. 청크에 메타데이터를 붙이고 검색 시 필터링하는 방법을 다룹니다.

---

청킹까지 완료했습니다. 이제 FAISS에 넣으면 검색이 됩니다. 그런데 "2024년 이후 정책 문서만 검색해줘", "인사팀 문서에서만 찾아줘"라는 요청이 오면 어떻게 하나요? 벡터 유사도만으로는 불가능합니다. 메타데이터 없이 벡터만 저장하면, 검색 결과에 2019년 폐기된 정책이 섞여 나옵니다.

바이브코딩으로 AI에게 "FAISS로 문서 검색 만들어줘"라고 하면, 메타데이터 없이 임베딩만 저장하는 코드가 나옵니다. 그 코드는 동작하지만 필터링이 불가능합니다.

이 글에서는 청크에 붙일 메타데이터 스키마를 설계하고, FAISS 기반 필터링을 구현하는 방법을 다룹니다.

> "메타데이터는 검색 정밀도를 높이는 두 번째 필터입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. FAISS에서 메타데이터 필터링이 가능한가요?
2. 청크에 어떤 메타데이터를 붙여야 하는지 기준이 있나요?
3. 복합 필터(AND/OR)를 어떻게 구현하나요?
4. 접근 제어를 메타데이터로 구현할 수 있나요?
5. 메타데이터 스키마 변경 시 기존 인덱스를 어떻게 처리하나요?

---

## 메타데이터 스키마 설계

```python
from dataclasses import dataclass
from datetime import date

@dataclass
class ChunkMetadata:
    source_file: str
    doc_type: str          # faq | manual | policy
    department: str        # hr | legal | engineering
    created_date: date
    access_level: str      # public | internal | confidential
    chunk_index: int
    page_num: int
```

메타데이터는 처음부터 스키마를 고정해야 합니다. 나중에 필드를 추가하면 기존 인덱스와 호환이 깨집니다.

## FAISS + 메타데이터 저장

FAISS는 메타데이터를 직접 저장하지 않으므로 별도로 관리합니다.

```python
import faiss
import numpy as np
import json

class MetadataFAISS:
    def __init__(self, dim: int):
        self.index = faiss.IndexFlatL2(dim)
        self.metadata_store: list[dict] = []

    def add(self, vectors: np.ndarray, metadata_list: list[dict]):
        self.index.add(vectors)
        self.metadata_store.extend(metadata_list)

    def search_with_filter(
        self, query_vector: np.ndarray, k: int, filters: dict
    ) -> list[dict]:
        # 넉넉하게 검색 후 필터링
        D, I = self.index.search(query_vector, k * 10)
        results = []
        for idx in I[0]:
            if idx == -1:
                continue
            meta = self.metadata_store[idx]
            if self._match(meta, filters):
                results.append(meta)
            if len(results) >= k:
                break
        return results

    def _match(self, meta: dict, filters: dict) -> bool:
        for key, value in filters.items():
            if meta.get(key) != value:
                return False
        return True
```

## 복합 필터

```python
def compound_filter(meta: dict, conditions: list[dict], operator: str = "AND") -> bool:
    matches = [meta.get(c["field"]) == c["value"] for c in conditions]
    if operator == "AND":
        return all(matches)
    elif operator == "OR":
        return any(matches)
    return False
```

---

## Before / After

| 항목 | Before (메타데이터 없음) | After (메타데이터 필터링) |
|------|------------------------|------------------------|
| 연도 필터 | 불가 | `year >= 2024` 적용 |
| 부서 필터 | 불가 | `department = hr` 적용 |
| 접근 제어 | 없음 | `access_level` 기반 차단 |
| 검색 정밀도 | 낮음(폐기 문서 포함) | 높음(유효 문서만) |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 메타데이터 스키마 미정의 | 필드 불일치 | 초기에 dataclass 고정 |
| FAISS에 메타데이터 포함 기대 | 런타임 오류 | 별도 메타데이터 스토어 관리 |
| 날짜를 문자열로 저장 | 범위 필터 불가 | ISO 날짜 형식 또는 timestamp |
| 접근 제어 없음 | 기밀 문서 노출 | access_level 필드 필수화 |

---

## AI 활용 팁

```
ChunkMetadata dataclass를 정의하고, FAISS 인덱스와 별도 메타데이터 스토어를 함께 관리하는 클래스를 만들어줘.
검색 시 department, doc_type, access_level 필터를 AND 조건으로 적용할 수 있어야 해.
```

---

## 체크리스트

- [ ] ChunkMetadata 스키마 dataclass로 정의
- [ ] FAISS + 별도 메타데이터 스토어 연동
- [ ] 단일 필터 검색 구현
- [ ] 복합 필터(AND/OR) 구현
- [ ] access_level 기반 접근 제어 구현
- [ ] 날짜 필드를 비교 가능한 형식으로 저장

---

## 처음 질문으로 돌아가기

"FAISS에 넣으면 검색이 되는 거 아닌가요?" — 벡터 유사도 검색은 됩니다. 하지만 "올해 문서만", "인사팀 문서만" 같은 필터는 메타데이터 없이 불가능합니다. 메타데이터 스키마와 필터링 구조가 있어야 RAG가 실용적인 검색 시스템이 됩니다.

---

## 정리

- 메타데이터 스키마는 초기에 dataclass로 고정한다
- FAISS는 메타데이터를 저장하지 않으므로 별도 스토어를 함께 관리한다
- 검색 후 필터링(post-filter) 방식으로 복합 조건을 처리한다
- access_level 필드로 접근 제어를 구현한다

---

## 참고 자료

- [FAISS 공식 문서](https://faiss.ai/)
- [LangChain Vectorstore 메타데이터 필터링](https://python.langchain.com/docs/modules/data_connection/vectorstores/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 메타데이터 스키마 설계
- FAISS + 메타데이터 저장
- 복합 필터
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, RAG, Metadata, FAISS, Python
