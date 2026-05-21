---
series: mlops-101
episode: 2
title: "MLOps 101 (2/10): 실험 관리"
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
  - ExperimentTracking
  - MLflow
  - Reproducibility
  - DataScience
seo_description: 실험 메타데이터를 기록하여 학습 과정을 재현 가능한 상태로 만들고, 팀 단위의 모델 비교와 의사결정 효율을 높이는 실험 관리 방법을 소개합니다.
last_reviewed: '2026-05-12'
---

# MLOps 101 (2/10): 실험 관리

모델을 여러 번 학습하다 보면 어느 순간부터 기억이 먼저 무너집니다. 지난주에 가장 잘 나온 조합이 무엇이었는지, 그때 데이터 버전이 무엇이었는지, 왜 이번 결과가 달라졌는지 노트북 파일명만으로는 설명이 안 됩니다.

팀 단위로 작업할 때는 더 심각해집니다. 누군가는 `final_v2_really.pkl`을 남기고, 누군가는 메트릭을 슬랙에만 적어 두고, 누군가는 실패한 실험을 아예 기록하지 않습니다. 이 상태에서는 모델 개선보다 과거 복원이 더 어려운 일이 됩니다.

이 글은 MLOps 101 시리즈의 2번째 글입니다.

여기서는 실험 관리를 팀의 단기 기억 장치로 보고, 어떤 정보를 어떻게 남겨야 재현과 비교가 가능해지는지 정리하겠습니다.


![MLOps 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/mlops-101/02/02-01-see-the-flow-first.ko.png)
*MLOps 101 2장 흐름 개요*
> 실험 관리의 핵심은 모든 run을 저장하는 것이 아니라, 같은 축에서 여러 run을 비교할 수 있게 메타데이터를 일관되게 남기는 일입니다. 실패한 실험도 자산입니다.

## 먼저 던지는 질문

- 실험 관리가 없으면 왜 같은 모델도 다시 만들기 어려울까요?
- 파라미터, 메트릭, 아티팩트, 환경 중 무엇을 반드시 남겨야 할까요?
- MLflow에서 experiment와 run은 어떤 관계로 이해하면 좋을까요?

## 왜 중요한가

실험 관리가 없으면 학습은 계속되는데 지식은 쌓이지 않습니다. 이번 주에 나온 최고 성능이 우연인지, 데이터 변화 덕분인지, 하이퍼파라미터 덕분인지 분리할 수 없기 때문입니다. 결국 모델 개선이 아니라 추측과 기억력 경쟁이 됩니다.

반대로 모든 run을 기록하면 모델 품질뿐 아니라 작업 과정도 자산이 됩니다. 실패한 실험이 남아 있으면 같은 실수를 반복하지 않고, 성공한 실험이 남아 있으면 승격 후보를 더 빨리 가를 수 있습니다.

### 실험 추적 도구 비교

많은 도구가 있지만 핵심 기능과 제약 사항은 비슷합니다. 다음 표는 대표 도구들의 특징과 무료 한도를 비교한 것입니다.

| 도구 | 무료 한도 | 특징 | 세팅 복잡도 |
|---|---|---|---|
| MLflow | 무제한 (셀프 호스팅) | 오픈소스, 로컬/원격 모두 가능, 모델 레지스트리 통합 | 낮음 |
| W&B (Weights & Biases) | 개인 프로젝트 무료, 팀은 유료 | UI 우수, 협업 기능 강력, Sweep 내장 | 낮음 |
| Neptune | 200시간 트래킹 무료 | 모델 비교 UI 우수, 긴 실험 기록 보관 | 보통 |
| Comet ML | 5000 run 무료 | 대시보드 커스터마이징, 실험 diff 기능 | 보통 |

처음 시작하는 팀에게는 MLflow를 권합니다. 설치가 간단하고, 로컬에서도 바로 쓸 수 있으며, 나중에 원격 서버로 확장하기도 쉽습니다.

### MLflow 코드 예제 — 완전한 흐름

위 예제를 조금 더 확장해서 보겠습니다. 데이터 버전을 param으로 남기고, 메트릭을 여러 번 기록하고, 아티팩트로 모델과 그래프를 함께 남기는 예제입니다.

