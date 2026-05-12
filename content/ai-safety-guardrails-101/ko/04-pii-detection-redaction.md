---
title: PII 감지와 마스킹
series: ai-safety-guardrails-101
episode: 4
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- AI Safety
- PII
- Presidio
- GDPR
last_reviewed: '2026-05-11'
seo_description: 법무팀이 가장 자주 묻는 질문입니다. LLM 애플리케이션은 두 방향에서 PII를 다룹니다.
---

# PII 감지와 마스킹

> AI Safety & Guardrails 101 시리즈 (4/10)

LLM 애플리케이션은 입력과 출력 양쪽에서 개인정보를 건드립니다. 법무팀이 "이메일은 마스킹했나요?"라고 묻는 이유도, 모델 로그와 응답 경로 어디서든 PII가 새어 나갈 수 있기 때문입니다.

이 글은 AI Safety & Guardrails 101 시리즈의 4번째 글입니다. 여기서는 PII를 어떤 범위로 정의해야 하는지부터 시작해 탐지와 마스킹 파이프라인을 구성합니다.

---

## Section 1

## "이메일은 마스킹했나요?"

법무팀이 가장 자주 묻는 질문입니다. LLM 애플리케이션은 두 방향에서 PII를 다룹니다.

- 입력 방향: 사용자가 자신의 신용카드 번호, 주소, 주민등록번호를 모델에 보냅니다. 모델 공급사 로그에 남거나 privacy violation으로 이어질 수 있고, training data에 포함될 가능성도 있습니다.
- 출력 방향: RAG 컨텍스트에 다른 사용자의 이메일이 들어 있어 응답에 그대로 흘러나올 수 있습니다.

이번 글에서는 PII를 정의하고, 정규식과 Microsoft Presidio를 결합한 탐지/마스킹 파이프라인을 구현합니다. GDPR / 개인정보보호법 관점도 함께 봅니다.

다룰 내용:

- PII 카테고리와 지역별 차이 (한국 RRN, 미국 SSN)
- 정규식 vs NER 기반 탐지의 trade-off
- Microsoft Presidio 사용법
- 가역적 마스킹 (decrypt 가능)과 비가역적 마스킹
- 입력 마스킹과 출력 재검사

---

## Section 1 — PII 카테고리

| 카테고리 | 한국 예시 | 글로벌 예시 |
| --- | --- | --- |
| 식별 번호 | 주민등록번호 (900101-1XXXXXX) | SSN, Passport |
| 연락처 | 휴대폰 (010-XXXX-XXXX), 이메일 | 동일 |
| 금융 | 카드번호, 계좌번호 | 동일 |
| 주소 | 도로명/지번 주소 | Address |
| 의료 | 진단명, 처방전 | HIPAA-protected |
| 자격 정보 | 비밀번호, API key | 동일 |
| 위치 | GPS 좌표 | 동일 |

GDPR은 이름, 위치, 온라인 식별자 (cookie ID, IP)도 personal data로 봅니다. 한국 개인정보보호법은 식별번호와 민감정보 (의료, 종교, 정치성향)를 별도로 강하게 보호합니다.

---

## Section 2 — 정규식 기반 탐지 (시작점)

가장 단순한 형식이 있는 PII는 정규식으로 잡습니다.

```python
import re

PII_PATTERNS = {
    "kr_rrn": re.compile(r"\b\d{6}[-\s]?[1-4]\d{6}\b"),  # 한국 주민등록번호
    "kr_phone": re.compile(r"\b01[016-9][-\s]?\d{3,4}[-\s]?\d{4}\b"),
    "us_ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

def detect_pii(text: str) -> list[tuple[str, int, int, str]]:
    """(카테고리, 시작, 끝, 값) 형태의 리스트를 반환합니다."""
    found = []
    for cat, pat in PII_PATTERNS.items():
        for m in pat.finditer(text):
            found.append((cat, m.start(), m.end(), m.group()))
    return found

text = "내 번호는 010-1234-5678이고 이메일은 alice@example.com 입니다."
print(detect_pii(text))
# 예: [('kr_phone', 6, 19, '010-1234-5678'), ('email', 27, 45, 'alice@example.com')]
```

