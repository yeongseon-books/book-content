---
title: "Korean AI Stack 101 (4/6): Document text extraction with CLOVA OCR API"
series: korean-ai-stack-101
episode: 4
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Korean NLP
- CLOVA
- OCR
- NaverCloud
- DocumentAI
- Python
last_reviewed: '2026-05-01'
seo_description: Master Korean document text extraction with CLOVA OCR. Learn to post-process JSON, reconstruct lines, and handle confidence scores for RAG.
---

# Korean AI Stack 101 (4/6): Document text extraction with CLOVA OCR API

Korean search and RAG pipelines often fail long before retrieval because the source material starts as scans, receipts, or photographed documents. If OCR breaks a meaningful line into the wrong pieces, every downstream embedding and ranking decision inherits that damage.

This is the fourth post in the Korean AI Stack 101 series. Here, we turn CLOVA OCR responses into line-level text that can safely enter a retrieval corpus.

![Korean AI Stack 101 chapter 4 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/04/04-01-core-flow.en.png)
*Korean AI Stack 101 chapter 4 flow overview*

> Korean OCR is not a solved problem — vertical text, mixed-script receipts, and bank statements break general-purpose OCR in ways that only a domain-tuned engine like CLOVA reliably handles, and the gap shows up directly in downstream RAG quality.

## Questions to Keep in Mind

- When you add OCR, should you inspect text accuracy first, or response structure first?
- Why do bounding boxes and `lineBreak` hints matter so much in post-processing?
- Why can you validate most of the OCR pipeline even without a real API key?

## Why this matters

This post processes Korean document images — receipts, tax invoices, scanned forms — with the CLOVA OCR API and shapes the result so it can drop into the BGE-M3 corpus from the previous post. The previous post handled multilingual retrieval over text. Here we make the source text in the first place.

OCR deserves its own stage because half of Korean enterprise search begins with PDFs, scanned images, or phone photos. A single misaligned line break in OCR turns "공급가액 45,000원" ("amount 45,000 KRW") into two separate documents — "공급가액" and "45,000원" — and semantic retrieval fails. CLOVA OCR is well tuned for Korean, so token accuracy is high. The hard work lives in post-processing the JSON payload back into lines, paragraphs, and table cells. This post defaults to a bundled mock response so the post-processing logic can be exercised without a key.

## Mental Model

The OCR pipeline has four stages.

```text
[document image / PDF]
       |
       v
[CLOVA OCR API call]  --> JSON payload (fields, bbox, confidence, lineBreak)
       |
       v
[post-process: reconstruct lines / paragraphs / tables]  <-- format checks
       |
       v
[clean text + meta] --> BGE-M3 / RAG corpus
```

Three things matter most:

- **The API only returns a `fields` array**: line breaks, paragraphs, and table structure must be reconstructed from `lineBreak` and coordinates.
- **Confidence is not truth**: a 0.99 token can be wrong; a 0.85 token can be right. Look at distributions, not absolute thresholds.
- **Mock-first is safer**: the response JSON is reproducible in code without a key, so CI can validate post-processing deterministically.

Two more facts:

- CLOVA OCR has two flavors. General OCR for free-form documents, Template OCR for fixed forms (receipts, ID cards) with field auto-mapping.
- Each field carries `inferText`, `inferConfidence`, `boundingPoly`, and `lineBreak`. This post focuses on the most common pair, `inferText` + `lineBreak`.

## Core concepts

| Item | Meaning |
| --- | --- |
| CLOVA OCR | NAVER Cloud Platform OCR API tuned for Korean |
| General OCR | Free-form documents. Returns coordinates and line metadata |
| Template OCR | Fixed forms (receipts, IDs). Auto-maps to declared field names |
| `inferText` | Recognized text token |
| `inferConfidence` | Recognition confidence (0-1) |
| `boundingPoly` | Four-point polygon for the token |
| `lineBreak` | Whether this token closes a line (boolean) |
| Mock response | A code-built JSON with the same shape, used to test post-processing without API calls |

## Before vs. After

**Before** — Indexing the raw payload directly puts each `inferText` token into the corpus as its own snippet. Retrieval treats "공급가액" and "45,000원" as separate documents and loses the meaning unit "공급가액 45,000원".

**After** — Reconstructing lines from `lineBreak` first produces a corpus like:

