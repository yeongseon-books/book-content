---
series: cloud-computing-101
episode: 4
title: Compute
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
  - Compute
  - EC2
  - AutoScaling
  - DevOps
seo_description: VM·컨테이너·서버리스 등 클라우드 컴퓨트의 종류와 선택 기준을 boto3 EC2 예제와 함께 정리한 입문 글
last_reviewed: '2026-05-04'
---

# Compute

> Cloud Computing 101 시리즈 (4/10)


## 이 글에서 다룰 문제

*컴퓨트 선택* 이 *비용 60%* 와 *운영 부하* 를 결정합니다.

## 전체 흐름
```mermaid
flowchart LR
    Bare["bare metal"] --> VM["vm"]
    VM --> Container["container"]
    Container --> Serverless["serverless"]
    Serverless --> Code["code"]
```

## Before/After

**Before**: *피크* 에 맞춘 *상시 큰 서버* (낭비).

**After**: *Auto Scaling* 으로 *수요* 따라 *늘고/줄고*.

## boto3로 EC2 인스턴스 다루기

### 1단계 — 클라이언트

```python
import boto3
ec2 = boto3.client("ec2", region_name="us-east-1")
```

### 2단계 — 인스턴스 시작 (예시)

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

## 이 코드에서 주목할 점

- *AMI* 가 *VM 의 출생 사진*.
- *terminate* 는 *되돌릴 수 없음*.
- *인스턴스 타입* = *family.size*.

## 자주 하는 실수 5가지

1. ***스팟* 을 *DB* 에 사용.**
2. ***Auto Scaling* 미설정 → *피크에 다운*.**
3. ***예약* 을 *유연성 없이* 과도 구매.**
4. ***인스턴스 정지 = 비용 0* 오해.**
5. ***로깅 없이* 인스턴스 종료 → *증거 손실*.**

## 실무에서는 이렇게 쓰입니다

*웹* 은 *On-demand + ASG*, *배치* 는 *Spot*, *DB* 는 *예약*, *비결정 워크로드* 는 *Lambda*.

## 체크리스트

- [ ] 워크로드 별 *컴퓨트 매핑*.
- [ ] *ASG* 적용 가능 여부.
- [ ] *예약/스팟* 비율 평가.
- [ ] *종료 정책* 문서.

## 정리 및 다음 단계

컴퓨트는 *움직임*, 다음은 *저장*. 다음 글은 *Storage* 입니다.

<!-- toc:begin -->
- [Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- [IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Region과 Availability Zone](./03-region-and-availability-zone.md)
- **Compute (현재 글)**
- Storage (예정)
- Network (예정)
- Identity와 Security (예정)
- Monitoring (예정)
- Cost Management (예정)
- Cloud Architecture 기초 (예정)
<!-- toc:end -->

## 참고 자료

- [AWS EC2 사용자 가이드](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/concepts.html)
- [AWS Auto Scaling](https://docs.aws.amazon.com/autoscaling/)
- [AWS — Spot Instances](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html)
- [AWS Lambda 개요](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
