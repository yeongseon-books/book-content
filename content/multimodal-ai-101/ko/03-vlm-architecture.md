---
title: "Multimodal AI 101 (3/10): Vision-Language Model 아키텍처"
series: multimodal-ai-101
episode: 3
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- VLM
- LLaVA
- Cross-Attention
- Q-Former
- BLIP-2
- Multimodal Fusion
last_reviewed: '2026-05-12'
seo_description: 2편에서 본 CLIP은 image와 text를 같은 공간에 정렬하는 데까지 갔습니다.
---

# Multimodal AI 101 (3/10): Vision-Language Model 아키텍처

멀티모달을 실제 제품에 넣으려는 순간 대부분의 질문은 결국 하나로 모입니다. “LLM은 원래 텍스트만 읽는데, 이미지는 어떻게 이해하게 되는가?” 이 질문에 답하지 못하면 모델 선택 기준도 흐려지고, fine-tuning 범위도 과도해지기 쉽습니다. VLM 아키텍처를 보는 이유는 논문을 외우기 위해서가 아니라, 어떤 설계가 비용·지연·품질의 균형을 어떻게 바꾸는지 이해하기 위해서입니다.

현재 많이 쓰이는 VLM은 크게 세 가지 길을 보여 줍니다. LLaVA처럼 간단한 projection으로 vision token을 LLM 입력으로 연결하는 방법, BLIP-2처럼 Q-Former로 토큰을 압축해 넘기는 방법, Flamingo처럼 LLM 내부에 cross-attention 층을 삽입하는 방법입니다. 겉으로는 모두 “이미지를 이해하는 모델”이지만 내부 교환 비용과 확장성은 꽤 다릅니다.

실무 관점에서 이 차이는 매우 현실적입니다. visual token 수가 길어지면 LLM context를 빨아먹고, adapter가 무거워지면 학습과 추론 비용이 커지며, base LLM과 vision encoder를 어디까지 고정할지에 따라 운영 난이도가 달라집니다. 즉 아키텍처 선택은 논문 취향 문제가 아니라 운영 모델 선택입니다.

이 글에서는 VLM을 “LLM에 눈을 다는 마법”이 아니라, image encoder의 출력을 LLM이 소비 가능한 형태로 연결하는 설계 계열로 정리합니다.

이 글은 Multimodal AI 101 시리즈의 3번째 글입니다.

세 학파의 공통 뼈대를 먼저 이해하면 모델 이름이 바뀌어도 판단 기준은 크게 흔들리지 않습니다.


![Multimodal AI 101 3장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/multimodal-ai-101/03/03-01-big-picture.ko.png)
*Multimodal AI 101 3장 흐름 개요*
> Vision-Language Model 아키텍처의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 먼저 던지는 질문

- VLM은 어떤 경로로 image encoder의 출력을 LLM 입력으로 연결할까요?
- Vision Encoder + Adapter + LLM이라는 공통 뼈대는 왜 대부분의 모델에서 반복될까요?
- LLaVA, BLIP-2, Flamingo는 각각 어떤 trade-off를 선택한 설계일까요?

## 왜 이 글이 중요한가

VLM 아키텍처를 이해하면 모델 선택이 훨씬 덜 감에 의존하게 됩니다. “요즘 많이 쓰니까”가 아니라, visual token 길이와 adapter 복잡도, base LLM 호환성 같은 실제 변수로 판단할 수 있기 때문입니다.

또한 adapter 레이어는 비용과 지연 시간에 직결됩니다. 비슷해 보이는 두 모델이라도 token compression을 어디서 하느냐에 따라 긴 문서 이미지나 다중 이미지 입력에서 성능이 크게 달라질 수 있습니다.

무엇보다도 아키텍처를 보면 어디를 학습시키고 어디를 고정할지 감이 생깁니다. 이 감이 없으면 fine-tuning 범위를 과도하게 잡아 데이터와 예산을 동시에 낭비하기 쉽습니다.

