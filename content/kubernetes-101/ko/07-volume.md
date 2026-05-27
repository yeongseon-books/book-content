---
series: kubernetes-101
episode: 7
title: "Kubernetes 101 (7/10): Volume"
status: publish-ready
targets:
  tistory: true
  medium: false
  hashnode: false
  mkdocs: true
  ebook: true
language: ko
tags:
  - Kubernetes
  - Volume
  - PersistentVolume
  - StorageClass
  - DevOps
seo_description: Volume과 PVC, StorageClass가 상태 데이터를 분리하는 방식을 설명합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (7/10): Volume

컨테이너는 가볍고 교체가 쉽다는 장점이 있습니다. 하지만 그 장점은 동시에 컨테이너 파일시스템이 영구 저장소가 아니라는 뜻이기도 합니다. 파드가 다시 스케줄되거나 새 컨테이너로 교체되면, 그 안에만 저장한 데이터는 함께 사라집니다.

이 글은 Kubernetes 101 시리즈의 7번째 글입니다.

여기서는 Volume을 단순히 디스크를 붙이는 기능이 아니라, 파드의 수명과 데이터의 수명을 분리해 stateful 워크로드를 운영 가능하게 만드는 저장소 모델로 정리하겠습니다.

![Kubernetes 101 7장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/07/07-01-concept-at-a-glance.ko.png)
*Kubernetes 101 7장 흐름 개요*

> Volume의 핵심은 '디스크를 붙인다'가 아니라 '파드의 수명과 데이터의 수명을 분리한다'입니다 — 컨테이너 파일시스템은 임시 작업 공간일 뿐이고, 영구 데이터는 PV/PVC 계층을 통해 파드 교체와 무관한 수명을 가져야 stateful 워크로드가 운영 가능해집니다.

## 먼저 던지는 질문

- 파드가 재시작되면 컨테이너 파일시스템은 왜 사라질까요?
- `emptyDir`와 PVC는 어떤 순간에 갈라질까요?
- StorageClass는 단순 옵션이 아니라 무엇을 결정할까요?

## 왜 중요한가

웹 API처럼 stateless한 애플리케이션은 파드가 교체돼도 큰 문제가 없을 수 있습니다. 하지만 데이터베이스, 파일 업로드, 작업 큐처럼 상태를 직접 다루는 워크로드는 저장 위치를 잘못 잡는 순간 장애가 바로 데이터 손실로 이어집니다.

초보자가 자주 하는 실수도 여기서 나옵니다. 파드가 다시 살아났으니 데이터도 남아 있을 것이라고 기대하는 것입니다. Kubernetes는 프로세스를 다시 띄우는 일에는 강하지만, 데이터 보존은 별도의 스토리지 계층을 제대로 연결했을 때만 가능합니다.

## 한눈에 보는 구조

애플리케이션은 보통 PVC를 통해 저장소를 요청하고, StorageClass는 어떤 종류의 디스크를 어떤 방식으로 만들지 결정합니다. 이 흐름을 이해하면 애플리케이션이 원하는 것과 클러스터가 실제로 제공하는 것이 분리되어 보입니다.

## 핵심 용어

- Volume: 파드 안에서 공유하거나 지속할 수 있는 저장소입니다.
- PersistentVolume: 클러스터 관점의 실제 저장소 리소스입니다.
- PersistentVolumeClaim: 워크로드가 원하는 저장소를 요청하는 객체입니다.
- StorageClass: 디스크를 어떤 방식으로 만들지 정의합니다.
- AccessMode: 저장소에 어떤 방식으로 접근할 수 있는지 나타냅니다.

## 도입 전과 후

파드 내부 파일시스템에 데이터베이스 파일을 두면 재시작이나 재배치 때 데이터가 사라질 수 있습니다. 개발 환경에서는 운 좋게 지나가도 운영에서는 반드시 문제가 됩니다.

PVC와 PV를 사용하면 데이터는 파드 바깥 디스크에 놓이고, 파드는 그 저장소를 마운트해 씁니다. 파드가 교체돼도 같은 저장소를 다시 붙일 수 있으므로 상태를 비교적 안정적으로 유지할 수 있습니다.

## 단계별로 파드에 디스크 붙이기

### 1단계 — PVC 작성

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

