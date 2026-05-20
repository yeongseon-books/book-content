---
series: computer-science-101
episode: 3
title: "Computer Science 101 (3/10): 데이터 표현"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 이진수
  - 문자 인코딩
  - UTF-8
  - 부동소수점
  - 자료형
seo_description: 이진수, UTF-8 문자 인코딩, 2의 보수 정수 표현 및 부동소수점 오차의 원인과 실무 해결책을 상세히 정리합니다.
last_reviewed: '2026-05-12'
---

# Computer Science 101 (3/10): 데이터 표현

컴퓨터는 결국 0과 1만 다룬다는 말을 자주 듣지만, 이 문장을 실제 디버깅으로 연결하는 사람은 많지 않습니다. 글자가 깨지고, 금액 계산이 틀어지고, 다른 언어로 옮기자 정수가 넘치는 순간 비로소 데이터 표현이 운영 문제로 보이기 시작합니다.

이 글은 Computer Science 101 시리즈의 3번째 글입니다.

여기서는 비트와 바이트, 문자 인코딩, 정수와 부동소수점 표현을 따라가며 데이터가 어떻게 의미를 얻는지 정리하겠습니다.

## 먼저 던지는 질문

- 컴퓨터는 0과 1만으로 숫자, 문자, 이미지를 어떻게 저장할까요?
- ASCII와 UTF-8은 무엇이 다르고 왜 바이트 수가 달라질까요?
- 음수는 왜 2의 보수 방식으로 표현할까요?

## 큰 그림

![Computer Science 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/03/03-01-concept-at-a-glance.ko.png)

*Computer Science 101 3장 흐름 개요*

이 그림에서는 데이터 표현를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 데이터 표현의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 이 글에서 배울 것

- 이진수와 십진수 변환 원리
- ASCII와 UTF-8 인코딩의 차이
- 부호 있는 정수와 2의 보수 표현
- 부동소수점이 근사값이라는 사실과 그 영향

## 왜 중요한가

문자 깨짐, 부동소수점 오차, 정수 오버플로우는 모두 데이터 표현을 모르면 해결할 수 없는 문제입니다. `0.1 + 0.2 != 0.3`이 되는 이유를 알아야 금융 시스템에서 올바른 설계를 할 수 있습니다.

> 데이터 표현 = 디지털 세계의 물리법칙

비트 수준의 이해가 디버깅과 성능 최적화의 기초입니다.

## 한눈에 보는 개념

> 모든 데이터는 비트(0/1)로 표현됩니다. 인코딩 규칙이 비트열에 의미를 부여합니다.

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| Bit | 0 또는 1 하나를 담는 최소 저장 단위 |
| Byte | 8개의 비트로 이루어진 단위 |
| ASCII | 영문자를 위한 7비트 문자 인코딩 표준 |
| UTF-8 | 전 세계 문자를 1~4바이트로 표현하는 가변 길이 인코딩 |
| Floating point | IEEE 754 규칙에 따라 실수를 근사 표현하는 방식 |

## Before / After

**Before — 데이터 표현을 모를 때:**

```python
# Why isn't 0.1 + 0.2 equal to 0.3?
result = 0.1 + 0.2
print(result)          # 0.30000000000000004
print(result == 0.3)   # False — and you do not know why
```

**After — 데이터 표현을 알 때:**

```python
from decimal import Decimal

# Floating point is a binary approximation; use Decimal for exact arithmetic.
result = Decimal("0.1") + Decimal("0.2")
print(result)              # 0.3
print(result == Decimal("0.3"))  # True
```

**Expected output:** `float`에서는 `0.30000000000000004`가 보이지만 `Decimal`에서는 정확히 `0.3`이 출력되어 표현 방식의 차이가 드러나야 합니다.

## 단계별로 따라하기

### 1단계: 이진수와 십진수 변환

