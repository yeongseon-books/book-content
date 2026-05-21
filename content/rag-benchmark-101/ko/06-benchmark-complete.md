---
title: "RAG Evaluation and Benchmarking 101 (6/6): RAG 벤치마크 완성"
series: rag-benchmark-101
episode: 6
language: ko
status: publish-ready
targets:
  tistory: true
  medium: false
  mkdocs: true
  ebook: true
tags:
- RAG
- Benchmarking
- Pipeline
- CI
- Reproducibility
- Reporting
last_reviewed: '2026-05-12'
seo_description: 완성된 벤치마크는 같은 설정과 같은 입력에서 같은 결과를 재현할 수 있는 하나의 실행 파이프라인이어야 합니다.
---

# RAG Evaluation and Benchmarking 101 (6/6): RAG 벤치마크 완성

완성된 벤치마크는 같은 설정과 같은 입력에서 같은 결과를 재현할 수 있는 하나의 실행 파이프라인이어야 합니다. 이 글은 RAG Benchmark 101 시리즈의 마지막 글입니다. 여기서는 검색, 생성, 평가를 하나의 실행 파일로 묶고, 회귀를 자동으로 막을 수 있는 보고 체계까지 정리하겠습니다.

![검색, 생성, 평가가 한 번의 실행으로 이어지는 파이프라인](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/06/06-01-end-to-end-benchmark-pipeline-in-one-run.ko.png)
*검색, 생성, 평가가 한 번의 실행으로 이어지는 파이프라인*
> 완성된 RAG 벤치마크는 **숫자 하나**가 아닙니다. 검색과 생성을 분리하면서도 같은 실험 조건에서 반복 실행할 수 있는 재현 가능한 파이프라인입니다.

## 먼저 던지는 질문

- 벤치마크를 한 번 실행하는 스크립트에서 반복 가능한 의사결정 도구로 바꾸려면 무엇이 필요할까요?
- 자동 리포트는 평균 점수뿐 아니라 어떤 실패 사례를 보여 줘야 할까요?
- CI에 벤치마크를 붙일 때 어떤 회귀 기준을 차단선으로 삼아야 할까요?

## 왜 이 주제가 중요한가

지금까지 만든 도구가 노트북 여기저기에 흩어져 있으면 실제 의사결정에는 잘 쓰이지 않습니다. 사람이 매번 손으로 돌려야 하는 측정은 결국 누락되기 쉽고, 그러면 시스템 품질에 대한 판단은 다시 "최근 몇 개 답변이 어땠는가" 수준으로 후퇴합니다.

반대로 하나의 실행 파일과 표준 리포트로 묶어 두면 네 가지가 가능해집니다.

- **PR 회귀 감지** — 변경 전후 점수를 자동 비교할 수 있습니다.
- **후보 비교** — 임베딩 모델, VectorDB, LLM을 동일 조건에서 비교할 수 있습니다.
- **운영 추적** — 야간 작업으로 추세를 계속 기록할 수 있습니다.
- **재현성 확보** — 몇 달 뒤에도 같은 설정으로 다시 돌려 동일한 비교를 할 수 있습니다.

이 글의 목표는 화려한 대시보드가 아니라, 위 네 가지를 가능하게 만드는 최소 구조를 세우는 것입니다.

## 기본 멘탈 모델

완성된 벤치마크는 하나의 함수로 생각할 수 있습니다.

```text
run_benchmark(config) ──►  report
   │
   ├─ Phase 1: build retriever (corpus + embedding + index)
   ├─ Phase 2: run queries → collect (ranked_ids, latency, contexts)
   ├─ Phase 3: generate answers via LLM
   ├─ Phase 4: compute retrieval metrics (hit, MRR, latency)
   ├─ Phase 5: compute generation metrics (faithfulness, answer_relevancy)
   └─ Phase 6: emit report (JSON + per-question log)
```

`config`에는 임베딩 모델, top-k, LLM 모델, 데이터셋 경로 같은 모든 실험 변수가 들어갑니다. 같은 `config`를 사용하면 같은 결과가 나와야 한다는 것이 이 파이프라인의 계약입니다.

## 핵심 개념

| 항목 | 의미 |
| --- | --- |
| Run config | 한 번의 벤치마크 실행에 필요한 모든 파라미터 |
| Run id | 각 실행을 식별하는 고유 ID |
| Report | 집계 지표와 질문별 로그 두 부분으로 이루어진 결과 |
| Baseline | 비교 대상이 되는 이전 실행 결과 |
| Regression | baseline 대비 임계치 이상 점수가 떨어진 상황 |

