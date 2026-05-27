---
series: secure-coding-101
episode: 5
title: "Secure Coding 101 (5/10): 안전한 데이터 저장"
status: content-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Encryption
  - DataProtection
  - PII
  - SecureCoding
  - Cryptography
seo_description: At-rest 암호화, 전송 암호화, 민감정보 분리 그리고 안전한 저장 5단계
last_reviewed: '2026-05-15'
---

# Secure Coding 101 (5/10): 안전한 데이터 저장

민감한 데이터를 저장하는 순간부터 애플리케이션은 기능 시스템이면서 동시에 보관 시스템이 됩니다. 사용자 입장에서는 회원가입 한 번이지만, 운영자 입장에서는 주민등록번호, 주소, 카드 정보, 비밀번호 해시, 백업 파일처럼 사고 비용이 큰 자산을 떠안는 셈입니다. 그래서 저장 보안은 데이터베이스 옵션 하나로 끝나지 않습니다.

이 글은 Secure Coding 101 시리즈의 5번째 글입니다.

여기서는 저장 보안을 디스크 암호화만으로 보지 않고, 어떤 데이터를 모을지부터 전송 구간, 저장 구간, 키 분리, 백업 보호까지 이어지는 흐름으로 정리하겠습니다. 이 관점을 잡아 두면 민감 데이터가 왜 가장 비싼 사고 자산인지, 그리고 왜 백업까지 같은 수준으로 봐야 하는지도 자연스럽게 이해할 수 있습니다.

![Secure Coding 101 5장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/secure-coding-101/05/05-01-concept-at-a-glance.ko.png)
*Secure Coding 101 5장 흐름 개요*

## 먼저 던지는 질문

- 저장 중 암호화와 전송 중 암호화는 무엇이 다를까요?
- PII와 민감 데이터를 분류하는 작업이 왜 먼저일까요?
- 대칭키, 비대칭키, KMS는 어떤 역할로 나뉠까요?

## 왜 중요한가

민감 데이터 유출은 법적 책임과 운영 비용이 모두 큽니다. 디스크 하나가 유출되거나 백업 파일 하나가 노출돼도 평문 저장이라면 사고는 즉시 사용자 피해로 이어집니다. 반대로 데이터가 암호화돼 있고 키가 분리돼 있으면 동일한 유출 상황에서도 피해 규모가 크게 달라집니다.

또한 저장 보안은 단일 컴포넌트 문제가 아닙니다. 애플리케이션에서 데이터베이스로 가는 전송 구간, 데이터베이스가 디스크에 쓰는 저장 구간, 복구를 위해 만드는 백업, 운영 편의를 위해 남기는 로그까지 모두 저장 체인 안에 들어갑니다. 한 곳만 안전하고 다른 한 곳이 비어 있으면 전체 방어가 무너집니다.

## 한눈에 보는 구조

이 구조에서 데이터는 애플리케이션과 데이터베이스 사이를 이동할 때도 보호돼야 하고, 데이터베이스가 디스크에 저장할 때도 보호돼야 합니다. 동시에 암호화 키는 데이터와 분리된 KMS에서 관리돼야 진짜 분리 효과가 생깁니다.

## 핵심 용어

- **개인 식별 정보(PII)**: 특정 개인을 직접 또는 간접으로 식별할 수 있는 정보입니다.
- **저장 중 데이터(at rest)**: 디스크나 객체 저장소처럼 저장 매체에 머무는 데이터입니다.
- **전송 중 데이터(in transit)**: 네트워크를 통해 이동하는 데이터입니다.
- **키 관리 시스템(KMS)**: 암호화 키 자체를 저장, 보호, 회전하는 서비스입니다.
- **토큰화(tokenization)**: 원본 값을 저장하지 않고 대체 토큰으로 치환해 보관하는 방식입니다.

## 바꾸기 전과 후

**바꾸기 전**: 주민등록번호와 카드 번호를 평문으로 저장하고, 운영 로그와 백업에도 그대로 남깁니다. 저장소가 한 번만 노출돼도 사고 범위가 큽니다.

**바꾼 후**: 주민등록번호는 조회 목적에 맞게 해시하거나 분리 저장하고, 카드 정보는 토큰화하며, 저장 구간은 KMS 기반 암호화를 적용합니다. 백업과 로그도 같은 기준으로 보호합니다.

