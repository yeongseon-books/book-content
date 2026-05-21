---
series: computer-architecture-101
episode: 2
title: "Computer Architecture 101 (2/10): 데이터 표현 — bit, byte, integer, floating point"
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

# Computer Architecture 101 (2/10): 데이터 표현 — bit, byte, integer, floating point

`0.1 + 0.2 == 0.3`이 왜 거짓이 되는지 이해하지 못하면 부동소수점은 늘 억울한 버그처럼 보입니다. 이 글은 Computer Architecture 101 시리즈의 두 번째 글입니다. 여기서는 컴퓨터가 모든 값을 결국 비트 패턴으로 저장한다는 사실에서 출발해, 정수와 부동소수점의 표현 한계가 실제 코드에서 어떻게 드러나는지 보겠습니다.

표현 방식은 언어 문법보다 한 단계 아래에 있지만, 실제 장애는 그 아래층에서 자주 시작됩니다. 정수 오버플로, 금액 계산 오차, 비트마스크 실수는 모두 데이터가 메모리에서 어떻게 생겼는지를 놓쳐서 생깁니다.


![Computer Architecture 101 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-architecture-101/02/02-01-big-picture.ko.png)
*Computer Architecture 101 2장 흐름 개요*

## 먼저 던지는 질문

- 비트, 바이트, 워드는 각각 무엇일까요?
- 음수는 왜 2의 보수로 저장할까요?
- IEEE 754 부동소수점은 어떤 구조를 가질까요?

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

## 적용 전과 후

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

다음 글에서는 이 비트 위에서 실제로 일하는 주체인 CPU와 명령어를 봅니다. ISA가 무엇이고 CPU가 한 사이클에 무엇을 하는지 짚어보겠습니다.

## 심화 학습: 데이터 표현의 경계 조건과 실무 함정

데이터 표현을 "변환 규칙 암기"로 끝내면 실제 버그를 못 잡습니다. 이 절에서는 경계 조건, 정밀도 손실, 엔디언 문제를 코드와 숫자로 확인합니다.

### IEEE 754 단정밀도(float32) 비트 분해

```text
부호(1)  지수(8)       가수(23)
  0     10000010    01000000000000000000000
  
  부호: 0 → 양수
  지수: 10000010 → 130, bias 제거 → 130 - 127 = 3
  가수: 1.01 (암묵적 1 포함) → 1 + 0.25 = 1.25
  값: +1.25 × 2^3 = 10.0
```

이 분해를 Python으로 검증합니다.

```python
import struct

def float_to_bits(f: float) -> str:
    """float32의 비트 표현을 문자열로 반환."""
    packed = struct.pack('>f', f)
    bits = ''.join(f'{b:08b}' for b in packed)
    return f"{bits[0]} {bits[1:9]} {bits[9:32]}"

def bits_to_float(sign: int, exp: int, mantissa: int) -> float:
    """비트 구성 요소에서 float32 복원."""
    raw = (sign << 31) | (exp << 23) | mantissa
    packed = struct.pack('>I', raw)
    return struct.unpack('>f', packed)[0]

# 10.0 검증
print(float_to_bits(10.0))
# 출력: 0 10000010 01000000000000000000000

# 역방향 검증
print(bits_to_float(0, 0b10000010, 0b01000000000000000000000))
# 출력: 10.0
```

### 부동소수점 정밀도 함정: 0.1 + 0.2 ≠ 0.3

```python
a = 0.1
b = 0.2
c = a + b

print(f"{c:.20f}")  # 0.30000000000000004441
print(c == 0.3)      # False

# 왜 그런가: 0.1의 실제 비트 표현
print(float_to_bits(0.1))
# 0 01111011 10011001100110011001101
# 0.1은 이진수로 무한소수(0.0001100110011...)이므로
# 23비트에서 잘림 → 오차 발생
```

이 문제는 금융 계산, 좌표 비교, 물리 시뮬레이션에서 실제 버그를 만듭니다.

**실무 해법:**

| 상황 | 권장 방법 |
|------|-----------|
| 금융(원/달러) | 정수 단위 저장(센트, 원) 또는 `decimal.Decimal` |
| 좌표 비교 | `abs(a - b) < epsilon` |
| 누적 합산 | Kahan summation 알고리즘 |
| 과학 계산 | float64 사용 + 오차 전파 분석 |

### 2의 보수가 선택된 이유: 하드웨어 관점

음수 표현 방식은 세 가지가 경쟁했습니다.

| 방식 | -5 표현 (8비트) | 0의 표현 | 덧셈기 추가 회로 |
|------|----------------|----------|----------------|
| 부호-크기 | 10000101 | +0, -0 두 개 | 부호 비교 로직 필요 |
| 1의 보수 | 11111010 | +0, -0 두 개 | end-around carry |
| 2의 보수 | 11111011 | 0 하나 | 추가 없음 |

