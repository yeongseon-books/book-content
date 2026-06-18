---
title: "바이브코딩을 위한 MLOps 기초 (9/10): 피처 스토어"
series: mlops-101
episode: 9
language: ko
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - MLOps
  - FeatureStore
  - Feast
  - DataScience
---

# 바이브코딩을 위한 MLOps 기초 (9/10): 피처 스토어

이 글은 "바이브코딩을 위한 MLOps 기초" 시리즈의 9번째 글입니다.

---

바이브코딩에서 AI는 피처 엔지니어링 코드를 빠르게 만들어 줍니다. 그런데 같은 이름의 피처를 학습 코드와 서빙 코드가 각각 따로 계산하기 시작하면 언젠가는 어긋납니다. 학습 때는 하루 단위 집계를 쓰고, 서빙 때는 실시간 계산식을 조금 다르게 쓰는 식의 작은 차이가 쌓이면 모델은 배포 전과 배포 후에 다른 세상을 보게 됩니다.

이른바 학습-서빙 불일치는 눈에 잘 띄지 않아서 더 까다롭습니다. 오프라인 검증에서는 잘 나오는데 운영 성능이 기대보다 낮을 때, 실제 원인이 모델 자체보다 피처 계산 경로 차이인 경우가 적지 않습니다.

피처 스토어는 피처 저장소가 아니라, 학습과 서빙이 같은 피처 정의를 공유하게 만드는 계약 계층입니다. 피처 스토어의 진짜 가치는 저장보다 일관성에 있습니다.

학습-서빙 불일치, 온라인/오프라인 저장소의 역할, Feast를 이용한 피처 관리, 시점 일치 조인을 중심으로 정리합니다.

> **핵심 인사이트:** 같은 피처를 학습 코드와 서빙 코드가 각자 계산하면 반드시 어긋납니다. 피처 뷰(Feature View)를 한 번 정의하면 학습과 서빙이 같은 로직을 씁니다. 시점 일치 조인 없이는 데이터 누수가 발생합니다.

## 이 글에서 다룰 문제

- 학습-서빙 불일치는 왜 자꾸 반복될까요?
- 온라인 저장소와 오프라인 저장소는 어떤 역할 차이가 있을까요?
- Feast에서 entity와 feature view는 어떻게 이해하면 좋을까요?
- 시점 일치 조인이 왜 데이터 누수 방지에 중요할까요?
- AI가 만든 피처 코드에서 확인해야 할 것은 무엇인가요?

## 피처 스토어 핵심 패턴

```python
from feast import FeatureStore, Entity, FeatureView, Field
from feast.types import Float32, Int64
from feast import FileSource
from datetime import timedelta

# 엔터티: 피처를 조인할 기준 키
user = Entity(name="user_id", description="사용자 ID")

# 피처 뷰: 학습과 서빙이 공유하는 피처 정의
user_features = FeatureView(
    name="user_activity_features",
    entities=[user],
    ttl=timedelta(days=1),
    schema=[
        Field(name="purchase_count_7d", dtype=Int64),
        Field(name="avg_session_duration", dtype=Float32),
    ],
    source=FileSource(path="data/user_features.parquet", timestamp_field="event_timestamp"),
)

# 피처 스토어 초기화
store = FeatureStore(repo_path=".")
```

```python
# 학습: 오프라인 저장소에서 시점 일치 조인으로 피처 추출
# (미래 데이터 누수 방지)
entity_df = pd.DataFrame({
    "user_id": [1, 2, 3],
    "event_timestamp": pd.to_datetime(["2026-01-01", "2026-01-02", "2026-01-03"])
})
training_data = store.get_historical_features(
    entity_df=entity_df,
    features=["user_activity_features:purchase_count_7d"]
).to_df()

# 서빙: 온라인 저장소에서 낮은 지연으로 실시간 피처 조회
online_features = store.get_online_features(
    features=["user_activity_features:purchase_count_7d"],
    entity_rows=[{"user_id": 1}]
).to_dict()
```

## 변경 전후 비교

**Before: 학습과 서빙이 각자 피처 계산**
```text
- 학습 코드: pandas로 7일 집계
- 서빙 코드: SQL로 같은 개념을 다르게 구현
- 결과: 배포 후 오프라인 메트릭과 운영 성능 차이
- 원인 파악: 여러 코드를 비교해 며칠 소요
```

