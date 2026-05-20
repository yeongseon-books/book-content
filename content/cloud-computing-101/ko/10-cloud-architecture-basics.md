---
series: cloud-computing-101
episode: 10
title: "Cloud Computing 101 (10/10): Cloud Architecture 기초"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Cloud
  - Architecture
  - WellArchitected
  - AWS
  - DevOps
seo_description: Well-Architected 5대 기둥과 기본 웹 아키텍처를 한 그림으로 정리합니다.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (10/10): Cloud Architecture 기초

이 시리즈에서 살펴본 컴퓨트, 스토리지, 네트워크, 보안, 모니터링, 비용은 각각 따로 존재하는 지식이 아닙니다. 실제 시스템에서는 이 조각들이 한 구조 안에서 함께 움직입니다.

좋은 아키텍처는 화려한 서비스 조합이 아니라 변경이 안전하고, 장애가 국소화되며, 운영이 반복 가능하다는 점에서 드러납니다. 그래서 마지막 글에서는 기능 목록보다 구조적 원칙에 집중하는 편이 더 중요합니다.

이 글은 Cloud Computing 101 시리즈의 마지막 글입니다.

여기서는 Well-Architected의 다섯 가지 관점을 기준으로, 앞선 내용이 하나의 클라우드 아키텍처로 어떻게 이어지는지 정리하겠습니다.

## 먼저 던지는 질문

- Well-Architected의 다섯 기둥은 각각 무엇을 보라고 말할까요?
- 기본적인 다층 웹 아키텍처는 어떤 모습일까요?
- Stateless와 Stateful을 왜 분리해야 할까요?

## 큰 그림

![Cloud Computing 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/10/10-01-concept-at-a-glance.ko.png)

*Cloud Computing 101 10장 흐름 개요*

이 그림에서는 Cloud Architecture 기초를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> Cloud Architecture 기초의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 중요한가

같은 기능이라도 아키텍처에 따라 비용이 몇 배 차이 날 수 있고, 장애의 범위도 달라질 수 있습니다. 단일 서버에 묶인 시스템은 작은 변경도 두렵고, 반대로 계층이 분리된 구조는 변경과 복구가 훨씬 안전합니다.

아키텍처는 추상적인 다이어그램이 아니라 실제 운영 비용과 팀 생산성을 결정하는 선택의 집합입니다. 그래서 마지막 단계에서는 각 서비스 지식을 한 그림으로 묶어 보는 훈련이 필요합니다.

## 한눈에 보는 개념

이 그림은 전형적인 다층 웹 구조를 보여 줍니다. CDN이 정적 콘텐츠와 글로벌 읽기 트래픽을 흡수하고, ALB가 요청을 분산하며, 앱 계층은 Stateless하게 확장되고, 데이터 계층은 캐시·DB·오브젝트 스토리지로 역할이 나뉩니다.

## 핵심 용어

- **Well-Architected**: AWS가 정리한 설계 모범 사례 프레임워크입니다.
- **Stateless**: 서버가 클라이언트 상태를 내부에 오래 들고 있지 않는 구조입니다.
- **IaC**: 인프라를 코드로 표현하는 방식입니다.
- **Loose coupling**: 컴포넌트를 큐나 API로 느슨하게 연결하는 방식입니다.
- **Idempotent**: 같은 요청을 반복해도 안전한 성질입니다.

## Before / After

**Before**에서는 모놀리식 애플리케이션이 단일 서버 한 대에 묶여 있습니다. 변경이 무섭고, 장애 하나가 전체 장애가 됩니다.

**After**에서는 Stateless 앱 계층과 Multi-AZ 데이터베이스, IaC 기반 배포를 조합합니다. 구조가 나뉘면 변경과 복구가 모두 안전해집니다.

## 실습: 다층 웹 아키텍처 의사 코드

### 1단계 — IaC 골조

```python
def vpc(): return {"cidr": "10.0.0.0/16", "azs": 2}
def subnets(): return ["public-a", "public-b", "private-a", "private-b"]
```

### 2단계 — 컴퓨트

```python
def asg(min_, max_): return {"min": min_, "max": max_, "policy": "cpu>60"}
```

### 3단계 — 데이터

```python
def rds(): return {"engine": "postgres", "multi_az": True, "backup_days": 7}
def cache(): return {"engine": "redis", "nodes": 2}
```

### 4단계 — 객체와 큐

```python
def s3(): return {"versioning": True, "lifecycle": "to-glacier-90d"}
def queue(): return {"visibility_timeout": 30, "dlq": True}
```

### 5단계 — 라우팅

```python
def alb(): return {"listeners": [{"port": 443, "tls": True}], "target": "asg"}
```

이 코드는 실제 Terraform이 아니지만, 클라우드 아키텍처를 어떤 식으로 계층별로 생각해야 하는지 잘 보여 줍니다. 네트워크, 컴퓨트, 데이터, 비동기 처리, 라우팅이 각각 분리되어 있어야 구조를 바꾸거나 검증하기 쉬워집니다.

## 이 코드에서 먼저 봐야 할 점