## 실습: 안전하게 저장하는 5단계

### 1단계 — 먼저 데이터를 분류합니다

```python
SENSITIVE = {"ssn", "card_number", "password", "address"}
def is_sensitive(field): return field in SENSITIVE
```

무엇이 민감한지 모른 채 암호화 전략을 짤 수는 없습니다. 먼저 어떤 필드가 규제 대상인지, 어떤 값이 유출되면 사용자를 식별할 수 있는지 분류해야 합니다. 이 목록이 있어야 저장, 로그, 백업 정책도 함께 맞출 수 있습니다.

### 2단계 — 전송 구간에 TLS를 강제합니다

```python
# 클라이언트와 DB 사이는 항상 TLS를 사용하고 인증서 검증을 끄지 않습니다.
import psycopg
conn = psycopg.connect("postgresql://...?sslmode=verify-full")
```

디스크 암호화가 잘돼 있어도 애플리케이션과 데이터베이스 사이 구간이 평문이면 중간자 공격에 취약합니다. TLS는 선택 기능이 아니라 기본 전제입니다. 특히 인증서 검증을 끄는 순간 보호 효과가 크게 약해집니다.

### 3단계 — 저장 구간은 봉투 암호화로 보호합니다

```python
from cryptography.fernet import Fernet
data_key = Fernet(kms.get_data_key())
ciphertext = data_key.encrypt(b"card-number")
```

봉투 암호화는 데이터 암호화에 쓰는 키와 그 키를 보호하는 KMS 키를 분리합니다. 이렇게 해야 키 회전과 접근 통제가 쉬워지고, 데이터와 키가 한곳에 함께 놓이는 실수를 줄일 수 있습니다.

### 4단계 — 조회가 필요하면 결정적 해시를 씁니다

```python
import hmac, hashlib
def lookup_hash(value, key):
    return hmac.new(key, value.encode(), hashlib.sha256).hexdigest()
```

일부 필드는 원문 복호화 없이도 동일 여부만 비교하면 됩니다. 이럴 때 결정적 해시를 쓰면 조회 기능을 유지하면서 원문 노출을 줄일 수 있습니다. 다만 이 키 역시 별도 관리가 필요합니다.

### 5단계 — 백업도 같은 수준으로 보호합니다

```bash
# 백업 파일 자체를 암호화하고 키는 다른 위치에 보관합니다.
gpg --symmetric --cipher-algo AES256 backup.sql
```

현장에서 가장 큰 사고 반경은 종종 운영 데이터베이스보다 백업에서 나옵니다. 백업은 이동과 복사, 장기 보관이 많아서 노출면이 넓습니다. 운영 데이터만 보호하고 백업을 평문으로 두면 저장 보안의 절반만 한 셈입니다.

## 이 코드에서 먼저 볼 점

- 봉투 암호화는 데이터 키와 KMS 키를 분리합니다.
- 결정적 해시는 조회 가능성을 남기지만 원문 노출을 줄입니다.
- 전송 구간과 저장 구간을 함께 보호해야 전체 설계가 완성됩니다.
- 백업과 로그도 저장 보안 범위 안에 있습니다.

## 실무에서 자주 헷갈리는 지점

1. **민감 데이터를 평문으로 저장하는 경우**: 디스크나 백업 파일 하나만 유출돼도 사고가 커집니다.
2. **암호화 키를 코드나 데이터 옆에 두는 경우**: 분리 보관의 이점이 사라집니다.
3. **TLS 인증서 검증을 끄는 경우**: 전송 구간이 중간자 공격에 노출됩니다.
4. **민감 데이터가 로그로 흘러가는 경우**: 로그도 결국 저장소입니다.
5. **백업을 평문으로 보관하는 경우**: 사고 시 가장 넓은 유출 반경을 만듭니다.

## 실무에서는 이렇게 봅니다

대부분의 팀은 AWS KMS, Google Cloud KMS, Vault 같은 KMS 계열 서비스를 중심으로 키를 관리하고, 애플리케이션 데이터에는 봉투 암호화를 적용합니다. 카드 번호처럼 규제 부담이 큰 값은 가능하면 토큰화해서 애초에 내부 시스템에 원문이 들어오지 않게 설계하기도 합니다.

