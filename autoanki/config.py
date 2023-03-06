from os import environ
from pathlib import Path


DEFAULT_USER = "Main"

if "ANKI_BASE" in environ:
    ANKI_PATH = Path(environ["ANKI_BASE"])
elif "XDG_DATA_HOME" in environ:
    ANKI_PATH = Path(environ["XDG_DATA_HOME"]) / "Anki2"
else:
    ANKI_PATH = Path.home() / ".local" / "share" / "Anki2"
