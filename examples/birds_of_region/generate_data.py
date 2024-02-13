import argparse
import json
from pathlib import Path

import bs4
import requests

from autoanki import create

SPECIES_URL_BASE = "https://ebird.org/species/"
CACHE = Path(__file__).parent / ".cache"


def parse_species_page(species_code: str) -> dict:
    species_url = f"{SPECIES_URL_BASE}{species_code}"
    page = requests.get(species_url)
    content = page.content
    parsed = bs4.BeautifulSoup(content, features="html.parser")
    classification_div = parsed.findAll("div", {"class": "Breadcrumbs"})
    assert len(classification_div) == 1

    order_li, family_li = classification_div[0].findChildren("li")
    order = order_li.string
    family = family_li.string

    common_name_span = parsed.findAll("span", {"class": "Media--hero-title"})
    assert len(common_name_span) == 1
    species_span = parsed.findAll("span", {"class": "Heading-sub--sci"})
    assert len(species_span) == 1
    common_name = common_name_span[0].string
    species_name = species_span[0].string

    image_div = parsed.findAll("div", {"class": "MediaThumbnail Media Media--hero"})
    if len(image_div) == 0:
        main_image_src = None
    else:
        main_image_src = image_div[0].findAll("img")[0].attrs["src"]
    data = {
        "Common Name": common_name,
        "Scientific Name": species_name,
        "order": order,
        "family": family,
        "Image": main_image_src,
    }
    return data


def parse_index_page(region: str = "US", year: str = "all") -> list[dict]:
    """Grab the eBird sitings for the given region.

    Args:
        region: The eBird region code. Defaults to "US" for the United States.
    """
    url = f"https://ebird.org/region/{region}?yr={year}"
    page = requests.get(url)
    content = page.content

    parsed = bs4.BeautifulSoup(content, features="html.parser")
    observations = parsed.findAll("div", {"id": "place-species-observed-results"})
    assert len(observations) == 1
    observations = observations[0]
    sections = observations.findAll("section")  # type: ignore
    card_details = []
    for i, section in enumerate(sections):
        # Break when we get to exotic provisional
        svg = section.find("svg")
        if svg is not None:
            if "Icon--exoticProvisional" in svg.attrs["class"]:
                break
        link = section.find("a")
        species_code = link.attrs["data-species-code"]
        common_name = section.find("span", {"class": "Heading-main"}).text
        card_details.append({"common_name": common_name, "species_code": species_code})
    return card_details


def fix_data(region="US") -> None:
    cache_path = CACHE / f"{region}.json"
    cache = json.load(cache_path.open("r"))
    new_cache = {}
    for k, v in cache.items():
        new_v = {}
        new_v["Common Name"] = v["common_name"]
        new_v["Scientific Name"] = v["species_name"]
        new_v["order"] = v["order"]
        new_v["family"] = v["family"]
        new_v["Image"] = v["image"]
        new_cache[k] = new_v
    json.dump(new_cache, cache_path.open("w"))


def build_deck(region: str = "US", deck_name: str = "Birds of"):
    card_details = {
        c["common_name"]: c["species_code"] for c in parse_index_page(region)
    }
    deck = create.load_deck(deck_name)
    note_type = deck.notes[0]._note_type["name"]
    already_present = {dict(n.items())["Common Name"] for n in deck.notes}
    needed = {k: v for k, v in card_details.items() if k not in already_present}

    cache_path = CACHE / f"{region}.json"
    if cache_path.exists():
        cache = json.load(cache_path.open("r"))
    else:
        cache = {}
    for i, (k, v) in enumerate(needed.items()):
        if k in already_present:
            continue
        print(i, k)
        if v in cache:
            data = cache[v]
        else:
            data = parse_species_page(v)
            cache[v] = data
            json.dump(cache, cache_path.open("w"))

        order = data.pop("order")
        family = data.pop("family")
        tags = [order, family]
        if data["Image"] is None:
            data["Image"] = ""
        deck.create_note(note_type, data, tags=tags)
        break
        # deck.add_note()
        # note = create.add_note(
        #     deck.collection,
        #     deck.name,
        #     "Birds of",
        #     **{
        #         "Common Name": data["common_name"],
        #         "Species Name": data["species_name"],
        #         "Order": data["order"],
        #         "Family": data["family"],
        #         "Image": data["image"],
        #     },
        # )
    import pdb

    pdb.set_trace()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str, default="US")
    parser.add_argument("--deck-name", type=str)
    args = parser.parse_args()
    build_deck(args.region, args.deck_name)
