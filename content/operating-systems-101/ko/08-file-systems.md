---
series: operating-systems-101
episode: 8
title: "Operating Systems 101 (8/10): 파일 시스템"
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

# Operating Systems 101 (8/10): 파일 시스템

파일에 write를 호출했다고 해서 데이터가 곧바로 안전해지는 것은 아닙니다. 메모리 캐시, 저널, 디스크 캐시, 실제 저장 매체를 차례로 통과해야 진짜로 남습니다.

그래서 파일 시스템을 모르면 "분명 저장했는데 왜 사라졌지" 같은 질문에 답하기 어렵습니다. 이 글에서는 안전한 저장이 어떤 약속 위에서 성립하는지 정리합니다.

이 글은 Operating Systems 101 시리즈의 8번째 글입니다.

![Operating Systems 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/08/08-01-the-path-from-write-to-durable-storage.ko.png)
*Operating Systems 101 8장 흐름 개요*

## 이 글에서 다룰 문제

- inode와 디렉터리 엔트리는 파일을 어떻게 표현할까요?
- 페이지 캐시와 `fsync`는 각각 어디까지를 보장할까요?
- 저널링은 충돌 이후 어떤 복구를 가능하게 할까요?
- 이 개념을 실무에서 잘못 적용하면 어떤 문제가 생길까요?
- 이 주제에서 초보자가 가장 자주 놓치는 포인트는 무엇일까요?

## 기본 모델

> 파일은 inode라는 메타데이터 구조와 데이터 블록의 조합입니다. 디렉터리는 이름과 inode 번호의 매핑일 뿐입니다. write는 보통 페이지 캐시에만 쓰이고, 실제 디스크에는 나중에 내려갑니다. fsync는 "지금 디스크에 내려라"고 OS에 요청하는 호출입니다.

### 쓰기가 안전해지기까지 거치는 경로

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
# 여기서 전원이 꺼지면? 빈 파일이나 불완전한 파일이 남을 수 있습니다
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

디렉터리 항목은 이름→inode 포인터입니다. hard link는 같은 inode에 또 다른 이름을 다는 일입니다.

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

# 행이 섞일 수 있습니다 — append는 행 단위 원자성을 보장하지 않습니다
```

POSIX는 작은 append에 한해 원자성을 약속하지만, 레코드 분리는 애플리케이션 책임입니다.

## 자주 하는 실수

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

## 운영 체크리스트

- [ ] inode와 디렉터리 항목의 관계를 안다
- [ ] write와 fsync의 차이를 안다
- [ ] atomic rename 패턴을 코드로 쓸 수 있다
- [ ] 페이지 캐시 효과가 시간에 미치는 영향을 안다
- [ ] 동시 쓰기에서 어떤 원자성이 보장되는지 안다

## 시스템 관찰: 파일 시스템 내구성 체크리스트

파일 저장 코드의 안전성은 "정상 종료"가 아니라 "비정상 종료"에서 평가해야 합니다.

### fsync 비용과 그룹 커밋

```bash
# iostat으로 디스크 쓰기 지연 측정
iostat -xz 1
# await: 평균 I/O 대기 시간 (ms)
# w_await: 쓰기 대기 시간
```

`await`가 높으면 fsync가 너무 자주 호출되거나 디스크가 느린 것입니다. 그룹 커밋은 여러 fsync 요청을 묶어 한 번의 I/O로 처리해 throughput을 높입니다.

### 원자적 저장 절차 표준안

```python
import os, tempfile

