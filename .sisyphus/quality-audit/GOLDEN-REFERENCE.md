# Golden Reference — Why `azure-app-service-101` Scores 5/5/5/5/5

This document distills the benchmark patterns from `content/azure-app-service-101/`. Use it as the concrete comparison set when auditing other series.

## Corpus and norm summary

- Canonical files reviewed: **14** (`7 ko + 7 en`)
- Korean total lines: **2,999** (avg **428.43** lines/article)
- English total lines: **3,011** (avg **430.14** lines/article)
- Fenced code/text blocks: **127 ko** + **128 en** (avg **18.14 ko**, **18.29 en** blocks/article)
- Diagrams/images: **24 ko** + **24 en** (avg **3.43** diagrams/article per language)
- Checklist items: **39 ko** + **47 en**
- References norm: typically **3 authoritative official links** plus **1 related-series link** per article
- Korean style automation baseline: `check-ko.sh content/azure-app-service-101/ko` returns **2 hits across 7 posts**. Treat this as noise tolerance, not a target to exceed.

---

## Axis 1 — Structural completeness: benchmark patterns

1. **H1 → hook → series-position sentence happens immediately.**
   - `content/azure-app-service-101/ko/01-what-is-app-service.md:21-28`
   - `content/azure-app-service-101/en/01-what-is-app-service.md:22-29`

2. **The reader gets an explicit scope block near the top.**
   - `content/azure-app-service-101/ko/02-request-lifecycle.md:31-39`
   - `content/azure-app-service-101/en/06-logging-monitoring.md:31-37`

3. **A mental-model blockquote appears early, before deep detail.**
   - `content/azure-app-service-101/ko/07-scaling-101.md:31-39`
   - `content/azure-app-service-101/en/02-request-lifecycle.md:32-40`

4. **Articles close with checklist → TOC → references → tags.**
   - `content/azure-app-service-101/ko/06-logging-monitoring.md:478-527`
   - `content/azure-app-service-101/en/04-first-deploy.md:423-458`

5. **TOC state is maintained correctly across the series.**
   - First post shows current + future posts: `content/azure-app-service-101/ko/01-what-is-app-service.md:268-279`
   - Final post shows linked history + current final post: `content/azure-app-service-101/ko/07-scaling-101.md:450-461`

### What excellence looks like here

The gold series does not treat structure as decoration. It uses the opening to orient the reader, uses end matter consistently, and makes every article scannable by problem, section, checklist, and TOC state.

---

## Axis 2 — Code & diagrams substance: benchmark patterns

1. **Hands-on chapters contain self-contained runnable code.**
   - `content/azure-app-service-101/ko/04-first-deploy.md:81-102` (`app.py` with imports, routes, and `PORT` binding)
   - `content/azure-app-service-101/en/04-first-deploy.md:78-99`

2. **The tutorial validates production parity, not just local happy path.**
   - `content/azure-app-service-101/ko/04-first-deploy.md:153-176`
   - `content/azure-app-service-101/en/04-first-deploy.md:150-172`

3. **Operational articles still use executable artifacts: commands, JSON, KQL, middleware code.**
   - `content/azure-app-service-101/ko/06-logging-monitoring.md:150-245`
   - `content/azure-app-service-101/en/06-logging-monitoring.md:148-244`
   - `content/azure-app-service-101/en/06-logging-monitoring.md:307-347`

4. **Examples explain trade-offs with production patterns, not toy snippets.**
   - `content/azure-app-service-101/en/07-scaling-101.md:137-170` (in-memory session anti-pattern vs Redis-backed version)
   - `content/azure-app-service-101/ko/07-scaling-101.md:315-325` (connection-pool configuration tied to scaling impact)

5. **Diagrams are explanatory and captioned.**
   - `content/azure-app-service-101/ko/01-what-is-app-service.md:68-70`
   - `content/azure-app-service-101/ko/06-logging-monitoring.md:43-45`
   - `content/azure-app-service-101/en/07-scaling-101.md:296-298`

### What excellence looks like here

The series gives the reader something to run, inspect, compare, or reason from in nearly every major section. Diagram count is high, but the diagrams always map to a mechanism or decision.

---

