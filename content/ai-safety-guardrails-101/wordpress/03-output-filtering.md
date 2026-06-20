---
series: ai-safety-guardrails-101
episode: 3
title: "바이브코딩을 위한 AI 안전 가드레일 (3/10): 출력 필터링과 콘텐츠 모더레이션"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - AI Safety
  - Content Moderation
  - Output Filtering
  - Llama Guard
language: ko
---

# 바이브코딩을 위한 AI 안전 가드레일 (3/10): 출력 필터링과 콘텐츠 모더레이션

> 이 글은 **바이브코딩을 위한 AI 안전 가드레일** 시리즈 3편입니다. 모델 출력을 사용자에게 보내기 전에 다시 검증하는 출력 필터링 구조를 다룹니다.

바이브코딩으로 LLM 앱을 빠르게 만들다 보면 "모델이 안전 훈련을 받았으니 괜찮겠지"라고 생각하기 쉽다. 하지만 모델 공급사의 안전 정렬이 있어도 애플리케이션 레이어의 출력 검증은 별개다. 미묘한 jailbreak 하나, RAG 문서 안의 욕설 인용 하나, 의료 도메인에서 처방을 권고하는 한 문장만으로도 서비스 신뢰는 무너진다.

바이브코딩 환경에서 입력 필터링은 챙기더라도 출력 필터링을 건너뛰는 경우가 많다. 실제 사고는 출력 단계에서 더 자주 발생한다. 모델이 위험한 문장을 새로 만들지 않아도, 검색 문맥에 있던 내용을 인용하거나 정책 위반 내용을 우회적으로 재구성하는 방식으로 문제가 생긴다.

콘텐츠 모더레이션은 모델 품질 보조 장치가 아니라 후단 안전 레이어다. 모델이 무엇을 말했는지와, 그 말이 사용자에게 전달되어도 되는지는 별개 판단이어야 한다. 특히 스트리밍 모드에서는 "이미 사용자가 본 토큰은 되돌릴 수 없다"는 제약이 있어서 더 신중한 설계가 필요하다.

실무에서는 OpenAI Moderation API, 오픈소스 분류기(Detoxify, Llama Guard), 사내 정책 judge를 계층으로 조합하는 구조가 현실적이다. 표준 카테고리로 공통 위험을 걸러내고, 비즈니스 고유 정책은 별도 judge로 분리한다. 스트리밍 엔드포인트는 chunk buffer 방식 또는 전체 응답을 받은 뒤 전달하는 방식 중 하나를 명시적으로 선택해야 한다.

> 모델 응답은 완성된 답변이 아니라, 사용자에게 보내기 전에 다시 검증해야 하는 데이터입니다.

## 이 글에서 다룰 문제

- 모델 응답을 왜 다시 데이터로 검증해야 할까요?
- OpenAI Moderation API, Detoxify, Llama Guard는 어떤 상황에서 쓸까요?
- 회사 고유 정책은 표준 카테고리와 어떻게 분리해야 할까요?
- 스트리밍 응답에서 출력 필터링은 어떻게 적용할까요?
- false positive를 어떻게 측정하고 관리해야 할까요?

## Before / After: 출력 필터링 전후

| 상황 | 필터링 없이 | 필터링 적용 후 |
|------|------------|---------------|
| jailbreak 우회 응답 | 유해 내용 그대로 사용자에게 전달 | 후단 모더레이션이 차단 |
| RAG 문서의 욕설 인용 | 응답에 욕설 포함 | 출력 재검사에서 탐지 |
| 사내 정책 위반(환불 확정) | 모델이 환불 약속 | 정책 judge가 차단 |
| 스트리밍 중 위험 토큰 | 사용자가 이미 노출 | chunk buffer로 조기 차단 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| 공급사 안전 장치만 신뢰 | 비즈니스 정책 위반 누락 | 애플리케이션 레이어에 후단 필터 추가 |
| `flagged` 불리언만 확인 | 도메인별 과차단 또는 과소차단 | 카테고리별 threshold 설정 |
| 회사 정책을 표준 카테고리에 억지로 맞춤 | 해석 혼란, 운영 어려움 | 정책 judge를 별도 레이어로 분리 |
| 스트리밍을 마지막에만 검사 | 노출된 토큰 회수 불가 | chunk buffer 또는 delayed delivery 선택 |

