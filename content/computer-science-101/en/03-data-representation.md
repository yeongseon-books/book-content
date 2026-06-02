---
series: computer-science-101
episode: 3
title: "Computer Science 101 (3/10): Data Representation"
status: publish-ready
targets:
  tistory: false
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: en
tags:
  - Computer Science
  - Binary
  - Character Encoding
  - UTF-8
  - Floating Point
  - Data Types
seo_description: How computers represent data — binary, character encoding (ASCII, UTF-8), and the way integers and floating-point numbers are stored.
last_reviewed: '2026-05-15'
---

# Computer Science 101 (3/10): Data Representation

People often say that computers only understand 0 and 1, but that sentence does not become useful until you can connect it to real bugs. Garbled text, wrong money totals, and surprising overflows all start to make sense once you understand how raw bits get meaning.

This is the 3rd post in the Computer Science 101 series.

In this article, we'll walk through bits and bytes, character encoding, signed integers, and floating-point limits so you can reason from representation to behavior.


![Computer Science 101 chapter 3 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/computer-science-101/03/03-01-concept-at-a-glance.en.png)
*Computer Science 101 chapter 3 flow overview*

## Questions to Keep in Mind

- What boundary should you inspect first when applying Data Representation?
- Which signal should the example or diagram make visible for Data Representation?
- What failure should be prevented first when Data Representation reaches a real system?

## Questions This Article Answers

- How does a computer store numbers, text, and images using only 0 and 1?
- Why do ASCII and UTF-8 use different byte counts?
- Why are negative integers usually represented with two's complement?
- Why does `0.1 + 0.2 != 0.3` happen in real programs?
- What kinds of bugs appear when you confuse character length with byte length?

## What You Will Learn

