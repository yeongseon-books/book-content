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

이 글은 Algorithms 101 시리즈의 9번째 글입니다.

문자열 안에서 패턴 하나 찾는 일이 단순해 보이는데, 왜 알고리즘이 그렇게 많을까요? 여기서는 단순 매칭, KMP, 트라이, 그리고 실무 정규식의 비용 감각을 정리합니다.

![Algorithms 101 9장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/algorithms-101/09/09-01-big-picture.ko.png)
*Algorithms 101 9장 흐름 개요*

## 먼저 던지는 질문

- 단순 매칭은 왜 최악에 O(nm)까지 갈까요?
- KMP의 실패 함수는 어떤 직관으로 이해해야 할까요?
- 트라이는 어떤 문제에서 특히 강할까요?

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

# 치명적인 역추적을 유발하는 패턴
pat = re.compile(r"^(a+)+$")
text = "a" * 30 + "!"

t = time.perf_counter()
pat.match(text)
print(f"regex: {time.perf_counter() - t:.3f}s")
# 캐릭터를 몇 개 더 추가하면 시간이 폭발적으로 늘어납니다.
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

다음 글이자 마지막 글에서는 알고리즘 문제 풀이 전략을 정리합니다. 문제를 패턴에 연결하고, 사고를 조직하고, 면접과 실무에서 "알고리즘을 잘한다"는 것이 무엇인지 봅니다.

## 실전 확장 워크북

이 절은 문자열 전처리와 매칭를 실제 문제 풀이와 운영 감각으로 연결하기 위한 보강 파트입니다. 개념을 암기하는 대신, 입력 크기·자료 구조·검증 순서를 함께 다루어 같은 유형의 문제를 반복적으로 안정적으로 풀 수 있게 만드는 데 목적이 있습니다. 핵심은 "정답 코드 한 번"이 아니라 "다음 문제에서도 재사용 가능한 판단 프레임"을 확보하는 것입니다.

### 1) 시간 복잡도와 입력 제약을 먼저 맞추기

| 입력 조건 | 우선 배제할 접근 | 현실적인 후보 | 확인 포인트 |
| --- | --- | --- | --- |
| n <= 10^3 | 없음(학습 목적 실험 가능) | 브루트포스, 정렬, 해시 | 구현 명확성 |
| n <= 10^5 | O(n^2) 대부분 배제 | O(n log n), O(n), BFS/DFS | 경계값 테스트 |
| n <= 10^6 이상 | O(n log n)도 부담 가능 | 단일 패스, 압축, 스트리밍 | 메모리 상한 |

복잡도 판단은 코드 스타일 논쟁보다 우선합니다. 같은 팀에서 코드 품질 기준이 달라도, 입력 제약과 차수를 맞추는 원칙은 공통으로 적용됩니다. 이 단계를 건너뛰면 구현이 아무리 깔끔해도 제출 실패나 운영 지연으로 이어집니다.

### 2) 단계별 추적 표로 경계 버그를 조기에 찾기

| 단계 | 관찰 값 | 기대 신호 | 실패 신호 |
| --- | --- | --- | --- |
| 초기화 | 포인터/상태/큐/테이블 | 문제 정의와 일치 | 초기값 누락 |
| 1회 반복 | 상태 전이 | 단조 증가 또는 감소 | 제자리 반복 |
| 종료 직전 | 반환 후보 | 문제 요구와 직접 연결 | 보조값 반환 |

경계 버그는 대부분 "한 줄"에서 발생하지만, 원인은 상태 전이 설계에 있습니다. 그래서 디버깅할 때는 출력값 하나만 보지 말고, 전이 로그를 함께 봐야 합니다. 특히 인덱스 기반 문제는 `lo, mid, hi`, DP 문제는 `state, transition`, 그래프 문제는 `queue size, visited count`를 같이 기록하면 원인 분리가 훨씬 빨라집니다.

### 3) Python 구현 앵커

```python
def prefix_function(p):
    pi = [0] * len(p)
    j = 0
    for i in range(1, len(p)):
        while j > 0 and p[i] != p[j]:
            j = pi[j - 1]
        if p[i] == p[j]:
            j += 1
            pi[i] = j
    return pi
```

코드는 짧아도 충분합니다. 중요한 점은 구현 전에 불변식(invariant)을 문장으로 먼저 고정하는 것입니다. 예를 들어 "현재 단계가 끝나면 최소 비용이 보장된다" 같은 문장이 없으면, 코드가 돌아가도 왜 맞는지 설명할 수 없고, 변형 문제에서 무너지기 쉽습니다.

