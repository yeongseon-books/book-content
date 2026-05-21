---
series: mlops-101
episode: 3
title: "MLOps 101 (3/10): 데이터 버전 관리"
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
  - DVC
  - DataVersioning
  - Reproducibility
  - DataScience
seo_description: 데이터 포인터와 원격 저장소를 활용하여, 코드와 데이터를 한 세트로 관리하고 학습 결과를 완벽하게 재현하는 데이터 버전 관리 방법을 소개합니다.
last_reviewed: '2026-05-12'
---

# MLOps 101 (3/10): 데이터 버전 관리

코드는 git에 남기고 모델 파일도 따로 저장해 두는데, 정작 가장 큰 입력인 데이터는 어디에 있었는지 모르는 경우가 많습니다. 어제 잘 돌아가던 학습이 오늘은 다른 결과를 내는데 이유를 찾지 못하는 장면도 대부분 여기서 시작합니다.

같은 코드라도 데이터가 달라지면 다른 모델이 나옵니다. 그래서 데이터 버전 관리가 빠진 MLOps는 절반만 완성된 체계에 가깝습니다. 코드를 재현할 수 있어도 학습 결과를 재현할 수는 없기 때문입니다.

이 글은 MLOps 101 시리즈의 3번째 글입니다.

여기서는 데이터 버전 관리를 파일 백업이 아니라, 팀이 같은 입력을 같은 방식으로 다시 가져올 수 있게 만드는 재현성 계약으로 보겠습니다.

## 먼저 던지는 질문

- 왜 코드 버전만으로는 학습 결과를 재현할 수 없을까요?
- DVC와 git-LFS는 어떤 차이로 이해하면 좋을까요?
- 큰 데이터 파일은 git 바깥에 두면서도 어떻게 버전 일관성을 유지할 수 있을까요?

## 큰 그림

![MLOps 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/03/03-01-see-the-flow-first.ko.png)

*MLOps 101 3장 흐름 개요*

이 그림은 데이터가 모델만큼 중요한 입력이며, 데이터 변화가 모델 성능 변화를 얼마나 크게 좌우하는지를 보여줍니다. 학습 파이프라인을 재현하려면 데이터 버전도 함께 기록해야 합니다.

> 데이터 버전 관리가 없으면 메트릭이 높아진 이유를 설명할 수 없습니다. 모델 코드는 같아도 데이터 버전이 다르면 결과는 완전히 달라지기 때문입니다.

## 왜 중요한가

학습 파이프라인에서 가장 흔한 오해는 모델이 코드에서 나온다고 생각하는 것입니다. 실제로 모델은 코드와 데이터가 만난 결과입니다. 코드가 같아도 데이터가 바뀌면 결과는 달라지고, 데이터가 같아도 전처리 순서가 달라지면 다시 다른 결과가 나옵니다.

그래서 데이터 버전이 없으면 실험 추적도 반쪽이 됩니다. 메트릭이 높았던 이유를 설명할 수도 없고, 과거 모델을 다시 만들어 비교할 수도 없습니다.

### Feature Store 아키텍처

Feature Store는 데이터 버전 관리와 함께 가는 개념입니다. 오프라인 저장소와 온라인 저장소로 나눠 훈련과 서빙에서 같은 feature를 재사용합니다.

| 구분 | 저장소 | 지연시간 | 주요 용도 |
|---|---|---|---|
| 오프라인 스토어 | Parquet on S3, BigQuery, Snowflake | 분~시간 | 훈련 데이터 준비, 배치 feature 생성 |
| 온라인 스토어 | Redis, DynamoDB, Cassandra | ms~초 | 실시간 추론 요청 feature 제공 |

훈련할 때는 오프라인 스토어에서 큰 데이터를 단번에 가져오고, 서빙할 때는 온라인 스토어에서 필요한 가장 최신 feature만 빠르게 읽습니다.

### Feast 설정 예시

Feast는 오픈소스 Feature Store입니다. 데이터 버전 관리와 함께 쓰면 훈련과 서빙에서 feature 정의가 일치하게 됩니다.

```yaml
# feature_repo/feature_store.yaml
project: mlops_demo
registry: data/registry.db
provider: local
online_store:
  type: redis
  connection_string: "localhost:6379"
offline_store:
  type: file
```

