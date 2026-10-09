# Cloud-Native DevOps — Microservices on AWS EKS

A production-grade, end-to-end Cloud-Native DevOps project that takes four Python/Flask
microservices from local development all the way to a Kubernetes cluster on AWS EKS, with
a full CI/CD pipeline, GitOps deployment, and a complete observability stack.

---

## Table of Contents

- [Architecture](#architecture)
- [Services](#services)
- [Project Structure](#project-structure)
- [Part 1 — Local Development](#part-1--local-development)
- [Part 2 — Docker and Docker Compose](#part-2--docker-and-docker-compose)
- [Part 3 — CI/CD Pipeline](#part-3--cicd-pipeline)
- [Part 4 — AWS Infrastructure with Terraform](#part-4--aws-infrastructure-with-terraform)
- [Part 5 — Kubernetes and GitOps with Argo CD](#part-5--kubernetes-and-gitops-with-argo-cd)
- [Part 6 — Observability](#part-6--observability)
- [Environment Variables and Configuration](#environment-variables-and-configuration)
- [Testing and Validation](#testing-and-validation)
- [Troubleshooting](#troubleshooting)
- [Cost Considerations](#cost-considerations)
- [Project Status](#project-status)

---

## Architecture

```
                            ┌──────────────────────────────────────┐
                            │            GitHub                    │
                            │   cloud-native-devops (app repo)     │
                            │   cloud-native-devops-gitops (k8s)   │
                            └────────────┬─────────────────────────┘
                                         │ push → GitHub Actions CI
                                         ▼
                            ┌────────────────────────┐
                            │   GitHub Actions CI/CD  │
                            │  test → build → scan   │
                            │  → push ECR → update   │
                            │    GitOps image tags   │
                            └────────────┬───────────┘
                                         │ Argo CD watches
                                         ▼
┌────────────────────────────────────────────────────────────────────┐
│                      AWS EKS Cluster (ap-south-1)                  │
│                                                                    │
│  Client                                                            │
│    │                                                               │
│    ▼                                                               │
│  api-gateway (NGINX) ── NodePort :30080                           │
│    ├── /users    → user-service    :5001  (ClusterIP)              │
│    ├── /products → product-service :5002  (ClusterIP)              │
│    ├── /orders   → order-service   :5003  (ClusterIP)              │
│    └── /payments → payment-service :5004  (ClusterIP)              │
│                                                                    │
│  Monitoring namespace:                                             │
│    Prometheus ← ServiceMonitors (all 5 services)                   │
│    Grafana    ← 4 dashboards (Flask, NGINX, Overview, Logs)        │
│    Loki       ← application logs                                   │
│    Alertmanager ← PrometheusRules (NGINX, Flask, Pod alerts)       │
│                                                                    │
│  AWS Resources (provisioned by Terraform):                         │
│    VPC · 4 subnets · IGW · Route Tables · Security Groups         │
│    ECR (5 repos) · EKS v1.33 · IAM Roles · Node Group (t3.small)  │
│    S3 (Terraform remote state)                                     │
└────────────────────────────────────────────────────────────────────┘
```

---

## Services

| Service | Port | Responsibility | Key Endpoints |
|---|---|---|---|
| `user-service` | 5001 | Manages user data | `GET /health`, `GET /users` |
| `product-service` | 5002 | Manages product catalogue | `GET /health`, `GET /products` |
| `order-service` | 5003 | Manages orders; calls other services | `GET /health`, `GET /orders`, `GET /orders/<id>/details` |
| `payment-service` | 5004 | Manages payment records | `GET /health`, `GET /payments` |
| `api-gateway` | 8080 | NGINX reverse proxy for all services | `/users`, `/products`, `/orders`, `/payments` |

All Flask services expose a `GET /metrics` endpoint (via `prometheus-flask-exporter`)
scraped by Prometheus via ServiceMonitors.

---

## Project Structure

```
cloud-native-devops/                  ← Application repository
│
├── .github/
│   └── workflows/
│       └── ci.yml                    ← GitHub Actions CI/CD pipeline
│
├── api-gateway/
│   ├── Dockerfile
│   └── nginx.conf                    ← NGINX proxy + stub_status
│
├── user-service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── product-service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── order-service/
│   ├── app.py                        ← Calls user, product, payment services
│   ├── requirements.txt
│   └── Dockerfile
│
├── payment-service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── monitoring/                       ← kubectl-applied observability manifests
│   ├── servicemonitors.yaml          ← Prometheus scrape targets
│   ├── prometheusrule-apps.yaml      ← Alerting rules
│   ├── nginx-prometheus-exporter.yaml
│   ├── grafana-datasource-loki.yaml
│   ├── grafana-dashboard-overview.yaml
│   ├── grafana-dashboard-flask.yaml
│   ├── grafana-dashboard-nginx.yaml
│   └── grafana-dashboard-logs.yaml
│
├── terraform/                        ← AWS infrastructure as code
│   ├── provider.tf                   ← S3 remote state backend
│   ├── variables.tf
│   ├── main.tf                       ← VPC, subnets, IGW, route tables
│   ├── security_groups.tf
│   ├── ecr.tf                        ← ECR repositories (for_each)
│   ├── eks.tf                        ← EKS cluster v1.33
│   ├── eks_iam.tf                    ← Cluster + node IAM roles
│   ├── node_group.tf                 ← Managed node group (t3.small)
│   └── outputs.tf
│
├── docker-compose.yml
├── ANTIGRAVITY_PROGRESS.md           ← Session progress tracking
└── README.md

cloud-native-devops-gitops/           ← GitOps repository (Argo CD source)
└── k8s/
    ├── app-config.yaml               ← ConfigMap: inter-service URLs
    ├── app-secret.yaml               ← Secret: API_ENV
    ├── user-service-deployment.yaml
    ├── user-service-service.yaml
    ├── product-service-deployment.yaml
    ├── product-service-service.yaml
    ├── order-service-deployment.yaml ← Reads ConfigMap for service URLs
    ├── order-service-service.yaml
    ├── payment-service-deployment.yaml
    ├── payment-service-service.yaml
    ├── api-gateway-deployment.yaml   ← Reads Secret for API_ENV
    └── api-gateway-service.yaml      ← NodePort :30080
```

---

## Part 1 — Local Development

### Prerequisites

- Python 3.8+
- pip

### Install dependencies

```bash
pip install -r user-service/requirements.txt
pip install -r product-service/requirements.txt
pip install -r order-service/requirements.txt
pip install -r payment-service/requirements.txt
```

### Run each service

Open four separate terminals from the project root:

```bash
# Terminal 1
python user-service/app.py      # http://localhost:5001

# Terminal 2
python product-service/app.py   # http://localhost:5002

# Terminal 3
python order-service/app.py     # http://localhost:5003

# Terminal 4
python payment-service/app.py   # http://localhost:5004
```

### Health checks

```bash
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5004/health
```

Example response:

```json
{ "service": "user-service", "status": "healthy" }
```

### API endpoints

```bash
curl http://localhost:5001/users
curl http://localhost:5002/products
curl http://localhost:5003/orders
curl http://localhost:5003/orders/1/details   # Calls all other services
curl http://localhost:5004/payments
```

---

## Part 2 — Docker and Docker Compose

### Prerequisites

- Docker Desktop (or Docker Engine)
- Docker Compose v2

### Build images

```bash
docker build -t user-service:latest    ./user-service
docker build -t product-service:latest ./product-service
docker build -t order-service:latest   ./order-service
docker build -t payment-service:latest ./payment-service
docker build -t api-gateway:latest     ./api-gateway
```

All Python images use `python:3.13-slim` with `apt-get upgrade` for OS-level security patches.

### Run with Docker Compose

```bash
docker compose up
```

This starts all five containers on a shared `cloud-native-network` bridge network.
All containers have Docker health checks. Wait for all services to report `healthy`:

```bash
docker compose ps
```

| Container | Port | Image tag |
|---|---|---|
| user-service-container | 5001 | user-service:1.1 |
| product-service-container | 5002 | product-service:1.1 |
| order-service-container | 5003 | order-service:1.2 |
| payment-service-container | 5004 | payment-service:1.1 |
| api-gateway-container | 8080 | api-gateway:1.0 |

Test via the API gateway:

```bash
curl http://localhost:8080/users
curl http://localhost:8080/products
curl http://localhost:8080/orders
curl http://localhost:8080/payments
```

### NGINX API Gateway

The gateway (`api-gateway/nginx.conf`) proxies requests by path prefix to the upstream
service DNS names (resolvable inside the Docker network / Kubernetes cluster):

```nginx
location /users    { proxy_pass http://user-service:5001; }
location /products { proxy_pass http://product-service:5002; }
location /orders   { proxy_pass http://order-service:5003; }
location /payments { proxy_pass http://payment-service:5004; }
location /stub_status { stub_status; }   # Scraped by nginx-prometheus-exporter
```

---

## Part 3 — CI/CD Pipeline

### Overview

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs on every push and pull
request to `main`. It has two jobs:

| Job | Trigger | Steps |
|---|---|---|
| `test` | push + PR | Install deps → `py_compile` all services |
| `docker-build` | push to main only | AWS OIDC auth → ECR login → Build images → Trivy scan → Push to ECR → Update GitOps tags |

### AWS authentication (OIDC)

The pipeline authenticates to AWS using GitHub's OIDC provider — no long-lived access
keys are stored as secrets. The IAM role
`arn:aws:iam::847283080148:role/cloud-native-devops-github-actions` is configured to
trust the GitHub Actions OIDC issuer for the `sam6611/cloud-native-devops` repository.

### Security scanning

[Trivy](https://github.com/aquasecurity/trivy-action) scans every image for HIGH and
CRITICAL vulnerabilities. The scan:

- Covers `os` and `library` vulnerability types.
- Ignores unfixed vulnerabilities (packages where no patched version exists yet).
- Skips pip's internal `bom.cdx.json` metadata file to avoid false positives.
- Fails the build (`exit-code: 1`) on any remaining HIGH/CRITICAL finding.

### ECR image tagging

Images are tagged with the full Git commit SHA:

```
847283080148.dkr.ecr.ap-south-1.amazonaws.com/cloud-native-devops/<service>:<sha>
```

### GitOps update step

After pushing images, the pipeline:

1. Checks out `sam6611/cloud-native-devops-gitops` using the `GITOPS_TOKEN` secret.
2. Uses `sed` to replace the image tag in each deployment YAML with the new commit SHA.
3. Commits and pushes the change as `github-actions[bot]`.

Argo CD then detects the change and rolls out the new image to the cluster.

### Required GitHub secrets

| Secret | Description |
|---|---|
| `GITOPS_TOKEN` | Personal access token (or fine-grained token) with write access to `cloud-native-devops-gitops` |

The AWS IAM role is assumed via OIDC — no `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY`
secrets are required.

---

## Part 4 — AWS Infrastructure with Terraform

### Resources provisioned

| Resource | Details |
|---|---|
| VPC | `10.0.0.0/16`, DNS enabled |
| Public subnets | `10.0.1.0/24` (ap-south-1a), `10.0.2.0/24` (ap-south-1b) |
| Private subnets | `10.0.11.0/24` (ap-south-1a), `10.0.12.0/24` (ap-south-1b) |
| Internet Gateway | Attached to VPC |
| Route tables | Public (IGW default route) + Private |
| Security groups | Cluster + node communication |
| ECR repositories | 5 repos (`user-service`, `product-service`, `order-service`, `payment-service`, `api-gateway`) |
| EKS cluster | `cloud-native-devops-cluster`, Kubernetes v1.33 |
| IAM roles | `eks_cluster` + `eks_node` with managed policy attachments |
| Managed node group | `t3.small`, ON_DEMAND, 1–2 nodes (public subnets) |

### Remote state

Terraform state is stored in S3 (with S3-native locking):

```hcl
backend "s3" {
  bucket       = "cloud-native-devops-tfstate-847283080148"
  key          = "cloud-native-devops/terraform.tfstate"
  region       = "ap-south-1"
  encrypt      = true
  use_lockfile = true
}
```

> **Note:** The S3 bucket must exist before running `terraform init`. Create it manually
> or with a separate bootstrap script if recreating from scratch.

### Deploy / recreate infrastructure

> **Cost warning:** EKS clusters, NAT Gateways, and EC2 nodes incur ongoing AWS charges.
> Always destroy the cluster when not in use.

```bash
cd terraform

# Initialise (downloads providers, connects to S3 backend)
terraform init

# Preview changes
terraform plan

# Apply — requires valid AWS credentials with appropriate IAM permissions
terraform apply

# Configure kubectl after apply
aws eks update-kubeconfig \
  --region ap-south-1 \
  --name cloud-native-devops-cluster

# Destroy all resources when done
terraform destroy
```

### Required AWS permissions

The operator applying Terraform needs permissions to manage: VPC, EC2, EKS, ECR, IAM,
and S3. A least-privilege policy is recommended for production.

---

## Part 5 — Kubernetes and GitOps with Argo CD

### How GitOps works

```
Push to app repo → CI builds + pushes image → CI updates gitops repo tag
                                                     │
                                              Argo CD detects change
                                                     │
                                         kubectl apply to EKS cluster
```

The `cloud-native-devops-gitops` repository is the **single source of truth** for the
cluster state. Direct `kubectl apply` should only be used for one-off operational tasks
(e.g., deploying monitoring manifests). All application changes go through CI.

### Install Argo CD

```bash
kubectl create namespace argocd
kubectl apply -n argocd \
  -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# Wait for Argo CD to be ready
kubectl wait --for=condition=available deployment/argocd-server \
  -n argocd --timeout=120s

# Retrieve the initial admin password
kubectl -n argocd get secret argocd-initial-admin-secret \
  -o jsonpath='{.data.password}' | base64 -d
```

### Create the Argo CD Application

```bash
kubectl apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: cloud-native-devops
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/sam6611/cloud-native-devops-gitops.git
    targetRevision: main
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
EOF
```

### Apply ConfigMap and Secret

```bash
kubectl apply -f k8s/app-config.yaml
kubectl apply -f k8s/app-secret.yaml
```

> **Security note:** `app-secret.yaml` currently stores `API_ENV: "production"` as a
> plain `stringData` value. For production systems, use a secrets manager such as AWS
> Secrets Manager with the External Secrets Operator, or seal the secret with Sealed Secrets.

### Verify deployments

```bash
kubectl get deployments
kubectl get services
kubectl get pods

# Access via NodePort (replace <node-ip> with an EKS node's public IP)
curl http://<node-ip>:30080/users
curl http://<node-ip>:30080/health
```

### K8s resource sizing

Each Flask service container is configured with:

| Resource | Request | Limit |
|---|---|---|
| CPU | 50m | 200m |
| Memory | 64Mi | 128Mi |

The API gateway (NGINX):

| Resource | Request | Limit |
|---|---|---|
| CPU | 25m | 100m |
| Memory | 32Mi | 64Mi |

These values are sized for the `t3.small` (2 vCPU, 2 GiB) node group. Tune them after
observing actual usage in Grafana → Container CPU/Memory panels.

---

## Part 6 — Observability

### Stack components

| Component | Role |
|---|---|
| kube-prometheus-stack | Prometheus Operator, Prometheus, Grafana, Alertmanager |
| Loki stack | Log aggregation |
| nginx-prometheus-exporter | Exposes NGINX `stub_status` metrics to Prometheus |
| ServiceMonitors | Tell Prometheus which pods/ports to scrape |
| PrometheusRules | Alerting expressions and severity routing |

### Install monitoring stack (Helm)

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Install kube-prometheus-stack
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace \
  --set grafana.sidecar.dashboards.enabled=true \
  --set grafana.sidecar.dashboards.label=grafana_dashboard \
  --set grafana.sidecar.datasources.enabled=true \
  --set grafana.sidecar.datasources.label=grafana_datasource

# Install Loki
helm upgrade --install loki grafana/loki \
  --namespace monitoring \
  --set loki.auth_enabled=false

# Install Promtail (log collector)
helm upgrade --install promtail grafana/promtail \
  --namespace monitoring \
  --set config.lokiAddress=http://loki-gateway.monitoring.svc.cluster.local/loki/api/v1/push
```

### Deploy monitoring manifests

```bash
cd monitoring

# NGINX Prometheus Exporter
kubectl apply -f nginx-prometheus-exporter.yaml

# Prometheus scrape targets
kubectl apply -f servicemonitors.yaml

# Alert rules
kubectl apply -f prometheusrule-apps.yaml

# Grafana Loki datasource
kubectl apply -f grafana-datasource-loki.yaml

# Grafana dashboards
kubectl apply -f grafana-dashboard-overview.yaml
kubectl apply -f grafana-dashboard-flask.yaml
kubectl apply -f grafana-dashboard-nginx.yaml
kubectl apply -f grafana-dashboard-logs.yaml
```

### Grafana dashboards

| Dashboard | UID | Description |
|---|---|---|
| Application Overview | `app-overview` | Service health, request rate, error rate, pod CPU/memory |
| Flask Microservices | `flask-microservices` | Per-service RPS, P50/P95/P99 latency, error ratio |
| NGINX API Gateway | `nginx-api-gateway` | Gateway RPS, active connections, accepted/handled rates |
| Application Logs | `app-logs` | Loki log explorer — error logs + full log stream |

### Access Grafana

```bash
# Forward port locally
kubectl port-forward -n monitoring svc/kube-prometheus-stack-grafana 3000:80

# Default credentials (change on first login)
# Username: admin
# Password:
kubectl -n monitoring get secret kube-prometheus-stack-grafana \
  -o jsonpath='{.data.admin-password}' | base64 -d
```

Then open `http://localhost:3000`.

### Alert rules

Three alert groups are defined in `monitoring/prometheusrule-apps.yaml`:

**`nginx-alerts`**
- `NginxDown` (critical) — NGINX unreachable for > 1 minute
- `NginxHighActiveConnections` (warning) — > 100 active connections for > 5 minutes
- `NginxDroppedConnections` (warning) — accepted ≠ handled for > 5 minutes

**`flask-service-alerts`**
- `HighErrorRate` (critical) — 5xx rate > 5% for > 5 minutes
- `HighLatencyP95` (warning) — P95 latency > 1 s for > 5 minutes
- `ServiceDown` (critical) — Prometheus target unreachable for > 1 minute

**`pod-alerts`**
- `PodCrashLooping` (critical) — pod restarted in last 15 minutes
- `PodImagePullBackOff` (critical) — image pull failure

### Alertmanager notifications

Alertmanager routing is configured in `monitoring/alertmanager-config.yaml`.
See [Alertmanager Configuration](#alertmanager-configuration) below.

---

## Environment Variables and Configuration

### Flask services

| Variable | Default | Description |
|---|---|---|
| `SERVICE_NAME` | `<service>-service` | Reported in health check responses |
| `SERVICE_PORT` | `5001`–`5004` | Port the Flask app listens on |

### order-service additional variables

| Variable | Default (Docker Compose) | Description |
|---|---|---|
| `USER_SERVICE_URL` | `http://user-service-container:5001` | Upstream user-service |
| `PRODUCT_SERVICE_URL` | `http://product-service-container:5002` | Upstream product-service |
| `PAYMENT_SERVICE_URL` | `http://payment-service-container:5004` | Upstream payment-service |

In Kubernetes these are set via the `app-config` ConfigMap.

### api-gateway (Kubernetes)

| Variable | Source | Description |
|---|---|---|
| `API_ENV` | `app-secret` Secret | Deployment environment identifier |

### Safe configuration practices

- Never commit real credentials, tokens, or passwords to Git.
- Use GitHub Actions OIDC for AWS — avoid static access keys.
- Replace `app-secret.yaml` with an External Secrets Operator integration for production.
- Rotate the `GITOPS_TOKEN` secret periodically and limit its scope to the GitOps repo only.

---

## Testing and Validation

### Python syntax

```bash
python -m py_compile user-service/app.py
python -m py_compile product-service/app.py
python -m py_compile order-service/app.py
python -m py_compile payment-service/app.py
```

### YAML validation

```bash
python -c "
import yaml, os
for d in ['monitoring', '.github/workflows']:
    for f in os.listdir(d):
        if f.endswith('.yaml') or f.endswith('.yml'):
            yaml.safe_load_all(open(f'{d}/{f}'))
            print('OK:', f)
"
```

### Dashboard JSON validation

```bash
python -c "
import yaml, json
for f in ['monitoring/grafana-dashboard-flask.yaml',
          'monitoring/grafana-dashboard-nginx.yaml',
          'monitoring/grafana-dashboard-overview.yaml',
          'monitoring/grafana-dashboard-logs.yaml']:
    d = yaml.safe_load(open(f))
    for k, v in d['data'].items():
        if k.endswith('.json'):
            json.loads(v)
            print('OK:', f, '->', k)
"
```

### Docker Compose validation

```bash
docker compose config   # validates and prints the resolved configuration
```

### Terraform formatting and validation

```bash
cd terraform
terraform fmt -check    # check formatting (does NOT modify files)
terraform validate      # validate HCL syntax (requires terraform init)
```

> `terraform validate` requires `terraform init` which will try to connect to the S3
> backend. Run only when valid AWS credentials are available.

### Kubernetes manifest linting

```bash
# Install kubeval (or use kubectl --dry-run)
kubeval --strict cloud-native-devops-gitops/k8s/*.yaml

# Or use kubectl dry-run (requires cluster access)
kubectl apply --dry-run=client -f cloud-native-devops-gitops/k8s/
```

---

## Alertmanager Configuration

The file `monitoring/alertmanager-config.yaml` configures notification routing.
**Edit it to fill in your real receiver credentials before deploying.**

To deploy:

```bash
kubectl apply -f monitoring/alertmanager-config.yaml
```

Refer to the inline comments in that file for what each field means and how to verify
that alerts are being received.

---

## Troubleshooting

### Pods stuck in `ImagePullBackOff`

```bash
kubectl describe pod <pod-name>
```

Common causes:
- ECR image not pushed yet — check the CI pipeline run.
- Node does not have ECR pull permissions — verify `AmazonEC2ContainerRegistryReadOnly`
  is attached to the node IAM role.
- Image tag in the k8s manifest does not exist in ECR — check the GitOps update step.

### order-service returns 503

The `GET /orders/<id>/details` endpoint calls user-service, product-service, and
payment-service. If any upstream is down, the order-service returns `503 Service Unavailable`.

```bash
kubectl logs deploy/order-service
kubectl get endpoints user-service product-service payment-service
```

### Grafana shows "No data"

- Confirm ServiceMonitors exist: `kubectl get servicemonitors -n monitoring`
- Confirm services have the correct `app: <name>` labels: `kubectl get svc --show-labels`
- Check Prometheus targets: `kubectl port-forward -n monitoring svc/prometheus-operated 9090:9090`
  then open `http://localhost:9090/targets`.

### Loki shows no logs

- Confirm Promtail is running: `kubectl get pods -n monitoring -l app.kubernetes.io/name=promtail`
- Confirm the Loki gateway is reachable: `kubectl get svc -n monitoring | grep loki`

### Terraform backend access denied

Ensure your AWS credentials have `s3:GetObject`, `s3:PutObject`, and `s3:ListBucket`
on `cloud-native-devops-tfstate-847283080148`, and `s3:GetBucketVersioning` for locking.

---

## Cost Considerations

The following AWS resources incur ongoing charges when deployed:

| Resource | Approx. cost (ap-south-1) |
|---|---|
| EKS cluster control plane | ~$0.10/hour |
| t3.small EC2 node × 1 | ~$0.023/hour |
| ECR storage | ~$0.10/GB/month |
| S3 (Terraform state) | Negligible |

**Estimated total: ~$0.12–0.15/hour (~$90–110/month) for a single-node cluster.**

### Safely destroy all resources

```bash
cd terraform
terraform destroy   # destroys EKS, EC2, VPC, ECR, IAM (NOT the S3 bucket)
```

ECR images and the S3 Terraform state bucket are not managed by this Terraform config
and must be deleted manually if no longer needed:

```bash
# Empty and delete ECR repos
aws ecr delete-repository --repository-name cloud-native-devops/user-service --force
# ... repeat for other repos

# Empty and delete S3 state bucket (irreversible)
aws s3 rm s3://cloud-native-devops-tfstate-847283080148 --recursive
aws s3api delete-bucket --bucket cloud-native-devops-tfstate-847283080148
```

---

## Project Status

| Part | Status | Notes |
|---|---|---|
| 1 — Local microservices | ✅ Complete | All four services + health + API endpoints |
| 2 — Docker / Compose | ✅ Complete | Hardened Dockerfiles, health checks, shared network |
| 3 — CI/CD pipeline | ✅ Complete | Test → Trivy scan → ECR push → GitOps update |
| 4 — AWS / Terraform | ✅ Complete | VPC, EKS, ECR, IAM provisioned; S3 remote state |
| 5 — Kubernetes / GitOps | ✅ Complete | All manifests with probes + resource limits; Argo CD |
| 6 — Observability | ✅ Complete | Prometheus, Grafana (4 dashboards), Loki, alerts |
| Alertmanager routing | ✅ Complete | Config template with Slack + email receivers |

**AWS Infrastructure:** The EKS cluster and supporting resources may have been destroyed
to avoid ongoing costs. Use `terraform apply` in the `terraform/` directory to recreate
them. Check `terraform show` or the AWS console to verify the current state.
