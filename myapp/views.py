from django.shortcuts import render
from django.http import JsonResponse
from googleapiclient.discovery import build
import openai
import os
import google.auth

# Create your views here.

class youtuberecommender:
    def __init__(self):
        # Set up the YouTube Data API client
        api_service_name = "youtube"
        api_version = "v3"
        DEVELOPER_KEY = os.environ.get('YOUTUBE_API_KEY') # Replace with your own API key
        self.youtube = build(api_service_name, api_version, developerKey=DEVELOPER_KEY)

def search_videos(self, query=''):
        if query == '':
            query = self.query
        search_response = self.youtube.search().list(
            q=query,
            type="video",
            part="id,snippet",
            maxResults=3,
            order='rating',
        ).execute()
        return search_response.get('items', [])
        videos = {}
        for search_result in search_response.get("items", []):
            video_id = search_result["id"]["videoId"]
            video_title = search_result["snippet"]["title"]
            video_description = search_result["snippet"]["description"]
            video_tags = search_result["snippet"]["tags"] if "tags" in search_result["snippet"] else []

            videos[video_title] = {
                "video_id": video_id,
                "video_description": video_description,
                "video_tags": video_tags
            }

        return JsonResponse(videos, safe=False)

class ExecuteView(View):
    def get(self, request):
        message_history = [...] 
        goal = request.GET.get('goal', '')  
        searcher = YoutubeSearcher()

        videos = {}
        for query in message_history:
            videos.update(searcher.search_videos(query))

        return JsonResponse(videos, safe=False)
