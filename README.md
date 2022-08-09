# NanoHttpy

NanoHttpy is an ultra lightweight web framework written in Python. It features Flask/FastAPI-like API to avoid learning
yet another web framework, with minimal memory footprint.


## Features

:warning: _Work in progress, it doesn't support all the features of a web framework yet_

**API**
 - [X] Handling of HTTP methods
   - [X] With FastAPI-like API: `@app.get(...)`, `@app.post(...)`
   - [ ] With Flask-like API: `@app.route(...)`
 - [X] Reply with different HTTP status code, headers, etc... 
 - [X] Automatic content type detection in response
   - [X] Plain text
   - [X] JSON
   - [ ] File
 - [X] Path parameters
   - [ ] Make them available as function parameter
   - [X] With FastAPI-like API: `"/hello/{name}"`
   - [ ] With Flask-like API: `"/hello/<name>"`
 - [X] Query parameters
   - [ ] Make them available as function parameter
 - [X] Body
   - [ ] Automatic conversion to ... ?
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

_TODO_


## Contributing

_TODO_

## Authors

 * **Jeremy Junac** - [jjunac](https://github.com/jjunac)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details


