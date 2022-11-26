from fastapi import FastAPI

from bs4 import BeautifulSoup
from requests_html import HTMLSession

from utils import replace_special_characters
from entities import MELI_BASE_URL, MELI_HTML_KEYS

app = FastAPI()


@app.get("/product_details/{country_code}/{code_or_url}")
def nuestro_comps(country_code: str, code_or_url: str) -> dict:
    meli_base_url = MELI_BASE_URL[country_code]
    if len(code_or_url) > 15:
        product_url = code_or_url
    else:
        product_code = code_or_url
        product_url = f"{meli_base_url}//p/{product_code}"

    session = HTMLSession()
    product_req = session.get(product_url)
    product_req.html.render(sleep=1)

    soup_product = BeautifulSoup(product_req.text, "html.parser")

    meli_html_keys = MELI_HTML_KEYS[country_code]
    title = soup_product.find(**meli_html_keys["title"])
    if bool(title):
        dict_ = {"name": replace_special_characters(title.text)}

    price = soup_product.find(**meli_html_keys["price"])
    if bool(price):
        price = int(price.text.replace(".", ""))
        dict_["price"] = price

    subtitle = soup_product.find(**meli_html_keys["subtitle"])
    if bool(subtitle):
        [condition, sales] = [subtitle.text.split()[i] for i in [0, 2]]
        dict_["condition"] = condition
        dict_["sales"] = sales

    img = soup_product.find(**meli_html_keys["img"])
    if bool(img):
        dict_["img_url"] = img.get("src")

    list_cat = soup_product.find_all(**meli_html_keys["categories"])
    if bool(list_cat):
        categories = [replace_special_characters(list_["title"]) for list_ in list_cat]
        dict_["categories"] = categories

    reviews = soup_product.find(**meli_html_keys["reviews"])
    reviews_url = f"{meli_base_url}{reviews.get('href')}"

    session2 = HTMLSession()
    reviews_req = session2.get(reviews_url)
    reviews_req.html.render(sleep=0)

    soup_reviews = BeautifulSoup(reviews_req.text, "html.parser")

    stars = soup_reviews.find(**meli_html_keys["stars"])
    if bool(stars):
        dict_["reviews"] = {"stars": float(stars.text)}

    num_reviews = soup_reviews.find(**meli_html_keys["num_reviews"])
    if bool(num_reviews):
        dict_["reviews"]["quantity"] = int(num_reviews.text.split()[0])

    num_stars = soup_reviews.find_all(**meli_html_keys["num_stars"])
    if bool(num_stars):
        dict_["reviews"]["stars_dist"] = dict(
            zip(
                [str(i) + "_star" for i in list(range(1, 6))[::-1]],
                [i["style"].split(":")[1] for i in num_stars],
            )
        )

    best_review = soup_reviews.find(**meli_html_keys["best_review"])
    if bool(best_review):
        dict_["reviews"]["best_review"] = replace_special_characters(best_review.text)

    return dict_
