---
title: "LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기"
series: llm-from-scratch-101
episode: 1
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- LLM
- PyTorch
- Transformer
- Tutorial
last_reviewed: '2026-05-12'
seo_description: 처음 LLM 코드를 뜯어볼 때 가장 낯설었던 장면은 모델이 문장을 전혀 읽지 못한다는 사실이었습니다.
---

# LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기

토크나이저는 너무 앞단에 있어서 가볍게 지나가기 쉽습니다. 하지만 언어 모델 관점에서 토크나이저는 입력 포맷을 정하는 핵심 계약입니다. 어떤 조각을 하나의 토큰으로 볼지 결정하는 순간, 모델이 학습해야 할 통계 구조도 함께 정해집니다.

이 글은 LLM from Scratch 101 시리즈의 첫 번째 글입니다.

LLM을 처음 배울 때 가장 먼저 생기는 오해는 모델이 문장을 그대로 읽는다는 생각입니다. 프롬프트 창에 텍스트를 넣고 답을 받다 보면, 모델이 글자를 문자 그대로 이해하고 있다고 느끼기 쉽습니다. 하지만 모델 내부로 들어가 보면 사정은 완전히 다릅니다.

신경망이 실제로 받는 것은 문자열이 아니라 정수 배열입니다. 우리가 보는 `Hello`는 모델에게는 토큰 ID 시퀀스일 뿐이고, 그 시퀀스가 없으면 임베딩도 어텐션도 시작할 수 없습니다. 이 출발점을 정확히 잡지 못하면 이후 모든 개념이 조금씩 공중에 뜹니다.

그래서 토크나이저는 단순한 전처리 단계가 아닙니다. 텍스트를 정수로 바꾸는 계약이자, 모델이 세상을 읽는 문자 체계입니다. 같은 문장이라도 토크나이저가 달라지면 전혀 다른 숫자 흐름이 만들어지고, 그 차이는 곧 모델 자체의 차이로 이어집니다.

이번 글에서는 가장 단순한 문자 단위 토큰화부터 출발해, 왜 서브워드가 실전에서 널리 쓰이는지, 그리고 왜 이 시리즈는 일부러 char-level 방식을 택하는지를 차근차근 정리하겠습니다.

![LLM from Scratch 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/01/01-01-vs.ko.png)
*LLM from Scratch 101 1장 흐름 개요*

## 이 글에서 다룰 문제

- 모델은 왜 문자열 대신 정수 시퀀스를 입력으로 받아야 할까요?
- 문자 단위, 단어 단위, 서브워드 토큰화는 각각 무엇을 얻고 무엇을 잃을까요?
- BPE는 실제로 어떤 식으로 어휘를 조금씩 키워 갈까요?
- vocab 밖 문자를 잘못 다루면 어떤 장애가 생길까요?
- 이 시리즈가 char-level을 택한 이유는 무엇일까요?

## 왜 이 글이 중요한가

토크나이저는 너무 앞단에 있어서 가볍게 지나가기 쉽습니다. 하지만 언어 모델 관점에서 토크나이저는 입력 포맷을 정하는 핵심 계약입니다. 어떤 조각을 하나의 토큰으로 볼지 결정하는 순간, 모델이 학습해야 할 통계 구조도 함께 정해집니다.

실무에서도 이 지점은 꽤 중요합니다. 토크나이저를 바꾸면 같은 문장이 다른 길이의 시퀀스로 변하고, 기존 임베딩 행렬과 체크포인트는 그대로 재사용할 수 없게 됩니다. 겉으로는 전처리 교체처럼 보여도 실제로는 모델 호환성을 깨는 변경인 경우가 많습니다.

무엇보다 이 글은 시리즈의 나머지 여덟 편을 읽기 위한 기초를 만듭니다. 임베딩은 토큰 ID를 벡터로 바꾸는 단계이고, 어텐션은 그 벡터들이 서로를 참조하는 단계이며, 학습은 그 전체 파이프라인의 숫자를 조정하는 단계입니다.

## 핵심 관점

토크나이저를 "문장을 잘게 자르는 도구" 정도로만 보면 중요성이 과소평가됩니다. 더 정확한 표현은 이렇습니다. **토크나이저는 사람이 읽는 문자열을 모델이 처리할 수 있는 정수 시퀀스로 바꾸는 엄격한 계약**입니다. 이 계약이 바뀌면 같은 데이터셋도 다른 학습 문제로 바뀝니다.

