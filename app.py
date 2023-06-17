from flask import Flask,request
from flask_restful import Resource, Api
from data import HabiticaData
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
        print(habits)
        TODAY = datetime.today()
        helping_assistant.messages = []
        helping_assistant.load_mentorship(habits,journal,TODAY,PAST_HISTORY)
        completion = gpt_model.get_completion(helping_assistant,temperature=0.5,update_history=True)

        helping_assistant.messages = [helping_assistant.messages[-1]] # Only loading the partner advice to save some tokens
        youtube.make_query(helping_assistant,goal)
        refine_list = youtube.youtube_searcher()
        helping_assistant.messages = []
        refine_list['completion'] = completion[0]
        #refine_list['tokens_used'] = completion[1]
        
        return refine_list

class Test(Resource):
    def post(self):
        print("Testing")
        habits = request.json.get('habits')
        print(habits)
        with open('test.json','r') as file_object:  
            data = json.load(file_object)
        return data
api.add_resource(Mentor, '/mentor')
api.add_resource(Test, '/test')
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')