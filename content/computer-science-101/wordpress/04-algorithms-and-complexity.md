---
series: computer-science-101
episode: 4
title: "바이브코딩을 위한 컴퓨터 과학 기초 (4/10): 알고리즘과 복잡도"
status: publish-ready
targets:
  wordpress: true
tags:
  - 바이브코딩
  - Computer Science
  - 알고리즘
  - Big-O
  - 복잡도
  - AI 코딩
seo_description: Big-O 복잡도를 바이브코딩 관점에서 이해합니다. AI가 만든 코드의 성능 문제를 발견하고 올바른 알고리즘을 요청하는 기초입니다.
language: ko
last_reviewed: '2026-06-18'
---

# 바이브코딩을 위한 컴퓨터 과학 기초 (4/10): 알고리즘과 복잡도

> 이 글은 **바이브코딩을 위한 컴퓨터 과학 기초** 시리즈의 네 번째 글입니다. AI에게 코드를 시키려면 컴퓨터가 어떻게 동작하는지 기본은 알아야 합니다.

---

AI가 만들어준 코드가 개발 환경에서는 잘 돌아갔는데, 운영 서버에서 데이터가 10만 건이 넘자 갑자기 응답이 느려졌다면, 그 이유는 거의 항상 알고리즘 복잡도에 있습니다.

작은 입력에서는 멀쩡하던 코드가 운영에서 갑자기 느려지는 이유는 대개 하드웨어보다 알고리즘 차수에서 먼저 설명됩니다. 같은 문제를 풀어도 어떤 코드는 선형으로 늘고, 어떤 코드는 제곱으로 무너집니다.

> **바이브코딩 관점:** AI에게 "이 코드의 시간 복잡도를 O(n)으로 줄여줘"라고 요청하려면 Big-O가 무엇인지 알아야 합니다. 복잡도를 모르면 AI 코드의 성능 한계를 판단할 수 없습니다.

---

## 이 글에서 다룰 문제

- 같은 문제를 푸는 두 코드 중 무엇이 더 빠를지 어떻게 판단할까요?
- 시간 복잡도와 공간 복잡도는 무엇을 각각 뜻할까요?
- Big-O 표기법은 왜 코드를 실행하지 않고도 성능을 가늠하게 해 줄까요?
- AI가 만든 코드에서 성능 문제를 어떻게 발견하고 수정을 요청할까요?
- 바이브코더가 알고리즘에서 가장 자주 놓치는 포인트는 무엇일까요?

---

## 핵심 개념 한 줄 정리

> **알고리즘 = 문제를 푸는 절차, 복잡도 = 그 절차의 비용**

코드가 100개 데이터에서 잘 돌아가도 100만 개에서는 멈출 수 있습니다. Big-O는 코드를 실행해 보지 않고도 성능 한계를 미리 판단하게 해 줍니다.

| 용어 | 설명 |
| --- | --- |
| Algorithm | 입력을 원하는 출력으로 바꾸는 유한하고 명확한 절차 |
| Time complexity | 입력 크기가 커질 때 연산 수가 증가하는 비율 |
| Space complexity | 입력 크기에 따라 추가 메모리가 늘어나는 비율 |
| Big-O | 입력이 무한히 커질 때의 상한 증가율 표기 |
| Data structure | 데이터를 저장하고 접근하는 방식 |

---

## Before / After: 복잡도를 알기 전과 후

**Before — 복잡도를 모를 때:**

```python
# 두 리스트의 공통 원소 찾기 — O(n²)
def common_slow(a: list[int], b: list[int]) -> list[int]:
    result = []
    for x in a:
        if x in b:        # list에서 in은 O(n)
            result.append(x)
    return result

# n=10,000이면 대략 1억 번 비교 — 수 초 소요
```

AI에게 "공통 원소 찾는 함수 만들어줘"라고 하면 이런 코드가 나올 수 있습니다.

**After — 복잡도를 알 때:**

