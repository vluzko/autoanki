from __future__ import annotations
import anki

from anki import collection, notes
from pathlib import Path
from typing import Any, List, Optional, Tuple, Dict


ANKI_PATH = Path.home() / '.local' / 'share' / 'Anki2'


def add_deck(coll: collection.Collection, deck_name: str):
    coll.decks.add_normal_deck_with_name(deck_name)
    coll.db.commit()


def list_decks(coll: collection.Collection):
    for deck in coll.decks.all_names_and_ids():
        print(deck.name)


def make_note(coll: collection.Collection):
    import pdb
    pdb.set_trace()


def add_note_to_deck(coll: collection.Collection, note, deck_id):
    coll.add_note(note, deck_id)
    coll.db.commit()


def get_all_models(coll):
    """Retrieve all available models"""
    print(coll.models.all_names())
    import pdb
    pdb.set_trace()
    return coll.models


def all_note_ids(coll):
    return coll.find_notes('')


def get_collection(user_name: str, base_path: Path=ANKI_PATH) -> collection.Collection:
    """Get a user's collection"""
    anki_path = base_path / user_name / 'collection.anki2'
    return collection.Collection(str(anki_path))


def get_deck(coll: collection.Collection, name: str) -> Optional[Dict[str, Any]]:
    """Get data for a particular deck"""
    for x in coll.decks.all_names_and_ids():
        if x.name == name:
            return coll.decks.get(x.id)  # type: ignore

    return None


def get_note_type(coll: collection.Collection, note_type: str) -> Optional[Dict[str, Any]]:
    """List all available note types"""
    for x in coll.models.all():
        if x['name'] == note_type:
            return x
    return None


def add_note(coll: collection.Collection, deck_name: str, note_type_name: str):
    deck = get_deck(coll, deck_name)
    assert deck is not None
    note_type = get_note_type(coll, note_type_name)
    assert note_type is not None
    new_note = coll.new_note(note_type)
    coll.add_note(new_note, deck['id'])
    coll.db.commit()
    return new_note