from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, Iterable, List, Optional, Sequence

from autoanki import backend, config


@dataclass
class Deck:
    """Wrapper around an Anki deck that captures the whole context."""

    _collection: backend.collection.Collection
    _deck: backend.DeckDict
    notes: List[backend.notes.Note]

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return f"Deck({self.name})"

    @property
    def id(self) -> int:
        return self._deck["id"]

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

    def map_notes_of_type(self, note_type: str, f: Callable):
        assert self._collection.db is not None

        raise NotImplementedError

    def add_note(self, note: backend.notes.Note) -> int:
        self._collection.add_note(note, self._deck["id"])
        assert self._collection.db is not None
        self._collection.after_note_updates([note.id], False)
        self.notes.append(note)
        return note.id

    def create_note(
        self, note_type: str, fields: Dict[str, str], tags: Optional[list[str]] = None
    ) -> int:
        """Create a note and add it to this deck.

        Args:
            note_type: The name of the note type
            fields: The fields of the note (as a dictionary)
            tags: The tags to add.

        Returns:
            int: The new note ID
        """
        note = backend.blank_note(self._collection, note_type)
        field_map = {k: i for i, k in enumerate(note.keys())}
        for k, v in fields.items():
            idx = field_map[k]
            note.fields[idx] = v
        if tags is not None:
            note.tags = tags
        return self.add_note(note)

    def delete_notes(self, notes: Sequence[int]):
        self._collection.remove_notes(notes)  # type: ignore

    def delete_note(self, note: int):
        self.delete_notes((note,))

    def get_media(self):
        raise NotImplementedError


def get_note_type(
    note_type_name: str,
    user_name: str = config.DEFAULT_USER,
    anki_path: Path = config.ANKI_PATH,
):
    """Get a note type by name."""
    collection = backend.get_collection(user_name, anki_path=anki_path)
    note_type = backend.get_note_type(collection, note_type_name)
    return note_type


def create_note_type(
    name: str,
    fields: Iterable[str],
    user_name: str = config.DEFAULT_USER,
    anki_path: Path = config.ANKI_PATH,
    exists_ok: bool = True,
):
    """Create a new note with the given fields."""
    collection = backend.get_collection(user_name, anki_path=anki_path)
    if backend.has_note_type(collection, name):
        if exists_ok:
            return backend.get_note_type(collection, name)
        else:
            raise ValueError
    # res = backend.new_note_type(collection, name, fields)
    raise NotImplementedError


def create_card_type(name: str, note_type: str, front: str, back: str):
    raise NotImplementedError


def create_deck_from_iterator(deck_name, note_type, note_data):
    raise NotImplementedError


def create_empty_deck(
    deck_name: str,
    user_name: str = config.DEFAULT_USER,
    anki_path: Path = config.ANKI_PATH,
    exists_ok: bool = True,
) -> Deck:
    """Create a new blank deck with the given name."""
    collection = backend.get_collection(user_name, anki_path=anki_path)
    if not exists_ok:
        assert not backend.has_deck(collection, deck_name)
    collection.decks.add_normal_deck_with_name(deck_name)
    assert collection.db is not None
    deck = backend.get_deck(collection, deck_name)
    cards = backend.get_deck_notes(collection, deck)
    return Deck(collection, deck, cards)


def load_deck(
    deck_name: str, user_name: str = config.DEFAULT_USER, anki_path=config.ANKI_PATH
) -> Deck:
    """Load a deck with the given name."""
    collection = backend.get_collection(user_name, anki_path=anki_path)
    deck = backend.get_deck(collection, deck_name)
    cards = backend.get_deck_notes(collection, deck)
    return Deck(collection, deck, cards)


def load_all_decks(
    user_name: str = config.DEFAULT_USER, anki_path=config.ANKI_PATH
) -> list[Deck]:
    collection = backend.get_collection(user_name, anki_path=anki_path)
    decks = []
    for obj in collection.decks.all_names_and_ids():
        deck = backend.get_deck(collection, obj.name)
        cards = backend.get_deck_notes(collection, deck)
        decks.append(Deck(collection, deck, cards))
    return decks