def atomic_write(path, data: bytes):
    d = os.path.dirname(path) or '.'
    fd, tmp = tempfile.mkstemp(dir=d)
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
        # 디렉터리 메타데이터도 내구성 보장
        dirfd = os.open(d, os.O_DIRECTORY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    except Exception:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
```

이 네 단계를 모두 거쳐야 크래시 이후에도 완전한 데이터가 보장됩니다.

### 저널링 복구 관점

저널링 파일시스템(ext4, xfs)은 메타데이터 일관성을 복구해 주지만, 애플리케이션 레코드 원자성까지 자동 보장하지는 않습니다. 따라서 애플리케이션 계층에서 append 단위, checksum, commit marker를 함께 설계해야 합니다.

| 파일시스템 이벤트 | 저널링이 보장 | 저널링이 보장하지 않음 |
| --- | --- | --- |
| 메타데이터(크기, 시간) | 일관성 복구 | |
| 데이터 내용 | data=journal 모드에서만 | 기본 모드에서는 미보장 |
| 애플리케이션 레코드 경계 | | 애플리케이션이 직접 관리 |

## 처음 질문으로 돌아가기

- **inode와 디렉터리 엔트리는 파일을 어떻게 표현할까요?**
  - inode는 파일의 메타데이터(크기, 권한, 수정 시각, 데이터 블록 포인터)를 저장하는 구조체입니다. 디렉터리 엔트리는 "파일명 → inode 번호"의 매핑입니다. 파일 이름 자체는 inode에 없고 디렉터리에 있기 때문에, 하드 링크는 같은 inode를 가리키는 여러 이름입니다.
- **페이지 캐시와 `fsync`는 각각 어디까지를 보장할까요?**
  - `write` 시스템 콜은 커널의 페이지 캐시까지만 씁니다. 커널이 캐시를 비울 때 비로소 디스크에 내려갑니다. `fsync`는 "지금 당장 디스크까지 내려가라"를 요청해, 호출이 반환된 시점에는 디스크에 안전하게 기록된 것을 보장합니다.
- **저널링은 충돌 이후 어떤 복구를 가능하게 할까요?**
  - 저널링 파일시스템은 실제 변경 전에 저널에 "무엇을 할 것인지" 기록합니다. 크래시 후 재부팅 시 저널을 확인해 완료된 트랜잭션만 반영하고 불완전한 것은 롤백합니다. 이로써 fsck 없이도 파일시스템 메타데이터 일관성을 빠르게 복원합니다.

## 연습 문제

1. fsync 유무에 따라 처리량이 얼마나 달라지는지 측정하고, 차이가 큰 이유를 한 문단으로 설명해 보세요.
2. atomic rename으로 설정 파일 저장 함수를 만든 뒤, 중간에 예외를 발생시켜도 원본이 유지되는지 확인해 보세요.
3. 스레드 네 개가 같은 로그 파일에 append하도록 만든 뒤, 라인이 어떻게 섞이는지 관찰해 보세요.

## 마무리와 다음 글

파일 시스템은 "쓰면 끝"이 아니라 페이지 캐시, fsync, atomic rename 같은 약속을 정확히 사용해야 데이터가 안전합니다. 빠름과 안전 사이의 위치는 개발자가 의식적으로 선택해야 합니다.

다음 글에서는 지금까지 본 모든 OS 기능을 코드가 호출하는 방식 — 시스템 콜로 넘어갑니다.

<!-- toc:begin -->
## 시리즈 목차

- [Operating Systems 101 (1/10): 운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [Operating Systems 101 (2/10): 프로세스와 스레드](./02-processes-and-threads.md)
- [Operating Systems 101 (3/10): 스케줄링](./03-scheduling.md)
- [Operating Systems 101 (4/10): 동시성과 경쟁 상태](./04-concurrency-and-race-conditions.md)
- [Operating Systems 101 (5/10): 락, 뮤텍스, 세마포어](./05-locks-mutex-semaphore.md)
- [Operating Systems 101 (6/10): 메모리 관리](./06-memory-management.md)
- [Operating Systems 101 (7/10): 가상 메모리](./07-virtual-memory.md)
- **Operating Systems 101 (8/10): 파일 시스템 (현재 글)**
- [Operating Systems 101 (9/10): 시스템 콜](./09-system-calls.md)
- [Operating Systems 101 (10/10): 컨테이너와 운영체제](./10-containers-and-the-os.md)

<!-- toc:end -->

## 참고 자료

- [Operating Systems 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/operating-systems-101/ko)
- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [Linux fsync(2) man page](https://man7.org/linux/man-pages/man2/fsync.2.html)
- [PostgreSQL — Reliability and the Write-Ahead Log](https://www.postgresql.org/docs/current/wal-reliability.html)
- [LWN — Ensuring data reaches disk](https://lwn.net/Articles/457667/)

Tags: Computer Science, 운영체제, 파일시스템, inode, fsync, journaling
