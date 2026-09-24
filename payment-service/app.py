import os
from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Read configuration from environment variables
SERVICE_NAME=os.getenv("SERVICE_NAME", "payment-service")
SERVICE_PORT=int(os.getenv("SERVICE_PORT", "5004"))

# Hardcoded payments data
payments = [
    {"id": 1, "order_id": 1, "amount": 49.99, "status": "completed"},
    {"id": 2, "order_id": 2, "amount": 1999.98, "status": "pending"},
    {"id": 3, "order_id": 3, "amount": 399.95, "status": "completed"},
]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": SERVICE_NAME,
        "status": "healthy"
    })

@app.route("/payments", methods=["GET"])
def get_payments():
    return jsonify(payments)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVICE_PORT)
