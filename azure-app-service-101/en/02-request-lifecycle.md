# Request Lifecycle: How Requests Reach Your App

> Azure App Service 101 Series (2/7)

"Why is my app returning a 502 error?" "Response times suddenly increased—what's the cause?"

To answer these questions, you need to understand the **complete journey of a request reaching your app**. In this post, we'll walk through the Azure App Service Request Lifecycle step by step.

---

## Overall Request Flow

A user's HTTP request passes through these layers before reaching your app:

```
Client → DNS → Azure Load Balancer → App Service Frontend → Worker Instance → App Process
```

Issues can occur at each stage, resulting in different error messages.

![Request Lifecycle flow diagram](../../assets/azure-app-service-101/02/01-full-request-lifecycle.en.png)

---

## Stage 1: DNS and Global Entry

### DNS Resolution

The request starts with DNS resolution of the app hostname.

- **Default domain:** `<app-name>.azurewebsites.net`
- **Custom domain:** `www.myapp.com` (with CNAME configured)

### TLS Handshake

After DNS resolution:
1. TLS handshake occurs
2. SNI (Server Name Indication) identifies the app
3. Host header routes to the correct app

```bash
# Verify DNS resolution
nslookup myapp.azurewebsites.net

# Check TLS certificate
openssl s_client -connect myapp.azurewebsites.net:443 -servername myapp.azurewebsites.net
```

![IMAGE: Custom Domain settings]
`📸 Screenshot: Azure Portal → App Service → Custom domains`

---

## Stage 2: Frontend Routing

The App Service Frontend performs these roles:

| Role | Description |
|------|-------------|
| TLS Termination | Decrypts HTTPS |
| Host Validation | Verifies request goes to correct app |
| Access Restriction Evaluation | IP restrictions, auth checks |
| Instance Selection | Routes to healthy Worker |

### ⚠️ What If Frontend Fails?

If no healthy backend exists, requests fail **before your app code even runs**.

| Error Code | Meaning |
|------------|---------|
| `403` | Blocked by access restrictions |
| `502` | Backend connection failed |
| `503` | Service unavailable |

```bash
# Check access restriction settings
az webapp config access-restriction show \
    --resource-group $RG \
    --name $APP_NAME \
    --output json
```

**Example output:**
```json
{
  "ipSecurityRestrictions": [
    {
      "action": "Allow",
      "ipAddress": "203.0.113.0/24",
      "name": "corp-office",
      "priority": 100
    }
  ]
}
```

![IMAGE: Access Restrictions settings]
`📸 Screenshot: Azure Portal → App Service → Networking → Access restrictions`

---

## Stage 3: Worker Reverse Proxy

Inside the Worker instance, a local reverse proxy forwards requests to the app process.

### Port Contract

**Key point:** Your app must bind to the **port provided by the platform**.

```python
# ❌ Wrong - hardcoded port
app.run(host="0.0.0.0", port=5000)

# ✅ Correct - read port from environment variable
import os
port = int(os.environ.get("PORT", 8000))
app.run(host="0.0.0.0", port=port)
```

**Common mistakes:**
- Works locally but fails after deployment
- Starts successfully but requests fail

![IMAGE: Startup Command in General Settings]
`📸 Screenshot: Azure Portal → App Service → Configuration → General settings`

---

## Stage 4: Application Execution

Finally, the request reaches your app code!

### Factors Affecting Performance

| Factor | Description |
|--------|-------------|
| CPU/Memory usage | Instance resource saturation |
| External dependencies | DB, API call latency |
| Threads/Event loop | Concurrency limits |
| Connection pools | Outbound connection management |

### Response Return Path

Responses travel back in reverse order:

```
App → Worker → Frontend → Load Balancer → Client
```

Headers added by the platform:
- Compression-related headers
- Security headers
- Reverse proxy metadata

---

## Timeouts and Connection Behavior

### Platform Timeouts

App Service has multiple levels of timeouts:

| Timeout | Impact |
|---------|--------|
| Frontend request timeout | Long-running requests → 504 Gateway Timeout |
| Idle connection timeout | Idle sockets closed |
| Slow dependencies | Queue buildup, tail latency increase |

### Design Guidelines

```python
# ❌ Bad pattern - long-running work in HTTP request
@app.route('/export')
def export():
    # 10-minute data processing...
    return huge_result  # Timeout risk!

# ✅ Good pattern - async processing
@app.route('/export')
def export():
    job_id = queue_export_job()
    return {"status": "accepted", "jobId": job_id}, 202
```

**Principles:**
- Keep interactive requests short (< 30 seconds)
- Move long tasks to background
- Return `202 Accepted`, then poll/webhook

---

