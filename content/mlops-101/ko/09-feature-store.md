---
series: mlops-101
episode: 9
title: "MLOps 101 (9/10): 피처 스토어"
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
  - FeatureStore
  - Feast
  - DataScience
  - Pipeline
seo_description: 학습-서빙 불일치를 해결하기 위해, 피처 정의를 표준화하고 온라인/오프라인 저장소를 통합 관리하는 피처 스토어 활용법을 소개합니다.
last_reviewed: '2026-05-12'
---

# MLOps 101 (9/10): 피처 스토어

같은 이름의 피처를 학습 코드와 서빙 코드가 각각 따로 계산하기 시작하면 언젠가는 어긋납니다. 학습 때는 하루 단위 집계를 쓰고, 서빙 때는 실시간 계산식을 조금 다르게 쓰는 식의 작은 차이가 쌓이면 모델은 배포 전과 배포 후에 다른 세상을 보게 됩니다.

이른바 학습-서빙 불일치는 눈에 잘 띄지 않아서 더 까다롭습니다. 오프라인 검증에서는 잘 나오는데 운영 성능이 기대보다 낮을 때, 실제 원인이 모델 자체보다 피처 계산 경로 차이인 경우가 적지 않습니다.

이 글은 MLOps 101 시리즈의 9번째 글입니다.

여기서는 피처 스토어를 피처 저장소가 아니라, 학습과 서빙이 같은 정의를 공유하게 만드는 계약 계층으로 보고 Feast 예제로 감각을 잡아 보겠습니다.

![MLOps 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/09/09-01-see-the-flow-first.ko.png)
*MLOps 101 9장 흐름 개요*
> 피처 스토어의 핵심은 단순 저장이 아니라, 학습 캐시스럽 배느에 스칼라도 써하는 동동남니다. 모들 먼 메타데이터는 본제 메타데이터로 남니다.

## 먼저 던지는 질문

- 학습-서빙 불일치는 왜 자꾸 반복될까요?
- 온라인 저장소와 오프라인 저장소는 어떤 역할 차이가 있을까요?
- Feast에서 entity와 feature view는 어떻게 이해하면 좋을까요?

## 왜 중요한가

같은 피처 이름을 두 시스템이 각자 계산하면 언젠가는 차이가 납니다. 구현이 조금만 달라도, 시간 기준이 조금만 달라도, 결측 처리 방식이 조금만 달라도 모델 입력은 달라집니다. 이 문제는 실험실에서는 잘 안 보이고 운영에서 크게 드러납니다.

그래서 피처 스토어의 진짜 가치는 저장보다 일관성에 있습니다. 학습용 추출과 서빙용 조회가 같은 정의를 바라보게 해야 학습-서빙 불일치를 줄일 수 있습니다.

---

## 전체 흐름을 먼저 보겠습니다

이 구조에서 중심은 피처 레지스트리입니다. 원천 데이터에서 정의된 피처가 오프라인 저장소와 온라인 저장소로 흘러가고, 학습은 오프라인에서, 서빙은 온라인에서 같은 정의를 씁니다.

즉, 피처 스토어는 값보다 정의를 중심에 둡니다.

---

## 먼저 잡아야 할 핵심 개념

- 엔터티: 피처를 조인할 기준 키입니다. 예를 들어 `user_id`가 여기에 해당합니다.
- **피처 뷰**: 특정 소스와 연결된 피처 정의 묶음입니다.
- **온라인 저장소**: 낮은 지연 시간으로 피처를 읽는 저장소입니다.
- **오프라인 저장소**: 대규모 분석과 학습용 추출을 담당하는 저장소입니다.
- **시점 일치 조인**: 과거 시점에 맞는 피처만 붙여 데이터 누수를 막는 방식입니다.

피처 스토어를 이해할 때는 저장소 종류보다 이 정의 계층을 먼저 봐야 합니다.

---

## 도입 전과 도입 후를 비교해 보겠습니다

**Before**: 학습 노트북과 서빙 코드가 피처를 각자 계산합니다.

**After**: 피처 뷰를 한 번 정의하고 학습과 서빙이 함께 씁니다.

Before 상태에서는 작은 구현 차이가 운영 성능 저하로 이어집니다. After 상태에서는 적어도 피처 정의가 한곳에서 관리됩니다.

---

## 데이터 버전 관리 도구 비교

