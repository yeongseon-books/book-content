---
series: computer-architecture-101
episode: 2
title: 데이터 표현 — bit, byte, integer, floating point
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
  - 컴퓨터 구조
  - 데이터 표현
  - 정수
  - 부동소수점
  - 비트 연산
seo_description: 비트와 바이트, 2의 보수, IEEE 754가 실제 버그로 이어지는 지점을 설명합니다.
last_reviewed: '2026-05-12'
---

# 데이터 표현 — bit, byte, integer, floating point

`0.1 + 0.2 == 0.3`이 왜 거짓이 되는지 이해하지 못하면 부동소수점은 늘 억울한 버그처럼 보입니다. 이 글은 Computer Architecture 101 시리즈의 두 번째 글입니다. 여기서는 컴퓨터가 모든 값을 결국 비트 패턴으로 저장한다는 사실에서 출발해, 정수와 부동소수점의 표현 한계가 실제 코드에서 어떻게 드러나는지 보겠습니다.

표현 방식은 언어 문법보다 한 단계 아래에 있지만, 실제 장애는 그 아래층에서 자주 시작됩니다. 정수 오버플로, 금액 계산 오차, 비트마스크 실수는 모두 데이터가 메모리에서 어떻게 생겼는지를 놓쳐서 생깁니다.

## 이 글에서 다룰 문제

- 비트, 바이트, 워드는 각각 무엇일까요?
- 음수는 왜 2의 보수로 저장할까요?
- IEEE 754 부동소수점은 어떤 구조를 가질까요?
- 표현 범위와 정밀도 한계는 실제 코드에서 어떻게 버그가 될까요?

> 모든 값은 메모리 안에서는 결국 비트 패턴이며, 정수와 실수는 서로 다른 규칙으로 그 패턴을 해석합니다.

## 왜 중요한가

표현 방식을 이해하지 못하면 가장 흔한 버그와 정면으로 부딪히게 됩니다. 정수 오버플로 취약점, 부동소수점 비교 실패, 잘못된 비트마스크 때문에 생기는 권한 오류는 모두 타입 아래 계층을 무시한 결과입니다.

정수는 정확하지만 유한합니다. 부동소수점은 넓은 범위를 다루지만 정확하지 않습니다. 둘 다 장점이 뚜렷하고, 둘 다 한계를 모르면 위험합니다.

## 한눈에 보는 개념

비트는 0 또는 1이고, 바이트는 8비트입니다. 정수는 보통 부호 없는 형식 또는 2의 보수 형식으로 저장되고, 실수는 IEEE 754 표준에 따라 부호·지수·가수로 저장됩니다.

```text
Unsigned 8-bit:   0 to 255
Signed 8-bit:    -128 to 127  (two's complement)

float64 = | sign 1 bit | exponent 11 bits | mantissa 52 bits |
          ~ 15 to 17 decimal digits of precision
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| bit | 0 또는 1인 최소 정보 단위 |
| byte | 8비트, 메모리 주소 지정의 기본 단위 |
| word | CPU가 자연스럽게 다루는 폭, 흔히 64비트 |
| 2의 보수 | 음수를 표현하는 표준 방식 |
| IEEE 754 | 부동소수점 국제 표준 |
| 오버플로 | 표현 가능한 범위를 넘는 결과 |

## Before / After

**Before — 표현 한계를 모르는 코드:**

```python
balance = 0.1 + 0.2
if balance == 0.3:
    print("exact")
else:
    print("not exact")  # this branch wins
```

**After — 표현 한계를 의식한 코드:**

```python
from decimal import Decimal

balance = Decimal("0.1") + Decimal("0.2")
print(balance == Decimal("0.3"))   # True

import math
print(math.isclose(0.1 + 0.2, 0.3))   # True
```

같은 덧셈이라도 어떤 표현을 택하느냐에 따라 결과와 의미가 달라집니다.

## 단계별로 따라가기

### 1단계: 비트 패턴 직접 보기

```python
def bits(value, width=8):
    return format(value & ((1 << width) - 1), f"0{width}b")