이 PVC는 5Gi 저장소를 요청합니다. `storageClassName: gp3`는 어떤 종류의 디스크를 만들지 클러스터에 알려 주는 값입니다.

### 2단계 — 파드에서 사용

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

컨테이너는 이 경로를 로컬 폴더처럼 보지만, 실제로는 PVC를 통해 연결된 외부 저장소를 사용합니다. 상태를 파드 바깥으로 밀어내는 핵심 지점입니다.

### 3단계 — 적용

```python
import subprocess

def apply(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
```

PVC를 적용하면 클러스터는 StorageClass를 참고해 PV를 동적으로 만들거나 기존 PV와 바인딩합니다. 이 과정을 동적 프로비저닝이라고 부릅니다.

### 4단계 — 상태 확인

```python
def get_pvc():
    res = subprocess.run(
        ["kubectl", "get", "pvc"],
        capture_output=True, text=True, check=True,
    )
    return res.stdout
```

`Pending` 상태가 오래 이어지면 StorageClass, 용량, 권한, AccessMode를 함께 확인해야 합니다. 상태 조회는 단순 목록 확인이 아니라 스토리지 문제를 읽는 출발점입니다.

### 5단계 — 정리

```python
def delete(name):
    subprocess.run(["kubectl", "delete", "pvc", name], check=True)
```

PVC 삭제는 특히 조심해야 합니다. reclaimPolicy에 따라 실제 디스크가 함께 삭제될 수 있기 때문입니다. 상태 데이터는 생성보다 삭제가 더 위험한 경우가 많습니다.

## 검증 흐름

```bash
kubectl get pvc
kubectl describe pvc data
kubectl get pv
```

**예상되는 결과:** PVC는 `Bound` 상태가 되어야 하고, describe 결과에는 어떤 StorageClass와 PV에 연결됐는지가 보여야 합니다. PV 목록까지 같이 보면 실제 디스크가 동적으로 만들어졌는지와 reclaim 정책을 한 번에 확인할 수 있습니다.

**먼저 의심할 실패 모드:**

- PVC가 `Pending`이면 애플리케이션보다 StorageClass, 용량, AccessMode를 먼저 봅니다.
- `Bound`인데 마운트가 실패하면 PVC 자체보다 Pod spec의 volumeMount 경로를 확인합니다.
- 삭제가 무서운 이유는 reclaimPolicy가 `Delete`일 때 실제 디스크까지 사라질 수 있기 때문입니다.

## 이 코드에서 먼저 봐야 할 점

- PVC는 직접 디스크를 고르는 객체가 아니라 저장소를 요청하는 객체입니다.
- `ReadWriteOnce`는 보통 한 노드에서만 읽기와 쓰기를 허용합니다.
- PVC 삭제는 데이터 삭제로 이어질 수 있습니다.

이 셋을 이해하면 Volume을 단순 마운트 설정으로 보지 않게 됩니다. 실제로는 워크로드와 저장소 수명을 분리하는 운영 규약입니다.

## 자주 하는 실수 다섯 가지

1. 상태 데이터를 `emptyDir`에 둡니다.
2. RWX가 어디서나 기본 지원된다고 생각합니다.
3. reclaimPolicy를 보지 않고 삭제합니다.
4. PVC만 있으면 백업도 끝났다고 오해합니다.
5. StorageClass를 신경 쓰지 않고 기본값만 사용합니다.

## 실무에서는 이렇게 봅니다

실무에서는 StatefulSet이 파드마다 PVC를 자동으로 만들고, Velero 같은 도구가 스냅샷과 백업을 맡는 구조를 자주 봅니다. 이때 중요한 점은 PVC가 운영 중인 저장소이고, 백업은 복구 전략이라는 사실입니다. 둘은 서로 대체되지 않습니다.

시니어 엔지니어는 가능하면 상태 데이터 자체를 관리형 데이터베이스로 분리하는 편도 많이 선택합니다. Kubernetes가 못 해서가 아니라, 스토리지 운영 난도가 애플리케이션 운영 난도와 다른 축이기 때문입니다.

## 체크리스트

- [ ] 상태 데이터가 PVC 또는 관리형 DB에 있는가
- [ ] 백업 정책을 준비했는가
- [ ] AccessMode를 명시했는가
- [ ] reclaimPolicy를 확인했는가

## 연습 문제

