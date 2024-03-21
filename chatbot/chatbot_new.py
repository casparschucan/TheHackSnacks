import os
from openai import AzureOpenAI
import json


role_text = """
You are an investment advisor for sustainable investments targeted at Gen-Z. You will probe the user step by step on the following points:
- What is your risk taking behaviour? (low, mid, high)
- How much money do you want to invest? (x chf)
- Are you a saint, a normie or a homo economicus. That is do you value only sustainability, a mix, or mostly profits. 

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
    - saint: Only wants to invest in the best companies
    - normie: Wants to invest in a balanced portfolio
    - homo economicus: Wants to invest in a lucrative portfolio
"""
diversification_questions = [f"Ask about the importance of {topic} in the investment decision. " + diversification_context for topic in esg_topics]


finish_question = """
Thank the user for their answers and tell them that you will now provide them with a personalized investment plan. Don't go into details.
"""

questions = [risk_question, money_question]
questions = questions + diversification_questions
questions.append(finish_question)



good_answer_judge_role = """
Your job is to check if the assistant should continue asking new questions. For this you need to figure out if the conversation has reached its natural end.
For this output a binary number 0 for not yet done and 1 for the conversation is done.
Do not output anything else than 0 or 1
Format:
0 or 1
"""


with open(r'openAI_config.json') as config_file:
    openAI_config = json.load(config_file)

my_config = openAI_config['openAIConfigs'][2]
# Setting up the deployment name
chatgpt_model_name = my_config['model']


def setup():
    # Load config values

    print(f"use openAI config {my_config['configName']}")


    client = AzureOpenAI(
        api_key=my_config['apiKey'],
        api_version=my_config['apiVersion'],
        azure_endpoint=my_config['urlBase']
    )

    return client

def is_0or1(input):
    if input is None:
        return False
    if input == '0' or input == '1':
        return True
    return False

def handle_user_input(client, message_history, user_input, last_question_index):
    if last_question_index == -1:
        #first contact
        message_history = [
            {"role": "system", "content": role_text + reminders},
            {"role": "system", "content": introduction + questions[0] + reminders},
        ]
    else:
        message_history.append(
            {"role": "user", "content": user_input}
        )
    
        


    response = client.chat.completions.create(
        model=chatgpt_model_name,
        messages=message_history,
        max_tokens=150,
        temperature=0.7,
        stop=["\n"],
    )
    r1_content =response.choices[0].message.content

    #append the answer
    message_history.append(
        {"role": "assistant", "content": r1_content}
    )

    if last_question_index == -1:
        return [r1_content], message_history, last_question_index +1
    else:
        good_answer_result = None
        while not is_0or1(good_answer_result):
            # TODO: don't proceed if user response is bad
            # check if response makes sense:
            last_two_messages = message_history[::-2]
            last_two_messages.append(
                    {"role": "system", "content": good_answer_judge_role}
                )
            good_answer = client.chat.completions.create(
                model=chatgpt_model_name,
                messages=last_two_messages,
                max_tokens=1,
                temperature=0.0,
                stop=["\n"],
            )
            good_answer_result = good_answer.choices[0].message.content

    if good_answer_result == '1':# answer was good we can proceed
        #we assume the response is good
        # start next question
        message_history.append(
            {"role": "system", "content": questions[last_question_index+1] + reminders}
        )

        response_2 = client.chat.completions.create(
            model=chatgpt_model_name,
            messages=message_history,
            max_tokens=150,
            temperature=0.7,
            stop=["\n"],
        )
        r2_content = response_2.choices[0].message.content

        #append the answer
        message_history.append(
            {"role": "assistant", "content": r2_content}
        )




        return [r1_content, r2_content], message_history, last_question_index + 1
    else:
        # TODO
        return [r1_content], message_history, last_question_index 


client = setup()
message_history = []
res, message_history, lq = handle_user_input(client, message_history, "", -1)
print(res)

# res, message_history, lq = handle_user_input(client, message_history, "low", lq)
# print("low")
# print(res)



# res, message_history, lq = handle_user_input(client, message_history, "1000 chf", lq)
# print("1000 chf")
# print(res)

# res, message_history, lq = handle_user_input(client, message_history, "I'm very eco concious", lq)
# print("I'm very eco concious")
# print(res)

# res, message_history, lq = handle_user_input(client, message_history, "Social issues leave me cold", lq)
# print("Social issues leave me cold")
# print(res)

# res, message_history, lq = handle_user_input(client, message_history, "Governance is kinda in the middle", lq)
# print("Governance is knda in the middle")

# print(res)


