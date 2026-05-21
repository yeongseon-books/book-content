---
series: cloud-computing-101
episode: 1
title: "Cloud Computing 101 (1/10): Cloud Computing이란 무엇인가?"
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
  - Infrastructure
  - DevOps
  - Networking
seo_description: 클라우드 컴퓨팅의 핵심 특성과 온프레미스와의 차이, 공동 책임 모델 및 실무 관점의 운영 원칙을 상세히 정리합니다.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (1/10): Cloud Computing이란 무엇인가?

서버를 산다는 말이 자연스럽던 시절에는 서비스 하나를 시작하기 위해서도 구매, 설치, 네트워크 연결, 운영 체제 준비를 먼저 끝내야 했습니다. 지금은 몇 분 안에 컴퓨트와 스토리지를 만들고 바로 실험을 시작할 수 있습니다.

클라우드를 처음 배우면 "남의 서버를 빌려 쓰는 것" 정도로 기억하기 쉽습니다. 틀린 말은 아니지만 충분하지는 않습니다. 더 중요한 점은 자원을 필요할 때 만들고, 사용한 만큼 비용을 내며, 공급자와 사용자가 책임을 나눠 갖는 방식이라는 점입니다.

이 글은 Cloud Computing 101 시리즈의 첫 번째 글입니다.

여기서는 클라우드를 단순한 유행어가 아니라, 비용 구조와 운영 책임까지 함께 바꾸는 실행 모델로 이해해 보겠습니다.


![Cloud Computing 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/01/01-01-concept-at-a-glance.ko.png)
*Cloud Computing 101 1장 흐름 개요*
> 클라우드의 핵심은 기술 이름이 아니라, 초기 투자 없이 필요에 따라 자원을 프로비저닝하고, 사용한 만큼 비용을 내며, 공급자와 사용자가 운영 책임을 명확히 나누는 실행 모델에 있습니다.

## 먼저 던지는 질문

- 왜 많은 팀이 서버를 직접 사는 방식에서 인터넷으로 자원을 빌려 쓰는 방식으로 이동했을까요?
- 클라우드의 핵심 특성은 무엇이고, 온프레미스와 비교하면 무엇이 달라질까요?
- AWS, Azure, Google Cloud 같은 사업자는 정확히 어떤 역할을 맡을까요?

## 왜 중요한가

클라우드의 가장 큰 장점은 초기 투자 없이 빠르게 시작할 수 있다는 점입니다. 작은 팀도 글로벌 서비스를 실험할 수 있고, 실패 비용도 예전보다 훨씬 작아집니다. 반대로 비용 관리와 책임 경계를 이해하지 못한 채 시작하면 편리함이 곧 혼란으로 바뀝니다.

예를 들어 예산 알림이 없으면 사용하지 않는 자원이 몇 주씩 살아남아 비용을 키울 수 있습니다. 공개 스토리지 설정을 잘못하면 보안 사고로 바로 이어질 수도 있습니다. 그래서 클라우드를 배운다는 말은 VM 이름을 외우는 것이 아니라, 속도와 비용과 책임을 함께 다루는 법을 익힌다는 뜻에 가깝습니다.

## 한눈에 보는 개념

사용자는 인터넷을 통해 클라우드 제공자에게 자원을 요청합니다. 제공자는 물리 장비를 직접 노출하지 않고, 가상 머신과 저장소, 네트워크 같은 추상화된 리소스로 응답합니다. 이 추상화 덕분에 팀은 하드웨어 설치보다 애플리케이션 설계와 운영 자동화에 더 집중할 수 있습니다.

## 핵심 용어

- **CSP**: AWS, Azure, Google Cloud처럼 클라우드 서비스를 제공하는 사업자입니다.
- **탄력성(Elasticity)**: 수요가 늘면 확장하고, 줄면 다시 축소하는 능력입니다.
- **온디맨드**: 필요해지는 즉시 자원을 만들 수 있는 운영 방식입니다.
- **사용량 기반 과금(Pay-as-you-go)**: 구매가 아니라 사용량을 기준으로 비용을 냅니다.
- **공동 책임 모델(Shared responsibility)**: 공급자와 사용자가 각각 무엇을 보호하는지 나누는 모델입니다.

## 온프레미스와 클라우드의 비교

**Before**에서는 서버를 주문하고, 랙에 넣고, 네트워크를 연결하고, 운영 체제를 설치한 뒤에야 첫 서비스를 띄울 수 있었습니다.

