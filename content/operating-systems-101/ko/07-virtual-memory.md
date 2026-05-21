---
series: operating-systems-101
episode: 7
title: "Operating Systems 101 (7/10): 가상 메모리"
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
  - 가상메모리
  - paging
  - TLB
  - swap
seo_description: 페이지, 페이지 테이블, TLB, 스왑, 페이지 폴트의 핵심을 정리합니다.
last_reviewed: '2026-05-15'
---

# Operating Systems 101 (7/10): 가상 메모리

프로세스는 늘 자기만의 넓은 메모리를 가진 것처럼 보입니다. 하지만 실제 RAM은 한정되어 있고, 여러 프로세스가 동시에 그 자원을 나눠 씁니다.

이 착시를 만드는 장치가 바로 가상 메모리입니다. 페이지 폴트와 스왑이 왜 시스템 전체를 갑자기 얼어붙게 만드는지 이해하려면 이 환상을 구성하는 부품부터 봐야 합니다.

이 글은 Operating Systems 101 시리즈의 7번째 글입니다.


![Operating Systems 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/operating-systems-101/07/07-01-how-a-virtual-address-reaches-ram.ko.png)
*Operating Systems 101 7장 흐름 개요*

## 먼저 던지는 질문

- 가상 주소와 물리 주소는 왜 굳이 분리되어 있을까요?
- 페이지, 페이지 테이블, TLB는 어떤 역할 분담을 할까요?
- minor fault와 major fault는 비용이 어떻게 다를까요?

## 기본 모델
> 모든 프로세스는 자신만의 가상 주소 공간을 가집니다. 가상 주소는 페이지 단위(보통 4KB)로 잘려 페이지 테이블을 통해 물리 주소로 매핑됩니다. CPU는 이 변환을 빠르게 하기 위해 TLB라는 캐시를 가집니다. 매핑이 없거나 페이지가 디스크에 있으면 page fault가 발생합니다.

### 가상 주소가 실제 RAM으로 가는 길

```text
virtual addr  →  [TLB hit]  →  physical addr  →  RAM
                   ↓ miss
              page table walk
                   ↓ not present
              page fault → OS handles (read from disk / allocate new page)
```

## 같은 코드를 다르게 읽는 법

**이전 관점 — "상주 메모리만 보면 충분하다":**

```bash
ps -o pid,rss,cmd -p $$
# Not enough. Two processes with the same RSS can have very different speeds
```

**바꿔서 보면 — "페이지 폴트와 변환 캐시 실패를 함께 본다":**

```bash
# major fault = went to disk (slow)
ps -o pid,min_flt,maj_flt,rss,cmd -p $$
# Rising major faults suggests swap-in
```

같은 RSS여도 page fault 패턴이 다르면 체감 속도가 다릅니다.

## 단계별로 확인하기

### 1단계: 페이지 폴트 카운트 보기

```bash
python3 -c "
import resource
r = resource.getrusage(resource.RUSAGE_SELF)
print('minor faults', r.ru_minflt)
print('major faults', r.ru_majflt)
"
```

minor fault는 RAM에서 새 페이지를 잡는 비용, major fault는 디스크에서 읽어오는 비용입니다. major가 늘면 swap 의심.

### 2단계: 메모리 매핑으로 큰 파일 읽기

```python
import mmap, os

with open('big.bin', 'wb') as f:
    f.write(b'A' * (10 * 1024 * 1024))     # 10MB

with open('big.bin', 'rb') as f:
    with mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ) as mm:
        print(mm[0:10])                     # only touched pages get loaded
```

mmap은 파일을 가상 메모리로 직접 매핑합니다. 실제 접근하는 페이지만 RAM에 올라와 큰 파일을 메모리처럼 다룰 수 있습니다.

### 3단계: 쓰기 시 복사 동작 관찰

```python
import os, time

big = bytearray(100 * 1024 * 1024)          # 100MB
pid = os.fork()
if pid == 0:                                 # child
    # Initially shares pages with the parent (CoW)
    big[0] = 1                               # write triggers a page copy
    time.sleep(2)
    os._exit(0)
else:
    os.waitpid(pid, 0)
```

