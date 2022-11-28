from fastapi import FastAPI

from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession

from utils import replace_special_characters
from entities import MELI_BASE_URL, MELI_HTML_KEYS, COUNTRIES_AVAILABILITY

import nest_asyncio

nest_asyncio.apply()
__import__("IPython").embed()

app = FastAPI()


@app.get("/available_country_codes")
def available_country_codes() -> dict:
    dict_ = COUNTRIES_AVAILABILITY
    return dict_


@app.get("/product_details/{country_code}/{code_or_url:path}")
async def product_details(country_code: str, code_or_url: str) -> dict:
    meli_base_url = f"{MELI_BASE_URL['base']}.{country_code}"
    if country_code.lower() == "cl":
        meli_base_url = meli_base_url.replace(".com", "")
    if country_code.lower() == "br":
        meli_base_url = meli_base_url.replace("b", "v")
    if len(code_or_url) > 15:
        product_url = code_or_url
    else:
        product_code = code_or_url
        product_url = f"{meli_base_url}//p/{product_code}"

    session = AsyncHTMLSession()

    async def get_product():
        product_req = await session.get(product_url)
        await product_req.html.arender(sleep=1)
        await session.close()
        return product_req

    product_req = session.run(get_product)

    soup_product = BeautifulSoup(product_req[0].text, "html.parser")

    title = soup_product.find(**MELI_HTML_KEYS["title"])
    if bool(title):
        dict_ = {"name": replace_special_characters(title.text)}

    price = soup_product.find_all(**MELI_HTML_KEYS["price"])
    if bool(price):
        full_price = int(price[0].text.replace(".", ""))
        dict_["price"] = full_price
        try:
            price_w_disc = int(price[1].text.replace(".", ""))
            dict_["price_w_discount"] = price_w_disc
            disc_perc = soup_product.find(**MELI_HTML_KEYS["discount_perc"])
            disc_perc = disc_perc.text.split()[0]
            dict_["discount_percentage"] = disc_perc
        except:
            None

    subtitle = soup_product.find(**MELI_HTML_KEYS["subtitle"])
    if bool(subtitle):
        [condition, sales] = [subtitle.text.split()[i] for i in [0, 2]]
        dict_["condition"] = condition
        dict_["sales"] = sales

    img = soup_product.find(**MELI_HTML_KEYS["img"])
    if bool(img):
        dict_["img_url"] = img.get("src")

    list_cat = soup_product.find_all(**MELI_HTML_KEYS["categories"])
    if bool(list_cat):
        categories = [replace_special_characters(list_["title"]) for list_ in list_cat]
        dict_["categories"] = categories

    stars = soup_product.find(**MELI_HTML_KEYS["stars"])
    if bool(stars):
        dict_["reviews"] = {"stars": float(stars.text)}

    num_reviews = soup_product.find(**MELI_HTML_KEYS["num_reviews"])
    if bool(num_reviews):
        dict_["reviews"]["quantity"] = int(num_reviews.text.split()[0])

    num_stars = soup_product.find_all(**MELI_HTML_KEYS["num_stars"])
    if bool(num_stars):
        dict_["reviews"]["stars_dist"] = dict(
            zip(
                [str(i) + "_star" for i in list(range(1, 6))[::-1]],
                [i["style"].split(":")[1] for i in num_stars],
            )
        )

    best_review = soup_product.find(**MELI_HTML_KEYS["best_review"])
    if bool(best_review):
        dict_["reviews"]["best_review"] = replace_special_characters(best_review.text)

    return dict_


@app.get("/product_urls/{country_code}/{search_string}")
async def product_details(
    country_code: str, search_string: str, page_number: int = 1
) -> dict:
    meli_base_listing_url = MELI_BASE_URL["listing"]
    if country_code.lower() == "cl":
        meli_base_listing_url = meli_base_listing_url.replace(".com", "")
    if country_code.lower() == "br":
        meli_base_listing_url = meli_base_listing_url.replace(
            "listado", "lista"
        ).replace("b", "v")
    search_string = search_string.lower().replace(" ", "-")
    try:
        page_number
    except:
        listing_url = f"{meli_base_listing_url}/{search_string}"
    else:
        if page_number == 1:
            listing_url = f"{meli_base_listing_url}/{search_string}"
        else:
            listing_url = f"{meli_base_listing_url}/{search_string}_Desde_{str(1 + (page_number-1) * 50)}_NoIndex_True"

    session = AsyncHTMLSession()

    async def get_listing():
        listing_req = await session.get(listing_url)
        await listing_req.html.arender(sleep=1)
        await session.close()
        return listing_req

    listing_req = session.run(get_listing)

    soup_listing = BeautifulSoup(listing_req[0].text, "html.parser")

    listing_data = soup_listing.find_all(**MELI_HTML_KEYS["listing_url"])

    product_names = [data.text for data in listing_data if data]
    product_urls = [data.get("href") for data in listing_data if data]

    current_page = int(soup_listing.find(**MELI_HTML_KEYS["current_page"]).text)

    list_ = []
    for product_name, product_url in zip(product_names, product_urls):
        dict__ = {"name": product_name, "url": product_url}
        list_.append(dict__)

    dict_ = {"total_urls": len(product_urls), "page": current_page, "products": list_}

    return dict_
