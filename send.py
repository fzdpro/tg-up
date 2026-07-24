
import os
import glob
import subprocess
import requests
import json

from mutagen.easyid3 import EasyID3
from mutagen import File


token = os.environ["BOT_TOKEN"]

chat_id = os.environ["CHAT_ID"]


audio_url = (
    f"https://api.telegram.org/"
    f"bot{token}/sendAudio"
)


voice_url = (
    f"https://api.telegram.org/"
    f"bot{token}/sendVoice"
)


def time_to_seconds(value):

    parts = value.split(":")

    minutes = int(parts[0])

    seconds = int(parts[1])

    milliseconds = int(parts[2])

    return (
        minutes * 60
        + seconds
        + milliseconds / 1000
    )


for file in glob.glob(
    "uploads/*.mp3"
):

    filename = os.path.splitext(
        os.path.basename(file)
    )[0]


    cover = (
        f"covers/"
        f"{filename}.jpg"
    )


    metadata_file = (
        f"voice-settings/"
        f"{filename}.json"
    )


    voice_enabled = False

    voice_start = "00:00:000"

    voice_duration = ""


    if os.path.exists(
        metadata_file
    ):

        try:

            with open(
                metadata_file,
                "r",
                encoding="utf-8"
            ) as metadata:

                config = json.load(
                    metadata
                )


            print(
                "VOICE SETTINGS:"
            )

            print(
                config
            )


            voice_enabled = (
                config.get(
                    "enabled",
                    False
                )
                is True
            )


            voice_start = (
                config.get(
                    "start",
                    "00:00:000"
                )
            )


            voice_duration = (
                config.get(
                    "duration",
                    ""
                )
            )


        except Exception as error:

            print(
                f"Settings error: {error}"
            )


    print(
        f"Voice enabled: "
        f"{voice_enabled}"
    )


    print(
        f"Voice start: "
        f"{voice_start}"
    )


    print(
        f"Voice duration: "
        f"{voice_duration}"
    )


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

    except:

        artist = "Unknown Artist"

        title = filename


    audio_info = File(file)


    duration = int(
        audio_info.info.length
    ) if audio_info and audio_info.info else 0


    # ==========================================
    # SEND MP3
    # ==========================================


    data = {

        "chat_id": chat_id,

        "title": title,

        "performer": artist,

        "duration": duration,

        "caption": "@TRTOPMUSIC"

    }


    audio = open(
        file,
        "rb"
    )


    files = {

        "audio": audio

    }


    cover_file = None


    if os.path.exists(
        cover
    ):

        cover_file = open(
            cover,
            "rb"
        )

        files["thumbnail"] = (
            cover_file
        )


    try:

        response = requests.post(

            audio_url,

            data=data,

            files=files

        )


        print(
            response.text
        )


        result = response.json()


        if not result.get(
            "ok"
        ):

            raise Exception(
                response.text
            )


    finally:

        audio.close()


        if cover_file:

            cover_file.close()


    # ==========================================
    # SEND VOICE
    # ==========================================


    if voice_enabled:

        print(
            "VOICE IS ENABLED"
        )


        try:

            voice_duration_seconds = float(
                voice_duration
            )


            start_seconds = (
                time_to_seconds(
                    voice_start
                )
            )


            voice_file = (
                f"/tmp/"
                f"{filename}_voice.ogg"
            )


            ffmpeg_command = [

                "ffmpeg",

                "-y",

                "-ss",

                str(start_seconds),

                "-i",

                file,

                "-t",

                str(
                    voice_duration_seconds
                ),

                "-vn",

                "-c:a",

                "libopus",

                "-b:a",

                "128k",

                "-application",

                "voip",

                voice_file

            ]


            subprocess.run(

                ffmpeg_command,

                check=True

            )


            voice = open(

                voice_file,

                "rb"

            )


            response = requests.post(

                voice_url,

                data={

                    "chat_id":
                        chat_id,

                    "caption":
                        artist

                },

                files={

                    "voice":
                        voice

                }

            )


            print(
                response.text
            )


            result = response.json()


            voice.close()


            if not result.get(
                "ok"
            ):

                raise Exception(
                    response.text
                )


            print(
                "VOICE SENT SUCCESSFULLY"
            )


            os.remove(
                voice_file
            )


        except Exception as error:

            print(
                f"VOICE ERROR: {error}"
            )

            raise


    else:

        print(
            "VOICE DISABLED"
        )


    # ==========================================
    # DELETE PROCESSED FILES
    # ==========================================


    os.remove(
        file
    )


    if os.path.exists(
        cover
    ):

        os.remove(
            cover
        )


    if os.path.exists(
        metadata_file
    ):

        os.remove(
            metadata_file
        )


# ==========================================
# SEND OGG FILES
# ==========================================


for file in glob.glob(
    "uploads/*.ogg"
):


    filename = os.path.splitext(
        os.path.basename(file)
    )[0]


    voice = open(
        file,
        "rb"
    )


    response = requests.post(

        voice_url,

        data={

            "chat_id":
                chat_id,

            "caption":
                filename

        },

        files={

            "voice":
                voice

        }

    )


    print(
        response.text
    )


    result = response.json()


    voice.close()


    if not result.get(
        "ok"
    ):

        raise Exception(
            response.text
        )


    os.remove(
        file
    )


