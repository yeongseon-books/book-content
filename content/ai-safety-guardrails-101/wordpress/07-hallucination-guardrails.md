---
series: ai-safety-guardrails-101
episode: 7
title: "바이브코딩을 위한 AI 안전 가드레일 (7/10): Hallucination Guardrail"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - AI Safety
  - Hallucination
  - RAG
  - Grounding
language: ko
---

# 바이브코딩을 위한 AI 안전 가드레일 (7/10): Hallucination Guardrail

> 이 글은 **바이브코딩을 위한 AI 안전 가드레일** 시리즈 7편입니다. RAG 시스템에서 답변이 근거에 실제로 지지되는지 검증하는 grounding 구조를 다룹니다.

바이브코딩으로 RAG 앱을 빠르게 만들다 보면 "모델이 검색한 문서를 바탕으로 답하니까 hallucination이 줄겠지"라고 생각하기 쉽다. 하지만 RAG 시스템도 hallucination에서 자유롭지 않다. 모델은 검색된 문서 안에 없는 내용을 자신 있게 말하거나, 인용 마커를 달았지만 실제로 그 chunk가 해당 주장을 지지하지 않는 경우도 있다.

운영에서 더 중요한 질문은 "이 답이 제공된 근거에 실제로 지지되는가"다. 전 세계 사실을 검증하는 open-domain hallucination은 비용이 크고 어렵지만, RAG 시스템의 closed-domain hallucination은 이미 가진 검색 문맥과 비교하면 되기 때문에 훨씬 현실적으로 접근할 수 있다.

grounding은 세 단계로 나눠야 한다. citation grounding(인용 마커가 있는가), source grounding(인용한 chunk가 실제 검색 결과에 있는가), semantic grounding(그 chunk가 해당 주장을 실제로 지지하는가). citation만 있으면 형식만 맞고, source만 맞으면 내용이 틀릴 수 있다. semantic grounding까지 가야 실제 검증이 된다.

바이브코딩 환경에서 현실적인 접근은 claim 단위 검증과 비용 라우팅이다. NLI 모델로 빠르게 걸러내고, 회색 구간만 LLM judge로 재판정한다. 모든 claim에 judge를 돌리면 지연과 비용을 견디기 어렵다.

> Hallucination을 줄이려면 답변을 문장 덩어리가 아니라 검증 가능한 주장 집합으로 봐야 합니다.

## 이 글에서 다룰 문제

- RAG 시스템에서 hallucination은 왜 여전히 발생할까요?
- citation grounding, source grounding, semantic grounding은 각각 무엇을 검증할까요?
- claim 단위 검증은 어떻게 설계할까요?
- NLI와 LLM judge는 어떻게 조합해야 할까요?
- 검증 실패 시 차단, 경고, 재검색 중 어떤 fallback을 선택해야 할까요?

## Before / After: Hallucination Guardrail 전후

| 상황 | 가드레일 없이 | 가드레일 적용 후 |
|------|--------------|----------------|
| 근거 없는 주장 | 사용자에게 그대로 전달 | claim 단위 검증에서 실패 탐지 |
| 존재하지 않는 chunk 인용 | 형식상 근거 있어 보임 | source grounding에서 즉시 차단 |
| 부분 hallucination | 전체 응답이 맞아 보임 | 실패한 claim만 제거하거나 경고 |
| 검증 비용 폭증 | 모든 claim에 judge 호출 | NLI 필터로 비용 절감, 회색 구간만 judge |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| citation 형식만 강제 | 내용은 틀려도 형식은 맞음 | semantic grounding까지 세 단계 검증 |
| 응답 전체를 한 번에 판단 | 부분 hallucination 놓침 | claim 단위로 분해해 각각 검증 |
| 실패 시 무조건 차단 | UX 급격히 저하 | 실패 수준에 따라 경고/재검색/차단 선택 |
| 모든 claim에 judge 호출 | 지연과 비용 폭증 | NLI 점수 기반 조건부 judge 호출 |