2의 보수가 승리한 결정적 이유는 **덧셈기 하나로 덧셈과 뺄셈을 모두 처리**할 수 있기 때문입니다.

```python
# 2의 보수에서 뺄셈 = 비트 반전 + 1 + 덧셈
def subtract_twos_complement(a: int, b: int, bits: int = 8) -> int:
    """a - b를 2의 보수 덧셈으로 구현."""
    mask = (1 << bits) - 1
    neg_b = (~b + 1) & mask  # -b의 2의 보수
    result = (a + neg_b) & mask
    # 부호 확장
    if result & (1 << (bits - 1)):
        result -= (1 << bits)
    return result

print(subtract_twos_complement(3, 5))   # -2
print(subtract_twos_complement(10, 3))  # 7
```

### 오버플로 감지: 하드웨어가 하는 일

```python
def add_with_overflow_check(a: int, b: int, bits: int = 8) -> tuple:
    """부호 있는 덧셈 + 오버플로 감지."""
    mask = (1 << bits) - 1
    max_val = (1 << (bits - 1)) - 1   # 127 for 8-bit
    min_val = -(1 << (bits - 1))       # -128 for 8-bit
    
    result = a + b
    overflow = result > max_val or result < min_val
    
    # 하드웨어 방식: 최상위 비트의 carry-in ≠ carry-out이면 overflow
    truncated = result & mask
    if truncated & (1 << (bits - 1)):
        truncated -= (1 << bits)
    
    return truncated, overflow

print(add_with_overflow_check(100, 50))    # (-106, True) — 오버플로!
print(add_with_overflow_check(50, 30))     # (80, False)
```

CPU의 상태 레지스터(FLAGS)에서 OF(Overflow Flag)는 바로 이 검사를 매 연산마다 수행한 결과입니다. C에서는 signed overflow가 undefined behavior이고, Rust에서는 debug 모드에서 panic을 발생시킵니다.

### 엔디언(Byte Order): 네트워크와 파일에서 만나는 함정

```python
import struct

value = 0x12345678

# 빅엔디언 (네트워크 바이트 오더)
big = struct.pack('>I', value)
print(' '.join(f'{b:02x}' for b in big))
# 출력: 12 34 56 78

# 리틀엔디언 (x86, ARM 기본)
little = struct.pack('<I', value)
print(' '.join(f'{b:02x}' for b in little))
# 출력: 78 56 34 12
```

| 상황 | 엔디언 | 예시 |
|------|--------|------|
| x86/ARM 메모리 | 리틀 | 일반 변수 저장 |
| 네트워크 프로토콜 | 빅 | TCP/IP 헤더 |
| Java `.class` 파일 | 빅 | 상수 풀 |
| ELF 바이너리 | 아키텍처 따름 | 헤더에 명시 |
| PNG 이미지 | 빅 | 청크 크기 |

실무에서 자주 하는 실수: 바이너리 파일을 파싱할 때 엔디언을 확인하지 않고 `int.from_bytes()`를 호출하면, 값이 수십억 배 다르게 읽힙니다.

### 문자 인코딩과 메모리 효율

```python
text = "안녕하세요"

# 각 인코딩별 바이트 수 비교
encodings = ['utf-8', 'utf-16', 'utf-32', 'euc-kr']
for enc in encodings:
    encoded = text.encode(enc)
    print(f"{enc:>8}: {len(encoded):>3} bytes — {' '.join(f'{b:02x}' for b in encoded[:10])}...")
```

일반적 결과:

| 인코딩 | "안녕하세요" 크기 | 특성 |
|--------|-------------------|------|
| UTF-8 | 15 bytes | 한글 3바이트, ASCII 1바이트 |
| UTF-16 | 12 bytes (+BOM 2) | 대부분 2바이트 |
| UTF-32 | 20 bytes (+BOM 4) | 모두 4바이트, 인덱싱 O(1) |
| EUC-KR | 10 bytes | 한글 2바이트, 비표준 영역 제한 |

UTF-8이 웹 표준이 된 이유: ASCII와 완전 호환되면서도 모든 유니코드를 표현할 수 있고, 영어 중심 텍스트에서 공간 효율이 최고입니다. 대신 한글 텍스트에서는 UTF-16보다 50% 더 큽니다.

### 정수 표현 범위 정리

| 타입 | 비트 수 | 최솟값 | 최댓값 |
|------|---------|--------|--------|
| int8 | 8 | -128 | 127 |
| uint8 | 8 | 0 | 255 |
| int16 | 16 | -32,768 | 32,767 |
| uint16 | 16 | 0 | 65,535 |
| int32 | 32 | -2,147,483,648 | 2,147,483,647 |
| uint32 | 32 | 0 | 4,294,967,295 |
| int64 | 64 | -9.2 × 10^18 | 9.2 × 10^18 |

