---
series: mlops-101
episode: 10
title: "MLOps 101 (10/10): 운영 가능한 ML 시스템"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - MLOps
  - Architecture
  - Production
  - DataScience
  - Pipeline
seo_description: 실험 관리부터 재학습까지의 MLOps 요소를 닫힌 운영 루프로 엮고, 팀의 성숙도를 평가하여 지속 가능한 ML 시스템을 구축하는 청사진입니다.
last_reviewed: '2026-05-12'
---

# MLOps 101 (10/10): 운영 가능한 ML 시스템

시리즈 앞부분에서는 실험 관리, 데이터 버전 관리, 학습 파이프라인, 배포, 모니터링, 드리프트, 재학습, 피처 스토어를 각각 따로 봤습니다. 그런데 개별 조각을 아는 것과 그것을 하나의 운영 시스템으로 묶는 일은 완전히 다른 문제입니다.

현업에서 어려운 지점도 여기에 있습니다. 도구 이름을 안다고 시스템이 되는 것은 아닙니다. 데이터가 언제 학습으로 넘어가고, 학습 결과가 어떤 기준으로 등록되고, 이상 징후가 보이면 누가 무엇을 해야 하는지까지 연결되어야 비로소 운영 가능한 시스템이 됩니다.

여기서는 앞선 아홉 개 조각을 하나의 운영 루프로 엮어 보고, 팀이 지금 어디쯤 와 있는지 평가하는 최소 체크리스트까지 정리하겠습니다.

![MLOps 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/10/10-01-see-the-loop-first.ko.png)
*MLOps 101 10장 흐름 개요*
> 됨 단계를 비파근총랐으로 단브 빠니다. 단단을 브는 단순냸답니다. 단뉸내거나 뮤랜발당니다.

## 먼저 던지는 질문

- 앞선 아홉 개 구성 요소는 실제 시스템에서 어떻게 연결될까요?
- 왜 도구를 각각 아는 것만으로는 운영 체계가 되지 않을까요?
- 런북, 온콜, SLI/SLO는 기술 요소와 어떻게 맞물릴까요?

## 왜 중요한가

좋은 모델 하나를 만드는 일과 운영 가능한 시스템을 만드는 일은 다릅니다. 전자는 실험 최적화에 가깝고, 후자는 경계 설계와 복구 설계에 가깝습니다. 그래서 개별 도구 이해만으로는 충분하지 않습니다.

운영 가능한 시스템이 되려면 세 가지가 함께 있어야 합니다. 첫째, 데이터와 모델 흐름이 자동으로 연결되어야 합니다. 둘째, 이상 징후가 보이면 관측과 대응이 이어져야 합니다. 셋째, 사람이 개입해야 할 순간과 자동화가 맡을 순간이 구분되어 있어야 합니다.

---

## 전체 흐름을 먼저 보겠습니다

이 그림은 시리즈 전체를 하나의 루프로 압축한 모습입니다. 데이터 버전 관리와 피처 스토어가 입력 일관성을 잡고, 학습 파이프라인이 모델을 만들고, 모델 레지스트리가 버전을 관리하고, 배포와 모니터링이 운영 상태를 관찰합니다. 드리프트와 재학습은 다시 학습 루프로 되돌아가게 만듭니다.

중요한 것은 이 구조가 직선이 아니라 순환 구조라는 사실입니다. 운영 중 나온 신호가 다시 학습으로 들어와야 MLOps가 완성됩니다.

---

## 먼저 잡아야 할 핵심 개념

- **MLOps 성숙도**: 수동 중심 단계에서 자동화 단계, 더 나아가 자율 운영 단계로 발전하는 정도입니다.
- 런북: 경고가 울렸을 때 무엇을 확인하고 어떤 조치를 취할지 적어 둔 문서입니다.
- 온콜: 운영 경고에 대응할 담당 책임 체계입니다.
- **SLI/SLO**: 서비스 상태를 측정하는 지표와 목표입니다.
- **포스트모템**: 사고 뒤에 원인과 재발 방지책을 정리하는 비난 없는 리뷰입니다.

이 다섯 개는 도구 목록에서 빠지기 쉽지만, 실제 운영 체계를 완성하는 데 꼭 필요합니다. 시스템은 자동화만으로 유지되지 않고 대응 절차까지 포함해 돌아갑니다.

---

## 도입 전과 도입 후를 비교해 보겠습니다

**Before**: 노트북에서 학습하고 수동 배포하고, 운영 이슈는 사용자가 먼저 발견합니다.

