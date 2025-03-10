from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, TypedDict, Union

from anki import collection, decks, models, notes

from autoanki import config

OPEN_COLLS: Dict[Path, Any] = {}


class DeckDict(TypedDict):
    """Anki's type describing a deck.
    Note that notes and cards are not directly attached to the deck.
    """

    id: decks.DeckId
    mod: int
    name: str
    usn: int
    lrnToday: List[int]
    revToday: List[int]
    newToday: List[int]
    mid: int


class FieldDict(TypedDict):
    """Anki's type describing a field of a note."""

    name: str
    ord: int
    sticky: bool
    rtl: bool
    font: str
    size: int
    description: str


class CardDict(TypedDict):
    """Anki's type describing a card.
    Within the anki code this is also called a "template".
    """

    name: str
    ord: int
    qfmt: str
    afmt: str
    bqmft: str
    bafmt: str
    did: Optional[Any]
    bfont: str
    bsize: int


class GoodNoteTypeDict(TypedDict):
    """Notetype Dict that actually declares its fields
    Not to be salty but Dict[str, Any] isn't a real type.
    """

    id: int
    name: str
    type: int
    mod: int
    usn: int
    sortf: int
    did: Optional[Any]
    tmpls: List[CardDict]
    flds: List[FieldDict]
    css: str
    latexPre: str
    latexPost: str
    latexsvg: bool
    req: List[Any]


def get_collection(
    user_name: str, anki_path: Path = config.ANKI_PATH
) -> collection.Collection:
    """Get a user's collection"""
    global OPEN_COLLS
    anki_path = anki_path / user_name / "collection.anki2"
    if anki_path in OPEN_COLLS:
        return OPEN_COLLS[anki_path]
    else:
        coll = collection.Collection(str(anki_path))
        OPEN_COLLS[anki_path] = coll
        return coll


def close_collection(coll: collection.Collection):
    global OPEN_COLLS
    coll.close()
    del OPEN_COLLS[Path(coll.path)]


def close_all():
    for c in tuple(OPEN_COLLS.values()):
        close_collection(c)


def add_deck(coll: collection.Collection, deck_name: str) -> DeckDict:
    """Add a deck to a collection"""
    coll.decks.add_normal_deck_with_name(deck_name)
    coll.db.commit()  # type: ignore
    return get_deck(coll, deck_name)


def all_decks(coll: collection.Collection) -> Dict[int, DeckDict]:
    """Get a list of all decks in the collection."""
    decks = {x.id: coll.decks.get(x.id) for x in coll.decks.all_names_and_ids()}  # type: ignore
    return decks  # type: ignore


def has_deck(coll: collection.Collection, name: str) -> bool:
    """Check if a deck already exists."""
    return name in coll.decks.all_names()


def get_deck(coll: collection.Collection, name: str) -> DeckDict:
    """Get data for a particular deck"""
    for x in coll.decks.all_names_and_ids():
        if x.name == name:
            return coll.decks.get(x.id)  # type: ignore
    raise ValueError("Deck not found")


def all_note_ids(coll: collection.Collection):
    """Get the ID of every note in the collection."""
    return coll.find_notes("")


def all_notes(coll: collection.Collection) -> List[notes.Note]:
    """Get every note in the collection."""
    ids = all_note_ids(coll)
    notes = [coll.get_note(x) for x in ids]
    return notes


def get_deck_notes(coll: collection.Collection, deck: DeckDict) -> List[notes.Note]:
    """Get all notes attached to a deck"""
    deck_note_ids = coll.find_notes('deck:"{}"'.format(deck["name"]))
    deck_notes = [coll.get_note(x) for x in deck_note_ids]
    return deck_notes


def blank_note(coll: collection.Collection, note_type_name: str):
    """Create a blank note"""
    note_type = get_note_type(coll, note_type_name)
    assert note_type is not None
    new_note = coll.new_note(note_type)  # type: ignore
    return new_note


