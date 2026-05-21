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

이 글은 LLM from Scratch 101 시리즈의 첫 번째 글입니다.

LLM을 처음 배울 때 가장 먼저 생기는 오해는 모델이 문장을 그대로 읽는다는 생각입니다. 프롬프트 창에 텍스트를 넣고 답을 받다 보면, 모델이 글자를 문자 그대로 이해하고 있다고 느끼기 쉽습니다. 하지만 모델 내부로 들어가 보면 사정은 완전히 다릅니다.

신경망이 실제로 받는 것은 문자열이 아니라 정수 배열입니다. 우리가 보는 `Hello`는 모델에게는 토큰 ID 시퀀스일 뿐이고, 그 시퀀스가 없으면 임베딩도 어텐션도 시작할 수 없습니다. 이 출발점을 정확히 잡지 못하면 이후 모든 개념이 조금씩 공중에 뜹니다.

그래서 토크나이저는 단순한 전처리 단계가 아닙니다. 텍스트를 정수로 바꾸는 계약이자, 모델이 세상을 읽는 문자 체계입니다. 같은 문장이라도 토크나이저가 달라지면 전혀 다른 숫자 흐름이 만들어지고, 그 차이는 곧 모델 자체의 차이로 이어집니다.

이번 글에서는 가장 단순한 문자 단위 토큰화부터 출발해, 왜 서브워드가 실전에서 널리 쓰이는지, 그리고 왜 이 시리즈는 일부러 char-level 방식을 택하는지를 차근차근 정리하겠습니다.

이제 텍스트가 어떻게 숫자가 되는지만 제대로 잡으면 이후 임베딩과 어텐션을 훨씬 덜 신비롭게 볼 수 있습니다.

![LLM from Scratch 101 1장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/01/01-01-vs.ko.png)
*LLM from Scratch 101 1장 흐름 개요*

## 먼저 던지는 질문

- 모델은 왜 문자열 대신 정수 시퀀스를 입력으로 받아야 할까요?
- 문자 단위, 단어 단위, 서브워드 토큰화는 각각 무엇을 얻고 무엇을 잃을까요?
- BPE는 실제로 어떤 식으로 어휘를 조금씩 키워 갈까요?

## 왜 이 글이 중요한가

토크나이저는 너무 앞단에 있어서 가볍게 지나가기 쉽습니다. 하지만 언어 모델 관점에서 토크나이저는 입력 포맷을 정하는 핵심 계약입니다. 어떤 조각을 하나의 토큰으로 볼지 결정하는 순간, 모델이 학습해야 할 통계 구조도 함께 정해집니다.

실무에서도 이 지점은 꽤 중요합니다. 토크나이저를 바꾸면 같은 문장이 다른 길이의 시퀀스로 변하고, 기존 임베딩 행렬과 체크포인트는 그대로 재사용할 수 없게 됩니다. 겉으로는 전처리 교체처럼 보여도 실제로는 모델 호환성을 깨는 변경인 경우가 많습니다.

무엇보다 이 글은 시리즈의 나머지 여덟 편을 읽기 위한 기초를 만듭니다. 임베딩은 토큰 ID를 벡터로 바꾸는 단계이고, 어텐션은 그 벡터들이 서로를 참조하는 단계이며, 학습은 그 전체 파이프라인의 숫자를 조정하는 단계입니다. 토큰 ID가 어떻게 만들어지는지 모르면 뒤 개념들을 정확히 연결하기 어렵습니다.

## 핵심 관점

토크나이저를 "문장을 잘게 자르는 도구" 정도로만 보면 중요성이 과소평가됩니다. 더 정확한 표현은 이렇습니다. **토크나이저는 사람이 읽는 문자열을 모델이 처리할 수 있는 정수 시퀀스로 바꾸는 엄격한 계약**입니다. 이 계약이 바뀌면 같은 데이터셋도 다른 학습 문제로 바뀝니다.

