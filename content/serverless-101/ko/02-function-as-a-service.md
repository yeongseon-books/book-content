---
series: serverless-101
episode: 2
title: Function as a Service
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Serverless
  - FaaS
  - Lambda
  - Runtime
  - Cloud
seo_description: FaaS의 실행 모델, 핸들러 구조, 런타임, 패키징, 배포 단위와 함께 입문자가 알아야 할 운영 포인트를 정리한 글
last_reviewed: '2026-05-04'
---

# Function as a Service

> Serverless 101 시리즈 (2/10)

<!-- a-grade-intro:begin -->

**핵심 질문**: *함수* 가 *클라우드* 위에서 *어떻게* 실행될까요?

> *FaaS* 는 *함수* 를 *컨테이너* 위에서 *짧게* 실행하고 *결과* 만 돌려주는 모델입니다.

<!-- a-grade-intro:end -->

## 이 글에서 배울 것

- *FaaS* 실행 모델
- *핸들러* 시그니처
- *런타임* 선택
- *패키징* 과 *배포 단위*
- *동시성* 과 *격리*

## 왜 중요한가

*FaaS* 의 *기본 가정* 을 모르면 *콜드 스타트, 동시성, 메모리* 모두 *직관* 이 어긋납니다.

## 개념 한눈에 보기

```mermaid
flowchart LR
    Code["function code"] --> Pkg["package zip/image"]
    Pkg --> Runtime["runtime container"]
    Runtime --> Exec["handler(event, context)"]
```

## 핵심 용어 정리

- **handler**: *진입점* 함수.
- **runtime**: *언어 환경* (Python, Node 등).
- **deployment package**: *zip* 또는 *컨테이너 이미지*.
- **concurrency**: *동시* 실행 *인스턴스 수*.
- **memory size**: *메모리* 와 *CPU* 가 *연동*.

## Before/After

**Before**: *서버* 에 *프로세스* 띄우고 *systemd* 관리.

**After**: *zip* 업로드, *플랫폼* 이 *실행*.

## 실습: 패키징과 실행

### 1단계 — 의존성 정리

```python
"""
requirements.txt:
requests==2.32.0
"""
```

### 2단계 — handler 작성

```python
import json

def handler(event, context):
    return {"statusCode": 200, "body": json.dumps({"ok": True})}
```

### 3단계 — 패키징

```python
import zipfile, pathlib

def package(src_dir, out):
    with zipfile.ZipFile(out, "w") as z:
        for p in pathlib.Path(src_dir).rglob("*"):
            z.write(p, p.relative_to(src_dir))
```

### 4단계 — 메모리 설정 효과 확인

```python
def memory_to_cpu(mb):
    return mb / 1769  # 대략 1 vCPU at ~1769MB
```

### 5단계 — 동시성 시뮬레이션

```python
import concurrent.futures as cf

def burst(handler, n):
    with cf.ThreadPoolExecutor(max_workers=n) as ex:
        return list(ex.map(lambda i: handler({"i": i}, None), range(n)))
```

## 이 코드에서 주목할 점

- *handler* 는 *순수 함수* 처럼 다루기 좋다.
- *메모리* 가 *CPU* 를 결정하는 플랫폼이 많다.
- *동시성* 은 *비용* 과 *지연* 의 균형.

## 자주 하는 실수 5가지

1. ***글로벌 상태* 에 캐싱 의존.**
2. ***대용량 의존성* 으로 *콜드 스타트* 악화.**
3. ***메모리* 를 *과소* 설정.**
4. ***동시성 제한* 을 모름.**
5. ***런타임 EOL* 을 *방치*.**

## 실무에서는 이렇게 쓰입니다

*HTTP API, S3 트리거, 큐 소비자* 같은 *짧은 단위 작업* 에 폭넓게 사용됩니다.

## 시니어 엔지니어는 이렇게 생각합니다

- *handler* 는 *작게* 유지.
- *메모리* 튜닝이 *비용 절감* 의 핵심.
- *컨테이너 이미지* 옵션도 고려.
- *런타임 업데이트* 는 *주기적*.
- *동시성* 은 *예산* 으로 본다.

## 체크리스트

- [ ] *의존성* 최소화.
- [ ] *메모리/CPU* 튜닝.
- [ ] *런타임* 최신.
- [ ] *동시성 한도* 인지.

## 연습 문제

1. *handler* 의 *시그니처* 한 줄로.
2. *메모리* 와 *CPU* 의 관계 한 줄로.
3. *동시성* 과 *비용* 의 관계 한 줄로.

## 정리 및 다음 단계

다음 글은 *Trigger* 와 *Event* 를 살펴봅니다.

<!-- toc:begin -->
- [Serverless란 무엇인가?](./01-what-is-serverless.md)
- **Function as a Service (현재 글)**
- Trigger와 Event (예정)
- Cold Start (예정)
- Scaling (예정)
- State 관리 (예정)
- Queue와 Event-driven Architecture (예정)
- Observability (예정)
- Cost (예정)
- Serverless 앱 설계 (예정)
<!-- toc:end -->

## 참고 자료

- [AWS Lambda 핸들러](https://docs.aws.amazon.com/lambda/latest/dg/python-handler.html)
- [Lambda 컨테이너 이미지](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Cloud Functions 런타임](https://cloud.google.com/functions/docs/runtime-support)
- [Azure Functions 호스팅](https://learn.microsoft.com/azure/azure-functions/functions-scale)

Tags: Serverless, FaaS, Lambda, Runtime, Cloud
