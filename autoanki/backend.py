from __future__ import annotations
import anki

from anki import collection, notes, decks
from os import environ
from pathlib import Path
from typing import Any, List, Optional, Tuple, Dict, TypedDict
from autoanki import config


OPEN_COLLS = {

}


class DeckDict(TypedDict):
    id: decks.DeckId
    mod: int
    name: str
    usn: int
    lrnToday: List[int]
    revToday: List[int]
    newToday: List[int]
    mid: int


def get_collection(user_name: str, anki_path: Path=config.ANKI_PATH) -> collection.Collection:
    """Get a user's collection"""
    global OPEN_COLLS
    anki_path = anki_path / user_name / 'collection.anki2'
    if anki_path in OPEN_COLLS:
        return OPEN_COLLS[anki_path]
    else:
        coll = collection.Collection(str(anki_path))
        OPEN_COLLS[anki_path] = coll
        return coll


def add_deck(coll: collection.Collection, deck_name: str):
    """Add a deck to a collection"""
    coll.decks.add_normal_deck_with_name(deck_name)
    coll.db.commit()  # type: ignore
    raise NotImplementedError
    # TODO: Return the deck


def all_decks(coll: collection.Collection) -> Dict[decks.DeckId, DeckDict]:
    raise NotImplementedError


def all_note_ids(coll):
    return coll.find_notes('')


def all_notes(coll):
    ids = all_note_ids(coll)
    notes = [coll.get_note(x) for x in ids]
    return notes


def list_decks(coll: collection.Collection):
    for deck in coll.decks.all_names_and_ids():
        print(deck.name)


def add_note_to_deck(coll: collection.Collection, note, deck_id):
    coll.add_note(note, deck_id)
    coll.db.commit()  # type: ignore


def get_deck(coll: collection.Collection, name: str) -> DeckDict:
    """Get data for a particular deck"""
    for x in coll.decks.all_names_and_ids():
        if x.name == name:
            return coll.decks.get(x.id)  # type: ignore
    raise ValueError('Deck not found')


def get_deck_notes(coll: collection.Collection, deck: DeckDict) -> List[notes.Note]:
    deck_note_ids = coll.find_notes('deck:"{}"'.format(deck['name']))
    deck_notes = [coll.get_note(x) for x in deck_note_ids]
    return deck_notes


def get_note_type(coll: collection.Collection, note_type: str) -> Optional[Dict[str, Any]]:
    """List all available note types"""
    for x in coll.models.all():
        if x['name'] == note_type:
            return x
    return None


def blank_note(coll: collection.Collection, note_type_name: str):
    note_type = get_note_type(coll, note_type_name)
    assert note_type is not None
    new_note = coll.new_note(note_type)
    return new_note


def add_note(coll: collection.Collection, deck_name: str, note_type_name: str):
    deck = get_deck(coll, deck_name)
    assert deck is not None
    note_type = get_note_type(coll, note_type_name)
    assert note_type is not None
    new_note = coll.new_note(note_type)
    coll.add_note(new_note, deck['id'])
    assert coll.db is not None
    coll.db.commit()
    return new_note


def new_note_type(coll: collection.Collection, name: str, fields: List[str]):
    raise NotImplementedError


def new_card(coll: collection.Collection, note_type: str):
    raise NotImplementedError


def add_media(coll: collection.Collection):
    raise NotImplementedError