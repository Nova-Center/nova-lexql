from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import json
import os
from lexql import execute_query, load_json_file

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

default_data_path = os.path.join("data", "data.json")
if os.path.exists(default_data_path):
    load_json_file(default_data_path)
    with open(default_data_path, "r") as f:
        default_data = json.load(f)
else:
    default_data = {}


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/execute", methods=["POST"])
def execute():
    data = request.json
    query = data.get("query", "")

    try:
        queries = [q.strip() for q in query.split(";") if q.strip()]
        results = []

        for single_query in queries:
            if not single_query.endswith(";"):
                single_query += ";"
            result = execute_query(single_query)
            results.append({"query": single_query, "result": result})

        return jsonify({"success": True, "results": results})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/api/data")
def get_data():
    return jsonify(default_data)


if __name__ == "__main__":
    app.run(debug=True)
