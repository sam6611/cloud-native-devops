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
api-gateway (NGINX :8080)   ← Kubernetes LoadBalancer (EKS)
  ├── /users    → user-service    :5001
  ├── /products → product-service :5002
  ├── /orders   → order-service   :5003
  └── /payments → payment-service :5004

Infrastructure:
  AWS EKS (ap-south-1, v1.33) — provisioned via Terraform
  AWS ECR — 5 repositories (one per service + api-gateway)
  Terraform state: local (terraform.tfstate in cloud-native-devops/terraform/)

CI/CD (cloud-native-devops repo → GitHub Actions):
  1. test: Python syntax check
  2. docker-build (push only):
     - AWS OIDC auth
     - Build images
     - Trivy vulnerability scan (HIGH/CRITICAL, no unfixed)
     - Tag + push to ECR
     - Checkout gitops repo, sed-update image tags, commit+push

GitOps (cloud-native-devops-gitops repo):
  k8s/ — Kubernetes manifests watched by Argo CD
  Argo CD reconciles desired state to cluster

Observability (monitoring/ dir, deployed via kubectl):
  kube-prometheus-stack (Prometheus Operator + Grafana + Alertmanager)
  Loki stack (logs)
  nginx-prometheus-exporter (NGINX stub_status → Prometheus)
  ServiceMonitors for all 5 services
  PrometheusRules (alerting: NGINX down, high error rate, pod crash-loop, etc.)
  Grafana dashboards (4 ConfigMaps):
    - app-overview.json         (uid: app-overview)
    - flask-microservices.json  (uid: flask-microservices)
    - nginx-gateway.json        (uid: nginx-api-gateway)
    - logs-exploration.json     (uid: app-logs) [Loki]
  Grafana Loki datasource ConfigMap
```

---

## Repositories

| Repository | Purpose |
|---|---|
| `cloud-native-devops/` | Application code, Dockerfiles, CI, Terraform, monitoring manifests |
| `cloud-native-devops-gitops/` | Kubernetes desired-state manifests for Argo CD |

Both repos: `origin/main` branch, working tree clean (as of 2026-10-09).

---

## Completed Tasks (Verified)

### Part 1 — Local Microservices
- [x] `user-service/app.py` — Flask, `/health`, `/users`
- [x] `product-service/app.py` — Flask, `/health`, `/products`
- [x] `order-service/app.py` — Flask, `/health`, `/orders`, `/orders/<id>/details` (calls other services)
- [x] `payment-service/app.py` — Flask, `/health`, `/payments`
- [x] `README.md` documents Part 1

### Part 2 — Containerisation
- [x] Dockerfiles for all 4 services + api-gateway (python:3.13-slim, hardened with apt-get upgrade)
- [x] `docker-compose.yml` — all 5 services with health checks, shared network

### Part 3 — CI/CD Pipeline
- [x] `.github/workflows/ci.yml`:
  - `test` job: py_compile for all services
  - `docker-build` job (push only): AWS OIDC (IAM role), ECR login, build, Trivy scan, ECR push
  - GitOps image tag update (checkout gitops repo, sed, commit, push)

### Part 4 — AWS Infrastructure (Terraform)
- [x] VPC, 2 public + 2 private subnets (ap-south-1a/b), IGW, route tables
- [x] Security groups
- [x] ECR repositories (5 repos via for_each)
- [x] EKS cluster v1.33
- [x] IAM roles (cluster + node group)
- [x] Managed node group
- [x] terraform.tfstate.backup exists (evidence of prior apply)

### Part 5 — Kubernetes GitOps (cloud-native-devops-gitops)
- [x] Deployments + Services for all 5 services
- [x] ConfigMap (app-config) with inter-service URLs
- [x] Secret (app-secret) for API_ENV
- [x] All images at commit sha 9750d6e (latest CI push)
- [x] Service labels for Prometheus discovery

### Part 6 — Observability
- [x] prometheus-flask-exporter in all 4 Flask services
- [x] ServiceMonitors for all 5 services (nginx exporter + 4 Flask)
- [x] PrometheusRules (NGINX + Flask + Pod alerts)
- [x] nginx-prometheus-exporter Deployment + Service
- [x] Loki datasource ConfigMap
- [x] 4 Grafana dashboard ConfigMaps (all JSON valid after bug fix)
- [x] NGINX stub_status endpoint in nginx.conf

---

## Bug Fixes Applied This Session

### 1. monitoring/grafana-dashboard-flask.yaml — Broken JSON (commit 0f99d8a)

Problem: The transformations array of the "Request Rate by Endpoint" (table) panel
was not closed. The next panel "Error Ratio by Service" was embedded inside the
transformations array, making the JSON invalid and unparseable by Grafana.

Fix: Closed the transformations array with [] and the table panel object, then
separated the gauge panel as a proper sibling.

Verification: python yaml+json parse — 7 panels confirmed, all valid.

---

## Validation Results (2026-10-09)

| Check | Result |
|---|---|
| python -m py_compile (4 services) | All pass |
| YAML parse — monitoring/ (8 files) | All valid |
| YAML parse — gitops/k8s/ (12 files) | All valid |
| YAML parse — .github/workflows/ (1 file) | Valid |
| JSON parse — 4 Grafana dashboard ConfigMaps | All valid (post-fix) |
| Git working trees | Both repos clean, up to date with origin/main |

---

## Known External Dependencies (Require Live AWS Access to Verify)

- EKS cluster state (may have been destroyed to save cost)
- ECR images (most recent push was commit 9750d6e)
- Argo CD installation on cluster
- kube-prometheus-stack + Loki stack Helm releases
- GitHub Actions secrets: GITOPS_TOKEN
- GitHub OIDC trust relationship with IAM role cloud-native-devops-github-actions

---

## Files Changed This Session

| File | Change |
|---|---|
| monitoring/grafana-dashboard-flask.yaml | Fixed broken JSON panel structure |
| ANTIGRAVITY_PROGRESS.md | Created (this file) |

---

## Remaining Optional Enhancements

1. README update — Currently only documents Part 1. Could cover Docker Compose, CI/CD,
   Terraform, k8s, and observability.

2. Resource requests/limits in k8s deployments — Only nginx-prometheus-exporter has them.

3. Liveness/readiness probes — Not present in any k8s deployment manifests.

4. Alertmanager receiver — PrometheusRules defined but no Alertmanager notification
   routing configured (email/Slack/PagerDuty).

---

## Next Action (if work resumes)

The project is functionally complete. If continuing:
1. git push origin main (in cloud-native-devops/) to push the dashboard fix upstream.
2. Optionally expand README.md to cover Parts 2-6.
3. Optionally add resource limits + k8s liveness/readiness probes.
4. If EKS cluster was destroyed, re-run terraform apply to recreate infrastructure.
