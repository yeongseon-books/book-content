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


![Cloud Computing 101 6장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/06/06-01-concept-at-a-glance.ko.png)
*Cloud Computing 101 6장 흐름 개요*
> 네트워크 설계는 보안, 성능, 비용을 동시에 고려하는 선택입니다. 단순한 연결이 아니라 운영 경계를 명확히 정하는 결정입니다.

## 먼저 던지는 질문

- VPC와 서브넷은 무엇이 다를까요?
- Security Group과 NACL은 왜 따로 존재할까요?
- Public 서브넷과 Private 서브넷은 어떤 패턴으로 나누는 것이 일반적일까요?

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
- **Internet Gateway**: VPC와 인터넷을 연결하는 관문입니다.
- **NAT Gateway**: Private 서브넷의 아웃바운드 인터넷 접속을 중개합니다.
- **Route Table**: 서브넷의 트래픽이 어디로 향하는지 결정하는 규칙 집합입니다.

## Before / After

**Before**에서는 모든 서버에 공인 IP를 붙입니다. 배포는 쉬워 보이지만 공격 표면이 크게 넓어집니다.

**After**에서는 앱은 Private 서브넷에 두고 ALB만 외부에 노출합니다. 데이터베이스는 별도의 내부 서브넷에 배치합니다.

## VPC CIDR 설계

VPC를 만들 때 가장 먼저 결정하는 것이 CIDR 블록입니다. 이 결정은 이후 서브넷 수, 인스턴스 수, VPC 간 피어링 가능 여부까지 영향을 미칩니다. 한 번 정하면 축소가 불가능하고 확장도 제한적이므로, 처음에 충분한 여유를 두는 편이 안전합니다.

### CIDR 크기별 용량

| CIDR | 총 IP 수 | AWS 예약 (5개/서브넷) 제외 후 | 용도 예시 |
| --- | --- | --- | --- |
| /16 | 65,536 | 서브넷 분할에 따라 다름 | 대규모 프로덕션 VPC |
| /20 | 4,096 | 서브넷당 ~4,091 | 중규모 서비스 |
| /24 | 256 | 251 | 소규모 서브넷, 관리용 |
| /28 | 16 | 11 | 최소 서브넷 (ALB 최소 요구) |

AWS는 각 서브넷에서 첫 4개 IP와 마지막 1개 IP를 예약합니다. 예를 들어 `10.0.0.0/24` 서브넷에서 실제 사용 가능한 IP는 `10.0.0.4`부터 `10.0.0.254`까지 251개입니다.

### 실무 CIDR 설계 원칙

1. VPC는 `/16`으로 시작합니다. 나중에 서브넷을 추가할 여유가 생깁니다.
2. 서브넷은 `/24` 단위로 나눕니다. 한 AZ당 Public 1개, App 1개, DB 1개가 기본입니다.
3. VPC 간 CIDR이 겹치면 피어링이 불가능합니다. `10.0.0.0/16`, `10.1.0.0/16`처럼 두 번째 옥텟으로 구분하는 방식이 흔합니다.
4. 온프레미스 네트워크와 VPN으로 연결할 계획이 있다면, 기존 대역과 겹치지 않도록 미리 확인해야 합니다.

## Security Group과 NACL 비교

두 계층의 방화벽이 존재하는 이유는 책임 범위가 다르기 때문입니다.

| 항목 | Security Group | Network ACL |
| --- | --- | --- |
| 적용 단위 | ENI(인스턴스) | 서브넷 |
| 상태 | Stateful (응답 자동 허용) | Stateless (인/아웃 별도 규칙) |
| 기본 정책 | 모든 인바운드 거부, 모든 아웃바운드 허용 | 모든 트래픽 허용 |
| 규칙 방식 | 허용만 가능 (거부 규칙 없음) | 허용 + 거부 가능, 번호 순서로 평가 |
| 규칙 수 제한 | 기본 60개 (인/아웃 합산) | 서브넷당 20개 (조정 가능) |
| 주요 용도 | 역할별 접근 제어 | 서브넷 경계의 거부 목록 |

실무에서는 Security Group이 주 방화벽이고, NACL은 보조 역할입니다. 예를 들어 특정 IP 대역을 서브넷 단위로 차단해야 할 때 NACL의 거부 규칙이 유용합니다. Security Group만으로는 거부를 명시할 수 없기 때문입니다.

## 실습: VPC 전체 구성 (boto3)

### 1단계 — VPC 생성

