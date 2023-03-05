from pathlib import Path
from dataclasses import dataclass
from typing import Callable, Dict, Iterable, List, Optional
from autoanki import backend, config


@dataclass
class Deck:
    _collection: backend.collection.Collection
    _deck: backend.DeckDict
    notes: List[backend.notes.Note]

    @property
    def name(self) -> str:
        return self._deck["name"]

    def get_field_by_index(
        self, field: int, note_type: Optional[str] = None
    ) -> List[str]:
        return [x.fields[field] for x in self.notes]

    def update_notes(self, notes):
        assert self._collection.db is not None
        for note in notes:
            self._collection.update_note(note)
        self._collection.db.commit()

    def map_notes_of_type(self, note_type: str, f: Callable):
        assert self._collection.db is not None

        raise NotImplementedError

    def add_note(self, card):
        self._collection.add_note(card, self._deck["id"])
        assert self._collection.db is not None
        self._collection.db.commit()

    def create_note(self, note_type: str, fields: Dict[str, str]):
        note = backend.blank_note(self._collection, note_type)

        raise NotImplementedError

    def get_media(self):
        raise NotImplementedError


def blank_note(
    note_type: str, user_name: str = "Main", anki_path=config.ANKI_PATH
) -> backend.notes.Note:
    """Create a blank note of the given type."""
    collection = backend.get_collection(user_name, anki_path=anki_path)
    return backend.blank_note(collection, note_type)


def create_note_type(
    name: str,
    fields: Iterable[str],
    user_name: str = "Main",
    anki_path: Path = config.ANKI_PATH,
    exists_ok: bool = True,
):
    """Create a new note with the given fields."""
    collection = backend.get_collection(user_name, anki_path=anki_path)
    import pdb

    pdb.set_trace()
    raise NotImplementedError


def create_card_type(name: str, note_type: str, front: str, back: str):
    raise NotImplementedError


def create_deck_from_iterator(deck_name, note_type, note_data):
    raise NotImplementedError


def create_empty_deck(
    deck_name: str,
    user_name: str = "Main",
    anki_path: Path = config.ANKI_PATH,
    exists_ok: bool = True,
) -> Deck:
    """Create a new blank deck with the given name."""
    collection = backend.get_collection(user_name, anki_path=anki_path)
    if not exists_ok:
        assert not backend.has_deck(collection, deck_name)
    collection.decks.add_normal_deck_with_name(deck_name)
    assert collection.db is not None
    collection.db.commit()
    deck = backend.get_deck(collection, deck_name)
    cards = backend.get_deck_notes(collection, deck)
    return Deck(collection, deck, cards)


def load_deck(
    deck_name: str, user_name: str = "Main", anki_path=config.ANKI_PATH
) -> Deck:
    """Load a deck with the given name."""
    collection = backend.get_collection(user_name, anki_path=anki_path)
    deck = backend.get_deck(collection, deck_name)
    cards = backend.get_deck_notes(collection, deck)
    return Deck(collection, deck, cards)


def load_all_decks(user_name: str = "Main", anki_path=config.ANKI_PATH):
    collection = backend.get_collection(user_name, anki_path=anki_path)
    decks = []
    for obj in collection.decks.all_names_and_ids():
        deck = backend.get_deck(collection, obj.name)
        cards = backend.get_deck_notes(collection, deck)
        decks.append(Deck(collection, deck, cards))
    return decks
