# LLM from Scratch 101 — 시리즈 작업 계획

> 시리즈 디렉토리: `llm-from-scratch-101/{ko,en,medium}/`
> 9 포스트 × 3 변형 = 27 마크다운 파일 + 9 Mermaid PNG (×2 언어)

## 시리즈 공통 컨텍스트 (모든 포스트가 따라야 함)

- **스택:** PyTorch 2.x (autograd 사용, HF transformers 사용 안 함)
- **데이터셋:** TinyShakespeare (40KB) — 모든 포스트가 같은 코퍼스 사용
- **모델 크기:** ~10M 파라미터 (n_layer=6, n_head=4, n_embd=128, block_size=64)
- **누적 코드:** 단일 `data.py` + `model.py` + `train.py` + `generate.py` + `finetune.py` + `server.py`
- **분량:** 한국어 기준 2,000~3,000자 / 영어 기준 그에 상응
- **톤:** 시니어 엔지니어 회상조, "~입니다" 격식. AI 슬롭 금지.
- **태그 (5개):** `LLM, PyTorch, Transformer, 딥러닝, Tutorial`

## AGENTS.md 형식 룰 (**필수**)

각 ko 포스트 구조 (위→아래):

1. `# 제목` (H1, 시리즈명 X, 본 글 제목만)
2. 도입부 3~4 문단 (독자 공감 hook → 이 글에서 다룰 것 → 멘탈 모델 한 줄)
3. `---` 구분자
4. 본문 H2 섹션들 (개념 → 다이어그램/코드 → 운영 포인트)
5. `## 다음 글 예고` (마지막 본문 섹션)
6. `## 참고 자료` (References)

**⚠️ TOC 블록과 태그 라인은 작성하지 말 것.** `finalize-posts.py`가 자동 삽입한다. 작성자는 본문 + `## 참고 자료`까지만 만든다.

## humanize-korean S1 패턴 — 처음부터 회피 (필수)

전문은 `.sisyphus/skills/humanize-korean/quick-rules.md` 참조. 작성 중 절대 쓰지 말 것:

- **A-1** "~에 대해(서)" → 목적격 조사 직결
- **A-2** "~를 통해/통하여" → "~로/~해서/~함으로써"
- **A-3** "~에 있어서" → "~에서/~을 볼 때"
- **A-7** "가지고 있다" → 형용사형
- **A-8** 이중 피동 "~되어진다" → 능동/단일 피동
- **C-5** 이모지 → 사용 금지 (✅ ❌ → "Pass"/"Fail")
- **D-1** "결론적으로/요약하면/정리하자면"
- **D-2** "시사하는 바가 크다/주목할 만하다"
- **D-4** hype 어휘 (혁신적인/획기적인/압도적인/막강한)
- **D-6** 결말 "~할 때입니다/~할 시점입니다"
- **H-1** 문두 접속사 5회+ ("또한/따라서/즉/나아가/아울러")
- **H-3** 메타 진입 "이는/이 점에서/이 관점에서"
- **I-1** "~한 것이다/~인 것이다" 결말
- **I-3** "~다는 뜻이다/~다는 의미다" 결말
- **I-4** 권고형 결말 "~해야 한다" 5회+
- **J-1** 헤딩 ** 강조 남발

또한 `.sisyphus/style/translation-smells.txt`도 grep 대상 — 작성 후 `.sisyphus/style/check-ko.sh` 통과 필수.

## 이미지 파일 경로

`assets/llm-from-scratch-101/<NN>/<NN>-<idx>-<slug>.{ko|en}.png`

작성 단계에서는 본문에 mermaid 코드블록을 넣어두면 된다. `mermaid-to-png.py`가 나중에 PNG로 바꾸고 본문 mermaid 블록을 이미지 참조로 교체한다.

---

## 9개 포스트 outline

### 01-tokenizer.md — "글자를 숫자로 바꾸기"