```python
import boto3

ec2 = boto3.client("ec2")


def create_vpc(cidr: str, name: str) -> str:
    resp = ec2.create_vpc(CidrBlock=cidr)
    vpc_id = resp["Vpc"]["VpcId"]
    ec2.create_tags(Resources=[vpc_id], Tags=[{"Key": "Name", "Value": name}])
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsSupport={"Value": True})
    ec2.modify_vpc_attribute(VpcId=vpc_id, EnableDnsHostnames={"Value": True})
    return vpc_id
```

### 2단계 — 서브넷 생성

```python
def create_subnet(vpc_id: str, cidr: str, az: str, name: str) -> str:
    resp = ec2.create_subnet(VpcId=vpc_id, CidrBlock=cidr, AvailabilityZone=az)
    subnet_id = resp["Subnet"]["SubnetId"]
    ec2.create_tags(Resources=[subnet_id], Tags=[{"Key": "Name", "Value": name}])
    return subnet_id
```

### 3단계 — Internet Gateway 연결

```python
def attach_igw(vpc_id: str) -> str:
    resp = ec2.create_internet_gateway()
    igw_id = resp["InternetGateway"]["InternetGatewayId"]
    ec2.attach_internet_gateway(InternetGatewayId=igw_id, VpcId=vpc_id)
    return igw_id
```

### 4단계 — Route Table 구성

```python
def create_public_route_table(vpc_id: str, igw_id: str, subnet_id: str) -> str:
    resp = ec2.create_route_table(VpcId=vpc_id)
    rtb_id = resp["RouteTable"]["RouteTableId"]
    ec2.create_route(
        RouteTableId=rtb_id,
        DestinationCidrBlock="0.0.0.0/0",
        GatewayId=igw_id,
    )
    ec2.associate_route_table(RouteTableId=rtb_id, SubnetId=subnet_id)
    return rtb_id
```

### 5단계 — Security Group 생성 및 규칙 추가

```python
def create_sg(vpc_id: str, name: str) -> str:
    resp = ec2.create_security_group(
        GroupName=name, Description=name, VpcId=vpc_id,
    )
    return resp["GroupId"]


def allow_https(sg_id: str) -> None:
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[{
            "IpProtocol": "tcp", "FromPort": 443, "ToPort": 443,
            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
        }],
    )


def allow_from_sg(sg_id: str, source_sg: str, port: int) -> None:
    ec2.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[{
            "IpProtocol": "tcp", "FromPort": port, "ToPort": port,
            "UserIdGroupPairs": [{"GroupId": source_sg}],
        }],
    )
```

### 6단계 — 전체 조립

```python
def build_network():
    vpc_id = create_vpc("10.0.0.0/16", "prod-vpc")
    igw_id = attach_igw(vpc_id)

    pub_a = create_subnet(vpc_id, "10.0.0.0/24", "ap-northeast-2a", "public-a")
    app_a = create_subnet(vpc_id, "10.0.10.0/24", "ap-northeast-2a", "app-a")
    db_a = create_subnet(vpc_id, "10.0.20.0/24", "ap-northeast-2a", "db-a")

    create_public_route_table(vpc_id, igw_id, pub_a)

    alb_sg = create_sg(vpc_id, "alb-sg")
    app_sg = create_sg(vpc_id, "app-sg")
    db_sg = create_sg(vpc_id, "db-sg")

    allow_https(alb_sg)
    allow_from_sg(app_sg, alb_sg, 8080)
    allow_from_sg(db_sg, app_sg, 5432)

    return {
        "vpc": vpc_id,
        "subnets": {"public": pub_a, "app": app_a, "db": db_a},
        "security_groups": {"alb": alb_sg, "app": app_sg, "db": db_sg},
    }
```

## CLI로 같은 작업 확인하기

boto3 코드와 동일한 결과를 AWS CLI로도 확인할 수 있습니다.

```bash
# VPC 생성
aws ec2 create-vpc --cidr-block 10.0.0.0/16 --query 'Vpc.VpcId' --output text

# 서브넷 생성
aws ec2 create-subnet --vpc-id vpc-xxx --cidr-block 10.0.0.0/24 \
    --availability-zone ap-northeast-2a --query 'Subnet.SubnetId' --output text

# Internet Gateway 생성 및 연결
aws ec2 create-internet-gateway --query 'InternetGateway.InternetGatewayId' --output text
aws ec2 attach-internet-gateway --internet-gateway-id igw-xxx --vpc-id vpc-xxx

# Route Table에 기본 라우트 추가
aws ec2 create-route --route-table-id rtb-xxx \
    --destination-cidr-block 0.0.0.0/0 --gateway-id igw-xxx

# Security Group 확인
aws ec2 describe-security-groups --group-ids sg-xxx sg-yyy \
    --query 'SecurityGroups[].{Name:GroupName,Rules:IpPermissions}'
```