- How to convert between binary and decimal
- ASCII and UTF-8 character encodings
- How signed integers are represented (two's complement)
- How floating point works and why precision is limited

## Why It Matters

Garbled characters, floating-point error, and integer overflow are all problems you cannot fix without understanding data representation. You need to know why `0.1 + 0.2 != 0.3` before you can design a financial system correctly.

> Data representation = the physics of the digital world.

Bit-level understanding is the foundation of debugging and performance work.

> Every piece of data is a sequence of bits (0/1). Encoding rules give meaning to the bits.

## Key Terms

| Term | Description |
| --- | --- |
| Bit | The smallest unit, storing 0 or 1 |
| Byte | A group of 8 bits |
| ASCII | A 7-bit standard for encoding English characters |
| UTF-8 | A variable-length encoding for the world's characters using 1-4 bytes |
| Floating point | An approximate representation of decimals defined by IEEE 754 |

## Before / After

**Before — without representation knowledge:**

```python
# Why isn't 0.1 + 0.2 equal to 0.3?
result = 0.1 + 0.2
print(result)          # 0.30000000000000004
print(result == 0.3)   # False — and you do not know why
```

**After — with representation knowledge:**

```python
from decimal import Decimal

# Floating point is a binary approximation; use Decimal for exact arithmetic.
result = Decimal("0.1") + Decimal("0.2")
print(result)              # 0.3
print(result == Decimal("0.3"))  # True
```

**Expected output:** the `float` version should show `0.30000000000000004`, while the `Decimal` version should print an exact `0.3`.

## Hands-On: Step by Step

### Step 1: Binary and decimal conversion

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

### Step 2: ASCII and UTF-8

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

### Step 3: Integer size and two's complement

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

### Step 4: The limits of floating point

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

### Step 5: Build intuition for data sizes

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

## Notable Points in This Code

- The same bit sequence can mean a number, a character, or a color depending on interpretation.
- UTF-8 uses a different number of bytes per character, so `len(string) != len(bytes)`.
- Floating point is approximate — never compare directly with `==`.
- Python integers never overflow, but other languages do.

## Five Common Mistakes

| Mistake | Problem | Fix |
| --- | --- | --- |
| Confusing string length with byte length | Wrong slicing of Korean text or emoji | `len()` gives characters; `len(s.encode())` gives bytes |
| Comparing floats with `==` | `0.1 + 0.2 != 0.3` | Use `math.isclose()` |
| Using floats for money | Cent-level errors accumulate | Use `Decimal` or integer cents |
| Reading files without specifying encoding | Garbled characters | Pass `encoding="utf-8"` explicitly |
| Assuming Python-style unbounded integers in other languages | Overflow bugs | Check the integer range per language |

## How This Is Used in Practice

- Setting `charset=utf-8` on the `Content-Type` header in a web API.
- Handling money with `Decimal` or integer cents in financial systems.
- Choosing INT vs BIGINT when picking database column types.
- Detecting BOM (Byte Order Mark) and encoding when processing files.
- Handling byte order (endianness) in network protocols.

## How a Senior Engineer Thinks

Senior engineers pick data types by *meaning and constraints*, not by storage size. Prices live as integer cents, identifiers as UUIDs, timestamps as ISO 8601 in UTC.

Encoding bugs come from not setting a standard early. A simple project-wide rule like "every string is UTF-8" prevents an enormous class of bugs.

## Bit Operations and Masking: Practical Tools for Data Representation

Bit-level operations are not just theoretical — they appear in permission systems, network protocols, and graphics programming.

```python
# Basic bit operations
a = 0b1100  # 12
b = 0b1010  # 10

print(f"a & b (AND)  = {bin(a & b):>10}  ({a & b})")   # 1000 (8)
print(f"a | b (OR)   = {bin(a | b):>10}  ({a | b})")   # 1110 (14)
print(f"a ^ b (XOR)  = {bin(a ^ b):>10}  ({a ^ b})")   # 0110 (6)
print(f"~a    (NOT)  = {bin(~a & 0xFF):>10}  ({~a & 0xFF})")  # 11110011 (243)
print(f"a << 2 (LEFT)= {bin(a << 2):>10}  ({a << 2})") # 110000 (48)
print(f"a >> 1 (RIGHT)= {bin(a >> 1):>10}  ({a >> 1})") # 110 (6)
```

### Permission Flags Example

Unix file permissions and role management use bitmask patterns.

```python
# Managing permissions with bit flags
READ = 0b100    # 4
WRITE = 0b010   # 2
EXECUTE = 0b001 # 1

def describe_permissions(perm: int) -> str:
    parts = []
    if perm & READ:
        parts.append("read")
    if perm & WRITE:
        parts.append("write")
    if perm & EXECUTE:
        parts.append("execute")
    return ", ".join(parts) if parts else "none"

# Combining permissions
admin = READ | WRITE | EXECUTE  # 7 (rwx)
viewer = READ                    # 4 (r--)
editor = READ | WRITE            # 6 (rw-)

print(f"admin:  {admin:03b} -> {describe_permissions(admin)}")
print(f"viewer: {viewer:03b} -> {describe_permissions(viewer)}")
print(f"editor: {editor:03b} -> {describe_permissions(editor)}")

# Adding and removing permissions
user_perm = READ
user_perm |= WRITE       # Add write permission
print(f"After add: {user_perm:03b} -> {describe_permissions(user_perm)}")
user_perm &= ~WRITE      # Remove write permission
print(f"After remove: {user_perm:03b} -> {describe_permissions(user_perm)}")
```

## Endianness and Network Byte Order

The same integer can be stored in different byte orders in memory. This difference causes issues in network protocols and file formats.

```python
import struct

number = 0x01020304  # 16909060

# Little-endian (x86, ARM default): low byte at low address
le_bytes = struct.pack("<I", number)
print(f"Little-endian: {' '.join(f'{b:02X}' for b in le_bytes)}")  # 04 03 02 01

# Big-endian (network byte order): high byte at low address
be_bytes = struct.pack(">I", number)
print(f"Big-endian:    {' '.join(f'{b:02X}' for b in be_bytes)}")  # 01 02 03 04

# Network protocols always use big-endian
import socket
network_order = socket.htonl(number)  # host to network long
print(f"Network order: {hex(network_order)}")
```

| Endianness | Used By | Characteristic |
| --- | --- | --- |
| Little-endian | x86, ARM (default), Windows | Stores low byte first |
| Big-endian | Network protocols, Java class files | Stores high byte first |
| Bi-endian | ARM (configurable) | Mode switchable |

## Floating Point Deep Dive: IEEE 754 Internal Structure

Why does `0.1 + 0.2 != 0.3`? Let us examine IEEE 754 internals.

```python
import struct

def float_to_parts(f: float) -> dict:
    """Decompose a 64-bit float into sign, exponent, and mantissa."""
    raw = struct.pack("d", f)
    bits = int.from_bytes(raw, byteorder="little")

    sign = (bits >> 63) & 1
    exponent_raw = (bits >> 52) & 0x7FF
    mantissa = bits & 0x000FFFFFFFFFFFFF

    exponent = exponent_raw - 1023  # remove bias
    return {
        "value": f,
        "sign": sign,
        "exponent_raw": exponent_raw,
        "exponent_actual": exponent,
        "mantissa_hex": f"{mantissa:013X}",
        "bit_pattern": f"{bits:064b}",
    }

for val in [0.1, 0.2, 0.3, 0.1 + 0.2]:
    parts = float_to_parts(val)
    print(f"{parts['value']:.20f}")
    print(f"  sign={parts['sign']} exp={parts['exponent_actual']} mantissa=0x{parts['mantissa_hex']}")
    print()
```

Running this reveals that the mantissa bits of `0.1 + 0.2` differ slightly from `0.3`. In binary, `0.1` is a repeating fraction (`0.0001100110011...`), so truncating to 52 mantissa bits introduces error.

### Floating-Point Strategies in Practice

| Situation | Recommended Approach | Reason |
| --- | --- | --- |
| Financial calculations | `Decimal` or integers (cents) | Exact decimal arithmetic required |
| Scientific computing | `float64` + tolerance | Range and speed take priority |
| Comparisons | `math.isclose(rel_tol=1e-9)` | Never compare with `==` directly |
| Cumulative sums | Kahan summation algorithm | Prevents error accumulation |
| Serialization | String or integer conversion | Cross-platform consistency |

```python
# Kahan summation: reduces floating-point accumulation error
def kahan_sum(values: list[float]) -> float:
    total = 0.0
    compensation = 0.0
    for val in values:
        y = val - compensation
        t = total + y
        compensation = (t - total) - y
        total = t
    return total

# Compare summing 0.1 ten thousand times
naive = sum([0.1] * 10000)
kahan = kahan_sum([0.1] * 10000)
print(f"Naive sum: {naive:.15f}")
print(f"Kahan sum: {kahan:.15f}")
print(f"Expected:  {1000.0:.15f}")
```

## Character Encoding in Practice: Recovering Broken Text

The most common encoding problem in production is "garbled text." Here are the causes and fixes in code.

```python
# Common encoding mistake: UTF-8 bytes decoded as latin-1
original = "\uc548\ub155\ud558\uc138\uc694"  # Korean greeting
utf8_bytes = original.encode("utf-8")

# Wrong decoding (produces mojibake)
broken = utf8_bytes.decode("latin-1")
print(f"Broken text: {broken}")

# Recovery: reverse the wrong encoding
recovered = broken.encode("latin-1").decode("utf-8")
print(f"Recovered text: {recovered}")

# Byte size comparison table by encoding
test_strings = [
    ("A", "English 1 char"),
    ("\uac00", "Korean 1 char"),
    ("\u4f60", "Chinese 1 char"),
    ("\U0001f40d", "Emoji 1 char"),
]

print(f"\n{'Char':<6} {'Description':<14} {'UTF-8':>6} {'UTF-16':>7} {'UTF-32':>7}")
print("-" * 45)
for char, desc in test_strings:
    u8 = len(char.encode("utf-8"))
    u16 = len(char.encode("utf-16-le"))
    u32 = len(char.encode("utf-32-le"))
    print(f"{char:<6} {desc:<14} {u8:>4}B  {u16:>5}B  {u32:>5}B")
```

### Data Alignment and Padding

CPUs read data from memory at natural boundaries. A 4-byte integer should start at an address divisible by 4 for a single memory access. Misaligned access requires two reads, degrading performance.

```text
struct Example {
    char  a;    // 1 byte, offset 0
    // 3 bytes padding (offset 1-3)
    int   b;    // 4 bytes, offset 4
    char  c;    // 1 byte, offset 8
    // 7 bytes padding (offset 9-15)
    double d;   // 8 bytes, offset 16
};
// sizeof(Example) = 24 bytes (14 bytes data + 10 bytes padding)
```

To reduce padding, arrange fields in descending size order.

```text
struct Optimized {
    double d;   // 8 bytes, offset 0
    int    b;   // 4 bytes, offset 8
    char   a;   // 1 byte, offset 12
    char   c;   // 1 byte, offset 13
    // 2 bytes padding (offset 14-15)
};
// sizeof(Optimized) = 16 bytes (14 bytes data + 2 bytes padding)
```

Network protocols sometimes use `__attribute__((packed))` to eliminate padding. However, unaligned access causes hardware exceptions on some architectures (older ARM, SPARC), so caution is required.

### Checksums and Error Detection

Bit errors can occur during data storage or transmission. Several techniques detect them.

| Technique | Principle | Detection Capability | Use Case |
| --- | --- | --- | --- |
| Parity bit | Match 1-count to even/odd | 1-bit error detection | Memory (ECC) |
| CRC-32 | Remainder of polynomial division | Consecutive errors ≤32 bits | Ethernet, ZIP |
| MD5/SHA | Hash function | Intentional tampering | File integrity |
| Hamming code | Extra bits locate error position | 1-bit correction, 2-bit detection | ECC memory |

## Learning Roadmap: Connecting This Article to the Curriculum

Rather than rushing through an intro to computer science, building interconnected concepts gradually produces better long-term learning efficiency. The core concepts in this article are not standalone knowledge — they are prerequisites that lead into operating systems, networks, databases, and software engineering.

| Learning Axis | Checkpoint in This Article | Connection to Later Subjects |
| --- | --- | --- |
| Computation Model | Clearly define input-state-output relationships | Algorithm design, distributed system modeling |
| Abstraction | Distinguish interfaces from hidden implementations | API design, module boundary design |
| Resource Constraints | Consider time, memory, and I/O costs simultaneously | Performance tuning, infrastructure cost optimization |
| Verifiability | Judge by measurement and counterexamples, not claims | Test strategy, experiment design |

Data representation concepts connect directly to serialization formats, network protocols, and storage engine design constraints. When the same value travels as a JSON API response, a binary message queue payload, and a database column (integer/string), tracking what losses and conversion costs arise at each step is essential.

### Learning Tip: See Representation-Transmission-Storage as One Flow

Data representation does not end at memory internals. When the same value moves across API responses (JSON), message queues (binary), and DB columns (integer/string), different losses and conversion costs appear. A practical exercise: serialize the same record into three formats and compare size, parsing time, and readability.

## Checklist

- [ ] I can convert between binary and decimal
- [ ] I can explain the difference between ASCII and UTF-8
- [ ] I understand the cause of floating-point error
- [ ] I distinguish character length from byte length
- [ ] I know why floats are unsafe for financial data

## Practice Problems

1. Write a function that converts integers 0 to 255 into binary and hexadecimal. Print the result as a table.

2. Write a program that compares the UTF-8 byte counts of various characters (English, Korean, Japanese, emoji).

3. Add `0.1` together 100 times using both `float` and `Decimal`, and observe the difference.

## Wrap-Up and Next Steps

Every piece of data in a computer is a bit sequence. Encoding rules give bits their meaning. Integers use two's complement, characters use UTF-8, and decimals use IEEE 754 floating point. Knowing each representation's limits is the basis of correct design.

The next article covers algorithms — how to process data efficiently — and complexity, the way we measure their performance.

## Answering the Opening Questions

- **How does a computer store numbers, characters, and images using only 0s and 1s?**
  - All data is represented as bits (0/1), and encoding rules assign meaning to bit sequences. The same byte `0x41` becomes character 'A' under ASCII, integer 65 as a number, or a brightness value as a color channel. The convention (rule) determines data's meaning.
- **How do ASCII and UTF-8 differ, and why do byte counts vary?**
  - ASCII is a fixed-length encoding representing 128 English characters in 1 byte. UTF-8 represents all world characters in variable-length 1–4 bytes. English uses 1 byte, Korean uses 3 bytes, emoji uses 4 bytes. Variable length gives space efficiency for English-heavy text but creates the trap that `len(string) != len(bytes)`.
- **Why are negative numbers represented using two's complement?**
  - Two's complement lets a single addition circuit handle both positive and negative operations. No separate subtraction hardware is needed, and there's no dual +0/-0 representation problem. As verified in the example, -5 is `11111011`, and adding it to 5 (`00000101`) produces exactly 0 (`00000000`, ignoring overflow bit).
<!-- toc:begin -->
## In this series

- [Computer Science 101 (1/10): What Is Computer Science?](./01-what-is-computer-science.md)
- [Computer Science 101 (2/10): Computation and Programs](./02-computation-and-programs.md)
- **Data Representation (current)**
- Algorithms and Complexity (upcoming)
- Computer Architecture (upcoming)
- Operating Systems (upcoming)
- Networks (upcoming)
- Databases (upcoming)
- Software Engineering (upcoming)
- From CS to AI and Data Science (upcoming)

<!-- toc:end -->

## References

- [Unicode official site](https://home.unicode.org/)
- [Python docs — Floating Point Arithmetic: Issues and Limitations](https://docs.python.org/3/tutorial/floatingpoint.html)
- [What Every Programmer Should Know About Floating-Point](https://floating-point-gui.de/)
- [Joel Spolsky — The Absolute Minimum About Unicode](https://www.joelonsoftware.com/2003/10/08/the-absolute-minimum-every-software-developer-absolutely-positively-must-know-about-unicode-and-character-sets-no-excuses/)

Tags: Computer Science, Binary, Character Encoding, UTF-8, Floating Point, Data Types