문자 단위 토큰화는 이 계약을 가장 투명하게 보여 줍니다. 각 글자에 번호를 붙이고, 문자열을 그 번호열로 바꿉니다. 단순해 보이지만 바로 이 단순함 덕분에 모델이 실제로 무엇을 보고 있는지 추적하기 쉬워집니다. 101 단계에서는 이 투명성이 성능보다 더 큰 장점입니다.

> 이 글에서 기억해야 할 핵심은 하나입니다. 모델은 텍스트를 읽지 않습니다. 토크나이저가 정의한 규칙에 따라 만들어진 정수 시퀀스만 읽습니다.

## 토큰화 방식 아키텍처 비교

```
텍스트: "hello world"

[문자 단위 tokenizer]
h -> 0
e -> 1
l -> 2
l -> 2
o -> 3
  -> 4 (공백)
w -> 5
o -> 3
r -> 6
l -> 2
d -> 7

IDs: [0, 1, 2, 2, 3, 4, 5, 3, 6, 2, 7]  길이=11

[단어 단위 tokenizer]
hello -> 0
world -> 1

IDs: [0, 1]  길이=2

[서브워드 BPE tokenizer - tiktoken/gpt2]
hell -> 7673
o    -> 78
wor  -> 1818
ld   -> 1086

IDs: [7673, 78, 1818, 1086]  길이=4
```

길이가 11 → 2 → 4로 달라지는 것만으로도 학습 비용, 메모리, attention 계산량이 전부 달라집니다.

## 핵심 개념

### 텍스트를 바로 넣을 수 없는 이유

신경망은 텐서 연산기로 동작합니다. 문자열에는 덧셈이나 행렬 곱을 바로 적용할 수 없기 때문에, 먼저 각 문자나 조각을 정수 ID로 바꿔야 합니다. 여기서 중요한 점은 토큰 ID 자체에는 의미가 없다는 사실입니다. 의미는 이후 임베딩 단계에서 학습됩니다.

토큰 ID를 단순 인덱스로 이해하면 이후 구조가 깔끔해집니다. 토크나이저는 텍스트를 번호표로 바꾸고, 임베딩은 그 번호표에 벡터 표현을 부여하며, 모델은 그 벡터 사이의 패턴을 학습합니다.

### 가장 단순한 출발점: 문자 단위 토큰화

문자 단위 토큰화의 장점은 구현이 짧고 디버깅이 쉽다는 사실입니다. 입력 문자열을 구성하는 문자 집합을 모은 뒤, 각 문자에 정수를 붙이면 됩니다.

```python
text = "hello world"
chars = sorted(set(text))
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}

print(f"vocab: {chars}")
print(f"vocab_size: {len(chars)}")
# vocab: [' ', 'd', 'e', 'h', 'l', 'o', 'r', 'w']
# vocab_size: 8

def encode(s: str) -> list[int]:
    dropped = sorted({c for c in s if c not in stoi})
    if dropped:
        print(f"[WARNING] dropped unsupported characters: {dropped}")
    return [stoi[c] for c in s if c in stoi]

def decode(ids: list[int]) -> str:
    return "".join(itos[i] for i in ids)

ids = encode(text)
print(ids)           # [3, 2, 4, 4, 5, 0, 7, 5, 6, 4, 1]
print(decode(ids))   # hello world
```

이 코드를 한 번 실행해 보면 문자열이 어떻게 정수 배열로 바뀌고, 다시 어떻게 원래 텍스트로 복원되는지 감각이 바로 잡힙니다.

### 문자 단위 vs 서브워드: 트레이드오프 표

| 방식 | vocab 크기 | 시퀀스 길이 | OOV 처리 | 투명성 | 실전 효율 |
| --- | --- | --- | --- | --- | --- |
| char-level | 매우 작음(~65) | 매우 길음 | 없음(byte 포함 시) | 매우 높음 | 낮음 |
| word-level | 폭발적(>100k) | 짧음 | OOV 문제 큼 | 중간 | 가변적 |
| BPE/서브워드 | 중간(8k~50k) | 중간 | 강건 | 중간 | 높음 |
| byte-level | 256 | 가장 길음 | 완전 강건 | 높음 | 중간 |

이 시리즈는 char-level을 선택합니다. 성능보다 구조 투명성이 우선이기 때문입니다.

### BPE: 자주 나오는 조각을 반복 병합하는 방식

BPE(Byte Pair Encoding)의 핵심 아이디어는 소박합니다. 가장 자주 함께 등장하는 문자 쌍이나 조각 쌍을 반복적으로 합쳐 더 긴 토큰으로 승격하는 방식입니다.

