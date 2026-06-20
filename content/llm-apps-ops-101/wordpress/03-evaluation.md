---
title: "바이브코딩을 위한 LLM 앱 운영 (3/6): LLM 출력 품질 평가"
series: llm-apps-ops-101
episode: 3
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLMOps
- Evaluation
- Python
- LLM
---

# 바이브코딩을 위한 LLM 앱 운영 (3/6): LLM 출력 품질 평가

이 글은 **바이브코딩을 위한 LLM 앱 운영** 시리즈의 세 번째 글입니다. 형식 오류와 품질 저하를 자동으로 감지하는 평가 레이어를 설계합니다.

---

"프롬프트 압축하고 저가 모델 라우팅 붙였더니 비용 40% 줄었습니다!" 슬랙에 이 메시지가 올라왔을 때, 진짜 어려운 부분은 비용 절감 자체가 아닙니다. 어려운 부분은 2주 뒤에 옵니다. "고객이 최근 답변이 예전보다 부실하다고 합니다." 비용을 줄인 시점과 품질이 떨어진 시점을 연결할 수 있는 팀은 빠르게 롤백합니다. 연결할 수 없는 팀은 2주 더 논의합니다.

바이브코딩으로 AI에게 "품질 평가 만들어줘"라고 하면 복잡한 평가 코드가 나올 수 있습니다. 운영 초기에는 형식 오류와 키워드 누락 같은 명백한 실패를 빠르게 거르는 규칙 레이어가 먼저입니다.

> "완벽한 품질 평가보다 명백한 실패를 빠르게 감지하는 것이 먼저입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. LLM 출력 품질을 코드로 자동 평가하는 방법이 있나요?
2. 형식 검증과 의미 품질 평가의 차이가 무엇인가요?
3. 평가 결과를 어떻게 모니터링 대시보드에 연결하나요?
4. 품질 평가가 실패율에 어떤 영향을 주나요?
5. LLM 기반 평가(LLM-as-judge)가 언제 필요한가요?

---

## 규칙 기반 평가기

```python
import re
from dataclasses import dataclass

@dataclass
class EvalResult:
    passed: bool
    score: float  # 0.0 ~ 1.0
    failures: list[str]

class RuleEvaluator:
    def __init__(self, rules: list[dict]):
        self.rules = rules

    def evaluate(self, response: str) -> EvalResult:
        failures = []
        for rule in self.rules:
            rule_type = rule["type"]
            if rule_type == "min_length" and len(response) < rule["value"]:
                failures.append(f"응답이 너무 짧습니다 ({len(response)} < {rule['value']}자)")
            elif rule_type == "max_length" and len(response) > rule["value"]:
                failures.append(f"응답이 너무 깁니다 ({len(response)} > {rule['value']}자)")
            elif rule_type == "contains" and rule["value"] not in response:
                failures.append(f"필수 키워드 누락: {rule['value']}")
            elif rule_type == "not_contains" and rule["value"] in response:
                failures.append(f"금지 패턴 발견: {rule['value']}")
            elif rule_type == "json_valid":
                try:
                    import json; json.loads(response)
                except json.JSONDecodeError:
                    failures.append("유효하지 않은 JSON 형식")

        score = 1.0 - (len(failures) / max(len(self.rules), 1))
        return EvalResult(passed=len(failures) == 0, score=score, failures=failures)
```

## 사용 예시

```python
evaluator = RuleEvaluator([
    {"type": "min_length", "value": 50},
    {"type": "max_length", "value": 2000},
    {"type": "contains", "value": "요약"},
    {"type": "not_contains", "value": "죄송합니다, 모르겠습니다"},
])

response = "이 문서의 핵심 요약: ..."
result = evaluator.evaluate(response)
print(result.passed, result.score, result.failures)
```

## 품질 이력 추적

```python
import json
from pathlib import Path

class QualityTracker:
    def __init__(self, log_file: str = "quality_log.jsonl"):
        self.log_file = Path(log_file)

    def record(self, call_id: str, endpoint: str, result: EvalResult):
        with open(self.log_file, "a") as f:
            f.write(json.dumps({
                "call_id": call_id,
                "endpoint": endpoint,
                "passed": result.passed,
                "score": result.score,
                "failures": result.failures,
            }) + "\n")

    def failure_rate(self, endpoint: str, last_n: int = 100) -> float:
        records = []
        with open(self.log_file) as f:
            for line in f:
                r = json.loads(line)
                if r["endpoint"] == endpoint:
                    records.append(r)
        recent = records[-last_n:]
        if not recent:
            return 0.0
        return sum(1 for r in recent if not r["passed"]) / len(recent)
```

---

## Before / After

| 항목 | Before (품질 평가 없음) | After (규칙 평가) |
|------|----------------------|-----------------|
| 형식 오류 감지 | 고객 불만 후 발견 | 자동 즉시 감지 |
| 품질 이력 | 없음 | 실패율 추적 |
| 비용-품질 연결 | 불가 | timestamp로 연결 |
| 평가 기준 | 암묵적 | rules 리스트로 명시 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 너무 엄격한 규칙 | 정상 응답 실패 | 규칙별 임계값 조정 |
| 평가 결과 미기록 | 이력 없음 | QualityTracker로 영속화 |
| 규칙만으로 의미 평가 | 형식은 맞지만 내용 부실 | LLM-as-judge 추가 |
| 실패율 임계값 없음 | 품질 저하 방치 | failure_rate > 10% 알람 |

---

## AI 활용 팁

```
LLM 응답 품질을 자동으로 평가하는 RuleEvaluator를 만들어줘.
규칙 유형: min_length, max_length, contains, not_contains, json_valid.
각 호출 결과를 QualityTracker로 JSONL에 기록하고, 엔드포인트별 실패율을 계산해줘.
실패율이 10% 초과 시 경고를 반환하는 로직도 포함해줘.
```

---

## 체크리스트

- [ ] RuleEvaluator(5가지 규칙 유형)
- [ ] EvalResult(passed, score, failures)
- [ ] QualityTracker(JSONL 저장)
- [ ] 엔드포인트별 실패율 계산
- [ ] 실패율 10% 초과 알람
- [ ] 규칙 설정 외부화(YAML)

---

## 처음 질문으로 돌아가기

"품질이 나빠졌다는 걸 어떻게 알 수 있나요?" — 규칙 평가기가 각 응답을 검사하고, QualityTracker가 실패율을 누적합니다. 비용 최적화를 배포한 타임스탬프와 실패율 증가 시점을 비교하면 원인을 찾을 수 있습니다.

---

## 정리

- 규칙 기반 평가기로 형식 오류와 키워드 누락을 자동 감지한다
- QualityTracker로 평가 결과를 영속화하고 엔드포인트별 실패율을 추적한다
- 실패율이 10%를 초과하면 알람을 발생시킨다
- 의미 품질이 중요한 경우 LLM-as-judge를 추가로 고려한다

---

## 참고 자료

- [LangSmith Evaluation](https://docs.smith.langchain.com/evaluation)
- [RAGAS RAG 평가](https://docs.ragas.io/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 규칙 기반 평가기
- 사용 예시
- 품질 이력 추적
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLMOps, Evaluation, Python, LLM