**After**: 데이터에서 학습, 등록, 배포, 경고, 재학습까지 하나의 루프가 이어집니다.

Before 상태에서는 사람 기억과 수작업이 시스템 경계를 대신합니다. After 상태에서는 경계가 명시적이고, 빠진 구성 요소도 체크리스트로 드러납니다.

---

## MLOps 성숙도 레벨

구글과 마이크로소프트는 MLOps 성숙도를 단계별로 정의하고 있습니다. 아래 표는 Level 0부터 Level 3까지 자동화, 재현성, 모니터링, 거버넝스 기준으로 비교합니다.

| 레벨 | 자동화 수준 | 재현성 | 모니터링 | 거버넝스 | 설명 |
|---|---|---|---|---|---|
| **Level 0** | 수동 | 낮음 | 없음 | 없음 | 노트북에서 실험, 수동 배포 |
| **Level 1** | 일부 | 중간 | 기본 | 약함 | 학습 파이프라인 자동화, 모델 레지스트리 |
| **Level 2** | 높음 | 높음 | 충분 | 중간 | 자동 재학습, 드리프트 감지, 피처 스토어 |
| **Level 3** | 완전 | 매우 높음 | 포괄적 | 강함 | 자율 재학습, A/B 테스트, 거버넝스 완비 |

Level 0은 모델을 한 번 학습해 배포하고 끝나는 단계입니다. Level 1은 학습 파이프라인이 자동화되지만 재학습은 수동입니다. Level 2는 드리프트 감지와 재학습 트리거가 연결됩니다. Level 3은 모델이 스스로 검증하고 승격하는 자율 단계입니다.

---

## 레벨별 도입 로드맵

대부분의 팀은 Level 0에서 시작합니다. 각 레벨로 올라가려면 어떤 구성 요소를 먼저 도입해야 할까요? 아래는 레벨별 권장 로드맵입니다.

### Level 0 → Level 1 (첫 6주)

1. 주 1-2: 데이터 버전 관리 (DVC 또는 Git LFS)
2. 주 3-4: 모델 레지스트리 (MLflow)
3. 주 5-6: 학습 파이프라인 (Airflow 또는 Prefect)

### Level 1 → Level 2 (다음 8주)

1. 주 1-2: 모델 모니터링 (Prometheus + Grafana)
2. 주 3-4: 드리프트 감지 (PSI, KS 계산)
3. 주 5-6: 재학습 트리거 (DAG + 비교 로직)
4. 주 7-8: 피처 스토어 (Feast)

### Level 2 → Level 3 (다음 12주)

1. 주 1-3: A/B 테스트 프레임워크
2. 주 4-6: 자동 승격 정책 (Staging → Production)
3. 주 7-9: 거버넝스 체계 (승인, 감사 로그)
4. 주 10-12: 자율 재학습 루프 통합

이 로드맵은 한 번에 하나씩 도입하는 것을 전제로 합니다. 동시에 여러 요소를 넣으면 복잡도만 커지고 효과는 분산됩니다.

---

## 팀 구성과 역할

MLOps가 성숙해지면 팀 구성도 달라집니다. Level 0에서는 데이터 과학자 한 명이 모든 것을 하지만, Level 2 이상에서는 역할이 분리됩니다.

| 역할 | 책임 | 필요한 레벨 |
|---|---|---|
| **ML Engineer** | 모델 학습, 평가, 배포, 모니터링 | Level 1+ |
| **Data Engineer** | 데이터 파이프라인, 피처 엔지니어링, 품질 | Level 1+ |
| **Platform Engineer** | 인프라, CI/CD, 모니터링, 보안 | Level 2+ |
| **Data Scientist** | 실험, 모델 프로토타입, 해석 | 모든 레벨 |

팀 크기가 작으면 한 명이 여러 역할을 겸하지만, 팀이 커지면 각 역할이 명확해집니다. 특히 Platform Engineer는 Level 2 이상에서 필수적입니다. 인프라, CI/CD, 모니터링, 보안은 ML 전문 지식보다 운영 전문 지식을 더 많이 필요로 하기 때문입니다.

역할 분리가 명확해지면 첱임 경계도 명확해집니다. 모델 성능이 떨어졌을 때 ML Engineer가 모델을 보고, Data Engineer가 데이터를 보고, Platform Engineer가 인프라를 볼 수 있습니다.

---

## 성숙도 점검표를 코드로 표현해 보겠습니다

