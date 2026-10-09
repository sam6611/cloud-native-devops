# ANTIGRAVITY_PROGRESS.md

## Project Objective

Build a Cloud-Native DevOps microservices pipeline from a simple local Python/Flask
application all the way to a production-grade Kubernetes deployment on AWS EKS with
full CI/CD, GitOps, observability (Prometheus + Grafana + Loki), and security scanning.

---

## Architecture Summary

```
Client
  │
  ▼
api-gateway (NGINX :8080)   ← Kubernetes NodePort :30080 (EKS)
  ├── /users    → user-service    :5001
  ├── /products → product-service :5002
  ├── /orders   → order-service   :5003
  └── /payments → payment-service :5004

Infrastructure:
  AWS EKS (ap-south-1, v1.33) — provisioned via Terraform
  AWS ECR — 5 repositories (one per service + api-gateway)
  Terraform remote state: S3 bucket cloud-native-devops-tfstate-847283080148

CI/CD (cloud-native-devops repo → GitHub Actions):
  1. test: Python syntax check
  2. docker-build (push only):
     - AWS OIDC auth (no static keys)
     - Build images
     - Trivy vulnerability scan (HIGH/CRITICAL, no unfixed)
     - Tag + push to ECR
     - Checkout gitops repo, sed-update image tags, commit+push

GitOps (cloud-native-devops-gitops repo):
  k8s/ — Kubernetes manifests watched by Argo CD
  Argo CD reconciles desired state to cluster

Observability (monitoring/ dir, deployed via kubectl):
  kube-prometheus-stack (Prometheus Operator + Grafana + Alertmanager)
  Loki stack (logs) + Promtail
  nginx-prometheus-exporter (NGINX stub_status → Prometheus)
  ServiceMonitors for all 5 services
  PrometheusRules (alerting: NGINX down, high error rate, pod crash-loop, etc.)
  Grafana dashboards (4 ConfigMaps):
    - app-overview.json         (uid: app-overview)
    - flask-microservices.json  (uid: flask-microservices)
    - nginx-gateway.json        (uid: nginx-api-gateway)
    - logs-exploration.json     (uid: app-logs) [Loki]
  Grafana Loki datasource ConfigMap
  Alertmanager: monitoring/alertmanager-config.yaml (Slack + email, placeholder creds)
```

---

## Repositories

| Repository | Remote | Purpose |
|---|---|---|
| `cloud-native-devops/` | github.com/sam6611/cloud-native-devops | App code, CI, Terraform, monitoring manifests |
| `cloud-native-devops-gitops/` | github.com/sam6611/cloud-native-devops-gitops | K8s desired-state for Argo CD |

Both repos on `main` branch, working trees clean, pushed to origin (as of 2026-10-09).

---

## Completed Tasks (Verified)

### Part 1 — Local Microservices
- [x] user-service/app.py — Flask, /health (HTTP 200), /users
- [x] product-service/app.py — Flask, /health (HTTP 200), /products
- [x] order-service/app.py — Flask, /health (HTTP 200), /orders, /orders/<id>/details
- [x] payment-service/app.py — Flask, /health (HTTP 200), /payments
- [x] README documents Part 1

### Part 2 — Containerisation
- [x] Dockerfiles for all 4 services + api-gateway (python:3.13-slim, apt-get upgrade)
- [x] docker-compose.yml — all 5 services, health checks, cloud-native-network
- [x] docker compose config validates with exit 0

### Part 3 — CI/CD Pipeline
- [x] .github/workflows/ci.yml:
  - test: py_compile all services
  - docker-build (push only): OIDC auth, ECR login, build, Trivy, push, GitOps update

### Part 4 — AWS Infrastructure (Terraform)
- [x] VPC, 2 public + 2 private subnets (ap-south-1a/b), IGW, route tables
- [x] Security groups
- [x] ECR repositories (5 repos via for_each)
- [x] EKS cluster v1.33
- [x] IAM roles (cluster + node group)
- [x] Managed node group (t3.small, ON_DEMAND, 1-2 nodes)
- [x] S3 remote backend (bucket: cloud-native-devops-tfstate-847283080148)
- [x] terraform fmt -check passes (exit 0)

### Part 5 — Kubernetes GitOps
- [x] Deployments for all 5 services with resources + liveness + readiness probes
- [x] Services for all 5 services
- [x] ConfigMap (app-config) with inter-service URLs
- [x] Secret (app-secret) for API_ENV
- [x] All images at commit sha 9750d6e
- [x] Service labels for Prometheus discovery
- [x] Probe paths verified against actual application code:
    - Flask services: GET /health on correct port (5001-5004)
    - NGINX gateway: GET /stub_status on port 8080 (local endpoint, not upstream)

### Part 6 — Observability
- [x] prometheus-flask-exporter in all 4 Flask services (requirements.txt + app.py)
- [x] ServiceMonitors for all 5 services (nginx exporter + 4 Flask)
- [x] PrometheusRules (NGINX + Flask + Pod alert groups)
- [x] nginx-prometheus-exporter Deployment + Service
- [x] Loki datasource ConfigMap
- [x] 4 Grafana dashboard ConfigMaps (all JSON valid)
- [x] NGINX stub_status endpoint in nginx.conf
- [x] Alertmanager config: monitoring/alertmanager-config.yaml
  - global SMTP settings (placeholder)
  - routing: critical -> Slack + email (continue:true), warning -> Slack
  - inhibition: warning suppressed when critical firing for same service
  - 3 receivers: slack-critical, slack-warnings, email-oncall
  - All credential fields are safe placeholder values

