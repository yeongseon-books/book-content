---
title: "바이브코딩을 위한 문서 수집 파이프라인 (6/6): 문서 수집 파이프라인 완성"
series: document-ingestion-101
episode: 6
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG
- Pipeline
- FAISS
- Python
---

# 바이브코딩을 위한 문서 수집 파이프라인 (6/6): 문서 수집 파이프라인 완성

이 글은 **바이브코딩을 위한 문서 수집 파이프라인** 시리즈의 마지막 글입니다. 파싱·청킹·메타데이터·증분 인덱싱·다중 포맷을 하나의 엔드투엔드 파이프라인으로 연결합니다.

---

파싱, 청킹, 메타데이터, 증분 인덱싱, 다중 포맷 — 각 단계를 개별적으로 만들었습니다. 이제 연결해야 합니다. "그냥 순서대로 실행하면 되지 않나요?"라고 생각하면, 한 단계가 실패했을 때 전체가 멈추거나, 실패한 단계만 재실행할 방법이 없다는 걸 발견합니다.

바이브코딩으로 AI에게 "파이프라인 연결해줘"라고 하면, 순차 실행 스크립트를 줍니다. 그건 시작점입니다. 스테이지 오케스트레이션, 스모크 쿼리, FAISS 저장·로드까지 갖춰야 실제로 운영할 수 있는 파이프라인입니다.

이 글에서는 지금까지 만든 모든 컴포넌트를 통합하고, 파이프라인을 검증하는 방법을 다룹니다.

> "파이프라인은 실행이 되는 것이 아니라 검증이 되는 것입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 파이프라인 스테이지가 실패했을 때 어떻게 처리하나요?
2. FAISS 인덱스를 디스크에 저장하고 로드하는 방법을 알고 있나요?
3. 파이프라인이 올바르게 작동하는지 검증하는 스모크 쿼리를 어떻게 설계하나요?
4. 각 스테이지의 실행 결과를 어떻게 추적하나요?
5. 파이프라인 재실행 시 이미 처리된 파일을 건너뛰는 방법이 있나요?

---

## 파이프라인 스테이지 오케스트레이터

```python
from dataclasses import dataclass, field
from typing import Callable

@dataclass
class StageResult:
    stage: str
    success: bool
    processed: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)

def run_pipeline(doc_dir: str, stages: list[tuple[str, Callable]]) -> list[StageResult]:
    results = []
    context = {"doc_dir": doc_dir, "documents": []}

    for stage_name, stage_fn in stages:
        try:
            stage_result = stage_fn(context)
            results.append(StageResult(
                stage=stage_name,
                success=True,
                processed=stage_result.get("processed", 0),
            ))
        except Exception as e:
            results.append(StageResult(
                stage=stage_name,
                success=False,
                errors=[str(e)],
            ))
            break  # 이전 스테이지 실패 시 중단

    return results
```

## FAISS 저장·로드

```python
import faiss
import pickle
from pathlib import Path

def save_index(index: faiss.Index, metadata: list, output_dir: str):
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, f"{output_dir}/index.faiss")
    with open(f"{output_dir}/metadata.pkl", "wb") as f:
        pickle.dump(metadata, f)

def load_index(output_dir: str) -> tuple[faiss.Index, list]:
    index = faiss.read_index(f"{output_dir}/index.faiss")
    with open(f"{output_dir}/metadata.pkl", "rb") as f:
        metadata = pickle.load(f)
    return index, metadata
```

## 스모크 쿼리

파이프라인 완료 후 최소한의 검증을 실행합니다.

```python
def smoke_query(index, metadata, embedder, queries: list[str]) -> dict:
    results = {}
    for q in queries:
        vec = embedder.embed_query(q)
        D, I = index.search(vec.reshape(1, -1), 3)
        top_hits = [metadata[i]["source_file"] for i in I[0] if i != -1]
        results[q] = top_hits
    return results
```

## 엔드투엔드 실행

