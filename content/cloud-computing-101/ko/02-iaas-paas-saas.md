---
series: cloud-computing-101
episode: 2
title: "Cloud Computing 101 (2/10): IaaS, PaaS, SaaS"
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
  - IaaS
  - PaaS
  - SaaS
  - Architecture
seo_description: 클라우드 서비스 모델인 IaaS, PaaS, SaaS의 책임 경계와 장단점, 선택 기준을 실무 예시와 함께 정리합니다.
last_reviewed: '2026-05-14'
---

# Cloud Computing 101 (2/10): IaaS, PaaS, SaaS

같은 클라우드라고 해도 어떤 서비스는 가상 머신을 직접 다루게 만들고, 어떤 서비스는 코드만 배포하면 끝나며, 어떤 서비스는 완성된 애플리케이션을 바로 쓰게 합니다. 이 차이를 감으로만 이해하면 팀 역량과 맞지 않는 선택을 하게 됩니다.

핵심 질문은 단순합니다. 누가 무엇을 운영하는가입니다. 이 한 문장을 붙잡고 보면 EC2, Heroku, Notion이 왜 모두 클라우드이면서도 전혀 다르게 느껴지는지 설명할 수 있습니다.

이 글은 Cloud Computing 101 시리즈의 2번째 글입니다.

여기서는 IaaS, PaaS, SaaS를 기능 이름이 아니라 책임 경계의 관점에서 정리하겠습니다.

## 먼저 던지는 질문

- EC2, Heroku, Notion처럼 모두 클라우드에 속하는 서비스가 왜 이렇게 다르게 느껴질까요?
- IaaS, PaaS, SaaS는 각각 어디까지를 사용자가 운영하고, 어디부터 공급자가 맡을까요?
- 조직 규모와 워크로드 특성에 따라 어떤 모델을 선택해야 할까요?

## 큰 그림

![Cloud Computing 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/cloud-computing-101/02/02-01-concept-at-a-glance.ko.png)

*Cloud Computing 101 2장 흐름 개요*

IaaS, PaaS, SaaS의 차이는 사용자가 운영 책임을 가지는 범위의 차이입니다. IaaS는 가상 머신, PaaS는 런타임, SaaS는 완성된 애플리케이션을 제공합니다.

> IaaS, PaaS, SaaS는 각 서비스 모델마다 공급자와 사용자가 맡는 책임의 경계가 다릅니다. 이 경계를 명확히 이해해야 올바른 기술을 선택할 수 있습니다.

## 왜 중요한가

작은 팀이 처음부터 IaaS 위에 모든 것을 직접 구축하면 속도가 크게 떨어질 수 있습니다. 반대로 세밀한 제어가 필요한 시스템을 PaaS에 무리하게 올리면 플랫폼 제약 때문에 우회 비용이 늘어납니다. 높은 추상화가 항상 더 좋은 것도 아니고, 낮은 추상화가 항상 더 유연한 정답도 아닙니다.

결국 서비스 모델은 기술 취향이 아니라 조직의 현재 상황을 반영하는 선택입니다. 배포 속도, 운영 인력, 규제 요구사항, 락인 허용 범위가 모두 여기에 연결됩니다.

## 한눈에 보는 개념

IaaS에서는 운영 체제와 런타임 관리가 여전히 사용자 쪽에 가깝습니다. PaaS에서는 운영 체제와 런타임을 플랫폼이 더 많이 맡습니다. SaaS에서는 사용자가 완성된 애플리케이션을 소비하는 쪽에 가까워집니다.

## 핵심 용어

- **IaaS**: 가상 머신, 디스크, 네트워크 같은 인프라 자원을 제공합니다.
- **PaaS**: 런타임과 배포 환경까지 포함해 애플리케이션 실행 기반을 제공합니다.
- **SaaS**: 완성된 소프트웨어를 서비스로 제공합니다.
- **FaaS**: 함수 단위로 코드를 실행하는 서버리스 모델입니다.
- **Managed**: 공급자가 운영을 대신 맡는 범위를 뜻합니다.