print(bits(0))     # 00000000
print(bits(1))     # 00000001
print(bits(255))   # 11111111
print(bits(-1))    # 11111111  (8-bit two's complement)
print(bits(-128))  # 10000000
```

음수의 비트 패턴은 양수와 전혀 다르게 보입니다. 특히 `-1`이 모든 비트가 1이라는 점은 이후 비트 연산을 이해할 때 자주 중요해집니다.

### 2단계: 2의 보수 계산하기

```python
def to_twos_complement(value, width=8):
    if value < 0:
        return (1 << width) + value
    return value

print(to_twos_complement(5, 8))    # 5
print(to_twos_complement(-5, 8))   # 251 = 256 - 5
print(bits(to_twos_complement(-5, 8)))   # 11111011
```

음수 `-x`는 `2^n - x`로 저장됩니다. 이 규칙 덕분에 덧셈 회로를 양수와 음수에 공통으로 사용할 수 있습니다.

### 3단계: 정수 오버플로 보기

```python
import numpy as np

# Python int is arbitrary precision (no overflow),
# but numpy uses fixed widths so the wrap-around is visible.
x = np.int8(127)
print(x + 1)   # -128 (overflow)

y = np.uint8(255)
print(y + 1)   # 0   (wrap-around)
```

Python 기본 `int`는 안전해 보여도, 고정 폭 정수는 여전히 현실의 대부분 시스템에서 기본입니다. 그래서 범위 감각이 중요합니다.

### 4단계: 부동소수점 내부 보기

```python
import struct

def float_bits(x):
    packed = struct.pack(">d", x)
    return "".join(f"{byte:08b}" for byte in packed)

print(float_bits(0.0))
print(float_bits(1.0))
print(float_bits(0.1))   # 0.1 is an infinite binary fraction
print(float_bits(0.2))
```

0.1과 0.2는 이진수로 정확히 끝나지 않습니다. 그래서 두 값을 더한 결과도 0.3과 정확히 같아질 수 없습니다.

### 5단계: 정밀도 손실 측정하기

```python
import math

print(0.1 + 0.2)                       # 0.30000000000000004
print(0.1 + 0.2 == 0.3)                # False
print(math.isclose(0.1 + 0.2, 0.3))    # True

