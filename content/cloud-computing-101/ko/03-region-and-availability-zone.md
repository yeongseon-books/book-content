---
series: cloud-computing-101
episode: 3
title: "Cloud Computing 101 (3/10): Region과 Availability Zone"
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
  - AWS
  - Region
  - HighAvailability
  - Architecture
seo_description: 리전과 AZ의 차이, Multi-AZ와 Multi-Region 판단 기준을 정리합니다.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (3/10): Region과 Availability Zone

같은 AWS 서비스라도 어떤 팀은 한 장애에도 멀쩡히 버티고, 어떤 팀은 바로 전체 서비스가 내려갑니다. 차이는 기능 이름보다 배치 전략에 있습니다.

클라우드에서 "어디에 둘 것인가"는 단순한 위치 선택이 아닙니다. 지연 시간, 데이터 복제 비용, 장애 범위, 복구 전략이 모두 이 결정에서 시작됩니다.

이 글은 Cloud Computing 101 시리즈의 3번째 글입니다.

여기서는 Region, Availability Zone, Edge의 차이를 정리하고, 가용성을 위해 무엇을 기본값으로 생각해야 하는지 살펴보겠습니다.

## 먼저 던지는 질문

- Region, Availability Zone, Edge는 각각 무엇을 뜻할까요?
- Multi-AZ는 정확히 무엇을 의미하고, 왜 기본값으로 봐야 할까요?
- Multi-Region은 언제 고려해야 하고, 언제 과한 선택이 될까요?

## 큰 그림

![Cloud Computing 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/03/03-01-concept-at-a-glance.ko.png)

*Cloud Computing 101 3장 흐름 개요*

모든 자원이 하나의 AZ에만 있으면 단일 장애가 곧 전체 장애가 됩니다. 데이터센터 전원 문제나 네트워크 장애 같은 사건 하나가 서비스 전체를 멈추게 만들 수 있습니다. 반대로 최소한의 Multi-AZ 구성을 갖추면 같은 리전 안에서도 훨씬 현실적인 수준의 고가용성을 확보할 수 있습니다.

> 리전은 도시 또는 대륙 규모의 위치이고, AZ는 리전 내부에서 물리적으로 분리된 장애 경계입니다. Multi-AZ 구성이 가장 기본이고, Multi-Region은 비용과 운영 복잡도를 크게 올리기 때문에 판단이 필요합니다.

## 왜 중요한가

모든 자원이 하나의 AZ에만 있으면 단일 장애가 곧 전체 장애가 됩니다. 데이터센터 전원 문제나 네트워크 장애 같은 사건 하나가 서비스 전체를 멈추게 만들 수 있습니다. 반대로 최소한의 Multi-AZ 구성을 갖추면 같은 리전 안에서도 훨씬 현실적인 수준의 고가용성을 확보할 수 있습니다.

많은 팀이 Multi-Region을 먼저 떠올리지만, 실제로는 AZ 분산이 더 기본입니다. Multi-Region은 비용과 운영 복잡도를 크게 올리는 선택이기 때문에, 언제나 첫 답이 되지는 않습니다.

## 한눈에 보는 개념

리전은 도시 또는 대륙 규모의 위치이고, AZ는 리전 내부에서 물리적으로 분리된 장애 경계입니다. Edge는 CDN이 사용자 가까이에 콘텐츠를 두는 마지막 홉입니다. 이 셋을 구분해야 지연 시간과 가용성을 같은 표 위에서 비교할 수 있습니다.

## 핵심 용어

- **Region**: 도시 또는 대륙 규모의 지리적 위치입니다.
- **AZ**: 리전 내부의 물리적으로 분리된 데이터센터 클러스터입니다.
- **Edge**: CDN의 마지막 홉입니다.
- **RTT**: 왕복 지연 시간으로, 물리 거리의 영향을 강하게 받습니다.
- **Failover**: 워크로드를 다른 AZ나 리전으로 전환하는 과정입니다.

## Before / After

**Before**에서는 EC2와 RDS가 모두 같은 `az a`에 있습니다.

**After**에서는 EC2를 `a/b/c`에 분산하고, RDS는 Multi-AZ 모드로 둡니다.

이 변화는 단순한 중복이 아닙니다. 하나의 장애가 전체 서비스로 번지지 않게 만드는 구조적 안전장치입니다.

