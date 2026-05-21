---
title: "AI Data Preparation 101 (2/10): Source Data Collection and Cataloging"
series: ai-data-preparation-101
episode: 2
language: en
status: publish-ready
targets:
  tistory: false
  medium: true
  mkdocs: true
  ebook: true
tags:
- Data Preparation
- Data Collection
- Cataloging
- Provenance
last_reviewed: '2026-05-14'
seo_description: 'A request lands: re-train the model from three months ago. You open
  the directory and find files like dataset_v2_final_real.csv with no record of…'
---

# AI Data Preparation 101 (2/10): Source Data Collection and Cataloging

The painful moment usually comes months later: you need to retrain a model, but all that remains is a directory full of vaguely named files. Once the source, license, and collection context are gone, reproducibility is already broken.

This is post 2 in the AI Data Preparation 101 series. Here we cover how to collect source data in a way that preserves cataloging and provenance from day one.

## Questions to Keep in Mind

- What metadata must exist the moment a dataset lands on disk?
- How do public datasets, web scraping, and vendor feeds differ in operational risk?
- Why should collection and dataset-card creation happen in one transaction?

## Big Picture

![AI data preparation chapter 2 flow overview](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/02/02-01-big-picture.en.png)

*AI data preparation chapter 2 flow overview*

This picture places Source Data Collection and Cataloging inside an operating flow. The point is not to memorize the concept in isolation, but to see how input, processing, verification, and operational signals connect across boundaries.

## "I Don't Remember Where This Data Came From"

A request lands: re-train the model from three months ago. You open the directory and find files like `dataset_v2_final_real.csv` with no record of where they originated. This common scene breaks reproducibility and seeds future license disputes.

The goal of the collection stage is not just "get useful data." It is "get useful data **and** record permanently when, where, and under what permission you got it." This episode spends more time on cataloging and provenance than on the act of collection itself.

## Four Source Types

Production sources fall into roughly four categories.

| Type | Examples | Main risks |
| --- | --- | --- |
| First-party logs | User clicks, API calls, transactions | PII inclusion, consent scope |
| Public datasets | Common Crawl, Wikipedia, HuggingFace | License terms, quality variance |
| Web scraping | News, blogs, forums | robots.txt, copyright, blocking |
| Vendor / licensed | Data brokers, partner APIs | Contracts, SLAs, renewal |

Collection code and metadata schemas vary by type, but the catalog fields you must record are the same.

## Metadata Every Dataset Should Carry

For ML reproducibility, every dataset must travel with a fixed metadata bundle.

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import hashlib
import json

@dataclass
class DatasetCard:
    name: str
    version: str  # semver: 1.2.0
    source_type: str  # "first-party" | "public" | "scrape" | "vendor"
    source_url: Optional[str]
    license: str  # "CC-BY-4.0" | "MIT" | "proprietary" | etc.
    snapshot_date: str  # ISO 8601
    row_count: int
    size_bytes: int
    sha256: str
    schema: dict
    description: str
    consent_basis: Optional[str] = None  # GDPR/PIPA legal basis
    pii_fields: list = field(default_factory=list)
    retention_days: Optional[int] = None
    owner: str = "unknown"
    tags: list = field(default_factory=list)

    def to_json(self) -> str:
        return json.dumps(self.__dict__, indent=2, ensure_ascii=False)

def fingerprint_file(path: str) -> tuple[str, int]:
    h = hashlib.sha256()
    size = 0
    with open(path, "rb") as f:
        while chunk := f.read(1 << 20):
            h.update(chunk)
            size += len(chunk)
    return h.hexdigest(), size
```

Keep the card next to the dataset and you can answer "where did this come from?" precisely six months later.

## Collection Script Example: HuggingFace Dataset

```python
from datasets import load_dataset
from datetime import datetime, timezone

ds = load_dataset("ag_news", split="train")
ds.to_csv("./data/raw/ag_news_train.csv")

