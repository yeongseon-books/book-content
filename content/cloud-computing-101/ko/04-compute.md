---
series: cloud-computing-101
episode: 4
title: "Cloud Computing 101 (4/10): Compute"
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
  - Compute
  - EC2
  - AutoScaling
  - DevOps
seo_description: 가상 머신, 컨테이너, 서버리스의 차이와 워크로드별 컴퓨트 선택 기준, 오토스케일링 및 비용 최적화 전략을 정리합니다.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (4/10): Compute

클라우드에서 비용과 운영 피로를 가장 크게 좌우하는 축 중 하나가 컴퓨트입니다. 같은 애플리케이션이라도 VM에 올릴지, 컨테이너로 돌릴지, 서버리스로 실행할지에 따라 비용 구조와 운영 방식이 완전히 달라집니다.

좋은 컴퓨트 선택은 기술 유행보다 워크로드 적합성에서 갈립니다. 좋은 팀은 익숙한 플랫폼을 앞세우기보다, 이 워크로드에 가장 잘 맞는 실행 모델이 무엇인지 먼저 묻습니다.

이 글은 Cloud Computing 101 시리즈의 4번째 글입니다.

여기서는 VM, 컨테이너, 서버리스, 베어메탈을 어떤 기준으로 구분해야 하는지 살펴보겠습니다.

## 먼저 던지는 질문

- VM, 컨테이너, 서버리스, 베어메탈은 각각 어떤 상황에서 선택할까요?
- Auto Scaling은 실제로 무엇을 자동화하고 무엇은 자동화하지 않을까요?
- On-Demand, Reserved, Spot은 어떤 식으로 조합해야 할까요?

## 큰 그림

![Cloud Computing 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/04/04-01-concept-at-a-glance.ko.png)

*Cloud Computing 101 4장 흐름 개요*

VM은 초기 투자 없이 가장 세밀한 제어권을 줍니다. 컨테이너는 배포 속도는 빠르지만 런타임 관리는 여전히 팀의 책임입니다. 서버리스는 상태 관리 걱정 없이 비즈니스 로직에만 집중할 수 있습니다. 베어메탈은 극도의 성능 요구 사항이 있을 때만 고려합니다.

> 워크로드의 특성에 맞는 추상화 수준을 선택하는 게 중요합니다. 추상화가 높을수록 운영 부담은 줄지만, 제어권과 비용 효율성은 함께 변합니다.

## 왜 중요한가

컴퓨트 선택은 청구서와 운영 난이도에 직접 영향을 줍니다. 과하게 큰 서버를 항상 켜 두면 비용이 새고, 반대로 제약을 무시한 서버리스 선택은 디버깅과 운영에 더 큰 비용을 만들 수 있습니다.

특히 컴퓨트는 데이터, 네트워크, 보안과 모두 연결됩니다. 그래서 “어디서 실행할까”는 단일 서비스 선택이 아니라 전체 시스템의 운영 모델을 정하는 결정에 가깝습니다.

## 한눈에 보는 개념

왼쪽으로 갈수록 제어권이 크고, 오른쪽으로 갈수록 플랫폼 자동화가 많아집니다. 하지만 오른쪽으로 갈수록 언제나 더 좋다는 뜻은 아닙니다. 워크로드 특성과 팀 역량에 맞는 수준을 고르는 것이 중요합니다.

## 핵심 용어

- **EC2**: AWS의 VM 서비스입니다.
- **AMI**: VM 시작에 사용하는 이미지입니다.
- **Auto Scaling Group**: 수요에 따라 인스턴스를 자동으로 관리하는 기능입니다.
- **Spot**: 남는 용량을 할인된 가격으로 사용하는 방식입니다.
- **Reserved**: 1년 또는 3년 약정으로 할인을 받는 방식입니다.

## Before / After

**Before**에서는 트래픽 피크에 맞춰 항상 큰 서버를 켜 둡니다. 대부분의 시간에는 낭비가 됩니다.

**After**에서는 Auto Scaling Group이 수요에 맞춰 늘고 줄어듭니다. 평균 구간에서는 비용을 줄이고, 피크 구간에서는 용량을 확보할 수 있습니다.