1. `emptyDir`와 PVC의 차이를 한 줄로 설명해 보세요.
2. RWO의 제약을 한 가지 적어 보세요.
3. PVC만으로는 백업이 끝나지 않는 이유를 한 줄로 써 보세요.

## 마무리와 다음 글

이 글에서는 Volume을 파드의 수명과 데이터의 수명을 분리하는 기본 도구로 정리했습니다. PVC는 워크로드가 원하는 저장소를 선언하고, StorageClass와 PV는 그 요청을 실제 디스크로 연결합니다.

다음 글에서는 저장소가 아니라 트래픽 변화에 따라 파드 수를 자동으로 조절하는 방법, HPA를 보겠습니다.

## 매니페스트 중심 운영 예시

Kubernetes의 강점은 명령형 조작보다 선언형 매니페스트에 있습니다. 아래 예시는 Deployment, Service, Ingress를 분리해 책임 경계를 명확히 둔 기본 형태입니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api
  labels:
    app: api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: api
  template:
    metadata:
      labels:
        app: api
    spec:
      containers:
        - name: api
          image: ghcr.io/example/api:1.2.0
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
          resources:
            requests:
              cpu: "200m"
              memory: "256Mi"
            limits:
              cpu: "500m"
              memory: "512Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  selector:
    app: api
  ports:
    - port: 80
      targetPort: 8000
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: api
spec:
  ingressClassName: nginx
  rules:
    - host: api.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: api
                port:
                  number: 80
```

readiness probe와 resource request/limit를 함께 정의하면 "배포는 되었지만 트래픽을 받으면 무너지는" 상태를 줄일 수 있습니다. 선언형 파일에서 운영 안정성을 미리 포함시키는 방식이 중요합니다.

## kubectl 운영 명령 모음

매니페스트를 적용한 뒤에는 상태 관찰 명령을 빠르게 순환해야 합니다. 아래 조합은 장애 분석에서 가장 자주 사용하는 기본 세트입니다.

```bash
kubectl apply -f k8s/
kubectl get deploy,rs,pod -n prod -o wide
kubectl rollout status deploy/api -n prod
kubectl describe pod -n prod -l app=api
kubectl logs -n prod deploy/api --tail=200
kubectl get events -n prod --sort-by=.metadata.creationTimestamp
```

`rollout status`와 `describe`를 먼저 보면 이미지 pull 실패, probe 실패, 스케줄링 실패를 빠르게 구분할 수 있습니다. 로그만 먼저 보면 인프라 원인을 애플리케이션 오류로 오판하기 쉽습니다.

## 아키텍처 관점에서 봐야 할 경계

- **API Server 경계**: 모든 선언 변경은 API 서버를 통과합니다. 직접 노드에 접속해 상태를 손으로 맞추는 방식은 drift를 만듭니다.
- **Scheduler 경계**: Pod 배치는 자원 요청, taint/toleration, affinity 규칙의 결과입니다. 노드 선택 문제는 애플리케이션 버그와 분리해 봐야 합니다.
- **Controller 경계**: Deployment Controller는 replica 수렴과 롤링 업데이트를 담당합니다. desired/current 값 차이를 관찰하는 습관이 핵심입니다.
- **Network 경계**: Service와 Ingress는 L4/L7 책임이 다릅니다. 내부 통신 실패와 외부 진입 실패를 분리해 진단해야 대응이 빨라집니다.

이 경계를 기준으로 장애를 분해하면 "클러스터 문제"라는 모호한 결론 대신, 어느 계층에서 어떤 신호가 깨졌는지 명확히 남길 수 있습니다.

## 배포 안정성을 높이는 실무 체크

1. 모든 워크로드에 readiness/liveness probe를 설정합니다.
2. `latest` 태그 대신 고정 버전 태그를 사용해 롤백 기준을 확보합니다.
3. 변경 전 `kubectl diff -f`로 영향을 검토해 무의식적 설정 누락을 줄입니다.
4. 운영 네임스페이스에는 ResourceQuota와 LimitRange를 적용해 폭주 범위를 제한합니다.
5. 배포 후 `kubectl rollout history`를 확인해 복구 경로를 문서화합니다.

Kubernetes는 기능이 많아서 어려운 도구가 아니라, 경계를 나누어 관찰하지 않으면 쉽게 혼란스러워지는 도구입니다. 매니페스트, 관찰 명령, 아키텍처 경계를 함께 묶어 운영하면 학습 속도와 안정성이 동시에 올라갑니다.

## 운영 관찰 지표 추가

클러스터 상태를 확인할 때 단순 성공 여부만 보지 말고 재시작 횟수, 스케줄링 지연, 이미지 풀 시간 같은 신호를 함께 봐야 합니다. `kubectl get pod -A -o wide`와 `kubectl top pod -A`를 주기적으로 확인하면 자원 부족으로 인한 지연을 조기에 발견할 수 있습니다. 또한 배포 직후 `kubectl rollout status`와 `kubectl get events`를 묶어 실행하면 문제를 애플리케이션 로그로만 좁혀 보는 실수를 줄일 수 있습니다.

```bash
kubectl get pod -A -o wide
kubectl top pod -A
kubectl rollout status deploy/<name> -n <ns>
```

운영 문서에는 위 명령의 기대 출력과 비정상 패턴을 함께 기록해 두는 편이 대응 품질을 높입니다.

## Volume 선택: 수명과 공유 범위를 먼저 정하기

Volume은 "저장"보다 "수명" 관점으로 선택해야 합니다. Pod와 함께 사라지는 `emptyDir`, 노드 경로에 묶이는 `hostPath`, 클러스터 외부 스토리지를 쓰는 PVC는 운영 성격이 완전히 다릅니다.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: api-data
spec:
  accessModes: ["ReadWriteOnce"]
  resources:
    requests:
      storage: 20Gi
  storageClassName: managed-csi
```

