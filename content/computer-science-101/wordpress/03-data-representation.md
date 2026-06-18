---
series: computer-science-101
episode: 3
title: "바이브코딩을 위한 컴퓨터 과학 기초 (3/10): 데이터 표현"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Computer Science
  - 이진수
  - 문자 인코딩
  - 부동소수점
  - AI 코딩
seo_description: 이진수, UTF-8 인코딩, 부동소수점 오차를 바이브코딩 관점에서 이해합니다. AI가 만든 코드에서 데이터 관련 버그를 잡는 기초입니다.
language: ko
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 컴퓨터 과학 기초 (3/10): 데이터 표현

> 이 글은 **바이브코딩을 위한 컴퓨터 과학 기초** 시리즈의 세 번째 글입니다. AI에게 코드를 시키려면 컴퓨터가 어떻게 동작하는지 기본은 알아야 합니다.

---

AI가 만들어준 금액 계산 코드를 그대로 썼다가 나중에 1원 오차가 쌓이는 걸 발견했다면, 이 글이 그 이유를 설명해줍니다. 글자가 깨지고, 금액 계산이 틀어지고, 다른 언어로 옮기자 정수가 넘치는 순간은 모두 데이터 표현을 모르면 해결할 수 없는 문제입니다.

컴퓨터는 결국 0과 1만 다룬다는 말을 자주 듣지만, 이 문장을 실제 디버깅으로 연결하는 사람은 많지 않습니다. AI가 생성한 코드에서 데이터 표현 관련 버그를 발견하고 수정하려면 비트 수준의 이해가 필요합니다.

> **바이브코딩 관점:** AI에게 금융 계산 코드를 요청할 때 "float 대신 Decimal을 써줘"라고 말할 수 있어야 합니다. 그 이유를 모르면 AI가 잘못된 코드를 줘도 알아챌 수 없습니다.

---

## 이 글에서 다룰 문제

- 컴퓨터는 0과 1만으로 숫자, 문자, 이미지를 어떻게 저장할까요?
- ASCII와 UTF-8은 무엇이 다르고 왜 바이트 수가 달라질까요?
- 음수는 왜 2의 보수 방식으로 표현할까요?
- AI가 만든 코드에서 데이터 표현 오류를 어떻게 발견할까요?
- 바이브코더가 데이터 표현에서 가장 자주 놓치는 포인트는 무엇일까요?

---

## 핵심 개념 한 줄 정리

> **데이터 표현 = 디지털 세계의 물리법칙**

모든 데이터는 비트(0/1)로 표현됩니다. 인코딩 규칙이 비트열에 의미를 부여합니다.

| 용어 | 설명 |
| --- | --- |
| Bit | 0 또는 1 하나를 담는 최소 저장 단위 |
| Byte | 8개의 비트로 이루어진 단위 |
| ASCII | 영문자를 위한 7비트 문자 인코딩 표준 |
| UTF-8 | 전 세계 문자를 1~4바이트로 표현하는 가변 길이 인코딩 |
| Floating point | IEEE 754 규칙에 따라 실수를 근사 표현하는 방식 |

---

## Before / After: 데이터 표현을 알기 전과 후

**Before — 데이터 표현을 모를 때:**

```python
# 왜 0.1 + 0.2는 0.3과 같지 않을까?
result = 0.1 + 0.2
print(result)          # 0.30000000000000004
print(result == 0.3)   # False
```

AI에게 "금액 더하는 함수 만들어줘"라고 하면 float을 쓴 코드가 나올 수 있습니다. 이렇게 쓰면 금액 오차가 쌓입니다.

**After — 데이터 표현을 알 때:**

```python
from decimal import Decimal

# 부동소수점은 2진 근사값이므로 정확한 계산에는 Decimal 사용
result = Decimal("0.1") + Decimal("0.2")
print(result)              # 0.3
print(result == Decimal("0.3"))  # True
```

AI에게 "금융 계산이므로 Decimal 타입을 써서 정확도를 보장해줘"라고 요청하면 올바른 코드를 받을 수 있습니다.

---

## 핵심 내용: 바이브코딩 관점에서 보는 데이터 표현

### 이진수와 십진수 변환

```python
# Decimal -> binary
print(bin(42))      # 0b101010
print(bin(255))     # 0b11111111

# Binary -> decimal
print(int("101010", 2))   # 42

def to_binary(n: int) -> str:
    if n == 0:
        return "0"
    bits = []
    while n > 0:
        bits.append(str(n % 2))
        n //= 2
    return "".join(reversed(bits))

print(to_binary(42))  # 101010
```

### ASCII와 UTF-8: 한글이 3바이트인 이유

```python
# ASCII: 영문자 1개당 1바이트
print(ord("A"))        # 65

# UTF-8: 한글 1글자는 3바이트
korean = "가"
print(korean.encode("utf-8"))       # b'\xea\xb0\x80' (3 bytes)
print(len(korean))                  # 1 (문자 수)
print(len(korean.encode("utf-8")))  # 3 (바이트 수)

# 이모지: 4바이트
emoji = "🐍"
print(len(emoji.encode("utf-8")))   # 4 (byte count)
```

AI에게 "한글 문자열 처리 코드 짜줘"라고 할 때 `len()`이 문자 수를 반환하는지 바이트 수를 반환하는지 구분해야 합니다.

### 부동소수점의 한계

