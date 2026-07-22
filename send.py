import os
import glob
import requests
from mutagen.easyid3 import EasyID3
from mutagen import File

token = os.environ["BOT_TOKEN"]
chat_id = os.environ["CHAT_ID"]

url = f"https://api.telegram.org/bot{token}/sendAudio"

for file in glob.glob("uploads/*.mp3"):

    filename = os.path.splitext(
        os.path.basename(file)
    )[0]

    cover = f"covers/{filename}.jpg"

    # خواندن Artist و Title
    try:
        tags = EasyID3(file)

        artist = tags.get(
            "artist",
            ["Unknown Artist"]
        )[0]

        title = tags.get(
            "title",
            [filename]
        )[0]

    except Exception as e:
        print(f"Could not read tags: {e}")

        artist = "Unknown Artist"
        title = filename

    # خواندن مدت زمان آهنگ
    audio_info = File(file)

    if audio_info and audio_info.info:
        duration = int(audio_info.info.length)
    else:
        duration = 0

    print(f"Artist: {artist}")
    print(f"Title: {title}")
    print(f"Duration: {duration} seconds")

    data = {
        "chat_id": chat_id,
        "title": title,
        "performer": artist,
        "duration": duration,
        "caption": "@TRTOPMUSIC"
    }

    audio = open(file, "rb")

    files = {
        "audio": audio
    }

    cover_file = None

    if os.path.exists(cover):
        cover_file = open(cover, "rb")
        files["thumbnail"] = cover_file

    try:
        response = requests.post(
            url,
            data=data,
            files=files
        )

        print(response.text)

        result = response.json()

        if result.get("ok"):

            print(
                f"Sent successfully: {file}"
            )

            os.remove(file)

            if os.path.exists(cover):
                os.remove(cover)

        else:

            raise Exception(
                f"Telegram error: {response.text}"
            )

    finally:

        audio.close()

        if cover_file:
            cover_file.close()

