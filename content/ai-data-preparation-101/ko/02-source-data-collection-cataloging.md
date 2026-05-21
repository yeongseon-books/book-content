---
title: "AI Data Preparation 101 (2/10): 원본 데이터 수집과 카탈로깅"

series: ai-data-preparation-101

episode: 2

language: ko

status: publish-ready

targets:

  tistory: true

  medium: false

  mkdocs: true

  ebook: true

tags:
- Data Preparation
- Data Collection
- Cataloging
- Provenance
last_reviewed: '2026-05-14'

seo_description: 3개월 전에 학습시킨 모델을 다시 돌려야 한다는 요청이 옵니다. 데이터셋을 찾으니 디렉터리에는 dataset_v2_final_real.csv…
---

# AI Data Preparation 101 (2/10): 원본 데이터 수집과 카탈로깅

데이터 수집 단계는 흔히 “필요한 파일만 내려받아 두는 일”로 축소됩니다. 하지만 몇 달 뒤 재학습 요청이 들어왔을 때 진짜 중요한 것은 파일의 존재 자체가 아니라 출처, 라이선스, 수집 시점, 변환 이력이 남아 있는지입니다.

이 정보가 없으면 모델 성능 재현은 물론이고, 계약 범위를 넘는 재사용이나 공개 불가능 데이터 혼입 같은 운영 문제가 바로 생깁니다. 실험 단계에서는 티가 안 나도, 팀이 커지고 데이터셋 수가 늘어나면 카탈로그 부재가 가장 먼저 병목이 됩니다.

시니어 엔지니어 관점에서 수집은 저장보다 기록이 먼저입니다. 데이터를 가져오는 함수와 메타데이터 카드를 남기는 함수를 분리해 두면 언젠가 반드시 카드 없는 파일이 생깁니다.

이 글은 AI Data Preparation 101 시리즈의 2번째 글입니다. 여기서는 원본 데이터를 수집할 때 어떤 메타데이터를 반드시 함께 저장해야 하는지, 그리고 provenance를 어떻게 끊기지 않는 체인으로 유지할지 살펴보겠습니다.

좋은 수집 파이프라인은 데이터를 “받아 둔다”가 아니라 “허용된 출처에서 가져오고, 그 사실을 나중에도 증명할 수 있게 남긴다”는 약속 위에 서 있습니다.

## 먼저 던지는 질문

- 재학습 시점에 “이 데이터가 어디서 왔는지”를 바로 답하려면 무엇을 남겨야 할까요?
- first-party, 공개 데이터셋, 스크레이핑, 벤더 데이터는 어떤 위험이 각각 다를까요?
- DatasetCard에는 최소 어떤 필드가 있어야 운영과 규제 대응이 가능할까요?

## 큰 그림

![AI 데이터 준비 2장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/ai-data-preparation-101/02/02-01-big-picture.ko.png)

*AI 데이터 준비 2장 흐름 개요*

이 그림에서는 원본 데이터 수집과 카탈로깅를 운영 흐름 안에서 어디에 배치해야 하는지 봅니다. 핵심은 개념을 따로 외우는 것이 아니라 입력, 처리, 검증, 운영 신호가 어떤 경계로 이어지는지 확인하는 데 있습니다.

> 원본 데이터 수집과 카탈로깅의 핵심은 기능 이름이 아니라, 어떤 경계에서 무엇을 검증하고 어떤 신호를 남길지 정하는 데 있습니다.

## 왜 이 글이 중요한가

수집과 카탈로깅을 잘하면 재현성이 생깁니다. 같은 데이터셋 버전을 다시 내려받거나, 어떤 실험이 어떤 스냅샷을 썼는지 추적하거나, 라이선스 범위를 증명하는 일이 훨씬 쉬워집니다.

반대로 카탈로그 없이 수집한 데이터는 시간이 지날수록 독이 됩니다. `final_v2_real.csv` 같은 파일명만 남고, 누가 언제 어떤 권한으로 모았는지 사라지면 재학습 요청 하나도 안전하게 처리할 수 없습니다.

이 글의 핵심은 데이터를 많이 모으는 방법이 아니라, 모은 데이터를 조직이 계속 믿고 쓸 수 있게 만드는 방법입니다. 이후 정제·PII·분할 단계도 결국 이 provenance 위에서만 안정적으로 돌아갑니다.

## 핵심 관점

