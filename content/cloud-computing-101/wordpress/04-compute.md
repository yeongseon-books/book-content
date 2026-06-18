---
series: cloud-computing-101
episode: 4
title: "바이브코딩을 위한 클라우드 컴퓨팅 기초 (4/10): Compute"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 클라우드
  - Compute
  - EC2
  - 서버리스
language: ko
---

# 바이브코딩을 위한 클라우드 컴퓨팅 기초 (4/10): Compute

이 글은 **바이브코딩을 위한 클라우드 컴퓨팅 기초** 시리즈의 4편입니다. AI가 만든 앱을 클라우드에서 실행하려면 컴퓨트를 이해해야 합니다. 10편에 걸쳐 클라우드의 핵심 개념을 바이브코딩 관점에서 정리합니다.

---

바이브코딩으로 만든 AI 챗봇을 배포했는데, 갑자기 사용자가 몰리자 서버가 먹통이 됩니다. 반대로 밤새 아무도 안 쓰는데 서버는 계속 켜져 있어서 월 $200이 나옵니다. 컴퓨트를 잘못 선택하면 이 두 가지 문제가 동시에 발생합니다.

클라우드에서 비용과 운영 피로를 가장 크게 좌우하는 것이 컴퓨트입니다. VM에 올릴지, 컨테이너로 돌릴지, 서버리스로 실행할지에 따라 비용과 운영 방식이 완전히 달라집니다.

> "워크로드의 특성에 맞는 실행 모델을 선택하는 게 중요합니다. 추상화가 높을수록 운영 부담은 줄지만, 제어권과 비용 효율성은 함께 변합니다."

## 이 글에서 다룰 질문들

- VM(EC2), 컨테이너, 서버리스 중 AI 앱에 무엇이 맞나요?
- Auto Scaling은 AI 앱에서 어떻게 동작하나요?
- GPU 인스턴스는 언제 필요하고 비용은 얼마나 되나요?
- Spot 인스턴스로 AI 학습 비용을 줄이는 방법은 무엇인가요?
- 컴퓨트 비용을 절반으로 줄이는 실용적인 전략은 무엇인가요?

---

## 바이브코딩과 컴퓨트: 무엇을 선택해야 하나요?

### Before: 컴퓨트 이해 없이 배포

```
AI 앱 완성 → "서버가 필요하다" → EC2 m5.xlarge 선택 (왜인지 모름)
→ 24시간 365일 켜둠 → 월 $140 청구
→ 밤에는 아무도 안 씀 → 낭비
→ 피크 때 하나로 버틸 수 없음 → 서비스 다운
```

### After: 워크로드에 맞는 컴퓨트 선택

```python
# AI 앱 워크로드 분석
workload_analysis = {
    "api_server": {
        "패턴": "상시 트래픽, 업무 시간 집중",
        "선택": "EC2 t3.small + Auto Scaling",
        "이유": "안정적 기본, 피크에 자동 확장"
    },
    "ai_inference": {
        "패턴": "요청 단위, 간헐적",
        "선택": "Lambda",
        "이유": "요청마다 과금, 0일 때 비용 0"
    },
    "ai_training": {
        "패턴": "야간 배치, 중단 가능",
        "선택": "Spot 인스턴스 (p3.2xlarge)",
        "이유": "온디맨드 대비 70% 절약"
    }
}
```

---

## 컴퓨트 유형 비교: AI 앱 관점

| 유형 | 예시 | AI 앱 적합 상황 | 월 비용 (참고) |
| --- | --- | --- | --- |
| 범용 VM | t3.micro, t3.small | 소규모 AI API 서버 | $8~$18 |
| 컴퓨트 최적화 | c5.large | LLM 추론, 텍스트 처리 | $62 |
| GPU 인스턴스 | g4dn.xlarge | 이미지 AI, 모델 미세조정 | $380 |
| 서버리스 | Lambda | 간헐적 AI 함수 호출 | 호출당 과금 |
| Spot | m5.large Spot | AI 모델 학습 배치 | ~$21 (70% 절약) |

---

## Auto Scaling으로 AI 앱 트래픽 대응

```python
import boto3

ec2 = boto3.client("ec2", region_name="ap-northeast-2")
autoscaling = boto3.client("autoscaling", region_name="ap-northeast-2")

# AI 앱 Auto Scaling 그룹 설정 (개념 예시)
asg_config = {
    "AutoScalingGroupName": "ai-app-asg",
    "MinSize": 1,          # 최소 1대 (비용 최적화)
    "MaxSize": 10,         # 피크 시 최대 10대
    "DesiredCapacity": 2,  # 평소 2대
    # CPU 60% 초과 시 스케일 아웃
    # CPU 30% 이하 유지 시 스케일 인
}

# 핵심: AI 앱이 Stateless여야 Auto Scaling 효과적
# 세션 정보를 서버 메모리가 아닌 Redis나 DynamoDB에 저장
```

**중요:** Auto Scaling은 마법이 아닙니다. AI 앱이 상태(세션, 캐시)를 서버 내부에 들고 있으면 새 인스턴스가 추가돼도 제대로 동작하지 않습니다.

---

## GPU 인스턴스: AI 앱에서 언제 필요한가

```python
# GPU가 필요한 경우와 그렇지 않은 경우

# GPU 불필요 - OpenAI/Anthropic API 호출
import openai

def get_ai_response(prompt: str) -> str:
    # API 호출 - GPU는 OpenAI 서버에 있음
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# GPU 필요 - 자체 모델 실행
# import torch
# model = load_local_model()  # GPU 메모리 필요
# result = model.generate(input_tensor.cuda())
```