선임 엔지니어는 여기서 수집 최소화 원칙을 함께 봅니다. 가장 강한 보호는 애초에 받지 않는 것입니다. 반드시 받아야 하는 데이터만 남기고, 조회 목적에 따라 해시나 토큰으로 대체할 수 있는지 먼저 검토합니다. 저장 보안은 더 강한 암호보다 더 적은 저장에서 출발하는 경우가 많습니다.

## 선임 엔지니어는 이렇게 생각합니다

- 가장 강한 방어는 덜 수집하는 것입니다.
- 키는 데이터와 물리적으로나 논리적으로 분리돼야 합니다.
- 전송 구간과 저장 구간을 둘 다 보호해야 합니다.
- 키 회전이 불가능하면 설계가 잘못된 것입니다.
- 백업도 운영 데이터와 같은 수준의 데이터입니다.

## 체크리스트

- [ ] PII와 민감 데이터 목록이 정리돼 있습니다.
- [ ] 저장 구간 암호화가 KMS 기반으로 적용돼 있습니다.
- [ ] 전송 구간에 인증서 검증을 포함한 TLS가 적용돼 있습니다.
- [ ] 백업이 암호화돼 있습니다.

## 연습 문제

1. 지금 서비스에서 PII에 해당하는 필드를 모두 적어 보세요.
2. 봉투 암호화 흐름을 그림으로 그려 보세요.
3. 카드 번호를 토큰화하는 함수를 설계해 보세요.

## 정리와 다음 글

안전한 데이터 저장은 디스크 암호화 한 줄로 끝나지 않습니다. 무엇을 모을지 결정하고, 전송과 저장을 함께 보호하며, 키를 분리하고, 백업까지 같은 기준으로 관리해야 비로소 실무 수준의 저장 보안이 됩니다.

다음 글에서는 이 저장 보안을 실제로 지탱하는 비밀값과 키를 어떻게 관리해야 하는지 다룹니다.

## 심화 실전 노트: 봉투 암호화, 필드 암호화, 키 회전, 컴플라이언스

저장 보안은 "암호화했다/안 했다"의 이분법이 아닙니다. 어떤 계층에서 어떤 키로 무엇을 암호화하는지, 키는 어떻게 회전하는지, 규제 요건과 어떻게 매핑되는지까지 구체적으로 설계해야 합니다.

### 봉투 암호화 전체 흐름

봉투 암호화는 데이터를 암호화하는 DEK(Data Encryption Key)와 DEK를 암호화하는 KEK(Key Encryption Key)를 분리하는 구조입니다.

```python
"""envelope_encryption.py — 봉투 암호화 전체 구현"""
import os
import json
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

class EnvelopeEncryption:
    def __init__(self, kms_client):
        self.kms = kms_client

    def encrypt(self, plaintext: bytes, kms_key_id: str) -> dict:
        """봉투 암호화: DEK 생성 → 데이터 암호화 → DEK를 KEK로 암호화"""
        # 1) DEK 생성(256비트 AES 키)
        dek = os.urandom(32)
        nonce = os.urandom(12)

        # 2) DEK로 데이터 암호화 (AES-GCM)
        aesgcm = AESGCM(dek)
        ciphertext = aesgcm.encrypt(nonce, plaintext, None)

        # 3) KMS로 DEK 자체를 암호화
        encrypted_dek = self.kms.encrypt(
            KeyId=kms_key_id,
            Plaintext=dek,
        )["CiphertextBlob"]

        # 4) 암호화된 데이터 + 암호화된 DEK + nonce를 함께 저장
        return {
            "ciphertext": base64.b64encode(ciphertext).decode(),
            "encrypted_dek": base64.b64encode(encrypted_dek).decode(),
            "nonce": base64.b64encode(nonce).decode(),
            "kms_key_id": kms_key_id,
        }

    def decrypt(self, envelope: dict) -> bytes:
        """복호화: KEK로 DEK 복호화 → DEK로 데이터 복호화"""
        # 1) KMS로 DEK 복호화
        dek = self.kms.decrypt(
            CiphertextBlob=base64.b64decode(envelope["encrypted_dek"]),
            KeyId=envelope["kms_key_id"],
        )["Plaintext"]

        # 2) DEK로 데이터 복호화
        aesgcm = AESGCM(dek)
        nonce = base64.b64decode(envelope["nonce"])
        ciphertext = base64.b64decode(envelope["ciphertext"])
        return aesgcm.decrypt(nonce, ciphertext, None)
```