- Multi-AZ는 선택 기능이 아니라 기본 전제에 가깝습니다.
- DLQ는 재시도 실패를 흡수하는 안전망입니다.
- ASG를 제대로 쓰려면 앱이 Stateless해야 합니다.

## 이 설계를 실제로 검증하는 순서

아키텍처 글에서는 코드가 실행되느냐만큼 설계 질문에 답할 수 있느냐가 중요합니다. 각 계층을 따로 읽지 말고 "이 구조가 장애, 변경, 복구에 어떤 행동을 가능하게 하는가"를 기준으로 검토해 보세요.

**Expected output:**

- 앱 계층을 늘려도 세션이나 상태가 깨지지 않는다는 설명이 가능해야 합니다.
- 데이터 계층에서 어떤 자원이 Multi-AZ인지, 어떤 자원이 백업과 복원을 맡는지 구분할 수 있어야 합니다.
- 큐와 DLQ를 둔 이유를 "재시도 실패를 격리하기 위해서"라고 설명할 수 있어야 합니다.

### 설계 리뷰에서 먼저 물을 질문

- 이 구조에서 단일 실패 지점은 어디에 남아 있는가.
- 수동 변경이 개입되는 구간은 어디이며, IaC로 어떻게 줄일 수 있는가.
- 비용 최적화와 신뢰성 최적화가 충돌할 때 어떤 원칙으로 우선순위를 정할 것인가.

## Well-Architected 다섯 기둥은 어떻게 쓰나

이 프레임워크는 정답 목록이라기보다 대화를 위한 질문 세트에 가깝습니다. 운영 우수성에서는 변경과 대응 절차를 보고, 보안에서는 권한과 암호화를 보고, 신뢰성에서는 장애 대응과 복구를 보고, 성능 효율성에서는 자원 선택과 확장 전략을 보고, 비용 최적화에서는 낭비를 줄이는 구조를 봅니다.

강한 팀은 이 다섯 기둥을 분기마다 점검합니다. 모든 항목을 완벽히 맞추는 것이 목적이 아니라, 지금 우리 시스템이 어떤 축에서 취약한지 드러내는 것이 목적입니다.

## 자주 하는 실수 5가지

1. 상태를 내부 메모리에 둔 앱을 그대로 수평 확장하려고 합니다.
2. 데이터베이스를 Single-AZ로 운영합니다.
3. IaC 없이 수동 변경에 의존합니다.
4. 외부 호출에 재시도를 넣지 않습니다.
5. 백업은 하지만 복구 연습을 하지 않습니다.

## 실무에서는 이렇게 생각합니다

- Well-Architected는 체크리스트보다 대화 도구에 가깝습니다.
- 모든 품질 중에서도 변경 안전성이 특히 중요합니다.
- 백업보다 복원 훈련이 더 현실적인 검증입니다.
- 작게 시작하고 필요할 때 모듈화하는 편이 낫습니다.
- 문서와 런북도 코드와 함께 출하되어야 합니다.

## 체크리스트

- [ ] Multi-AZ 구성이 적용되어 있는가.
- [ ] IaC로 환경을 재현할 수 있는가.
- [ ] 복원 훈련 일정이 있는가.
- [ ] 5대 기둥 기준 점검을 분기마다 하는가.

## 연습 문제

1. Well-Architected의 다섯 기둥을 모두 적어 보세요.
2. 애플리케이션을 Stateless하게 만드는 대표 기법 하나를 설명해 보세요.
3. IaC가 수동 변경보다 안전한 이유를 한 줄로 적어 보세요.

## 정리 및 다음 단계

여기까지가 Cloud Computing 101의 마무리입니다. 이제 클라우드를 하나의 서비스 목록이 아니라, 운영·보안·신뢰성·성능·비용을 함께 조립하는 설계 문제로 볼 수 있어야 합니다. 다음 시리즈에서는 Containers 101, Kubernetes 101, Serverless 101처럼 더 구체적인 실행 추상화로 들어가게 됩니다.

## 처음 질문으로 돌아가기

- **Well-Architected의 다섯 기둥은 각각 무엇을 보라고 말할까요?**
  - 본문의 기준은 Cloud Architecture 기초를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **기본적인 다층 웹 아키텍처는 어떤 모습일까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Stateless와 Stateful을 왜 분리해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Cloud Computing 101 (1/10): Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region과 Availability Zone](./03-region-and-availability-zone.md)
- [Cloud Computing 101 (4/10): Compute](./04-compute.md)
- [Cloud Computing 101 (5/10): Storage](./05-storage.md)
- [Cloud Computing 101 (6/10): Network](./06-network.md)
- [Cloud Computing 101 (7/10): Identity와 Security](./07-identity-and-security.md)
- [Cloud Computing 101 (8/10): Monitoring](./08-monitoring.md)
- [Cloud Computing 101 (9/10): Cost Management](./09-cost-management.md)
- **Cloud Architecture 기초 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [AWS Well-Architected Framework](https://docs.aws.amazon.com/wellarchitected/latest/framework/welcome.html)
- [Multi-AZ design](https://docs.aws.amazon.com/whitepapers/latest/aws-overview/global-infrastructure.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Twelve-Factor App](https://12factor.net/)

Tags: Cloud, Architecture, WellArchitected, AWS, DevOps
