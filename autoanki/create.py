from dataclasses import dataclass
from typing import Iterable, List
from autoanki import backend, config


@dataclass
class Deck:
    _collection: backend.collection.Collection
    _deck: backend.DeckDict
    cards: List[backend.notes.Note]

    def update_cards(self, notes):
        for note in notes:
            self._collection.update_note(note)
        self._collection.db.commit()

    def map_cards(self, f):
        raise NotImplementedError

    def add_card(self, json: dict, note_type: str):
        raise NotImplementedError

    def get_media(self):
        raise NotImplementedError


def create_note_type(name: str, fields: Iterable[str]):
    raise NotImplementedError


def create_deck_from_iterator(deck_name, note_type, note_data):
    raise NotImplementedError


def load_deck(deck_name: str, user_name: str='User 1', anki_path=config.ANKI_PATH) -> Deck:
    collection = backend.get_collection(user_name, anki_path=anki_path)
    deck = backend.get_deck(collection, deck_name)
    cards = backend.get_deck_notes(collection, deck)
    return Deck(collection, deck, cards)