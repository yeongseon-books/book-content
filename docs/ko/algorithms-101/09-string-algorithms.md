---
series: algorithms-101
episode: 9
title: 문자열 알고리즘 기초
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
  - 알고리즘
  - 문자열
  - KMP
  - 트라이
  - 정규식
seo_description: 단순 매칭의 비용, KMP의 실패 함수, 트라이 자료구조, 그리고 실무에서 가장 자주 쓰이는 정규식의 비용 감각까지 정리합니다.
last_reviewed: '2026-05-04'
---

# 문자열 알고리즘 기초

> Algorithms 101 시리즈 (9/10)


## 이 글에서 다룰 문제

문자열은 로그·문서·코드·검색·자연어 처리 등 모든 영역에 등장합니다. 단순 매칭이 충분한 경우도 많지만, 패턴이 길거나 텍스트가 매우 클 때 또는 다중 패턴을 동시에 찾아야 할 때는 적절한 알고리즘이 시스템 성능을 좌우합니다. 정규식의 함정은 보안 문제(ReDoS)로 직결됩니다.

> 문자열 알고리즘은 단순함의 가면 뒤에 폭발적인 비용을 숨기고 있습니다.

## 전체 흐름
> 단순 매칭은 텍스트의 모든 시작점에서 패턴 비교를 시도하므로 최악 O(nm)입니다. KMP는 패턴 안의 자기 자신과의 일치를 미리 계산한 실패 함수를 이용해 텍스트의 같은 위치를 두 번 보지 않습니다 — O(n+m). 트라이는 prefix를 공유하는 트리이며, 다중 패턴 검색과 자동완성에 쓰입니다. 정규식은 NFA/DFA 또는 백트래킹 엔진으로 구현되며 후자는 입력에 따라 지수적으로 느려질 수 있습니다.

```text
단순 매칭   : O(nm)
KMP        : O(n+m), 실패 함수 전처리 O(m)
Aho-Corasick: 다중 패턴 동시 매칭 O(n + 매치 수)
트라이      : prefix 공유, 자동완성·다중 패턴
정규식      : 표현력 높음, 백트래킹 엔진은 ReDoS 위험
```

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

## 단계별로 따라하기

### 1단계: 단순 매칭의 최악 케이스

```python
text = "a" * 100000 + "b"
pat = "a" * 1000 + "b"

import time
t = time.perf_counter()
naive_match(text, pat)
print(f"naive: {time.perf_counter() - t:.3f}s")
```

같은 문자가 반복되는 텍스트에서 단순 매칭은 매 시작점에서 거의 m번 비교합니다. 입력이 커지면 실용적이지 않습니다.

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

실패 함수는 "패턴의 i번째까지 본 상태에서 불일치가 나면 다시 비교를 시작할 위치"를 미리 계산합니다. 이 한 표가 KMP의 핵심입니다.

### 3단계: KMP 매칭 실행

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

텍스트 위에서 한 번 훑으며 j 포인터만 점프합니다. O(n+m).

### 4단계: 트라이 — 자동완성의 자료구조

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

트라이는 같은 prefix를 공유하므로 사전 크기 대비 메모리 효율이 높고 prefix 조회가 매우 빠릅니다.

### 5단계: 정규식의 함정 — ReDoS

```python
import re, time

# catastrophic backtracking 발생 가능 패턴
pat = re.compile(r"^(a+)+$")
text = "a" * 30 + "!"

t = time.perf_counter()
pat.match(text)
print(f"regex: {time.perf_counter() - t:.3f}s")
# 입력 길이가 5만 늘어나도 시간이 폭발
```

탐욕적 양화사 + 중첩 그룹은 백트래킹 엔진에서 지수 시간이 걸릴 수 있습니다. 신뢰 못 할 입력에 정규식을 쓰려면 패턴을 단순화하거나 RE2 같은 선형 시간 엔진을 검토해야 합니다.

## 이 코드에서 주목할 점

- 단순 매칭은 짧은 패턴·짧은 텍스트에는 충분하지만 한계가 분명
- KMP의 실패 함수는 한 번 만들어 놓으면 매칭이 깔끔
- 트라이는 prefix가 공유되는 모든 문제의 1순위 자료구조
- 정규식은 강력하지만 입력 신뢰도와 함께 비용을 봐야 함

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 큰 텍스트에 단순 매칭 | 느림 | KMP 또는 라이브러리(`str.find`/`re`) 활용 |
| KMP 실패 함수 직접 구현 시 인덱스 오류 | 잘못된 매치 | 표준 의사코드를 그대로 따라가기 |
| 트라이 종료 표시 누락 | "car"와 "card" 구분 불가 | 노드에 END 표시 |
| ReDoS 패턴 사용 | 서비스 지연 | 패턴 단순화, RE2 검토, timeout |
| 정규식으로 너무 많이 처리 | 가독성 저하 | 분리·검증 가능한 파서 |

## 실무에서는 이렇게 쓰입니다

- 검색 엔진의 inverted index 빌드와 prefix 검색
- 코드 에디터의 자동완성 (트라이 또는 fuzzy match)
- 보안 도구의 시그니처 매칭 (Aho-Corasick)
- 로그 파이프라인의 패턴 추출 (정규식 + 안전한 엔진)
- 자연어 전처리의 토크나이저

## 체크리스트

- [ ] 단순 매칭의 최악 비용을 안다
- [ ] KMP의 실패 함수 직관을 한 줄로 설명할 수 있는가
- [ ] 트라이를 직접 구현할 수 있는가
- [ ] 정규식의 비용·보안 위험을 인지하는가
- [ ] 다중 패턴이 필요한 경우 적절한 도구를 선택할 수 있는가

## 정리 및 다음 단계

문자열 알고리즘은 단순함과 폭발적인 비용 사이의 균형을 다루는 분야입니다. 단순 매칭, KMP, 트라이, 정규식의 네 어휘만 익혀도 일상적인 문자열 작업의 대부분을 안전하게 처리할 수 있습니다. 더 깊이 들어가면 접미사 배열, 접미사 자동자, 비트 병렬 매칭 같은 고급 주제가 기다리고 있습니다.

다음 글이자 시리즈의 마지막 글에서는 알고리즘 문제 풀이 전략을 정리합니다. 어떤 문제에 어떤 패턴을 적용할지, 어떻게 사고를 정리할지, 그리고 면접·실무에서 알고리즘을 잘 다룬다는 것이 무엇인지를 다룹니다.

<!-- toc:begin -->
- [알고리즘이란 무엇인가?](./01-what-is-an-algorithm.md)
- [시간 복잡도와 공간 복잡도](./02-time-and-space-complexity.md)
- [탐색 알고리즘](./03-search-algorithms.md)
- [정렬 알고리즘](./04-sorting-algorithms.md)
- [재귀와 분할 정복](./05-recursion-and-divide-and-conquer.md)
- [동적 계획법](./06-dynamic-programming.md)
- [그리디 알고리즘](./07-greedy-algorithms.md)
- [그래프 알고리즘](./08-graph-algorithms.md)
- **문자열 알고리즘 기초 (현재 글)**
- 알고리즘 문제 풀이 전략 (예정)
<!-- toc:end -->

## 참고 자료

- [Python `re` documentation](https://docs.python.org/3/library/re.html)
- [Wikipedia — Knuth–Morris–Pratt algorithm](https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm)
- [Wikipedia — Aho–Corasick algorithm](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm)
- [OWASP — Regular expression Denial of Service](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)
