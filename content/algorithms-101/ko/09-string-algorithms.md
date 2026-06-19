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

문자열 안에서 패턴 하나 찾는 일이 단순해 보이는데, 왜 알고리즘이 그렇게 많을까요? 여기서는 단순 매칭, KMP, 트라이, 그리고 실무 정규식의 비용 감각을 정리합니다.

이 글은 Algorithms 101 시리즈의 9번째 글입니다.

![Algorithms 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/09/09-01-big-picture.ko.png)
*Algorithms 101 9장 흐름 개요*

## 이 글에서 다룰 문제

- 단순 매칭은 왜 최악에 O(nm)까지 갈까요?
- KMP의 실패 함수는 어떤 직관으로 이해해야 할까요?
- 트라이는 어떤 문제에서 특히 강할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

문자열은 로그, 문서, 코드, 검색, NLP 등 거의 모든 영역에 등장합니다. 단순 매칭으로 충분한 경우도 많지만, 패턴이 길고 텍스트가 크거나 다중 패턴을 동시에 처리해야 하면 적절한 알고리즘이 성능을 좌우합니다. 정규식의 함정은 보안 사고로도 이어집니다.

> 문자열 알고리즘은 단순해 보이는 표면 아래에 폭발적인 비용을 숨기고 있습니다.

> 단순 매칭은 모든 시작 위치에서 패턴을 비교하므로 최악 O(nm)입니다. KMP는 패턴이 자기 자신과 얼마나 겹치는지를 실패 함수로 미리 계산해 같은 문자를 다시 보지 않으므로 O(n+m)입니다. 트라이는 prefix를 공유하는 트리로, 다중 패턴 검색과 자동완성에 적합합니다. 정규식 엔진은 구현 방식에 따라 선형에 가깝게 동작하기도 하고, 백트래킹 때문에 지수 시간으로 무너지기도 합니다.

```text
String matching cost
    Naive         : O(nm)         — n: text length, m: pattern length
    KMP           : O(n+m)        — failure function preprocessing O(m)
    Rabin-Karp    : O(n+m) avg   — rolling hash
    Boyer-Moore   : O(nm) worst, O(n/m) best in practice
    Aho-Corasick  : O(n + total_matches) — multi-pattern
    Trie          : prefix sharing, autocomplete, multi-pattern
    Regex (NFA)   : O(nm) — backtracking risk → ReDoS
```

| 용어 | 설명 |
| --- | --- |
| 패턴 | 텍스트 안에서 찾고 싶은 문자열 |
| 실패 함수 | KMP에서 prefix-suffix 겹침 길이를 저장한 배열 |
| 트라이 | 공통 접두사를 공유하는 트리 자료구조 |
| Aho-Corasick | 트라이와 failure link를 결합한 다중 패턴 매칭 |
| ReDoS | 백트래킹 정규식의 지수 시간 취약점 |

## 개선 전 / 개선 후

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

### 1단계: 단순 매칭의 최악 경우 시연

```python
import time

def naive_match(text, pat):
    n, m = len(text), len(pat)
    comparisons = 0
    for i in range(n - m + 1):
        for j in range(m):
            comparisons += 1
            if text[i + j] != pat[j]:
                break
        else:
            return i, comparisons
    return -1, comparisons

# 최악 케이스: 반복 텍스트
text = "a" * 10000 + "b"
pat  = "a" * 100 + "b"

t0 = time.perf_counter()
pos, cmp = naive_match(text, pat)
elapsed = time.perf_counter() - t0
print(f"위치: {pos}, 비교 횟수: {cmp:,}, 시간: {elapsed*1000:.1f}ms")
```

반복적인 텍스트에서는 매 시작 위치마다 거의 m번 비교가 일어납니다. n=10^4, m=100이면 약 10^6번 비교입니다.

### 2단계: KMP의 실패 함수

```python
def compute_failure(pat):
    """
    fail[i] = pat[0..i]에서 가장 긴 proper prefix-suffix의 길이.
    직관: 불일치 발생 시 패턴의 어느 위치에서 재시작할지를 미리 계산.
    """
    fail = [0] * len(pat)
    k = 0
    for i in range(1, len(pat)):
        while k > 0 and pat[k] != pat[i]:
            k = fail[k - 1]
        if pat[k] == pat[i]:
            k += 1
        fail[i] = k
    return fail

# "ababaca" → [0, 0, 1, 2, 3, 0, 1]
# fail[4]=3: "ababa"에서 "aba"가 prefix이자 suffix
pat = "ababaca"
fail = compute_failure(pat)
print(f"패턴: {pat}")
print(f"fail: {fail}")
for i, f in enumerate(fail):
    if f > 0:
        print(f"  fail[{i}]={f}: '{pat[:i+1]}'의 가장 긴 prefix-suffix = '{pat[:f]}'")
```

