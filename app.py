from bottle import route, run, template
import logging

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

@route('/hello/<name>')
def index(name):
	logger.info('index called.')
    return template('<b>Hello {{name}}</b>!', name=name)

#run(host='localhost', port=8080)

if __name__ == '__main__':
    run(server=srv, host='verkehrsbot.azurewebsites.de', port=80)
