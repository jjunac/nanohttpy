# Benchmarks

Little benchmark suite, aiming at comparing the performances of different Python frameworks.

This is greatly inspired by [Go HTTP Router Benchmark](https://github.com/julienschmidt/go-http-routing-benchmark) and 
[TechEmpower Framework Benchmarks](https://github.com/TechEmpower/FrameworkBenchmarks)

**Tested frameworks:**
 - [FastAPI](https://fastapi.tiangolo.com/)
 - [Flask](https://flask.palletsprojects.com/en/2.1.x/)
 - [NanoHTTPy](https://github.com/jjunac/nanohttpy)
 - [Starlette](https://www.starlette.io/)


## Results

### Hello JSON Api
This is a really simple benchmark. The point is to compare the performances of the different router, and returning a
JSON object based on the path parameter.

Although it seems quite disconnected from the reality, it still gives a pretty good idea of the performance differences
of the framework cores.

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


## Conclusion

Besides the coroutine based implementation, NanoHTTPy performances are very similar to the other frameworks, while
maintaining a very low memory footprint.


## How to run the benchmarks

:warning: _This is not using Docker to avoid the performance overhead on MacOS, and this has only been tested on my_
_machine (MacOS) for now. I can't guarantee that I'll work out of the box on any other machine._

### Requirements
 - [Go 1.18+](https://go.dev/)
 - [Python3](https://www.python.org/)
 - [GNU Make](https://www.gnu.org/software/make/)

:information_source: If you don't have `make` or if you're running on Windows, just run the commands you'll find in the `Makefile`.

### Installation
```bash
make install
```

### Running everything
```bash
make run
```

### Running a particular framework (or framework variant)
```bash
make <name>  # e.g. make flask-gevent
```

### Explanations
Each folder contains the implementations of the benchmark cases with a particular framework.
Then the `benchmark.yaml` is here to tell the [runner](runner) information about the framework name, how to run the
server, which port target, etc...

### Test cases

#### Hello JSON Api

|                Input                |             Expected output             |
| ----------------------------------- | --------------------------------------- |
| `GET /api/hello/<name>`             | `{"message":"Hello <name>!"}`           |


