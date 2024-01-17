from flask import Flask, render_template, request,jsonify,session
from flask_restful import Api
from .message_completion import Message_Completion,Test
import dotenv
import os
from datetime import timedelta
from api.message_completion_legacy import Message_Completion_legacy

dotenv.load_dotenv()

app = Flask(__name__)
api = Api(app)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')


api.add_resource(Message_Completion, '/mentor/chat/dev')
api.add_resource(Test, '/test')
api.add_resource(Message_Completion_legacy,'/mentor/chat')
