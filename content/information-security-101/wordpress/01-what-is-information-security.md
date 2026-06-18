---
series: information-security-101
episode: 1
title: "바이브코딩을 위한 정보 보안 기초 (1/10): 정보보안이란 무엇인가?"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 정보보안
  - CIA트라이어드
  - 위협모델링
  - STRIDE
  - AI보안
language: ko
---

# 바이브코딩을 위한 정보 보안 기초 (1/10): 정보보안이란 무엇인가?

이 글은 **바이브코딩을 위한 정보 보안 기초** 시리즈의 1편입니다. AI가 만들어주는 코드에는 보안 취약점이 숨어 있을 수 있습니다. 10편에 걸쳐 바이브코딩 개발자가 직접 확인해야 할 보안 개념을 정리합니다.

---

AI에게 "로그인 기능 만들어줘"라고 하면 그럴싸한 코드가 바로 나옵니다. 동작도 합니다. 그런데 그 코드, 진짜 안전할까요? 비밀번호를 어떻게 저장하고 있는지, 세션은 어떻게 관리하는지, 어떤 정보를 어디에 남기는지 — AI는 물어보지 않으면 말해주지 않습니다. 바이브코딩 개발자가 보안을 직접 챙겨야 하는 이유가 바로 여기에 있습니다.

> "정보보안은 기술 이름을 아는 것이 아니라 '무엇을 보호하고, 어떤 위협을 먼저 줄일지'를 명확히 말할 수 있는 상태를 만드는 것입니다. AI가 코드를 만들어준다고 해서 이 판단이 자동으로 따라오지는 않습니다."

## 이 글에서 다룰 질문들

- 정보보안은 정확히 무엇을 뜻할까요?
- CIA 트라이어드는 바이브코딩에서 왜 중요할까요?
- 위협, 취약점, 위험은 어떻게 연결될까요?
- STRIDE 체크리스트를 AI 생성 코드에 어떻게 적용할까요?
- 위험 우선순위를 정하지 않으면 무슨 일이 생길까요?

---

## 바이브코딩과 정보보안: 왜 지금 보안을 배워야 하나요?

바이브코딩(Vibe Coding)은 AI 모델과 대화하듯 코드를 작성하는 방식입니다. 개발 속도가 빨라지고 복잡한 기능도 빠르게 구현할 수 있습니다. 그런데 이 속도가 보안의 구멍을 함께 만들기도 합니다.

**문제는 AI가 "작동하는 코드"와 "안전한 코드"를 구분하지 않는다는 점입니다.**

AI는 평균적인 코드를 생성합니다. 인터넷에서 수집한 수많은 예제 중에는 보안이 약한 코드도 포함되어 있습니다. AI가 비밀번호를 SHA-256으로 해시해서 저장하는 코드를 생성했다면, 그게 왜 문제인지 직접 알아야 합니다.

### Before: 보안 기초 없이 AI 코드 그대로 쓰기

```python
# AI가 생성한 코드를 아무 검토 없이 사용
import hashlib

def save_user(username, password):
    # AI가 생성한 코드: SHA-256으로 비밀번호 해시
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    db.save(username, password_hash)
    # 문제: SHA-256은 비밀번호 저장에 부적합
    # GPU로 초당 수십억 번 시도 가능 — 레인보우 테이블 공격에 취약
```

### After: CIA와 위협 모델을 알고 코드 검토하기

```python
# 보안 기초를 알면 AI 코드의 문제를 바로 발견
import bcrypt

def save_user(username, password):
    # 기밀성(C): 비밀번호는 의도적으로 느린 해시 함수 필요
    # 위협(T): 데이터베이스 유출 시 크래킹 공격
    # 통제(Control): bcrypt, argon2처럼 salt + 느린 해시 사용
    password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt(12))
    db.save(username, password_hash)
```

---

## CIA 트라이어드: 보안의 세 축

정보보안의 모든 통제는 CIA 세 축 중 하나 이상을 지키기 위해 존재합니다.