한계:

- 이름 ("김철수", "John Doe")은 형식이 없어 정규식으로 못 잡음
- 주소는 너무 다양해서 정규식 어려움
- 신용카드 정규식은 false positive가 많음 (Luhn 알고리즘으로 검증해야)

---

## Section 3 — Microsoft Presidio

Presidio는 NER 기반 PII 탐지/마스킹 라이브러리입니다. 정규식과 spaCy NER를 결합해 형식이 없는 PII (이름, 주소)도 탐지합니다.

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

text = "Alice Kim called from 010-1234-5678 about her order."

results = analyzer.analyze(text=text, language="en")
# 예: [<RecognizerResult PERSON, 0, 9, 0.85>, <PHONE_NUMBER, 22, 35, 0.75>, ...]

masked = anonymizer.anonymize(text=text, analyzer_results=results)
print(masked.text)
# 예: "<PERSON> called from <PHONE_NUMBER> about her order."
```

한국어 지원은 spaCy 한국어 모델 또는 KoBERT 기반 NER을 함께 등록해야 합니다.

```python
from presidio_analyzer import PatternRecognizer, Pattern

kr_rrn_recognizer = PatternRecognizer(
    supported_entity="KR_RRN",
    patterns=[Pattern(name="rrn", regex=r"\b\d{6}[-\s]?[1-4]\d{6}\b", score=0.9)],
    supported_language="ko",
)
analyzer.registry.add_recognizer(kr_rrn_recognizer)
```

---

## Section 4 — 가역적 마스킹 (Tokenization)

단순 마스킹 (`<PHONE>`)은 모델이 같은 사람을 일관되게 다루지 못하게 합니다. 예를 들어 "Alice의 주문을 Alice에게 보내라"가 "<PERSON>의 주문을 <PERSON>에게 보내라"가 되면 모호해집니다.

가역적 토큰화 (FPE — format-preserving encryption 또는 단순 mapping)를 사용합니다.

```python
import secrets
from dataclasses import dataclass, field

@dataclass
class PIITokenizer:
    mapping: dict[str, str] = field(default_factory=dict)
    reverse: dict[str, str] = field(default_factory=dict)

    def tokenize(self, text: str, detected: list[tuple]) -> str:
        # end부터 거꾸로 치환 (offset 깨짐 방지)
        for cat, start, end, value in sorted(detected, key=lambda x: -x[1]):
            if value not in self.mapping:
                token = f"<{cat.upper()}_{secrets.token_hex(4)}>"
                self.mapping[value] = token
                self.reverse[token] = value
            text = text[:start] + self.mapping[value] + text[end:]
        return text

    def detokenize(self, text: str) -> str:
        for token, value in self.reverse.items():
            text = text.replace(token, value)
        return text

tk = PIITokenizer()
detected = detect_pii("Alice (alice@example.com) ordered. Send to alice@example.com.")
masked = tk.tokenize("Alice (alice@example.com) ordered. Send to alice@example.com.", detected)
# 예: "Alice (<EMAIL_a3b2c1d0>) ordered. Send to <EMAIL_a3b2c1d0>."
# 같은 이메일은 같은 토큰으로 바뀌므로 모델이 동일 entity로 인식

response = llm.complete(masked)
final = tk.detokenize(response)  # 사용자에게 보내기 전 복원
```

원칙:

- mapping은 요청 단위로만 유지합니다. cross-request 매핑은 PII leak 위험이 큽니다.
- token에는 형식 정보를 담아 모델이 처리할 수 있게 합니다.
- 같은 값은 같은 token으로 치환해 coreference를 유지합니다.

---

## Section 5 — 출력 재검사

모델이 RAG 컨텍스트나 system prompt에서 본 PII를 응답에 포함할 수 있습니다. 출력에도 같은 detector를 돌려야 합니다.

```python
def safe_call(user_input: str, retrieved_docs: list[str]) -> str:
    # 입력 마스킹
    user_detected = detect_pii(user_input)
    masked_input = mask_text(user_input, user_detected)

    # RAG 문서도 마스킹
    masked_docs = [mask_text(d, detect_pii(d)) for d in retrieved_docs]

    response = llm.complete(SYSTEM_PROMPT, user=masked_input, context="\n".join(masked_docs))

    # 출력 재검사 — 마스킹을 우회한 PII가 있는지
    output_detected = detect_pii(response)
    if output_detected:
        log_pii_leak(output_detected, response)
        # 옵션 1: 차단
        # return "응답에 개인정보가 포함되어 차단되었습니다."
        # 옵션 2: 마스킹해서 전달
        response = mask_text(response, output_detected)

    return response