Feature 정의 파일:

```python
# feature_repo/features.py
from feast import Entity, FeatureView, Field, FileSource
from feast.types import Float32, Int64
from datetime import timedelta

user = Entity(name="user_id", join_keys=["user_id"])

user_features_source = FileSource(
    path="data/user_features.parquet",
    timestamp_field="event_timestamp",
)

user_features = FeatureView(
    name="user_features",
    entities=[user],
    ttl=timedelta(days=1),
    schema=[
        Field(name="age", dtype=Int64),
        Field(name="score", dtype=Float32),
    ],
    source=user_features_source,
)
```

이 설정을 적용하려면 `feast apply`를 실행합니다. 그러면 레지스트리에 feature 정의가 등록되고, 훈련과 서빙 코드에서 같은 이름으로 feature를 불러올 수 있습니다.

### Feature 버전 관리

Feature 정의도 코드와 같이 버전 관리가 필요합니다. Feature 계산 로직이 바뀌면 모델 결과도 달라지기 때문입니다.

#### Feature 이름에 버전 포함

Feature 이름 자체에 버전을 넣으면 변경 이력이 남습니다.

```python
# 초기 버전
user_age_v1 = Entity(name="user_age_v1", ...)

# 계산 로직 변경 후
user_age_v2 = Entity(name="user_age_v2", ...)
```

#### Git으로 feature 정의 추적

Feature 정의 파일을 git에 커밋하면 코드 버전과 feature 버전을 함께 관리할 수 있습니다.

```bash
git add feature_repo/features.py
git commit -m "Add user_age_v2 feature definition"
```

### 훈련-서빙 스큐 방지

훈련에서는 한 가지 feature를 쓰는데 서빙에서는 다른 feature를 쓰면 모델 성능이 크게 떨어집니다. 이것을 training-serving skew라고 부릅니다.

#### 발생 원인

1. 훈련 코드에서 pandas로 feature를 만들고, 서빙 코드에서 SQL로 다시 만듭니다. 로직이 조금만 달라도 결과가 달라집니다.
2. 훈련은 batch feature를 쓰는데, 서빙은 실시간 feature를 쓰고 로직이 훈련과 다릅니다.
3. Feature 버전이 훈련과 서빙에서 달라서 훈련은 v1을 쓰는데 서빙은 v2를 쓰게 됩니다.

#### 방지 방법

1. **Feature Store 사용**: 훈련과 서빙이 같은 feature 정의를 참조합니다.
2. **Feature 테스트 작성**: 훈련 feature와 서빙 feature를 같은 입력으로 비교하는 테스트를 만듭니다.
3. **버전 명시**: Feature 이름에 버전을 포함하고, 모델은 특정 feature 버전을 기록합니다.

```python
# 훈련
features_train = feast_store.get_historical_features(
    entity_df=train_entities,
    features=["user_features:age", "user_features:score"],
)

# 서빙
features_online = feast_store.get_online_features(
    entity_rows=[{"user_id": 123}],
    features=["user_features:age", "user_features:score"],
)
```

Feature Store를 쓰면 같은 feature 이름이 훈련과 서빙에서 자동으로 일치하고, skew 발생 가능성이 크게 줄어듭니다.
---

## 전체 흐름을 먼저 보겠습니다

이 구조를 이해하면 왜 DVC 같은 도구가 필요한지 감이 옵니다. git 저장소에는 실제 대용량 파일이 아니라 포인터 파일이 들어가고, 실제 데이터는 원격 저장소에 둡니다. 파이프라인은 포인터를 읽어 정확한 데이터 상태를 다시 가져옵니다.

포인터와 원격 저장소는 함께 움직여야 합니다. 둘 중 하나만 있으면 재현성이 깨집니다.

---

## 먼저 잡아야 할 핵심 개념

- **DVC**: git 위에서 데이터와 모델 버전을 추적하도록 돕는 도구입니다.
- **포인터 파일**: 해시와 메타데이터를 담아 실제 데이터 상태를 식별합니다.
- **원격 저장소**: S3, GCS, SSH, 로컬 디렉터리처럼 실제 파일이 놓이는 장소입니다.
- **단계(stage)**: 입력, 명령, 출력이 정의된 파이프라인 단위입니다.
- **재현 실행(repro)**: 입력이 달라진 단계만 다시 실행하는 방식입니다.

