from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
from pydantic import BaseModel,Field
import firebase_admin
from firebase_admin import credentials, firestore
import openai
from lib import rag


class MessageData(BaseModel):
    apikey: str
    user_id: str
    messages: str

app = FastAPI()
cred = credentials.Certificate("anti-distractor-firebase-adminsdk-lxfge-af9394634f.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
messages_collection = db.collection("users")



@app.post("/mentor")
async def get_model(data:MessageData):
     # Get the user ID from the request data
        user_id = data.user_id

        # Query Firestore to get the message corresponding to the user ID
        user_doc = messages_collection.document(user_id).get()
        if not user_doc.exists:
            return make_response(jsonify({"error": "User ID not found"}), 401)
        user_data = user_doc.to_dict()
        # Check if the API key is valid
        API_KEY = data.apikey
        if user_data['apikey'] != API_KEY:
            return make_response(jsonify({"error": "Invalid API key"}), 401)
        model = rag.RAG(user_id)
        output = model.make_query(data.messages)
        return {"message": output}