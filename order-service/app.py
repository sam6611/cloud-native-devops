from flask import Flask, jsonify

app = Flask(__name__)

# Hardcoded orders data
orders = [
    {"id": 1, "user_id": 1, "product_id": 2, "quantity": 1, "status": "confirmed"},
    {"id": 2, "user_id": 2, "product_id": 1, "quantity": 2, "status": "pending"},
    {"id": 3, "user_id": 3, "product_id": 3, "quantity": 5, "status": "shipped"},
]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "order-service", "status": "healthy"})


@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify(orders)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
