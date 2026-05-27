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

이 글은 Cloud Computing 101 시리즈의 4번째 글입니다.

좋은 컴퓨트 선택은 기술 유행보다 워크로드 적합성에서 갈립니다. 좋은 팀은 익숙한 플랫폼을 앞세우기보다, 이 워크로드에 가장 잘 맞는 실행 모델이 무엇인지 먼저 묻습니다.

여기서는 VM, 컨테이너, 서버리스, 베어메탈을 어떤 기준으로 구분해야 하는지 봅니다.

![Cloud Computing 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/04/04-01-concept-at-a-glance.ko.png)
*Cloud Computing 101 4장 흐름 개요*
> 워크로드의 특성에 맞는 추상화 수준을 선택하는 게 중요합니다. 추상화가 높을수록 운영 부담은 줄지만, 제어권과 비용 효율성은 함께 변합니다.

## 먼저 던지는 질문

- VM, 컨테이너, 서버리스, 베어메탈은 각각 어떤 상황에서 선택할까요?
- Auto Scaling은 실제로 무엇을 자동화하고 무엇은 자동화하지 않을까요?
- On-Demand, Reserved, Spot은 어떤 식으로 조합해야 할까요?

## 왜 중요한가

컴퓨트 선택은 청구서와 운영 난이도에 직접 영향을 줍니다. 과하게 큰 서버를 항상 켜 두면 비용이 새고, 반대로 제약을 무시한 서버리스 선택은 디버깅과 운영에 더 큰 비용을 만들 수 있습니다.

특히 컴퓨트는 데이터, 네트워크, 보안과 모두 연결됩니다. 그래서 "어디서 실행할까"는 단일 서비스 선택이 아니라 전체 시스템의 운영 모델을 정하는 결정에 가깝습니다.

## 한눈에 보는 개념

왼쪽으로 갈수록 제어권이 크고, 오른쪽으로 갈수록 플랫폼 자동화가 많아집니다. 하지만 오른쪽으로 갈수록 언제나 더 좋다는 뜻은 아닙니다. 워크로드 특성과 팀 역량에 맞는 수준을 고르는 것이 중요합니다.

## 핵심 용어

- **EC2**: AWS의 VM 서비스입니다.
- **AMI**: VM 시작에 사용하는 이미지입니다.
- **Auto Scaling Group**: 수요에 따라 인스턴스를 자동으로 관리하는 기능입니다.
- **Spot**: 남는 용량을 할인된 가격으로 사용하는 방식입니다.
- **Reserved**: 1년 또는 3년 약정으로 할인을 받는 방식입니다.

## 적용 전후 비교
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

이 세 가지를 이해하면 컴퓨트를 "그냥 서버 하나"가 아니라, 조합 가능한 자원 단위로 보기 쉬워집니다.

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

운영에서 자주 놓치는 점은 "스케일 아웃 조건"만 있고 "스케일 인 안전장치"가 없다는 사실입니다. 스케일 인이 너무 공격적이면 지연 시간이 반복적으로 출렁이고, 너무 보수적이면 비용이 고정적으로 높게 유지됩니다. 따라서 스케일링 정책은 기능 배포와 동일한 수준으로 테스트 대상이 되어야 합니다.

## 인스턴스 패밀리 명명 규칙

EC2 인스턴스 타입 이름은 `패밀리 + 세대 + 속성.크기` 구조로 되어 있습니다. 이 규칙을 알면 콘솔에서 수백 가지 타입을 볼 때 용도를 바로 추측할 수 있습니다.

| 패밀리 접두사 | 최적화 대상 | 대표 사용 사례 |
| --- | --- | --- |
| t | 버스트 가능 범용 | 개발 환경, 소규모 웹 서버, CI runner |
| m | 균형 범용 | 중간 규모 애플리케이션, 백엔드 API |
| c | 컴퓨트 최적화 | 배치 처리, 인코딩, 과학 계산 |
| r | 메모리 최적화 | 인메모리 캐시, 대규모 데이터 분석 |
| i | 스토리지 최적화 | 고빈도 I/O, NoSQL 데이터베이스 |
| g | GPU 그래픽 | 머신러닝 추론, 그래픽 렌더링 |
| p | GPU 고성능 | 대규모 모델 학습, HPC |
| d | 로컬 스토리지 밀집 | 분산 파일 시스템, 데이터 레이크 노드 |
| hpc | HPC 최적화 | 밀결합 병렬 계산, 유한요소 시뮬레이션 |