## 이 코드에서 먼저 봐야 할 점

- DB 보안 그룹은 CIDR보다 애플리케이션 보안 그룹을 참조하는 방식이 일반적입니다.
- `0.0.0.0/0`은 전 세계에 열겠다는 명시적 선언입니다.
- SG는 상태 저장, NACL은 무상태라는 차이가 있습니다.
- Route Table이 없으면 서브넷 간 트래픽이 의도와 다르게 흐를 수 있습니다.

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

## VPC 연결 옵션 비교

서비스가 커지면 하나의 VPC로는 부족해집니다. 팀별 VPC를 분리하거나, 공유 서비스를 별도 VPC에 두는 패턴이 생깁니다. 이때 VPC 간 연결 방식을 선택해야 합니다.

| 항목 | VPC Peering | Transit Gateway | PrivateLink |
| --- | --- | --- | --- |
| 연결 구조 | 1:1 | Hub-and-spoke | Provider-Consumer |
| CIDR 겹침 허용 | 불가 | 불가 | 가능 |
| 전이적 라우팅 | 불가 (A-B, B-C 연결해도 A-C 불가) | 가능 | 해당 없음 |
| 비용 | 데이터 전송 요금만 | 시간당 요금 + 데이터 전송 | 시간당 요금 + 데이터 전송 |
| 적합한 경우 | VPC 2-3개 직접 연결 | VPC 10개 이상 중앙 관리 | 특정 서비스만 노출 |
| 관리 복잡도 | VPC 수 증가 시 O(n^2) | 중앙 집중 관리 | 서비스 단위로 독립 |

**판단 기준**: VPC가 3개 이하이고 모두 같은 팀이 관리한다면 Peering으로 충분합니다. VPC가 늘어나기 시작하면 Transit Gateway로 전환하는 편이 낫습니다. 외부 팀이나 파트너에게 내부 서비스 하나만 노출해야 한다면 PrivateLink가 적합합니다.

## 로드 밸런서 유형 비교

AWS에서 제공하는 로드 밸런서는 세 종류입니다. 선택 기준은 프로토콜과 성능 요구사항입니다.

| 항목 | ALB (Application) | NLB (Network) | CLB (Classic) |
| --- | --- | --- | --- |
| 계층 | L7 (HTTP/HTTPS) | L4 (TCP/UDP/TLS) | L4 + L7 혼합 |
| 라우팅 | 경로, 호스트, 헤더 기반 | 포트 기반 | 단순 라운드로빈 |
| 성능 | 수백만 RPS | 수억 PPS, 고정 IP 지원 | 레거시 |
| WebSocket | 지원 | 지원 | 미지원 |
| 고정 IP | 불가 (DNS 기반) | 가능 (EIP 연결) | 불가 |
| 주요 용도 | 웹 API, 마이크로서비스 | gRPC, 게임, IoT | 신규 사용 비권장 |

대부분의 웹 서비스는 ALB로 시작합니다. gRPC처럼 L4 수준의 제어가 필요하거나, 고정 IP를 방화벽 화이트리스트에 등록해야 하는 경우 NLB를 선택합니다. CLB는 레거시이므로 신규 프로젝트에서는 사용하지 않습니다.

### ALB 경로 기반 라우팅 예시

ALB는 URL 경로에 따라 서로 다른 대상 그룹으로 트래픽을 분배할 수 있습니다. 마이크로서비스 아키텍처에서 하나의 도메인 뒤에 여러 서비스를 배치할 때 유용합니다.

```text
api.example.com/users/*   → Target Group A (사용자 서비스)
api.example.com/orders/*  → Target Group B (주문 서비스)
api.example.com/health    → Target Group C (헬스체크 전용)
```

이 구성을 사용하면 서비스별로 독립적인 배포와 스케일링이 가능합니다. 한 서비스의 장애가 다른 서비스에 영향을 주지 않도록 대상 그룹을 분리하는 것이 핵심입니다.

## DNS 해석 흐름

VPC 내부의 DNS 해석은 다음 순서로 진행됩니다.