실무 사고: 2038년 문제는 Unix timestamp(int32)가 2,147,483,647초(2038-01-19)에 오버플로하는 문제입니다. int64로 전환하면 2920억 년까지 안전합니다.


### 비트 마스크 연산의 실무 활용

비트 마스크는 "플래그 집합"을 하나의 정수로 압축하여 저장하는 기법으로, 운영체제 권한, 네트워크 프로토콜 필드, 하드웨어 레지스터에서 광범위하게 사용됩니다.

```python
# Unix 파일 권한 예시
READ    = 0b100  # 4
WRITE   = 0b010  # 2
EXECUTE = 0b001  # 1

def check_permission(perm: int, flag: int) -> bool:
    return bool(perm & flag)

def add_permission(perm: int, flag: int) -> int:
    return perm | flag

def remove_permission(perm: int, flag: int) -> int:
    return perm & ~flag

user_perm = READ | WRITE  # 0b110 = 6
print(f"읽기 가능: {check_permission(user_perm, READ)}")    # True
print(f"실행 가능: {check_permission(user_perm, EXECUTE)}")  # False

user_perm = add_permission(user_perm, EXECUTE)  # 0b111 = 7
print(f"전체 권한: {bin(user_perm)}")  # 0b111
```

이 패턴은 CPU의 상태 레지스터(FLAGS)에서도 동일하게 사용됩니다. Zero Flag, Carry Flag, Overflow Flag 등이 각각 1비트 위치에 매핑되어 있고, 조건 분기 명령어가 이 비트들을 마스크로 검사합니다.

### 고정소수점(Fixed-Point) 표현

부동소수점의 정밀도 문제를 피하면서도 소수를 표현해야 할 때 고정소수점을 사용합니다. 임베디드 시스템, 오디오 DSP, 금융 계산에서 흔합니다.

```python
# Q8.8 고정소수점: 상위 8비트 = 정수부, 하위 8비트 = 소수부
FRAC_BITS = 8
SCALE = 1 << FRAC_BITS  # 256

def to_fixed(f: float) -> int:
    return int(f * SCALE)

def from_fixed(q: int) -> float:
    return q / SCALE

def fixed_mul(a: int, b: int) -> int:
    """고정소수점 곱셈: 결과를 SCALE로 나눠 정규화."""
    return (a * b) >> FRAC_BITS

# 3.14 × 2.5 = 7.85
a = to_fixed(3.14)   # 804
b = to_fixed(2.5)    # 640
c = fixed_mul(a, b)
print(f"3.14 × 2.5 = {from_fixed(c):.4f}")  # 7.8438 (Q8.8 정밀도 한계)

# float32와 비교
print(f"float: {3.14 * 2.5}")  # 7.85 (더 정확)
```

고정소수점의 장점은 **연산이 정수 ALU만으로 가능**하다는 것입니다. FPU가 없는 마이크로컨트롤러에서 오디오 필터, PID 제어를 구현할 때 필수적인 기법입니다.

### 데이터 정렬(Alignment)과 성능

현대 프로세서는 자연 정렬(natural alignment)된 데이터 접근이 가장 빠릅니다.

```text
주소:  0x00  0x04  0x08  0x0C
       ┌─────┬─────┬─────┬─────┐
       │ int │ int │ int │ int │  ← 정렬됨: 한 번에 읽기
       └─────┴─────┴─────┴─────┘

주소:  0x01  0x05  0x09
       ┌──┬──┬──┬──┬──┐
       │??│ int  │??│    ← 비정렬: 두 번 읽기 + 조합 필요
       └──┴──┴──┴──┴──┘
```

```python
import struct
import sys

# 구조체 패딩 확인
class Unpadded:
    # char(1) + int(4) + char(1) = 6 바이트 "논리적" 크기
    pass

# C 구조체를 struct로 시뮬레이션
# 패딩 없이 팩
packed = struct.pack('=bib', 1, 1000, 2)
print(f"팩된 크기: {len(packed)} bytes")  # 6

# 자연 정렬 시 (컴파일러 기본)
aligned = struct.pack('=bi3xb3x', 1, 1000, 2)  # padding 포함
print(f"정렬된 크기: {len(aligned)} bytes")  # 12
```

구조체 멤버 순서를 크기 내림차순으로 정렬하면 패딩을 최소화할 수 있습니다. 이것이 "구조체 멤버 순서가 메모리 사용량을 바꾼다"는 규칙의 원리입니다.

### 특수 부동소수점 값과 NaN 전파

IEEE 754는 일반 숫자 외에 특수 값을 정의합니다.

