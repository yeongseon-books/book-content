---
title: "AI Safety & Guardrails 101 (4/10): PII 감지와 마스킹"
series: ai-safety-guardrails-101
episode: 4
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- AI Safety
- PII
- Presidio
- GDPR
last_reviewed: '2026-05-14'
seo_description: 법무팀이 가장 자주 묻는 질문입니다. LLM 애플리케이션은 두 방향에서 PII를 다룹니다.
---

# AI Safety & Guardrails 101 (4/10): PII 감지와 마스킹

LLM 애플리케이션은 개인정보를 한 방향으로만 다루지 않습니다. 사용자는 카드 번호, 주소, 이메일, 주민식별자 같은 정보를 입력으로 보낼 수 있고, 모델은 검색 문맥이나 로그에 있던 다른 사람의 정보를 다시 응답으로 내보낼 수도 있습니다. 그래서 PII 문제는 입력 전처리와 출력 후처리를 모두 포함합니다.

이 주제가 까다로운 이유는 법무·보안·제품 요구가 한 지점에 겹치기 때문입니다. 최소 수집 원칙을 지켜야 하고, 사용자가 삭제를 요청하면 흔적을 지워야 하며, 동시에 모델이 문맥을 이해할 정도의 정보는 남겨 두고 싶습니다. 무조건 `<PERSON>`으로 바꾸면 개인정보는 줄어들지만, 모델 품질도 같이 무너질 수 있습니다.

실무에서는 이 균형을 잘 잡아야 합니다. 구조화된 PII는 빠르게 감지하고, 이름이나 주소처럼 비정형인 정보는 NER 계열로 보완하며, 필요하면 가역적 토큰화로 문맥 일관성을 유지합니다. 이 설계가 없으면 로그와 RAG, 응답 단계 어디서든 누출이 발생합니다.

이 글은 AI Safety & Guardrails 101 시리즈의 4번째 글입니다.

이 글에서는 PII 범위 정의부터 regex·Presidio·가역적 토큰화·출력 재검사까지 프로덕션 관점에서 정리합니다.

## 먼저 던지는 질문

- PII 보호는 왜 모델에 보내는 정보와 내부에 보관하는 정보를 분리해야 할까요?
- regex, Presidio, reversible tokenization은 각각 어떤 단계에서 유용할까요?
- 응답 outbound 단계에서 다시 검사하지 않으면 어떤 유출이 생길까요?

## 큰 그림