## 실습: boto3로 EC2 인스턴스 다루기

### 1단계 — 클라이언트

```python
import boto3
ec2 = boto3.client("ec2", region_name="us-east-1")
```

### 2단계 — 인스턴스 시작

```python
def launch(ami: str, type_: str = "t3.micro"):
    res = ec2.run_instances(
        ImageId=ami, InstanceType=type_, MinCount=1, MaxCount=1,
    )
    return res["Instances"][0]["InstanceId"]
```

### 3단계 — 상태 조회

```python
def status(instance_id: str):
    res = ec2.describe_instances(InstanceIds=[instance_id])
    return res["Reservations"][0]["Instances"][0]["State"]["Name"]
```

### 4단계 — 종료

```python
def terminate(instance_id: str):
    ec2.terminate_instances(InstanceIds=[instance_id])
```

### 5단계 — 인스턴스 타입 읽기

```python
def parse_type(t: str) -> dict:
    family, size = t.split(".")
    return {"family": family, "size": size}

print(parse_type("t3.micro"))
print(parse_type("m5.large"))
```

이 예제는 컴퓨트가 얼마나 명시적인 자원인지를 잘 보여 줍니다. 어떤 이미지를 쓸지, 어떤 크기로 띄울지, 언제 종료할지, 비용과 성능을 어떤 이름 규칙으로 읽을지 모두 사용자가 결정합니다.

## 이 코드에서 먼저 봐야 할 점

- AMI는 VM의 출생 사진 같은 기준 이미지입니다.
- `terminate`는 되돌릴 수 없는 작업입니다.
- 인스턴스 타입 이름은 `family.size` 구조로 읽습니다.

이 세 가지를 이해하면 컴퓨트를 “그냥 서버 하나”가 아니라, 조합 가능한 자원 단위로 보기 쉬워집니다.

## 이 예제를 실제로 검증하는 순서

컴퓨트 실습에서는 "인스턴스를 띄웠다"보다 상태 전이가 어떻게 보이는지 확인하는 편이 더 중요합니다. 시작, 조회, 종료가 각각 어떤 운영 이벤트인지 이해하면 오토스케일링과 비용 이야기가 훨씬 쉽게 연결됩니다.

```bash
aws ec2 describe-instances --instance-ids i-xxxxxxxx --query 'Reservations[0].Instances[0].State.Name'
```

**Expected output:**

- 시작 직후에는 `pending`, 이후에는 `running`으로 상태가 바뀌어야 합니다.
- 종료를 호출한 뒤에는 `shutting-down`을 거쳐 `terminated`로 이동해야 합니다.
- 이 흐름을 알고 있어야 오토스케일링 이벤트가 정상 동작인지, 장애 상황인지 구분할 수 있습니다.

### 자주 막히는 지점

- 중지와 종료를 같은 것으로 생각하면 비용과 복구 전략을 잘못 세우기 쉽습니다.
- Spot은 값이 싸다는 이유만으로 데이터베이스에 쓰면 안 됩니다. 중단 신호를 견딜 수 있는 작업에만 배치해야 합니다.
- 인스턴스 타입 이름은 성능 보장이 아니라 출발점입니다. 실제 사용량을 메트릭으로 확인해야 라이트사이징이 가능합니다.

## 어떤 실행 모델을 언제 고를까

VM은 운영 체제 수준 제어가 필요할 때 강합니다. 컨테이너는 배포 일관성과 이식성이 중요할 때 좋습니다. 서버리스는 실행 시간이 짧고 변동성이 큰 워크로드에서 인간의 운영 시간을 크게 줄여 줍니다. 베어메탈은 특수한 성능 요구사항이나 하드웨어 제어가 필요할 때 고려합니다.

Auto Scaling도 오해가 많습니다. 이것은 애플리케이션 설계 문제를 자동으로 해결해 주는 기능이 아니라, 수요에 맞춰 인스턴스 개수를 조정하는 장치입니다. 애플리케이션이 상태를 내부에 품고 있다면 ASG를 붙여도 기대만큼 잘 확장되지 않습니다.