## 실습: Python으로 가용 AZ 조회하기

### 1단계 — 클라이언트

```python
import boto3
ec2 = boto3.client("ec2", region_name="us-east-1")
```

### 2단계 — AZ 목록

```python
def list_azs():
    res = ec2.describe_availability_zones()
    return [z["ZoneName"] for z in res["AvailabilityZones"]]

print(list_azs())
```

### 3단계 — 리전 목록

```python
def list_regions():
    res = boto3.client("ec2").describe_regions()
    return [r["RegionName"] for r in res["Regions"]]

print(list_regions())
```

### 4단계 — RTT 추정

```python
def estimate_rtt(km: float) -> float:
    # fiber ~200,000 km/s, plus router overhead, round trip
    return (km / 200_000) * 2 * 1000 * 1.5  # ms
```

### 5단계 — 분산 배치

```python
def placement(azs: list[str], replicas: int) -> list[str]:
    return [azs[i % len(azs)] for i in range(replicas)]

print(placement(["a", "b", "c"], 5))
```

이 예제는 분산 배치가 추상적인 권장사항이 아니라 실제 선택 가능한 설계라는 점을 보여 줍니다. 어떤 AZ가 있고, 물리 거리가 지연 시간에 어떤 하한을 만들며, 복제본을 어떻게 흩어 놓을지 생각하는 감각이 중요합니다.

## 이 코드에서 먼저 봐야 할 점

- AZ 이름은 계정마다 다르게 매핑될 수 있습니다.
- RTT에는 물리적인 하한이 있습니다.
- 단순한 라운드로빈 분산도 생각보다 효과적입니다.

특히 첫 번째 포인트가 중요합니다. 내 계정의 `az a`와 다른 계정의 `az a`가 같은 물리 위치라고 단정하면 안 됩니다. 이름보다 장애 경계를 이해하는 편이 더 중요합니다.

## 이 예제를 실제로 검증하는 순서

리전과 AZ를 다룰 때는 문서 설명보다 실제 계정에서 보이는 목록을 먼저 보는 편이 이해에 도움이 됩니다. 특히 AZ 이름은 계정마다 다르게 매핑될 수 있으므로, 표기만 보고 같은 물리 위치라고 단정하면 안 됩니다.

```bash
python -c 'import boto3; print([z["ZoneName"] for z in boto3.client("ec2", region_name="us-east-1").describe_availability_zones()["AvailabilityZones"]])'
python -c 'import boto3; print([r["RegionName"] for r in boto3.client("ec2").describe_regions()["Regions"]][:5])'
```

**Expected output:**

- 첫 번째 명령에서는 `us-east-1a`, `us-east-1b` 같은 AZ 목록이 보여야 합니다.
- 두 번째 명령에서는 계정이 조회 가능한 리전 이름이 출력되어야 합니다.
- 이 결과를 보면 "리전 안에 여러 장애 경계가 있다"는 설명이 문서 문장이 아니라 실제 자원 구조로 연결됩니다.

### 자주 막히는 지점

- Multi-AZ를 구성했다고 해도 실제 데이터베이스나 캐시가 단일 AZ에 남아 있으면 장애 범위는 그대로입니다.
- Multi-Region은 늘 더 좋은 답이 아닙니다. 복제 비용과 운영 복잡도까지 함께 계산해야 합니다.
- RTT 계산 예제는 정확한 측정값이 아니라 물리 거리의 하한을 감 잡기 위한 도구로 보는 편이 맞습니다.

## Multi-AZ와 Multi-Region을 어떻게 나눌까

Multi-AZ는 같은 리전 안에서 장애 영역을 분리하는 방식입니다. 지연 시간 증가가 비교적 작고, 대부분의 웹 서비스에서 기본값으로 삼기 좋습니다. Multi-Region은 더 큰 장애를 견디기 위한 선택이지만, 데이터 동기화 비용과 운영 복잡도가 크게 늘어납니다.

그래서 질문 순서는 보통 이렇습니다. 먼저 AZ 분산이 되어 있는가. 그다음 RTO와 RPO 요구사항상 리전 단위 장애까지 견뎌야 하는가. 마지막으로 그 비용과 복잡도를 감당할 가치가 있는가. 이 순서가 뒤집히면 화려하지만 과한 설계가 나오기 쉽습니다.

