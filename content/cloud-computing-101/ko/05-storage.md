---
series: cloud-computing-101
episode: 5
title: "Cloud Computing 101 (5/10): Storage"
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
  - Storage
  - S3
  - EBS
  - Architecture
seo_description: 객체, 블록, 파일, 아카이브 스토리지의 차이와 선택 기준을 정리합니다.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (5/10): Storage

클라우드 스토리지는 전부 비슷해 보이지만, 실제로는 접근 패턴과 내구성, 비용 구조에 따라 완전히 다른 서비스로 나뉩니다. S3, EBS, EFS, Glacier가 따로 존재하는 이유도 여기에 있습니다.

저장소를 잘못 고르면 비용이 늘고 성능이 흔들리며 복구 전략까지 취약해집니다. 반대로 처음에 맞는 저장소를 고르면 오랫동안 큰 수정 없이 안정적으로 운영할 수 있습니다.

이 글은 Cloud Computing 101 시리즈의 5번째 글입니다.

여기서는 객체, 블록, 파일, 아카이브 스토리지를 어떤 기준으로 구분해야 하는지 살펴보겠습니다.

## 먼저 던지는 질문

- 객체, 블록, 파일, 아카이브 스토리지는 각각 무엇이 다를까요?
- 내구성과 가용성은 왜 같은 말이 아닐까요?
- S3 라이프사이클 정책은 어떤 문제를 해결할까요?

## 큰 그림

![Cloud Computing 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/05/05-01-concept-at-a-glance.ko.png)

*Cloud Computing 101 5장 흐름 개요*

Block Storage는 VM에 직접 부착되는 디스크로, OS 설치나 데이터베이스 처리에 사용합니다. Object Storage는 파일 업로드, 백업, 정적 콘텐츠 배포에 최적화됩니다. File Storage는 여러 VM이 동시에 접근해야 할 때 씁니다. Database는 구조화된 데이터와 쿼리가 필요할 때 고르고, Archive는 거의 접근하지 않는 오래된 데이터를 저장할 때 선택합니다.

> 스토리지 선택은 데이터의 구조, 접근 패턴, 내구성 요구사항을 함께 고려하는 결정입니다.

## 왜 중요한가

모든 데이터를 VM 디스크에 몰아넣는 방식은 처음에는 단순해 보여도 백업, 확장, 복구에서 빠르게 한계를 드러냅니다. 반대로 데이터의 성격에 맞춰 저장 계층을 분리하면 비용과 운영 모두 훨씬 예측 가능해집니다.

예를 들어 로그는 S3에 쌓아 두었다가 시간이 지나면 Glacier로 내리는 편이 합리적입니다. 데이터베이스 볼륨은 블록 스토리지가 적합하고, 여러 인스턴스가 공유해야 하는 디렉터리는 파일 스토리지가 맞습니다. 저장소는 “어디든 넣으면 되는 공간”이 아니라 워크로드 구조의 일부입니다.

## 한눈에 보는 개념

블록 스토리지는 디스크처럼, 객체 스토리지는 키-값 저장소처럼, 파일 스토리지는 공유 디렉터리처럼 동작합니다. 아카이브는 거의 읽지 않지만 오래 보관해야 하는 데이터를 위한 계층입니다.

## 핵심 용어

- **Object**: 메타데이터를 가진 키-값 객체 저장 방식입니다.
- **Block**: 고정 블록 단위의 디스크형 저장소입니다.
- **File**: POSIX 스타일 디렉터리 구조를 가진 파일시스템입니다.
- **Durability**: 데이터가 살아남을 확률입니다.
- **Lifecycle**: 시간이 지나면서 저장 계층을 전환하는 정책입니다.

## Before / After

**Before**에서는 모든 파일이 VM 디스크에 놓여 백업과 복구가 악몽이 됩니다.

**After**에서는 객체는 S3에 저장하고, 오래된 데이터는 Glacier로 넘기는 정책을 둡니다.

이렇게 계층을 나누면 저장 비용뿐 아니라 복구 전략도 훨씬 명확해집니다.

## 실습: S3 객체 라이프사이클

### 1단계 — 클라이언트

```python
import boto3
s3 = boto3.client("s3")
```

### 2단계 — 객체 업로드

```python
def put(bucket, key, body):
    s3.put_object(Bucket=bucket, Key=key, Body=body)
    return f"s3://{bucket}/{key}"
```

### 3단계 — 객체 조회

```python
def get(bucket, key):
    res = s3.get_object(Bucket=bucket, Key=key)
    return res["Body"].read()
```

### 4단계 — 라이프사이클 정책

```python
policy = {
    "Rules": [{
        "ID": "to-glacier-after-90d",
        "Status": "Enabled",
        "Filter": {"Prefix": "logs/"},
        "Transitions": [{"Days": 90, "StorageClass": "GLACIER"}],
    }]
}
```

