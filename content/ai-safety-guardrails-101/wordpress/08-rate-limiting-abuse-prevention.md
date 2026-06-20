---
series: ai-safety-guardrails-101
episode: 8
title: "바이브코딩을 위한 AI 안전 가드레일 (8/10): Rate Limiting과 남용 방지"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - AI Safety
  - Rate Limiting
  - Abuse Prevention
  - Anomaly Detection
language: ko
---

# 바이브코딩을 위한 AI 안전 가드레일 (8/10): Rate Limiting과 남용 방지

> 이 글은 **바이브코딩을 위한 AI 안전 가드레일** 시리즈 8편입니다. LLM 앱에서 비용 폭주와 남용을 막는 다차원 rate limiting 구조를 다룹니다.

바이브코딩으로 LLM 앱을 빠르게 배포하다 보면 rate limiting은 "나중에 추가하면 되겠지"라고 미루기 쉽다. 그런데 LLM API는 전통적인 웹 API와 다르다. 한 요청이 100토큰일 수도 있고 100,000토큰일 수도 있다. 초당 요청 수(RPS)가 낮아도 긴 컨텍스트와 장문 출력만으로 하루 비용이 폭증할 수 있다.

LLM rate limiting을 트래픽 제어 문제가 아니라 비용, 남용, 가용성을 동시에 통제하는 예산 시스템으로 봐야 한다. RPS만 제한하면 출력 토큰 남용을 막지 못한다. 입력 토큰만 계산하면 스트리밍 무한 출력 공격을 놓친다. 사용자 기준 한도만 두면 IP 회전이나 API 키 공유 남용을 막지 못한다.

현실적인 설계는 네 차원을 동시에 관리하는 것이다. RPS, 분당 입력 토큰(IPM), 분당 출력 토큰(OPM), 일일 비용($). 그리고 세 경계를 겹치는 것이다. 사용자 ID, IP 주소, API 키. 이 구조가 있어야 우회 비용이 높아진다.

이상 징후 탐지와 단계적 escalation도 함께 있어야 한다. 첫 이상 신호에서 즉시 차단하면 정상 burst까지 같이 막아 사용자 불만이 커진다. 경고 → 완화(응답 축소) → CAPTCHA → 정지 순서의 단계적 대응이 안정적이다.

> LLM rate limiting의 단위는 요청 한 번이 아니라 토큰, 비용, 도구 호출처럼 실제로 고갈되는 자원입니다.

## 이 글에서 다룰 문제

- LLM rate limiting은 왜 요청 수가 아니라 리소스 소비 기준이어야 할까요?
- token bucket 알고리즘을 RPS, 토큰, 비용에 어떻게 재사용할 수 있을까요?
- 스트리밍 출력의 남용은 어떻게 막을 수 있을까요?
- 이상 징후 탐지와 단계적 escalation은 어떻게 설계할까요?
- 한도 초과 시 차단과 완화 응답은 어떻게 나눠야 할까요?

## Before / After: Rate Limiting 전후

| 상황 | 제한 없이 | 제한 적용 후 |
|------|-----------|-------------|
| 대용량 컨텍스트 요청 반복 | 비용 폭증 | 입력 토큰 한도로 차단 |
| 스트리밍 무한 출력 공격 | 출력 비용 통제 불가 | output budget 실시간 차감 |
| IP 회전 공격 | 사용자 한도 우회 | IP 경계 추가로 차단 |
| 비정상 burst | 사후 발견 | z-score 기반 이상 탐지 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| RPS 한도만 설정 | 대형 입력/출력 비용 폭주 | RPS + 토큰 + 비용 4차원 관리 |
| 입력 토큰만 측정 | 출력 스트리밍 남용 허용 | 스트리밍 중 출력 토큰 실시간 차감 |
| 사용자 기준만 제한 | IP 회전, 키 공유 우회 | 사용자·IP·API 키 세 경계 겹치기 |
| 이상 징후에 즉시 차단 | 정상 burst 사용자 이탈 | 경고 → 완화 → CAPTCHA → 정지 순서 |

## AI 팁: Rate Limiting 빠르게 구현하는 방법

