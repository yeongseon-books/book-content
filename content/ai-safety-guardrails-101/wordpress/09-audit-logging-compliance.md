---
series: ai-safety-guardrails-101
episode: 9
title: "바이브코딩을 위한 AI 안전 가드레일 (9/10): 감사 로깅과 컴플라이언스"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - AI Safety
  - Audit Logging
  - Compliance
  - GDPR
language: ko
---

# 바이브코딩을 위한 AI 안전 가드레일 (9/10): 감사 로깅과 컴플라이언스

> 이 글은 **바이브코딩을 위한 AI 안전 가드레일** 시리즈 9편입니다. LLM 앱의 감사 로그를 컴플라이언스 증거로 쓸 수 있도록 설계하는 방법을 다룹니다.

바이브코딩으로 LLM 앱을 빠르게 만들다 보면 로깅은 "디버깅 용도로 대충 남기면 되겠지"라고 생각하기 쉽다. 하지만 AI 앱에서 감사 로그는 디버깅 도구가 아니다. 나중에 "왜 이 답이 나왔는가", "어떤 guardrail이 통과했고 무엇이 차단됐는가", "삭제 요청은 언제 처리됐는가"를 재구성해야 하는 증거 자료다.

특히 AI 시스템에서는 결정 근거를 남기지 않으면 사고 대응이 거의 불가능하다. 어떤 RAG chunk를 봤는지, 어떤 모델 설정이 적용됐는지, 어떤 정책 judge가 통과했는지까지 함께 남아야 규제 대응과 재현, drift 탐지가 가능하다.

application log와 audit log는 목적, 형식, 보존 정책이 모두 달라야 한다. application log는 7~30일 자유 형식 텍스트이고, audit log는 1~7년 구조화된 스키마로 append-only, 제한된 접근이 필요하다. 원문 프롬프트와 응답은 audit log 본문에 두지 않는다. hash만 남기고 별도 암호화 저장소와 분리해야 GDPR 삭제 요청에 대응할 수 있다.

append-only는 운영 규칙만으로는 부족하다. WORM S3 버킷, append-only 데이터베이스, hash chain 중 하나로 기술적으로 강제해야 변조 불가를 증명할 수 있다.

> 감사 로그는 많이 남기는 로그가 아니라, 나중에 누가 무엇을 왜 했는지 재구성할 수 있는 증거입니다.

## 이 글에서 다룰 문제

- 감사 로그는 일반 디버그 로그와 어떻게 달라야 할까요?
- 원문 데이터는 왜 별도 저장소로 분리해야 할까요?
- append-only를 기술적으로 강제하는 방법은 무엇인가요?
- decision rationale을 어떻게 구조화해야 규제 대응이 가능할까요?
- 보존 기간과 자동 삭제는 어떻게 관리해야 할까요?

## Before / After: 감사 로깅 전후

| 상황 | 로깅 없이 | 감사 로깅 적용 후 |
|------|-----------|----------------|
| guardrail 결정 재현 | 불가 | request-id로 전 단계 재구성 |
| GDPR 삭제 요청 | 어디에 무엇이 있는지 모름 | PII 저장소 분리로 즉시 삭제 |
| 보안 감사 | 수동 조사 | audit log에서 자동 리포트 |
| 원문 프롬프트 누출 | application log에 평문 기록 | hash만 audit에, 원문은 암호화 분리 |

## 흔한 실수

| 실수 | 결과 | 올바른 접근 |
|------|------|------------|
| application log = audit log로 취급 | 보존 기간, 접근 권한 혼재 | 목적별 별도 저장소와 스키마 분리 |
| 원문 프롬프트를 audit에 저장 | 가장 큰 PII 누출 표면 | hash만 남기고 원문은 암호화 별도 보관 |
| append-only를 규칙으로만 관리 | 변조 불가 증명 불가 | WORM 버킷, hash chain 기술적 강제 |
| 삭제 요청을 원문 저장소에만 적용 | 캐시, 로그에 잔류 | 삭제 자체도 audit 이벤트로 기록 |

## AI 팁: 감사 로깅 빠르게 시작하는 방법

