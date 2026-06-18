---
title: "바이브코딩을 위한 자료구조 기초 (7/10): 이진 탐색 트리"
series: data-structures-101
episode: 7
language: ko
status: draft
targets:
  wordpress: true
tags:
- 바이브코딩
- 자료구조
- AI코딩
seo_description: "바이브코딩 시대, AI가 정렬된 데이터를 다루는 코드를 줄 때 BST와 균형 트리의 원리를 알면 더 나은 선택을 할 수 있습니다."
---

# 바이브코딩을 위한 자료구조 기초 (7/10): 이진 탐색 트리

이 글은 바이브코딩을 위한 자료구조 기초 시리즈의 7번째 글입니다.

가격 범위로 상품을 검색하는 기능을 만들고 있습니다. AI에게 "1만원~5만원 사이 상품 모두 가져와, 실시간으로 상품이 추가/삭제돼"라고 했습니다. AI가 이렇게 줬습니다.

```python
import bisect

prices = []

def add_product(price, product):
    bisect.insort(prices, (price, product))   # 정렬 유지 + 삽입

def search_range(low, high):
    # 이진 탐색으로 범위 찾기
    start = bisect.bisect_left(prices, (low,))
    end = bisect.bisect_right(prices, (high, chr(0x10ffff)))
    return prices[start:end]
```

검색은 O(log n)으로 빠릅니다. 그런데 삽입(`bisect.insort`)은 어떨까요? 이진 탐색으로 위치는 O(log n)에 찾지만, 배열에 삽입하면서 원소들을 밀어야 하므로 O(n)입니다. 삽입이 자주 일어나는 시스템이라면 이것이 병목이 됩니다.

정렬을 유지하면서 삽입과 검색이 모두 빠른 구조가 이진 탐색 트리(BST)입니다. 파이썬 표준 라이브러리에는 없지만, `sortedcontainers` 같은 라이브러리나 데이터베이스 인덱스가 이 계열을 씁니다.

> 정렬과 검색, 삽입, 삭제를 모두 O(log n)에 가깝게 동시에 제공하는 것은 BST 계열만의 강점입니다.

---

## 이 글에서 다룰 문제
- BST의 불변식이 왜 빠른 검색을 가능하게 하는지 이해할 수 있나요?
- 편향 트리가 왜 O(n)으로 무너지는지, 균형 트리가 왜 필요한지 알 수 있나요?
- `sortedcontainers.SortedList`가 어떤 상황에서 bisect보다 나은가요?
- 데이터베이스 인덱스가 BST 계열이라는 것이 실무에서 어떤 의미인지 이해할 수 있나요?
- AI에게 정렬된 동적 데이터 관련 코드를 어떻게 요청할까요?

## 핵심 개념: BST 불변식과 균형

BST의 핵심 규칙: 각 노드의 왼쪽 서브트리 전체는 더 작고, 오른쪽 서브트리 전체는 더 큽니다.

```text
균형 BST (좋음):         편향 BST (나쁨):
       5                  1
      / \                  \
     3   7                  2
    / \ / \                  \
   2  4 6  8                  3
                               \
   검색: O(log n)               ...  검색: O(n)
```

삽입 순서가 정렬된 데이터이면 편향 트리가 됩니다. AVL, Red-Black 같은 균형 트리는 자동으로 균형을 유지합니다. 파이썬의 `sortedcontainers.SortedList`나 데이터베이스의 B-Tree가 이 계열입니다.

## Before / After

**Before — 정렬된 배열 + bisect (삽입 O(n)):**

```python
import bisect

data = []
for v in stream:
    bisect.insort(data, v)   # 탐색 O(log n) + 삽입 이동 O(n)
```

**After — SortedList (삽입/검색 모두 O(log n)):**

```python
from sortedcontainers import SortedList

data = SortedList()
for v in stream:
    data.add(v)              # O(log n)

# 범위 검색
result = list(data.irange(low, high))   # O(log n + k)
```

삽입이 빈번하고 정렬 유지가 필요하다면 SortedList가 훨씬 적합합니다.

## 바이브코딩할 때 자주 하는 실수