피처 스토어는 피처 정의를 관리하지만, 원천 데이터 자체의 버전 관리는 별도 도구가 필요합니다. 아래 표는 대표적인 데이터 버전 관리 도구를 저장 방식, Git 연동, 확장 규모로 비교합니다.

| 도구 | 저장 방식 | Git 연동 | 확장 규모 | 주요 특징 |
|---|---|---|---|---|
| **DVC** | 원격 저장소 (S3, GCS) | Git 리모트 연동 | 중간 | 코드와 데이터 버전 분리 |
| **LakeFS** | S3/Azure 위 Git 계층 | Git 유사 명령어 | 대규모 | 브랜치/머지/태그 가능 |
| **Delta Lake** | Parquet + 트랜잭션 로그 | 별도 | 대규모 | ACID, 타임 트래블, 스키마 진화 |

DVC는 Git과 가장 유사하게 동작하며, 코드 저장소와 데이터 저장소를 명시적으로 분리합니다. LakeFS는 S3 위에서 Git 버전 관리 개념을 제공하고, Delta Lake는 Spark 환경에서 ACID 트랜잭션을 지원합니다. 선택 기준은 팀 Git 숙련도, 데이터 크기, 클라우드 인프라입니다.

---

## DVC 사용 예제

DVC는 데이터 파일을 Git으로 직접 관리하지 않고, 메타데이터만 Git에 넣고 실제 파일은 원격 저장소로 분리합니다. 아래는 최소 예제입니다.

```bash
# 1. DVC 초기화
dvc init

# 2. 데이터 파일 추가
dvc add data/train.csv

# 3. 메타데이터 커밋
git add data/train.csv.dvc .gitignore
git commit -m "Add training data"

# 4. 원격 저장소 설정
dvc remote add -d storage s3://my-bucket/dvc-store

# 5. 데이터 푸시
dvc push

# 6. 다른 환경에서 풀
dvc pull
```

`dvc add`는 데이터 파일을 `.dvc` 메타데이터 파일로 바꿔 주고, 원본 파일은 `.gitignore`에 추가합니다. `dvc push`는 원격 저장소로 데이터를 업로드하고, `dvc pull`은 다운로드합니다. 이 구조는 코드와 데이터를 같은 Git 커밋으로 묶어, 모델 버전과 데이터 버전을 함께 추적할 수 있게 합니다.

---

## 데이터 리니지 추적

데이터 버전 관리를 하더라도, 어떤 데이터가 어떤 모델을 학습시켰는지 추적하지 않으면 문제가 생겤도 원인을 찾기 어렵습니다. 데이터 리니지는 데이터 생성, 변환, 소비 경로를 기록하는 개념입니다.

리니지 추적의 핵심 요소는 다음과 같습니다.

1. **원천 데이터**: 어디서 수집했는지
2. **변환 단계**: 정제, 피처 엔지니어링, 집계
3. **모델 학습**: 어떤 모델이 이 데이터로 학습되었는지
4. **예측 로그**: 어떤 모델이 어떤 입력을 받았는지

리니지가 없으면 모델 성능이 나빠졌을 때 데이터가 문제인지 모델이 문제인지 분리하기 어렵습니다. 리니지를 기록하는 방법은 다양하지만, 가장 간단한 방법은 학습 스크립트에서 데이터 경로와 해시를 MLflow 같은 도구에 함께 기록하는 것입니다.

```python
import mlflow
import hashlib

data_path = "data/train.csv"
with open(data_path, "rb") as f:
    data_hash = hashlib.md5(f.read()).hexdigest()

with mlflow.start_run():
    mlflow.log_param("data_path", data_path)
    mlflow.log_param("data_hash", data_hash)
    # 학습 코드
```

이 방법은 모델 버전과 데이터 해시를 연결해, 나중에 모델 성능이 떨어졌을 때 어떤 데이터로 학습했는지 역추적할 수 있게 합니다.

---

## Feast로 아주 작은 흐름을 따라가 보겠습니다

### 1단계 — 피처 정의를 만듭니다

```python
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32

user = Entity(name="user_id", join_keys=["user_id"])
src = FileSource(path="users.parquet", timestamp_field="event_ts")

view = FeatureView(
    name="user_stats",
    entities=[user],
    schema=[Field(name="age", dtype=Float32)],
    source=src,
)
```

이 예제에서 가장 먼저 봐야 할 것은 엔터티와 피처 뷰입니다. 어떤 키로 조인할지, 어떤 소스에서 어떤 피처를 가져올지 정의가 코드로 고정됩니다.

