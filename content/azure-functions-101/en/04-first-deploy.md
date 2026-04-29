---
title: Deploy a Function App — From Localhost to Azure
series: azure-functions-101
episode: 4
language: en
status: ready
targets:
  tistory: true
  medium: true
  mkdocs: true
  ebook: true
tags:
- Azure
- Azure Functions
- Serverless
- Cloud
last_reviewed: '2026-04-29'
---

# Deploy a Function App — From Localhost to Azure

> Azure Functions 101 series (4/7)

The first three posts set up the mental model. This one is about execution: **create a function locally, deploy it to Azure, and get back a real URL you can call**.

By the end, you'll have:

- A local environment for running functions
- A real Function App on Azure
- An HTTPS endpoint you can call from anywhere
- A concrete sense of what redeploy actually does

The sample uses the Python v2 programming model. The overall flow is nearly identical for the other runtimes.

One more framing note before we start. This walkthrough uses the **classic Consumption plan** because it is still the shortest demo path. As of 2025, though, Consumption is a legacy plan, and **Flex Consumption is the default serverless recommendation for new apps**. We will compare the plans in Part 5; here the goal is to keep the first deployment path simple.

---

## Tooling — three pieces

You need three tools.

| Tool | Role | Install |
|---|---|---|
| **Azure Functions Core Tools** | Local runs + deployment command (`func`) | `npm i -g azure-functions-core-tools@4` |
| **Azure CLI** | Create and manage Azure resources | OS-specific install ([official docs](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)) |
| **Python 3.11+** | Worker runtime | pyenv or the official installer |

You can do all of this from VS Code, but the post sticks to **the CLI only**. Once you've done the full path by hand, the IDE automation is easier to reason about.

Check versions first.

```bash
func --version       # 4.x
az --version         # 2.x
python --version     # 3.11+
```

---

## The full flow on one page

![The full flow on one page](../../../assets/azure-functions-101/04/04-01-the-full-flow-on-one-page.en.png)
---

## 1. Create the project

Start from an empty directory.

```bash
mkdir hello-functions && cd hello-functions
func init . --worker-runtime python --model V2
```

That gives you the basic scaffold. The first three files worth noticing are:

- `host.json` — Host configuration
- `local.settings.json` — Environment variables for local runs
- `requirements.txt` — Python dependencies

`local.settings.json` plays the same role as **App Settings** in Azure. Local execution reads from this file; the deployed app reads from App Settings on the Function App. **The code stays the same across that boundary.**

---

## 2. Add a function

Add the simplest HTTP-triggered function.

```bash
func new --template "Http Trigger" --name hello --authlevel anonymous
```

In the Python v2 model, the function definition lives in `function_app.py`. The generated result looks roughly like this.

```python
import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

@app.function_name(name="hello")
@app.route(route="hello")
def hello(req: func.HttpRequest) -> func.HttpResponse:
    name = req.params.get("name")

    if not name:
        name = req.get_body().decode("utf-8") if req.get_body() else "world"

    return func.HttpResponse(f"Hello, {name}!")
```

That is enough to run immediately.

---

## 3. Run it locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
func start
```

If you see this near the bottom of the output, you're set:

```
Functions:
        hello: [GET,POST] http://localhost:7071/api/hello
```

Call it from another terminal.

```bash
curl "http://localhost:7071/api/hello?name=Sisyphus"
# Hello, Sisyphus!
```

At this point, `func start` is running **a real Functions Host on your machine**. The Host and Worker from Part 3 are both alive, with a gRPC channel between them. It is the same architecture as production, just running on your laptop.

---

## 4. Create Azure resources

Three Azure resources are required.

| Resource | Role |
|---|---|
| **Resource Group** | Logical container for related resources |
| **Storage Account** | Required storage for host state, locks, and trigger metadata |
| **Function App** | The compute resource that runs your functions |

![4. Create Azure resources](../../../assets/azure-functions-101/04/04-02-4-create-azure-resources.en.png)
> Note: The Storage Account is infrastructure storage for the Functions platform itself. It holds things like trigger leases, invocation metadata, and Timer schedule state. Keep business data in a separate store.

Now create the resources. Names must be globally unique, so adjust them as needed.

```bash
RG=rg-hello
LOC=koreacentral
SA=sthello$RANDOM
APP=func-hello-$RANDOM

# 1) Resource Group
az group create --name $RG --location $LOC

# 2) Storage Account
az storage account create \
    --name $SA --resource-group $RG \
    --location $LOC --sku Standard_LRS

