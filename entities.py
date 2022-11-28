MELI_BASE_URL = {
    "base": "https://www.mercadolibre.com",
    "listing": "https://listado.mercadolibre.com",
}
MELI_HTML_KEYS = {
    "title": {"name": "h1", "class_": "ui-pdp-title"},
    "price": {"name": "span", "class_": "andes-money-amount__fraction"},
    "discount_perc": {"name": "span", "class_": "andes-money-amount__discount"},
    "strike": {
        "name": "s",
        "class_": "andes-money-amount ui-pdp-price__part ui-pdp-price__original-value andes-money-amount--previous andes-money-amount--cents-superscript andes-money-amount--compact",
    },
    "subtitle": {"name": "span", "class_": "ui-pdp-subtitle"},
    "img": {"name": "img", "class_": "ui-pdp-image ui-pdp-gallery__figure__image"},
    "categories": {"name": "a", "class_": "andes-breadcrumb__link"},
    "reviews": {
        "name": "a",
        "class_": "ui-pdp-review__label ui-pdp-review__label--link",
    },
    "stars": {
        "name": "p",
        "class_": "ui-review-capability__rating__average ui-review-capability__rating__average--desktop",
    },
    "num_reviews": {"name": "p", "class_": "ui-review-capability__rating__label"},
    "num_stars": {
        "name": "span",
        "class_": "ui-review-capability-rating__level__progress-bar__fill-background",
    },
    "best_review": {
        "name": "p",
        "class_": "ui-review-capability-comments__comment__content",
    },
    "listing_url": {
        "name": "a",
        "class_": "ui-search-item__group__element shops__items-group-details ui-search-link",
    },
    "current_page": {"name": "span", "class_": "andes-pagination__link"},
}
COUNTRIES_AVAILABILITY = {
    "available": {
        "Colombia": "CO",
        "Peru": "PE",
        "Uruguay": "UY",
        "Argentina": "AR",
        "Mexico": "MX",
        "Chile": "CL",
        "Brazil": "BR",
    }
}

