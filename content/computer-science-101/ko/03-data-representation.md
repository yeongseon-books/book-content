---
series: computer-science-101
episode: 3
title: 데이터 표현
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
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
seo_description: 이진수, 문자 인코딩(ASCII, UTF-8), 정수와 부동소수점 표현 방식을 다루는 CS 입문 시리즈입니다.
last_reviewed: '2026-05-04'
---

# 데이터 표현

> Computer Science 101 시리즈 (3/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 컴퓨터는 0과 1밖에 모르는데, 문자, 숫자, 이미지를 어떻게 저장하고 처리할까요?

> 컴퓨터 내부에서 모든 데이터는 비트(0 또는 1)의 나열입니다. 숫자 42도, 문자 'A'도, 이미지의 한 픽셀도 결국 비트로 표현됩니다. 같은 비트열이 맥락에 따라 정수가 되기도 하고 문자가 되기도 합니다. 이 글에서는 이진수, 문자 인코딩, 정수와 부동소수점의 표현 방식을 다룹니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 이진수와 십진수 변환
- ASCII와 UTF-8 문자 인코딩
- 정수의 부호 표현(2의 보수)
- 부동소수점의 원리와 정밀도 한계

## 왜 중요한가

문자 깨짐, 부동소수점 오차, 정수 오버플로우는 모두 데이터 표현을 모르면 해결할 수 없는 문제입니다. `0.1 + 0.2 != 0.3`이 되는 이유를 알아야 금융 시스템에서 올바른 설계를 할 수 있습니다.

> 데이터 표현 = 디지털 세계의 물리법칙

비트 수준의 이해가 디버깅과 성능 최적화의 기초입니다.

## 개념 한눈에 보기

> 모든 데이터는 비트(0/1)로 표현됩니다. 인코딩 규칙이 비트열에 의미를 부여합니다.

```text
비트열: 01000001
   │
   ├── 정수로 해석 → 65
   ├── ASCII로 해석 → 'A'
   └── 컬러값으로 해석 → 매우 어두운 파란색
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 비트(bit) | 0 또는 1을 저장하는 가장 작은 단위 |
| 바이트(byte) | 8비트의 묶음 |
| ASCII | 영문 문자를 7비트로 인코딩하는 표준 |
| UTF-8 | 전 세계 문자를 1~4바이트로 인코딩하는 가변 길이 표준 |
| 부동소수점(floating point) | 소수를 근사적으로 표현하는 IEEE 754 규격 |

## Before / After

**Before — 데이터 표현을 모를 때:**

```python
# 왜 0.1 + 0.2가 0.3이 아닐까?
result = 0.1 + 0.2
print(result)          # 0.30000000000000004
print(result == 0.3)   # False — 이유를 모릅니다
```

**After — 데이터 표현을 알 때:**

```python
from decimal import Decimal

# 부동소수점은 이진 근사이므로 정확한 계산에는 Decimal을 사용합니다
result = Decimal("0.1") + Decimal("0.2")
print(result)              # 0.3
print(result == Decimal("0.3"))  # True
```

## 실습: 단계별로 따라하기

### 1단계: 이진수와 십진수 변환

```python
# 십진수 → 이진수
print(bin(42))      # 0b101010
print(bin(255))     # 0b11111111

# 이진수 → 십진수
print(int("101010", 2))   # 42
print(int("11111111", 2)) # 255


# 변환 원리를 코드로 확인합니다
def to_binary(n: int) -> str:
    """십진수를 이진수 문자열로 변환합니다."""
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
# ASCII: 영문 1바이트
print(ord("A"))        # 65
print(chr(65))         # A
print(ord("a"))        # 97

# UTF-8: 한글 3바이트
korean = "가"
print(ord(korean))                # 44032
print(korean.encode("utf-8"))     # b'\xea\xb0\x80' (3바이트)
print(len(korean))                # 1 (문자 수)
print(len(korean.encode("utf-8")))  # 3 (바이트 수)

# 이모지: 4바이트
emoji = "🐍"
print(len(emoji))                  # 1 (문자 수)
print(len(emoji.encode("utf-8")))  # 4 (바이트 수)
```

### 3단계: 정수의 크기와 2의 보수

```python
# Python의 정수는 크기 제한이 없습니다 (임의 정밀도)
big_number = 2 ** 100
print(big_number)  # 1267650600228229401496703205376

# 하지만 C, Java 등에서는 고정 크기입니다
# 8비트 부호 있는 정수: -128 ~ 127
# 32비트 부호 있는 정수: -2,147,483,648 ~ 2,147,483,647

# 2의 보수로 음수를 표현합니다
def twos_complement(n: int, bits: int = 8) -> str:
    """n의 2의 보수 표현을 반환합니다."""
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

# 0.1의 실제 저장 값을 확인합니다
print(f"{0.1:.20f}")  # 0.10000000000000000555

# IEEE 754 double의 비트 표현
bits = struct.pack("d", 0.1)
print(" ".join(f"{b:08b}" for b in bits))

# 비교할 때는 오차 범위를 사용합니다
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True

# 금융 계산에는 Decimal 또는 정수(센트 단위)를 사용합니다
price_cents = 1099  # $10.99를 센트로 저장
tax_cents = int(price_cents * 0.1)
total_cents = price_cents + tax_cents
print(f"${total_cents / 100:.2f}")  # $12.09
```

### 5단계: 데이터 크기 감각 익히기

```python
data_sizes = {
    "1 bit": 1,
    "1 byte": 8,
    "ASCII 문자 1개": 8,
    "UTF-8 한글 1자": 24,
    "32비트 정수": 32,
    "64비트 double": 64,
    "1 KB": 8 * 1024,
    "1 MB": 8 * 1024 ** 2,
    "1 GB": 8 * 1024 ** 3,
}

for name, bits in data_sizes.items():
    print(f"{name:20s} = {bits:>15,} bits")
```

## 이 코드에서 주목할 점

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

시니어 엔지니어는 데이터 타입을 "저장 공간"이 아니라 "의미와 제약"의 관점에서 선택합니다. 가격은 정수(센트 단위)로 저장하고, 식별자는 UUID로 표현하며, 타임스탬프는 UTC 기준 ISO 8601로 통일합니다.

인코딩 관련 버그는 초기에 표준을 정하지 않아서 발생합니다. 프로젝트 시작 시 "모든 문자열은 UTF-8"이라는 단순한 규칙 하나가 수많은 버그를 예방합니다.

## 체크리스트

- [ ] 이진수와 십진수를 상호 변환할 수 있는가
- [ ] ASCII와 UTF-8의 차이를 설명할 수 있는가
- [ ] 부동소수점 오차의 원인을 이해했는가
- [ ] 문자열 길이와 바이트 길이의 차이를 구분하는가
- [ ] 금융 데이터에 float을 사용하면 안 되는 이유를 아는가

## 연습 문제

1. 십진수 0~255를 이진수, 16진수로 변환하는 함수를 작성하세요. 결과를 표로 출력합니다.

2. 다양한 문자(영문, 한글, 일본어, 이모지)의 UTF-8 바이트 수를 비교하는 프로그램을 작성하세요.

3. `0.1`을 100번 더한 결과를 `float`과 `Decimal`로 각각 계산하고 차이를 확인하세요.

## 정리 및 다음 단계

컴퓨터의 모든 데이터는 비트로 표현됩니다. 인코딩 규칙이 비트열에 의미를 부여합니다. 정수는 2의 보수로, 문자는 UTF-8로, 소수는 IEEE 754 부동소수점으로 표현합니다. 각 표현 방식의 한계를 알아야 올바른 설계가 가능합니다.

다음 글에서는 데이터를 효율적으로 처리하는 방법인 알고리즘과 그 성능을 측정하는 복잡도를 다룹니다.

<!-- toc:begin -->
- [Computer Science란 무엇인가?](./01-what-is-computer-science.md)
- [계산과 프로그램](./02-computation-and-programs.md)
- **데이터 표현 (현재 글)**
- [알고리즘과 복잡도](./04-algorithms-and-complexity.md)
- [컴퓨터 구조](./05-computer-architecture.md)
- [운영체제](./06-operating-systems.md)
- [네트워크](./07-networks.md)
- [데이터베이스](./08-databases.md)
- [소프트웨어 엔지니어링](./09-software-engineering.md)
- [AI와 데이터사이언스까지의 연결](./10-ai-and-data-science.md)
<!-- toc:end -->

## 참고 자료

- [Unicode 공식 문서](https://home.unicode.org/)
- [IEEE 754 — 부동소수점 표준](https://en.wikipedia.org/wiki/IEEE_754)
- [What Every Programmer Should Know About Floating-Point](https://floating-point-gui.de/)
- [Joel Spolsky — The Absolute Minimum About Unicode](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)

Tags: Computer Science, 이진수, 문자 인코딩, UTF-8, 부동소수점, 자료형