### 1단계 — 점검 항목을 둡니다

```python
checks = {
    "data_versioned": True,
    "pipeline_dag": True,
    "model_registry": True,
    "container_image": True,
    "metrics_endpoint": True,
    "drift_alert": False,
    "retraining_trigger": False,
    "feature_store": False,
    "runbook": True,
}
```

이 딕셔너리는 팀이 갖춰야 할 운영 요소를 단순하게 보여 줍니다. 어떤 항목이 빠져 있는지 코드로 드러내면, 추상적인 성숙도 논의가 훨씬 구체적인 개선 목록으로 바뀝니다.

### 2단계 — 성숙도 점수를 계산합니다

```python
def maturity(checks: dict) -> str:
    score = sum(checks.values())
    if score >= 8:
        return "production"
    if score >= 5:
        return "transitional"
    return "early"

print(maturity(checks))
```

물론 실제 성숙도를 숫자 하나로 완벽하게 표현할 수는 없습니다. 그래도 팀 대화에서는 이런 공통 기준이 유용합니다. 지금이 초기 단계인지, 전환 구간인지, 운영 수준인지 빠르게 공유할 수 있기 때문입니다.

### 3단계 — 빠진 항목을 찾습니다

```python
def missing(checks: dict) -> list:
    return [k for k, v in checks.items() if not v]

print(missing(checks))
```

성숙도라는 말은 자주 추상적으로 흘러갑니다. 빠진 항목을 바로 나열하면, 부족한 부분이 논쟁이 아니라 작업 목록으로 바뀝니다.

### 4단계 — 다음 우선순위를 고릅니다

```python
def next_step(missing_items: list) -> str:
    priority = ["drift_alert", "retraining_trigger", "feature_store"]
    for p in priority:
        if p in missing_items:
            return p
    return "done"

print(next_step(missing(checks)))
```

운영 체계는 한 번에 완성되지 않습니다. 그래서 가장 중요한 다음 한 걸음을 고르는 일이 중요합니다. 부족한 것을 다 아는 것보다, 지금 무엇부터 고칠지 정하는 편이 더 실전적입니다.

### 5단계 — 팀 상태 문장을 만듭니다

```python
def status_line(checks: dict) -> str:
    return f"{maturity(checks)} | next={next_step(missing(checks))}"

print(status_line(checks))
```

짧은 상태 문장은 팀이 같은 상황 인식을 공유하게 해 줍니다. 긴 문서도 필요하지만, 운영에서는 지금 상태와 다음 우선순위를 한 줄로 말할 수 있는지가 더 중요할 때가 많습니다.

---

## 이 코드에서 먼저 봐야 할 점

- 체크리스트를 코드로 두면 진척이 눈에 보입니다.
- 성숙도 기준이 있어야 팀이 같은 언어로 대화합니다.
- 다음 한 가지를 고르는 것만으로도 개선 속도가 붙습니다.
- 운영 요소와 기술 요소를 함께 봐야 시스템이 완성됩니다.

이 예제는 단순하지만 중요한 태도를 보여 줍니다. MLOps는 플랫폼 도입이 아니라, 점검 가능하고 설명 가능한 운영 상태를 만드는 일입니다.

---

## 자주 헷갈리는 지점

1. **모든 구성 요소를 한 번에 도입하려고 합니다.**
   복잡도만 커지고 팀 피로가 빨리 옵니다.
2. **도구만 보고 조직 변화는 놓칩니다.**
   소유자와 대응 절차가 없으면 시스템이 굴러가지 않습니다.
3. **SLO 없이 경고부터 붙입니다.**
   무엇이 중요한 신호인지 합의되지 않습니다.
4. **런북 없이 온콜부터 시작합니다.**
   경고를 받아도 첫 10분 행동이 정해지지 않습니다.
5. **같은 사고를 반복하면서 포스트모템을 남기지 않습니다.**
   시스템은 사고 뒤의 학습으로 자랍니다.

---

## 실무에서는 이렇게 봅니다

예를 들어 핀테크 팀이 결제 이상 탐지 모델을 운영한다면, 데이터 준비와 학습은 DAG로 돌고, 모델 버전은 레지스트리에서 관리하고, 온라인 피처는 피처 스토어에서 읽고, 운영 지표는 Prometheus로 수집하며, 드리프트 경고가 오면 재학습 후보를 만들고 온콜이 런북에 따라 대응하는 구조가 흔합니다.

