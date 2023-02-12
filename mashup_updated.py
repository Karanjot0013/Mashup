from pytube import YouTube
from googleapiclient.discovery import build
from pydub import AudioSegment
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
import sys

gmail = "ksingh5_be20@thapar.com"
gmailpwd = "wnwjybblnexbkzth"

def send_email(subject, body, sender, recipients, password):
    message = MIMEMultipart()
    message['Subject'] = subject
    message['From'] = sender
    message['To'] = recipients
    html_part = MIMEText(body)
    message.attach(html_part)
    
    filename = "./output/" + subject
    attachment = open(filename, "rb")
  
    # instance of MIMEBase and named as p
    p = MIMEBase('application', 'octet-stream')
    
    # To change the payload into encoded form
    p.set_payload((attachment).read())
    
    # encode into base64
    encoders.encode_base64(p)
    
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename)
    
    # attach the instance 'p' to instance 'msg'
    message.attach(p)

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    server.login(sender, password)
    server.sendmail(sender, recipients, message.as_string())
    server.quit()
    print("Email Sent!")

def createMashup(name, n, time, outputFileName):
    os.system("rm -r ./raw_audios")
    os.system("rm -r ./processed_audios")
    os.system("rm -r ./output")
    time = int(time) * 1000
    api_key = 'AIzaSyANhubQ4t8L5wb7L2YSWwMeipFPyzQtWZE'

    youtube = build('youtube', 'v3', developerKey=api_key)

    # Find Channel id

    request = youtube.search().list(
            part='snippet,id',
            q=name,
            type="channel",
            maxResults=1
        )

    response = request.execute()

    channelID = response['items'][0]['id']['channelId']

    print(channelID)
    # List Videos

    request = youtube.search().list(
        part='snippet,id',
        channelId=channelID,
        type="video",
        topicId="/m/04rlf",
        maxResults=n
    )

    response = request.execute()

    # list(response['items'])

    video_url_list = []
    for item in response['items']:
        video_url_list.append("https://www.youtube.com/watch?v="+item['id']['videoId']);

    video_url_list
    # Youtube video to mp3

    #!mkdir raw_audios
    dir_name = "raw_audios"
    if not os.path.exists("./" + dir_name):
        raw_audios = os.mkdir("./" + dir_name)
    else:
        print("Folder Already Present")
        os.system("rm -r ./"+dir_name+"/*")
        exit(1)

    count = 1
    for video_url in video_url_list:
        yt = YouTube(video_url)
        video = yt.streams.filter(only_audio=True).first()
        destination = './raw_audios/'
        filename = destination + str(count) + ".mp3"
        out_file = video.download(output_path=destination)
        os.rename(out_file, filename)
        print(filename, "completed!")
        count=count+1

    # Trim audio

    #!mkdir processed_audios
    dir_name = "processed_audios"
    if not os.path.exists("./" + dir_name):
        raw_audios = os.mkdir("./" + dir_name)
    else:
        print("Folder Already Present")
        os.system("rm -r ./"+dir_name+"/*")
        exit(1)

    #AudioSegment.converter = r"C:\ffmpeg\bin\ffmpeg.exe" # Letting the library know where ffmpeg is installed

    dirPath = os.getcwd()

    for f in range(1,count):
        filePath=dirPath + "/raw_audios/" + str(f) + ".mp3"
        sound = AudioSegment.from_file(filePath, format="mp4")
        extract = sound[0:time]
        extract.export("./processed_audios/" + str(f) + ".mp3", format="mp3")
        print(str(f) + ".mp3 processed!")
    # Merge audios

    #!mkdir output
    dir_name = "output"
    if not os.path.exists("./" + dir_name):
        raw_audios = os.mkdir("./" + dir_name)
    else:
        print("Folder Already Present")
        os.system("rm -r ./"+dir_name+"/*")
        exit(1)

    for f in range(1,count):
        filePath = dirPath + "/processed_audios/" + str(f) + ".mp3"
        if f == 1:
            sounds = AudioSegment.from_file(filePath, format="mp3")
        else:
            sound = AudioSegment.from_file(filePath, format="mp3")
            sounds = sounds + sound
        print(str(f)+".mp3 appended!")

    sounds.export("./output/"+str(outputFileName), format="mp3")



name = input("Enter singer name: ")
n = int(input("Enter number of songs: "))
time = int(input("Enter duration of each to cut from starting: "))
outputFileName = input("Output filename (must write .mp3): ")
email = input("Enter your email: ")

createMashup(name, n, time, outputFileName)
send_email(outputFileName, outputFileName, gmail, email, gmailpwd)