| 실수 | 왜 문제인가 | 해결 |
|------|------------|------|
| bisect.insort로 동적 삽입을 자주 함 | 삽입마다 O(n) 이동 | sortedcontainers.SortedList 사용 |
| BST를 직접 구현해 달라고 요청 | 균형 처리 없으면 O(n)으로 무너짐 | sortedcontainers나 heapq 같은 검증된 라이브러리 요청 |
| 해시 테이블로 범위 쿼리 시도 | dict는 범위 검색 지원 안 함 | BST 계열이나 정렬된 배열 + bisect 사용 |
| 데이터베이스 인덱스 없이 범위 쿼리 | DB가 전체 스캔을 함 | 범위 쿼리 컬럼에 인덱스 생성 요청 |
| 정렬된 입력으로 BST 직접 구현 | 편향 트리가 되어 O(n) 검색 | AVL이나 Red-Black 계열 구현 요청 |

## AI에게 자료구조 관련 질문하는 팁

1. **정렬 유지 + 동적 삽입이면 명시하세요.** "정렬을 유지하면서 실시간으로 추가/삭제도 있어" → SortedList
2. **범위 쿼리를 말해주세요.** "a 이상 b 이하인 값을 자주 조회해야 해" → BST 계열 또는 DB 인덱스
3. **삽입 빈도를 알려주세요.** "데이터가 자주 바뀌어" vs "한 번 만들고 자주 읽어" → 동적 vs 정적 구조 선택
4. **DB 컨텍스트라면 인덱스를 요청하세요.** "이 쿼리에 인덱스가 필요해?" → 범위 조건 컬럼에 인덱스
5. **외부 라이브러리 사용 가능 여부를 말해주세요.** "sortedcontainers 써도 돼" → 직접 구현보다 안정적

## 운영 체크리스트
- [ ] BST 불변식(왼쪽 < 부모 < 오른쪽)을 설명할 수 있습니다
- [ ] 편향 트리가 왜 O(n)이 되는지 이해했습니다
- [ ] 균형 트리가 필요한 이유를 설명할 수 있습니다
- [ ] bisect vs SortedList의 삽입 비용 차이를 알고 있습니다
- [ ] 데이터베이스 인덱스가 BST 계열이라는 연결을 이해했습니다
- [ ] 범위 쿼리와 키 기반 조회의 차이에 따라 자료구조를 선택할 수 있습니다

## 처음 질문으로 돌아가기

가격 범위 검색에서 `bisect.insort`가 왜 실시간 삽입에 적합하지 않은지 이제 명확합니다. 배열 삽입은 원소를 밀어야 하므로 O(n)입니다. 삽입이 잦다면 `SortedList`가 O(log n) 삽입과 O(log n) 범위 검색을 모두 제공합니다. AI에게 "정렬 유지하면서 동적 삽입이 빈번해, SortedList 쓸게"라고 명시하면 처음부터 적합한 코드를 받을 수 있습니다.

## 정리

BST는 정렬을 유지하면서 검색/삽입/삭제를 O(log n)에 가깝게 처리합니다. 단, 편향 트리가 되면 O(n)으로 무너지므로 균형 트리가 필요합니다. 파이썬에서는 `sortedcontainers.SortedList`가 실용적인 선택이고, 데이터베이스 B-Tree 인덱스가 같은 계열입니다. 바이브코딩에서는 정렬된 동적 데이터와 범위 쿼리가 나오면 BST 계열을 요청하는 것이 핵심입니다.

## 참고 자료

### 공식 문서
- [Python Data Structures (python.org)](https://docs.python.org/3/tutorial/datastructures.html)

### 관련 시리즈
- [Algorithms 101](../../algorithms-101/ko/)

---

<!-- toc:begin -->
## 시리즈 목차

- 바이브코딩을 위한 자료구조 기초 (1/10): 자료구조란 무엇인가?
- 바이브코딩을 위한 자료구조 기초 (2/10): 배열과 동적 배열
- 바이브코딩을 위한 자료구조 기초 (3/10): 연결 리스트
- 바이브코딩을 위한 자료구조 기초 (4/10): 스택과 큐
- 바이브코딩을 위한 자료구조 기초 (5/10): 해시 테이블
- 바이브코딩을 위한 자료구조 기초 (6/10): 트리
- **바이브코딩을 위한 자료구조 기초 (7/10): 이진 탐색 트리 (현재 글)**
- 바이브코딩을 위한 자료구조 기초 (8/10): 힙
- 바이브코딩을 위한 자료구조 기초 (9/10): 그래프
- 바이브코딩을 위한 자료구조 기초 (10/10): 자료구조 선택 기준
<!-- toc:end -->

Tags: 바이브코딩, 자료구조, AI코딩