문자 단위 토큰화는 이 계약을 가장 투명하게 보여 줍니다. 각 글자에 번호를 붙이고, 문자열을 그 번호열로 바꿉니다. 단순해 보이지만 바로 이 단순함 덕분에 모델이 실제로 무엇을 보고 있는지 추적하기 쉬워집니다. 101 단계에서는 이 투명성이 성능보다 더 큰 장점입니다.

반대로 실전형 서브워드 토크나이저는 더 압축된 표현을 제공하는 대신, 내부 동작이 눈에 덜 들어옵니다. 그래서 입문 단계에서는 먼저 가장 단순한 계약을 이해하고, 그다음에 더 복잡한 토크나이저가 왜 필요한지 올라가는 편이 훨씬 안정적입니다.

> 이 글에서 기억해야 할 핵심은 하나입니다. 모델은 텍스트를 읽지 않습니다. 토크나이저가 정의한 규칙에 따라 만들어진 정수 시퀀스만 읽습니다.

## 핵심 개념

### 텍스트를 바로 넣을 수 없는 이유

신경망은 텐서 연산기로 동작합니다. 문자열에는 덧셈이나 행렬 곱을 바로 적용할 수 없기 때문에, 먼저 각 문자나 조각을 정수 ID로 바꿔야 합니다. 여기서 중요한 점은 토큰 ID 자체에는 의미가 없다는 사실입니다. 의미는 이후 임베딩 단계에서 학습됩니다.

토큰 ID를 단순 인덱스로 이해하면 이후 구조가 깔끔해집니다. 토크나이저는 텍스트를 번호표로 바꾸고, 임베딩은 그 번호표에 벡터 표현을 부여하며, 모델은 그 벡터 사이의 패턴을 학습합니다. 의미를 앞단에 억지로 넣는 것이 아니라, 뒤에서 점진적으로 형성하는 구조입니다.

### 가장 단순한 출발점은 문자 단위 토큰화입니다

문자 단위 토큰화의 장점은 구현이 짧고 디버깅이 쉽다는 점입니다. 입력 문자열을 구성하는 문자 집합을 모은 뒤, 각 문자에 정수를 붙이면 됩니다. 다음 코드는 그 핵심을 가장 직접적으로 보여 줍니다.

```python
text = "hello world"
chars = sorted(set(text))
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}

def encode(s: str) -> list[int]:
    dropped = sorted({c for c in s if c not in stoi})
    if dropped:
        print(f"dropped unsupported characters: {dropped}")
    return [stoi[c] for c in s if c in stoi]

decode = lambda ids: "".join(itos[i] for i in ids)

ids = encode(text)
print(ids)
print(decode(ids))
```

이 코드를 한 번 실행해 보면 문자열이 어떻게 정수 배열로 바뀌고, 다시 어떻게 원래 텍스트로 복원되는지 감각이 바로 잡힙니다. 또한 지원하지 않는 문자가 경고와 함께 드롭된다는 점도 중요한 운영 포인트입니다. vocab 밖 문자를 어떻게 다룰지는 토크나이저 설계의 일부이기 때문입니다.

### 문자 단위와 서브워드 사이에는 분명한 트레이드오프가 있습니다

문자 단위는 어휘 수가 작고 투명하지만 시퀀스가 길어집니다. 반대로 단어 단위는 시퀀스가 짧아지지만 어휘가 폭발하고 OOV 문제가 커집니다. 실전 모델이 서브워드를 선호하는 이유는 바로 이 중간 지점을 노릴 수 있기 때문입니다.

이 그림을 볼 때 중요한 포인트는 "어느 방식이 절대적으로 더 좋다"가 아닙니다. 데이터 규모, 목표 작업, 컨텍스트 길이, 구현 복잡도에 따라 최적점이 달라집니다. 이번 시리즈는 학습용 소형 GPT를 직접 구현하는 것이 목적이므로, 성능보다 구조 투명성이 더 중요합니다.

### BPE는 자주 함께 등장하는 조각을 반복해서 합치는 방식입니다

