from llama_index.core.tools import FunctionTool
import os
from contextvars import ContextVar
from llama_index.readers.youtube_transcript import YoutubeTranscriptReader
from llama_index.core import SummaryIndex
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from .recommendation_system import *

yt_recommender = youtube_recommender()
Notification_var: ContextVar[list] = ContextVar("Notifications", default=["",""])
Answer_var: ContextVar[list] = ContextVar("Answer", default=[])
Video_var: ContextVar[dict] = ContextVar("Videos", default={})
User_var: ContextVar[dict] = ContextVar("User",default={})
loader = YoutubeTranscriptReader()

# Set up the SMTP server
smtp_server = "smtp.gmail.com"
port = 587  # For starttls
username = os.environ.get('MAIL_EMAIL')
password = os.environ.get('MAIL_PASSWORD')

def recommend_videos(query,intent):
    videos = Video_var.get()
    video_data = yt_recommender.recommend_videos(query=query,intent=intent)
    videos_dict = {}
    for video in video_data.videos:
        videos_dict[video.title] = [video.video_id, video.description]
    videos.update(videos_dict)
    Video_var.set(videos)

    return "recommended"

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

def send_mail(subject,message):
    # Create a multipart message
    msg = MIMEMultipart()
    msg['From'] = username
    msg['To'] = User_var.get()['parentmail']
    msg['Subject'] = subject

    # Add your message body
    msg.attach(MIMEText(message, 'plain'))

    # Start a secure connection with the server
    server = smtplib.SMTP(smtp_server, port)
    server.starttls()

    # Log in to the server
    server.login(username, password)

    # Send the email
    server.send_message(msg)

    # Close the connection to the server
    server.quit()
    return "Sent Message to parents"

mail_engine = FunctionTool.from_defaults(
    fn=send_mail,
    name="sendmail",
    description="this tool is used to send mail to their parents about users concerns",
)
