# __import__('pysqlite3')
# import sys
# sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI,Request
from pydantic import BaseModel,Field
import firebase_admin
from firebase_admin import credentials, firestore
import openai
from lib import rag
from lib.tools import Notification_var,Answer_var,Video_var,User_var
from starlette.middleware.base import BaseHTTPMiddleware
class MessageData(BaseModel):
    apikey: str
    user_id: str
    messages: str
    message_history: str

app = FastAPI()
cred = credentials.Certificate("anti-distractor-firebase-adminsdk-lxfge-af9394634f.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
messages_collection = db.collection("users")


class ResetContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Reset the ContextVar
        Notification_var.set(["",""])
        Answer_var.set([])
        Video_var.set({})
        User_var.set({})
        # Process the request
        response = await call_next(request)
        return response

app.add_middleware(ResetContextMiddleware)

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
    User_var.set(user_data)
    model = rag.RAG(user_id,chatmemory=data.message_history)
    output=''
    try:
        output = [model.make_query(data.messages).response]
        
    except ValueError as e:
        print("error",e)
        pass
    answer = Answer_var.get()
    if answer != []:
        output=answer
    Notification = Notification_var.get()
    return {"reply":output,"notification":{"title":Notification[0],"message":Notification[1]},"message_history":model.chat_store.json(),"videos":Video_var.get()}