```python
import mlflow
import hashlib
import json
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
import pickle
import matplotlib.pyplot as plt

mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("demo-full")

# 데이터 버전 계산
X, y = make_classification(n_samples=1000, random_state=42)
data_repr = json.dumps({"n": len(X), "seed": 42})
data_version = hashlib.sha1(data_repr.encode()).hexdigest()[:8]

X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=0)

with mlflow.start_run():
    # 1. 파라미터 기록
    C = 1.0
    max_iter = 1000
    mlflow.log_param("C", C)
    mlflow.log_param("max_iter", max_iter)
    mlflow.log_param("data_version", data_version)

    # 2. 학습
    model = LogisticRegression(C=C, max_iter=max_iter, random_state=0).fit(X_train, y_train)

    # 3. 메트릭 기록
    train_acc = model.score(X_train, y_train)
    val_acc = model.score(X_val, y_val)
    mlflow.log_metric("train_acc", train_acc)
    mlflow.log_metric("val_acc", val_acc)

    # 4. 모델 아티팩트
    with open("model.pkl", "wb") as f:
        pickle.dump(model, f)
    mlflow.log_artifact("model.pkl")

    # 5. 시각화 아티팩트
    fig, ax = plt.subplots()
    ax.bar(["train", "val"], [train_acc, val_acc])
    ax.set_ylim(0, 1)
    ax.set_title("Accuracy")
    fig.savefig("acc.png")
    mlflow.log_artifact("acc.png")
    plt.close()

    print(f"Run completed. train={train_acc:.3f}, val={val_acc:.3f}")
```

이 코드에서 중요한 점은 데이터 버전, 파라미터, 모델, 메트릭, 시각화가 모두 하나의 run 안에 묶여 있다는 점입니다. 나중에 이 run을 열면 모든 결과를 함께 볼 수 있습니다.

### 실험 명명 규칙

실험이 쌓이면 이름만으로도 의도를 파악할 수 있어야 합니다. 다음은 팀 단위로 쓸 수 있는 표준 명명 규칙 예시입니다.

#### Experiment 이름 규칙

- `<project>-<task>` 형식 사용: `fraud-detection-baseline`, `recommendation-v2`
- 별도 브랜치나 티켓 번호 추가 가능: `fraud-detection-TICKET-123`

#### Run 명명 패턴

MLflow는 run ID를 자동 생성하지만 `mlflow.set_tag("mlflow.runName", ...)`로 이름을 명시할 수도 있습니다.

```python
with mlflow.start_run():
    mlflow.set_tag("mlflow.runName", "C=1.0-seed=42-v1")
    # ...
```

#### Tag 활용

실험 의도, 담당자, 버전을 tag로 남기면 후에 필터링이 쉽습니다.

```python
mlflow.set_tag("purpose", "hyperparameter-search")
mlflow.set_tag("owner", "data-science-team")
mlflow.set_tag("model_type", "logistic-regression")
```

표준 규칙이 있으면 팀원이 각자의 방식으로 run을 만들더라도 공통 축에서 비교할 수 있습니다.
---

## 전체 흐름을 먼저 보겠습니다

이 흐름은 실험 관리의 본질을 잘 보여 줍니다. 코드와 파라미터, 데이터 버전이 하나의 run으로 묶이고, 그 run에서 메트릭과 아티팩트와 태그가 나옵니다. 그 결과를 여러 run과 비교할 수 있어야 비로소 실험 관리가 됩니다.

즉, 실험 관리의 핵심은 저장 자체가 아니라 비교 가능성입니다. run이 많아지는 것은 자연스러운 일이고, 중요한 것은 그 run들을 같은 축에서 읽을 수 있는가입니다.

---

## 먼저 잡아야 할 핵심 개념

- **Experiment**: 관련 run들을 모아 두는 논리적 상자입니다.
- **Run**: 학습 한 번의 실행 단위입니다.
- **Param**: 학습 전에 정해지는 입력 값입니다.
- **Metric**: 실행 뒤 측정된 결과 값입니다.
- **Artifact**: 모델 파일, 그래프, 로그처럼 파일 형태로 남는 결과물입니다.

실무에서는 이 다섯 개를 얼마나 일관되게 쓰느냐가 더 중요합니다. 같은 의미의 메트릭을 팀원이 제각각 다른 이름으로 남기면 비교 화면이 금세 쓸모없어집니다.

---

## 도입 전과 도입 후를 비교해 보겠습니다

**Before**: `v3_final2.pkl` 같은 파일명이 사실상 기록 시스템을 대신합니다.

