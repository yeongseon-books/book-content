---
title: '모델 서빙'
series: llm-finetuning-101
episode: 6
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

# 모델 서빙

## 이 글에서 답할 질문

- 파인튜닝된 소형 모델을 FastAPI 엔드포인트로 감싸는 최소 구조는 무엇일까?
- 서빙 코드에서 학습과 추론 경계를 어디서 끊어야 할까?
- 브라우저를 열지 않고도 엔드포인트를 어떻게 실행 검증할 수 있을까?

> 서빙은 모델을 더 똑똑하게 만드는 단계가 아니라, 이미 준비된 모델을 예측 가능한 HTTP 계약 뒤에 놓는 단계입니다.

예제 코드: [github.com/yeongseon-books/llm-finetuning-101](https://github.com/yeongseon-books/llm-finetuning-101/tree/main/ko/06-serving)

시리즈 마지막 글에서는 학습된 어댑터를 API 뒤에 놓습니다. 운영 환경에서는 학습과 서빙을 분리하는 것이 원칙이지만, 데모 단계에서는 작은 한 걸음 파인튜닝을 한 뒤 곧바로 엔드포인트로 감싸는 편이 전체 흐름을 이해하기 좋습니다.

예제 코드는 tiny GPT-2 + LoRA 모델에 한 번의 toy update를 적용한 뒤 FastAPI 앱을 만들고, `TestClient`로 `/health`와 `/generate`를 호출합니다. 그래서 `python main.py`만 실행해도 서버 프로세스를 따로 띄우지 않고 서빙 경로를 검증할 수 있습니다.

## 데모 서빙에서 꼭 분리해서 볼 것

실전에서는 모델 로딩, 요청 검증, 생성 옵션, 응답 직렬화, 관측성 로그가 서로 다른 책임입니다. 이 글의 예제는 이 중 **모델 준비**와 **HTTP 계약**만 최소 단위로 보여 줍니다. 작은 데모라도 health check와 generate endpoint를 분리해 두면 운영 코드로 확장하기 쉬워집니다.

![데모 서빙에서 꼭 분리해서 볼 것](../../../assets/llm-finetuning-101/06/06-01-what-this-demo-isolates-on-purpose.ko.png)
## 최소 실행 예제

```python
from fastapi import FastAPI
from fastapi.testclient import TestClient

app = FastAPI()

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.post("/generate")
def generate(payload: dict) -> dict:
    prompt = payload["prompt"]
    outputs = model.generate(**tokenizer(prompt, return_tensors="pt"), max_new_tokens=20)
    return {"completion": tokenizer.decode(outputs[0], skip_special_tokens=True)}

client = TestClient(app)
print(client.get("/health").json())
print(client.post("/generate", json={"prompt": "파이썬 함수 예시"}).json())
```

## 이 코드에서 봐야 할 것

- 예제는 실제로 toy training loss를 한 번 계산한 뒤 앱 상태에 저장합니다. 즉, 완전히 순수한 베이스 모델 서빙이 아닙니다.
- `TestClient`를 쓰면 uvicorn을 띄우지 않아도 엔드포인트 계약을 검증할 수 있어 CI 친화적입니다.
- `/health`와 `/generate`를 분리해 두면 모델 상태 확인과 추론 실패 원인 분리가 쉬워집니다.

## 실무에서 헷갈리는 지점

- 서빙 코드 안에서 학습을 계속 돌리는 것은 실전 기본값이 아닙니다. 이 글은 전체 흐름을 한 파일에서 재현하기 위한 데모입니다.
- 생성 결과 문장이 자연스럽지 않은 것은 tiny 모델 한계 때문입니다. 서빙 구조 검증과 생성 품질 평가는 별개 문제입니다.
- FastAPI 엔드포인트가 성공했다고 운영 준비가 끝난 것은 아닙니다. 배치, 타임아웃, 인증, 로깅은 별도 설계가 필요합니다.

## 체크리스트

- [ ] 모델 준비와 HTTP 엔드포인트 책임을 구분해서 설명할 수 있다.
- [ ] `TestClient`로 `/health`와 `/generate`를 검증했다.
- [ ] tiny 모델 데모와 실제 운영 서빙의 차이를 이해했다.
- [ ] 시리즈 1편부터 6편까지의 흐름을 한 번에 연결할 수 있다.

## 정리

이제 파인튜닝 시리즈의 최소 전체 경로가 완성되었습니다. 수식으로 감을 잡고, 데이터를 정리하고, LoRA를 붙이고, 한 step 학습하고, 평가한 뒤, 마지막에 HTTP 엔드포인트까지 연결했습니다.

<!-- blog-only:start -->
시리즈 첫 글로 돌아가기: [LLM 파인튜닝 입문](./01-intro.md)
<!-- blog-only:end -->

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

- [FastAPI documentation](https://fastapi.tiangolo.com/)
- [Starlette TestClient reference](https://www.starlette.io/testclient/)

Tags: Fine-tuning, LoRA, LLM, Python
