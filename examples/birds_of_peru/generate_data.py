from autoanki import create
import pandas as pd
from pathlib import Path


cache = Path(__file__).parent / '.cache'
cache.mkdir(exist_ok=True)


def build_note(s_name: str, c_name: str, level: str):
    blank_note = create.blank_note('Taxonomy')
    blank_note.fields[0] = c_name
    blank_note.fields[1] = s_name
    blank_note.fields[2] = level
    return blank_note


def build_all_notes():
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
        note = build_note(order, f'{i}', 'order')
        deck.add_card(note)


    for s, c in zip(s_fam, c_fam):
        if s in present:
            continue
        else:
            note = build_note(s, f'{c} (family)', 'family')
            deck.add_card(note)


def get_wiki_desc(n: str):
    import requests
    from bs4 import BeautifulSoup
    url = f'https://en.wikipedia.org/wiki/{n}'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    content = soup.find('div', attrs={'id': "mw-content-text"})
    try:
        first_p = content.findAll('p')[1].text
        print(first_p)
        return first_p
    except IndexError:
        print(f'No description for {n}')
        return ''


def add_descriptions():
    deck = create.load_deck('Nature - Avian Taxonomy')
    for note in deck.cards:
        desc = get_wiki_desc(note.fields[1])
        note.fields[-1] = note.fields[-1] + "\n" + desc
    deck.update_notes(deck.cards)


if __name__ == "__main__":
    add_descriptions()