## Instance Selection and Session Affinity

### Default Behavior: Round Robin

Frontend distributes traffic across healthy instances by default.

### Session Affinity (ARR Affinity)

You can pin specific clients to the same instance:

```
Client A ─(Affinity Cookie)─→ Instance 2
Client B ─(Affinity Cookie)─→ Instance 1
```

**Trade-offs:**

| Pros | Cons |
|------|------|
| Supports legacy session code | Uneven load distribution |
| Utilizes in-memory cache | Vulnerable to instance failure |

**Recommendation:** Store sessions/state in **external storage** (Redis, DB)

```bash
# Disable ARR Affinity
az webapp update \
    --resource-group $RG \
    --name $APP_NAME \
    --client-affinity-enabled false
```

![IMAGE: ARR Affinity in Configuration]
`📸 Screenshot: Azure Portal → App Service → Configuration → General settings → ARR affinity`

---

## Health Check and Traffic Eligibility

Health Check determines whether an instance is **eligible** to receive traffic.

### Behavior by State

| State | Traffic |
|-------|---------|
| Healthy | Included in routing pool ✅ |
| Unhealthy | Excluded from pool ❌ |
| Recovering | Re-included after probes pass |

### Health Probe Design Principles

```python
@app.route('/health')
def health():
    # 1. Keep it lightweight
    # 2. Check only dependencies critical for traffic handling
    # 3. Avoid slow external calls
    
    try:
        # Simple check of critical dependencies
        db.execute("SELECT 1")
        return {"status": "healthy"}, 200
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}, 503
```

![IMAGE: Health check settings]
`📸 Screenshot: Azure Portal → App Service → Monitoring → Health check`

---

## Impact of Deployment Slots

Deployment Slots help minimize user impact during deployments.

### Slot Swap Process

1. Deploy new version to Staging Slot
2. Staging completes warm-up
3. Production continues handling traffic
4. Slot Swap switches traffic

**Benefits:**
- Reduces cold start exposure
- Easy rollback of failed deployments

![IMAGE: Deployment slots]
`📸 Screenshot: Azure Portal → App Service → Deployment slots`

---

## Observability: Tracing the Entire Lifecycle

Connect each stage to diagnose issues:

### Correlation Signals

| Signal | Purpose |
|--------|---------|
| Request logs | Status code distribution |
| Frontend diagnostics | Platform-level errors |
| Instance restarts | Stability issues |
| Dependency timing | External call bottlenecks |
| Correlation ID | Per-request tracing |

### Log Configuration

```bash
# Enable HTTP logging
az webapp log config \
    --resource-group $RG \
    --name $APP_NAME \
    --application-logging filesystem \
    --detailed-error-messages true \
    --failed-request-tracing true \
    --web-server-logging filesystem

# Real-time log stream
az webapp log tail \
    --resource-group $RG \
    --name $APP_NAME
```

![IMAGE: Log stream]
`📸 Screenshot: Azure Portal → App Service → Monitoring → Log stream`

---

## Common Failure Patterns

| Symptom | Suspected Layer | First Check |
|---------|----------------|-------------|
| 403 (no app logs) | Frontend | Access restrictions, auth settings |
| 502/503 spike | Worker/app startup | Restart events, Health probe |
| 504 responses | Long request path | Dependency latency, request design |
| Intermittent timeouts | Outbound | SNAT, connection pools |

### Troubleshooting Workflow

1. **Check Frontend**: DNS/TLS/access restrictions
2. **Check Worker**: Health status, restart events
3. **Check App Process**: Ready state, port binding
4. **Check Dependencies**: External call latency, connection issues

---

## Summary

Understanding each stage of the Request Lifecycle helps you:

- **Quickly identify where issues occur**
- **Check the right logs/metrics**
- **Apply the correct solutions**

In the next post, we'll explore **Hosting Models** - App Service Plan selection and deployment models.

---

## Series Index

1. What is Azure App Service? - Understanding the Platform Architecture
2. **[Current] Request Lifecycle: How Requests Reach Your App**
3. Hosting Models: Which Plan Should You Choose?
4. First Deployment: From Local to Azure (Python/Flask)
5. Mastering Configuration: App Settings & Environment Variables
6. Logging and Monitoring Basics
7. Scaling 101: When to Scale Up vs Scale Out?

---

## References

- [Deployment Slots in App Service (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/deploy-staging-slots)
- [Inbound and outbound IPs (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/overview-inbound-outbound-ips)
- [Troubleshoot diagnostic logs (Microsoft Learn)](https://learn.microsoft.com/azure/app-service/troubleshoot-diagnostic-logs)

---

**Tags:** `Azure` `App Service` `Cloud` `Networking` `DevOps`
