import bs4
import requests

url = "https://ebird.org/species/chiswi"


def main():
    page = requests.get(url)
    content = page.content
    parsed = bs4.BeautifulSoup(content, features="html.parser")
    import pdb

    pdb.set_trace()
    classification_div = parsed.findAll("div", {"class": "Classification"})
    assert len(classification_div) == 1

    order_li, family_li = classification_div[0].findChildren("li")
    order = order_li.string
    family = family_li.string

    image_div = parsed.findAll("div", {"class": "MediaThumbnail Media Media--hero"})
    main_image_src = image_div[0].findAll("img")[0].attrs["src"]
    return {
        "name": name,
        "s_name": s_name,
        "order": order,
        "family": family,
        "image": main_image_src,
    }


if __name__ == "__main__":
    main()