## Before / After

**Before**에서는 서버, 운영 체제, 런타임, 배포, 로그 수집까지 모두 팀이 직접 책임져야 했습니다.

**After**에서는 플랫폼이나 완성형 서비스를 선택함으로써 팀은 코드와 비즈니스 로직, 또는 실제 업무 흐름에 더 집중할 수 있습니다.

중요한 점은 추상화가 올라갈수록 운영 부담은 줄지만, 세밀한 제어권도 함께 줄어든다는 점입니다. 결국 무엇을 포기하고 무엇을 얻는지 이해해야 올바른 모델을 고를 수 있습니다.

## 실습: 작은 Flask 앱으로 보는 PaaS

PaaS가 왜 빠른지 감을 잡으려면 실제 배포 흐름을 보는 편이 좋습니다.

### 1단계 — 앱 코드

```python
# app.py
from flask import Flask
app = Flask(__name__)

@app.route("/")
def home():
    return {"hello": "cloud"}
```

### 2단계 — 의존성

```text
flask==3.0.0
gunicorn==21.2.0
```

### 3단계 — 실행 명령

```text
# Procfile
web: gunicorn app:app
```

### 4단계 — 배포 (PaaS is this short)

```bash
git init
git add .
git commit -m "init"
# example: heroku create && git push heroku main
```

### 5단계 — IaaS 비교

```python
# On IaaS you would also need to:
# - provision a VM
# - install OS packages
# - configure a reverse proxy
# - install a log shipper
print("PaaS = git push, IaaS = the four steps above by hand")
```

이 예제가 보여 주는 핵심은 배포 계약의 길이입니다. PaaS에서는 애플리케이션이 어떻게 실행될지만 명시하면 플랫폼이 많은 준비를 대신합니다. IaaS에서는 같은 앱 하나를 띄우기 위해 네트워크, OS 패키지, 웹 서버, 프로세스 관리, 로그 수집까지 직접 설계해야 합니다.

## 이 코드에서 먼저 봐야 할 점

- PaaS 배포에서는 Procfile 한 줄이 실행 계약이 됩니다.
- IaaS에서는 각 단계를 모두 팀이 설계하고 운영해야 합니다.
- SaaS에서는 애초에 이런 애플리케이션 코드를 우리가 배포하지 않을 수도 있습니다.

이 차이는 편의성의 차이를 넘어 팀 구조에도 영향을 줍니다. 운영 인력이 많지 않다면 PaaS가 빠른 선택일 수 있고, 플랫폼 제약을 감당하기 어렵다면 IaaS나 컨테이너 기반 운영이 더 맞을 수 있습니다.

## 이 예제를 실제로 검증하는 순서

이 예제의 핵심은 Flask 문법이 아니라 배포 계약이 얼마나 짧아지는지 눈으로 확인하는 데 있습니다. 로컬에서 먼저 PaaS가 기대하는 형태로 앱이 뜨는지 확인하면, 왜 PaaS가 운영 부담을 줄여 주는지 감이 빨리 옵니다.

```bash
pip install -r requirements.txt
gunicorn app:app --bind 0.0.0.0:8000
curl http://127.0.0.1:8000/
```

**Expected output:**

- Gunicorn 프로세스가 에러 없이 기동해야 합니다.
- `curl` 결과로 `{"hello":"cloud"}` 같은 JSON 응답이 보여야 합니다.
- 이 단계가 통과되면 PaaS가 요구하는 것은 런타임과 시작 명령이라는 점이 훨씬 분명해집니다.

### 자주 막히는 지점

- 로컬에서는 되는데 PaaS에서 실패한다면 `Procfile`의 시작 명령과 실제 모듈 경로가 다른 경우가 많습니다.
- IaaS 비교를 볼 때는 "PaaS가 마법처럼 다 해 준다"보다 "운영 책임을 어디서 끊어 주는가"에 초점을 두는 편이 좋습니다.
- SaaS를 평가할 때는 기능 목록만 보지 말고 데이터 내보내기와 SSO 같은 운영 항목도 함께 봐야 합니다.

