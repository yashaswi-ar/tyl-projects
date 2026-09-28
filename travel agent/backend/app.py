from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from travel_agent import run_agent, approve_booking


app = Flask(__name__)
CORS(app)

FRONTEND_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "frontend"
)


# ---------------- FRONTEND ----------------

@app.route("/")
def home():
    return send_from_directory(
        FRONTEND_FOLDER,
        "index.html"
    )


@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(
        FRONTEND_FOLDER,
        filename
    )


# ---------------- CREATE TRAVEL PLAN ----------------

@app.route("/plan", methods=["POST"])
def create_travel_plan():

    data = request.get_json()

    try:
        goal = {
            "source": data["source"],
            "destination": data["destination"],
            "days": int(data["days"]),
            "budget": int(data["budget"]),
            "preference": data["preference"]
        }

        result = run_agent(goal)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


# ---------------- APPROVE BOOKING ----------------

@app.route("/approve", methods=["POST"])
def approve():

    data = request.get_json()

    try:
        goal = data["goal"]
        plan = data["plan"]

        result = approve_booking(
            goal,
            plan
        )

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "success": False,
            "message": str(e)
        }), 400


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    app.run(
        debug=True,
        port=5003
    )