### 2단계 — 정의를 등록합니다

```bash
feast apply
```

등록 단계는 선언한 피처 정의를 시스템에 반영하는 과정입니다. 피처 스토어를 쓰는 이유는 결국 이 정의를 여러 팀과 여러 경로에서 공유하기 위해서입니다.

### 3단계 — 학습용 피처를 조회합니다

```python
from feast import FeatureStore
import pandas as pd

fs = FeatureStore(repo_path=".")
entity_df = pd.DataFrame({"user_id": [1, 2], "event_timestamp": pd.to_datetime(["2026-01-01", "2026-01-02"])})
training = fs.get_historical_features(entity_df, ["user_stats:age"]).to_df()
```

학습용 조회에서는 시점이 특히 중요합니다. 특정 시점의 엔터티에 대해 그때 실제로 알 수 있었던 피처만 붙여야 데이터 누수를 막을 수 있습니다.

### 4단계 — 온라인 저장소로 적재합니다

```bash
feast materialize-incremental $(date -u +"%Y-%m-%dT%H:%M:%S")
```

적재 단계는 오프라인 정의를 온라인 조회 경로와 연결합니다. 이 다리가 있어야 학습 때 본 정의가 서빙에도 같은 형태로 들어옵니다.

### 5단계 — 서빙용 피처를 조회합니다

```python
online = fs.get_online_features(
    features=["user_stats:age"],
    entity_rows=[{"user_id": 1}],
).to_dict()
```

이 단계에서 학습과 서빙이 같은 정의를 공유한다는 점이 드러납니다. 입력 경로는 달라도, 읽는 피처 이름과 정의는 같아야 합니다.

---

## 이 코드에서 먼저 봐야 할 점

- 엔터티는 조인 키 역할을 합니다.
- 피처 뷰는 정의와 소스를 함께 묶습니다.
- 온라인 적재가 오프라인과 온라인 경로를 연결합니다.
- 학습과 서빙의 정의 일치가 가장 중요합니다.

피처 스토어의 가치는 결국 재사용성과 일관성에서 나옵니다. 똑같은 피처를 여러 팀이 따로 계산하지 않게 만드는 효과가 큽니다.

---

## 자주 헷갈리는 지점

1. **팀마다 같은 이름의 피처를 다르게 정의합니다.**
   재사용보다 충돌이 먼저 생깁니다.
2. **시점 일치 조인을 생략합니다.**
   학습 데이터에 미래 정보가 섞입니다.
3. **온라인과 오프라인 정의가 다릅니다.**
   학습-서빙 불일치가 다시 생깁니다.
4. **TTL이나 신선도 정책이 없습니다.**
   오래된 피처가 계속 서빙될 수 있습니다.
5. **피처 자체 모니터링이 없습니다.**
   결측이나 지연이 조용히 쌓입니다.

## 피처 스토어 없이 학습-서빙 일관성 유지하기

피처 스토어를 도입하지 않더라도, 학습-서빙 불일치를 줄이는 방법이 있습니다. 핑심은 피처 계산 코드를 함수로 분리하고, 학습과 서빙 모두에서 같은 함수를 불러쓰는 것입니다.

```python
# features.py
def compute_user_features(user_id: int, df) -> dict:
    user_df = df[df["user_id"] == user_id]
    return {
        "age": int(user_df["age"].iloc[0]),
        "purchase_count_7d": len(user_df[user_df["days_ago"] <= 7]),
    }
```

학습 스크립트와 서빙 API 모두 이 함수를 가져와 사용합니다.

```python
# train.py
from features import compute_user_features

features = compute_user_features(user_id, df)
```

```python
# serve.py
from features import compute_user_features

features = compute_user_features(user_id, live_df)
```

이 방법은 피처 스토어보다 가볍지만, 실시간 조회가 필요한 경우 지연 시간이 길어질 수 있습니다. 그래도 팀 규모가 작고 모델이 적을 때는 충분히 실용적입니다.

---

## 피처 스토어 도입 판단 기준

피처 스토어는 모든 팀에 필요한 것은 아닙니다. 아래는 피처 스토어 도입을 고려할 만한 상황입니다.

1. **여러 모델이 같은 피처를 사용합니다.** 중복 계산을 피할 수 있습니다.
2. **학습-서빙 불일치가 반복됩니다.** 피처 정의를 한곳에서 관리해야 합니다.
3. **실시간 피처가 필요합니다.** 요청당 5ms 이내에 피처를 가져와야 합니다.
4. **팀 규모가 5명 이상입니다.** 피처 정의를 공유하는 효과가 커집니다.