## 서버리스는 어디에 들어갈까

FaaS는 보통 PaaS보다 더 높은 추상화로 이해하면 편합니다. 사용자는 함수 코드와 트리거에 집중하고, 인프라와 스케일링은 플랫폼이 대부분 맡습니다. 다만 콜드 스타트, 짧은 실행 시간, 상태 저장 제약이 있기 때문에 모든 워크로드에 잘 맞는 것은 아닙니다.

이벤트 기반 작업, 간헐적 실행, 배치성 처리에는 매우 강력할 수 있습니다. 반대로 긴 연결 유지나 큰 메모리 상태를 오래 붙잡는 애플리케이션에는 불리할 수 있습니다. 그래서 FaaS를 “더 현대적이니 무조건 낫다”로 보기보다, 이벤트 중심 워크로드에 잘 맞는 별도 실행 모델로 보는 편이 정확합니다.

## IaaS 실습: EC2 인스턴스 프로비저닝

PaaS가 Procfile 한 줄로 배포를 끝내는 반면, IaaS에서는 인프라 자원을 하나씩 만들어야 합니다. 아래는 AWS CLI로 EC2 인스턴스를 생성하는 최소 예시입니다.

```bash
# 1. VPC와 서브넷 확인 (기본 VPC 사용)
aws ec2 describe-vpcs --filters Name=isDefault,Values=true \
  --query 'Vpcs[0].VpcId' --output text

# 2. 보안 그룹 생성
aws ec2 create-security-group \
  --group-name demo-sg \
  --description "Demo security group" \
  --vpc-id vpc-0abc1234

# 3. SSH 포트 허용
aws ec2 authorize-security-group-ingress \
  --group-name demo-sg \
  --protocol tcp --port 22 \
  --cidr 203.0.113.0/32

# 4. 인스턴스 생성
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --key-name my-key \
  --security-groups demo-sg \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=demo}]'
```

이 과정을 보면 PaaS와의 차이가 즉시 드러납니다. PaaS에서는 `git push` 한 번이었지만, IaaS에서는 VPC 확인, 보안 그룹 생성, 포트 정책 설정, 인스턴스 생성까지 네 단계가 필요합니다. 그 대신 네트워크와 보안을 사용자가 직접 제어할 수 있습니다.

### IaaS에서 놓치기 쉬운 후속 작업

인스턴스를 만든 뒤에도 다음 작업이 남습니다.

| 후속 작업 | 설명 | 누락 시 위험 |
| --- | --- | --- |
| OS 패치 | 보안 업데이트 적용 | CVE 노출 |
| 로그 에이전트 설치 | CloudWatch Agent 또는 Fluentd | 장애 시 로그 부재 |
| 모니터링 설정 | CPU/메모리/디스크 알림 | 무응답 인스턴스 방치 |
| 백업 정책 | EBS 스냅샷 자동화 | 데이터 손실 |
| 태그 부여 | Project, Owner, Environment | 비용 추적 불가 |

PaaS에서는 이 항목 대부분을 플랫폼이 처리합니다. IaaS를 선택했다면 이 후속 작업까지 팀이 운영 범위로 인식해야 합니다.

## SaaS 평가 프레임워크

SaaS를 도입할 때 기능 목록만 보면 나중에 락인이나 운영 비효율로 돌아옵니다. 아래 프레임워크는 SaaS 평가 시 반드시 확인해야 할 항목을 정리한 것입니다.

