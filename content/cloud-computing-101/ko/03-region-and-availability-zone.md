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

여기서는 Region, Availability Zone, Edge의 차이를 정리하고, 가용성을 위해 무엇을 기본값으로 생각해야 하는지 봅니다.

![Cloud Computing 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/03/03-01-concept-at-a-glance.ko.png)
*Cloud Computing 101 3장 흐름 개요*
> 리전은 도시 또는 대륙 규모의 위치이고, AZ는 리전 내부에서 물리적으로 분리된 장애 경계입니다. Multi-AZ 구성이 가장 기본이고, Multi-Region은 비용과 운영 복잡도를 크게 올리기 때문에 판단이 필요합니다.

## 먼저 던지는 질문

- Region, Availability Zone, Edge는 각각 무엇을 뜻할까요?
- Multi-AZ는 정확히 무엇을 의미하고, 왜 기본값으로 봐야 할까요?
- Multi-Region은 언제 고려해야 하고, 언제 과한 선택이 될까요?

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

## 적용 전후 비교
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
    # 광섬유 ~200,000km/s, 라우터 오버헤드, 왕복
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

## Failover 실습: Multi-AZ RDS 장애 전환 테스트

Multi-AZ구성을 만들었다고 안심하면 안 됩니다. 실제로 Failover가 일어날 때 애플리케이션이 어떻게 동작하는지 테스트해야 합니다.

```bash
# Multi-AZ RDS 인스턴스 생성 (실습용)
aws rds create-db-instance \
  --db-instance-identifier demo-multi-az \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password 'ChangeMe123!' \
  --allocated-storage 20 \
  --multi-az \
  --tags Key=Project,Value=cloud-101 Key=Environment,Value=dev
```

```bash
# Failover 강제 실행 (테스트 목적)
aws rds reboot-db-instance \
  --db-instance-identifier demo-multi-az \
  --force-failover
```

```bash
# Failover 완료 확인
aws rds describe-db-instances \
  --db-instance-identifier demo-multi-az \
  --query 'DBInstances[0].{AZ:AvailabilityZone,Status:DBInstanceStatus}' \
  --output table
```

**Expected output:**

- Failover 후 `AvailabilityZone`이 이전과 다른 AZ로 변경되어야 합니다.
- `DBInstanceStatus`가 `available`로 돌아왔는지 확인합니다.
- Failover 시간은 보통 30초~2분 정도입니다. 이 시간 동안 애플리케이션이 어떻게 동작하는지(재시도, 에러, 타임아웃) 확인하는 것이 핵심입니다.

### Failover 관찰 스크립트

```python
import time
import boto3

rds = boto3.client("rds", region_name="ap-northeast-2")

def watch_failover(db_id: str, interval: int = 10, max_checks: int = 30):
    """인스턴스 상태를 주기적으로 확인하며 Failover 완료를 감지합니다."""
    for i in range(max_checks):
        resp = rds.describe_db_instances(DBInstanceIdentifier=db_id)
        inst = resp["DBInstances"][0]
        status = inst["DBInstanceStatus"]
        az = inst["AvailabilityZone"]
        print(f"[{i*interval}s] status={status}, az={az}")
        if status == "available" and i > 0:
            print("Failover complete.")
            return
        time.sleep(interval)
    print("Timeout: failover not completed within expected time.")

watch_failover("demo-multi-az")
```

이 스크립트를 주기적으로(월 1회 권장) 실행하면 Failover 시간의 실제 분포를 파악할 수 있습니다. 장애 복구 훈련을 "해야 한다"고만 알고 실제로 하지 않는 팀이 많습니다. 이 코드가 그 첨 번째 단계를 낮춥니다.

## 리전 간 데이터 복제 비용 계산

리전 간 전송은 무료가 아닙니다. Multi-Region을 고려할 때 가장 먼저 부딱히는 것이 데이터 전송 비용입니다.

```python
def cross_region_cost(
    daily_change_gb: float,
    price_per_gb: float = 0.02,  # AWS inter-region 전송 단가 근사치
    days: int = 30,
) -> dict:
    """리전 간 복제 월 비용을 추정합니다."""
    monthly_transfer = daily_change_gb * days
    cost = monthly_transfer * price_per_gb
    return {"monthly_transfer_gb": monthly_transfer, "monthly_cost_usd": round(cost, 2)}

# 예시: 매일 50GB 변경량이 있는 서비스
print(cross_region_cost(50))
# {'monthly_transfer_gb': 1500, 'monthly_cost_usd': 30.0}

# 예시: 매일 500GB 변경량 (대규모 서비스)
print(cross_region_cost(500))
# {'monthly_transfer_gb': 15000, 'monthly_cost_usd': 300.0}
```