이 개념을 정확히 잡아 두면, 데이터 버전 관리를 단순 백업이나 파일 복사와 구분할 수 있습니다.

---

## 도입 전과 도입 후를 비교해 보겠습니다

**Before**: `data_v3_final.csv`가 특정 팀원 노트북에만 있습니다.

**After**: `git pull && dvc pull`만으로 어디서나 같은 데이터셋을 다시 가져옵니다.

이 차이는 생각보다 큽니다. Before 상태에서는 데이터 전달이 협업 병목이 되고, 작은 수정도 메신저와 수동 복사에 의존합니다. After 상태에서는 데이터가 팀 공용 자산이 됩니다.

---

## 작은 예제로 DVC 감각을 따라가 보겠습니다

### 1단계 — 샘플 데이터를 만듭니다

```python
import pandas as pd
df = pd.DataFrame({"x": range(100), "y": [i % 2 for i in range(100)]})
df.to_csv("data.csv", index=False)
```

여기서는 아주 작은 CSV를 만듭니다. 실제 현업 데이터는 훨씬 크겠지만, 버전 관리 원리는 같습니다. 중요한 것은 파일 크기가 아니라 상태를 식별할 수 있어야 한다는 점입니다.

### 2단계 — DVC 초기화를 가정합니다

```bash
# pip install dvc
# git init && dvc init
# dvc add data.csv
# git add data.csv.dvc .gitignore
# git commit -m "track data v1"
```

이 단계가 말해 주는 것은 명확합니다. 실제 데이터 파일은 DVC가 관리하고, git에는 포인터와 관련 설정만 남깁니다. 즉, 코드 저장소를 무겁게 만들지 않으면서도 데이터 상태를 버전으로 묶을 수 있습니다.

### 3단계 — 포인터 파일을 흉내 냅니다

```python
import hashlib, json
h = hashlib.md5(open("data.csv", "rb").read()).hexdigest()
pointer = {"path": "data.csv", "md5": h}
with open("data.csv.ptr", "w") as f:
    json.dump(pointer, f, indent=2)
print(pointer)
```

포인터 파일은 데이터를 직접 들고 있지 않지만, 어떤 데이터인지 정확히 가리킵니다. 이 해시가 바뀌면 입력이 달라졌다는 뜻이고, 그 신호는 이후 재학습이나 재현 실행의 기준이 됩니다.

### 4단계 — 파이프라인 단계를 실행합니다

```python
from sklearn.linear_model import LogisticRegression
import pickle
df = pd.read_csv("data.csv")
m = LogisticRegression().fit(df[["x"]], df["y"])
with open("model.pkl", "wb") as f:
    pickle.dump(m, f)
```

데이터 버전 관리는 결국 파이프라인과 연결되어야 의미가 있습니다. 데이터 입력이 바뀌었을 때 어떤 단계가 다시 실행되어야 하는지 알아야 운영 자동화로 이어집니다.

### 5단계 — 입력 변경 신호를 확인합니다

```python
df.loc[0, "y"] = 1 - df.loc[0, "y"]
df.to_csv("data.csv", index=False)
new_h = hashlib.md5(open("data.csv", "rb").read()).hexdigest()
print("changed:", new_h != h)
```

이 예제는 왜 해시가 중요한지 바로 보여 줍니다. 파일 이름이 같아도 내용이 달라졌다는 사실을 시스템이 감지할 수 있어야 합니다. 데이터 버전 관리의 핵심은 사람이 아니라 파이프라인이 이 변화를 읽게 만드는 데 있습니다.

---

## 이 코드에서 먼저 봐야 할 점

- 해시 변경은 재학습과 재현 실행의 출발 신호입니다.
- git에는 실제 데이터가 아니라 포인터 파일만 들어갑니다.
- 단계는 입력, 명령, 출력의 조합으로 이해해야 합니다.
- 데이터와 모델 버전은 함께 남아야 비교가 가능합니다.

이 네 가지를 놓치면 데이터 버전 관리는 단순 저장소 관리로 축소됩니다. 하지만 실제 목표는 저장이 아니라 재현입니다.

---

## 자주 헷갈리는 지점