BPE가 처음에는 복잡해 보일 수 있지만, 핵심 아이디어는 소박합니다. 가장 자주 함께 등장하는 문자 쌍이나 조각 쌍을 반복적으로 합쳐 더 긴 토큰으로 승격하는 방식입니다. 즉, 자주 나오는 패턴에 더 짧은 표현을 주는 통계적 압축 전략에 가깝습니다.

`low`, `lower`, `lowest` 같은 예시를 떠올리면 직관적입니다. 처음에는 문자 단위로 시작하지만, 빈도가 높은 `l + o`, `lo + w` 같은 조합이 점차 하나의 어휘 항목이 됩니다. 그래서 자주 나오는 패턴은 더 짧은 시퀀스로 표현되고, 처음 보는 단어도 여전히 더 작은 조각들로 분해해서 처리할 수 있습니다.

### 실제 GPT-2 스타일 토크나이저도 직접 확인해 볼 수 있습니다

직접 구현한 char-level 예제와 실전형 토크나이저의 차이를 비교하려면 `tiktoken`이 좋습니다. 같은 문자열도 토큰 분할 방식이 달라지면 완전히 다른 ID 배열이 만들어진다는 점을 눈으로 확인할 수 있습니다.

```python
import tiktoken

enc = tiktoken.get_encoding("gpt2")
text = "Hello, tokenizer!"

ids = enc.encode(text)
decoded = enc.decode(ids)

print(ids)
print(decoded)
```

이 비교는 단순한 호기심용이 아닙니다. 같은 문장을 어떤 단위로 쪼개느냐에 따라 컨텍스트 길이, 학습 난이도, 추론 비용이 달라진다는 점을 가장 빠르게 체감하게 해 줍니다.

### 이번 시리즈는 의도적으로 char-level을 선택합니다

실전 서비스 관점에서는 서브워드가 더 일반적입니다. 하지만 이 시리즈는 TinyShakespeare 위에서 소형 GPT를 처음부터 끝까지 직접 구현하는 것이 목표입니다. 문자 수가 약 65개 수준이면 vocab이 작고, 마지막 softmax도 가볍고, 디버깅할 때 `decode()`로 쉽게 원문을 복원할 수 있습니다.

즉, 이번 선택은 성능 최적화가 아니라 교육용 최적화입니다. 처음 세 편에서는 "빠르고 강한 모델"보다 "구조를 끝까지 추적할 수 있는 모델"이 더 좋은 교재입니다.

### TinyShakespeare를 정수 데이터셋으로 바꾸는 첫 파일을 만듭니다

이제 이 시리즈의 첫 코드 파일인 `data.py`를 작성합니다. 이 스크립트는 TinyShakespeare를 다운로드하고, 문자 vocab을 만들고, 학습용/검증용 바이너리 파일을 저장합니다.

```python
from pathlib import Path
from urllib.request import urlretrieve

import numpy as np

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

input_file = DATA_DIR / "tinyshakespeare.txt"
if not input_file.exists():
    urlretrieve(
        "https://raw.githubusercontent.com/karpathy/char-rnn/master/data/tinyshakespeare/input.txt",
        input_file,
    )

text = input_file.read_text(encoding="utf-8")
chars = sorted(set(text))
vocab_size = len(chars)

stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}

def encode(s: str) -> list[int]:
    dropped = sorted({c for c in s if c not in stoi})
    if dropped:
        print(f"dropped unsupported characters: {dropped}")
    return [stoi[c] for c in s if c in stoi]

def decode(ids: list[int]) -> str:
    return "".join(itos[i] for i in ids)

data = np.array(encode(text), dtype=np.uint16)
n = int(0.9 * len(data))
train_ids = data[:n]
val_ids = data[n:]

(DATA_DIR / "train.bin").write_bytes(train_ids.tobytes())
(DATA_DIR / "val.bin").write_bytes(val_ids.tobytes())

print(f"vocab_size={vocab_size}, train={len(train_ids)}, val={len(val_ids)}")
print(decode(train_ids[:80].tolist()))
```

