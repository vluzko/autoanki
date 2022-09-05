from dataclasses import dataclass
from typing import List
from autoanki import backend, config



@dataclass
class Deck:
    _collection: backend.collection.Collection
    _deck: backend.DeckDict
    cards: List[backend.notes.Note]

def create_deck_from_iterator(deck_name, note_type, note_data):
    import pdb
    pdb.set_trace()
    raise NotImplementedError


def load_deck(deck_name: str, user_name: str='User 1', anki_path=config.ANKI_PATH) -> backend.collection.Collection:
    collection = backend.get_collection(user_name, anki_path=anki_path)
    deck = backend.get_deck(collection, deck_name)
    cards = backend.get_deck_notes(collection, deck)
    return Deck(collection, deck, cards)
    # import pdbj
    # pdb.set_trace()
    # return deck