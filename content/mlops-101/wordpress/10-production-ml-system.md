---
title: "바이브코딩을 위한 MLOps 기초 (10/10): 운영 가능한 ML 시스템"
series: mlops-101
episode: 10
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - MLOps
  - Architecture
  - Production
  - Pipeline
---

# 바이브코딩을 위한 MLOps 기초 (10/10): 운영 가능한 ML 시스템

이 글은 "바이브코딩을 위한 MLOps 기초" 시리즈의 마지막 글입니다.

---

바이브코딩에서 AI는 각각의 MLOps 구성 요소를 빠르게 만들어 줍니다. 그런데 개별 조각을 아는 것과 그것을 하나의 운영 시스템으로 묶는 일은 완전히 다른 문제입니다. 도구 이름을 안다고 시스템이 되는 것이 아닙니다.

좋은 모델 하나를 만드는 일과 운영 가능한 시스템을 만드는 일은 다릅니다. 전자는 실험 최적화에 가깝고, 후자는 경계 설계와 복구 설계에 가깝습니다. 데이터가 언제 학습으로 넘어가고, 학습 결과가 어떤 기준으로 등록되고, 이상 징후가 보이면 누가 무엇을 해야 하는지까지 연결되어야 비로소 운영 가능한 시스템이 됩니다.

운영 가능한 ML 시스템이 되려면 세 가지가 함께 있어야 합니다. 첫째, 데이터와 모델 흐름이 자동으로 연결되어야 합니다. 둘째, 이상 징후가 보이면 관측과 대응이 이어져야 합니다. 셋째, 사람이 개입해야 할 순간과 자동화가 맡을 순간이 구분되어 있어야 합니다.

앞선 아홉 개 구성 요소를 하나의 운영 루프로 엮고, 팀의 MLOps 성숙도를 평가하는 최소 체크리스트를 정리합니다.

> **핵심 인사이트:** MLOps 성숙도는 도구 수가 아니라 순환 루프 완성도로 판단합니다. 운영 중 신호가 학습으로 다시 들어오는 피드백 루프가 닫혀 있어야 시스템이 스스로 개선됩니다.

## 이 글에서 다룰 문제

- 앞선 아홉 개 구성 요소는 실제 시스템에서 어떻게 연결될까요?
- 왜 도구를 각각 아는 것만으로는 운영 체계가 되지 않을까요?
- 런북, 온콜, SLI/SLO는 ML 시스템에서 어떤 역할을 할까요?
- MLOps 성숙도는 어떻게 평가할 수 있을까요?
- AI가 만든 ML 파이프라인에서 운영 관점으로 확인할 것은 무엇인가요?

## 운영 ML 시스템 핵심 패턴

```python
# MLOps 운영 루프: 데이터 → 학습 → 배포 → 모니터링 → 재학습
# 각 단계가 자동으로 연결되어 순환

class MLOpsLoop:
    """MLOps 운영 루프의 최소 구현"""

    def run(self, data_version: str):
        # 1. 데이터 검증
        data = self.validate_and_load(data_version)

        # 2. 학습 및 실험 추적
        model, metrics = self.train_with_tracking(data)

        # 3. 모델 레지스트리 등록 (Staging)
        version = self.register_model(model, metrics)

        # 4. 챔피언-챌린저 비교
        if self.is_better_than_champion(version, margin=0.01):
            self.promote_to_production(version)
        else:
            self.keep_champion()

        # 5. 배포 후 드리프트 모니터링
        self.schedule_drift_monitoring(version)

    def on_drift_detected(self, psi_score: float):
        """드리프트 감지 시 재학습 트리거"""
        if psi_score > 0.2:
            self.trigger_retraining()
```

```yaml
# SLI/SLO 정의 예시
sli_slo:
  prediction_latency:
    sli: "P99 예측 지연 시간"
    slo: "< 100ms (99% 요청)"
  model_accuracy:
    sli: "검증 세트 정확도"
    slo: "> 0.85 (일별 확인)"
  drift_detection:
    sli: "PSI 스코어"
    slo: "< 0.1 (주별 확인)"
  data_freshness:
    sli: "학습 데이터 최신성"
    slo: "< 7일"
```

## 변경 전후 비교

**Before: 분리된 도구 집합**
```text
- 노트북에서 학습, 수동 배포
- 운영 이슈는 사용자가 먼저 발견
- 모델 버전과 데이터 버전 연결 없음
- 재학습 타이밍을 개인 판단으로 결정
```