시니어 엔지니어는 처음부터 완성형 플랫폼을 만들기보다 가장 약한 연결부를 먼저 고칩니다. 그리고 경고는 행동 요청이어야 하고, 문서는 시스템의 일부이며, 변화는 한 번에 하나씩만 넣어야 원인을 읽을 수 있다고 봅니다.

---

## 체크리스트

- [ ] 데이터 버전 관리가 들어가 있다.
- [ ] 학습이 DAG로 반복 실행된다.
- [ ] 모델 레지스트리가 있다.
- [ ] 모니터링과 드리프트 감지가 운영에 연결되어 있다.
- [ ] 재학습 트리거가 정의되어 있다.
- [ ] 런북과 온콜 체계가 있다.

## 연습 문제

1. 지금 팀에 없는 구성 요소 세 가지를 골라 6주 도입 계획을 적어 보세요.
2. `99% < 200ms` 같은 SLO를 가장 먼저 깨뜨릴 수 있는 구성 요소를 골라 보세요.
3. 자동 재학습이 새로 만드는 조직 리스크 두 가지를 정리해 보세요.

## 운영 ML 아키텍처 구성 요소 표준화

개별 도구를 나열하는 대신, 운영 시스템을 구성 요소와 책임으로 분해하면 전체 구조가 훨씬 명확해집니다.

| 구성 요소 | 핵심 책임 | 대표 도구 |
|---|---|---|
| 데이터 수집 계층 | 원천 데이터 적재, 스키마 검증 | Kafka, Airbyte, dbt |
| 데이터/피처 계층 | 버전 관리, 피처 정의, 적재 | DVC, Feast, LakeFS |
| 학습 계층 | 재현 가능한 학습, 평가 | Airflow, Prefect, MLflow |
| 모델 관리 계층 | 버전, 스테이지 전환, 승인 | MLflow Registry, SageMaker Registry |
| 서빙 계층 | 온라인 추론 API, 배치 추론 | FastAPI, BentoML, Spark |
| 관측 계층 | 메트릭/로그/알림/런북 연계 | Prometheus, Grafana, Alertmanager |
| 운영 거버넌스 | 온콜, 포스트모템, 변경 승인 | PagerDuty, Jira, 문서 체계 |

이 표를 기반으로 현재 시스템에서 누락된 계층을 먼저 확인하면 도입 우선순위가 분명해집니다.

## 팀 역할과 책임 경계

| 역할 | 주요 책임 | 산출물 |
|---|---|---|
| Data Engineer | 데이터 파이프라인, 품질 보장 | 정제 데이터셋, 스키마 정책 |
| ML Engineer | 학습/배포 자동화 | DAG, 모델 아티팩트, 배포 스크립트 |
| Data Scientist | 피처/모델 설계, 실험 | 실험 리포트, 모델 비교 결과 |
| Backend Engineer | API/서빙 안정화 | 서빙 코드, 성능 개선 |
| SRE/Platform | 모니터링, 온콜, SLO | 대시보드, 경고 정책, 런북 |
| Product Owner | KPI 우선순위, 릴리스 승인 | 목표 지표, 배포 결정 |

MLOps는 기술 문제이면서 동시에 협업 구조 문제입니다. 책임 경계가 모호하면 자동화가 있어도 장애 대응이 느려집니다.

## 시스템 상태 점검 스코어카드

```python
scorecard = {
    "data_versioning": True,
    "feature_consistency": True,
    "reproducible_training": True,
    "registry_governance": True,
    "safe_rollout": True,
    "monitoring_alerts": True,
    "drift_response": False,
    "retraining_automation": False,
    "runbook_oncall": True,
}

score = sum(scorecard.values())
print({"score": score, "max": len(scorecard)})
```

점수 자체보다 중요한 것은 누락 항목을 분명히 드러내는 기능입니다. 이 스코어카드는 분기별 개선 회의의 공통 입력으로 사용할 수 있습니다.

## 90일 개선 로드맵 예시

1. 1-30일: 드리프트 경고와 런북 연결을 완성합니다.
2. 31-60일: 재학습 트리거와 챔피언-챌린저 비교 자동화를 붙입니다.
3. 61-90일: 승격 승인 절차와 사고 포스트모템 템플릿을 정착시킵니다.

로드맵의 핵심은 "모든 것을 동시에"가 아니라 "가장 약한 연결부를 순차적으로 보강"하는 데 있습니다.

## 프로덕션 ML 구성요소 점검 표