**한 문장 핵심:** 모델은 텍스트를 못 읽는다. 정수 시퀀스만 읽는다. 그 변환기가 토크나이저다.

**섹션 구조 (H2):**
1. 도입: GPT한테 "안녕"을 보내면 모델 안에서 무슨 일이? 사실 [50256, 21082] 같은 숫자가 들어간다
2. `## 텍스트는 왜 직접 못 넣나` — 신경망이 받는 입력은 텐서, 단어가 아닌 ID
3. `## 가장 단순한 방법: 문자 단위 토큰화` — 26 letters + 공백, char-level 구현 (10줄 코드)
4. `## 단어 단위 vs 서브워드 — 트레이드오프 한 장` — 어휘 폭발 vs OOV, BPE 등장 배경 (Mermaid: 3-way 비교)
5. `## BPE를 손으로 한 번 — 의미 없는 마법 아니다` — "low/lower/lowest" 5단계 추적, GPT-2 50257 어휘 언급
6. `## tiktoken으로 GPT-2 토크나이저 써보기` — `pip install tiktoken`, encode/decode (15줄)
7. `## 우리 시리즈는 char-level로 간다 — 왜?` — 학습 속도, 디버깅 용이, 어휘 65개
8. `## 데이터 준비: TinyShakespeare 다운로드 + 인코딩` — `data.py` 작성, train.bin/val.bin 저장
9. `## 다음 글 예고` — 정수 시퀀스를 모델에 어떻게 먹일지, 임베딩
10. `## 참고 자료`

**코드 마일스톤:** `data.py` (~40줄)
**Mermaid 1개:** char vs word vs BPE 토큰화 비교

### 02-embedding.md — "정수에서 벡터로, 그리고 위치"

**핵심:** 토큰 ID는 룩업 테이블로 벡터, 위치 정보는 별도 임베딩으로 더한다.

**H2 구조:**
1. 도입: 토큰 ID 5는 ID 6보다 가깝지 않다. 정수에는 의미 거리가 없다
2. `## nn.Embedding은 사실 그냥 룩업 테이블` — `(vocab_size, d_model)`, gradient로 의미 학습
3. `## 직접 만들어보기 — Embedding은 5줄짜리 클래스` — nn.Module mini 구현
4. `## 위치 정보는 어디로 갔지?` — 어텐션은 순서를 모른다, 위치 임베딩 등장
5. `## Sinusoidal vs Learned Positional Embedding` — 원조 vs GPT, 우리는 learned (Mermaid: 두 임베딩 합산)
6. `## 한 토큰의 입력 벡터 = token_emb + pos_emb` — `(B, T, C)` 모양 잡기
7. `## TinyShakespeare 첫 미니배치 만들기` — `get_batch()` 함수, `(4, 8)` shape
8. `## 다음 글 예고` — 어텐션
9. `## 참고 자료`

**코드 마일스톤:** `model.py` 시작 — `class GPT(nn.Module)` 골격 + 임베딩 두 줄
**Mermaid 1개:** 입력 시퀀스 → token emb + pos emb → 합산 → `(B, T, C)`

### 03-attention.md — "어떤 토큰을 얼마나 볼지 스스로 정하기"

**핵심:** 각 토큰이 자기 Query로 다른 토큰들의 Key를 채점하고, 가중치만큼 Value를 가져온다.

**H2 구조:**
1. 도입: "그가 그것을 던졌다"의 '그것'은? 사람도 어텐션을 한다
2. `## QKV는 그냥 세 개의 선형 변환` — 같은 입력에서 세 행렬로 사영
3. `## 점수 계산: Q · K^T / sqrt(d)` — 손으로 4×4 행렬 곱, scaling 이유
4. `## Causal Mask — 미래는 못 본다` — 상삼각 -inf (Mermaid: 4×4 attention before/after mask)
5. `## softmax → V 가중합 → 출력` — 한 헤드 완성, 30줄 PyTorch
6. `## Multi-head: 여러 시선을 동시에` — 차원 분할 병렬, concat → projection
7. `## einsum 없이 nn.Linear와 reshape만` — 디버깅 가능 우선
8. `## 단일 head 출력 한 번 찍어보기` — attention weight 시각화
9. `## 다음 글 예고` — 트랜스포머 블록
10. `## 참고 자료`

