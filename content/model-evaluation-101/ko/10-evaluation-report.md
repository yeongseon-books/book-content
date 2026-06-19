---
series: model-evaluation-101
episode: 10
title: "Model Evaluation 101 (10/10): 평가 리포트 만들기"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - ModelEvaluation
  - Reporting
  - ModelCard
  - Reproducibility
  - scikit-learn
seo_description: 프로덕션 배포 결정의 근거가 되는 종합적인 모델 평가 리포트 구성 요소와 자동화된 파이프라인 구축 방법을 설명합니다.
last_reviewed: '2026-05-15'
---

# Model Evaluation 101 (10/10): 평가 리포트 만들기

새 모델 배포 6개월 후, 성능이 왜 떨어졌는지 조사해야 합니다. 배포 당시 리포트를 찾았는데 슬라이드 한 장에 "F1=0.86, 배포 승인"이라고만 적혀 있습니다. 어떤 데이터로 측정했는지, 임계값은 무엇이었는지, 알려진 취약점은 있었는지 아무것도 없습니다. 같은 실험을 재현하는 데 이틀이 걸립니다. 이 상황을 막는 것이 좋은 평가 리포트입니다.

이 글은 Model Evaluation 101 시리즈의 마지막 글입니다.

좋은 평가 리포트는 문서 작업이 아니라 의사결정 기록입니다. 리뷰, 감사, 사고 후 분석이 모두 같은 문서를 참고할 수 있어야 팀의 속도도 유지되고 책임 경계도 분명해집니다.

![Model Evaluation 101 10장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/model-evaluation-101/10/10-01-concept-at-a-glance.ko.png)
*Model Evaluation 101 10장 흐름 개요*

> 평가 보고서는 망각을 막는 운영 기록입니다 — 데이터·임계값·슬라이스·이미 알려진 리스크를 하나의 문서에 묶어 두어야 리뷰, 감사, 사후 분석이 모두 같은 근거를 참조할 수 있습니다.

## 이 글에서 다룰 문제

- 좋은 평가 리포트에 반드시 포함해야 할 요소는 무엇일까요?
- 오프라인 지표와 온라인 지표는 어떻게 다르고 둘 다 왜 필요할까요?
- 평가 리포트와 Model Card는 어떻게 다를까요?
- 재현성 정보는 왜 빠지면 안 될까요?
- 자동화된 리포트 생성을 어떻게 구현할까요?

## 평가 리포트의 5가지 필수 요소

좋은 평가 리포트는 다음 5가지를 반드시 포함해야 합니다.

| 요소 | 내용 | 없으면 어떻게 되는가 |
| --- | --- | --- |
| 데이터 정보 | 어떤 데이터로 측정했는가 | 재현 불가, 드리프트 추적 불가 |
| 핵심 지표 | 어떤 지표를 어떤 임계값에서 | 의사결정 근거 없음 |
| 슬라이스 성능 | 세그먼트별 약점 | 숨겨진 실패 발견 불가 |
| 재현성 메타데이터 | 코드/데이터 버전 | 같은 실험 재현 불가 |
| 알려진 리스크 | 이미 알고 있는 약점 | 책임 회피, 미래 감사 실패 |

## 오프라인 지표 vs. 온라인 지표

배포 전 테스트 세트에서의 성능(오프라인)과 실제 운영 중 성능(온라인)은 다를 수 있습니다.

