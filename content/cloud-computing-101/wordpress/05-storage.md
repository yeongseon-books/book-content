---
series: cloud-computing-101
episode: 5
title: "바이브코딩을 위한 클라우드 컴퓨팅 기초 (5/10): Storage"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 클라우드
  - Storage
  - S3
  - AWS
language: ko
---

# 바이브코딩을 위한 클라우드 컴퓨팅 기초 (5/10): Storage

이 글은 **바이브코딩을 위한 클라우드 컴퓨팅 기초** 시리즈의 5편입니다. AI가 만든 앱이 생성하는 데이터를 어디에 저장할지 알아야 합니다. 10편에 걸쳐 클라우드의 핵심 개념을 바이브코딩 관점에서 정리합니다.

---

바이브코딩으로 만든 AI 앱이 이미지를 생성하거나 사용자 파일을 처리한다고 합시다. 그 파일들을 어디에 저장해야 할까요? EC2 서버 디스크에 저장했다가 서버를 삭제하면 모든 파일이 사라집니다. 반대로 처음부터 S3를 쓰면 서버와 독립적으로 파일이 안전하게 보관됩니다.

저장소를 잘못 고르면 비용이 늘고, 성능이 흔들리며, 복구 전략까지 취약해집니다. AI 앱은 특히 이미지, 모델 파일, 학습 데이터, 사용자 업로드 등 다양한 종류의 데이터를 다루기 때문에 스토리지 선택이 중요합니다.

> "스토리지 선택은 데이터의 구조, 접근 패턴, 내구성 요구사항을 함께 고려하는 결정입니다."

## 이 글에서 다룰 질문들

- S3, EBS, EFS, Glacier는 어떤 상황에 사용해야 할까요?
- AI 생성 이미지나 모델 파일은 어디에 저장해야 할까요?
- S3 라이프사이클 정책으로 비용을 어떻게 줄이나요?
- S3 버킷을 실수로 공개하면 어떤 위험이 생기나요?
- 내구성과 가용성은 어떻게 다른가요?

---

## 바이브코딩 AI 앱의 스토리지 패턴

### Before: 서버 디스크에 모든 것 저장

```python
import os

# AI 생성 이미지를 서버 로컬에 저장
def save_generated_image(image_data: bytes, filename: str):
    path = f"/home/ubuntu/images/{filename}"
    with open(path, "wb") as f:
        f.write(image_data)
    return path

# 문제들:
# 1. 서버 재시작/삭제 시 파일 사라짐
# 2. 서버 하나에만 있어 다른 서버에서 접근 불가
# 3. 디스크 용량 제한
# 4. 백업 없음
```

### After: S3로 분리

```python
import boto3

s3 = boto3.client("s3", region_name="ap-northeast-2")
BUCKET = "my-ai-app-generated"

def save_generated_image(image_data: bytes, filename: str) -> str:
    """AI 생성 이미지를 S3에 저장하고 URL 반환"""
    s3.put_object(
        Bucket=BUCKET,
        Key=f"images/{filename}",
        Body=image_data,
        ContentType="image/png"
    )
    return f"https://{BUCKET}.s3.ap-northeast-2.amazonaws.com/images/{filename}"

# 장점:
# - 서버와 독립적으로 보관
# - 여러 서버에서 동시 접근 가능
# - 거의 무제한 용량
# - 99.999999999% 내구성
```

---

## AI 앱을 위한 스토리지 유형 선택 가이드

| 스토리지 유형 | AWS 서비스 | AI 앱 사용 예 | 특징 |
| --- | --- | --- | --- |
| 객체(Object) | S3 | 이미지, 모델 파일, 데이터셋 | 거의 무제한, HTTP 직접 접근 |
| 블록(Block) | EBS | AI 서버 OS 디스크, DB 볼륨 | 빠른 I/O, 단일 서버 연결 |
| 파일(File) | EFS | 여러 서버가 공유하는 모델 파일 | 공유 파일시스템, NFS |
| 아카이브 | Glacier | 오래된 학습 로그, 규정 보관 | 저렴하지만 복구에 시간 필요 |

---

## S3로 AI 앱 데이터 관리하기

```python
import boto3
import json
from datetime import datetime

s3 = boto3.client("s3")

# AI 앱에서 S3를 쓰는 패턴들

# 1. 사용자 업로드 파일 저장
def upload_user_file(file_content: bytes, user_id: str, filename: str) -> str:
    key = f"users/{user_id}/uploads/{filename}"
    s3.put_object(Bucket="my-app", Key=key, Body=file_content)
    return key

# 2. AI 처리 결과 저장
def save_ai_result(result: dict, request_id: str) -> str:
    key = f"results/{datetime.now():%Y/%m/%d}/{request_id}.json"
    s3.put_object(
        Bucket="my-app",
        Key=key,
        Body=json.dumps(result, ensure_ascii=False).encode()
    )
    return key

# 3. 라이프사이클: 오래된 데이터 자동 저렴한 계층으로 이동
lifecycle_policy = {
    "Rules": [{
        "ID": "move-old-results-to-ia",
        "Status": "Enabled",
        "Filter": {"Prefix": "results/"},
        "Transitions": [
            {"Days": 30, "StorageClass": "STANDARD_IA"},
            {"Days": 90, "StorageClass": "GLACIER"},
        ],
        "Expiration": {"Days": 365}  # 1년 후 자동 삭제
    }]
}
```

