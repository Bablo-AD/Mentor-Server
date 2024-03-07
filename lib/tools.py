from llama_index.core.tools import FunctionTool
import os
from contextvars import ContextVar
Notification_var: ContextVar[list] = ContextVar("Notifications", default=["",""])
Answer_var: ContextVar[str] = ContextVar("Answer", default="")
#yt_recommender = recommendation_system.youtube_recommender()

# def recommend_videos(query):
#     try:
#         print(yt_recommender.youtube_searcher(query))
#     except:
#         pass

#     return "Recommended Videos"

# youtube_engine = FunctionTool.from_defaults(
#     fn=recommend_videos,
#     name="youtube_video_recommender",
#     description="this tool is used to recommend youtube videos to users from search query",
# )

def notification(title,body):
    Notification_var.set([title,body])
    return "Sent Notification"


notification_engine = FunctionTool.from_defaults(
    fn=notification,
    name="notification",
    description="this tool is used to send notification to user to help him",
)

def answer(message):
    Answer_var.set(message)
    return "Sent Message"

answer_engine = FunctionTool.from_defaults(
    fn=answer,
    name="answer",
    description="this tool is used to send reply messages to the user",
)