| 패턴 | 지수 | 가수 | 의미 |
|------|------|------|------|
| 0 00000000 00...0 | 0 | 0 | +0 |
| 1 00000000 00...0 | 0 | 0 | -0 |
| 0 11111111 00...0 | 255 | 0 | +∞ |
| 1 11111111 00...0 | 255 | 0 | -∞ |
| X 11111111 ≠0 | 255 | ≠0 | NaN |
| 0 00000000 ≠0 | 0 | ≠0 | 비정규수(denormal) |

```python
import math
import numpy as np

# 특수 값 생성과 비교
print(float('inf') > 1e308)         # True
print(float('nan') == float('nan'))  # False (NaN ≠ NaN)
print(math.isnan(0.0 / 0.0 if False else float('nan')))  # True

# NaN 전파: 어떤 연산이든 NaN이 섞이면 결과도 NaN
arr = np.array([1.0, 2.0, float('nan'), 4.0])
print(f"합계: {np.sum(arr)}")        # nan
print(f"nansum: {np.nansum(arr)}")   # 7.0 (NaN 무시)
```

NaN 전파는 데이터 파이프라인에서 "조용한 오염"을 일으킵니다. 수천 개 피처 중 하나에 NaN이 섞이면 모델 전체의 예측이 NaN이 됩니다. 이것이 데이터 검증 파이프라인에서 `isnan` 체크를 초기 단계에 넣어야 하는 이유입니다.


### 실수 비교의 올바른 구현

부동소수점 비교에서 epsilon을 사용하는 것은 기본이지만, "어떤 epsilon"을 써야 하는지가 실무에서는 더 중요합니다.

```python
import math

def naive_equal(a: float, b: float, eps: float = 1e-9) -> bool:
    """절대 오차 비교 — 큰 수에서 실패."""
    return abs(a - b) < eps

def relative_equal(a: float, b: float, rel_eps: float = 1e-9) -> bool:
    """상대 오차 비교 — 0 근처에서 실패."""
    if a == b:
        return True
    return abs(a - b) / max(abs(a), abs(b)) < rel_eps

def robust_equal(a: float, b: float, rel_eps: float = 1e-9, abs_eps: float = 1e-12) -> bool:
    """혼합 비교: 0 근처는 절대, 큰 수는 상대 오차 사용."""
    if a == b:
        return True
    diff = abs(a - b)
    if diff < abs_eps:
        return True
    return diff / max(abs(a), abs(b)) < rel_eps

# 테스트
print(naive_equal(1e10, 1e10 + 1))     # False (실제로는 같다고 봐야 함)
print(relative_equal(1e10, 1e10 + 1))  # True
print(robust_equal(1e-15, 2e-15))      # True (0 근처)
```

이 패턴은 물리 시뮬레이션의 충돌 감지, 그래픽 엔진의 교차점 계산, 수치 최적화의 수렴 판정에서 직접 사용됩니다. "==" 연산자로 float를 비교하는 코드가 있다면 거의 항상 버그입니다.

## 처음 질문으로 돌아가기

- **비트, 바이트, 워드는 각각 무엇일까요?**
  - 비트는 0 또는 1 하나, 바이트는 8비트 묶음으로 문자 하나를 표현하는 최소 단위, 워드는 CPU가 한 번에 처리하는 단위(현대 64비트 프로세서에서는 8바이트)입니다. 본문에서 보았듯이 이 단위들이 메모리 주소 지정, 정렬(alignment), 엔디언 해석의 기본 경계가 됩니다.
- **음수는 왜 2의 보수로 저장할까요?**
  - 하드웨어 관점에서 덧셈기 하나로 덧셈과 뺄셈을 모두 처리할 수 있고, 0의 표현이 하나뿐이어서 비교 로직이 단순해지기 때문입니다. 심화 학습에서 확인한 것처럼, 부호-크기 방식이나 1의 보수는 추가 회로가 필요하고 +0/-0 문제를 일으킵니다.
- **IEEE 754 부동소수점은 어떤 구조를 가질까요?**
  - 부호(1비트) + 지수(8비트, bias 127) + 가수(23비트, 암묵적 1)의 구조입니다. 심화 학습에서 10.0을 비트 분해한 것처럼, 이 구조 때문에 0.1 같은 십진 소수는 정확히 표현할 수 없고, 이것이 `0.1 + 0.2 ≠ 0.3` 문제의 근본 원인입니다.

## 참고 자료

- [IEEE 754 — Wikipedia](https://en.wikipedia.org/wiki/IEEE_754)
- [What Every Computer Scientist Should Know About Floating-Point Arithmetic](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)
- [Two's complement — Wikipedia](https://en.wikipedia.org/wiki/Two%27s_complement)
- [Python `decimal` module documentation](https://docs.python.org/3/library/decimal.html)
- [예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-architecture-101/ko)

Tags: Computer Science, 컴퓨터 구조, 데이터 표현, 정수, 부동소수점, 비트 연산