## 자주 하는 실수 5가지

1. 단일 AZ만 사용합니다.
2. Multi-Region을 적용하면서 지연 증가 비용을 고려하지 않습니다.
3. DB Failover 테스트를 하지 않습니다.
4. 리전 간 데이터 동기화 비용을 무시합니다.
5. 글로벌 사용자에게 Edge 캐시를 활용하지 않습니다.

## 실무에서는 이렇게 생각합니다

- AZ 분산은 사치가 아니라 기본값입니다.
- Multi-Region은 큰 비용과 복잡도를 수반하는 결정입니다.
- Edge는 읽기 트래픽에 특히 강합니다.
- Failover는 패닉 상황이 아니라 정기 훈련으로 검증해야 합니다.
- 지연 시간과 일관성의 균형은 기술 문제가 아니라 비즈니스 결정이기도 합니다.

## 체크리스트

- [ ] 워크로드가 AZ에 분산되어 있는가.
- [ ] Failover가 자동화되어 있는가.
- [ ] RTO와 RPO가 정의되어 있는가.
- [ ] 연 1회 이상 재해 복구 훈련을 하는가.

## 연습 문제

1. 서울 리전과 도쿄 리전 사이에서 데이터를 동기화하는 방법 두 가지를 적어 보세요.
2. Edge 캐싱이 동적 페이지에 항상 잘 맞지 않는 이유를 설명해 보세요.
3. 의도적으로 단일 AZ를 선택할 만한 합리적 이유 하나를 떠올려 보세요.

## 정리 및 다음 단계

어디에 둘지 정했다면 이제 그 위에서 무엇을 돌릴지 판단해야 합니다. 다음 글에서는 VM, 컨테이너, 서버리스 같은 실행 모델을 다루는 Compute로 넘어가겠습니다.


## 리전/AZ 의사결정 프레임워크

리전 선택은 단순히 지도에서 가까운 위치를 고르는 작업이 아닙니다. 지연 시간, 데이터 주권, 장애 복구 전략, 비용을 함께 보는 다변수 문제입니다. 먼저 기본 비교표를 통해 어떤 지표를 같이 봐야 하는지 정리합니다.

| 항목 | 단일 AZ | Multi-AZ | Multi-Region |
| --- | --- | --- | --- |
| AZ 장애 내성 | 낮음 | 높음 | 높음 |
| 리전 장애 내성 | 낮음 | 낮음 | 높음 |
| 평균 지연 시간 증가 | 낮음 | 낮음 | 중간~높음 |
| 운영 복잡도 | 낮음 | 중간 | 높음 |
| 데이터 동기화 비용 | 낮음 | 낮음 | 높음 |
| 권장 사용 시점 | 실험/개발 | 기본 프로덕션 | 명확한 DR/규제 요구 |

대부분의 웹 서비스는 Multi-AZ를 기본값으로 두고 시작하는 편이 합리적입니다. Multi-Region은 RTO/RPO 목표가 리전 단위 장애를 반드시 포함할 때만 정당화됩니다.

### 리전 선택 기준표

| 평가 기준 | 질문 | 예시 판단 |
| --- | --- | --- |
| 사용자 지연 시간 | 핵심 사용자와 100ms 이내인가 | 한국 사용자 중심이면 ap-northeast-2 우선 |
| 데이터 주권 | 특정 국가 내 저장 의무가 있는가 | 규제 대상이면 해당 국가 리전 고정 |
| 서비스 가용성 | 필요한 관리형 서비스가 제공되는가 | 일부 리전은 최신 서비스 미지원 |
| 재해복구 전략 | 보조 리전과 거리/독립성이 충분한가 | 동일 지진대 회피 필요 |
| 비용 | 전송 단가와 컴퓨트 단가가 감당 가능한가 | 리전 간 복제 비용 사전 계산 |

### 지연 시간 개념 비교

아래 값은 실제 측정값이 아니라 설계 단계의 보수적 가정치 예시입니다.

| 경로 | 예상 RTT 범위 |
| --- | --- |
| 동일 AZ | 1~2 ms |
| 동일 리전 내 다른 AZ | 2~5 ms |
| 서울 ↔ 도쿄 | 30~60 ms |
| 서울 ↔ 미국 서부 | 120~180 ms |