**After**에서는 콘솔이나 API로 인스턴스를 만들고, 스토리지를 붙이고, 네트워크 정책을 적용한 뒤 몇 분 안에 서비스를 시작할 수 있습니다.

이 차이는 단순한 속도 개선이 아닙니다. 실험 주기가 빨라지고, 인프라가 코드로 다뤄지며, 팀의 역량이 하드웨어 운영에서 시스템 설계와 자동화로 이동합니다.

| 비교 항목 | 온프레미스 | 클라우드 |
| --- | --- | --- |
| 초기 투자 | 서버 구매, 데이터센터 임대 | 없음 (종량제) |
| 확장 시간 | 주~월 단위 | 분~시간 단위 |
| 운영 책임 | 전체 스택 | 모델에 따라 분리 |
| 비용 구조 | 고정 비용 중심 | 변동 비용 중심 |
| 폐기 비용 | 감가상각, 처분 필요 | 리소스 삭제로 즉시 종료 |
| 글로벌 배포 | 물리적 확장 필요 | 리전 선택으로 가능 |

이 표가 보여 주는 핵심은 단순히 "클라우드가 낫다"가 아닙니다. 비용 구조, 운영 모델, 팀 역량에 따라 적합한 선택이 다르다는 점입니다. 규제가 강한 금융이나 의료 분야에서는 여전히 온프레미스가 필수인 영역도 있습니다.

## NIST가 정의한 클라우드의 다섯 가지 필수 특성

NIST SP 800-145에서는 클라우드 컴퓨팅의 필수 특성을 다섯 가지로 정리합니다. 이 정의를 알아 두면 "이건 클라우드인가?"라는 질문에 명확히 답할 수 있습니다.

| 특성 | 설명 | 실무 예시 |
| --- | --- | --- |
| 온디맨드 셀프서비스 | 사람 개입 없이 자원을 프로비저닝 | 콘솔에서 EC2 생성 |
| 광범위한 네트워크 접근 | 표준 메커니즘으로 다양한 클라이언트에서 접근 | HTTPS API |
| 리소스 풀링 | 여러 고객이 동일 인프라를 공유 | 멀티테넌시 |
| 빠른 탄력성 | 수요에 따라 자동 확장·축소 | Auto Scaling |
| 측정 가능한 서비스 | 사용량 기반 과금과 모니터링 | CloudWatch 메트릭 |

이 다섯 가지를 모두 만족하지 않는다면 엄밀히는 클라우드가 아니라 호스팅에 가깝습니다. 예를 들어 고정 월정액 VPS는 탄력성과 측정 기반 과금을 충족하지 못하므로 완전한 클라우드로 분류하기 어렵습니다.


## 배포 모델 — Public, Private, Hybrid

NIST는 서비스 모델(IaaS/PaaS/SaaS)과 별개로 배포 모델도 네 가지로 구분합니다. 팀의 규제 요건과 데이터 민감도에 따라 어떤 모델이 적합한지 달라집니다.

| 배포 모델 | 인프라 소유 | 접근 범위 | 대표 사례 |
| --- | --- | --- | --- |
| Public Cloud | CSP | 인터넷 전체 | AWS, Azure, GCP |
| Private Cloud | 조직 자체 | 조직 내부 | OpenStack, VMware vSphere |
| Hybrid Cloud | CSP + 조직 | 혼합 | Azure Arc, AWS Outposts |
| Community Cloud | 복수 조직 공동 | 커뮤니티 | 정부 공동 클라우드, 의료 데이터 공유 플랫폼 |

Public Cloud는 초기 투자가 없고 글로벌 확장이 쉽지만, 데이터 주권이나 규제 요건이 강한 산업에서는 Private Cloud가 필수인 경우가 있습니다. Hybrid Cloud는 두 세계를 연결하지만 네트워크 복잡도와 운영 비용이 증가합니다.

### 배포 모델 선택 기준

```yaml
deployment_model_decision:
  data_sovereignty_required: true   # → Private 또는 Hybrid
  burst_capacity_needed: true        # → Hybrid (on-prem 기본 + cloud burst)
  multi_region_latency_critical: true # → Public Cloud
  compliance_framework: "금융감독원"  # → Private 또는 승인된 CSP 리전
  team_ops_capacity: small            # → Public Cloud (관리형 서비스 활용)
```