```python
import numpy as np
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score, brier_score_loss

# 데이터 및 모델
X, y = make_classification(n_samples=5000, weights=[0.7, 0.3], random_state=42)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, stratify=y, random_state=42
)

model = LogisticRegression(max_iter=1000, random_state=42).fit(X_train, y_train)
proba = model.predict_proba(X_test)[:, 1]
pred = (proba >= 0.5).astype(int)

# 오프라인 지표 계산
offline_metrics = {
    "f1_macro": f1_score(y_test, pred, average="macro"),
    "f1_positive": f1_score(y_test, pred),
    "auc_roc": roc_auc_score(y_test, proba),
    "brier_score": brier_score_loss(y_test, proba),
}

print("=== 오프라인 지표 (테스트 세트) ===")
for name, value in offline_metrics.items():
    print(f"  {name}: {value:.4f}")

print()
print("=== 오프라인 vs. 온라인 지표 비교 ===")
print()
print("오프라인 지표:")
print("  - 고정된 테스트 세트에서 측정")
print("  - 배포 전에 미리 계산 가능")
print("  - 예: F1, AUC, Brier Score")
print("  - 한계: 실제 운영 환경과 다를 수 있음")
print()
print("온라인 지표:")
print("  - 실제 운영 중 실시간 측정")
print("  - 사용자 행동, 비즈니스 KPI와 연결")
print("  - 예: 클릭률, 전환율, 사기 탐지율, 정확한 거래 차단율")
print("  - 한계: 라벨이 실시간으로 없는 경우 많음")
print()
print("두 지표가 모두 필요한 이유:")
print("  오프라인이 좋지만 온라인이 나쁜 경우 → 배포 환경 드리프트")
print("  오프라인이 나쁘지만 온라인이 좋은 경우 → 테스트 데이터 대표성 문제")
```

## 슬라이스 성능 자동 수집

```python
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
)

def collect_slice_metrics(X_test, y_test, pred, proba, feature_idx=0, n_bins=4):
    """피처 구간별 성능 지표를 수집합니다."""
    feat = X_test[:, feature_idx]
    bins = np.percentile(feat, np.linspace(0, 100, n_bins + 1))
    slices = {}

    for i in range(len(bins) - 1):
        lo, hi = bins[i], bins[i+1]
        mask = (feat >= lo) & (feat <= hi)
        seg_name = f"feat{feature_idx}_{i+1}Q"

        if mask.sum() < 10 or len(np.unique(y_test[mask])) < 2:
            continue

        y_seg = y_test[mask]
        pred_seg = pred[mask]
        proba_seg = proba[mask]

        cm = confusion_matrix(y_seg, pred_seg)
        tn_s, fp_s, fn_s, tp_s = cm.ravel()

        slices[seg_name] = {
            "n_samples": int(mask.sum()),
            "positive_rate": float(y_seg.mean()),
            "f1_macro": float(f1_score(y_seg, pred_seg, average="macro", zero_division=0)),
            "recall": float(recall_score(y_seg, pred_seg, zero_division=0)),
            "precision": float(precision_score(y_seg, pred_seg, zero_division=0)),
            "fp": int(fp_s),
            "fn": int(fn_s),
        }

    return slices

slice_metrics = collect_slice_metrics(X_test, y_test, pred, proba, feature_idx=0)
print("=== 슬라이스 성능 ===")
print(f"{'세그먼트':>15} {'샘플수':>8} {'F1':>8} {'재현율':>8} {'정밀도':>8}")
print("-" * 55)
for seg, metrics in slice_metrics.items():
    flag = " ← 약점" if metrics["f1_macro"] < 0.70 else ""
    print(f"{seg:>15} {metrics['n_samples']:>8d} {metrics['f1_macro']:>8.3f} "
          f"{metrics['recall']:>8.3f} {metrics['precision']:>8.3f}{flag}")
```

## 재현성 메타데이터 수집

```python
import hashlib
import sys
import json
import datetime
import sklearn

def collect_metadata(X, model, threshold=0.5):
    """재현성을 위한 메타데이터를 수집합니다."""
    return {
        "timestamp": datetime.datetime.now().isoformat(),
        "python_version": sys.version.split()[0],
        "sklearn_version": sklearn.__version__,
        "numpy_version": np.__version__,
        "data_hash_sha1": hashlib.sha1(X.tobytes()).hexdigest()[:16],
        "data_shape": list(X.shape),
        "threshold": threshold,
        "model_class": type(model).__name__,
        "model_params": model.get_params(),
    }

meta = collect_metadata(X_test, model, threshold=0.5)
print("=== 재현성 메타데이터 ===")
for key, value in meta.items():
    if key == "model_params":
        print(f"  {key}:")
        for k, v in value.items():
            print(f"    {k}: {v}")
    else:
        print(f"  {key}: {value}")
```

## 완전한 평가 리포트 생성

