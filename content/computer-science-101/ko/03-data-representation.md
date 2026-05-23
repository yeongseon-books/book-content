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


![Computer Science 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/03/03-01-concept-at-a-glance.ko.png)
*Computer Science 101 3장 흐름 개요*

## 먼저 던지는 질문

- 컴퓨터는 0과 1만으로 숫자, 문자, 이미지를 어떻게 저장할까요?
- ASCII와 UTF-8은 무엇이 다르고 왜 바이트 수가 달라질까요?
- 음수는 왜 2의 보수 방식으로 표현할까요?

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

## 적용 전후 비교
**Before — 데이터 표현을 모를 때:**

```python
# 왜 0.1 + 0.2는 0.3과 같지 않을까?
result = 0.1 + 0.2
print(result)          # 0.30000000000000004
print(result == 0.3)   # False — and you do not know why
```

**After — 데이터 표현을 알 때:**

```python
from decimal import Decimal

# 부동소수점은 2진 근사값이므로 정확한 계산에는 Decimal 사용
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

# 변환 원리를 코드로 검증
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
# ASCII: 영문자 1개당 1바이트
print(ord("A"))        # 65
print(chr(65))         # A
print(ord("a"))        # 97

# UTF-8: 한글 1글자는 3바이트
korean = "가"
print(ord(korean))                  # 44032
print(korean.encode("utf-8"))       # b'\xea\xb0\x80' (3 bytes)
print(len(korean))                  # 1 (character count)
print(len(korean.encode("utf-8")))  # 3 (byte count)

# 이모지: 4바이트
emoji = "🐍"
print(len(emoji))                   # 1 (character count)
print(len(emoji.encode("utf-8")))   # 4 (byte count)
```

### 3단계: 정수의 크기와 2의 보수

```python
# Python 정수는 크기 제한이 없음(arbitrary precision)
big_number = 2 ** 100
print(big_number)  # 1267650600228229401496703205376

# 하지만 C, Java 등은 고정 크기 사용
# 8-bit signed: -128부터 127
# 32-bit signed: -2,147,483,648부터 2,147,483,647

# 음수는 2의 보수로 표현
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

# 0.1의 실제 저장값 확인
print(f"{0.1:.20f}")  # 0.10000000000000000555

# IEEE 754 배정밀도 비트 패턴
bits = struct.pack("d", 0.1)
print(" ".join(f"{b:08b}" for b in bits))

# 허용 오차를 두고 비교
import math
print(math.isclose(0.1 + 0.2, 0.3))  # True

# 금액 계산에는 Decimal 또는 정수 cents 사용
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

## 비트 연산과 마스킹: 데이터 표현의 실전 도구

비트 연산은 데이터 표현을 직접 조작하는 가장 낮은 수준의 도구입니다. 네트워크 프로토콜 파싱, 권한 플래그 관리, 그래픽스 색상 조작 등 실무 곳곳에서 등장합니다.

```python
# 비트 연산 기본
a = 0b1100  # 12
b = 0b1010  # 10

print(f"a & b (AND)  = {bin(a & b):>10}  ({a & b})")   # 1000 (8)
print(f"a | b (OR)   = {bin(a | b):>10}  ({a | b})")   # 1110 (14)
print(f"a ^ b (XOR)  = {bin(a ^ b):>10}  ({a ^ b})")   # 0110 (6)
print(f"~a    (NOT)  = {bin(~a & 0xFF):>10}  ({~a & 0xFF})")  # 11110011 (243)
print(f"a << 2 (LEFT)= {bin(a << 2):>10}  ({a << 2})") # 110000 (48)
print(f"a >> 1 (RIGHT)= {bin(a >> 1):>10}  ({a >> 1})") # 110 (6)
```

### 권한 플래그 관리 예시

Unix 파일 권한이나 사용자 역할 관리에서 비트 마스크를 사용하는 패턴입니다.

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

# 권한 조합
admin = READ | WRITE | EXECUTE  # 7 (rwx)
viewer = READ                    # 4 (r--)
editor = READ | WRITE            # 6 (rw-)

print(f"admin:  {admin:03b} -> {describe_permissions(admin)}")
print(f"viewer: {viewer:03b} -> {describe_permissions(viewer)}")
print(f"editor: {editor:03b} -> {describe_permissions(editor)}")

# 권한 추가와 제거
user_perm = READ
user_perm |= WRITE       # 쓰기 권한 추가
print(f"추가 후: {user_perm:03b} -> {describe_permissions(user_perm)}")
user_perm &= ~WRITE      # 쓰기 권한 제거
print(f"제거 후: {user_perm:03b} -> {describe_permissions(user_perm)}")
```

## 엔디안과 네트워크 바이트 순서

