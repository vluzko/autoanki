from pathlib import Path

import test_backend
from pytest import fixture

from autoanki import backend, create

USER = "User 1"
ANKI_PATH = Path(__file__).parent / "fake_anki"
ANKI_REF = ANKI_PATH / "User 1" / "collection.bak"


@fixture
def main_coll():
    coll = backend.get_collection("User 1", anki_path=ANKI_PATH)
    return coll


def test_add_note(main_coll):
    note_type_name = "Basic"
    deck = create.load_deck("Default", user_name=USER, anki_path=ANKI_PATH)
    note_type = create.get_note_type(
        note_type_name, user_name=USER, anki_path=ANKI_PATH
    )
    fields = note_type["flds"]
    note_data = {x["name"]: "test" for x in fields}
    note_id = deck.create_note(note_type_name, note_data)

    all_notes = backend.all_notes(main_coll)
    assert len(all_notes) == 1
    assert all_notes[0].id == note_id


def test_update_note():
    # raise NotImplementedError
    pass


def test_create_deck():
    create.create_empty_deck("Test Deck", "User 1", anki_path=ANKI_PATH)
    decks = create.load_all_decks("User 1", anki_path=ANKI_PATH)

    assert len(decks) == 2
    assert decks[0].name == "Default"
    assert decks[1].name == "Test Deck"


def test_create_note_type():
    # res = create.create_note_type("Test Note", [], user_name=USER, anki_path=ANKI_PATH)
    pass


@fixture(autouse=True)
def clean_db():
    """Make a clean copy of the collection after each test"""
    test_backend.clean()
    yield
