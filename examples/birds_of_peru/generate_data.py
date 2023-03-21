from typing import Dict, List, Tuple
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


def get_region(region_name: str) -> List[Tuple[str, str]]:
    cache = Path(__file__).parent / ".cache"
    cache.mkdir(exist_ok=True)
    cached = cache / "index"
    url = f"https://ebird.org/region/{region_name}?YR=all"
    if cached.exists():
        content = cached.read_bytes()
    else:
        page = requests.get(url)
        content = page.content
        cached.write_bytes(content)

    parsed = bs4.BeautifulSoup(content, features="html.parser")
    observations = parsed.findAll("div", {"id": "place-species-observed-results"})
    assert len(observations) == 1
    observations = observations[0]
    sections = []
    for child in observations.children:
        if child.name == "section":
            sections.append(child)
        elif child.name == "div":
            if "ObservationSeparator" in child.attrs["class"]:
                break
    name_codes = []
    for i, section in enumerate(sections):
        link = section.find("a")
        species_code = link.attrs["data-species-code"]
        species_name = link.findChild().string
        name_codes.append((species_name, species_code))
    return name_codes


def main():
    region_name = "PE"
    names_codes = get_region(region_name)
    print(get_page_data(*names_codes[0]))
    # deck = create.create_empty_deck("Nature - Birds of Peru")
    # create.create_note_type(
    #     "Birds", ["Name", "Scientific Name", "Image", "Distribution"]
    # )


if __name__ == "__main__":
    main()
