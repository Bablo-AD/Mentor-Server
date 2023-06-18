from flask import Flask,request
from flask_restful import Resource, Api
import recommendation_system
from brain import message_history, brain_api
from datetime import datetime,timedelta
from dotenv import load_dotenv
import os
import json

load_dotenv()

PAST_HISTORY = 3
GKEEP_LABEL = "Journal"
openai_api_key = os.environ.get('OPENAI_API_KEY')

helping_assistant = message_history()
gpt_model = brain_api(openai_api_key)
youtube = recommendation_system.youtube_recommender(gpt_model)

app = Flask(__name__)
api = Api(app)


class Mentor(Resource):
    def post(self):
        # Retrieve data from the request
        habits = request.json.get('habits')
        journal = request.json.get('journal')
        goal = request.json.get('goal')
        phone_usage = request.json.get('usage')
        usergoal = request.json.get('usergoal')
        selfperception = request.json.get('selfperception')

        # Mentor Stuff
        TODAY = datetime.today()
        helping_assistant.messages = []
        helping_assistant.load_mentorship(habits,journal,phone_usage,TODAY,PAST_HISTORY)
        if selfperception != '' and  usergoal != '':
            helping_assistant.add_system(f'Hey this is what the user thinks of himself {selfperception} and this is his goal or ambition {usergoal}')
        completion = gpt_model.get_completion(helping_assistant,temperature=0.5,update_history=True)

        # Recommendation Stuff
        refine_list = {}
        helping_assistant.messages = [helping_assistant.messages[-1]] # Only loading the partner advice to save some tokens
        refine_list['videos'] = youtube.execute(helping_assistant,goal)
        helping_assistant.messages = []
        refine_list['completion'] = completion[0]
        refine_list['tokens_used'] = completion[1]
        
        # with open('test.json','w') as file_object:  
        #     json.dump(refine_list,file_object)
        return refine_list
class Message(Resource):
    def post(self):
        
        output_json = {}
        messages = request.json.get('messages')
        chat_model = brain_api(openai_api_key)
        chat_msg = message_history()
        chat_msg.messages = messages
        model_output = chat_model.get_completion(chat_msg)
        output_json['completion'] = model_output[0]
        return output_json
class Test(Resource):
    def post(self):
        print("Testing")
        habits = request.json.get('habits')
        journal = request.json.get('journal')
        goal = request.json.get('goal')
        phone_usage = request.json.get('usage')
        with open('test.json','r') as file_object:  
            data = json.load(file_object)
        return data

api.add_resource(Mentor, '/mentor')
api.add_resource(Message, '/mentor/messages')
api.add_resource(Test, '/test')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')