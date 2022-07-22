from pathlib import Path
from autoanki import backend
ANKI_PATH = Path(__file__).parent / 'fake_anki'

def test_coll():
    coll = backend.get_collection('User 1', base_path=ANKI_PATH)


def test_get_deck():
    coll = backend.get_collection('User 1', base_path=ANKI_PATH)
    deck = backend.get_deck(coll, 'Default')


def test_get_note_type():
    coll = backend.get_collection('User 1', base_path=ANKI_PATH)
    note_type = backend.get_note_type(coll, 'Basic')