수집 파이프라인은 파일 저장과 메타데이터 기록이 하나의 트랜잭션이어야 합니다. 데이터만 떨어지고 카드가 없거나, 카드만 있고 실제 파일 fingerprint가 없으면 나중에 어느 쪽도 믿을 수 없습니다.

운영에서는 “어디서 왔는가”와 “무엇으로 변했는가”를 모두 묻습니다. 따라서 수집 단계의 DatasetCard와 이후 변환 단계의 TransformRecord를 연결해 provenance 체인을 만든다고 생각하는 편이 정확합니다.

이렇게 설계하면 샘플 수 감소, 라이선스 문의, 스냅샷 차이 같은 질문을 감으로 푸는 대신 sha256과 커밋 기록으로 바로 추적할 수 있습니다.

> 좋은 데이터 수집은 데이터를 더 많이 모으는 일이 아니라, 그 데이터가 언제·어디서·어떤 권한으로 들어왔는지 영구적으로 설명 가능하게 만드는 일입니다.

## 핵심 개념

### 소스 유형이 다르면 위험도 다르게 봐야 합니다

프로덕션 수집 경로는 대체로 네 가지로 정리됩니다.

| 유형 | 예시 | 주된 위험 |
| --- | --- | --- |
| **1st-party 로그** | 사용자 클릭, API 요청, 거래 데이터 | PII 포함, 동의 범위 초과 |
| **공개 데이터셋** | Common Crawl, Wikipedia, HuggingFace | 라이선스 조건, 품질 편차 |
| **웹 스크레이핑** | 뉴스, 블로그, 포럼 | robots.txt, 저작권, 차단 |
| **벤더/계약 데이터** | 파트너 API, 데이터 브로커 | 계약 범위, 갱신, SLA |

수집 코드는 달라도 카탈로그 필드는 거의 같습니다. 출처 유형이 달라질수록 코드보다 메타데이터 정책이 먼저 달라져야 합니다.

### 모든 데이터셋은 DatasetCard를 가져야 합니다

원본 데이터 옆에 붙는 카드가 없으면, 팀은 결국 파일명과 기억에 의존하게 됩니다. 아래 예제는 최소한의 DatasetCard 구조를 보여 줍니다.

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

여기서 중요한 필드는 이름, 버전, source type, source URL, license, snapshot date, row count, sha256, schema입니다. 여기에 PII 컬럼과 retention 정책까지 들어가면 이후 개인정보 처리 단계와도 자연스럽게 이어집니다.

### 수집과 카드 생성은 같은 함수 안에서 끝내야 합니다

HuggingFace 같은 공개 데이터셋을 가져올 때도 데이터 저장과 카드 저장을 분리하지 않는 편이 안전합니다.

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

실무에서는 이 예제를 더 감싸서 “카드 없는 데이터셋은 디스크에 존재할 수 없다”는 규칙으로 만듭니다. 사람이 까먹지 않게 만드는 것이 핵심입니다.

### 스크레이핑은 polite crawler로 시작해야 합니다

스크레이핑은 데이터 확보 속도보다 정책 준수가 먼저입니다. 최소한 robots.txt 확인, rate limit, 명시적 User-Agent는 기본으로 둬야 합니다.

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

이 규칙을 빼면 데이터는 모일 수 있어도 운영 리스크가 커집니다. IP 차단, 법적 이슈, 불완전 수집이 한 번에 생기고, 이후 파이프라인 전체의 신뢰도도 떨어집니다.

### provenance는 변환 단계까지 이어져야 합니다

수집 카드만 있고 이후 변환 이력이 없으면 절반만 해결한 셈입니다. 정제, 중복 제거, 익명화, 필터링을 거치면서 입력 sha256과 출력 sha256, 실행 커밋, 설정값을 모두 남겨야 합니다.

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

이 체인을 유지하면 “왜 이 학습셋 행 수가 줄었지?” 같은 질문이 감정 싸움이 아니라 추적 가능한 운영 질문이 됩니다.

### 카탈로그 백엔드는 규모에 맞게 고릅니다

데이터셋이 적을 때는 JSON 카드만으로도 충분합니다. 하지만 100개를 넘기면 검색, 소유자 기준 조회, 라이선스 확인이 급격히 귀찮아집니다. 그 시점부터는 SQLite나 메타데이터 플랫폼으로 올리는 편이 낫습니다.

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

작게 시작하는 것은 좋지만, 검색이 안 되는 상태를 오래 끌고 가는 것은 좋지 않습니다. 데이터 카탈로그도 조기 과최적화보다, 너무 늦은 구조화가 더 비쌉니다.