집계와 질문별 로그를 분리하는 이유는 분명합니다. 집계만 있으면 왜 점수가 떨어졌는지 알 수 없고, 질문별 로그만 있으면 빠른 비교가 어렵습니다. 둘이 함께 있어야 운영 가능한 리포트가 됩니다.

## 수동 점검만 할 때와 자동 리포트가 있을 때

이전에는 PR 작성자가 노트북을 열어 몇 가지 지표를 손으로 확인합니다. 어떤 PR은 평가하고 어떤 PR은 잊습니다. 한 달 뒤 성능 저하가 발견되어도 어느 변경이 원인인지 추적하기 어렵습니다.

이후에는 모든 PR이 같은 명령을 자동으로 실행합니다.

```text
                  baseline  this PR  delta
hit_rate@3        0.94      0.96    +0.02 ✓
MRR               0.78      0.81    +0.03 ✓
faithfulness      0.91      0.84    -0.07 ✗
answer_relevancy  0.85      0.86    +0.01 ✓
avg_latency_ms    62.1      63.4    +1.3
```

예를 들어 faithfulness가 0.07 떨어졌다면 사람이 놓치기 전에 CI가 바로 차단할 수 있습니다. 회귀 감지가 자동화된 상태가 되는 것입니다.

## 단계별로 통합 벤치마크 만들기

### 1단계 — 실행 설정 고정하기

```yaml
# configs/ci.yaml
corpus_path: "data/corpus.jsonl"
gold_set_path: "data/gold.jsonl"
embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
index_type: "IndexFlatIP"
top_k: 3
llm_model: "llama-3.1-8b-instant"
ragas_metrics: ["faithfulness", "answer_relevancy"]
```

실험 변수는 코드 곳곳에 흩어져 있으면 안 됩니다. 설정 파일 한곳에 모아야 비교가 재현 가능해집니다.

### 2단계 — 검색, 생성, 평가를 하나의 함수로 묶기

실행 코드는 `rag-benchmark-101/en/06-benchmark-complete/main.py`에 있습니다. `GROQ_API_KEY`가 필요합니다.

```bash
cd en/06-benchmark-complete
export GROQ_API_KEY=...
python3 main.py
```

```python
def run_benchmark(config):
    retriever = build_retriever(config)
    rows, retrieval_metrics = [], []

    for case in load_gold_set(config["gold_set_path"]):
        t0 = time.perf_counter()
        docs = retriever.invoke(case["question"])
        latency_ms = (time.perf_counter() - t0) * 1000

        ranked = [d.metadata["id"] for d in docs]
        contexts = [d.page_content for d in docs]
        retrieval_metrics.append({
            "hit": hit_rate(ranked, case["gold"]),
            "rr": reciprocal_rank(ranked, case["gold"]),
            "latency_ms": latency_ms,
        })

        answer = generate_answer(case["question"], contexts, config)
        rows.append({
            "question": case["question"],
            "contexts": contexts,
            "answer": answer,
            "ranked_ids": ranked,
        })

    ragas_scores = run_ragas(rows, config)
    return assemble_report(retrieval_metrics, ragas_scores, rows, config)
```

이 함수가 중요한 이유는 측정 층이 하나의 실행 흐름 안에 들어 있기 때문입니다. 검색과 생성을 따로 재면 실행 조건이 어긋나기 쉽습니다.

### 3단계 — 리포트를 검색과 생성으로 분리하기

![검색 리포트와 생성 리포트를 나누는 구조](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/06/06-02-retrieval-and-generation-report-split.ko.png)

*검색 리포트와 생성 리포트를 나누는 구조*

```python
def assemble_report(retrieval_metrics, ragas_scores, rows, config):
    return {
        "run_id": f"{datetime.utcnow():%Y%m%dT%H%M%S}-{git_sha()[:7]}",
        "config": config,
        "retrieval": {
            "hit_rate@k": mean([m["hit"] for m in retrieval_metrics]),
            "MRR": mean([m["rr"] for m in retrieval_metrics]),
            "avg_latency_ms": mean([m["latency_ms"] for m in retrieval_metrics]),
            "p95_latency_ms": percentile([m["latency_ms"] for m in retrieval_metrics], 95),
        },
        "generation": {
            "faithfulness": ragas_scores["faithfulness"],
            "answer_relevancy": ragas_scores["answer_relevancy"],
        },
        "per_question": rows,
    }
```

