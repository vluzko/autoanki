from autoanki import create
import pandas as pd
from pathlib import Path


cache = Path(__file__).parent / '.cache'
cache.mkdir(exist_ok=True)

def build_card(s_name: str, c_name: str, level: str):
    blank_note = create.blank_note('Taxonomy')
    blank_note.fields[0] = c_name
    blank_note.fields[1] = s_name
    blank_note.fields[2] = level
    return blank_note


def main():
    fpath = Path(__file__).parent / 'clements_checklist_2022.csv'
    df = pd.read_csv(fpath)
    orders = df['order'].dropna().unique()
    families = df['family'].str.split(' ', n=1, expand=True)
    s_fam = families[0].dropna().unique()
    c_fam = [x[1:-1] for x in families[1].dropna().unique()]

    deck = create.load_deck('Nature - Avian Taxonomy')
    present = set(deck.get_field_all(1))
    for i, order in enumerate(orders):
        if order in present:
            continue
        note = build_card(order, f'{i}', 'order')
        deck.add_card(note)


    for s, c in zip(s_fam, c_fam):
        if s in present:
            continue
        else:
            note = build_card(s, f'{c} (family)', 'family')
            deck.add_card(note)


if __name__ == "__main__":
    main()