#!/usr/bin/env python3

import inspect
from nanohttpy import Nanohttpy


app = Nanohttpy(debug=True)


@app.get("/")
def index():
    return f"{inspect.stack()[0][3]}"


@app.get("/status")
def status():
    return {"status": "ok"}


@app.get("/hello/{name}")
def hello_name(name):
    return f"{inspect.stack()[0][3]}: hello {name}"


@app.get("/hello/{name}/{lastname}")
def hello_name_surname(name, lastname):
    return f"{inspect.stack()[0][3]}: hello {name} {lastname}"


if __name__ == "__main__":
    app.run(port=5000)