| AI 작업 | GPU 필요 여부 | 대안 |
| --- | --- | --- |
| OpenAI API 호출 | 불필요 | 일반 인스턴스 |
| 자체 LLM 서빙 | 필요 | g4dn.xlarge ($0.526/h) |
| 이미지 생성 모델 | 필요 | g5.xlarge ($1.006/h) |
| 텍스트 분류 (소형 모델) | 선택 | CPU도 가능 |
| 모델 파인튜닝 | 필요 | Spot p3 권장 |

---

## Spot 인스턴스로 AI 학습 비용 절약

```python
# Spot 인스턴스는 중단 가능한 AI 학습에 최적
# 온디맨드 대비 60-90% 저렴

spot_config = {
    "이점": "온디맨드 $0.096/h → Spot ~$0.03/h (p5.48xlarge는 더 극적)",
    "주의": "AWS가 용량 필요 시 2분 전 알림 후 강제 중단",
    "대응": "체크포인트 저장으로 중단 시 이어서 학습 가능"
}

# 체크포인트 패턴 (PyTorch 예시 개념)
def save_checkpoint(model, optimizer, epoch, path):
    """2분 중단 알림 시 즉시 저장"""
    import torch
    torch.save({
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
    }, path)
    print(f"Checkpoint saved at epoch {epoch}")
```

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| GPU 인스턴스 24시간 켜두기 | 월 $380+ 청구 | 사용 시간에만 켜기, Spot 활용 |
| AI 앱에 무조건 큰 인스턴스 | "혹시 모르니" 과잉 프로비저닝 | t3.small에서 시작, 모니터링 후 조정 |
| 중지 = 비용 0 착각 | 중지해도 EBS 비용 발생 | 테스트 인스턴스는 종료(terminate) |
| Auto Scaling 없이 단일 인스턴스 | 피크 시 서비스 다운 | 최소 ASG min=1, max=3으로 설정 |
| Spot으로 DB 운영 | 강제 중단 시 데이터 손실 | DB는 온디맨드/Reserved만 사용 |

---

## AI 팁: 컴퓨트 비용 최적화

1. **작게 시작하기**: AI 앱을 처음 배포할 때 t3.micro(무료 티어)나 t3.small에서 시작하세요. 실제 CPU/메모리 사용량을 보고 조정합니다.
2. **개발 환경 야간 중지**: Lambda나 EventBridge로 업무 시간 외에는 개발 EC2를 자동 중지하면 비용을 70% 이상 줄일 수 있습니다.
3. **API 기반 AI 사용**: 자체 GPU 서버 대신 OpenAI, Anthropic API를 쓰면 인프라 비용 없이 AI 기능을 추가할 수 있습니다.
4. **Spot으로 AI 학습**: 모델 파인튜닝은 체크포인트를 저장하면서 Spot 인스턴스로 돌리면 비용이 극적으로 줄어듭니다.

---

## 실전 체크리스트

- [ ] AI 앱의 워크로드 패턴(상시/간헐적/배치)을 파악했다
- [ ] 적절한 인스턴스 타입을 선택했다 (t3, c5, g4dn 중)
- [ ] Auto Scaling을 설정했다 (min/max/desired)
- [ ] AI 앱이 Stateless하게 설계되어 있다
- [ ] 개발 환경의 야간/주말 자동 중지를 설정했다
- [ ] GPU가 필요한지 vs API 호출로 대체 가능한지 검토했다

---

## 처음 질문으로 돌아가기

- **VM, 컨테이너, 서버리스 중 AI 앱에 무엇이 맞나요?**
  처음 배포라면 PaaS(컨테이너 기반)나 Lambda(서버리스)가 운영 부담이 적습니다. 세밀한 GPU 제어가 필요하면 EC2로 이동합니다.

- **GPU 인스턴스는 언제 필요한가요?**
  OpenAI/Anthropic API를 쓴다면 GPU 인스턴스는 불필요합니다. 자체 모델을 운영하거나 미세조정할 때 필요합니다.

- **컴퓨트 비용을 절반으로 줄이는 방법은?**
  개발 환경 야간 중지(70% 절약), AI 학습에 Spot 인스턴스 활용(60~90% 절약), 실제 사용량 기반 라이트사이징이 핵심입니다.

---

## 정리

컴퓨트는 AI 앱의 성능과 비용을 동시에 결정합니다. 작게 시작해서 모니터링하고 조정하는 습관이 비용 폭탄을 막는 핵심입니다. 다음 글에서는 AI 앱이 생성하는 데이터를 어디에, 어떻게 저장할지 Storage를 다룹니다.

---

## 참고 자료

- [AWS EC2 인스턴스 타입](https://aws.amazon.com/ec2/instance-types/)
- [AWS Lambda 개요](https://docs.aws.amazon.com/lambda/latest/dg/welcome.html)
- [AWS Spot 인스턴스](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/using-spot-instances.html)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (1/10): Cloud Computing이란 무엇인가?
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (2/10): IaaS, PaaS, SaaS
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (3/10): Region과 Availability Zone
- **바이브코딩을 위한 클라우드 컴퓨팅 기초 (4/10): Compute (현재 글)**
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (5/10): Storage
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (6/10): Network
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (7/10): Identity와 Security
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (8/10): Monitoring
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (9/10): Cost Management
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (10/10): Cloud Architecture 기초
<!-- toc:end -->

Tags: 바이브코딩, 클라우드, Compute, EC2, 서버리스
