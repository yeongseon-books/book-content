---
series: ai-safety-guardrails-101
episode: 2
title: "바이브코딩을 위한 AI 안전 가드레일 (2/10): Prompt Injection 방어"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - AI Safety
  - Prompt Injection
  - Guardrails
  - Red Team
language: ko
---

# 바이브코딩을 위한 AI 안전 가드레일 (2/10): Prompt Injection 방어

> 이 글은 **바이브코딩을 위한 AI 안전 가드레일** 시리즈 2편입니다. Prompt Injection 공격의 원리와 이를 막는 다층 방어 구조를 다룹니다.

바이브코딩으로 LLM 앱을 빠르게 만들다 보면 입력 검증을 나중으로 미루기 쉽다. "사용자가 이상한 걸 입력하겠어?"라는 생각도 자연스럽다. 하지만 Prompt Injection은 사용자가 악의적이지 않아도 발생한다. RAG 문서 안에 숨어 있거나, 이메일 본문 안에 숨겨진 지시가 에이전트를 조작할 수 있다. 시스템 메시지와 사용자 메시지가 같은 컨텍스트 창에 들어가는 순간, 경계는 언제든 무너질 수 있다.

Prompt Injection 방어는 패턴 하나를 막는 일이 아니다. 어떤 입력을 신뢰할 수 있는지, 어떤 외부 데이터를 구조적으로 감싸야 하는지를 명확히 하는 아키텍처 문제다. "Ignore previous instructions"가 왜 통하는지 이해하면, 방어도 자연스럽게 설계할 수 있다.

바이브코딩 환경에서는 빠르게 프로토타입을 만들고 배포하는 과정에서 이런 경계 설계를 건너뛰기 쉽다. 하지만 Prompt Injection은 나쁜 문장이 아니라 비신뢰 데이터가 실행 지시로 승격되는 경계 실패다. 이 사실을 코드 구조로 받아들이지 않으면 방어는 늘 한 단계 늦는다.

> Prompt Injection 방어의 핵심은 모델에게 더 강하게 명령하는 것이 아닙니다. 사용자 입력과 외부 데이터를 지시 채널로 승격시키지 않도록 시스템 경계를 분리하는 것입니다.

## 이 글에서 다룰 문제

- Prompt Injection은 언제 데이터가 지시로 바뀌면서 시작될까요?
- 직접 injection과 간접 injection은 방어 위치가 어떻게 다를까요?
- Regex, 임베딩, LLM Judge를 어떻게 계층으로 묶어야 할까요?
- Red team 사례를 regression set으로 어떻게 관리해야 할까요?
- 간접 공격을 막으려면 외부 데이터를 어떻게 다뤄야 할까요?

## Before / After: Prompt Injection 방어 전후

| 상황 | 방어 없이 | 방어 적용 후 |
|------|-----------|-------------|
| 직접 공격 | "Ignore previous instructions"로 시스템 프롬프트 노출 | Regex 레이어에서 즉시 차단 |
| 인코딩 우회 | base64, zero-width 문자 통과 | 정규화 후 필터 통과 불가 |
| RAG 문서 공격 | 외부 문서 안의 지시를 모델이 실행 | 비신뢰 데이터 구조적 격리 |
| 공격 감지 | 차단 여부 불명확 | 레이어별 차단 이유 로그 보존 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| Regex만 늘리기 | 변형 공격에 무기력 | 임베딩 + Judge 레이어 추가 |
| 사용자가 정상이면 안전하다고 가정 | 간접 공격 놓침 | 외부 데이터도 비신뢰로 처리 |
| Judge와 응답 모델 동일 | 우회된 모델이 자기 판정 | 응답 모델과 Judge 분리 |
| 차단 사유 상세 노출 | 우회 힌트 제공 | 내부 로그에만 상세 사유 보존 |

## AI 팁: Prompt Injection 탐지 시스템 빠르게 시작하는 방법

