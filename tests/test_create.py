import shutil
from pathlib import Path

from pytest import fixture

from autoanki import backend, create

USER = "User 1"
ANKI_PATH = Path(__file__).parent / "fake_anki"
ANKI_REF = ANKI_PATH / "User 1" / "collection.bak"


@fixture
def main_coll():
    coll = backend.get_collection("User 1", anki_path=ANKI_PATH)


def test_add_note():
    raise NotImplementedError


def test_update_note():
    raise NotImplementedError


def test_create_deck():
    create.create_empty_deck("Test Deck", "User 1", anki_path=ANKI_PATH)
    decks = create.load_all_decks("User 1", anki_path=ANKI_PATH)

    assert len(decks) == 2
    assert decks[0].name == "Default"
    assert decks[1].name == "Test Deck"


def test_create_note_type():
    res = create.create_note_type("Test Note", [], user_name=USER, anki_path=ANKI_PATH)


@fixture(autouse=True)
def clean_db():
    """Make a clean copy of the collection after each test"""
    yield
    shutil.copy(ANKI_REF, ANKI_PATH / "User 1" / "collection.anki2")
