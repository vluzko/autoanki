import json

from autoanki import create


def main(deck_name: str, f: str):
    deck = create.load_deck(deck_name)

    # Create a note with "Basic" note type
    # The Basic note type typically has "Front" and "Back" fields

    with open(f, "r") as file:
        data = json.load(file)

    notes = []
    for item in data:
        note_id = deck.create_note(
            note_type="Basic",
            fields={"Front": item["Front"], "Back": item["Back"]},
        )
        notes.append(note_id)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Create Anki cards from JSON file")
    parser.add_argument("deck", help="Name of the Anki deck", type=str)
    parser.add_argument("file", help="JSON file containing card data", type=str)
    args = parser.parse_args()
    main(args.deck, args.file)
