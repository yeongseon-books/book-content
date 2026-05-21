---
title: "AI Data Preparation 101 (4/10): 학습 데이터 PII 탐지와 익명화"

series: ai-data-preparation-101

episode: 4

language: ko

status: publish-ready

targets:

  tistory: true

  medium: false

  mkdocs: true

  ebook: true

tags:
- Data Preparation
- PII
- Anonymization
- Privacy
last_reviewed: '2026-05-14'

seo_description: LLM이 학습 데이터에 있던 이메일 주소나 전화번호를 그대로 출력해 버리는 사고는 이미 여러 사례로 보고됐습니다.
---

# AI Data Preparation 101 (4/10): 학습 데이터 PII 탐지와 익명화

학습 데이터 안의 개인정보는 나중에 한 번 더 지우면 되는 문제가 아닙니다. 이메일 주소, 전화번호, 이름이 코퍼스에 들어간 순간부터 이후 캐시, 중간 산출물, 샘플링 로그, 파인튜닝 데이터셋 전체가 영향을 받습니다.

특히 LLM 시대에는 문제가 더 직접적입니다. 모델이 학습 시 본 문자열을 추론 시점에 재생산할 수 있기 때문입니다. 개인정보는 단순한 compliance 체크리스트가 아니라 실제 모델 출력 품질과 안전성 문제입니다.

현업에서는 regex만 믿거나, 반대로 NER만 붙여 놓고 끝내는 경우가 많습니다. 그러나 실제 운영 파이프라인은 탐지, 분류, 익명화, 감사라는 네 단계를 모두 가져야 하고, 각 단계의 false negative를 줄이는 별도 장치가 필요합니다.

이 글은 AI Data Preparation 101 시리즈의 4번째 글입니다. 여기서는 학습 데이터에서 PII를 탐지하고 익명화할 때 어떤 계층을 쌓아야 하는지, 그리고 감사 로그와 사람 검토를 어디에 붙여야 하는지 정리하겠습니다.

개인정보 처리는 “최대한 많이 가리자”가 아니라 사용 목적과 리스크에 맞게 적절한 기법을 고르는 문제이기도 합니다. redact, mask, pseudonymize, synthesize는 목적이 서로 다릅니다.

## 먼저 던지는 질문

- PII 처리 파이프라인을 detection, classification, anonymization, audit로 나누는 이유는 무엇일까요?
- regex만으로 잡히는 정보와 NER가 추가로 잡아내는 정보는 어떻게 다를까요?
- redact, mask, pseudonymize, synthesize는 각각 어떤 운영 목적에 맞을까요?

## 큰 그림

![AI 데이터 준비 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/04/04-01-big-picture.ko.png)

*AI 데이터 준비 4장 흐름 개요*

이 그림에서는 학습 데이터 PII 탐지와 익명화를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 학습 데이터 PII 탐지와 익명화의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

PII 처리를 제대로 하면 학습 데이터 안전성이 올라가고, 규제 대응과 배포 리스크가 동시에 낮아집니다. 특히 여러 팀이 같은 코퍼스를 공유할 때, 조기 익명화는 이후 재사용 비용을 크게 줄여 줍니다.

반대로 이 단계를 늦추면 raw PII가 디스크와 로그에 남습니다. 그 상태에서 증강, 합성, 평가 데이터 생성까지 진행하면 나중에 무엇을 삭제해야 하는지조차 추적하기 어려워집니다.

이 글은 개인정보 처리를 보안 팀 전용 주제가 아니라 데이터 준비 파이프라인의 필수 단계로 정리합니다. 이후 토큰화와 품질 필터링 단계도 이 전처리된 안전한 텍스트를 기준으로 돌아가야 합니다.

## 핵심 관점

개인정보 처리는 한 번의 정규식 치환으로 끝나지 않습니다. 직접 식별자, 준식별자, 민감 속성, 간접 식별자를 서로 다른 위험도로 나눠 보고, 빠른 1차 탐지와 정확한 2차 탐지를 조합해야 합니다.

익명화 방식도 목적에 따라 달라집니다. 컨텍스트를 최대한 보존해야 하는지, 사용자를 추적 가능하게 남겨야 하는지, 분포를 유지해야 하는지에 따라 redact와 pseudonymize의 선택이 달라집니다.

마지막으로 감사 로그가 있어야 이 파이프라인을 믿을 수 있습니다. 단, 감사 로그가 새 개인정보 저장소가 되지 않도록 무엇을 남길지 엄격히 제한해야 합니다.

