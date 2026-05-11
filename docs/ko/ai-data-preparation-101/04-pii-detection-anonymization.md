---
title: 학습 데이터 PII 탐지와 익명화
series: ai-data-preparation-101
episode: 4
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Data Preparation
- PII
- Anonymization
- Privacy
last_reviewed: '2026-05-03'
seo_description: LLM이 학습 데이터에 있던 이메일 주소나 전화번호를 그대로 출력해 버리는 사고는 이미 여러 사례로 보고됐습니다.
---

# 학습 데이터 PII 탐지와 익명화

> AI Data Preparation 101 시리즈 (4/10)

---

## "학습 데이터에 PII가 있으면 안 되는 거죠?"

LLM이 학습 데이터에 있던 이메일 주소나 전화번호를 그대로 출력해 버리는 사고는 이미 여러 사례로 보고됐습니다. Carlini et al.(2021)의 "Extracting Training Data from Large Language Models" 논문은 GPT-2에서 실제 사람의 이름과 연락처가 추출되는 것을 보여줬습니다. 학습 단계의 PII는 inference 단계에서 leak됩니다.

PII anonymization은 단순한 정규식 매칭이 아닙니다. 4단계 파이프라인이 필요합니다.

1. **Detection**: 어떤 텍스트가 PII를 포함하는지 식별
2. **Classification**: PII 종류 판별 (email, phone, SSN, 이름 등)
3. **Anonymization**: 제거(redact) 또는 가명화(pseudonymize)
4. **Audit**: 처리 결과를 기록하고 sampling으로 검증

## PII 종류 — 무엇을 잡아야 하는가

production에서 다루는 PII는 보통 다음 카테고리입니다.

| Category | 예시 | 위험도 |
| --- | --- | --- |
| Direct identifier | email, phone, SSN, 신용카드 번호 | High |
| Quasi-identifier | 이름, 주소, 생년월일, 직장명 | Medium |
| Sensitive attribute | 의료 정보, 종교, 정치 성향 | High |
| Indirect identifier | IP, device ID, browser fingerprint | Medium |

GDPR Article 4와 PIPA(개인정보보호법) 제2조는 "다른 정보와 결합하여 식별 가능한 정보"까지 PII로 봅니다. quasi-identifier 3~4개가 결합되면 individual을 특정할 수 있다는 연구(Sweeney, 2000)는 유명합니다.

## Stage 1: Regex 기반 detection

가장 빠르고, 가장 false negative가 많은 방법입니다. 하지만 1차 layer로는 필수입니다.

```python
import re

PATTERNS = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "phone_kr": re.compile(r"\b01[016789]-?\d{3,4}-?\d{4}\b"),
    "phone_intl": re.compile(r"\+\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{1,4}[\s-]?\d{1,9}"),
    "ssn_us": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "rrn_kr": re.compile(r"\b\d{6}-?[1-4]\d{6}\b"),  # 주민등록번호
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

def detect_regex(text: str) -> dict[str, list[str]]:
    return {k: p.findall(text) for k, p in PATTERNS.items() if p.search(text)}

# 테스트
sample = "Contact: alice@example.com or 010-1234-5678. RRN 900101-1234567"
print(detect_regex(sample))
```

regex만으로는 이름이나 주소 같은 자연어 PII를 못 잡습니다. 그래서 NER(Named Entity Recognition)를 추가합니다.

## Stage 2: NER 기반 detection

`spaCy`나 Microsoft의 `Presidio`를 쓰면 이름, 조직, 위치를 잡을 수 있습니다.

```python
# pip install presidio-analyzer presidio-anonymizer
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()  # 영어 default; ko는 spaCy ko 모델 필요
anonymizer = AnonymizerEngine()

def detect_ner(text: str, language: str = "en") -> list[dict]:
    results = analyzer.analyze(
        text=text,
        entities=["EMAIL_ADDRESS", "PHONE_NUMBER", "PERSON",
                  "LOCATION", "CREDIT_CARD", "IP_ADDRESS"],
        language=language,
    )
    return [{"type": r.entity_type, "start": r.start, "end": r.end,
             "score": r.score, "text": text[r.start:r.end]} for r in results]

text = "John Smith works at Acme Corp in Seoul. Email: john@acme.com"
for hit in detect_ner(text):
    print(hit)
```

Presidio는 confidence score를 제공합니다. score < 0.6이면 false positive 가능성이 높으니 별도 검토 큐로 보내거나 conservative하게 redact합니다.

## Stage 3: Anonymization 기법 4가지

PII를 발견한 다음 처리 방법은 4가지가 있습니다.

