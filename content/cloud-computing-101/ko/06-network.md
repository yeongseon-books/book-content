---
series: cloud-computing-101
episode: 6
title: "Cloud Computing 101 (6/10): Network"
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
  - Networking
  - VPC
  - Security
  - AWS
seo_description: VPC, 서브넷, 보안 그룹, 로드밸런서의 역할과 설계 패턴을 격리, 배치, 허용, 분산의 관점에서 상세히 정리합니다.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (6/10): Network

클라우드 네트워크는 처음 설계할 때는 단순해 보여도, 한번 구조가 잡히면 나중에 되돌리기 가장 어려운 영역 중 하나입니다. VPC, 서브넷, 보안 그룹, 로드밸런서는 이름만 보면 비슷하게 느껴지지만 서로 다른 층위의 책임을 맡습니다.

좋은 네트워크 설계는 화려한 구성이 아니라 기본값을 얼마나 안전하게 잡았는가에서 드러납니다. 특히 외부에 공개되는 지점과 내부 자원이 구분되어야 이후의 보안과 운영이 훨씬 쉬워집니다.

이 글은 Cloud Computing 101 시리즈의 6번째 글입니다.

여기서는 클라우드 네트워크를 격리, 배치, 허용, 분산이라는 네 단계로 이해해 보겠습니다.

## 먼저 던지는 질문

- VPC와 서브넷은 무엇이 다를까요?
- Security Group과 NACL은 왜 따로 존재할까요?
- Public 서브넷과 Private 서브넷은 어떤 패턴으로 나누는 것이 일반적일까요?

## 큰 그림

![Cloud Computing 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/06/06-01-concept-at-a-glance.ko.png)

*Cloud Computing 101 6장 흐름 개요*

VPC는 클라우드 네트워크의 기본 경계입니다. 서브넷은 VPC 내부의 더 작은 네트워크 단위로, 리전 또는 가용성 영역(AZ) 단위로 나뉩니다. 보안 그룹과 네트워크 ACL은 트래픽을 필터링합니다. 로드 밸런서는 여러 인스턴스로 트래픽을 분산합니다.

> 네트워크 설계는 보안, 성능, 비용을 동시에 고려하는 선택입니다. 단순한 연결이 아니라 운영 경계를 명확히 정하는 결정입니다.

## 왜 중요한가

초기 한 시간의 네트워크 설계가 이후 몇 년의 운영을 좌우하는 경우가 많습니다. 모든 서버에 공인 IP를 붙인 구조는 처음에는 단순해 보여도 공격 표면이 급격히 넓어집니다. 반대로 앱은 Private 서브넷에 두고 외부 공개는 ALB 한 지점으로 제한하면 보안과 운영이 함께 단순해집니다.

네트워크는 기능보다 경계를 설계하는 영역입니다. 그래서 한 번 꼬이면 단순한 설정 수정으로 해결되지 않고, 서비스 구조 전체를 다시 정리해야 하는 경우가 많습니다.

## 한눈에 보는 개념

외부 인터넷은 로드밸런서로만 들어오고, 애플리케이션과 데이터베이스는 내부망에 둡니다. 이런 구성이 흔한 이유는 멋져서가 아니라, 공개 지점을 최소화하는 편이 가장 강력한 기본 보안이기 때문입니다.

## 핵심 용어

- **VPC**: 논리적으로 격리된 가상 네트워크입니다.
- **Subnet**: VPC 내부의 IP 범위이며, AZ 단위로 배치됩니다.
- **Security Group**: 인스턴스 단위의 상태 저장 방화벽입니다.
- **NACL**: 서브넷 단위의 무상태 방화벽입니다.
- **Load Balancer**: 여러 대상에 트래픽을 분산합니다.

## Before / After

**Before**에서는 모든 서버에 공인 IP를 붙입니다. 배포는 쉬워 보이지만 공격 표면이 크게 넓어집니다.

**After**에서는 앱은 Private 서브넷에 두고 ALB만 외부에 노출합니다. 데이터베이스는 별도의 내부 서브넷에 배치합니다.

## 실습: 보안 그룹 만들기

### 1단계 — 클라이언트

```python
import boto3
ec2 = boto3.client("ec2")
```

