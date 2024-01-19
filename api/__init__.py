from flask import Flask, render_template, request,jsonify,session
from flask_restful import Api
from .message_completion import Message_Completion,Test
import dotenv
import os
from datetime import timedelta

dotenv.load_dotenv()

app = Flask(__name__)
api = Api(app)

app.secret_key = os.environ.get('FLASK_SECRET_KEY')


api.add_resource(Message_Completion, '/mentor/chat/<string:assistant_model>')
api.add_resource(Test, '/test')