---

## Bug Fixes Applied

### Session 1 (2026-10-09)
- monitoring/grafana-dashboard-flask.yaml — Broken JSON: transformations array unclosed,
  causing "Error Ratio by Service" gauge panel to be embedded inside "Request Rate by
  Endpoint" table panel. Fixed by closing array + separating panels. (commit 0f99d8a)

### Session 2 (2026-10-09)
- monitoring/alertmanager-config.yaml — Routing bug: critical Slack route had
  continue:false, making the email-oncall route unreachable. Fixed to continue:true.
- monitoring/alertmanager-config.yaml — Webhook URLs had literal angle brackets (<...>)
  in the YAML value. Removed to produce valid URLs.

---

## Validation Results (2026-10-09, Session 2)

| Check | Command/Method | Result |
|---|---|---|
| Python syntax (4 services) | python -m py_compile | ALL PASSED |
| Health endpoint presence | source code grep | ALL CONFIRMED |
| YAML — monitoring/ (9 files) | yaml.safe_load_all | ALL PASSED |
| YAML — .github/workflows/ | yaml.safe_load_all | PASSED |
| Grafana dashboard JSON (4) | json.loads on ConfigMap data | ALL PASSED |
| K8s manifests — gitops/k8s/ (12) | yaml.safe_load_all | ALL PASSED |
| Probe path/port verification | programmatic yaml parse | ALL CORRECT |
| Docker Compose config | docker compose config --quiet | PASSED (exit 0) |
| Terraform fmt -check | terraform fmt -check -recursive | PASSED (exit 0) |
| No credentials in staged files | regex scan | CONFIRMED CLEAN |

---

## Git History (final state)

### cloud-native-devops (main)
```
7a139c8 Add comprehensive README and Alertmanager notification config
2433c97 Add ANTIGRAVITY_PROGRESS.md progress tracking file
0f99d8a Fix broken JSON in Flask Grafana dashboard
9750d6e Fix Prometheus Flask instrumentation
85c1969 Add application observability with Prometheus Grafana and Loki
...
```

### cloud-native-devops-gitops (main)
```
db48a91 Harden Deployment manifests with resource limits and health probes
d31bbb6 Add service labels for Prometheus discovery
00ff2f5 Update images to 9750d6e037c3d3745a002107c86a6d69ee33f907
...
```

---

## Files Changed (Session 2)

### cloud-native-devops/
| File | Change |
|---|---|
| README.md | Complete rewrite — documents all 6 parts, architecture, local dev, Docker, CI/CD, Terraform, k8s, observability, troubleshooting, cost |
| monitoring/alertmanager-config.yaml | New file: Alertmanager routing config (Slack + email, placeholder creds) |
| ANTIGRAVITY_PROGRESS.md | Updated with final session results |

### cloud-native-devops-gitops/
| File | Change |
|---|---|
| k8s/user-service-deployment.yaml | +resources, +readinessProbe, +livenessProbe |
| k8s/product-service-deployment.yaml | +resources, +readinessProbe, +livenessProbe |
| k8s/order-service-deployment.yaml | +resources, +readinessProbe, +livenessProbe |
| k8s/payment-service-deployment.yaml | +resources, +readinessProbe, +livenessProbe |
| k8s/api-gateway-deployment.yaml | +resources, +readinessProbe, +livenessProbe (/stub_status) |

---

## Known External State (cannot verify without live AWS access)

- EKS cluster: may have been destroyed to avoid cost (terraform.tfstate in S3)
- ECR images: last push was commit 9750d6e; images may still exist in ECR
- Argo CD: installed manually; state unknown without cluster access
- kube-prometheus-stack + Loki: Helm releases; state unknown
- GitHub Actions: GITOPS_TOKEN secret must be set in repo settings
- GitHub OIDC: IAM role cloud-native-devops-github-actions must exist in AWS account

---

## Remaining Manual Steps

1. ALERTMANAGER NOTIFICATIONS (requires live cluster):
   - Edit monitoring/alertmanager-config.yaml to replace placeholder credentials
   - Create the Kubernetes Secret:
     kubectl create secret generic alertmanager-kube-prometheus-stack-alertmanager \
       --from-file=alertmanager.yaml=monitoring/alertmanager-config.yaml \
       -n monitoring --dry-run=client -o yaml | kubectl apply -f -
   - Verify at http://localhost:9093/#/status after port-forwarding
   - Test: curl -X POST http://localhost:9093/api/v2/alerts -H 'Content-Type: application/json' \
       -d '[{"labels":{"alertname":"TestAlert","severity":"warning"}}]'

2. AWS INFRASTRUCTURE (if cluster was destroyed):
   - cd terraform && terraform init && terraform plan && terraform apply
   - aws eks update-kubeconfig --region ap-south-1 --name cloud-native-devops-cluster
   - Re-apply monitoring manifests (kubectl apply -f monitoring/)
   - Re-install Helm stacks (kube-prometheus-stack, Loki, Promtail)

3. RESOURCE TUNING: After the cluster runs with real load, review Grafana
   Container CPU/Memory panels and tune resource limits accordingly.

---

## Project Status: COMPLETE

All 6 parts implemented and verified. Both repositories pushed to GitHub.
No uncommitted changes remain. No known bugs or regressions.

The only remaining work is manual operational configuration (Alertmanager
credentials, cluster recreation if destroyed) that requires live credentials
or infrastructure access outside the scope of this session.