> PII 처리는 “찾아서 가린다”보다 “여러 계층으로 찾고, 목적에 맞게 바꾸고, 그 과정이 다시 누수가 되지 않게 감사한다”는 설계에 가깝습니다.

## 핵심 개념

### 어떤 개인정보를 잡아야 하는지 먼저 분류합니다

프로덕션 데이터에서 만나는 개인정보는 대체로 아래 네 범주로 나눌 수 있습니다.

| 범주 | 예시 | 위험도 |
| --- | --- | --- |
| **직접 식별자** | 이메일, 전화번호, 주민등록번호, 카드번호 | 높음 |
| **준식별자** | 이름, 주소, 생년월일, 소속 | 중간 |
| **민감 속성** | 의료 정보, 종교, 정치 성향 | 높음 |
| **간접 식별자** | IP, device ID, 브라우저 fingerprint | 중간 |

GDPR과 한국 PIPA 모두 다른 정보와 결합해 개인을 식별할 수 있는 정보까지 넓게 봅니다. 따라서 탐지 범위를 너무 좁게 잡으면 실제 위험을 놓치게 됩니다.

### Stage 1: regex 탐지는 빠른 첫 번째 방어선입니다

정규식은 속도가 빠르고 배치 처리에 적합합니다. 다만 자연어 속 인명과 주소 같은 항목은 거의 잡지 못합니다.

```python
import re

PATTERNS = {
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "phone_kr": re.compile(r"\b01[016789]-?\d{3,4}-?\d{4}\b"),
    "phone_intl": re.compile(r"\+\d{1,3}[\s-]?\(?\d{1,4}\)?[\s-]?\d{1,4}[\s-]?\d{1,9}"),
    "ssn_us": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "rrn_kr": re.compile(r"\b\d{6}-?[1-4]\d{6}\b"),  # Korean RRN
    "credit_card": re.compile(r"\b(?:\d[ -]?){13,19}\b"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

def detect_regex(text: str) -> dict[str, list[str]]:
    return {k: p.findall(text) for k, p in PATTERNS.items() if p.search(text)}

# Test
sample = "Contact: alice@example.com or 010-1234-5678."
print(detect_regex(sample))
```

**Expected output:**

```text
{'email': ['alice@example.com'], 'phone_kr': ['010-1234-5678']}
```

이 출력은 가장 값싼 1차 검증입니다. 여기서도 명확한 식별자가 잡히지 않으면 뒤 단계가 아무리 정교해도 파이프라인은 이미 눈이 먼 상태입니다.

## 익명화 전에 반드시 거쳐야 할 검증 단계

regex와 NER를 둘 다 붙였다면, 두 계층이 실제로 서로를 보완하는지 확인해야 합니다. 짧은 테스트 하네스만 있어도 회귀를 꽤 많이 막을 수 있습니다.

```python
TEST_ROWS = [
    {"text": "Contact Alice at alice@example.com or 010-1234-5678."},
    {"text": "John Smith from Acme lives in Seoul."},
]

for row in TEST_ROWS:
    regex_hits = detect_regex(row["text"])
    ner_hits = detect_ner(row["text"], language="en")
    print({
        "text": row["text"],
        "regex_types": sorted(regex_hits.keys()),
        "ner_types": sorted({hit["type"] for hit in ner_hits}),
    })
```

**Expected output:**

```text
{'text': 'Contact Alice at alice@example.com or 010-1234-5678.', 'regex_types': ['email', 'phone_kr'], 'ner_types': ['EMAIL_ADDRESS', 'PERSON', 'PHONE_NUMBER']}
{'text': 'John Smith from Acme lives in Seoul.', 'regex_types': [], 'ner_types': ['LOCATION', 'PERSON']}
```

이 결과가 유용한 이유는 두 가지입니다. 빠른 regex 계층이 직접 식별자를 놓치지 않는지 확인할 수 있고, NER 계층이 자연어 안의 이름·위치처럼 regex가 약한 구간을 실제로 보완하는지도 알 수 있습니다.

## 운영에서 자주 놓치는 실패 모드

1. **감사 로그에 원문을 남기는 경우**: 그 순간 감사 로그가 새 개인정보 저장소가 됩니다.
2. **NER threshold를 지나치게 높게 잡는 경우**: 이름과 위치가 review queue로도 못 올라옵니다.
3. **한국어 테스트 샘플이 없는 경우**: 주민등록번호, 사업자번호, 한국어 이름 누락이 오래 숨어 있습니다.

중요한 식별자마다 최소 한 줄의 테스트 데이터를 직접 보여 줄 수 없다면, 아직은 개인정보 파이프라인을 신뢰하기 어렵습니다.

