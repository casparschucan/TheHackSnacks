import flask
from flask import request, jsonify
from backend.curate_data import get_viable_funds

app = flask.Flask(__name__)


@app.route('/')
def index():
    return 'Hello, World!'


@app.route('/visons')
def visons():
    return flask.render_template('visons.html')

@app.route('/goals/<vision_data>', methods=['GET'])
def goals(vision_data):
    print(vision_data)
    
    # vision data is encoded as E,S,G
    E,S,G = vision_data.split(',')
    
    print(E)
    print(S)
    print(G)

    #TODO: pass the esg values to the backend to select goals
    #currently just maps E to CarbonFootprint
    #S to WageGap

    criteria = []
    if E == '1':
        criteria.append('CarbonFootprint')
    if S == '1':
        criteria.append('WageGap')
    if G == '1':
        pass 

    data = {
        "criteria": criteria,
    }

    return flask.render_template('goals.html', data=data)

@app.route('/chat')
def chat():
    return flask.render_template('chat.html')

@app.route('/profile')


def run_server():
    app.run(host='0.0.0.0', port=5000, debug=True)