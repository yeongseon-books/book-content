# 학술적 관점 — Azure Functions를 분석한 논문들

> Azure Functions Deep Dive 시리즈 (7/7) · 마지막 화

지금까지 6화 동안 호스트의 코드를 직접 따라가며 부팅, 워커 프로세스, gRPC, Dispatcher, 스케일링, Placeholder까지 봤습니다. 마지막 화에서는 한 단계 물러서서, **Azure Functions를 학술적으로 분석한 논문들**을 봅니다.

이 글의 목표는 두 가지입니다.

1. Microsoft 연구진이 직접 발표한 **Azure Functions 운영 데이터 기반 논문**을 통해, 코드만으로는 알 수 없는 "실제 워크로드가 어떻게 생겼는가"를 보는 것
2. 우리가 6화에서 본 Placeholder, Always Ready, target-based scaling 같은 메커니즘이 **어떤 학술적 관찰에서 나왔는지** 연결하는 것

코드는 "어떻게 동작하는가"를 알려주고, 논문은 "왜 그렇게 만들었는가"를 알려줍니다. 둘이 만나면 시스템에 대한 이해가 입체적으로 됩니다.

---

## 핵심 논문 — Shahrad et al., USENIX ATC 2020

### "Serverless in the Wild: Characterizing and Optimizing the Serverless Workload at a Large Cloud Provider"

이 시리즈에서 가장 자주 인용한 논문이고, 이 글의 중심입니다.