## AI 팁: Grounding 검증 빠르게 시작하는 방법

Claude나 GPT-4에 "Python으로 RAG 응답의 claim을 추출하고 NLI로 grounding을 검증하는 파이프라인을 만들어줘"라고 요청하면 기본 골격을 얻을 수 있다. claim 추출은 `gpt-4o-mini`에 JSON 출력 프롬프트로 빠르게 구현할 수 있다. NLI는 `cross-encoder/nli-deberta-v3-large`를 Hugging Face에서 바로 사용할 수 있다. 먼저 citation 형식 강제(chunk-ID 마커)부터 시작하면 source grounding 자동화가 쉬워진다. judge는 NLI score가 0.4~0.7인 회색 구간에만 호출하는 것이 비용 최적화의 핵심이다.

## 운영 체크리스트

- [ ] RAG 응답에 citation 형식을 강제하고 chunk-ID를 유지하는가
- [ ] answer를 claim 단위로 분해한 뒤 NLI entailment를 계산하는가
- [ ] 회색 구간만 LLM judge로 보내 비용을 통제하는가
- [ ] 실패 시 block, warning, re-retrieval 중 어떤 fallback을 쓸지 사전에 정했는가
- [ ] claim precision, recall, 검증 지연을 regression 세트로 지속 측정하는가

## 처음 질문으로 돌아가기

- **RAG에서도 hallucination이 발생하는 이유는?** 모델은 검색 문맥에 없는 내용을 추가하거나, 인용 마커를 달았지만 실제 chunk가 그 주장을 지지하지 않을 수 있다.
- **세 단계 grounding의 역할은?** citation grounding은 마커 존재 확인, source grounding은 chunk 실존 확인, semantic grounding은 실제 지지 여부 확인이다.
- **NLI vs judge?** NLI는 빠르고 일관되지만 복잡한 추론에는 약하다. 회색 구간만 judge로 보내는 비용 라우팅이 현실적이다.

## 정리

Hallucination guardrail의 핵심은 모델을 더 똑똑하게 만드는 것이 아니라, 모델이 한 주장에 대해 어떤 근거를 갖고 있는지 검증하는 것이다. RAG 시스템에서는 닫힌 문맥 안에서 비교적 잘 정의된 문제다.

운영에서는 citation, source, semantic grounding을 분리하고 claim 단위로 검증하는 구조가 가장 실용적이다. 이 구조가 있어야 어떤 부분이 실패했는지 설명할 수 있고 지표로 튜닝할 수 있다.

## 참고 자료

- [Cross-Encoder NLI — DeBERTa v3 large](https://huggingface.co/cross-encoder/nli-deberta-v3-large)
- [HaluEval — Hallucination Evaluation Benchmark](https://arxiv.org/abs/2305.11747)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/ai-safety-guardrails-101/ko/07-hallucination-guardrails)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 AI 안전 가드레일 (1/10): AI Safety가 왜 중요한가
- 바이브코딩을 위한 AI 안전 가드레일 (2/10): Prompt Injection 방어
- 바이브코딩을 위한 AI 안전 가드레일 (3/10): 출력 필터링과 콘텐츠 모더레이션
- 바이브코딩을 위한 AI 안전 가드레일 (4/10): PII 감지와 마스킹
- 바이브코딩을 위한 AI 안전 가드레일 (5/10): Jailbreak 탐지
- 바이브코딩을 위한 AI 안전 가드레일 (6/10): 독성과 편향 탐지
- **바이브코딩을 위한 AI 안전 가드레일 (7/10): Hallucination Guardrail (현재 글)**
- 바이브코딩을 위한 AI 안전 가드레일 (8/10): Rate Limiting과 남용 방지
- 바이브코딩을 위한 AI 안전 가드레일 (9/10): 감사 로깅과 컴플라이언스
- 바이브코딩을 위한 AI 안전 가드레일 (10/10): 운영 가드레일 시스템 구축
<!-- toc:end -->

Tags: 바이브코딩, AI Safety, Hallucination, RAG, Grounding
