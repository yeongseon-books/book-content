---
title: "바이브코딩을 위한 문서 수집 파이프라인 (5/6): 다중 포맷 문서 파이프라인"
series: document-ingestion-101
episode: 5
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG
- Document Processing
- Python
---

# 바이브코딩을 위한 문서 수집 파이프라인 (5/6): 다중 포맷 문서 파이프라인

이 글은 **바이브코딩을 위한 문서 수집 파이프라인** 시리즈의 다섯 번째 글입니다. PDF 외에 DOCX, TXT, HWPX, HTML 등 여러 포맷을 단일 파이프라인으로 처리하는 방법을 다룹니다.

---

실제 조직에서 문서는 PDF만 오지 않습니다. DOCX, TXT, HWPX, HTML, Excel이 섞여서 들어옵니다. 포맷별로 로더를 따로 만들면, 로더가 5개로 늘어나고 각각 유지보수해야 합니다. "새 포맷 추가해야 해요"라는 요청이 올 때마다 코드를 찾아 수정합니다.

바이브코딩으로 AI에게 "다중 포맷 처리해줘"라고 하면, `if filename.endswith(".pdf"): ... elif filename.endswith(".docx"): ...` 식의 분기가 끝없이 늘어납니다. 그 코드는 작동하지만 확장성이 없습니다.

이 글에서는 LoaderAdapter 패턴으로 포맷별 로더를 플러그인처럼 추가하는 구조를 설계합니다.

> "포맷 추가가 if-else 분기가 아닌 어댑터 등록으로 끝나야 합니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. DOCX, HWPX, HTML 파일을 Python으로 읽는 방법을 알고 있나요?
2. 포맷마다 다른 로더를 어떻게 통합 인터페이스로 묶을 수 있나요?
3. 지원하지 않는 포맷이 들어왔을 때 어떻게 처리해야 하나요?
4. 포맷 정규화(normalized text)가 왜 필요한가요?
5. 디렉터리 전체를 재귀적으로 처리하는 방법이 있나요?

---

## LoaderAdapter 패턴

```python
from abc import ABC, abstractmethod
from pathlib import Path

class LoaderAdapter(ABC):
    @abstractmethod
    def load(self, path: str) -> str:
        """파일을 읽어 정규화된 텍스트를 반환"""
        ...

    @abstractmethod
    def supported_extensions(self) -> list[str]:
        ...
```

각 포맷별 어댑터를 별도 클래스로 구현합니다.

```python
from pypdf import PdfReader
from docx import Document

class PdfLoader(LoaderAdapter):
    def load(self, path: str) -> str:
        reader = PdfReader(path)
        return "\n\n".join(page.extract_text() or "" for page in reader.pages)

    def supported_extensions(self) -> list[str]:
        return [".pdf"]

class DocxLoader(LoaderAdapter):
    def load(self, path: str) -> str:
        doc = Document(path)
        return "\n".join(para.text for para in doc.paragraphs if para.text.strip())

    def supported_extensions(self) -> list[str]:
        return [".docx"]

class TxtLoader(LoaderAdapter):
    def load(self, path: str) -> str:
        return Path(path).read_text(encoding="utf-8")

    def supported_extensions(self) -> list[str]:
        return [".txt", ".md"]
```

## 로더 레지스트리

```python
class LoaderRegistry:
    def __init__(self):
        self._loaders: dict[str, LoaderAdapter] = {}

    def register(self, loader: LoaderAdapter):
        for ext in loader.supported_extensions():
            self._loaders[ext] = loader

    def get(self, path: str) -> LoaderAdapter | None:
        ext = Path(path).suffix.lower()
        return self._loaders.get(ext)

registry = LoaderRegistry()
registry.register(PdfLoader())
registry.register(DocxLoader())
registry.register(TxtLoader())
```

## 안전한 파일 로드

```python
def safe_load_document(path: str, registry: LoaderRegistry) -> dict:
    loader = registry.get(path)
    if loader is None:
        return {"path": path, "text": None, "error": "unsupported format"}
    try:
        text = loader.load(path)
        return {"path": path, "text": text, "error": None}
    except Exception as e:
        return {"path": path, "text": None, "error": str(e)}
```

## 디렉터리 전체 처리

```python
def load_directory(dir_path: str, registry: LoaderRegistry) -> list[dict]:
    results = []
    for path in Path(dir_path).rglob("*"):
        if path.is_file():
            results.append(safe_load_document(str(path), registry))
    return results
```

---

## Before / After

| 항목 | Before (if-else 분기) | After (LoaderAdapter) |
|------|----------------------|-----------------------|
| 새 포맷 추가 | if-else 수정 | 어댑터 클래스 작성 + 등록 |
| 미지원 포맷 | 예외 또는 누락 | error 필드 반환 |
| 테스트 | 분기 조합 | 어댑터별 단위 테스트 |
| 코드 가독성 | 길어지는 조건문 | 각 클래스가 명확한 책임 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 예외 처리 없는 로드 | 한 파일 실패 시 전체 중단 | safe_load_document |
| 인코딩 미지정 | 한국어 텍스트 깨짐 | utf-8 또는 euc-kr 명시 |
| 미지원 포맷 무시 | 조용한 누락 | error 필드 기록 |
| 어댑터 미등록 | 런타임 None 오류 | 등록 여부 확인 테스트 |

---

## AI 활용 팁

```
PDF, DOCX, TXT를 지원하는 LoaderAdapter 패턴을 만들어줘.
각 어댑터는 supported_extensions()와 load() 메서드를 구현해야 해.
LoaderRegistry로 어댑터를 등록하고, safe_load_document는 미지원 포맷과 예외를 error 필드로 반환해야 해.
새 포맷 추가 시 Registry에 등록만 하면 되는 구조로 만들어줘.
```

---

## 체크리스트

- [ ] LoaderAdapter 추상 클래스 정의
- [ ] PDF/DOCX/TXT 어댑터 구현
- [ ] LoaderRegistry 구현
- [ ] safe_load_document(예외·미지원 포맷 처리)
- [ ] load_directory(재귀 탐색)
- [ ] 한국어 인코딩 처리

---

## 처음 질문으로 돌아가기

"포맷이 다양한데 어떻게 하나의 파이프라인으로 처리하나요?" — if-else로 시작하면 포맷이 추가될수록 코드가 복잡해집니다. LoaderAdapter 패턴은 새 포맷을 클래스 하나로 추가할 수 있고, 기존 코드를 건드리지 않습니다.

---

## 정리

- LoaderAdapter 추상 클래스로 포맷별 로더의 인터페이스를 통일한다
- LoaderRegistry에 어댑터를 등록하면 확장자 기반으로 자동 라우팅된다
- safe_load_document로 예외와 미지원 포맷을 error 필드로 처리한다
- load_directory로 디렉터리 전체를 재귀 처리한다

---

## 참고 자료

- [python-docx 문서](https://python-docx.readthedocs.io/)
- [LangChain Document Loaders](https://python.langchain.com/docs/modules/data_connection/document_loaders/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- LoaderAdapter 패턴
- 로더 레지스트리
- 안전한 파일 로드
- 디렉터리 전체 처리
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, RAG, Document Processing, Python