만약 모델이 1-2개이고 팀이 2-3명이면, 피처 스토어 도입보다 함수 분리로 충분할 수 있습니다. 피처 스토어는 도구이지만 동시에 운영 비용도 만듭니다.

---
---

## 실무에서는 이렇게 봅니다

결제 이상 탐지나 추천 시스템처럼 사용자 행동 피처를 여러 모델이 함께 쓰는 환경에서는 피처 스토어의 투자 대비 효과가 큽니다. 한 번 정의한 피처를 여러 팀이 공통으로 재사용할 수 있기 때문입니다.

시니어 엔지니어는 피처를 모델 입력이 아니라 조직 자산으로 봅니다. 그래서 이름 규칙, 정의 문서화, 시점 일치, 신선도 모니터링을 함께 설계합니다.

---

## 체크리스트

- [ ] 피처 뷰 정의가 버전 관리된다.
- [ ] 시점 일치 조인을 사용한다.
- [ ] 온라인 적재가 스케줄링되어 있다.
- [ ] 피처 신선도와 결측을 모니터링한다.

## 연습 문제

1. 7일 이동 매출 같은 피처를 피처 뷰로 정의해 보세요.
2. 시점 일치 조인이 없으면 어떤 데이터 누수가 생기는지 설명해 보세요.
3. Feast 대신 쓸 수 있는 대안 두 가지와 그 차이를 정리해 보세요.

## Feast 실무 사용 패턴 확장

피처 스토어의 가치는 피처 재사용과 학습-서빙 일관성에 있습니다. 이를 위해 피처 정의, 적재 주기, 신선도 정책을 함께 설계해야 합니다.

### Feast 엔터티/피처뷰 예시 확장

```python
from datetime import timedelta
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Int64, Float32

user = Entity(name="user_id", join_keys=["user_id"])

src = FileSource(
    path="data/user_features.parquet",
    timestamp_field="event_timestamp",
)

user_behavior_v1 = FeatureView(
    name="user_behavior_v1",
    entities=[user],
    ttl=timedelta(days=2),
    schema=[
        Field(name="purchase_cnt_7d", dtype=Int64),
        Field(name="avg_spend_30d", dtype=Float32),
    ],
    source=src,
)
```

TTL을 명시하면 오래된 값이 무기한 서빙되는 위험을 줄일 수 있습니다.

## 피처 서빙 패턴 비교

| 패턴 | 장점 | 주의점 |
|---|---|---|
| 온디맨드 계산 | 최신성 높음 | 지연시간 증가 가능 |
| 온라인 스토어 조회 | 지연시간 낮음 | 적재 지연 관리 필요 |
| 하이브리드 | 성능/최신성 균형 | 아키텍처 복잡도 증가 |

추천, 사기 탐지 같은 저지연 서비스는 온라인 조회를 기본으로 두고, 일부 고비용 피처만 온디맨드로 계산하는 하이브리드가 흔합니다.

## materialization 운영 예시

```bash
# 기준 시점까지 오프라인 -> 온라인 적재
feast materialize 2026-05-01T00:00:00 2026-05-12T00:00:00

# 최근 구간 증분 적재
feast materialize-incremental 2026-05-12T00:00:00
```

적재가 실패하면 온라인 스토어 값이 오래되어 모델 품질이 떨어질 수 있으므로, 적재 성공률과 지연시간 자체를 모니터링해야 합니다.

## 학습/서빙 일관성 점검 코드

```python

def compare_feature_value(train_value: float, serve_value: float, tolerance: float = 1e-6) -> bool:
    return abs(train_value - serve_value) <= tolerance
```

실무에서는 샘플 엔터티를 뽑아 학습 추출값과 온라인 조회값을 주기적으로 비교하는 검증 배치를 두는 편이 좋습니다.

## 피처 거버넌스 제안

- 피처 이름에 도메인 접두사와 버전을 포함합니다. 예: `risk_user_behavior_v1`.
- 피처별 소유 팀과 변경 승인자를 지정합니다.
- 피처 정의 변경 시 영향 모델 목록을 자동 생성합니다.
- 결측률, 신선도, 적재 지연을 피처 품질 SLI로 둡니다.