```python
def run_full_pipeline(doc_dir: str, index_dir: str, embedder) -> dict:
    # 1. 다중 포맷 로드
    documents = load_directory(doc_dir, registry)

    # 2. 파싱 + 품질 게이트
    parsed = [safe_parse(doc) for doc in documents if doc["text"]]

    # 3. 청킹
    all_chunks = []
    for doc in parsed:
        splitter = get_splitter(doc.get("doc_type", "manual"))
        chunks = splitter.split_text(doc["text"])
        all_chunks.extend([(c, doc["metadata"]) for c in chunks])

    # 4. 임베딩 + 인덱싱
    texts = [c[0] for c in all_chunks]
    metas = [c[1] for c in all_chunks]
    vectors = embedder.embed_documents(texts)

    index = faiss.IndexFlatL2(len(vectors[0]))
    index.add(np.array(vectors, dtype="float32"))

    # 5. 저장
    save_index(index, metas, index_dir)

    # 6. 스모크 쿼리
    smoke_results = smoke_query(
        index, metas, embedder,
        queries=["테스트 문서", "정책 변경 사항"]
    )

    return {"indexed": len(all_chunks), "smoke": smoke_results}
```

---

## Before / After

| 항목 | Before (순차 스크립트) | After (오케스트레이터) |
|------|----------------------|----------------------|
| 실패 감지 | 예외 전파 후 중단 | 스테이지별 결과 기록 |
| FAISS 저장 | 없음(재실행 필요) | 디스크 영속화 |
| 검증 | 없음 | 스모크 쿼리 자동 실행 |
| 재실행 | 전체 처음부터 | 실패 스테이지부터 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| FAISS 저장 없음 | 재시작 시 재인덱싱 필요 | write_index + metadata.pkl |
| 스모크 쿼리 없음 | 파이프라인 성공 여부 불명 | 기본 쿼리 2~3개 자동 실행 |
| 스테이지 오류 미기록 | 실패 지점 파악 불가 | StageResult에 errors 필드 |
| 전체 파이프라인 단일 함수 | 테스트 불가 | 스테이지별 함수 분리 |

---

## AI 활용 팁

```
문서 수집 파이프라인의 마지막 단계야. 로드·파싱·청킹·임베딩·FAISS 저장을 스테이지로 묶어줘.
각 스테이지는 StageResult를 반환하고, 실패 시 해당 스테이지부터 재실행 가능해야 해.
완료 후 스모크 쿼리 2개를 실행해서 검색 결과가 비어있지 않은지 확인해줘.
```

---

## 체크리스트

- [ ] 스테이지 오케스트레이터 구현
- [ ] FAISS 인덱스 디스크 저장·로드
- [ ] 메타데이터 영속화(pickle)
- [ ] 스모크 쿼리 자동 실행
- [ ] 스테이지별 처리 결과 로깅
- [ ] 증분 인덱싱과 파이프라인 통합

---

## 처음 질문으로 돌아가기

"그냥 순서대로 실행하면 되지 않나요?" — 스크립트 하나로 시작할 수 있습니다. 하지만 실패 지점 추적, FAISS 영속화, 스모크 쿼리 검증이 없으면 파이프라인을 신뢰할 수 없습니다. 오케스트레이터 구조가 있어야 파이프라인이 실제 운영 도구가 됩니다.

---

## 정리

- 파싱·청킹·임베딩·저장을 스테이지로 분리하고 각 결과를 기록한다
- FAISS 인덱스와 메타데이터를 디스크에 저장해 재시작 시 재사용한다
- 스모크 쿼리로 파이프라인 완료 후 최소 검증을 자동 실행한다
- 스테이지 실패 시 해당 단계부터 재실행할 수 있는 구조를 만든다

---

## 참고 자료

- [FAISS write_index / read_index](https://faiss.ai/cpp_api/file/index__io_8h.html)
- [LangChain RAG 파이프라인 가이드](https://python.langchain.com/docs/use_cases/question_answering/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 파이프라인 스테이지 오케스트레이터
- FAISS 저장·로드
- 스모크 쿼리
- 엔드투엔드 실행
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, RAG, Pipeline, FAISS, Python