## 자주 하는 실수 5가지

1. Spot 인스턴스를 데이터베이스에 사용합니다.
2. Auto Scaling을 두지 않아 피크 순간에만 서비스가 무너집니다.
3. 유연성을 고려하지 않고 Reserved를 과도하게 구매합니다.
4. 중지한 인스턴스는 비용이 0이라고 생각합니다.
5. 로그를 외부로 보내지 않은 채 인스턴스를 종료합니다.

## 실무에서는 이렇게 생각합니다

- 워크로드에 컴퓨트를 맞추지, 컴퓨트에 워크로드를 억지로 맞추지 않습니다.
- Auto Scaling은 예외가 아니라 기본값에 가깝습니다.
- Spot은 재시도가 쉬운 작업에 배치합니다.
- Reserved는 안정적인 기준 부하에만 적용합니다.
- 서버리스는 컴퓨트 비용보다 사람의 운영 시간이 비쌀 때 특히 강력합니다.

## 체크리스트

- [ ] 워크로드별로 적절한 컴퓨트 모델을 매핑했는가.
- [ ] 각 계층에 Auto Scaling을 검토했는가.
- [ ] Reserved와 Spot 비율이 의도적으로 설계되어 있는가.
- [ ] 종료 정책과 로그 보존 방식이 문서화되어 있는가.

## 연습 문제

1. Lambda의 최대 실행 시간이 설계에 주는 제약을 설명해 보세요.
2. Spot 중단 알림이 왔을 때 graceful shutdown을 어떻게 구현할지 생각해 보세요.
3. `t3`와 `m5`를 워크로드 적합성 관점에서 비교해 보세요.

## 정리 및 다음 단계

컴퓨트가 코드를 실행한다면, 그 결과로 생기는 데이터는 어딘가에 안정적으로 저장되어야 합니다. 다음 글에서는 객체, 블록, 파일, 아카이브를 다루는 Storage로 넘어가겠습니다.


## 컴퓨트 옵션 선택표와 비용 계산 예시

컴퓨트는 성능 문제가 발생했을 때 가장 먼저 의심되는 계층이지만, 비용 최적화에서도 가장 큰 영향력을 가집니다. 따라서 VM, 컨테이너, 서버리스를 비교할 때는 "편한가"보다 "우리 부하 패턴에 맞는가"를 먼저 확인해야 합니다.

| 항목 | VM | Container | Serverless |
| --- | --- | --- | --- |
| 기동 시간 | 분 단위 | 초~분 | 밀리초~초 |
| 운영 책임 | OS 포함 높음 | 오케스트레이션 포함 중간 | 런타임 외 낮음 |
| 장시간 처리 | 강함 | 강함 | 제약 있음 |
| 트래픽 급변 대응 | ASG 설계 필요 | HPA 설계 필요 | 자동 확장 강함 |
| 비용 구조 | 시간 기반 | 노드/사용량 혼합 | 호출/실행시간 기반 |
| 디버깅 난이도 | 중간 | 중간~높음 | 높음 |

### 비용 계산 간단 모델

아래 식은 의사결정 초기에 대략적인 비교를 위해 쓰는 계산 예시입니다.

- VM 월비용 = 인스턴스 단가 * 24 * 30 * 대수
- 컨테이너 월비용 = 노드 단가 * 노드수 + 관리형 제어 plane 비용
- 서버리스 월비용 = 요청수 * 요청단가 + 실행시간(GB-s) * 단가

예시 값:

| 시나리오 | 월 요청량 | 평균 실행시간 | 추천 모델 |
| --- | --- | --- | --- |
| 배치 API | 낮음, 간헐적 | 짧음 | Serverless |
| 백오피스 웹 | 일정 | 중간 | Container/VM |
| 실시간 세션 서버 | 높고 지속적 | 김 | VM/Container |

### 라이트사이징 검토표