`fork`는 페이지를 즉시 복사하지 않고, 쓰기가 일어날 때만 복사합니다. 메모리를 거의 안 쓰고 자식 프로세스를 만들 수 있는 핵심 기법입니다.

### 4단계: 스왑 사용량 보기

```bash
free -h
swapon --show
# or
cat /proc/swaps
```

스왑이 보이고 응답 시간이 무너진다면 RAM이 부족하거나 실제로 자주 만지는 메모리 범위가 RAM을 넘어선 상태입니다.

### 5단계: 큰 배열 접근 패턴과 변환 캐시

```python
import time
N = 5000
m = [[0]*N for _ in range(N)]

t = time.time()
for i in range(N):
    for j in range(N):
        m[i][j] = 1                          # row-major — good page locality
print('row-major', time.time() - t)

t = time.time()
for j in range(N):
    for i in range(N):
        m[i][j] = 1                          # column-major — TLB/cache misses explode
print('col-major', time.time() - t)
```

같은 데이터, 같은 횟수, 다른 접근 패턴 — 결과는 수 배 차이 납니다. 가상 메모리의 비용은 접근 패턴이 결정합니다.

## 여기서 먼저 볼 점

- mmap은 파일 I/O를 메모리 접근으로 바꿉니다 — 큰 데이터에 자연스러운 추상화
- copy-on-write는 fork를 가볍게 만드는 핵심 기법입니다
- swap이 보이기 시작하면 응답 시간은 이미 무너지고 있습니다
- 같은 RSS여도 접근 지역성에 따라 체감 속도가 크게 달라집니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| RSS만 보고 메모리 판단 | swap, page fault 무시 | major fault, swap 사용량 같이 모니터링 |
| 큰 파일을 모두 read | OOM 또는 swap | mmap 또는 chunk 스트리밍 |
| fork 후 즉시 큰 데이터 수정 | CoW 무력화, 메모리 폭증 | exec 직전까지 쓰기 최소화 |
| 접근 지역성 무시 | TLB miss 폭증 | 데이터 구조와 루프 순서를 함께 설계 |
| swap on이면 안전 | 사실 응답 시간 폭락 | 운영 시스템에서는 swap을 끄거나 최소화 |

## 실무에서는 이렇게 본다

- 데이터베이스: mmap으로 인덱스/페이지 캐시
- 컨테이너: cgroup memory + swap 설정으로 OOM 동작 제어
- ML 학습: 큰 배열은 mmap-backed numpy로 메모리 압박 완화
- 백엔드: fork 기반 워커 모델 (gunicorn, uwsgi)에서 CoW 활용
- 성능 튜닝: perf 등으로 TLB miss / page fault 측정

## 체크리스트

- [ ] 가상 주소와 물리 주소의 차이를 안다
- [ ] minor fault와 major fault의 비용 차이를 안다
- [ ] mmap이 언제 유용한지 안다
- [ ] copy-on-write의 의미를 설명할 수 있다
- [ ] swap이 보이기 시작하면 위험 신호임을 안다

## 연습 문제

1. 같은 2차원 배열을 row-major와 column-major로 채우고, 실행 시간 차이가 나는 이유를 페이지 지역성 관점에서 설명해 보세요.
2. 1GB 파일을 `read()`와 `mmap` 두 방식으로 처리해 RSS와 시간을 비교해 보세요.
3. 같은 메모리 부하를 swap on/off 환경에서 실행하고 응답성 차이를 기록해 보세요.

## 마무리와 다음 글

가상 메모리는 OS가 만든 환상이지만, page fault와 swap이라는 청구서로 정확히 비용을 회수합니다. mmap과 copy-on-write 같은 기법은 이 환상을 응용해 큰 데이터를 우아하게 다룹니다. 가상 메모리를 알면 시스템이 굳는 순간을 짚어낼 수 있습니다.

다음 글에서는 OS가 메모리만큼이나 자주 다루는 자원 — 파일 시스템으로 넘어갑니다.


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


## 페이지 테이블 워크를 손으로 따라가기