| 평가 영역 | 확인 항목 | 위험 신호 |
| --- | --- | --- |
| 데이터 소유권 | 내보내기 API 존재 여부 | CSV만 지원, 자동화 불가 |
| 인증 통합 | SSO/SAML/OIDC 지원 | 자체 계정만 허용 |
| SLA | 가용성 보장 수준 | 99.9% 미만, 보상 조건 불명확 |
| 감사 로그 | 관리자 행동 추적 | 로그 보존 기간 30일 미만 |
| 가격 모델 | 좌석/사용량 과금 구조 | 연간 선결제만 허용, 축소 불가 |
| 지역 규제 | 데이터 저장 위치 | 리전 선택 불가, EU 외 저장 |

```yaml
saas_evaluation:
  product: "Notion"
  export_api: true
  sso_support: [SAML, OIDC]
  sla_percent: 99.9
  audit_log_retention_days: 90
  data_region_selectable: false
  contract_flexibility: annual_only
  risk_level: medium
  mitigation: "quarterly data export to S3"
```

이 평가를 도입 전에 한 번 정리해 두면, 나중에 공급사를 교체하거나 데이터를 이전해야 할 때 비용과 리스크를 사전에 예측할 수 있습니다.

## 비용 비교: 같은 앱을 세 모델로 운영할 때

같은 웹 애플리케이션을 IaaS, PaaS, FaaS로 운영할 때 비용 구조가 어떻게 달라지는지 비교합니다. 월 100만 요청, 평균 응답 시간 200ms 기준입니다.

| 항목 | IaaS (EC2 t3.small) | PaaS (Heroku Standard-1X) | FaaS (Lambda) |
| --- | --- | --- | --- |
| 컴퓨트 월 비용 | $15.18 (24/7) | $25.00 (dyno) | $2.08 (1M req × 200ms) |
| 로드밸런서 | $16.20 (ALB) | 포함 | 포함 (API Gateway $3.50) |
| 로그/모니터링 | $5~15 (CloudWatch) | 포함 (기본) | $3~5 (CloudWatch) |
| OS 패치/운영 인건비 | 높음 | 없음 | 없음 |
| 합계 (인프라만) | ~$36 + 인건비 | $25 | ~$9 |
| 적합한 트래픽 패턴 | 상시 트래픽 | 상시 + 간헐 피크 | 간헐적/이벤트 기반 |

이 표의 핵심은 "가장 싼 것이 최선"이 아니라는 점입니다. FaaS는 간헐적 트래픽에서 극적으로 저렴하지만, 상시 높은 트래픽에서는 오히려 비용이 올라갈 수 있습니다. IaaS는 인프라 비용이 예측 가능하지만 운영 인건비를 빼면 비교가 불완전합니다.

### TCO 계산 팁

```python
def monthly_tco(
    compute_usd: float,
    ops_hours: float,
    hourly_rate: float = 50.0,
    managed_services_usd: float = 0.0,
) -> dict:
    """총소유비용(TCO) = 인프라 + 운영 인건비 + 관리형 서비스."""
    ops_cost = ops_hours * hourly_rate
    total = compute_usd + ops_cost + managed_services_usd
    return {"compute": compute_usd, "ops": ops_cost, "managed": managed_services_usd, "total": total}

# IaaS: 인프라 $36, 주 2시간 운영 (월 8시간)
print(monthly_tco(36, ops_hours=8))  # total: $436
# PaaS: 인프라 $25, 주 0.5시간 운영 (월 2시간)
print(monthly_tco(25, ops_hours=2))  # total: $125
# FaaS: 인프라 $9, 거의 무운영 (월 0.5시간)
print(monthly_tco(9, ops_hours=0.5)) # total: $34
```

운영 인건비를 포함하면 IaaS의 실질 비용은 인프라 가격의 10배 이상이 될 수 있습니다. 이것이 "IaaS가 가장 싸다"는 직관이 실무에서 자주 뒤집히는 이유입니다.


## 선택 기준 5가지

1. 우리 팀은 운영 체제와 네트워크까지 직접 다룰 역량과 시간이 있는가.
2. 배포 속도와 제어권 중 무엇이 지금 더 중요한가.
3. 공급사 종속성을 얼마나 감수할 수 있는가.
4. 워크로드가 이벤트 기반인지, 장시간 실행형인지.
5. 보안과 규제 요구사항 때문에 세밀한 환경 제어가 필요한가.