```python
import hashlib
import secrets

def redact(text: str, hits: list[dict]) -> str:
    """완전 제거: 가장 안전, context 손실"""
    out = text
    for h in sorted(hits, key=lambda x: -x["start"]):
        out = out[:h["start"]] + f"[{h['type']}]" + out[h["end"]:]
    return out

def mask(text: str, hits: list[dict], keep: int = 4) -> str:
    """일부만 마스킹: card last4 같은 케이스"""
    out = text
    for h in sorted(hits, key=lambda x: -x["start"]):
        original = text[h["start"]:h["end"]]
        masked = "*" * (len(original) - keep) + original[-keep:]
        out = out[:h["start"]] + masked + out[h["end"]:]
    return out

_PEPPER = secrets.token_hex(16)  # process-local secret

def pseudonymize(text: str, hits: list[dict]) -> str:
    """동일 입력 -> 동일 가명. analytics 가능, reversible 아님"""
    out = text
    for h in sorted(hits, key=lambda x: -x["start"]):
        original = text[h["start"]:h["end"]]
        token = hashlib.sha256(
            (_PEPPER + original).encode()
        ).hexdigest()[:12]
        out = out[:h["start"]] + f"<{h['type']}_{token}>" + out[h["end"]:]
    return out

def synthesize(text: str, hits: list[dict], faker) -> str:
    """가짜 데이터로 치환: 학습 데이터 분포 보존"""
    out = text
    gen = {"PERSON": faker.name, "EMAIL_ADDRESS": faker.email,
           "PHONE_NUMBER": faker.phone_number}
    for h in sorted(hits, key=lambda x: -x["start"]):
        replacement = gen.get(h["type"], lambda: "[REDACTED]")()
        out = out[:h["start"]] + replacement + out[h["end"]:]
    return out
```

선택 기준:

- **Redact**: training data 안전이 최우선일 때
- **Mask**: 일부 식별자(예: card last 4 digits)를 보존해야 할 때
- **Pseudonymize**: 같은 사용자의 행동 패턴을 추적해야 하지만 ID는 숨기고 싶을 때
- **Synthesize**: 데이터 분포(이름의 길이, 이메일 형식)를 학습 데이터에 보존해야 할 때

## Stage 4: Audit과 sampling 검증

PII 처리 결과를 매번 기록하고, 일부를 사람이 검토합니다.

```python
import json
import random
from datetime import datetime, timezone

def anonymize_with_audit(rows: list[dict], audit_path: str,
                         sample_rate: float = 0.01) -> list[dict]:
    out = []
    audit = []
    for row in rows:
        text = row["text"]
        hits = detect_ner(text) + sum(
            [[{"type": k, "start": m.start(), "end": m.end()}
              for m in PATTERNS[k].finditer(text)]
             for k in PATTERNS], []
        )
        clean = redact(text, hits)
        out.append({**row, "text": clean})
        audit.append({
            "row_id": row.get("id"),
            "pii_count": len(hits),
            "pii_types": list({h["type"] for h in hits}),
            "char_reduction": len(text) - len(clean),
            "ts": datetime.now(timezone.utc).isoformat(),
        })
    # human review를 위한 random sample
    sample = random.sample(rows, max(1, int(len(rows) * sample_rate)))
    with open(audit_path, "w") as f:
        json.dump({"audit": audit, "review_sample": sample}, f, ensure_ascii=False)
    return out
```

**audit log는 PII 자체를 저장하지 않습니다.** count, type, char reduction만 기록합니다. review sample은 별도 access-controlled 위치에 보관합니다.

## 한국어 텍스트의 추가 위험

한국어 데이터는 영어와 다른 함정이 있습니다.

- **주민등록번호 (RRN)**: 13자리 숫자 패턴(`900101-1234567`). regex로 잡힙니다.
- **사업자등록번호**: 10자리(`123-45-67890`). 회사 정보지만 일부 자영업자에게는 PII입니다.
- **자동차 번호판**: `12가3456` 같은 패턴.
- **이름**: 한국어 이름은 2~4자가 대부분이라 일반 NER로 잡기 어려운 경우가 있어 별도 ko 모델이 필요합니다.

## 흔한 실수 5가지

1. **Regex만 의존**: 이름, 주소 같은 자연어 PII를 놓칩니다. 반드시 NER stage를 추가합니다.
2. **Pseudonymize에 동일 hash 사용**: pepper 없이 sha256만 쓰면 rainbow table 공격 가능. process-local secret을 추가합니다.
3. **Audit log에 원문 PII 저장**: audit 자체가 leak source가 됩니다. count와 type만 기록합니다.
4. **한국어 데이터에 영어 NER 모델 사용**: ko 이름은 거의 다 missed. spaCy ko 모델 또는 Korean NER 모델을 명시적으로 로드합니다.
5. **Sample review 단계 생략**: 자동화만 믿으면 false negative를 영원히 못 잡습니다. 1% 정도라도 사람 검토를 유지합니다.

## 핵심 요약

- PII 처리는 4단계입니다: Detection → Classification → Anonymization → Audit.
- Regex(빠른 1차)와 NER(자연어 PII)를 함께 사용합니다. 한 가지로는 부족합니다.
- Anonymization 기법 4가지(redact / mask / pseudonymize / synthesize) 중 use case에 맞는 것을 선택합니다.
- Pseudonymize는 process-local pepper를 반드시 추가하고, audit log에는 PII 자체를 저장하지 않습니다.
- 한국어 데이터는 RRN, 사업자번호, 한국어 이름 NER을 별도로 처리해야 합니다.
- Sampling을 통한 human review를 유지해야 false negative가 누적되지 않습니다.
- 다음 편(5편)은 tokenization과 chunking입니다.
## 참고 자료

- [Microsoft Presidio - PII detection and anonymization](https://microsoft.github.io/presidio/)
- [Extracting Training Data from Large Language Models (Carlini et al., 2021)](https://arxiv.org/abs/2012.07805)
- [k-anonymity: A model for protecting privacy (Sweeney, 2002)](https://dataprivacylab.org/dataprivacy/projects/kanonymity/)
- [GDPR Article 4 - Definitions](https://gdpr-info.eu/art-4-gdpr/)
