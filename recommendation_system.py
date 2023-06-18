import openai
import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from brain import brain_api,message_history

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