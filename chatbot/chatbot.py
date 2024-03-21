# This is a basic sample to use Azure OpenAI
# 3 configurations are available in the file openAI_config.json
#
# pre-requisites:
#   - pip install --upgrade openai


import os
from openai import AzureOpenAI
import json


role_text = """
You are an investment advisor for sustainable investments targeted at Gen-Z. You will probe the user step by step on the following points:
- What is your risk taking behaviour? (low, mid, high)
- How much money do you want to invest? (x chf)
- How much do you care about only investing in the best of the best companies vs not putting all of your eggs into one basket. (best, balanced, all)

You will rephrase the users answer and ascribe one of the possible values and ask to confirm. Keep yourself short in those answers


"""

reminders = """
Keep in mind the target audience is Gen-Z. Make relatable examples and keep the language simple. 
Rephrase the users answer and ascribe one of the possible values.
Formating:
- Highlight important words using bold
"""
introduction = """
introduce yourself as Turing, the investment advisor for sustainable investments. The user is a Gen-Z person who wants to invest in sustainable companies.
"""

risk_question = """
Ask about risk taking behaviour.
Context for the categories:
- risk taking:
    - low: Very risk averse, only wants the savest bets
    - mid: Somewhat risk averse, wants to be safe but is willing to take some risk
    - high: Very risk taking, willing to take big risks for big rewards
"""
money_question = """
Ask about the amount of money to invest. 
Context for the categories:
- investment amount:
    - x chf: The amount of money the user wants to invest
"""


esg_topics = ["environment", "social", "governance"]
diversification_context = """
Context for the categories:
- diversification:
    - angel: Only wants to invest in the best companies
    - balanced: Wants to invest in a balanced portfolio, prioritizing good ones.
    - all: Wants to invest in as many companies as possible to diversify
"""
diversification_questions = [f"Ask about the importance of {topic} in the investment decision. " + diversification_context for topic in esg_topics]


finish_question = """
Thank the user for their answers and tell them that you will now provide them with a personalized investment plan. Don't go into details.
"""

questions = [risk_question, money_question]
questions = questions + diversification_questions
questions.append(finish_question)

# Load config values
with open(r'openAI_config.json') as config_file:
    openAI_config = json.load(config_file)

my_config = openAI_config['openAIConfigs'][2]
# Setting up the deployment name
chatgpt_model_name = my_config['model']

def setup():

    print(f"use openAI config {my_config['configName']}")


    client = AzureOpenAI(
        api_key=my_config['apiKey'],
        api_version=my_config['apiVersion'],
        azure_endpoint=my_config['urlBase']
    )

    return client

def first_contact(client):
    response = client.chat.completions.create(
        model=chatgpt_model_name,
        messages=[
            {"role": "system", "content": role_text + reminders},
            {"role": "system", "content": introduction + questions[0] + reminders}
        ]
        ,
        max_tokens=200
    )
    response_text, response_code = parse_gpt_response(response)
    return [response_text]



def parse_gpt_response(response):
    return response.choices[0].message.content, None
def handle_user_input(client, message, last_topic_no):

    response_messages = []
    if last_topic_no == -1:
        #first contact
        return first_contact(client)


    response = client.chat.completions.create(
        model=chatgpt_model_name,
        messages=[
            {"role": "system", "content": role_text + reminders},
            {"role": "user", "content": message}
        ]
    )
    response_text, response_code = parse_gpt_response(response)
    response_messages.append(response_text)

    #proceed to next question

    next_question = questions[last_topic_no + 1] 

    response_2 = client.chat.completions.create(
        model=chatgpt_model_name,
        messages=[
            {"role": "system", "content": role_text + reminders},
            {"role":"system", "content": next_question + reminders}
        ],
        max_tokens=100
    )
    response_text_2, response_code_2 = parse_gpt_response(response_2)

    # stitch together messages
    response_messages.append(response_text_2)
            

    return response_messages


def start():
    client = setup()
    answer = first_contact(client)
    print(answer)
    return client

client = start()