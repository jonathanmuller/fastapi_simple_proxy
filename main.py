import urllib.parse
import fastapi
import requests
import uvicorn
from fastapi import Request, Response

app = fastapi.FastAPI()

base_url = "/my_proxy/"
base_port = 8000
redirect_to_url = "https://www.apple.com"
redirect_to_port = 443


@app.head(base_url)
@app.head(base_url + '{path:path}')
@app.patch(base_url)
@app.patch(base_url + '{path:path}')
@app.put(base_url)
@app.put(base_url + '{path:path}')
@app.delete(base_url)
@app.delete(base_url + '{path:path}')
@app.post(base_url)
@app.post(base_url + '{path:path}')
@app.get(base_url)
@app.get(base_url + '{path:path}')
async def proxy(request: Request, path=""):
    new_url = urllib.parse.unquote(f"{redirect_to_url}:{redirect_to_port}/{path}")
    print(new_url)

    data = await request.body()
    match request.method:
        case "GET" | "POST" | "DELETE" | "PUT" | "PATCH" | "HEAD":
            requests_method = getattr(requests, request.method.lower())

            res = requests_method(new_url, params=dict(request.query_params), data=data, headers=request.headers, cookies=request.cookies)
        case _:
            raise NotImplementedError(request.method)

    dict_headers = {}
    for element in res.headers:
        if element not in ["content-length", "content-encoding"]:
            dict_headers[element] = res.headers[element]
    print(f"Redirected {path} -> {new_url}")

    return Response(content=res.content, status_code=res.status_code, headers=dict_headers)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=base_port)
