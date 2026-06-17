---
title: "바이브코딩을 위한 Python 기초 (5/10): 제어 흐름"
series: python-101
episode: 5
language: ko
status: draft
targets:
  wordpress: true
  tistory: false
  medium: false
tags:
- 바이브코딩
- Python
- AI코딩
- 제어흐름
- if문
- for루프
- comprehension
seo_description: "바이브코딩 시대, AI가 만든 if/for 로직이 맞는지 검증하려면 제어 흐름을 읽을 줄 알아야 합니다."
---

# 바이브코딩을 위한 Python 기초 (5/10): 제어 흐름

AI에게 "60점 미만 학생은 제외하고 합격자 명단 만들어줘"라고 했더니 이런 코드가 나왔습니다.

```python
names = ["김철수", "이영희", "박민준", "최지원"]
scores = [92, 55, 78, 61]

result = []
i = 0
while i < len(names):
    if scores[i] >= 60:
        result.append(names[i] + ": " + str(scores[i]))
    i += 1
```

동작은 합니다. 그런데 뭔가 길고 어색합니다. 직접 돌아보니 이것과 같은 결과입니다.

```python
result = [f"{name}: {score}" for name, score in zip(names, scores) if score >= 60]
```

한 줄이고, 더 읽기 쉽습니다. AI가 처음 만든 코드가 틀린 건 아니지만, Python 제어 흐름에 익숙하다면 더 간결하게 요청할 수 있었습니다.

더 심각한 경우도 있습니다. AI가 만든 `if` 분기 로직이 경계값에서 미묘하게 틀리거나, `while` 루프가 특정 조건에서 무한 루프에 빠지거나, `zip`이 두 리스트의 길이가 다를 때 조용히 데이터를 잘라버리는 경우입니다. 이를 검증하려면 AI가 만든 제어 흐름을 직접 읽고 판단할 수 있어야 합니다.

> AI가 만든 분기와 루프가 올바른지 검증하는 것은 바이브코더의 핵심 역할입니다.

---

## 이 글에서 다룰 문제

- AI가 만든 `if value:` 조건이 왜 `value = 0`이나 `value = []` 때 의도와 다르게 동작하나?
- AI가 `while i < len(data):`로 만든 루프를 `for`와 `zip`으로 더 안전하게 바꾸려면?
- AI가 만든 comprehension이 읽기 어려울 때 언제 일반 `for`로 바꾸라고 해야 하나?
- AI가 `zip`으로 두 리스트를 묶을 때 길이가 달라도 에러 없이 통과하는 버그를 어떻게 잡나?
- 경계값(`>=` vs `>`, `<` vs `<=`)이 로직에 맞는지 빠르게 확인하는 방법은?

---

## truthy/falsy: AI 조건문에서 가장 흔한 버그 원인

Python의 `if` 조건은 `bool()`로 변환해서 평가합니다. 이 때문에 예상과 다르게 동작하는 경우가 있습니다.

**falsy 값의 목록**

```python
# 다음 값들은 모두 if 조건에서 False로 취급됩니다
False, None
0, 0.0                    # 숫자 0
"", [], {}, set()         # 빈 컨테이너
```

**AI 코드에서 자주 보이는 버그 패턴**

```python
# AI가 생성한 코드
def process(count):
    if count:                  # 의도: "count가 주어졌으면"
        return count * 10

process(0)     # None 반환 — count=0도 유효한 입력인데!
process(None)  # None 반환 — OK
```

`count = 0`은 유효한 입력일 수 있습니다. 하지만 `if count:`는 `0`을 falsy로 처리해서 함수가 아무것도 반환하지 않습니다. 의도가 "값이 주어지지 않은 경우"를 걸러내는 거라면 `if count is None:`이 정확합니다.

AI가 만든 조건문에서 이 문제를 발견하면: "이 if 조건이 0, 빈 문자열, 빈 리스트를 어떻게 처리하는지 확인해줘. 의도적으로 falsy를 이용하는 게 아니라면 명시적 None 체크로 바꿔줘."

## for 루프: AI가 만든 C 스타일 루프를 Python 방식으로 개선하기

AI는 종종 다른 언어 스타일의 인덱스 기반 루프를 만듭니다. Python에는 더 나은 방법이 있습니다.

**인덱스 루프 → enumerate**

```python
# AI가 자주 생성하는 패턴
names = ["ada", "bob", "carol"]
for i in range(len(names)):
    print(i + 1, names[i])

# Python 방식
for i, name in enumerate(names, start=1):
    print(i, name)
```

**두 리스트 병렬 순회 → zip**

```python
# AI가 자주 생성하는 패턴
for i in range(len(names)):
    print(names[i], "->", roles[i])

# Python 방식
for name, role in zip(names, roles):
    print(name, "->", role)
```

`zip`의 중요한 특성: **짧은 쪽 길이에 맞춰 자동으로 멈춥니다.** 두 리스트의 길이가 다를 때 에러가 나지 않고 조용히 데이터가 잘립니다.