이 기준표는 "어떤 클라우드가 좋은가"가 아니라 "우리 팀의 제약 조건에서 무엇이 현실적인가"를 판단하는 출발점입니다. 실무에서는 하나의 모델로 모든 워크로드를 처리하기보다, 워크로드별로 다른 모델을 적용하는 경우가 더 흔합니다.

## 실습: 첫 번째 클라우드 자원 만들기 — boto3로 S3 사용하기

클라우드가 추상적인 개념으로만 남지 않도록 가장 작은 예제를 보겠습니다. AWS의 객체 스토리지인 S3에 버킷을 만들고 파일을 업로드하는 코드입니다.

### 1단계 — 의존성 설치

```bash
pip install boto3
```

### 2단계 — 자격 증명 설정

```bash
export AWS_ACCESS_KEY_ID="..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_DEFAULT_REGION="us-east-1"
```

### 3단계 — 클라이언트

```python
import boto3

s3 = boto3.client("s3")
```

### 4단계 — 버킷 생성

```python
def create_bucket(name: str):
    s3.create_bucket(Bucket=name)
    return name
```

### 5단계 — 객체 업로드

```python
def upload(bucket: str, key: str, data: bytes):
    s3.put_object(Bucket=bucket, Key=key, Body=data)
    return f"s3://{bucket}/{key}"

print(upload("my-test-bucket-2026", "hello.txt", b"hi cloud"))
```

이 코드는 짧지만 중요한 감각을 보여 줍니다. 저장소를 API 호출로 만들고, 로컬 디스크 대신 관리형 스토리지에 데이터를 올리며, 인프라가 코드의 일부로 다뤄집니다. 이것이 클라우드가 운영 모델이라고 말하는 이유입니다.

## 이 코드에서 먼저 봐야 할 점

- 자격 증명은 소스 코드가 아니라 환경 변수에 둡니다.
- 클라이언트는 한 번 만들고 여러 번 재사용하는 패턴이 자연스럽습니다.
- S3 버킷 이름은 AWS 전체에서 전역적으로 고유해야 합니다.

이 세 가지는 문법보다 운영 습관에 가깝습니다. 자격 증명을 코드에 넣으면 유출 위험이 커지고, 리전과 이름 규칙을 무시하면 자동화가 불안정해집니다.

## 이 예제를 실제로 검증하는 순서

S3 예제를 실행할 때는 "코드가 돌아갔다"에서 멈추지 말고, 실제로 버킷과 객체가 생성되었는지 바로 확인하는 습관이 중요합니다. 클라우드 입문 단계에서 가장 흔한 실수는 API 호출이 성공했다고 믿고 뒤 단계를 건너뛰는 것입니다.

```bash
aws s3 ls
aws s3 ls s3://my-test-bucket-2026
```

**Expected output:**

- 첫 번째 명령에서는 방금 만든 버킷 이름이 보여야 합니다.
- 두 번째 명령에서는 `hello.txt` 객체가 보여야 합니다.
- 둘 다 비어 있다면 자격 증명, 리전, 버킷 이름 충돌부터 다시 확인해야 합니다.

### 자주 막히는 지점

- `BucketAlreadyExists`가 나오면 버킷 이름이 전역에서 이미 사용 중인 경우가 많습니다. 프로젝트명이나 날짜를 붙여 고유성을 높이는 편이 안전합니다.
- `AccessDenied`가 나오면 키 권한보다 먼저 현재 계정이 어떤 프로필을 보고 있는지 확인해야 합니다.
- 실습이 끝난 뒤 버킷을 비우지 않으면 입문 실습도 장기 비용으로 남을 수 있습니다.


### 정리 자동화 — 실습 후 리소스 삭제

입문 단계에서 가장 중요한 습관은 실습이 끝나면 만든 자원을 바로 정리하는 것입니다. 아래 코드는 버킷의 모든 객체를 비운 뒤 버킷 자체를 삭제합니다.

```python
def cleanup_bucket(name: str):
    """버킷의 모든 객체를 삭제한 뒤 버킷을 제거합니다."""
    bucket = boto3.resource("s3").Bucket(name)
    bucket.objects.all().delete()
    bucket.delete()
    print(f"Deleted: {name}")

cleanup_bucket("my-test-bucket-2026")
```

```bash
# 삭제 확인
aws s3 ls | grep my-test-bucket-2026
# 출력이 비어 있으면 성공
```