가상 주소 변환은 그림으로만 보면 추상적이지만, 숫자를 넣어 한 번 계산하면 정확히 이해됩니다.

가정:
- 32비트 가상 주소
- 페이지 크기 4KB(12비트 offset)
- 2단계 페이지 테이블(10비트 + 10비트 + 12비트)

가상 주소 `0x1234ABCD`를 분해하면:

```text
0x1234ABCD = [PDI:0x48][PTI:0x34A][OFF:0xBCD]
```

1. CR3가 가리키는 page directory에서 `PDI=0x48` 엔트리 조회
2. 엔트리가 present이면 page table base 획득
3. page table에서 `PTI=0x34A` 엔트리 조회
4. 엔트리의 frame base + `OFF=0xBCD` => 물리 주소 완성

### 페이지 폴트 처리 흐름

```text
CPU access -> TLB miss -> page walk
page not present -> #PF trap
kernel checks VMA and permission
valid: allocate/read page, update PTE, resume
invalid: SIGSEGV
```

### TLB 미스 비용 줄이기 팁

- 순차 접근으로 지역성을 높입니다.
- 큰 페이지(huge page)를 검토합니다.
- 랜덤 인덱스 접근 구조를 배치 처리로 완화합니다.

이 기준은 대형 행렬, 검색 인덱스, 캐시 서버 같은 워크로드에서 바로 성능 차이로 드러납니다.


## 심화 실습: 운영체제 문제를 계층별로 좁히는 워크북

실무에서 운영체제 문제는 보통 "느리다", "가끔 멈춘다", "재시작하면 잠깐 괜찮다"처럼 모호한 문장으로 시작합니다. 이때 중요한 것은 추측을 늘리는 것이 아니라, 관찰 단위를 줄여서 재현 가능한 사실로 바꾸는 일입니다. 아래 워크북은 CPU 스케줄링, 메모리 압박, 시스템 콜 패턴, 파일 시스템 내구성, 락 경합을 같은 순서로 점검하도록 구성했습니다.

### 1) 증상 분류: 실행 대기인가, I/O 대기인가

```bash
vmstat 1
pidstat -w -p <PID> 1
iostat -xz 1
```

- `r`(run queue)가 길고 `wa`가 낮으면 CPU 경쟁이 중심입니다.
- `wa`가 높고 디스크 지연이 길면 I/O 병목 가능성이 큽니다.
- 컨텍스트 스위치(`cs`)가 급증하면 락 경합이나 과도한 타임슬라이스 분할을 의심합니다.

이 단계의 목표는 "CPU가 부족하다" 같은 포괄 진단이 아니라, "CPU runnable 대기"와 "디스크 대기"를 명확히 분리하는 것입니다.

### 2) 메모리 계층 점검: RSS, 페이지 폴트, 스왑

```bash
cat /proc/<PID>/status | grep -E "VmRSS|VmSize|Threads"
cat /proc/<PID>/stat | awk '{print "minflt=" $10 ", majflt=" $12}'
free -h
cat /proc/swaps
```

- `majflt` 증가: 디스크에서 페이지를 자주 가져오는 상태입니다.
- 스왑 사용 증가: 워킹셋이 물리 메모리를 넘어 응답성이 무너지기 쉬운 상태입니다.
- 스레드 수 급증 + RSS 증가: 스택 증가와 큐 적체를 같이 확인해야 합니다.

메모리 이슈는 OOM 시점보다 그 이전 신호를 보는 것이 중요합니다. RSS만 보면 늦고, 페이지 폴트와 스왑 추세를 같이 봐야 앞단에서 대응할 수 있습니다.

### 3) 시스템 콜 트레이스: 호출 의미를 비용으로 읽기

```bash
strace -f -tt -T -c -p <PID>
```

요약표에서 자주 보는 패턴:
- `read`/`write` 호출 수 과다: 버퍼링 단위가 너무 작을 가능성
- `futex` 비중 과다: 락 경합, 임계 구역 과대
- `epoll_wait` 비중 높음: 이벤트 대기 중심 workload
- `openat`/`close` 반복 과다: 핸들 재사용 부족

