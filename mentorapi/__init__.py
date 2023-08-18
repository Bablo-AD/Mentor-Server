from flask import Flask
from flask_restful import Api
from .message_completion import Message_Completion,Test
app = Flask(__name__)
api = Api(app)


api.add_resource(Message_Completion, '/mentor/chat')
api.add_resource(Test, '/test')