```python
# Post-processed output (one line per document)
'공급가액 45,000원'      # confidence min: 0.994
'부가세 4,500원'          # confidence min: 0.991
'합계 49,500원'           # confidence min: 0.989
```

What matters: (1) lines are bound at the meaning level so BGE-M3 retrieval lifts the right line, (2) per-line minimum confidence is preserved for downstream review, and (3) the raw payload is kept around so the pipeline can be reprocessed at any time.

## Why start from a mock payload

![Minimal runnable example](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/04/04-01-minimal-runnable-example.en.png)

*Minimal runnable example*

Most OCR integration pain lives after the API call. Teams hit issues with row order, broken line reconstruction, and split numbers long before they hit authentication issues. Reproducing a mock payload in code first means CI can validate the same input the same way every time, and the only diff when a real key arrives is the line that fetches the response.

## Step-by-step practice

### Step 1 — Define the mock response

```python
MOCK_RESPONSE = {
    'images': [
        {
            'fields': [
                {'inferText': '공급가액', 'inferConfidence': 0.997, 'lineBreak': False},
                {'inferText': '45,000원', 'inferConfidence': 0.994, 'lineBreak': True},
                {'inferText': '부가세',   'inferConfidence': 0.996, 'lineBreak': False},
                {'inferText': '4,500원',  'inferConfidence': 0.991, 'lineBreak': True},
                {'inferText': '합계',     'inferConfidence': 0.998, 'lineBreak': False},
                {'inferText': '49,500원', 'inferConfidence': 0.989, 'lineBreak': True},
            ]
        }
    ]
}
```

Once a real key is available, swap the dict construction for `requests.post(...).json()`.

### Step 2 — Reconstruct lines

![What to notice in this code](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/04/04-02-what-to-notice-in-this-code.en.png)

*What to notice in this code*

```python
def reconstruct_lines(payload):
    lines = []
    for image in payload['images']:
        current_text, current_conf = [], []
        for field in image['fields']:
            current_text.append(field['inferText'])
            current_conf.append(field['inferConfidence'])
            if field['lineBreak']:
                lines.append({
                    'text': ' '.join(current_text),
                    'min_confidence': min(current_conf),
                })
                current_text, current_conf = [], []
    return lines

lines = reconstruct_lines(MOCK_RESPONSE)
for line in lines:
    print(f"{line['min_confidence']:.3f}  {line['text']}")
```

Group tokens by `lineBreak` and carry the per-line minimum confidence. This one tiny function handles roughly 90% of receipt and invoice post-processing.

### Step 3 — Numeric and amount validation

```python
import re

AMOUNT_RE = re.compile(r'^[\d,]+원$')

for line in lines:
    tokens = line['text'].split()
    amounts = [t for t in tokens if AMOUNT_RE.match(t)]
    if not amounts and ('원' in line['text']):
        print('WARN suspicious amount format:', line['text'])
```

OCR sometimes reads "45,000원" as "45.000원". A domain regex catches more real bugs than a confidence threshold ever will.

### Step 4 — Shape into a corpus document

```python
def to_corpus_doc(image_id, lines):
    return {
        'image_id': image_id,
        'lines': [line['text'] for line in lines],
        'min_confidence': min(line['min_confidence'] for line in lines),
        'raw_payload_path': f's3://ocr-raw/{image_id}.json',
    }

doc = to_corpus_doc('receipt_001', lines)
print(doc)
```

Storing the raw payload path beside the text keeps reprocessing simple when the OCR model is upgraded. Text-only storage loses provenance.

### Step 5 — Swap in the real API call (optional)

```python
import os, requests

def call_clova_ocr(image_path):
    url = os.environ['CLOVA_OCR_URL']
    secret = os.environ['CLOVA_OCR_SECRET']
    headers = {'X-OCR-SECRET': secret}
    files = {'file': open(image_path, 'rb')}
    data = {'message': '{"version":"V2","requestId":"x","timestamp":0,"images":[{"format":"jpg","name":"x"}]}'}
    return requests.post(url, headers=headers, files=files, data=data).json()
```

Returns the same shape as the mock dict, so steps 1-4 stay unchanged.

## What to notice in this code

- The reader inspects `lineBreak` as carefully as `inferText`. That single habit drives table and receipt accuracy.
- Per-line minimum confidence creates a natural triage queue for downstream review.
- Keeping raw payload + post-processed text together is the single biggest asset for future model swaps.
- Even with a real key in place, keeping the mock test in CI makes the build deterministic.