```python
def generate_evaluation_report(
    y_test, pred, proba, X_test,
    model, threshold=0.5,
    known_risks=None,
    deployment_notes=None,
):
    """완전한 평가 리포트를 생성합니다."""
    if known_risks is None:
        known_risks = []
    if deployment_notes is None:
        deployment_notes = {}

    from sklearn.metrics import balanced_accuracy_score

    # 핵심 지표
    metrics = {
        "accuracy": float((pred == y_test).mean()),
        "balanced_accuracy": float(balanced_accuracy_score(y_test, pred)),
        "f1_macro": float(f1_score(y_test, pred, average="macro")),
        "f1_positive": float(f1_score(y_test, pred)),
        "precision": float(precision_score(y_test, pred, zero_division=0)),
        "recall": float(recall_score(y_test, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_test, proba)),
        "brier_score": float(brier_score_loss(y_test, proba)),
    }

    # 혼동 행렬
    cm = confusion_matrix(y_test, pred)
    tn, fp, fn, tp = cm.ravel()
    confusion = {"TN": int(tn), "FP": int(fp), "FN": int(fn), "TP": int(tp)}

    # 슬라이스 성능
    slices = collect_slice_metrics(X_test, y_test, pred, proba, feature_idx=0)

    # 메타데이터
    meta = collect_metadata(X_test, model, threshold)

    # 리포트 조립
    report = {
        "report_version": "1.0",
        "generated_at": meta["timestamp"],
        "metrics": metrics,
        "confusion_matrix": confusion,
        "threshold": threshold,
        "slices": slices,
        "metadata": meta,
        "known_risks": known_risks,
        "deployment_notes": deployment_notes,
    }

    return report

# 리포트 생성
report = generate_evaluation_report(
    y_test, pred, proba, X_test, model,
    threshold=0.5,
    known_risks=[
        "피처 0 하위 25% 세그먼트 F1 낮음 (0.62)",
        "FN 비율 높음 — 재현율 개선 여지 있음",
        "보정(calibration) 검증 미완료",
    ],
    deployment_notes={
        "approved_by": "평가팀 리뷰",
        "deployment_condition": "재현율 목표 65% 달성 시",
        "next_review_date": "2026-09-01",
    },
)

print("=== 평가 리포트 (JSON) ===")
print(json.dumps(report, indent=2, ensure_ascii=False)[:1500] + "\n... (생략)")
```

## 마크다운 리포트 렌더링

```python
def render_markdown_report(report):
    """평가 리포트를 마크다운으로 렌더링합니다."""
    lines = []
    lines.append(f"# 모델 평가 리포트")
    lines.append(f"생성 시각: {report['generated_at']}")
    lines.append("")

    # 핵심 지표
    lines.append("## 핵심 지표")
    lines.append("")
    lines.append(f"| 지표 | 값 |")
    lines.append(f"| --- | ---: |")
    for metric, value in report["metrics"].items():
        flag = " ← 주요 지표" if metric in ["f1_macro", "recall", "roc_auc"] else ""
        lines.append(f"| {metric} | {value:.4f}{flag} |")
    lines.append("")

    # 임계값
    lines.append(f"**운영 임계값: {report['threshold']}**")
    lines.append("")

    # 혼동 행렬
    cm = report["confusion_matrix"]
    lines.append("## 혼동 행렬")
    lines.append("")
    lines.append(f"| | 예측: 음성 | 예측: 양성 |")
    lines.append(f"| --- | ---: | ---: |")
    lines.append(f"| 실제: 음성 | {cm['TN']} (TN) | {cm['FP']} (FP) |")
    lines.append(f"| 실제: 양성 | {cm['FN']} (FN) | {cm['TP']} (TP) |")
    lines.append("")

    # 슬라이스 성능
    lines.append("## 세그먼트별 성능")
    lines.append("")
    lines.append("| 세그먼트 | 샘플수 | F1 | 재현율 | 정밀도 |")
    lines.append("| --- | ---: | ---: | ---: | ---: |")
    for seg, metrics in report["slices"].items():
        flag = " ⚠" if metrics["f1_macro"] < 0.70 else ""
        lines.append(
            f"| {seg}{flag} | {metrics['n_samples']} | "
            f"{metrics['f1_macro']:.3f} | {metrics['recall']:.3f} | "
            f"{metrics['precision']:.3f} |"
        )
    lines.append("")

    # 알려진 리스크
    if report.get("known_risks"):
        lines.append("## 알려진 리스크")
        lines.append("")
        for risk in report["known_risks"]:
            lines.append(f"- {risk}")
        lines.append("")

    # 배포 메모
    if report.get("deployment_notes"):
        lines.append("## 배포 메모")
        lines.append("")
        for key, value in report["deployment_notes"].items():
            lines.append(f"- **{key}**: {value}")
        lines.append("")

    # 재현성 정보
    meta = report["metadata"]
    lines.append("## 재현성 정보")
    lines.append("")
    lines.append(f"- Python: {meta['python_version']}")
    lines.append(f"- scikit-learn: {meta['sklearn_version']}")
    lines.append(f"- 데이터 해시: `{meta['data_hash_sha1']}`")
    lines.append(f"- 데이터 크기: {meta['data_shape']}")
    lines.append(f"- 모델 클래스: {meta['model_class']}")
    lines.append("")

    return "\n".join(lines)

md_report = render_markdown_report(report)
print("=== 마크다운 리포트 ===")
print(md_report[:2000])
print("... (생략)")
```

