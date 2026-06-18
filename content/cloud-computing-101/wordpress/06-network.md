---
series: cloud-computing-101
episode: 6
title: "바이브코딩을 위한 클라우드 컴퓨팅 기초 (6/10): Network"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - 클라우드
  - 네트워크
  - VPC
  - AWS
language: ko
---

# 바이브코딩을 위한 클라우드 컴퓨팅 기초 (6/10): Network

이 글은 **바이브코딩을 위한 클라우드 컴퓨팅 기초** 시리즈의 6편입니다. AI가 만든 앱을 클라우드에 올리려면 네트워크 구조를 이해해야 합니다. 10편에 걸쳐 클라우드의 핵심 개념을 바이브코딩 관점에서 정리합니다.

---

바이브코딩으로 AI 앱을 만들고 EC2에 올렸는데, 외부에서 접속이 안 됩니다. 포트를 열어야 한다는 건 알겠는데 보안 그룹? NACL? VPC? 서브넷? 용어가 낯설고 헷갈립니다. 잘못 설정하면 보안 구멍이 뚫리거나, 반대로 아무것도 접근이 안 됩니다.

클라우드 네트워크는 처음 설계할 때는 단순해 보여도, 한번 구조가 잡히면 나중에 되돌리기 가장 어려운 영역입니다. 초반에 제대로 이해하면 이후 모든 것이 쉬워집니다.

> "네트워크 설계는 보안, 성능, 비용을 동시에 고려하는 선택입니다. 단순한 연결이 아니라 운영 경계를 명확히 정하는 결정입니다."

## 이 글에서 다룰 질문들

- VPC, 서브넷, 보안 그룹의 역할은 각각 무엇인가요?
- AI 앱 서버는 Public 서브넷에 둬야 할까요, Private 서브넷에 둬야 할까요?
- 로드 밸런서(ALB)는 왜 필요하고 어떻게 동작하나요?
- SSH 포트를 0.0.0.0/0으로 열면 왜 위험한가요?
- AI 앱의 데이터베이스 서버는 어떻게 보호해야 하나요?

---

## 바이브코딩 AI 앱의 네트워크 기본 구조

### Before: 보안 없이 모든 포트 개방

```
EC2 인스턴스 → 보안 그룹: 모든 포트, 모든 IP 허용
AI 앱 DB 서버 → Public IP 부여, 인터넷에서 직접 접근 가능
→ 봇이 22번 포트 스캔 → 브루트포스 공격
→ DB 포트 3306이 노출 → 직접 공격 가능
```

### After: 계층적 보안 구조

```
인터넷 → ALB (Public 서브넷, 443 포트만 허용)
            ↓
         AI 앱 서버 (Private 서브넷, ALB에서만 접근)
            ↓
         DB 서버 (별도 Private 서브넷, 앱 서버에서만 접근)

→ 외부에서 DB 직접 접근 불가
→ 22번 포트는 VPN이나 Bastion Host를 통해서만 접근
```

---

## VPC 핵심 구성 요소

| 구성 요소 | 역할 | AI 앱 예시 |
| --- | --- | --- |
| VPC | 논리적으로 격리된 네트워크 | AI 앱 전체 인프라를 담는 울타리 |
| Public 서브넷 | 인터넷에서 직접 접근 가능 | ALB, NAT Gateway 배치 |
| Private 서브넷 | 인터넷에서 직접 접근 불가 | AI 앱 서버, DB 배치 |
| 보안 그룹 | 인스턴스 단위 방화벽 | "앱 서버는 ALB에서만 8080 허용" |
| ALB | 트래픽 분산, HTTPS 종료 | 외부에서 AI 앱으로의 유일한 관문 |

---

## 보안 그룹 설정: AI 앱의 올바른 패턴

```python
# boto3로 보안 그룹 설정 (개념 예시)
import boto3

ec2 = boto3.client("ec2", region_name="ap-northeast-2")

# ALB 보안 그룹: 인터넷에서 443만 허용
alb_sg_rules = [
    {
        "IpProtocol": "tcp",
        "FromPort": 443,
        "ToPort": 443,
        "IpRanges": [{"CidrIp": "0.0.0.0/0"}]  # 전 세계 HTTPS
    }
]

# AI 앱 서버 보안 그룹: ALB에서만 8080 허용
app_sg_rules = [
    {
        "IpProtocol": "tcp",
        "FromPort": 8080,
        "ToPort": 8080,
        "UserIdGroupPairs": [{"GroupId": "sg-alb-id"}]  # ALB에서만
    }
]

# DB 보안 그룹: 앱 서버에서만 5432 허용
db_sg_rules = [
    {
        "IpProtocol": "tcp",
        "FromPort": 5432,
        "ToPort": 5432,
        "UserIdGroupPairs": [{"GroupId": "sg-app-id"}]  # 앱 서버에서만
    }
]

# 핵심: DB 보안 그룹에 0.0.0.0/0이 없어야 함
```

---

## 로드 밸런서(ALB)가 필요한 이유