시스템 콜 추적은 "언어 런타임 이슈"를 "커널 경계 비용"으로 번역해 줍니다. 이 번역이 되면 코드 수정 지점이 훨씬 구체적으로 보입니다.

### 4) 스케줄링 정책을 간단 모델로 검증

아래처럼 작은 작업 집합을 만들어 정책 차이를 먼저 머리로 검증해 두면, 실제 서비스 지표 해석이 쉬워집니다.

```text
작업 집합: A(도착0,실행6), B(도착1,실행2), C(도착2,실행1)

FCFS:
0      6  8 9
|---A---|-B|-C|
평균 대기시간 = (0 + 5 + 6) / 3 = 3.67

SRTF:
0 1 3 4     9
|A|B|C|--A--|
평균 대기시간 = (3 + 0 + 1) / 3 = 1.33
```

서비스가 인터랙티브 중심이면 짧은 작업 응답성 개선이 체감 품질을 좌우합니다. 반대로 배치 중심이면 컨텍스트 스위치 감소와 처리량 안정성이 더 중요할 수 있습니다.

### 5) 파일 시스템 안정성 검증 시나리오

저장 코드는 정상 흐름이 아니라 비정상 종료를 기준으로 검증해야 합니다.

검증 순서:
1. 임시 파일에 기록
2. `fsync(fd)`
3. `rename`
4. 부모 디렉터리 `fsync(dirfd)`

이 절차를 지키면 전원 장애나 프로세스 크래시에서도 "부분 파일" 위험을 크게 줄일 수 있습니다. 운영체제는 내구성을 제공하지만, 애플리케이션이 내구성 경계를 정확히 호출해 주어야 보장이 성립합니다.

### 6) 데드락과 락 경합을 구분해서 대응

데드락은 진행이 완전히 멈추고, 락 경합은 진행은 되지만 매우 느린 상태입니다. 둘은 대응이 다릅니다.

- 데드락 대응: 락 획득 순서 전역 규약, 타임아웃, 순환 대기 탐지
- 경합 대응: 임계 구역 단축, 락 분할, 공유 상태 축소, 큐 기반 전달

```text
T1: lock(A) -> wait(B)
T2: lock(B) -> wait(A)
=> 순환 대기, 데드락
```

대부분의 서비스 장애는 완전 데드락보다 "느린 경합" 형태로 나타납니다. `futex` 비중, 대기 큐 길이, p95 지연시간을 함께 보면 판별이 쉽습니다.

### 7) 컨테이너 환경에서 반드시 추가할 관찰 항목

컨테이너에서는 호스트와 보이는 값이 다를 수 있으므로 cgroup 파일을 직접 읽어야 합니다.

```bash
cat /sys/fs/cgroup/memory.max
cat /sys/fs/cgroup/memory.current
cat /sys/fs/cgroup/cpu.max
cat /proc/1/cgroup
```

- `memory.max` 대비 `memory.current` 추세로 OOM 위험을 예측합니다.
- `cpu.max` 쿼터가 낮으면 runnable 상태여도 실제 처리량이 제한됩니다.
- PID 1 처리(signal, zombie reap) 상태를 확인합니다.

컨테이너 문제는 애플리케이션 버그와 리소스 격리 정책이 겹쳐 보이는 경우가 많기 때문에, OS 계층과 cgroup 계층을 동시에 보아야 합니다.

### 8) 장애 보고서에 남겨야 할 최소 증거

문제를 재현 가능하게 만들려면 지표 스냅샷을 표준 형식으로 남겨야 합니다.

- 시간: 관찰 시작/종료 시각
- CPU: `vmstat`, `pidstat -w`
- 메모리: `/proc/<pid>/status`, major/minor fault
- 시스템 콜: `strace -c` 상위 10개
- 파일/저장: `fsync` 유무, 쓰기 단위, 저장 방식(덮어쓰기/원자적 교체)
- 동기화: 락 순서, 임계 구역 길이, 타임아웃 정책

