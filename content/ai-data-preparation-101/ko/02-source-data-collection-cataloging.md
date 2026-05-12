---
title: 원본 데이터 수집과 카탈로깅
series: ai-data-preparation-101
episode: 2
language: ko
status: content-ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Data Preparation
- Data Collection
- Cataloging
- Provenance
last_reviewed: '2026-05-03'
seo_description: 3개월 전에 학습시킨 모델을 다시 돌려야 한다는 요청이 옵니다. 데이터셋을 찾으니 디렉터리에는 dataset_v2_final_real.csv…
---

# 원본 데이터 수집과 카탈로깅

> AI Data Preparation 101 시리즈 (2/10)

몇 달 전에 학습에 쓴 데이터를 다시 찾아야 하는데 파일명만 남고 출처와 수집 맥락이 사라진 경우가 흔합니다. 이런 순간부터 재현성과 라이선스 관리가 함께 흔들리기 시작합니다.

이 글은 AI Data Preparation 101 시리즈의 2번째 글입니다. 여기서는 원본 데이터를 모으는 일보다 더 중요한 카탈로깅과 provenance 기록을 어떤 기준으로 남겨야 하는지 다룹니다.

---

## "데이터를 어디서 가져왔는지 기억 안 나요"

3개월 전에 학습시킨 모델을 다시 돌려야 한다는 요청이 옵니다. 데이터셋을 찾으니 디렉터리에는 `dataset_v2_final_real.csv` 같은 파일만 남아 있고, 어디서 가져왔는지 기록이 없습니다. 이 흔한 사고가 reproducibility를 무너뜨리고, 라이선스 분쟁의 출발점이 됩니다.

데이터 수집 단계의 목표는 "쓸모있는 데이터를 가져오는 것"만이 아닙니다. **언제, 어디서, 어떤 권한으로 가져왔는지를 영구히 기록하는 것**까지가 한 묶음입니다. 이 편에서는 수집 자체보다 카탈로깅과 provenance에 더 많은 시간을 씁니다.

## 데이터 소스 4가지 유형

production에서 마주치는 소스는 크게 네 가지로 나뉩니다.

| 유형 | 예시 | 주요 위험 |
| --- | --- | --- |
| First-party logs | 사용자 클릭, API 호출, 트랜잭션 | PII 포함 가능, 동의 범위 |
| Public datasets | Common Crawl, Wikipedia, HuggingFace | 라이선스, 품질 편차 |
| Web scraping | 뉴스, 블로그, 포럼 | robots.txt, 저작권, 차단 |
| Vendor / licensed | 데이터 브로커, 파트너 API | 계약, SLA, 갱신 |

각 유형마다 수집 코드와 메타데이터 스키마가 다릅니다. 그러나 카탈로그에 기록해야 할 항목은 공통입니다.

## 모든 데이터셋이 가져야 할 메타데이터

ML 모델 reproducibility를 위해 모든 데이터셋에 반드시 따라다녀야 하는 메타데이터가 있습니다.

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

이 카드를 데이터셋 옆에 항상 함께 두면, 6개월 뒤 누군가 "이 데이터 어디서 왔어요?"라고 물었을 때 정확하게 답할 수 있습니다.

## 수집 스크립트 예시: HuggingFace 데이터셋

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

수집과 카드 생성은 항상 한 트랜잭션입니다. 카드 없이 데이터만 디스크에 떨어지지 않게 함수로 묶어 놓는 것이 핵심입니다.

## Web scraping 시 robots.txt와 rate limit

scraping은 가장 사고가 잦은 수집 방식입니다. 최소한 다음 세 가지를 지킵니다.

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
            pass  # robots.txt 부재 시 보수적으로 처리

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

세 가지 원칙: robots.txt 준수, request rate 제한, 명확한 User-Agent 식별. 이를 어기면 IP 차단은 물론 법적 분쟁까지 갑니다.

## Provenance 체인 — 한 단계 더 깊게

수집한 raw 데이터에서 학습 셋이 만들어지기까지 보통 5~10개의 변환 단계를 거칩니다. 각 단계마다 입력 카드의 sha256과 변환 코드의 git commit을 기록합니다.

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

