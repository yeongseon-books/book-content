---
series: kubernetes-101
episode: 4
title: "Kubernetes 101 (4/10): Service"
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
  - Service
  - Networking
  - DNS
  - DevOps
seo_description: Service가 Pod 집합에 안정적인 주소와 이름을 주는 방식을 설명합니다.
last_reviewed: '2026-05-15'
---

# Kubernetes 101 (4/10): Service

Pod를 여러 개 띄우기 시작하면 다음 문제가 바로 등장합니다. Pod IP가 계속 바뀌는데, 다른 서비스나 사용자는 그 파드를 어떻게 안정적으로 찾아야 할까 하는 문제입니다. 파드가 재시작되거나 새로 생성될 때마다 주소가 달라지면 애플리케이션끼리 서로를 부르기가 금방 불안정해집니다.

이 글은 Kubernetes 101 시리즈의 4번째 글입니다.

여기서는 Service를 단순한 포트 노출 기능이 아니라, 라벨로 선택된 파드 집합에 안정적인 가상 IP와 DNS 이름을 부여하는 네트워킹 기본 객체라는 관점에서 정리하겠습니다.


![Kubernetes 101 4장 흐름 개요](https://yeongseon-books.github.io/book-public-assets/assets/kubernetes-101/04/04-01-concept-at-a-glance.ko.png)
*Kubernetes 101 4장 흐름 개요*

## 먼저 던지는 질문

- Service는 정확히 어떤 문제를 해결할까요?
- ClusterIP, NodePort, LoadBalancer는 언제 갈라질까요?
- selector와 labels는 왜 정확히 맞아야 할까요?

## 왜 중요한가

마이크로서비스 구조에서는 애플리케이션이 다른 애플리케이션을 이름으로 호출해야 합니다. 그런데 Pod IP를 직접 쓰는 방식은 재시작 한 번으로 바로 깨집니다. Kubernetes에서 내부 통신이 안정적으로 보이려면 중간에서 변하는 파드 집합을 고정된 이름으로 가려 주는 계층이 필요합니다.

그 역할을 Service가 맡습니다. 많은 입문자가 Service를 단순히 외부 노출용으로만 이해하지만, 실제로는 내부 통신에서 더 자주 중요합니다. Service를 이해하지 못하면 Ingress도, 서비스 디스커버리도, DNS 기반 호출도 모두 흐릿하게 남습니다.

## 한눈에 보는 구조

Service는 특정 파드를 직접 고정해 가리키지 않습니다. 라벨로 선택된 파드 집합을 뒤에 두고, 앞단에는 안정적인 가상 IP와 이름을 제공합니다. 클라이언트는 뒤에서 어떤 파드가 바뀌는지 신경 쓰지 않고 Service 이름만 알면 됩니다.

## 핵심 용어

- ClusterIP: 클러스터 내부에서만 쓰는 기본 가상 IP입니다.
- NodePort: 모든 노드의 특정 포트를 통해 접근하게 하는 방식입니다.
- LoadBalancer: 클라우드 로드 밸런서를 연결해 외부 진입점을 여는 방식입니다.
- selector: 라벨로 파드 집합을 고르는 조건입니다.
- DNS 이름: `svc.namespace.svc.cluster.local` 형태의 서비스 이름입니다.

## 도입 전과 후

Service가 없으면 클라이언트가 Pod IP를 직접 호출해야 합니다. 이 방식은 파드 재시작이나 재배치가 일어나는 순간 바로 깨집니다.

Service를 두면 클라이언트는 DNS 이름으로 Service를 호출하고, Service가 뒤의 파드 집합으로 트래픽을 보냅니다. 파드가 바뀌어도 호출 방식은 바뀌지 않습니다. 이것이 내부 통신 안정성의 출발점입니다.

## 단계별로 Service 노출해 보기

### 1단계 — Service 매니페스트 작성

```python
"""
apiVersion: v1
kind: Service
metadata: {name: web}
spec:
  selector: {app: web}
  ports:
  - port: 80
    targetPort: 80
"""
```

이 설정은 `app: web` 라벨을 가진 파드 집합을 `web`이라는 이름의 Service 뒤에 묶습니다. 여기서 가장 중요한 값은 `selector`입니다.

### 2단계 — 적용 후 조회

```python
import subprocess

def apply_and_get(path):
    subprocess.run(["kubectl", "apply", "-f", path], check=True)
    return subprocess.run(
        ["kubectl", "get", "svc", "web"],
        capture_output=True, text=True, check=True,
    ).stdout
```

적용 후 바로 상태를 보는 습관이 중요합니다. Service 자체는 생성됐더라도 뒤에 연결된 파드가 없으면 실제 라우팅은 되지 않기 때문입니다.

### 3단계 — DNS 확인

```python
def dns_check(target):
    res = subprocess.run([
        "kubectl", "run", "tmp", "--rm", "-i", "--restart=Never",
        "--image=busybox", "--", "nslookup", target,
    ], capture_output=True, text=True, check=True)
    return res.stdout
```

Service를 이해할 때는 DNS 관점이 중요합니다. 내부 서비스 간 통신을 IP가 아니라 이름으로 바꾸는 핵심 고리가 바로 여기입니다.

### 4단계 — NodePort로 변경

```python
def to_nodeport(svc):
    subprocess.run([
        "kubectl", "patch", "svc", svc, "-p",
        '{"spec": {"type": "NodePort"}}',
    ], check=True)
```

Service 타입을 바꾸면 접근 경로가 달라집니다. 다만 NodePort는 외부 접근 실험에는 편해도, 보통 운영의 최종 외부 진입점으로 삼는 경우는 드뭅니다.

### 5단계 — 정리

```python
def delete(svc):
    subprocess.run(["kubectl", "delete", "svc", svc], check=True)
```

리소스를 지울 때는 Service 삭제 자체보다, 이 Service를 바라보는 다른 애플리케이션이 있는지 먼저 보는 편이 중요합니다. 이름 기반 호출 구조에서는 이름 하나가 계약이 되기 때문입니다.

## 검증 흐름

```bash
kubectl get svc web
kubectl get endpoints web
kubectl run dnscheck --rm -i --restart=Never --image=busybox -- nslookup web.default.svc.cluster.local
```

**예상되는 결과:** Service에는 ClusterIP가 할당돼야 하고, Endpoints에는 실제 Pod IP가 하나 이상 연결돼 있어야 합니다. DNS 조회는 서비스 이름이 클러스터 내부에서 해석된다는 사실을 확인하는 가장 빠른 점검입니다.

**먼저 의심할 실패 모드:**

- Service는 있는데 Endpoints가 비어 있으면 selector와 labels 불일치를 먼저 봅니다.
- DNS는 되는데 응답이 실패하면 `targetPort`와 컨테이너 listen port가 다른지 확인합니다.
- 다른 네임스페이스에서 실패하면 Service 자체보다 호출 이름에 네임스페이스를 빠뜨린 경우가 흔합니다.

## 이 코드에서 먼저 봐야 할 점

- `selector`는 Deployment가 붙인 라벨과 정확히 맞아야 합니다.
- `targetPort`는 컨테이너가 실제로 듣는 포트입니다.
- DNS 이름이 서비스 호출의 표준 경로가 됩니다.

이 셋이 연결되면 Service를 단순 프록시가 아니라 네트워크 계약으로 볼 수 있습니다. 호출하는 쪽은 이름만 알고, 실제 파드 교체는 뒤에서 계속 일어나도 괜찮아집니다.

## 자주 하는 실수 다섯 가지

1. selector와 labels가 어긋나는데도 Service가 동작할 것이라 기대합니다.
2. NodePort를 운영 환경의 최종 외부 진입점으로 씁니다.
3. Pod IP를 직접 호출합니다.
4. 일반적인 경우에도 Headless Service부터 꺼내 듭니다.
5. DNS 이름에서 네임스페이스 개념을 무시합니다.

## 실무에서는 이렇게 봅니다

실무에서는 ClusterIP가 내부 통신의 기본값이고, 외부 진입은 LoadBalancer와 Ingress가 나눠 맡는 구성이 흔합니다. Service는 그 사이에서 안정적인 서비스 이름과 백엔드 파드 집합을 연결하는 핵심 고리입니다.

시니어 엔지니어는 Service 이름을 사실상 API 계약처럼 봅니다. 파드가 어떻게 바뀌든, 내부 호출자가 기대하는 이름과 포트는 오래 유지되기 때문입니다. 그래서 라벨 설계와 네이밍이 운영 품질에 직접 영향을 줍니다.

## 체크리스트

- [ ] selector가 실제 파드 라벨과 맞는가
- [ ] Service 타입을 명시했는가
- [ ] 내부 호출이 DNS 이름 기준으로 이뤄지는가
- [ ] 외부 노출은 Ingress 중심으로 검토했는가

## 연습 문제

1. ClusterIP와 LoadBalancer의 차이를 한 줄로 설명해 보세요.
2. selector가 왜 중요한지 한 줄로 적어 보세요.
3. Headless Service의 대표적인 사용 예를 하나 떠올려 보세요.

## 마무리와 다음 글

이 글에서는 Service를 변하는 파드 집합 앞에 안정적인 주소와 이름을 붙여 주는 객체로 정리했습니다. Kubernetes 네트워킹이 복잡해 보일 때도, 먼저 Service가 어떤 파드 집합을 어떤 이름으로 대표하는지부터 보면 흐름이 빠르게 정리됩니다.

다음 글에서는 내부 통신을 넘어서, 외부에서 들어오는 HTTP 요청을 도메인과 경로 기준으로 어떻게 나누는지 Ingress를 보겠습니다.


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

## Service 타입 선택 기준을 명확히 하기

Service를 만들 때 가장 먼저 정할 것은 "이 트래픽이 어디서 들어오는가"입니다. 내부 통신이면 ClusterIP, 노드 경유 테스트면 NodePort, 클라우드 LB 연동이면 LoadBalancer가 기본입니다. 타입을 잘못 고르면 네트워크 디버깅 시간이 크게 늘어납니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: api
spec:
  type: ClusterIP
  selector:
    app: api
  ports:
    - name: http
      port: 80
      targetPort: 8000
```

## Endpoints/EndpointSlice로 실제 연결 상태 확인

Service 정의가 맞아도 selector 불일치로 트래픽이 비는 경우가 많습니다. 이때는 Pod 로그보다 Endpoints를 먼저 보는 편이 빠릅니다.

```bash
kubectl get svc api -n prod -o yaml
kubectl get endpoints api -n prod -o yaml
kubectl get endpointslices -n prod -l kubernetes.io/service-name=api
kubectl get pod -n prod -l app=api --show-labels
```

Endpoints가 비어 있으면 selector와 label을 우선 확인하세요. readiness가 실패한 Pod는 엔드포인트에서 제외되므로, probe 상태도 함께 점검해야 합니다.

## 세션, 타임아웃, 장애 분리

상태 저장 세션을 Service 뒤에 그대로 두면 스케일 아웃 시 불안정해질 수 있습니다. 가능하면 세션은 Redis 같은 외부 저장소로 분리하고, Service는 stateless 트래픽 분산에 집중시키는 구성이 좋습니다. 또한 클라이언트 타임아웃과 서버 타임아웃을 문서로 맞춰 두면 간헐적 504 분석이 쉬워집니다.

## 운영 시뮬레이션 확장

Service 관점의 문서를 읽고 끝내면 실제 운영에서 금방 잊힙니다. 그래서 학습 직후에 "장애를 일부러 만들어 보고 복구하는" 시뮬레이션을 반드시 권장합니다. 여기서 중요한 점은 성공 데모를 반복하는 것이 아니라, 실패 신호를 표준 절차로 읽는 훈련을 하는 것입니다. 팀이 성장할수록 기술 격차보다 절차 격차가 더 큰 장애를 만듭니다.

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

## 운영 한 줄 원칙

운영에서 가장 중요한 원칙은 "원인 추정 전에 상태 증거를 먼저 수집한다"입니다. `describe`, `events`, `rollout` 세 신호를 먼저 확보하면 잘못된 가정으로 시간을 쓰는 일을 줄일 수 있습니다.

## 처음 질문으로 돌아가기

- **Service는 정확히 어떤 문제를 해결할까요?**
  - Pod IP는 재시작·재스케줄에 따라 계속 바뀌기 때문에, 클라이언트가 IP를 직접 잡으면 통신이 자주 끊깁니다. Service는 selector로 묶인 Pod 집합 앞에 안정적인 가상 IP와 이름을 두어, 호출하는 쪽이 "현재 어떤 Pod인지"를 신경 쓰지 않아도 되게 만듭니다.
- **ClusterIP, NodePort, LoadBalancer는 언제 갈라질까요?**
  - 본문 예시처럼 ClusterIP는 클러스터 내부에서만 닿을 때, NodePort는 노드의 특정 포트로 외부 접근을 열어 둘 때, LoadBalancer는 클라우드 LB와 연동해 공개 트래픽을 받을 때 선택합니다. 즉 "어디서 들어오는 트래픽인지"가 type을 가르는 기준입니다.
- **selector와 labels는 왜 정확히 맞아야 할까요?**
  - Service는 selector로 Pod를 찾고 그 결과를 Endpoints로 묶어 라우팅합니다. selector와 Pod의 label이 한 글자라도 어긋나면 Endpoints가 비어 트래픽이 어디로도 가지 못하는 블랙홀 상태가 되기 때문에, `kubectl get endpoints`로 확인하는 습관이 운영 기본이 됩니다.

<!-- toc:begin -->
## 시리즈 목차

- [Kubernetes 101 (1/10): Kubernetes란 무엇인가?](./01-what-is-kubernetes.md)
- [Kubernetes 101 (2/10): Pod](./02-pod.md)
- [Kubernetes 101 (3/10): Deployment](./03-deployment.md)
- **Service (현재 글)**
- Ingress (예정)
- ConfigMap과 Secret (예정)
- Volume (예정)
- HPA (예정)
- Helm (예정)
- 운영 관점의 Kubernetes (예정)

<!-- toc:end -->

## 참고 자료

- [Service (Kubernetes)](https://kubernetes.io/docs/concepts/services-networking/service/)
- [DNS for Services and Pods](https://kubernetes.io/docs/concepts/services-networking/dns-pod-service/)
- [Service types](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types)
- [Headless Services](https://kubernetes.io/docs/concepts/services-networking/service/#headless-services)
- [Debug Services](https://kubernetes.io/docs/tasks/debug/debug-application/debug-service/)

- [Kubernetes 101 예제 코드 (book-examples)](https://github.com/yeongseon-books/book-examples/tree/main/kubernetes-101/ko)

Tags: Kubernetes, Service, Networking, DNS, DevOps
