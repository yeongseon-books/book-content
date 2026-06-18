---
title: "바이브코딩을 위한 MLOps 기초 (8/10): 재학습"
series: mlops-101
episode: 8
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - MLOps
  - Retraining
  - Automation
  - Pipeline
---

# 바이브코딩을 위한 MLOps 기초 (8/10): 재학습

이 글은 "바이브코딩을 위한 MLOps 기초" 시리즈의 8번째 글입니다.

---

바이브코딩에서 AI는 재학습 파이프라인 코드를 빠르게 만들어 줍니다. 그런데 많은 팀이 재학습을 단순 반복 실행으로만 봅니다. 기준 없이 자주 재학습하면 작은 잡음에도 모델이 계속 바뀌고, 운영 안정성은 오히려 나빠질 수 있습니다. 반대로 검증 없이 새 모델을 바로 교체하면 더 나쁜 모델이 프로덕션에 들어갈 수 있습니다.

모델은 한 번 배포했다고 끝나지 않습니다. 입력 분포가 바뀌고, 사용자 행동이 바뀌면 언젠가는 다시 학습해야 합니다. 문제는 그 시점을 누가 어떤 기준으로 판단하느냐입니다.

재학습은 단순 재실행이 아니라, 명시적 트리거와 챔피언-챌린저 비교를 거쳐 승격 여부를 판단하는 운영 루프입니다. 트리거와 비교 근거가 명확해야 "왜 교체했는가"에 대답할 수 있습니다.

재학습 트리거 유형, 챔피언-챌린저 비교, 카나리 배포, A/B 통계 검정을 중심으로 정리합니다.

> **핵심 인사이트:** 재학습에서 중요한 것은 자동 실행 자체보다 정책입니다. 어떤 신호가 트리거인지, 챌린저가 챔피언보다 얼마나 좋아야 승격하는지, 실패하면 어떻게 롤백하는지가 먼저 정의되어야 합니다.

## 이 글에서 다룰 문제

- 언제 재학습해야 하는지를 어떤 신호로 정할 수 있을까요?
- 일정 기반, 드리프트 기반, 성능 기반 트리거는 어떻게 다를까요?
- 챔피언과 챌린저를 비교할 때 왜 마진(히스테리시스)이 필요할까요?
- 카나리 배포와 A/B 테스트는 어떻게 다를까요?
- AI가 만든 재학습 파이프라인에서 확인해야 할 것은 무엇인가요?

## 재학습 핵심 패턴

```python
# 챔피언-챌린저 비교: 통계적으로 유의미한 성능 차이만 승격
import numpy as np
from scipy.stats import ttest_rel

champion_acc = np.array([0.82, 0.83, 0.81, 0.84, 0.82])
challenger_acc = np.array([0.84, 0.85, 0.83, 0.86, 0.84])

stat, p = ttest_rel(champion_acc, challenger_acc)
print(f"t-statistic: {stat:.3f}, p-value: {p:.4f}")

# 히스테리시스 마진: 우연한 차이로 모델이 자주 바뀌지 않도록
MARGIN = 0.01  # 챌린저가 최소 1% 이상 좋아야 승격
if p < 0.05 and challenger_acc.mean() > champion_acc.mean() + MARGIN:
    print("챌린저 승격: 통계적으로 유의미하게 더 좋음")
else:
    print("챔피언 유지: 유의미한 차이 없음")
```

```python
# MLflow로 챔피언-챌린저 버전 관리
import mlflow
from mlflow.tracking import MlflowClient

client = MlflowClient()

# 챌린저 학습 후 Staging 등록 → 검증 후 Production 승격
def promote_challenger(model_name: str, challenger_version: str):
    # 1. Staging으로 전환 (검증 단계)
    client.transition_model_version_stage(
        name=model_name,
        version=challenger_version,
        stage="Staging",
    )
    # 2. 검증 통과 후 Production 승격
    client.transition_model_version_stage(
        name=model_name,
        version=challenger_version,
        stage="Production",
    )
```

## 변경 전후 비교

**Before: 감 기반 재학습**
```text
- 분기마다 한 번씩 감으로 재학습
- 새 모델이 더 좋은지 검증 없이 바로 교체
- 왜 교체했는지 근거 없음
- 나쁜 모델이 프로덕션에 배포될 위험
```