```

---

## Section 6 — 컴플라이언스 체크리스트

GDPR / 개인정보보호법 관점에서:

- [ ] 수집 최소화: 모델에 보내는 데이터에서 불필요한 PII를 제거합니다.
- [ ] 목적 명시: 사용자에게 LLM 처리 동의를 받습니다.
- [ ] 국외 이전 통지: OpenAI 같은 해외 공급사 사용 사실을 명시합니다.
- [ ] 삭제 권리: 사용자가 요청하면 로그와 캐시에서 삭제할 수 있어야 합니다.
- [ ] 로깅 정책: PII가 로그에 남지 않게 관리합니다. 자세한 내용은 이번 시리즈 Ep9에서 다룹니다.
- [ ] DPA 체결: 공급사와 Data Processing Agreement를 맺습니다.
- [ ] 민감정보 별도 처리: 의료, 종교 같은 민감정보에는 추가 동의를 받습니다.

LLM API 공급사의 zero-data-retention 옵션(OpenAI Enterprise, Azure OpenAI)을 사용하면 모델 공급사 측 보관 위험을 낮출 수 있습니다.

---

## 흔한 실수

1. 정규식만으로 끝냅니다. 이름, 주소처럼 형식이 없는 PII는 NER이 필요합니다.
2. 단순 마스킹만 쓰고 토큰 일관성을 유지하지 않습니다. `<PERSON>`이 여러 명을 가리키면 모델이 혼란스러워하므로 가역적 토큰화를 써야 합니다.
3. 출력 재검사를 빼먹습니다. RAG 컨텍스트의 PII가 그대로 응답에 흘러나올 수 있습니다.
4. 로그에 PII를 남깁니다. 디버깅 로그에서 PII가 새는 사고가 가장 흔하므로 로깅 전에도 마스킹해야 합니다.
5. 국외 LLM 공급사 사용 사실을 사용자에게 알리지 않습니다. GDPR과 개인정보보호법 위반으로 이어질 수 있습니다.

---

## 핵심 요약

- PII 처리는 입력과 출력 양방향에서 모두 필요합니다.
- 정규식은 전화번호, 카드번호처럼 형식이 있는 PII에 효과적이고, Microsoft Presidio가 NER 기반 탐지를 보완합니다.
- 가역적 토큰화를 사용하면 모델이 같은 entity를 일관되게 처리할 수 있습니다.
- 출력 재검사로 RAG / system prompt를 통한 leak을 막습니다.
- 컴플라이언스 체크리스트(수집 최소화, 동의, 삭제권, DPA)는 운영 초기부터 적용해야 합니다.

---

<!-- toc:begin -->
## AI Safety & Guardrails 101 시리즈

- [AI Safety가 왜 중요한가](./01-why-ai-safety-matters.md)
- [Prompt Injection 방어](./02-prompt-injection-defense.md)
- [출력 필터링과 콘텐츠 모더레이션](./03-output-filtering.md)
- **PII 감지와 마스킹 (현재 글)**
- Jailbreak 탐지 (예정)
- 독성과 편향 탐지 (예정)
- Hallucination Guardrail — Grounding 검증 (예정)
- Rate Limiting과 남용 방지 (예정)
- 감사 로깅과 컴플라이언스 (예정)
- 운영 가드레일 시스템 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Microsoft Presidio](https://microsoft.github.io/presidio/)
- [GDPR Article 4 — Definitions](https://gdpr.eu/article-4-definitions/)
- [한국 개인정보보호위원회 — 가이드라인](https://www.pipc.go.kr/)
- [OpenAI — Enterprise Privacy](https://openai.com/enterprise-privacy)

Tags: AI Safety, PII, Presidio, GDPR
