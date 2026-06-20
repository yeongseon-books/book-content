---
title: "바이브코딩을 위한 AI 데이터 준비 (2/10): 원본 데이터 수집과 카탈로깅"
series: ai-data-preparation-101
episode: 2
language: ko
tags:
- Data Collection
- Cataloging
- DatasetCard
- 바이브코딩
- Vibe Coding
targets:
  wordpress: true
---

# 바이브코딩을 위한 AI 데이터 준비 (2/10): 원본 데이터 수집과 카탈로깅

이 글은 **바이브코딩을 위한 AI 데이터 준비** 시리즈의 두 번째 글입니다.

---

바이브코딩으로 AI 모델을 만들 때 "데이터를 어디서 가져오고 어떻게 관리하나요?"라는 질문이 자주 나옵니다. 웹에서 긁어오는 것? 공개 데이터셋을 쓰는 것? 직접 만드는 것? 어떤 방법이든 "이 데이터가 어디서 왔는지", "어떤 라이선스인지", "얼마나 신뢰할 수 있는지"를 기록해두지 않으면 나중에 문제가 생깁니다.

데이터 카탈로깅은 "데이터의 이력서"를 만드는 작업입니다. 어디서 왔고, 언제 수집했고, 어떤 변환을 거쳤고, sha256 체크섬이 무엇인지 — 이 정보가 있어야 나중에 "이 데이터 맞아?" 확인하거나 "이 데이터로 학습한 모델"을 추적할 수 있습니다.

> "데이터도 코드처럼 버전 관리가 필요합니다. 어떤 데이터로 어떤 모델을 만들었는지 추적할 수 없으면 재현 가능한 AI를 만들 수 없습니다."

## 이 글에서 다룰 질문

1. DatasetCard에 반드시 포함해야 할 정보는 무엇인가요?
2. 웹 스크래핑 시 robots.txt를 어떻게 존중하나요?
3. 데이터 변환 이력(TransformRecord)을 어떻게 추적하나요?
4. 소스 유형별 데이터 신뢰도는 어떻게 다른가요?
5. 카탈로그를 실제로 어떻게 구현하나요?

---

## 소스 유형별 신뢰도와 위험

| 소스 유형 | 신뢰도 | 주요 위험 | 처리 방법 |
|----------|--------|----------|----------|
| 공식 문서/논문 | 높음 | 라이선스 확인 필요 | 출처와 라이선스 기록 |
| 공개 데이터셋 | 높음 | 카테고리 편향 | 데이터 분포 확인 |
| 웹 크롤링 | 중간 | 저품질, 저작권 | robots.txt 준수, 품질 필터 |
| 사용자 생성 콘텐츠 | 낮음 | PII, 욕설, 허위정보 | PII 처리, 콘텐츠 필터 |

## DatasetCard: 데이터의 이력서

```python
from dataclasses import dataclass, field
from typing import Optional
import hashlib

@dataclass
class DatasetCard:
    name: str
    version: str
    source_url: str
    source_type: str  # "crawl", "api", "manual", "synthetic"
    license: str
    language: str
    collection_date: str
    sha256: str  # 파일 무결성 검증
    row_count: int
    description: str = ""
    known_issues: list[str] = field(default_factory=list)
    usage_policy: dict = field(default_factory=dict)
    transforms_applied: list[str] = field(default_factory=list)

def fingerprint_file(filepath: str) -> str:
    """파일의 sha256 체크섬을 계산합니다."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha256.update(chunk)
    return sha256.hexdigest()
```

## robots.txt를 준수하는 스크래퍼

```python
import time
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

class PoliteScraper:
    def __init__(self, user_agent: str = "MyBot/1.0", delay: float = 1.0):
        self.user_agent = user_agent
        self.delay = delay
        self._robots_cache = {}

    def can_fetch(self, url: str) -> bool:
        """robots.txt 기준으로 해당 URL 크롤링 허용 여부를 확인합니다."""
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"

        if robots_url not in self._robots_cache:
            rp = RobotFileParser()
            rp.set_url(robots_url)
            try:
                rp.read()
                self._robots_cache[robots_url] = rp
            except Exception:
                return False  # 읽기 실패 시 안전하게 불허

        return self._robots_cache[robots_url].can_fetch(self.user_agent, url)

    def fetch(self, url: str) -> str | None:
        if not self.can_fetch(url):
            print(f"robots.txt에 의해 차단됨: {url}")
            return None

        time.sleep(self.delay)  # 서버 부하 줄이기
        # 실제 HTTP 요청...
        return ""
```

## 변환 이력 추적

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class TransformRecord:
    transform_id: str
    input_sha256: str
    output_sha256: str
    transform_type: str  # "clean", "dedup", "pii_redact", "filter"
    params: dict
    rows_in: int
    rows_out: int
    applied_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    applied_by: str = ""  # 코드 버전 또는 사람 이름
```

변환 이력을 기록하면 "왜 이 데이터가 삭제됐는지", "어느 단계에서 데이터 수가 줄었는지" 추적할 수 있습니다.

## 카탈로그 구현

```python
import sqlite3
import json