def add_note(coll: collection.Collection, deck_name: str, note_type_name: str):
    """Add a blank note to a deck"""
    deck = get_deck(coll, deck_name)
    assert deck is not None
    note_type = get_note_type(coll, note_type_name)
    assert note_type is not None
    new_note = coll.new_note(note_type)  # type: ignore
    coll.add_note(new_note, deck["id"])
    assert coll.db is not None
    return new_note


def update_note_field(
    coll: collection.Collection, note: notes.Note, field: str, new_value: str
):
    """Update a single field of an existing note."""
    field_idx = note.keys().index(field)
    note.fields[field_idx] = new_value
    coll.update_note(note)
    coll.after_note_updates([note.id], False)


def add_note_to_deck(
    coll: collection.Collection, note: notes.Note, deck_id: decks.DeckId
):
    """Add an existing note to a deck."""
    coll.add_note(note, deck_id)
    coll.db.commit()  # type: ignore


def all_note_types(coll: collection.Collection) -> List[models.NotetypeNameId]:
    """Get all note names and IDs."""
    return list(coll.models.all_names_and_ids())


def get_note_type(coll: collection.Collection, note_type: str) -> GoodNoteTypeDict:
    """List all available note types."""
    for x in coll.models.all():
        if x["name"] == note_type:
            return x  # type: ignore
    raise ValueError("Note type not found")


def has_note_type(coll: collection.Collection, name) -> bool:
    """Check if a note type with the given name exists."""
    return name in {x.name for x in all_note_types(coll)}


def new_note_type(
    coll: collection.Collection,
    name: str,
    fields: List[str],
    cards: Union[CardDict, Tuple[CardDict, ...]] = (),
) -> int:
    """Add a new note type to the collection

    Returns:
        The id of the new note type.
    """
    note_dict: GoodNoteTypeDict = coll.models.new(name)  # type: ignore
    field_dicts = [make_default_field(n) for n in fields]
    note_dict["flds"] = field_dicts

    if cards == ():
        note_dict["tmpls"] = make_default_card(name, fields)
    else:
        raise NotImplementedError
    res = coll.models.add_dict(note_dict)  # type: ignore

    return res.id


def make_default_field(name: str) -> FieldDict:
    """Create a basic field dict."""
    return {
        "name": name,
        "ord": 0,
        "sticky": False,
        "rtl": False,
        "font": "Arial",
        "size": 20,
        "description": "",
    }


def make_default_card(note_type: str, fields: List[str]) -> List[CardDict]:
    """Create a basic card.
    Puts the first field on the front and all other fields on the back.
    """
    front = f"{{{{{fields[0]}}}}}"
    back_fields = r"\n\n".join([f"{{{{{{x}}}}}}" for x in fields[1:]])  # noqa: F541
    back = f"{{{{FrontSide}}}}\n\n<hr id=answer>\n\n{back_fields}"

    return [
        {
            "name": f"{note_type}_card_1",
            "ord": 0,
            "qfmt": front,
            "afmt": back,
            "bqmft": "",
            "bafmt": "",
            "did": None,
            "bfont": "",
            "bsize": 0,
        }
    ]


def new_card(coll: collection.Collection, note_type: str):
    raise NotImplementedError


def add_media(coll: collection.Collection, media_path: Path):
    """Add a media file to the collection."""
    coll.media.add_file(str(media_path.absolute()))
    return media_path.name


def has_media(coll: collection.Collection, name_or_path: Union[str, Path]) -> bool:
    """Check if a piece of media has already been added
    Arguably this should check md5sums but *shrug*
    """
    if isinstance(name_or_path, Path):
        f_name = name_or_path.name
    else:
        f_name = name_or_path
    return coll.media.have(f_name)


def list_media(
    coll: collection.Collection, extension: Optional[str] = None
) -> List[str]:
    """List all media files."""
    media_folder = Path(coll.media._dir)
    glob = "*" if extension is None else f"*.{extension}"
    return [x.name for x in media_folder.glob(glob)]
