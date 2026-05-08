
# 글자를 숫자로 바꾸기

> LLM from Scratch 101 시리즈 (1/9)

처음 LLM 코드를 뜯어볼 때 가장 낯설었던 장면은 모델이 문장을 전혀 읽지 못한다는 사실이었습니다. 우리가 프롬프트 창에 "안녕"을 치면 뭔가 말을 알아듣는 것처럼 보이지만, 모델 안으로 들어가는 순간에는 이미 숫자 배열입니다. 사람 눈에는 인사말인데, 신경망 눈에는 `[31495, ...]` 같은 정수일 뿐입니다.

저는 이 지점을 빨리 받아들여야 뒤가 쉬워진다고 봤습니다. 토크나이저를 대충 넘기면 이후 임베딩, 어텐션, 손실 함수가 전부 공중에 뜹니다. 반대로 "아, 결국 문자열을 안정적으로 정수 시퀀스로 자르는 문제구나"라고 잡고 나면 LLM이 갑자기 덜 신비로워집니다.

이번 시리즈는 TinyShakespeare로 작은 GPT를 직접 만듭니다. 화려한 프레임워크는 잠시 접어 두고, PyTorch 2.x와 몇 개 파일만으로 끝까지 가보겠습니다.

오늘 멘탈 모델은 간단합니다. **모델은 텍스트를 읽지 않고, 토크나이저가 만든 정수 시퀀스를 읽습니다.**

---

<!-- a-grade-intro:begin -->

## 핵심 질문

- 왜 모델은 텍스트 대신 정수를 입력으로 받을까요?
- 문자 단위·단어 단위·서브워드 단위 토크나이저는 어떤 trade-off를 가질까요?
- BPE는 실제로 어떻게 vocabulary를 만들어 갈까요?
- 이 시리즈가 character-level 토크나이저를 고른 이유는 무엇일까요?

<!-- a-grade-intro:end -->

## 텍스트는 왜 직접 못 넣나

신경망은 텐서를 받습니다. 문자열 자체는 덧셈도 못 하고 행렬 곱도 못 합니다. 그래서 "To be, or not to be" 같은 문장을 먼저 숫자로 바꿔야 합니다. 이 숫자가 토큰 ID입니다.

여기서 중요한 점 하나만 짚고 가겠습니다. 토큰 ID는 뜻을 담은 숫자가 아닙니다. 아직은 단순한 인덱스입니다. 5번 토큰이 6번 토큰과 가깝다는 보장도 없고, 알파벳 순서처럼 의미가 정렬되어 있지도 않습니다. 일단 정수로 바꾸고, 나중에 임베딩 단계에서 그 정수에 벡터 의미를 입힙니다.

입문 단계에서 흔히 놓치는 부분도 여기입니다. 토크나이저가 달라지면 같은 문장도 전혀 다른 ID 시퀀스로 바뀝니다. 그러면 뒤에서 학습한 임베딩도 달라지고, 체크포인트 호환성도 깨집니다. 토크나이저가 모델 바깥의 전처리처럼 보여도, 실제로는 모델의 일부라고 보는 편이 정확합니다.

## 가장 단순한 방법: 문자 단위 토큰화

가장 손쉬운 출발점은 문자 단위입니다. 어휘 집합을 문자 목록으로 만들고, 각 문자에 번호를 붙이면 끝입니다. 복잡한 예외도 없고 디버깅도 쉽습니다.

```python
text = "hello world"
chars = sorted(set(text))
stoi = {ch: i for i, ch in enumerate(chars)}
itos = {i: ch for ch, i in stoi.items()}

def encode(s: str) -> list[int]:
    dropped = sorted({c for c in s if c not in stoi})
    if dropped:
        print(f"지원하지 않는 문자를 건너뜁니다: {dropped}")
    return [stoi[c] for c in s if c in stoi]

decode = lambda ids: "".join(itos[i] for i in ids)

ids = encode(text)
print(ids)
print(decode(ids))
```

한 번 돌려 보면 문자열이 숫자 시퀀스로 바뀌는 감각이 바로 옵니다. 다만 char-level 토크나이저는 자기 vocab에 있는 문자만 다룰 수 있어서, 처음 보는 문자는 경고를 찍고 건너뜁니다.

## 단어 단위 vs 서브워드 — 트레이드오프 한 장

문자 단위가 늘 정답은 아닙니다. 단어 단위는 시퀀스가 짧아지지만 어휘가 금방 불어나고, 처음 보는 단어에 약합니다. 서브워드는 그 중간을 노립니다.

![단어 단위와 서브워드의 절충 관계](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/01/01-01-vs.ko.png)

*단어 단위와 서브워드의 절충 관계*
현업 모델이 BPE류를 많이 쓰는 이유가 여기 있습니다. 어휘 크기와 표현력을 적당한 선에서 맞추기 좋기 때문입니다.

## BPE를 손으로 한 번 — 의미 없는 마법 아니다

BPE를 처음 들으면 꽤 거창해 보이지만, 아이디어는 의외로 소박합니다. 자주 붙어 나오는 쌍을 반복해서 합칩니다. `low`, `lower`, `lowest`를 놓고 보면 `l + o`, 그다음 `lo + w`, 이런 식으로 합쳐 가며 점점 긴 조각을 만듭니다. 자주 쓰는 패턴이 어휘에 승격되는 셈입니다.

