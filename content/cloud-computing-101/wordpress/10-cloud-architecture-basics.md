---
title: "바이브코딩을 위한 Cloud Computing 기초 (10/10): Cloud Architecture 기초"
series: cloud-computing-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Cloud
  - Architecture
  - WellArchitected
  - AWS
---

# 바이브코딩을 위한 Cloud Computing 기초 (10/10): Cloud Architecture 기초

이 글은 "바이브코딩을 위한 Cloud Computing 기초" 시리즈의 마지막 글입니다.

---

바이브코딩에서 AI는 Terraform 코드와 아키텍처 다이어그램을 빠르게 만들어 줍니다. 하지만 같은 기능이라도 아키텍처에 따라 비용이 몇 배 차이 날 수 있고, 장애의 범위도 달라질 수 있습니다. 컴퓨트, 스토리지, 네트워크, 보안, 모니터링, 비용은 각각 따로 존재하는 지식이 아닙니다. 실제 시스템에서는 이 조각들이 한 구조 안에서 함께 움직입니다.

좋은 아키텍처는 화려한 서비스 조합이 아니라 변경이 안전하고, 장애가 국소화되며, 운영이 반복 가능하다는 점에서 드러납니다. 단일 서버에 묶인 시스템은 작은 변경도 두렵고, 반대로 계층이 분리된 구조는 변경과 복구가 훨씬 안전합니다.

AI가 만들어 준 IaC 코드에서 Multi-AZ 구성 여부, Stateless 앱 계층 설계, Design for Failure 패턴 적용을 확인해야 합니다. 아키텍처는 추상적인 다이어그램이 아니라 실제 운영 비용과 팀 생산성을 결정하는 선택의 집합입니다.

Well-Architected의 여섯 가지 관점을 기준으로, 앞선 내용이 하나의 클라우드 아키텍처로 어떻게 이어지는지 정리합니다.

> **핵심 인사이트:** 좋은 아키텍처는 완벽한 설계가 아니라, 운영 과정에서 계속 배우고 개선하는 문화입니다. Well-Architected 6개 기둥은 체크리스트보다 설계 리뷰 대화 도구에 가깝습니다.

## 이 글에서 다룰 문제

- Well-Architected의 여섯 기둥은 각각 무엇을 보라고 말할까요?
- 기본적인 다층 웹 아키텍처는 어떤 모습일까요?
- Stateless와 Stateful을 왜 분리해야 할까요?
- Design for Failure 패턴은 어떻게 적용할까요?
- AI가 만든 IaC에서 운영 관점으로 확인할 것은 무엇인가요?

## 핵심 아키텍처 패턴

```text
[사용자] → [CDN / CloudFront]
                │
                ▼
        [ALB - HTTPS 종료]
         ┌──────┴──────┐
         ▼             ▼
   [App AZ-a]    [App AZ-b]   ← Stateless Auto Scaling Group
         └──────┬──────┘
                │
      ┌─────────┼─────────┐
      ▼         ▼         ▼
 [Redis]   [RDS Multi-AZ]  [S3]
```

```python
# Well-Architected 6개 기둥 요약
pillars = {
    "운영 우수성": "IaC, 런북, 배포 파이프라인",
    "보안": "IAM 최소 권한, 전송/저장 암호화, 감사 로그",
    "신뢰성": "Multi-AZ, 자동 복구, 백업/복원 훈련",
    "성능 효율성": "적정 인스턴스, 캐싱, CDN",
    "비용 최적화": "예약 인스턴스, 태그 정책, 유휴 자원 정리",
    "지속 가능성": "적정 크기 조정, 관리형 서비스 활용",
}

# Design for Failure 핵심 패턴
patterns = ["Retry (지수 백오프)", "Circuit Breaker", "Timeout", "Fallback"]
```

## 변경 전후 비교

**Before: 단일 서버 구조**
```text
- 모놀리식 앱이 단일 서버 한 대에 묶여 있음
- 장애 하나가 전체 장애
- 수동 콘솔 변경으로 인프라 관리
- 백업은 있지만 복구 연습 없음
```