실패 함수는 "여기서 불일치가 났을 때 비교를 어디서 다시 시작할지"를 미리 계산해 둔 표입니다. KMP의 핵심은 사실상 이 배열 하나입니다.

### 3단계: KMP 실행 — 모든 위치 찾기

```python
def kmp_search_all(text, pat):
    """KMP로 패턴의 모든 등장 위치 반환. O(n+m) 시간."""
    if not pat:
        return []
    fail = compute_failure(pat)
    positions = []
    j = 0
    for i, c in enumerate(text):
        while j > 0 and c != pat[j]:
            j = fail[j - 1]
        if c == pat[j]:
            j += 1
            if j == len(pat):
                positions.append(i - j + 1)
                j = fail[j - 1]   # 겹치는 매치를 위해 리셋
    return positions

text = "ababcababcabc"
pat  = "ababc"
print(kmp_search_all(text, pat))   # [0, 5]

# 비교: 단순 매칭
import re
naive_positions = [m.start() for m in re.finditer(f'(?={re.escape(pat)})', text)]
print(naive_positions)   # [0, 5]
```

텍스트는 한 번만 훑고, 점프하는 것은 패턴 쪽 포인터 `j`입니다. 전체 비용이 O(n+m)에 머뭅니다.

### 4단계: 트라이 — 자동완성의 기본 자료구조

```python
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()

    def insert(self, word):
        node = self.root
        for c in word:
            if c not in node.children:
                node.children[c] = TrieNode()
            node = node.children[c]
        node.is_end = True

    def search(self, word):
        node = self.root
        for c in word:
            if c not in node.children:
                return False
            node = node.children[c]
        return node.is_end

    def starts_with(self, prefix):
        """prefix로 시작하는 모든 단어 반환."""
        node = self.root
        for c in prefix:
            if c not in node.children:
                return []
            node = node.children[c]
        results = []
        self._dfs(node, prefix, results)
        return sorted(results)

    def _dfs(self, node, current, results):
        if node.is_end:
            results.append(current)
        for c, child in node.children.items():
            self._dfs(child, current + c, results)

trie = Trie()
words = ["car", "card", "care", "cargo", "cat", "cats"]
for w in words:
    trie.insert(w)

print(trie.starts_with("car"))   # ['car', 'card', 'care', 'cargo']
print(trie.search("card"))       # True
print(trie.search("cars"))       # False
```

트라이는 접두사를 공유하므로 prefix 질의가 O(m), 전체 메모리는 O(총 문자 수)입니다.

### 5단계: 정규식의 함정 — ReDoS

```python
import re, time

# 안전한 패턴
safe_pat = re.compile(r"\d+")
text = "abc" * 1000

t0 = time.perf_counter()
safe_pat.findall(text)
print(f"안전한 패턴: {(time.perf_counter()-t0)*1000:.2f}ms")

# ReDoS 위험 패턴 (주의: 긴 입력에서 실행하면 매우 느림)
# 아래 코드는 교육 목적으로 짧은 입력에만 실행
danger_pat = re.compile(r"^(a+)+$")
short_text = "a" * 20 + "!"   # 짧게 유지

t0 = time.perf_counter()
danger_pat.match(short_text)
print(f"위험한 패턴(n=20): {(time.perf_counter()-t0)*1000:.3f}ms")

# ReDoS를 유발하는 패턴 식별 기준
redos_signals = [
    "중첩 양화사: (a+)+, (a*)*, (a|a)+",
    "대안 겹침: (a|aa)+",
    "그룹 내 반복: (.+)*",
]
print("ReDoS 위험 신호:")
for s in redos_signals:
    print(f"  - {s}")
```

그룹 안에 중첩된 greedy quantifier는 백트래킹 엔진에서 지수 시간을 일으킬 수 있습니다. 신뢰할 수 없는 입력을 받는 경우 패턴을 단순화하거나 RE2 같은 선형 시간 엔진을 검토해야 합니다.