이 구조의 장점:
- DEK가 유출돼도 KEK 없이는 복호화 불가
- KEK 회전 시 데이터를 다시 암호화할 필요 없이 DEK만 새 KEK로 재암호화
- KMS 호출 횟수를 줄이면서도 강한 보호 유지 (DEK는 메모리에서만 존재)

### 필드 수준 암호화

데이터베이스 전체 암호화(TDE)만으로는 애플리케이션 레벨 접근을 통제할 수 없습니다. 특정 필드만 선택적으로 암호화하면 DBA도 민감 데이터 원문을 볼 수 없게 됩니다.

```python
from sqlalchemy import TypeDecorator, String
import json

class EncryptedField(TypeDecorator):
    """SQLAlchemy 컬럼 타입 — 투명한 필드 암호화/복호화"""
    impl = String
    cache_ok = True

    def __init__(self, envelope_enc: EnvelopeEncryption, kms_key_id: str):
        super().__init__()
        self.enc = envelope_enc
        self.kms_key_id = kms_key_id

    def process_bind_param(self, value, dialect):
        """저장 시 암호화"""
        if value is None:
            return None
        envelope = self.enc.encrypt(value.encode("utf-8"), self.kms_key_id)
        return json.dumps(envelope)

    def process_result_value(self, value, dialect):
        """조회 시 복호화"""
        if value is None:
            return None
        envelope = json.loads(value)
        return self.enc.decrypt(envelope).decode("utf-8")

# 사용 예시
class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))  # 일반 필드
    ssn = Column(EncryptedField(enc, "alias/patient-key"))  # 암호화 필드
    diagnosis = Column(EncryptedField(enc, "alias/medical-key"))  # 별도 키
```

필드별로 다른 KMS 키를 쓰면 접근 정책도 필드별로 분리할 수 있습니다. 예를 들어 접수 담당자는 이름만, 의사는 진단 정보까지 볼 수 있게 KMS 키 정책으로 제어합니다.

### 키 회전 절차

키 회전은 단순히 새 키를 만드는 것이 아닙니다. 기존 데이터가 이전 키로 암호화돼 있으므로 점진적 마이그레이션이 필요합니다.

```python
def rotate_dek_for_table(table_name: str, old_key_id: str, new_key_id: str):
    """테이블의 암호화된 필드를 새 키로 재암호화합니다."""
    rows = db.query(table_name).filter(
        table_name.kms_key_version == old_key_id
    ).limit(1000).all()

    for row in rows:
        # 1) 이전 키로 복호화
        plaintext = envelope_enc.decrypt(json.loads(row.encrypted_data))
        # 2) 새 키로 재암호화
        new_envelope = envelope_enc.encrypt(plaintext, new_key_id)
        # 3) 업데이트
        row.encrypted_data = json.dumps(new_envelope)
        row.kms_key_version = new_key_id

    db.commit()
    return len(rows)
```

키 회전 원칙:
1. 회전은 배치로 점진 실행합니다. 한 번에 전체를 바꾸면 장시간 락이 걸립니다.
2. 이전 키와 새 키를 동시에 유효하게 유지하는 grace period가 필요합니다.
3. 회전 진행률을 모니터링하고, 이전 키로 암호화된 레코드가 0이 되면 이전 키를 비활성화합니다.
4. 회전 이력을 감사 로그에 남깁니다.

### 규제 매핑표

| 규제 | 대상 데이터 | 주요 요구사항 | 코드 수준 대응 |
| --- | --- | --- | --- |
| GDPR | EU 거주자 개인정보 | 삭제권, 최소 수집, 암호화 | 필드 암호화 + 삭제 API |
| 개인정보보호법(PIPA) | 한국 거주자 개인정보 | 동의 기반 수집, 안전조치 | 동의 이력 저장 + 암호화 |
| PCI DSS | 카드 번호(PAN) | 토큰화 또는 암호화, 키 분리 | 토큰화 서비스 연동 |
| HIPAA | 의료 정보(PHI) | 접근 통제, 감사, 암호화 | 필드별 키 분리 + 접근 로그 |

