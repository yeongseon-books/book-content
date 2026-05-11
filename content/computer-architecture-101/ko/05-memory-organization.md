---
series: computer-architecture-101
episode: 5
title: 메모리 구조
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
  - 메모리
  - 가상 메모리
  - 주소 공간
  - 스택과 힙
seo_description: RAM의 주소 공간, 가상 메모리, 스택과 힙, 그리고 프로세스가 메모리를 보는 방식을 정리합니다.
last_reviewed: '2026-05-04'
---

# 메모리 구조

> Computer Architecture 101 시리즈 (5/10)


## 이 글에서 다룰 문제

메모리 모델을 이해하지 못하면 가장 흔한 버그를 만나게 됩니다. 스택 오버플로, 메모리 누수, 잘못된 포인터, 정렬 오류 — 모두 메모리 구조의 어느 부분을 의식하지 못해 생기는 문제입니다. 또한 가상 메모리는 모든 시스템 성능의 가장 큰 단일 요인 중 하나로, 페이지 폴트가 발생하는 순간 코드가 1만 배 느려질 수 있습니다.

> "이 변수는 어디에 사는가?"라는 질문은 메모리 안전과 성능 모두의 출발점입니다.

## 전체 흐름
> 프로세스마다 자기만의 가상 주소 공간을 갖고, MMU가 가상 주소를 물리 RAM 주소로 매핑합니다. 한 프로세스 안에는 코드(text), 초기화된 데이터, 초기화되지 않은 데이터(BSS), 힙(아래에서 위로 자람), 스택(위에서 아래로 자람)이 정해진 자리에 배치됩니다.

```text
   +------------------+  높은 주소
   |     STACK        |  ← 함수 호출, 지역 변수
   |        |         |
   |        v         |
   |                  |
   |        ^         |
   |        |         |
   |     HEAP         |  ← malloc, new, 동적 할당
   +------------------+
   |     BSS          |  ← 초기화 안된 전역 변수
   +------------------+
   |     DATA         |  ← 초기화된 전역 변수
   +------------------+
   |     TEXT         |  ← 실행 코드
   +------------------+  낮은 주소
```

## Before / After

**Before — "메모리는 평탄한 바이트 배열"이라는 모델:**

```python
data = [0] * 1_000_000
data[12345] = 42
# "그냥 12345번째에 저장된다"
```

**After — "그 주소는 가상이고, 페이지를 거친다"는 모델:**

```text
프로세스 가상 주소: 0x7f8a4c001000 + 12345*8
                    │
                    v  (MMU + 페이지 테이블)
                    │
물리 RAM 주소:      0x00000000abcd1000
                    │
                    v  (캐시 → DRAM 셀)
```

같은 인덱스 접근도 가상 주소→물리 주소→캐시→DRAM의 단계를 거칩니다.

## 단계별로 따라하기

### 1단계: 변수의 실제 주소 확인

```python
import ctypes

x = ctypes.c_int(42)
y = ctypes.c_int(99)
print(hex(ctypes.addressof(x)))
print(hex(ctypes.addressof(y)))
print(f"두 주소 차이: {ctypes.addressof(y) - ctypes.addressof(x)} bytes")
```

C 호환 타입은 실제 주소를 갖습니다. 두 변수의 주소 차이를 보면 메모리가 어떻게 할당되는지 직관이 생깁니다.

### 2단계: 정렬(alignment) 확인

```python
import ctypes

class Misaligned(ctypes.Structure):
    _fields_ = [("a", ctypes.c_char), ("b", ctypes.c_int), ("c", ctypes.c_char)]

class Aligned(ctypes.Structure):
    _fields_ = [("b", ctypes.c_int), ("a", ctypes.c_char), ("c", ctypes.c_char)]

print(ctypes.sizeof(Misaligned))   # 보통 12 (패딩 포함)
print(ctypes.sizeof(Aligned))       # 보통 8
```

같은 필드라도 순서를 바꾸면 패딩이 달라져 크기가 줄어듭니다. 메모리 정렬은 자료구조 설계의 보이지 않는 비용입니다.

### 3단계: 스택과 힙 위치 비교

```python
import ctypes

def stack_var():
    x = ctypes.c_int(1)
    return ctypes.addressof(x)

heap_var = ctypes.c_int(2)
print("힙(전역) 주소:", hex(ctypes.addressof(heap_var)))
print("스택 주소:    ", hex(stack_var()))
```

스택 변수는 호출마다 다른(보통 더 큰) 주소를 갖고, 전역/동적 변수는 안정된 주소에 머뭅니다. 정확한 주소 범위는 시스템마다 다릅니다.

### 4단계: 페이지 크기 확인

