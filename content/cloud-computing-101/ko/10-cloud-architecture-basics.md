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

고가용성(High Availability)은 시스템이 장애를 견디고 계속 동작하는 능력입니다. 확장성(Scalability)은 트래픽 증가에 따라 성능을 유지하는 능력입니다. 느슨한 결합(Loose Coupling)은 서비스들이 독립적으로 동작하도록 설계하는 원칙입니다. 오토메이션(Automation)은 반복적인 운영 작업을 자동화해 사람의 실수를 줄입니다.

> 좋은 아키텍처는 완벽한 설계가 아니라, 운영 과정에서 계속 배우고 개선하는 문화입니다.

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

각 아키텍처 원칙을 처음부터 모두 구현할 필요는 없습니다. 서비스가 성장하고 문제가 드러나면서 단계적으로 개선하는 게 현실적입니다.

토이 프로젝트는 단일 VM도 충분할 수 있습니다. 팀이 성장하고 트래픽이 증가하면 그때 Multi-AZ, 로드 밸런싱, 캐싱을 추가합니다.
  - 본문의 기준은 Cloud Architecture 기초를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
아키텍처는 비즈니스 요구사항, 팀 역량, 예산 제약을 모두 고려해야 합니다. 기술적으로 완벽하지만 유지보수 불가능한 설계는 실무에서 실패합니다.
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Stateless와 Stateful을 왜 분리해야 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

## 멀티클라우드 비교와 마이그레이션 체크리스트

| 항목 | 단일 클라우드 | 멀티클라우드 |
| --- | --- | --- |
| 초기 구축 속도 | 빠름 | 느림 |
| 운영 복잡도 | 중간 | 높음 |
| 공급사 장애 분산 | 제한적 | 높음 |
| 기술 표준화 필요성 | 보통 | 매우 높음 |
| 인력 요구 | 보통 | 높음 |

| 단계 | 확인 항목 |
| --- | --- |
| 발견(Discover) | 현재 자산, 의존성, 데이터 흐름 목록화 |
| 분류(Assess) | Rehost/Replatform/Refactor 대상 분류 |
| 설계(Design) | 네트워크, IAM, 관측, 백업 표준 정의 |
| 이전(Migrate) | 파일럿 워크로드로 절차 검증 |
| 안정화(Operate) | 비용/성능/보안 지표 기반 개선 루프 |

```yaml
architecture_review:
  reliability:
    multi_az: true
    backup_restore_tested: true
  security:
    least_privilege: true
    key_rotation_days: 90
  performance:
    autoscaling_enabled: true
    p95_latency_target_ms: 500
  cost:
    monthly_budget_usd: 1000
    commitment_review_cycle: quarterly
```



### 운영 리뷰 질문 세트

아래 질문은 설계 문서 리뷰와 장애 회고에서 반복적으로 사용할 수 있는 체크 질문입니다.

| 질문 | 확인 포인트 | 흔한 실패 |
| --- | --- | --- |
| 책임 경계가 명확한가 | 공급자/사용자 책임 문서화 | "누가 고칠지" 미정 상태 |
| 변경 영향이 예측 가능한가 | 롤백/격리 경로 존재 | 단일 경로 의존 |
| 비용 신호가 보이는가 | 태그/예산/알림 연동 | 비용 급증 사후 인지 |
| 보안 기준이 자동화되었는가 | 정책 코드화, 주기 점검 | 수동 예외 누적 |
| 복구 가능성이 검증되었는가 | 정기 복원 리허설 | 백업만 있고 복원 실패 |

이 질문 세트는 기술 스택과 무관하게 적용할 수 있습니다. 중요한 것은 문장으로 "대답할 수 있는가"가 아니라, 로그/정책/테스트로 "증명할 수 있는가"입니다.

### 팀 운영 계약 예시

```yaml
team_operating_contract:
  deploy:
    requires_review: true
    rollback_plan_required: true
  security:
    least_privilege_default: true
    mfa_for_privileged_actions: true
  reliability:
    monthly_recovery_drill: true
    incident_postmortem_required: true
  cost:
    budget_alert_thresholds: [50, 80, 100]
    untagged_resource_policy: deny
```

운영 계약을 명시하면 담당자가 바뀌어도 품질 기준이 유지됩니다. 클라우드의 핵심은 리소스를 빨리 만드는 능력이 아니라, 같은 품질을 반복해서 만드는 능력입니다. 따라서 이 문서와 같은 계약은 초기에 작게 시작해도 반드시 있어야 하며, 분기 단위로 업데이트하는 루틴을 두는 편이 안정적입니다.

### 장애/비용/보안을 함께 보는 회고 포맷

1. 무엇이 실패했는가를 한 문장으로 기록합니다.
2. 탐지 시점과 첫 대응 시점을 분 단위로 기록합니다.
3. 영향 범위(사용자 수, 금액, 데이터 범위)를 숫자로 기록합니다.
4. 재발 방지 항목을 자동화/문서/훈련으로 분류합니다.
5. 다음 점검 날짜를 지정하고 담당자를 명시합니다.

위 다섯 단계는 단순하지만 반복 효과가 큽니다. 특히 비용 이슈도 장애와 같은 수준으로 회고에 포함하면, 기술 선택과 운영 비용을 분리해서 보는 습관을 줄일 수 있습니다.



### 실무 적용 시나리오

다음 시나리오는 교육용 예시이지만, 실제 프로젝트에서 의사결정을 정리할 때 그대로 활용할 수 있습니다.

| 상황 | 선택 | 이유 | 검증 방법 |
| --- | --- | --- | --- |
| 신규 서비스 초기 론칭 | 단순한 기본 아키텍처 + 필수 가드레일 | 속도와 안정성의 균형 | 체크리스트 기반 사전 점검 |
| 트래픽 급증 이벤트 | 자동 확장 + 임계값 알림 강화 | 수동 대응 지연 방지 | 부하 테스트 + 알람 리허설 |
| 보안 감사 대응 | 권한 축소 + 로그 보존 정책 정리 | 증빙 가능성 확보 | 감사 항목 매핑 문서 |
| 비용 급증 발생 | 태그 누락/유휴 자원 우선 정리 | 즉시 효과가 큼 | 주간 비용 리포트 비교 |

시나리오 기반으로 운영하면 기술 논의가 추상적 취향 싸움으로 흐르지 않습니다. 각 선택에 대해 "왜 이 결정을 했는가"와 "어떻게 검증할 것인가"를 짝지어 기록하면, 팀이 커져도 의사결정 품질을 유지할 수 있습니다. 또한 운영 회고에서 같은 포맷을 재사용하면 변경 누락과 책임 공백을 줄일 수 있습니다.



### 빠른 점검 메모

운영 단계에서는 정답 하나보다 반복 가능한 점검 리듬이 더 중요합니다. 배포 전 점검, 주간 운영 점검, 월간 개선 회고를 분리해 기록하면 누락이 줄어듭니다. 특히 신규 팀원이 합류할 때는 문서의 완성도보다 문서의 최신성이 더 큰 가치를 만듭니다. 따라서 작은 변경이라도 근거와 검증 결과를 함께 남기는 습관이 필요합니다.

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