sha, size = fingerprint_file("./data/raw/ag_news_train.csv")
card = DatasetCard(
    name="ag_news",
    version="1.0.0",
    source_type="public",
    source_url="https://huggingface.co/datasets/ag_news",
    license="custom (academic only)",
    snapshot_date=datetime.now(timezone.utc).isoformat(),
    row_count=len(ds),
    size_bytes=size,
    sha256=sha,
    schema={"text": "string", "label": "int (0-3)"},
    description="AG News topic classification dataset (4 classes).",
    pii_fields=[],
    owner="ml-platform-team",
    tags=["nlp", "classification", "news"],
)
with open("./data/raw/ag_news_train.card.json", "w") as f:
    f.write(card.to_json())
```

Collection and card creation belong to the same transaction. Wrap them in one function so a dataset can never land on disk without its card.

## Web Scraping: robots.txt and Rate Limiting

Scraping is the highest-risk collection method. At minimum follow these three rules.

```python
from urllib.robotparser import RobotFileParser
from urllib.parse import urljoin
import time
import requests

class PoliteScraper:
    def __init__(self, base_url: str, user_agent: str, rps: float = 1.0):
        self.base_url = base_url
        self.user_agent = user_agent
        self.min_interval = 1.0 / rps
        self._last = 0.0
        self.rp = RobotFileParser()
        self.rp.set_url(urljoin(base_url, "/robots.txt"))
        try:
            self.rp.read()
        except Exception:
            pass  # Treat missing robots.txt conservatively

    def can_fetch(self, path: str) -> bool:
        return self.rp.can_fetch(self.user_agent, urljoin(self.base_url, path))

    def get(self, path: str) -> requests.Response:
        if not self.can_fetch(path):
            raise PermissionError(f"robots.txt disallows {path}")
        elapsed = time.time() - self._last
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self._last = time.time()
        return requests.get(
            urljoin(self.base_url, path),
            headers={"User-Agent": self.user_agent},
            timeout=10,
        )
```

Three principles: respect robots.txt, throttle requests, identify yourself with a clear User-Agent. Skip these and you risk IP bans plus legal exposure.

## Provenance Chain — One Level Deeper

A raw dataset typically goes through five to ten transformation steps before becoming a training set. Record the input card sha256 and the transformation code's git commit at every step.

```python
@dataclass
class TransformRecord:
    input_card_path: str
    input_sha256: str
    output_card_path: str
    output_sha256: str
    code_commit: str  # git rev-parse HEAD
    started_at: str
    finished_at: str
    config: dict

# Example
record = TransformRecord(
    input_card_path="./data/raw/ag_news_train.card.json",
    input_sha256="abc123...",
    output_card_path="./data/clean/ag_news_train.card.json",
    output_sha256="def456...",
    code_commit="a1b2c3d",
    started_at="2026-05-03T10:00:00Z",
    finished_at="2026-05-03T10:02:34Z",
    config={"min_length": 20, "lowercase": False},
)
```

With this chain, "why did the row count drop in this training set?" becomes a one-step lookup. Just follow the input/output sha256 chain.

## Catalog Backend: Filesystem vs Metadata DB

For small teams, JSON cards alongside the data are enough. Past 100 datasets, search becomes painful. Three options:

1. **SQLite catalog**: single file, commit to git alongside code. Fits 50-500 datasets.
2. **Postgres + DataHub/OpenMetadata**: search, RBAC, lineage visualization. Suits large orgs.
3. **MLflow / Weights & Biases**: track experiments and datasets together. Strong ML workflow integration.

Below is the minimal SQLite schema:

```python
import sqlite3

def init_catalog(db_path: str = "catalog.db"):
    conn = sqlite3.connect(db_path)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS datasets (
        name TEXT NOT NULL,
        version TEXT NOT NULL,
        source_type TEXT,
        license TEXT,
        snapshot_date TEXT,
        row_count INTEGER,
        sha256 TEXT,
        owner TEXT,
        card_json TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (name, version)
    );
    CREATE INDEX IF NOT EXISTS idx_datasets_owner ON datasets(owner);
    CREATE INDEX IF NOT EXISTS idx_datasets_license ON datasets(license);
    """)
    return conn

def register(conn, card: DatasetCard):
    conn.execute("""
    INSERT OR REPLACE INTO datasets
    (name, version, source_type, license, snapshot_date, row_count, sha256, owner, card_json)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (card.name, card.version, card.source_type, card.license,
          card.snapshot_date, card.row_count, card.sha256, card.owner,
          card.to_json()))
    conn.commit()
