import os
from tempfile import NamedTemporaryFile
from typing import Optional

from gtts import gTTS  # type: ignore
from playaudio import playaudio  # type: ignore


def say(text: str, output: Optional[str] = None) -> None:
    tempmp3 = NamedTemporaryFile(suffix=".mp3", delete=False)
    tempmp3.close()
    try:
        tts = gTTS(text=text, lang="en")
        if output:
            tts.save(output)
            return
        tts.save(tempmp3.name)
        playaudio(tempmp3.name)
    finally:
        os.remove(tempmp3.name)
