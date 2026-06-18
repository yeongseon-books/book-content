---
series: cloud-computing-101
episode: 2
title: "바이브코딩을 위한 클라우드 컴퓨팅 기초 (2/10): IaaS, PaaS, SaaS"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 클라우드
  - IaaS
  - PaaS
  - SaaS
language: ko
---

# 바이브코딩을 위한 클라우드 컴퓨팅 기초 (2/10): IaaS, PaaS, SaaS

이 글은 **바이브코딩을 위한 클라우드 컴퓨팅 기초** 시리즈의 2편입니다. AI가 만든 앱을 클라우드에 올리려면 어떤 서비스 모델을 선택해야 하는지 알아야 합니다. 10편에 걸쳐 클라우드의 핵심 개념을 바이브코딩 관점에서 정리합니다.

---

바이브코딩으로 AI 챗봇을 만들었습니다. 이제 배포해야 하는데, 친구는 "EC2에 올려"라고 하고, 유튜브는 "Heroku가 쉬워"라고 하며, 회사 선배는 "Lambda 써봐"라고 합니다. 다 클라우드인데 왜 이렇게 다를까요?

핵심 질문은 하나입니다. **누가 무엇을 운영하는가.** 이 한 문장을 이해하면 EC2, Heroku, Notion이 왜 모두 클라우드이면서도 전혀 다르게 느껴지는지 설명할 수 있습니다.

> "IaaS, PaaS, SaaS는 각 서비스 모델마다 공급자와 사용자가 맡는 책임의 경계가 다릅니다. 이 경계를 명확히 이해해야 AI 앱에 맞는 기술을 선택할 수 있습니다."

## 이 글에서 다룰 질문들

- EC2(IaaS)와 Heroku(PaaS)와 Notion(SaaS)은 왜 이렇게 다르게 느껴질까요?
- AI 앱을 처음 배포할 때 IaaS, PaaS, FaaS 중 무엇을 선택해야 할까요?
- 운영 인력 없이 혼자 AI 앱을 운영하려면 어떤 모델이 현실적인가요?
- PaaS에서 IaaS로 전환해야 하는 시점은 언제인가요?
- 서버리스(FaaS)가 AI 앱에 항상 좋은 선택일까요?

---

## 바이브코딩과 서비스 모델: 어떤 것을 골라야 하나요?

AI 앱을 배포하는 방법은 크게 세 가지입니다. 각각 운영 부담과 유연성이 다릅니다.

### Before: 무조건 IaaS(EC2) 선택

```bash
# "서버에 올려야 한다" → EC2 선택
# 그 다음 해야 할 일들...
# 1. OS 업데이트
# 2. Python 설치
# 3. nginx 설정
# 4. SSL 인증서
# 5. 로그 수집
# 6. 모니터링 설정
# ...
# 일주일이 지나도 AI 앱은 아직 배포 안 됨
```

### After: 목적에 맞는 모델 선택

```python
# PaaS (예: Render, Railway, Heroku)
# app.py만 있으면 됨
from flask import Flask
app = Flask(__name__)

@app.route("/chat")
def chat():
    # AI 로직
    return {"response": "안녕하세요!"}

# git push 하면 배포 완료
# OS, 서버 설정은 플랫폼이 처리
```

---

## IaaS, PaaS, SaaS, FaaS 한눈에 비교

| 구분 | 예시 | 내가 관리 | 플랫폼이 관리 | AI 앱 적합도 |
| --- | --- | --- | --- | --- |
| IaaS | EC2, Compute Engine | OS, 런타임, 앱 | 물리 인프라 | 세밀한 제어 필요 시 |
| PaaS | Heroku, Render, Railway | 앱 코드 | OS, 런타임, 인프라 | 빠른 시작에 최적 |
| FaaS | Lambda, Cloud Functions | 함수 코드 | 실행 환경 전체 | 간헐적 AI 추론에 좋음 |
| SaaS | OpenAI API, Google Translate | 사용자 설정 | 모든 것 | AI 기능을 API로 쓸 때 |

---

## 바이브코딩 AI 앱의 배포 경로

AI 앱은 보통 이런 순서로 발전합니다:

```
1단계: 로컬 테스트
   └─ python app.py

2단계: PaaS 배포 (권장 시작점)
   └─ git push → 자동 배포
   └─ 운영 부담 최소

3단계: 컨테이너 (트래픽 증가 시)
   └─ Docker → ECS/Cloud Run
   └─ 유연성 증가, 운영 부담 증가

4단계: IaaS (고급 제어 필요 시)
   └─ GPU 인스턴스, 특수 설정
   └─ 최대 유연성, 최대 운영 부담
```

---

## FaaS(서버리스)와 AI 앱

Lambda나 Cloud Functions는 AI 앱에 자주 쓰입니다. 하지만 함정도 있습니다.