```text
[애플리케이션] 
    → VPC DNS Resolver (VPC CIDR + 2 주소, 예: 10.0.0.2)
        → Route 53 Resolver
            → Private Hosted Zone (내부 도메인)
            → Public Hosted Zone (외부 도메인)
            → 외부 DNS (재귀 해석)
```

`EnableDnsSupport`를 켜면 VPC 내부 인스턴스가 Amazon 제공 DNS를 사용할 수 있습니다. `EnableDnsHostnames`를 켜면 퍼블릭 IP가 있는 인스턴스에 자동으로 DNS 호스트명이 부여됩니다. 이 두 설정은 RDS 엔드포인트 해석, VPC 엔드포인트 사용, ACM 인증서 검증 등에 필수입니다.

## NAT Gateway와 VPC Endpoint

Private 서브넷의 인스턴스가 외부 인터넷에 접근해야 할 때 NAT Gateway를 사용합니다. 패키지 업데이트, 외부 API 호출, 라이선스 검증 등이 대표적인 사례입니다. NAT Gateway는 아웃바운드만 허용하고 인바운드는 차단하므로 보안과 편의를 동시에 제공합니다.

그러나 NAT Gateway는 비용이 큽니다. 시간당 과금과 데이터 처리 요금이 모두 발생합니다. 특히 S3나 DynamoDB처럼 AWS 내부 서비스에 접근할 때 NAT Gateway를 경유하면 불필요한 비용이 쌓입니다. 이때 Gateway Endpoint를 사용하면 트래픽이 AWS 내부 네트워크를 통해 직접 전달되므로 NAT Gateway를 거치지 않습니다.

```text
[Private 서브넷 인스턴스]
    ├─ 외부 인터넷 → NAT Gateway → Internet Gateway → 인터넷
    ├─ S3 접근    → Gateway Endpoint → S3 (무료, AWS 내부망)
    └─ SQS 접근   → Interface Endpoint → SQS (시간당 + GB당 과금)
```

Gateway Endpoint는 S3와 DynamoDB만 지원하며 무료입니다. Interface Endpoint는 그 외 대부분의 AWS 서비스를 지원하지만 시간당 요금과 데이터 처리 요금이 발생합니다. 그래도 NAT Gateway보다 저렴한 경우가 많으므로, 특정 서비스 호출이 빈번하다면 Interface Endpoint도 검토할 가치가 있습니다.

### VPC Endpoint 설정 예시 (CLI)

```bash
# S3용 Gateway Endpoint 생성
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-xxx \
    --service-name com.amazonaws.ap-northeast-2.s3 \
    --route-table-ids rtb-xxx

# SQS용 Interface Endpoint 생성
aws ec2 create-vpc-endpoint \
    --vpc-id vpc-xxx \
    --vpc-endpoint-type Interface \
    --service-name com.amazonaws.ap-northeast-2.sqs \
    --subnet-ids subnet-xxx \
    --security-group-ids sg-xxx
```

## VPC Flow Logs 활용

VPC Flow Logs는 네트워크 인터페이스를 오가는 IP 트래픽 정보를 기록합니다. 보안 감사, 트러블슈팅, 비용 분석에 필수적인 데이터입니다.

```bash
# VPC 수준 Flow Log 생성 (CloudWatch Logs로 전송)
aws ec2 create-flow-logs \
    --resource-type VPC \
    --resource-ids vpc-xxx \
    --traffic-type ALL \
    --log-destination-type cloud-watch-logs \
    --log-group-name /vpc/flow-logs/prod
```

Flow Logs에서 확인할 수 있는 정보는 다음과 같습니다.

- 출발지/목적지 IP와 포트
- 프로토콜 번호
- 패킷 수와 바이트 수
- 허용(ACCEPT) 또는 거부(REJECT) 여부
- 타임스탬프

거부된 트래픽만 필터링하면 보안 그룹이나 NACL에 의해 차단된 시도를 빠르게 파악할 수 있습니다. 허용된 트래픽 중에서도 예상치 못한 대량 전송이 보이면 비용 이상의 원인을 추적하는 데 활용할 수 있습니다.

### Flow Logs 분석 팁

1. REJECT 로그를 주기적으로 확인합니다. 정상적인 거부인지, 설정 오류로 인한 거부인지 구분해야 합니다.
2. 특정 포트로의 반복적인 REJECT는 스캐닝 시도일 수 있습니다.
3. Cross-AZ 트래픽 양을 측정하면 비용 예측에 도움이 됩니다.
4. S3로 직접 전송하면 CloudWatch Logs보다 저렴하게 장기 보관할 수 있습니다.
## 네트워크 비용 인식

