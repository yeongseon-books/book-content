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

## 먼저 던지는 질문

- inode와 디렉터리 엔트리는 파일을 어떻게 표현할까요?
- 페이지 캐시와 `fsync`는 각각 어디까지를 보장할까요?
- 저널링은 충돌 이후 어떤 복구를 가능하게 할까요?

## 큰 그림

![Operating Systems 101 8장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/08/08-01-the-path-from-write-to-durable-storage.ko.png)

*Operating Systems 101 8장 흐름 개요*

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


## 운영체제 개념을 실무 판단으로 연결하기

### 스케줄링 정책을 숫자로 비교하는 방법
스케줄링은 이론 용어보다 대기시간과 응답시간으로 비교할 때 이해가 빠릅니다. 예를 들어 작업 집합이 `P1(도착 0, 실행 7)`, `P2(도착 2, 실행 4)`, `P3(도착 4, 실행 1)`일 때 FCFS와 SRTF의 결과를 비교하면 차이가 명확합니다.

- FCFS 평균 대기시간: `(0 + 5 + 7) / 3 = 4.0`
- SRTF 평균 대기시간: `(5 + 1 + 0) / 3 = 2.0`

같은 작업 집합이라도 정책에 따라 사용자 체감 지연이 크게 달라집니다. 서버가 인터랙티브 트래픽 중심인지, 배치 작업 중심인지에 따라 정책 선택 기준이 달라져야 합니다.

### 메모리 계층과 페이지 교체를 그림으로 정리하기
가상 메모리에서는 "어떤 페이지를 언제 내보내는가"가 성능을 좌우합니다. 아래 개념도는 자주 발생하는 페이지 폴트 경로를 보여줍니다.

```text
CPU 접근 -> 페이지 테이블 조회 -> miss
miss -> 페이지 폴트 트랩 -> 커널 핸들러
핸들러 -> victim 페이지 선택(LRU 근사)
victim dirty? yes -> 디스크 write-back
새 페이지 read -> 매핑 갱신 -> 재실행
```

핵심은 디스크 I/O가 개입되는 순간 지연이 급증한다는 점입니다. 따라서 워킹셋을 메모리에 유지하도록 데이터 구조와 접근 패턴을 설계해야 합니다. 순차 접근과 지역성 높은 캐시 친화 구조가 중요한 이유가 여기에 있습니다.

### 시스템 콜 경계에서 비용이 발생하는 이유
애플리케이션 코드는 사용자 모드에서 실행되지만, 파일 I/O와 네트워크 I/O는 커널 모드 전환이 필요합니다. 전환이 잦으면 오버헤드가 누적되므로 호출 단위를 조정하는 것이 좋습니다.

| syscall | 용도 | 성능 관점 포인트 |
| --- | --- | --- |
| `read` | 파일/소켓 입력 | 작은 크기로 반복 호출하면 전환 비용 증가 |
| `write` | 파일/소켓 출력 | 버퍼링 없이 자주 호출하면 처리량 저하 |
| `open` | 파일 디스크립터 획득 | 반복 open/close는 캐시 이점 상실 |
| `epoll_wait` | 이벤트 대기 | 다중 연결 처리에서 busy loop 방지 |
| `mmap` | 파일 메모리 매핑 | 랜덤 접근 workload에서 복사 비용 절감 가능 |

예를 들어 로그 수집기를 구현할 때 `write`를 1줄마다 호출하기보다 버퍼 단위로 모아 호출하면 syscall 횟수가 줄어 처리량이 개선됩니다. 운영체제 지식이 코드 수준 최적화로 직접 이어지는 지점입니다.

### 병행성 디버깅 체크리스트
경합 문제를 조사할 때는 증상만 보지 말고 스케줄링, 락 소유 시간, I/O 대기 시간을 함께 봐야 합니다.

1. `pidstat -w`로 컨텍스트 스위치 급증 여부 확인
2. `vmstat 1`로 run queue 길이와 I/O wait 확인
3. `strace -f -tt`로 블로킹 syscall 지점 식별
4. 락 획득/반납 시각을 애플리케이션 로그에 기록

이 네 단계를 함께 적용하면 "CPU가 느린 문제"인지 "락 경합 문제"인지 "디스크 대기 문제"인지를 분리할 수 있습니다. 운영체제 개념은 결국 문제를 정확히 분해하는 관측 프레임입니다.

## 시스템 관찰 지표와 커널 동작의 연결