## Pod에 마운트하고 상태 검증하기

```yaml
volumeMounts:
  - name: data
    mountPath: /var/lib/api
volumes:
  - name: data
    persistentVolumeClaim:
      claimName: api-data
```

```bash
kubectl get pvc,pv -n prod
kubectl describe pvc api-data -n prod
kubectl exec -n prod deploy/api -- df -h
```

PVC가 `Pending`이면 StorageClass, 용량, 접근 모드를 먼저 확인해야 합니다. 애플리케이션 로그만 보면 스토리지 원인을 놓치기 쉽습니다.

## 백업/복구 워크플로를 함께 설계하기

상태 저장 워크로드는 배포보다 복구 절차가 더 중요합니다. 스냅샷 주기, 복구 테스트 주기, 데이터 마이그레이션 책임자를 미리 정해 두세요. Volume 전략 없이 장애를 맞으면 복구 시간이 길어집니다.

## 운영 시뮬레이션 확장

Volume 관점의 문서를 읽고 끝내면 실제 운영에서 금방 잊힙니다. 그래서 학습 직후에 "장애를 일부러 만들어 보고 복구하는" 시뮬레이션을 반드시 권장합니다. 여기서 중요한 점은 성공 데모를 반복하는 것이 아니라, 실패 신호를 표준 절차로 읽는 훈련을 하는 것입니다. 팀이 성장할수록 기술 격차보다 절차 격차가 더 큰 장애를 만듭니다.

먼저 시뮬레이션 전 공통 기준을 맞춥니다. 대상 네임스페이스를 분리하고, 적용한 매니페스트의 Git SHA를 기록하고, 관찰 명령 5개를 고정합니다. 이 기준이 있어야 "누가, 어떤 상태에서, 무엇을 바꿨는지"를 추적할 수 있습니다.

```bash
kubectl config current-context
kubectl get ns
kubectl get deploy,po,svc,ing -n prod -o wide
kubectl get events -n prod --sort-by=.metadata.creationTimestamp
kubectl top pod -n prod
```

다음으로 장애 주입 시나리오를 단계적으로 실행합니다. 첫째, 잘못된 이미지 태그를 넣어 `ImagePullBackOff`를 발생시킵니다. 둘째, readiness probe 경로를 의도적으로 틀려 `Ready` 전환 실패를 만듭니다. 셋째, 메모리 limit를 과도하게 낮춰 OOM 재시작을 유도합니다. 넷째, selector 불일치를 만들어 트래픽 블랙홀을 재현합니다. 이 네 가지는 초급 팀이 실제 운영에서 가장 자주 만나는 장애 패턴입니다.