네트워크 비용은 아키텍처 결정에 직접 영향을 미칩니다. 같은 기능이라도 트래픽 경로에 따라 월 비용이 몇 배씩 달라질 수 있습니다.

| 트래픽 경로 | 비용 (GB당, 서울 리전 기준) | 비고 |
| --- | --- | --- |
| 같은 AZ 내 (Private IP) | 무료 | 가장 저렴한 경로 |
| Cross-AZ (같은 리전) | ~$0.01 (송신 + 수신 각각) | 고가용성의 비용 |
| Cross-Region | ~$0.08 | DR, 멀티리전 배포 시 주의 |
| 인터넷 아웃바운드 | $0.08 ~ $0.12 (구간별 체감) | 첫 10TB 이후 단가 하락 |
| NAT Gateway 처리 | $0.045 (GB당) + 시간당 요금 | Private 서브넷 외부 접속 비용 |
| VPC Endpoint (Gateway) | 무료 | S3, DynamoDB 전용 |
| VPC Endpoint (Interface) | 시간당 요금 + $0.01/GB | 기타 AWS 서비스 |

**비용 최적화 팁**:

1. S3, DynamoDB 접근이 빈번하다면 Gateway Endpoint를 반드시 설정합니다. NAT Gateway를 경유하면 불필요한 비용이 발생합니다.
2. Cross-AZ 비용은 고가용성을 위해 수용하되, 불필요한 AZ 간 호출은 줄입니다.
3. NAT Gateway는 AZ당 하나씩 두는 것이 고가용성에 좋지만, 개발 환경에서는 하나로 충분합니다.
4. 대용량 데이터 전송이 예상되면 AWS Direct Connect나 CloudFront를 검토합니다.

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
- Gateway Endpoint는 비용 절감의 첫 번째 선택입니다.
- NAT Gateway 비용은 월말에 놀랄 수 있으므로 태그와 알림을 설정합니다.

## 체크리스트

- [ ] Public 서브넷에 데이터베이스가 없는가.
- [ ] 보안 그룹이 역할별로 분리되어 있는가.
- [ ] Flow Logs가 활성화되어 있는가.
- [ ] Egress 규칙이 명시적으로 정의되어 있는가.
- [ ] S3/DynamoDB용 Gateway Endpoint가 설정되어 있는가.
- [ ] CIDR이 다른 VPC 및 온프레미스와 겹치지 않는가.
- [ ] Route Table이 서브넷별로 올바르게 연결되어 있는가.

## 연습 문제

1. Security Group과 NACL의 차이 세 가지를 적어 보세요.
2. Public/Private 서브넷 분리가 보안에 도움이 되는 이유를 한 문장으로 설명해 보세요.
3. ALB와 NLB의 큰 차이 하나를 적어 보세요.
4. `/16` VPC를 `/24` 서브넷으로 나누면 최대 몇 개의 서브넷을 만들 수 있는지 계산해 보세요.
5. NAT Gateway 대신 Gateway Endpoint를 사용하면 비용이 줄어드는 이유를 설명해 보세요.

## 처음 질문으로 돌아가기

- **VPC와 서브넷은 무엇이 다를까요?**
  - VPC는 논리적으로 격리된 전체 네트워크 경계이고, 서브넷은 그 안에서 AZ 단위로 나눈 더 작은 IP 범위입니다. VPC가 건물이라면 서브넷은 층입니다.

- **Security Group과 NACL은 왜 따로 존재할까요?**
  - Security Group은 인스턴스 단위의 stateful 허용 규칙이고, NACL은 서브넷 단위의 stateless 허용/거부 규칙입니다. SG로는 거부를 명시할 수 없으므로, 특정 IP를 서브넷 수준에서 차단할 때 NACL이 필요합니다.

- **Public 서브넷과 Private 서브넷은 어떤 패턴으로 나누는 것이 일반적일까요?**
  - ALB만 Public에 두고, 앱 서버와 데이터베이스는 Private에 두는 3계층 패턴이 기본입니다. 외부 공개 지점을 최소화하면 방화벽 규칙이 단순해지고 공격 표면이 좁아집니다.

## 정리 및 다음 단계

연결 경로를 정했다면, 이제는 누가 어떤 권한으로 그 경로를 사용할지를 설계해야 합니다. 다음 글에서는 Identity와 Security를 다루겠습니다.

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
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)

Tags: Cloud, Networking, VPC, Security, AWS
