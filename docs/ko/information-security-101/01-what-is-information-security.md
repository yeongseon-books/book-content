---
series: information-security-101
episode: 1
title: 정보보안이란 무엇인가?
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - Security
  - CIA
  - ThreatModel
  - RiskAssessment
  - InfoSec
seo_description: 정보보안의 출발점 - 기밀성, 무결성, 가용성과 위협 모델, 위험 평가의 기본기를 한 화면에 정리합니다.
last_reviewed: '2026-05-04'
---

# 정보보안이란 무엇인가?

> Information Security 101 시리즈 (1/10)


## 이 글에서 다룰 문제

보안 사고는 거의 모두 "기술이 부족해서"가 아니라 "선택을 안 해서" 일어납니다. 이 시리즈의 다른 9편은 모두 "어떻게"이지만, 1편은 "무엇을, 왜"를 정합니다. 이 위에 다른 모든 글이 서 있습니다.

> 보안은 기술이 아니라 의사결정의 학문입니다.

## 전체 흐름
```mermaid
flowchart LR
    A["asset"] --> T["threat"]
    A --> V["vulnerability"]
    T --> R["risk"]
    V --> R
    R --> C["control"]
```

자산이 위협과 취약점을 만나면 위험이 됩니다. 위험을 통제(control)하는 것이 보안 활동입니다.

## Before/After

**Before — 보안은 인프라 팀의 일**

```text
배포 직전에 보안 검토 -> 일정 지연 -> 부분적 우회
```

**After — 설계 시점에 위협 모델링**

```text
설계 회의에 STRIDE 한 페이지 -> 위험 우선순위 결정 -> 통제 합의
```

보안을 뒤로 미룰수록 비용이 커진다는 사실이 산업적 관찰입니다.

## 위협 모델 한 페이지

### 1단계 — 자산을 적는다

```text
1_assets.md
- 사용자 비밀번호
- 결제 토큰
- 관리자 세션 쿠키
```

먼저 "보호할 것"의 목록부터 만듭니다. 자산이 없으면 위협을 정의할 수 없습니다.

### 2단계 — STRIDE로 위협 나열

```text
2_threats.md
- Spoofing: 다른 사용자 행세 (auth 우회)
- Tampering: 결제 금액 변조
- Repudiation: 결제 부인
- Information disclosure: DB 덤프 노출
- DoS: 로그인 폭주로 서비스 마비
- Elevation: 일반 사용자가 admin 권한 획득
```

각 자산에 STRIDE 한 줄씩 적어 보면 빠진 위협이 보입니다.

### 3단계 — 위험 우선순위 (간단)

```python
# 3_risk.py
def risk_score(likelihood, impact):
    return likelihood * impact   # 1-5 척도
print(risk_score(3, 5))   # 15
```

이 점수만으로도 "지금 막을 것 vs 나중에 볼 것"이 갈립니다.

### 4단계 — 통제 매핑

```text
4_controls.md
- Spoofing -> MFA, password policy
- Tampering -> HMAC, audit log
- Information disclosure -> 암호화, 접근 통제
```

통제는 위협별로 적습니다. 막연한 "보안 강화"는 검증할 수 없습니다.

### 5단계 — 잔여 위험 합의

```text
5_residual.md
- DoS는 CDN의 rate limit으로 약하게만 방어
- 사고 시 대응 절차 9편 참고
- 분기 1회 재평가
```

모든 위험을 제거할 수 없습니다. 남은 위험을 명시적으로 합의하는 것이 어른의 보안.

## 이 코드에서 주목할 점

- 위협 모델은 "완벽"이 아니라 "공유된 그림"이 목적입니다.
- STRIDE는 빠지지 않게 도와주는 체크리스트입니다.
- 위험 점수는 비교용이지 절댓값이 아닙니다.
- 잔여 위험을 적는 것이 책임을 분명히 합니다.

## 자주 하는 실수 5가지

1. **자산 없이 위협을 나열한다.** 무엇을 보호할지 모르면 통제도 정할 수 없습니다.
2. **모든 위협을 동일하게 대응한다.** 우선순위 없는 보안은 실현되지 않습니다.
3. **보안을 마지막에 한다.** 변경 비용이 100배 커집니다.
4. **위험을 0으로 만들려 한다.** 트레이드오프 없는 보안은 가용성을 죽입니다.
5. **사고 절차 없이 통제만 강화한다.** 사고는 결국 일어납니다.

## 실무에서는 이렇게 쓰입니다

OWASP의 위협 모델링, ISO 27001 / SOC 2의 위험 평가, AWS Well-Architected Security Pillar, Microsoft SDL 모두 같은 골격(자산 - 위협 - 위험 - 통제)을 따릅니다. 큰 조직일수록 이 한 페이지가 의사결정의 출발점입니다.

## 체크리스트

- [ ] CIA를 한 줄로 설명할 수 있는가?
- [ ] STRIDE 6항목을 한 자산에 적용할 수 있는가?
- [ ] 위협 / 취약점 / 위험의 차이를 답할 수 있는가?
- [ ] 잔여 위험이라는 단어가 자연스러운가?
- [ ] 위험 우선순위에 따라 일을 정할 수 있는가?

## 정리 및 다음 단계

정보보안의 출발점은 통제 기술이 아니라 "무엇을 왜 보호하는가"의 질문입니다. 다음 글에서는 가장 자주 마주치는 통제 — 인증과 인가 — 를 다룹니다.

<!-- toc:begin -->
- **정보보안이란 무엇인가? (현재 글)**
- 인증과 인가 (예정)
- 암호화와 해시 (예정)
- TLS와 인증서 (예정)
- Web 보안 기초 (예정)
- SQL Injection과 XSS (예정)
- secret 관리 (예정)
- 권한 최소화 (예정)
- 로그와 감사 (예정)
- 보안 사고 대응 (예정)
<!-- toc:end -->

## 참고 자료

- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [Microsoft STRIDE](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [NIST SP 800-30 Risk Assessment](https://csrc.nist.gov/publications/detail/sp/800-30/rev-1/final)
- [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)
