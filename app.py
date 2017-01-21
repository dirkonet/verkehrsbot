from bottle import route, run, template

def wsgi_app(environ, start_response):
    return bottle.default_app()

def index():
	return template('<b>Index</b>')


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    httpd = make_server('verkehrsbot', 80, wsgi_app)
    httpd.serve_forever()
