---
title: '데이터셋 준비와 전처리'
series: llm-finetuning-101
episode: 2
language: ko
status: publish-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Fine-tuning
- LoRA
- LLM
- Python
last_reviewed: '2026-05-01'
---

# 데이터셋 준비와 전처리

## 이 글에서 답할 질문

- instruction, input, output 세 필드를 어떤 형태로 정리해야 할까?
- Hugging Face datasets로 작은 JSONL 파일을 어떻게 바로 읽어 올릴까?
- 전처리 단계에서 꼭 확인해야 할 최소 검증 포인트는 무엇일까?

> 좋은 파인튜닝 데이터셋은 문장 모음이 아니라, 모델이 반복해서 따라 배워야 하는 요청-응답 계약서입니다.

예제 코드: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/ko/02-dataset)

데이터셋 단계에서 가장 중요한 것은 양보다 형식의 일관성입니다. 모델이 무엇을 입력으로 보고, 어디까지를 응답으로 학습해야 하는지 애매하면 학습 손실이 내려가도 결과는 흐릿합니다. 그래서 2편에서는 큰 코퍼스를 모으는 일보다 **작은 샘플을 명확하게 구조화하는 법**에 집중합니다.

예제 코드는 `toy.jsonl`을 만들고, `datasets.load_dataset()`으로 읽은 뒤, instruction 템플릿과 토크나이저 전처리를 적용합니다. 실행하면 행 수, 컬럼, 토큰 길이가 출력되므로 전처리 파이프라인이 실제로 동작하는지 바로 확인할 수 있습니다.

## 데이터셋에서 먼저 고정할 것

파인튜닝 데이터는 보통 세 층으로 나뉩니다. **원본 샘플**, **프롬프트 템플릿을 적용한 텍스트**, **토크나이즈된 텐서**입니다. 이 세 층을 분리해서 생각해야 필터링 문제와 토큰 길이 문제를 따로 잡을 수 있습니다.

![데이터셋에서 먼저 고정할 것](../../../assets/llm-finetuning-101/02/02-01-the-three-layers-of-dataset-preparation.ko.png)
## 최소 실행 예제

```python
import json
from pathlib import Path

from datasets import load_dataset
from transformers import AutoTokenizer

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "toy.jsonl"

with DATA_PATH.open("w", encoding="utf-8") as file:
    file.write(json.dumps({
        "instruction": "파이썬 리스트를 뒤집는 두 가지 방법을 설명하세요.",
        "input": "예제 코드 한 줄을 함께 보여주세요.",
        "output": "lst[::-1]과 lst.reverse()를 쓸 수 있습니다.",
    }, ensure_ascii=False) + "\n")

dataset = load_dataset("json", data_files=str(DATA_PATH), split="train")
tokenizer = AutoTokenizer.from_pretrained("sshleifer/tiny-gpt2")
```

## 이 코드에서 봐야 할 것

- `datasets.load_dataset()`을 쓰면 실전에서 받는 JSONL 구조를 그대로 흉내 낼 수 있습니다.
- 템플릿 적용과 토크나이즈를 분리하면 나중에 모델별 chat template으로 교체하기 쉽습니다.
- 예제는 `padding="max_length"`, `max_length=64`로 고정해 아주 작은 실습에서도 길이 통계를 바로 볼 수 있게 했습니다.

## 실무에서 헷갈리는 지점

- 데이터가 많다고 좋은 것이 아닙니다. 중복 답변이 많거나 형식이 섞이면 작은 모델은 더 빨리 망가집니다.
- 전처리에서 `input_ids`만 만들고 `labels`를 만들지 않는 것은 정상입니다. 4편에서 학습용 레이블을 붙입니다.
- instruction과 output 길이 필터는 정답이 아니라 출발점입니다. 실제 프로젝트에서는 금칙어, PII, 중복, 클래스 불균형 검사가 더 필요합니다.

## 체크리스트

- [ ] JSONL 원본 샘플이 instruction, input, output 구조로 정리되었다.
- [ ] `datasets.load_dataset()`으로 실제 파일을 읽어 왔다.
- [ ] 토크나이저 전처리 후 컬럼과 길이를 확인했다.
- [ ] 다음 글에서 어떤 모듈에 LoRA를 꽂을지 데이터 길이와 함께 생각해 봤다.

## 정리

데이터셋 준비의 핵심은 모델이 배워야 할 입출력 경계를 분명히 만드는 것입니다. 작은 샘플로 먼저 구조를 맞춰 두면 이후 학습 루프를 디버깅할 때 훨씬 덜 흔들립니다.

<!-- blog-only:start -->
다음 글: [LoRA 어댑터 구성](./03-lora.md)
<!-- blog-only:end -->

<!-- toc:begin -->
## 시리즈 목차

- [LLM 파인튜닝 입문](./01-intro.md)
- **데이터셋 준비와 전처리 (현재 글)**
- LoRA 어댑터 구성 (예정)
- 학습 루프와 하이퍼파라미터 (예정)
- 모델 평가 (예정)
- 모델 서빙 (예정)

<!-- toc:end -->

---

## 참고 자료

- [Hugging Face Datasets documentation](https://huggingface.co/docs/datasets)
- [Instruction tuning overview](https://arxiv.org/abs/2203.02155)

Tags: Fine-tuning, LoRA, LLM, Python
