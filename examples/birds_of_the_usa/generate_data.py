from pathlib import Path

import bs4
import requests

cache = Path(__file__).parent / ".cache"
cache.mkdir(exist_ok=True)


SPECIES_URL = "https://ebird.org/species/chiswi"


def parse_species_page():
    page = requests.get(SPECIES_URL)
    content = page.content
    parsed = bs4.BeautifulSoup(content, features="html.parser")
    classification_div = parsed.findAll("div", {"class": "Classification"})
    assert len(classification_div) == 1

    order_li, family_li = classification_div[0].findChildren("li")
    order = order_li.string
    family = family_li.string

    image_div = parsed.findAll("div", {"class": "MediaThumbnail Media Media--hero"})
    main_image_src = image_div[0].findAll("img")[0].attrs["src"]
    data = {
        # "name": name,
        # "s_name": s_name,
        "order": order,
        "family": family,
        "image": main_image_src,
    }
    raise NotImplementedError
    return data


def parse_index_page(region: str = "US", year: str = "all"):
    """Grab the eBird sitings for the given region.

    Args:
        region: The eBird region code. Defaults to "US" for the United States.
    """
    url = f"https://ebird.org/region/{region}?yr={year}"
    cached = cache / "index"
    if cached.exists():
        content = cached.read_text()
    else:
        page = requests.get(url)
        content = page.content
        cached.write_bytes(content)

    parsed = bs4.BeautifulSoup(content, features="html.parser")
    observations = parsed.findAll("div", {"id": "place-species-observed-results"})
    assert len(observations) == 1
    observations = observations[0]
    sections = observations.findAll("section")
    name_codes = []
    for i, section in enumerate(sections):
        link = section.find("a")
        species_code = link.attrs["data-species-code"]
        species_name = link.findChild().string
        name_codes.append(f"{species_name} {species_code}")
        if i == 1109:
            break
    p = cache / "name_codes.txt"
    s = "\n".join(name_codes)
    p.write_text(s)
    return s


if __name__ == "__main__":
    parse_index_page()