1. **대용량 데이터를 git에 직접 커밋합니다.**
   저장소가 무거워질 뿐 아니라 협업도 금세 불편해집니다.
2. **원격 저장소를 설정하지 않습니다.**
   동료는 포인터 파일만 받고 실제 데이터는 받지 못합니다.
3. **데이터를 바꾸고도 버전 변경을 남기지 않습니다.**
   학습 결과 차이를 나중에 설명할 수 없습니다.
4. **단계의 입력과 출력을 선언하지 않습니다.**
   어떤 단계를 다시 돌려야 하는지 시스템이 알 수 없습니다.
5. **데이터만 추적하고 모델은 별도로 굴립니다.**
   데이터-모델 연결 고리가 약해집니다.

---

## 실무에서는 이렇게 봅니다

비전 데이터셋, 대형 텍스트 코퍼스, 로그 기반 추천 데이터처럼 파일 크기가 빠르게 커지는 영역에서는 DVC와 객체 저장소 조합이 흔합니다. 작은 테스트 샘플은 git에 남기더라도, 실제 학습 입력은 별도 원격 저장소에 두고 포인터로 연결하는 편이 안정적입니다.

시니어 엔지니어는 데이터 버전 관리를 모델 운영의 선행 조건으로 봅니다. 코드는 git, 데이터와 모델은 DVC 같은 계층, 그리고 파이프라인은 입력 해시를 기준으로 다시 도는 구조가 기본입니다.

---

## 체크리스트

- [ ] 데이터 파일을 DVC나 LFS로 추적한다.
- [ ] 원격 저장소가 설정되어 있다.
- [ ] 모델 버전도 함께 추적한다.
- [ ] 재현 명령이나 절차가 문서화되어 있다.

## 연습 문제

1. 작은 CSV 파일 하나를 DVC로 추적해 보세요.
2. 데이터를 바꾼 뒤 해시가 어떻게 달라지는지 확인해 보세요.
3. 로컬 디렉터리로 원격 저장소를 흉내 내 보는 실습을 해 보세요.

## 정리

데이터 버전 관리는 재현성의 전제입니다. 같은 코드를 남기는 것만으로는 충분하지 않고, 같은 데이터를 다시 가져올 수 있어야 같은 모델을 다시 만들 수 있습니다.

이 글에서 기억할 핵심은 하나입니다. **ML 시스템에서 데이터는 입력 파일이 아니라 버전이 붙은 운영 자산입니다.** 다음 글에서는 그 자산을 반복 가능한 단계로 묶는 학습 파이프라인을 다루겠습니다.


## DVC 워크플로를 운영 관점으로 정리하기

데이터 버전 관리는 명령어를 아는 것보다 흐름을 이해하는 편이 중요합니다. 아래는 가장 보편적인 DVC 운영 흐름입니다.

1. 원천 데이터나 전처리 결과를 `dvc add`로 추적합니다.
2. 생성된 `.dvc` 파일과 파이프라인 정의를 git에 커밋합니다.
3. 실제 데이터 파일은 `dvc push`로 원격 저장소에 업로드합니다.
4. 다른 환경에서는 `git pull` 후 `dvc pull`로 동일 상태를 복원합니다.
5. 데이터가 변경되면 동일 절차를 반복해 새 버전을 남깁니다.

이 구조의 장점은 협업자가 "같은 코드 + 같은 데이터" 상태를 기계적으로 복원할 수 있다는 점입니다.

## 자주 쓰는 DVC 명령어 모음

```bash
# 초기 설정
pip install dvc[s3]
dvc init
dvc remote add -d storage s3://my-bucket/mlops-demo

# 데이터 추적
dvc add data/raw/train.parquet
git add data/raw/train.parquet.dvc .gitignore
git commit -m "Track raw training dataset"

# 원격 동기화
dvc push

# 다른 환경 복원
git pull
dvc pull

# 버전 조회
git log -- data/raw/train.parquet.dvc
```

명령 자체는 단순하지만, 실제 팀 운영에서 중요한 것은 커밋 메시지 규약과 데이터 변경 사유를 남기는 습관입니다.

## `.dvc` 파일 구조 읽기

일반적으로 `.dvc` 파일은 아래와 비슷합니다.