## 핵심 관점

VLM을 설명할 때 흔히 “LLM에 눈을 달았다”는 표현을 씁니다. 직관에는 도움이 되지만, 실제 구현을 이해하기에는 너무 모호합니다. 더 정확한 설명은 image encoder가 만든 시각 토큰을 LLM이 이해할 수 있는 계약으로 재매핑한다는 것입니다.

이 계약을 얼마나 단순하게 둘지, 얼마나 압축할지, 어느 층에서 반복 상호작용하게 만들지가 LLaVA·BLIP-2·Flamingo를 나누는 핵심입니다. 즉 차이는 모델의 목적이 아니라 시각 정보를 텍스트 중심 LLM에 흘려 넣는 연결 방식에 있습니다.

이렇게 보면 새 모델이 등장해도 구조를 읽기가 쉬워집니다. vision encoder, adapter, language model 세 층을 분리해서 보면 어느 부분이 병목이고 어느 부분이 비용을 만들고 있는지 바로 추적할 수 있기 때문입니다.

> VLM의 본질은 시각 정보를 더 많이 넣는 것이 아니라, LLM이 소화할 수 있는 길이와 형태로 토큰 계약을 재설계하는 데 있습니다.

## 핵심 개념

### VLM은 어떻게 LLM에 "눈"을 다는가

2편에서 본 CLIP은 image와 text를 같은 공간에 정렬하는 데까지 갔습니다. 그런데 GPT-4V나 LLaVA처럼 "이 이미지를 설명하고 표를 markdown으로 변환해 줘" 같은 reasoning을 하려면 한 단계가 더 필요합니다. image vector를 LLM이 token처럼 소화할 수 있도록 연결해야 합니다.

VLM 아키텍처는 이 연결 방식에 따라 크게 세 학파로 나뉩니다. LLaVA의 projection 방식, BLIP-2의 Q-Former 방식, Flamingo의 cross-attention 방식. 이번 편에서 각 패턴이 무엇을 풀려고 했는지, 어떤 trade-off가 있는지를 봅니다.

### 공통 구조: Vision Encoder + Adapter + LLM

VLM은 결국 다음 세 부품의 조합입니다.

```text
[Image] -> Vision Encoder (CLIP/SigLIP) -> visual features
                                               |
                                               v
                                          Adapter
                                               |
                                               v
[Text]  -> Tokenizer -> text tokens ----> LLM -> output
```

차이는 Adapter입니다. visual feature를 LLM이 "이해할 수 있는" token sequence로 변환하는 모듈인데, 여기서 학파가 갈립니다.

### 학파 1: LLaVA - 단순 MLP projection

LLaVA는 가장 단순합니다. CLIP image encoder의 출력 (예: 576 patch x 1024 dim)을 그대로 LLM hidden dim으로 projection하고, LLM 입력 sequence 앞에 끼워 넣습니다.

```python
import torch
import torch.nn as nn

class LLaVAProjector(nn.Module):
    def __init__(self, vision_dim: int = 1024, llm_dim: int = 4096):
        super().__init__()
        self.proj = nn.Sequential(
            nn.Linear(vision_dim, llm_dim),
            nn.GELU(),
            nn.Linear(llm_dim, llm_dim),
        )

    def forward(self, vision_features: torch.Tensor) -> torch.Tensor:
        # vision_features: (B, num_patches, vision_dim)
        return self.proj(vision_features)  # (B, num_patches, llm_dim)
```

학습은 두 단계입니다.

1. **Stage 1 (alignment)**: vision encoder와 LLM은 frozen, projection layer만 학습. 데이터는 (image, caption) 쌍.
2. **Stage 2 (instruction tuning)**: LLM과 projection을 함께 학습 (vision encoder는 여전히 frozen). 데이터는 GPT-4가 생성한 (image, instruction, answer) 쌍.

