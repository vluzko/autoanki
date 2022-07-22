import shutil
from pathlib import Path
from pytest import fixture
from autoanki import backend

ANKI_PATH = Path(__file__).parent / 'fake_anki'
ANKI_REF = ANKI_PATH / 'User 1' / 'collection.bak'

def test_coll():
    coll = backend.get_collection('User 1', base_path=ANKI_PATH)


def test_get_deck():
    coll = backend.get_collection('User 1', base_path=ANKI_PATH)
    deck = backend.get_deck(coll, 'Default')


def test_get_note_type():
    coll = backend.get_collection('User 1', base_path=ANKI_PATH)
    note_type = backend.get_note_type(coll, 'Basic')


def test_add_card():
    coll = backend.get_collection('User 1', base_path=ANKI_PATH)
    new_note = backend.add_note(coll, 'Default', 'Basic')
    all_notes = coll.find_notes('')
    assert len(all_notes) == 1



@fixture(autouse=True)
def clean_db():
    """Make a clean copy of the collection after each test"""
    yield
    shutil.copy(ANKI_REF, ANKI_PATH / 'User 1' / 'collection.anki2')
