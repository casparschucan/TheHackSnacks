import flask
from flask import request, jsonify
from backend.curate_data import generate_portfolio, get_viable_funds
import copy
import json
from flask import session
import uuid

import chatbot.chatbot as chatbot

app = flask.Flask(__name__)

@app.route('/media/<path:path>')
def send_media(path):
    return flask.send_from_directory('media', path)
@app.route('/static/<path:path>')
def send_static(path):
    return flask.send_from_directory('static', path)

@app.route('/')
def index():
    return flask.render_template('index.html')

@app.route('/visions')
def visons():
    return flask.render_template('visions.html')

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
        criteria.append('GreenSpace')
        pass

    serve_goals =  [
                {
                    "name": "CarbonFootprint",
                    "image_path": "../media/coin7.png",
                    "title": "I want to Help",
                    "description1": "Reducing Carbon",
                    "description2": "Emissions to Combat Climate Change",
                },
                {
                    "name": "WageGap",
                    "image_path": "../media/coin8.png",
                    "title": "I want to Help",
                    "description1": "Supporting the",
                    "description2": "Elimination of Gender Wage Gap",
                },
                {
                    "name": "GreenSpace",
                    "image_path": "../media/coin4.png",
                    "title": "I want to Help",
                    "description1": "Planting Trees to",
                    "description2": "Restore Green Space",
                }
            ]
    not_serve_goals = copy.deepcopy(serve_goals) #copy
    #filter the serve goals
    serve_goals = [goal for goal in serve_goals if goal['name'] in criteria]
    not_serve_goals = [goal for goal in not_serve_goals if goal['name'] not in criteria]
    data = {
        "criteria": criteria,
        "goals": serve_goals,
        "not_goals": not_serve_goals
    }
    print(not_serve_goals)

    return flask.render_template('goals.html', data=data)

@app.route('/forms')
def form():
    return flask.render_template('forms.html')

# @app.route('/api/investment-preferences/', methods=['POST'])
# def investment_preferences():
#     pref_json = request.get_json()
#     investment = pref_json['investment']
#     risk = pref_json['risk']
#     env = pref_json['env']
#     social = pref_json['social']
#     governance = pref_json['governance']

#     # Process data (example: print to console)
#     print(f"Investment amount: ${investment}")
#     print(f"Risk tolerance: {risk}")
#     print(f"Importance of Environmental Investing: {env}")
#     print(f"Importance of Social Investing: {social}")
#     print(f"Importance of Governance Investing: {governance}")

#     # You can further process the data here (e.g., database storage, calculations)

#     # Return a response (example: confirmation message)    
#     resp = jsonify({"message": "Investment preferences received!"})
#     resp.set_cookie("preferences", [env, social, governance])
#     return jsonify({"message": "Investment preferences received!"})

@app.route('/chat')
def chat():
    return flask.render_template('chat.html')

@app.route('/api/chat_message/', methods=['POST'])
def chat_message():
    #TODO: parse string to json
    data = request.get_json()
    #read data from post
    message = data['message']
    session_id = data['session_id']
    first_message = data['first_message']



    if session_id is None:
        #setup session id
        # set to random id
        session_id = str(uuid.uuid4())


    print(message)
    print(session_id)
    print(first_message)
    
    #client = chatbot.setup()

    question = chatbot.handle_user_message(session_id, message, first_message)

    # setup return dict
    return_dict = {
        "message": question,
        "session_id": session_id
    }

    return return_dict
@app.route('/ai')
def ai():
    return flask.render_template('ai.html')

@app.route('/profile')
def profile():
    return flask.render_template('profile.html')

@app.route('/overview/', methods=['POST', 'GET'])
def overview():

    if request.method == 'POST':
        raw_input_data = request.form
        print(raw_input_data)
    if request.method == 'GET':
        raw_input_data = request.cookies.get('userFields')
        raw_input_data = json.loads(raw_input_data)
        # parse list to dict
        raw_dict = {}
        for elem in raw_input_data:
            raw_dict[elem['id']] = elem['value']
        raw_input_data = raw_dict 
        print(raw_input_data)

    value = raw_input_data['investment']

    #high, mid, low to int
    parse_dict = {
        'high': 1,
        'medium': 0,
        'low':-1 
    }

    #parse value from 
    value = int(value)
    criteria = dict()
    visions = request.cookies.get('visions') #social governance environ 
    visions = visions.split(',')
    if visions[2] == '1':
        criteria['CarbonFootprint'] = parse_dict[raw_input_data['env']]
    if visions[0] == '1':
        criteria['WageGap'] = parse_dict[raw_input_data['social']]
    if visions[1] == '1':
        criteria['BoardDiversity'] = parse_dict[raw_input_data['governance']]

    print(visions)
    funfacts, plots, portfolio = generate_portfolio(criteria, value)

    data = {
            "goals": [
                {
                    "name": "CarbonFootprint",
                    "image_path": "../media/coin7.png",
                    "title": "I want to Help",
                    "description1": "Reducing Carbon",
                    "description2": "Emissions to Combat Climate Change",
                    "funfact": funfacts.get('CarbonFootprint',''),
                    "plot": plots.get('CarbonFootprint', '')
                },
                {
                    "name": "WageGap",
                    "image_path": "../media/coin8.png",
                    "title": "I want to Help",
                    "description1": "Reducing Wage Gap",
                    "funfact": funfacts.get('WageGap',''),
                    "plot": plots.get('WageGap', '')
                },
                {
                    "name": "BoardDiversity",
                    "image_path": "../media/coin4.png",
                    "title": "I want to Help",
                    "description1": "Increasing Board Diversity",
                    "funfact": funfacts.get('BoardDiversity',''),
                    "plot": plots.get('BoardDiversity','')
                }
                
            ],
        }
    
    return flask.render_template('overview.html', data=data)



def run_server():
    app.run(host='0.0.0.0', port=5000, debug=True)
