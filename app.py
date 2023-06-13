from flask import Flask,request
from flask_restful import Resource, Api
from data import HabiticaData,GoogleKeepData
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
        api_key = request.json.get('habitica_api_key')
        user_id = request.json.get('habitica_user_id')
        email = request.json.get('email')
        password = request.json.get('password')
        goal = request.json.get('goal')
        TODAY = datetime.today()

        habitica_data = HabiticaData(user_id, api_key)
        habitica_data.get_user_data()
        habitica_data = habitica_data.get_past_dates(TODAY, PAST_HISTORY).to_json()

        gkeep_data = GoogleKeepData(email, password)
        gkeep_notes = gkeep_data.get_notes_for_past_days(gkeep_data.get_notes(GKEEP_LABEL), TODAY, PAST_HISTORY)
        
        
        helping_assistant.messages = []
        helping_assistant.load_mentorship(habitica_data,gkeep_notes,TODAY,PAST_HISTORY)
        completion = gpt_model.get_completion(helping_assistant,temperature=0.5,update_history=True)
        
        helping_assistant.messages = [helping_assistant.messages[-1]] # Only loading the partner advice to save some tokens
        youtube.make_query(helping_assistant,goal)
        refine_list = youtube.youtube_searcher()
        helping_assistant.messages = []
        refine_list['completion'] = completion[0]
        #refine_list['tokens_used'] = completion[1]
        del habitica_data,gkeep_data
        return refine_list
class Test(Resource):
    def post(self):
        print("Testing")
        with open('test.json','r') as file_object:  
            data = json.load(file_object)
        return data
api.add_resource(Mentor, '/mentor')
api.add_resource(Test, '/test')
if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')