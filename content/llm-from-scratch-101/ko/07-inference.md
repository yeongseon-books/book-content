---
title: "LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기"
series: llm-from-scratch-101
episode: 7
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
seo_description: 지난 글에서 ckpt.pt를 저장하고 나면 바로 말을 시켜 보고 싶어집니다. 그런데 model.eval()만으로는 문장이 나오지 않습니다.
---

# LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기

학습이 끝나고 `ckpt.pt`까지 저장하면 바로 모델에게 말을 시켜 보고 싶어집니다. 하지만 `model.eval()`만 호출한다고 문장이 저절로 나오지는 않습니다. 학습된 다음 토큰 분포를 실제 문자열로 펼쳐 내는 생성 루프가 따로 필요합니다.

생성은 의외로 단순한 반복입니다. 현재 문맥을 모델에 넣고, 마지막 위치의 logits만 꺼내고, 그 분포에서 토큰 하나를 고른 뒤, 그 토큰을 다시 문맥 뒤에 붙입니다. 이 과정을 여러 번 반복하면 텍스트가 한 글자씩 자라납니다.

여기서부터는 품질보다도 샘플링 전략이 눈에 들어오기 시작합니다. 같은 모델이라도 argmax만 쓰면 지루해지고, temperature를 높이면 더 무작위가 되고, top-k와 top-p를 쓰면 후보군을 다른 방식으로 자를 수 있습니다. 즉, 생성은 모델만이 아니라 decoding 정책의 결과이기도 합니다.

이번 글에서는 자기회귀 생성 루프의 뼈대를 만들고, greedy decoding, temperature, top-k, top-p, sliding context window가 어떤 역할을 하는지 `generate.py` 기준으로 정리하겠습니다.

이 글은 LLM from Scratch 101 시리즈의 일곱 번째 글입니다.

이제 생성 루프를 이해하면 다음 글에서 같은 베이스 모델 위에 instruction 형식을 덧입히는 파인튜닝도 자연스럽게 연결됩니다.

## 먼저 던지는 질문

- 생성 루프는 정확히 무엇을 반복할까요?
- greedy decoding은 왜 자주 지루하고 반복적인 출력을 만들까요?
- temperature는 logits 분포를 어떻게 바꿀까요?

## 큰 그림

![LLM from Scratch 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/llm-from-scratch-101/07/07-01-autoregressive-generation-one-token-at-a.ko.png)

*LLM from Scratch 101 7장 흐름 개요*

이 그림에서는 샘플링 — 학습된 모델에서 글 뽑아내기를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 샘플링 — 학습된 모델에서 글 뽑아내기의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

생성은 학습된 언어 모델을 실제로 체감하게 만드는 첫 단계입니다. 앞선 글들에서 loss를 낮추고 체크포인트를 저장했다면, 여기서는 그 숫자 변화가 실제 텍스트 출력으로 어떻게 나타나는지 확인하게 됩니다. 즉, 학습과 추론 사이를 잇는 관문입니다.

또한 샘플링은 모델 품질을 해석하는 방식에도 큰 영향을 줍니다. 같은 가중치라도 greedy, top-k, top-p, temperature 설정에 따라 결과의 다양성과 일관성이 크게 달라집니다. 모델이 이상한 것이 아니라 decoding 정책이 그렇게 만든 경우도 많습니다.

실전 감각에서도 중요합니다. 생성 루프는 나중에 챗봇, API, 스트리밍 서버를 만들 때 그대로 재사용됩니다. 그리고 context window 자르기, 확률 분포 변형, 반복적인 sampling step은 거의 모든 autoregressive LLM 시스템의 공통 기반입니다.

## 핵심 관점

생성은 복잡한 문장 작성기라기보다 **다음 토큰 분포를 한 번 계산하고, 그중 하나를 선택해서 다시 입력으로 되먹이는 자기회귀 피드백 루프**입니다. 모델은 매번 전체 답변을 한꺼번에 쓰지 않고, 현재까지의 문맥 위에서 바로 다음 한 조각을 계속 예측합니다.

