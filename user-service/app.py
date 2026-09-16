import os
from flask import Flask, jsonify

app = Flask(__name__)

# Read configuration from environment variables
SERVICE_NAME = os.getenv("SERVICE_NAME", "user-service")
SERVICE_PORT = int(os.getenv("SERVICE_PORT", "5001"))

# Hardcoded users data
users = [
    {"id": 1, "name": "Alice Johnson", "email": "alice@example.com"},
    {"id": 2, "name": "Bob Smith", "email": "bob@example.com"},
    {"id": 3, "name": "Charlie Brown", "email": "charlie@example.com"},
]


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "service": SERVICE_NAME,
        "status": "healthy"
    })


@app.route("/users", methods=["GET"])
def get_users():
    return jsonify(users)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=SERVICE_PORT)