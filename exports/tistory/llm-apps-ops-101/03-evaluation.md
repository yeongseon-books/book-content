
# LLM Apps Ops 101 (3/6): LLM 출력 품질 평가

이 글은 LLM Apps Ops 101 시리즈의 세 번째 글입니다.

"프롬프트 압축하고 저가 모델 라우팅 붙였더니 비용 40% 줄었습니다!" 슬랙에 이 메시지가 올라왔을 때, 진짜 어려운 부분은 비용 절감 자체가 아닙니다. 어려운 부분은 2주 뒤에 옵니다. "고객이 최근 답변이 예전보다 부실하다고 합니다." 비용을 줄인 시점과 품질이 떨어진 시점을 연결할 수 있는 팀은 빠르게 롤백합니다. 연결할 수 없는 팀은 "원래 이랬나?"를 2주 더 논의합니다.

저는 팀들이 비용 최적화에 성공한 직후, 품질 저하를 한 달 넘게 모른 채 운영하는 경우를 여러 번 봤습니다. 문제는 품질이 떨어진 게 아닙니다. 품질이 떨어졌는지 판단할 기준이 코드에 없었다는 겁니다. 사람이 응답을 읽어야만 품질을 판단할 수 있는 구조에서는, 트래픽이 늘어나는 순간 평가가 멈춥니다.

그래서 평가의 출발점은 정교한 AI 심판이 아닙니다. 명백한 실패를 값싸게, 자주, 자동으로 걸러내는 규칙층, 이것이 출발점입니다.

![LLM 출력 품질 평가 파이프라인](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/03/03-01-big-picture.ko.png)
*규칙 기반 평가가 명백한 실패를 먼저 거르고, 의미 평가가 그 다음에 오는 구조*
> 값싼 규칙층이 먼저 있어야 비싼 평가를 정말 필요한 곳에만 쓸 수 있습니다.

## 먼저 던지는 질문

- 형식 통과와 품질 통과는 왜 다른 검사여야 할까요?
- 평가 결과가 "실패했다"만 알려주면 왜 운영에 쓸 수 없을까요?
- 배포 전 평가와 배포 후 평가는 무엇이 달라야 할까요?

## 왜 사람 리뷰만으로는 안 되는가

![규칙 기반 평가가 명확한 실패를 거르는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/03/03-01-why-this-layer-matters.ko.png)

*규칙 기반 평가가 명확한 실패를 거르는 흐름*

하루에 LLM 호출이 100건이면 사람이 전부 읽을 수 있습니다. 1,000건이면 샘플링을 해야 합니다. 10,000건이면 샘플링조차 운영 부담입니다. 문제는 바로 이 지점입니다. 사람이 읽지 않는 9,000건 안에 형식이 깨진 응답, 핵심 정보가 빠진 응답, 허용 길이를 벗어난 응답이 섞여 있어도 아무도 모릅니다.

저는 한 팀이 프롬프트를 수정한 뒤, JSON 응답의 필수 키가 빠지는 비율이 15%까지 올라갔는데 2주간 발견하지 못한 경우를 봤습니다. 원인은 단순했습니다. 그 팀의 품질 관리 방법이 "주 1회 10건 샘플 리뷰"였고, 10건에는 그 실패가 포함되지 않았습니다.

자동 평가가 필요한 이유는 "사람보다 잘 판단해서"가 아닙니다. "사람이 보지 못하는 9,000건에서 명백한 실패를 즉시 잡아내서"입니다.

| 평가 방식 | 커버리지 | 비용 | 잡아내는 실패 |
|---|---|---|---|
| 사람 샘플 리뷰 | 1-5% | 높음 | 의미 품질, 톤, 정확성 |
| 규칙 기반 자동 | 100% | 거의 0 | 형식 오류, 길이 이탈, 키워드 누락 |
| LLM-as-judge | 5-20% | 중간 | 사실성, 유용성, 근거 품질 |

