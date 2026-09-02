from flask import Flask, jsonify

app = Flask(__name__)

# Hardcoded payments data
payments = [
    {"id": 1, "order_id": 1, "amount": 49.99, "status": "completed"},
    {"id": 2, "order_id": 2, "amount": 1999.98, "status": "pending"},
    {"id": 3, "order_id": 3, "amount": 399.95, "status": "completed"},
]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "payment-service", "status": "healthy"})


@app.route("/payments", methods=["GET"])
def get_payments():
    return jsonify(payments)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
