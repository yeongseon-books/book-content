---
title: "바이브코딩을 위한 문서 수집 파이프라인 (4/6): 증분 인덱싱 — 변경된 문서만 업데이트"
series: document-ingestion-101
episode: 4
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG
- Incremental Indexing
- Python
---

# 바이브코딩을 위한 문서 수집 파이프라인 (4/6): 증분 인덱싱 — 변경된 문서만 업데이트

이 글은 **바이브코딩을 위한 문서 수집 파이프라인** 시리즈의 네 번째 글입니다. 문서가 변경될 때 전체를 재색인하지 않고 변경된 부분만 업데이트하는 증분 인덱싱을 다룹니다.

---

문서가 100개일 때는 전체 재색인이 괜찮습니다. 1만 개가 되면 매일 전체를 재색인하는 건 비현실적입니다. 문서 하나가 바뀔 때마다 10분씩 기다려야 한다면, 파이프라인은 실용적이지 않습니다.

바이브코딩으로 AI에게 "문서 업데이트 처리해줘"라고 하면, AI는 전체 재색인 코드를 줍니다. 처음엔 작동합니다. 문서가 늘어날수록 느려지고, 팀은 "왜 인덱싱이 이렇게 오래 걸리지?"를 반복합니다.

이 글에서는 파일 해시로 변경을 감지하고, 변경된 문서만 재처리하는 증분 인덱싱을 구현합니다.

> "변경된 문서만 처리하면 인덱싱 시간이 문서 수가 아닌 변경 수에 비례합니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 파일이 변경되었는지 해시로 감지하는 방법을 알고 있나요?
2. 삭제된 문서의 청크를 인덱스에서 제거하는 방법이 있나요?
3. 증분 인덱싱 상태를 어디에 저장해야 하나요?
4. 청크 매니페스트가 왜 필요한가요?
5. 인덱싱 실패 시 재시도 전략이 있나요?

---

## 파일 해시로 변경 감지

```python
import hashlib
from pathlib import Path

def file_hash(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()
```

파일 수정 시간 대신 해시를 쓰면 내용이 같으면 변경으로 취급하지 않습니다.

## IndexStateStore

```python
import json
from pathlib import Path

class IndexStateStore:
    def __init__(self, state_path: str = ".index_state.json"):
        self.path = Path(state_path)
        self.state: dict = self._load()

    def _load(self) -> dict:
        if self.path.exists():
            return json.loads(self.path.read_text())
        return {}

    def save(self):
        self.path.write_text(json.dumps(self.state, indent=2))

    def is_changed(self, file_path: str) -> bool:
        current_hash = file_hash(file_path)
        return self.state.get(file_path) != current_hash

    def update(self, file_path: str):
        self.state[file_path] = file_hash(file_path)

    def remove(self, file_path: str):
        self.state.pop(file_path, None)
```

## 증분 동기화

```python
def delta_sync(doc_dir: str, store: IndexStateStore, indexer) -> dict:
    current_files = set(Path(doc_dir).glob("**/*.pdf"))
    indexed_files = set(store.state.keys())

    added = [f for f in current_files if str(f) not in indexed_files]
    changed = [f for f in current_files if store.is_changed(str(f))]
    deleted = [f for f in indexed_files if not Path(f).exists()]

    for f in added + changed:
        indexer.index_file(str(f))
        store.update(str(f))

    for f in deleted:
        indexer.remove_file(str(f))
        store.remove(str(f))

    store.save()
    return {"added": len(added), "changed": len(changed), "deleted": len(deleted)}
```

---

## Before / After

| 항목 | Before (전체 재색인) | After (증분 인덱싱) |
|------|--------------------|--------------------|
| 1만 문서 업데이트 | 10분 | 변경 10개면 1분 |
| 삭제 문서 처리 | 수동 | 자동 감지·제거 |
| 변경 추적 | 없음 | 해시 기반 감지 |
| 장애 복구 | 전체 재실행 | 실패 파일만 재처리 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| mtime으로 변경 감지 | 내용 미변경 파일 재처리 | SHA-256 해시 사용 |
| 상태 파일 미저장 | 재시작 시 전체 재처리 | JSON 상태 파일 영속화 |
| 삭제 파일 미처리 | 좀비 청크 누적 | delta_sync에서 deleted 처리 |
| 청크 매니페스트 없음 | 파일별 청크 추적 불가 | file→chunk_ids 매핑 유지 |

---

## AI 활용 팁

```
SHA-256 해시로 파일 변경을 감지하고 JSON 파일에 상태를 저장하는 IndexStateStore를 만들어줘.
delta_sync 함수는 추가/변경/삭제 파일을 감지해서 FAISS 인덱스를 업데이트해야 해.
파일당 chunk_ids를 매니페스트로 관리해서 삭제 시 해당 청크만 제거할 수 있어야 해.
```

---

## 체크리스트

- [ ] SHA-256 파일 해시 구현
- [ ] IndexStateStore(추가/변경/삭제 감지)
- [ ] delta_sync 함수 구현
- [ ] 청크 매니페스트(file → chunk_ids 매핑)
- [ ] 상태 파일 영속화(JSON)
- [ ] 실패 파일 재시도 로직

---

## 처음 질문으로 돌아가기

"문서가 바뀔 때마다 전체를 재색인해야 하나요?" — 처음에는 그래도 됩니다. 문서가 수천 개를 넘는 순간 전체 재색인은 운영 부담이 됩니다. 해시 기반 변경 감지와 delta_sync가 있으면 인덱싱 시간이 변경 수에 비례하게 됩니다.

---

## 정리

- SHA-256 해시로 파일 변경을 정확하게 감지한다
- IndexStateStore에 해시를 저장하고 영속화한다
- delta_sync로 추가·변경·삭제 파일을 각각 처리한다
- 파일당 chunk_ids 매니페스트로 삭제 시 정확한 청크 제거를 보장한다

---

## 참고 자료

- [Python hashlib 문서](https://docs.python.org/3/library/hashlib.html)
- [FAISS remove_ids](https://faiss.ai/cpp_api/struct/structfaiss_1_1Index.html)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 파일 해시로 변경 감지
- IndexStateStore
- 증분 동기화
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, RAG, Incremental Indexing, Python
