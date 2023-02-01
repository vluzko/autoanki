from dataclasses import dataclass
from typing import Iterable, List
from autoanki import backend, config


@dataclass
class Deck:
    _collection: backend.collection.Collection
    _deck: backend.DeckDict
    cards: List[backend.notes.Note]

    def get_field_all(self, field: int):
        return [x.fields[field] for x in self.cards]

    def update_cards(self, notes):
        assert self._collection.db is not None
        for note in notes:
            self._collection.update_note(note)
        self._collection.db.commit()

    def map_cards(self, f):
        raise NotImplementedError

    def add_card(self, card):
        self._collection.add_note(card, self._deck['id'])
        assert self._collection.db is not None
        self._collection.db.commit()

    def add_card_json(self, json: dict, note_type: str):
        raise NotImplementedError

    def get_media(self):
        raise NotImplementedError


def blank_note(note_type: str, user_name: str='Main', anki_path=config.ANKI_PATH) -> backend.notes.Note:
    collection = backend.get_collection(user_name, anki_path=anki_path)
    return backend.blank_note(collection, note_type)


def create_note_type(name: str, fields: Iterable[str]):
    raise NotImplementedError


def create_deck_from_iterator(deck_name, note_type, note_data):
    raise NotImplementedError


def load_deck(deck_name: str, user_name: str='Main', anki_path=config.ANKI_PATH) -> Deck:
    collection = backend.get_collection(user_name, anki_path=anki_path)
    deck = backend.get_deck(collection, deck_name)
    cards = backend.get_deck_notes(collection, deck)
    return Deck(collection, deck, cards)