**코드 마일스톤:** `class CausalSelfAttention(nn.Module)` (~50줄)
**Mermaid 1개:** Q·K^T → softmax → V 가중합 흐름 + causal mask 위치

### 04-transformer-block.md — "블록 하나, 깊이의 단위"

**핵심:** Attention은 토큰끼리 정보 섞기, FFN은 한 토큰 안 변환. 잔차로 묶는다.

**H2 구조:**
1. 도입: 어텐션만 쌓으면 안 되는 이유 — 비선형성 부족
2. `## FeedForward는 그냥 2-layer MLP` — `Linear(C, 4C) → GELU → Linear(4C, C)`, 4배 확장 이유
3. `## 잔차 연결(Residual) — Skip이 학습을 살린다` — gradient highway
4. `## LayerNorm — Pre-norm vs Post-norm` — GPT-2 이후 Pre-norm 표준 (Mermaid: Pre-norm block)
5. `## Block 한 개 PyTorch 구현 — 25줄` — `class Block(nn.Module)`
6. `## 같은 블록을 N번 쌓는다` — `nn.ModuleList`
7. `## 파라미터 수 계산 — 어디에 가중치가 몰리나` — attention 4C² + FFN 8C², FFN이 2/3
8. `## 다음 글 예고` — 모델 클래스 통합
9. `## 참고 자료`

**코드 마일스톤:** `class Block(nn.Module)` `model.py`에 통합
**Mermaid 1개:** Pre-norm Block 내부 흐름

### 05-gpt-model.md — "조립: GPT 모델 클래스 완성"

**핵심:** 임베딩 + N개 블록 + LayerNorm + LM Head. 끝.

**H2 구조:**
1. 도입: 부품들을 한 클래스에 끼워 맞춘다
2. `## 전체 forward 패스 한눈에 보기` — 입력 ID → emb → blocks → ln_f → lm_head → logits (Mermaid: 전체 모델)
3. `## class GPT(nn.Module) — 80줄짜리 모델` — 전체 init + forward
4. `## LM Head는 사실 Embedding 행렬과 묶을 수 있다 (weight tying)` — 흔한 트릭
5. `## 손실 함수: cross_entropy 한 줄` — `(B, T, vocab) → (B*T, vocab)` reshape
6. `## 모델 인스턴스 한 번 만들고 파라미터 카운트` — ~10M 확인
7. `## sanity check: 학습 전에 한 번 forward` — loss 값(약 ln(65))
8. `## config dataclass로 하이퍼 정리` — `n_layer=6, n_head=4, n_embd=128, block_size=64`
9. `## 다음 글 예고` — 학습 루프
10. `## 참고 자료`

**코드 마일스톤:** `model.py` 완성형 (~150줄), `GPTConfig` dataclass
**Mermaid 1개:** 전체 GPT 아키텍처 한 장

### 06-training-loop.md — "기울기로 배우기"

**핵심:** 미니배치 → forward → loss → backward → optimizer step. 5줄을 5천 번.

