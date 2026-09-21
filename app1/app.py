from flask import Flask, jsonify
import os

app = Flask(__name__)

VERSION = os.getenv("APP_VERSION", "4.2.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", "production")
PAYMENT_STATUS = os.getenv("PAYMENT_STATUS", "fixed")
HEALTH_STATUS = os.getenv("HEALTH_STATUS", "healthy")


@app.route("/")
def home():
    return jsonify({
        "application": "retail-platform",
        "version": VERSION,
        "environment": ENVIRONMENT,
        "payment_status": PAYMENT_STATUS
        "feature": "customer-dashboard"
        "transaction_summary": "enabled"
    })


@app.route("/health")
def health():
    if HEALTH_STATUS != "healthy":
        return jsonify({
            "status": "unhealthy",
            "version": VERSION
        }), 500

    return jsonify({
        "status": "healthy",
        "version": VERSION
    })


@app.route("/version")
def version():
    return jsonify({
        "version": VERSION
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8081)