일 50GB 수준의 서비스는 월 $30 정도이지만, 대규모 서비스는 월 $300 이상이 됩니다. 여기에 스냅샷 복제, 로그 전송, 모니터링 데이터까지 더하면 실제 비용은 더 커집니다. Multi-Region 결정 전에 이 계산을 먼저 해 보는 것이 좋습니다.

## AWS 리전별 서비스 가용성 확인

모든 리전이 동일한 서비스를 제공하지는 않습니다. 새로운 리전이나 소규모 리전은 최신 서비스가 지원되지 않을 수 있습니다.

```bash
# 특정 서비스가 리전에서 사용 가능한지 확인
aws ssm get-parameters-by-path \
  --path /aws/service/global-infrastructure/regions/ap-northeast-2/services \
  --query 'Parameters[*].Value' \
  --output text | tr '\t' '\n' | sort | head -20
```

```bash
# 리전별 EC2 인스턴스 타입 가용성 확인
aws ec2 describe-instance-type-offerings \
  --location-type region \
  --filters Name=instance-type,Values=m5.large \
  --region ap-northeast-2 \
  --query 'InstanceTypeOfferings[*].Location' \
  --output text
```

리전을 선택하기 전에 필요한 서비스와 인스턴스 타입이 해당 리전에서 지원되는지 반드시 확인해야 합니다. "서울 리전이니 당연히 될 것"이라는 가정은 위험합니다.

## 재해 복구(DR) 패턴 비교

| DR 패턴 | RTO | RPO | 월 비용 (대략) | 적합한 상황 |
| --- | --- | --- | --- | --- |
| Backup & Restore | 시간 단위 | 시간 단위 | 낮음 ($10~50) | 비핵심 서비스, 개발/스테이징 |
| Pilot Light | 10~30분 | 분 단위 | 중간 ($100~300) | 주요 웹 애플리케이션 |
| Warm Standby | 1~10분 | 초~분 단위 | 높음 ($500~1500) | 비즈니스 크리티컬 서비스 |
| Multi-Site Active | 실시간 | 실시간 | 매우 높음 ($3000+) | 글로벌 플랫폼, 금융 |

DR 패턴을 선택할 때는 "얼마나 빨리 복구해야 하는가(RTO)"와 "얼마나의 데이터 손실을 감당할 수 있는가(RPO)"를 먼저 정의해야 합니다. 비즈니스 요구사항이 마련되지 않은 상태에서 기술적으로 가장 높은 수준을 맞추려 하면 비용만 커집니다.

### DR 구성 예시 (Pilot Light)

```yaml
disaster_recovery:
  strategy: pilot_light
  primary:
    region: ap-northeast-2
    services: [ec2, rds, elasticache]
  secondary:
    region: ap-northeast-1
    services:
      rds: read_replica  # 항상 동기화
      ami: daily_copy     # 매일 AMI 복사
      infra_code: ready   # Terraform 적용만 하면 기동
  failover_trigger:
    automated: false     # 수동 판단 후 실행
    runbook: "docs/dr-failover-runbook.md"
  testing:
    frequency: quarterly
    last_test: "2026-04-15"
    result: pass
```

Pilot Light는 보조 리전에 최소한의 인프라(데이터베이스 복제본)만 유지하고, 장애 시 나머지 인프라를 빠르게 기동하는 방식입니다. Multi-Site Active보다 비용이 훨씬 낮으면서도 합리적인 복구 시간을 제공합니다.

## Edge 활용 전략

Edge(CDN)는 사용자와 가장 가까운 위치에서 콘텐츠를 제공합니다. 리전 선택과는 다른 차원의 지연 시간 최적화 수단입니다.

| 콘텐츠 유형 | Edge 캐싱 적합성 | 사유 |
| --- | --- | --- |
| 정적 이미지/CSS/JS | 매우 높음 | 변경 빈도 낮음, 전 세계 동일 |
| API 응답 (공개 데이터) | 높음 | TTL 설정으로 신선도 관리 가능 |
| 사용자별 동적 데이터 | 낮음 | 개인화 데이터는 캐싱 부적합 |
| 실시간 WebSocket | 해당 없음 | 지속적 연결, 캐싱 불가 |

