from autoanki import create
import requests
import bs4


def build_note_type():
    raise NotImplementedError


def build_note(s_name: str, c_name: str, level: str):
    blank_note = create.blank_note("Bird")
    blank_note.fields[0] = c_name
    blank_note.fields[1] = s_name
    blank_note.fields[2] = level
    return blank_note


def parse_index_page(region: str):
    url = f"https://ebird.org/region/{region}?yr=all"
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
    # for i, section in enumerate(sections):
    #     link = section.find('a')
    #     species_code = link.attrs['data-species-code']
    #     species_name = link.findChild().string
    #     name_codes.append(f'{species_name} {species_code}')
    raise NotImplementedError


def build_all_notes():
    deck = create.new_deck("Birds of Peru")
    note_type = build_note_type()
    page = parse_index_page("PE")

    # Build cards
    # Add cards to deck
    # Add media


if __name__ == "__main__":
    build_all_notes()
