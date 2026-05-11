---
series: computer-architecture-101
episode: 2
title: 데이터 표현 — bit, byte, integer, floating point
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
  - 컴퓨터 구조
  - 데이터 표현
  - 정수
  - 부동소수점
  - 비트 연산
seo_description: 비트와 바이트, 정수의 2의 보수 표현, IEEE 754 부동소수점, 그리고 표현 한계가 만드는 버그를 정리합니다.
last_reviewed: '2026-05-04'
---

# 데이터 표현 — bit, byte, integer, floating point

> Computer Architecture 101 시리즈 (2/10)


## 이 글에서 다룰 문제

데이터 표현을 이해하지 못하면 가장 흔한 버그를 만나게 됩니다. 정수 오버플로로 인한 보안 취약점, 부동소수점 비교 실패로 깨지는 회계 시스템, 잘못된 비트 마스크로 인한 권한 오류 — 모두 표현 계층을 의식하지 못해 생기는 문제입니다. 모든 언어의 모든 변수는 결국 메모리 안의 비트 패턴으로 환원됩니다.

> 정수는 정확하지만 유한합니다. 부동소수점은 광범위하지만 부정확합니다. 둘 다 그 한계를 알고 써야 합니다.

## 전체 흐름
> 비트는 0 또는 1, 바이트는 8비트입니다. 정수는 보통 부호 없는(unsigned) 또는 2의 보수(two's complement)로 저장됩니다. 실수는 IEEE 754 표준에 따라 부호·지수·가수의 세 부분으로 나누어 저장됩니다. 단정도(float32)와 배정도(float64)는 정밀도가 다릅니다.

```text
부호 없는 8비트:   0 ~ 255
부호 있는 8비트:  -128 ~ 127  (2의 보수)

float64 = | 부호 1bit | 지수 11bit | 가수 52bit |
          → 약 15~17자리의 십진 정밀도
```

## Before / After

**Before — 표현 한계를 모르는 코드:**

```python
balance = 0.1 + 0.2
if balance == 0.3:
    print("정확")
else:
    print("오차 있음")  # 실제로 출력됨
```

**After — 표현 한계를 의식한 코드:**

```python
from decimal import Decimal

balance = Decimal("0.1") + Decimal("0.2")
print(balance == Decimal("0.3"))   # True

# 또는 부동소수점 비교 시 허용 오차 사용
import math
print(math.isclose(0.1 + 0.2, 0.3))   # True
```

같은 덧셈이라도 어떤 표현을 쓰느냐에 따라 결과가 달라집니다.

## 단계별로 따라하기

### 1단계: 비트 패턴 직접 보기

```python
def bits(value, width=8):
    return format(value & ((1 << width) - 1), f"0{width}b")

print(bits(0))     # 00000000
print(bits(1))     # 00000001
print(bits(255))   # 11111111
print(bits(-1))    # 11111111  (8비트 2의 보수)
print(bits(-128))  # 10000000
```

음수의 비트 패턴이 양수와 어떻게 다른지 확인합니다. `-1`은 모든 비트가 1입니다.

### 2단계: 2의 보수 직접 계산

```python
def to_twos_complement(value, width=8):
    if value < 0:
        return (1 << width) + value
    return value

print(to_twos_complement(5, 8))    # 5
print(to_twos_complement(-5, 8))   # 251 = 256 - 5
print(bits(to_twos_complement(-5, 8)))   # 11111011
```

음수 `-x`를 표현하려면 `2^n - x`를 저장합니다. 그래서 -5는 8비트에서 251이 됩니다.

### 3단계: 정수 오버플로 관찰

```python
import numpy as np

# 파이썬 int는 임의 정밀도라 오버플로가 없지만,
# numpy는 고정 폭이라 명확히 보입니다
x = np.int8(127)
print(x + 1)   # -128 (오버플로!)

y = np.uint8(255)
print(y + 1)   # 0   (랩어라운드)
```

C, Go, Java, Rust(release) 등 대부분의 언어는 numpy처럼 고정 폭 정수를 씁니다. 오버플로는 보안 취약점의 단골 원인입니다.

### 4단계: 부동소수점의 내부 구조

```python
import struct

def float_bits(x):
    packed = struct.pack(">d", x)
    return "".join(f"{byte:08b}" for byte in packed)

print(float_bits(0.0))
print(float_bits(1.0))
print(float_bits(0.1))   # 0.1은 이진법으로 무한소수
print(float_bits(0.2))
```

0.1과 0.2는 이진법으로 정확히 표현되지 않기 때문에, 더한 결과도 0.3과 정확히 같지 않습니다.

### 5단계: 정밀도 손실 측정

```python
import math

print(0.1 + 0.2)                       # 0.30000000000000004
print(0.1 + 0.2 == 0.3)                # False
print(math.isclose(0.1 + 0.2, 0.3))    # True

# 큰 수 + 작은 수의 흡수
big = 1e16
small = 1.0
print(big + small - big)   # 0.0  (작은 값이 흡수됨)
```

부동소수점은 항상 상대 오차를 가지며, 큰 값과 작은 값을 함께 다루면 작은 값이 사라질 수 있습니다.

## 이 코드에서 주목할 점

- 정수는 고정 폭이면 오버플로가 발생하고, 그 결과는 잘 정의되어 있지만 직관과 다릅니다
- 부동소수점은 십진 소수를 정확히 표현하지 못합니다
- 큰 값과 작은 값을 함께 더하면 작은 값이 사라질 수 있습니다
- 금액·식별자는 부동소수점 대신 정수나 Decimal을 씁니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 부동소수점으로 금액 계산 | 1원 단위 오차 누적 | Decimal 또는 정수(원 단위)로 |
| `==`로 부동소수점 비교 | 항상 거짓이 될 수 있음 | `math.isclose` 사용 |
| 정수 오버플로 무시 | 보안 취약점·잘못된 결과 | 범위 확인, 큰 정수 타입 사용 |
| 비트 폭 가정하지 않음 | 플랫폼 간 결과 다름 | 명시적 폭(int32, uint64 등) |
| 부호 비트 잊음 | 음수 처리 오류 | unsigned vs signed 명시 |

## 실무에서는 이렇게 쓰입니다

- 결제·회계: Decimal 또는 정수 단위로 금액을 다룸
- 그래픽·과학 계산: float32(GPU) vs float64(CPU)의 트레이드오프
- 네트워크 프로토콜: 비트 단위로 정의된 헤더 파싱
- 보안 검사: 정수 오버플로를 막기 위한 입력 범위 검증
- 머신러닝: 양자화(8비트 정수)로 모델 크기와 추론 속도 개선

## 체크리스트

- [ ] 1바이트로 표현 가능한 부호 없는/있는 정수 범위를 안다
- [ ] 2의 보수에서 -1이 어떻게 표현되는지 그릴 수 있는가
- [ ] IEEE 754의 세 부분(부호·지수·가수)을 말할 수 있는가
- [ ] 부동소수점 비교에 `==`을 쓰지 않는다
- [ ] 금액 계산에 부동소수점을 쓰지 않는다

## 정리 및 다음 단계

컴퓨터의 모든 값은 비트 패턴으로 환원됩니다. 정수는 2의 보수로, 실수는 IEEE 754로 저장되며, 각각 표현 가능한 범위와 정밀도라는 한계를 갖습니다. 그 한계를 의식하면 흔한 버그의 절반은 미리 막을 수 있고, 의식하지 못하면 시스템의 가장 위험한 자리에 숨어 있다가 문제를 일으킵니다.

다음 글에서는 이 비트들 위에서 동작하는 CPU와 명령어를 살펴봅니다. 명령어 집합(ISA)이 무엇이며, CPU가 한 사이클에 무엇을 하는지를 다룹니다.

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
