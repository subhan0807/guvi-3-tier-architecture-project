import os
from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

DB_CONFIG = {
    "host": os.environ.get("DB_HOST", "YOUR_RDS_ENDPOINT"),
    "user": os.environ.get("DB_USER", "admin"),
    "password": os.environ.get("DB_PASSWORD", ""),
    "database": os.environ.get("DB_NAME", "feedbackdb"),
    "port": int(os.environ.get("DB_PORT", "3306")),
}

@app.route("/")
def home():
    return jsonify({"status": "Flask is running"})

@app.route("/submit", methods=["POST"])
def submit_feedback():
    data = request.get_json(silent=True) or request.form
    name = data.get("name")
    email = data.get("email")
    feedback = data.get("feedback")

    if not all([name, email, feedback]):
        return jsonify({"message": "All fields are required"}), 400

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (name, email, feedback) VALUES (%s, %s, %s)",
        (name, email, feedback),
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"message": "Feedback submitted successfully!"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

