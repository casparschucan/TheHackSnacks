# This is a basic sample to use Azure OpenAI
# 3 configurations are available in the file openAI_config.json
#
# pre-requisites:
#   - pip install --upgrade openai

import os
from openai import AzureOpenAI
import json
import pandas as pd
import json


#Make role strings

#AskerGPT
role_asker = """
You are Turing, an investment advisor for sustainable investments targeted at Gen-Z under the sus.fund service. You will probe the user step-by-step on the following points:
- How much money can the user invest?
Possible evaluations: some number of CHF. When asking for this, provide several ranges for the user to choose one from. In the end you will have to convert the ranges into a single number.

The user must specify 1) their risk taking behavior and 2) their affinity for Environmental, Social, and Governance related concerns respectively.
the user must specity those values by answering in the format of a number between -1 and 1. 1 means that the user is very risk-taking or values sustainability very highly, 0 means that the user is somewhat risk-taking or values sustainability somewhat highly, and -1 means that the user is very risk-averse or values sustainability very little.

So for each of the ESG dimensions, you must be able to elicit the following:
- Does the user value only sustainability <for the particular ESG dimension>, a mix of risk-adjusted returns and sustainability, or mostly mostly risk-adjusted returns?
Possible evaluations: 1 if "Saint" (someone who is willing to sacrifice risk-adjusted returns for better sustainability outcomes), 0 if "Normie" (Someone who is somewhat willing to forego risk-adjusted return for better sustainability but still is profit-oriented), -1 if "Homo-oeconomicus" (someone who only cares about profits and is indifferent about sustainability); This is a categorical variable that must fall into the specified buckets.
And to gauge risk you must ask questions that allow you to sort users into risk-affinity buckets
- How much risk is the user willing to take?
Possible evaluations: 1 if "Risk-Taker" (someone who is willing to take significant risk for better returns), 0 if "Risk-Averse" (Someone who is somewhat willing to take risks for better returns), -1 if "Risk-Fearing" (someone who cares deeply about avoiding financial risks); This is a categorical variable that must fall into the specified buckets.

Keep in mind that the target audience is Gen-Z. Make relatable examples and keep the language simple and engaging. Directly address the user in second person and try to be sociable and likeable. Do not ask any questions that are not aimed at extracting the specified information after you have introduced yourself in the first message. Each question must be targeted to filling in the missing information but can be a creative attempt to make answeing the question easier for the user.

"""

#Before asking your first question, you must greet the user and introduce yourself as Turing from sus.fund, the first goal-based sustainable investment fund. Inform the user that you will help them identify their sustainability goals and to sus out the specific objectives they might have.

#ExtractorGPT
extractor_role = """
You are a data extraction specialist tasked with extracting data from a natural language conversation history and converting it into a structured format. You will be given a conversation history and you must return the following information in .json format:
- The user's risk-taking behavior
- The user's affinity for Environmental, Social, and Governance related concerns
- The amount of money the user wants to invest

If not all data is contained return a .json string with the following structure
{
    "extraction": "incomplete"
}

If all fields can be filled, the format of the .json file must be as follows.
{
    "risk_taking_behavior": <risk-taking behavior integer> (defaults to None),
    "esg_affinity_environmental": <environmental affinity integer> (defaults to None),
    "esg_affinity_social": <social affinity integer> (defaults to None),
    "esg_affinity_governance": <governance affinity integer> (defaults to None)
    "investment_amount": <investment amount integer> (defaults to None)
}

Legal values for the risk_taking_behavior are integer 1 to categorize someone as a "Risk-Taker", integer 0 to categorize someone as "Risk-Averse", and integer -1 to categorize someone as "Risk-Fearing".
Legal values for the esg_affinity entries are integer 1 to categorize someone as "Saint", integer 0 to categorize someone as "Normie", integer -1 to categorize someone as "Homo-oeconomicus"
Legal values for the investment amount are positive integers to represent a CHF amount (round up to nearest whole CHF if necessary). In case the user mentions a different currency, just ignore their currency wishes.

"""

extractor_role_alt = """
    You are tasked with extracting the answers of a user in a conversation with a chat bot. 
    You will evaluate what question was asked from the pool: 
        - risk_taking_behaviour
        - esg_affinity_environmental
        - esg_affinity_social
        - esg_affinity_governance
        - investment_amount
    Possible answers for the categories are:
        - risk_taking_behaviour
            - 1: risk taker
            - 0: moderate risk
            - -1: risk averse
        - 
    
    Expected output:
    {
        "question" : "risk_taking_behaviour",
        "answer" : -1
    }
"""