```python
names = ["ada", "bob", "carol"]
scores = [92, 78]           # carol의 점수가 없음

for name, score in zip(names, scores):
    print(name, score)
# ada 92
# bob 78
# carol은 출력 안 됨 — 에러도 안 남!
```

이게 의도가 아니라면 `zip(..., strict=True)`로 길이 불일치를 즉시 잡을 수 있습니다.

```python
for name, score in zip(names, scores, strict=True):
    print(name, score)
# ValueError: zip() has arguments with different lengths
```

AI에게 두 리스트를 zip으로 묶는 코드를 요청할 때: "두 리스트 길이가 다르면 에러를 내야 해. strict=True 옵션 추가해줘."

## while 루프: AI 무한 루프 버그를 잡는 체크포인트

AI가 만든 `while` 루프에서 무한 루프 가능성을 점검하는 세 가지 체크포인트입니다.

**체크포인트 1: 루프 변수가 본문에서 변경되는가?**

```python
# 버그: remaining이 변하지 않는 조건
remaining = 5
while remaining > 0:
    print("tick")
    # remaining -= 1 이 빠졌음 → 무한 루프
```

**체크포인트 2: `while True` + `break` 패턴에서 break 조건이 도달 가능한가?**

```python
# AI가 자주 만드는 패턴
while True:
    line = input("> ")
    if line == "quit":
        break
    print("echo:", line)
```

이 패턴은 괜찮습니다. 단, `break` 조건이 사용자 입력, 외부 API, 타임아웃처럼 보장되지 않는 경우에는 무한 루프 가능성을 항상 검토해야 합니다.

**체크포인트 3: 재시도 루프에 상한이 있는가?**

```python
# AI가 생성한 재시도 코드 — 상한 없음
while True:
    response = api.call()
    if response.ok:
        break
    time.sleep(1)
# API가 영원히 실패하면 무한 루프

# 개선: 최대 재시도 횟수 추가
max_retries = 5
for attempt in range(max_retries):
    response = api.call()
    if response.ok:
        break
    time.sleep(1)
else:
    raise Exception("최대 재시도 횟수 초과")
```

AI에게 재시도 로직을 요청할 때: "최대 재시도 횟수 제한을 넣고, 초과 시 예외를 발생시켜줘."

## comprehension: 언제 쓰고 언제 for로 돌아가야 하나

comprehension은 "입력을 새 컬렉션으로 변환"할 때만 씁니다. 부수효과가 있으면 일반 `for`로 돌아갑니다.

```python
# 좋은 comprehension 사용 — 순수 변환
squares = [x * x for x in range(10)]
passed = [name for name, score in zip(names, scores) if score >= 60]
by_name = {name: score for name, score in zip(names, scores)}

# 나쁜 comprehension 사용 — 부수효과가 있음
[print(x) for x in nums]     # None으로 채워진 리스트가 만들어짐
[log(x) for x in nums]       # 부수효과를 위해 리스트를 만드는 코드
```

**comprehension 가독성 한계**

조건이 두 개 이상이거나 중첩이 깊으면 일반 `for`로 풀어야 합니다.

```python
# 읽기 어려운 comprehension
result = [f"{name}: {score}" for name, score in zip(names, scores)
          if score >= 60 if name.startswith("김")]

# 더 읽기 쉬운 for 루프
result = []
for name, score in zip(names, scores):
    if score < 60:
        continue
    if not name.startswith("김"):
        continue
    result.append(f"{name}: {score}")
```

AI에게: "이 comprehension이 조건이 두 개라 읽기 어려워. 일반 for 루프로 풀어줘. continue로 가드 패턴 써줘."

## Before / After

**Before — AI가 생성한 C 스타일 루프**

```python
names = ["ada", "bob", "carol", "dan"]
scores = [92, 71, 85, 58]

i = 0
result = []
while i < len(names):
    name = names[i]
    score = scores[i]
    if score >= 60:
        result.append(name + ":" + str(score))
    i += 1
print(result)
```

인덱스를 직접 관리하고, 두 리스트를 인덱스로 연결하고, 문자열 `+` 연결을 씁니다.

**After — Python 제어 흐름 활용**

```python
names = ["ada", "bob", "carol", "dan"]
scores = [92, 71, 85, 58]

result = [f"{name}:{score}" for name, score in zip(names, scores) if score >= 60]
print(result)
```

"두 시퀀스를 짝지어 돌면서 60점 이상인 것만 모은다"는 의도가 한 줄로 보입니다.

만약 실패한 경우에 로그를 남겨야 한다면 comprehension을 포기하고 for로 돌아갑니다.

```python
result = []
for name, score in zip(names, scores, strict=True):
    if score < 60:
        logger.warning(f"{name} 점수 미달: {score}")
        continue
    result.append(f"{name}:{score}")
```

## 바이브코딩할 때 자주 하는 실수

