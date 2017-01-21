from bottle import route, run, template

@route('/hello/<name>')
def index(name):
    return template('<b>Hello {{name}}</b>!', name=name)

#run(host='localhost', port=8080)

if __name__ == '__main__':
    run(server=srv, host="verkehrsbot.azurewebsites.de", port=443)