```python
# BPE의 핵심 알고리즘 스케치
def get_stats(vocab: dict[str, int]) -> dict[tuple, int]:
    """단어 내 인접 쌍의 빈도를 계산합니다."""
    pairs: dict[tuple, int] = {}
    for word, freq in vocab.items():
        symbols = word.split()
        for i in range(len(symbols) - 1):
            pair = (symbols[i], symbols[i + 1])
            pairs[pair] = pairs.get(pair, 0) + freq
    return pairs

def merge_vocab(pair: tuple, vocab: dict[str, int]) -> dict[str, int]:
    """가장 빈번한 쌍을 하나의 심볼로 합칩니다."""
    bigram = " ".join(pair)
    replacement = "".join(pair)
    new_vocab = {}
    for word, freq in vocab.items():
        new_word = word.replace(bigram, replacement)
        new_vocab[new_word] = freq
    return new_vocab

# 예시: 초기 vocab
vocab = {
    "l o w </w>": 5,
    "l o w e r </w>": 2,
    "n e w e s t </w>": 6,
    "w i d e s t </w>": 3,
}

for i in range(5):
    pairs = get_stats(vocab)
    best = max(pairs, key=pairs.get)
    vocab = merge_vocab(best, vocab)
    print(f"step {i+1}: merge {best} -> {''.join(best)}")

# step 1: merge ('e', 's') -> es
# step 2: merge ('es', 't') -> est
# step 3: merge ('est', '</w>') -> est</w>
# step 4: merge ('l', 'o') -> lo
# step 5: merge ('lo', 'w') -> low
```

`low`, `lower`, `lowest` 같은 단어에서 `lo`, `low` 같은 조합이 점차 하나의 어휘 항목이 됩니다.

### GPT-2 스타일 토크나이저와 직접 비교

```python
import tiktoken

enc = tiktoken.get_encoding("gpt2")
text = "Hello, tokenizer! 안녕하세요."

ids = enc.encode(text)
decoded = enc.decode(ids)

print(f"ids: {ids}")
print(f"decoded: {decoded}")
print(f"char-level length: {len(text)}")
print(f"bpe length:        {len(ids)}")

# 비율 계산
print(f"compression ratio: {len(text)/len(ids):.2f}x")

# 토큰별 텍스트 확인
for token_id in ids:
    print(repr(enc.decode([token_id])), end=" ")
```

같은 문자열도 토큰 분할 방식이 달라지면 완전히 다른 ID 배열이 만들어진다는 점을 눈으로 확인할 수 있습니다.

### 토큰 길이 분포 분석

토크나이저 선택은 결국 시퀀스 길이 분포를 바꿉니다. 시퀀스가 길어지면 attention 계산량이 `T^2`로 늘고, 같은 GPU 메모리에서 batch size를 줄여야 합니다.

```python
import numpy as np

samples = [
    "To be, or not to be, that is the question.",
    "What light through yonder window breaks?",
    "O Romeo, Romeo! wherefore art thou Romeo?",
    "All the world's a stage, and all the men and women merely players.",
]

# char-level 길이
char_lengths = [len(s) for s in samples]
print("char-level lengths:", char_lengths)
print("mean:", float(np.mean(char_lengths)))
print("p95:", float(np.percentile(char_lengths, 95)))

# BPE 길이 (tiktoken)
import tiktoken
enc = tiktoken.get_encoding("gpt2")
bpe_lengths = [len(enc.encode(s)) for s in samples]
print("\nbpe lengths:", bpe_lengths)
print("mean:", float(np.mean(bpe_lengths)))
print("p95:", float(np.percentile(bpe_lengths, 95)))

# 압축률
for s, cl, bl in zip(samples, char_lengths, bpe_lengths):
    print(f"ratio={cl/bl:.2f}x | {s[:40]}")
```

char-level에서는 평균 길이가 길게 나오지만, 그만큼 디버깅 가시성이 높습니다.

## TinyShakespeare 데이터셋 준비: `data.py`

이제 이 시리즈의 첫 코드 파일인 `data.py`를 작성합니다. 이 스크립트는 TinyShakespeare를 다운로드하고, 문자 vocab을 만들고, 학습용/검증용 바이너리 파일을 저장합니다.

