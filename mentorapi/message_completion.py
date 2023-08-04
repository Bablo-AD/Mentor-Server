from flask import Flask, request, jsonify
from flask_restful import Resource, Api
import firebase_admin
from firebase_admin import credentials, firestore
import json
from prompthandler import PromptHandler
import os


# Initialize Firebase Admin SDK
cred = credentials.Certificate("./anti-distractor-firebase-adminsdk-lxfge-af9394634f.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
messages_collection = db.collection("users")

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

class Message_Completion(Resource):
   
    def post():
        # Parse the JSON data from the request
        data = request.json

        # Check if API key and user id are present in the request
        if 'apikey' not in data or 'user_id' not in data:
            return jsonify({"error": "Invalid request"}), 400

        
        # Get the user ID from the request data
        user_id = data['user_id']

        # Query Firestore to get the message corresponding to the user ID
        user_doc = messages_collection.document(user_id).get()
        if not user_doc.exists:
            return jsonify({"error": "User ID not found"}), 404
        user_data = user_doc.to_dict()
        # Check if the API key is valid
        try:
            API_KEY = user_data['apikey']
        except KeyError:
            return jsonify({"error": "Invalid API key"}), 401
        if data['apikey'] != API_KEY:
            return jsonify({"error": "Invalid API key"}), 401
        # Get the message data from the Firestore document
        message = user_data.get('messages',"{'head':[],'body':[]}")
        message = json.loads(message)
        model = PromptHandler(api_key=OPENAI_API_KEY)
        model.load(message)
        output = model.get_completion(data['messages'])
        message = json.dumps(model.dump())
        if data.get('update_history', False):
            user_data['messages'] = message
            messages_collection.document(user_id).set(user_data)
        return jsonify({"response": output}), 200

