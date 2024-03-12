from llama_index.core.tools import FunctionTool
import os
from contextvars import ContextVar
from lib import recommendation_system
yt_recommender = recommendation_system.youtube_recommender()
Notification_var: ContextVar[list] = ContextVar("Notifications", default=["",""])
Answer_var: ContextVar[list] = ContextVar("Answer", default=[])
Video_var: ContextVar[dict] = ContextVar("Videos", default={})


def recommend_videos(query):
    videos = Video_var.get()
    video_data = yt_recommender.youtube_searcher(query=query)
    videos.update(video_data)
    Video_var.set(videos)

    return "Sent Videos"

youtube_engine = FunctionTool.from_defaults(
    fn=recommend_videos,
    name="youtube",
    description="This is used to suggest useful youtube videos to user",
)

def notification(title,body):
    Notification_var.set([title,body])
    return "Sent Notification"


notification_engine = FunctionTool.from_defaults(
    fn=notification,
    name="notification",
    description="this tool is used to send notification to user",
)

def answer(message):
    message_list = Answer_var.get()
    message_list.append(message)
    Answer_var.set(message_list)
    return "Sent Message"

answer_engine = FunctionTool.from_defaults(
    fn=answer,
    name="answer",
    description="this tool is used to send reply message to the user",
)