# Large + small absorption
big = 1e16
small = 1.0
print(big + small - big)   # 0.0  (the small value is absorbed)
```

부동소수점은 상대 오차를 항상 품고 있습니다. 아주 큰 값과 아주 작은 값을 더하면 작은 값이 사라질 수도 있습니다.

## 이 코드에서 먼저 봐야 할 점

- 고정 폭 정수는 오버플로가 나며 그 결과는 직관적이지 않습니다.
- 부동소수점은 모든 십진 소수를 정확히 표현하지 못합니다.
- 큰 값과 작은 값을 섞으면 작은 값이 흡수될 수 있습니다.
- 금액과 식별자처럼 정확성이 중요한 값은 float를 피해야 합니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 돈을 float로 계산 | 누적 오차 발생 | Decimal 또는 정수 단위 사용 |
| float에 `==` 사용 | 비교가 예상대로 안 됨 | `math.isclose` 사용 |
| 오버플로 무시 | 취약점과 오답 발생 | 범위 확인, 더 넓은 타입 사용 |
| 비트 폭을 암묵적으로 가정 | 플랫폼마다 동작 차이 | `int32`, `uint64`처럼 명시 |
| 부호 비트 감각 부족 | 음수 처리 오류 | signed/unsigned를 분명히 구분 |

## 실무에서는 이렇게 드러납니다

- 결제와 회계는 Decimal 또는 정수 센트 단위를 선호합니다.
- 그래픽스와 과학 계산은 float32와 float64의 비용 차이를 계산합니다.
- 네트워크 프로토콜은 헤더를 비트 단위로 해석합니다.
- 보안 검사는 정수 범위를 엄격히 확인해 오버플로를 막습니다.
- 머신러닝은 8비트 양자화로 모델 크기와 추론 비용을 줄입니다.

## 시니어 엔지니어는 이렇게 생각합니다

시니어는 새 시스템을 보면 먼저 "이 값의 타입과 폭이 무엇인가"를 묻습니다. 이 합이 int32에 들어가는지, 이 곱셈이 오버플로를 일으키는지, 이 비교가 float 위에서 일어나는지부터 확인합니다. 표현을 모르면 그 위의 비즈니스 로직도 안전하게 다룰 수 없기 때문입니다.

또한 시니어는 정확성이 중요한 값에 float를 쓰지 않는다는 강한 규칙을 갖고 있습니다. 돈, 식별자, 동등성 비교는 정수나 Decimal로 갑니다. float는 빠르고 넓지만, 그 자리를 제대로 구분해 써야 합니다.

## 체크리스트

- [ ] 1바이트의 unsigned/signed 범위를 알고 있는가
- [ ] 2의 보수에서 `-1`이 어떻게 보이는지 그릴 수 있는가
- [ ] IEEE 754의 세 부분(부호, 지수, 가수)을 말할 수 있는가
- [ ] float 비교에 `==`를 쓰지 않아야 함을 아는가
- [ ] 금액 계산에 float를 쓰면 안 되는 이유를 설명할 수 있는가

## 연습 문제

1. `to_twos_complement`를 이용해 -128부터 127까지의 signed 8비트 정수 비트 패턴을 모두 출력해 보세요. 최상위 비트가 양수와 음수를 어떻게 가르는지 확인해 보세요.

2. `0.1`을 100번 더한 결과와 `0.1 * 100`을 비교해 보세요. 두 값이 정확히 같은지 확인하고, 어떤 허용 오차에서 `math.isclose`가 참이 되는지도 실험해 보세요.

3. `numpy.int8`로 1부터 200까지 합산하는 코드를 작성해 오버플로가 어디서 시작되는지 확인해 보세요.

## 정리 및 다음 글

컴퓨터 안의 모든 값은 비트 패턴입니다. 정수는 2의 보수로, 실수는 IEEE 754로 저장되며, 각각은 표현 가능한 범위와 정밀도라는 분명한 한계를 갖습니다. 이 한계를 존중하면 흔한 버그 대부분을 미리 피할 수 있고, 무시하면 가장 민감한 경로에서 문제가 터집니다.

다음 글에서는 이 비트 위에서 실제로 일하는 주체인 CPU와 명령어를 봅니다. ISA가 무엇이고 CPU가 한 사이클에 무엇을 하는지 살펴보겠습니다.

<!-- toc:begin -->
- [컴퓨터 구조란 무엇인가?](./01-what-is-computer-architecture.md)
- **데이터 표현 — bit, byte, integer, floating point (현재 글)**
- CPU와 명령어 (예정)
- 레지스터와 ALU (예정)
- 메모리 구조 (예정)
- 캐시와 지역성 (예정)
- 파이프라인 (예정)
- I/O와 장치 (예정)
- 병렬성과 멀티코어 (예정)
- 성능을 이해하는 법 (예정)
<!-- toc:end -->

## 참고 자료

- [IEEE 754 — Wikipedia](https://en.wikipedia.org/wiki/IEEE_754)
- [What Every Computer Scientist Should Know About Floating-Point Arithmetic](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)
- [Two's complement — Wikipedia](https://en.wikipedia.org/wiki/Two%27s_complement)
- [Python `decimal` module documentation](https://docs.python.org/3/library/decimal.html)

Tags: Computer Science, 컴퓨터 구조, 데이터 표현, 정수, 부동소수점, 비트 연산