이 관점이 중요한 이유는 sampling 전략의 위치가 분명해지기 때문입니다. 모델은 logits만 내고, 실제로 어떤 토큰을 선택할지는 decoding 정책이 결정합니다. temperature, top-k, top-p는 모두 이 정책에 속합니다.

따라서 생성 품질은 모델 가중치와 decoding 설정의 합성 결과입니다. 모델이 배운 다음 토큰 분포가 기반이고, 샘플링 정책은 그 분포를 얼마나 보수적으로 또는 얼마나 다양하게 소비할지를 결정합니다.

> 이번 글의 핵심은 간단합니다. 생성은 다음 토큰 분포에서 하나를 뽑고, 그 결과를 다시 입력으로 넣는 자기회귀 루프입니다.

## 핵심 개념

### 자기회귀 생성은 한 토큰씩 이어 붙입니다

현재 문맥 `idx`를 모델에 넣으면 각 위치별 logits가 나오지만, 생성에 필요한 것은 마지막 위치의 logits뿐입니다. 그 분포에서 하나를 선택해 문맥 뒤에 붙이고, 늘어난 문맥으로 다시 같은 연산을 반복합니다.

이 구조를 이해하면 왜 생성이 느린지, 왜 KV cache 같은 최적화가 나중에 중요한지까지 자연스럽게 이어집니다. 지금은 가장 단순한 char-level 구현으로 원리를 보는 단계입니다.

### greedy decoding은 안전하지만 금방 단조로워집니다

`argmax`는 매 step마다 가장 확률이 높은 토큰을 고릅니다. 논리적으로는 깔끔하지만, 실제 출력은 쉽게 반복되고 평평해집니다. 모델이 조금만 한쪽 패턴으로 기울어 있어도 매번 같은 선택을 하게 되기 때문입니다.

이 방식은 디버깅이나 deterministic 비교에는 좋지만, 자연스러운 텍스트 생성에는 종종 너무 보수적입니다. 그래서 보통은 확률 분포에서 샘플링을 하거나 후보군을 제한하는 기법을 함께 사용합니다.

### temperature는 logits의 날카로움을 조절합니다

temperature는 softmax 전에 logits를 나누는 스케일링 계수입니다. `T < 1`이면 분포가 더 날카로워져 높은 확률 토큰이 더 유리해지고, `T > 1`이면 분포가 평평해져 무작위성이 커집니다.

직관적으로 보면, temperature는 모델의 자신감을 증폭하거나 완화하는 손잡이입니다. 너무 낮으면 반복적이고, 너무 높으면 의미 없는 문자가 튈 수 있습니다. 작은 모델일수록 이 설정의 영향이 더 크게 체감됩니다.

### top-k와 top-p는 후보군을 자르는 두 가지 방식입니다

top-k는 확률이 높은 상위 `k`개 토큰만 남기고 나머지를 버립니다. 긴 꼬리 영역의 매우 낮은 확률 토큰이 뽑히는 일을 줄여, 출력이 완전히 무너지지 않게 도와줍니다.

반면 top-p, 즉 nucleus sampling은 누적 확률이 `p`를 넘을 때까지의 최소 토큰 집합만 남깁니다. 모델이 확신이 큰 경우에는 후보군이 작아지고, 확신이 약한 경우에는 후보군이 조금 더 넓어집니다. 고정 개수인 top-k보다 더 적응적으로 움직이는 방식입니다.

### 컨텍스트 창보다 길어지면 앞부분을 잘라야 합니다

이번 모델은 learned positional embedding을 쓰므로 최대 길이가 `block_size`로 고정되어 있습니다. 따라서 생성 중 문맥이 그보다 길어지면 최근 `block_size`개 토큰만 남기고 앞부분을 잘라야 합니다. 보통 `idx[:, -self.config.block_size :]` 형태로 처리합니다.