Claude나 GPT-4에 "Python으로 LLM 앱의 감사 로그 스키마와 hash chain append 함수를 만들어줘"라고 요청하면 기본 골격을 얻을 수 있다. AuditRecord dataclass에 request_id, timestamp, user_id_hash(원문 아닌 hash), prompt_hash, response_hash, guardrail_decisions, blocked, block_reason 필드를 넣는 것이 출발점이다. hash chain은 `prev_hash + str(sorted(record.items()))`를 sha256으로 해싱하는 10줄이면 된다. 원문 데이터는 KMS로 암호화해 TTL이 있는 별도 저장소에 보관한다.

## 운영 체크리스트

- [ ] audit schema와 application log schema를 분리했는가
- [ ] 원문 프롬프트·응답은 KMS 기반 별도 저장소에 두고 audit에는 hash만 남기는가
- [ ] WORM, 권한 통제, hash chain 중 최소 하나로 append-only를 기술적으로 강제하는가
- [ ] 검색 chunk, 모델 파라미터, guardrail 결정을 rationale 필드로 기록하는가
- [ ] 보존 기간 만료와 삭제 요청 처리 자체도 audit log에 남기는가

## 처음 질문으로 돌아가기

- **감사 로그와 디버그 로그의 차이는?** 보존 기간(며칠 vs 수년), 형식(자유 텍스트 vs 구조화 스키마), 접근 권한(엔지니어 vs 보안/준법팀), PII 처리(권장 vs 필수 분리)가 모두 다르다.
- **원문 분리가 필요한 이유는?** GDPR 삭제 요청 시 원문만 지우고 audit hash는 무결성 목적으로 보존할 수 있다. 같은 저장소에 있으면 둘 다 지우거나 둘 다 남겨야 하는 상황이 된다.
- **append-only 기술 강제 방법은?** AWS S3 Object Lock(Compliance Mode), ClickHouse/TimescaleDB(UPDATE/DELETE 권한 미부여), 레코드별 hash chain 세 가지가 대표적이다.

## 정리

감사 로깅은 나중에 보기 위한 로그가 아니라, 나중에 설명하기 위한 증거다. 이 차이를 이해하면 왜 별도 저장소, 별도 권한, 별도 보존 정책이 필요한지 자연스럽게 보인다.

원문 데이터와 audit 데이터를 분리하고, append-only 무결성을 기술적으로 강제하며, decision rationale을 구조화된 필드로 남기는 방식이 가장 안정적이다. 보존과 삭제 기록까지 들어가야 컴플라이언스가 완성된다.

## 참고 자료

- [GDPR Article 30 — Records of processing activities](https://gdpr-info.eu/art-30-gdpr/)
- [AWS S3 Object Lock — Compliance mode](https://docs.aws.amazon.com/AmazonS3/latest/userguide/object-lock-overview.html)
- [SOC 2 — Trust Services Criteria](https://www.aicpa-cima.com/resources/landing/system-and-organization-controls-soc-suite-of-services)
- [이 글의 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/ai-safety-guardrails-101/ko/09-audit-logging-compliance)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 AI 안전 가드레일 (1/10): AI Safety가 왜 중요한가
- 바이브코딩을 위한 AI 안전 가드레일 (2/10): Prompt Injection 방어
- 바이브코딩을 위한 AI 안전 가드레일 (3/10): 출력 필터링과 콘텐츠 모더레이션
- 바이브코딩을 위한 AI 안전 가드레일 (4/10): PII 감지와 마스킹
- 바이브코딩을 위한 AI 안전 가드레일 (5/10): Jailbreak 탐지
- 바이브코딩을 위한 AI 안전 가드레일 (6/10): 독성과 편향 탐지
- 바이브코딩을 위한 AI 안전 가드레일 (7/10): Hallucination Guardrail
- 바이브코딩을 위한 AI 안전 가드레일 (8/10): Rate Limiting과 남용 방지
- **바이브코딩을 위한 AI 안전 가드레일 (9/10): 감사 로깅과 컴플라이언스 (현재 글)**
- 바이브코딩을 위한 AI 안전 가드레일 (10/10): 운영 가드레일 시스템 구축
<!-- toc:end -->

Tags: 바이브코딩, AI Safety, Audit Logging, Compliance, GDPR