## Axis 3 — Korean naturalness: benchmark patterns

1. **Problem-first hook in natural spoken-technical Korean.**
   - `content/azure-app-service-101/ko/01-what-is-app-service.md:23-27`

2. **Concise series intro and scope sentence without AI-template phrasing.**
   - `content/azure-app-service-101/ko/02-request-lifecycle.md:23-27`

3. **Operational thesis stated directly, without translation-heavy abstraction.**
   - `content/azure-app-service-101/ko/06-logging-monitoring.md:23-27`

4. **Warning language is concrete, not melodramatic.**
   - `content/azure-app-service-101/ko/07-scaling-101.md:23-32`

5. **Long explanations still keep rhythm and specificity.**
   - `content/azure-app-service-101/ko/01-what-is-app-service.md:192-202`
   - `content/azure-app-service-101/ko/02-request-lifecycle.md:225-292`

### What excellence looks like here

The Korean voice sounds like an experienced engineer explaining failure modes and operating constraints to another engineer. It is formal but not stiff, concrete without becoming chatty, and varied in sentence length.

---

## Axis 4 — Narrative flow & reader value: benchmark patterns

1. **Mental model first, then consequences.**
   - `content/azure-app-service-101/ko/01-what-is-app-service.md:49-67`

2. **Symptoms are turned into first-check sequences.**
   - `content/azure-app-service-101/ko/02-request-lifecycle.md:99-131`
   - `content/azure-app-service-101/ko/02-request-lifecycle.md:353-365`

3. **The article keeps answering “so what?” with operational implications.**
   - `content/azure-app-service-101/ko/01-what-is-app-service.md:117-126`
   - `content/azure-app-service-101/ko/05-configuration.md:332-355`

4. **Scaling guidance is tied to downstream systems, not just App Service knobs.**
   - `content/azure-app-service-101/ko/07-scaling-101.md:289-325`

5. **Reader complaints are converted into observability workflow.**
   - `content/azure-app-service-101/en/06-logging-monitoring.md:238-244`

### What excellence looks like here

Gold-level flow is not “definition → options → conclusion.” It is “pain → model → mechanism → verification → checklist,” with most sections earning their place by helping a reader make a decision or debug faster.

---

## Axis 5 — References & metadata polish: benchmark patterns

1. **Front matter is complete and status-aware.**
   - `content/azure-app-service-101/ko/05-configuration.md:1-18`
   - `content/azure-app-service-101/en/06-logging-monitoring.md:1-18`

2. **SEO descriptions are short, article-specific, and problem-led.**
   - `content/azure-app-service-101/ko/02-request-lifecycle.md:17-18`
   - `content/azure-app-service-101/en/07-scaling-101.md:17-19`

3. **References are named, authoritative, and verification-friendly.**
   - `content/azure-app-service-101/ko/05-configuration.md:441-446`
   - `content/azure-app-service-101/en/06-logging-monitoring.md:511-516`
   - `content/azure-app-service-101/en/07-scaling-101.md:464-469`

4. **Visible tag line is stable and truly last.**
   - `content/azure-app-service-101/ko/01-what-is-app-service.md:293-295`
   - `content/azure-app-service-101/en/06-logging-monitoring.md:521-523`

### What excellence looks like here

Metadata is not treated as clerical overhead. It reinforces search intent, publication hygiene, and later verification by auditors and readers.

---

## Length and density norms to compare against

| Metric | Korean benchmark | English benchmark |
| --- | ---: | ---: |
| Avg lines/article | 428.43 | 430.14 |
| Avg fenced blocks/article | 18.14 | 18.29 |
| Avg diagrams/article | 3.43 | 3.43 |
| Total diagrams/series | 24 | 24 |
| Total checklist items/series | 39 | 47 |

### Interpretation

- A 101 series far below **~300 lines/article average** is unlikely to match the chapter depth of the gold reference unless it is unusually dense and still complete.
- A hands-on series with **few or no fenced blocks** is unlikely to match the practical depth of the benchmark.
- A series with **0-1 diagrams total** should usually score below gold on Axis 2 unless the subject truly does not benefit from visual explanation.

---

## Voice samples

### Korean sample 1