### 5단계 — 적용

```python
def apply_lifecycle(bucket, policy):
    s3.put_bucket_lifecycle_configuration(
        Bucket=bucket, LifecycleConfiguration=policy,
    )
```

이 예제는 저장소 비용 최적화가 나중의 정리 작업이 아니라, 처음부터 정책으로 설계할 수 있는 영역이라는 점을 보여 줍니다. 데이터를 얼마나 오래 둘지, 언제 더 싼 계층으로 내릴지 미리 정해 두면 운영이 훨씬 단순해집니다.

## 이 코드에서 먼저 봐야 할 점

- Prefix를 기준으로 객체 묶음에 같은 정책을 적용할 수 있습니다.
- Transition 규칙이 실제 비용 절감의 핵심입니다.
- EBS는 보통 한 시점에 하나의 VM에 연결합니다.

## 이 예제를 실제로 검증하는 순서

라이프사이클 정책은 만들어 두는 것보다 실제로 버킷에 적용되었는지 확인하는 과정이 더 중요합니다. 정책이 저장되지 않았거나 Prefix가 잘못 잡혀 있으면 비용 최적화는 문서에만 남고 실제 데이터는 계속 비싼 계층에 머뭅니다.

```bash
aws s3api get-bucket-lifecycle-configuration --bucket my-test-bucket-2026
```

**Expected output:**

- `to-glacier-after-90d` 같은 Rule ID가 출력되어야 합니다.
- `logs/` Prefix와 `GLACIER` 전환 규칙이 함께 보여야 합니다.
- 이 확인이 있어야 비용 절감 정책이 실제 저장소에 반영되었다고 말할 수 있습니다.

### 자주 막히는 지점

- S3 버킷 정책과 라이프사이클 정책은 목적이 다릅니다. 하나는 접근 제어이고, 다른 하나는 보관 계층 관리입니다.
- Glacier는 값이 싸지만 즉시 읽기에는 적합하지 않습니다. 복원 시간까지 운영 계획에 넣어야 합니다.
- EFS를 공유 파일시스템으로 쓰면서도 EBS 같은 지연 시간 특성을 기대하면 구조가 어긋납니다.

## 내구성과 가용성은 왜 다를까

내구성은 데이터가 장기적으로 살아남는 가능성에 가깝고, 가용성은 지금 당장 읽고 쓸 수 있는가에 더 가깝습니다. 입문 단계에서는 이 둘을 같은 말처럼 쓰기 쉽지만, 실무에서는 분리해서 봐야 합니다.

예를 들어 아카이브 계층은 내구성이 매우 높아도 즉시 읽기에는 적합하지 않을 수 있습니다. 반대로 빠르게 접근 가능한 스토리지가 항상 가장 싸거나 가장 오래 보관하기 좋은 것은 아닙니다. 저장소 선택은 결국 접근 패턴을 기준으로 해야 합니다.

## 자주 하는 실수 5가지

1. 공개 ACL로 S3 버킷을 노출합니다.
2. 라이프사이클 정책을 만들지 않아 비용이 계속 누적됩니다.
3. EBS 스냅샷을 남기지 않습니다.
4. EFS를 고성능 IOPS 스토리지처럼 기대합니다.
5. Glacier 복원 시간을 고려하지 않습니다.

## 실무에서는 이렇게 생각합니다

- 접근 패턴이 저장소를 결정합니다.
- 암호화는 선택 기능이 아니라 기본값입니다.
- 라이프사이클 정책은 첫날부터 정의하는 편이 좋습니다.
- 복원 비용과 시간도 총비용의 일부입니다.
- 백업과 복제는 같은 개념이 아닙니다.

## 체크리스트

- [ ] 기본 암호화를 활성화했는가.
- [ ] 라이프사이클 정책을 정의했는가.
- [ ] 공개 접근 차단이 기본값으로 설정되어 있는가.
- [ ] 연 1회 이상 복원 테스트를 수행하는가.

## 연습 문제

1. Glacier의 복원 속도 계층 세 가지를 적어 보세요.
2. S3 버전 관리를 켜 둘 만한 현실적인 시나리오 하나를 설명해 보세요.
3. EBS와 EFS의 공유 방식 차이를 한 문장으로 정리해 보세요.

## 정리 및 다음 단계

데이터가 어디에 놓일지 정했다면, 이제는 그 데이터에 어떻게 연결하고 어떤 경로로 접근을 통제할지 살펴봐야 합니다. 다음 글에서는 Cloud 네트워킹의 기본인 Network로 넘어가겠습니다.

Block Storage는 데이터베이스 같은 높은 성능이 필요한 워크로드, Object Storage는 아카이브와 정적 콘텐츠, File Storage는 여러 VM이 공유하는 파일, Archive는 거의 접근하지 않는 데이터에 각각 사용합니다.