def init_catalog(db_path: str = "catalog.db"):
    """데이터셋 카탈로그 DB를 초기화합니다."""
    conn = sqlite3.connect(db_path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS datasets (
            name TEXT PRIMARY KEY,
            version TEXT,
            card_json TEXT,
            registered_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS transforms (
            transform_id TEXT PRIMARY KEY,
            dataset_name TEXT,
            record_json TEXT
        )
    """)
    conn.commit()
    return conn

def register_dataset(conn: sqlite3.Connection, card: DatasetCard):
    """데이터셋을 카탈로그에 등록합니다."""
    conn.execute(
        "INSERT OR REPLACE INTO datasets VALUES (?, ?, ?, datetime('now'))",
        (card.name, card.version, json.dumps(card.__dict__))
    )
    conn.commit()
```

## 흔한 실수

| 실수 | 문제 | 해결 방법 |
|------|------|-----------|
| 소스 URL 기록 안 함 | 데이터 출처 추적 불가 | DatasetCard에 항상 기록 |
| robots.txt 무시 | 법적 문제, 서버 차단 | PoliteScraper로 확인 후 수집 |
| sha256 없이 파일 관리 | 파일이 변경됐는지 모름 | 모든 파일에 sha256 기록 |
| 변환 이력 기록 안 함 | 어느 단계에서 데이터 손실 몰라 | TransformRecord로 모든 변환 기록 |

## AI 팁

데이터를 수집할 때 annotation(라벨링)이 필요한 항목을 미리 표시해두면 나중에 어떤 데이터에 사람 검토가 필요한지 빠르게 찾을 수 있습니다.

```python
ANNOTATION_REQUIRED = ["borderline_content", "ambiguous_label", "rare_category"]

def needs_annotation(row: dict) -> bool:
    """이 데이터 행이 사람 검토가 필요한지 판단합니다."""
    return (
        row.get("confidence", 1.0) < 0.7 or
        row.get("category") in ANNOTATION_REQUIRED or
        len(row.get("text", "")) < 50  # 너무 짧은 텍스트
    )
```

## 체크리스트

- [ ] 모든 데이터 소스에 DatasetCard를 작성했다
- [ ] sha256 체크섬으로 파일 무결성을 검증한다
- [ ] 웹 크롤링 시 robots.txt를 확인한다
- [ ] 모든 데이터 변환을 TransformRecord로 기록한다
- [ ] 라이선스와 사용 정책을 DatasetCard에 명시했다

## 처음 질문으로 돌아가기

**DatasetCard에 반드시 포함할 정보는?** 이름, 버전, 소스 URL, 라이선스, 언어, 수집일, sha256, 행 수, 알려진 문제점.

**robots.txt 준수 방법은?** PoliteScraper처럼 RobotFileParser로 크롤링 허용 여부를 확인하고, 불허된 URL은 수집하지 않습니다.

**변환 이력 추적 방법은?** TransformRecord에 입력/출력 sha256, 변환 유형, 파라미터, 행 수 변화를 기록합니다.

**소스 유형별 신뢰도는?** 공식 문서 > 공개 데이터셋 > 웹 크롤링 > 사용자 생성 콘텐츠 순으로 신뢰도가 낮아집니다.

**카탈로그 구현은?** SQLite로 간단히 시작할 수 있습니다. 규모가 커지면 전용 데이터 카탈로그 도구(Delta Lake, Apache Atlas)로 이전합니다.

## 정리

데이터 수집과 카탈로깅은 AI 데이터 파이프라인의 기반입니다. DatasetCard로 모든 데이터 소스를 문서화하고, sha256으로 무결성을 보장하고, 변환 이력을 기록해야 재현 가능한 데이터 파이프라인을 만들 수 있습니다.

다음 글에서는 수집된 데이터에서 노이즈를 제거하고 중복을 없애는 **데이터 정제와 중복 제거**를 다룹니다.

## 참고 자료

- [AI 데이터 준비 원문: 원본 데이터 수집과 카탈로깅](../ko/02-source-data-collection-cataloging.md)

---

<!-- toc:begin -->
## 시리즈 목차

1. [바이브코딩을 위한 AI 데이터 준비 (1/10): 데이터 준비가 모델 품질을 결정하는 이유](./01-why-data-preparation-matters.md)
2. **바이브코딩을 위한 AI 데이터 준비 (2/10): 원본 데이터 수집과 카탈로깅 (현재 글)**
3. [바이브코딩을 위한 AI 데이터 준비 (3/10): 데이터 정제와 중복 제거](./03-cleaning-deduplication.md)
4. [바이브코딩을 위한 AI 데이터 준비 (4/10): PII 탐지와 익명화](./04-pii-detection-anonymization.md)
5. [바이브코딩을 위한 AI 데이터 준비 (5/10): Tokenization과 Chunking](./05-tokenization-chunking.md)
6. [바이브코딩을 위한 AI 데이터 준비 (6/10): 데이터 품질 필터링](./06-quality-filtering.md)
7. [바이브코딩을 위한 AI 데이터 준비 (7/10): 합성 데이터 생성](./07-synthetic-data-generation.md)
8. [바이브코딩을 위한 AI 데이터 준비 (8/10): 데이터 증강 기법](./08-data-augmentation.md)
9. [바이브코딩을 위한 AI 데이터 준비 (9/10): 학습/평가/테스트 분할](./09-train-eval-test-splitting.md)
10. [바이브코딩을 위한 AI 데이터 준비 (10/10): 프로덕션 데이터 파이프라인](./10-production-data-pipeline.md)
<!-- toc:end -->

Tags: Data Collection, Cataloging, DatasetCard, 바이브코딩, Vibe Coding