```python
# data.py
from pathlib import Path
from urllib.request import urlretrieve

import numpy as np

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

input_file = DATA_DIR / "tinyshakespeare.txt"
if not input_file.exists():
    print("Downloading TinyShakespeare...")
    urlretrieve(
        "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt",
        input_file,
    )
    print(f"Downloaded: {input_file.stat().st_size / 1024:.1f} KB")

text = input_file.read_text(encoding="utf-8")
print(f"Total characters: {len(text):,}")

# vocab 구성
chars = sorted(set(text))
vocab_size = len(chars)
print(f"Unique characters: {vocab_size}")
print(f"Vocab sample: {chars[:20]}")

stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}

def encode(s: str) -> list[int]:
    dropped = sorted({c for c in s if c not in stoi})
    if dropped:
        print(f"[WARNING] dropped unsupported characters: {dropped}")
    return [stoi[c] for c in s if c in stoi]

def decode(ids: list[int]) -> str:
    return "".join(itos[i] for i in ids)

# 학습/검증 분할 (90/10)
data = np.array(encode(text), dtype=np.uint16)
n = int(0.9 * len(data))
train_ids = data[:n]
val_ids = data[n:]

(DATA_DIR / "train.bin").write_bytes(train_ids.tobytes())
(DATA_DIR / "val.bin").write_bytes(val_ids.tobytes())

print(f"\nvocab_size={vocab_size}")
print(f"train tokens: {len(train_ids):,}")
print(f"val tokens:   {len(val_ids):,}")
print(f"\nFirst 80 chars of train set:")
print(decode(train_ids[:80].tolist()))
```

실행 예시:

```text
Downloading TinyShakespeare...
Downloaded: 1115.4 KB
Total characters: 1,115,394
Unique characters: 65
Vocab sample: ['\n', ' ', '!', '$', '&', "'", ',', '-', '.', '3', ':', ';', '?', 'A', 'B', 'C', 'D', 'E', 'F', 'G']

vocab_size=65
train tokens: 1,003,854
val tokens:   111,540

First 80 chars of train set:
First Citizen:
Before we proceed any further, hear me speak.

All:
Speak, speak.
```

이 파일이 중요한 이유는 단순히 데이터를 내려받기 때문이 아닙니다. 이후 모든 글에서 사용할 입력 계약을 여기서 확정하기 때문입니다.

## BPE 토크나이저 학습 스크립트 (선택 사항)

char-level을 교육용 기본값으로 쓰더라도, 실제 프로젝트에서는 "어휘를 어떻게 만들었는가"를 코드로 남겨 두는 편이 안전합니다.

```python
# train_tokenizer.py (선택 사항 - char-level 시리즈에서는 사용 안 함)
from pathlib import Path

from tokenizers import Tokenizer, models, normalizers, pre_tokenizers, trainers

def train_bpe_tokenizer(corpus_path: str, out_dir: str, vocab_size: int = 8000) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    tokenizer = Tokenizer(models.BPE(unk_token="<unk>"))
    tokenizer.normalizer = normalizers.Sequence([
        normalizers.NFKC(),
        normalizers.StripAccents(),
    ])
    tokenizer.pre_tokenizer = pre_tokenizers.ByteLevel(add_prefix_space=False)

    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=2,
        special_tokens=["<pad>", "<unk>", "<bos>", "<eos>"],
    )
    tokenizer.train([corpus_path], trainer)

    # 재현성을 위해 vocab/merge 파일 저장
    tokenizer.model.save(str(out), "tokenizer")
    tokenizer.save(str(out / "tokenizer.json"))
    print(f"Saved tokenizer to {out}")

# train_bpe_tokenizer("data/tinyshakespeare.txt", "artifacts/tokenizer", vocab_size=2000)
```

특히 `special_tokens` 순서를 바꾸면 ID 매핑이 달라지고, 그 순간부터 기존 체크포인트와 비호환이 됩니다.

## 토크나이저 메타데이터 고정

실험 재현성을 위해 토크나이저 메타데이터를 함께 기록합니다.

```json
{
  "tokenizer_type": "char",
  "vocab_size": 65,
  "normalization": "none",
  "special_tokens": [],
  "train_corpus_sha256": "8d1f...",
  "created_at": "2026-05-21T11:10:00Z"
}
```

이 메타데이터가 있으면 "모델이 갑자기 이상해졌다"는 문제를 만났을 때, 모델 구조보다 먼저 입력 계약 변경 여부를 확인할 수 있습니다.

## 흔히 나타나는 실패 패턴

### vocab 밖 문자가 조용히 손실될 때

