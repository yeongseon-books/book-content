# Oracle Content Review — ai-web-dev-101

- **Session**: `ses_228dc648dffekXk0pGzzRlp337`
- **Date**: 2026-04-29
- **Verdict**: **NEEDS-FIXES**
- **Effort**: Medium
- **Layout**: Korean-only (actual files at `content/ai-web-dev-101/ko/*.md` despite docs claiming flat layout)

## P0 blockers (broken on fresh install today)

### 1. Vercel AI SDK example broken — `ko/03-ai-chatbot.md:56, 74-90, 112-140, 177-239`
**Problem**: Installs `npm install ai @ai-sdk/openai` only (line 56); imports `useChat` from `ai/react` (lines 112, 200); uses `input/handleInputChange/handleSubmit/isLoading` (lines 115, 203); renders `message.content` (lines 125, 222).

Current AI SDK requires: `@ai-sdk/react`, `sendMessage`, `message.parts`, `convertToModelMessages(...)`, `toUIMessageStreamResponse()`.

**Fix**: Install `npm install ai @ai-sdk/react @ai-sdk/openai`. Client: `useState + sendMessage + status + message.parts`. Server: `UIMessage[] -> convertToModelMessages(...) -> result.toUIMessageStreamResponse()`.

### 2. Azure App Service FastAPI deployment incomplete — `ko/06-deploy.md:117-156`
**Problem**: Mentions both Flask and FastAPI (line 117), but only documents `az webapp up` (lines 131-138). FastAPI requires startup command per current Azure docs; without it, default site appears instead of app.

**Fix**: Add startup command `gunicorn -w 2 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000 main:app` and `requirements.txt` requirements (`fastapi`, `uvicorn`, `gunicorn`). Or narrow scope to Flask deployment only.

## P1 important

- **`ko/01-hello-ai-api.md:69-70, 85-86, 109, 140-142, 158-159`** — Teaches `gpt-3.5-turbo` as default; OpenAI docs list it as legacy. Switch to `gpt-4o-mini` class.
- **`ko/01-hello-ai-api.md:140-142`** — Hardcoded KRW token cost is fragile. Replace with "check pricing page."
- **`ko/01-hello-ai-api.md:82, 155` / `ko/04-rag-intro.md:114`** — API key hardcoded in code conflicts with security messaging. Use `OpenAI()` + `os.environ["OPENAI_API_KEY"]`.
- **All 7 articles** — Series teaches Chat Completions only; never mentions OpenAI Responses API is now primary. Add "for new projects, also consider Responses API" note OR migrate eps 1+5.
- **`ko/04-rag-intro.md:141-146`** — Description says "cosine similarity" but code uses `np.dot(...)`. Add normalization OR change description to "dot product similarity."
- **`ko/04-rag-intro.md:176-182`** — RAG cautions missing **prompt injection / malicious document instructions**. Add: "retrieved docs are reference data not trusted commands," document delimiters, no-answer-outside-evidence rule, source attribution.
- **`ko/05-ai-agent.md:208-211`** — `eval(expression)` dangerous even as demo. Replace with `ast`-based arithmetic parser or whitelisted operator calculator.
- **`ko/05-ai-agent.md:313-319`** — Agent safety section covers infinite loops/cost only; missing **tool arg validation, permission scope, side-effect control**. Add allowlist, schema validation, timeout, retry caps, user confirmation for writes.
- **`ko/06-deploy.md:150-156`** — `az webapp config appsettings set --settings OPENAI_API_KEY=sk-xxxx...` leaks secret to shell history. Use local env var substitution (`OPENAI_API_KEY=$OPENAI_API_KEY`) or portal.
- **`ko/03-ai-chatbot.md:44-57, 67-71`** — Python-centric series suddenly switches to Next.js/TypeScript without prerequisite explanation. Either label as "frontend interlude" with Node/npm/React App Router prerequisites, OR replace with FastAPI streaming chapter.
- **`ko/01-hello-ai-api.md:69` / `ko/04-rag-intro.md:104`** — All `pip install` commands unpinned. Add "tested on YYYY-MM-DD" + version range or example `requirements.txt`.

## P2 polish

- **`ko/01-hello-ai-api.md:25, 37, 39, 171, 179, 181`** — `거대한 두뇌`, `무궁무진한 가능성`, `축하드립니다`, `정리하면` — AI slop / promotional tone. Use plainer prose.
- **`ko/05-ai-agent.md:291`** — "정말 대견하지 않나요?" awkward for tutorial tone.
- **`ko/07-eval-improve.md:27, 192`** — "여러분의 손에는…", "어떤 멋진 서비스를…" — translation smell / encouragement tone. Use practical closer.
- **`ko/03-ai-chatbot.md:207`** — Code UI uses emoji (`🧑‍🍳`); conflicts with repo no-emoji rule.

## Per-article summary

- **`ko/01-hello-ai-api.md`** — Good structure, natural intro. Default model, pricing, key-management examples are decay points.
- **`ko/02-prompt-engineering.md`** — Most stable of the 7; low code dependency, no major errors found.
- **`ko/03-ai-chatbot.md`** — Top fix priority. Latest AI SDK contract changed; examples broken on fresh install.
- **`ko/04-rag-intro.md`** — OpenAI embeddings choice still OK. Hardcoded keys, similarity description mismatch, prompt-injection warning missing.
- **`ko/05-ai-agent.md`** — Tool calling flow OK. `eval` example + weak safety section weaken practical sense.
- **`ko/06-deploy.md`** — Operational sense good but FastAPI on App Service incomplete per current docs. Security examples need work.
- **`ko/07-eval-improve.md`** — Series closer well-placed. Model recommendations need version-neutral phrasing.

## Series-wide observations

- **Structural rules mostly pass**: All 7 have H1, `## 시리즈 목차`, `## 참고 자료`, final `Tags:` line.
- **Layout discrepancy**: Repo docs say flat Korean-only; actual files in `ko/`. Metadata/docs inconsistency (not content blocker).
- **Biggest decay points**: Vercel AI SDK and Azure FastAPI deployment (NOT OpenAI Python SDK).
- **Series cohesion break**: Episodes 1-2, 4-7 are Python+LLM; episode 3 jumps to JS/TS. Either label intentionally or replace with FastAPI streaming.
- **Security messaging inconsistent**: Eps 1/4 hardcode keys, ep 5 has `eval`, ep 6 has secret-in-CLI.

## Action list

**P0**
1. Rewrite `03-ai-chatbot.md` AI SDK example for current `@ai-sdk/react` API
2. Fix `06-deploy.md` FastAPI deployment with startup command + correct requirements

**P1**
3. Update default model from `gpt-3.5-turbo` to `gpt-4o-mini` class throughout
4. Remove hardcoded KRW token costs
5. Standardize API key handling via `os.environ`
6. Add Responses API mention (at minimum) or migrate eps 1+5
7. Fix cosine similarity description/code mismatch in `04-rag-intro.md`
8. Add prompt-injection warnings to RAG chapter
9. Replace `eval` in agent chapter with safe arithmetic parser
10. Expand agent safety section (allowlist, schema validation, timeout, retry caps)
11. Fix secret-in-CLI in deploy chapter
12. Label episode 3 as frontend interlude OR replace with FastAPI streaming
13. Pin pip dependencies with "tested on" date

**P2**
14. Tone down AI-slop/promotional phrasing across eps 1, 5, 7
15. Remove emoji from code UI in episode 3
