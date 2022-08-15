# NanoHttpy

NanoHttpy is an ultra lightweight web framework written in Python. It features Flask/FastAPI-like API to avoid learning
yet another web framework, with minimal memory footprint.


## Features

**API**
 - [X] Handling of HTTP methods
   - [X] With FastAPI-like API: `@app.get(...)`, `@app.post(...)`
   - [X] With Flask-like API: `@app.route(...)`
 - [X] Reply with different HTTP status code, headers, etc... 
 - [X] Automatic content type detection in response
   - [X] Plain text
   - [X] JSON
   - [ ] File
 - [X] Path parameters
   - [X] Make them available as function parameter
   - [X] With FastAPI-like API: `"/hello/{name}"`
   - [X] With Flask-like API: `"/hello/<name>"`
 - [X] Query parameters
   - [X] Make them available as function parameter
 - [X] Body
   - [ ] Automatic conversion to ... ?
 - [ ] Redirection when multiple path ? Case insensitive matching ? (see [Go's httprouter](https://github.com/julienschmidt/httprouter))
 - [ ] Plugins
   - [ ] Jinja

**Internals**
 - [ ] Differrent engines
   - [ ] Asyncio
   - [ ] Gevent


## Installation

_TODO_


## Quick start

_TODO_


## Benchmarks

```
System information:
OS:  Darwin 12.5 Kernel Darwin 21.6.0 x86_64
CPU: 4 X Intel(R) Core(TM) i5-1038NG7 CPU @ 2.00GHz
RAM: 16 GB

fastapi           2409.397 req/s    0.415 ms/req    RSS: 28.031 MB
flask              205.795 req/s    4.859 ms/req    RSS: 24.492 MB
flask-gunicorn     201.399 req/s    4.965 ms/req    RSS: 28.941 MB
flask-gevent      2717.459 req/s    0.367 ms/req    RSS: 36.168 MB
nanohttpy          200.396 req/s    4.990 ms/req    RSS: 15.914 MB
starlette         3116.733 req/s    0.320 ms/req    RSS: 21.504 MB
```

:information_source: starlette, fastapi (based on starlette) and flask-gevent all use coroutines, either through
[uvloop](https://github.com/MagicStack/uvloop) or [gevent](http://www.gevent.org/), which makes the results not really
comparable with NanoHTTPy (at least until a coroutine based Engine is implemented).

See [benchmarks](benchmarks) for more details.


## Contributing

_TODO_

## Authors

 * **Jeremy Junac** - [jjunac](https://github.com/jjunac)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details