| 점검 항목 | 확인 질문 | Pass 기준 |
|---|---|---|
| 입력 경계 | 스키마 변경이 감지되면 자동 차단되는가 | 스키마 검증 실패 시 학습/서빙 중단 |
| 학습 재현성 | 동일 커밋과 데이터 버전으로 재실행 가능한가 | 동일 메트릭 재현 오차 허용범위 내 |
| 배포 안전성 | 카나리/롤백 절차가 자동화되어 있는가 | 5분 내 이전 챔피언 복구 가능 |
| 관측성 | 모델/피처/인프라 메트릭이 함께 보이는가 | 단일 대시보드에서 상호 연관 분석 가능 |
| 운영 대응 | 경고 이후 첫 10분 행동이 정의되어 있는가 | 런북 기반 표준 대응 시나리오 존재 |

이 표는 도구 도입 여부보다 운영 가능성을 평가하는 기준입니다. 시스템 점검 회의에서 이 다섯 항목을 반복 확인하면, 기능 추가보다 안정성 보강의 우선순위를 유지하기 쉽습니다.

## 플랫폼 설정 코드로 일관성 유지하기

운영 ML 시스템에서는 여러 컴포넌트의 설정이 일관되어야 합니다. 피처 스토어, 모델 레지스트리, 모니터링, 배포 환경이 서로 다른 설정을 참조하면 사고가 납니다. 설정을 코드로 관리하는 패턴을 보겠습니다.

```python
from dataclasses import dataclass, field
from pathlib import Path
import yaml

@dataclass
class ModelConfig:
    name: str
    version: str
    registry_uri: str
    serving_endpoint: str
    min_replicas: int = 1
    max_replicas: int = 4
    target_latency_ms: int = 100

@dataclass
class MonitoringConfig:
    prometheus_endpoint: str
    alert_slack_channel: str
    drift_check_interval_hours: int = 6
    slo_availability: float = 0.999
    slo_latency_p95_ms: int = 100

@dataclass
class FeatureStoreConfig:
    offline_store_path: str
    online_store_type: str = "redis"
    online_store_host: str = "redis.internal"
    ttl_days: int = 7

@dataclass
class PlatformConfig:
    environment: str  # dev, staging, production
    models: list[ModelConfig] = field(default_factory=list)
    monitoring: MonitoringConfig = None
    feature_store: FeatureStoreConfig = None

    @classmethod
    def from_yaml(cls, path: str) -> "PlatformConfig":
        with open(path) as f:
            data = yaml.safe_load(f)
        models = [ModelConfig(**m) for m in data.get("models", [])]
        monitoring = MonitoringConfig(**data["monitoring"]) if "monitoring" in data else None
        feature_store = FeatureStoreConfig(**data["feature_store"]) if "feature_store" in data else None
        return cls(
            environment=data["environment"],
            models=models,
            monitoring=monitoring,
            feature_store=feature_store,
        )
```

대응하는 YAML 설정 파일은 다음과 같습니다.

```yaml
environment: production

models:
  - name: fraud-detector
    version: "3.2.1"
    registry_uri: http://mlflow.internal:5000
    serving_endpoint: http://fraud-api.internal:8000
    min_replicas: 2
    max_replicas: 8
    target_latency_ms: 50
  - name: recommender
    version: "2.1.0"
    registry_uri: http://mlflow.internal:5000
    serving_endpoint: http://rec-api.internal:8000
    min_replicas: 3
    max_replicas: 12
    target_latency_ms: 80

monitoring:
  prometheus_endpoint: http://prometheus.internal:9090
  alert_slack_channel: "#ml-alerts"
  drift_check_interval_hours: 4
  slo_availability: 0.999
  slo_latency_p95_ms: 100

feature_store:
  offline_store_path: s3://ml-data/feature-store/
  online_store_type: redis
  online_store_host: redis-cluster.internal
  ttl_days: 14
```

이 설정을 Git으로 관리하면 변경 이력이 남고, PR 리뷰로 실수를 잡을 수 있습니다. "누가 언제 왜 replica 수를 바꿨는지" 추적이 가능합니다.

## 시스템 통합 테스트

개별 컴포넌트가 잘 동작해도, 연결 지점에서 문제가 발생할 수 있습니다. 통합 테스트는 전체 파이프라인이 끝에서 끝까지 동작하는지 검증합니다.