세대 숫자가 높을수록 같은 가격에 성능이 좋아집니다. 속성 접미사도 의미가 있습니다.

| 속성 문자 | 의미 |
| --- | --- |
| a | AMD 프로세서 |
| g | AWS Graviton (ARM) |
| i | Intel 프로세서 |
| n | 네트워크 강화 |
| d | 로컬 NVMe 디스크 포함 |
| e | 추가 메모리 또는 스토리지 |

### 인스턴스 타입 파서 확장판

앞서 간단한 파서를 보았습니다. 실무에서는 `m5a.2xlarge` 같은 복합 이름을 패밀리, 세대, 속성, 크기로 분리해야 할 때가 있습니다.

```python
import re
from dataclasses import dataclass

@dataclass
class InstanceType:
    family: str
    generation: int
    attributes: str
    size: str

    @property
    def full_name(self) -> str:
        return f"{self.family}{self.generation}{self.attributes}.{self.size}"

    @property
    def is_graviton(self) -> bool:
        return "g" in self.attributes

    @property
    def has_local_disk(self) -> bool:
        return "d" in self.attributes

def parse_instance_type(name: str) -> InstanceType:
    """EC2 인스턴스 타입 이름을 구조화된 객체로 변환합니다."""
    pattern = r"^([a-z]+)(\d+)([a-z]*)\.(.+)$"
    match = re.match(pattern, name)
    if not match:
        raise ValueError(f"인스턴스 타입 형식이 올바르지 않습니다: {name}")
    return InstanceType(
        family=match.group(1),
        generation=int(match.group(2)),
        attributes=match.group(3),
        size=match.group(4),
    )

# 사용 예시
examples = ["t3.micro", "m5a.2xlarge", "c7g.large", "r6id.4xlarge", "p4d.24xlarge"]
for name in examples:
    it = parse_instance_type(name)
    print(f"{name:>16} -> family={it.family}, gen={it.generation}, "
          f"attr={it.attributes or '없음'}, size={it.size}, "
          f"graviton={it.is_graviton}")
```

이 파서를 비용 보고서 자동화나 태깅 정책에 연결하면, 어떤 패밀리가 비용을 많이 차지하는지 집계하기 쉬워집니다.

## Spot 인스턴스 중단 핸들러

Spot 인스턴스는 AWS가 용량을 회수할 때 2분 전에 메타데이터 엔드포인트로 중단 알림을 보냅니다. 이 신호를 폴링해서 graceful shutdown을 수행하는 패턴이 필수입니다.

```python
import time
import signal
import sys
from urllib.request import urlopen, Request
from urllib.error import URLError

METADATA_URL = "http://169.254.169.254/latest/meta-data/spot/instance-action"
TOKEN_URL = "http://169.254.169.254/latest/api/token"
POLL_INTERVAL_SECONDS = 5

def get_imds_token(ttl_seconds: int = 21600) -> str:
    """IMDSv2 토큰을 발급받습니다."""
    req = Request(TOKEN_URL, method="PUT")
    req.add_header("X-aws-ec2-metadata-token-ttl-seconds", str(ttl_seconds))
    with urlopen(req, timeout=2) as resp:
        return resp.read().decode()

def check_spot_interruption(token: str) -> dict | None:
    """Spot 중단 알림이 있으면 action 정보를 반환합니다."""
    req = Request(METADATA_URL)
    req.add_header("X-aws-ec2-metadata-token", token)
    try:
        with urlopen(req, timeout=2) as resp:
            import json
            return json.loads(resp.read().decode())
    except URLError:
        return None

def graceful_shutdown():
    """진행 중인 작업을 안전하게 종료합니다."""
    print("[SPOT] 중단 알림 수신 - graceful shutdown 시작")
    # 1. 새 작업 수신 중단 (큐 폴링 정지)
    # 2. 진행 중인 작업 체크포인트 저장
    # 3. 로드 밸런서에서 자신을 제거 (deregister)
    # 4. 로그 플러시
    print("[SPOT] 체크포인트 저장 완료")
    print("[SPOT] 로드 밸런서 등록 해제 완료")
    sys.exit(0)

def run_spot_monitor():
    """Spot 중단 신호를 주기적으로 확인합니다."""
    token = get_imds_token()
    print(f"[SPOT] 모니터 시작 (폴링 간격: {POLL_INTERVAL_SECONDS}초)")

    while True:
        action = check_spot_interruption(token)
        if action is not None:
            print(f"[SPOT] 중단 예정: {action}")
            graceful_shutdown()
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    signal.signal(signal.SIGTERM, lambda *_: graceful_shutdown())
    run_spot_monitor()
```