이 표가 보여주는 핵심은 역할 분담입니다. 규칙층이 100% 커버리지로 명백한 실패를 먼저 치우면, 비싼 사람 리뷰와 LLM judge는 정말 애매한 경계 케이스에 집중할 수 있습니다. 반대로 규칙층 없이 사람 리뷰만 하면, 리뷰어의 시간 절반이 "JSON이 깨졌네"처럼 기계적으로 잡을 수 있는 문제에 낭비됩니다.

## 최소 실행 예제 — 실패 이유를 설명하는 평가

```python
import json
import os
from dataclasses import asdict, dataclass

from groq import Groq

MODEL = "llama-3.1-8b-instant"

@dataclass
class EvalResult:
    passed: bool
    length_ok: bool
    keywords_ok: bool
    format_ok: bool
    failure_reasons: list[str]
    answer_length: int

def ask_for_json(client: Groq, topic: str) -> str:
    response = client.chat.completions.create(
        model=MODEL,
        temperature=0,
        messages=[
            {
                "role": "system",
                "content": (
                    "Return JSON only with keys 'answer' and 'keywords'. "
                    "The answer must be concise and technical."
                ),
            },
            {
                "role": "user",
                "content": f"Explain {topic} in JSON. Include one short answer and a keyword list.",
            },
        ],
        response_format={"type": "json_object"},
    )
    return response.choices[0].message.content or "{}"

def evaluate(text: str, expected_keywords: list[str], min_len: int = 60, max_len: int = 280) -> EvalResult:
    reasons: list[str] = []

    # Layer 1: 형식 검사
    try:
        payload = json.loads(text)
        answer = payload["answer"]
        keywords = payload["keywords"]
        format_ok = isinstance(answer, str) and isinstance(keywords, list)
        if not format_ok:
            reasons.append("type_mismatch: answer must be str, keywords must be list")
    except json.JSONDecodeError:
        reasons.append("json_parse_failed")
        return EvalResult(False, False, False, False, reasons, 0)
    except KeyError as e:
        reasons.append(f"missing_key: {e}")
        return EvalResult(False, False, False, False, reasons, 0)

    # Layer 2: 길이 검사
    length_ok = min_len <= len(answer) <= max_len
    if not length_ok:
        reasons.append(f"length_out_of_range: {len(answer)} (expected {min_len}-{max_len})")

    # Layer 3: 키워드 검사
    normalized = answer.lower() + " " + " ".join(str(k).lower() for k in keywords)
    missing = [kw for kw in expected_keywords if kw.lower() not in normalized]
    keywords_ok = not missing
    if missing:
        reasons.append(f"missing_keywords: {missing}")

    return EvalResult(
        passed=format_ok and length_ok and keywords_ok,
        length_ok=length_ok,
        keywords_ok=keywords_ok,
        format_ok=format_ok,
        failure_reasons=reasons,
        answer_length=len(answer),
    )

def main() -> None:
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    raw = ask_for_json(client, "Python's GIL")
    result = evaluate(raw, ["CPython", "thread", "lock"])
    print(json.dumps({"raw": json.loads(raw), "evaluation": asdict(result)}, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
```

이 코드에서 라이브러리 사용법은 중요하지 않습니다. 중요한 것은 설계 결정 세 가지입니다.

![형식·길이·키워드 검사가 분리된 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/03/03-02-what-to-notice-in-this-code.ko.png)

*형식·길이·키워드 검사가 분리된 구조*

**첫째, 검사를 Layer 1/2/3으로 분리합니다.** 형식이 깨지면 길이를 볼 필요가 없고, 길이가 벗어나도 키워드를 볼 수는 있습니다. 이렇게 나누면 실패 시 "그냥 품질이 낮다"가 아니라 "형식이 깨졌는지, 길이가 벗어났는지, 키워드가 빠졌는지"를 즉시 분류할 수 있습니다. 분류가 되어야 수정 방향이 정해집니다.