데이터 일관성이 중요한 동기 호출 경로는 가능한 같은 리전 내부에 두는 편이 안전합니다. 반대로 읽기 위주의 글로벌 콘텐츠는 Edge 캐시로 분산해도 괜찮습니다.

### 배치 템플릿 예시

```yaml
placement_policy:
  primary_region: ap-northeast-2
  az_spread: 3
  app_tier:
    min_instances_per_az: 2
  db_tier:
    mode: multi_az
    cross_region_replica: ap-northeast-1
  failover:
    rto_minutes: 30
    rpo_minutes: 5
```

이 템플릿은 "어디에 배치할지"를 운영 목표와 연결합니다. 중요한 것은 기술적 가능성이 아니라 목표 복구 시간과 데이터 손실 허용 범위를 문서화하는 것입니다. 그 기준이 있어야 Multi-Region이 필요한지, 아니면 과한지 판단할 수 있습니다.

## 리전/AZ 의사결정 프레임워크

| 항목 | 단일 AZ | Multi-AZ | Multi-Region |
| --- | --- | --- | --- |
| AZ 장애 내성 | 낮음 | 높음 | 높음 |
| 리전 장애 내성 | 낮음 | 낮음 | 높음 |
| 평균 지연 시간 증가 | 낮음 | 낮음 | 중간~높음 |
| 운영 복잡도 | 낮음 | 중간 | 높음 |
| 데이터 동기화 비용 | 낮음 | 낮음 | 높음 |

| 평가 기준 | 질문 | 예시 판단 |
| --- | --- | --- |
| 사용자 지연 시간 | 핵심 사용자와 100ms 이내인가 | 한국 사용자 중심이면 ap-northeast-2 우선 |
| 데이터 주권 | 특정 국가 내 저장 의무가 있는가 | 규제 대상이면 해당 국가 리전 고정 |
| 서비스 가용성 | 필요한 관리형 서비스가 제공되는가 | 일부 리전은 최신 서비스 미지원 |
| 재해복구 전략 | 보조 리전과 거리/독립성이 충분한가 | 동일 지진대 회피 필요 |
| 비용 | 전송 단가와 컴퓨트 단가가 감당 가능한가 | 리전 간 복제 비용 사전 계산 |

```yaml
placement_policy:
  primary_region: ap-northeast-2
  az_spread: 3
  app_tier:
    min_instances_per_az: 2
  db_tier:
    mode: multi_az
    cross_region_replica: ap-northeast-1
  failover:
    rto_minutes: 30
    rpo_minutes: 5
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

## 처음 질문으로 돌아가기

- **Region, Availability Zone, Edge는 각각 무엇을 뜻할까요?**
  Region은 도시 또는 대륙 규모의 지리적 위치이고, AZ는 리전 내부의 물리적으로 분리된 데이터센터 클러스터입니다. Multi-AZ는 기본 선택지이고, Multi-Region은 극히 제한된 상황에서만 정당화됩니다.
- **Multi-AZ는 정확히 무엇을 의미하고, 왜 기본값으로 봐야 할까요?**
  Multi-AZ는 한 AZ의 장애를 견딜 수 있도록 최소 2개 이상의 AZ에 리소스를 분산하는 구성입니다. 이것이 고가용성 아키텍처의 첫 단계입니다.
- **Multi-Region은 언제 고려해야 하고, 언제 과한 선택이 될까요?**
  Multi-Region은 서로 다른 지역에 서비스를 복제하는 결정입니다. 데이터 주권, 레이턴시, 재해복구 요구사항이 명확한 경우에만 고려합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Cloud Computing 101 (1/10): Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- **Region과 Availability Zone (현재 글)**
- Compute (예정)
- Storage (예정)
- Network (예정)
- Identity와 Security (예정)
- Monitoring (예정)
- Cost Management (예정)
- Cloud Architecture 기초 (예정)

<!-- toc:end -->

## 참고 자료

- [AWS — regions and AZs](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-regions-availability-zones.html)
- [Google Cloud — geography and regions](https://cloud.google.com/about/locations)
- [Azure — availability zones](https://learn.microsoft.com/azure/reliability/availability-zones-overview)
- [Cloudflare — what is a CDN](https://www.cloudflare.com/learning/cdn/what-is-a-cdn/)

Tags: Cloud, AWS, Region, HighAvailability, Architecture