초기 스타트업은 보통 속도가 더 중요하므로 PaaS나 관리형 서비스를 선호합니다. 반대로 대규모 플랫폼 팀은 비용 최적화와 세밀한 제어를 위해 IaaS나 컨테이너 플랫폼으로 이동하기도 합니다. SaaS는 직접 만들 이유가 없는 업무 영역에서 특히 강력합니다.

## 자주 하는 실수 5가지

1. PaaS를 VM처럼 다루려고 합니다.
2. 운영 인력이 부족한데도 IaaS를 먼저 선택합니다.
3. SaaS 도입 시 데이터 락인과 내보내기 전략을 무시합니다.
4. FaaS의 콜드 스타트와 실행 제약을 과소평가합니다.
5. 여러 모델을 섞어 쓰면서 책임 경계를 명확히 정리하지 않습니다.

실무에서는 다섯 번째 실수가 특히 자주 문제를 만듭니다. 인증은 SaaS, 앱은 PaaS, 데이터 처리는 IaaS에서 돌리는데 책임 문서가 없다면 장애가 났을 때 어디서 무슨 문제가 시작됐는지 추적하기 어려워집니다. 장애 발생 시 "이건 PaaS 공급자 문제인가, 우리 코드 문제인가"를 5분 안에 판단할 수 없다면 책임 경계가 불명확한 상태입니다.

## 실무에서는 이렇게 생각합니다

- 공급자보다 우리가 더 잘할 수 있는 운영만 직접 맡습니다.
- PaaS에서 IaaS로 가는 이동은 비용과 제어권 사이의 교환입니다.
- SaaS의 가격에는 기능뿐 아니라 공급사 리스크도 포함됩니다.
- FaaS는 이벤트 기반 작업에 강력하지만 만능은 아닙니다.
- 추상화는 자유를 주지만 동시에 락인도 만듭니다.


이 다섯 가지 원칙을 더 구체적으로 풀어 보겠습니다.

**"공급자보다 우리가 더 잘할 수 있는 운영만 직접 맡습니다"**는 말은 데이터베이스를 예로 들면 명확합니다. PostgreSQL을 EC2에 직접 설치하면 레플리카, 백업, 페일오버, 버전 업그레이드 모두를 팀이 책임져야 합니다. RDS를 쓰면 이 작업의 대부분을 AWS가 맡습니다. 팀에 DBA가 없다면 RDS가 현실적 선택이고, 전용 DBA가 있고 특수 확장 모듈이나 커널 튜닝이 필요하다면 직접 운영이 맞습니다.

**"추상화는 자유를 주지만 동시에 락인도 만듭니다"**라는 원칙은 대안 전략을 함께 준비해야 한다는 뜻입니다. PaaS를 쓸 때는 컨테이너화가 용이한 구조로 앱을 만들어 두면, 나중에 Kubernetes로 옮길 때 비용이 줄어듭니다. SaaS를 쓸 때는 주기적으로 데이터를 내보내서 다른 도구로 전환할 수 있는 상태를 유지해야 합니다.

## 모델 전환 시나리오

실무에서 자주 볼 수 있는 모델 전환 사례 세 가지를 정리합니다.

**시나리오 1: PaaS → 컨테이너 플랫폼**

- 이유: 트래픽 증가로 dyno 비용이 $500+/월을 초과하고, 플랫폼 제약으로 WebSocket 지원이 불안정해지는 경우.
- 전환 경로: Heroku → Docker 컨테이너화 → ECS/EKS 또는 Cloud Run.
- 전제 조건: 12-Factor App 원칙을 따른 코드 구조, Dockerfile 작성 능력.

**시나리오 2: IaaS → 관리형 서비스**