각 스토리지 타입은 성능, 비용, 내구성, 스케일 특성이 크게 다릅니다. 워크로드에 맞지 않는 선택은 높은 비용이나 성능 저하로 이어집니다.
  - 본문의 기준은 Storage를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
정기적인 백업, 암호화, 접근 제어를 기본값으로 설정하면 운영 안정성과 보안이 크게 올라갑니다.
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **S3 라이프사이클 정책은 어떤 문제를 해결할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

## 스토리지 선택 기준 상세표

| 유형 | 대표 서비스 | 지연 특성 | 확장 방식 | 적합 워크로드 |
| --- | --- | --- | --- | --- |
| Block | EBS | 낮음 | 볼륨 단위 확장 | DB, 트랜잭션 로그 |
| Object | S3 | 중간 | 거의 무제한 | 이미지, 백업, 로그 |
| File | EFS | 중간 | 공유 파일시스템 | 다중 인스턴스 공유 디렉터리 |
| Archive | Glacier | 높음 | 장기 보관 | 규제 보관, 장기 백업 |

| 질문 | Block | Object | File | Archive |
| --- | --- | --- | --- | --- |
| 랜덤 I/O 성능이 중요한가 | 적합 | 부적합 | 보통 | 부적합 |
| HTTP로 직접 접근해야 하는가 | 부적합 | 적합 | 부적합 | 부적합 |
| 여러 서버가 동시 쓰기하는가 | 제한적 | 제한적 | 적합 | 부적합 |

```yaml
storage_lifecycle:
  logs:
    hot_days: 30
    warm_class: STANDARD_IA
    archive_after_days: 90
    delete_after_days: 365
  uploads:
    versioning: true
    replication: cross_region
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



짧은 결론으로 정리하면, 운영 품질은 도구 선택 자체보다 기준의 일관성과 검증 습관에서 결정됩니다. 기준이 문서와 자동화로 남아 있어야 다음 변경에서도 같은 품질을 반복할 수 있습니다.

## 스토리지 운영 설정 예시

아래는 실제 운영에서 자주 쓰는 검증 명령과 IaC 예시입니다. 핵심은 저장소를 생성한 뒤 접근 제어, 암호화, 수명 주기, 복구 가능성을 함께 점검하는 흐름을 고정하는 것입니다.

```bash
# AWS S3 기본 보안/보관 설정 확인
aws s3api get-public-access-block --bucket my-app-prod
aws s3api get-bucket-encryption --bucket my-app-prod
aws s3api get-bucket-versioning --bucket my-app-prod

# Azure Blob 컨테이너 접근 수준 확인
az storage container show --account-name mystorageacct --name uploads --query properties.publicAccess

# Google Cloud Storage 수명 주기 확인
gcloud storage buckets describe gs://my-app-prod --format="value(lifecycle)"
```

```hcl
resource "aws_s3_bucket" "app" {
  bucket = "my-app-prod"
}

resource "aws_s3_bucket_versioning" "app" {
  bucket = aws_s3_bucket.app.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_lifecycle_configuration" "app" {
  bucket = aws_s3_bucket.app.id
  rule {
    id     = "logs-tiering"
    status = "Enabled"
    filter { prefix = "logs/" }
    transition {
      days          = 30
      storage_class = "STANDARD_IA"
    }
    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}
```

| 비교 항목 | S3 Standard | S3 Standard-IA | S3 Glacier Instant Retrieval |
| --- | --- | --- | --- |
| 접근 빈도 | 높음 | 중간~낮음 | 낮음 |
| 조회 지연 | 낮음 | 낮음 | 중간 |
| 저장 단가 경향 | 높음 | 중간 | 낮음 |
| 주요 용도 | 운영 데이터 | 장기 로그 | 감사/보관 데이터 |

텍스트 아키텍처 다이어그램:
`App -> S3(Standard) -> Lifecycle(30일) -> S3 IA -> Lifecycle(90일) -> Glacier -> Restore Job`

<!-- toc:begin -->
## 시리즈 목차

- [Cloud Computing 101 (1/10): Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region과 Availability Zone](./03-region-and-availability-zone.md)
- [Cloud Computing 101 (4/10): Compute](./04-compute.md)
- **Storage (현재 글)**
- Network (예정)
- Identity와 Security (예정)
- Monitoring (예정)
- Cost Management (예정)
- Cloud Architecture 기초 (예정)

<!-- toc:end -->

## 참고 자료

- [AWS S3 user guide](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [AWS EBS](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html)
- [AWS EFS](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html)
- [AWS Glacier — restore options](https://docs.aws.amazon.com/AmazonS3/latest/userguide/restoring-objects-retrieval-options.html)

Tags: Cloud, Storage, S3, EBS, Architecture