같은 정수라도 메모리에 저장하는 바이트 순서가 다를 수 있습니다. 이 차이가 네트워크 프로토콜과 파일 포맷에서 문제를 일으킵니다.

```python
import struct

number = 0x01020304  # 16909060

# 리틀 엔디안 (x86, ARM 기본): 낮은 바이트가 낮은 주소
le_bytes = struct.pack("<I", number)
print(f"리틀 엔디안: {' '.join(f'{b:02X}' for b in le_bytes)}")  # 04 03 02 01

# 빅 엔디안 (네트워크 바이트 순서): 높은 바이트가 낮은 주소
be_bytes = struct.pack(">I", number)
print(f"빅 엔디안:   {' '.join(f'{b:02X}' for b in be_bytes)}")  # 01 02 03 04

# 네트워크 프로토콜은 항상 빅 엔디안을 사용합니다
import socket
network_order = socket.htonl(number)  # host to network long
print(f"네트워크 순서: {hex(network_order)}")
```

| 엔디안 | 사용처 | 특징 |
| --- | --- | --- |
| 리틀 엔디안 | x86, ARM(기본), Windows | 하위 바이트부터 저장 |
| 빅 엔디안 | 네트워크 프로토콜, Java class 파일 | 상위 바이트부터 저장 |
| 바이 엔디안 | ARM(설정 가능) | 모드 전환 가능 |

## 부동소수점 깊이 보기: IEEE 754 내부 구조

`0.1 + 0.2 != 0.3`이 왜 발생하는지를 IEEE 754 내부 구조 수준에서 봅니다.

```python
import struct

def float_to_parts(f: float) -> dict:
    """64비트 부동소수점을 부호, 지수, 가수로 분해합니다."""
    raw = struct.pack("d", f)
    bits = int.from_bytes(raw, byteorder="little")

    sign = (bits >> 63) & 1
    exponent_raw = (bits >> 52) & 0x7FF
    mantissa = bits & 0x000FFFFFFFFFFFFF

    exponent = exponent_raw - 1023  # bias 제거
    return {
        "값": f,
        "부호": sign,
        "지수(raw)": exponent_raw,
        "지수(실제)": exponent,
        "가수(hex)": f"{mantissa:013X}",
        "비트 패턴": f"{bits:064b}",
    }

for val in [0.1, 0.2, 0.3, 0.1 + 0.2]:
    parts = float_to_parts(val)
    print(f"{parts['값']:.20f}")
    print(f"  부호={parts['부호']} 지수={parts['지수(실제)']} 가수=0x{parts['가수(hex)']}")
    print()
```

이 코드를 실행하면 `0.1 + 0.2`의 가수 비트가 `0.3`과 미세하게 다르다는 것을 직접 확인할 수 있습니다. 이진법으로 `0.1`은 무한 소수(`0.0001100110011...`)이므로, 유한한 52비트 가수로 잘리면서 오차가 생깁니다.

### 실무에서의 부동소수점 처리 전략

| 상황 | 권장 방식 | 이유 |
| --- | --- | --- |
| 금융 계산 | `Decimal` 또는 정수(센트) | 정확한 십진 연산 필요 |
| 과학 계산 | `float64` + 오차 허용 | 범위와 속도 우선 |
| 비교 연산 | `math.isclose(rel_tol=1e-9)` | 직접 `==` 비교 금지 |
| 누적 합산 | Kahan 합산 알고리즘 | 오차 누적 방지 |
| 직렬화 | 문자열 또는 정수 변환 | 플랫폼 간 일관성 보장 |

```python
# Kahan 합산: 부동소수점 누적 오차를 줄이는 알고리즘
def kahan_sum(values: list[float]) -> float:
    total = 0.0
    compensation = 0.0
    for val in values:
        y = val - compensation
        t = total + y
        compensation = (t - total) - y
        total = t
    return total

# 0.1을 10000번 더한 결과 비교
naive = sum([0.1] * 10000)
kahan = kahan_sum([0.1] * 10000)
print(f"단순 합산: {naive:.15f}")
print(f"Kahan 합산: {kahan:.15f}")
print(f"기대값:     {1000.0:.15f}")
```

## 문자 인코딩 실전: 깨진 텍스트 복구하기

실무에서 가장 흔한 인코딩 문제는 "깨진 글자"입니다. 원인과 해결법을 코드로 확인합니다.