이 파일이 중요한 이유는 단순히 데이터를 내려받기 때문이 아닙니다. 이후 모든 글에서 사용할 입력 계약을 여기서 확정하기 때문입니다. `train.bin`과 `val.bin`은 이제 모델이 실제로 읽게 될 정수 데이터셋입니다.

## 흔히 헷갈리는 지점

- 토큰 ID가 의미를 담고 있다고 생각하기 쉽지만, 실제 의미는 이후 임베딩 벡터에 학습됩니다.
- 토크나이저를 모델 바깥 전처리로만 보지만, 체크포인트 호환성까지 좌우하므로 사실상 모델의 일부입니다.
- 문자 단위가 단순하니 낡은 방식이라고 여기기 쉽지만, 교육용·디버깅용으로는 매우 강력합니다.
- BPE를 복잡한 마법으로 느끼기 쉽지만, 자주 나오는 조각을 반복 병합하는 통계적 절차에 가깝습니다.
- vocab 밖 문자를 무시하는 동작을 사소하게 넘기기 쉽지만, 실제 서비스에서는 입력 손실과 품질 저하로 바로 이어질 수 있습니다.

## 운영 체크리스트

- [ ] 현재 모델이 어떤 토크나이저 계약을 전제로 학습됐는지 설명할 수 있는가
- [ ] vocab 밖 문자 처리 방식(drop, unknown, byte fallback 등)을 명시했는가
- [ ] 같은 문장을 char-level과 BPE로 각각 인코딩해 길이 차이를 확인했는가
- [ ] `encode()`와 `decode()`를 모두 유지해 숫자↔문자 복원을 검증할 수 있는가
- [ ] 학습 데이터셋을 `train.bin`과 `val.bin` 같은 재현 가능한 산출물로 고정했는가

## 실험 재현성을 위한 토크나이저 고정 원칙

LLM 실험에서 같은 코드인데 결과가 달라지는 대표 원인 중 하나가 토크나이저 불일치입니다. 그래서 최소한 vocab 파일, special token 정의, 전처리 규칙을 체크포인트와 함께 버전으로 묶어 두는 습관이 중요합니다.

토크나이저를 고정해 두면 학습 곡선 비교가 정직해집니다. 모델 구조를 바꾼 영향인지, 입력 분해 방식이 바뀐 영향인지 분리해서 읽을 수 있기 때문입니다.

## 토크나이저 학습 스크립트를 직접 두면 바뀌는 점

char-level을 교육용 기본값으로 쓰더라도, 실제 프로젝트에서는 "어휘를 어떻게 만들었는가"를 코드로 남겨 두는 편이 안전합니다. 이때 가장 흔한 선택이 BPE 학습 스크립트입니다. 핵심은 복잡한 라이브러리보다 **동일 입력에서 동일 vocab/merge 파일이 나오도록 재현성 경로를 고정**하는 데 있습니다.

```python
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

    tokenizer.model.save(str(out), "tokenizer")
    tokenizer.save(str(out / "tokenizer.json"))

train_bpe_tokenizer("data/tinyshakespeare.txt", "artifacts/tokenizer", vocab_size=2000)
```

위 코드는 학습 성능을 올리기 위한 예제가 아니라, 토크나이저 변경이 실험 결과를 오염시키지 않게 만드는 예제입니다. 특히 `special_tokens` 순서를 바꾸면 ID 매핑이 달라지고, 그 순간부터 기존 체크포인트와 비호환이 됩니다. 그래서 토크나이저 산출물은 `ckpt.pt`와 별도 파일이 아니라 같은 릴리스 단위로 다루는 편이 좋습니다.

아래처럼 "토크나이저 메타데이터"를 함께 기록하면 나중에 회귀 분석이 쉬워집니다.

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

이 메타데이터가 있으면 "모델이 갑자기 이상해졌다"는 문제를 만났을 때, 모델 구조보다 먼저 입력 계약 변경 여부를 확인할 수 있습니다. 실무에서 디버깅 시간을 가장 크게 줄이는 습관 중 하나입니다.