| 메트릭 | 임계 기준 예시 | 조치 |
| --- | --- | --- |
| CPU 평균 | 20% 미만(2주 이상) | 인스턴스 다운사이징 |
| 메모리 피크 | 85% 이상 반복 | 상향 또는 캐시 분리 |
| 디스크 IOPS | 포화 빈발 | 타입 변경 또는 분산 |
| 네트워크 송신 | 일정 시간 급증 | 오토스케일 정책 보정 |

### 오토스케일링 정책 예시

```yaml
auto_scaling:
  target_group: web-asg
  min_size: 2
  max_size: 12
  policies:
    - metric: cpu_utilization
      target: 55
    - metric: request_per_target
      target: 800
  cooldown_seconds: 180
```

운영에서 자주 놓치는 점은 "스케일 아웃 조건"만 있고 "스케일 인 안전장치"가 없다는 것입니다. 스케일 인이 너무 공격적이면 지연 시간이 반복적으로 출렁이고, 너무 보수적이면 비용이 고정적으로 높게 유지됩니다. 따라서 스케일링 정책은 기능 배포와 동일한 수준으로 테스트 대상이 되어야 합니다.

## 컴퓨트 옵션 선택표와 비용 계산 예시

| 항목 | VM | Container | Serverless |
| --- | --- | --- | --- |
| 기동 시간 | 분 단위 | 초~분 | 밀리초~초 |
| 운영 책임 | OS 포함 높음 | 오케스트레이션 포함 중간 | 런타임 외 낮음 |
| 장시간 처리 | 강함 | 강함 | 제약 있음 |
| 트래픽 급변 대응 | ASG 설계 필요 | HPA 설계 필요 | 자동 확장 강함 |
| 비용 구조 | 시간 기반 | 노드/사용량 혼합 | 호출/실행시간 기반 |

| 메트릭 | 임계 기준 예시 | 조치 |
| --- | --- | --- |
| CPU 평균 | 20% 미만(2주 이상) | 인스턴스 다운사이징 |
| 메모리 피크 | 85% 이상 반복 | 상향 또는 캐시 분리 |
| 디스크 IOPS | 포화 빈발 | 타입 변경 또는 분산 |

```yaml
auto_scaling:
  target_group: web-asg
  min_size: 2
  max_size: 12
  policies:
    - metric: cpu_utilization
      target: 55
    - metric: request_per_target
      target: 800
  cooldown_seconds: 180
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

- **VM, 컨테이너, 서버리스, 베어메탈은 각각 어떤 상황에서 선택할까요?**
VM은 장기간 안정적인 워크로드, 컨테이너는 마이크로서비스 아키텍처, 서버리스는 불규칙한 트래픽이나 이벤트 기반 작업, 베어메탈은 매우 높은 성능이 필요한 경우에 선택합니다.
- **Auto Scaling은 실제로 무엇을 자동화하고 무엇은 자동화하지 않을까요?**
Auto Scaling Group은 수요에 따라 인스턴스 수를 자동으로 조정합니다. 하지만 인스턴스 유형 변경, 스토리지 크기 조정, 네트워크 정책 변경 같은 세밀한 조정은 여전히 수동입니다.
- **On-Demand, Reserved, Spot은 어떤 식으로 조합해야 할까요?**
On-Demand는 트래픽이 예측 불가능할 때, Reserved는 최소 기준 용량이 예상될 때, Spot은 종료 가능한 배치 작업에 사용합니다. 대부분의 팀은 셋을 조합해 비용 효율성을 높입니다.

<!-- toc:begin -->
## 시리즈 목차

- [Cloud Computing 101 (1/10): Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region과 Availability Zone](./03-region-and-availability-zone.md)
- **Compute (현재 글)**
- Storage (예정)
- Network (예정)
- Identity와 Security (예정)
- Monitoring (예정)
- Cost Management (예정)
- Cloud Architecture 기초 (예정)

<!-- toc:end -->

## 참고 자료

- [AWS EC2 user guide](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)
- [AWS Auto Scaling](https://docs.aws.amazon.com/autoscaling/)
- [AWS — Spot Instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html)
- [AWS Lambda overview](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)

Tags: Cloud, Compute, EC2, AutoScaling, DevOps