**After: 닫힌 운영 루프**
```text
- 데이터 → 학습 → 등록 → 배포 → 모니터링 → 재학습 자동 연결
- 드리프트 감지 시 사람보다 먼저 경고
- 모델 버전, 데이터 버전, 실험 런이 모두 연결됨
- 런북으로 이상 징후 대응 절차 표준화
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 순환 루프 없이 일회성 파이프라인 | 운영 신호가 학습으로 돌아오지 않음 | 드리프트 → 재학습 피드백 루프 구축 |
| SLO 없이 모니터링 | 경보 기준이 없어 경보 피로 발생 | 지연/정확도/드리프트 SLO 명시 |
| 런북 없이 자동화 | 경보 시 무엇을 해야 할지 모름 | 주요 경보 유형별 런북 작성 |
| 모델-데이터 버전 연결 없음 | 성능 저하 원인 추적 불가 | MLflow로 모델과 데이터 버전 함께 기록 |
| 성숙도 평가 없음 | 다음 개선 우선순위 결정 불가 | 팀 성숙도 체크리스트로 현재 위치 파악 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"운영 가능한 ML 시스템 아키텍처를 설계해줘.
데이터 버전 관리(DVC) → 학습 파이프라인(MLflow) →
모델 레지스트리 → 배포(FastAPI) → 드리프트 모니터링 → 재학습 트리거,
SLI/SLO 정의, 주요 경보별 런북 포함"

# AI 결과물 검증 체크포인트:
# - 운영 신호가 학습으로 피드백되는 순환 루프가 있는가?
# - SLI/SLO가 수치로 명시되어 있는가?
# - 주요 경보 유형별 런북이 있는가?
# - 모델 버전과 데이터 버전이 연결되어 있는가?
# - 사람이 개입해야 할 순간이 명시되어 있는가?
```

## 운영 체크리스트

- [ ] 데이터 → 학습 → 배포 → 모니터링 → 재학습 루프가 연결되어 있다
- [ ] 예측 지연, 정확도, 드리프트에 SLO가 정의되어 있다
- [ ] 주요 경보 유형별 런북이 작성되어 있다
- [ ] 모델 버전, 데이터 버전, 실험 런이 모두 연결되어 추적된다
- [ ] 팀의 MLOps 성숙도를 평가하고 다음 개선 항목을 알고 있다

## 처음 질문으로 돌아가기

- **도구를 알아도 운영 체계가 안 되는 이유는?** 각 도구는 특정 문제를 풀지만 경계 설계, 피드백 루프, 이상 대응 절차가 없으면 연결이 끊어집니다. "무엇이 트리거인가", "누가 결정하는가", "어떻게 롤백하는가"가 명시되어야 운영 체계입니다.
- **MLOps 성숙도란?** 수동 중심(Level 1)에서 자동화(Level 2), 자율 운영(Level 3)으로 발전하는 단계입니다. 다음 레벨로 가기 위해 무엇이 필요한지 체크리스트로 파악합니다.
- **SLI/SLO가 ML에서 중요한 이유는?** "모델이 잘 동작하는가"를 수치 없이 논의하면 혼선이 생깁니다. P99 지연 < 100ms, 정확도 > 0.85 같이 수치로 정의해야 경보 기준과 포스트모텀 기준이 명확해집니다.

## 정리

바이브코딩에서 AI가 만들어 준 ML 파이프라인에서 순환 루프 완성도, SLO 명시, 런북 존재를 반드시 확인하세요. 운영 가능한 ML 시스템은 도구의 합이 아니라 신호가 순환하는 닫힌 루프입니다. MLOps 101 시리즈를 통해 실험 추적부터 드리프트, 재학습, 피처 스토어, 운영 루프까지 ML 시스템 운영의 기초를 갖추셨기를 바랍니다.

## 참고 자료

- [Google MLOps Whitepaper](https://cloud.google.com/architecture/mlops-continuous-delivery-and-automation-pipelines-in-machine-learning)
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
- 바이브코딩을 위한 MLOps 기초 (8/10): 재학습
- 바이브코딩을 위한 MLOps 기초 (9/10): 피처 스토어
- **바이브코딩을 위한 MLOps 기초 (10/10): 운영 가능한 ML 시스템 (현재 글)**
<!-- toc:end -->

Tags: 바이브코딩, MLOps, Architecture, Production, Pipeline
