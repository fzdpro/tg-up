
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


def time_to_seconds(time_string):

    try:

        minutes, seconds, milliseconds = map(
            int,
            time_string.split(":")
        )

        return (
            minutes * 60
            + seconds
            + milliseconds / 1000
        )

    except Exception:

        return 0


# ==================================================
# SEND MP3 FILES
# ==================================================


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


    # ----------------------------------------------
    # READ VOICE SETTINGS FROM CORRECT LOCATION
    # ----------------------------------------------


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
                or
                "00:00:000"
            )


            voice_duration = (
                config.get(
                    "duration",
                    ""
                )
                or
                ""
            )


            print(
                "Voice settings loaded:"
            )


            print(
                f"Enabled: "
                f"{voice_enabled}"
            )


            print(
                f"Start: "
                f"{voice_start}"
            )


            print(
                f"Duration: "
                f"{voice_duration}"
            )


        except Exception as e:

            print(
                f"Could not read voice settings: {e}"
            )


    else:

        print(
            "No voice settings file found:"
        )


        print(
            metadata_file
        )


    # ----------------------------------------------
    # READ MP3 TAGS
    # ----------------------------------------------


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

        print(
            f"Could not read tags: {e}"
        )


        artist = (
            "Unknown Artist"
        )


        title = filename


    audio_info = File(file)


    if (

        audio_info
        and
        audio_info.info

    ):

        duration = int(
            audio_info.info.length
        )

    else:

        duration = 0


    # ==================================================
    # SEND ORIGINAL MP3
    # ==================================================


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

                "Telegram audio error: "
                +
                response.text

            )


        print(
            "MP3 sent successfully"
        )


    finally:

        audio.close()


        if cover_file:

            cover_file.close()


    # ==================================================
    # CREATE AND SEND VOICE
    # ==================================================


    if voice_enabled:

        try:

            voice_duration_seconds = float(
                voice_duration
            )


        except Exception:

            voice_duration_seconds = 0


        if voice_duration_seconds <= 0:

            print(
                "Voice skipped:"
                " invalid duration"
            )

        else:

            start_seconds = (
                time_to_seconds(
                    voice_start
                )
            )


            voice_file = (
                f"/tmp/"
                f"{filename}_voice.ogg"
            )


            fade_start = max(
                voice_duration_seconds - 2,
                0
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

                "-af",

                (
                    f"afade="
                    f"t=out:"
                    f"st={fade_start}:"
                    f"d=2"
                ),

                "-c:a",

                "libopus",

                "-b:a",

                "128k",

                "-application",

                "voip",

                voice_file

            ]


            print(
                "Creating voice:"
            )


            print(
                voice_file
            )


            subprocess.run(

                ffmpeg_command,

                check=True

            )


            voice = open(

                voice_file,

                "rb"

            )


            voice_files = {

                "voice": voice

            }


            voice_data = {

                "chat_id": chat_id,

                "caption": artist

            }


            try:

                response = requests.post(

                    voice_url,

                    data=voice_data,

                    files=voice_files

                )


                print(
                    response.text
                )


                result = response.json()


                if not result.get(
                    "ok"
                ):

                    raise Exception(

                        "Telegram voice error: "
                        +
                        response.text

                    )


                print(
                    "Voice sent successfully"
                )


            finally:

                voice.close()


                if os.path.exists(
                    voice_file
                ):

                    os.remove(
                        voice_file
                    )


    else:

        print(
            "Voice disabled"
        )


    # ==================================================
    # DELETE PROCESSED FILES
    # ==================================================


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


# ==================================================
# SEND MANUALLY UPLOADED OGG FILES
# ==================================================


for file in glob.glob(
    "uploads/*.ogg"
):


    filename = os.path.splitext(
        os.path.basename(file)
    )[0]


    print(
        f"Sending voice: {file}"
    )


    voice = open(

        file,

        "rb"

    )


    voice_files = {

        "voice": voice

    }


    voice_data = {

        "chat_id": chat_id,

        "caption": filename

    }


    try:

        response = requests.post(

            voice_url,

            data=voice_data,

            files=voice_files

        )


        print(
            response.text
        )


        result = response.json()


        if result.get(
            "ok"
        ):

            print(
                "Voice sent successfully"
            )


            os.remove(
                file
            )

        else:

            raise Exception(

                "Telegram voice error: "
                +
                response.text

            )


    finally:

        voice.close()