## 평가 리포트 vs. Model Card

두 문서는 목적이 다릅니다.

| 항목 | 평가 리포트 | Model Card |
| --- | --- | --- |
| 목적 | 특정 배포 결정 근거 | 모델의 전반적 설명 |
| 작성 시점 | 매 배포 전 | 모델 출시 시 |
| 대상 독자 | 팀 내부 (개발자, PM) | 외부 이해관계자 포함 |
| 내용 | 테스트 세트 지표, 임계값, 슬라이스 | 의도된 용도, 제한사항, 윤리 고려 |
| 갱신 주기 | 매 배포마다 | 모델 버전이 크게 바뀔 때 |
| 재현성 | 필수 | 선택 |

```python
# Model Card 최소 구조 예시
model_card = {
    "model_name": "고객 이탈 예측 모델 v2.1",
    "intended_use": "30일 내 이탈 가능성 높은 고객 사전 식별",
    "not_intended_for": "개별 고객 처벌 또는 서비스 차별",
    "training_data": "2025년 1월~12월 활성 사용자 거래 로그",
    "evaluation_data": "2026년 1월~2월 홀드아웃 세트",
    "metrics": {
        "primary": "recall (목표 ≥ 65%)",
        "secondary": ["f1_macro", "precision"],
    },
    "known_limitations": [
        "신규 가입 30일 미만 사용자에 대한 성능 제한",
        "비정기 결제 패턴에 대한 학습 데이터 부족",
    ],
    "ethical_considerations": [
        "예측 점수를 이유로 서비스를 차단하지 않을 것",
        "고소득 사용자 그룹에 대한 편향 검토 미완료",
    ],
    "contact": "ml-team@example.com",
}

print("=== Model Card 구조 ===")
print(json.dumps(model_card, indent=2, ensure_ascii=False))
```

## 자동화된 리포트 파이프라인