장점은 단순함과 빠른 학습입니다. LLaVA-1.5는 8xA100에서 1일 학습으로 GPT-4V 수준 reasoning 일부를 따라잡았습니다. 단점은 visual token 수가 그대로 LLM context에 누적된다는 점입니다 (576 token은 long-context model이 아니면 부담입니다).

### 학파 2: BLIP-2 - Q-Former로 token 압축

BLIP-2는 visual token이 너무 많다는 문제를 정면으로 풀었습니다. Q-Former라는 작은 Transformer를 만들어, learnable query 32개가 vision feature에서 핵심 정보를 cross-attention으로 끌어옵니다. 결과적으로 LLM이 받는 visual token은 32개로 고정됩니다.

```python
import torch
import torch.nn as nn

class QFormer(nn.Module):
    def __init__(self, num_queries: int = 32, vision_dim: int = 1408,
                 hidden_dim: int = 768, num_layers: int = 12):
        super().__init__()
        self.queries = nn.Parameter(torch.randn(num_queries, hidden_dim))
        layer = nn.TransformerDecoderLayer(
            d_model=hidden_dim, nhead=12, batch_first=True
        )
        self.decoder = nn.TransformerDecoder(layer, num_layers=num_layers)
        self.vision_proj = nn.Linear(vision_dim, hidden_dim)

    def forward(self, vision_features: torch.Tensor) -> torch.Tensor:
        # vision_features: (B, num_patches, vision_dim)
        B = vision_features.size(0)
        q = self.queries.unsqueeze(0).expand(B, -1, -1)  # (B, 32, hidden)
        memory = self.vision_proj(vision_features)
        return self.decoder(q, memory)  # (B, 32, hidden)
```

Q-Former 출력 32개 token이 다시 작은 linear projection을 거쳐 LLM에 들어갑니다. context 부담이 LLaVA의 1/18이라서 7B LLM에서도 multi-image batch가 가능합니다.

학습 trade-off: Q-Former 자체가 ITC, ITM, ITG 같은 복합 loss를 단계별로 학습해야 해서 LLaVA보다 파이프라인이 무겁습니다.

### 학파 3: Flamingo - LLM에 cross-attention layer 삽입

Flamingo는 다른 방향을 택했습니다. LLM의 transformer block 사이사이에 새 cross-attention layer를 끼워 넣고, 이 새 layer만 학습합니다. 기존 LLM weight는 모두 frozen입니다.

```text
LLM Block 1
GATED CROSS-ATTENTION (new) <- vision features
LLM Block 2
GATED CROSS-ATTENTION (new) <- vision features
LLM Block 3
...
```

gated cross-attention은 처음에 gate=0으로 시작해 학습이 진행되며 천천히 열립니다. 이 덕분에 학습 초기에 LLM 성능이 망가지지 않습니다.

```python
import torch
import torch.nn as nn

class GatedCrossAttention(nn.Module):
    def __init__(self, dim: int, num_heads: int = 8):
        super().__init__()
        self.attn = nn.MultiheadAttention(dim, num_heads, batch_first=True)
        self.gate = nn.Parameter(torch.zeros(1))  # tanh-gated
        self.ff = nn.Sequential(nn.Linear(dim, dim * 4), nn.GELU(),
                                nn.Linear(dim * 4, dim))
        self.gate_ff = nn.Parameter(torch.zeros(1))

    def forward(self, x: torch.Tensor, vision: torch.Tensor) -> torch.Tensor:
        attn_out, _ = self.attn(x, vision, vision)
        x = x + torch.tanh(self.gate) * attn_out
        x = x + torch.tanh(self.gate_ff) * self.ff(x)
        return x
```

장점은 multi-image / video 입력에 가장 자연스럽다는 점입니다. cross-attention이라 sequence 길이를 늘리지 않습니다. 단점은 LLM 내부에 손을 대야 해서, 이미 학습된 LLM에 plug-in하기가 LLaVA보다 어렵습니다.

### 세 학파 비교