**둘째, `failure_reasons`가 행동 가능한 정보를 남깁니다.** `passed: false`만으로는 운영에 쓸 수 없습니다. "왜 실패했고 무엇을 고쳐야 하는가"가 함께 나와야 합니다. `missing_keywords: ["lock"]`이면 프롬프트에 해당 용어를 강조하는 지시를 추가하면 됩니다. `length_out_of_range: 312`이면 max_tokens를 조정하거나 프롬프트에 길이 제약을 명시하면 됩니다. 저는 팀들이 `passed/failed` 이진값만 남기다가, 실패가 늘었을 때 "왜 늘었지?"를 다시 전수 조사해야 했던 경우를 봤습니다. 처음부터 이유를 남기면 그 작업이 사라집니다.

**셋째, `min_len`과 `max_len`을 매개변수로 뺍니다.** 엔드포인트마다 기대하는 응답 길이가 다릅니다. 요약 엔드포인트는 50-200자, 설명 엔드포인트는 100-500자, 코드 생성 엔드포인트는 200-2000자일 수 있습니다. 하드코딩하면 새 엔드포인트를 추가할 때마다 evaluate 함수를 복제해야 합니다.

## JSON Schema로 형식 계약을 명확하게

규칙 기반 검사의 다음 단계는 스키마 검증입니다. 키 존재 여부만 보는 것은 "answer가 있나?"까지만 확인합니다. 스키마는 "answer가 문자열이고 60자 이상 280자 이하인가?", "keywords가 최소 1개 이상인 문자열 배열인가?"까지 한 번에 검사합니다.

```python
from jsonschema import ValidationError, validate

ANSWER_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {"type": "string", "minLength": 60, "maxLength": 280},
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
        },
    },
    "required": ["answer", "keywords"],
    "additionalProperties": False,
}

def validate_schema(payload: dict) -> tuple[bool, list[str]]:
    errors: list[str] = []
    try:
        validate(instance=payload, schema=ANSWER_SCHEMA)
    except ValidationError as exc:
        errors.append(f"schema_violation: {exc.json_path} - {exc.message}")
    return (not errors), errors
```

이 단계가 중요한 이유는 두 가지입니다. 첫째, 여러 팀이 하나의 응답 포맷을 공유할 때, 스키마 파일 하나가 계약서 역할을 합니다. "answer 필드가 숫자로 들어와도 되나요?" 같은 질문이 스키마를 보면 바로 답이 나옵니다. 둘째, 스키마 위반은 모호하지 않습니다. "keywords에 문자열 대신 정수가 들어왔다"는 해석의 여지가 없는 실패이므로, 자동 재시도나 자동 차단 규칙에 바로 연결할 수 있습니다.

실무에서 자주 보는 실수는 `additionalProperties: false`를 빠뜨리는 것입니다. 이걸 안 넣으면 모델이 `confidence`, `source`, `reasoning` 같은 필드를 임의로 추가해도 스키마가 통과합니다. 다운스트림 파이프라인이 예상하지 못한 필드 때문에 깨지는 건 배포 한참 뒤에야 발견됩니다.

## 배치 평가로 변경 전후를 비교하기

한 건씩 평가하는 것은 실시간 가드레일입니다. 배치 평가는 다른 역할입니다. 프롬프트 버전 A와 B를 같은 입력 세트에 돌려서, 합격률과 실패 유형이 어떻게 달라졌는지 비교하는 것입니다.