| 축 | 의미 | 바이브코딩 예시 |
| --- | --- | --- |
| 기밀성(Confidentiality) | 권한 있는 사람만 정보를 볼 수 있어야 한다 | AI가 만든 API 응답에서 불필요한 필드 노출 확인 |
| 무결성(Integrity) | 데이터가 의도치 않게 바뀌지 않아야 한다 | AI가 만든 DB 쿼리에서 입력값 검증 여부 확인 |
| 가용성(Availability) | 필요할 때 시스템이 동작해야 한다 | AI가 만든 코드에 레이트 리밋 부재 확인 |

**바이브코딩 관점에서:** AI가 생성한 코드를 받았을 때 "이 코드는 CIA 중 어떤 축을 다루는가?"를 먼저 물어보세요. 그 답이 없거나 모호하다면 보안을 고려하지 않은 코드일 가능성이 높습니다.

---

## 위협 모델링: AI 코드에 STRIDE 적용하기

STRIDE는 여섯 가지 위협 범주로 AI 생성 코드의 빈 구멍을 빠르게 찾는 체크리스트입니다.

| STRIDE | 위협 | AI 코드에서 자주 나타나는 패턴 |
| --- | --- | --- |
| Spoofing | 다른 사람인 척 속이기 | 인증 없는 API 엔드포인트 |
| Tampering | 데이터 변조 | 서버에서 입력값 검증 누락 |
| Repudiation | 행위 부인 | 감사 로그 미생성 |
| Information Disclosure | 정보 유출 | 에러 메시지에 스택 트레이스 포함 |
| Denial of Service | 서비스 거부 | 레이트 리밋 없는 엔드포인트 |
| Elevation of Privilege | 권한 상승 | 권한 검사 누락 |

```python
# AI가 만든 사용자 조회 API — STRIDE로 점검
@app.route("/user/<int:user_id>")
def get_user(user_id):
    user = db.query(f"SELECT * FROM users WHERE id={user_id}")
    return jsonify(user)

# Spoofing: 로그인 여부 확인 없음 (인증 미처리)
# Tampering: f-string 쿼리 → SQL 인젝션 가능
# Information Disclosure: SELECT * 로 비밀번호 해시까지 반환 가능
# Elevation: 다른 사용자의 정보도 조회 가능 (인가 미처리)
```

---

## 위험 평가: 어디서부터 고쳐야 할까요?

AI가 만든 코드 전체를 다 고칠 수는 없습니다. 우선순위가 필요합니다.

```python
# 간단한 위험 점수 계산
def risk_score(likelihood, impact):
    """가능성(1-5) × 영향(1-5) = 위험 점수"""
    return likelihood * impact

# AI가 만든 코드의 대표적인 위험들
risks = [
    ("SQL 인젝션 (f-string 쿼리)", risk_score(4, 5)),       # 20
    ("비밀번호 SHA-256 해시", risk_score(3, 5)),             # 15
    ("레이트 리밋 없는 로그인 API", risk_score(4, 3)),       # 12
    ("에러 메시지에 스택 트레이스", risk_score(3, 3)),       # 9
]

for name, score in sorted(risks, key=lambda x: x[1], reverse=True):
    print(f"{score:3d} | {name}")
```

출력:
```
 20 | SQL 인젝션 (f-string 쿼리)
 15 | 비밀번호 SHA-256 해시
 12 | 레이트 리밋 없는 로그인 API
  9 | 에러 메시지에 스택 트레이스
```

높은 점수부터 먼저 고칩니다. AI 코드를 배포 전에 전부 다시 짤 필요는 없습니다. 위험 순서대로 중요한 것부터 고치면 됩니다.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| "AI가 만들었으니 안전하겠지" | AI는 보안을 자동으로 보장하지 않는다 | STRIDE 체크리스트로 직접 점검 |
| 모든 위협을 동등하게 취급 | 우선순위 없이는 아무것도 고치지 못한다 | 가능성 × 영향도 점수로 정렬 |
| 보안을 배포 후에 추가 | 배포 후 수정 비용이 10배 이상 올라간다 | 설계 단계에서 CIA 축 확인 |
| CIA 중 하나만 신경 쓰기 | 무결성을 놓치면 암호화도 무의미해진다 | 세 축을 동시에 점검 |

---

## AI 팁: AI에게 보안을 물어보는 법