GPT-2는 이런 방식의 서브워드 어휘를 50,257개 규모로 잡았습니다. 거대한 마법 상자가 아니라, 통계를 이용해 잘게 자른 텍스트 조각 사전이라고 보면 이해가 편합니다.

저는 BPE를 설명할 때 늘 "압축과 사전 편집의 중간쯤"이라고 말합니다. 자주 나오는 패턴은 짧은 ID 하나로 줄이고, 드문 패턴은 더 잘게 남겨 둡니다. 그래서 흔한 단어는 시퀀스가 짧아지고, 처음 보는 단어도 완전히 포기하지 않습니다.

## tiktoken으로 GPT-2 토크나이저 써보기

이론만 보면 감이 덜 옵니다. 실제 GPT-2 계열 토크나이저는 아래처럼 바로 만져볼 수 있습니다.

```python
import tiktoken

enc = tiktoken.get_encoding("gpt2")
text = "Hello, tokenizer!"

ids = enc.encode(text)
decoded = enc.decode(ids)

print(ids)
print(decoded)
```

`pip install tiktoken`만 해두면 바로 실행됩니다. 같은 문장을 문자 단위로 자를 때와 전혀 다른 ID 배열이 나옵니다.

## 우리 시리즈는 char-level로 간다 — 왜?

이번 시리즈는 char-level로 갑니다. 이유는 세 가지입니다. 코드가 짧고, TinyShakespeare처럼 작은 말뭉치에서는 학습이 빠르며, 디버깅이 눈에 잘 들어옵니다. 글자가 대략 65개 안팎이라 마지막 softmax도 부담이 적습니다.

거대한 서비스 모델을 만들 때는 부족합니다. 하지만 원리를 익히는 101 시리즈에서는 이 선택이 오히려 좋습니다. 처음 세 편에서 중요한 건 성능보다 투명성입니다.

## 데이터 준비: TinyShakespeare 다운로드 + 인코딩

이제 시리즈 첫 코드 파일인 `data.py`를 만듭니다. TinyShakespeare를 내려받고, 문자 사전을 만든 뒤, 학습용과 검증용 바이너리로 저장합니다.

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
        print(f"지원하지 않는 문자를 건너뜁니다: {dropped}")
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

이 스크립트를 한 번 돌려 두면 다음 글부터는 숫자 시퀀스를 바로 배치로 뽑아 쓸 수 있습니다. 저는 여기서 `decode()`를 꼭 남겨 둡니다. 모델 디버깅은 결국 숫자를 다시 사람이 읽는 글로 되돌려 보는 작업이 자주 나오기 때문입니다.

## 다음 글 예고

이제 정수 시퀀스는 준비됐습니다. 다음 글에서는 이 차가운 ID 배열에 벡터 의미를 입힙니다. 토큰 임베딩과 위치 임베딩을 더해서, 모델이 읽을 첫 입력 텐서를 만들겠습니다.

<!-- a-grade-example:begin -->

## 시니어 엔지니어는 이렇게 생각합니다

- **입력 단위 결정** — char/byte/BPE 선택이 모델 행동을 가장 크게 좌우합니다.
- **Vocab 크기** — 어휘 크기는 메모리·임베딩·정확도의 트레이드오프입니다.
- **UNK 처리** — OOV 정책을 명시해 학습·추론 일관성을 유지합니다.
- **재현성** — 토크나이저 자체를 버전으로 관리합니다.
- **도메인 영향** — 도메인 어휘 분포에 따라 토크나이저를 다시 평가합니다.

## 체크리스트

- [ ] TinyShakespeare를 다운로드해 정수 시퀀스로 인코딩했다.
- [ ] vocabulary 크기와 토큰 수의 관계를 직접 출력해 확인했다.
- [ ] tiktoken으로 같은 문장을 BPE로 토큰화해 결과를 비교했다.
- [ ] character-level의 한계와 장점을 한 문장으로 요약할 수 있다.

<!-- a-grade-example:end -->

## 시리즈 목차

- **글자를 숫자로 바꾸기 (현재 글)**
- 정수에서 벡터로, 그리고 위치 (예정)
- 어떤 토큰을 얼마나 볼지 스스로 정하기 (예정)
- 블록 하나, 깊이의 단위 (예정)
- 조립: GPT 모델 클래스 완성 (예정)
- 기울기로 배우기 (예정)
- 샘플링 — 학습된 모델에서 글 뽑아내기 (예정)
- 베이스 모델을 우리 작업에 맞추기 (예정)
- 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

## 참고 자료

- [Karpathy minBPE](https://github.com/karpathy/minbpe)
- [OpenAI tiktoken](https://github.com/openai/tiktoken)
- [Language Models are Unsupervised Multitask Learners (GPT-2)](https://cdn.openai.com/better-language-models/language_models_are_unsupervised_multitask_learners.pdf)
- [Neural Machine Translation of Rare Words with Subword Units](https://arxiv.org/abs/1508.07909)

Tags: LLM, PyTorch, Transformer, Tutorial

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