```python
# 위험한 패턴: 경고 없이 드롭
ids = [stoi[c] for c in text]  # KeyError 가능

# 안전한 패턴: 경고 출력 후 드롭
def encode_safe(s: str) -> list[int]:
    dropped = [c for c in s if c not in stoi]
    if dropped:
        print(f"[WARNING] dropped {len(dropped)} chars: {sorted(set(dropped))}")
    return [stoi[c] for c in s if c in stoi]

# 테스트
test = "Hello 안녕! 🎉"
ids = encode_safe(test)
# [WARNING] dropped 5 chars: [' ', '!', '🎉', '안', '녕']
# (위 chars는 영문 이외의 문자가 vocab에 없을 경우 예시)
```

### 토크나이저 불일치로 체크포인트가 호환 안 될 때

```python
# 체크포인트 저장 시 토크나이저 정보도 함께
import json
import torch

checkpoint = {
    "model": model.state_dict(),
    "config": asdict(config),
    "tokenizer": {
        "type": "char",
        "vocab_size": vocab_size,
        "stoi": stoi,
        "itos": itos,
    },
}
torch.save(checkpoint, "ckpt.pt")

# 로드 시 검증
ckpt = torch.load("ckpt.pt")
assert ckpt["tokenizer"]["vocab_size"] == config.vocab_size, \
    f"tokenizer vocab_size mismatch: {ckpt['tokenizer']['vocab_size']} vs {config.vocab_size}"
```

### train/val 토크나이저가 다를 때

```python
# 잘못된 패턴: val 데이터에서 vocab을 다시 만들면 안 됨
val_text = Path("data/val.txt").read_text()
val_chars = sorted(set(val_text))  # 위험! train vocab과 다를 수 있음

# 올바른 패턴: train에서 만든 stoi/itos를 그대로 사용
val_ids = np.array(encode(val_text), dtype=np.uint16)  # train의 encode() 사용
```

## 운영 체크리스트

- [ ] 현재 모델이 어떤 토크나이저 계약을 전제로 학습됐는지 설명할 수 있는가
- [ ] vocab 밖 문자 처리 방식(drop, unknown, byte fallback 등)을 명시했는가
- [ ] 같은 문장을 char-level과 BPE로 각각 인코딩해 길이 차이를 확인했는가
- [ ] `encode()`와 `decode()`를 모두 유지해 숫자 ↔ 문자 복원을 검증할 수 있는가
- [ ] 학습 데이터셋을 `train.bin`과 `val.bin` 같은 재현 가능한 산출물로 고정했는가
- [ ] 체크포인트에 토크나이저 메타데이터(vocab_size, stoi 등)를 함께 저장했는가

## 한 줄 결론

토크나이저는 전처리 도구가 아니라 모델의 문자 체계입니다. 이 체계를 고정하고 버전 관리하는 순간, 이후 단계의 실험 품질이 안정됩니다.

## 정리

이번 글에서는 모델이 텍스트를 직접 읽지 않고, 토크나이저가 만든 정수 시퀀스를 입력으로 받는다는 가장 중요한 출발점을 정리했습니다. 이 관점 하나만 분명해져도 LLM의 내부 구조가 훨씬 덜 신비롭게 보입니다.

또한 문자 단위, 단어 단위, 서브워드 토큰화가 무엇을 교환하는지도 살펴봤습니다. char-level은 길지만 투명하고, 서브워드는 효율적이지만 구조가 더 복잡합니다. 이번 시리즈가 char-level을 택한 이유도 바로 이 투명성에 있습니다.

이제 다음 글로 넘어가면 이 정수 ID들에 벡터 의미를 부여하게 됩니다. 즉, 토크나이저가 만든 숫자열이 임베딩을 거쳐 모델이 실제로 다룰 수 있는 표현 공간으로 들어가게 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- **LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기 (현재 글)**
- LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치 (예정)
- LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기 (예정)
- LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위 (예정)
- LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성 (예정)
- LLM from Scratch 101 (6/9): 기울기로 배우기 (예정)
- LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기 (예정)
- LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기 (예정)
- LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Karpathy minBPE](https://github.com/karpathy/minbpe)
- [OpenAI tiktoken](https://github.com/openai/tiktoken)
- [Language Models are Unsupervised Multitask Learners (GPT-2)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
- [Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909)

### 관련 시리즈

- [LLM 앱 기초 — 토큰 이해하기](../../llm-app-foundations-101/ko/02-understanding-tokens.md)
- [Vector Search 101 — 임베딩이 필요한 이유](../../vector-search-101/ko/01-what-is-embedding.md)
- [LangChain 101 — Prompt와 LLM Chain](../../langchain-101/ko/02-prompt-llm-chain.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/llm-from-scratch-101/ko/01-tokenizer)

Tags: LLM, PyTorch, Transformer, Tutorial