> 처음 Azure App Service를 접하면 대개 이렇게 생각합니다. “좋네. 서버 안 만져도 되고, 그냥 코드만 올리면 되네.” 실제로 맞는 말입니다. 그런데 운영에 들어가면 그다음 질문이 바로 따라옵니다. “그런데 왜 설정 하나 바꿨는데 앱이 재시작됐지?” “배포는 끝났는데 왜 요청이 이상하게 들어오지?” “Kudu는 보이는데 앱은 왜 안 뜨지?”
>
> — `content/azure-app-service-101/ko/01-what-is-app-service.md:23-23`

### Korean sample 2

> “앱이 느려요.” “에러가 나요.” “언제부터 시작된 거죠?” 이런 질문에 답하지 못하면 App Service는 관리형 플랫폼이 아니라 보이지 않는 상자처럼 느껴집니다.
>
> 이 글은 Azure App Service 101 시리즈의 6번째 글입니다.
>
> 여기서는 App Service를 로그와 메트릭, 추적 정보로 읽을 수 있는 시스템으로 바꾸는 방법을 다룹니다. 핵심은 로그가 어디로 가는지, 실시간 디버깅과 장기 분석을 어떻게 나눌지, 어떤 알림 기준이 실제로 유용한지 정리하는 것입니다.
>
> — `content/azure-app-service-101/ko/06-logging-monitoring.md:23-27`

### English sample 1

> When deploying a web application to Azure, **Azure App Service** is often the first service you encounter. It's a PaaS (Platform as a Service) where you just deploy your code without managing VMs. To use this service effectively, understanding its internals is crucial.
>
> In this post, we'll explore how the platform works, focusing on the **3-Plane Architecture**.
>
> This is the first post in the Azure App Service 101 series. It sets up the platform mental model you need before deployment, configuration, and troubleshooting start to feel real.
>
> — `content/azure-app-service-101/en/01-what-is-app-service.md:24-28`

### English sample 2

> "Traffic increased and the app is slow." "Want to reduce costs but maintain performance."
>
> **Scaling** is the key strategy for solving these problems. In this post, we'll cover the difference between Scale Up and Scale Out, when to choose each, and how to configure Autoscale.
>
> This is the final post in the Azure App Service 101 series. It ties the earlier platform, deployment, configuration, and monitoring topics into concrete scaling decisions.
>
> — `content/azure-app-service-101/en/07-scaling-101.md:24-28`

---

## Common deviations to flag in other series

Use this as a downgrade checklist. If several items below are present, the series is not gold-level.

### Structural red flags

- [ ] No standalone series-position sentence near the top
- [ ] Missing questions block, mental-model blockquote, or checklist in multiple posts
- [ ] TOC, references, or visible `Tags:` line missing or out of order
- [ ] `<!-- a-grade-intro:begin -->` used as a bypass for otherwise ordinary 101 posts

### Code and diagram red flags

- [ ] Hands-on or troubleshooting chapters contain only toy snippets or pseudo-code
- [ ] Commands are shown with critical flags omitted and no verification step
- [ ] Images are screenshots or diagrams without captions
- [ ] No production-pattern examples for state, auth, logging, deployment, or scaling when those are the chapter topics

### Korean red flags

- [ ] Repeated `~에 대해`, `~에 있어서`, `가지고 있다`, `~한 것이다`
- [ ] Frequent formula endings like `정리하면`, `결론적으로`, `~할 때입니다`
- [ ] Mixed register or visibly translated English syntax
- [ ] Several dense paragraphs in a row with flat sentence rhythm

### Narrative red flags

- [ ] The opening states what the article covers but not why the reader should care
- [ ] Sections list options without a decision frame or failure-mode perspective
- [ ] The article never turns symptoms into “check this first” guidance
- [ ] The ending restates the intro instead of yielding checklist/actionable next steps

### Metadata and references red flags

- [ ] Missing `seo_description`, `last_reviewed`, or required front matter fields
- [ ] Generic tags unrelated to the actual series topic
- [ ] References are vague (“Azure docs”, “see portal”) rather than exact named pages
- [ ] Tags line is missing, not last, or inconsistent with front matter/theme
