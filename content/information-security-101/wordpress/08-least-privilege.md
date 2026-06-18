---
title: "바이브코딩을 위한 Information Security 기초 (8/10): 권한 최소화"
series: information-security-101
episode: 8
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Security
  - LeastPrivilege
  - IAM
  - ZeroTrust
---

# 바이브코딩을 위한 Information Security 기초 (8/10): 권한 최소화

이 글은 "바이브코딩을 위한 Information Security 기초" 시리즈의 8번째 글입니다.

---

바이브코딩에서 AI는 IAM 정책과 권한 설정을 빠르게 만들어 줍니다. 하지만 편하다는 이유로 과한 권한을 열어 두면 평소에는 아무 일도 없어 보이지만, 침해가 발생하는 순간 그 편의가 그대로 폭발 반경이 됩니다.

보안 사고를 완전히 막을 수는 없습니다. 대신 사고가 났을 때 얼마나 멀리 번지는지는 설계로 줄일 수 있습니다. 그 중심에 있는 원칙이 권한 최소화입니다. 서비스 하나가 뚫렸을 때 전체 클러스터가 넘어갈지, 해당 서비스 자원만 영향을 받을지는 권한 설계에서 갈립니다.

권한 최소화는 권한을 적게 주는 것이 아니라 "이 사용자/서비스가 정말 이 작업을 지금 이 환경에서 해야 하는가"를 매 요청마다 확인하는 메커니즘입니다.

IAM 정책, RBAC, ABAC, 제로 트러스트를 중심으로 권한 최소화를 정리합니다.

> **핵심 인사이트:** 권한은 많을수록 좋은 것이 아니라, 필요한 만큼만 열려 있을수록 안전합니다. 모든 권한은 명시적으로 부여되고 추적 가능해야 합니다.

## 이 글에서 다룰 문제

- 권한 최소화 원칙은 정확히 무엇을 뜻할까요?
- IAM 정책에서 허용과 거부는 어떻게 설계해야 할까요?
- RBAC, ABAC는 언제 구분해서 쓸까요?
- 제로 트러스트는 기존 경계 보안과 무엇이 다를까요?
- AI가 만든 IAM 설정에서 확인해야 할 것은 무엇인가요?

## 권한 최소화 핵심 패턴

```json
// AWS IAM 최소 권한 정책 예시
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject"
      ],
      "Resource": "arn:aws:s3:::my-app-bucket/uploads/*",
      "Condition": {
        "StringEquals": {
          "s3:prefix": "uploads/"
        }
      }
    }
  ]
}
// 나쁜 예: "s3:*" + "*" (전체 S3 접근)
```

```python
# RBAC 구현 예시
from enum import Enum

class Role(Enum):
    VIEWER = "viewer"   # 읽기만
    EDITOR = "editor"   # 읽기 + 쓰기
    ADMIN = "admin"     # 전체 (최소 사람에게만)

PERMISSIONS = {
    Role.VIEWER: {"read"},
    Role.EDITOR: {"read", "write"},
    Role.ADMIN: {"read", "write", "delete", "admin"},
}

def check_permission(user_role: Role, required_action: str) -> bool:
    allowed = PERMISSIONS.get(user_role, set())
    return required_action in allowed

# 정기 권한 검토: 사용하지 않는 권한 회수
def audit_unused_permissions(user_id: str, last_access_days: int = 90):
    """90일 이상 미사용 권한 회수 대상 식별"""
    pass
```

## 변경 전후 비교

**Before: 광범위한 권한 설정**
```text
- IAM에 "s3:*" + "*" (전체 S3 접근)
- 모든 개발자가 Admin 역할
- 서비스 계정이 프로덕션 DB 삭제 권한 보유
- 권한 검토 없이 계속 누적
```