### 6단계: 롤링 해시 — Rabin-Karp

```python
def rabin_karp(text, pat, base=31, mod=10**9 + 7):
    """
    롤링 해시로 O(n+m) 평균 패턴 매칭.
    충돌 시 문자별 비교로 확인.
    """
    n, m = len(text), len(pat)
    if m > n:
        return -1

    # 패턴 해시 계산
    pat_hash = 0
    for c in pat:
        pat_hash = (pat_hash * base + ord(c)) % mod

    # 텍스트 첫 m자 해시
    window_hash = 0
    for c in text[:m]:
        window_hash = (window_hash * base + ord(c)) % mod

    high_pow = pow(base, m - 1, mod)   # base^(m-1) mod mod

    for i in range(n - m + 1):
        if window_hash == pat_hash:
            if text[i:i + m] == pat:   # 해시 충돌 방지
                return i
        if i < n - m:
            # 롤링: 첫 글자 제거, 새 글자 추가
            window_hash = (window_hash - ord(text[i]) * high_pow) % mod
            window_hash = (window_hash * base + ord(text[i + m])) % mod
    return -1

text = "hello world"
print(rabin_karp(text, "world"))   # 6
print(rabin_karp(text, "xyz"))     # -1
```

## 문자열 알고리즘 Big-O 비교

| 알고리즘 | 전처리 | 검색 | 공간 | 특징 |
| --- | --- | --- | --- | --- |
| 단순 매칭 | O(1) | O(nm) | O(1) | 구현 간단, 짧은 패턴 |
| KMP | O(m) | O(n) | O(m) | 단일 패턴, 긴 텍스트 |
| Rabin-Karp | O(m) | O(n) 평균 | O(1) | 다중 패턴 후보, 해시 충돌 주의 |
| Boyer-Moore | O(m+알파벳) | O(nm) 최악, 실용적 O(n/m) | O(m) | 영어 텍스트에서 빠름 |
| Aho-Corasick | O(합산 m) | O(n + matches) | O(합산 m) | 다중 패턴 동시 검색 |
| Trie | O(합산 m) | O(m) 탐색 | O(합산 m) | 자동완성, prefix 공유 |
| Suffix Array | O(n log n) | O(m log n) | O(n) | 모든 부분 문자열 질의 |
| Regex (NFA) | O(m) | O(nm) 최악 | O(m) | 표현력 높음, ReDoS 주의 |

## 이 글에서 먼저 가져갈 점

- 단순 매칭은 짧은 패턴과 짧은 텍스트에는 충분하지만 한계가 분명합니다.
- 실패 함수만 제대로 이해하면 KMP는 생각보다 깔끔합니다.
- 트라이는 prefix 공유 문제가 보이면 가장 먼저 떠올릴 자료구조입니다.
- 정규식의 편의성 뒤에는 성능과 보안 비용이 숨어 있습니다.
- 다중 패턴 매칭이 필요하면 Aho-Corasick을 고려합니다.

## 자주 하는 실수

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 큰 텍스트에 단순 매칭 고집 | 느림 | KMP나 표준 라이브러리를 사용합니다 |
| KMP를 손으로 구현하며 off-by-one 발생 | 잘못된 매치 | 표준 의사코드를 그대로 따릅니다 |
| 트라이의 종료 표시 누락 | 'car'와 'card' 구분 실패 | 끝 노드에 is_end 마커를 둡니다 |
| ReDoS 위험 패턴 사용 | 서비스 지연 | 패턴을 단순화하고 timeout이나 선형 엔진을 검토합니다 |
| 하나의 정규식에 너무 많은 의미를 담음 | 가독성 저하 | 검증 가능한 파서로 쪼갭니다 |
| 라빈-카프의 해시 충돌 미처리 | 간헐적 오답 | 해시 일치 시 반드시 문자별 확인을 합니다 |

## 실무에서는 이렇게 쓰입니다

- 검색 엔진의 prefix 검색과 인덱스 구성
- 코드 에디터 자동완성
- 보안 도구의 시그니처 매칭
- 로그 파이프라인의 안전한 패턴 추출
- NLP 전처리의 토크나이저

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 먼저 "패턴이 짧고 일회성인가, 길고 반복적인가"를 묻습니다. 짧고 단발이면 표준 라이브러리로 충분하고, 패턴이 많거나 반복된다면 트라이, KMP, Aho-Corasick 같은 전용 도구를 고려합니다.