핵심은 2분이라는 시간 안에 무엇을 정리할지 미리 정해 두는 것입니다. 체크포인트 저장, 큐 메시지 반환, 로드 밸런서 등록 해제가 일반적인 순서입니다. 이 패턴을 적용하지 않으면 Spot의 비용 이점이 운영 장애로 상쇄됩니다.

## 구매 옵션 조합 전략

대부분의 프로덕션 워크로드는 단일 구매 옵션만으로 운영하지 않습니다. Reserved로 기준선을 확보하고, On-Demand로 예측 불가능한 구간을 커버하며, Spot으로 비용을 깎는 3계층 전략이 표준입니다.

| 계층 | 구매 옵션 | 대상 워크로드 | 할인율(대략) |
| --- | --- | --- | --- |
| 기준선 | Reserved (1년/3년) | 24시간 상시 가동 서비스 | 30-60% |
| 변동 구간 | On-Demand | 예측 어려운 트래픽 피크 | 0% (정가) |
| 비용 절감 | Spot | 배치, 큐 워커, CI/CD | 60-90% |

### 비용 시뮬레이션 코드

```python
from dataclasses import dataclass

@dataclass
class PurchaseMix:
    reserved_count: int
    ondemand_count: int
    spot_count: int
    reserved_hourly: float   # RI 시간당 단가
    ondemand_hourly: float   # On-Demand 시간당 단가
    spot_hourly: float       # Spot 시간당 단가
    spot_interruption_rate: float = 0.05  # 월간 중단 비율

    @property
    def monthly_hours(self) -> int:
        return 24 * 30

    def monthly_cost(self) -> dict:
        hours = self.monthly_hours
        reserved = self.reserved_count * self.reserved_hourly * hours
        ondemand = self.ondemand_count * self.ondemand_hourly * hours
        spot_effective = self.spot_count * self.spot_hourly * hours
        # 중단 시 On-Demand 대체 비용
        fallback = (self.spot_count * self.spot_interruption_rate
                    * self.ondemand_hourly * hours * 0.1)
        return {
            "reserved": round(reserved, 2),
            "ondemand": round(ondemand, 2),
            "spot": round(spot_effective, 2),
            "spot_fallback": round(fallback, 2),
            "total": round(reserved + ondemand + spot_effective + fallback, 2),
        }

    def vs_all_ondemand(self) -> float:
        """전부 On-Demand일 때 대비 절감률을 반환합니다."""
        total_instances = (self.reserved_count + self.ondemand_count
                          + self.spot_count)
        all_od = total_instances * self.ondemand_hourly * self.monthly_hours
        actual = self.monthly_cost()["total"]
        return round((1 - actual / all_od) * 100, 1)

# 시뮬레이션: m5.large 10대 운영
mix = PurchaseMix(
    reserved_count=4,
    ondemand_count=3,
    spot_count=3,
    reserved_hourly=0.056,   # 1년 RI
    ondemand_hourly=0.096,
    spot_hourly=0.035,
)

result = mix.monthly_cost()
print(f"월간 비용 내역: {result}")
print(f"전량 On-Demand 대비 절감률: {mix.vs_all_ondemand()}%")
```

