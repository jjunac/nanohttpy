from nanohttpy import NanoHttpy


app = NanoHttpy(debug=False)


@app.get("/api/hello/{name}")
def api_hello(_, name):
    return {"message": f"Hello {name}!"}


if __name__ == "__main__":
    app.run(port=5000)