```bash
kubectl set image deploy/api api=ghcr.io/example/api:not-found -n prod
kubectl rollout status deploy/api -n prod
kubectl describe pod -n prod -l app=api
kubectl logs -n prod deploy/api --previous
kubectl rollout undo deploy/api -n prod
```

복구 절차는 항상 동일한 순서를 사용합니다. 1) 영향 범위 확인, 2) 즉시 완화(rollback/scale), 3) 원인 확인, 4) 재발 방지 반영입니다. 순서를 바꾸면 현장에서 토론만 길어지고 복구는 늦어집니다. 특히 온콜 시간대에는 "정확한 분석"보다 "안전한 복구"를 먼저 해야 합니다.

운영 품질을 높이려면 기술 항목을 문서 항목으로 바꿔야 합니다. 예를 들어 "probe를 잘 설정한다"가 아니라 "모든 워크로드는 readiness/liveness를 필수로 포함하고, 경로는 헬스 라우터 표준(`/readyz`, `/livez`)을 사용한다"처럼 검증 가능한 규칙으로 적어야 합니다. 또 "리소스를 적절히 준다" 대신 "CPU request는 최근 7일 P50의 1.3배, memory limit는 P99의 1.2배" 같은 팀 기준선을 고정하면 논쟁 비용이 줄어듭니다.

### 런북에 남겨야 할 최소 항목

- 장애 유형별 최초 확인 명령 3개
- 즉시 완화 명령과 금지 명령
- 롤백 기준 버전과 검증 체크리스트
- 관련 대시보드 링크와 알림 임계치
- 동일 유형 재발 시 담당 팀 에스컬레이션 경로

문서를 이 수준으로 남기면 신규 팀원이 들어와도 대응 품질이 유지됩니다. Kubernetes 운영 성숙도는 기능 사용량이 아니라 "동일 장애를 같은 속도로 복구할 수 있는가"로 측정하는 편이 정확합니다.

## 실무 검증 체크포인트

운영에서 변경을 배포할 때는 코드 리뷰와 별도로 클러스터 검증 체크를 둬야 합니다. 체크 항목은 복잡할 필요가 없습니다. 적용 전 `kubectl diff`, 적용 후 `rollout status`, 엔드포인트 연결 확인, 로그 샘플 확인, 자원 사용률 확인 정도만 일관되게 수행해도 대다수 실수를 초기에 차단할 수 있습니다.

```bash
kubectl diff -f k8s/ -n prod
kubectl apply -f k8s/ -n prod
kubectl rollout status deploy/api -n prod
kubectl get endpoints api -n prod
kubectl top pod -n prod -l app=api
```

여기서 마지막으로 중요한 원칙은 "수동 핫픽스를 원복 가능한 상태로 남긴다"는 점입니다. 긴급 대응 중에 `kubectl edit`로 해결했다면, 근무 종료 전에 반드시 매니페스트에 같은 변경을 반영해 drift를 없애야 합니다. 선언형 시스템에서 drift는 시간이 지날수록 큰 장애로 돌아옵니다.

## 관측성과 보안 기본선

Kubernetes 학습이 진행될수록 기능 사용량은 늘어나지만, 실제 장애를 줄이는 요소는 관측성과 보안 기본선입니다. 최소한 애플리케이션 로그, 인프라 이벤트, 자원 메트릭이 같은 시간축에서 비교 가능해야 하고, 서비스 계정 권한과 시크릿 접근 범위가 분리되어 있어야 합니다. 이 두 축이 약하면 배포 속도가 빨라질수록 실패 속도도 같이 빨라집니다.

관측성 기본선은 거창할 필요가 없습니다. 워크로드마다 공통 레이블(`app`, `component`, `version`)을 강제하고, 로그에 요청 식별자와 에러 코드를 남기고, 대시보드에서 레이블 필터로 바로 분해할 수 있으면 됩니다. 이벤트 스트림까지 함께 보면 "배포 변경"과 "오류 급증"의 시간적 상관관계를 빠르게 확인할 수 있습니다.

```bash
kubectl get events -n prod --sort-by=.metadata.creationTimestamp
kubectl logs -n prod deploy/api --since=10m
kubectl top pod -n prod -l app=api
kubectl top node
```