**H2 구조:**
1. 도입: 학습은 무겁게 들리지만 PyTorch로는 진짜 5줄
2. `## 학습 루프 5줄의 구조` — `zero_grad / backward / step` 의미
3. `## AdamW가 SGD보다 잘 되는 이유 — 짧게` — 모멘텀 + 분산 적응 + weight decay 분리
4. `## Learning Rate Warmup + Cosine Decay` — 초기 작게 (Mermaid: LR schedule 곡선)
5. `## Gradient Clipping — 폭발 방지 1줄` — `clip_grad_norm_`
6. `## eval_interval로 train/val loss 같이 찍기` — `@torch.no_grad()`, overfit 감지
7. `## train.py 전체 실행 — CPU 5분, GPU 1분` — loss 곡선 (~4.2 → ~1.5)
8. `## 학습된 모델 저장 — torch.save 한 줄` — `.pt` + config
9. `## 다음 글 예고` — 텍스트 생성
10. `## 참고 자료`

**코드 마일스톤:** `train.py` (~100줄), `ckpt.pt` 저장
**Mermaid 1개:** 학습 1 step 데이터 흐름

### 07-inference.md — "샘플링 — 학습된 모델에서 글 뽑아내기"

**핵심:** Logits에서 다음 토큰 선택이 모델 "성격"을 만든다. temperature 하나로 천재가 되거나 미친다.

**H2 구조:**
1. 도입: `model.eval()` 만으론 부족, 자기회귀 생성을 직접 짜야
2. `## 자기회귀 생성 — 한 토큰 뽑고 다시 입력` — `for _ in range(max_new_tokens):` 12줄
3. `## Greedy Decoding — argmax는 왜 지루한가` — 같은 답만, 시연
4. `## Temperature — logits를 나누는 한 숫자` — T=0.5 vs 1.0 vs 1.5 (Mermaid: 분포 변화)
5. `## Top-k 샘플링 — 후보 풀 자르기` — `topk` + `softmax`
6. `## Top-p (Nucleus) 샘플링 — 누적 확률로 자르기` — 더 자연스러운 이유
7. `## Context Window 슬라이딩 — block_size 넘어가면` — `idx[:, -block_size:]` 트릭
8. `## generate.py — 명령줄로 셰익스피어 흉내내기` — `python generate.py --prompt "ROMEO:" --max 200`
9. `## 다음 글 예고` — 파인튜닝
10. `## 참고 자료`

**코드 마일스톤:** `generate.py` (~80줄) + `model.generate()` 메서드
**Mermaid 1개:** 자기회귀 생성 루프 (logits → temp → top-k/p → 샘플링 → context append → 반복)

### 08-finetuning.md — "베이스 모델을 우리 작업에 맞추기"

**핵심:** Pre-train 모델을 작은 instruction 데이터로 한 번 더 학습 → "질문에 답하는" 형태로 형질 변경.

**H2 구조:**
1. 도입: ChatGPT가 GPT-3와 다른 점 — RLHF 전에 SFT, 우리는 SFT만
2. `## Pre-training vs Fine-tuning vs RLHF — 1분 정리` — 세 단계 (Mermaid: 3단계 파이프라인)
3. `## Instruction 데이터 한 줄의 형태` — `{"instruction": ..., "response": ...}`, prompt 템플릿
4. `## 작은 데이터셋 만들기 — 50개로 충분한가` — TinyShakespeare 위에 "Q:/A:" 50쌍
5. `## 학습 루프는 거의 그대로 — 두 가지만 바뀐다` — LR 10× 낮추기, prompt 부분 loss masking
6. `## Loss masking — instruction 토큰은 학습 안 시킨다` — `-100`으로 무시
7. `## finetune.py — train.py에서 30줄만 추가` — diff
8. `## Before/After 비교 출력` — 같은 프롬프트 base vs SFT
9. `## 다음 글 예고` — 챗봇
10. `## 참고 자료`

**코드 마일스톤:** `finetune.py` (~80줄) + `instructions.jsonl` + `ckpt_sft.pt`
**Mermaid 1개:** Pre-training → SFT → RLHF(회색) 3단계 파이프라인

### 09-chatbot-wrapper.md — "직접 만든 LLM을 챗봇으로 — FastAPI + 스트리밍"