## 흔히 헷갈리는 지점

- **파일만 잘 보관하면 재현성은 충분합니다**: 파일의 존재만으로는 출처, 라이선스, 시점, 스키마를 설명할 수 없어서 재현성이 성립하지 않습니다.
- **카탈로그는 데이터셋이 아주 많아진 뒤에 도입하면 됩니다**: 초기부터 카드 구조를 강제해 두어야 이후 SQLite나 메타데이터 플랫폼으로 옮겨도 체인이 끊기지 않습니다.
- **공개 데이터셋은 라이선스를 따로 기록하지 않아도 됩니다**: 공개라는 사실과 재사용 허용 범위는 다릅니다. 카드에 명시적으로 남겨야 합니다.
- **robots.txt는 참고 사항일 뿐입니다**: 무시한 스크레이핑은 운영과 법무 리스크를 동시에 키웁니다. 자동화 파이프라인에선 더 위험합니다.

## 운영 체크리스트

- [ ] 모든 원본 데이터셋 저장 시 DatasetCard를 같은 트랜잭션에서 생성한다
- [ ] 카드에 license, snapshot_date, sha256, schema, owner, pii_fields를 필수 필드로 강제했다
- [ ] 스크레이퍼가 robots.txt 확인, request throttling, 명시적 User-Agent를 기본으로 사용한다
- [ ] 각 변환 단계에서 input/output sha256과 code commit을 남기는 TransformRecord를 저장한다
- [ ] 데이터셋 검색 수요가 커지기 전에 SQLite 또는 메타데이터 백엔드 전환 기준을 정했다

## 정리

수집 단계의 핵심은 데이터를 더 빨리 모으는 것이 아니라, 그 데이터의 출처와 사용 가능 범위를 나중에도 설명할 수 있게 만드는 것입니다. DatasetCard와 provenance 체인은 재현성의 출발점입니다.

공개 데이터셋, first-party 로그, 스크레이핑, 벤더 데이터는 각각 다른 위험을 갖지만, 공통적으로 라이선스·소유자·스냅샷·fingerprint를 남겨야만 이후 단계가 안전해집니다.

다음 글에서는 이렇게 모아 둔 원본 데이터를 어떻게 정제하고, 어떤 순서로 중복을 제거해야 품질과 평가 신뢰도를 동시에 지킬 수 있는지 다룹니다.

## 처음 질문으로 돌아가기

- **재학습 시점에 “이 데이터가 어디서 왔는지”를 바로 답하려면 무엇을 남겨야 할까요?**
  - 본문의 기준은 원본 데이터 수집과 카탈로깅를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **first-party, 공개 데이터셋, 스크레이핑, 벤더 데이터는 어떤 위험이 각각 다를까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **DatasetCard에는 최소 어떤 필드가 있어야 운영과 규제 대응이 가능할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [AI Data Preparation 101 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
- **원본 데이터 수집과 카탈로깅 (현재 글)**
- 데이터 정제와 중복 제거 (예정)
- 학습 데이터 PII 탐지와 익명화 (예정)
- Tokenization과 Chunking 전략 (예정)
- 데이터 품질 필터링 — Heuristic과 Classifier (예정)
- 합성 데이터 생성 — Self-Instruct부터 Distillation까지 (예정)
- 데이터 증강 기법 — EDA부터 Back-Translation까지 (예정)
- 학습/평가/테스트 분할과 Contamination 통제 (예정)
- 프로덕션 데이터 파이프라인 구축 (예정)

<!-- toc:end -->

## 참고 자료

### 공식 문서
- [Datasheets for Datasets (Gebru et al., 2018)](https://arxiv.org/abs/1803.09010)
- [HuggingFace Datasets documentation](https://huggingface.co/docs/datasets/index)
- [DataHub - Open Source Metadata Platform](https://datahubproject.io/)
- [MLflow Tracking - Dataset versioning](https://mlflow.org/docs/latest/tracking/data-api.html)

### 관련 시리즈
- [LLM 파인튜닝 101 — 데이터셋 준비와 전처리](../../llm-finetuning-101/ko/02-dataset.md)
- [AI Evaluation 101 — 평가 데이터셋 설계하기](../../ai-evaluation-101/ko/02-evaluation-dataset-design.md)

- [이 글의 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/ai-data-preparation-101/ko/02-source-data-collection-cataloging)

Tags: Data Preparation, Data Collection, Cataloging, Provenance