이 패턴을 익혀 두면 이후 실습에서도 비용 누수 없이 안전하게 실험할 수 있습니다. 프로덕션에서는 Lifecycle Policy를 설정해 자동 삭제를 적용하는 것이 일반적입니다.

## 공동 책임 모델은 왜 중요한가

입문자가 가장 자주 오해하는 부분이 바로 책임 경계입니다. 많은 팀이 "클라우드에 올렸으니 보안은 사업자가 알아서 하겠지"라고 생각하지만, 실제로는 그렇지 않습니다. 데이터센터와 물리 장비, 하이퍼바이저 같은 기반 영역은 공급자가 맡지만, 계정 권한, 데이터 공개 범위, 네트워크 접근 제어, 애플리케이션 설정은 사용자 책임인 경우가 많습니다.

예를 들어 공개 버킷 때문에 데이터가 유출됐다면 S3라는 서비스 자체가 문제라기보다, 구성 실수가 원인인 경우가 대부분입니다. 비용과 함께 책임 경계를 초반에 이해해야 이후의 모든 선택이 덜 흔들립니다.

## 서비스 모델과 책임 경계 확장 정리

클라우드를 이해할 때 가장 실무적인 관점은 "누가 무엇을 운영하는가"입니다. 같은 기능을 제공하더라도 서비스 모델에 따라 장애 대응 속도, 보안 운영의 난이도, 비용 구조가 크게 달라집니다. 아래 표는 IaaS, PaaS, SaaS를 기능이 아니라 운영 책임과 변경 속도 관점에서 비교한 것입니다.

| 구분 | IaaS | PaaS | SaaS |
| --- | --- | --- | --- |
| 주요 예시 | EC2, Compute Engine | App Engine, Heroku | Google Workspace, Notion |
| 사용자가 직접 관리하는 범위 | OS, 런타임, 앱, 데이터 | 앱, 데이터 | 사용자 설정, 데이터 입력 |
| 공급자가 관리하는 범위 | 물리 인프라, 가상화 | 인프라, OS, 런타임 | 인프라, 플랫폼, 애플리케이션 |
| 배포 속도 | 중간 | 빠름 | 매우 빠름 |
| 제어권 | 높음 | 중간 | 낮음 |
| 운영 난이도 | 높음 | 중간 | 낮음 |
| 락인 위험 | 중간 | 중간~높음 | 높음 |

팀이 빠르게 실험해야 한다면 PaaS나 SaaS가 유리할 수 있습니다. 반대로 보안 규정이 강하고 운영 체제 레벨 제어가 필요하다면 IaaS가 더 적합합니다. 중요한 점은 "무엇이 더 현대적인가"가 아니라 "우리 팀의 현재 책임 능력과 규제 요건에 맞는가"입니다.

### 책임 분담 매트릭스

아래 매트릭스는 클라우드 입문 팀이 자주 헷갈리는 책임 분리를 한 번에 확인할 수 있게 정리한 것입니다.

| 운영 항목 | 온프레미스 | IaaS | PaaS | SaaS |
| --- | --- | --- | --- | --- |
| 데이터센터 전원/냉각 | 사용자 | 공급자 | 공급자 | 공급자 |
| 물리 서버 유지보수 | 사용자 | 공급자 | 공급자 | 공급자 |
| 하이퍼바이저 | 사용자 | 공급자 | 공급자 | 공급자 |
| 운영 체제 패치 | 사용자 | 사용자 | 공급자 | 공급자 |
| 런타임/미들웨어 | 사용자 | 사용자 | 공급자 | 공급자 |
| 애플리케이션 코드 | 사용자 | 사용자 | 사용자 | 공급자 |
| 데이터 분류/접근 권한 | 사용자 | 사용자 | 사용자 | 사용자 |
| 계정/권한 설계 | 사용자 | 사용자 | 사용자 | 사용자 |

이 매트릭스의 핵심은 마지막 두 줄입니다. 어떤 모델을 쓰더라도 데이터 분류와 접근 권한은 여전히 사용자 책임입니다. 즉, 클라우드 도입은 보안 책임의 제거가 아니라 책임 경계의 재배치입니다.

## 비용 구조가 바뀌면 의사결정도 바뀐다

온프레미스에서는 서버를 한번 사면 감가상각이 끝날 때까지 활용하는 것이 합리적이었습니다. 클라우드에서는 반대입니다. 쓰지 않는 자원을 빨리 끄는 것이 합리적입니다. 이 차이가 팀의 의사결정 습관을 바꿉니다.