보안 기본선에서는 RBAC 최소 권한 원칙을 먼저 적용하세요. 운영 계정이 모든 네임스페이스에 쓰기 권한을 가지면 단기적으로는 편하지만, 실수 한 번이 전체 서비스로 번질 수 있습니다. 네임스페이스 단위 Role/RoleBinding을 기본으로 두고, 클러스터 전역 권한은 예외 승인 절차를 거치도록 설계하는 편이 안전합니다.

또한 NetworkPolicy를 도입하면 "통신이 되는 것이 기본"인 상태를 "허용한 통신만 된다"는 상태로 바꿀 수 있습니다. 초기에는 DNS, 내부 API, 데이터베이스 같은 필수 경로부터 열고, 나머지는 점진적으로 차단하는 방식이 현실적입니다. 정책은 기능이 아니라 운영 안전장치입니다.

마지막으로, 변경 후 검증을 자동화하세요. `kubectl apply` 이후에 상태 확인 명령을 사람이 매번 동일하게 수행하기 어렵기 때문에, CI에서 `kubectl diff`, `kubeconform`류 스키마 체크, 서버 사이드 dry-run을 묶어 두면 기본 결함을 배포 전에 차단할 수 있습니다. Kubernetes 운영 성숙도는 고급 기능보다 "기본 검증을 빠짐없이 반복하는 능력"에서 먼저 올라갑니다.

## 최종 점검 메모

배포 전 마지막 점검은 단순하지만 효과가 큽니다. 첫째, 이번 변경이 어느 리소스에 영향을 주는지 `kubectl diff`로 확인합니다. 둘째, 적용 후 `rollout status`가 끝날 때까지 기다리고, 이벤트 로그에서 경고 신호가 없는지 확인합니다. 셋째, 사용자 경로 기준 헬스 체크를 직접 호출해 응답 코드와 지연 시간을 기록합니다. 넷째, 이전 안정 버전으로 되돌릴 명령을 미리 준비해 둡니다.

```bash
kubectl diff -f k8s/ -n prod
kubectl rollout status deploy/api -n prod
kubectl get events -n prod --sort-by=.metadata.creationTimestamp
curl -fsS https://app.example.com/healthz
```

이 네 단계를 표준화하면 변경 속도가 빨라져도 운영 안정성을 유지하기 쉽습니다.

## 처음 질문으로 돌아가기

- **파드가 재시작되면 컨테이너 파일시스템은 왜 사라질까요?**
  - 컨테이너 이미지 위 writable layer는 컨테이너가 죽으면 함께 폐기되도록 설계됐기 때문에, 그 안에 쓴 파일은 재시작 시 그대로 사라집니다. 본문에서 본 것처럼 데이터를 살리려면 Pod 바깥에 존재하는 Volume에 마운트해야 하고, 이 분리가 곧 stateless·stateful 워크로드를 가르는 기준이 됩니다.
- **`emptyDir`와 PVC는 어떤 순간에 갈라질까요?**
  - `emptyDir`는 Pod와 함께 생기고 Pod가 사라지면 같이 지워지는 임시 공간이라 캐시·임시 빌드 파일에 적합합니다. 본문에서 강조한 대로 PVC는 Pod 수명과 분리된 영구 볼륨을 요청하는 방식이라, 재배포 후에도 데이터가 남아야 하는 DB·업로드 파일 같은 경우에 선택해야 합니다.
- **StorageClass는 단순 옵션이 아니라 무엇을 결정할까요?**
  - StorageClass는 provisioner·디스크 종류(SSD/HDD)·복제 정책·`reclaimPolicy` 같은 "이 PVC를 어떻게 만들고 지울지"를 묶어 둔 규칙입니다. 본문에서 보듯 `reclaimPolicy: Delete`냐 `Retain`이냐에 따라 PVC 삭제 시 실제 데이터가 함께 사라지는지가 달라지므로, 운영 데이터에는 신중히 고르고 표준화해야 합니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- [Kubernetes 101 (4/10): Service](./04-service.md)
- [Kubernetes 101 (5/10): Ingress](./05-ingress.md)
- [Kubernetes 101 (6/10): ConfigMap과 Secret](./06-configmap-and-secret.md)
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
- [Change the reclaim policy of a PersistentVolume](https://kubernetes.io/docs/tasks/administer-cluster/change-pv-reclaim-policy/)

- [Kubernetes 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

Tags: Kubernetes, Volume, PersistentVolume, StorageClass, DevOps
