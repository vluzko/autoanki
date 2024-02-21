import filecmp
import shutil
from pathlib import Path

from pytest import fixture

from autoanki import backend

ANKI_PATH = Path(__file__).parent / "fake_anki"
ANKI_REF = Path(__file__).parent / "reference" / "collection.bak"


def make_test_coll() -> backend.collection.Collection:
    return backend.get_collection("User 1", anki_path=ANKI_PATH)


def test_coll():
    coll = backend.get_collection("User 1", anki_path=ANKI_PATH)
    assert isinstance(coll, backend.collection.Collection)
    assert coll.path == str(ANKI_PATH / "User 1" / "collection.anki2")


def test_get_all_decks():
    coll = make_test_coll()
    decks = backend.all_decks(coll)
    assert len(decks) == 1
    assert decks[1]["name"] == "Default"


def test_get_deck():
    coll = make_test_coll()
    deck = backend.get_deck(coll, "Default")
    assert deck["id"] == 1
    assert deck["name"] == "Default"


def test_has_deck():
    coll = make_test_coll()
    assert backend.has_deck(coll, "Default")
    assert not backend.has_deck(coll, "Does not exist")


def test_get_note_type():
    coll = make_test_coll()
    note_type = backend.get_note_type(coll, "Basic")
    assert note_type["name"] == "Basic"
    assert note_type["type"] == 0
    assert note_type["usn"] == 0


def test_add_note():
    coll = make_test_coll()
    new_note = backend.add_note(coll, "Default", "Basic")
    print(new_note.id)
    all_notes = coll.find_notes("")
    print(coll)
    assert all_notes == [new_note.id]


def test_update_note():
    coll = make_test_coll()
    new_note = backend.add_note(coll, "Default", "Basic")
    coll = make_test_coll()
    all_notes = coll.find_notes("")

    note_id = all_notes[0]
    note = coll.get_note(note_id)
    assert new_note.items() == note.items()
    note.fields[0] = "test"

    coll.update_note(note)
    assert coll.db is not None
    del coll
    coll = backend.get_collection("User 1", anki_path=ANKI_PATH)
    note = coll.get_note(note_id)
    assert note.fields[0] == "test"


def test_recreate_existing_note_type():
    coll = make_test_coll()
    original = backend.get_note_type(coll, "Basic")
    new = coll.models.new("A")

    # This is some legacy key.
    if "originalStockKind" in new:
        del new["originalStockKind"]
    assert original.keys() == new.keys()
    for f, v in original.items():
        if f == "name" or f == "id":
            continue
        new[f] = v
    coll.models.add_dict(new)
    del coll

    coll = make_test_coll()
    check = backend.get_note_type(coll, "A")

    for k, v in check.items():
        if k in {"id", "mod", "usn"}:
            continue
        assert v == new[k]


def get_all_note_types():
    coll = make_test_coll()
    note_types = backend.all_note_types(coll)
    assert len(note_types) == 4


def test_create_note_type():
    coll = make_test_coll()
    res = backend.new_note_type(coll, "Test note", ["Test field"])

    del coll

    coll = make_test_coll()
    check = backend.get_note_type(coll, "Test note")
    assert check["id"] == res


def test_add_media():
    coll = make_test_coll()
    image_path = Path(__file__).parent / "logo.png"
    backend.add_media(coll, image_path)
    new_path = ANKI_PATH / "User 1" / "collection.media" / "logo.png"
    filecmp.cmp(image_path, new_path)


def test_list_media():
    coll = make_test_coll()
    image_path = Path(__file__).parent / "logo.png"
    backend.add_media(coll, image_path)
    assert backend.list_media(coll) == ["logo.png"]


def clean():
    """Make a clean copy of the collection before each test"""
    files = (
        "collection.bak",
        "collection.bak-shm",
        "collection.bak-wal",
        "collection.media.db2",
        "collection.anki2-wal",
    )
    for f in files:
        path = ANKI_PATH / "User 1" / f
        if path.exists():
            path.unlink()

    folders = ("collection.media", "media.trash")
    for f in folders:
        path = ANKI_PATH / "User 1" / f
        if path.exists():
            for child in path.glob("*"):
                assert child.is_file()
                child.unlink()
    shutil.copy(ANKI_REF, ANKI_PATH / "User 1" / "collection.anki2")
    backend.close_all()


@fixture(autouse=True)
def clean_db():
    clean()
    yield
