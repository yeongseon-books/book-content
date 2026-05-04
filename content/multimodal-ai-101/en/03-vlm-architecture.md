---
title: Vision-Language Model Architecture
series: multimodal-ai-101
episode: 3
language: en
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- VLM
- LLaVA
- Cross-Attention
- Q-Former
- BLIP-2
- Multimodal Fusion
last_reviewed: '2026-05-03'
seo_description: Episode 2 covered CLIP, which aligns image and text in the same space.
  To do the kind of reasoning GPT-4V or LLaVA does ("describe this image and…
---

# Vision-Language Model Architecture

> Multimodal AI 101 series (3/10)

---

## How VLMs give an LLM "eyes"

Episode 2 covered CLIP, which aligns image and text in the same space. To do the kind of reasoning GPT-4V or LLaVA does ("describe this image and convert the table to markdown"), you need one more step: connecting image vectors so the LLM can consume them like tokens.

VLM architectures split into three schools by how they wire that connection. LLaVA uses a projection. BLIP-2 uses a Q-Former. Flamingo inserts cross-attention into the LLM. This episode covers what each pattern was trying to solve and what trade-offs come with it.

## Common skeleton: Vision Encoder + Adapter + LLM

Every VLM is a combination of three parts.

```
[Image] -> Vision Encoder (CLIP/SigLIP) -> visual features
                                               |
                                               v
                                          Adapter
                                               |
                                               v
[Text]  -> Tokenizer -> text tokens ----> LLM -> output
```

The Adapter is where schools differ. It is the module that converts visual features into a token sequence the LLM can understand.

## School 1: LLaVA - simple MLP projection

LLaVA is the simplest. It projects the CLIP image encoder output (e.g., 576 patches x 1024 dim) directly to the LLM hidden dim and prepends those tokens to the LLM input sequence.

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

Training has two stages.

1. **Stage 1 (alignment)**: vision encoder and LLM are frozen, only the projection layer trains. Data: (image, caption) pairs.
2. **Stage 2 (instruction tuning)**: LLM and projection train together (vision encoder still frozen). Data: GPT-4 generated (image, instruction, answer) triples.

The wins are simplicity and fast training. LLaVA-1.5 reached partial GPT-4V-level reasoning after one day on 8xA100. The cost: visual tokens accumulate in the LLM context (576 tokens is heavy for any non-long-context model).

## School 2: BLIP-2 - Q-Former for token compression

BLIP-2 attacks the visual-token-count problem head-on. A small Transformer called the Q-Former owns 32 learnable queries that pull key information out of the vision features via cross-attention. The LLM then sees a fixed 32 visual tokens.

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

The 32 Q-Former outputs go through another small linear projection into the LLM. Context cost is roughly 1/18 of LLaVA, which makes multi-image batches feasible even on 7B LLMs.

Trade-off: the Q-Former itself trains in stages with mixed losses (ITC, ITM, ITG), so the pipeline is heavier than LLaVA's.

## School 3: Flamingo - inserting cross-attention into the LLM

Flamingo took a different direction. It inserts new cross-attention layers between the LLM's transformer blocks, training only those new layers. Existing LLM weights are frozen.

```
LLM Block 1
GATED CROSS-ATTENTION (new) <- vision features
LLM Block 2
GATED CROSS-ATTENTION (new) <- vision features
LLM Block 3
...
```

The gated cross-attention starts at gate=0 and opens slowly during training. That keeps LLM quality from collapsing in the early steps.

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

The win: this is the most natural fit for multi-image and video inputs. Cross-attention does not extend the sequence length. The cost: you must modify the LLM internals, so plugging this into an already-trained LLM is harder than the LLaVA approach.

## Comparing the three schools

| Item | LLaVA | BLIP-2 | Flamingo |
| --- | --- | --- | --- |
| Adapter | MLP projection | Q-Former (cross-attn) | Gated cross-attn inserts |
| LLM modification | None (input prefix) | None (input prefix) | Yes (layer insertion) |
| Visual tokens to LLM | 256-576 | 32 | 0 (cross-attn only) |
| Training difficulty | Low (2-stage) | Medium (3-stage Q-Former) | High |
| Multi-image | Possible but heavy | Efficient | Most natural |
| Representative models | LLaVA-1.5, MiniGPT-4 | BLIP-2, InstructBLIP | Flamingo, IDEFICS |

In practice the starting point is almost always LLaVA: open weights, public training code, low fine-tuning cost. When multi-image or video workloads become serious, look at BLIP-2 derivatives or IDEFICS-2.

## First inference with LLaVA

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

The `<image>` token marks the slot for the visual prefix; the processor splices image features in automatically.

## Five common pitfalls

### 1. Visual tokens eating LLM context

A single image costs LLaVA 576 tokens. With a 4096-token context, you lose room fast once you add system prompt and question. In multi-turn conversations, keep only one or two images alive at a time.

### 2. Instruction-tuning data quality is the cap

LLaVA's secret sauce was a 158K instruction dataset built by GPT-4. If you fine-tune your own VLM, instruction data quality sets the upper bound on capability. Low-quality instructions amplify hallucination.

### 3. Unfreezing the vision encoder during fine-tuning

LLaVA-1.5 keeps the vision encoder frozen by default. Unfreezing causes catastrophic forgetting of zero-shot generalization. Even for domain-specific fine-tuning, train only the projection first.

### 4. Weak multilingual base LLM

LLaVA-1.5 is built on Vicuna (LLaMA), which is weak in many non-English languages. For multilingual multimodal needs, pick a multilingual-strong base such as KoLLaVA, Qwen2-VL, or InternVL2.

### 5. Single-benchmark evaluation

VLMs span a wide task spectrum: OCR, charts, diagrams, real-world photos, documents. Track MMMU, ChartQA, DocVQA, TextVQA, and RealWorldQA together to expose model weaknesses.

## Key Takeaways

- Every VLM is vision encoder + adapter + LLM; the adapter design defines the school.
- LLaVA: MLP projection. Simple, easy to train. The open-source starting point.
- BLIP-2: Q-Former compresses to 32 visual tokens. Efficient for multi-image.
- Flamingo: gated cross-attention inserted inside the LLM. Most natural fit for multi-image and video.
- Production starting point is LLaVA. For multilingual, evaluate Qwen2-VL or InternVL2.
- Verify visual-token context budget, instruction data quality, vision encoder freeze policy, multilingual base choice, and multi-benchmark evaluation before going live.

---

<!-- toc:begin -->
## Multimodal AI 101 series

- [Why Multimodal AI Matters](./01-why-multimodal-matters.md)
- [Image Encoders: CLIP and ViT](./02-image-encoders-clip-vit.md)
- **Vision-Language Model Architecture (current)**
- Image Captioning and OCR Pipelines (upcoming)
- Multimodal RAG: Searching Images and Text Together (upcoming)
- Audio Processing and Whisper STT (upcoming)
- Text-to-Image with Diffusion (upcoming)
- Multimodal Embeddings and Cross-modal Search (upcoming)
- Video Understanding (Frame Sampling to Video-LLaVA) (upcoming)
- Building a Production Multimodal Application (upcoming)
<!-- toc:end -->

## References

- [Liu et al. - Visual Instruction Tuning (LLaVA)](https://arxiv.org/abs/2304.08485)
- [Li et al. - BLIP-2: Bootstrapping Language-Image Pre-training](https://arxiv.org/abs/2301.12597)
- [Alayrac et al. - Flamingo: a Visual Language Model for Few-Shot Learning](https://arxiv.org/abs/2204.14198)
- [HuggingFace - LLaVA model docs](https://huggingface.co/docs/transformers/model_doc/llava)

Tags: VLM, LLaVA, Cross-Attention, Q-Former, BLIP-2, Multimodal Fusion
