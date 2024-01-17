from flask import Flask, request, jsonify,make_response
from flask_restful import Resource, Api
import firebase_admin
from firebase_admin import credentials, firestore
import json
import os
from dotenv import load_dotenv
from openai import OpenAI
from api.recommendation_system import youtube_recommender
import time
load_dotenv()

# Initialize Firebase Admin SDK
print(os.getcwd())
cred = credentials.Certificate("./anti-distractor-firebase-adminsdk-lxfge-af9394634f.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
messages_collection = db.collection("users")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)
yt_recommender = youtube_recommender()
class Message_Completion(Resource):

    def post(self):
        # Parse the JSON data from the request
        data = request.json

        # Check if API key and user id are present in the request
        if data.get('apikey') is None or data.get('user_id') is None:
            return jsonify({"error": "Invalid request user_id or apikey is not correct"}), 400


        # Get the user ID from the request data
        user_id = data['user_id']

        # Query Firestore to get the message corresponding to the user ID
        user_doc = messages_collection.document(user_id).get()
        if not user_doc.exists:
            return make_response(jsonify({"error": "User ID not found"}), 401)
        user_data = user_doc.to_dict()
        # Check if the API key is valid
        API_KEY = data['apikey']
        if user_data['apikey'] != API_KEY:
            return make_response(jsonify({"error": "Invalid API key"}), 401)
        
        # OpenAI assistant
        if user_data.get('thread_id') is None:
            thread = client.beta.threads.create()
            data['thread_id'] = thread.id
        thread_id = user_data['thread_id']
        message = client.beta.threads.messages.create(
                    thread_id=thread_id,
                    role="user",
                    content=data['messages'],
                )
        
        if data['assistant_model'] == 'mentor':
            assistant_id = "asst_kp023V8yl5vmyyHem5MhRaB0"
        elif data['assistant_model'] == 'mentorlite':
            assistant_id = "asst_CYh4Ek8bCbeB5xRBBx6k50q1"
        run = client.beta.threads.runs.create(
                thread_id=thread_id,
                assistant_id=assistant_id,
                 )
        run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
                )
        while True:
            run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run.status == "completed":
                break
            time.sleep(1)
        if run.status == "completed":
            messages = client.beta.threads.messages.list(thread_id=thread_id,order="desc",limit=2)
            messages = messages.data[-1].content[-1].text.value
            
            response = {"response": messages}
            for i in run.required_action.submit_tool_outputs.tool_calls:
                if i.function.name == "get_videos":
                    videos={}
                    videos = yt_recommender.youtube_searcher(videos,i.function.arguments)
                    response['videos'] = videos
                elif i.function.name == "send_notifications":
                    response['notifications'] = i.function.arguments
                
            return make_response(jsonify(response), 200)
        elif run.status == "active":
            client.beta.threads.delete(thread_id)
            return make_response(jsonify({"response": "Assistant is gone for vocation"}), 200)

class Test(Resource):
    def post(self):
        # Parse the JSON data from the request
        data = request.json

        # Check if API key and user id are present in the request
        if data.get('apikey') is None or  data.get('user_id') is None:
            return jsonify({"error": "Invalid request"}), 400
        with open('test.json','r') as file_object:
            response = json.load(file_object)
        return response,200