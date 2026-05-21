---
series: algorithms-101
episode: 9
title: "Algorithms 101 (9/10): 문자열 알고리즘 기초"
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
  - 알고리즘
  - 문자열
  - KMP
  - Trie
  - Regex
seo_description: 단순 매칭의 비용, KMP 실패 함수의 직관, 트라이 자료구조, 그리고 정규식의 비용·보안 함정을 정리합니다.
last_reviewed: '2026-05-12'
---

# Algorithms 101 (9/10): 문자열 알고리즘 기초

문자열 안에서 패턴 하나 찾는 일이 단순해 보이는데, 왜 알고리즘이 그렇게 많을까요? 이 글은 Algorithms 101 시리즈의 아홉 번째 글입니다. 여기서는 단순 매칭, KMP, 트라이, 그리고 실무 정규식의 비용 감각을 정리합니다.

## 먼저 던지는 질문

- 단순 매칭은 왜 최악에 O(nm)까지 갈까요?
- KMP의 실패 함수는 어떤 직관으로 이해해야 할까요?
- 트라이는 어떤 문제에서 특히 강할까요?

## 큰 그림

![Algorithms 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/09/09-01-big-picture.ko.png)

*Algorithms 101 9장 흐름 개요*

## 왜 중요한가

문자열은 로그, 문서, 코드, 검색, NLP 등 거의 모든 영역에 등장합니다. 단순 매칭으로 충분한 경우도 많지만, 패턴이 길고 텍스트가 크거나 다중 패턴을 동시에 처리해야 하면 적절한 알고리즘이 성능을 좌우합니다. 정규식의 함정은 보안 사고로도 이어집니다.

> 문자열 알고리즘은 단순해 보이는 표면 아래에 폭발적인 비용을 숨기고 있습니다.

## 한눈에 보는 개념

> 단순 매칭은 모든 시작 위치에서 패턴을 비교하므로 최악 O(nm)입니다. KMP는 패턴이 자기 자신과 얼마나 겹치는지를 실패 함수로 미리 계산해 같은 문자를 다시 보지 않으므로 O(n+m)입니다. 트라이는 prefix를 공유하는 트리로, 다중 패턴 검색과 자동완성에 적합합니다. 정규식 엔진은 구현 방식에 따라 선형에 가깝게 동작하기도 하고, 백트래킹 때문에 지수 시간으로 무너지기도 합니다.

```text
Naive matching     : O(nm)
KMP                : O(n+m), failure function preprocessing O(m)
Aho-Corasick       : multi-pattern in O(n + matches)
Trie               : prefix sharing, autocomplete, multi-pattern
Regex              : expressive, backtracking engines risk ReDoS
```

## 핵심 용어

| 용어 | 설명 |
| --- | --- |
| 패턴 | 텍스트 안에서 찾고 싶은 문자열 |
| 실패 함수 | KMP에서 prefix-suffix 겹침 길이를 저장한 배열 |
| 트라이 | 공통 접두사를 공유하는 트리 자료구조 |
| Aho-Corasick | 트라이와 failure link를 결합한 다중 패턴 매칭 |
| ReDoS | 백트래킹 정규식의 지수 시간 취약점 |

## Before / After

**Before — 단순 매칭, 최악 O(nm):**

```python
def naive_match(text, pat):
    n, m = len(text), len(pat)
    for i in range(n - m + 1):
        if text[i:i + m] == pat:
            return i
    return -1
```

**After — KMP, O(n+m):**

```python
def kmp_search(text, pat):
    fail = compute_failure(pat)
    j = 0
    for i, c in enumerate(text):
        while j > 0 and c != pat[j]:
            j = fail[j - 1]
        if c == pat[j]:
            j += 1
            if j == len(pat):
                return i - j + 1
    return -1
```

## 단계별로 따라가기

### 1단계: 단순 매칭의 최악 경우

```python
text = "a" * 100000 + "b"
pat = "a" * 1000 + "b"

import time
t = time.perf_counter()
naive_match(text, pat)
print(f"naive: {time.perf_counter() - t:.3f}s")
```