**After: 트리거 기반 재학습 루프**
```text
- 드리프트 경고 또는 성능 저하 시 자동 재학습 트리거
- 챔피언-챌린저 A/B 비교 후 통계적으로 더 좋을 때만 승격
- 트리거 이벤트, 학습 메트릭, 승격 근거 모두 기록
- 문제 시 즉시 롤백 가능
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 트리거 없이 정기 재학습만 | 필요 없을 때 자원 낭비, 필요할 때 놓침 | 드리프트/성능 기반 트리거 추가 |
| 검증 없이 챌린저 바로 승격 | 더 나쁜 모델이 프로덕션에 배포됨 | Staging → 검증 → Production 단계 |
| 히스테리시스 마진 없음 | 작은 잡음에도 모델이 자주 교체됨 | 최소 성능 개선 마진(예: 1%) 설정 |
| A/B 기간이 너무 짧음 | 라벨 지연으로 충분한 데이터 없음 | 라벨 수집 주기에 맞춰 2-4주 설정 |
| 롤백 절차 없음 | 나쁜 모델 배포 후 복구 불가 | 이전 챔피언 버전 보존 + 빠른 전환 절차 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"ML 모델 재학습 파이프라인을 만들어줘.
드리프트 감지 시 자동 트리거,
챔피언-챌린저 A/B 비교 (paired t-test),
MLflow로 버전 관리,
카나리 배포로 5% 트래픽 먼저 검증,
문제 시 자동 롤백 포함"

# AI 결과물 검증 체크포인트:
# - 재학습 트리거가 명시되어 있는가? (드리프트/성능/일정)
# - 챌린저 검증 없이 바로 승격하지 않는가?
# - 히스테리시스 마진이 설정되어 있는가?
# - 이전 챔피언으로 롤백 절차가 있는가?
# - 재학습 이유와 비교 결과가 기록되는가?
```

## 운영 체크리스트

- [ ] 재학습 트리거가 명시적으로 정의되어 있다 (드리프트/성능/일정)
- [ ] 챌린저가 Staging에서 검증된 후 Production으로 승격된다
- [ ] 통계적 유의성 검정(p-value)으로 승격 여부를 결정한다
- [ ] 이전 챔피언 버전이 보존되고 롤백 절차가 있다
- [ ] 재학습 이유, 비교 메트릭, 승격 결정이 모두 기록된다

## 처음 질문으로 돌아가기

- **재학습 트리거 유형은?** 일정 기반(매주/매월), 드리프트 기반(PSI > 0.2), 성능 기반(정확도 < 임계값) 세 가지가 있습니다. 실무에서는 세 가지를 조합해 사용합니다.
- **히스테리시스 마진이 필요한 이유는?** 마진 없이 챌린저가 조금이라도 나으면 교체하면, 측정 잡음으로 인해 모델이 자주 바뀝니다. 최소 1-2%의 유의미한 차이가 있을 때만 교체해야 운영이 안정됩니다.
- **카나리 배포와 A/B 테스트의 차이는?** 카나리는 5-10% 트래픽에만 새 모델을 먼저 적용해 운영 메트릭을 확인합니다. A/B는 두 모델에 무작위로 트래픽을 배분해 성능 지표를 통계 검정으로 비교합니다.

## 정리

바이브코딩에서 AI가 만들어 준 재학습 파이프라인에서 트리거 명시화, 챌린저 검증 단계, 롤백 절차를 반드시 확인하세요. 재학습은 자동화 자체보다 언제, 어떤 기준으로, 어떻게 검증할지 정책이 더 중요합니다. 다음 글에서는 피처 스토어를 다룹니다.

## 참고 자료

- [MLflow — Model Registry](https://mlflow.org/docs/latest/model-registry.html)
- [Chip Huyen — Designing Machine Learning Systems](https://www.oreilly.com/library/view/designing-machine-learning/9781098107956/)
- [book-examples](https://github.com/yeongseon-books/book-examples/tree/main/mlops-101/ko)

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 MLOps 기초 (1/10): MLOps란 무엇인가?
- 바이브코딩을 위한 MLOps 기초 (2/10): 실험 추적
- 바이브코딩을 위한 MLOps 기초 (3/10): 데이터 버전 관리
- 바이브코딩을 위한 MLOps 기초 (4/10): 학습 파이프라인
- 바이브코딩을 위한 MLOps 기초 (5/10): 모델 배포
- 바이브코딩을 위한 MLOps 기초 (6/10): 모델 모니터링
- 바이브코딩을 위한 MLOps 기초 (7/10): 데이터 드리프트와 모델 드리프트
- **바이브코딩을 위한 MLOps 기초 (8/10): 재학습 (현재 글)**
- 바이브코딩을 위한 MLOps 기초 (9/10): 피처 스토어
- 바이브코딩을 위한 MLOps 기초 (10/10): 운영 가능한 ML 시스템
<!-- toc:end -->

Tags: 바이브코딩, MLOps, Retraining, Automation, Pipeline