```python
# Decimal -> binary
print(bin(42))      # 0b101010
print(bin(255))     # 0b11111111

# Binary -> decimal
print(int("101010", 2))   # 42
print(int("11111111", 2)) # 255

# Verify the conversion principle in code
def to_binary(n: int) -> str:
    """Convert a decimal integer to a binary string."""
    if n == 0:
        return "0"
    bits = []
    while n > 0:
        bits.append(str(n % 2))
        n //= 2
    return "".join(reversed(bits))

print(to_binary(42))  # 101010
```

### 2단계: ASCII와 UTF-8

```python
# ASCII: one byte per English character
print(ord("A"))        # 65
print(chr(65))         # A
print(ord("a"))        # 97

# UTF-8: a Korean character takes three bytes
korean = "가"
print(ord(korean))                  # 44032
print(korean.encode("utf-8"))       # b'\xea\xb0\x80' (3 bytes)
print(len(korean))                  # 1 (character count)
print(len(korean.encode("utf-8")))  # 3 (byte count)

# Emoji: four bytes
emoji = "🐍"
print(len(emoji))                   # 1 (character count)
print(len(emoji.encode("utf-8")))   # 4 (byte count)
```

### 3단계: 정수의 크기와 2의 보수

```python
# Python integers have no size limit (arbitrary precision)
big_number = 2 ** 100
print(big_number)  # 1267650600228229401496703205376

# But C, Java, and others use fixed sizes
# 8-bit signed: -128 to 127
# 32-bit signed: -2,147,483,648 to 2,147,483,647

# Two's complement represents negatives
def twos_complement(n: int, bits: int = 8) -> str:
    """Return the two's-complement representation of n."""
    if n >= 0:
        return format(n, f"0{bits}b")
    return format((1 << bits) + n, f"0{bits}b")

print(twos_complement(5))    # 00000101
print(twos_complement(-5))   # 11111011
print(twos_complement(-1))   # 11111111
```

### 4단계: 부동소수점의 한계

```python
import struct

# Inspect the actual stored value of 0.1
print(f"{0.1:.20f}")  # 0.10000000000000000555

# IEEE 754 double-precision bit pattern
bits = struct.pack("d", 0.1)
print(" ".join(f"{b:08b}" for b in bits))

# Compare with a tolerance
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True

# For money, use Decimal or integer cents
price_cents = 1099  # $10.99 stored as cents
tax_cents = int(price_cents * 0.1)
total_cents = price_cents + tax_cents
print(f"${total_cents / 100:.2f}")  # $12.09
```

### 5단계: 데이터 크기 감각 익히기

```python
data_sizes = {
    "1 bit": 1,
    "1 byte": 8,
    "1 ASCII character": 8,
    "1 UTF-8 Korean char": 24,
    "32-bit int": 32,
    "64-bit double": 64,
    "1 KB": 8 * 1024,
    "1 MB": 8 * 1024 ** 2,
    "1 GB": 8 * 1024 ** 3,
}

for name, bits in data_sizes.items():
    print(f"{name:22s} = {bits:>15,} bits")
```

## 이 코드에서 먼저 봐야 할 점

- 같은 비트열도 해석 방식에 따라 숫자, 문자, 색상이 됩니다
- UTF-8은 문자마다 바이트 수가 다르므로 `len(문자열) != len(바이트열)`입니다
- 부동소수점은 근사 표현이므로 직접 비교하면 안 됩니다
- Python 정수는 오버플로우가 없지만, 다른 언어에서는 주의해야 합니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 문자열 길이와 바이트 길이를 혼동 | 한글, 이모지에서 잘못된 슬라이싱 | `len()`은 문자 수, `len(encode())`는 바이트 수 |
| 부동소수점을 `==`로 비교 | `0.1 + 0.2 != 0.3` | `math.isclose()`를 사용합니다 |
| 금융 계산에 float 사용 | 센트 단위 오차 누적 | `Decimal` 또는 정수(센트)를 사용합니다 |
| 인코딩 지정 없이 파일 읽기 | 문자 깨짐 발생 | `encoding="utf-8"`을 명시합니다 |
| Python 정수가 다른 언어에서도 무한하다고 가정 | 오버플로우 발생 | 언어별 정수 범위를 확인합니다 |