```python
import os, resource

print("페이지 크기:", resource.getpagesize(), "bytes")   # 보통 4096
print("내 프로세스 RSS(KB):", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
```

OS는 메모리를 페이지 단위(4KB)로 다룹니다. 한 변수만 접근해도 한 페이지 전체가 RAM으로 들어옵니다. 이것이 다음 글의 캐시 친화성과 연결됩니다.

### 5단계: 스택 깊이 한계 관찰

```python
import sys

def recurse(n):
    return n if n == 0 else recurse(n - 1) + 1

print(sys.getrecursionlimit())
try:
    recurse(2000)
except RecursionError as e:
    print("스택 한계 도달:", e)
```

스택은 정해진 크기로 미리 잡혀 있으며, 깊은 재귀는 그 한계를 넘기면 스택 오버플로가 됩니다. 힙은 동적으로 자라지만 스택은 그렇지 않습니다.

## 이 코드에서 주목할 점

- 모든 변수는 가상 주소를 갖고, MMU가 물리 주소로 변환합니다
- 자료구조의 필드 순서는 패딩과 크기에 영향을 줍니다
- 스택은 한정적이고 빠르며, 힙은 크고 느립니다
- 페이지 단위(4KB)로 메모리가 관리됩니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 깊은 재귀 | 스택 오버플로 | 반복문 또는 명시적 스택 |
| 큰 객체를 스택에 | 스택 크기 초과 | 힙 할당(malloc, new) |
| 필드 정렬 무시 | 메모리 낭비 | 큰 타입 → 작은 타입 순 배치 |
| 가상 주소를 물리로 가정 | 주소 비교, 캐싱 오류 | 가상/물리 구분 의식 |
| 페이지 폴트 무관심 | 갑작스런 1만 배 슬로우다운 | mlock, prefetch, 워킹셋 줄이기 |

## 실무에서는 이렇게 쓰입니다

- 데이터베이스 엔진: 페이지 단위 I/O와 버퍼 풀 관리
- 게임 엔진: 캐시 친화적 구조체(SoA vs AoS) 선택
- 임베디드: 정해진 RAM 안에 스택과 힙 영역 명시적 분할
- 보안: ASLR, NX 비트 등 주소 공간 보호 기능
- 시스템 프로그래밍: mmap으로 파일을 메모리에 직접 매핑

## 체크리스트

- [ ] 가상 주소와 물리 주소의 차이를 안다
- [ ] 페이지 크기가 보통 4KB임을 안다
- [ ] 스택과 힙의 차이를 한 문장으로 말할 수 있는가
- [ ] 구조체의 필드 순서가 크기에 영향을 줄 수 있음을 이해했는가
- [ ] 깊은 재귀가 왜 위험한지 설명할 수 있는가

## 정리 및 다음 단계

메모리는 평탄한 바이트 배열로 보이지만, 그 평탄함은 가상 메모리가 만든 환상입니다. 실제로는 페이지 단위로 매핑되고, 코드·데이터·힙·스택의 영역이 나뉘어 있고, 정렬과 패딩이 자료구조의 진짜 크기를 결정합니다. 이 모델을 잡고 나면 다음 단계인 캐시 이야기가 자연스럽게 따라옵니다.

다음 글에서는 메모리와 CPU 사이에 있는 캐시를 살펴봅니다. 왜 캐시가 필요한지, 지역성이 무엇인지, 그리고 캐시를 의식한 코드와 그렇지 않은 코드의 차이를 다룹니다.

<!-- toc:begin -->
- [컴퓨터 구조란 무엇인가?](./01-what-is-computer-architecture.md)
- [데이터 표현 — bit, byte, integer, floating point](./02-data-representation.md)
- [CPU와 명령어](./03-cpu-and-instructions.md)
- [레지스터와 ALU](./04-registers-and-alu.md)
- **메모리 구조 (현재 글)**
- 캐시와 지역성 (예정)
- 파이프라인 (예정)
- I/O와 장치 (예정)
- 병렬성과 멀티코어 (예정)
- 성능을 이해하는 법 (예정)
<!-- toc:end -->

## 참고 자료

- [Wikipedia — Virtual memory](https://en.wikipedia.org/wiki/Virtual_memory)
- [What every programmer should know about memory (Ulrich Drepper)](https://www.akkadia.org/drepper/cpumemory.pdf)
- [Wikipedia — Data structure alignment](https://en.wikipedia.org/wiki/Data_structure_alignment)
- [Linux Memory Management documentation](https://www.kernel.org/doc/html/latest/admin-guide/mm/index.html)

Tags: Computer Science, 컴퓨터 구조, 메모리, 가상 메모리, 주소 공간, 스택과 힙