```python
# 같은 문제 — O(n)
def common_fast(a: list[int], b: list[int]) -> list[int]:
    b_set = set(b)        # 한 번만 O(n)
    return [x for x in a if x in b_set]   # set에서 in은 O(1)

# n=10,000이면 대략 2만 번 비교 — 밀리초 단위
```

AI에게 "set을 써서 O(n) 복잡도로 만들어줘"라고 요청하면 올바른 코드를 받을 수 있습니다.

---

## 핵심 내용: 바이브코딩 관점에서 보는 알고리즘과 복잡도

### 복잡도 직관 익히기

```python
import math

def complexity_table(sizes: list[int]) -> None:
    print(f"{'n':>10} {'O(log n)':>12} {'O(n)':>12} {'O(n log n)':>14} {'O(n²)':>16}")
    for n in sizes:
        log_n = math.log2(n)
        print(f"{n:>10} {log_n:>12.1f} {n:>12} {n * log_n:>14.0f} {n * n:>16,}")

complexity_table([10, 100, 1_000, 10_000, 100_000])
```

| n | O(log n) | O(n) | O(n log n) | O(n²) |
|---|----------|------|------------|-------|
| 1,000 | 10 | 1,000 | 10,000 | 1,000,000 |
| 100,000 | 17 | 100,000 | 1,700,000 | 10,000,000,000 |

n=100,000에서 O(n²)는 O(n)보다 10만 배 느립니다.

### 자료구조 선택이 복잡도를 바꾼다

```python
import time

nums_list = list(range(1_000_000))
nums_set = set(nums_list)

# list에서 in은 O(n)
start = time.perf_counter()
print(999_999 in nums_list)
print(f"list   : {time.perf_counter() - start:.4f}s")

# set에서 in은 평균 O(1)
start = time.perf_counter()
print(999_999 in nums_set)
print(f"set    : {time.perf_counter() - start:.6f}s")
```

AI에게 "자주 조회하는 데이터는 list 대신 set을 써줘"라고 요청하면 성능이 크게 개선됩니다.

### 공간-시간 트레이드오프

```python
# 시간 우선: hash map 기반 Two Sum — O(n) time, O(n) space
def two_sum_hash(nums: list[int], target: int) -> tuple[int, int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return (seen[complement], i)
        seen[num] = i
    return (-1, -1)

# 공간 우선: sort + two pointers — O(n log n) time, O(1) space
def two_sum_sort(nums: list[int], target: int) -> tuple[int, int]:
    indexed = sorted(enumerate(nums), key=lambda x: x[1])
    lo, hi = 0, len(indexed) - 1
    while lo < hi:
        s = indexed[lo][1] + indexed[hi][1]
        if s == target:
            return (indexed[lo][0], indexed[hi][0])
        elif s < target:
            lo += 1
        else:
            hi -= 1
    return (-1, -1)
```

AI에게 "메모리가 충분하면 해시맵으로 O(n)으로 해결해줘, 메모리 제약이 있으면 정렬 후 투 포인터로 해줘"처럼 조건을 주면 상황에 맞는 코드를 받을 수 있습니다.

---

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| AI 코드를 작은 데이터에서만 테스트 | n이 커지면 폭발적으로 느려짐 | 입력 크기를 10배, 100배로 늘려 가며 측정 |
| AI 코드에서 list에 in 연산 반복 사용 | O(n²) 누적 | 조회 대상은 set이나 dict로 변환 요청 |
| AI에게 복잡도 요구사항 없이 요청 | 느린 알고리즘이 나올 수 있음 | "O(n log n) 이하로 해줘" 명시 |
| 모든 코드를 O(1)로 만들려는 시도 | 가독성 저하, 메모리 폭증 | 병목 구간만 최적화 |
| 평균과 최악 복잡도를 혼동 | dict가 항상 O(1)이라고 가정 | 해시 충돌이 있으면 최악은 O(n) |