```python
# Lambda로 AI 추론 함수 만들기
import json
import boto3

def lambda_handler(event, context):
    # 간단한 텍스트 분류
    text = event.get("text", "")

    # AI 모델 호출 (예: Bedrock, SageMaker)
    # ...

    return {
        "statusCode": 200,
        "body": json.dumps({"result": "positive", "confidence": 0.87})
    }
```

| 상황 | FaaS 적합 여부 | 이유 |
| --- | --- | --- |
| 간헐적 AI 추론 (분당 수 건) | 적합 | 실행 시간만 과금 |
| 실시간 챗봇 (초당 수십 건) | 주의 | 콜드 스타트 지연 발생 |
| 대용량 모델 로딩 | 부적합 | 메모리/시간 제한 존재 |
| 이미지 처리 파이프라인 | 적합 | 이벤트 기반 처리에 강함 |

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| AI 앱에 무조건 IaaS 선택 | 운영 부담이 너무 큼 | PaaS로 시작해서 필요 시 이전 |
| FaaS로 대용량 모델 서빙 | 메모리/시간 제한에 걸림 | ECS나 전용 인스턴스 사용 |
| SaaS API 키 코드에 하드코딩 | 보안 사고 위험 | 환경 변수 또는 Secrets Manager |
| 처음부터 Kubernetes 선택 | 학습 비용 과다 | PaaS → 컨테이너 순서로 이동 |
| SaaS 데이터 락인 무시 | 나중에 이전 비용 폭발 | 데이터 내보내기 API 확인 필수 |

---

## AI 팁: 서비스 모델 선택 가이드

1. **처음 배포**: PaaS(Render, Railway, Heroku)로 시작하세요. git push 한 번으로 배포됩니다.
2. **AI API 연동**: OpenAI, Anthropic 같은 SaaS API를 쓰면 모델 운영 없이 AI 기능 추가 가능합니다.
3. **비용 모니터링**: PaaS도 사용량이 늘면 비용이 늘어납니다. 무료 티어 한도를 확인하세요.
4. **FaaS 적합성 체크**: AI 함수의 실행 시간이 15분 이하이고 간헐적 호출이면 Lambda가 경제적입니다.

---

## 실전 체크리스트

- [ ] 내 AI 앱의 트래픽 패턴(상시/간헐적)을 파악했다
- [ ] IaaS, PaaS, FaaS 중 현재 상황에 맞는 것을 선택했다
- [ ] 선택한 서비스 모델의 운영 책임 범위를 이해하고 있다
- [ ] API 키 등 비밀 정보를 환경 변수로 관리하고 있다
- [ ] 월 비용 예상치를 계산해봤다
- [ ] SaaS를 도입한다면 데이터 내보내기 옵션을 확인했다

---

## 처음 질문으로 돌아가기

- **AI 앱을 처음 배포할 때 어떤 모델을 선택해야 할까요?**
  PaaS로 시작하는 것이 현실적입니다. 운영 인력 없이도 git push 한 번으로 배포할 수 있고, 트래픽이 증가하면 그때 IaaS나 컨테이너로 이전합니다.

- **서버리스(FaaS)가 AI 앱에 항상 좋은 선택일까요?**
  간헐적 추론, 이벤트 기반 처리에는 강력하지만 대용량 모델 서빙, 긴 실행 시간, WebSocket에는 부적합합니다. 워크로드 특성을 먼저 확인하세요.

- **PaaS에서 IaaS로 전환해야 하는 시점은 언제인가요?**
  월 PaaS 비용이 $200~500을 넘거나, 플랫폼 제약(특수 하드웨어, 커널 설정 등)이 생길 때입니다.

---

## 정리

AI 앱 배포의 첫 질문은 "어느 클라우드?"가 아니라 "어떤 서비스 모델?"이어야 합니다. 혼자 운영한다면 PaaS, 간헐적 AI 함수라면 FaaS, 외부 AI API를 쓴다면 SaaS가 가장 빠른 선택입니다. 다음 글에서는 어디에 배포할지, 즉 Region과 가용 영역(AZ)을 다룹니다.

---

## 참고 자료

- [NIST SP 800-145 — service models](https://csrc.nist.gov/publications/detail/sp/800-145/final)
- [AWS — types of cloud computing](https://aws.amazon.com/types-of-cloud-computing/)
- [Vercel — serverless functions](https://vercel.com/docs/functions)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (1/10): Cloud Computing이란 무엇인가?
- **바이브코딩을 위한 클라우드 컴퓨팅 기초 (2/10): IaaS, PaaS, SaaS (현재 글)**
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (3/10): Region과 Availability Zone
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (4/10): Compute
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (5/10): Storage
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (6/10): Network
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (7/10): Identity와 Security
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (8/10): Monitoring
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (9/10): Cost Management
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (10/10): Cloud Architecture 기초
<!-- toc:end -->

Tags: 바이브코딩, 클라우드, IaaS, PaaS, SaaS