```python
def run_full_evaluation_pipeline(
    model, X_train, y_train, X_test, y_test,
    threshold=None,
    output_path=None,
):
    """
    모델 평가부터 리포트 생성까지 전체 파이프라인을 실행합니다.
    threshold=None이면 검증 세트에서 자동 탐색합니다.
    """
    from sklearn.model_selection import train_test_split
    import numpy as np

    # 검증 세트에서 임계값 탐색 (옵션)
    if threshold is None:
        X_tr, X_val, y_tr, y_val = train_test_split(
            X_train, y_train, test_size=0.2, stratify=y_train, random_state=42
        )
        model.fit(X_tr, y_tr)
        val_proba = model.predict_proba(X_val)[:, 1]

        best_f1, best_threshold = 0, 0.5
        for t in np.arange(0.1, 0.9, 0.05):
            pred_t = (val_proba >= t).astype(int)
            f1_t = f1_score(y_val, pred_t, zero_division=0)
            if f1_t > best_f1:
                best_f1 = f1_t
                best_threshold = float(t)
        threshold = best_threshold
        print(f"검증 세트 최적 임계값: {threshold:.2f} (F1={best_f1:.4f})")

        # 전체 훈련 데이터로 재학습
        model.fit(X_train, y_train)
    else:
        model.fit(X_train, y_train)

    # 테스트 세트 평가
    proba = model.predict_proba(X_test)[:, 1]
    pred = (proba >= threshold).astype(int)

    # 리포트 생성
    report = generate_evaluation_report(
        y_test, pred, proba, X_test, model, threshold=threshold
    )

    # 배포 판정
    recall_val = report["metrics"]["recall"]
    f1_val = report["metrics"]["f1_macro"]

    print(f"\n=== 배포 판정 ===")
    print(f"재현율: {recall_val:.4f} (목표: 0.65)")
    print(f"F1 macro: {f1_val:.4f}")

    if recall_val >= 0.65:
        print("판정: 배포 가능 (재현율 목표 달성)")
    else:
        print("판정: 배포 보류 (재현율 목표 미달)")
        print(f"  → 임계값 낮추기 또는 모델 개선 필요")

    if output_path:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"\n리포트 저장: {output_path}")

    return report

# 파이프라인 실행
final_report = run_full_evaluation_pipeline(
    LogisticRegression(max_iter=2000, random_state=42),
    X_train, y_train, X_test, y_test,
    threshold=None,
)
```

## 자주 하는 실수

**실수 1 — 임계값을 기록하지 않음**

임계값 없는 F1 점수는 재현 불가능합니다. 임계값 0.5와 0.3에서의 F1은 완전히 다를 수 있습니다. 모든 지표는 어떤 임계값에서 측정했는지를 함께 기록해야 합니다.

**실수 2 — 슬라이스 성능 생략**

전체 F1만 보고에 넣으면 숨겨진 약점을 은폐하게 됩니다. 최소한 3개 이상의 중요 세그먼트 성능을 포함해야 합니다. 슬라이스 성능이 없으면 감사(audit) 시 문제가 됩니다.

**실수 3 — 재현성 정보 미포함**

버전과 해시 정보 없이는 6개월 후 같은 실험을 재현할 수 없습니다. scikit-learn 버전 차이 하나로도 결과가 달라질 수 있습니다. Python 버전, 라이브러리 버전, 데이터 해시를 반드시 포함해야 합니다.

**실수 4 — 알려진 리스크 섹션 비워두기**

"약점이 없다"가 아니라 "약점을 파악했지만 허용 가능한 범위로 판단했다"가 좋은 리포트입니다. 알려진 리스크를 숨기면 나중에 그 리스크가 실제 문제가 됐을 때 신뢰를 잃습니다.

**실수 5 — 수동으로 작성한 요약만 남기기**

수동 요약은 오류 가능성이 있고, 다음 배포 시 재사용이 어렵습니다. JSON 형식의 구조화된 리포트를 먼저 생성하고, 그것에서 마크다운을 자동으로 생성하는 파이프라인을 구축해야 합니다.

## 운영 체크리스트

- [ ] 핵심 지표와 임계값을 함께 기록했습니다.
- [ ] 최소 3개 세그먼트의 슬라이스 성능을 포함했습니다.
- [ ] Python, 라이브러리 버전, 데이터 해시를 기록했습니다.
- [ ] 알려진 리스크 목록을 솔직하게 작성했습니다.
- [ ] 배포 조건과 다음 검토 일정을 명시했습니다.
- [ ] JSON 형식으로 구조화된 리포트를 생성했습니다.
- [ ] 마크다운 요약을 자동으로 생성하는 코드를 작성했습니다.
- [ ] 오프라인 지표와 온라인 지표를 모두 추적 계획을 수립했습니다.

## 처음 질문으로 돌아가기

- **좋은 평가 리포트에 반드시 포함해야 할 요소는 무엇일까요?**
  - 5가지 필수 요소: 데이터 정보(어떤 데이터로 측정했는가), 핵심 지표(임계값과 함께), 슬라이스 성능(세그먼트별 약점), 재현성 메타데이터(버전/해시), 알려진 리스크(이미 파악한 약점). 이 중 하나라도 빠지면 6개월 후 문제가 생겼을 때 조사가 불가능합니다.

