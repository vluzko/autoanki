import shutil
from pathlib import Path
from pytest import fixture
from autoanki import backend


ANKI_PATH = Path(__file__).parent / "fake_anki"
ANKI_REF = ANKI_PATH / "User 1" / "collection.bak"


def make_test_coll() -> backend.collection.Collection:
    return backend.get_collection("User 1", anki_path=ANKI_PATH)


@fixture
def coll() -> backend.collection.Collection:
    return make_test_coll()


def test_coll():
    coll = backend.get_collection("User 1", anki_path=ANKI_PATH)


def test_get_deck(coll):
    deck = backend.get_deck(coll, "Default")


def test_has_deck(coll):
    assert backend.has_deck(coll, "Default")
    assert not backend.has_deck(coll, "Does not exist")


def test_get_note_type(coll):
    note_type = backend.get_note_type(coll, "Basic")


def test_add_note(coll):
    new_note = backend.add_note(coll, "Default", "Basic")
    all_notes = coll.find_notes("")
    assert len(all_notes) == 1


def test_update_note(coll):
    new_note = backend.add_note(coll, "Default", "Basic")
    del coll
    coll = make_test_coll()
    all_notes = coll.find_notes("")
    note_id = all_notes[0]
    note = coll.get_note(note_id)
    note.fields[0] = "test"
    coll.update_note(note)
    assert coll.db is not None
    coll.db.commit()
    del coll
    coll = backend.get_collection("User 1", anki_path=ANKI_PATH)
    note = coll.get_note(note_id)
    assert note.fields[0] == "test"


def test_recreate_existing_note_type(coll):
    original = backend.get_note_type(coll, "Basic")
    new = coll.models.new("A")

    assert original.keys() == new.keys()
    for f, v in original.items():
        if f == 'name' or f == 'id':
            continue
        new[f] = v
    res = coll.models.add_dict(new)
    del coll

    coll = make_test_coll()
    check = backend.get_note_type(coll, "A")

    for k, v in check.items():
        if k in {'id', 'mod', 'usn'}:
            continue
        assert v == new[k]


def test_create_note_type(coll):
    res = backend.new_note_type(coll, 'Test note', ['Test field'])

    del coll

    coll = make_test_coll()
    check = backend.get_note_type(coll, "Test note")
    assert check['id'] == res


@fixture(autouse=True)
def clean_db():
    """Make a clean copy of the collection after each test"""
    yield
    shutil.copy(ANKI_REF, ANKI_PATH / "User 1" / "collection.anki2")
