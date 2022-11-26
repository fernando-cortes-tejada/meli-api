from fastapi import FastAPI

import requests
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession

from utils import replace_special_characters
from entities import MELI_BASE_URL, MELI_HTML_KEYS

import nest_asyncio

nest_asyncio.apply()
__import__("IPython").embed()

app = FastAPI()


@app.get("/product_details/{country_code}/{code_or_url:path}")
async def nuestro_comps(country_code: str, code_or_url: str) -> dict:
    meli_base_url = MELI_BASE_URL[country_code]
    if len(code_or_url) > 15:
        product_url = code_or_url
    else:
        product_code = code_or_url
        product_url = f"{meli_base_url}//p/{product_code}"

    session = AsyncHTMLSession()

    async def get_product():
        product_req = await session.get(product_url)
        await product_req.html.arender(sleep=5)
        return product_req

    product_req = session.run(get_product)

    soup_product = BeautifulSoup(product_req[0].text, "html.parser")

    meli_html_keys = MELI_HTML_KEYS[country_code]
    title = soup_product.find(**meli_html_keys["title"])
    if bool(title):
        dict_ = {"name": replace_special_characters(title.text)}

    print(dict_)

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

    stars = soup_product.find(**meli_html_keys["stars"])
    if bool(stars):
        dict_["reviews"] = {"stars": float(stars.text)}

    print(dict_)

    num_reviews = soup_product.find(**meli_html_keys["num_reviews"])
    if bool(num_reviews):
        dict_["reviews"]["quantity"] = int(num_reviews.text.split()[0])

    num_stars = soup_product.find_all(**meli_html_keys["num_stars"])
    if bool(num_stars):
        dict_["reviews"]["stars_dist"] = dict(
            zip(
                [str(i) + "_star" for i in list(range(1, 6))[::-1]],
                [i["style"].split(":")[1] for i in num_stars],
            )
        )

    best_review = soup_product.find(**meli_html_keys["best_review"])
    if bool(best_review):
        dict_["reviews"]["best_review"] = replace_special_characters(best_review.text)

    return dict_