```bash
# AWS CLI로 현재 계정의 월간 비용 추정 확인
aws ce get-cost-and-usage \
  --time-period Start=2026-05-01,End=2026-05-21 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --output table
```

이 명령은 입문 단계에서도 꼭 알아 두는 편이 좋습니다. 비용을 콘솔이 아니라 CLI로 확인하는 습관이 있으면, 비용 알림 자동화나 주간 리포트 스크립트로 확장하기 훨씬 쉬워집니다.

### 비용 감각을 키우는 간단한 계산

```python
def monthly_cost(hourly_price: float, hours_per_day: int = 24, days: int = 30) -> float:
    """인스턴스 하나의 월 비용 추정."""
    return hourly_price * hours_per_day * days

# t3.micro (약 $0.0104/h) vs m5.large (약 $0.096/h)
print(f"t3.micro 월비용: ${monthly_cost(0.0104):.2f}")
print(f"m5.large 월비용: ${monthly_cost(0.096):.2f}")
print(f"m5.large를 업무시간만 쓰면: ${monthly_cost(0.096, hours_per_day=10, days=22):.2f}")
```

이 계산이 보여 주는 점은 분명합니다. 개발용 인스턴스를 24시간 켜 두는 것과 업무시간만 켜 두는 것은 비용이 크게 다릅니다. 클라우드에서는 "끄는 것"도 비용 관리의 일부입니다.

### 주요 CSP 인스턴스 비교

같은 사양이라도 CSP마다 이름과 가격이 다릅니다. 입문 단계에서 자주 쓰는 범용 인스턴스를 비교해 보겠습니다.

| 사양 (2 vCPU, 8 GB RAM) | AWS | Azure | GCP |
| --- | --- | --- | --- |
| 인스턴스 타입 | m5.large | Standard_D2s_v3 | e2-standard-2 |
| 시간당 가격 (US East) | $0.096 | $0.096 | $0.067 |
| 월 비용 (730h) | $70.08 | $70.08 | $48.91 |
| 1년 예약 할인율 | ~40% | ~35% | ~37% (CUD) |

가격은 리전, 결제 옵션, 시점에 따라 달라지므로 위 수치는 방향성을 잡는 참고용입니다. 중요한 점은 클라우드 비용 비교가 단순히 시간당 가격만으로 끝나지 않는다는 것입니다. 네트워크 전송 비용, 스토리지 IOPS 과금, 관리형 서비스 가격까지 포함해야 실질적인 TCO(Total Cost of Ownership)가 나옵니다.


## 자주 하는 실수 5가지

1. 루트 계정으로 일상 작업을 처리합니다.
2. 리전을 명시하지 않아 자원이 예상과 다른 위치에 생성됩니다.
3. 공개 버킷 설정을 잘못해 데이터가 노출됩니다.
4. 태그 정책이 없어 비용을 서비스별로 추적하지 못합니다.
5. 테스트 자원을 지우지 않아 비용이 조용히 누적됩니다.

이 실수들은 초보자만의 문제가 아닙니다. 팀이 바쁠수록 태깅, 예산 알림, 최소 권한 같은 기본 원칙이 뒤로 밀리기 쉽습니다. 그래서 초기에 작더라도 규칙을 세워 두는 편이 훨씬 안전합니다.

각 실수에 대한 즉각적인 대응 방법을 정리하면 다음과 같습니다.

| 실수 | 즉각 대응 | 예방 자동화 |
| --- | --- | --- |
| 루트 계정 사용 | IAM 사용자 생성 후 루트 잠금 | AWS Organizations SCP로 루트 API 차단 |
| 리전 미지정 | AWS_DEFAULT_REGION 환경 변수 설정 | Terraform provider block에 리전 고정 |
| 공개 버킷 | S3 Block Public Access 활성화 | 계정 수준 공개 접근 차단 정책 적용 |
| 태그 미적용 | 기존 자원에 태그 일괄 부여 | AWS Config 규칙으로 미태깅 자원 감지 |
| 자원 미삭제 | 비프로덕션 자원 수동 정리 | Lambda + EventBridge로 야간 자동 중지 |

## 운영 기준선 예시

아래 예시는 실제 운영에서 "최소 기준선"을 코드로 관리하는 방법을 보여 줍니다.

```yaml
cloud_baseline:
  account:
    root_mfa_required: true
    break_glass_account: enabled
  security:
    default_public_access_block: true
    iam_access_analyzer: enabled
  cost:
    monthly_budget_usd: 300
    alert_threshold_percent: [50, 80, 100]
  tagging:
    required_keys: [Project, Owner, Environment, CostCenter]
```

