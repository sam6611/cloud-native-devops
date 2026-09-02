from flask import Flask, jsonify

app = Flask(__name__)

# Hardcoded products data
products = [
    {"id": 1, "name": "Laptop", "price": 999.99},
    {"id": 2, "name": "Headphones", "price": 49.99},
    {"id": 3, "name": "Keyboard", "price": 79.99},
]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"service": "product-service", "status": "healthy"})


@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(products)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
