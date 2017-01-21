from bottle import route, run, template
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

@route('/hello/<name>')
def hello(name):
	logger.info('index called.')
    return template('<b>Hello {{name}}</b>!', name=name)

def index():
	return template('<b>Index</b>')

def wsgi_app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    response_body = 'Hello World'
    yield response_body.encode()

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    httpd = make_server('localhost', 80, wsgi_app)
    httpd.serve_forever()