피처 스토어를 도입해도 거버넌스가 없으면 정의 난립이 다시 발생합니다. 따라서 기술 계층과 운영 정책을 함께 설계해야 합니다.

## 온라인/오프라인 스토어 비교 표

| 관점 | 오프라인 스토어 | 온라인 스토어 |
|---|---|---|
| 주 용도 | 학습 데이터 추출, 백필, 분석 | 실시간 추론 피처 조회 |
| 지연 시간 | 분~시간 | 밀리초~초 |
| 데이터 형태 | 대용량 배치, 시점 기반 조인 | 키 기반 최신값 조회 |
| 품질 점검 | 누락률, 스키마, 시점 일치 | 신선도, 적재 지연, TTL 만료 |
| 대표 기술 | Parquet/S3, BigQuery, Snowflake | Redis, DynamoDB, Cassandra |

팀이 가장 자주 놓치는 부분은 오프라인 데이터 품질 기준과 온라인 신선도 기준이 다르다는 점입니다. 학습 데이터가 깨끗해도 온라인 적재가 늦으면 서빙 품질은 바로 떨어질 수 있습니다.

## Feast 조회 코드 패턴

학습과 서빙에서 같은 피처 이름을 사용하되, 조회 경로만 분리하는 패턴이 운영에서 가장 단순합니다.

```python
from __future__ import annotations

import pandas as pd
from feast import FeatureStore

store = FeatureStore(repo_path="feature_repo")

def load_training_features() -> pd.DataFrame:
    entity_df = pd.DataFrame(
        {
            "user_id": [101, 102, 103],
            "event_timestamp": pd.to_datetime(["2026-05-10", "2026-05-11", "2026-05-12"]),
        }
    )
    return store.get_historical_features(
        entity_df=entity_df,
        features=["user_behavior_v1:purchase_cnt_7d", "user_behavior_v1:avg_spend_30d"],
    ).to_df()

def load_online_features(user_id: int) -> dict:
    return store.get_online_features(
        features=["user_behavior_v1:purchase_cnt_7d", "user_behavior_v1:avg_spend_30d"],
        entity_rows=[{"user_id": user_id}],
    ).to_dict()
```

피처 이름 집합이 학습과 서빙에서 동일하게 유지되면, 성능 하락 시 문제 원인을 모델과 피처 중 어디에서 먼저 볼지 훨씬 빠르게 좁힐 수 있습니다.

## Feast 피처 정의 상세 예시

Feast에서 피처를 정의할 때는 엔티티, 데이터 소스, 피처 뷰, 피처 서비스 네 가지 구성 요소를 이해해야 합니다.

```python
from feast import Entity, FeatureView, Field, FileSource, FeatureService
from feast.types import Float32, Int64, String
from datetime import timedelta

# 1. 엔티티 정의 — 피처를 조회할 때 사용하는 키
customer = Entity(
    name="customer_id",
    join_keys=["customer_id"],
    description="고객 고유 식별자",
)

# 2. 데이터 소스 — 피처 값이 저장된 곳
customer_source = FileSource(
    path="data/customer_features.parquet",
    timestamp_field="event_timestamp",
    created_timestamp_column="created_timestamp",
)

# 3. 피처 뷰 — 피처 그룹과 메타데이터
customer_features = FeatureView(
    name="customer_features",
    entities=[customer],
    ttl=timedelta(days=7),
    schema=[
        Field(name="total_purchases", dtype=Int64),
        Field(name="avg_order_value", dtype=Float32),
        Field(name="days_since_last_order", dtype=Int64),
        Field(name="preferred_category", dtype=String),
        Field(name="lifetime_value", dtype=Float32),
    ],
    source=customer_source,
    online=True,
    tags={"team": "ml-platform", "version": "v2"},
)

# 4. 피처 서비스 — 모델별로 필요한 피처를 묶음
fraud_detection_service = FeatureService(
    name="fraud_detection_features",
    features=[customer_features],
    description="사기 탐지 모델에 필요한 피처 묶음",
)
```

`ttl=timedelta(days=7)`은 7일 이상 지난 피처 값은 온라인 스토어에서 제거한다는 뜻입니다. TTL을 너무 짧게 잡으면 조회 시 null이 반환되고, 너무 길게 잡으면 오래된 값으로 추론하게 됩니다.

## 피처 검증과 스키마 진화

