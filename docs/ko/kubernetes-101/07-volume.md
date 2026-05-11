---
series: kubernetes-101
episode: 7
title: Volume
status: content-ready
targets:
  tistory: true
  medium: true
  hashnode: true
  mkdocs: true
  ebook: true
language: ko
tags:
  - Kubernetes
  - Volume
  - PersistentVolume
  - StorageClass
  - DevOps
seo_description: Kubernetes Volume과 PVC, StorageClass, 동적 프로비저닝의 흐름을 입문자 관점에서 정리한 글
last_reviewed: '2026-05-04'
---

# Volume

> Kubernetes 101 시리즈 (7/10)


## 이 글에서 다룰 문제

*컨테이너 파일시스템* 은 *Pod* 와 함께 *사라집니다*. *상태* 가 있는 워크로드에는 *Volume* 이 *필수*.

## 전체 흐름
```mermaid
flowchart LR
    Pod["pod"] --> PVC["pvc"]
    PVC --> SC["storageclass"]
    SC --> PV["pv (disk)"]
```

## Before/After

**Before**: *DB* 데이터를 *Pod 내부* 에 → *재시작 시 손실*.

**After**: *PVC + PV* 로 *외부 디스크* 보관.

## PVC로 Pod에 디스크 연결

### 1단계 — PVC

```python
"""
apiVersion: v1
kind: PersistentVolumeClaim
metadata: {name: data}
spec:
  accessModes: [ReadWriteOnce]
  resources: {requests: {storage: 5Gi}}
  storageClassName: gp3
"""
```

### 2단계 — Pod에서 사용

```python
"""
spec:
  containers:
  - name: app
    image: postgres:16
    volumeMounts:
    - name: data
      mountPath: /var/lib/postgresql/data
  volumes:
  - name: data
    persistentVolumeClaim: {claimName: data}
"""
```

### 3단계 — apply

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

### 4단계 — 상태 조회

```python
def get_pvc():
    res = subprocess.run(
        ["kubectl", "get", "pvc"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

### 5단계 — 정리 (주의)

```python
def delete(name):
    subprocess.run(["kubectl", "delete", "pvc", name], check=True)
```

## 이 코드에서 주목할 점

- *PVC* 가 *PV* 를 *동적* 으로 받음.
- *RWO* 는 *한 노드* 에서만 *읽기/쓰기*.
- *PVC 삭제* 가 *디스크 삭제* 일 수 있음.

## 자주 하는 실수 5가지

1. ***emptyDir* 에 *상태* 보관.**
2. ***RWX* 가 *기본 가능* 이라 단정.**
3. ***reclaimPolicy* 무지로 *데이터 유실*.**
4. ***백업 시스템* 없이 *PVC* 만 신뢰.**
5. ***스토리지 클래스* 미지정으로 *기본* 만 사용.**

## 실무에서는 이렇게 쓰입니다

*StatefulSet* 이 *Pod 별 PVC* 를 자동 생성하고, *Velero* 같은 도구가 *볼륨 스냅샷* 을 정기 *백업* 합니다.

## 체크리스트

- [ ] *상태* 는 *PVC* 또는 *managed DB*.
- [ ] *백업* 정책 존재.
- [ ] *AccessMode* 명시.
- [ ] *reclaimPolicy* 명시.

## 정리 및 다음 단계

상태가 잡혔으면 *부하 변화* 에 *Pod* 수를 *맞추는* 차례입니다. 다음 글은 *HPA*.

<!-- toc:begin -->
- [Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Pod](./02-pod.md)
- [Deployment](./03-deployment.md)
- [Service](./04-service.md)
- [Ingress](./05-ingress.md)
- [ConfigMap과 Secret](./06-configmap-and-secret.md)
- **Volume (현재 글)**
- HPA (예정)
- Helm (예정)
- 운영 관점의 Kubernetes (예정)
<!-- toc:end -->

## 참고 자료

- [Volumes](https://kubernetes.io/docs/concepts/storage/volumes/)
- [Persistent Volumes](https://kubernetes.io/docs/concepts/storage/persistent-volumes/)
- [Storage Classes](https://kubernetes.io/docs/concepts/storage/storage-classes/)
- [Velero](https://velero.io/)