### 2단계 — SG 생성

```python
def create_sg(vpc_id, name):
    res = ec2.create_security_group(
        GroupName=name, Description=name, VpcId=vpc_id,
    )
    return res["GroupId"]
```

### 3단계 — 인바운드 허용

```python
def allow_https(sg_id):
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[{
            "IpProtocol": "tcp", "FromPort": 443, "ToPort": 443,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        }],
    )
```

### 4단계 — DB SG는 앱 SG만 허용

```python
def allow_db_from_app(db_sg, app_sg):
    ec2.authorize_security_group_ingress(
        GroupId=db_sg,
        IpPermissions=[{
            "IpProtocol": "tcp", "FromPort": 5432, "ToPort": 5432,
            "UserIdGroupPairs": [{"GroupId": app_sg}],
        }],
    )
```

### 5단계 — 검증

```python
def describe(sg_id):
    return ec2.describe_security_groups(GroupIds=[sg_id])
```

이 예제는 네트워크 보안에서 가장 흔한 패턴 하나를 보여 줍니다. 데이터베이스는 CIDR 대역 전체가 아니라 애플리케이션 보안 그룹 자체를 신뢰합니다. 즉, IP 주소보다 역할에 맞춰 접근을 허용하는 방식입니다.

## 이 코드에서 먼저 봐야 할 점

- DB 보안 그룹은 CIDR보다 애플리케이션 보안 그룹을 참조하는 방식이 일반적입니다.
- `0.0.0.0/0`은 전 세계에 열겠다는 명시적 선언입니다.
- SG는 상태 저장, NACL은 무상태라는 차이가 있습니다.

## 이 예제를 실제로 검증하는 순서

네트워크 예제는 규칙을 만드는 것보다 "누가 누구를 신뢰하는가"를 검증하는 단계가 더 중요합니다. DB 보안 그룹이 앱 보안 그룹만 참조하게 만들면, 네트워크 보안이 IP 관리가 아니라 역할 관리에 가까워진다는 점이 분명해집니다.

```bash
aws ec2 describe-security-groups --group-ids sg-xxxxxxxx sg-yyyyyyyy
```

**Expected output:**

- 앱 보안 그룹에는 `443` 인바운드 규칙이 보여야 합니다.
- DB 보안 그룹에는 `5432` 포트와 함께 앱 보안 그룹 ID 참조가 보여야 합니다.
- 데이터베이스 보안 그룹에 `0.0.0.0/0`이 보인다면 설계 의도가 이미 무너진 상태입니다.

### 자주 막히는 지점

- 외부 인터넷에서 곧바로 들어올 수 있는 자원과 내부 자원을 같은 서브넷에 두면 운영과 보안이 함께 복잡해집니다.
- NAT Gateway가 있다고 해서 인바운드가 자동으로 차단되는 것은 아닙니다. 라우팅과 SG를 같이 봐야 합니다.
- Public 서브넷과 Private 서브넷을 나눌 때는 향후 AZ 확장까지 고려해 CIDR을 잡는 편이 안전합니다.

## Public / Private 패턴은 왜 기본값일까

퍼블릭 서브넷은 인터넷과 직접 연결될 수 있는 자원을 위한 공간입니다. 프라이빗 서브넷은 외부에서 직접 들어오지 못하고, 필요한 경우 NAT 같은 별도 출구로만 나갑니다. 앱 서버와 데이터베이스를 프라이빗 서브넷에 두는 이유는 분명합니다. 외부 공개가 꼭 필요한 지점만 드러내기 위해서입니다.

실무에서는 ALB를 Public 서브넷에 두고, 앱 서버는 Private 서브넷에, RDS는 DB 전용 Private 서브넷에 두는 구성이 기본입니다. 이렇게 하면 진입점이 명확해지고, 방화벽 규칙도 역할별로 단순하게 유지할 수 있습니다.

## 자주 하는 실수 5가지

1. SSH를 `0.0.0.0/0`으로 열어 둡니다.
2. 데이터베이스를 Public 서브넷에 둡니다.
3. NACL과 SG의 책임을 혼동합니다.
4. Cross-AZ 트래픽 비용을 무시합니다.
5. Egress 규칙을 검토하지 않습니다.