**After**: run 목록이 남고, MLflow 화면이나 API로 파라미터와 메트릭을 나란히 비교할 수 있습니다.

Before 상태에서는 최고 성능 모델을 다시 찾는 데도 사람 기억이 필요합니다. After 상태에서는 실패한 run까지 포함해 전체 탐색 과정을 읽을 수 있습니다.

---

## MLflow로 아주 작은 추적기를 만들어 보겠습니다

### 1단계 — 트래커를 준비합니다

```python
# 핍 설치 mlflow
import mlflow
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("demo")
```

이 단계는 기록을 어디에 남길지 정하는 과정입니다. 처음에는 로컬 파일 기반으로도 시작할 수 있지만, 팀이 함께 쓰기 시작하면 원격 서버가 필요해집니다.

### 2단계 — run 하나를 기록합니다

```python
from sklearn.datasets import make_classification
from sklearn.linear_model import LogisticRegression
X, y = make_classification(n_samples=500, random_state=0)

with mlflow.start_run():
    C = 1.0
    mlflow.log_param("C", C)
    m = LogisticRegression(C=C, max_iter=1000).fit(X, y)
    mlflow.log_metric("acc", m.score(X, y))
```

`with` 블록 하나가 run 경계입니다. 어떤 파라미터로 시작했고 어떤 메트릭으로 끝났는지를 이 블록 안에서 모읍니다. 실험 관리에서 가장 중요한 감각 중 하나가 바로 이 경계를 명시적으로 나누는 일입니다.

### 3단계 — 모델 아티팩트를 남깁니다

```python
import pickle, os
os.makedirs("art", exist_ok=True)
with mlflow.start_run():
    m = LogisticRegression().fit(X, y)
    with open("art/model.pkl", "wb") as f:
        pickle.dump(m, f)
    mlflow.log_artifact("art/model.pkl")
```

메트릭만 있으면 결과를 비교할 수는 있어도, 실제 산출물을 다시 가져오기는 어렵습니다. 모델 파일이나 시각화 결과까지 함께 남겨야 run이 운영 자산으로 이어집니다.

### 4단계 — 파라미터를 바꿔 여러 run을 만듭니다

```python
for C in [0.1, 1.0, 10.0]:
    with mlflow.start_run():
        mlflow.log_param("C", C)
        m = LogisticRegression(C=C, max_iter=1000).fit(X, y)
        mlflow.log_metric("acc", m.score(X, y))
```

이제 run이 여러 개 생깁니다. 실험 관리가 힘을 발휘하는 순간이 바로 여기입니다. 단일 run 저장은 로그일 뿐이고, 여러 run을 같은 기준으로 비교할 수 있어야 추적기가 됩니다.

### 5단계 — API로 비교합니다

```python
client = mlflow.tracking.MlflowClient()
exp = client.get_experiment_by_name("demo")
runs = client.search_runs(exp.experiment_id, order_by=["metrics.acc DESC"])
for r in runs[:3]:
    print(r.data.params, r.data.metrics)
```

실험 관리 도구를 쓰는 이유는 결국 비교를 자동화하기 위해서입니다. 상위 run을 바로 정렬해서 볼 수 있으면, 모델 선택 과정이 개인 감각이 아니라 공통 절차로 바뀝니다.

---

## 이 코드에서 먼저 봐야 할 점

- `with` 블록이 run의 경계를 만듭니다.
- param과 metric은 같은 이름 규칙으로 쌓여야 비교가 쉬워집니다.
- artifact는 파일 그대로 보존되므로 결과 재사용에 유리합니다.
- API 비교가 가능해져야 실험 선택이 수작업에서 벗어납니다.

실험 관리의 품질은 도구 선택보다 기록 규약에 더 크게 좌우됩니다. 팀마다 키 이름이 다르고, 일부 run만 남기고, 데이터 버전을 빼먹는 순간 기록은 있어도 비교는 불가능해집니다.

---

## 자주 헷갈리는 지점

1. **성공한 run만 남깁니다.**
   실패한 실험이 빠지면 탐색 과정이 사라지고 같은 실수를 반복합니다.
2. **데이터 버전을 기록하지 않습니다.**
   메트릭만 높아도 무엇이 바뀌었는지 알 수 없습니다.
3. **파라미터와 메트릭 이름을 제각각 씁니다.**
   비교 화면이 금세 읽기 어려워집니다.
4. **로컬 `mlruns`만 쓰고 공유 서버를 두지 않습니다.**
   팀의 기억이 개인 노트북에 갇힙니다.