- **저자**: Mohammad Shahrad, Rodrigo Fonseca, Íñigo Goiri, Gohar Chaudhry, Paul Batum, Jason Cooke, Eduardo Laureano, Colby Tresness, Mark Russinovich, Ricardo Bianchini
- **소속**: Microsoft Azure + Microsoft Research
- **발표**: USENIX ATC 2020, **Community Award Winner**
- **링크**: [USENIX 페이지](https://www.usenix.org/conference/atc20/presentation/shahrad) · [arXiv:2003.03423](https://arxiv.org/abs/2003.03423)

저자 명단을 자세히 보세요. **Mark Russinovich (Azure CTO)**가 공저자입니다. 그리고 Paul Batum, Eduardo Laureano, Colby Tresness는 Azure Functions 팀의 엔지니어입니다. 즉 이 논문은 **외부 연구자가 추정해서 쓴 게 아니라, 실제 Azure Functions를 만드는 사람들이 자기 시스템의 운영 데이터를 분석해서 쓴 논문**입니다. 신뢰도가 다릅니다.

### 논문이 답한 질문

> "FaaS 워크로드는 실제로 어떻게 생겼는가? 그리고 그 특성을 알면 콜드 스타트를 어떻게 줄일 수 있는가?"

기존 학계의 한계는 명확했습니다. AWS Lambda, Azure Functions, GCF 같은 상용 FaaS 플랫폼의 **실제 운영 데이터는 공개된 적이 없었습니다.** 연구자들은 자체 부하 생성기로 합성 트래픽을 만들거나, 작은 사례 연구에 의존했습니다. 이 논문은 그 공백을 메웠습니다.

### 핵심 발견 (논문이 직접 보고한 것)

논문의 abstract에서 직접 인용합니다.

> "We show for example that **most functions are invoked very infrequently**, but there is an **8-order-of-magnitude range of invocation frequencies**."
> — Shahrad et al., 2020

두 문장에 핵심이 다 들어 있습니다.

**1. 대부분의 함수는 거의 호출되지 않는다.**

대부분의 함수가 매우 드물게 호출된다면, "호출이 끝나면 인스턴스를 즉시 죽이는" 단순 정책은 콜드 스타트를 양산합니다. 다음 호출이 언제 올지 모르고, 그 시간 간격이 평균 매우 길기 때문입니다.

**2. 호출 빈도의 동적 범위가 8자리수에 걸쳐 있다.**

분당 수백만 회 호출되는 함수도, 하루에 한 번 호출될까 말까 한 함수도 같은 플랫폼 위에 공존합니다. 한 종류의 정책으로 둘 다 잘 다루는 건 거의 불가능합니다. **함수마다 다른 정책이 필요합니다.**

이 두 발견이 논문의 핵심 제안으로 이어집니다.

### 논문의 제안 (요약)

> "We then propose a practical resource management policy that **significantly reduces the number of function cold starts, while spending fewer resources** than state-of-the-practice policies."
> — Shahrad et al., 2020

논문은 단순한 "고정 idle timeout" 대신 **함수별 호출 패턴을 학습해서, 다음 호출이 언제 올지 예측하고, 그에 맞춰 인스턴스를 살려두는 정책**을 제안합니다. 자주 호출되는 함수는 더 길게, 드물게 호출되는 함수는 더 짧게 살려둡니다. 정확한 알고리즘은 논문에 보고되어 있고, 결과는 **콜드 스타트 수가 줄면서 동시에 살려둔 인스턴스 자원도 줄었다**는 것입니다.

> 정확한 알고리즘 이름과 수치는 논문에 보고된 대로이며, 이 글에서는 "공개적으로 보고된 결과 톤"으로만 인용합니다. 정확한 절감률을 인용하려면 [원 논문](https://www.usenix.org/conference/atc20/presentation/shahrad)을 참조하세요.

### 데이터셋 공개

논문이 학계에 미친 또 다른 큰 기여는 **익명화된 트레이스 데이터셋을 공개**한 것입니다.

- **Azure Functions Trace 2019** (이 논문에 사용된 데이터)

이 데이터셋은 후속 학술 논문 수십 편에서 베이스라인으로 사용됐습니다. "내가 만든 새 정책을 실제 FaaS 워크로드에서 평가하고 싶다"는 모든 후속 연구의 표준 입력이 됐습니다.

> 데이터셋 링크는 논문의 "Code, Data, Media" 섹션 또는 [Microsoft AzurePublicDataset 저장소](https://github.com/Azure/AzurePublicDataset)에서 확인할 수 있습니다.

### 호스트 코드와의 연결 — 6화에서 본 것

6화에서 우리는 Placeholder와 Always Ready를 봤습니다. 이 논문의 메시지를 코드 레벨에서 보면 이렇게 매핑됩니다.

| 논문의 관찰 | 호스트가 채택한 메커니즘 |
|---|---|
| 대부분의 함수는 드물게 호출됨 | **Placeholder 풀** — 어떤 함수가 와도 빠르게 specialize |
| 호출 빈도가 8자리수 범위 | **함수별/플랜별 차등 정책** — Consumption은 종량, Premium은 Always Ready, Flex는 per-function scaling |
| 다음 호출 예측이 가치 있음 | **Always Ready 인스턴스 수를 사용자가 지정** — 사용자가 자기 함수의 패턴을 알고 있다는 가정 |
| 실시간 학습보다 사전 정책 | Flex Consumption의 **target-based scaling** — 큐 길이라는 직접 신호로 결정 |

논문의 주장을 그대로 production에 옮긴 건 아니지만, **"한 정책으로 모두를 만족시킬 수 없다"는 핵심 통찰**은 4화의 4가지 플랜과 5화의 Flex per-function scaling으로 명확하게 반영돼 있습니다.

---

## 보조 논문 — 같은 흐름의 시스템 연구들

Shahrad et al. 만큼 이 시리즈와 직결되지는 않지만, 같은 문제 공간을 다룬 중요 논문 두 편을 짧게 짚습니다.

### Cortez et al., SOSP 2017 — Resource Central

- **제목**: "Resource Central: Understanding and Predicting Workloads for Improved Resource Management in Large Cloud Platforms"
- **저자**: Eli Cortez, Anand Bonde, Alexandre Muzio, Mark Russinovich, Marcus Fontoura, Ricardo Bianchini
- **소속**: Microsoft

VM 워크로드를 분석한 논문이지만 **방법론과 철학이 Shahrad 논문의 직접적 선조**입니다. "워크로드를 잘 이해하면 자원 관리를 잘 할 수 있다", "예측을 운영 정책에 넣자"는 같은 신념을 공유합니다. Russinovich와 Bianchini가 두 논문 모두에 이름을 올리고 있는 게 우연이 아닙니다.

### Ambati et al., OSDI 2020 — Harvest VMs

- **제목**: "Providing SLOs for Resource-Harvesting VMs in Cloud Platforms"
- **소속**: Microsoft

남는 자원을 동적으로 회수해 활용하는 메커니즘에 대한 논문입니다. "정해진 만큼만 보장하고 나머지는 best-effort로 활용한다"는 사고방식은 Functions의 **Pre-warmed 인스턴스, Always Ready의 차등 보장**과 사상적 결을 같이 합니다.

> 위 두 논문은 Azure Functions를 직접 다루지는 않습니다. 같은 그룹·같은 사상 계열의 시스템 연구로 참고하세요.

---

## 시리즈를 마치며 — 우리는 무엇을 봤는가

7화에 걸쳐 본 것을 한 줄씩 정리합니다.

| 화 | 우리가 본 것 | 핵심 코드/개념 |
|---|---|---|
| 1 | 호스트가 부팅하는 과정 | `WebJobsScriptHostService`, `ScriptHost.InitializeAsync` |
| 2 | 워커 프로세스가 어떻게 떠지는가 | `RpcWorkerProcess`, `worker.config.json` |
| 3 | 호스트와 워커가 어떻게 대화하는가 | `FunctionRpc.proto`, `EventStream`, `StreamingMessage` |
| 4 | 실제 호출이 워커로 디스패치되는 흐름 | `FunctionInvocationDispatcher`, `InvocationRequest` |
| 5 | 인스턴스가 어떻게 늘어나는가 | `IScaleMonitor`, `ITargetScaler`, Flex per-function scaling |
| 6 | 첫 호출이 빠르려면 무엇이 필요한가 | Placeholder 모드, `StandbyManager`, Specialization |
| 7 | 이 모든 결정 뒤에 있는 학술적 근거 | Shahrad et al., USENIX ATC 2020 |

### 한 가지 결론

Azure Functions의 호스트는 **거대한 단일 추상화**가 아닙니다. 부팅, IPC, 디스패치, 스케일링, 워밍이 각각 독립된 모듈로 존재하고, 각 모듈마다 명확한 인터페이스와 명확한 출처(공개 코드 또는 공개 논문)가 있습니다. "Functions가 마법처럼 동작한다"는 인상은 잘 만들어진 추상화가 만든 환상일 뿐, 그 아래에는 우리가 따라갈 수 있는 평범한 .NET 코드와 평범한 시스템 연구가 있습니다.

이 시리즈가 그 환상을 한 겹 벗기는 데 도움이 되었기를 바랍니다.

---

## 시리즈 목차

| # | 제목 |
|---|---|
| 1 | [호스트 부트스트랩 — `WebJobsScriptHostService`부터 `ScriptHost`까지](./01-host-bootstrap.md) |
| 2 | [워커 프로세스 — `RpcWorkerProcess`와 언어 워커의 시작](./02-worker-process.md) |
| 3 | [gRPC 이벤트 스트림 — 호스트와 워커는 무엇을 주고받는가](./03-grpc-event-stream.md) |
| 4 | [Dispatcher와 Invocation — 함수 호출이 워커에 도달하기까지](./04-dispatcher-and-invocation.md) |
| 5 | [스케일링 내부 — 인스턴스는 어떻게 늘어나는가](./05-scaling-internals.md) |
| 6 | [콜드 스타트와 Placeholder — 첫 호출은 왜 빠를 수 있는가](./06-cold-start-placeholder.md) |
| 7 | **학술적 관점 — Azure Functions를 분석한 논문들** ← 현재 글 |

---

## 입문편으로 돌아가기

심화편을 다 읽었다면, [입문편(Azure Functions 101)](../../azure-functions-101/ko/01-what-is-azure-functions.md)으로 돌아가 같은 주제를 처음의 시각으로 다시 보는 것을 권합니다. 같은 단어가 다르게 들릴 겁니다.

---

## References

**핵심 논문**
- Shahrad et al. (2020). *Serverless in the Wild: Characterizing and Optimizing the Serverless Workload at a Large Cloud Provider*. USENIX ATC 2020. [USENIX 페이지](https://www.usenix.org/conference/atc20/presentation/shahrad) · [arXiv:2003.03423](https://arxiv.org/abs/2003.03423)

**관련 논문**
- Cortez et al. (2017). *Resource Central: Understanding and Predicting Workloads for Improved Resource Management in Large Cloud Platforms*. SOSP 2017.
- Ambati et al. (2020). *Providing SLOs for Resource-Harvesting VMs in Cloud Platforms*. OSDI 2020.

**데이터셋**
- [Azure Public Dataset 저장소](https://github.com/Azure/AzurePublicDataset)

**호스트 코드 (commit `5e59423`)**
- [Azure/azure-functions-host](https://github.com/Azure/azure-functions-host/tree/5e59423ba45491041d18224c3e72c168a4a5b7f7)