![PII 보호의 핵심: 모델에 보내는 정보와 보관 정보의 분리](https://yeongseon-books.github.io/book-public-assets/assets/ai-safety-guardrails-101/04/04-01-pii.ko.png)

*PII 보호의 핵심: 모델에 보내는 정보와 보관 정보의 분리*

이 그림에서는 PII를 모델에 보내기 전 탐지·치환하고, 내부 보관 정보와 모델 입력 정보를 분리하는 흐름을 봅니다. PII guardrail은 한 번 마스킹하는 함수가 아니라 inbound와 outbound를 모두 지키는 데이터 경계입니다.

> PII 보호의 핵심은 정보를 숨기는 것이 아니라, 모델이 볼 정보와 시스템이 보관할 정보를 분리하는 것입니다.

## 왜 이 글이 중요한가

PII 보호를 초기에 구조로 넣어 두면 개인정보 처리 범위가 명확해집니다. 무엇을 모델에 보내고, 무엇을 마스킹하고, 무엇을 별도 저장소에 두는지를 정하면 법무 검토와 보안 감사도 훨씬 수월해집니다. 특히 로그와 캐시, 검색 문맥을 분리하면 나중에 삭제 요청이나 침해 사고 대응이 쉬워집니다.

반대로 PII를 나중 문제로 미루면 가장 먼저 로그가 오염됩니다. 디버그 로그에 원문 프롬프트가 남고, RAG 문맥에 있던 다른 사용자의 이메일이 응답으로 재노출되고, 해외 모델 공급사를 쓰면서 고지와 동의가 빠지는 식입니다. 이 문제는 기능 버그보다 규제 리스크로 더 크게 돌아옵니다.

따라서 PII 방어는 단순한 패턴 치환이 아니라 데이터 경로 설계입니다. 입력 전에 최소화하고, 모델 앞에서 토큰화하고, 출력 후에 다시 검사하며, 저장소는 목적별로 분리해야 합니다.

## 핵심 관점

많은 팀이 개인정보 보호를 “마스킹 함수 하나”로 생각합니다. 하지만 운영에서는 그보다 더 큰 질문이 먼저입니다. 이 데이터를 정말 모델에 보내야 하는가, 로그에 남겨도 되는가, 사용자 삭제 요청이 왔을 때 어느 저장소에서 지워야 하는가입니다.

그래서 좋은 설계는 두 축으로 움직입니다. 첫째, 탐지 정확도입니다. 구조화된 PII는 regex로 빠르게 찾고, 사람 이름·주소·의료 정보처럼 비정형인 범주는 NER 기반 도구로 보완합니다. 둘째, 표현 방식입니다. 완전 마스킹이 적합한지, 문맥 유지가 필요해 가역적 토큰화가 적합한지 결정해야 합니다.

> PII 보호의 본질은 텍스트를 가리는 데 있지 않습니다. 개인정보가 필요한 경계를 넘지 않도록 데이터 흐름 자체를 제어하는 데 있습니다.

## 핵심 개념

### PII 범위를 먼저 넓게 정의해야 합니다

PII는 카드 번호나 전화번호만을 의미하지 않습니다. 규제와 관할권에 따라 이름, 위치, 온라인 식별자도 개인정보로 분류됩니다.

| Category | Examples |
| --- | --- |
| National ID | SSN, passport, EU national IDs |
| Contact | Phone, email |
| Financial | Credit card, bank account |
| Address | Street address |
| Medical | Diagnosis, prescription (HIPAA-protected in US) |
| Credentials | Password, API key |
| Location | GPS coordinates |

GDPR은 이름, 위치, cookie ID, IP까지 개인정보로 봅니다. 건강, 종교, 정치 성향 같은 민감 정보는 대부분의 규제에서 더 강한 보호 대상입니다. 따라서 팀은 법무와 함께 “우리 제품에서 PII가 무엇인지”를 먼저 정의해야 합니다.

### regex는 구조화된 PII의 빠른 출발점입니다

형식이 고정된 PII는 regex가 효율적입니다.

```python
import re

PII_PATTERNS = {
    "us_ssn": re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),
    "us_phone": re.compile(r"\b(?:\+?1[-\s.]?)?\(?\d{3}\)?[-\s.]?\d{3}[-\s.]?\d{4}\b"),
    "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.-]+\b"),
    "credit_card": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
}

def detect_pii(text: str) -> list[tuple[str, int, int, str]]:
    """Returns list of (category, start, end, value)."""
    found = []
    for cat, pat in PII_PATTERNS.items():
        for m in pat.finditer(text):
            found.append((cat, m.start(), m.end(), m.group()))
    return found

text = "Reach me at 555-123-4567 or alice@example.com."
print(detect_pii(text))
# [('us_phone', 12, 24, '555-123-4567'), ('email', 28, 45, 'alice@example.com')]
```

regex의 장점은 빠르고 explainable하다는 점입니다. 다만 이름, 주소, 의료 표현처럼 형식이 고정되지 않은 정보는 잘 잡지 못합니다. 카드 번호도 Luhn 검증 없이 정규식만 쓰면 false positive가 많습니다.

### Presidio는 비정형 PII 탐지에 유용합니다

Microsoft Presidio는 regex와 NER를 결합해 비정형 PII를 더 잘 잡습니다.

```python
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

text = "Alice Kim called from 555-123-4567 about her order."

results = analyzer.analyze(text=text, language="en")
# [<RecognizerResult PERSON, 0, 9, 0.85>, <PHONE_NUMBER, 22, 34, 0.75>, ...]

masked = anonymizer.anonymize(text=text, analyzer_results=results)
print(masked.text)
# "<PERSON> called from <PHONE_NUMBER> about her order."
```

다국어 환경에서는 언어별 spaCy 모델이나 별도 NER 모델을 등록해 보완할 수 있습니다. 회사 내부 식별자도 커스텀 recognizer로 추가합니다.

```python
from presidio_analyzer import PatternRecognizer, Pattern

custom_id = PatternRecognizer(
    supported_entity="EMPLOYEE_ID",
    patterns=[Pattern(name="emp_id", regex=r"\bEMP-\d{6}\b", score=0.95)],
    supported_language="en",
)
analyzer.registry.add_recognizer(custom_id)
```

이 접근은 사번, 주문번호, 계약번호처럼 서비스 고유 식별자가 있을 때 특히 중요합니다.

### 단순 마스킹은 문맥을 망가뜨릴 수 있습니다

`<PERSON>` 치환은 쉽지만, 동일 인물을 구분하지 못하게 만듭니다. “Alice의 주문을 Alice에게 보내라”가 모두 `<PERSON>`으로 바뀌면 coreference가 깨집니다. 그래서 경우에 따라 가역적 토큰화가 더 낫습니다.

```python
import secrets
from dataclasses import dataclass, field

@dataclass
class PIITokenizer:
    mapping: dict[str, str] = field(default_factory=dict)
    reverse: dict[str, str] = field(default_factory=dict)

    def tokenize(self, text: str, detected: list[tuple]) -> str:
        # Iterate in reverse order so offsets stay valid
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
src = "Alice (alice@example.com) ordered. Send to alice@example.com."
detected = detect_pii(src)
masked = tk.tokenize(src, detected)
# "Alice (<EMAIL_a3b2c1d0>) ordered. Send to <EMAIL_a3b2c1d0>."
# Same email maps to the same token → model treats it as one entity.

response = llm.complete(masked)
final = tk.detokenize(response)  # restore before sending to user
```

운영 원칙은 세 가지입니다. 매핑은 요청 단위로만 유지할 것, 토큰에 범주 정보를 넣을 것, 동일 값에는 동일 토큰을 줄 것. 요청 간 매핑을 재사용하면 그 자체가 새로운 개인정보 저장소가 됩니다.

### outbound re-check가 빠지면 RAG 누출을 놓칩니다

입력만 마스킹하고 끝내면 안 됩니다. 모델은 검색 문맥이나 시스템 프롬프트에서 본 PII를 출력할 수 있습니다. 같은 탐지기를 출력에도 다시 적용해야 합니다.

```python
def safe_call(user_input: str, retrieved_docs: list[str]) -> str:
    user_detected = detect_pii(user_input)
    masked_input = mask_text(user_input, user_detected)

    masked_docs = [mask_text(d, detect_pii(d)) for d in retrieved_docs]

    response = llm.complete(SYSTEM_PROMPT, user=masked_input, context="\n".join(masked_docs))

    output_detected = detect_pii(response)
    if output_detected:
        log_pii_leak(output_detected, response)
        # Option 1: block
        # return "Response blocked due to detected personal information."
        # Option 2: mask and pass through
        response = mask_text(response, output_detected)

    return response
```

이 단계는 특히 다중 사용자 RAG, 고객지원 검색, 내부 문서 검색에서 중요합니다. 문맥에 있던 정보가 답변으로 흘러나오는 순간 사고가 됩니다.

### 컴플라이언스는 구현 체크리스트와 연결되어야 합니다

기술 설계는 결국 규제 요구와 만나야 합니다. 최소한 아래 항목은 체크해야 합니다.

- [ ] **Minimization**: strip unneeded PII before sending to the model.
- [ ] **Purpose disclosure**: obtain user consent for LLM processing.
- [ ] **Cross-border notice**: disclose use of foreign providers like OpenAI.
- [ ] **Right to delete**: support deletion from logs and caches on request.
- [ ] **Logging policy**: ensure PII does not land in logs (covered in Ep9).
- [ ] **DPA in place**: Data Processing Agreement signed with each provider.
- [ ] **Sensitive categories**: extra consent for health, religion, etc.

해외 공급사를 쓴다면 보관 기간, zero-data-retention 옵션, 삭제 절차를 함께 검토해야 합니다. 기술 구현과 법적 고지는 분리할 수 없습니다.

## 흔히 헷갈리는 지점

- regex만 충분히 많이 쓰면 PII를 거의 다 잡을 수 있다고 생각하기 쉽지만, 이름과 주소 같은 비정형 정보는 놓칩니다.
- `<PERSON>` 같은 단순 마스킹이 항상 안전하다고 보기 쉽지만, 모델 추론 품질을 크게 떨어뜨릴 수 있습니다.
- 입력만 마스킹하면 충분하다고 생각하기 쉽지만, 실제 누출은 출력과 로그에서 더 자주 발생합니다.
- 삭제 요청은 원문 저장소에만 적용하면 된다고 보기 쉽지만, 캐시·로그·분석 테이블도 함께 봐야 합니다.

## 운영 체크리스트

- 구조화된 PII용 regex와 비정형 PII용 NER 도구를 함께 운영합니다.
- 문맥 일관성이 중요하면 요청 단위 가역적 토큰화를 적용합니다.
- 입력, 검색 문맥, 출력, 로그를 각각 별도 PII 검사 지점으로 둡니다.
- 해외 모델 공급사 사용 여부와 데이터 보관 정책을 사용자 고지 문구와 일치시킵니다.
- 삭제 요청과 보존 기간 만료를 자동화한 운영 절차를 문서화합니다.

## 정리

PII 보호는 단일 마스킹 함수로 끝나지 않습니다. 무엇을 모델에 보내는지, 무엇을 로그에 남기는지, 무엇을 다시 복원할 수 있어야 하는지를 함께 설계해야 합니다. 이 문제를 데이터 흐름 관점으로 보면 기술 선택과 규제 대응이 훨씬 명확해집니다.

실무적으로는 regex와 Presidio를 조합해 탐지 정확도를 높이고, 필요할 때는 가역적 토큰화로 문맥 품질을 유지하는 방식이 현실적입니다. 여기에 outbound re-check와 저장소 분리를 넣어야 실제 누출을 줄일 수 있습니다.

더 중요한 일은 개인정보를 숨기는 것 자체보다, 개인정보가 넘어가면 안 되는 경계를 정확히 관리하는 일입니다.

## 처음 질문으로 돌아가기

- **PII 보호는 왜 모델에 보내는 정보와 내부에 보관하는 정보를 분리해야 할까요?**
  - 모델에는 최소화된 token이나 masked value만 보내고, 원본은 접근 통제된 저장소에 둬야 유출 범위를 줄일 수 있습니다.
- **regex, Presidio, reversible tokenization은 각각 어떤 단계에서 유용할까요?**
  - regex는 빠른 시작점, Presidio는 다국어·복합 엔터티 탐지, reversible tokenization은 나중에 원본 복원이 필요한 업무에 유용합니다.
- **응답 outbound 단계에서 다시 검사하지 않으면 어떤 유출이 생길까요?**
  - 모델이 학습된 패턴이나 context 조각에서 개인정보를 재구성해 응답할 수 있으므로 outbound 재검사가 없으면 사용자에게 PII가 나갈 수 있습니다.
<!-- toc:begin -->
## 시리즈 목차

- [AI Safety & Guardrails 101 (1/10): AI Safety가 왜 중요한가](./01-why-ai-safety-matters.md)
- [AI Safety & Guardrails 101 (2/10): Prompt Injection 방어](./02-prompt-injection-defense.md)
- [AI Safety & Guardrails 101 (3/10): 출력 필터링과 콘텐츠 모더레이션](./03-output-filtering.md)
- **AI Safety & Guardrails 101 (4/10): PII 감지와 마스킹 (현재 글)**
- AI Safety & Guardrails 101 (5/10): Jailbreak 탐지 (예정)
- AI Safety & Guardrails 101 (6/10): 독성과 편향 탐지 (예정)
- AI Safety & Guardrails 101 (7/10): Hallucination Guardrail — Grounding 검증 (예정)
- AI Safety & Guardrails 101 (8/10): Rate Limiting과 남용 방지 (예정)
- AI Safety & Guardrails 101 (9/10): 감사 로깅과 컴플라이언스 (예정)
- AI Safety & Guardrails 101 (10/10): 운영 가드레일 시스템 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Microsoft Presidio](https://microsoft.github.io/presidio/)
- [GDPR Article 4 — Definitions](https://gdpr.eu/article-4-definitions/)
- [HIPAA — Privacy Rule Summary](https://www.hhs.gov/hipaa/for-professionals/privacy/laws-regulations/index.html)
- [OpenAI — Enterprise Privacy](https://openai.com/enterprise-privacy)

### 관련 시리즈

- [LLM 앱 운영 101 — LLM 앱 보안](../../llm-apps-ops-101/ko/04-security.md)
- [감사 로깅과 컴플라이언스](./09-audit-logging-compliance.md)

Tags: AI Safety, PII, Presidio, GDPR