각 규제가 요구하는 "암호화"의 수준은 다릅니다. PCI DSS는 PAN의 저장과 전송 모두를 구체적으로 규정하고, GDPR은 기술적 조치의 적절성을 요구합니다. 코드 설계 시점에 대상 규제를 먼저 파악해야 불필요한 재작업을 줄일 수 있습니다.

### 토큰화 서비스 연동

카드 번호처럼 규제 부담이 특히 큰 데이터는 아예 원문을 시스템에 두지 않는 토큰화가 가장 안전합니다.

```python
class TokenizationService:
    """외부 토큰화 서비스를 호출하는 클라이언트"""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.api_key = api_key

    def tokenize(self, pan: str) -> str:
        """카드 번호를 토큰으로 치환합니다. 원문은 내부 시스템에 저장하지 않습니다."""
        resp = httpx.post(
            f"{self.base_url}/tokenize",
            json={"value": pan, "format": "preserving"},
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        resp.raise_for_status()
        return resp.json()["token"]  # 예: "tok_4242424242421234"

    def detokenize(self, token: str) -> str:
        """결제 시점에만 원문을 복원합니다. 접근 감사 필수."""
        resp = httpx.post(
            f"{self.base_url}/detokenize",
            json={"token": token},
            headers={"Authorization": f"Bearer {self.api_key}"},
        )
        resp.raise_for_status()
        return resp.json()["value"]
```

토큰화의 핵심 이점은 PCI DSS 범위를 줄이는 것입니다. 원문 카드 번호가 내부 시스템에 없으면 해당 시스템은 PCI DSS 감사 대상에서 제외됩니다.

### 안전한 삭제와 삭제권 구현

GDPR의 삭제권(Right to Erasure)이나 개인정보보호법의 파기 요청을 코드로 구현하려면 단순 DELETE가 아닌 체계적 접근이 필요합니다.

```python
from datetime import datetime, timezone
from enum import Enum

class DeletionStatus(str, Enum):
    REQUESTED = "requested"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class DeletionRequest:
    id: str
    user_id: str
    requested_at: datetime
    status: DeletionStatus
    affected_systems: list[str]

def process_deletion_request(request_id: str):
    """삭제 요청을 처리합니다. 모든 저장소에서 데이터를 제거합니다."""
    req = get_deletion_request(request_id)
    req.status = DeletionStatus.IN_PROGRESS

    systems = [
        ("primary_db", delete_from_primary_db),
        ("search_index", delete_from_search_index),
        ("analytics", anonymize_in_analytics),
        ("backups", schedule_backup_purge),
        ("logs", redact_from_logs),
        ("cache", invalidate_cache),
    ]

    results = {}
    for system_name, delete_fn in systems:
        try:
            delete_fn(req.user_id)
            results[system_name] = "success"
        except Exception as e:
            results[system_name] = f"failed: {e}"

    if all(v == "success" for v in results.values()):
        req.status = DeletionStatus.COMPLETED
    else:
        req.status = DeletionStatus.FAILED

    # 삭제 이력은 남겨야 합니다 (법적 증빙)
    audit_log(
        "data_deletion",
        user_id=req.user_id,
        results=results,
        completed_at=datetime.now(timezone.utc).isoformat(),
    )
```

삭제 구현에서 놓치기 쉬운 점:
- 백업에서의 삭제는 즉시 불가능할 수 있습니다. 보존 기간이 지나면 자동 제거되도록 설계합니다.
- 분석 데이터는 삭제 대신 익명화가 적절할 수 있습니다.
- 삭제 이력 자체는 법적 증빙으로 보존해야 합니다.
- 캐시와 검색 인덱스도 삭제 대상입니다.

### 백업 암호화와 복구 테스트

백업이 암호화되어 있어도 복구가 불가능하면 의미가 없습니다. 복구 절차를 정기적으로 검증해야 합니다.

