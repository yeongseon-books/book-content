---
series: computer-architecture-101
episode: 2
title: Data Representation — Bit, Byte, Integer, Floating Point
status: content-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Computer Architecture
  - Data Representation
  - Integers
  - Floating Point
  - Bit Operations
seo_description: How computers represent integers with two's complement and reals with IEEE 754, why precision and range matter, and the bugs the limits create.
last_reviewed: '2026-05-04'
---

# Data Representation — Bit, Byte, Integer, Floating Point

> Computer Architecture 101 series (2/10)

<!-- a-grade-intro:begin -->

**Core question**: Why is `0.1 + 0.2 == 0.3` false — is that a Python bug, or is the computer telling the truth?

> Computers store everything as bundles of zeros and ones. Integers use two's complement, real numbers use IEEE 754 floating point, and both come with limits on range and precision. This article walks through how those limits show up in real code and how to handle them deliberately.

<!-- a-grade-intro:end -->

This is post 2 in the Computer Architecture 101 series.

## What You Will Learn

- The definitions of bit, byte, and word
- Integer representation (unsigned and two's complement)
- The structure of IEEE 754 floating point
- How to handle overflow and precision loss

## Why It Matters

If you do not understand representation, you meet the most common bugs head-on. Integer overflow vulnerabilities, accounting systems that fail because of float comparison, permission errors from a wrong bitmask — all of them come from ignoring the layer below the type. Every variable in every language is, in the end, a bit pattern in memory.

> Integers are exact but finite. Floats are wide but imprecise. Both must be used with their limits in mind.

## Concept at a Glance

> A bit is 0 or 1; a byte is 8 bits. Integers are stored as unsigned or two's complement. Real numbers follow IEEE 754: sign, exponent, and mantissa. Single precision (float32) and double precision (float64) trade range for precision.

```text
Unsigned 8-bit:   0 to 255
Signed 8-bit:    -128 to 127  (two's complement)

float64 = | sign 1 bit | exponent 11 bits | mantissa 52 bits |
          ~ 15 to 17 decimal digits of precision
```

## Key Terms

| Term | Description |
| --- | --- |
| bit | 0 or 1, the smallest unit of information |
| byte | 8 bits, the basic unit of memory addressing |
| word | The CPU's natural width, often 64 bits |
| Two's complement | Standard way to encode negative integers |
| IEEE 754 | International standard for floating point |
| Overflow | A result outside the representable range |

## Before / After

**Before — code unaware of representation limits:**

```python
balance = 0.1 + 0.2
if balance == 0.3:
    print("exact")
else:
    print("not exact")  # this branch wins
```

**After — code aware of the limits:**

```python
from decimal import Decimal

balance = Decimal("0.1") + Decimal("0.2")
print(balance == Decimal("0.3"))   # True

import math
print(math.isclose(0.1 + 0.2, 0.3))   # True
```

The same addition produces different answers depending on the representation you choose.

## Hands-on: Step by Step

### Step 1: Inspect bit patterns directly

```python
def bits(value, width=8):
    return format(value & ((1 << width) - 1), f"0{width}b")

print(bits(0))     # 00000000
print(bits(1))     # 00000001
print(bits(255))   # 11111111
print(bits(-1))    # 11111111  (8-bit two's complement)
print(bits(-128))  # 10000000
```

Note how negative numbers look different from positive ones. `-1` is all ones.

### Step 2: Compute two's complement by hand

```python
def to_twos_complement(value, width=8):
    if value < 0:
        return (1 << width) + value
    return value

print(to_twos_complement(5, 8))    # 5
print(to_twos_complement(-5, 8))   # 251 = 256 - 5
print(bits(to_twos_complement(-5, 8)))   # 11111011
```

To represent `-x`, you store `2^n - x`. That is why -5 is 251 in 8 bits.

### Step 3: Watch integer overflow

```python
import numpy as np

# Python int is arbitrary precision (no overflow),
# but numpy uses fixed widths so the wrap-around is visible.
x = np.int8(127)
print(x + 1)   # -128 (overflow)

y = np.uint8(255)
print(y + 1)   # 0   (wrap-around)
```

C, Go, Java, and release-mode Rust use fixed-width integers like numpy. Overflow has a long history of producing security vulnerabilities.

### Step 4: Look inside a float

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

0.1 and 0.2 cannot be represented exactly in binary, so their sum cannot equal 0.3 exactly either.

### Step 5: Measure precision loss

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

Floats always carry relative error. When you add a very large value to a very small one, the small one disappears.

## What to Notice in This Code

- Fixed-width integers overflow, and the result is well-defined but not intuitive
- Floats cannot represent every decimal fraction exactly
- Mixing very large and very small floats can erase the small value
- Money and identifiers should not use floats; use integers or Decimal

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Floats for money | Cumulative cent-level errors | Decimal or integer cents |
| `==` for floats | Can always be false | Use `math.isclose` |
| Ignoring overflow | Vulnerabilities and wrong answers | Check ranges, use wider types |
| Assuming bit width | Behavior differs across platforms | Use explicit widths (int32, uint64) |
| Forgetting the sign bit | Wrong negative handling | Be explicit about signed vs unsigned |

## How This Shows Up in Production

- Payments and accounting: Decimal or integer cents
- Graphics and science: float32 (GPU) versus float64 (CPU) tradeoffs
- Network protocols: bit-precise header parsing
- Security: range checks to prevent integer overflow
- Machine learning: 8-bit quantization to shrink models and speed inference

## How a Senior Engineer Thinks

A senior engineer asks about the type and width of a variable as a reflex. "Will this sum fit in int32?" "Can this multiplication overflow?" "Is this comparison happening on floats?" Whenever they meet a new language or system, the first thing they check is integer width and float standard.

A senior also follows a hard rule: never use floats where exactness matters. Money, coordinate equality, identifiers — all integer or Decimal. Floats are fast and wide-ranging, but they have their proper place.

## Checklist

- [ ] You know the unsigned and signed range of one byte
- [ ] You can sketch how -1 looks in two's complement
- [ ] You can name the three parts of IEEE 754 (sign, exponent, mantissa)
- [ ] You never use `==` for float comparison
- [ ] You never use floats for money

## Practice Problems

1. Write a function that prints the bit pattern of every signed 8-bit integer from -128 to 127. Use `to_twos_complement`. Notice how positive and negative values differ in the most significant bit.

2. Compare adding `0.1` a hundred times against `0.1 * 100`. Confirm that the results differ and find a tolerance for which `math.isclose` returns True.

3. Predict what happens when you sum 1 through 200 using `numpy.int8`, then run the code and confirm where the overflow begins.

## Wrap-up and Next Steps

Every value in a computer is a bit pattern. Integers use two's complement, reals use IEEE 754, and each has its own range and precision limits. Respecting those limits prevents most of the common bugs; ignoring them hides the worst ones in the most sensitive parts of your system.

Next we look at what acts on these bits: the CPU and the instruction set. We will see what an ISA is and what the CPU actually does in one cycle.

<!-- toc:begin -->
- [What Is Computer Architecture?](./01-what-is-computer-architecture.md)
- **Data Representation — Bit, Byte, Integer, Floating Point (current)**
- CPU and Instructions (upcoming)
- Registers and the ALU (upcoming)
- Memory Organization (upcoming)
- Cache and Locality (upcoming)
- Pipelining (upcoming)
- I/O and Devices (upcoming)
- Parallelism and Multicore (upcoming)
- Understanding Performance (upcoming)
<!-- toc:end -->

## References

- [IEEE 754 — Wikipedia](https://en.wikipedia.org/wiki/IEEE_754)
- [What Every Computer Scientist Should Know About Floating-Point Arithmetic](https://docs.oracle.com/cd/E19957-01/806-3568/ncg_goldberg.html)
- [Two's complement — Wikipedia](https://en.wikipedia.org/wiki/Two%27s_complement)
- [Python `decimal` module documentation](https://docs.python.org/3/library/decimal.html)

Tags: Computer Science, Computer Architecture, Data Representation, Integers, Floating Point, Bit Operations
