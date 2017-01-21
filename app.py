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

#run(host='localhost', port=8080)

#run(host='verkehrsbot', port=80)