| 항목 | LLaVA | BLIP-2 | Flamingo |
| --- | --- | --- | --- |
| Adapter | MLP projection | Q-Former (cross-attn) | Gated cross-attn 삽입 |
| LLM 수정 | 없음 (input prefix만) | 없음 (input prefix만) | 있음 (layer 삽입) |
| Visual tokens to LLM | 256~576 | 32 | 0 (cross-attn) |
| 학습 난이도 | 낮음 (2-stage) | 중간 (3-stage Q-Former) | 높음 |
| Multi-image | 가능하지만 context 부담 | 효율적 | 가장 자연스러움 |
| 대표 모델 | LLaVA-1.5, MiniGPT-4 | BLIP-2, InstructBLIP | Flamingo, IDEFICS |

실무에서 시작점은 거의 LLaVA입니다. open weight, 학습 코드 공개, fine-tuning 비용이 낮기 때문입니다. multi-image / video 워크로드가 본격화되면 BLIP-2 계열이나 IDEFICS-2를 검토합니다.

### LLaVA로 첫 추론 돌리기

```python
import torch
from PIL import Image
from transformers import LlavaForConditionalGeneration, AutoProcessor

model_id = "llava-hf/llava-1.5-7b-hf"
processor = AutoProcessor.from_pretrained(model_id)
model = LlavaForConditionalGeneration.from_pretrained(
    model_id, torch_dtype=torch.float16, device_map="auto"
)

image = Image.open("samples/chart.png").convert("RGB")
prompt = "USER: <image>\nSummarize the key trend in this chart in one sentence.\nASSISTANT:"

inputs = processor(images=image, text=prompt, return_tensors="pt").to(model.device)
with torch.no_grad():
    output = model.generate(**inputs, max_new_tokens=128, do_sample=False)
print(processor.decode(output[0], skip_special_tokens=True))
```

`<image>` 토큰이 visual prefix가 들어갈 자리를 잡아주고, processor가 자동으로 image feature를 끼워 넣습니다.

### 어떤 아키텍처가 어느 팀에 맞는가

작은 팀이 첫 VLM을 도입할 때는 대개 단순한 연결 구조가 유리합니다. LLaVA류처럼 projection이 명확한 모델은 디버깅 포인트가 적고, serving 구조도 비교적 단순합니다. 빠르게 가설을 검증해야 하는 단계라면 이 단순함이 큰 장점입니다.

반면 긴 문서 이미지나 다중 이미지 입력이 많다면 token compression이나 deeper fusion의 이점이 커질 수 있습니다. BLIP-2와 Flamingo 계열이 보여 주는 차별점이 바로 이 지점입니다. 시각 토큰을 어떻게 줄이고 언제 상호작용시키느냐가 실제 품질과 비용을 동시에 바꿉니다.

결국 좋은 선택은 가장 강한 모델이 아니라, 현재 팀의 데이터 규모와 serving 제약에 맞는 구조를 고르는 것입니다. 아키텍처를 이해하는 목적도 바로 이 현실적인 선택지를 분별하기 위해서입니다.

## Adapter 선택을 위한 실험 프로토콜

VLM 아키텍처를 비교할 때는 "정답률" 하나로 끝내면 안 됩니다. Adapter는 토큰 길이, 추론 지연, GPU 메모리에 직접 영향을 주므로 최소한 네 가지 지표를 함께 봐야 합니다. 첫째는 task별 정확도(TextVQA, ChartQA, DocVQA)입니다. 둘째는 평균 토큰 사용량입니다. 셋째는 P95 latency입니다. 넷째는 요청당 평균 비용입니다. 이 네 값을 같이 두면 LLaVA, BLIP-2, Flamingo 계열의 선택 기준이 명확해집니다.