1. **직접 물어보기**: "이 코드에 SQL 인젝션 취약점이 있나요?"라고 물으면 AI가 답해줍니다.
2. **STRIDE 요청**: "이 API를 STRIDE로 점검해주세요"라고 하면 체계적인 분석이 나옵니다.
3. **CIA 검토 요청**: "이 코드에서 기밀성, 무결성, 가용성 측면에서 문제가 될 부분을 알려주세요"라고 해보세요.
4. **자동 신뢰 금지**: AI의 보안 분석도 완벽하지 않습니다. 결과를 참고용으로만 사용하고 직접 확인하세요.

---

## 실전 체크리스트

- [ ] AI가 만든 코드에서 CIA 세 축이 어떻게 다뤄지는지 확인했다
- [ ] STRIDE 여섯 항목 중 하나라도 적용해봤다
- [ ] 위협 항목에 가능성과 영향도 점수를 매겨봤다
- [ ] 가장 위험 점수가 높은 항목을 먼저 수정했다
- [ ] "AI가 만들었으니 안전하다"는 생각을 경계하고 있다
- [ ] 보안 검토를 배포 전 체크리스트에 추가했다

---

## 처음 질문으로 돌아가기

- **정보보안은 정확히 무엇을 뜻할까요?**
  기밀성, 무결성, 가용성을 지키기 위해 위협을 식별하고 위험을 줄이는 의사결정의 연속입니다. AI가 코드를 만들어줘도 이 판단은 개발자가 직접 내려야 합니다.

- **STRIDE 체크리스트를 AI 생성 코드에 어떻게 적용할까요?**
  AI가 만든 코드의 각 API 엔드포인트마다 STRIDE 여섯 항목을 한 줄씩 점검합니다. Spoofing(인증 확인?), Tampering(입력 검증?), Repudiation(로그 남김?), Information Disclosure(불필요한 정보 노출?), DoS(레이트 리밋?), Elevation(권한 검사?)을 순서대로 물어보면 됩니다.

- **위험 우선순위를 정하지 않으면 무슨 일이 생길까요?**
  모든 위협을 동시에 고치려다 아무것도 못 고치는 상황이 됩니다. 가능성 × 영향도 점수를 매기고 높은 것부터 하나씩 수정하는 것이 현실적인 접근입니다.

---

## 정리

정보보안의 출발점은 CIA 트라이어드와 위협 모델링입니다. AI가 코드를 생성해준다고 해서 보안이 자동으로 따라오지는 않습니다. STRIDE 체크리스트로 AI 생성 코드를 점검하고, 위험 점수로 우선순위를 정해 중요한 것부터 수정하는 습관이 바이브코딩 개발자에게 가장 필요한 보안 기초입니다. 다음 글에서는 가장 자주 빠지는 보안 취약점인 인증과 인가를 다룹니다.

---

## 참고 자료

- [OWASP Threat Modeling](https://owasp.org/www-community/Threat_Modeling)
- [Microsoft STRIDE](https://learn.microsoft.com/en-us/azure/security/develop/threat-modeling-tool-threats)
- [NIST SP 800-30 Risk Assessment](https://csrc.nist.gov/publications/detail/sp/800-30/rev-1/final)
- [AWS Well-Architected Security Pillar](https://docs.aws.amazon.com/wellarchitected/latest/security-pillar/welcome.html)

---

<!-- toc:begin -->
## 시리즈 목차

- **바이브코딩을 위한 정보 보안 기초 (1/10): 정보보안이란 무엇인가? (현재 글)**
- 바이브코딩을 위한 정보 보안 기초 (2/10): 인증과 인가
- 바이브코딩을 위한 정보 보안 기초 (3/10): 암호화와 해시
- 바이브코딩을 위한 정보 보안 기초 (4/10): TLS와 인증서
- 바이브코딩을 위한 정보 보안 기초 (5/10): 웹 보안 기초
- 바이브코딩을 위한 정보 보안 기초 (6/10): SQL 인젝션과 XSS
- 바이브코딩을 위한 정보 보안 기초 (7/10): 비밀 정보 관리
- 바이브코딩을 위한 정보 보안 기초 (8/10): 권한 최소화
- 바이브코딩을 위한 정보 보안 기초 (9/10): 로그와 감사
- 바이브코딩을 위한 정보 보안 기초 (10/10): 보안 사고 대응
<!-- toc:end -->

Tags: 바이브코딩, 정보보안, CIA트라이어드, 위협모델링, STRIDE, AI보안