- 이유: 자체 운영 DB의 페일오버로 장애가 반복되고, DBA 채용이 어려운 경우.
- 전환 경로: EC2 PostgreSQL → RDS PostgreSQL (pg_dump/pg_restore).
- 전제 조건: 커스텀 확장 모듈 미사용, RDS 지원 버전 호환.

**시나리오 3: SaaS → 자체 구축**

- 이유: SaaS 공급사의 가격 인상이 연 30% 이상이거나, API 제한으로 워크플로우 자동화가 불가능해진 경우.
- 전환 경로: Notion → 자체 Wiki (예: Outline) + S3 + RDS.
- 전제 조건: 내보내기 API로 데이터 이전 가능, 자체 운영 인력 확보.

모델 전환은 항상 비용이 듭니다. 핵심은 "전환이 필요해진 시점"을 정량적으로 정의해 두는 것입니다. 예를 들어 "월 비용이 $X를 넘으면", "운영 장애가 월 Y회 이상이면"처럼 마지노선을 미리 정해 두면 감정적 판단을 피할 수 있습니다.

## 체크리스트

- [ ] 각 워크로드가 적절한 서비스 모델에 매핑되어 있는가.
- [ ] 공급사 락인을 평가했는가.
- [ ] 비용을 단순 나열이 아니라 시뮬레이션했는가.
- [ ] 필요한 운영 인력이 준비되어 있는가.

## 연습 문제

1. 데이터베이스를 IaaS 위에 직접 운영하는 경우와 PaaS 데이터베이스를 쓰는 경우를 비교해 보세요.
2. FaaS에 잘 맞지 않는 워크로드 하나를 떠올려 보세요.
3. SaaS를 도입할 때 데이터 내보내기 기능이 왜 필수인지 설명해 보세요.

## 정리 및 다음 단계

IaaS, PaaS, SaaS의 차이는 기능 이름보다 책임 경계에서 분명해집니다. 어디까지를 우리가 운영하고, 어디부터를 공급자가 맡는지 이해하면 모델 선택이 훨씬 쉬워집니다. 다음 글에서는 모델을 골랐다면 그다음에 따라오는 질문, 즉 어디에서 실행할지를 보겠습니다.


## 선택 기준을 숫자로 만드는 방법

IaaS, PaaS, SaaS를 감으로 고르면 팀마다 기준이 달라져 의사결정이 흔들립니다. 그래서 실무에서는 선택 기준을 표로 고정해 두는 편이 좋습니다. 아래 표는 서비스 모델을 평가할 때 자주 쓰는 질문을 정량화한 예시입니다.

| 평가 항목 | 질문 | IaaS 점수 경향 | PaaS 점수 경향 | SaaS 점수 경향 |
| --- | --- | --- | --- | --- |
| 배포 속도 | 오늘 시작해 다음 주 배포 가능한가 | 2 | 4 | 5 |
| 제어권 | OS/네트워크를 세밀히 제어해야 하는가 | 5 | 3 | 1 |
| 운영 인력 부담 | 온콜과 패치 운영을 감당 가능한가 | 1 | 3 | 5 |
| 커스터마이징 | 커널/런타임 레벨 수정이 필요한가 | 5 | 2 | 1 |
| 규제 대응 | 감사 추적과 분리 통제가 필요한가 | 4 | 3 | 2 |
| 공급사 종속성 | 특정 플랫폼 의존을 허용 가능한가 | 3 | 2 | 1 |

점수는 절대값이 아니라 팀 상황에 따른 상대 비교 도구입니다. 예를 들어 작은 팀에서 "운영 인력 부담" 가중치를 높게 두면 PaaS나 SaaS가 현실적 선택이 됩니다.

### 책임 분리 상세 매트릭스

