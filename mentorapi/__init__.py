from flask import Flask
from flask_restful import Api
from .message_completion import MessageCompletion
from .message_completion import Mentor,Message,Test
app = Flask(__name__)
api = Api(app)

api.add_resource(Message_Completion, '/get_completion')
api.add_resource(Mentor, '/mentor')
api.add_resource(Message, '/mentor/messages')
api.add_resource(Test, '/test')

