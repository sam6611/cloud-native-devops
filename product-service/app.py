import os
from flask import Flask, jsonify
from prometheus_flask_instrumentator import Instrumentator

app = Flask(__name__)

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Read configuration from environment variables
SERVICE_NAME = os.getenv("SERVICE_NAME", "product-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5002"))

# Hardcoded products data
products = [
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Headphones", "price": 49.99},
    {"id": 3, "name": "Keyboard", "price": 79.99},
]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": SERVICE_NAME,
        "status": "healthy"
    })


@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(products)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVICE_PORT)