```python
# 흔한 인코딩 실수: UTF-8 바이트를 latin-1로 잘못 해석
original = "안녕하세요"
utf8_bytes = original.encode("utf-8")

# 잘못된 디코딩 (mojibake 발생)
broken = utf8_bytes.decode("latin-1")
print(f"깨진 텍스트: {broken}")

# 복구: 잘못된 인코딩을 역으로 되돌림
recovered = broken.encode("latin-1").decode("utf-8")
print(f"복구된 텍스트: {recovered}")

# 인코딩별 바이트 크기 비교표
test_strings = [
    ("A", "영문 1자"),
    ("가", "한글 1자"),
    ("你", "중국어 1자"),
    ("🐍", "이모지 1자"),
]

print(f"\n{'문자':<6} {'설명':<10} {'UTF-8':>6} {'UTF-16':>7} {'UTF-32':>7}")
print("-" * 40)
for char, desc in test_strings:
    u8 = len(char.encode("utf-8"))
    u16 = len(char.encode("utf-16-le"))
    u32 = len(char.encode("utf-32-le"))
    print(f"{char:<6} {desc:<10} {u8:>4}B  {u16:>5}B  {u32:>5}B")
```

### 데이터 정렬과 패딩

CPU는 메모리에서 데이터를 읽을 때 자연 경계(natural boundary)에 맞춰 읽습니다. 예를 들어 4바이트 정수는 4의 배수 주소에서 시작해야 한 번의 메모리 접근으로 읽을 수 있습니다. 경계에 맞지 않으면 두 번 읽어야 하므로 성능이 떨어집니다.

```text
struct Example {
    char  a;    // 1바이트, 오프셋 0
    // 패딩 3바이트 (오프셋 1-3)
    int   b;    // 4바이트, 오프셋 4
    char  c;    // 1바이트, 오프셋 8
    // 패딩 7바이트 (오프셋 9-15)
    double d;   // 8바이트, 오프셋 16
};
// sizeof(Example) = 24바이트 (실제 데이터 14바이트 + 패딩 10바이트)
```

패딩을 줄이려면 필드를 크기 내림차순으로 배치합니다.

```text
struct Optimized {
    double d;   // 8바이트, 오프셋 0
    int    b;   // 4바이트, 오프셋 8
    char   a;   // 1바이트, 오프셋 12
    char   c;   // 1바이트, 오프셋 13
    // 패딩 2바이트 (오프셋 14-15)
};
// sizeof(Optimized) = 16바이트 (실제 데이터 14바이트 + 패딩 2바이트)
```

네트워크 프로토콜에서는 `__attribute__((packed))`를 사용해 패딩을 제거하기도 합니다. 단, 비정렬 접근은 일부 아키텍처(ARM 구형, SPARC)에서 하드웨어 예외를 발생시키므로 주의가 필요합니다.

### 체크섬과 오류 검출

데이터가 저장되거나 전송될 때 비트 오류가 발생할 수 있습니다. 이를 감지하기 위해 여러 기법을 사용합니다.

| 기법 | 원리 | 검출 능력 | 사용처 |
|------|------|-----------|--------|
| 패리티 비트 | 1의 개수를 짝수/홀수로 맞춤 | 1비트 오류 검출 | 메모리(ECC) |
| CRC-32 | 다항식 나눗셈의 나머지 | 연속 32비트 이하 오류 | Ethernet, ZIP |
| MD5/SHA | 해시 함수 | 의도적 변조 검출 | 파일 무결성 |
| 해밍 코드 | 여분 비트로 위치 특정 | 1비트 수정, 2비트 검출 | ECC 메모리 |

패리티 비트 계산 예시:

```python
def even_parity(byte: int) -> int:
    """8비트 데이터에 짝수 패리티 비트를 추가합니다."""
    ones = bin(byte).count("1")
    parity = ones % 2  # 1의 개수가 홀수면 1, 짝수면 0
    return (byte << 1) | parity

# 예: 0b1010_0110 (1이 4개, 짝수) → 패리티 0 → 0b1_0100_1100
# 예: 0b1010_0111 (1이 5개, 홀수) → 패리티 1 → 0b1_0100_1111
print(f"{even_parity(0b10100110):09b}")  # 101001100
print(f"{even_parity(0b10100111):09b}")  # 101001111
```

CRC는 더 강력합니다. 데이터를 이진 다항식으로 취급하고, 생성 다항식으로 나눈 나머지를 붙입니다. 수신 측에서 같은 나눗셈을 하면 나머지가 0이어야 정상입니다. 실무에서는 하드웨어 회로나 테이블 기반 알고리즘으로 고속 처리합니다.

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


## 학습 설계 지도: 이 글을 커리큘럼에 연결하기

컴퓨터 과학 입문을 빠르게 끝내는 접근보다, 서로 연결된 개념을 축적하는 접근이 이후 학습 효율을 높입니다. 이 글의 핵심 개념은 단독 지식이 아니라 운영체제, 네트워크, 데이터베이스, 소프트웨어 공학으로 이어지는 선행 지식입니다. 따라서 한 주 단위 학습에서 이 글을 기준점으로 삼고, 다음과 같은 연결 훈련을 함께 수행하는 것이 좋습니다.