### run queue와 CPU 사용률을 함께 읽기
CPU 사용률이 낮다고 항상 여유가 있는 것은 아닙니다. run queue 길이가 길고 I/O wait가 높으면 병목이 디스크나 네트워크일 수 있습니다.

```bash
vmstat 1
mpstat -P ALL 1
iostat -xz 1
```

세 도구를 같이 보면 CPU 바운드인지 I/O 바운드인지 분리할 수 있습니다. 운영체제 관점에서 중요한 것은 단일 지표가 아니라 지표 간 관계입니다.

### 페이지 폴트와 메모리 압박 해석
메모리 문제는 OOM 직전에야 드러나는 경우가 많습니다. 아래 지표를 주기적으로 보면 이상 징후를 조기에 잡을 수 있습니다.

- major page fault 증가: 디스크에서 페이지를 자주 끌어오는 상태
- swap in/out 급증: 워킹셋이 물리 메모리를 초과한 상태
- reclaim 스레드 활동 증가: 커널이 메모리 회수에 과도한 시간을 쓰는 상태

애플리케이션이 GC를 쓰는 런타임이라면, 힙 크기 조정과 객체 생존 시간 최적화가 커널 메모리 압박을 완화하는 직접 수단이 됩니다.

### 시스템 콜 추적으로 성능 병목 찾기
`strace`는 느리지만 원인 파악에는 매우 강력합니다. 호출 빈도와 지연 구간을 보면 어떤 API 사용이 비효율적인지 확인할 수 있습니다.

```bash
strace -f -c -p <pid>
```

요약표에서 `read`, `write`, `futex`, `epoll_wait` 비중이 높게 나오면 각각 I/O, 락 경합, 이벤트 대기 구조를 의심할 수 있습니다. 이후 애플리케이션 코드에서 버퍼 크기, 락 범위, 이벤트 루프 타임아웃을 조정하는 식으로 대응합니다.

### 스케줄링과 우선순위 튜닝 주의점
`nice`와 `ionice`는 빠른 응급처치지만, 남용하면 전체 시스템 공정성을 해칠 수 있습니다. 특정 작업의 우선순위를 올리면 다른 서비스의 tail latency가 악화될 수 있기 때문입니다.

운영 환경에서는 다음 원칙을 권장합니다. 첫째, 우선순위 조정은 임시 대응으로 제한합니다. 둘째, 조정 전후 지표를 캡처해 회귀를 확인합니다. 셋째, 근본 원인은 워크로드 분리, 큐 제어, 배치 시간 분산으로 해결합니다. 운영체제 기능은 문제를 숨기는 도구가 아니라 구조를 개선하기 위한 관측/제어 도구입니다.

### 운영 트러블슈팅 미니 시나리오
실무에서 자주 보는 상황은 "요청량은 비슷한데 지연이 갑자기 증가"하는 경우입니다. 이때 애플리케이션 로그만 보면 원인이 흐려질 수 있으므로, 커널 관점 지표를 먼저 확인하는 편이 정확합니다. 메모리 글에서는 page fault와 swap 동향을 보고 워킹셋 이탈 여부를 판단하고, 파일시스템 글에서는 fsync 빈도와 디스크 큐 대기시간을 함께 봐서 쓰기 경합을 확인하고, 시스템 콜 글에서는 `strace -c`로 호출 분포를 잡아 과도한 모드 전환을 식별합니다. 이 절차를 표준화해 두면 장애 초기에 원인 후보를 빠르게 줄일 수 있습니다.

## 처음 질문으로 돌아가기

- **inode와 디렉터리 엔트리는 파일을 어떻게 표현할까요?**
  - 본문의 기준은 파일 시스템를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **페이지 캐시와 `fsync`는 각각 어디까지를 보장할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **저널링은 충돌 이후 어떤 복구를 가능하게 할까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Operating Systems 101 (1/10): 운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [Operating Systems 101 (2/10): 프로세스와 스레드](./02-processes-and-threads.md)
- [Operating Systems 101 (3/10): 스케줄링](./03-scheduling.md)
- [Operating Systems 101 (4/10): 동시성과 경쟁 상태](./04-concurrency-and-race-conditions.md)
- [Operating Systems 101 (5/10): 락, 뮤텍스, 세마포어](./05-locks-mutex-semaphore.md)
- [Operating Systems 101 (6/10): 메모리 관리](./06-memory-management.md)
- [Operating Systems 101 (7/10): 가상 메모리](./07-virtual-memory.md)
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
