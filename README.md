# Cloud-Native DevOps Microservices

A cloud-native microservices application built with Python and Flask. This project demonstrates a simple microservices architecture where each service runs independently and communicates via REST APIs.

---

## Architecture

```
                 Client
                   │
                   ▼
              API Gateway
                   │
       ┌───────────┼───────────┐
       ▼           ▼           ▼
   User Service  Product    Order Service
                 Service         │
                                 ▼
                           Payment Service
```

---

## Services

| Service           | Port | Description                  |
|-------------------|------|------------------------------|
| user-service      | 5001 | Manages user data            |
| product-service   | 5002 | Manages product catalog      |
| order-service     | 5003 | Manages customer orders      |
| payment-service   | 5004 | Manages payment processing   |

---

## Prerequisites

- Python 3.8+
- pip
- Docker (for containerized deployment)

---

## Install Dependencies

Install Flask for each service:

```bash
pip install -r user-service/requirements.txt
pip install -r product-service/requirements.txt
pip install -r order-service/requirements.txt
pip install -r payment-service/requirements.txt
```

Or simply install Flask once (it covers all services):

```bash
pip install Flask
```

---

## Run Each Service

Open **four separate terminals** and run one service in each:

**Terminal 1 — User Service:**
```bash
python user-service/app.py
```

**Terminal 2 — Product Service:**
```bash
python product-service/app.py
```

**Terminal 3 — Order Service:**
```bash
python order-service/app.py
```

**Terminal 4 — Payment Service:**
```bash
python payment-service/app.py
```

---

## Test Health Endpoints

Once all services are running, verify each one is healthy:

```bash
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5004/health
```

Each should return:

```json
{
  "service": "<service-name>",
  "status": "healthy"
}
```

---

## Test API Endpoints

```bash
curl http://localhost:5001/users
curl http://localhost:5002/products
curl http://localhost:5003/orders
curl http://localhost:5004/payments
```

---

## Project Structure

```
cloud-native-devops/
│
├── user-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── product-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── order-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
├── payment-service/
│   ├── app.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .dockerignore
│
└── README.md
```

---

## Dockerization

Each microservice is containerized with its own Docker image and runs as an independent container.

### How It Works

```
Python Flask Application
        ↓
    Dockerfile
        ↓
    Docker Image
        ↓
    Docker Container
```

Each service has its own Dockerfile so that it can be built, deployed, and scaled independently — a core principle of microservices architecture.

### Docker Images

| Service         | Image Name           |
|-----------------|----------------------|
| user-service    | cloud-native-user    |
| product-service | cloud-native-product |
| order-service   | cloud-native-order   |
| payment-service | cloud-native-payment |

### Build All Images

```bash
docker build -t cloud-native-user ./user-service
docker build -t cloud-native-product ./product-service
docker build -t cloud-native-order ./order-service
docker build -t cloud-native-payment ./payment-service
```

### Run All Containers

```bash
docker run -d --name user-service -p 5001:5001 cloud-native-user
docker run -d --name product-service -p 5002:5002 cloud-native-product
docker run -d --name order-service -p 5003:5003 cloud-native-order
docker run -d --name payment-service -p 5004:5004 cloud-native-payment
```

### Port Mappings

| Container       | Host Port | Container Port |
|-----------------|-----------|----------------|
| user-service    | 5001      | 5001           |
| product-service | 5002      | 5002           |
| order-service   | 5003      | 5003           |
| payment-service | 5004      | 5004           |

### Verify Running Containers

```bash
docker ps
docker images
```

### Test Containerized APIs

```bash
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5004/health

curl http://localhost:5001/users
curl http://localhost:5002/products
curl http://localhost:5003/orders
curl http://localhost:5004/payments
```

### Useful Docker Commands

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# List images
docker images

# Stop all containers
docker stop user-service product-service order-service payment-service

# Remove all containers
docker rm user-service product-service order-service payment-service

# Remove all images
docker rmi cloud-native-user cloud-native-product cloud-native-order cloud-native-payment

# View container logs
docker logs user-service
docker logs product-service
docker logs order-service
docker logs payment-service
```