# 사용 예
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

이 체인이 있으면 "왜 이 학습 셋의 row 수가 줄었지?" 같은 질문에 한 번에 답할 수 있습니다. 각 단계의 input/output sha256만 따라가면 됩니다.

## 카탈로그 저장소: 파일 시스템 vs 메타데이터 DB

소규모 팀에서는 카드 JSON 파일을 데이터와 함께 디스크에 두는 것으로 충분합니다. 데이터셋이 100개를 넘어가면 검색이 어려워집니다. 다음 세 가지 옵션이 있습니다.

1. **SQLite 카탈로그**: 단일 파일, git에 같이 커밋 가능. 50~500개 데이터셋에 적합.
2. **Postgres + DataHub/OpenMetadata**: 검색, 권한 관리, lineage 시각화. 대규모 조직.
3. **MLflow / Weights & Biases**: 학습 실험과 데이터셋을 함께 추적. ML 워크플로 통합이 강함.

다음은 SQLite 옵션의 최소 스키마입니다.

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

50개 이하라면 SQLite로 시작하고, 검색 요구가 늘어나면 그때 옮기면 됩니다. premature optimization은 데이터 카탈로그에서도 위험합니다.

## 흔한 실수 5가지

1. **수집과 카드 생성이 분리됨**: 데이터만 떨어지고 카드가 안 만들어지면 며칠 뒤 출처를 추적할 수 없습니다. 항상 한 함수에서 둘 다 처리합니다.
2. **버전이 `final`, `final_v2`, `real_final`**: semver(1.0.0, 1.1.0)를 강제합니다. 의미 있는 버전 정책 없이는 어떤 데이터로 어떤 모델을 학습했는지 추적 불가능합니다.
3. **license 필드 비어 있음**: CC-BY, MIT, proprietary 등 명확하게 적습니다. 비어 있으면 외부 발행 시 리스크가 됩니다.
4. **scraping에서 robots.txt 무시**: 한두 번은 통과할 수 있지만 대규모 수집은 IP 차단과 법적 위험을 동시에 키웁니다.
5. **PII 필드를 카드에 기록 안 함**: 어떤 컬럼에 PII가 있는지 명시 안 하면 4편의 anonymization 단계에서 누락됩니다.

## 핵심 요약

- 수집의 목표는 데이터 확보뿐 아니라 reproducibility를 위한 provenance 기록입니다.
- 모든 데이터셋에는 DatasetCard(이름, 버전, 출처, 라이선스, sha256, 스키마, PII 필드)가 따라다녀야 합니다.
- Web scraping에는 robots.txt 준수 + rate limit + 명확한 User-Agent 세 가지가 기본입니다.
- 변환 단계마다 input/output sha256과 code commit을 기록한 TransformRecord를 남깁니다.
- 카탈로그는 50개 이하라면 SQLite로 충분합니다. 그 이상이면 DataHub나 MLflow로 확장합니다.
- 다음 편(3편)은 정제와 중복 제거를 다룹니다.

---

<!-- toc:begin -->
## AI Data Preparation 101 시리즈

- [데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- **원본 데이터 수집과 카탈로깅 (현재 글)**
- 데이터 정제와 중복 제거 (예정)
- 학습 데이터 PII 탐지와 익명화 (예정)
- 토큰화와 청킹 전략 (예정)
- 데이터 품질 필터링 (예정)
- 합성 데이터 생성 (예정)
- 데이터 증강 기법 (예정)
- 학습/평가/테스트 분할과 오염 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)
<!-- toc:end -->

## 참고 자료

- [Datasheets for Datasets (Gebru et al., 2018)](https://arxiv.org/abs/1803.09010)
- [HuggingFace Datasets documentation](https://huggingface.co/docs/datasets/index)
- [DataHub - Open Source Metadata Platform](https://datahubproject.io/)
- [MLflow Tracking - Dataset versioning](https://mlflow.org/docs/latest/tracking/data-api.html)

Tags: Data Preparation, Data Collection, Cataloging, Provenance
