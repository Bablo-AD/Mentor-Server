from llama_index.core.tools import FunctionTool
import os
#yt_recommender = recommendation_system.youtube_recommender()



# def recommend_videos(query):
#     try:
#         print(yt_recommender.youtube_searcher(query))
#     except:
#         pass

#     return "Recommended Videos"

def notification(title,body):
    print("Notification",title,body)
    return "Sent Notification"


notification_engine = FunctionTool.from_defaults(
    fn=notification,
    name="notification",
    description="this tool is used to send notification to user to keep him motivated",
)

# youtube_engine = FunctionTool.from_defaults(
#     fn=recommend_videos,
#     name="youtube_video_recommender",
#     description="this tool is used to recommend youtube videos to users from search query",
# )