**핵심:** 모델은 만들었으니 사람이 쓸 인터페이스가 필요. FastAPI 한 파일 + SSE 스트리밍.

**H2 구조:**
1. 도입: `generate.py`는 일회성. 챗봇은 멀티턴 + 스트리밍 + 동시접속
2. `## 챗봇 = 모델 + 대화 히스토리 + 스트리밍 + UI` — 4 부품 (Mermaid: 사용자 ↔ FastAPI ↔ Model)
3. `## 멀티턴 프롬프트 포맷 디자인` — `User: ...\nBot: ...\nUser: ...\nBot:` 구조
4. `## 모델을 한 번만 로드 — FastAPI startup event` — `@app.on_event("startup")` 글로벌 싱글톤
5. `## /chat 엔드포인트 — 가장 단순한 동기 호출 먼저` — REST POST (~20줄)
6. `## 스트리밍이 왜 필요한가 — 토큰 하나씩 떨어지는 ChatGPT UX` — UX 차이
7. `## SSE(Server-Sent Events)로 토큰 스트리밍` — `StreamingResponse` + `yield`, generator (~30줄)
8. `## 미니멀 HTML 클라이언트 — 50줄짜리 단일 페이지` — `EventSource`
9. `## 실행 — uvicorn 한 번, 브라우저에서 셰익스피어와 대화하기`
10. `## 시리즈 마무리 — 9편을 거쳐 우리가 만든 것` — 누적 ~720 LOC, ~10M 모델, 다음 단계 포인터(LoRA, vLLM, RLHF)
11. `## 참고 자료`

**코드 마일스톤:** `server.py` (~120줄) + `templates/index.html` (~50줄), `uvicorn server:app` 실행
**Mermaid 1개:** 브라우저 ↔ FastAPI ↔ Model.generate (SSE 스트리밍 강조) 시퀀스

---

## 시리즈 누적 코드 LOC (감사용)

| 포스트 | 새 파일/추가 | 누적 LOC |
|---|---|---|
| 01 | `data.py` | ~40 |
| 02 | `model.py` (시작) | ~80 |
| 03 | `model.py` (Attention) | ~140 |
| 04 | `model.py` (Block) | ~170 |
| 05 | `model.py` (완성) | ~250 |
| 06 | `train.py` | ~360 |
| 07 | `generate.py` + `model.generate()` | ~450 |
| 08 | `finetune.py` + `instructions.jsonl` | ~540 |
| 09 | `server.py` + `index.html` | ~720 |

## 시리즈 톤 가이드 (모든 포스트)

- 1인 시니어 회상조 ("저는 ~ 봤습니다", "한 가지 짚자면 ~"). 사무체·강의체 회피.
- 코드 블록 위에는 "이 코드는 ~를 한다" 같은 안내문 금지. 본문에서 자연스럽게 진입.
- 표·코드·다이어그램·산문이 적절히 섞여야 함. 글이 표 위주로만 가면 AI 슬롭.
- 문장 길이 변주 (단문 1~2개 / 장문 1개를 각 문단에 의도적으로). E-1, E-4 회피.
- "예를 들어 ~를 들 수 있습니다" 대신 직접 예시로 진입.
- 코드는 진짜 동작하는 것만. 의사코드·placeholder 금지.

## 시리즈 톤 anti-example (이렇게 쓰지 말 것)

- ❌ "이번 글에서는 토크나이저에 대해 알아보겠습니다." (A-1, J-3 사무체)
- ❌ "토크나이저는 매우 중요한 역할을 가지고 있습니다." (F-1, A-7)
- ❌ "결론적으로 BPE는 혁신적인 알고리즘입니다." (D-1, D-4)
- ❌ "이 점에서 우리는 ~할 필요가 있습니다." (H-3, I-4)

✅ 대안: "토크나이저는 모델로 들어가는 첫 관문입니다. 여기서 한 번 잘못 자르면 다음 단계가 다 흔들립니다."