```bash
# CloudFront 배포 상태 확인
aws cloudfront list-distributions \
  --query 'DistributionList.Items[*].{Id:Id,Domain:DomainName,Status:Status}' \
  --output table
```

Edge를 활용할 때 가장 중요한 결정은 TTL(캐시 만료 시간)입니다. TTL이 너무 길면 배포 시 사용자가 오래된 콘텐츠를 보게 되고, 너무 짧으면 캐시 효율이 떨어집니다. 일반적으로 정적 자산은 24시간, API 응답은 60초~5분을 기본으로 시작하고, 트래픽 패턴을 보면서 조정합니다.

## 리전 선택이 비용에 미치는 영향

같은 인스턴스 타입이라도 리전에 따라 가격이 다릅니다. 또한 리전 간 데이터 전송 비용도 무시할 수 없습니다.

| 리전 | m5.large 시간당 | 월 비용 (730h) | 데이터 전송 단가 (/GB) |
| --- | --- | --- | --- |
| us-east-1 (N. Virginia) | $0.096 | $70.08 | $0.02 |
| ap-northeast-2 (서울) | $0.118 | $86.14 | $0.08 |
| eu-west-1 (아일랜드) | $0.107 | $78.11 | $0.02 |
| ap-southeast-1 (싱가폴) | $0.114 | $83.22 | $0.08 |

서울 리전은 미국 리전보다 약 23% 비싸고, 데이터 전송 단가는 4배입니다. 따라서 "서울 리전을 주로 쓰고 DR 리전을 도쿄로 두는"이라는 선택이 항상 삼은 것은 아닙니다. 데이터 전송량이 많다면 오히려 운영 비용이 커질 수 있습니다.

### 비용 최적화 팁

- **같은 AZ 내 통신**: AZ 간 전송은 비용이 발생하지만, 같은 AZ 내에서는 무료입니다. 성능보다 비용이 우선이라면 애플리케이션과 캐시를 같은 AZ에 두는 전략도 가능합니다.
- **NAT Gateway 비용**: 각 AZ에 NAT Gateway를 두면 가용성은 올라가지만 비용도 AZ 수만큼 늘어납니다. 트래픽 규모가 작다면 하나의 NAT Gateway로 시작하고, 병목이 생길 때 추가하는 편이 합리적입니다.
- **Reserved Instance/Savings Plan**: 리전이 고정되면 1년/3년 예약으로 30~60% 절감이 가능합니다. DR 리전은 예약하지 않고 온디맨드로 두는 것이 보통입니다.

## 자주 하는 실수 5가지

1. 단일 AZ만 사용합니다.
2. Multi-Region을 적용하면서 지연 증가 비용을 고려하지 않습니다.
3. DB Failover 테스트를 하지 않습니다.
4. 리전 간 데이터 동기화 비용을 무시합니다.
5. 글로벌 사용자에게 Edge 캐시를 활용하지 않습니다.

각 실수에 대한 구체적인 예방 조치를 정리하면 다음과 같습니다.

| 실수 | 예방 조치 | 검증 방법 |
| --- | --- | --- |
| 단일 AZ | ALB + Auto Scaling을 Multi-AZ로 설정 | `describe-auto-scaling-groups`로 AZ 목록 확인 |
| 지연 무시 | RTT 최소화 리전 선택 + 복제 전략 문서화 | `ping`/`traceroute`로 실측 |
| Failover 미테스트 | 월 1회 `reboot-db-instance --force-failover` | Failover 시간 기록 + 앱 에러 로그 확인 |
| 동기화 비용 무시 | 사전 비용 계산 + 예산 알림 | `cross_region_cost()` 함수로 월별 추적 |
| Edge 미활용 | CloudFront + S3 정적 자산 분리 | `list-distributions`로 배포 상태 확인 |

이 표를 스프린트 단위로 점검하면 같은 실수가 반복되는 것을 구조적으로 막을 수 있습니다. 특히 Failover 테스트는 "해야 한다"고만 알고 실제로는 하지 않는 팀이 많으므로, 캘린더에 등록해 두는 것을 권장합니다.

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
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

Tags: Cloud, AWS, Region, HighAvailability, Architecture