```python
from dataclasses import asdict

TEST_CASES = [
    {"topic": "Python's GIL", "expected_keywords": ["CPython", "thread", "lock"]},
    {"topic": "asyncio.gather", "expected_keywords": ["coroutine", "concurrent", "await"]},
    {"topic": "HTTP/2 multiplexing", "expected_keywords": ["stream", "frame", "connection"]},
]

def run_batch(client: Groq) -> dict:
    results = []
    for case in TEST_CASES:
        raw = ask_for_json(client, case["topic"])
        result = evaluate(raw, case["expected_keywords"])
        results.append({
            "topic": case["topic"],
            "passed": result.passed,
            "failure_reasons": result.failure_reasons,
            "answer_length": result.answer_length,
        })

    passed_count = sum(1 for r in results if r["passed"])
    return {
        "total": len(results),
        "passed": passed_count,
        "pass_rate": round(passed_count / len(results) * 100, 1),
        "failures": [r for r in results if not r["passed"]],
    }
```

**Expected output:**

```text
{
  "total": 3,
  "passed": 2,
  "pass_rate": 66.7,
  "failures": [
    {
      "topic": "asyncio.gather",
      "passed": false,
      "failure_reasons": ["missing_keywords: ['await']"],
      "answer_length": 81
    }
  ]
}
```

이 출력이 운영에 유용한 이유는 실패가 행동 가능한 질문으로 변환되기 때문입니다. "asyncio.gather 설명에서 await이 빠졌다"는 프롬프트에 "반드시 await 키워드를 언급하라"는 지시를 추가하면 해결되는 문제입니다. 반대로 "pass_rate 66.7%"만 보면 어디를 고쳐야 할지 모릅니다.

배치 평가의 핵심 규칙 하나: 테스트 케이스를 코드 저장소에 버전 관리합니다. 프롬프트 v12에서 통과하던 케이스가 v13에서 실패하면, git diff로 프롬프트 변경과 실패 변경을 같은 커밋 히스토리에서 추적할 수 있습니다. 이 연결이 끊어지면 "이번 변경이 문제인가 아닌가?"를 매번 처음부터 조사해야 합니다.

## 평가 결과를 배포 게이트로 쓰기

