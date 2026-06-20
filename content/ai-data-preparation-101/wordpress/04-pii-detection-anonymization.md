---
title: "바이브코딩을 위한 AI 데이터 준비 (4/10): PII 탐지와 익명화"
series: ai-data-preparation-101
episode: 4
language: ko
tags:
- PII Detection
- Anonymization
- Presidio
- Privacy
- 바이브코딩
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 데이터 준비 (4/10): PII 탐지와 익명화

이 글은 **바이브코딩을 위한 AI 데이터 준비** 시리즈의 네 번째 글입니다.

---

바이브코딩으로 실제 고객 데이터나 사용자 대화를 AI 학습에 쓰려고 할 때 반드시 거쳐야 하는 단계가 있습니다. 바로 PII(개인식별정보) 탐지와 익명화입니다. 이름, 이메일, 전화번호, 주민등록번호 같은 개인정보가 학습 데이터에 포함되면 모델이 이를 학습하고 나중에 출력할 수 있습니다.

PII 처리는 단순히 "이름을 지우는 것"이 아닙니다. 탐지 방법(정규식 vs NER 모델), 익명화 방법(삭제 vs 마스킹 vs 가명화 vs 합성), 그리고 처리 결과를 감사할 수 있는 로그가 필요합니다.

> "PII가 포함된 데이터로 학습한 모델은 개인정보를 기억하고 출력합니다. 이는 기술 문제가 아니라 법적, 윤리적 문제입니다."

## 이 글에서 다룰 질문

1. PII를 탐지하는 두 가지 방법(정규식, NER)은 어떻게 다른가요?
2. 삭제, 마스킹, 가명화, 합성 중 어떤 익명화 방법을 선택해야 하나요?
3. Presidio로 PII를 탐지하는 방법은?
4. PII 처리 감사 로그는 왜 필요하고 어떻게 만드나요?
5. 준식별자(quasi-identifier) 위험이란 무엇인가요?

---

## PII 카테고리와 위험 수준

| PII 유형 | 예시 | 위험 수준 | 처리 방법 |
|----------|------|----------|----------|
| 직접 식별자 | 이름, 주민번호, 이메일 | 매우 높음 | 반드시 처리 |
| 연락처 | 전화번호, 주소 | 높음 | 반드시 처리 |
| 금융 정보 | 카드번호, 계좌번호 | 높음 | 반드시 처리 |
| 준식별자 | 나이+지역+직업 조합 | 중간 | 조합 위험 확인 |

## 1단계: 정규식으로 명확한 PII 탐지

```python
import re

PATTERNS = {
    "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
    "phone_kr": r'0\d{1,2}[-.\s]?\d{3,4}[-.\s]?\d{4}',
    "resident_id": r'\d{6}-[1-4]\d{6}',
    "credit_card": r'\b\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}\b',
}

def detect_regex(text: str) -> list[dict]:
    """정규식으로 PII를 탐지합니다."""
    findings = []
    for pii_type, pattern in PATTERNS.items():
        for match in re.finditer(pattern, text):
            findings.append({
                "type": pii_type,
                "value": match.group(),
                "start": match.start(),
                "end": match.end()
            })
    return findings
```

## 2단계: Presidio NER로 고급 PII 탐지

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

def detect_ner(text: str, language: str = "en") -> list[dict]:
    """Presidio NER로 이름, 조직, 위치 등을 탐지합니다."""
    results = analyzer.analyze(text=text, language=language)
    return [
        {
            "type": r.entity_type,
            "start": r.start,
            "end": r.end,
            "score": r.score
        }
        for r in results
    ]
```

## 익명화 방법 4가지

```python
def redact(text: str, findings: list[dict]) -> str:
    """탐지된 PII를 완전히 삭제합니다: '홍길동' → '[REDACTED]'"""
    for finding in sorted(findings, key=lambda x: x["start"], reverse=True):
        text = text[:finding["start"]] + f"[{finding['type']}_REDACTED]" + text[finding["end"]:]
    return text