---

## AI 코딩 팁

1. **복잡도를 요구사항에 명시하세요.** "O(n) 이하로 구현해줘", "set을 써서 O(1) 조회가 되게 해줘"처럼 요청하면 성능이 보장된 코드를 받을 수 있습니다.
2. **AI 코드에서 중첩 루프를 먼저 확인하세요.** 중첩 루프는 대부분 O(n²) 이상입니다. 발견하면 AI에게 "이 중첩 루프를 O(n)으로 최적화해줘"라고 요청합니다.
3. **자료구조 선택을 AI에게 맡기되 결과를 검토하세요.** "빠른 조회를 위해 어떤 자료구조가 적합한지 복잡도와 함께 설명해줘"라고 물어보는 것이 좋습니다.

---

## 체크리스트

- [ ] Big-O 표기법으로 알고리즘의 차수를 말할 수 있는가
- [ ] list, set, dict의 주요 연산 복잡도를 이해하는가
- [ ] AI 코드에서 O(n²) 패턴을 발견할 수 있는가
- [ ] 시간-공간 트레이드오프를 AI에게 조건으로 전달할 수 있는가
- [ ] 작은 데이터의 결과만 보고 성능을 판단하지 않는가

---

## 처음 질문으로 돌아가기

- **같은 문제를 푸는 두 코드 중 무엇이 더 빠를지 어떻게 판단할까요?**
  Big-O 차수를 비교합니다. O(n) < O(n log n) < O(n²) 순으로 빠릅니다.

- **AI가 만든 코드에서 성능 문제를 어떻게 발견할까요?**
  중첩 루프를 찾고, list에서 in 연산이 반복되는지 확인하며, AI에게 복잡도를 설명해달라고 요청합니다.

- **자료구조 선택이 왜 복잡도를 바꿀까요?**
  list의 in은 O(n), set/dict의 in은 O(1)입니다. 같은 로직도 어떤 자료구조를 쓰느냐에 따라 복잡도가 바뀝니다.

---

## 정리

알고리즘은 문제를 푸는 절차이고, 복잡도는 그 절차의 비용입니다. Big-O는 AI 코드의 성능을 평가하는 언어입니다. AI에게 복잡도 요구사항을 명시하면 더 효율적인 코드를 받을 수 있습니다.

다음 글에서는 이 알고리즘이 실제로 돌아가는 하드웨어, CPU와 메모리 계층이 코드 성능에 어떤 영향을 주는지 봅니다.

---

## 참고 자료

- [Big-O Cheat Sheet](https://www.bigocheatsheet.com/)
- [Python TimeComplexity Wiki](https://wiki.python.org/moin/TimeComplexity)
- [Introduction to Algorithms (CLRS)](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 컴퓨터 과학 기초 (1/10): Computer Science란 무엇인가?
- 바이브코딩을 위한 컴퓨터 과학 기초 (2/10): 계산과 프로그램
- 바이브코딩을 위한 컴퓨터 과학 기초 (3/10): 데이터 표현
- **바이브코딩을 위한 컴퓨터 과학 기초 (4/10): 알고리즘과 복잡도 (현재 글)**
- 바이브코딩을 위한 컴퓨터 과학 기초 (5/10): 컴퓨터 구조
- 바이브코딩을 위한 컴퓨터 과학 기초 (6/10): 운영체제
- 바이브코딩을 위한 컴퓨터 과학 기초 (7/10): 네트워크
- 바이브코딩을 위한 컴퓨터 과학 기초 (8/10): 데이터베이스
- 바이브코딩을 위한 컴퓨터 과학 기초 (9/10): 소프트웨어 엔지니어링
- 바이브코딩을 위한 컴퓨터 과학 기초 (10/10): AI와 데이터사이언스까지의 연결
<!-- toc:end -->

Tags: 바이브코딩, Computer Science, 알고리즘, Big-O, 복잡도, AI 코딩