![규칙층 위에 judge 모델이 올라가는 구조](https://yeongseon-books.github.io/book-public-assets/assets/llm-apps-ops-101/03/03-03-where-engineers-get-confused.ko.png)

*평가 레이어가 배포 결정에 영향을 미치는 흐름*

평가가 운영 도구가 되려면, 결과가 배포 결정에 실제로 영향을 미쳐야 합니다. "평가 돌렸는데 실패가 많네요, 그래도 배포할게요"가 반복되면 평가 시스템은 무시되기 시작합니다.

저는 팀들이 평가 파이프라인을 만들고도 배포와 연결하지 않아서, 3개월 뒤 "이거 돌리는 의미가 있나?"라는 논의가 나온 경우를 봤습니다. 평가가 의미를 갖는 조건은 하나입니다. 평가 실패가 배포를 실제로 막는 순간이 존재하는 것입니다.

권장하는 게이트 구조:

| 단계 | 기준 | 실패 시 행동 |
|---|---|---|
| 형식 게이트 | 스키마 실패율 < 5% | 배포 차단, 프롬프트 수정 |
| 핵심 시나리오 게이트 | 필수 테스트 케이스 전체 통과 | 배포 차단, 회귀 분석 |
| 품질 게이트 | pass_rate >= 이전 버전 - 3%p | 경고, 릴리스 노트에 명시 |

여기서 중요한 점은 "평균만 보면 안 된다"는 것입니다. 전체 pass_rate가 92%여도 특정 도메인 질문에서만 40%로 떨어질 수 있습니다. 평균은 이 문제를 감춥니다. 카테고리별로 분해해서 하위 10% 구간을 반드시 확인해야 합니다.

```python
def evaluate_batch_for_gate(results: list[dict], threshold: float = 0.90) -> dict:
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    pass_rate = passed / total if total > 0 else 0.0

    # 실패 유형 분포
    reason_counts: dict[str, int] = {}
    for r in results:
        for reason in r.get("failure_reasons", []):
            category = reason.split(":")[0]
            reason_counts[category] = reason_counts.get(category, 0) + 1

    gate_passed = pass_rate >= threshold
    return {
        "gate_passed": gate_passed,
        "pass_rate": round(pass_rate * 100, 1),
        "threshold": threshold * 100,
        "failure_distribution": reason_counts,
        "action": "deploy" if gate_passed else "block",
    }
```

이 함수가 반환하는 `failure_distribution`이 핵심입니다. 게이트를 통과하지 못했을 때, "형식이 문제인가 길이가 문제인가 키워드가 문제인가"를 한 번에 볼 수 있어야 수정 방향이 정해집니다. 단순히 "pass_rate 87% — 차단"만으로는 다음 행동을 결정할 수 없습니다.

## 오프라인 평가와 온라인 평가의 차이

배포 전에 돌리는 평가(오프라인)와 배포 후 실트래픽에서 돌리는 평가(온라인)는 같은 규칙을 쓰되 운영 방식이 다릅니다.

오프라인 평가는 고정된 테스트셋에서 결정적(deterministic) 결과를 기대합니다. 같은 프롬프트 버전을 같은 입력에 돌리면 pass_rate가 일정해야 합니다. 이게 흔들리면 모델 API의 비결정성(temperature > 0, 서버 측 변경)을 의심해야 합니다.

온라인 평가는 실트래픽의 분포가 테스트셋과 다를 수 있다는 전제에서 출발합니다. 테스트셋에 없는 질문 유형이 들어올 수 있고, 입력 길이의 분포가 달라질 수 있습니다. 그래서 온라인 평가는 "합격/불합격" 판정보다 "실패율 추이 모니터링"에 초점을 맞춥니다.

실무에서 자주 보는 실수: 오프라인 테스트셋을 한 번 만들고 6개월간 갱신하지 않는 것입니다. 그사이 사용자 질문 유형이 바뀌면, 테스트셋 pass_rate는 95%인데 실트래픽 만족도는 떨어지는 괴리가 생깁니다. 최소 월 1회, 실패한 실트래픽 샘플 10-20건을 테스트셋에 추가하는 루틴이 필요합니다.

## 어디서 자주 잘못 빠지는가

**"정교한 LLM judge가 없으면 평가가 아니다"라는 착각.** 실제 운영에서 가장 많은 가치를 만드는 평가는 규칙층입니다. JSON이 깨졌거나, 필수 키가 빠졌거나, 답변이 10자밖에 안 되는 경우는 AI 심판을 붙일 필요가 없습니다. 이런 명백한 실패를 100% 커버리지로 잡는 것만으로도 운영 품질은 크게 개선됩니다.

**"형식이 맞으면 좋은 답변이다"라는 반대쪽 착각.** 형식 통과는 필요조건이지 충분조건이 아닙니다. JSON이 완벽하고 길이도 적절한데, 내용이 완전히 틀린 응답은 규칙층을 통과합니다. 그래서 규칙층 위에 의미 평가 레이어(LLM-as-judge, 사람 리뷰)가 필요합니다. 다만 이 레이어는 비싸므로, 규칙층을 통과한 응답에만 선택적으로 적용하는 것이 현실적입니다.

**길이 기준을 절대값으로 고정하는 실수.** "모든 답변은 100-300자"라고 고정하면, 코드 생성 응답이나 목록 응답이 불필요하게 잘립니다. 엔드포인트별로, 또는 질문 유형별로 기준을 다르게 설정해야 합니다.

**테스트 케이스의 expected_keywords를 너무 빡빡하게 잡는 실수.** "반드시 CPython이라는 단어가 들어가야 한다"고 정하면, 모델이 "C로 작성된 Python 구현체"라고 우회 표현할 때 불합격 처리됩니다. 핵심 개념의 동의어까지 고려한 키워드 세트를 만들거나, 키워드 검사 대신 의미 유사도 검사로 올려야 할 수 있습니다.

## 체크리스트

- [ ] 형식 검사(JSON 파싱, 필수 키, 타입)를 별도 레이어로 분리한다
- [ ] 실패 시 `failure_reasons`에 수정 가능한 정보를 남긴다
- [ ] 엔드포인트별 길이 기준을 매개변수로 관리한다
- [ ] 배치 테스트 케이스를 코드 저장소에 버전 관리한다
- [ ] 평가 결과가 배포를 실제로 차단하는 게이트를 연결한다
- [ ] 월 1회 실트래픽 실패 샘플을 테스트셋에 추가한다

## 정리

평가가 운영 도구로 동작하는 순간은, 사람이 보기 전에 명백한 실패를 자동으로 걸러내기 시작할 때입니다. 형식 → 길이 → 키워드 순서의 규칙층이 100% 트래픽을 먼저 걸러내면, 비싼 LLM judge나 사람 리뷰는 정말 판단이 필요한 경계 케이스에만 집중할 수 있습니다.

다음 글에서는 이 평가 레이어를 통과한 응답이라도, 입력에 위험한 지시가 들어오거나 출력에 민감 정보가 새어 나갈 수 있는 보안 레이어를 다루겠습니다. 형식이 맞고 품질이 괜찮아도, 프롬프트가 탈취되거나 PII가 노출되면 운영 기준에서는 여전히 실패입니다.

## 처음 질문으로 돌아가기

- **형식 통과와 품질 통과는 왜 다른 검사여야 할까요?**
  형식 통과는 "파이프라인이 깨지지 않는가"를 확인하는 것이고, 품질 통과는 "내용이 기대에 부합하는가"를 확인하는 것입니다. 형식이 깨지면 아예 처리할 수 없으므로 먼저 거르고, 형식을 통과한 응답에만 품질 검사를 적용하는 것이 비용과 분류 정확도 양쪽에서 효율적입니다.
- **평가 결과가 "실패했다"만 알려주면 왜 운영에 쓸 수 없을까요?**
  `passed: false`만으로는 "프롬프트를 고쳐야 하는가, 모델을 바꿔야 하는가, 길이 제한을 조정해야 하는가"를 판단할 수 없습니다. `failure_reasons`에 실패 유형과 구체 수치가 있어야 다음 행동이 결정됩니다.
- **배포 전 평가와 배포 후 평가는 무엇이 달라야 할까요?**
  배포 전(오프라인)은 고정 테스트셋으로 결정적 합격/불합격을 판정합니다. 배포 후(온라인)는 실트래픽에서 실패율 추이를 모니터링하고, 테스트셋에 없는 새로운 실패 유형을 발견해 테스트셋을 갱신합니다.

## 시리즈 목차

- [LLM Apps Ops 101 (1/6): LLM 앱 모니터링과 로깅](https://yeongseonchoe.tistory.com/284)
- [LLM Apps Ops 101 (2/6): LLM 비용 추적과 최적화](https://yeongseonchoe.tistory.com/285)
- **LLM Apps Ops 101 (3/6): LLM 출력 품질 평가 (현재 글)**
- [LLM Apps Ops 101 (4/6): LLM 앱 보안](https://yeongseonchoe.tistory.com/287)
- [LLM Apps Ops 101 (5/6): LLM 앱 배포 전략](https://yeongseonchoe.tistory.com/288)
- [LLM Apps Ops 101 (6/6): LLM 앱 운영 완성](https://yeongseonchoe.tistory.com/289)
---

## 참고 자료

- [LLM Apps Ops 101 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/llm-apps-ops-101/ko)
### 공식 문서

- [OpenAI Structured Outputs guide](https://platform.openai.com/docs/guides/structured-outputs)
- [JSON Schema](https://json-schema.org/)

### 검증에 도움 되는 자료

- [G-Eval paper](https://arxiv.org/abs/2303.16634)
- [Promptfoo docs](https://www.promptfoo.dev/docs/)

Tags: LLMOps, Observability, Python, LLM

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
