---
title: "바이브코딩을 위한 RAG 심화 (1/6): 문서 로딩과 청크 전략"
series: rag-deep-dive
episode: 1
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- RAG심화
- 청크전략
- LangChain
- AI코딩
seo_description: "바이브코딩을 위한 RAG 심화 1편: 문서 로딩과 청크 전략. PyPDFLoader와 RecursiveCharacterTextSplitter가 검색 품질에 미치는 영향을 이해합니다."
---

# 바이브코딩을 위한 RAG 심화 (1/6): 문서 로딩과 청크 전략

이 글은 바이브코딩을 위한 RAG 심화 시리즈의 1번째 글입니다.

RAG 시스템에서 답변 품질이 나쁠 때 가장 먼저 의심해야 할 곳은 LLM이 아닙니다. 검색기에 전달되는 청크가 의미 경계를 올바르게 담고 있는지 먼저 확인해야 합니다. 청킹은 텍스트를 잘게 자르는 전처리 작업이 아닙니다. 나중에 retrieval이 다시 회수하길 바라는 의미 경계를 지금 결정하는 설계 단계입니다. chunk_size와 chunk_overlap 한 쌍의 숫자가 검색 정밀도와 컨텍스트 보존 사이의 트레이드오프를 결정합니다.

바이브코딩에서 이 개념이 중요한 이유는 단순합니다. AI에게 문서 처리 코드를 요청할 때 splitter 종류, chunk_size, chunk_overlap, 메타데이터 보존을 함께 명시하지 않으면, 검색 품질을 해치는 기본값으로 동작하는 코드가 생성되기 때문입니다.

> 청킹은 텍스트를 잘게 자르는 작업이 아닙니다. 나중에 retrieval이 다시 회수하길 바라는 의미 경계를 지금 얼려 두는 작업입니다.

---

## 이 글에서 다룰 문제

- 로더와 splitter의 경계 결정이 왜 검색 품질을 좌우할까요?
- Character, Recursive, Token splitter는 같은 텍스트를 어떻게 다르게 자를까요?
- chunk_overlap이 설정값만큼 정확히 겹치지 않는 것처럼 보일 때 어디를 봐야 할까요?
- 자주 하는 실수와 그 해결책은 무엇일까요?
- 이 개념을 실무에 적용하는 방법은 무엇일까요?

청크 전략을 이해하면 AI에게 "RecursiveCharacterTextSplitter로 chunk_size=512, overlap=64, 소스 메타데이터 보존"처럼 정확한 요청을 할 수 있습니다. 이것이 바이브코딩 시대에 이 개념을 배우는 이유입니다.

## Before / After

**Before — AI에게 컨텍스트 없이 질문:**

```
Q: "PDF 문서를 RAG용으로 처리하는 코드 작성해줘"
→ splitter 종류 선택 근거 없음
→ chunk_size 기본값 사용으로 성능 예측 불가
→ 메타데이터(소스, 페이지) 누락
```

**After — 개념을 이해하고 구체적으로 질문:**

```
Q: "PyPDFLoader로 PDF를 로드하고
    RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)로 분할해줘.
    각 청크에 source, page 메타데이터를 보존하고
    청크 수와 첫 번째 청크 내용을 출력해줘"
→ 의미 경계를 고려한 분할
→ retrieval 추적 가능한 메타데이터
```

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| CharacterTextSplitter만 사용 | 문단 중간을 잘라 의미 손실 | RecursiveCharacterTextSplitter로 계층적 분할 |
| chunk_overlap=0 | 경계 걸친 내용 검색 불가 | 10~15% overlap으로 경계 문맥 보존 |
| 메타데이터 없이 청킹 | 어느 문서 어느 페이지인지 추적 불가 | source, page 메타데이터 반드시 유지 |
| chunk_size를 고정 후 조정 안 함 | 도메인마다 최적값이 다름 | 실제 도메인 데이터로 청크 크기 실험 |
| 토큰 수 대신 문자 수로만 설정 | 임베딩 모델 토큰 한도 초과 가능 | TokenTextSplitter로 토큰 기준 분할 고려 |

## AI 협업 팁

문서 로딩과 청킹 관련 효과적인 AI 프롬프트 패턴:

1. **splitter 비교 요청**: "같은 텍스트를 CharacterTextSplitter, RecursiveCharacterTextSplitter, TokenTextSplitter로 각각 분할하고 청크 수와 평균 길이를 비교하는 코드 작성해줘"
2. **메타데이터 보존 요청**: "PDF 각 페이지를 청킹할 때 source 파일명과 page 번호를 메타데이터로 유지하는 코드 작성해줘"
3. **청크 검사 요청**: "청크 중에서 너무 짧거나(50자 미만) 너무 긴(600자 초과) 것을 필터링하고 통계를 출력하는 코드 작성해줘"

예시 프롬프트:
> "RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=64)로 텍스트를 분할하고 CharacterTextSplitter 결과와 청크 수, 평균 길이, 최소/최대 길이를 비교하는 코드를 작성해줘. 각 청크에 source 메타데이터 포함."

## 운영 체크리스트

- [ ] splitter 종류를 도메인 특성에 맞게 선택했는가?
- [ ] chunk_size와 chunk_overlap이 임베딩 모델 토큰 한도 안에 들어 있는가?
- [ ] 각 청크에 source와 page 메타데이터가 보존되는가?
- [ ] 너무 짧거나 긴 청크를 필터링하는 로직이 있는가?
- [ ] 다음 글에서 이 청크를 임베딩할 때 동일한 메타데이터가 유지되는가?

## 처음 질문으로 돌아가기

문서 로딩과 청크 전략을 배운 지금, AI에게 이 주제로 더 정확한 질문을 할 수 있게 되었습니다. splitter 종류와 overlap 설정을 명시한 사람과 그렇지 않은 사람이 AI에게 받는 청킹 코드의 품질은 크게 다릅니다.

## 정리

문서 로딩과 청크 전략은 바이브코딩을 위한 RAG 심화의 출발점입니다. 청킹이 단순한 전처리가 아니라 검색 품질을 결정하는 설계 단계임을 이해했습니다. 다음 글에서는 이 청크를 임베딩하고 FAISS 인덱스에 저장하는 방법을 다룹니다.

## 참고 자료

- [LangChain Text Splitters](https://python.langchain.com/docs/concepts/text_splitters/)
- [RecursiveCharacterTextSplitter API](https://python.langchain.com/api_reference/text_splitters/character/langchain_text_splitters.character.RecursiveCharacterTextSplitter.html)
- [PyPDFLoader](https://python.langchain.com/docs/integrations/document_loaders/pypdfloader/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/rag-deep-dive/ko/01-document-loading-and-chunking)

---

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 RAG 심화 (1/6): 문서 로딩과 청크 전략 (현재 글)**
- 바이브코딩을 위한 RAG 심화 (2/6): 임베딩과 벡터 인덱스
- 바이브코딩을 위한 RAG 심화 (3/6): Retriever 설계
- 바이브코딩을 위한 RAG 심화 (4/6): 프롬프트 구성과 컨텍스트 주입
- 바이브코딩을 위한 RAG 심화 (5/6): RAG Chain 조립
- 바이브코딩을 위한 RAG 심화 (6/6): 평가와 품질 게이트
<!-- toc:end -->

Tags: 바이브코딩, RAG심화, 청크전략, AI코딩