점수를 하나로 합쳐 버리면 어느 층이 무너졌는지 알 수 없습니다. 따라서 retrieval과 generation은 끝까지 분리된 키 아래 유지해야 합니다.

### 4단계 — baseline과 비교하기

```python
def compare(report, baseline):
    deltas = {}
    for layer in ["retrieval", "generation"]:
        for k, v in report[layer].items():
            base = baseline[layer].get(k)
            if isinstance(v, (int, float)) and isinstance(base, (int, float)):
                deltas[f"{layer}.{k}"] = v - base
    return deltas
```

비교 로직은 단순해 보여도 매우 중요합니다. 자동 비교가 있어야 같은 리포트를 사람이 일일이 읽지 않아도 회귀를 잡을 수 있습니다.

### 5단계 — CI 게이트 만들기

![검색 문제와 생성 문제를 분기해 차단하는 흐름](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/06/06-03-branching-search-failures-from-generatio.ko.png)

*검색 문제와 생성 문제를 분기해 차단하는 흐름*

```python
THRESHOLDS = {
    "retrieval.hit_rate@k": -0.02,
    "generation.faithfulness": -0.03,
}

def gate(deltas):
    failed = [k for k, t in THRESHOLDS.items() if deltas.get(k, 0) < t]
    if failed:
        sys.exit(f"Regression in: {failed}")
```

처음에는 경고 수준으로 시작해도 좋습니다. 하지만 일정 기간 안정화가 되면, 최소한 핵심 지표 하나는 실제 차단 조건으로 승격하는 편이 좋습니다.

## 자주 하는 실수

- **점수 하나로 압축하기** — 어느 층이 망가졌는지 설명할 수 없게 됩니다.
- **질문별 로그를 버리기** — 집계만 남기면 회귀 원인을 찾을 수 없습니다.
- **Baseline을 매번 자동 갱신하기** — 점진적 성능 저하가 누적될 수 있습니다.
- **설정을 코드에 흩뿌리기** — top-k, temperature, 모델 이름이 실행마다 다르면 비교가 무의미합니다.
- **외부 LLM 호출의 retry와 timeout을 무시하기** — CI가 쉽게 flaky해집니다.

## 운영 환경으로 가져갈 때

운영에서는 `run_id`에 git sha를 포함하는 것이 좋습니다. 그래야 결과와 코드를 1:1로 묶을 수 있습니다. 또한 토큰 사용량과 예상 비용도 리포트에 포함하면, 품질 개선이 비용 증가를 얼마나 동반하는지 함께 볼 수 있습니다.

데이터셋이 커지면 병렬 실행과 캐싱도 중요해집니다. 다만 병렬화는 무조건 내부 평가 라이브러리에만 맡기기보다, 샤딩 후 외부에서 합치는 방식이 더 안정적일 때가 많습니다. 또 이미 본 `(question, context)` 쌍의 답변을 재사용하면 CI 비용을 크게 줄일 수 있습니다.

무엇보다 벤치마크는 자동으로 돌고, 결과가 팀이 자주 보는 곳에 노출되어야 합니다. 대시보드든 PR 코멘트든, 측정 결과가 흐르지 않으면 벤치마크는 곧 잊힙니다.

## 체크리스트