이 슬라이딩 윈도우는 단순하지만 중요합니다. 이 처리가 없으면 위치 임베딩 범위를 넘어가거나, 모델이 설계된 최대 길이를 초과한 입력을 받아 오류가 납니다.

### `generate()`와 `generate.py`를 붙이면 바로 생성 실험을 할 수 있습니다

이제 생성 로직을 모델 메서드와 CLI 스크립트로 정리합니다.

```python
# model.py
def generate(self, idx, max_new_tokens, temperature=1.0, top_k=None, top_p=None):
    for _ in range(max_new_tokens):
        idx_cond = idx[:, -self.config.block_size :]
        logits, _ = self(idx_cond)
        logits = logits[:, -1, :] / max(temperature, 1e-5)
        if top_k is not None:
            v, _ = torch.topk(logits, min(top_k, logits.size(-1)))
            logits[logits < v[:, [-1]]] = float("-inf")
        if top_p is not None:
            s_logits, s_idx = torch.sort(logits, descending=True)
            cutoff = F.softmax(s_logits, dim=-1).cumsum(dim=-1) > top_p
            cutoff[..., 1:] = cutoff[..., :-1].clone(); cutoff[..., 0] = False
            s_logits[cutoff] = float("-inf")
            logits = torch.full_like(logits, float("-inf")).scatter(1, s_idx, s_logits)
        probs = F.softmax(logits, dim=-1)
        idx_next = torch.multinomial(probs, num_samples=1)
        idx = torch.cat((idx, idx_next), dim=1)
    return idx
```

```python
# generate.py
import argparse, torch
from data import decode, encode
from model import GPT, GPTConfig

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prompt", type=str, default="ROMEO:")
    parser.add_argument("--max", type=int, default=200)
    parser.add_argument("--temp", type=float, default=0.8)
    parser.add_argument("--top_k", type=int, default=20)
    parser.add_argument("--top_p", type=float, default=0.9)
    args = parser.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    ckpt = torch.load("ckpt.pt", map_location=device)
    config = GPTConfig(**ckpt["config"])
    model = GPT(config).to(device)
    model.load_state_dict(ckpt["model"]); model.eval()
    idx = torch.tensor([encode(args.prompt)], dtype=torch.long, device=device)
    with torch.no_grad(): out = model.generate(idx, args.max, args.temp, args.top_k, args.top_p)
    print(decode(out[0].tolist()))

if __name__ == "__main__":
    main()
```

```bash
python generate.py --prompt "ROMEO:" --max 200 --temp 0.8 --top_k 20 --top_p 0.9
```

이 구성은 다음 글의 파인튜닝, 마지막 글의 챗봇 래퍼로 그대로 이어집니다. 먼저 CLI에서 생성 루프가 명확히 보이도록 해 두면, 이후 API나 UI로 감싸는 일이 훨씬 쉬워집니다.

### 출력은 품질보다 리듬 변화에 먼저 주목하면 됩니다

소형 char-level GPT의 출력은 처음에는 완성도 높은 문장이 아니라 셰익스피어풍 리듬에 더 가깝습니다. 하지만 이 단계의 목표는 완벽한 답변이 아니라, 학습된 분포가 실제 텍스트 흐름으로 바뀌는지 확인하는 데 있습니다.

```text
ROMEO:
What thou me for the king,
And in thy lord I cry.
Thee no more of men.
```

출력이 다소 뒤틀려 보여도, 리듬과 문자 패턴이 학습 데이터셋의 분위기를 반영한다면 생성 루프는 제대로 작동하고 있는 것입니다.

## 흔히 헷갈리는 지점

- `model.eval()`만 호출하면 텍스트가 나온다고 생각하기 쉽지만, 실제로는 autoregressive generation loop가 필요합니다.
- greedy decoding이 가장 "정확한" 생성이라고 느끼기 쉽지만, 실제 텍스트는 쉽게 단조로워집니다.
- temperature를 무작위 버튼 정도로 보지만, logits 분포의 날카로움을 직접 조절하는 중요한 손잡이입니다.
- top-k와 top-p를 같은 방식으로 오해하기 쉽지만, 하나는 개수 기준이고 다른 하나는 누적 확률 기준입니다.
- 컨텍스트 자르기를 구현 디테일로만 보지만, `block_size` 제약을 지키는 필수 장치입니다.

