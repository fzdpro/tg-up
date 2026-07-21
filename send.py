import os
import glob
import requests

token = os.environ["BOT_TOKEN"]
chat_id = os.environ["CHAT_ID"]

url = f"https://api.telegram.org/bot{token}/sendAudio"

for file in glob.glob("uploads/*.mp3"):

    filename = os.path.splitext(
        os.path.basename(file)
    )[0]

    cover = f"covers/{filename}.jpg"

    data = {
        "chat_id": chat_id,
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
            print(f"Sent successfully: {file}")

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
