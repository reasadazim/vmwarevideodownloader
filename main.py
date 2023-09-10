import re
import requests
import m3u8
import webbrowser
import pyautogui
import keyboard
import csv
import time
from moviepy.editor import *


# ######################### Check internet connection ###################
def internet_connection():
    try:
        response = requests.get("https://google.com", timeout=5)
        return True
    except requests.ConnectionError:
        return False


if not internet_connection():
    print("No internet connection!")
    print("Closing program...")
    time.sleep(10)
    exit()
# ######################### END - Check internet connection #############

# ##################### Create directories if not exists ################

paths = ["streams", "downloads", "list"]
for path in paths:
    # Check whether the specified path exists or not
    isExist = os.path.exists(path)
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(path)

# ##################### END - Create directories if not exists ###########

# ##################### Read CSV ###########################
if os.path.isfile('./list/files.csv'):
    with open('./list/files.csv', mode='r') as file:
        csvFile = csv.reader(file)
        next(csvFile)
        data = []
        for lines in csvFile:
            data.append(lines)
else:
    print("No 'files.csv' file exists in 'list directory'! Nothing to download.")
    print("Closing program...")
    time.sleep(10)
    exit()


# ##################### Read CSV ###########################

# ######################### Download m3u8 #########################

def download_m3u8(url):
    firefox = webbrowser.Mozilla("C:\\Program Files\\Mozilla Firefox\\firefox.exe")
    firefox.open(url)
    time.sleep(5)
    keyboard.press_and_release('F12')
    time.sleep(2)
    pyautogui.hotkey("ctrlleft", "f5")
    time.sleep(5)
    pyautogui.press("tab", presses=2)
    pyautogui.write("master.m3u8?fastly_token")
    time.sleep(1)
    pyautogui.press("tab", presses=28)
    time.sleep(1)
    pyautogui.hotkey("ctrlleft", "down")
    time.sleep(1)
    keyboard.press_and_release('menu')
    time.sleep(1)
    pyautogui.press("down", presses=6)
    time.sleep(1)
    pyautogui.press("enter")
    time.sleep(2)


# ######################### END - Download m3u8 #########################

queue = 1  # counting queue

# Start iterating videos from CSV list
for datum in data:

    # Read video name and URL
    video_title = datum[0]
    video_url = datum[1]

    print(f'Downloading [{queue}/{len(data)}]')

    # Generating video filename as slug to avoid file saving error
    video_title = re.sub('\W+', ' ', video_title)

    time.sleep(2)

    # ######################### READ m3u8 and download video #########################

    # Check the m3u8 file downloaded
    if os.path.isfile('./streams/master.m3u8'):
        T = False
    else:
        T = True

    while T:
        # Trigger download m3u8 file
        download_m3u8(video_url)
        # Check the m3u8 file downloaded
        if os.path.isfile('./streams/master.m3u8'):
            T = False
        else:
            T = True
    else:
        # Read the m3u8 file
        m3u8_master = m3u8.load('./streams/master.m3u8')

        video = m3u8_master.data['playlists'][0]['uri']
        audio = m3u8_master.data['media'][0]['uri']

        # Download video ts file
        r = requests.get(video)
        playlist = m3u8.loads(r.text)
        r = requests.get(playlist.data['segments'][0]['uri'])
        with open('./streams/vidl_v.ts', 'wb') as f:
            for segment in playlist.data['segments']:
                url = segment['uri']
                r = requests.get(url)
                f.write(r.content)

                sys.stdout.write('.')
                sys.stdout.flush()  # otherwise, won't show until some newline printed

        # Download audio ts file
        r = requests.get(audio)
        playlist = m3u8.loads(r.text)
        r = requests.get(playlist.data['segments'][0]['uri'])
        with open('./streams/vidl_a.ts', 'wb') as f:
            for segment in playlist.data['segments']:
                url = segment['uri']
                r = requests.get(url)
                f.write(r.content)
                sys.stdout.write('.')
                sys.stdout.flush()  # otherwise, won't show until some newline printed

        time.sleep(5)

        print('')

        # Combine audio and video ts files and produce mp4 video
        videoclip = VideoFileClip("./streams/vidl_v.ts")
        audioclip = AudioFileClip("./streams/vidl_a.ts")

        new_audioclip = CompositeAudioClip([audioclip])
        videoclip.audio = new_audioclip
        videoclip.write_videofile(f"./downloads/{video_title}.mp4")

        queue = queue + 1

        time.sleep(2)

        # Delete exising m3u8, video and audio ts file.
        os.remove("./streams/vidl_v.ts")
        os.remove("./streams/vidl_a.ts")
        os.remove("./streams/master.m3u8")

        time.sleep(2)
        print('')

        # ######################### END - READ m3u8 and download video #######################

        if queue > len(data):
            print('All files are downloaded.')
            time.sleep(10)