반복적인 텍스트에서는 매 시작 위치마다 거의 m번 비교가 일어납니다. 입력이 커지면 금세 비실용적이 됩니다.

### 2단계: KMP의 실패 함수

```python
def compute_failure(pat):
    fail = [0] * len(pat)
    k = 0
    for i in range(1, len(pat)):
        while k > 0 and pat[k] != pat[i]:
            k = fail[k - 1]
        if pat[k] == pat[i]:
            k += 1
        fail[i] = k
    return fail

print(compute_failure("ababaca"))   # [0, 0, 1, 2, 3, 0, 1]
```

실패 함수는 "여기서 불일치가 났을 때 비교를 어디서 다시 시작할지"를 미리 계산해 둔 표입니다. KMP의 핵심은 사실상 이 배열 하나입니다.

### 3단계: KMP 실행

```python
def kmp_search(text, pat):
    if not pat:
        return 0
    fail = compute_failure(pat)
    j = 0
    for i, c in enumerate(text):
        while j > 0 and c != pat[j]:
            j = fail[j - 1]
        if c == pat[j]:
            j += 1
            if j == len(pat):
                return i - j + 1
    return -1

print(kmp_search("ababcababcabc", "ababcabc"))   # 4
```

텍스트는 한 번만 훑고, 점프하는 것은 패턴 쪽 포인터 `j`입니다. 그래서 전체 비용이 O(n+m)에 머뭅니다.

### 4단계: 트라이 — 자동완성의 기본 자료구조

```python
class Trie:
    def __init__(self):
        self.root = {}
        self.END = "$"
    def insert(self, word):
        node = self.root
        for c in word:
            node = node.setdefault(c, {})
        node[self.END] = True
    def starts_with(self, prefix):
        node = self.root
        for c in prefix:
            if c not in node:
                return []
            node = node[c]
        out = []
        def dfs(n, path):
            if self.END in n:
                out.append(prefix + "".join(path))
            for c, child in n.items():
                if c == self.END:
                    continue
                path.append(c); dfs(child, path); path.pop()
        dfs(node, [])
        return out

t = Trie()
for w in ["car", "card", "care", "cargo", "cat"]:
    t.insert(w)
print(t.starts_with("car"))   # ['car', 'card', 'care', 'cargo']
```

트라이는 접두사를 공유하므로 prefix 질의가 매우 빠르고, 많은 문자열을 다룰 때 구조적 이점을 가집니다.

### 5단계: 정규식의 함정 — ReDoS

```python
import re, time

# A pattern that triggers catastrophic backtracking
pat = re.compile(r"^(a+)+$")
text = "a" * 30 + "!"

t = time.perf_counter()
pat.match(text)
print(f"regex: {time.perf_counter() - t:.3f}s")
# Add a few more characters and the time explodes
```

그룹 안에 중첩된 greedy quantifier는 백트래킹 엔진에서 지수 시간을 일으킬 수 있습니다. 신뢰할 수 없는 입력을 받는 경우 패턴을 단순화하거나 RE2 같은 선형 시간 엔진을 검토해야 합니다.

## 이 글에서 먼저 가져갈 점

- 단순 매칭은 짧은 패턴과 짧은 텍스트에는 충분하지만 한계가 분명합니다.
- 실패 함수만 제대로 이해하면 KMP는 생각보다 깔끔합니다.
- 트라이는 prefix 공유 문제가 보이면 가장 먼저 떠올릴 자료구조입니다.
- 정규식의 편의성 뒤에는 성능과 보안 비용이 숨어 있습니다.

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 큰 텍스트에 단순 매칭 고집 | 느림 | KMP나 표준 라이브러리를 사용합니다 |
| KMP를 손으로 구현하며 off-by-one 발생 | 잘못된 매치 | 표준 의사코드를 그대로 따릅니다 |
| 트라이의 종료 표시 누락 | `car`와 `card` 구분 실패 | 끝 노드에 END 마커를 둡니다 |
| ReDoS 위험 패턴 사용 | 서비스 지연 | 패턴을 단순화하고 timeout이나 선형 엔진을 검토합니다 |
| 하나의 정규식에 너무 많은 의미를 담음 | 가독성 저하 | 검증 가능한 파서로 쪼갭니다 |