## 실무에서는 이렇게 쓰입니다

- 웹 API에서 Content-Type 헤더의 charset=utf-8 설정
- 금융 시스템에서 Decimal 또는 정수 기반 금액 처리
- 데이터베이스 컬럼 타입 선택 시 정수 크기 결정 (INT vs BIGINT)
- 파일 처리 시 BOM(Byte Order Mark)과 인코딩 감지
- 네트워크 프로토콜에서 바이트 순서(엔디안) 처리

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 저장 크기보다 데이터의 의미와 제약을 먼저 봅니다. 금액은 부동소수점이 아니라 정수 센트나 Decimal로, 식별자는 숫자처럼 보여도 UUID나 문자열 규약으로 다룹니다.

문자 인코딩도 초기에 표준을 못 박습니다. 프로젝트 전역에서 UTF-8을 기본으로 삼고, 파일·HTTP 헤더·DB 연결마다 그 사실을 명시하는 습관이 수많은 깨짐 문제를 예방합니다.

## 체크리스트

- [ ] 이진수와 십진수를 상호 변환할 수 있는가
- [ ] ASCII와 UTF-8의 차이를 설명할 수 있는가
- [ ] 부동소수점 오차의 원인을 이해했는가
- [ ] 문자열 길이와 바이트 길이의 차이를 구분하는가
- [ ] 금융 데이터에 float을 사용하면 안 되는 이유를 아는가

## 연습 문제

1. 0부터 255까지의 정수를 이진수와 16진수로 함께 출력하는 함수를 작성해 보세요.
2. 영문, 한글, 일본어, 이모지를 골라 UTF-8 바이트 길이를 비교하는 표를 만들어 보세요.
3. `float`와 `Decimal`로 `0.1`을 100번씩 더한 결과를 비교해 차이를 기록해 보세요.

## 정리 및 다음 단계

컴퓨터의 모든 데이터는 비트로 표현됩니다. 인코딩 규칙이 비트열에 의미를 부여합니다. 정수는 2의 보수로, 문자는 UTF-8로, 소수는 IEEE 754 부동소수점으로 표현합니다. 각 표현 방식의 한계를 알아야 올바른 설계가 가능합니다.

다음 글에서는 데이터를 효율적으로 처리하는 방법인 알고리즘과 그 성능을 측정하는 복잡도를 다룹니다.

## 처음 질문으로 돌아가기

- **컴퓨터는 0과 1만으로 숫자, 문자, 이미지를 어떻게 저장할까요?**
  - 본문의 기준은 데이터 표현를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **ASCII와 UTF-8은 무엇이 다르고 왜 바이트 수가 달라질까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **음수는 왜 2의 보수 방식으로 표현할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Computer Science 101 (1/10): Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): 계산과 프로그램](./02-computation-and-programs.md)
- **데이터 표현 (현재 글)**
- 알고리즘과 복잡도 (예정)
- 컴퓨터 구조 (예정)
- 운영체제 (예정)
- 네트워크 (예정)
- 데이터베이스 (예정)
- 소프트웨어 엔지니어링 (예정)
- AI와 데이터사이언스까지의 연결 (예정)

<!-- toc:end -->

## 참고 자료

- [Unicode 공식 문서](https://home.unicode.org/)
- [Python 문서 — Floating Point Arithmetic: Issues and Limitations](https://docs.python.org/3/tutorial/floatingpoint.html)
- [What Every Programmer Should Know About Floating-Point](https://floating-point-gui.de/)
- [Joel Spolsky — The Absolute Minimum About Unicode](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)

Tags: Computer Science, 이진수, 문자 인코딩, UTF-8, 부동소수점, 자료형