```python
import struct

# 0.1의 실제 저장값 확인
print(f"{0.1:.20f}")  # 0.10000000000000000555

# 허용 오차를 두고 비교
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True

# 금액 계산에는 Decimal 또는 정수 cents 사용
price_cents = 1099  # $10.99 stored as cents
tax_cents = int(price_cents * 0.1)
total_cents = price_cents + tax_cents
print(f"${total_cents / 100:.2f}")  # $12.09
```

### 권한 플래그로 보는 비트 연산

```python
# 권한을 비트 플래그로 관리
READ = 0b100    # 4
WRITE = 0b010   # 2
EXECUTE = 0b001 # 1

def describe_permissions(perm: int) -> str:
    parts = []
    if perm & READ:
        parts.append("읽기")
    if perm & WRITE:
        parts.append("쓰기")
    if perm & EXECUTE:
        parts.append("실행")
    return ", ".join(parts) if parts else "없음"

admin = READ | WRITE | EXECUTE  # 7
print(describe_permissions(admin))  # 읽기, 쓰기, 실행
```

---

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| AI 금융 코드에서 float 그대로 사용 | 센트 단위 오차 누적 | AI에게 "Decimal 또는 정수(센트)를 써줘" 요청 |
| 문자열 길이와 바이트 길이를 혼동 | 한글, 이모지에서 잘못된 슬라이싱 | `len()`은 문자 수, `len(encode())`는 바이트 수 |
| 부동소수점을 `==`로 비교 | `0.1 + 0.2 != 0.3` | `math.isclose()`를 사용합니다 |
| 인코딩 지정 없이 파일 읽기 | 문자 깨짐 발생 | AI에게 `encoding="utf-8"` 명시 요청 |
| Python 정수가 다른 언어에서도 무한하다고 가정 | 오버플로우 발생 | 언어별 정수 범위를 확인합니다 |

---

## AI 코딩 팁

1. **금융 코드에는 Decimal을 명시하세요.** "금액 계산이므로 float 대신 Decimal 타입을 써줘"라고 요청하면 정확한 코드를 받을 수 있습니다.
2. **문자열 처리 시 인코딩을 명시하세요.** "파일을 UTF-8로 읽고 한글 처리할 때 바이트 길이를 조심해줘"라고 하면 인코딩 버그를 예방할 수 있습니다.
3. **비교 연산 시 isclose를 요청하세요.** "부동소수점 비교는 math.isclose()를 써줘"라고 명시하면 정밀도 오류를 막을 수 있습니다.

---

## 체크리스트

- [ ] 이진수와 십진수를 상호 변환할 수 있는가
- [ ] ASCII와 UTF-8의 차이를 설명할 수 있는가
- [ ] 부동소수점 오차의 원인을 이해했는가
- [ ] 문자열 길이와 바이트 길이의 차이를 구분하는가
- [ ] AI 코드에서 금융 데이터에 float를 사용하면 안 되는 이유를 아는가

---

## 처음 질문으로 돌아가기

- **컴퓨터는 0과 1만으로 숫자, 문자, 이미지를 어떻게 저장할까요?**
  인코딩 규칙이 비트열에 의미를 부여합니다. 숫자는 이진수로, 문자는 UTF-8로, 소수는 IEEE 754 부동소수점으로 표현됩니다.

- **ASCII와 UTF-8은 무엇이 다를까요?**
  ASCII는 영문자만 1바이트로 표현하고, UTF-8은 전 세계 문자를 1~4바이트로 가변 표현합니다. 한글은 3바이트입니다.

- **AI가 만든 코드에서 데이터 표현 오류를 어떻게 발견할까요?**
  금융 계산에 float가 사용됐는지, 문자열 처리에 바이트 길이와 문자 길이가 혼용됐는지, 부동소수점 비교에 `==`가 쓰였는지 확인합니다.

---

## 정리

컴퓨터의 모든 데이터는 비트로 표현됩니다. 인코딩 규칙이 비트열에 의미를 부여합니다. 각 표현 방식의 한계를 알아야 AI가 만든 코드를 올바르게 검토할 수 있습니다.

다음 글에서는 데이터를 효율적으로 처리하는 알고리즘과 그 성능을 AI에게 요청하는 방법을 봅니다.

---

## 참고 자료

- [Unicode 공식 문서](https://home.unicode.org/)
- [Python 문서 — Floating Point Arithmetic](https://docs.python.org/3/tutorial/floatingpoint.html)
- [What Every Programmer Should Know About Floating-Point](https://floating-point-gui.de/)
- [Joel Spolsky — The Absolute Minimum About Unicode](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 컴퓨터 과학 기초 (1/10): Computer Science란 무엇인가?
- 바이브코딩을 위한 컴퓨터 과학 기초 (2/10): 계산과 프로그램
- **바이브코딩을 위한 컴퓨터 과학 기초 (3/10): 데이터 표현 (현재 글)**
- 바이브코딩을 위한 컴퓨터 과학 기초 (4/10): 알고리즘과 복잡도
- 바이브코딩을 위한 컴퓨터 과학 기초 (5/10): 컴퓨터 구조
- 바이브코딩을 위한 컴퓨터 과학 기초 (6/10): 운영체제
- 바이브코딩을 위한 컴퓨터 과학 기초 (7/10): 네트워크
- 바이브코딩을 위한 컴퓨터 과학 기초 (8/10): 데이터베이스
- 바이브코딩을 위한 컴퓨터 과학 기초 (9/10): 소프트웨어 엔지니어링
- 바이브코딩을 위한 컴퓨터 과학 기초 (10/10): AI와 데이터사이언스까지의 연결
<!-- toc:end -->

Tags: 바이브코딩, Computer Science, 이진수, 문자 인코딩, 부동소수점, AI 코딩