![기준선 비교부터 의사결정까지 이어지는 벤치마크 루프](https://yeongseon-books.github.io/book-public-assets/assets/rag-benchmark-101/06/06-04-baseline-to-decision-benchmark-loop.ko.png)

*기준선 비교부터 의사결정까지 이어지는 벤치마크 루프*

- [ ] 검색과 생성을 같은 실행 안에서 측정하는가?
- [ ] 두 층의 점수를 분리된 키 아래 저장하는가?
- [ ] 설정 파일에 임베딩 모델, top-k, LLM 모델, 데이터셋 경로가 모두 들어 있는가?
- [ ] `run_id`에 시각과 git sha가 들어가는가?
- [ ] 집계 리포트와 질문별 로그를 함께 저장하는가?
- [ ] baseline과 비교해 임계치 위반 시 차단하는가?
- [ ] 모든 LLM 호출에 retry와 timeout을 적용하는가?

## 연습 문제

1. 임베딩 모델 2개와 LLM 2개를 조합해 총 4개 실험을 한 번에 실행하도록 확장해 보세요.
2. 같은 git sha에서 두 번 실행했는데 결과가 다르다면, 어떤 비결정성이 남아 있는지 점검해 보세요.
3. 데이터셋 크기에 따라 CI 임계치를 다르게 두는 방식은 어떻게 설계할 수 있을까요?

## 정리와 시리즈 마무리

이 시리즈에서는 여섯 편에 걸쳐 다음을 만들었습니다.

| 글 | 도구 |
| --- | --- |
| 1 | hit rate / MRR / nDCG를 손으로 읽는 기본 감각 |
| 2 | 단일 검색기를 계량하는 검색 측정 루프 |
| 3 | 임베딩 모델을 한 변수씩 비교하는 실험 골격 |
| 4 | flat과 IVF의 recall/latency 트레이드오프 비교 |
| 5 | RAGAS를 이용한 faithfulness / answer relevancy 평가 |
| 6 | 검색·생성·평가를 묶은 통합 벤치마크와 CI 게이트 |

이 시리즈의 핵심은 단일 점수를 만드는 데 있지 않습니다. **같은 조건에서 반복 가능한 측정을 만들고, 점수가 흔들릴 때 어느 층을 고쳐야 하는지 분명하게 만드는 것**이 핵심입니다.

이후 확장 주제로는 더 긴 코퍼스, 하이브리드 검색기, reranker, 다회전 대화 평가가 자연스럽게 이어질 수 있습니다. 하지만 그 확장도 결국 같은 원칙 위에 서야 합니다. 먼저 변수와 측정 조건을 고정하고, 그다음에 비교해야 합니다.

## 통합 벤치마크를 운영 파이프라인으로 고정하는 설계

시리즈 마지막 단계에서는 "실험 코드"를 "운영 파이프라인"으로 바꾸는 작업이 필요합니다. 핵심은 실행 절차와 산출물 포맷을 표준화해 누구나 같은 방식으로 돌릴 수 있게 만드는 것입니다.

### 권장 디렉터리 구조

```text
rag-benchmark/
  configs/
    ci.yaml
    nightly.yaml
  data/
    corpus.jsonl
    gold_queries.jsonl
  reports/
    baseline.json
    latest.json
    history/
  src/
    run_benchmark.py
    compare_reports.py
    render_markdown.py
```

구조가 고정되어 있으면 CI, 로컬 실행, 야간 배치가 같은 경로를 공유할 수 있어 운영 부담이 줄어듭니다.

### 실행 설정에 포함해야 할 필수 항목

```yaml
run:
  seed: 42
  sample_size: 200
  top_k: 5
retrieval:
  embedding_model: sentence-transformers/all-MiniLM-L6-v2
  index_type: ivf
  nprobe: 8
generation:
  llm_model: llama-3.1-8b-instant
  temperature: 0
evaluation:
  metrics: [faithfulness, answer_relevancy]
  max_workers: 1
  timeout_sec: 300
```

`seed`와 `sample_size`를 남기면 샘플링 기반 평가에서도 비교 가능성을 유지할 수 있습니다.

### 통합 리포트 JSON 스키마 예시

```json
{
  "run_id": "20260521T020500-1a2b3c4",
  "git_sha": "1a2b3c4d",
  "config_hash": "f2fcbf...",
  "retrieval": {
    "hit_rate@5": 0.93,
    "mrr": 0.79,
    "avg_latency_ms": 58.4,
    "p95_latency_ms": 91.2
  },
  "generation": {
    "faithfulness": 0.88,
    "answer_relevancy": 0.86
  },
  "cost": {
    "prompt_tokens": 421991,
    "completion_tokens": 109823,
    "estimated_usd": 7.42
  },
  "per_question": []
}
```

`config_hash`를 추가하면 같은 실행 조건인지 자동 판별할 수 있습니다.

### 회귀 판정 규칙을 레이어별로 나누기

통합 벤치마크는 회귀를 한 줄로 판정하면 위험합니다. 검색과 생성을 분리한 게이트가 필요합니다.

| 레이어 | 지표 | 차단 기준 예시 |
| --- | --- | --- |
| Retrieval | hit_rate@5 | baseline 대비 -0.03 미만 |
| Retrieval | p95_latency_ms | baseline 대비 +25ms 초과 |
| Generation | faithfulness | baseline 대비 -0.04 미만 |
| Generation | answer_relevancy | baseline 대비 -0.03 미만 |

이 규칙은 품질 하락과 지연 증가를 동시에 감시합니다. 한쪽만 보면 다른 쪽 악화를 놓치기 쉽습니다.

### CI 워크플로 예시

```yaml
name: rag-benchmark-gate
on:
  pull_request:
    branches: [main]

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -r requirements.txt
      - run: python src/run_benchmark.py --config configs/ci.yaml --out reports/latest.json
      - run: python src/compare_reports.py --baseline reports/baseline.json --current reports/latest.json
```

이 워크플로는 최소 구조입니다. 실제 환경에서는 캐시, 아티팩트 업로드, 실패 시 샘플 로그 첨부를 추가하는 편이 좋습니다.

### 사람이 읽는 요약 리포트 생성

JSON만으로는 협업이 어렵기 때문에 Markdown 요약을 자동 생성하는 단계를 함께 두면 효과적입니다.

```python
def render_summary_md(report: dict) -> str:
    return f"""
## RAG Benchmark Report

- run_id: {report['run_id']}
- retrieval.hit_rate@5: {report['retrieval']['hit_rate@5']:.3f}
- retrieval.mrr: {report['retrieval']['mrr']:.3f}
- generation.faithfulness: {report['generation']['faithfulness']:.3f}
- generation.answer_relevancy: {report['generation']['answer_relevancy']:.3f}
""".strip()
```

이 요약을 PR 코멘트에 자동 첨부하면, 리뷰어가 원본 JSON을 열지 않아도 핵심 변화를 빠르게 파악할 수 있습니다.

### 장애 대응 관점의 운영 런북 항목

벤치마크 파이프라인도 운영 시스템이므로 장애 대응 절차가 필요합니다.

1. 외부 LLM API 타임아웃 발생 시 재시도 횟수와 백오프 정책 확인
2. VectorDB 연결 실패 시 fallback 인덱스 사용 여부 확인
3. baseline 파일 손상 시 마지막 정상 실행에서 복구
4. 평가 비용 급등 시 샘플 수 자동 축소 모드로 전환

런북을 벤치마크 코드와 같은 저장소에 두면 온콜 상황에서 훨씬 빠르게 복구할 수 있습니다.

### 보고 체계를 분기/월 단위로 축적하기

단일 실행 결과만 보면 추세를 읽기 어렵습니다. 최소한 아래 두 축을 같이 저장하면 장기 품질 관리가 가능해집니다.

| 축 | 저장 항목 |
| --- | --- |
| 브랜치/PR | baseline 대비 delta, 실패 질문 목록 |
| 월간 추세 | 7일 이동평균, 분산, 회귀 발생 빈도 |

추세 데이터를 축적하면 "최근 품질이 떨어졌다"를 감으로 말하지 않고, 실제 숫자로 설명할 수 있습니다.

## 실전 부록: 통합 벤치마크 운영 체크포인트

마지막으로, 통합 파이프라인을 실제 조직에서 유지하기 위한 운영 체크포인트를 정리합니다.

### 실행 단계별 산출물 규약

| 단계 | 산출물 | 저장 경로 예시 |
| --- | --- | --- |
| retrieval 실행 | 질문별 ranked_ids, latency | `reports/run_id/retrieval.jsonl` |
| generation 실행 | 질문별 answer, prompt 토큰 | `reports/run_id/generation.jsonl` |
| evaluation 실행 | faithfulness, answer relevancy | `reports/run_id/eval.jsonl` |
| 통합 리포트 | aggregate + delta + 실패 목록 | `reports/run_id/summary.json` |

산출물 규약이 있어야 장애 시 특정 단계만 재실행할 수 있습니다.

### 실패 재현 명령을 리포트에 포함하기

리포트에 아래 정보가 없으면 실패한 실행을 다시 재현하기 어렵습니다.

```text
reproduce_command:
python src/run_benchmark.py --config configs/ci.yaml --run-id 20260521T020500-1a2b3c4
```

한 줄 명령을 같이 저장해 두면 온콜 상황에서도 빠르게 재현할 수 있습니다.

### 비용 가드레일 추가

품질 회귀만 막고 비용 급등을 놓치는 경우가 많습니다. 비용 가드레일을 같이 두는 편이 안전합니다.

| 항목 | 경고 기준 | 차단 기준 |
| --- | ---: | ---: |
| 실행당 평가 비용(USD) | +20% | +35% |
| 질문당 평균 토큰 | +15% | +25% |
| 월간 예상 비용 | 예산 90% 도달 | 예산 초과 |

이 기준을 넘으면 성능 개선이 있어도 릴리스를 재검토해야 합니다.

### 배포 전 승인용 요약 템플릿

```text
Release Candidate Benchmark Review
- Retrieval: hit@5 0.93 (+0.01), MRR 0.80 (+0.02), p95 92ms (+4ms)
- Generation: faithfulness 0.89 (+0.01), answer_relevancy 0.87 (+0.00)
- Cost: +8.4% within budget
- Decision: PASS (no blocking regression)
```

승인 템플릿을 정해 두면 릴리스 회의가 수치 중심으로 정리됩니다.

### 장기 유지보수에서 자주 발생하는 이슈

1. baseline이 오래되어 현재 데이터 분포를 반영하지 못하는 문제
2. 평가 모델 버전 변경 후 과거 점수와 직접 비교하는 문제
3. 코퍼스 갱신 주기와 벤치마크 주기가 어긋나는 문제
4. 질문 샘플링 편향으로 특정 도메인 회귀를 놓치는 문제

이 이슈를 피하려면 baseline 갱신 정책, 평가자 버전 정책, 데이터 동기화 정책을 별도 문서로 유지해야 합니다.

### 운영 점검용 주간 체크리스트

- 지난 7일 기준 `faithfulness`, `MRR`, `p95 latency` 이동평균을 확인합니다.
- 회귀 차단으로 실패한 PR의 공통 원인을 분류합니다.
- 실패 질문 상위 20개가 동일 질문군에 편중되는지 확인합니다.
- 평가 비용이 예산 대비 정상 범위인지 검토합니다.
- baseline 갱신 필요 여부를 결정하고 기록합니다.

이 체크리스트를 정기적으로 수행하면 벤치마크가 일회성 이벤트가 아니라 지속적인 품질 관리 루프로 유지됩니다.

여기에 더해, 분기마다 벤치마크 데이터셋 대표성을 점검하는 절차를 넣는 편이 좋습니다. 제품 기능이 바뀌면 사용자 질문 분포도 바뀌기 때문에, 오래된 질문 세트만으로는 최신 회귀를 놓칠 수 있습니다. 대표성 점검은 벤치마크 유지비용을 줄이는 것이 아니라, 잘못된 안전감으로 인한 운영 리스크를 줄이는 투자입니다.

## 처음 질문으로 돌아가기

- **벤치마크를 한 번 실행하는 스크립트에서 반복 가능한 의사결정 도구로 바꾸려면 무엇이 필요할까요?**
  고정된 데이터셋, 버전 기록, 재현 가능한 실행 명령, 구조화된 JSON 결과, 사람이 읽는 리포트, 회귀 기준이 필요합니다.

- **자동 리포트는 평균 점수뿐 아니라 어떤 실패 사례를 보여 줘야 할까요?**
  평균뿐 아니라 최악의 질문, 점수 하락 쿼리, latency 증가, 실패 원문, 이전 실행 대비 diff를 보여 줘야 합니다.

- **CI에 벤치마크를 붙일 때 어떤 회귀 기준을 차단선으로 삼아야 할까요?**
  Recall, MRR, faithfulness, latency 같은 핵심 지표가 정한 허용 폭을 넘게 하락하거나 증가하면 CI에서 차단해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [RAG Evaluation and Benchmarking 101 (1/6): RAG 평가 지표 이해](./01-evaluation-metrics.md)
- [RAG Evaluation and Benchmarking 101 (2/6): 검색 성능 측정](./02-retrieval-benchmarking.md)
- [RAG Evaluation and Benchmarking 101 (3/6): 임베딩 모델 비교](./03-embedding-comparison.md)
- [RAG Evaluation and Benchmarking 101 (4/6): VectorDB 선택 기준](./04-vectordb-selection.md)
- [RAG Evaluation and Benchmarking 101 (5/6): 종단 간 RAG 파이프라인 평가](./05-e2e-evaluation.md)
- **RAG Evaluation and Benchmarking 101 (6/6): RAG 벤치마크 완성 (현재 글)**

<!-- toc:end -->

---

## 참고 자료

- [RAGAS documentation](https://docs.ragas.io/)
- [LangChain retrieval overview](https://python.langchain.com/docs/concepts/retrieval/)
- [FAISS documentation](https://faiss.ai/)
- [GitHub Actions](https://docs.github.com/en/actions)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/rag-benchmark-101/ko/06-benchmark-complete)

Tags: RAG, VectorDB, Benchmarking, LLM
