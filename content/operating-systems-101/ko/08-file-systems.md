---
series: operating-systems-101
episode: 8
title: 파일 시스템
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
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
seo_description: inode, 페이지 캐시, fsync, 저널링이 데이터 안전을 어떻게 지키는지 정리합니다.
last_reviewed: '2026-05-15'
---

# 파일 시스템

파일에 write를 호출했다고 해서 데이터가 곧바로 안전해지는 것은 아닙니다. 메모리 캐시, 저널, 디스크 캐시, 실제 저장 매체를 차례로 통과해야 진짜로 남습니다.

그래서 파일 시스템을 모르면 "분명 저장했는데 왜 사라졌지" 같은 질문에 답하기 어렵습니다. 이 글에서는 안전한 저장이 어떤 약속 위에서 성립하는지 정리합니다.

이 글은 Operating Systems 101 시리즈의 8번째 글입니다.

## 이 글에서 다룰 문제

- inode와 디렉터리 엔트리는 파일을 어떻게 표현할까요?
- 페이지 캐시와 `fsync`는 각각 어디까지를 보장할까요?
- 저널링은 충돌 이후 어떤 복구를 가능하게 할까요?
- 원자적 이름 바꾸기 패턴은 왜 설정 파일 저장에서 자주 쓰일까요?

> 파일 시스템은 단순한 바이트 저장소가 아닙니다. 이름과 inode의 연결, 페이지 캐시, 저널, 디스크 반영 시점을 조합해 "빠름"과 "안전함" 사이에서 어떤 약속을 할지 정하는 계층입니다.

## 기본 모델
> 파일은 inode라는 메타데이터 구조와 데이터 블록의 조합입니다. 디렉터리는 이름과 inode 번호의 매핑일 뿐입니다. write는 보통 페이지 캐시에만 쓰이고, 실제 디스크에는 나중에 내려갑니다. fsync는 "지금 디스크에 내려라"고 OS에 요청하는 호출입니다.

### 쓰기가 안전해지기까지 거치는 경로

![쓰기가 안전해지기까지 거치는 경로](../../../assets/operating-systems-101/08/08-01-the-path-from-write-to-durable-storage.ko.png)
*write가 끝났다는 사실과 디스크에 안전하게 남았다는 사실은 서로 다른 단계입니다.*

```text
path: /var/log/app.log
   ↓ directory lookup
 inode #1234 (metadata: perms, size, block pointers)
   ↓
 data blocks → [page cache] → fsync → [disk]
```

## 같은 코드를 다르게 읽는 법

**이전 관점 — "쓰기 호출을 했으니 안전하다":**

```python
with open('config.json', 'w') as f:
    f.write(new_config)
# What if the power dies here? You may end up with an empty or partial file
```

**바꿔서 보면 — "원자적 이름 바꾸기 패턴":**

```python
import os, tempfile, json

def save_atomic(path, data):
    d = os.path.dirname(path) or '.'
    fd, tmp = tempfile.mkstemp(dir=d)
    with os.fdopen(fd, 'w') as f:
        json.dump(data, f)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, path)   # atomic rename within the same FS
```

크래시가 어디에서 일어나도 `path`는 옛 내용 그대로이거나 완전한 새 내용이 됩니다.

## 단계별로 확인하기

### 1단계: 아이노드와 하드 링크 보기

```bash
echo hi > a.txt
ln a.txt b.txt
ls -li a.txt b.txt
# Same inode number — two names, one underlying object
```

디렉터리 항목은 이름→inode 포인터입니다. hard link는 같은 inode에 또 다른 이름을 다는 일.

### 2단계: 페이지 캐시 효과

```bash
# First read goes to disk; second comes from cache
dd if=/dev/zero of=big.bin bs=1M count=100
sync; echo 3 | sudo tee /proc/sys/vm/drop_caches    # clear caches
time wc -c big.bin    # cold (slow)
time wc -c big.bin    # warm (fast)
```

같은 파일에 같은 명령을 썼는데 시간이 수십 배 차이 나면 페이지 캐시 효과가 드러난 것입니다.

### 3단계: 강제 디스크 반영 비용 측정

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

### 4단계: 원자적 이름 바꾸기 패턴 직접 작성

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

# Lines may interleave — append does not give per-line atomicity
```

POSIX는 작은 append에 한해 원자성을 약속하지만, 레코드 분리는 애플리케이션 책임입니다.

## 여기서 먼저 볼 점

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

## 실무에서는 이렇게 본다

- DB: WAL + 그룹 커밋으로 안전성과 처리량을 동시에 확보
- 설정 파일: atomic rename으로 무중단 갱신
- 로그: 한 워커당 한 파일 또는 syslog로 동시 쓰기 회피
- 컨테이너: overlayfs로 layered filesystem 구성
- 백업: hard link로 increment-only 스냅샷

## 체크리스트

- [ ] inode와 디렉터리 항목의 관계를 안다
- [ ] write와 fsync의 차이를 안다
- [ ] atomic rename 패턴을 코드로 쓸 수 있다
- [ ] 페이지 캐시 효과가 시간에 미치는 영향을 안다
- [ ] 동시 쓰기에서 어떤 원자성이 보장되는지 안다

## 연습 문제

1. fsync 유무에 따라 처리량이 얼마나 달라지는지 측정하고, 차이가 큰 이유를 한 문단으로 설명해 보세요.
2. atomic rename으로 설정 파일 저장 함수를 만든 뒤, 중간에 예외를 발생시켜도 원본이 유지되는지 확인해 보세요.
3. 스레드 네 개가 같은 로그 파일에 append하도록 만든 뒤, 라인이 어떻게 섞이는지 관찰해 보세요.

## 마무리와 다음 글

파일 시스템은 "쓰면 끝"이 아니라 페이지 캐시, fsync, atomic rename 같은 약속을 정확히 사용해야 데이터가 안전합니다. 빠름과 안전 사이의 위치는 개발자가 의식적으로 선택해야 합니다.

다음 글에서는 지금까지 본 모든 OS 기능을 코드가 호출하는 방식 — 시스템 콜로 넘어갑니다.

<!-- toc:begin -->
- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [프로세스와 스레드](./02-processes-and-threads.md)
- [스케줄링](./03-scheduling.md)
- [동시성과 경쟁 상태](./04-concurrency-and-race-conditions.md)
- [락, 뮤텍스, 세마포어](./05-locks-mutex-semaphore.md)
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

Tags: Computer Science, 운영체제, 파일시스템, inode, fsync, journaling
