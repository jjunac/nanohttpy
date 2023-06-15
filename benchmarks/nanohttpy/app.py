from nanohttpy import NanoHttpy
import sys

app = NanoHttpy(debug=False)


@app.get("/api/hello/{name}")
def api_hello(_, name):
    return {"message": f"Hello {name}!"}


if __name__ == "__main__":
    engine = None
    if len(sys.argv) >= 2:
        if sys.argv[1] == "--python":
            from nanohttpy.engines import PythonEngine
            engine = PythonEngine
        elif sys.argv[1] == "--uvloop":
            from nanohttpy.engines import PythonEngine
            engine = PythonEngine
    if engine is None:
        from nanohttpy.engines import PythonEngine
        engine = PythonEngine

    app.run(port=5000, engine=engine)