이런 기준선을 문서가 아니라 설정으로 유지하면, 신규 프로젝트가 시작될 때마다 같은 실수를 반복할 가능성이 줄어듭니다. 클라우드의 장점은 빠른 생성이고, 단점은 빠른 생성으로 인한 빠른 누수입니다. 기준선 자동화는 이 단점을 구조적으로 줄이는 수단입니다.

## 실무에서는 이렇게 생각합니다

시니어 엔지니어는 클라우드를 "빠르게 실험하게 해 주는 환경"으로 봅니다. 동시에 비용, 권한, 가용성을 아키텍처의 일부로 다룹니다.

- 클라우드는 빠른 실험을 가능하게 하지만, 방치하면 비용도 빠르게 커집니다.
- 책임 경계는 문서로 남겨야 팀 안의 오해가 줄어듭니다.
- 멀티 리전은 목표가 아니라 요구사항의 결과여야 합니다.
- 비용은 회계 항목이 아니라 설계 지표입니다.
- IAM 최소 권한은 처음부터 적용할수록 나중이 편합니다.

## 팀 운영 계약 예시

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

운영 계약을 명시하면 담당자가 바뀌어도 품질 기준이 유지됩니다. 클라우드의 핵심은 리소스를 빨리 만드는 능력이 아니라, 같은 품질을 반복해서 만드는 능력입니다.

## 체크리스트

- [ ] 루트 계정을 잠가 두었는가.
- [ ] MFA가 활성화되어 있는가.
- [ ] 예산 알림이 설정되어 있는가.
- [ ] 리소스 태그 정책이 있는가.
- [ ] 비프로덕션 자원에 자동 중지 정책이 있는가.

## 연습 문제

1. 위 코드에 버킷 삭제 함수를 추가해 보세요.
2. 가까운 리전을 선택하면 왜 지연 시간이 줄어드는지 한 문장으로 설명해 보세요.
3. 지금도 온프레미스가 더 적합한 워크로드 하나를 떠올려 보세요.

## 처음 질문으로 돌아가기

- **왜 많은 팀이 서버를 직접 사는 방식에서 인터넷으로 자원을 빌려 쓰는 방식으로 이동했을까요?**
  초기 투자 부담이 없어지면서 실험과 배포 주기가 빨라졌고, 팀이 하드웨어 운영보다 애플리케이션 설계에 집중할 수 있게 되었기 때문입니다.
- **클라우드의 핵심 특성은 무엇이고, 온프레미스와 비교하면 무엇이 달라질까요?**
  온프레미스는 대규모 초기 투자와 고정 비용이 필요하지만, 클라우드는 종량제 과금과 탄력적 스케일링을 제공합니다. 또한 공급자가 물리 인프라와 기본 서비스를 관리하므로 사용자 팀의 운영 부담이 크게 줄어듭니다.
- **AWS, Azure, Google Cloud 같은 사업자는 정확히 어떤 역할을 맡을까요?**
  AWS, Azure, Google Cloud 같은 CSP는 물리 데이터센터, 네트워크, 기본 보안을 운영하고 사용자에게 추상화된 인터페이스(VM, 스토리지, 데이터베이스 등)를 제공합니다. 사용자는 그 위에 자신의 애플리케이션과 데이터를 올리고, 접근 제어, 운영 자동화, 비용 관리를 담당합니다.

<!-- toc:begin -->
## 시리즈 목차

- **Cloud Computing이란 무엇인가? (현재 글)**
- IaaS, PaaS, SaaS (예정)
- Region과 Availability Zone (예정)
- Compute (예정)
- Storage (예정)
- Network (예정)
- Identity와 Security (예정)
- Monitoring (예정)
- Cost Management (예정)
- Cloud Architecture 기초 (예정)

<!-- toc:end -->

## 참고 자료

- [NIST — Cloud Computing 정의](https://csrc.nist.gov/publications/detail/sp/800-145/final)
- [AWS Well-Architected](https://aws.amazon.com/architecture/well-architected/)
- [Google Cloud — concepts](https://cloud.google.com/docs/overview)
- [Azure — what is cloud computing](https://learn.microsoft.com/azure/cloud-adoption-framework/)
- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

Tags: Cloud, AWS, Infrastructure, DevOps, Networking
