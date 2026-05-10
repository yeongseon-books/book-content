---
series: operating-systems-101
episode: 8
title: 파일 시스템
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Computer Science
  - 운영체제
  - 파일시스템
  - inode
  - fsync
  - journaling
seo_description: inode, 디렉터리 트리, 페이지 캐시, fsync, 저널링 — 파일 시스템이 데이터를 잃지 않게 만드는 원리를 정리합니다.
last_reviewed: '2026-05-04'
---

# 파일 시스템

> Operating Systems 101 시리즈 (8/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: 파일을 쓴 후 갑자기 전원이 끊겨도 데이터가 살아남게 하려면, 운영체제와 디스크는 어떤 약속을 지켜야 할까요?

> "write 했으니 끝"은 거짓말입니다. 파일 시스템은 페이지 캐시, 저널, fsync, 그리고 디스크 자체의 캐시까지 여러 층의 약속을 지켜야 데이터가 안전하게 저장됩니다. 이 약속을 모르면 "분명히 저장했는데 사라진" 사건의 진짜 원인을 영원히 모릅니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- inode와 디렉터리 트리의 구조
- 페이지 캐시와 fsync의 역할
- 저널링이 크래시 안전성을 보장하는 방법
- 동시 쓰기와 atomic rename 패턴

## 왜 중요한가

데이터 유실 사고의 절반은 "fsync를 안 했다" 또는 "rename이 atomic이라고 잘못 가정했다"에서 옵니다. 파일 시스템의 동작 모델을 모르면, 같은 코드가 어느 환경에서는 잘 돌고 어느 환경에서는 데이터를 잃는 미스터리에 휘말립니다. 신뢰할 수 있는 저장은 코드가 아니라 약속의 정확한 사용에서 옵니다.

> 파일 시스템은 "느리지만 안전" 또는 "빠르지만 위험"의 스펙트럼이고, 어디에 점을 찍을지는 개발자의 결정입니다.

## 개념 한눈에 보기

> 파일은 inode라는 메타데이터 구조와 데이터 블록의 조합입니다. 디렉터리는 이름과 inode 번호의 매핑일 뿐입니다. write는 보통 페이지 캐시에만 쓰이고, 실제 디스크에는 나중에 내려갑니다. fsync는 "지금 디스크에 내려라"고 OS에 요청하는 호출입니다.

```text
파일 경로: /var/log/app.log
       ↓ 디렉터리 lookup
   inode #1234 (메타: 권한, 크기, 블록 포인터)
       ↓
   data blocks → [페이지 캐시] → fsync → [디스크]
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| inode | 파일 메타데이터(소유자, 권한, 블록 위치) |
| 페이지 캐시 | 디스크 블록을 캐싱하는 RAM 영역 |
| fsync | 변경분을 디스크에 강제로 내리는 호출 |
| 저널링 | 변경을 기록한 후 적용해 크래시에 안전하게 만드는 기법 |
| atomic rename | 같은 파일 시스템 내에서 rename은 원자적 |

## Before / After

**Before — "write 했으니 안전":**

```python
with open('config.json', 'w') as f:
    f.write(new_config)
# 전원이 여기서 끊기면? 빈 파일 또는 일부만 적힌 파일이 남을 수 있다
```

**After — "atomic rename 패턴":**

```python
import os, tempfile, json

def save_atomic(path, data):
    d = os.path.dirname(path) or '.'
    fd, tmp = tempfile.mkstemp(dir=d)
    with os.fdopen(fd, 'w') as f:
        json.dump(data, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)   # 같은 FS 내 atomic rename
```

크래시가 어디에서 일어나도 `path`는 옛 내용 그대로이거나 완전한 새 내용이 됩니다.

## 실습: 단계별로 따라하기

### 1단계: inode와 hard link 보기

```bash
echo hi > a.txt
ln a.txt b.txt
ls -li a.txt b.txt
# 같은 inode 번호 — 이름만 두 개, 실체는 하나
```

디렉터리 항목은 이름→inode 포인터입니다. hard link는 같은 inode에 또 다른 이름을 다는 일.

### 2단계: 페이지 캐시 효과

```bash
# 처음 read는 디스크에서, 두 번째는 캐시에서
dd if=/dev/zero of=big.bin bs=1M count=100
sync; echo 3 | sudo tee /proc/sys/vm/drop_caches    # 캐시 비우기
time wc -c big.bin    # 첫 read (느림)
time wc -c big.bin    # 두 번째 read (빠름)
```

같은 파일, 같은 명령 — 시간이 수십 배 차이 나면 페이지 캐시가 일하고 있다는 뜻입니다.

### 3단계: fsync 비용 측정

```python
import os, time

def write_n(n, do_sync):
    with open('t.bin', 'wb') as f:
        for _ in range(n):
            f.write(b'x' * 4096)
            if do_sync:
                f.flush(); os.fsync(f.fileno())

t = time.time(); write_n(1000, False); print('no sync', time.time()-t)
t = time.time(); write_n(1000, True);  print('with sync', time.time()-t)
```

fsync는 매번 디스크 회전을 기다리므로 수십~수백 배 느릴 수 있습니다. 그래서 DB는 그룹 커밋을 합니다.

### 4단계: atomic rename 패턴 직접 작성

위 "After" 코드를 그대로 실행해 보고, 중간에 일부러 예외를 던져도 원본 파일이 손상되지 않는지 확인합니다.

### 5단계: 동시에 같은 파일에 쓰기

```python
import threading

def write_lines(name, n):
    with open('shared.log', 'a') as f:
        for i in range(n):
            f.write(f'{name} {i}\n')

ts = [threading.Thread(target=write_lines, args=(f't{i}', 100)) for i in range(4)]
for t in ts: t.start()
for t in ts: t.join()

# 줄이 섞일 수 있다 — append는 라인 원자성을 보장하지 않음
```

POSIX는 작은 append에 한해 원자성을 약속하지만, 레코드 분리는 애플리케이션 책임입니다.

## 이 코드에서 주목할 점

- write는 페이지 캐시까지만 — 디스크는 fsync 후에야 안전
- atomic rename은 데이터 안전성의 가장 단순하고 강력한 패턴
- 페이지 캐시는 두 번째 접근부터 수십 배 빠름
- 동시 append는 라인 원자성을 자동으로 주지 않음

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| write 후 fsync 생략 | 크래시 시 유실 | 중요한 변경은 fsync 호출 |
| 같은 파일에 직접 덮어쓰기 | 부분 쓰기 위험 | tmp 파일 + atomic rename |
| 다른 FS로 rename | 원자성 깨짐 | 같은 FS 안에서만 rename |
| fsync를 모든 write마다 호출 | 처리량 폭락 | 그룹 커밋, 배치 |
| append가 항상 원자적이라 가정 | 라인 섞임 | 명시적 락 또는 큐 |

## 실무에서는 이렇게 쓰입니다

- DB: WAL + 그룹 커밋으로 안전성과 처리량을 동시에 확보
- 설정 파일: atomic rename으로 무중단 갱신
- 로그: 한 워커당 한 파일 또는 syslog로 동시 쓰기 회피
- 컨테이너: overlayfs로 layered filesystem 구성
- 백업: hard link로 increment-only 스냅샷

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "어디까지가 메모리이고 어디부터가 디스크인가"를 항상 의식합니다. 페이지 캐시, OS, 디스크 캐시, 디스크 미디어 — 각 층에 머무는 데이터는 다른 종류의 위험을 가집니다. 어떤 층까지 동기화했는지 명시할 수 없다면, 그 시스템은 "데이터를 보관한다"고 말할 수 없습니다.

또한 시니어는 atomic rename 같은 작은 패턴을 코드 리뷰의 기본 도구로 씁니다. 데이터 안전성은 거창한 시스템보다 이런 작은 패턴의 일관된 사용에서 옵니다. 그 사용은 "느려도 좋다"가 아니라 "어디서 빠르게, 어디서 안전하게"라는 의식적 선택입니다.

## 체크리스트

- [ ] inode와 디렉터리 항목의 관계를 안다
- [ ] write와 fsync의 차이를 안다
- [ ] atomic rename 패턴을 코드로 쓸 수 있다
- [ ] 페이지 캐시 효과가 시간에 미치는 영향을 안다
- [ ] 동시 쓰기에서 어떤 원자성이 보장되는지 안다

## 연습 문제

1. fsync 있는 버전과 없는 버전의 처리량을 측정하고, 차이가 왜 발생하는지 한 문단으로 설명합니다.

2. atomic rename 패턴으로 설정 파일 갱신 함수를 만들고, 중간에 예외를 던져도 원본이 손상되지 않는지 검증합니다.

3. 4개 스레드가 같은 로그 파일에 동시에 append할 때 라인 섞임이 발생하는지 실험하고 결과를 정리합니다.

## 정리 및 다음 단계

파일 시스템은 "쓰면 끝"이 아니라 페이지 캐시, fsync, atomic rename 같은 약속을 정확히 사용해야 데이터가 안전합니다. 빠름과 안전 사이의 위치는 개발자가 의식적으로 선택해야 합니다.

다음 글에서는 지금까지 본 모든 OS 기능을 코드가 호출하는 방식 — 시스템 콜로 넘어갑니다.

<!-- toc:begin -->
- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [프로세스와 스레드](./02-processes-and-threads.md)
- [스케줄링](./03-scheduling.md)
- [동시성과 race condition](./04-concurrency-and-race-conditions.md)
- [lock, mutex, semaphore](./05-locks-mutex-semaphore.md)
- [메모리 관리](./06-memory-management.md)
- [가상 메모리](./07-virtual-memory.md)
- **파일 시스템 (현재 글)**
- 시스템 콜 (예정)
- 컨테이너와 운영체제 (예정)
<!-- toc:end -->

## 참고 자료

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Linux fsync(2) man page](https://man7.org/linux/man-pages/man2/fsync.2.html)
- [PostgreSQL — Reliability and the Write-Ahead Log](https://www.postgresql.org/docs/current/wal-reliability.html)
- [LWN — Ensuring data reaches disk](https://lwn.net/Articles/457667/)
