from typing import Dict, Tuple
import requests
import bs4
from pathlib import Path
from autoanki import create


def get_page_data(name: str, code: str):
    url = f"https://ebird.org/species/{code}/"
    path = Path(__file__).parent / "data"
    path.mkdir(exist_ok=True)
    f_path = path / code
    if f_path.exists():
        page_content = f_path.open("r").read()
    else:
        page = requests.get(url)
        if page.status_code == 404:
            return None
        else:
            f_path.write_bytes(page.content)
        page_content = page.content
    parsed = bs4.BeautifulSoup(page_content, features="html.parser")
    name_span = parsed.findAll("span", {"class": "Heading-main Media--hero-title"})
    assert len(name_span) == 1
    name = name_span[0].string

    s_name_span = parsed.findAll(
        "span",
        {"class": "Heading-sub Heading-sub--sci Heading-sub--custom u-text-4-loose"},
    )
    assert len(s_name_span) == 1
    s_name = s_name_span[0].string

    classification_div = parsed.findAll(
        "div", {"class": "Breadcrumbs Breadcrumbs--reverse u-stack-sm"}
    )
    assert len(classification_div) == 1

    order_li, family_li = classification_div[0].findChildren("li")
    order = order_li.string
    family = family_li.string

    # image_div = parsed.findAll('div', {'class': 'MediaThumbnail Media Media--hero'})
    # main_image_src = image_div[0].findAll('img')[0].attrs['src']
    return {"name": name, "s_name": s_name, "order": order, "family": family}


def build_card(card, codes):
    name = card.fields[1]
    new_card = False
    if name == "":
        new_card = True
        image_field = card.fields[-2]
        src_end = image_field.find("[")
        if src_end == -1:
            name = image_field.strip()
        else:
            name = image_field[:src_end].strip()
    name = name.lower()
    name = name.replace("&nbsp", "").replace("-", " ").strip()
    name = name.replace(";", "")
    if name in codes:
        code = codes[name]
        data = get_page_data(name, code)
        if data is None:
            print(name)
        else:
            card.fields[2] = data["s_name"]
            if new_card:
                start = card.fields[3].find("<img")
                end = card.fields[3].find('.jpg"/>')
                if start != -1:
                    new_field = card.fields[3][start : end + 7]
                    card.fields[3] = new_field
                    card.tags = [data["order"], data["family"]]
        return card
    else:
        print(name)


def main():
    deck = create.create_empty_deck("Nature - Birds of Peru")
    create.create_note_type(
        "Birds", ["Name", "Scientific Name", "Image", "Distribution"]
    )
    # deck = create.load_deck('Nature - Birds of the Americas')
    # codes = get_codes()
    # missing = []
    # updated = []
    # for i, card in enumerate(deck.cards):
    #     res = build_card(card, codes)
    #     if res is None:
    #         missing.append(card)
    #     else:
    #         updated.append(res)
    # deck.update_notes(updated)


if __name__ == "__main__":
    main()
