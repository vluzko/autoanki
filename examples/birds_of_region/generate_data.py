import argparse
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import bs4
import requests

from autoanki import backend, create

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
    parsed = bs4.BeautifulSoup(page.content, features="html.parser")
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


def parse_all_about_birds(url: str):
    """Parse the relevant All About Birds page.
    Used to grab images, audio, and range maps.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
    }
    page = requests.get(url, headers=headers)
    if page.status_code != 200:
        print(f"Failed to get {url} with status code {page.status_code}")
        return None
    else:
        parsed = bs4.BeautifulSoup(page.content, features="html.parser")

        main_div = parsed.find("div", {"class": "hero-content"})

        # Grab images and audio
        images = []
        audio = None
        if main_div is not None:
            pic_list = main_div.findAll("img")
            for pic in pic_list:
                try:
                    caption = pic.attrs["alt"]
                except KeyError:
                    caption = ""
                all_src = pic.attrs["data-interchange"].split(" ")
                large_src = all_src[-2][1:-1]
                images.append({"caption": caption, "src": large_src})

            # Grab audio
            audio_div = main_div.find("div", {"class": "jp-jplayer"})
            if audio_div is not None:
                audio = audio_div.attrs["name"]

        # Grab range map
        range_src = None
        narrow_div = parsed.find("div", {"class": "narrow-content"})
        if narrow_div is not None:
            range_map = narrow_div.find("img")
            range_src = range_map.attrs["data-interchange"].split(" ")[-2][1:-1]
        return images, audio, range_src


def download_and_store(note, url: str):
    s_name = note.fields[2].lower().replace(" ", "_")
    data_path: Path = CACHE / "bird_data" / s_name
    data_path.mkdir(parents=True, exist_ok=True)
    f_name = urlparse(url).path.split("/")[-1]
    p = data_path / f_name
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0"
    }
    if not p.exists():
        resp = requests.get(url, headers=headers)
        with p.open("wb") as f:
            f.write(resp.content)
    return p


def add_images(deck: create.Deck, note: Any, images: Any):
    if note.fields[3] != "":
        return
    image_strings = []
    for v in images:
        media_path = download_and_store(note, v["src"])
        if not backend.has_media(deck._collection, media_path):
            backend.add_media(deck._collection, media_path)
        caption = v["caption"]
        img_str = f'<img src="{media_path.name}">'
        full_str = f"{caption}\n<br/>\n{img_str}"
        image_strings.append(full_str)
    final_string = "\n<br/>\n".join(image_strings)
    backend.update_note_field(deck._collection, note, "Image", final_string)


def add_audio(deck: create.Deck, note, audio: str):
    if note.fields[0] != "":
        return
    media_path = download_and_store(note, audio)
    if not backend.has_media(deck._collection, media_path):
        backend.add_media(deck._collection, media_path)
    final_string = f"[sound:{media_path.name}]"
    backend.update_note_field(deck._collection, note, "Call", final_string)


def add_range_map(deck: create.Deck, note, range_map: str):
    if note.fields[4] != "":
        return
    media_path = download_and_store(note, range_map)
    if not backend.has_media(deck._collection, media_path):
        backend.add_media(deck._collection, media_path)
    final_string = f'<img src="{media_path.name}">'
    backend.update_note_field(deck._collection, note, "Range", final_string)


def add_media_content(region: str = "US", deck_name: str = "Birds of"):
    deck = create.load_deck(deck_name)
    base_url = "https://www.allaboutbirds.org/guide/"
    for note in deck.notes:
        audio = note.fields[0]
        c_name = note.fields[1]
        image = note.fields[3]
        range_map = note.fields[4]
        if image != "" and audio != "" and range_map != "":
            continue
        else:
            print(f"Getting {c_name}")
            page_name = c_name.replace(" ", "_").replace("'", "")
            page_url = f"{base_url}{page_name}"
            result = parse_all_about_birds(page_url)
            if result is None:
                print(f"Failed to get {page_url} for {c_name}")
            else:
                images, audio, range_map = result
                if len(images) == 0:
                    print("No images found for", c_name)
                else:
                    add_images(deck, note, images)
                if audio is None:
                    print("No audio found for", c_name)
                else:
                    add_audio(deck, note, audio)

                if range_map is None:
                    print("No range map found for", c_name)
                else:
                    add_range_map(deck, note, range_map)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--region", type=str, default="US")
    parser.add_argument("--deck-name", type=str)
    args = parser.parse_args()
    # build_deck(args.region, args.deck_name)
    add_media_content(args.region, args.deck_name)
