import os
import requests
from flask import Flask, jsonify
from prometheus_flask_instrumentator import Instrumentator

app = Flask(__name__)

# Initialize Prometheus metrics
Instrumentator().instrument(app).expose(app)

# Service configuration
SERVICE_NAME = os.getenv("SERVICE_NAME", "order-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5003"))

USER_SERVICE_URL = os.getenv(
    "USER_SERVICE_URL",
    "http://user-service-container:5001"
)

PRODUCT_SERVICE_URL = os.getenv(
    "PRODUCT_SERVICE_URL",
    "http://product-service-container:5002"
)

PAYMENT_SERVICE_URL = os.getenv(
    "PAYMENT_SERVICE_URL",
    "http://payment-service-container:5004"
)

# Hardcoded orders data
orders = [
    {"id": 1, "user_id": 1, "product_id": 2, "quantity": 1, "status": "confirmed"},
    {"id": 2, "user_id": 2, "product_id": 1, "quantity": 2, "status": "pending"},
    {"id": 3, "user_id": 3, "product_id": 3, "quantity": 5, "status": "shipped"},
]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": SERVICE_NAME,
        "status": "healthy"
    })


@app.route("/orders", methods=["GET"])
def get_orders():
    return jsonify(orders)


@app.route("/orders/<int:order_id>/details", methods=["GET"])
def get_order_details(order_id):

    # Find the order
    order = next(
        (order for order in orders if order["id"] == order_id),
        None
    )

    if order is None:
        return jsonify({"error": "Order not found"}), 404

    try:
        # Get users
        users_response = requests.get(
            f"{USER_SERVICE_URL}/users",
            timeout=3
        )
        users_response.raise_for_status()
        users = users_response.json()

        # Get products
        products_response = requests.get(
            f"{PRODUCT_SERVICE_URL}/products",
            timeout=3
        )
        products_response.raise_for_status()
        products = products_response.json()

        # Get payments
        payments_response = requests.get(
            f"{PAYMENT_SERVICE_URL}/payments",
            timeout=3
        )
        payments_response.raise_for_status()
        payments = payments_response.json()

        # Find related user
        user = next(
            (user for user in users if user["id"] == order["user_id"]),
            None
        )

        # Find related product
        product = next(
            (product for product in products if product["id"] == order["product_id"]),
            None
        )

        # Find related payment
        payment = next(
            (payment for payment in payments if payment["order_id"] == order["id"]),
            None
        )

        return jsonify({
            "order": order,
            "user": user,
            "product": product,
            "payment": payment
        })

    except requests.RequestException as e:
        return jsonify({
            "error": "Failed to communicate with another service",
            "details": str(e)
        }), 503


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=SERVICE_PORT
    )