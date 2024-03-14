import openai
import os
import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
from llama_index.readers.youtube_transcript import YoutubeTranscriptReader
from llama_index.agent.openai import OpenAIAgent
from llama_index.llms.openai import OpenAI
from llama_index.core.query_pipeline import QueryPipeline
from llama_index.core import PromptTemplate
loader = YoutubeTranscriptReader()
from typing import List
from pydantic import BaseModel, Field
from llama_index.core.output_parsers import PydanticOutputParser
import json

class Video(BaseModel):
    """Object representing a single movie."""

    title: str = Field(..., description="Name of the video.")
    video_id: str = Field(..., description="id of the video.")
    description: str = Field(...,description="Description of the video.")

class Videos(BaseModel):
  videos:List[Video]=Field(..., description="List of videos.")

llm = OpenAI(model="gpt-3.5-turbo")
output_parser = PydanticOutputParser(Videos)
youtube_llm="""Hey you are a subpart of a Mentor a virtual productivity assistant. Your role is to suggest videos to users from the json that align with the intent and query. Only provide the videos that give value and worth the time spending if the video is not that good you can ignore it Query:{query} Intent:{intent} Videos:{videos}  Output with the following JSON format: """
youtube_llm = output_parser.format(youtube_llm)
json_prompt_tmpl = PromptTemplate(youtube_llm)
p = QueryPipeline(chain=[json_prompt_tmpl, llm, output_parser], verbose=True)

class youtube_recommender:
  def __init__(self):
    # Set up the YouTube Data API client\
    api_service_name = "youtube"
    api_version = "v3"
    DEVELOPER_KEY = os.environ.get('YOUTUBE_API_KEY') # Replace with your own API key
    self.youtube = build(api_service_name, api_version, developerKey=DEVELOPER_KEY)
    llm = OpenAI(model="gpt-3.5-turbo")
    self.agent = OpenAIAgent.from_llm(llm=llm)



  def youtube_searcher(self,query,videos={}):
    
    search_response = self.youtube.search().list(
    q=query,
    type="video",
    part="id,snippet",
    maxResults=10,
    order='relevance',
    safeSearch='strict',
    videoEmbeddable='true',
    videoDuration='medium'
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
    videos = {}
    for i in self.query:
      self.youtube_searcher(videos,query=i)
    return videos
  
  def recommend_videos(self,query,intent):
      #ideos = Video_var.get()
      video_data = self.youtube_searcher(query=query)
      
      output = p.run(query=query,intent=intent,videos=json.dumps(video_data))
      # self.agent.query(youtube_llm+f" Query:{query}, Intent:{intent}, Videos:{video_data}")
      # for key,value in video_data.items():
      #     try:
      #         documents = loader.load_data(ytlinks=[f"https://www.youtube.com/watch?v={value[0]}"])
      #     except:
      #         del video_data[key]
      #         continue
      #     index = SummaryIndex.from_documents(documents)
      #     query_engine = index.as_query_engine(response_mode="simple_summarize")
      #     response = query_engine.query("Give the summary of the video")
      #     print(key,response)
      # video_data[key].append(response)
      # videos.update(video_data)
      #Video_var.set(videos)

      return output