이 여섯 항목만 확보해도 "느리다"는 제보를 재현 가능한 기술 보고서로 바꿀 수 있습니다.

### 9) 운영체제 학습을 코드 리뷰 기준으로 연결하기

운영체제 지식은 문답형 지식으로 끝나면 금방 사라집니다. 코드 리뷰 체크리스트로 연결해야 팀의 습관으로 남습니다.

- 시스템 콜 경계: 작은 read/write 반복이 없는가
- 메모리 상한: 캐시에 용량/회수 정책이 있는가
- 동기화 경계: 락 순서 규약이 문서화되어 있는가
- 내구성 경계: 원자적 저장 절차를 따르는가
- 관찰 가능성: `/proc`, strace, 메트릭으로 검증 가능한가

이 체크리스트를 PR 템플릿에 넣으면 운영체제 개념이 설계 단계에서 바로 작동합니다.

### 10) 한 줄 정리

운영체제는 배경지식이 아니라, 성능/안정성/보안 문제를 분해하는 좌표계입니다. 좌표계가 있으면 같은 장애도 더 짧은 시간에 더 정확하게 해결할 수 있습니다.


### 짧은 검증 실습: 5분 점검

아래 세 줄만 실행해도 현재 상태를 빠르게 교차 검증할 수 있습니다.

```bash
vmstat 1 3
cat /proc/self/status | grep -E "State|VmRSS|Threads"
strace -c -e trace=read,write,openat,close python3 -c "open('/etc/hosts').read()"
```

핵심은 단일 지표가 아니라 관계를 보는 것입니다. 실행 대기, 메모리 사용, 시스템 콜 패턴을 함께 보면 원인 후보를 빠르게 줄일 수 있습니다.


### 추가 메모: 페이지 테이블 해석 습관

`majflt`가 증가할 때는 단순히 "메모리가 크다"가 아니라 "현재 접근 패턴이 디스크 왕복을 유발한다"로 해석해야 합니다. 같은 RSS라도 랜덤 접근은 체감 지연을 크게 키웁니다.

## 처음 질문으로 돌아가기

- **가상 주소와 물리 주소는 왜 굳이 분리되어 있을까요?**
  - 본문의 기준은 가상 메모리를 한 덩어리 개념으로 보지 않고 입력, 처리, 검증, 운영 신호가 만나는 경계로 나누어 확인하는 것입니다.
- **페이지, 페이지 테이블, TLB는 어떤 역할 분담을 할까요?**
  - 예제와 그림에서는 어떤 값이 들어오고, 어느 단계에서 바뀌며, 어떤 기준으로 통과 또는 실패하는지를 먼저 확인해야 합니다.
- **minor fault와 major fault는 비용이 어떻게 다를까요?**
  - 운영에서는 이 판단을 체크리스트, 로그, 테스트로 남겨 다음 변경에서도 같은 실패가 반복되지 않게 막아야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Operating Systems 101 (1/10): 운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- [Operating Systems 101 (2/10): 프로세스와 스레드](./02-processes-and-threads.md)
- [Operating Systems 101 (3/10): 스케줄링](./03-scheduling.md)
- [Operating Systems 101 (4/10): 동시성과 경쟁 상태](./04-concurrency-and-race-conditions.md)
- [Operating Systems 101 (5/10): 락, 뮤텍스, 세마포어](./05-locks-mutex-semaphore.md)
- [Operating Systems 101 (6/10): 메모리 관리](./06-memory-management.md)
- **가상 메모리 (현재 글)**
- 파일 시스템 (예정)
- 시스템 콜 (예정)
- 컨테이너와 운영체제 (예정)

<!-- toc:end -->

## 참고 자료

- [Operating Systems 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/operating-systems-101/ko)
- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [What Every Programmer Should Know About Memory — Ulrich Drepper](https://people.freebsd.org/~lstewart/articles/cpumemory.pdf)
- [Linux mmap(2) man page](https://man7.org/linux/man-pages/man2/mmap.2.html)
- [Python mmap](https://docs.python.org/3/library/mmap.html)

Tags: Computer Science, 운영체제, 가상메모리, paging, TLB, swap
