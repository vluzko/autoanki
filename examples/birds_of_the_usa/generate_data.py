import pickle
from pathlib import Path

import bs4
import requests

cache = Path(__file__).parent / ".cache"
cache.mkdir(exist_ok=True)


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
    p = Path(__file__).parent / "name_codes.txt"
    s = "\n".join(name_codes)
    p.write_text(s)


if __name__ == "__main__":
    parse_index_page()