```yaml
outs:
  - md5: 3f7dd2b9c8a8f6a9e33f0d6b14f7d22a
    size: 128947221
    path: data/raw/train.parquet
```

- `md5`: 파일 내용을 식별하는 해시입니다.
- `size`: 파일 크기입니다.
- `path`: 작업 디렉터리 기준 경로입니다.

핵심은 이 파일이 데이터 자체가 아니라 "데이터 상태를 가리키는 포인터"라는 점입니다.

## 파이프라인 정의와 결합하기

데이터 버전 관리는 학습 파이프라인과 연결될 때 가치가 커집니다.

```yaml
stages:
  preprocess:
    cmd: python src/preprocess.py --input data/raw/train.parquet --output data/processed/train.parquet
    deps:
      - src/preprocess.py
      - data/raw/train.parquet
    outs:
      - data/processed/train.parquet

  train:
    cmd: python src/train.py --data data/processed/train.parquet --model artifacts/model.pkl
    deps:
      - src/train.py
      - data/processed/train.parquet
    outs:
      - artifacts/model.pkl
```

이렇게 `deps`와 `outs`를 명시하면 입력 변경 시 필요한 단계만 다시 실행할 수 있어 비용과 시간을 크게 줄일 수 있습니다.

## 운영 정책 제안

| 항목 | 권장 정책 |
|---|---|
| 원천 데이터 보존 | 최소 90일 이상 버전 보존 |
| 재현 보장 | 배포 모델은 학습 당시 데이터 해시를 필수 기록 |
| 접근 제어 | 원격 저장소 권한을 읽기/쓰기 분리 |
| 감사 추적 | 모델 승격 시 데이터 버전 링크 필수 |

데이터 버전 관리는 스토리지 관리가 아니라 모델 책임 추적 체계입니다. 이 연결이 있어야 품질 문제 발생 시 원인을 좁힐 수 있습니다.

## 데이터 리니지 추적 표

데이터 버전 관리는 변경 이력 보존에서 끝나지 않고, 어떤 데이터가 어떤 모델 버전으로 이어졌는지 추적 가능해야 완성됩니다.

| 단계 | 추적 항목 | 기록 예시 | 운영 목적 |
|---|---|---|---|
| Ingest | 원천 파일 경로, 수집 시각 | `s3://raw/2026-05-12/events.parquet` | 수집 누락/지연 원인 파악 |
| Validate | 스키마 버전, 품질 점수 | `schema=v3, null_rate=0.7%` | 이상 입력 조기 차단 |
| Train | 데이터 해시, 모델 버전 | `md5=...`, `model=v42` | 학습 재현성 보장 |
| Deploy | 승격 모델, 기준 데이터 링크 | `champion=v42, data=v18` | 배포 근거 감사 추적 |

리니지 표를 문서와 레지스트리에 함께 남기면, 성능 저하가 생겼을 때 모델 코드와 데이터 경로를 동시에 역추적할 수 있습니다.

## 처음 질문으로 돌아가기

- **왜 코드 버전만으로는 학습 결과를 재현할 수 없을까요?**
  - 본문의 기준은 데이터 버전 관리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **DVC와 git-LFS는 어떤 차이로 이해하면 좋을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **큰 데이터 파일은 git 바깥에 두면서도 어떻게 버전 일관성을 유지할 수 있을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [MLOps 101 (1/10): MLOps란 무엇인가?](./01-what-is-mlops.md)
- [MLOps 101 (2/10): 실험 관리](./02-experiment-tracking.md)
- **데이터 버전 관리 (현재 글)**
- 모델 학습 파이프라인 (예정)
- 모델 배포 (예정)
- 모델 모니터링 (예정)
- 데이터 드리프트와 모델 드리프트 (예정)
- 재학습 (예정)
- 피처 스토어 (예정)
- 운영 가능한 ML 시스템 (예정)

<!-- toc:end -->

## 참고 자료

- [DVC — Get Started](https://dvc.org/doc/start)
- [git-LFS](https://git-lfs.com/)
- [Pachyderm](https://www.pachyderm.com/)
- [Google — Data versioning](https://cloud.google.com/architecture/ml-on-gcp-best-practices)

Tags: MLOps, DVC, DataVersioning, Reproducibility, DataScience