이 시뮬레이션은 정밀한 예측이 아니라 의사결정 방향을 잡기 위한 도구입니다. Reserved 비율을 너무 높이면 유연성이 줄고, Spot 비율을 너무 높이면 안정성이 줄어드는 트레이드오프를 숫자로 확인할 수 있습니다.

## 컨테이너 vs 서버리스 결정 흐름

컨테이너와 서버리스 사이에서 고민이 될 때는 다음 다섯 가지 질문을 순서대로 확인합니다.

1. **실행 시간이 15분을 초과하는가?** 초과한다면 Lambda는 선택지에서 제외됩니다. ECS/EKS 또는 Step Functions 분할을 검토합니다.
2. **콜드 스타트가 SLA에 영향을 주는가?** p99 응답 시간이 엄격한 동기 API라면 Provisioned Concurrency 비용을 감안해야 합니다. 이 비용이 컨테이너 상시 운영보다 비싸다면 컨테이너가 유리합니다.
3. **상태를 로컬에 유지해야 하는가?** WebSocket 세션, 인메모리 캐시 등 로컬 상태가 필수라면 서버리스는 부적합합니다.
4. **트래픽이 0으로 떨어지는 시간이 있는가?** 야간이나 주말에 요청이 거의 없다면 서버리스의 과금 모델이 유리합니다. 항상 트래픽이 있다면 컨테이너의 고정 비용이 더 예측 가능합니다.
5. **팀이 컨테이너 오케스트레이션을 운영할 역량이 있는가?** Kubernetes 운영 경험이 없는 소규모 팀이라면 서버리스로 운영 부담을 줄이는 편이 현실적입니다.

이 다섯 질문 중 하나라도 서버리스에 불리하게 답이 나오면 컨테이너를 우선 검토합니다. 반대로 모두 서버리스에 유리하다면 Lambda + API Gateway 조합이 운영 비용을 크게 줄여 줍니다.

## Lambda CLI 운영 명령어

서버리스를 선택했을 때 자주 사용하는 AWS CLI 명령어를 정리합니다.

### 함수 생성

```bash
aws lambda create-function \
  --function-name my-handler \
  --runtime python3.12 \
  --role arn:aws:iam::123456789012:role/lambda-exec \
  --handler app.handler \
  --zip-file fileb://deployment.zip \
  --timeout 30 \
  --memory-size 256
```

### Provisioned Concurrency 설정

콜드 스타트를 제거해야 하는 동기 API에서 사용합니다. 비용이 발생하므로 필요한 만큼만 설정합니다.

```bash
# 버전 발행
aws lambda publish-version \
  --function-name my-handler \
  --description "v1 for provisioned concurrency"

# Provisioned Concurrency 할당
aws lambda put-provisioned-concurrency-config \
  --function-name my-handler \
  --qualifier 1 \
  --provisioned-concurrent-executions 10
```

### Reserved Concurrency 설정

특정 함수가 계정 전체 동시 실행 한도를 독점하지 못하도록 상한을 설정합니다. 반대로 중요한 함수에 최소 용량을 보장하는 용도로도 사용합니다.

```bash
aws lambda put-function-concurrency \
  --function-name my-handler \
  --reserved-concurrent-executions 50
```

### 함수 호출 테스트

```bash
aws lambda invoke \
  --function-name my-handler \
  --payload '{"key": "value"}' \
  --cli-binary-format raw-in-base64-out \
  response.json

cat response.json
```

Provisioned Concurrency와 Reserved Concurrency는 이름이 비슷하지만 목적이 다릅니다. Provisioned는 "미리 워밍업"이고 Reserved는 "동시 실행 상한"입니다. 둘을 혼동하면 비용이 불필요하게 늘거나, 스로틀링이 예상치 못한 곳에서 발생합니다.

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
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

Tags: Cloud, Compute, EC2, AutoScaling, DevOps
