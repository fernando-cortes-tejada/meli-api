from datetime import datetime
from itertools import compress
import os
import pandas as pd
import requests

from bs4 import BeautifulSoup
from csv import writer
import google.auth
from google.cloud import bigquery
from google.cloud import storage
import pandas_gbq as pdgbq
from urllib.parse import urljoin

from src.models.meli_scraper.entities import (
    BASE_MELI_URL,
    BUCKET_NAME,
    DATA_FILE_NAME,
    HEADERS,
    SELECTED_COLUMNS,
    SCOPES,
    CONTROL_SHEET_PATH,
    send_file_format,
    file_read_format,
    prefix,
    year,
    week,
)
from src.models.meli_scraper.queries import get_categories_list_query
from src.models.meli_scraper.utils import find_nth
from src.entities import GCP_CRED_LOCATION
from src.utils import upload_blob


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GCP_CRED_LOCATION

credentials, project_id = google.auth.default(scopes=SCOPES)
pdgbq.context.credentials = credentials
pdgbq.context.project = project_id
bigquery.Client(project_id, credentials)


def execute_favik_meli_scraper() -> None:
    while True:
        with open(DATA_FILE_NAME, "w", encoding="utf8", newline="") as csv_file:
            thewriter = writer(csv_file)
            header = HEADERS
            thewriter.writerow(header)

        try:
            control_sheet = pd.read_csv(CONTROL_SHEET_PATH)
        except Exception as e:
            print(f"control_sheet not found due to {e}...")
            control_sheet = pd.DataFrame(columns=SELECTED_COLUMNS)

        week_day = datetime.now().isocalendar()[2]
        if "category" in locals():
            del category

        category_list = pd.read_gbq(get_categories_list_query())
        n_cat = sum(category_list["ACTIVO"] == 1)
        active_list = category_list[category_list["ACTIVO"] == 1][
            "BUSCADOR_SCRAPER"
        ].tolist()

        control_sheet_tmp = control_sheet[
            control_sheet["BUSCADOR_SCRAPER"].isin(active_list)
        ]
        started_not_finished = control_sheet_tmp.loc[
            (control_sheet_tmp["STARTED"] == 1)
            & (control_sheet_tmp["FINISHED"] == 0)
            & (control_sheet["YEAR"] == year)
            & (control_sheet["ISO_WEEK"] == week)
        ]

        if not started_not_finished.empty:
            category = started_not_finished.iloc[0, :]["BUSCADOR_SCRAPER"]
            control_sheet = control_sheet.loc[
                ~(
                    (control_sheet["STARTED"] == 1)
                    & (control_sheet["FINISHED"] == 0)
                    & (control_sheet["YEAR"] == year)
                    & (control_sheet["ISO_WEEK"] == week)
                )
            ]

        else:
            control_sheet = control_sheet[control_sheet["FINISHED"] == 1]
            control_sheet_tmp = control_sheet.loc[
                (control_sheet["YEAR"] == year) & (control_sheet["ISO_WEEK"] == week)
            ]
            cat_already_scraped = control_sheet_tmp["BUSCADOR_SCRAPER"].tolist()
            for cats in active_list:
                if cats not in cat_already_scraped:
                    category = cats
                    break

        if not "category" in locals():
            print("All categories are already scraped this week")
            break
        else:
            cat_num = active_list.index(category) + 1

        info = [
            category_list[category_list["BUSCADOR_SCRAPER"] == category].iloc[0, 0],
            category_list[category_list["BUSCADOR_SCRAPER"] == category].iloc[0, 1],
            category_list[category_list["BUSCADOR_SCRAPER"] == category].iloc[0, 2],
            category,
            year,
            week,
            week_day,
            1,
            datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            0,
            None,
        ]
        control_sheet.loc[len(control_sheet)] = info

        control_sheet.to_csv(CONTROL_SHEET_PATH, index=False)

        print(f"Started scraping: {category} ({str(cat_num)}/{str(n_cat)})")

        url = urljoin(BASE_MELI_URL, category.lower().replace(" ", "-"))

        while True:
            page = requests.get(url)
            print("Root page status code: " + str(page.status_code))

            soup = BeautifulSoup(page.content, "html.parser")

            urls = soup.find_all(
                "a",
                class_="ui-search-item__group__element shops-custom-secondary-font ui-search-link",
            )
            if not bool(urls):
                urls = soup.find_all(
                    "a", class_="ui-search-result__content ui-search-link"
                )
            if not bool(urls):
                urls = soup.find_all(
                    "a",
                    class_="ui-search-item__group__element shops__items-group-details ui-search-link",
                )

            products = [url.text for url in urls if url]
            urls = [url.get("href") for url in urls if url]
            print(f"Total urls: {str(len(urls))}")

            current_page = soup.find("span", class_="andes-pagination__link")
            if bool(current_page):
                current_page = int(current_page.text)
                total_pages = soup.find("li", class_="andes-pagination__page-count")
                total_pages = int(
                    list(
                        compress(
                            total_pages.text.split(),
                            [val.isdigit() for val in total_pages.text.split()],
                        )
                    )[0]
                )
                print(f"Current page: {str(current_page)} of {str(total_pages)}")
            else:
                current_page = 1
                total_pages = 1
                print(f"Current page: {str(current_page)} of {str(total_pages)}")

            i = 0

            for url in urls:

                page2 = requests.get(url)
                print(
                    f"""Category: category ({str(cat_num)}/{str(n_cat)}). Current page: ({str(current_page)}/{str(total_pages)}). Branch page ({str(i + 1)}/{str(len(urls))}) status code: {str(page2.status_code)}"""
                )

                soup2 = BeautifulSoup(page2.content, "html.parser")

                price = soup2.find("span", class_="andes-money-amount__fraction")

                if bool(price):
                    price = int(
                        soup2.find(
                            "span", class_="andes-money-amount__fraction"
                        ).text.replace(".", "")
                    )
                else:
                    price = 0

                sales = soup2.find("span", class_="ui-pdp-subtitle")
                if bool(sales):
                    sales = list(
                        compress(
                            sales.text.split(),
                            [val.isdigit() for val in sales.text.split()],
                        )
                    )
                    if len(sales) == 0:
                        sales = 0
                    else:
                        sales = int(sales[0])
                else:
                    sales = 0

                reviews = soup2.find("span", class_="ui-pdp-review__amount")
                if bool(reviews):
                    reviews = int(reviews.text.replace("(", "").replace(")", ""))
                else:
                    reviews = 0

                stars = soup2.find("span", class_="ui-pdp-review__ratings")

                if bool(stars):
                    stars = stars.find_all("use")
                    stars = [star.get("href").replace("#", "") for star in stars]
                    stars = (
                        sum([star == "star_full" for star in stars])
                        + sum([star == "star_half" for star in stars]) * 0.5
                    )
                else:
                    stars = 0

                list_cat = soup2.find_all("a", class_="andes-breadcrumb__link")
                categories = [list["title"] for list in list_cat]
                while len(categories) < 6:
                    categories = categories + [""]

                info = [
                    products[i].encode("utf-8").strip(),
                    datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    urls[i],
                    price,
                    sales,
                    reviews,
                    stars,
                    current_page,
                ] + categories

                with open(DATA_FILE_NAME, "a", encoding="utf8", newline="") as csv_file:
                    thewriter = writer(csv_file)
                    thewriter.writerow(info)

                i += 1

            if current_page < min(total_pages, 10):
                url = urljoin(
                    BASE_MELI_URL,
                    category.lower().replace(" ", "-")
                    + "_Desde_"
                    + str(1 + current_page * 50)
                    + "_NoIndex_True",
                )
            else:
                upload_blob(
                    BUCKET_NAME,
                    DATA_FILE_NAME,
                    f"meli/data_{str(year)}_{str(week)}/data_{category.lower().replace(' ', '').replace(',','_')}_{str(year)}{str(week)}.csv",
                )
                control_sheet.iloc[len(control_sheet) - 1, 9] = 1
                control_sheet.iloc[
                    len(control_sheet) - 1, 10
                ] = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                control_sheet.to_csv(
                    CONTROL_SHEET_PATH, index=False,
                )
                print("Finished scraping: " + category)
                break


def execute_data_meli_join() -> None:

    client = storage.Client()
    filenames = []
    for blob in client.list_blobs(BUCKET_NAME, prefix=prefix):
        initpos = str(blob).find(prefix) + len(prefix) + 1
        finpos = find_nth(str(blob), ",", 2)
        filenames = filenames + [str(blob)[initpos:finpos]]

    df = pd.DataFrame()
    for filename in filenames:
        if filename:
            try:
                df = pd.concat((df, pd.read_csv(f"{file_read_format}/{filename}")))
            except Exception as e:
                print(f"Unable to load {filename} category due to {e}")

    df.to_csv(send_file_format, index=False)