### 토큰 길이 분포를 먼저 보면 학습 병목을 빨리 찾을 수 있습니다

토크나이저 선택은 결국 시퀀스 길이 분포를 바꿉니다. 시퀀스가 길어지면 attention 계산량이 `T^2`로 늘고, 같은 GPU 메모리에서 batch size를 줄여야 합니다. 따라서 토크나이저 단계에서 길이 분포를 출력해 두면 이후 학습 설정을 더 합리적으로 잡을 수 있습니다.

```python
import numpy as np

samples = [
    "To be, or not to be, that is the question.",
    "What light through yonder window breaks?",
    "O Romeo, Romeo! wherefore art thou Romeo?",
]

lengths = [len(encode(s)) for s in samples]
print("lengths:", lengths)
print("mean:", float(np.mean(lengths)))
print("p95:", float(np.percentile(lengths, 95)))
```

char-level에서는 평균 길이가 길게 나오지만, 그만큼 디버깅 가시성이 높습니다. 반대로 서브워드는 길이가 줄어들어 학습이 유리해지지만, 인코딩 결과를 사람이 직관적으로 읽기 어려워집니다. 이 트레이드오프를 숫자로 확인하고 선택해야 "왜 이 토크나이저를 썼는가"를 끝까지 설명할 수 있습니다.

| 선택 | 장점 | 비용 |
| --- | --- | --- |
| char-level | 구현/디버깅 단순, 완전 가시성 | 긴 시퀀스, 느린 학습 |
| BPE/서브워드 | 짧은 시퀀스, 실전 효율 | 학습 파이프라인 복잡, 가시성 저하 |
| byte-level | OOV 강건성 | 후처리/가독성 부담 |

시리즈 초반에 char-level을 고정한 이유도 여기 있습니다. 성능 절대값보다 입력 계약을 눈으로 추적하는 경험을 먼저 확보해야, 뒤에서 attention과 loss 곡선을 읽을 때 판단이 흔들리지 않습니다.

## 토크나이저를 바꿀 때 반드시 점검할 운영 포인트

토크나이저는 코드 한 파일의 변경처럼 보이지만, 실제로는 학습 데이터와 모델 가중치의 해석 규칙을 동시에 바꾸는 작업입니다. 그래서 작은 변경도 운영 관점에서는 스키마 마이그레이션에 가깝게 다뤄야 합니다. 특히 다음 네 가지를 사전에 점검하면, 학습 재시작과 추론 불일치 문제를 크게 줄일 수 있습니다.

### 어휘 사전 크기와 특수 토큰 정책

`<pad>`, `<bos>`, `<eos>`, `<unk>`의 존재 여부와 ID 배치는 모델 전체에 전파됩니다. 학습 중간에 특수 토큰 순서를 바꾸면 체크포인트를 재사용하기 어려워지고, 디코딩 결과도 즉시 달라집니다. 따라서 토크나이저 버전별로 특수 토큰 표를 고정 문서로 남기는 것이 좋습니다.

### 정규화 규칙과 역변환 가능성

소문자화, 공백 정리, 유니코드 정규화는 데이터 손실을 만들 수 있습니다. 예를 들어 한국어+영어 혼합 코퍼스에서 과도한 정규화는 도메인 용어를 깨뜨릴 수 있습니다. 학습 전에는 반드시 `encode -> decode` 왕복 샘플을 만들어, 의미 손실이 허용 범위인지 확인해야 합니다.

### 학습/추론 경로의 토크나이저 동기화

학습 스크립트와 서비스 추론 코드가 서로 다른 토크나이저 파일을 참조하면, 모델은 "학습 때 본 입력"과 "실서비스 입력"을 다르게 해석합니다. 이 문제는 정확도 저하로만 나타나서 발견이 늦습니다. 체크포인트 메타데이터에 토크나이저 파일 해시를 함께 저장하면 이 불일치를 초기에 차단할 수 있습니다.