이 단계는 false negative가 높다는 한계를 안고 시작해야 합니다. 그래서 regex만으로 끝내지 않고, “명확한 패턴은 빠르게 제거한다”는 역할로 두는 편이 맞습니다.

### Stage 2: NER로 자연어 속 PII를 추가 탐지합니다

`Presidio`나 `spaCy` 기반 NER는 인명, 위치, 조직명, 주소처럼 정규식이 약한 구간을 보완합니다.

```python
# pip install presidio-analyzer presidio-anonymizer
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()  # English default; Korean needs spaCy ko model
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

confidence score가 낮은 결과를 어떻게 처리할지도 정책으로 정해야 합니다. 안전성이 우선인 코퍼스라면 보수적으로 가리고, 사람이 검토할 review queue를 둘 수 있습니다.

### Stage 3: 익명화는 목적에 따라 네 가지로 나뉩니다

PII를 찾았다고 해서 항상 같은 방식으로 가리면 되는 것은 아닙니다.

```python
import hashlib
import secrets

def redact(text: str, hits: list[dict]) -> str:
    """Full removal: safest, loses context"""
    out = text
    for h in sorted(hits, key=lambda x: -x["start"]):
        out = out[:h["start"]] + f"[{h['type']}]" + out[h["end"]:]
    return out

def mask(text: str, hits: list[dict], keep: int = 4) -> str:
    """Partial mask: keeps trailing chars (e.g., card last4)"""
    out = text
    for h in sorted(hits, key=lambda x: -x["start"]):
        original = text[h["start"]:h["end"]]
        masked = "*" * (len(original) - keep) + original[-keep:]
        out = out[:h["start"]] + masked + out[h["end"]:]
    return out

_PEPPER = secrets.token_hex(16)  # process-local secret

def pseudonymize(text: str, hits: list[dict]) -> str:
    """Same input -> same pseudonym. Analytics-friendly, not reversible."""
    out = text
    for h in sorted(hits, key=lambda x: -x["start"]):
        original = text[h["start"]:h["end"]]
        token = hashlib.sha256(
            (_PEPPER + original).encode()
        ).hexdigest()[:12]
        out = out[:h["start"]] + f"<{h['type']}_{token}>" + out[h["end"]:]
    return out

def synthesize(text: str, hits: list[dict], faker) -> str:
    """Replace with fake data. Preserves training distribution."""
    out = text
    gen = {"PERSON": faker.name, "EMAIL_ADDRESS": faker.email,
           "PHONE_NUMBER": faker.phone_number}
    for h in sorted(hits, key=lambda x: -x["start"]):
        replacement = gen.get(h["type"], lambda: "[REDACTED]")()
        out = out[:h["start"]] + replacement + out[h["end"]:]
    return out
```

실무 기준으로 정리하면 다음과 같습니다.

- **Redact**: 무엇보다 안전성이 중요할 때 사용합니다.
- **Mask**: 마지막 4자리 같은 일부 식별자를 남겨야 할 때 씁니다.
- **Pseudonymize**: 동일 사용자의 행태 패턴은 보되 실제 신원은 숨기고 싶을 때 적합합니다.
- **Synthesize**: 이름 길이, 이메일 형식 같은 분포를 유지해야 하는 학습 작업에서 유용합니다.

### Stage 4: 감사 로그와 샘플링 검토를 붙입니다

개인정보 처리 파이프라인은 결과를 다시 확인할 장치가 있어야 합니다. 완전 자동화만 믿으면 false negative가 조용히 누적됩니다.

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
    sample = random.sample(rows, max(1, int(len(rows) * sample_rate)))
    with open(audit_path, "w") as f:
        json.dump({"audit": audit, "review_sample": sample}, f, ensure_ascii=False)
    return out
```

중요한 규칙은 감사 로그에 원본 PII를 남기지 않는 것입니다. 타입, 개수, 문자 감소량 정도만 남기고, 사람이 보는 review sample은 별도 접근 통제를 걸어야 합니다.

### 한국어 데이터는 별도 규칙을 가져야 합니다

한국어 데이터는 영어 중심 예제를 그대로 쓰면 놓치는 항목이 많습니다.

- **주민등록번호**: `900101-1234567` 형태를 정규식으로 우선 잡아야 합니다.
- **사업자등록번호**: 개인사업자 데이터에서는 사실상 PII로 봐야 합니다.
- **차량번호**: `12가3456` 형태처럼 도메인에 따라 중요할 수 있습니다.
- **한국어 이름**: 일반 영어 NER로는 잘 잡히지 않으므로 한국어 전용 모델이 필요합니다.