# 3) Function App (classic Consumption, Python 3.11)
az functionapp create \
    --name $APP --resource-group $RG \
    --storage-account $SA \
    --consumption-plan-location $LOC \
    --runtime python --runtime-version 3.11 --functions-version 4
```

When the last command finishes, the Function App exists in Azure. The compute target is ready; the code just is not deployed yet.

The `az functionapp create` shape changes by hosting plan. `--consumption-plan-location` is for classic Consumption only. **Premium** and **Dedicated (App Service Plan)** use `--plan` with an existing plan resource. **Flex Consumption** uses a Flex-specific path with `--flexconsumption-location` and `--flexconsumption-runtime`.

For example, a Flex Consumption create flow looks like this.

```bash
az functionapp create \
    --name $APP --resource-group $RG \
    --storage-account $SA \
    --runtime python --runtime-version 3.11 \
    --functions-version 4 \
    --flexconsumption-location $LOC \
    --flexconsumption-runtime python
```

For a new serverless production app, start by evaluating Flex Consumption. This post keeps Consumption only because it is the smallest end-to-end demo.

---

## 5. Deploy

Deployment is one command.

```bash
func azure functionapp publish $APP
```

Under the hood, the flow looks like this.

![5. Deploy](../../../assets/azure-functions-101/04/04-03-5-deploy.en.png)
You should see something like this at the end.

```
Functions in func-hello-xxxxx:
    hello - [httpTrigger]
        Invoke url: https://func-hello-xxxxx.azurewebsites.net/api/hello
```

That URL is your public endpoint.

---

## 6. Call it from the internet

```bash
curl "https://func-hello-xxxxx.azurewebsites.net/api/hello?name=Sisyphus"
# Hello, Sisyphus!
```

That is the shortest path from local code to a live endpoint on Azure. Run the same command again and you redeploy.

---

## Five production concerns to keep in mind

The flow above is **the shortest demo path**. Production work adds a few layers.

1. **App Settings = environment variables** — Values in `local.settings.json` move to Azure through `az functionapp config appsettings set`. Secrets usually belong behind Key Vault references.
2. **Authentication** — `anonymous` is fine for a demo. Real systems usually front functions with function keys, Microsoft Entra ID, or API Management.
3. **CI/CD** — `func ... publish` is good for local demos. Production teams automate the same flow in GitHub Actions or Azure DevOps.
4. **Logs and monitoring** — Connect Application Insights and you get invocation logs, exceptions, and performance metrics in one place.
5. **Plan choice** — Consumption is a fine teaching path, but for new serverless apps the default candidate is usually Flex Consumption.

---

## Three places people usually get stuck

- **Storage Account name collision** — Storage names are globally unique. Patterns like `sthello$RANDOM` help.
- **`func` behaves differently than expected** — Check that Core Tools v4 is installed.
- **Deployment succeeded but the URL returns 404** — Function indexing failures are common. The portal's Log stream usually shows the reason.

---

## Next up

Once the app is deployed, the next real question is **which hosting plan it should live on**. Part 5 compares Consumption, Flex Consumption, Premium, and Dedicated with actual trade-offs instead of marketing labels.

---

## Series context

This is Part 4 of Azure Functions 101. The earlier posts covered triggers and bindings, then the Host and Worker split; this post turns that model into a working deployment path. Parts 5 and 6 move into plan selection, scaling, and cold-start behavior, which is where most production decisions start.

---

<!-- toc:begin -->
## In this series

- [What Is Azure Functions? — A World Where Events Call Your Code](./01-what-is-azure-functions.md)
- [Triggers and Bindings — Everything About Function I/O](./02-triggers-and-bindings.md)
- [Host and Worker — Who Actually Runs Your Functions?](./03-host-and-worker.md)
- **Deploy a Function App — From Localhost to Azure (current)**
- Which Plan Should You Pick? — Consumption / Flex / Premium / Dedicated (upcoming)
- Scaling and Cold Starts — When Serverless Feels Fast and When It Doesn’t (upcoming)
- Monitoring and Operations Fundamentals (upcoming)

<!-- toc:end -->

---

## References

**Official docs**
- [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
- [`az functionapp` CLI reference](https://learn.microsoft.com/en-us/cli/azure/functionapp)
- [Azure Functions Flex Consumption plan hosting](https://learn.microsoft.com/en-us/azure/azure-functions/flex-consumption-plan)
- [Function scale and hosting options](https://learn.microsoft.com/en-us/azure/azure-functions/functions-scale)
- [Run from package deployment](https://learn.microsoft.com/en-us/azure/azure-functions/run-functions-from-deployment-package)

Tags: Azure, Azure Functions, Serverless, Cloud