## AI 팁: 출력 필터링 빠르게 시작하는 방법

Claude나 GPT-4에 "OpenAI Moderation API와 사내 정책 judge를 조합한 출력 필터링 파이프라인을 만들어줘"라고 요청하면 기본 골격을 얻을 수 있다. Moderation API는 `openai.moderations.create()`로 한 줄이면 되고, 정책 judge는 소형 LLM에 JSON 출력 프롬프트를 넣는 방식으로 빠르게 구현할 수 있다. 스트리밍 엔드포인트는 일단 delayed delivery 방식(전체 응답 수신 후 검사 후 전달)으로 시작하는 것이 가장 안전하다. false positive율은 처음부터 로그에 기록하고 주기적으로 확인하는 습관을 들여야 한다.

## 운영 체크리스트

- [ ] 표준 moderation 카테고리와 회사 고유 정책 judge를 분리했는가
- [ ] 카테고리별 threshold를 도메인 정책에 맞게 설정하고 문서화했는가
- [ ] 스트리밍 엔드포인트에서 chunk buffer 또는 delayed delivery를 명시적으로 선택했는가
- [ ] 차단 메시지는 일반화하고 상세 사유는 내부 로그에만 보존하는가
- [ ] false positive율을 대시보드에서 주기적으로 모니터링하는가

## 처음 질문으로 돌아가기

- **모델 응답을 왜 다시 검증해야 하나?** 공급사 안전 장치는 표준 카테고리 기준이고, 비즈니스 정책은 훨씬 더 구체적이다. 모델 품질과 정책 집행은 분리해서 운영해야 한다.
- **각 도구의 역할은?** OpenAI Moderation API는 빠른 공통 카테고리 필터, Detoxify는 self-hosting 독성 분류, Llama Guard는 커스텀 정책 텍스트를 넣을 수 있는 구조적 분류기다.
- **스트리밍 제약은?** 이미 사용자가 본 토큰은 되돌릴 수 없다. 고위험 도메인에서는 delayed delivery가 더 안전하다.

## 정리

출력 필터링은 모델을 불신해서가 아니라, 서비스 책임을 모델 밖에서 집행하기 위해 필요하다. 공급사 안전 장치가 있어도 애플리케이션은 자체 정책을 가져야 하고, 그 정책은 도메인과 비즈니스 규칙을 반영해야 한다.

표준 moderation API, 오픈소스 분류기, 회사 정책 judge를 계층으로 조합하는 방식이 가장 현실적이다. 여기에 스트리밍 제약과 false positive 측정을 함께 설계해야 운영 가능한 시스템이 된다.

## 참고 자료

- [OpenAI Moderation API](https://platform.openai.com/docs/guides/moderation)
- [Meta Llama Guard](https://github.com/meta-llama/PurpleLlama/tree/main/Llama-Guard3)
- [Detoxify GitHub](https://github.com/unitaryai/detoxify)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/ai-safety-guardrails-101/ko/03-output-filtering)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 AI 안전 가드레일 (1/10): AI Safety가 왜 중요한가
- 바이브코딩을 위한 AI 안전 가드레일 (2/10): Prompt Injection 방어
- **바이브코딩을 위한 AI 안전 가드레일 (3/10): 출력 필터링과 콘텐츠 모더레이션 (현재 글)**
- 바이브코딩을 위한 AI 안전 가드레일 (4/10): PII 감지와 마스킹
- 바이브코딩을 위한 AI 안전 가드레일 (5/10): Jailbreak 탐지
- 바이브코딩을 위한 AI 안전 가드레일 (6/10): 독성과 편향 탐지
- 바이브코딩을 위한 AI 안전 가드레일 (7/10): Hallucination Guardrail
- 바이브코딩을 위한 AI 안전 가드레일 (8/10): Rate Limiting과 남용 방지
- 바이브코딩을 위한 AI 안전 가드레일 (9/10): 감사 로깅과 컴플라이언스
- 바이브코딩을 위한 AI 안전 가드레일 (10/10): 운영 가드레일 시스템 구축
<!-- toc:end -->

Tags: 바이브코딩, AI Safety, Content Moderation, Output Filtering, Llama Guard