| 레이어 | IaaS에서 사용자 책임 | PaaS에서 사용자 책임 | SaaS에서 사용자 책임 |
| --- | --- | --- | --- |
| 네트워크 | VPC/방화벽/라우팅 | 앱 레벨 접근 정책 | 사용자 접근 정책 |
| 컴퓨트 | 인스턴스/OS 패치 | 앱 코드/빌드 아티팩트 | 없음 |
| 데이터 | 암호화/백업/권한 | 데이터 스키마/권한 | 데이터 분류/보존 |
| 관측 | 에이전트 설치/수집 | 앱 로그/메트릭 | 감사 로그 확인 |
| 비용 | 인스턴스 사이징/예약 | 사용량 추적 | 라이선스/좌석 관리 |

이 표가 유용한 이유는 책임 공백을 빨리 찾을 수 있기 때문입니다. 예를 들어 PaaS를 선택했는데 백업 책임을 플랫폼이 자동으로 다 해 준다고 오해하면, 사고 시 복구 가능 시점(RPO)을 보장하지 못할 수 있습니다.

### 모델 혼합 전략

실제 조직은 하나만 고르지 않고 혼합합니다.

- 인증/협업: SaaS
- 고객 API: PaaS 또는 컨테이너 플랫폼
- 데이터 파이프라인: IaaS + 관리형 서비스

혼합 자체는 문제없지만, 책임 문서를 분리하지 않으면 장애 대응 단계에서 경계가 무너집니다. 따라서 아키텍처 다이어그램 옆에 다음 형태의 책임표를 붙이는 것을 권장합니다.

```json
{
  "service": "customer-api",
  "model": "PaaS",
  "owner_team": "platform-app",
  "shared_responsibility": {
    "provider": ["runtime_patch", "base_network"],
    "customer": ["app_security", "data_classification", "iam_policy"]
  }
}
```

이 문서가 있으면 감사 대응, 장애 분석, 인수인계 품질이 동시에 올라갑니다. 모델 선택의 목적은 최신 기술 채택이 아니라 운영 예측 가능성을 높이는 데 있습니다.

## 처음 질문으로 돌아가기

- **EC2, Heroku, Notion처럼 모두 클라우드에 속하는 서비스가 왜 이렇게 다르게 느껴질까요?**
  EC2는 가상 머신을 직접 관리해야 하는 IaaS입니다. Heroku는 언어와 런타임만 선택하면 배포를 자동화하는 PaaS입니다. Notion은 사용자가 완성된 협업 도구를 소비하는 SaaS입니다. 같은 클라우드이지만 운영 책임과 추상화 수준이 크게 다릅니다.
- **IaaS, PaaS, SaaS는 각각 어디까지를 사용자가 운영하고, 어디부터 공급자가 맡을까요?**
  작은 팀이 IaaS에서 모든 것을 직접 구축하면 배포 속도가 느려지고, PaaS 제약에 맞추는 데 시간이 많이 걸립니다. 조직의 개발 역량, 규제 요구사항, 운영 팀 규모를 고려해 선택해야 합니다.
- **조직 규모와 워크로드 특성에 따라 어떤 모델을 선택해야 할까요?**
  IaaS를 선택하면 세밀한 제어가 가능하지만 운영 부담이 큽니다. PaaS를 선택하면 배포는 빠르지만 플랫폼 제약이 있습니다. SaaS는 즉시 사용 가능하지만 커스터마이징이 제한됩니다. 각 모델의 장단점을 명확히 이해한 후 팀의 상황에 맞게 선택하는 것이 중요합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Cloud Computing 101 (1/10): Cloud Computing이란 무엇인가?](./01-what-is-cloud-computing.md)
- **IaaS, PaaS, SaaS (현재 글)**
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

- [NIST SP 800-145 — service models](https://csrc.nist.gov/publications/detail/sp/800-145/final)
- [AWS — types of cloud computing](https://aws.amazon.com/types-of-cloud-computing/)
- [Heroku — platform overview](https://devcenter.heroku.com/categories/platform)
- [Vercel — serverless functions](https://vercel.com/docs/functions)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/cloud-computing-101/ko)
Tags: Cloud, IaaS, PaaS, SaaS, Architecture