영어 데이터 파이프라인을 그대로 복사하면 한국어 이름과 국내 식별자가 빠지기 쉽습니다. 한국어 도메인은 별도의 테스트 샘플셋으로 탐지율을 검증하는 편이 안전합니다.

## 흔히 헷갈리는 지점

- **regex만 잘 짜면 개인정보 처리는 끝납니다**: 정규식은 인명, 주소, 자연어 속 식별 표현을 거의 놓칩니다. NER와 함께 써야 합니다.
- **pseudonymize는 sha256만 쓰면 충분합니다**: pepper 없는 해시는 rainbow-table 공격에 취약합니다. 프로세스 로컬 비밀값을 섞어야 합니다.
- **감사 로그는 원문까지 남겨야 추적이 쉽습니다**: 그 순간 감사 로그가 새로운 개인정보 저장소가 됩니다. 타입과 개수만 남겨야 합니다.
- **영어 NER 모델도 한국어 이름을 대충 잡아 줍니다**: 한국어 이름과 국내 식별자는 누락 비율이 높아 전용 모델과 테스트가 필요합니다.

## 운영 체크리스트

- [ ] regex 탐지와 NER 탐지를 분리해 두고 둘 다 실행한다
- [ ] 익명화 방식(redact/mask/pseudonymize/synthesize)을 데이터 사용 목적별로 문서화했다
- [ ] pepper 없는 단순 해시 기반 pseudonymize를 금지했다
- [ ] 감사 로그에는 PII 원문을 남기지 않고 count/type/char_reduction만 저장한다
- [ ] 최소 1% 샘플에 대해 사람 검토 또는 보수적 리뷰 큐를 운영한다

## 정리

PII 처리는 탐지 한 번으로 끝나는 부가 작업이 아닙니다. detection, classification, anonymization, audit라는 네 단계를 모두 갖춰야 학습 데이터 안전성을 실제로 높일 수 있습니다.

정규식과 NER를 함께 써야 하고, 익명화 방식도 운영 목적에 맞게 선택해야 합니다. 특히 감사 로그가 또 다른 누수원이 되지 않도록 무엇을 기록할지 엄격히 제한해야 합니다.

다음 글에서는 이렇게 정리된 텍스트를 모델 입력 단위로 바꾸는 tokenization과 chunking을 다룹니다. 개인정보를 안전하게 처리한 뒤에야 토큰 효율과 검색 품질을 논할 수 있습니다.

## 처음 질문으로 돌아가기

- **PII 처리 파이프라인을 detection, classification, anonymization, audit로 나누는 이유는 무엇일까요?**
  - 본문의 기준은 학습 데이터 PII 탐지와 익명화를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **regex만으로 잡히는 정보와 NER가 추가로 잡아내는 정보는 어떻게 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **redact, mask, pseudonymize, synthesize는 각각 어떤 운영 목적에 맞을까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Data Preparation 101 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- [AI Data Preparation 101 (2/10): 원본 데이터 수집과 카탈로깅](./02-source-data-collection-cataloging.md)
- [AI Data Preparation 101 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
- **학습 데이터 PII 탐지와 익명화 (현재 글)**
- Tokenization과 Chunking 전략 (예정)
- 데이터 품질 필터링 — Heuristic과 Classifier (예정)
- 합성 데이터 생성 — Self-Instruct부터 Distillation까지 (예정)
- 데이터 증강 기법 — EDA부터 Back-Translation까지 (예정)
- 학습/평가/테스트 분할과 Contamination 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Microsoft Presidio - PII detection and anonymization](https://microsoft.github.io/presidio/)
- [Extracting Training Data from Large Language Models (Carlini et al., 2021)](https://arxiv.org/abs/2012.07805)
- [k-anonymity: A model for protecting privacy (Sweeney, 2002)](https://dataprivacylab.org/dataprivacy/projects/kanonymity/)
- [GDPR Article 4 - Definitions](https://gdpr-info.eu/art-4-gdpr/)

### 관련 시리즈
- [LLM 파인튜닝 101 — 데이터셋 준비와 전처리](../../llm-finetuning-101/ko/02-dataset.md)
- [AI Evaluation 101 — 평가 데이터셋 설계하기](../../ai-evaluation-101/ko/02-evaluation-dataset-design.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-data-preparation-101/ko/04-pii-detection-anonymization)

Tags: Data Preparation, PII, Anonymization, Privacy