## 실무에서는 이렇게 쓰입니다

- 검색 엔진의 prefix 검색과 인덱스 구성
- 코드 에디터 자동완성
- 보안 도구의 시그니처 매칭
- 로그 파이프라인의 안전한 패턴 추출
- NLP 전처리의 토크나이저

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 먼저 "패턴이 짧고 일회성인가, 길고 반복적인가"를 묻습니다. 짧고 단발이면 표준 라이브러리로 충분하고, 패턴이 많거나 반복된다면 트라이, KMP, Aho-Corasick 같은 전용 도구를 고려합니다.

또한 정규식 입력의 출처를 항상 의식합니다. 사용자 입력이나 외부 데이터가 들어오면 패턴을 단순화하고, 가능하면 선형 시간 엔진을 선호하며, timeout을 두는 편이 안전합니다. ReDoS는 실제 운영 사고 패턴입니다.

## 체크리스트

- [ ] 단순 매칭의 최악 비용을 설명할 수 있는가
- [ ] KMP 실패 함수의 직관을 한 문장으로 말할 수 있는가
- [ ] 트라이를 직접 구현할 수 있는가
- [ ] 정규식의 비용과 보안 위험을 알고 있는가
- [ ] 다중 패턴 매칭이 필요할 때 적절한 도구를 고를 수 있는가

## 연습 문제

1. KMP의 실패 함수만 사용해, 패턴이 텍스트에 등장하는 모든 위치를 반환하는 함수를 작성해 보세요.

2. 트라이를 이용해 자동완성 결과를 사전순으로 반환해 보세요. 결과가 너무 많을 때는 상위 k개만 반환하도록 확장해 보세요.

3. ReDoS 위험 정규식을 정적으로 감지하는 간단한 휴리스틱을 설계해 보세요. 예를 들어 중첩 양화사 같은 규칙부터 시작해 보세요.

## 정리 및 다음 단계

문자열 알고리즘은 단순함과 폭발적인 비용 사이의 균형을 다룹니다. 단순 매칭, KMP, 트라이, 정규식 비용 감각만 익혀도 대부분의 일상적인 문자열 문제를 안전하게 다룰 수 있습니다. 그 너머에는 suffix array, suffix automaton, bit-parallel matching 같은 고급 주제가 이어집니다.

다음 글이자 마지막 글에서는 알고리즘 문제 풀이 전략을 정리합니다. 문제를 패턴에 연결하고, 사고를 조직하고, 면접과 실무에서 "알고리즘을 잘한다"는 것이 무엇인지 살펴보겠습니다.


## 추가 실전 섹션: 복잡도·추적·구현 선택을 한 번에 연결하기

알고리즘 학습에서 가장 중요한 전환점은 "개념 이해"와 "문제 풀이" 사이를 잇는 기준을 갖는 것입니다. 아래 표는 정렬·탐색·재귀·DP·그리디·그래프·문자열 문제를 만났을 때 가장 먼저 결정해야 할 선택지를 한눈에 정리한 것입니다.

| 문제 신호 | 1차 후보 | 시간 복잡도 목표 | 확인할 함정 |
| --- | --- | --- | --- |
| 정렬 여부가 핵심 단서 | 이진 탐색 / bisect | O(log n) | 데이터 정렬 전제 누락 |
| 전체 순위가 필요 | 정렬(Timsort/merge) | O(n log n) | 안정 정렬 필요 여부 |
| 상위 k개만 필요 | heap | O(n log k) | 전체 정렬로 과투자 |
| 부분 문제가 반복 | DP | O(states * transition) | 상태 정의 모호 |
| 즉시 최선 선택이 유력 | 그리디 | 보통 O(n log n) 이하 | 교환 논증 부재 |
| 연결·최단·순서 제약 | 그래프(BFS/DFS/다익스트라) | O(V+E), O((V+E)logV) | 가중치 조건 혼동 |
| 긴 텍스트 패턴 검색 | KMP/Trie | O(n+m) | 정규식 백트래킹 비용 |