- **오프라인 지표와 온라인 지표는 어떻게 다르고 둘 다 왜 필요할까요?**
  - 오프라인 지표는 배포 전 테스트 세트에서 측정한 F1, AUC 같은 지표입니다. 온라인 지표는 배포 후 실제 운영에서 측정한 클릭률, 전환율, 사기 탐지율 같은 비즈니스 KPI입니다. 두 지표 모두 필요한 이유는 오프라인 성능이 온라인 성능을 보장하지 않기 때문입니다. 데이터 드리프트, 피드백 루프, 사용자 행동 변화로 인해 온라인 성능이 오프라인과 다를 수 있습니다.

- **재현성 정보는 왜 빠지면 안 될까요?**
  - 재현성 정보 없이는 6개월 후 같은 실험을 재현할 수 없습니다. Python 버전, scikit-learn 버전 차이로 부동소수점 결과가 달라질 수 있고, 데이터 해시가 없으면 어떤 데이터를 썼는지 추적이 불가능합니다. 감사, 사고 분석, 모델 비교 등 모든 후속 작업이 재현성에 의존합니다.

---

## 정리

좋은 평가 리포트는 한 장짜리 요약이면서도, 배포 판단에 필요한 맥락을 빠짐없이 담고 있어야 합니다. 데이터, 지표, 임계값, 슬라이스, 재현성, 리스크가 한곳에 모여야 숫자가 의사결정의 근거가 됩니다.

이것으로 Model Evaluation 101 시리즈의 10가지 주제를 모두 다루었습니다.

1. 모델 평가는 의사결정 설계입니다 (1장)
2. 데이터 분할이 평가의 신뢰성을 결정합니다 (2장)
3. 정확도 하나로는 불충분합니다 (3장)
4. 정밀도-재현율 트레이드오프를 운영 정책으로 연결합니다 (4장)
5. F1은 올바른 절차와 함께 사용해야 합니다 (5장)
6. AUC는 운영 임계값 선택과 연결되어야 합니다 (6장)
7. 확률 신뢰성은 순위 성능과 별도로 검증합니다 (7장)
8. 교차 검증으로 평가의 불확실성을 추정합니다 (8장)
9. 오류 분석으로 다음 개선의 방향을 찾습니다 (9장)
10. 모든 것을 기록하여 의사결정 흔적을 남깁니다 (10장)

이 10가지가 모델 평가의 기본 어휘입니다. 이후에는 MLOps와 지속적인 모니터링, 더 깊은 오류 분석으로 자연스럽게 이어집니다.

<!-- toc:begin -->
## 시리즈 목차

- [Model Evaluation 101 (1/10): 모델 평가는 왜 어려운가?](./01-why-evaluation-is-hard.md)
- [Model Evaluation 101 (2/10): 훈련·검증·테스트 데이터 나누기](./02-train-val-test.md)
- [Model Evaluation 101 (3/10): 정확도의 한계](./03-limits-of-accuracy.md)
- [Model Evaluation 101 (4/10): 정밀도와 재현율](./04-precision-and-recall.md)
- [Model Evaluation 101 (5/10): F1 점수](./05-f1-score.md)
- [Model Evaluation 101 (6/10): ROC와 AUC 이해하기](./06-roc-and-auc.md)
- [Model Evaluation 101 (7/10): 확률 보정 이해하기](./07-calibration.md)
- [Model Evaluation 101 (8/10): 교차 검증 이해하기](./08-cross-validation.md)
- [Model Evaluation 101 (9/10): 오류 분석으로 약점 찾기](./09-error-analysis.md)
- **Model Evaluation 101 (10/10): 평가 리포트 만들기 (현재 글)**

<!-- toc:end -->

## 참고 자료

- [Google — Model Cards](https://modelcards.withgoogle.com/about)
- [Datasheets for Datasets](https://arxiv.org/abs/1803.09010)
- [scikit-learn — Model evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [MLOps — Production ML guide](https://ml-ops.org/)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/model-evaluation-101/ko)

Tags: ModelEvaluation, Reporting, ModelCard, Reproducibility, scikit-learn