Claude나 GPT-4에 "Prompt Injection을 탐지하는 3레이어 Python 파이프라인을 만들어줘"라고 요청하면 기본 골격을 얻을 수 있다. Regex는 `re` 모듈로 한 줄이면 되고, 임베딩 유사도는 `sentence-transformers`로 빠르게 구현할 수 있다. 중요한 것은 cheap filter부터 expensive judge 순서로 실행하는 것이다. 외부 문서는 `<external_data trusted="false">` 형식으로 감싸는 습관만 들여도 간접 공격 리스크를 크게 줄일 수 있다.

## 운영 체크리스트

- [ ] Direct injection용 Regex 레이어와 의미 기반 분류 레이어를 분리했는가
- [ ] 외부 문서는 항상 비신뢰 데이터로 감싸고 지시 채널과 분리했는가
- [ ] Judge 입력은 delimiter로 감싸고, 응답 모델과 별도 소형 모델을 사용했는가
- [ ] Red-team 세트를 CI에 넣고 recall과 false positive를 함께 추적하는가
- [ ] 차단 메시지는 일반화하고 상세 사유는 내부 로그에만 보존하는가

## 처음 질문으로 돌아가기

- **Prompt Injection은 언제 시작될까?** 모델은 시스템 메시지와 사용자 메시지를 운영체제 권한처럼 구분하지 않는다. 뒤에 오는 문장이 앞의 문장을 재해석하게 만들 수 있다.
- **직접 injection vs 간접 injection 방어 위치?** 직접 공격은 입력 레이어에서 빠르게 거른다. 간접 공격은 RAG 문서나 외부 데이터를 비신뢰 데이터로 구조적으로 격리해야 막을 수 있다.
- **외부 데이터를 어떻게 다뤄야 하나?** 모든 외부 데이터를 비신뢰로 간주하고, 데이터와 지시를 구조적으로 분리하고, 지시처럼 보이는 패턴을 미리 제거하거나 이스케이프해야 한다.

## 정리

Prompt Injection은 텍스트 분류 문제가 아니라 시스템 경계 문제다. 사용자 입력과 외부 문서를 안전한 데이터처럼 취급하는 순간, 모델은 그것을 지시로 오해할 수 있다. 방어는 프롬프트 문구가 아니라 레이어 설계에서 시작해야 한다.

실무적으로는 cheap filter에서 expensive judge로 이어지는 순서가 중요하다. Regex는 빠르고 싸지만 약하고, 임베딩은 더 넓게 잡지만 튜닝이 필요하며, LLM Judge는 강하지만 비용이 크다. 이 레이어를 잘 조합하면 성능과 보안의 균형을 맞출 수 있다.

## 참고 자료

- [OWASP LLM01 — Prompt Injection](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- [Greshake et al. — Indirect Prompt Injection (paper)](https://arxiv.org/abs/2302.12173)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/ai-safety-guardrails-101/ko/02-prompt-injection-defense)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 AI 안전 가드레일 (1/10): AI Safety가 왜 중요한가
- **바이브코딩을 위한 AI 안전 가드레일 (2/10): Prompt Injection 방어 (현재 글)**
- 바이브코딩을 위한 AI 안전 가드레일 (3/10): 출력 필터링과 콘텐츠 모더레이션
- 바이브코딩을 위한 AI 안전 가드레일 (4/10): PII 감지와 마스킹
- 바이브코딩을 위한 AI 안전 가드레일 (5/10): Jailbreak 탐지
- 바이브코딩을 위한 AI 안전 가드레일 (6/10): 독성과 편향 탐지
- 바이브코딩을 위한 AI 안전 가드레일 (7/10): Hallucination Guardrail
- 바이브코딩을 위한 AI 안전 가드레일 (8/10): Rate Limiting과 남용 방지
- 바이브코딩을 위한 AI 안전 가드레일 (9/10): 감사 로깅과 컴플라이언스
- 바이브코딩을 위한 AI 안전 가드레일 (10/10): 운영 가드레일 시스템 구축
<!-- toc:end -->

Tags: 바이브코딩, AI Safety, Prompt Injection, Guardrails, Red Team