### 데이터 분포와 토큰 길이 모니터링

토크나이저 변경 후에는 평균 토큰 길이와 상위 퍼센타일 길이가 크게 달라질 수 있습니다. 길이가 늘면 같은 컨텍스트 길이에서 담을 수 있는 정보량이 줄고, 학습 비용도 증가합니다. 반대로 지나치게 짧아지면 의미 단위가 깨져 모델이 패턴을 학습하기 어려워질 수 있습니다.

## 작은 실험으로 빠르게 검증하는 방법

토크나이저 변경은 전체 학습을 다시 돌리기 전에 작은 검증으로 실패 가능성을 줄일 수 있습니다. 예를 들어 샘플 문장 100개를 고정해 `토큰 수`, `희귀 토큰 비율`, `왕복 복원율`을 비교하면, 변경의 성격을 빠르게 파악할 수 있습니다. 이 검증을 PR 단계에서 자동화하면, 모델 품질 저하를 사전에 차단하기 쉽습니다.

## 한 줄 결론

토크나이저는 전처리 도구가 아니라 모델의 문자 체계입니다. 이 체계를 고정하고 버전 관리하는 순간, 이후 단계의 실험 품질이 안정됩니다.

## 현업에서 자주 받는 질문

### 작은 모델에서도 이 단계를 엄격하게 지켜야 하나요?

네, 오히려 작은 모델일수록 기본 계약을 엄격하게 지켜야 합니다. 모델 용량이 작을수록 입력 노이즈와 구현 불일치의 영향을 크게 받기 때문입니다. 재현 가능한 실험 단위를 먼저 확보하면, 모델 크기 확장 이전에도 품질 개선 속도가 올라갑니다.

### 실험 속도와 품질 관리가 충돌할 때는 어떻게 하나요?

속도를 높이려면 실험 횟수를 늘리는 것이 아니라 실패 비용을 줄여야 합니다. 설정 파일 고정, 로그 표준화, 체크포인트 메타데이터 저장 같은 장치를 먼저 도입하면, 같은 시간에 더 많은 "유효한" 실험을 수행할 수 있습니다.

### 마지막으로 무엇을 기록해 두면 도움이 되나요?

변경 이유, 기대 효과, 실제 관측 결과를 짧게 남기면 다음 실험의 품질이 올라갑니다. 특히 "왜 이 값을 선택했는가"를 기록하면, 몇 주 뒤에도 의사결정 맥락을 복원할 수 있습니다.

짧은 검증이라도 자동화해 두면 토크나이저 변경 리스크를 크게 줄일 수 있습니다.

## 정리

이번 글에서는 모델이 텍스트를 직접 읽지 않고, 토크나이저가 만든 정수 시퀀스를 입력으로 받는다는 가장 중요한 출발점을 정리했습니다. 이 관점 하나만 분명해져도 LLM의 내부 구조가 훨씬 덜 신비롭게 보입니다.

또한 문자 단위, 단어 단위, 서브워드 토큰화가 무엇을 교환하는지도 살펴봤습니다. char-level은 길지만 투명하고, 서브워드는 효율적이지만 구조가 더 복잡합니다. 이번 시리즈가 char-level을 택한 이유도 바로 이 투명성에 있습니다.

이제 다음 글로 넘어가면 이 정수 ID들에 벡터 의미를 부여하게 됩니다. 즉, 토크나이저가 만든 숫자열이 임베딩을 거쳐 모델이 실제로 다룰 수 있는 표현 공간으로 들어가게 됩니다.

## 처음 질문으로 돌아가기

- **모델은 왜 문자열 대신 정수 시퀀스를 입력으로 받아야 할까요?**
  - 본문의 기준은 글자를 숫자로 바꾸기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **문자 단위, 단어 단위, 서브워드 토큰화는 각각 무엇을 얻고 무엇을 잃을까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **BPE는 실제로 어떤 식으로 어휘를 조금씩 키워 갈까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

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