```python
from dataclasses import dataclass

@dataclass
class EvalRow:
    model: str
    docvqa: float
    chartqa: float
    avg_input_tokens: int
    p95_latency_ms: int
    usd_per_1k_requests: float

rows = [
    EvalRow("llava-1.6-7b", 0.71, 0.58, 3900, 1820, 7.4),
    EvalRow("blip2-flan-t5-xl", 0.69, 0.55, 1700, 1490, 5.2),
    EvalRow("flamingo-style", 0.74, 0.60, 1500, 2410, 9.8),
]
for r in rows:
    print(r)
```

학습 실험에서도 단계를 분리해야 합니다. projection 또는 Q-Former만 학습하는 단계와 LLM 일부를 풀어 미세조정하는 단계를 섞으면 원인 분석이 어려워집니다. 운영 관점에서는 "어느 레이어를 변경했는가"를 변경 이력으로 강하게 관리하는 편이 안전합니다.

## Vision API를 포함한 이중 검증 경로

내부 VLM만으로 불확실한 답이 나오면 GPT-4V나 Claude로 재검증하는 경로를 두면 품질이 안정됩니다. 특히 문서 표 해석이나 작은 숫자 판독처럼 실패 비용이 큰 도메인에서 효과가 큽니다.

```python
def route_for_second_opinion(confidence: float, answer: str) -> str:
    if confidence < 0.55:
        return "gpt4v"
    if "불확실" in answer or "잘 보이지" in answer:
        return "claude"
    return "accept"
```

재검증 경로는 모든 요청에 적용하지 않고 저신뢰 요청에만 걸어야 비용이 통제됩니다. 이때 confidence는 모델 logprob뿐 아니라 길이 이상치, OCR 불일치율 같은 보조 신호와 함께 계산하는 것이 안정적입니다.

## 문서·차트·일반 이미지를 분리한 라우팅 전략

하나의 VLM으로 모든 입력을 처리하면 운영은 단순해지지만 비용과 품질이 동시에 악화될 수 있습니다. 문서 OCR 중심 질문은 표와 숫자 읽기에 강한 모델로, 일반 장면 질문은 가벼운 모델로 보내는 라우팅이 전체 성능을 안정화합니다. 이때 입력 분류기는 복잡한 모델이 아니라 간단한 규칙 기반으로 시작해도 충분합니다.

```python
def route_model(question: str, has_table_like_text: bool, image_count: int) -> str:
    if has_table_like_text:
        return "gpt4v_doc"
    if image_count > 3:
        return "claude_long_context"
    if "차트" in question or "그래프" in question:
        return "vlm_chart"
    return "llava_fast"
```

이 라우팅을 도입하면 평균 latency를 낮추면서도 어려운 케이스는 고성능 모델로 보낼 수 있습니다. 핵심은 규칙을 정한 뒤 주기적으로 오분류 케이스를 검토해 업데이트하는 것입니다.

## 운영 설계 포인트: 토큰 예산과 실패 모드 문서화

VLM 요청은 텍스트 요청보다 실패 모드가 다양합니다. 이미지 디코딩 실패, 시각 토큰 과다, OCR 불일치, 모델 환각이 한 요청 안에서 동시에 나타날 수 있습니다. 그래서 운영 전에는 토큰 예산표와 실패 모드 대응표를 문서화하는 편이 좋습니다.

예를 들어 "입력 이미지 1장 = 평균 500 visual token"처럼 경험치를 표로 두고, 질문 길이와 합쳐 총 입력 토큰을 사전에 추정하면 timeout을 줄일 수 있습니다. 추정치가 임계값을 넘으면 자동으로 이미지 수를 줄이거나 고성능 모델 경로로 분기하는 정책을 둘 수 있습니다.

```python
def estimate_total_tokens(text_tokens: int, image_count: int, visual_tokens_per_image: int = 500) -> int:
    return text_tokens + image_count * visual_tokens_per_image

def enforce_token_budget(estimated: int, budget: int = 6000) -> bool:
    return estimated <= budget
```