Claude나 GPT-4에 "Python으로 Redis를 사용한 token bucket rate limiter를 사용자·IP·API 키 세 경계에 적용하는 코드를 만들어줘"라고 요청하면 기본 골격을 얻을 수 있다. Redis `hset`으로 tokens와 ts(타임스탬프)를 저장하는 token bucket 구현은 50줄 이내로 가능하다. cost 파라미터를 1로 두면 RPS limiter, 입력 토큰 수로 두면 TPM limiter, 비용 단위로 두면 spend limiter가 된다. 같은 함수를 세 차원에 재사용하는 구조가 가장 단순하다. 스트리밍 output budget은 yield 루프 안에서 토큰을 차감하는 방식으로 구현한다.

## 운영 체크리스트

- [ ] RPS, 입력 토큰, 출력 토큰, 비용 한도를 각각 정의했는가
- [ ] 사용자·IP·API 키 경계를 동시에 적용하는가
- [ ] 스트리밍 도중 출력 토큰 예산을 차감하고 별도 output cap을 두는가
- [ ] z-score 기반 이상 탐지와 단계적 escalation 정책을 문서화했는가
- [ ] 예산 70/85/95% 구간 알림을 분리해서 설정했는가

## 처음 질문으로 돌아가기

- **왜 요청 수가 아니라 리소스 소비 기준이어야 하나?** 한 요청이 100토큰일 수도 100,000토큰일 수도 있다. RPS가 낮아도 비용은 폭증할 수 있다.
- **token bucket을 어떻게 재사용하나?** cost 파라미터를 1로 두면 RPS, 토큰 수로 두면 TPM, 비용 단위로 두면 spend limiter가 된다. 같은 메커니즘을 여러 차원에 재사용한다.
- **단계적 escalation이 왜 필요한가?** 첫 이상 신호에서 즉시 차단하면 정상 burst 사용자도 같이 막힌다. 완화 응답(응답 축소, cheap 모델 전환)을 거치면 사용자 경험을 덜 해친다.

## 정리

LLM rate limiting은 초당 요청 제한이 아니라 토큰과 비용이 예산 밖으로 새지 않게 만드는 리소스 회계 시스템이다. 이 구조를 갖춰야 남용과 비용 폭주를 동시에 막을 수 있다.

token bucket이 좋은 출발점이지만, anomaly detection과 escalation이 빠지면 거친 차단 시스템이 된다. 반대로 이상 탐지만 있고 강제 한도가 없으면 사고를 실시간으로 막지 못한다. 요청을 세지 말고, 소비를 계산해야 한다.

## 참고 자료

- [Stripe Engineering — Scaling your API with rate limiters](https://stripe.com/blog/rate-limiters)
- [OpenAI API — Rate limits documentation](https://platform.openai.com/docs/guides/rate-limits)
- [Redis — Rate limiting patterns](https://redis.io/docs/latest/develop/use/patterns/distributed-locks/)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/ai-safety-guardrails-101/ko/08-rate-limiting-abuse-prevention)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 AI 안전 가드레일 (1/10): AI Safety가 왜 중요한가
- 바이브코딩을 위한 AI 안전 가드레일 (2/10): Prompt Injection 방어
- 바이브코딩을 위한 AI 안전 가드레일 (3/10): 출력 필터링과 콘텐츠 모더레이션
- 바이브코딩을 위한 AI 안전 가드레일 (4/10): PII 감지와 마스킹
- 바이브코딩을 위한 AI 안전 가드레일 (5/10): Jailbreak 탐지
- 바이브코딩을 위한 AI 안전 가드레일 (6/10): 독성과 편향 탐지
- 바이브코딩을 위한 AI 안전 가드레일 (7/10): Hallucination Guardrail
- **바이브코딩을 위한 AI 안전 가드레일 (8/10): Rate Limiting과 남용 방지 (현재 글)**
- 바이브코딩을 위한 AI 안전 가드레일 (9/10): 감사 로깅과 컴플라이언스
- 바이브코딩을 위한 AI 안전 가드레일 (10/10): 운영 가드레일 시스템 구축
<!-- toc:end -->

Tags: 바이브코딩, AI Safety, Rate Limiting, Abuse Prevention, Anomaly Detection