## Common mistakes

![Where engineers get confused](https://yeongseon-books.github.io/book-public-assets/assets/korean-ai-stack-101/04/04-03-where-engineers-get-confused.en.png)

*Where engineers get confused*

- **Assuming higher OCR accuracy means better RAG** — token accuracy and meaning-unit accuracy are different problems. Bad line reconstruction defeats 99% OCR.
- **Using absolute confidence thresholds** — a 0.95 cutoff means different things across model versions. Prefer reviewing the bottom 5% of the score distribution.
- **Treating PDF and image OCR identically** — PDFs may carry a real text layer. `pdfplumber` is faster and more accurate when one exists. Always check for a text layer first.
- **Discarding the raw payload** — replacing the OCR model later forces a re-call from scratch. Cost and latency are nontrivial.
- **Multi-column layout collapsed to single lines** — without `boundingPoly`, multi-column documents merge incorrectly. Group by x-coordinate when columns matter.
- **Mock paths inside production code paths** — without an explicit env switch, mock data can leak into production. Use something like `os.environ.get('CLOVA_OCR_MODE', 'mock')`.

## Production application

- **Two-stage OCR**: General OCR for the whole page, Template OCR re-applied to specific zones (receipts, IDs). Cost and accuracy stay balanced.
- **PDF branching**: try `pdfplumber` first; fall back to OCR only for pages without a text layer. Often cuts cost by 70%+.
- **Reprocessing queue**: tag the bottom 5% of confidence lines as `needs_review` and route to humans. More effective than absolute alerts.
- **Table reconstruction**: group rows by y-coordinate of `boundingPoly` and sort columns by x-coordinate. `lineBreak` alone is not enough.
- **Image preprocessing**: deskew, denoise, and binarize before the OCR call. Average confidence often rises by 0.05-0.1 with one-line OpenCV calls.
- **Monitoring**: dashboard daily volume, mean confidence, and reconstruction-failure rate. Model upgrades make all three drift visibly.

## Checklist

- [ ] Raw payload and post-processed text are stored together.
- [ ] Decided which of `lineBreak`, coordinates, or confidence are required downstream.
- [ ] Amounts, dates, and identifiers have dedicated regex validation.
- [ ] Line/paragraph reconstruction is verified before the embedding step.
- [ ] A mock-first test is part of CI.

## Exercises

1. Add three more lines to the mock response and intentionally insert two consecutive `lineBreak: False` fields. Observe how the reconstruction function handles it and discuss how to harden it.
2. Build a mock response with `boundingPoly` populated and write a function that splits left and right columns by x-coordinate.
3. Write a wrapper function that tries `pdfplumber` first on a PDF page and only falls back to a mock CLOVA call when no text layer is present.

## Summary · Next article

The value of the CLOVA OCR example is that it puts response-shape understanding ahead of text accuracy. Three small commitments — group by `lineBreak`, preserve per-line confidence, store the raw payload — keep OCR safe to feed into a RAG corpus. Once that step is clean, the next post can reason clearly about which context gets handed to a generation API.

The next article (episode 5) covers HyperCLOVA X and Solar API. We will look at safe prompt patterns when handing OCR text or BGE-M3 retrieval results to a Korean LLM, with concrete API call code.

## Separating the OCR Post-Processing Pipeline by Function Boundaries

In practice, OCR quality issues arrive all at once — line reconstruction failures, number format errors, and column merge errors appear simultaneously, making root-cause analysis slow. Splitting by function boundary first lets you isolate failure points in logs.

```python
def extract_fields(payload):
    for image in payload.get('images', []):
        for field in image.get('fields', []):
            yield {
                'text': field.get('inferText', ''),
                'confidence': float(field.get('inferConfidence', 0.0)),
                'line_break': bool(field.get('lineBreak', False)),
                'poly': field.get('boundingPoly', {}),
            }

def reconstruct_lines_from_fields(fields):
    lines = []
    cur_text, cur_conf = [], []
    for f in fields:
        cur_text.append(f['text'])
        cur_conf.append(f['confidence'])
        if f['line_break']:
            lines.append({'text': ' '.join(cur_text), 'min_conf': min(cur_conf)})
            cur_text, cur_conf = [], []
    if cur_text:
        lines.append({'text': ' '.join(cur_text), 'min_conf': min(cur_conf)})
    return lines

def validate_lines(lines):
    errors = []
    for i, line in enumerate(lines):
        if len(line['text']) < 2:
            errors.append((i, 'too_short'))
        if '원' in line['text'] and not any(ch.isdigit() for ch in line['text']):
            errors.append((i, 'amount_without_digits'))
    return errors
```

With this separation, you can swap the API provider and still keep the post-processing core intact. This is especially effective when mixing General OCR, Template OCR, and other engines.

## Defining Benchmark Metrics for Korean Documents

Judging OCR quality by a single accuracy number often leads to operational failures. For Korean documents, it is better to track at least these metrics separately.

| Metric | Definition | Recommended initial target | Notes |
| --- | --- | --- | --- |
| Line reconstruction accuracy | Ratio of lines matching human expectation | 0.93+ | Separate from token-level accuracy |
| Amount format pass rate | Ratio passing currency regex | 0.98+ | Must document currency symbol/comma rules |
| Date normalization pass rate | Ratio of successful date standardization | 0.95+ | Support both `2026.05.01` and `2026-05-01` |
| Low-confidence review ratio | Ratio sent to human review queue | 0.05–0.15 | Too low = misses; too high = cost increase |

Connecting this table to a dashboard lets you objectively measure the effect of OCR model version upgrades.

## Production Config Example: OCR Ingestion Worker

OCR is typically operated as an asynchronous batch. Processing time per request is long and there is external API dependency.

```yaml
worker:
  name: ocr-ingestion-worker
  concurrency: 8
  queue: docs-ocr

clova:
  mode: real
  endpoint: https://example.apigw.ntruss.com/custom/v1/12345/abcd/general
  timeout_seconds: 15
  max_retries: 3
  retry_backoff_seconds: [1, 2, 4]

postprocess:
  line_min_conf_threshold: 0.82
  amount_regex: '^[0-9,]+원$'
  keep_raw_payload: true
  raw_payload_bucket: s3://ocr-raw-prod

output:
  cleaned_bucket: s3://ocr-clean-prod
  corpus_topic: rag-corpus-update

monitoring:
  error_rate_alert_threshold: 0.03
  p95_latency_ms_alert_threshold: 12000
```

`keep_raw_payload` is worth the storage cost — it lets you reprocess without re-calling the API when quality issues surface later.

## Making OCR Results Embedding-Friendly

When passing results to BGE-M3 or KoSimCSE, attaching minimal metadata alongside line text is better for long-term operation than sending raw text alone.

```python
def to_embedding_records(doc_id, lines, source='clova-ocr'):
    records = []
    for i, line in enumerate(lines):
        records.append({
            'chunk_id': f'{doc_id}#L{i:03d}',
            'text': line['text'],
            'meta': {
                'doc_id': doc_id,
                'source': source,
                'line_no': i,
                'min_confidence': round(line['min_conf'], 4),
            },
        })
    return records
```

This structure lets you show original line numbers directly in search results and easily build policies that filter out low-confidence lines.

## Coordinate-Based Column Restoration Example

For tax invoices and statements with 2+ columns, `lineBreak` alone may produce incomplete restoration. A minimal example using coordinates:

```python
def left_x(field):
    vertices = field.get('boundingPoly', {}).get('vertices', [])
    if not vertices:
        return 0
    return min(v.get('x', 0) for v in vertices)

def split_two_columns(fields, boundary_x=540):
    left_col, right_col = [], []
    for f in fields:
        if left_x(f) < boundary_x:
            left_col.append(f)
        else:
            right_col.append(f)
    return left_col, right_col
```

For services with fixed document layouts, this simple split alone significantly reduces line merge errors.

## Building a Regression Test Set for OCR Quality

OCR pipelines are sensitive to model version changes and preprocessing modifications. Fixing a small test set and attaching quantitative verification catches regressions quickly.

```python
EVAL_CASES = [
    {
        'name': 'receipt_simple',
        'expected_lines': ['공급가액 45,000원', '부가세 4,500원', '합계 49,500원'],
    },
    {
        'name': 'invoice_with_date',
        'expected_lines': ['작성일자 2026-05-01', '청구 금액 120,000원'],
    },
]

def line_exact_match_rate(pred_lines, expected_lines):
    pred_set = set(pred_lines)
    exp_set = set(expected_lines)
    return len(pred_set & exp_set) / len(exp_set)
```

The exact-line-match metric is simple but powerful — especially for structured documents like receipts and invoices.

## Amount/Date Normalization Utilities

In Korean documents, number format normalization directly affects search quality. The same amount written as `45,000원`, `45000원`, or `45.000원` disperses search hits.

```python
import re

AMOUNT_PATTERNS = [
    re.compile(r'^(\d{1,3}(,\d{3})+)원$'),
    re.compile(r'^(\d+)원$'),
]

DATE_PATTERNS = [
    re.compile(r'^(\d{4})\.(\d{2})\.(\d{2})$'),
    re.compile(r'^(\d{4})-(\d{2})-(\d{2})$'),
]

def normalize_amount(token: str) -> str:
    clean = token.replace('.', '').replace(',', '')
    if clean.endswith('원'):
        num = clean[:-1]
        if num.isdigit():
            return f"{int(num):,}원"
    return token

def normalize_date(token: str) -> str:
    for pat in DATE_PATTERNS:
        m = pat.match(token)
        if m:
            y, mm, dd = m.groups()
            return f'{y}-{mm}-{dd}'
    return token
```

This normalization is not flashy, but it serves as the foundation for aligning same-meaning units to identical strings in the embedding corpus.

## Failure Recovery Strategy for Operational Batches

OCR calls frequently encounter network errors, capacity limits, and transient 5xx responses. In queue-based batches, defining failure reprocessing policy first stabilizes overall throughput.

| Failure type | Retry policy | DLQ escalation threshold |
| --- | --- | --- |
| timeout | 1s, 2s, 4s backoff retry | 3 failures → DLQ |
| 429 | Long backoff (5s+) + jitter | 5 failures → DLQ |
| 5xx | Short backoff retry | 3 failures → DLQ |
| payload parse error | No retry | Immediate DLQ |

```python
def next_retry_delay(attempt, reason):
    if reason == 'rate_limit':
        return min(30, 5 * (2 ** attempt))
    return min(10, 1 * (2 ** attempt))
```

This level of policy alone significantly reduces worker stalls during bulk document processing.

## Answering the Opening Questions

- **When plugging in OCR, should you check text accuracy first or response structure first?**
  - Check response structure first. Even if every token is read correctly, if `공급가액` and `45,000원` end up as separate lines or unrelated document fragments, retrieval and RAG break immediately. That's why post-processing that reassembles `fields` into line-level text matters as much as OCR accuracy itself.
- **Why are bounding boxes and `lineBreak` hints so important in post-processing?**
  - `lineBreak` tells you which tokens form a single line; bounding boxes provide the reference for reconstructing column or table-cell structures. On receipts and invoices, without these hints amounts, dates, and item names can mix across rows. The OCR response JSON is not plain text—it's raw material for rebuilding lines and layout.
- **Why can you verify most of the OCR pipeline even without a real API key?**
  - The part that breaks most often in production is post-processing logic, not authentication. With a mock payload alone you can deterministically test line reconstruction, amount regex validation, confidence aggregation, and corpus conversion—the core path. When a real key arrives, only the front end that fetches responses changes; the back-end logic is reused as-is.

<!-- toc:begin -->
## In this series

- [Korean AI Stack 101 (1/6): Korean embedding models compared — KoSimCSE, BGE-M3, Solar](./01-korean-embedding-models.md)
- [Korean AI Stack 101 (2/6): Building sentence similarity search with KoSimCSE](./02-kosimcse-similarity.md)
- [Korean AI Stack 101 (3/6): BGE-M3 multilingual embedding in practice](./03-bge-m3-multilingual.md)
- **Korean AI Stack 101 (4/6): Document text extraction with CLOVA OCR API (current)**
- Korean AI Stack 101 (5/6): Using HyperCLOVA X and Solar API (upcoming)
- Korean AI Stack 101 (6/6): Assembling a Korean RAG pipeline (upcoming)

<!-- toc:end -->

---

## References

- [NAVER Cloud CLOVA OCR overview](https://www.ncloud.com/product/aiService/ocr)
- [CLOVA OCR API guide](https://api.ncloud-docs.com/docs/ai-application-service-ocr-ocr)
- [pdfplumber](https://github.com/jsvine/pdfplumber)
- [OCR post-processing patterns](https://cloud.google.com/document-ai/docs/process-documents-client-libraries)

Tags: Korean NLP, LLM, Embeddings, OCR
