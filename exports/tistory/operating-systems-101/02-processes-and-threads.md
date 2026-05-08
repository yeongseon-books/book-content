
# 프로세스와 스레드

> Operating Systems 101 시리즈 (2/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: "실행 중인 프로그램"이라는 말은 너무 모호합니다. OS 입장에서 그것은 정확히 무엇으로 이루어져 있을까요?

> 프로세스는 OS가 응용 프로그램을 다루는 가장 기본 단위입니다. 메모리, 열린 파일, 권한, CPU 상태가 한 묶음으로 묶여 있고, 각 프로세스는 다른 프로세스로부터 격리되어 있습니다. 스레드는 그 한 프로세스 안에서 메모리를 공유하며 동시에 실행되는 흐름입니다. 이 글에서는 프로세스의 내부 구조, 스레드와의 차이, 그리고 둘 중 무엇을 언제 써야 하는지를 정리합니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- 프로세스가 가진 자원의 목록(메모리, fd, 권한, CPU 상태)
- 스레드가 프로세스와 무엇을 공유하고 무엇을 따로 가지는가
- 프로세스 생성 모델 — `fork`와 `exec`, 그리고 윈도우의 `CreateProcess`
- 멀티프로세스 vs 멀티스레드의 트레이드오프

## 왜 중요한가

프로세스와 스레드는 동시성을 구현하는 두 가지 기본 빌딩 블록입니다. 둘을 혼동하면 메모리 격리가 깨지거나, 스레드 안전성을 잘못 가정하거나, 자식 프로세스를 좀비로 남기는 식의 문제가 생깁니다. "왜 같은 데이터인데 한쪽에서는 보이고 다른 쪽에서는 안 보이지?"라는 질문 대부분은 프로세스/스레드 모델로 풀립니다.

> 프로세스는 격리의 단위, 스레드는 동시성의 단위입니다. 둘을 같은 도구로 쓰면 거의 항상 한쪽이 새거나 한쪽이 막힙니다.

## 개념 한눈에 보기

> 한 프로세스는 자기만의 가상 주소 공간, 파일 디스크립터 테이블, 신호 처리기, 권한을 가집니다. 그 안에 한 개 이상의 스레드가 있고, 스레드는 메모리와 fd는 공유하지만 자신만의 스택과 레지스터 상태를 갖습니다.

```text
+-----------------------------------------+
|  Process                                |
|  +----------+ +-----------+ +--------+  |
|  | Code     | | Heap      | | Globals|  |
|  +----------+ +-----------+ +--------+  |
|  +-------- File descriptor table -----+ |
|  |  0:stdin  1:stdout  2:stderr  ...  | |
|  +-----------------------------------+  |
|                                         |
|  +-- Thread A --+   +-- Thread B --+    |
|  |  Stack       |   |  Stack       |    |
|  |  Registers   |   |  Registers   |    |
|  +--------------+   +--------------+    |
+-----------------------------------------+
```

## 핵심 용어 정리

| 용어 | 설명 |
| --- | --- |
| 주소 공간 | 프로세스가 보는 가상 메모리 영역(코드, 데이터, 힙, 스택) |
| 파일 디스크립터 테이블 | 프로세스가 열어 둔 파일/소켓의 정수 인덱스 표 |
| `fork` | 호출 프로세스를 거의 그대로 복제하여 자식을 만드는 시스템 콜 |
| `exec` | 현재 프로세스의 메모리 이미지를 새 프로그램으로 교체 |
| GIL | CPython의 전역 인터프리터 락, 같은 시점에 한 스레드만 파이썬 바이트코드 실행 |

## Before / After

**Before — "스레드와 프로세스는 그냥 다 동시 실행":**

```python
# 두 작업을 "동시에" 돌리고 싶다
import threading, multiprocessing
```

이 한 줄은 둘 중 어느 것을 골라야 하는지 알려 주지 않습니다.

**After — "공유 모델이 다르다"는 모델:**

```text
multiprocessing.Process : 메모리 따로, 통신은 큐/파이프/공유 메모리
threading.Thread        : 메모리 같이, 락이 필요하고 GIL이 있음

CPU 바운드(numpy로 큰 행렬 곱) → 멀티프로세스가 보통 빠름
I/O 바운드(HTTP 요청 100건)    → 멀티스레드 또는 asyncio가 보통 충분
```

같은 "동시 실행"이라도 무엇을 공유하느냐로 도구가 갈립니다.

## 실습: 단계별로 따라하기

### 1단계: PID와 부모-자식 관계 보기

```python
import os

print(f"부모 PID(이 프로세스): {os.getpid()}")

pid = os.fork()
if pid == 0:
    print(f"자식  PID: {os.getpid()}, 부모: {os.getppid()}")
else:
    os.waitpid(pid, 0)
    print(f"부모: 자식 {pid} 종료 확인")
```

`fork`는 한 번 호출되어 두 번 리턴합니다. 부모에는 자식 PID가, 자식에는 0이 돌아옵니다. 같은 코드인데 두 줄기로 갈라지는 경험이 핵심입니다.

### 2단계: `fork` 이후의 메모리 격리 확인

```python
import os

x = [1, 2, 3]
if os.fork() == 0:
    x.append(99)
    print(f"자식의 x: {x}")
    os._exit(0)
os.wait()
print(f"부모의 x: {x}")
```

자식이 `x`를 바꿔도 부모의 `x`는 그대로입니다. 두 프로세스는 같은 메모리를 보지 못합니다(겉보기는 같지만 내부적으로는 copy-on-write).

### 3단계: 스레드는 메모리를 공유한다

```python
import threading

x = [1, 2, 3]
def worker():
    x.append(99)

t = threading.Thread(target=worker)
t.start(); t.join()
print(f"메인의 x: {x}")
```

같은 `x` 리스트가 보입니다. 스레드는 같은 주소 공간을 공유하기 때문에 동기화가 필요해집니다.

### 4단계: 스레드 vs 프로세스 성능 직관

```python
import time, math
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def cpu_heavy(n):
    return sum(math.sqrt(i) for i in range(n))

N = 5_000_000
tasks = [N] * 4

for Pool, label in [(ThreadPoolExecutor, "Thread"), (ProcessPoolExecutor, "Process")]:
    start = time.perf_counter()
    with Pool(max_workers=4) as ex:
        list(ex.map(cpu_heavy, tasks))
    print(f"{label}: {time.perf_counter() - start:.2f} s")
```

CPU 바운드 작업에서는 보통 프로세스 풀이 빠릅니다. CPython의 GIL 때문에 스레드는 같은 시점에 하나만 파이썬 코드를 실행할 수 있습니다.

### 5단계: `exec`로 다른 프로그램 되기

```python
import os

if os.fork() == 0:
    os.execvp("ls", ["ls", "-la"])  # 자식이 ls로 변신
    # 여기는 도달하지 않음
os.wait()
```

`fork`로 자식을 만들고 곧바로 `exec`로 다른 프로그램이 되는 패턴이 셸이 명령을 실행하는 표준 방식입니다. 자식 프로세스의 메모리는 새 프로그램의 이미지로 통째로 교체됩니다.

## 이 코드에서 주목할 점

- `fork`는 한 번 호출되고 두 번 리턴합니다
- 프로세스 간 메모리는 격리되어 있고, 스레드 간 메모리는 공유됩니다
- CPython의 GIL 때문에 CPU 바운드 + 스레드 조합은 종종 기대만큼 빠르지 않습니다
- `fork`+`exec`는 셸과 컨테이너 런타임의 기본 패턴입니다

## 자주 하는 실수 5가지

| 실수 | 문제 | 해결 |
| --- | --- | --- |
| 모든 동시성에 스레드 사용 | CPU 바운드는 GIL로 막힘 | CPU 바운드는 프로세스, I/O 바운드는 스레드/asyncio |
| 자식 프로세스 회수 안 함 | 좀비 프로세스 누적 | `os.wait`/`waitpid`로 회수 |
| 스레드 간 공유 데이터 락 미사용 | race condition, 알 수 없는 버그 | `threading.Lock` 또는 큐 사용 |
| `fork` 직후 큰 라이브러리 임포트 가정 | macOS에서 동작 차이, 안전성 문제 | `multiprocessing.set_start_method('spawn')` 고려 |
| 프로세스를 가볍다고 가정 | 수천 개 프로세스 생성으로 OS 자원 고갈 | 워커 풀 패턴으로 재사용 |

## 실무에서는 이렇게 쓰입니다

- 웹 서버: gunicorn은 워커 프로세스, uvicorn은 비동기, 둘을 조합
- 데이터 처리: `multiprocessing.Pool`로 CPU 바운드 ETL 분산
- 컨테이너: 컨테이너 런타임이 `clone`+`exec` 변형으로 격리된 자식 실행
- 백엔드 디버깅: `ps -ef`, `pstree`, `htop`로 프로세스/스레드 트리 확인
- 데이터 과학: `joblib`이 백엔드(스레드/프로세스)를 골라서 병렬화

## 시니어 엔지니어는 이렇게 생각합니다

시니어 엔지니어는 "동시에 돌리자"는 요청을 받으면 먼저 작업의 성격을 묻습니다. CPU를 태우는가, 외부를 기다리는가, 메모리를 얼마나 공유해야 하는가, 실패가 한쪽에 가두어져야 하는가. 이 답에 따라 프로세스, 스레드, 비동기 중 무엇을 쓸지가 거의 자동으로 정해집니다.

또한 시니어는 "프로세스는 비싸고 스레드는 싸다"는 단순한 비교를 경계합니다. 프로세스는 격리와 안정성이라는 큰 가치를 같이 줍니다. 한 워커가 망가져도 다른 워커가 살아남는 시스템은 운영 측면에서 종종 더 가치 있습니다.

## 체크리스트

- [ ] 프로세스가 가진 자원 네 가지를 말할 수 있는가
- [ ] 스레드와 프로세스가 공유하는 것과 안 하는 것을 안다
- [ ] CPU 바운드와 I/O 바운드의 적절한 도구를 안다
- [ ] `fork`와 `exec`의 역할 분리를 설명할 수 있는가
- [ ] 자식 프로세스 회수의 필요성을 안다

## 연습 문제

1. 자신의 프로젝트에서 가장 무거운 함수 하나를 골라 (a) 단일 스레드, (b) 4-스레드 풀, (c) 4-프로세스 풀로 각각 실행해 시간을 비교해 보세요. 어느 쪽이 빠른지와 그 이유를 한 문단으로 정리합니다.

2. `os.fork`로 자식을 만들고 회수하지 않는 작은 스크립트를 작성한 뒤 `ps -ef`로 좀비(`Z` 상태) 프로세스를 관찰해 보세요. 그 다음 `os.wait`를 추가해 좀비가 사라지는지 확인합니다.

3. `threading`으로 두 스레드가 같은 정수를 1억 번 증가시키는 코드를 작성하고, 락 없이/락 사용 두 가지 결과를 비교하세요. 왜 결과가 다른지 한 문단으로 설명합니다.

## 정리 및 다음 단계

프로세스는 격리된 자원 묶음이고, 스레드는 그 안에서 흐르는 동시 실행 단위입니다. 둘을 헷갈리면 동시성 코드가 미묘하게 깨지거나 성능이 기대만큼 나오지 않습니다. CPU 바운드와 I/O 바운드, 격리의 필요성, 메모리 공유 정도라는 세 가지 축으로 도구를 고를 수 있습니다.

다음 글에서는 OS가 그 많은 프로세스와 스레드 중 누구에게 CPU를 줄지를 결정하는 메커니즘 — 스케줄링을 봅니다.

- [운영체제란 무엇인가?](./01-what-is-an-operating-system.md)
- **프로세스와 스레드 (현재 글)**
- 스케줄링 (예정)
- 동시성과 race condition (예정)
- lock, mutex, semaphore (예정)
- 메모리 관리 (예정)
- 가상 메모리 (예정)
- 파일 시스템 (예정)
- 시스템 콜 (예정)
- 컨테이너와 운영체제 (예정)
## 참고 자료

- [Tanenbaum & Bos — Modern Operating Systems](https://www.pearson.com/store/p/modern-operating-systems/P100000869539)
- [The Linux Programming Interface — Michael Kerrisk](https://man7.org/tlpi/)
- [Python multiprocessing 문서](https://docs.python.org/3/library/multiprocessing.html)
- [Python threading 문서](https://docs.python.org/3/library/threading.html)

Tags: Computer Science, 운영체제, 프로세스, 스레드, 동시성, 시스템

---

© 2026 영선북스. 이 글의 저작권은 저자에게 있습니다.
