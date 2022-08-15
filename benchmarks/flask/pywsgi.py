from gevent import monkey
monkey.patch_all()


from gevent.pywsgi import WSGIServer, LoggingLogAdapter
from werkzeug.middleware.proxy_fix import ProxyFix
from app import app


_logger = app.logger.getChild('pywsgi')
ADDRESS = '0.0.0.0'
PORT = 5000

http_server = WSGIServer((ADDRESS, PORT), ProxyFix(app, x_for=1, x_host=1, x_port=1), log=LoggingLogAdapter(_logger))

_logger.info(f"Start listening on http://{ADDRESS}:{PORT} ...")
http_server.serve_forever()