#extractor_role = """Just ouput a json string containing number as a key and 4 as a value"""


curr_folder = "/".join(__file__.split('/')[:-1])

#Setup and Config
with open(curr_folder + "/" + r'openAI_config.json') as config_file:
    openAI_config = json.load(config_file)

my_config = openAI_config['openAIConfigs'][2]
# Setting up the deployment name
chatgpt_model_name = my_config['model']

# Setting up the fields to be extracted TODO: do this dynamically
requested_fields = ["riskTakingBehavior", "sustainabilityTradeOff"]

# Setting up message histories for all clients
message_histories = {}

def setup():
    # Load config values

    #print(f"use openAI config {my_config['configName']}")


    client = AzureOpenAI(
        api_key=my_config['apiKey'],
        api_version=my_config['apiVersion'],
        azure_endpoint=my_config['urlBase']
    )

    return client

#Calling this bitch
client=setup()


def ask(client, session_id, data):
    """Promts gpt to ask for more information

    Args:
        client (_type_): gpt client
        session_id (_type_): unique id of user
        data (_type_): dict with the data. None marks the missig

    Returns:
        _type_: Question chat gpt wants to ask
    """    
    curr_mh = message_histories.get(session_id, [])

    curr_mh.append(
        {"role": "system", "content": make_intent(data,"ask")}
    )
    response = client.chat.completions.create(
            model=chatgpt_model_name,
            messages=curr_mh,
            max_tokens=200,
            temperature=0.7,
            #stop=["\n"],
        )
    
    text_response = response.choices[0].message.content
    message_histories[session_id].append(
        {"role": "assistant", "content": text_response}
    )

    return text_response

def make_intent(survey_data,mode):
    #Generate intent by 
    intent_str=''

    if mode=='ask':

        topics = []
        #compare survey data to requested fields
        for key,value in survey_data.items():
            if value is None:
                topics.append(key)

        intent_str += role_asker
        #intent_str += f"The topics you still need to probe are {topics}"
        pass
    elif mode=='extract':
        intent_str += extractor_role

        pass
    else:
        raise ValueError('Mode not recognized')
    return intent_str

def update_data(client,session_id,data):
    curr_mh = message_histories.get(session_id, [])

    #removes previous system message
    #curr_mh = [i for i in curr_mh if i['role']!='system']

    # get last two messages
    #curr_mh = curr_mh[-2:]

    curr_mh.append(
        {"role": "system", "content": make_intent(data,mode='extract')}
    )
    #print(curr_mh)
    response = client.chat.completions.create(
            model=chatgpt_model_name,
            messages=curr_mh,
            max_tokens=150,
            temperature=0.7,
            #stop=["\n"],
        )
    
    text_response = response.choices[0].message.content
    print(text_response)
    try:
        out=json.loads(text_response)
        # check if out contains the key extraction
        if 'extraction' in out.keys():
            return data

    except: 

        print('Response not in json format')
        print(text_response)
        #return the data as is and hope its better next time
        return data
        
    #only update the data if the value in data was none
    
    for key,value in data.items():
        if value is None:
            data[key]=out.get(key,None)

    return data

#survey_data=pd.DataFrame(columns=['E','S','G'],index=['Risk-Taking','Sustainability Tradeoff'])




def handle_user_message(session_id, message, first_message=False):
    
    survey_data = {
        "risk_taking_behavior": None,
        "esg_affinity_environmental": None,
        "esg_affinity_social": None,
        "esg_affinity_governance": None,
        "investment_amount": None
    }
    
    #check if this is the first message
    if session_id not in message_histories.keys():
        first_message = True
    if first_message:
        #TODO: FIXME
        message_histories[session_id] = []
        
        question = ask(client,session_id,survey_data)
        return question
        #TODO: create proper intent and call ask

    else:
        #Deal with the user message



        #update the data
        survey_data=update_data(client,session_id,survey_data)

        #check if the data is complete
        if is_incomplete(survey_data):
            #ask the next question
            question = ask(client,session_id,survey_data)
            return question
        else:
            #end the conversation
            print(survey_data)
            return "<END OF CONVERSATION>"




def is_incomplete(dictionary):
    for key in dictionary.keys():
        if dictionary[key] == None:
            return True
    return False
   
def loop(data):
    while is_incomplete(data):
        question = ask(client,1,'E')#TODO: get real session id
        # send the question to the user
        
        # get the response from the user
        # update the data
        # check if the data is complete
