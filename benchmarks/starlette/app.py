from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route


async def api_hello(request):
    return JSONResponse({"message": f"Hello {request.path_params['name']}!"})


app = Starlette(debug=True, routes=[
    Route("/api/hello/{name}", api_hello),
])