5. **비교 규칙 없이 사람이 임의로 우승 모델을 고릅니다.**
   재현 가능한 승격 기준이 생기지 않습니다.

---

## 실무에서는 이렇게 봅니다

하이퍼파라미터 스윕, 주간 모델 리뷰, 챌린저 비교 같은 작업은 모두 실험 관리 체계 위에서 돌아갑니다. MLflow나 W&B 같은 도구는 단순히 로그를 저장하는 것이 아니라, 팀이 같은 run 테이블을 보며 의사결정하게 만드는 기반입니다.

시니어 엔지니어는 run 자체보다 run 메타데이터의 일관성을 먼저 봅니다. 데이터 버전을 param처럼 다루는지, 메트릭 키가 표준화되어 있는지, 실패한 run도 남기는지, 로컬이 아니라 공유 추적 서버를 기본값으로 두는지를 확인합니다.

---

## 체크리스트

- [ ] 모든 학습 실행이 run으로 기록된다.
- [ ] 데이터 버전과 코드 정보가 함께 남는다.
- [ ] 공유 추적 서버를 사용한다.
- [ ] 비교 화면이나 API를 기준으로 모델을 선택한다.

## 연습 문제

1. 파라미터 세 조합을 돌리고 상위 run을 출력해 보세요.
2. 데이터 해시를 param으로 추가해 보세요.
3. run tag를 사용해 실험 의도를 구분해 보세요.

## 정리

실험 관리는 팀의 단기 기억입니다. 모델을 계속 바꾸는 조직이라면, 무엇을 시도했고 무엇이 잘됐고 무엇이 실패했는지를 구조적으로 남겨야 합니다.

이 글에서 기억할 핵심은 하나입니다. **실험 추적이 있어야 모델 개선이 개인 기억이 아니라 팀 자산이 됩니다.** 다음 글에서는 그 기억을 더 오래 보존하는 데이터 버전 관리를 다루겠습니다.


## MLflow Tracking 실무 패턴

실험 추적은 "기록한다"에서 끝나지 않고 "비교한다"까지 가야 합니다. 이를 위해서는 기록 키 이름과 실험 범위를 먼저 표준화해야 합니다.

### 권장 기록 스키마

| 구분 | 필수 키 예시 | 목적 |
|---|---|---|
| Param | `model_type`, `learning_rate`, `seed`, `data_version` | 입력 조건 고정 |
| Metric | `val_auc`, `val_f1`, `train_time_sec` | 성능과 비용 비교 |
| Tag | `owner`, `ticket`, `purpose` | 조직 문맥 연결 |
| Artifact | `model.pkl`, `confusion_matrix.png`, `feature_importance.csv` | 결과 재사용 |

키를 표준화하면 다음 분기부터 큰 차이가 납니다. 팀원이 바뀌어도 같은 실험 테이블을 읽을 수 있고, 모델 리뷰가 "감각"이 아니라 "증거" 중심으로 바뀝니다.

### 실험 비교 코드 예시

```python
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient(tracking_uri="file:./mlruns")
exp = client.get_experiment_by_name("demo-full")
runs = client.search_runs(
    experiment_ids=[exp.experiment_id],
    order_by=["metrics.val_auc DESC"],
)

print("top runs")
for r in runs[:5]:
    print({
        "run_id": r.info.run_id,
        "val_auc": r.data.metrics.get("val_auc"),
        "lr": r.data.params.get("learning_rate"),
        "data": r.data.params.get("data_version"),
    })
```

이런 비교 코드가 있어야 회고 회의에서 "어떤 실험이 왜 이겼는가"를 빠르게 설명할 수 있습니다.

## 실험 비교 테이블 템플릿

아래 형식으로 주간 모델 리뷰를 운영하면 승격 판단이 훨씬 명확해집니다.

| run_id | data_version | val_auc | val_f1 | train_time_sec | 승격 후보 |
|---|---|---:|---:|---:|---|
| a1b2c3 | 2026-05-10 | 0.861 | 0.742 | 388 | 후보 |
| d4e5f6 | 2026-05-10 | 0.854 | 0.739 | 220 | 보류 |
| g7h8i9 | 2026-05-03 | 0.847 | 0.733 | 190 | 탈락 |

점수만 높은 모델이 아니라 학습 비용, 데이터 시점, 안정성까지 함께 보아야 실제 운영에서 후회가 줄어듭니다.