### 추적 예시 1: 이진 탐색 경계 버그를 잡는 로그

```python
def lower_bound(arr, target):
    lo, hi = 0, len(arr)
    trace = []
    while lo < hi:
        mid = (lo + hi) // 2
        trace.append((lo, mid, hi, arr[mid]))
        if arr[mid] < target:
            lo = mid + 1
        else:
            hi = mid
    return lo, trace

pos, trace = lower_bound([1, 2, 2, 2, 5, 9], 2)
print(pos)
for t in trace:
    print(t)
```

이런 추적은 오프바이원 버그를 빠르게 드러냅니다. 특히 `lo`, `hi` 경계 갱신이 틀렸을 때 무한 루프가 나는 문제는 값만 출력하는 디버깅보다 경계 튜플을 기록하는 편이 더 효율적입니다.

### 추적 예시 2: 정렬 알고리즘 선택 비교

| 입력 특성 | `sorted`(Timsort) | 직접 quicksort | heap 기반 |
| --- | --- | --- | --- |
| 이미 거의 정렬 | 매우 강함(run 활용) | pivot 품질에 따라 흔들림 | 순위 작업에서는 유리 |
| 무작위 대량 데이터 | 안정적 | 평균은 빠르지만 편차 존재 | top-k에 특화 |
| 다중 키 정렬 | 안정성 덕분에 단순 | 구현 복잡 | 부분 순위만 적합 |

실무에서는 "직접 구현"보다 "표준 라이브러리 + 문제 특화 자료구조" 조합이 장기 유지보수에 유리합니다. 코드 길이가 아니라 오류 가능성과 운영 신뢰성이 핵심 기준입니다.

### 문제 풀이 루틴: 5분 점검

1. 입력 크기로 불가능한 차수(O(n^2), O(2^n) 등)를 먼저 제거합니다.
2. 전제(정렬됨, DAG, 음수 가중치 없음, 중복 허용)를 명시합니다.
3. 템플릿(이진 탐색, BFS, DP 상태 전이)을 선택합니다.
4. 작은 반례 2개를 직접 넣어 경계 동작을 확인합니다.
5. 마지막에 복잡도와 메모리 사용량을 한 줄로 기록합니다.

이 루틴을 습관화하면 "코드가 돌아간다"와 "운영에서도 안전하다" 사이의 간격이 크게 줄어듭니다.


## 처음 질문으로 돌아가기

- **단순 매칭은 왜 최악에 O(nm)까지 갈까요?**
  - 본문의 기준은 문자열 알고리즘 기초를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **KMP의 실패 함수는 어떤 직관으로 이해해야 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **트라이는 어떤 문제에서 특히 강할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Algorithms 101 (1/10): 알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [Algorithms 101 (2/10): 시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [Algorithms 101 (3/10): 탐색 알고리즘](./03-search-algorithms.md)
- [Algorithms 101 (4/10): 정렬 알고리즘](./04-sorting-algorithms.md)
- [Algorithms 101 (5/10): 재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [Algorithms 101 (6/10): 동적 계획법](./06-dynamic-programming.md)
- [Algorithms 101 (7/10): 그리디 알고리즘](./07-greedy-algorithms.md)
- [Algorithms 101 (8/10): 그래프 알고리즘](./08-graph-algorithms.md)
- **문자열 알고리즘 기초 (현재 글)**
- 알고리즘 문제 풀이 전략 (예정)

<!-- toc:end -->

## 참고 자료

- [Python `re` documentation](https://docs.python.org/3/library/re.html)
- [Wikipedia — Knuth-Morris-Pratt algorithm](https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm)
- [Wikipedia — Aho-Corasick algorithm](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm)
- [OWASP — Regular expression Denial of Service](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)

Tags: Computer Science, 알고리즘, 문자열, KMP, Trie, Regex