---

## S3 스토리지 클래스: 비용 최적화

| 클래스 | 월 비용(GB) | 접근 속도 | 최적 사용 |
| --- | --- | --- | --- |
| Standard | $0.023 | 즉시 | AI 앱 활성 데이터 |
| Standard-IA | $0.0125 | 즉시 | 30일 이상 미접근 데이터 |
| Glacier Instant | $0.004 | 즉시 | 장기 보관, 가끔 접근 |
| Glacier Deep | $0.00099 | 12~48시간 | 규정 준수 장기 보관 |

**바이브코딩 관점 팁:** AI 앱의 학습 로그나 이전 모델 파일은 Lifecycle Policy로 자동으로 Glacier로 내리면 비용을 80% 이상 절약할 수 있습니다.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| S3 버킷 공개 설정 실수 | 사용자 데이터가 인터넷에 노출 | Block Public Access 기본 활성화 |
| 라이프사이클 정책 없음 | 오래된 데이터가 비싼 계층에 쌓임 | 30/90일 IA/Glacier 전환 규칙 설정 |
| 암호화 미설정 | 데이터 보호 기준 미충족 | SSE-S3 기본 암호화 설정 |
| 버전 관리 없이 파일 덮어쓰기 | 실수로 삭제 시 복구 불가 | 중요 버킷은 Versioning 활성화 |
| 로컬 디스크에 AI 모델 파일 저장 | 서버 삭제 시 모델 분실 | S3에 모델 파일 보관 |

---

## AI 팁: AI 앱 스토리지 설계

1. **사용자 업로드 → S3 직접 업로드**: 서버를 거치지 않고 Presigned URL로 S3에 직접 업로드하면 서버 부하가 줄어듭니다.
2. **AI 모델 파일 중앙 관리**: 모델 파일을 S3에 저장하고 서버 시작 시 다운로드하면 여러 서버가 같은 모델을 공유합니다.
3. **비용 태그 붙이기**: S3 버킷에 `project`, `team` 태그를 붙이면 나중에 비용 추적이 쉬워집니다.
4. **암호화 기본값 설정**: 처음 버킷 만들 때부터 SSE-S3 암호화를 기본으로 켜두세요.

---

## 실전 체크리스트

- [ ] AI 앱의 모든 파일을 S3에 저장하고 있다 (서버 디스크 아님)
- [ ] S3 버킷의 Block Public Access가 활성화되어 있다
- [ ] 라이프사이클 정책으로 오래된 데이터를 자동으로 저렴한 계층으로 이동한다
- [ ] 기본 암호화(SSE-S3)가 설정되어 있다
- [ ] 중요한 데이터는 Versioning이 켜져 있다
- [ ] 아카이브 데이터 복원 시간을 운영 계획에 포함시켰다

---

## 처음 질문으로 돌아가기

- **AI 생성 이미지나 모델 파일은 어디에 저장해야 할까요?**
  S3가 정답입니다. 서버와 독립적이고, 거의 무제한 용량이며, 99.999999999% 내구성을 제공합니다. 서버 디스크(EBS)는 임시 작업 파일에만 사용하세요.

- **S3 버킷을 실수로 공개하면 어떤 위험이 생기나요?**
  사용자 개인정보, AI 모델, 학습 데이터가 인터넷에 그대로 노출됩니다. Block Public Access를 기본값으로 설정하고, 공개가 필요한 파일만 CloudFront를 통해 제공하세요.

- **S3 라이프사이클 정책으로 비용을 어떻게 줄이나요?**
  30일 이상 미접근 파일은 Standard-IA로, 90일 후에는 Glacier로 자동 이동하도록 설정하면 스토리지 비용을 80% 이상 줄일 수 있습니다.

---

## 정리

AI 앱의 데이터는 처음부터 S3를 기반으로 설계해야 합니다. 서버 디스크는 임시 작업용이고, 영구 보관은 S3입니다. 라이프사이클 정책과 암호화는 처음 버킷 만들 때 설정하는 것이 나중에 고치는 것보다 훨씬 쉽습니다. 다음 글에서는 AI 앱에 접속하는 네트워크 구조를 다룹니다.

---

## 참고 자료

- [AWS S3 사용자 가이드](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Welcome.html)
- [AWS EBS 볼륨 타입](https://docs.aws.amazon.com/ebs/latest/userguide/ebs-volume-types.html)
- [S3 스토리지 클래스](https://aws.amazon.com/s3/storage-classes/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (1/10): Cloud Computing이란 무엇인가?
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (2/10): IaaS, PaaS, SaaS
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (3/10): Region과 Availability Zone
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (4/10): Compute
- **바이브코딩을 위한 클라우드 컴퓨팅 기초 (5/10): Storage (현재 글)**
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (6/10): Network
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (7/10): Identity와 Security
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (8/10): Monitoring
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (9/10): Cost Management
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (10/10): Cloud Architecture 기초
<!-- toc:end -->

Tags: 바이브코딩, 클라우드, Storage, S3, AWS