**After: 피처 뷰 공유**
```text
- 피처 뷰 한 번 정의
- 학습: get_historical_features() (오프라인)
- 서빙: get_online_features() (온라인)
- 동일한 피처 정의 → 학습-서빙 불일치 제거
```

## 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 방법 |
|------|-------------|-----------|
| 학습/서빙 피처 코드 분리 | 조금만 달라도 모델 입력이 달라짐 | 피처 뷰로 단일 정의 |
| 시점 일치 조인 없음 | 미래 데이터 누수 → 과도하게 낙관적인 성능 | get_historical_features()로 시점 고정 |
| 온라인 저장소 업데이트 잊음 | 서빙 시 오래된 피처값 사용 | 피처 materialize 자동화 |
| 피처 TTL 없음 | 오래된 피처가 서빙에 사용됨 | FeatureView에 TTL 설정 |
| 피처 의존성 추적 없음 | 업스트림 변경이 모델에 미치는 영향 모름 | 데이터 리니지 기록 |

## AI 활용 팁

```
# AI에게 이렇게 요청하세요:
"Feast 피처 스토어를 사용해서 사용자 구매 예측 모델용 피처를 정의해줘.
user_id 엔터티,
7일 구매 횟수 + 평균 세션 시간 피처,
학습은 get_historical_features로 시점 일치 조인,
서빙은 get_online_features로 실시간 조회"

# AI 결과물 검증 체크포인트:
# - 학습과 서빙이 같은 FeatureView를 쓰는가?
# - 학습 시 시점 일치 조인(get_historical_features)을 사용하는가?
# - FeatureView에 TTL이 설정되어 있는가?
# - 온라인 저장소 업데이트(materialize) 자동화가 있는가?
# - 피처 계산 로직이 중복 구현되지 않았는가?
```

## 운영 체크리스트

- [ ] 피처 정의가 피처 뷰로 중앙화되어 학습/서빙이 공유한다
- [ ] 학습 데이터 추출 시 시점 일치 조인을 사용한다
- [ ] 온라인 저장소 업데이트가 자동화되어 있다
- [ ] 피처 TTL이 비즈니스 요구사항에 맞게 설정되어 있다
- [ ] 피처 변경 시 영향받는 모델 목록이 추적된다

## 처음 질문으로 돌아가기

- **학습-서빙 불일치란?** 학습 코드와 서빙 코드가 같은 피처 이름이지만 다른 로직으로 계산할 때 발생합니다. 오프라인 검증 성능이 좋아도 운영 성능이 낮은 원인 중 하나입니다.
- **온라인/오프라인 저장소의 역할은?** 오프라인 저장소(Parquet, BigQuery)는 대규모 학습 데이터 추출용입니다. 온라인 저장소(Redis, DynamoDB)는 낮은 지연 시간으로 서빙 시 실시간 피처 조회용입니다.
- **시점 일치 조인이 중요한 이유는?** 과거 특정 시점의 레이블에 미래 데이터를 붙이면 데이터 누수가 발생합니다. get_historical_features()는 각 엔터티의 이벤트 시점 이전 데이터만 붙여 누수를 방지합니다.

## 정리

바이브코딩에서 AI가 만들어 준 피처 코드에서 학습-서빙 일관성, 시점 일치 조인, 온라인 저장소 업데이트 자동화를 반드시 확인하세요. 피처 스토어의 핵심 가치는 저장이 아닌 학습과 서빙 간 피처 정의 일관성입니다. 다음 글에서는 운영 가능한 ML 시스템을 다룹니다.

## 참고 자료

- [Feast — Open Source Feature Store](https://docs.feast.dev/)
- [Chip Huyen — Feature Store Blog](https://huyenchip.com/2020/12/27/real-time-machine-learning.html)
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
- **바이브코딩을 위한 MLOps 기초 (9/10): 피처 스토어 (현재 글)**
- 바이브코딩을 위한 MLOps 기초 (10/10): 운영 가능한 ML 시스템
<!-- toc:end -->

Tags: 바이브코딩, MLOps, FeatureStore, Feast, DataScience