| 학습 축 | 이 글에서 확인할 포인트 | 다음 과목 연결 |
| --- | --- | --- |
| 계산 모델 | 입력, 상태, 출력의 관계를 명확히 정의 | 알고리즘 설계, 분산 시스템 모델링 |
| 추상화 | 세부 구현을 숨기고 인터페이스를 구분 | API 설계, 모듈 경계 설계 |
| 자원 제약 | 시간·메모리·I/O 비용을 동시에 고려 | 성능 튜닝, 인프라 비용 최적화 |
| 검증 가능성 | 주장 대신 측정과 반례로 판단 | 테스트 전략, 실험 설계 |

연결 학습을 할 때는 "개념 정의 1회 + 사례 적용 2회 + 반례 점검 1회" 구조를 반복합니다. 예를 들어 시간 복잡도를 배웠다면, 단순히 O 표기법을 외우지 않고 입력 크기 변화에 따른 실행 시간 그래프를 직접 기록합니다. 그래프가 기대와 다를 때 원인을 추정하고, 캐시 지역성이나 상수항의 영향을 설명해 보는 과정이 필요합니다. 이 연습이 쌓이면 글에서 다룬 개념이 시험 대비 지식이 아니라 실무 의사결정 기준으로 바뀝니다.

또한 과목 간 언어를 통일해 두는 것이 중요합니다. 같은 현상을 운영체제에서는 스케줄링, 네트워크에서는 큐잉, 데이터베이스에서는 트랜잭션 대기라고 부를 수 있습니다. 이름은 달라도 "경합 상태에서 자원을 배분한다"는 본질은 동일합니다. 학습 노트에 용어 사전을 만들어 개념 동치 관계를 표시해 두면, 새로운 분야를 배울 때 기존 이해를 재사용하기 쉬워집니다.

마지막으로 주간 복습은 요약보다 질문 중심으로 구성합니다. "왜 이 추상화가 필요한가", "어떤 조건에서 깨지는가", "대안의 비용은 무엇인가"를 각각 한 문장으로 답하면 학습 깊이가 빠르게 올라갑니다. 이렇게 축적한 질문-답변 세트는 면접, 설계 리뷰, 코드 리뷰에서 그대로 활용 가능한 사고 프레임이 됩니다.

데이터 표현 단원에서는 비트/바이트 수준 표현이 직렬화 포맷, 네트워크 프로토콜, 저장 엔진의 설계 제약과 직접 연결된다는 점을 반복 확인합니다.

### 학습 팁: 표현-전송-저장을 한 흐름으로 보기

데이터 표현은 메모리 내부 문제로 끝나지 않습니다. 같은 값이 API 응답(JSON), 메시지 큐(바이너리), DB 컬럼(정수/문자열)로 이동할 때 어떤 손실과 변환 비용이 생기는지 추적해야 합니다. 실습으로는 동일 레코드를 세 포맷으로 직렬화하고 크기, 파싱 시간, 가독성을 비교해 보는 방법이 효과적입니다.

## 처음 질문으로 돌아가기

- **컴퓨터는 0과 1만으로 숫자, 문자, 이미지를 어떻게 저장할까요?**
  - 모든 데이터는 비트(0/1)로 표현되며, 인코딩 규칙이 비트열에 의미를 부여합니다. 같은 바이트열 `0x41`도 ASCII로 해석하면 문자 'A', 정수로 해석하면 65, 색상 채널로 해석하면 밝기 값이 됩니다. 약속(규칙)이 데이터의 의미를 결정합니다.
- **ASCII와 UTF-8은 무엇이 다르고 왜 바이트 수가 달라질까요?**
  - ASCII는 영문 128자를 1바이트로 표현하는 고정 길이 인코딩입니다. UTF-8은 전 세계 문자를 1~4바이트 가변 길이로 표현합니다. 영문은 1바이트, 한글은 3바이트, 이모지는 4바이트를 사용합니다. 가변 길이 덕분에 영문 중심 텍스트는 공간 효율이 높지만, `len(문자열) != len(바이트열)`이라는 함정이 생깁니다.
- **음수는 왜 2의 보수 방식으로 표현할까요?**
  - 2의 보수는 덧셈 회로 하나로 양수와 음수 연산을 모두 처리할 수 있게 합니다. 별도의 뺄셈 하드웨어가 필요 없고, +0/-0 이중 표현 문제도 없습니다. 예제에서 확인한 것처럼 -5는 `11111011`로, 5(`00000101`)와 더하면 정확히 0(`00000000`, 오버플로우 비트 무시)이 됩니다.

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
- [이 시리즈의 예제 코드 저장소](https://github.com/yeongseon-books/book-examples/tree/main/computer-science-101/ko)

Tags: Computer Science, 이진수, 문자 인코딩, UTF-8, 부동소수점, 자료형
