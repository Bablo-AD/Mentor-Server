import openai
import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from brain import brain_api,message_history

from flask import Flask,request
from flask_restful import Resource, Api
import recommendation_system
from datetime import datetime,timedelta
from dotenv import load_dotenv
import json

load_dotenv()

PAST_HISTORY = 1
openai_api_key = os.environ.get('OPENAI_API_KEY')

helping_assistant = message_history()
gpt_model = brain_api(openai_api_key)
youtube = recommendation_system.youtube_recommender(gpt_model)

class youtube_recommender:
  def __init__(self,gpt_model):
    # Set up the YouTube Data API client
    self.temperature = 0.3
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.environ.get('YOUTUBE_API_KEY') # Replace with your own API key
    self.youtube = build(api_service_name, api_version, developerKey=DEVELOPER_KEY)
    self.gpt_model = gpt_model

  # Makes query
  def make_query(self,message_history,goal=''):
    message_history.load_python_fear()
    message_history.load_query(goal)
    self.gpt_model.get_completion(message_history,temperature=self.temperature,update_history=True)
    self.query = re.findall(r'"([^"]*)"', message_history.messages[-1]['content'])
    return self.query

  def youtube_searcher(self,videos,query=''):
    if query == '':
      query = self.query
    search_response = self.youtube.search().list(
    q=query,
    type="video",
    part="id,snippet",
    maxResults=5,
    order='rating',
    ).execute()
    
    for search_result in search_response.get("items", []):
        video_id = search_result["id"]["videoId"]
        video_title = search_result["snippet"]["title"]
        video_description = search_result["snippet"]["description"]
        video_tags = search_result["snippet"]["tags"] if "tags" in search_result["snippet"] else []
 
        videos[video_title] = [video_id,video_description]
    self.youtube_videos = videos
    return self.youtube_videos


  def execute(self,message_history,goal=''):
    self.make_query(message_history,goal)
    videos = {}
    for i in self.query:
      self.youtube_searcher(videos,query=i)
    return videos

 


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
        if selfperception != '' and  usergoal != '':
           helping_assistant.add_system(f'Hey this is what the user thinks of himself "{selfperception}" and this is his goal or ambition "{usergoal}"')
        
        helping_assistant.load_mentorship(habits,journal,phone_usage,TODAY,PAST_HISTORY)
      
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