```python
import subprocess
from datetime import datetime

def create_encrypted_backup(db_url: str, backup_dir: str, kms_key_id: str) -> str:
    """데이터베이스를 덤프하고 봉투 암호화로 보호합니다."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dump_file = f"{backup_dir}/dump_{timestamp}.sql"
    encrypted_file = f"{dump_file}.enc"

    # 1) DB 덤프
    subprocess.run(
        ["pg_dump", db_url, "-f", dump_file],
        check=True,
    )

    # 2) 봉투 암호화
    with open(dump_file, "rb") as f:
        plaintext = f.read()

    envelope = envelope_enc.encrypt(plaintext, kms_key_id)

    with open(encrypted_file, "w") as f:
        json.dump(envelope, f)

    # 3) 평문 덤프 즉시 삭제
    os.unlink(dump_file)

    return encrypted_file

def verify_backup_restore(encrypted_file: str) -> bool:
    """백업 복구 가능성을 검증합니다. 월 1회 자동 실행 권장."""
    try:
        with open(encrypted_file, "r") as f:
            envelope = json.load(f)
        plaintext = envelope_enc.decrypt(envelope)
        # 복호화된 내용이 유효한 SQL인지 기본 검증
        assert plaintext.startswith(b"--") or plaintext.startswith(b"SET")
        return True
    except Exception as e:
        alert("backup_restore_failed", file=encrypted_file, error=str(e))
        return False
```

백업 보안 체크리스트:
- 백업 파일은 운영 데이터와 같은 수준으로 암호화합니다.
- 백업 복구를 정기적으로 테스트합니다 (최소 월 1회).
- 백업 보존 기간을 규제 요건에 맞춰 설정합니다.
- 백업 접근 로그를 별도로 남깁니다.
- 평문 중간 파일은 즉시 삭제합니다.

## 처음 질문으로 돌아가기

- **저장 중 암호화와 전송 중 암호화는 무엇이 다를까요?**
  - 저장 중 암호화(at-rest)는 디스크에 머무는 데이터를 보호하고, 전송 중 암호화(in-transit)는 네트워크를 이동하는 데이터를 보호합니다. 봉투 암호화 구현에서 보았듯이 저장 중 암호화는 DEK+KEK 구조로 키를 분리하고, 전송 중 암호화는 TLS로 구간을 보호합니다. 둘 다 적용해야 전체 체인이 안전합니다.
- **PII와 민감 데이터를 분류하는 작업이 왜 먼저일까요?**
  - 규제 매핑표에서 보았듯이 데이터 종류에 따라 적용할 보호 수준과 규제가 다릅니다. 분류 없이 일괄 암호화하면 과잉 보호로 성능이 나빠지거나, 반대로 규제 대상을 놓쳐 법적 위험이 생깁니다. 1단계의 SENSITIVE 분류가 모든 후속 결정의 기준이 됩니다.
- **대칭키, 비대칭키, KMS는 어떤 역할로 나뉠까요?**
  - 봉투 암호화에서 데이터는 대칭키(AES-GCM)로 빠르게 암호화하고, 그 대칭키는 KMS가 관리하는 KEK로 보호합니다. 비대칭키는 키 교환이나 서명에 사용됩니다. KMS는 KEK의 저장·접근 통제·회전·감사를 담당하는 중앙 서비스입니다.
<!-- toc:begin -->
## 시리즈 목차

- [Secure Coding 101 (1/10): Secure Coding이란 무엇인가?](./01-what-is-secure-coding.md)
- [Secure Coding 101 (2/10): 입력값 검증](./02-input-validation.md)
- [Secure Coding 101 (3/10): 인증과 세션](./03-authentication-and-session.md)
- [Secure Coding 101 (4/10): 인가와 권한](./04-authorization-and-permissions.md)
- **안전한 데이터 저장 (현재 글)**
- Secret과 키 관리 (예정)
- SQL Injection과 ORM 안전 사용 (예정)
- XSS와 CSRF 방어 (예정)
- Dependency 취약점 관리 (예정)
- 안전한 로깅과 감사 (예정)

<!-- toc:end -->

## 참고 자료

- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [AWS KMS — Envelope Encryption](https://docs.aws.amazon.com/kms/latest/developerguide/concepts.html)
- [Google Cloud KMS](https://cloud.google.com/kms/docs)
- [HashiCorp Vault](https://developer.hashicorp.com/vault/docs)
- [NIST SP 800-57 Part 1 Rev. 5 — Key Management](https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final)

- [이 시리즈 예제 코드](https://github.com/yeongseon-books/book-examples/tree/main/secure-coding-101/ko)

Tags: Encryption, DataProtection, PII, SecureCoding, Cryptography