## 재현 가능한 실험 실행 래퍼

```python
import os
import subprocess
import mlflow

def run_experiment(cfg_path: str, data_version: str) -> None:
    mlflow.set_experiment("fraud-lr")
    with mlflow.start_run():
        mlflow.log_param("config", cfg_path)
        mlflow.log_param("data_version", data_version)
        mlflow.log_param("git_sha", os.getenv("GIT_SHA", "unknown"))

        subprocess.run(["python", "train.py", "--config", cfg_path], check=True)
        subprocess.run(["python", "evaluate.py", "--output", "metrics.json"], check=True)

        mlflow.log_artifact("metrics.json")
        mlflow.log_artifact("model.pkl")
```

이 래퍼의 목적은 학습 스크립트를 복잡하게 만드는 것이 아닙니다. 실험 실행 경계에 메타데이터를 강제로 남기게 해서 재현 누락을 줄이는 데 있습니다.

## 운영 규약 제안

- 실패한 run도 삭제하지 않습니다.
- `data_version`과 `git_sha`가 없는 run은 승격 후보에서 제외합니다.
- 승격 심사에는 최근 3회 실행의 분산값을 포함합니다.
- 실험 리뷰 주기를 정해 모델 선택 과정을 문서화합니다.

이 규약이 있으면 실험 추적이 단순 로그 저장소에서 운영 의사결정 시스템으로 바뀝니다.


## MLflow 자동 로깅과 중첩 실행

수동으로 `log_param`, `log_metric`을 호출하는 방식은 정확하지만, 매 실험마다 반복 코드가 늘어납니다. MLflow는 `autolog`를 제공해 이 부담을 줄입니다.

### autolog 사용법

```python
import mlflow
mlflow.autolog()

from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split

X, y = make_classification(n_samples=2000, n_features=20, random_state=42)
X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2)

with mlflow.start_run():
    clf = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=0)
    clf.fit(X_train, y_train)
    # autolog가 파라미터, 메트릭, 모델을 자동 기록합니다
```

`autolog`를 켜면 `fit()` 호출 시점에 하이퍼파라미터, 학습 메트릭, 모델 아티팩트가 한꺼번에 기록됩니다. 그러나 데이터 버전이나 팀 태그는 자동으로 남지 않으므로, 이 부분은 여전히 수동으로 추가해야 합니다.

### 중첩 실행으로 하이퍼파라미터 스윕 구조화

하이퍼파라미터 탐색을 할 때, 모든 run을 동일 레벨에 두면 나중에 "이 run이 어떤 스윕에서 나왔는지" 구분하기 어렵습니다. 중첩 실행(nested run)을 사용하면 부모-자식 관계로 구조화할 수 있습니다.

```python
import mlflow
from sklearn.linear_model import LogisticRegression
from sklearn.datasets import make_classification

X, y = make_classification(n_samples=1000, random_state=42)

with mlflow.start_run(run_name="sweep-2026-05-12"):
    mlflow.set_tag("sweep_type", "grid")
    mlflow.set_tag("owner", "ml-team")

    for C in [0.01, 0.1, 1.0, 10.0]:
        for solver in ["lbfgs", "liblinear"]:
            with mlflow.start_run(run_name=f"C={C}-{solver}", nested=True):
                mlflow.log_param("C", C)
                mlflow.log_param("solver", solver)
                m = LogisticRegression(C=C, solver=solver, max_iter=1000).fit(X, y)
                mlflow.log_metric("acc", m.score(X, y))
```

부모 run은 스윕 메타데이터(날짜, 목적, 담당자)를 담고, 자식 run은 개별 조합 결과를 담습니다. 이 구조가 있으면 스윕 단위 비교와 개별 run 비교를 모두 쉽게 할 수 있습니다.

### 원격 추적 서버 구성

로컬 `mlruns` 디렉터리는 빠르게 시작할 수 있지만, 팀 공유에는 적합하지 않습니다. 원격 서버를 두면 모든 팀원이 같은 실험 테이블을 봅니다.

```bash
# 추적 서버 시작 (PostgreSQL 백엔드)
mlflow server \
    --backend-store-uri postgresql://user:pass@db:5432/mlflow \
    --default-artifact-root s3://mlflow-artifacts/ \
    --host 0.0.0.0 \
    --port 5000
```

```python
# 클라이언트 코드에서 원격 서버 지정
import mlflow
mlflow.set_tracking_uri("http://mlflow-server:5000")
```