```
단일 서버 없이 ALB 없을 때:
  사용자 → EC2 (1대) → AI 처리
  문제: 트래픽 몰리면 서버 하나가 감당 불가

ALB 적용 후:
  사용자 → ALB → EC2 (1번)
              └→ EC2 (2번)  ← 트래픽 자동 분산
              └→ EC2 (3번)
  추가: HTTPS 인증서 ALB에서 처리
  추가: 비정상 서버 자동 제외
  추가: Auto Scaling과 연동
```

**AI 앱에서 ALB가 특히 중요한 이유:** AI 추론은 CPU/메모리를 많이 씁니다. 사용자가 몰리면 서버 하나가 버티기 어렵습니다. ALB + Auto Scaling으로 자동으로 서버를 늘리고 트래픽을 분산시킵니다.

---

## 자주 하는 실수

| 실수 | 설명 | 올바른 접근 |
| --- | --- | --- |
| SSH 0.0.0.0/0 개방 | 전 세계에서 SSH 접근 가능 | 특정 IP만 허용 또는 SSM Session Manager 사용 |
| DB를 Public 서브넷에 배치 | DB 포트가 인터넷에 노출 | DB는 반드시 Private 서브넷 |
| 보안 그룹 하나로 모든 서비스 | 역할 분리 어려움 | ALB/앱/DB 각각 별도 보안 그룹 |
| HTTP로만 서비스 | 사용자 데이터 평문 전송 | ALB에 HTTPS 인증서 설정 |
| Egress 규칙 무시 | 서버가 외부로 데이터 유출 가능 | 아웃바운드도 필요한 것만 허용 |

---

## AI 팁: 네트워크 설정 자동화

1. **Terraform/CDK로 네트워크 코드화**: 네트워크 설정을 콘솔에서 수동으로 하지 말고 코드로 관리하세요. AI가 Terraform 코드를 생성해줄 수 있습니다.
2. **SSM Session Manager 사용**: EC2에 SSH 포트를 열지 않고 AWS Systems Manager를 통해 접근하면 보안이 훨씬 강화됩니다.
3. **VPC Flow Logs 활성화**: AI 앱으로 들어오고 나가는 트래픽을 기록해두면 보안 사고 시 분석이 가능합니다.
4. **S3용 Gateway Endpoint**: AI 앱 서버가 S3에 접근할 때 NAT Gateway를 거치지 않고 직접 연결하면 비용이 절약됩니다.

---

## 실전 체크리스트

- [ ] AI 앱 서버가 Private 서브넷에 배치되어 있다
- [ ] DB 서버가 별도 Private 서브넷에 있다
- [ ] 외부 접근은 ALB를 통해서만 이루어진다
- [ ] SSH 포트(22)가 0.0.0.0/0으로 열려있지 않다
- [ ] HTTPS 인증서를 ALB에 설정했다
- [ ] 보안 그룹이 역할(ALB/앱/DB)별로 분리되어 있다

---

## 처음 질문으로 돌아가기

- **AI 앱 서버는 Public과 Private 서브넷 중 어디에?**
  AI 앱 서버는 Private 서브넷에, ALB만 Public 서브넷에 배치하세요. 외부에서 앱 서버에 직접 접근하는 경로를 없애는 것이 핵심입니다.

- **SSH 포트를 0.0.0.0/0으로 열면 왜 위험한가요?**
  전 세계 누구나 SSH 접속을 시도할 수 있어서 브루트포스 공격의 표적이 됩니다. 특정 IP만 허용하거나, SSM Session Manager를 사용하면 SSH 포트 자체를 열 필요가 없습니다.

- **AI 앱의 데이터베이스 서버는 어떻게 보호해야 하나요?**
  DB는 Private 서브넷에 배치하고, 보안 그룹에서 앱 서버의 보안 그룹 ID만 허용하세요. 인터넷에서 DB 포트가 보이면 안 됩니다.

---

## 정리

클라우드 네트워크의 핵심은 "Public은 최소화, Private은 기본값"입니다. AI 앱의 외부 진입점을 ALB 하나로 제한하고, 앱 서버와 DB는 내부 네트워크에 두면 보안과 운영이 동시에 단순해집니다. 다음 글에서는 누가 무엇에 접근할 수 있는지 결정하는 Identity와 Security를 다룹니다.

---

## 참고 자료

- [AWS VPC 사용자 가이드](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
- [AWS 보안 그룹](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [AWS Elastic Load Balancing](https://docs.aws.amazon.com/elasticloadbalancing/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (1/10): Cloud Computing이란 무엇인가?
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (2/10): IaaS, PaaS, SaaS
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (3/10): Region과 Availability Zone
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (4/10): Compute
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (5/10): Storage
- **바이브코딩을 위한 클라우드 컴퓨팅 기초 (6/10): Network (현재 글)**
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (7/10): Identity와 Security
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (8/10): Monitoring
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (9/10): Cost Management
- 바이브코딩을 위한 클라우드 컴퓨팅 기초 (10/10): Cloud Architecture 기초
<!-- toc:end -->

Tags: 바이브코딩, 클라우드, 네트워크, VPC, AWS