## 실무에서는 이렇게 생각합니다

- Private가 기본값이고, Public은 예외입니다.
- 보안 그룹은 역할별로 쪼개는 편이 낫습니다.
- 인바운드만큼 아웃바운드도 명시적으로 제한해야 합니다.
- VPC Flow Logs는 기본적으로 켜 두는 편이 좋습니다.
- CIDR 범위는 미래의 병합과 확장을 고려해 잡아야 합니다.

## 체크리스트

- [ ] Public 서브넷에 데이터베이스가 없는가.
- [ ] 보안 그룹이 역할별로 분리되어 있는가.
- [ ] Flow Logs가 활성화되어 있는가.
- [ ] Egress 규칙이 명시적으로 정의되어 있는가.

## 연습 문제

1. Security Group과 NACL의 차이 세 가지를 적어 보세요.
2. Public/Private 서브넷 분리가 보안에 도움이 되는 이유를 한 문장으로 설명해 보세요.
3. ALB와 NLB의 큰 차이 하나를 적어 보세요.

## 정리 및 다음 단계

연결 경로를 정했다면, 이제는 누가 어떤 권한으로 그 경로를 사용할지를 설계해야 합니다. 다음 글에서는 Identity와 Security를 다루겠습니다.

단일 가용성 영역(AZ)에만 배포하면 간단하지만, AZ 장애 시 서비스가 전체 중단됩니다. Multi-AZ 배포는 신뢰성을 높이지만 복잡도와 비용도 증가합니다.

보안 그룹은 상태 저장(stateful)이고, 네트워크 ACL은 상태 비저장(stateless)입니다. 정책을 작게 권한을 부여하는 최소 권한 원칙을 따르면 보안이 올라갑니다.
  - 본문의 기준은 Network를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
NAT 게이트웨이는 프라이빗 서브넷의 인스턴스가 인터넷에 연결되게 해줍니다. 하지만 인바운드 연결은 차단되므로, 외부 접근이 필요한 경우 로드 밸런서 또는 베스천 호스트를 사용합니다.
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Public 서브넷과 Private 서브넷은 어떤 패턴으로 나누는 것이 일반적일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

## VPC 설계 예시와 규칙 템플릿

| 계층 | 서브넷 | 예시 CIDR | 외부 접근 |
| --- | --- | --- | --- |
| Edge | public-a/public-b | 10.0.0.0/24, 10.0.1.0/24 | 허용(ALB) |
| App | private-app-a/private-app-b | 10.0.10.0/24, 10.0.11.0/24 | 직접 불가 |
| Data | private-db-a/private-db-b | 10.0.20.0/24, 10.0.21.0/24 | 직접 불가 |

```yaml
security_groups:
  alb_sg:
    inbound:
      - protocol: tcp
        port: 443
        cidr: 0.0.0.0/0
  app_sg:
    inbound:
      - protocol: tcp
        port: 8080
        source_sg: alb_sg
  db_sg:
    inbound:
      - protocol: tcp
        port: 5432
        source_sg: app_sg
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

<!-- toc:begin -->
## 시리즈 목차

- [Cloud Computing 101 (1/10): Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- [Cloud Computing 101 (2/10): IaaS, PaaS, SaaS](./02-iaas-paas-saas.md)
- [Cloud Computing 101 (3/10): Region과 Availability Zone](./03-region-and-availability-zone.md)
- [Cloud Computing 101 (4/10): Compute](./04-compute.md)
- [Cloud Computing 101 (5/10): Storage](./05-storage.md)
- **Network (현재 글)**
- Identity와 Security (예정)
- Monitoring (예정)
- Cost Management (예정)
- Cloud Architecture 기초 (예정)

<!-- toc:end -->

## 참고 자료

- [AWS VPC user guide](https://docs.aws.amazon.com/vpc/latest/userguide/what-is-amazon-vpc.html)
- [AWS Security Groups](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-security-groups.html)
- [AWS Network ACL](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-network-acls.html)
- [AWS Elastic Load Balancing](https://docs.aws.amazon.com/elasticloadbalancing/latest/userguide/what-is-load-balancing.html)

Tags: Cloud, Networking, VPC, Security, AWS