이 예산 정책을 로깅과 연결하면 어떤 유형의 요청이 시스템을 압박하는지 빠르게 보입니다. 결국 아키텍처 선택의 현실적 기준은 성능만이 아니라, 실패를 얼마나 예측 가능하게 다루는지에 달려 있습니다.

## 평가 데이터셋 구성 예시

VLM 아키텍처 비교를 위해서는 데이터셋도 입력 유형별로 분리해야 합니다. 문서 이미지, 차트, 일반 장면, UI 스크린샷을 섞어 두고 각 묶음의 점수를 따로 계산하면 모델의 편향이 더 선명하게 드러납니다. 이 기준이 있으면 특정 모델이 어디에서 유리한지 팀 내 합의를 만들기 쉽습니다.

```python
EVAL_SPLITS = {
    "doc": 500,
    "chart": 300,
    "photo": 400,
    "ui": 300,
}
```

## 운영 검증 루프: 주간 점검 항목을 고정하기

멀티모달 시스템은 모델 정확도만으로 상태를 판단하면 늦게 대응하게 됩니다. 그래서 주간 운영 회의에서 항상 같은 항목을 점검하는 루프를 고정하는 편이 좋습니다. 예를 들어 요청량, 평균 지연 시간, P95 지연, 오류율, 재시도율, 캐시 히트율, 사용자 불만 비율을 동일 포맷으로 기록하면 작은 이상 징후를 초기에 잡을 수 있습니다.

또한 지표는 기능별로 분해해야 합니다. 단일 "성공률" 수치만 보면 어떤 단계에서 손실이 났는지 알기 어렵습니다. 입력 검증 단계, 전처리 단계, 검색 단계, 생성 단계를 분리해 성공률을 기록하면 병목 구간이 명확해집니다. 이 분해 지표는 모델 교체나 파이프라인 변경 후 회귀를 탐지하는 데 특히 유용합니다.

```python
weekly_health = {
    "request_count": 0,
    "avg_latency_ms": 0,
    "p95_latency_ms": 0,
    "error_rate": 0.0,
    "retry_rate": 0.0,
    "cache_hit_rate": 0.0,
    "user_downvote_rate": 0.0,
}
```

운영 루프를 고정하면 기술 선택도 더 현실적으로 바뀝니다. 새 모델을 도입할 때 "정확도 상승"만 보지 않고, 지연 증가와 비용 증가를 같은 표에서 비교할 수 있기 때문입니다. 결국 프로덕션 품질은 한 번의 모델 업그레이드가 아니라, 반복 가능한 점검 루프를 통해 유지됩니다.

## 흔히 헷갈리는 지점

- **visual token이 LLM context를 잠식** LLaVA는 image 한 장에 576 token을 씁니다. context 4096짜리 모델이라면 system prompt와 question을 빼고 남는 용량이 빠르게 줄어듭니다. multi-turn conversation에서는 한 번에 1~2장만 유지하는 정책을 둡니다.
- **instruction tuning data 품질이 결과를 좌우** LLaVA의 핵심 비밀은 GPT-4가 만든 158K instruction dataset입니다. 자체 fine-tuning을 한다면 instruction data 품질이 모델 capability의 상한을 정합니다. low-quality instruction은 hallucination을 키웁니다.
- **fine-tuning 시 vision encoder를 같이 unfreeze** LLaVA-1.5는 vision encoder를 frozen으로 두는 게 기본입니다. 같이 학습하면 catastrophic forgetting으로 zero-shot 일반화가 무너집니다. 도메인 특화 fine-tuning이라도 처음에는 projection만 학습합니다.
- **다국어에 약한 base LLM** LLaVA-1.5의 base LLM은 Vicuna(LLaMA)입니다. 한국어 reasoning이 약합니다. 한국어 multimodal이 필요하면 KoLLaVA, Qwen2-VL, InternVL2처럼 다국어가 강한 base를 선택합니다.
- **evaluation을 단일 benchmark로만 검증** VLM은 OCR, chart, diagram, real-world photo, document 등 task spectrum이 넓습니다. MMMU, ChartQA, DocVQA, TextVQA, RealWorldQA를 함께 봐야 모델의 약점이 보입니다.