```python
import httpx
import time

def integration_test(config: PlatformConfig) -> dict:
    """전체 ML 시스템의 통합 테스트를 실행합니다."""
    results = {}

    # 1. 피처 스토어 접근 가능 여부
    try:
        from feast import FeatureStore
        store = FeatureStore(repo_path="feature_repo/")
        store.get_online_features(
            features=["customer_features:total_purchases"],
            entity_rows=[{"customer_id": "test-001"}],
        )
        results["feature_store"] = "PASS"
    except Exception as e:
        results["feature_store"] = f"FAIL: {e}"

    # 2. 각 모델 서빙 엔드포인트 헬스 체크
    for model in config.models:
        try:
            resp = httpx.get(f"{model.serving_endpoint}/healthz", timeout=5.0)
            results[f"model_{model.name}_health"] = (
                "PASS" if resp.status_code == 200 else f"FAIL: {resp.status_code}"
            )
        except Exception as e:
            results[f"model_{model.name}_health"] = f"FAIL: {e}"

    # 3. 모니터링 시스템 접근
    try:
        resp = httpx.get(
            f"{config.monitoring.prometheus_endpoint}/api/v1/status/config",
            timeout=5.0,
        )
        results["monitoring"] = "PASS" if resp.status_code == 200 else f"FAIL: {resp.status_code}"
    except Exception as e:
        results["monitoring"] = f"FAIL: {e}"

    # 4. 종단 간 추론 테스트
    for model in config.models:
        try:
            start = time.time()
            resp = httpx.post(
                f"{model.serving_endpoint}/predict",
                json={"features": [0.1] * 10},
                timeout=float(model.target_latency_ms) / 1000 * 3,
            )
            latency_ms = (time.time() - start) * 1000
            if resp.status_code == 200 and latency_ms < model.target_latency_ms:
                results[f"model_{model.name}_e2e"] = f"PASS ({latency_ms:.0f}ms)"
            else:
                results[f"model_{model.name}_e2e"] = f"FAIL: status={resp.status_code}, latency={latency_ms:.0f}ms"
        except Exception as e:
            results[f"model_{model.name}_e2e"] = f"FAIL: {e}"

    return results
```

이 테스트를 매일 새벽에 실행하면, 인프라 변경이나 네트워크 문제로 시스템이 조용히 깨지는 것을 조기에 발견할 수 있습니다.

## 정리

운영 가능한 ML 시스템은 여러 도구를 나열한다고 생기지 않습니다. 데이터, 학습, 등록, 배포, 관측, 재학습이 닫힌 루프로 연결되고, 각 단계의 책임과 대응 절차가 분명해야 비로소 시스템이 됩니다.

이 시리즈에서 가져가야 할 마지막 문장은 이것입니다. **MLOps의 완성은 더 많은 도구가 아니라, 더 분명한 경계와 더 짧은 운영 루프입니다.** 이제 실제 프로젝트에서 가장 약한 연결부 하나를 골라, 그 지점부터 시스템으로 바꿔 보시면 됩니다.

## 처음 질문으로 돌아가기

- **앞선 아홉 개 구성 요소는 실제 시스템에서 어떻게 연결될까요?**
  - 본문의 기준은 운영 가능한 ML 시스템를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **왜 도구를 각각 아는 것만으로는 운영 체계가 되지 않을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **런북, 온콜, SLI/SLO는 기술 요소와 어떻게 맞물릴까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [MLOps 101 (1/10): MLOps란 무엇인가?](./01-what-is-mlops.md)
- [MLOps 101 (2/10): 실험 관리](./02-experiment-tracking.md)
- [MLOps 101 (3/10): 데이터 버전 관리](./03-data-versioning.md)
- [MLOps 101 (4/10): 모델 학습 파이프라인](./04-training-pipeline.md)
- [MLOps 101 (5/10): 모델 배포](./05-model-deployment.md)
- [MLOps 101 (6/10): 모델 모니터링](./06-model-monitoring.md)
- [MLOps 101 (7/10): 데이터 드리프트와 모델 드리프트](./07-data-and-model-drift.md)
- [MLOps 101 (8/10): 재학습](./08-retraining.md)
- [MLOps 101 (9/10): 피처 스토어](./09-feature-store.md)
- **운영 가능한 ML 시스템 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/mlops-101/ko)

- [Google — MLOps maturity](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
- [Microsoft — MLOps maturity model](https://learn.microsoft.com/azure/architecture/example-scenario/mlops/mlops-maturity-model)
- [Made With ML](https://madewithml.com/)
- [Hidden Technical Debt in ML Systems](https://papers.nips.cc/paper_files/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html)

Tags: MLOps, Architecture, Production, DataScience, Pipeline