```

Start with SQLite under 50 datasets and migrate when your search needs grow. Premature optimization hurts data catalogs too.

## Common Mistakes

1. **Collection separated from card creation**: Data lands but the card is missing. A few days later, no one can trace the source. Always do both in one function.
2. **Versions named `final`, `final_v2`, `real_final`**: Enforce semver (1.0.0, 1.1.0). Without a real version policy you cannot tell which dataset produced which model.
3. **Empty license field**: Record CC-BY, MIT, proprietary, or similar explicitly. Empty fields are a publishing risk waiting to happen.
4. **Ignoring robots.txt while scraping**: One-off scripts may sneak through, but at scale you trigger IP bans and legal trouble simultaneously.
5. **PII columns not declared in the card**: Fail to mark which columns contain PII and the anonymization step in episode 4 will miss them.

## Key Takeaways

- Collection is not just data acquisition; it is permanent provenance recording for reproducibility.
- Every dataset must carry a DatasetCard (name, version, source, license, sha256, schema, PII fields).
- Web scraping requires robots.txt compliance, rate limiting, and a clear User-Agent.
- Record a TransformRecord with input/output sha256 and code commit at every transformation step.
- Use SQLite for catalogs under 50 datasets; scale to DataHub or MLflow beyond that.
- Episode 3 covers cleaning and deduplication.

---

## Operational checklist

- [ ] Create the dataset card in the same function that writes the raw data
- [ ] Store source URL, license, snapshot date, sha256, schema, and owner for every dataset version
- [ ] Treat scraping as policy-sensitive work with robots.txt, throttling, and a clear User-Agent
- [ ] Record transform lineage with input/output hashes and code commit for every stage
- [ ] Decide in advance when the catalog should move from flat files to SQLite or a metadata platform

## Answering the Opening Questions

- **What metadata must exist the moment a dataset lands on disk?**
  - The article treats Source Data Collection and Cataloging as a set of boundaries rather than one abstract idea, then separates input, processing, verification, and operational signals.
- **How do public datasets, web scraping, and vendor feeds differ in operational risk?**
  - The example and diagram should make visible what enters the system, where it changes, and which check decides pass or fail.
- **Why should collection and dataset-card creation happen in one transaction?**
  - In production, keep that decision in checklists, logs, and tests so the same failure does not return after the next change.

<!-- toc:begin -->
## In this series

- [AI Data Preparation 101 (1/10): Why Data Preparation Determines Model Quality](./01-why-data-preparation-matters.md)
- **Source Data Collection and Cataloging (current)**
- Cleaning and Deduplication (upcoming)
- PII Detection and Anonymization for Training Data (upcoming)
- Tokenization and Chunking Strategies (upcoming)
- Quality Filtering - Heuristics and Classifiers (upcoming)
- Synthetic Data Generation - From Self-Instruct to Distillation (upcoming)
- Data Augmentation - From EDA to Back-Translation (upcoming)
- Train/Eval/Test Splitting and Contamination Control (upcoming)
- Building a Production Data Pipeline (upcoming)

<!-- toc:end -->

## References

- [Datasheets for Datasets (Gebru et al., 2018)](https://arxiv.org/abs/1803.09010)
- [HuggingFace Datasets documentation](https://huggingface.co/docs/datasets/index)
- [DataHub - Open Source Metadata Platform](https://datahubproject.io/)
- [MLflow Tracking - Dataset versioning](https://mlflow.org/docs/latest/tracking/data-api.html)

Tags: Data Preparation, Data Collection, Cataloging, Provenance