또한 정규식 입력의 출처를 항상 의식합니다. 사용자 입력이나 외부 데이터가 들어오면 패턴을 단순화하고, 가능하면 선형 시간 엔진을 선호하며, timeout을 두는 편이 안전합니다. ReDoS는 실제 운영 사고 패턴입니다.

## 운영 체크리스트

- [ ] 단순 매칭의 최악 비용을 설명할 수 있는가
- [ ] KMP 실패 함수의 직관을 한 문장으로 말할 수 있는가
- [ ] 트라이를 직접 구현할 수 있는가
- [ ] 정규식의 비용과 보안 위험을 알고 있는가
- [ ] 다중 패턴 매칭이 필요할 때 적절한 도구를 고를 수 있는가
- [ ] 롤링 해시의 원리를 설명할 수 있는가

## 연습 문제

1. KMP의 실패 함수만 사용해, 패턴이 텍스트에 등장하는 모든 위치를 반환하는 함수를 작성해 보세요. 겹치는 매치도 찾아야 합니다.

2. 트라이를 이용해 자동완성 결과를 사전순으로 반환해 보세요. 결과가 너무 많을 때는 상위 k개만 반환하도록 확장해 보세요.

3. ReDoS 위험 정규식을 정적으로 감지하는 간단한 휴리스틱을 설계해 보세요. 예를 들어 중첩 양화사 같은 규칙부터 시작해 보세요.

4. Rabin-Karp를 이용해 주어진 텍스트에서 길이 k인 모든 중복 부분 문자열을 O(n) 시간에 찾아 보세요. 어떤 자료구조와 결합하면 효율적인지도 설명하세요.

## 정리 및 다음 단계

문자열 알고리즘은 단순함과 폭발적인 비용 사이의 균형을 다룹니다. 단순 매칭, KMP, 트라이, 정규식 비용 감각만 익혀도 대부분의 일상적인 문자열 문제를 안전하게 다룰 수 있습니다. 그 너머에는 suffix array, suffix automaton, bit-parallel matching 같은 고급 주제가 이어집니다.

다음 글이자 마지막 글에서는 알고리즘 문제 풀이 전략을 정리합니다. 문제를 패턴에 연결하고, 사고를 조직하고, 면접과 실무에서 "알고리즘을 잘한다"는 것이 무엇인지 봅니다.

## 처음 질문으로 돌아가기

- **단순 매칭은 왜 최악에 O(nm)까지 갈까요?**
  - 텍스트의 모든 시작 위치(n개)에서 패턴을 처음부터 비교합니다. "aaaa...ab"에서 "aaa...ab" 패턴을 찾을 때처럼 반복 텍스트에서는 매 시작 위치마다 거의 m번 비교가 필요합니다. 총 비교 횟수가 n×m에 근접합니다.
- **KMP의 실패 함수는 어떤 직관으로 이해해야 할까요?**
  - 실패 함수 `fail[i]`는 패턴의 부분 문자열 `pat[0..i]`에서 "가장 긴 proper prefix이자 suffix의 길이"입니다. 불일치가 발생했을 때, 이미 매칭한 부분 중 접두사로 재사용 가능한 길이가 얼마인지 미리 계산해 둔 것입니다. 이를 통해 텍스트 포인터를 뒤로 돌리지 않고 O(n+m)에 검색이 가능합니다.
- **트라이는 어떤 문제에서 특히 강할까요?**
  - prefix 공유가 많은 문자열 집합에서 강합니다. 자동완성(입력 prefix로 모든 단어 탐색), 사전 검색, 다중 패턴 매칭(Aho-Corasick의 기반), IP 라우팅 테이블이 대표적입니다. n개의 단어를 저장할 때 공통 prefix를 공유하므로 해시 맵보다 공간 효율적인 경우가 많습니다.

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
- **Algorithms 101 (9/10): 문자열 알고리즘 기초 (현재 글)**
- [알고리즘 문제 풀이 전략](./10-problem-solving-strategies.md)

<!-- toc:end -->

## 참고 자료

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [Python `re` documentation](https://docs.python.org/3/library/re.html)
- [Wikipedia — Knuth-Morris-Pratt algorithm](https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm)
- [Wikipedia — Aho-Corasick algorithm](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm)
- [OWASP — Regular expression Denial of Service](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)

Tags: Computer Science, 알고리즘, 문자열, KMP, Trie, Regex
