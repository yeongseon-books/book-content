---
title: "바이브코딩을 위한 LLM 앱 운영 (5/6): LLM 앱 배포 전략"
series: llm-apps-ops-101
episode: 5
language: ko
targets:
  wordpress: true
tags:
- 바이브코딩
- LLMOps
- Deployment
- Python
- LLM
---

# 바이브코딩을 위한 LLM 앱 운영 (5/6): LLM 앱 배포 전략

이 글은 **바이브코딩을 위한 LLM 앱 운영** 시리즈의 다섯 번째 글입니다. 모델·프롬프트·보안 규칙을 버전 세트로 관리하고 안전하게 배포하는 전략을 다룹니다.

---

보안 규칙까지 붙였는데, 배포 직후 3분간 구버전 인스턴스가 살아 있었습니다. 그 3분 동안 신규 보안 규칙이 적용되지 않은 상태로 트래픽을 받았고, 프롬프트 인젝션 한 건이 그 틈을 뚫었습니다. 코드는 완벽했습니다 — 배포 과정이 문제였습니다.

LLM 앱 배포는 코드 배포가 아닙니다. 모델 버전, 프롬프트, 보안 규칙이 한 번에 교체되어야 합니다. 바이브코딩으로 AI에게 "배포 스크립트 만들어줘"라고 하면 코드 배포 스크립트가 나옵니다. LLM 버전 세트 개념과 카나리 배포, 롤백 전략을 모르면 배포 과정에서 취약점이 생깁니다.

> "LLM 앱 배포는 코드가 아닌 버전 세트 전환입니다."

---

**이 글을 읽기 전에 스스로 답해보세요:**

1. 모델·프롬프트·보안 규칙을 하나의 버전 세트로 관리하는 방법이 있나요?
2. 카나리 배포와 블루-그린 배포의 차이가 무엇인가요?
3. 배포 후 품질이 저하되면 어떻게 자동 롤백하나요?
4. 프롬프트 버전을 코드와 별도로 관리해야 하는 이유가 무엇인가요?
5. 배포 중 트래픽 분할을 어떻게 구현하나요?

---

## 버전 세트 관리

```python
from dataclasses import dataclass
import yaml
from pathlib import Path

@dataclass
class LLMVersionSet:
    version: str
    model: str
    prompt_template: str
    security_rules: list[str]
    eval_rules: list[dict]
    created_at: str

def load_version_set(version_dir: str) -> LLMVersionSet:
    config = yaml.safe_load(Path(f"{version_dir}/config.yaml").read_text())
    prompt = Path(f"{version_dir}/system_prompt.txt").read_text()
    return LLMVersionSet(
        version=config["version"],
        model=config["model"],
        prompt_template=prompt,
        security_rules=config["security_rules"],
        eval_rules=config["eval_rules"],
        created_at=config["created_at"],
    )
```

## 카나리 배포

```python
import random

class CanaryRouter:
    def __init__(self, stable_version: LLMVersionSet, canary_version: LLMVersionSet, canary_ratio: float = 0.1):
        self.stable = stable_version
        self.canary = canary_version
        self.canary_ratio = canary_ratio
        self.metrics = {"stable": {"calls": 0, "failures": 0}, "canary": {"calls": 0, "failures": 0}}

    def route(self) -> tuple[LLMVersionSet, str]:
        if random.random() < self.canary_ratio:
            return self.canary, "canary"
        return self.stable, "stable"

    def record_result(self, lane: str, failed: bool):
        self.metrics[lane]["calls"] += 1
        if failed:
            self.metrics[lane]["failures"] += 1

    def canary_failure_rate(self) -> float:
        m = self.metrics["canary"]
        return m["failures"] / max(m["calls"], 1)

    def should_rollback(self, threshold: float = 0.05) -> bool:
        return self.canary_failure_rate() > threshold
```

## 자동 롤백

```python
class DeploymentController:
    def __init__(self, router: CanaryRouter):
        self.router = router
        self.current_version = "stable"

    def step(self) -> dict:
        if self.router.should_rollback():
            self.current_version = "stable"
            return {
                "action": "rollback",
                "reason": f"카나리 실패율 {self.router.canary_failure_rate():.1%} 초과",
            }

        # 카나리 비율 점진적 증가
        if self.router.canary_ratio < 1.0:
            self.router.canary_ratio = min(self.router.canary_ratio * 2, 1.0)
            return {"action": "promote", "canary_ratio": self.router.canary_ratio}

        # 완전 전환
        return {"action": "complete"}
```

---

## Before / After

| 항목 | Before (코드만 배포) | After (버전 세트 배포) |
|------|--------------------|-----------------------|
| 프롬프트 버전 | 코드에 하드코딩 | 버전 세트 파일 |
| 배포 일관성 | 컴포넌트별 순차 배포 | 버전 세트 원자적 전환 |
| 품질 저하 감지 | 고객 불만 후 | 카나리 자동 롤백 |
| 롤백 | 수동 코드 복원 | canary_ratio=0 즉시 |

---

## 자주 하는 실수

| 실수 | 결과 | 해결책 |
|------|------|--------|
| 프롬프트 코드 내 하드코딩 | 배포마다 재배포 | 버전 세트 YAML 분리 |
| 즉시 100% 전환 | 장애 전체 노출 | 카나리 10%부터 시작 |
| 롤백 기준 없음 | 품질 저하 방치 | 실패율 임계값 설정 |
| 버전 세트 검증 없음 | 잘못된 설정 배포 | 배포 전 config 검증 |

---

## AI 활용 팁

```
LLM 앱 버전 세트(모델+프롬프트+보안 규칙)를 YAML로 관리하는 시스템을 만들어줘.
CanaryRouter로 10%를 카나리 버전에 보내고, 실패율 5% 초과 시 자동 롤백해줘.
DeploymentController로 카나리 비율을 점진적으로 높이고, 완전 전환까지 자동화해줘.
```

---

## 체크리스트

- [ ] LLMVersionSet dataclass 정의
- [ ] YAML 버전 세트 파일 구조
- [ ] CanaryRouter(10% 카나리)
- [ ] should_rollback(실패율 5% 임계값)
- [ ] DeploymentController(점진적 증가)
- [ ] 배포 전 config 검증

---

## 처음 질문으로 돌아가기

"프롬프트가 바뀌면 그냥 배포하면 되는 거 아닌가요?" — 프롬프트, 모델, 보안 규칙이 함께 교체되어야 일관성이 보장됩니다. 카나리 배포로 작은 비율부터 트래픽을 보내고, 품질 지표를 모니터링하다가 문제가 생기면 즉시 롤백하는 구조가 안전한 배포입니다.

---

## 정리

- 모델·프롬프트·보안 규칙을 버전 세트(YAML)로 통합 관리한다
- 카나리 배포로 10%부터 시작해 점진적으로 비율을 높인다
- 카나리 실패율이 5%를 초과하면 자동 롤백한다
- 배포 전 버전 세트 config 유효성을 반드시 검증한다

---

## 참고 자료

- [카나리 배포 패턴](https://martinfowler.com/bliki/CanaryRelease.html)
- [LangServe 배포](https://python.langchain.com/docs/langserve/)

---

<!-- wp:heading -->
**목차**
<!-- /wp:heading -->

<!-- wp:list -->
- 버전 세트 관리
- 카나리 배포
- 자동 롤백
- Before / After
- 자주 하는 실수
- AI 활용 팁
- 체크리스트
<!-- /wp:list -->

Tags: 바이브코딩, LLMOps, Deployment, Python, LLM