**After: 다층 분산 구조**
```text
- Stateless 앱 계층 + Multi-AZ 데이터베이스
- AZ 장애 시 트래픽이 다른 AZ로 자동 전환
- IaC(Terraform)로 환경 코드화
- 분기별 복구 훈련 일정 운영
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 앱 내부 메모리에 상태 저장 후 수평 확장 시도 | 인스턴스마다 상태가 달라 오작동 | 세션을 Redis로 외부화, Stateless 설계 |
| 데이터베이스를 Single-AZ로 운영 | AZ 장애 시 30분 이상 다운타임 | Multi-AZ 기본 설정 |
| IaC 없이 수동 변경 | 재현 불가, 드리프트 누적 | Terraform으로 모든 변경 코드화 |
| 백업만 하고 복구 연습 안 함 | 장애 시 복구 절차에서 실패 | 분기별 실제 복원 훈련 |
| 외부 호출에 재시도 없음 | 일시적 장애가 전체 서비스 장애로 번짐 | Retry + Circuit Breaker 적용 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"3-tier 웹 아키텍처를 Terraform으로 만들어줘.
Multi-AZ RDS, Stateless 앱 계층, Auto Scaling,
ALB HTTPS 종료, S3 버저닝까지 포함해야 해.
Well-Architected 6개 기둥 기준으로 확인할 항목도 알려줘"

# AI 결과물 검증 체크포인트:
# - Multi-AZ: RDS, 서브넷이 2개 AZ에 분산되어 있는가
# - Stateless: 세션이 외부 스토리지(Redis, DB)에 저장되는가
# - IaC: 수동 콘솔 변경 없이 코드로 재현 가능한가
# - Design for Failure: retry, timeout, circuit breaker가 있는가
```

## 운영 체크리스트

- [ ] Multi-AZ 구성이 적용되어 있다
- [ ] IaC로 환경을 재현할 수 있다
- [ ] 복원 훈련 일정이 있다
- [ ] Well-Architected 6대 기둥 기준 점검을 분기마다 한다
- [ ] Design for Failure 패턴(retry, circuit breaker, timeout, fallback)이 적용되어 있다
- [ ] 헬스 체크 엔드포인트가 핵심 의존성까지 확인한다
- [ ] ADR로 주요 아키텍처 결정을 기록하고 있다

## 처음 질문으로 돌아가기

- **Well-Architected의 여섯 기둥은?** 운영 우수성, 보안, 신뢰성, 성능 효율성, 비용 최적화, 지속 가능성입니다. 각 기둥은 정답이 아니라 설계 리뷰에서 물어야 할 질문 영역입니다.
- **다층 웹 아키텍처의 핵심은?** CDN이 정적 콘텐츠를 흡수하고, ALB가 요청을 분산하며, Stateless 앱 계층이 Auto Scaling하고, Multi-AZ 데이터 계층이 가용성을 확보합니다.
- **Stateless와 Stateful을 왜 분리해야 할까요?** 앱 계층이 Stateless해야 Auto Scaling이 안전합니다. 상태는 Redis나 DB에 외부화하고, 앱 서버는 언제든 추가/제거 가능해야 합니다.

## 정리

바이브코딩에서 AI가 만들어 준 IaC 코드에서 Multi-AZ 설정, Stateless 앱 계층, Design for Failure 패턴, IaC 기반 배포 여부를 반드시 확인하세요. 좋은 아키텍처는 처음부터 완벽할 필요가 없습니다. 서비스가 성장하고 문제가 드러나면서 단계적으로 개선하는 것이 현실적입니다. Cloud Computing 101 시리즈를 통해 클라우드 기초를 갖추셨기를 바랍니다.

## 참고 자료

- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Twelve-Factor App](https://12factor.net/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 Cloud Computing 기초 (1/10): Cloud Computing이란 무엇인가?
- 바이브코딩을 위한 Cloud Computing 기초 (2/10): IaaS, PaaS, SaaS
- 바이브코딩을 위한 Cloud Computing 기초 (3/10): Region과 Availability Zone
- 바이브코딩을 위한 Cloud Computing 기초 (4/10): Compute
- 바이브코딩을 위한 Cloud Computing 기초 (5/10): Storage
- 바이브코딩을 위한 Cloud Computing 기초 (6/10): Network
- 바이브코딩을 위한 Cloud Computing 기초 (7/10): Identity와 Security
- 바이브코딩을 위한 Cloud Computing 기초 (8/10): Monitoring
- 바이브코딩을 위한 Cloud Computing 기초 (9/10): Cost Management
- **바이브코딩을 위한 Cloud Computing 기초 (10/10): Cloud Architecture 기초 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, Cloud, Architecture, WellArchitected, AWS
