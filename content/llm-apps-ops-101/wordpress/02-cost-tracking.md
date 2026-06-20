---
title: "바이브코딩을 위한 LLM 앱 운영 (2/6): LLM 비용 추적과 최적화"
series: llm-apps-ops-101
episode: 2
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLMOps
- Cost Tracking
- Python
- LLM
---

# 바이브코딩을 위한 LLM 앱 운영 (2/6): LLM 비용 추적과 최적화

이 글은 **바이브코딩을 위한 LLM 앱 운영** 시리즈의 두 번째 글입니다. 호출별 토큰과 비용을 기록하고, 엔드포인트·사용자별 비용 분석과 최적화 전략을 다룹니다.

---

"이번 달 OpenAI 청구서가 왜 3배죠?" 슬랙에 이 메시지가 올라왔을 때, 가장 어려운 부분은 금액 자체가 아닙니다. 어렵 부분은 그 다음 질문입니다. "어떤 엔드포인트에서 많이 썼지?", "언제부터 늘었지?", "누가 긴 프롬프트를 배포했지?" 호출 단위 비용 기록이 없으면, 이 질문들에 답할 방법이 없습니다.

바이브코딩으로 AI에게 "비용 추적해줘"라고 하면 기본 계산 코드가 나옵니다. 엔드포인트별, 사용자별, 시간대별 비용을 집계하고 알람을 설정하는 구조를 모르면 비용이 폭발해도 발견이 늦습니다.

> "호출 단위 비용 기록이 있어야 최적화가 추측이 아닌 검증이 됩니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 비용을 엔드포인트별로 집계하려면 어떤 필드가 필요한가요?
2. 일일 비용 한도를 초과하면 어떻게 알림을 받나요?
3. 프롬프트 압축이 품질에 영향을 주지 않는지 어떻게 검증하나요?
4. 모델 라우팅(비싼 모델 vs 저렴한 모델)을 어떻게 구현하나요?
5. 비용 증가가 버그인지 사용량 증가인지 어떻게 구분하나요?

---

## 비용 레코드 구조

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CostRecord:
    timestamp: str
    endpoint: str
    user_id: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: float
```

## 비용 집계기

```python
from collections import defaultdict
import json
from pathlib import Path

class CostTracker:
    def __init__(self, log_file: str = "cost_records.jsonl"):
        self.log_file = Path(log_file)
        self._daily: dict = defaultdict(float)  # date → cost

    def record(self, record: CostRecord):
        date = record.timestamp[:10]
        self._daily[date] += record.cost_usd

        with open(self.log_file, "a") as f:
            f.write(json.dumps({
                "timestamp": record.timestamp,
                "endpoint": record.endpoint,
                "user_id": record.user_id,
                "model": record.model,
                "prompt_tokens": record.prompt_tokens,
                "completion_tokens": record.completion_tokens,
                "cost_usd": record.cost_usd,
            }) + "\n")

    def daily_total(self, date: str) -> float:
        return self._daily.get(date, 0.0)

    def by_endpoint(self) -> dict:
        totals = defaultdict(float)
        with open(self.log_file) as f:
            for line in f:
                r = json.loads(line)
                totals[r["endpoint"]] += r["cost_usd"]
        return dict(totals)
```

## 비용 알람

```python
class CostAlarm:
    def __init__(self, tracker: CostTracker, daily_limit: float = 10.0):
        self.tracker = tracker
        self.daily_limit = daily_limit

    def check(self, date: str) -> dict:
        current = self.tracker.daily_total(date)
        ratio = current / self.daily_limit
        return {
            "date": date,
            "current_usd": current,
            "limit_usd": self.daily_limit,
            "ratio": ratio,
            "alert": ratio >= 0.8,  # 80% 초과 시 경고
        }
```

## 모델 라우팅

```python
def route_model(prompt_tokens: int, requires_reasoning: bool = False) -> str:
    """비용 vs 품질 기반 모델 선택"""
    if requires_reasoning:
        return "gpt-4o"
    if prompt_tokens < 1000:
        return "gpt-4o-mini"
    return "gpt-4o-mini"  # 긴 프롬프트도 mini로 처리
```

---

## Before / After

| 항목 | Before (비용 미추적) | After (비용 추적) |
|------|--------------------|--------------------|
| 비용 급증 원인 | 청구서 확인 후 추측 | 엔드포인트별 즉시 파악 |
| 모델 선택 | 하나의 모델로 통일 | 복잡도별 라우팅 |
| 일일 한도 | 없음 | 알람으로 자동 감지 |
| 최적화 효과 | 측정 불가 | 전후 비용 비교 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 월 단위만 추적 | 급증 시점 파악 불가 | 일별 집계 |
| 엔드포인트 미기록 | 원인 불명 | endpoint 필드 필수 |
| 한도 없음 | 비용 폭발 | CostAlarm 설정 |
| 비용=품질 희생 | 고객 불만 | 라우팅 전후 품질 비교 |

---

## AI 활용 팁

```
LLM API 호출별 비용을 CostRecord로 기록하고, 엔드포인트별로 집계하는 CostTracker를 만들어줘.
일일 비용이 한도의 80%를 초과하면 경고를 반환하는 CostAlarm도 만들어줘.
요청 복잡도에 따라 gpt-4o-mini와 gpt-4o를 자동으로 선택하는 route_model 함수도 포함해줘.
```

---

## 체크리스트

- [ ] CostRecord dataclass 정의
- [ ] CostTracker(JSONL 저장 + 집계)
- [ ] 엔드포인트별 비용 집계
- [ ] CostAlarm(80% 임계값 경고)
- [ ] route_model(복잡도별 모델 선택)
- [ ] 일별 비용 리포트

---

## 처음 질문으로 돌아가기

"비용이 갑자기 올랐는데 어디서 나온지 모르겠어요" — 호출별로 endpoint, model, tokens, cost_usd를 기록해야 합니다. by_endpoint()로 어느 기능에서 비용이 가장 많이 나오는지 바로 파악할 수 있습니다. CostAlarm으로 폭발 전에 경고를 받으세요.

---

## 정리

- 모든 LLM 호출에 endpoint, user_id, cost_usd를 기록한다
- 일별 집계로 비용 증가 시점을 정확히 파악한다
- CostAlarm으로 일일 한도 80% 초과 시 자동 경고를 받는다
- route_model로 요청 복잡도에 따라 최적 모델을 선택한다

---

## 참고 자료

- [OpenAI 요금 페이지](https://openai.com/pricing)
- [LLM 비용 최적화 가이드](https://platform.openai.com/docs/guides/production-best-practices)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 비용 레코드 구조
- 비용 집계기
- 비용 알람
- 모델 라우팅
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLMOps, Cost Tracking, Python, LLM