| 실수 패턴 | AI 코드 예시 | 문제 | 올바른 방향 |
| --- | --- | --- | --- |
| falsy 값 오용 | `if count:` | `count=0`도 걸러냄 | `if count is not None:` |
| 순회 중 리스트 수정 | `for x in items: items.remove(x)` | 인덱스 어긋남, 원소 건너뜀 | `items = [x for x in items if cond(x)]` |
| zip 길이 불일치 무시 | `zip(a, b)` (길이 다름) | 조용히 데이터 잘림 | `zip(a, b, strict=True)` |
| comprehension에 부수효과 | `[print(x) for x in nums]` | None 리스트 생성 | 일반 for 루프 사용 |
| while 무한 루프 | 재시도에 상한 없음 | 서비스 장애 | 최대 횟수 제한 추가 |
| 경계값 오류 | `if score > 60` vs `>= 60` | 60점 처리 방식 다름 | 경계값 테스트 케이스로 확인 |

## AI에게 이 주제 관련 질문하는 팁

**루프 개선 요청**

나쁜 프롬프트: "루프 최적화해줘"

좋은 프롬프트: "이 while 루프에서 인덱스를 직접 관리하고 있어. enumerate와 zip 써서 Python 스타일로 바꿔줘. 두 리스트 길이가 다를 때 에러 내도록 strict=True 추가해줘."

**조건 논리 검증 요청**

좋은 프롬프트: "이 if-elif 분기에서 score=60, score=90 경계값이 어느 분기로 들어가는지 설명해줘. 의도와 맞는지 확인하고 싶어."

**comprehension 가독성**

좋은 프롬프트: "이 comprehension에 조건이 두 개 달려 있어서 읽기 어려워. for 루프로 풀고, 실패 케이스는 continue로 먼저 걸러내는 guard 패턴으로 작성해줘."

**무한 루프 방어**

좋은 프롬프트: "이 while True 루프에 최대 재시도 횟수(5회)와 타임아웃(10초) 조건을 동시에 추가해줘. 둘 중 하나라도 초과하면 예외를 발생시켜."

## 운영 체크리스트

- [ ] AI가 만든 `if value:` 조건에서 `value = 0`이나 빈 컨테이너가 들어올 가능성 확인
- [ ] `zip(a, b)` 코드에서 두 시퀀스 길이가 항상 같다고 보장되는지 확인, 아니면 `strict=True` 추가
- [ ] `while True` 루프에 도달 가능한 `break` 조건이 있는지 확인
- [ ] 재시도 루프에 최대 횟수나 타임아웃 상한이 있는지 확인
- [ ] comprehension 안에 `print`, 파일 쓰기, 외부 상태 변경 등 부수효과가 없는지 확인
- [ ] 경계값(`>=` vs `>`)이 요구사항과 일치하는지 테스트 케이스로 확인

## 처음 질문으로 돌아가기

**AI의 `if value:` 조건이 `value = 0`일 때 의도와 다르게 동작하는 이유는?**
`0`, `""`, `[]`, `None`은 모두 Python에서 falsy입니다. `if value:`는 이 모든 경우를 False로 처리합니다. "값이 전달되지 않은 경우"를 걸러내려면 `if value is None:`으로 명시적으로 체크해야 합니다.

**AI의 `while i < len(data):` 루프를 더 안전하게 바꾸려면?**
순회할 대상이 있을 때는 `for`가 자연스럽습니다. 두 리스트를 병렬로 순회한다면 `zip`을 쓰고, `strict=True`로 길이 불일치를 잡으세요. 인덱스가 필요하다면 `enumerate`를 씁니다.

**AI의 comprehension이 읽기 어려울 때 언제 for로 바꿔야 하나?**
조건이 두 개 이상이거나, 부수효과(로그, 파일 쓰기, 외부 상태 변경)가 있거나, 중첩이 두 단계 이상이면 일반 `for` 루프가 더 읽기 쉽습니다.

**AI가 `zip`으로 두 리스트를 묶을 때 길이가 달라도 에러 없이 통과하는 버그를 어떻게 잡나?**
`zip(a, b, strict=True)`를 쓰면 길이가 다를 때 즉시 `ValueError`를 발생시킵니다. 데이터가 조용히 잘리는 버그를 예방할 수 있습니다.

**경계값(`>=` vs `>`)이 맞는지 빠르게 확인하는 방법은?**
AI에게 "이 조건에서 score=60일 때 어느 분기로 가는지 설명해줘"라고 물어보거나, 경계값을 직접 REPL에서 테스트해보세요. `label(60)`, `label(59)`, `label(61)` 세 케이스를 확인하면 경계값 로직을 빠르게 검증할 수 있습니다.

## 정리

바이브코딩에서 AI가 만든 제어 흐름을 검증하는 능력은 코드 품질을 결정하는 핵심입니다. truthy/falsy 규칙으로 조건문을 읽고, `zip`과 `enumerate`로 루프를 개선하고, comprehension의 한계를 알고 for 루프로 전환하는 판단을 할 수 있으면 AI 코드를 단순히 실행하는 것에서 나아가 신뢰할 수 있는 코드로 만들 수 있습니다.