피처 스토어를 운영하다 보면 피처 스키마가 바뀌는 경우가 생깁니다. 새 피처를 추가하거나, 기존 피처의 타입을 변경하거나, 더 이상 사용하지 않는 피처를 제거해야 합니다.

```python
from great_expectations.core import ExpectationSuite, ExpectationConfiguration
import great_expectations as gx

def create_feature_validation_suite(feature_view_name: str) -> ExpectationSuite:
    """피처 뷰에 대한 데이터 품질 검증 스위트를 생성합니다."""
    suite = ExpectationSuite(expectation_suite_name=f"{feature_view_name}_validation")

    # null 비율 검증
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_not_be_null",
            kwargs={"column": "customer_id"},
        )
    )

    # 값 범위 검증
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_values_to_be_between",
            kwargs={
                "column": "avg_order_value",
                "min_value": 0,
                "max_value": 100000,
            },
        )
    )

    # 고유값 비율 검증
    suite.add_expectation(
        ExpectationConfiguration(
            expectation_type="expect_column_proportion_of_unique_values_to_be_between",
            kwargs={
                "column": "customer_id",
                "min_value": 0.99,
                "max_value": 1.0,
            },
        )
    )

    return suite
```

이 검증을 피처 적재 파이프라인에 넣으면, 잘못된 값이 온라인 스토어에 들어가는 것을 막을 수 있습니다. 특히 `avg_order_value`가 음수이거나 비현실적으로 큰 값이면 업스트림 ETL에 문제가 있다는 신호입니다.

## 온라인/오프라인 일관성 검증

피처 스토어의 핵심 약속은 "학습 시점과 서빙 시점에 같은 피처 값을 제공한다"는 것입니다. 이 약속이 깨지면 training-serving skew가 발생합니다.

```python
import numpy as np
from feast import FeatureStore

def validate_online_offline_consistency(
    store: FeatureStore,
    entity_ids: list[dict],
    feature_service_name: str,
    tolerance: float = 0.01,
) -> dict:
    """온라인과 오프라인 피처 값의 일관성을 검증합니다."""
    # 온라인 조회
    online_features = store.get_online_features(
        features=store.get_feature_service(feature_service_name),
        entity_rows=entity_ids,
    ).to_dict()

    # 오프라인 조회 (같은 시점)
    offline_features = store.get_historical_features(
        features=store.get_feature_service(feature_service_name),
        entity_df=create_entity_df(entity_ids),
    ).to_df()

    mismatches = []
    for col in online_features:
        if col in ("customer_id", "event_timestamp"):
            continue
        online_vals = np.array(online_features[col])
        offline_vals = offline_features[col].values
        diff = np.abs(online_vals - offline_vals).max()
        if diff > tolerance:
            mismatches.append({"feature": col, "max_diff": float(diff)})

    return {
        "consistent": len(mismatches) == 0,
        "mismatches": mismatches,
        "checked_features": len(online_features) - 2,
    }
```

이 검증을 주기적으로 실행하면 training-serving skew를 조기에 발견할 수 있습니다.

## 정리

피처 스토어는 피처를 저장하는 상자가 아니라, 학습과 서빙이 같은 정의를 보게 만드는 계약 계층입니다. 이 계층이 있어야 모델이 오프라인에서 본 세상과 운영에서 보는 세상이 덜 어긋납니다.

이 글에서 기억할 핵심은 하나입니다. **피처 스토어의 목적은 편의성이 아니라 학습-서빙 일관성입니다.** 다음 글에서는 지금까지의 조각들을 묶어 하나의 운영 가능한 ML 시스템으로 정리하겠습니다.

## 처음 질문으로 돌아가기

- **학습-서빙 불일치는 왜 자꾸 반복될까요?**
  - 본문의 기준은 피처 스토어를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **온라인 저장소와 오프라인 저장소는 어떤 역할 차이가 있을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **Feast에서 entity와 feature view는 어떻게 이해하면 좋을까요?**
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
- **피처 스토어 (현재 글)**
- 운영 가능한 ML 시스템 (예정)

<!-- toc:end -->

## 참고 자료

- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/mlops-101/ko)

- [Feast documentation](https://docs.feast.dev/)
- [Tecton — feature platforms](https://www.tecton.ai/blog/)
- [Uber — feature store](https://www.uber.com/blog/michelangelo-machine-learning-platform/)
- [Google Vertex AI Feature Store](https://cloud.google.com/vertex-ai/docs/featurestore)

Tags: MLOps, FeatureStore, Feast, DataScience, Pipeline
