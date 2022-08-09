#!/usr/bin/env python3

import inspect
from nanohttpy import NanoHttpy
from nanohttpy.requests import Request


app = NanoHttpy(debug=True)


@app.get("/")
def index():
    return f"{inspect.stack()[0][3]}"


@app.get("/status")
def status(req: Request):
    return {"status": "ok"}


@app.get("/hello/{name}")
def hello_name(req: Request):
    return f"{inspect.stack()[0][3]}: hello {req.param('name')}"


@app.get("/hello/{name}/{lastname}")
def hello_name_surname(req: Request):
    return f"{inspect.stack()[0][3]}: hello {req.param('name')} {req.param('lastname')}"


if __name__ == "__main__":
    app.run(port=5000)
