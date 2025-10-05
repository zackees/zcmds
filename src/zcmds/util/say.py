import os
from tempfile import NamedTemporaryFile

from gtts import gTTS  # type: ignore
from playaudio import playaudio  # type: ignore


def say(text: str, output: str | None = None) -> None:
    tempmp3 = NamedTemporaryFile(suffix=".mp3", delete=False)
    tempmp3.close()
    try:
        tts = gTTS(text=text, lang="en")
        if output:
            tts.save(output)  # type: ignore[no-untyped-call]
            return
        tts.save(tempmp3.name)  # type: ignore[no-untyped-call]
        playaudio(tempmp3.name)
    finally:
        os.remove(tempmp3.name)
