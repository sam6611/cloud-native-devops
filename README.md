# Cloud-Native DevOps Microservices

A simple microservices application built with Python and Flask. The application is divided into four independent services, each running on its own port and providing REST APIs.

---

## Architecture

```text
                 Client
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

| Service         | Port | Responsibility          |
| --------------- | ---: | ----------------------- |
| user-service    | 5001 | Manages user data       |
| product-service | 5002 | Manages product data    |
| order-service   | 5003 | Manages customer orders |
| payment-service | 5004 | Handles payment data    |

Each service is an independent Flask application.

---

## Prerequisites

* Python 3.8+
* pip

---

## Install Dependencies

Install the dependencies for each service:

```bash
pip install -r user-service/requirements.txt
pip install -r product-service/requirements.txt
pip install -r order-service/requirements.txt
pip install -r payment-service/requirements.txt
```

Since all services currently use Flask, you can also install it directly:

```bash
pip install Flask
```

---

## Run the Services

Open **four separate terminals** from the project root.

### Terminal 1 — User Service

```bash
python user-service/app.py
```

Runs on:

```text
http://localhost:5001
```

### Terminal 2 — Product Service

```bash
python product-service/app.py
```

Runs on:

```text
http://localhost:5002
```

### Terminal 3 — Order Service

```bash
python order-service/app.py
```

Runs on:

```text
http://localhost:5003
```

### Terminal 4 — Payment Service

```bash
python payment-service/app.py
```

Runs on:

```text
http://localhost:5004
```

---

## Health Checks

Each service provides a health endpoint:

```text
GET /health
```

Test them with:

```bash
curl http://localhost:5001/health
curl http://localhost:5002/health
curl http://localhost:5003/health
curl http://localhost:5004/health
```

Example response:

```json
{
  "service": "payment-service",
  "status": "healthy"
}
```

---

## API Endpoints

### User Service

```text
GET /users
```

Example:

```bash
curl http://localhost:5001/users
```

### Product Service

```text
GET /products
```

Example:

```bash
curl http://localhost:5002/products
```

### Order Service

```text
GET /orders
```

Example:

```bash
curl http://localhost:5003/orders
```

### Payment Service

```text
GET /payments
```

Example:

```bash
curl http://localhost:5004/payments
```

---

## Project Structure

```text
cloud-native-devops/
│
├── user-service/
│   ├── app.py
│   └── requirements.txt
│
├── product-service/
│   ├── app.py
│   └── requirements.txt
│
├── order-service/
│   ├── app.py
│   └── requirements.txt
│
├── payment-service/
│   ├── app.py
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

---

## Part 1 Objective

The objective of Part 1 is to build and verify four independent microservices locally.

```text
Python + Flask
      │
      ▼
Independent Services
      │
      ├── User       :5001
      ├── Product    :5002
      ├── Order      :5003
      └── Payment    :5004
```

All services can be started and tested independently.

**Part 1 completed successfully.**
