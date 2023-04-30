#!/usr/bin/env python3

import traceback
from flask import Flask, jsonify


app = Flask(__name__)


@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(traceback.format_exc())
    # re-raising the error, we just want to log it
    return e


@app.route("/")
def index():
    return jsonify({"status": "ok"})


@app.route("/<name>")
def index2(name):
    return jsonify({"name": name})


if __name__ == "__main__":
    app.run(debug=True)
