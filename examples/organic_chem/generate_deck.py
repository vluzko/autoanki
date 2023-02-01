import autoanki
import requests
import bs4


def create_note_type():
    raise NotImplementedError


def create_card_type():
    raise NotImplementedError


def scrape_page():
    url = "https://chem.libretexts.org/Ancillary_Materials/Reference/Organic_Chemistry_Glossary"
    page = requests.get(url)
    import pdb
    pdb.set_trace()
    raise NotImplementedError


def main():
    res = scrape_page()


if __name__ == "__main__":
    main()