## 운영 체크리스트

- [ ] 시각 토큰 수가 실제 context budget을 얼마나 차지하는지 측정했는가
- [ ] adapter 학습 범위와 frozen layer 범위를 명시적으로 분리했는가
- [ ] instruction tuning 데이터셋의 품질과 도메인 적합성을 먼저 검증했는가
- [ ] 다국어 입력이 필요할 경우 base LLM의 언어 커버리지를 별도로 확인했는가
- [ ] 단일 벤치마크가 아니라 문서·차트·일반 이미지 평가를 분리해 비교했는가

## 정리

대부분의 VLM은 Vision Encoder, Adapter, LLM이라는 공통 뼈대를 공유합니다. 차이는 시각 토큰을 얼마나 단순하게 연결할지, 얼마나 압축할지, 어느 층에서 반복 상호작용하게 만들지에 있습니다.

LLaVA는 단순함, BLIP-2는 압축 효율, Flamingo는 깊은 상호작용이라는 장점을 보여 줍니다. 어느 쪽이 더 좋다기보다, 입력 길이와 학습 비용에 따라 적합한 선택이 달라집니다.

이 구조 감각을 잡고 나면 이후의 OCR+VLM, 멀티모달 RAG, production serving에서도 훨씬 현실적인 의사결정을 할 수 있습니다. 결국 모든 문제는 시각 토큰을 어디서 어떻게 다루느냐로 다시 돌아오기 때문입니다.

## 처음 질문으로 돌아가기

- **VLM은 어떤 경로로 image encoder의 출력을 LLM 입력으로 연결할까요?**
  - 본문의 기준은 Vision-Language Model 아키텍처를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **Vision Encoder + Adapter + LLM이라는 공통 뼈대는 왜 대부분의 모델에서 반복될까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **LLaVA, BLIP-2, Flamingo는 각각 어떤 trade-off를 선택한 설계일까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Multimodal AI 101 (1/10): Multimodal AI가 중요한 이유](./01-why-multimodal-matters.md)
- [Multimodal AI 101 (2/10): Image Encoder: CLIP과 ViT](./02-image-encoders-clip-vit.md)
- **Vision-Language Model 아키텍처 (현재 글)**
- Image Captioning과 OCR 파이프라인 (예정)
- Multimodal RAG: 이미지와 텍스트를 함께 검색하기 (예정)
- 오디오 처리와 Whisper STT (예정)
- Diffusion으로 Text-to-Image 생성 (예정)
- Multimodal Embedding과 Cross-modal 검색 (예정)
- Video 이해 - Frame Sampling에서 Video-LLaVA까지 (예정)
- Production Multimodal Application 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서

- [Liu et al. - Visual Instruction Tuning (LLaVA)](https://arxiv.org/abs/2304.08485)
- [Li et al. - BLIP-2: Bootstrapping Language-Image Pre-training](https://arxiv.org/abs/2301.12597)
- [Alayrac et al. - Flamingo: a Visual Language Model for Few-Shot Learning](https://arxiv.org/abs/2204.14198)
- [HuggingFace - LLaVA model docs](https://huggingface.co/docs/transformers/model_doc/llava)

### 관련 시리즈

- [LLM 앱 기초 101 - 토큰 이해하기](../../llm-app-foundations-101/ko/02-understanding-tokens.md)
- [AI 앱 패턴 101 - 문서 어시스턴트](../../ai-app-patterns-101/ko/03-document-assistant.md)
- [LangGraph 101 - 상태 관리와 체크포인트](../../langgraph-101/ko/02-state-and-checkpoints.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/multimodal-ai-101/ko/03-vlm-architecture)

Tags: VLM, LLaVA, Cross-Attention, Q-Former, BLIP-2, Multimodal Fusion
