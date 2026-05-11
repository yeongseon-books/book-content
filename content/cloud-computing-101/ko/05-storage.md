---
series: cloud-computing-101
episode: 5
title: Storage
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Cloud
  - Storage
  - S3
  - EBS
  - Architecture
seo_description: 객체·블록·파일·아카이브 등 클라우드 스토리지 종류와 선택 기준을 S3 boto3 예제와 함께 정리한 입문 글
last_reviewed: '2026-05-04'
---

# Storage

> Cloud Computing 101 시리즈 (5/10)


## 이 글에서 다룰 문제

*잘못된 스토리지* 는 *비싸고 느리고* *깨지기 쉽습니다*. 맞으면 *수년간* 그대로.

## 전체 흐름
```mermaid
flowchart LR
    Block["block (EBS)"] --> VM["vm disk"]
    Object["object (S3)"] --> Web["web/api"]
    File["file (EFS)"] --> Share["multi-host share"]
    Archive["archive (Glacier)"] --> Cold["compliance"]
```

## Before/After

**Before**: *모든 파일* 을 *VM 디스크* 에 → *백업 부담*.

**After**: *S3* 에 *객체 저장* + *Glacier* 로 *수명 주기*.

## S3 객체 라이프사이클

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

### 4단계 — 라이프사이클 정책 (의사 JSON)

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

## 이 코드에서 주목할 점

- *prefix* 로 *객체 묶음* 정책.
- *Transition* 은 *비용 절감* 의 *핵심*.
- *EBS* 는 *VM 1개* 와만 결합 (보통).

## 자주 하는 실수 5가지

1. ***공개 ACL* 로 *S3 노출*.**
2. ***라이프사이클 없음* → *비용 누적*.**
3. ***EBS 스냅샷* 미실시.**
4. ***EFS* 를 *고성능 IOPS* 가정.**
5. ***Glacier 복원 시간* 미고려.**

## 실무에서는 이렇게 쓰입니다

*로그* 는 *S3 → 90일 후 Glacier*, *DB 데이터* 는 *EBS gp3*, *공유 디렉터리* 는 *EFS*.

## 체크리스트

- [ ] *기본 암호화* 활성.
- [ ] *수명 주기* 정의.
- [ ] *공개 차단* 기본.
- [ ] *복원 테스트* 연 1회.

## 정리 및 다음 단계

데이터가 자리잡았으면 *연결* 이 다음. 다음 글은 *Network*.

<!-- toc:begin -->
- [Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- [IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Region과 Availability Zone](./03-region-and-availability-zone.md)
- [Compute](./04-compute.md)
- **Storage (현재 글)**
- Network (예정)
- Identity와 Security (예정)
- Monitoring (예정)
- Cost Management (예정)
- Cloud Architecture 기초 (예정)
<!-- toc:end -->

## 참고 자료

- [AWS S3 사용자 가이드](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [AWS EBS](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html)
- [AWS EFS](https://docs.aws.amazon.com/efs/latest/ug/whatisefs.html)
- [AWS Glacier — restore options](https://docs.aws.amazon.com/AmazonS3/latest/userguide/restoring-objects-retrieval-options.html)

Tags: Cloud, Storage, S3, EBS, Architecture