## 운영 체크리스트

- [ ] 마지막 위치 logits만 사용해 새 토큰을 뽑는 루프를 설명할 수 있는가
- [ ] greedy, temperature, top-k, top-p를 각각 바꿔 출력 차이를 확인했는가
- [ ] `idx[:, -self.config.block_size :]`가 왜 필요한지 이해했는가
- [ ] `generate.py`에서 체크포인트와 config를 함께 복원하고 있는가
- [ ] 같은 프롬프트로 여러 샘플링 설정을 비교해 decoding 영향도를 체감했는가

## 정리

이번 글에서는 학습된 GPT를 실제 텍스트 생성기로 바꾸는 자기회귀 샘플링 루프를 구현했습니다. 핵심은 마지막 위치의 logits를 읽고, 그 분포에서 토큰 하나를 뽑아 다시 입력으로 넣는 반복 구조입니다.

또한 temperature, top-k, top-p, sliding context window가 왜 필요한지도 살펴봤습니다. 모델 가중치가 생성의 기반이라면, 샘플링 전략은 그 기반을 어떤 성격의 출력으로 풀어낼지를 결정하는 정책입니다.

다음 글에서는 이 베이스 모델 위에 instruction-response 형식을 덧입히는 파인튜닝을 수행합니다. 즉, 셰익스피어풍 문자 예측기에서 조금 더 질문-응답에 가까운 출력 습관으로 모델을 이동시키게 됩니다.

## 처음 질문으로 돌아가기

- **생성 루프는 정확히 무엇을 반복할까요?**
  - 본문의 기준은 샘플링 — 학습된 모델에서 글 뽑아내기를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **greedy decoding은 왜 자주 지루하고 반복적인 출력을 만들까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **temperature는 logits 분포를 어떻게 바꿀까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM from Scratch 101 (1/9): 글자를 숫자로 바꾸기](./01-tokenizer.md)
- [LLM from Scratch 101 (2/9): 정수에서 벡터로, 그리고 위치](./02-embedding.md)
- [LLM from Scratch 101 (3/9): 어떤 토큰을 얼마나 볼지 스스로 정하기](./03-attention.md)
- [LLM from Scratch 101 (4/9): 블록 하나, 깊이의 단위](./04-transformer-block.md)
- [LLM from Scratch 101 (5/9): 조립: GPT 모델 클래스 완성](./05-gpt-model.md)
- [LLM from Scratch 101 (6/9): 기울기로 배우기](./06-training-loop.md)
- **LLM from Scratch 101 (7/9): 샘플링 — 학습된 모델에서 글 뽑아내기 (현재 글)**
- LLM from Scratch 101 (8/9): 베이스 모델을 우리 작업에 맞추기 (예정)
- LLM from Scratch 101 (9/9): 직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [The Curious Case of Neural Text Degeneration (arXiv:1904.09751)](https://arxiv.org/abs/1904.09751)
- [Hierarchical Neural Story Generation (arXiv:1805.04833)](https://arxiv.org/abs/1805.04833)
- [nanoGPT model.py generate (GitHub)](https://github.com/karpathy/nanoGPT/blob/master/model.py)
- [How to generate text: using different decoding methods for language generation with Transformers (Hugging Face)](https://huggingface.co/blog/how-to-generate)

### 관련 시리즈

- [LLM 앱 기초 — 스트리밍 응답 처리](../../llm-app-foundations-101/ko/06-streaming-responses.md)
- [LangChain 101 — Streaming](../../langchain-101/ko/05-streaming.md)
- [LLM API 프로덕션 101 — 스트리밍 심화](../../llm-api-production-101/ko/03-streaming-in-depth.md)

Tags: LLM, PyTorch, Transformer, Tutorial