원격 서버를 기본값으로 두면 "개인 노트북에만 실험이 남는" 문제가 사라집니다. 백엔드를 PostgreSQL 같은 RDBMS로 두면 검색과 필터링 성능도 올라갑니다.

### 실험 관리 운영 정책 확장

| 항목 | 권장 정책 | 위반 시 영향 |
|---|---|---|
| 키 이름 표준 | 팀 위키에 정의, PR 리뷰 시 확인 | 비교 화면 무의미화 |
| 데이터 버전 필수 | `data_version` param 없으면 CI 실패 | 재현 불가 |
| 실패 run 보존 | 삭제 금지, `status=failed` 태그 부착 | 탐색 이력 소실 |
| 승격 후보 기준 | 최근 3회 val_auc 평균 > threshold | 우연한 고점 배포 |
| 정리 주기 | 90일 이상 미참조 run은 아카이브 | 저장 비용 증가 |

이 정책이 팀 온보딩 문서에 포함되면, 새 팀원도 처음부터 일관된 방식으로 실험을 기록하게 됩니다.


### MLflow UI 활용 팁

MLflow UI는 `mlflow ui` 명령으로 시작합니다. 기본 포트는 5000입니다.

```bash
mlflow ui --port 5000
# 브라우저에서 http://localhost:5000 접속
```

UI에서 가장 자주 쓰는 기능 세 가지는 다음과 같습니다.

1. **비교 뷰**: 여러 run을 선택하고 Compare 버튼을 누르면 파라미터와 메트릭을 나란히 볼 수 있습니다.
2. **차트 뷰**: 메트릭을 x축/y축에 놓아 산점도로 비교할 수 있습니다. 어떤 파라미터 조합이 성능에 영향을 주는지 시각적으로 파악합니다.
3. **검색 필터**: `params.C > 0.5 and metrics.val_auc > 0.85` 같은 필터로 관심 있는 run만 골라낼 수 있습니다.

### 실험 데이터 내보내기

실험 결과를 팀 회의에서 공유하거나 문서화할 때, DataFrame으로 내보내는 패턴이 유용합니다.

```python
import mlflow
import pandas as pd

client = mlflow.tracking.MlflowClient()
exp = client.get_experiment_by_name("demo-full")
runs = client.search_runs(
    experiment_ids=[exp.experiment_id],
    order_by=["metrics.val_auc DESC"],
    max_results=50,
)

rows = []
for r in runs:
    rows.append({
        "run_id": r.info.run_id[:8],
        "C": r.data.params.get("C"),
        "solver": r.data.params.get("solver"),
        "val_auc": r.data.metrics.get("val_auc"),
        "data_version": r.data.params.get("data_version"),
    })

df = pd.DataFrame(rows)
df.to_csv("experiment_report.csv", index=False)
print(df.head(10))
```

이 CSV를 팀 위키나 슬랙에 공유하면, 실험 결과를 MLflow 접근 권한 없이도 리뷰할 수 있습니다.

## 처음 질문으로 돌아가기

- **실험 관리가 없으면 왜 같은 모델도 다시 만들기 어려울까요?**
  - 본문의 기준은 실험 관리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **파라미터, 메트릭, 아티팩트, 환경 중 무엇을 반드시 남겨야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **MLflow에서 experiment와 run은 어떤 관계로 이해하면 좋을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [MLOps 101 (1/10): MLOps란 무엇인가?](./01-what-is-mlops.md)
- **실험 관리 (현재 글)**
- 데이터 버전 관리 (예정)
- 모델 학습 파이프라인 (예정)
- 모델 배포 (예정)
- 모델 모니터링 (예정)
- 데이터 드리프트와 모델 드리프트 (예정)
- 재학습 (예정)
- 피처 스토어 (예정)
- 운영 가능한 ML 시스템 (예정)

<!-- toc:end -->

## 참고 자료

- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/mlops-101/ko)

- [MLflow — Tracking](https://mlflow.org/docs/latest/tracking.html)
- [Weights & Biases](https://docs.wandb.ai/)
- [Neptune.ai — Comparison](https://neptune.ai/blog/best-ml-experiment-tracking-tools)
- [Google — Reproducible ML](https://cloud.google.com/architecture/ml-on-gcp-best-practices)

Tags: MLOps, ExperimentTracking, MLflow, Reproducibility, DataScience
