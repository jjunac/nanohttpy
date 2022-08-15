from flask import Flask, jsonify


app = Flask(__name__)


@app.route("/api/hello/<name>")
def api_hello(name):
    return jsonify(message=f"Hello {name}!")


if __name__ == "__main__":
    app.run()