**After: 최소 권한 설계**
```text
- 서비스별 필요한 Action/Resource만 허용
- 역할 기반(RBAC)으로 업무별 권한 분리
- 서비스 계정은 해당 서비스 자원만 접근
- 분기별 미사용 권한 회수 검토
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| "편의"를 위한 광범위 권한 | 침해 시 폭발 반경이 최대 | 작업별 최소 권한, 필요 시 상향 |
| 서비스 계정에 사람 권한 부여 | 자동화 실수가 전체 영향 | 서비스 계정은 서비스 자원만 |
| 권한 정기 검토 없음 | 미사용 권한 누적 | 분기별 권한 감사 |
| 모든 개발자가 Admin | 실수 하나가 치명적 | 최소한 "개발/운영 Admin" 분리 |
| 거부 정책 없이 허용만 | 누락 항목이 자동 허용 | 기본 거부 + 명시적 허용 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"S3 버킷에 대한 최소 권한 IAM 정책을 만들어줘.
uploads/ 경로에만 GET/PUT 허용,
DELETE는 절대 안 되고,
특정 VPC에서만 접근 가능해야 해"

# AI 결과물 검증 체크포인트:
# - Action에 와일드카드(*)가 없는가?
# - Resource가 특정 ARN으로 제한되어 있는가?
# - Condition이 추가 제약을 걸고 있는가?
# - 불필요한 권한이 포함되어 있지 않은가?
```

## 운영 체크리스트

- [ ] 모든 IAM 정책에 와일드카드(*) 대신 구체적인 Action/Resource가 있다
- [ ] 서비스 계정이 해당 서비스 자원만 접근한다
- [ ] 분기별 권한 검토와 미사용 권한 회수를 실시한다
- [ ] 모든 권한 변경이 감사 로그에 기록된다
- [ ] Admin 계정은 MFA가 강제되어 있다

## 처음 질문으로 돌아가기

- **권한 최소화 원칙이란?** 작업 수행에 필요한 최소 권한만 부여하는 원칙입니다. 과한 권한은 침해 시 폭발 반경을 키웁니다.
- **RBAC와 ABAC의 차이는?** RBAC는 역할(Role) 기반으로 단순하고 관리하기 쉽습니다. ABAC는 속성(Attribute) 기반으로 더 세밀한 제어가 가능하지만 복잡합니다.
- **제로 트러스트란?** 내부 네트워크도 믿지 않고, 모든 요청을 인증/인가합니다. "이미 내부에 있으니 신뢰"라는 전제를 없앱니다.

## 정리

바이브코딩에서 AI가 만들어 준 IAM 정책에서 와일드카드(*) 사용, 필요 이상의 Action, Resource 제한 여부를 반드시 확인하세요. "일단 열어두고 나중에 좁히겠다"는 계획은 대부분 실행되지 않습니다. 처음부터 최소 권한으로 시작하고, 필요할 때 추가하는 방식이 안전합니다. 다음 글에서는 로그와 감사를 다룹니다.

## 참고 자료

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [Zero Trust Security — NIST](https://www.nist.gov/publications/zero-trust-architecture)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/information-security-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Information Security 기초 (1/10): 정보 보안이란 무엇인가?
- 바이브코딩을 위한 Information Security 기초 (2/10): 인증과 인가
- 바이브코딩을 위한 Information Security 기초 (3/10): 암호화와 해시
- 바이브코딩을 위한 Information Security 기초 (4/10): TLS와 인증서
- 바이브코딩을 위한 Information Security 기초 (5/10): 웹 보안 기초
- 바이브코딩을 위한 Information Security 기초 (6/10): SQL Injection과 XSS
- 바이브코딩을 위한 Information Security 기초 (7/10): 비밀 정보 관리
- **바이브코딩을 위한 Information Security 기초 (8/10): 권한 최소화 (현재 글)**
- 바이브코딩을 위한 Information Security 기초 (9/10): 로그와 감사
- 바이브코딩을 위한 Information Security 기초 (10/10): 보안 사고 대응
<!-- toc:end -->

Tags: 바이브코딩, Security, LeastPrivilege, IAM, ZeroTrust
