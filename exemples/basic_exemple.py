#!/usr/bin/env python3

import inspect
from nanohttpy import NanoHttpy
from nanohttpy.requests import Request


app = NanoHttpy(debug=True)


@app.get("/")
def index():
    return f"{inspect.stack()[0][3]}"


@app.get("/status")
def status():
    return {"status": "ok"}


@app.get("/hello")
def hello_name(req: Request):
    return f"{inspect.stack()[0][3]}: hello"


@app.get("/hello-qs")
def hello_name_qs(req: Request, name):
    return f"{inspect.stack()[0][3]}: hello {name}"


@app.get("/hello/{name}")
def hello_name(req: Request, name):
    return f"{inspect.stack()[0][3]}: hello {name}"


@app.get("/hello/{name}/{lastname}")
def hello_name_surname(req: Request, name, lastname):
    return f"{inspect.stack()[0][3]}: hello {name} {lastname}"


if __name__ == "__main__":
    app.run(port=5000)