### 4) LeetCode 스타일 매핑

| 문제 | 핵심 패턴 | 첫 시도에서 자주 틀리는 지점 |
| --- | --- | --- |
| 3 Longest Substring Without Repeating Characters | 제약을 통한 후보 축소 | 입력 조건을 늦게 반영 |
| 49 Group Anagrams | 상태/포인터 유지 | 경계 인덱스 처리 |
| 28 Find the Index of the First Occurrence | 자료구조 선택 | 복잡도 목표 미달 |

문제 매핑의 목적은 정답 암기가 아닙니다. 같은 구조를 빠르게 인식하고, "왜 이 패턴을 쓰는가"를 재현하는 데 있습니다. 시리즈 전체를 관통하는 실력 차이는 여기서 발생합니다.

### 5) 비교 벤치마크를 읽는 기준

| 비교 항목 | A 접근 | B 접근 | 의사결정 기준 |
| --- | --- | --- | --- |
| 시간 | 평균적으로 빠름 | 최악 케이스 안정적 | 입력 분포가 고정인지 |
| 메모리 | 추가 배열 필요 | 제자리 처리 가능 | 메모리 제한 강도 |
| 구현 난이도 | 짧음 | 디버깅 난이도 높음 | 팀 유지보수 역량 |

벤치마크 숫자는 환경에 따라 달라집니다. 하지만 차수와 메모리 계층에서 발생하는 방향성은 반복됩니다. 그래서 한 번 측정한 결과를 절대값으로 외우기보다, 어떤 조건에서 우위가 바뀌는지(입력 크기, 정렬 여부, 중복 비율)를 함께 기록해야 다음 의사결정에 도움이 됩니다.

### 6) 제출/배포 전 점검 루틴

1. 문제 제약을 한 줄로 요약하고 불가능한 차수를 먼저 제거합니다.
2. 핵심 자료구조 선택 이유를 "삽입/조회/삭제 비용" 기준으로 적습니다.
3. 경계 입력 3종(빈값, 최소값, 중복/극단값) 테스트를 고정합니다.
4. 시간·공간 복잡도를 코드 옆에 기록하고, 실제 측정값을 짧게 남깁니다.
5. 같은 패턴의 변형 문제를 1개 더 풀어 일반화 여부를 확인합니다.

이 루틴을 꾸준히 적용하면 "이번 문제를 맞춤"에서 끝나지 않고 "같은 유형을 안정적으로 재현"하는 상태로 넘어갈 수 있습니다. 알고리즘 학습은 지식 축적이 아니라 판단 체계 구축이라는 점을 계속 기억하는 것이 중요합니다.

## 처음 질문으로 돌아가기

- **단순 매칭은 왜 최악에 O(nm)까지 갈까요?**
  - `text = "a" * 100000 + "b"`와 `pat = "a" * 1000 + "b"`처럼 반복 패턴이 있으면 시작 위치마다 거의 m번 비교하게 되기 때문입니다. 본문의 `naive_match()` 실험이 보여 준 것은 바로 이 “거의 다 맞다가 마지막에 틀리는” 최악 경우입니다.
- **KMP의 실패 함수는 어떤 직관으로 이해해야 할까요?**
  - `compute_failure("ababaca")`가 주는 배열은 불일치가 났을 때 패턴 포인터 `j`를 어디로 되돌릴지 미리 적어 둔 표입니다. 그래서 KMP는 텍스트를 다시 뒤로 물리지 않고도 `j = fail[j - 1]`만으로 O(n+m)을 유지합니다.
- **트라이는 어떤 문제에서 특히 강할까요?**
  - `Trie.starts_with("car")`처럼 접두사 공유가 핵심인 자동완성, prefix 검색, 다중 패턴 전처리에서 강합니다. 본문 예제에서 `car`, `card`, `care`, `cargo`가 한 구조를 공유하는 모습이 바로 그 장점을 압축해 보여 줍니다.

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

- [book-examples — algorithms-101/ko](https://github.com/yeongseon-books/book-examples/tree/main/algorithms-101/ko)
- [Python `re` documentation](https://docs.python.org/3/library/re.html)
- [Wikipedia — Knuth-Morris-Pratt algorithm](https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm)
- [Wikipedia — Aho-Corasick algorithm](https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm)
- [OWASP — Regular expression Denial of Service](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS)

Tags: Computer Science, 알고리즘, 문자열, KMP, Trie, Regex
