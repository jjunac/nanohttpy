from fastapi import FastAPI


app = FastAPI()


@app.get("/api/hello/{name}")
async def api_hello(name):
    return {"message": f"Hello {name}!"}
