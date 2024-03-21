import flask

app = flask.Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'


def run_server():
    app.run(host='0.0.0.0', port=5000, debug=True)