def mask(text: str, findings: list[dict]) -> str:
    """PII의 일부만 마스킹합니다: '010-1234-5678' → '010-****-5678'"""
    for finding in sorted(findings, key=lambda x: x["start"], reverse=True):
        original = finding["value"]
        visible = max(len(original) // 4, 2)
        masked = original[:visible] + "*" * (len(original) - visible * 2) + original[-visible:]
        text = text[:finding["start"]] + masked + text[finding["end"]:]
    return text

def pseudonymize(text: str, findings: list[dict], mapping: dict = None) -> tuple[str, dict]:
    """PII를 일관된 가명으로 대체합니다: '홍길동' → 'Person_001'"""
    if mapping is None:
        mapping = {}
    counter = {"PERSON": 0, "EMAIL": 0, "PHONE": 0}

    for finding in sorted(findings, key=lambda x: x["start"], reverse=True):
        original = finding["value"]
        if original not in mapping:
            pii_type = finding["type"]
            counter[pii_type] = counter.get(pii_type, 0) + 1
            mapping[original] = f"{pii_type}_{counter[pii_type]:03d}"
        text = text[:finding["start"]] + mapping[original] + text[finding["end"]:]
    return text, mapping
```

## PII 처리 감사 로그

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class PIIAuditRow:
    doc_id: str
    pii_type: str
    method_used: str  # redact, mask, pseudonymize, synthesize
    was_found: bool
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.utcnow().isoformat()

def anonymize_with_audit(text: str, doc_id: str, method: str = "redact", sample_rate: float = 0.1):
    """PII를 익명화하고 감사 로그를 기록합니다."""
    findings = detect_regex(text) + detect_ner(text)
    audit_rows = []

    if findings:
        anonymized = redact(text, findings) if method == "redact" else mask(text, findings)
        for finding in findings:
            audit_rows.append(PIIAuditRow(
                doc_id=doc_id,
                pii_type=finding["type"],
                method_used=method,
                was_found=True
            ))
    else:
        anonymized = text

    return anonymized, audit_rows
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 정규식만 사용 | 이름, 조직명 등 놓침 | 정규식 + NER 두 단계 모두 적용 |
| 감사 로그 없음 | 얼마나 처리됐는지 추적 불가 | 모든 PII 탐지/처리를 기록 |
| 준식별자 무시 | 조합으로 개인 식별 가능 | 나이+지역+직업 같은 조합 위험 확인 |
| 익명화 후 검증 없음 | PII가 남아 있을 수 있음 | 처리 후 재탐지로 검증 |

## AI 팁

익명화 방법 선택 기준은 "이 데이터를 나중에 어떻게 쓸 것인가"입니다. 학습 데이터로만 쓴다면 redact(완전 삭제)가 가장 안전합니다. 데이터 분석이나 디버깅에도 써야 한다면 pseudonymize(가명화)로 일관성을 유지하면서 개인을 보호합니다.

준식별자 위험을 확인하려면 나이 + 지역 + 직업 조합처럼 개별적으로는 문제없지만 조합하면 특정 개인을 식별할 수 있는 경우를 찾아야 합니다.

```python
def quasi_identifier_risk(df, quasi_columns: list[str], threshold: int = 5) -> list[dict]:
    """준식별자 조합으로 소규모 그룹을 찾습니다."""
    groups = df.groupby(quasi_columns).size().reset_index(name='count')
    risky = groups[groups['count'] <= threshold]
    return risky.to_dict('records')
```

## 체크리스트

- [ ] 정규식과 NER 두 단계로 PII를 탐지한다
- [ ] 데이터 사용 목적에 맞는 익명화 방법을 선택했다
- [ ] 모든 PII 처리를 감사 로그에 기록한다
- [ ] 익명화 후 재탐지로 PII 잔존 여부를 확인한다
- [ ] 준식별자 조합 위험을 점검했다

## 처음 질문으로 돌아가기

**정규식 vs NER 탐지 차이는?** 정규식은 이메일, 전화번호 같은 패턴이 명확한 PII를 빠르게 찾습니다. NER은 이름, 조직명, 위치처럼 문맥이 필요한 PII를 찾습니다. 둘을 함께 써야 합니다.

**익명화 방법 선택 기준은?** 학습 데이터에는 redact(완전 삭제), 분석 데이터에는 pseudonymize(가명화), 부분 표시가 필요하면 mask(마스킹).

**Presidio 사용 방법은?** `AnalyzerEngine`으로 탐지하고 `AnonymizerEngine`으로 익명화합니다. 한국어 지원을 위해 커스텀 recognizer를 추가해야 합니다.

**감사 로그가 필요한 이유는?** "이 데이터에서 얼마나 많은 PII를 처리했는가"를 GDPR 같은 규정 준수 보고에 사용합니다.

**준식별자 위험이란?** 개별 항목은 PII가 아니지만 조합하면 특정 개인을 식별할 수 있는 정보입니다. 나이 45, 서울 강남, 정형외과 의사 — 각각은 PII가 아니지만 조합하면 특정 인물을 특정할 수 있습니다.

## 정리

PII 처리는 학습 데이터 준비에서 건너뛸 수 없는 단계입니다. 정규식으로 패턴 기반 PII를 잡고, Presidio NER로 문맥 기반 PII를 찾은 뒤, 목적에 맞는 익명화 방법을 적용하고, 모든 처리를 감사 로그에 기록해야 합니다.

다음 글에서는 텍스트를 모델 입력 형식으로 변환하는 **Tokenization과 Chunking**을 다룹니다.

## 참고 자료

- [AI 데이터 준비 원문: PII 탐지와 익명화](../ko/04-pii-detection-anonymization.md)
- [Microsoft Presidio](https://microsoft.github.io/presidio/)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 데이터 준비 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
2. [바이브코딩을 위한 AI 데이터 준비 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
3. [바이브코딩을 위한 AI 데이터 준비 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
4. **바이브코딩을 위한 AI 데이터 준비 (4/10): PII 탐지와 익명화 (현재 글)**
5. [바이브코딩을 위한 AI 데이터 준비 (5/10): Tokenization과 Chunking](./05-tokenization-chunking.md)
6. [바이브코딩을 위한 AI 데이터 준비 (6/10): 데이터 품질 필터링](./06-quality-filtering.md)
7. [바이브코딩을 위한 AI 데이터 준비 (7/10): 합성 데이터 생성](./07-synthetic-data-generation.md)
8. [바이브코딩을 위한 AI 데이터 준비 (8/10): 데이터 증강 기법](./08-data-augmentation.md)
9. [바이브코딩을 위한 AI 데이터 준비 (9/10): 학습/평가/테스트 분할](./09-train-eval-test-splitting.md)
10. [바이브코딩을 위한 AI 데이터 준비 (10/10): 프로덕션 데이터 파이프라인](./10-production-data-pipeline.md)
<!-- toc:end -->

Tags: PII Detection, Anonymization, Presidio, Privacy, 바이브코딩
