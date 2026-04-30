# 모델 서빙

> LLM 파인튜닝 101 (6/6)

파인튜닝된 모델을 서비스에 배포하는 방법을 다룹니다. LoRA 어댑터를 베이스 모델에 병합해 단일 모델로 만들고, FastAPI로 추론 엔드포인트를 구성하고, Hugging Face Hub에 배포하는 전체 흐름을 구현합니다.

---

## 어댑터 병합

LoRA 어댑터를 베이스 모델과 병합하면 추론 시 별도의 PEFT 레이어 없이 단일 모델로 서빙할 수 있습니다. 병합 후에는 원본과 동일한 파라미터 수를 가집니다.

```python
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

BASE_MODEL = "microsoft/phi-2"
ADAPTER_PATH = "./outputs/finetuned"
MERGED_PATH = "./outputs/merged"

def merge_adapter(
    base_model_name: str = BASE_MODEL,
    adapter_path: str = ADAPTER_PATH,
    output_path: str = MERGED_PATH,
) -> None:
    """LoRA 어댑터를 베이스 모델에 병합하고 저장합니다."""
    print("베이스 모델 로드 중...")
    # 병합은 fp16으로 수행 (4비트 양자화 없이)
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        trust_remote_code=True,
    )
    tokenizer = AutoTokenizer.from_pretrained(adapter_path)

    print("어댑터 로드 및 병합 중...")
    model = PeftModel.from_pretrained(model, adapter_path)
    model = model.merge_and_unload()  # 어댑터 가중치를 베이스에 흡수

    print(f"병합된 모델 저장: {output_path}")
    model.save_pretrained(output_path, safe_serialization=True)
    tokenizer.save_pretrained(output_path)
    print("병합 완료")
```

---

## FastAPI 추론 서버

```python
import time
from contextlib import asynccontextmanager
from typing import Optional

import torch
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig

ALPACA_TEMPLATE = """Below is an instruction that describes a task. Write a response that appropriately completes the request.

### Instruction:
{instruction}

### Response:
"""

class InferenceRequest(BaseModel):
    instruction: str
    input: Optional[str] = ""
    max_new_tokens: int = 200
    temperature: float = 0.7
    do_sample: bool = True

class InferenceResponse(BaseModel):
    response: str
    latency_ms: float
    tokens_generated: int

# 전역 모델 상태
_model = None
_tokenizer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global _model, _tokenizer
    model_path = "./outputs/merged"
    print(f"모델 로드 중: {model_path}")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
    )
    _tokenizer = AutoTokenizer.from_pretrained(model_path)
    if _tokenizer.pad_token is None:
        _tokenizer.pad_token = _tokenizer.eos_token
    _model = AutoModelForCausalLM.from_pretrained(
        model_path,
        quantization_config=bnb_config,
        device_map="auto",
        trust_remote_code=True,
    )
    _model.eval()
    print("모델 로드 완료")
    yield
    _model = None
    _tokenizer = None

app = FastAPI(title="LLM Inference API", lifespan=lifespan)

@app.post("/generate", response_model=InferenceResponse)
async def generate(request: InferenceRequest):
    if _model is None:
        raise HTTPException(status_code=503, detail="모델이 준비되지 않았습니다.")

    prompt = ALPACA_TEMPLATE.format(instruction=request.instruction)
    inputs = _tokenizer(prompt, return_tensors="pt").to(_model.device)

    start = time.time()
    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=request.max_new_tokens,
            do_sample=request.do_sample,
            temperature=request.temperature if request.do_sample else 1.0,
            pad_token_id=_tokenizer.eos_token_id,
        )
    latency_ms = (time.time() - start) * 1000

    generated = outputs[0][inputs["input_ids"].shape[1]:]
    response_text = _tokenizer.decode(generated, skip_special_tokens=True)
    return InferenceResponse(
        response=response_text,
        latency_ms=round(latency_ms, 1),
        tokens_generated=len(generated),
    )

@app.get("/health")
async def health():
    return {"status": "ok", "model_loaded": _model is not None}
```

---

## Hugging Face Hub 배포

```python
from huggingface_hub import HfApi

def push_to_hub(
    model_path: str,
    repo_id: str,
    private: bool = True,
    token: str | None = None,
) -> None:
    """병합된 모델을 Hugging Face Hub에 배포합니다."""
    from transformers import AutoModelForCausalLM, AutoTokenizer
    import torch

    print(f"Hub 배포 시작: {repo_id}")
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(
        model_path, torch_dtype=torch.float16, trust_remote_code=True
    )
    tokenizer.push_to_hub(repo_id, private=private, token=token)
    model.push_to_hub(repo_id, private=private, token=token)
    print(f"배포 완료: https://huggingface.co/{repo_id}")

def push_adapter_only(
    adapter_path: str,
    repo_id: str,
    private: bool = True,
    token: str | None = None,
) -> None:
    """어댑터만 배포합니다 (베이스 모델 제외, 용량 절약)."""
    api = HfApi(token=token)
    api.create_repo(repo_id=repo_id, private=private, exist_ok=True)
    api.upload_folder(
        folder_path=adapter_path,
        repo_id=repo_id,
        token=token,
    )
    print(f"어댑터 배포 완료: https://huggingface.co/{repo_id}")
```

---

## 시리즈 완성

```python
# 전체 파인튜닝 파이프라인 요약
pipeline_steps = [
    "1. 베이스 모델 로드 (4비트 양자화)",
    "2. 데이터셋 준비 및 전처리 (Alpaca 형식)",
    "3. LoRA 어댑터 구성 (r=16, alpha=32)",
    "4. SFTTrainer로 학습 (3 에폭, lr=2e-4)",
    "5. 평가 (F1, 베이스 모델 대비 비교)",
    "6. 어댑터 병합 및 FastAPI 서빙",
]
for step in pipeline_steps:
    print(step)
```

이 시리즈에서 구축한 파인튜닝 파이프라인은 소비자 GPU 한 장에서 실행 가능합니다. LoRA 덕분에 7B 모델도 8GB VRAM에서 학습할 수 있습니다. 데이터 품질, 하이퍼파라미터 탐색, 평가 지표 설계가 실제 프로덕션 파인튜닝의 핵심입니다.

<!-- toc:begin -->
## 시리즈 목차

- [LLM 파인튜닝 입문](./01-intro.md)
- [데이터셋 준비와 전처리](./02-dataset.md)
- [LoRA 어댑터 구성](./03-lora.md)
- [학습 루프와 하이퍼파라미터](./04-training.md)
- [모델 평가](./05-evaluation.md)
- **모델 서빙 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [Hugging Face Hub 배포 문서](https://huggingface.co/docs/hub/models-uploading)
- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [PEFT merge_and_unload](https://huggingface.co/docs/peft/package_reference/lora#peft.LoraModel.merge_and_unload)

Tags: Fine-tuning, LoRA, LLM, Python
