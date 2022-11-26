MELI_BASE_URL = {"CO": "https://www.mercadolibre.com.co"}
MELI_HTML_KEYS = {
    "CO": {
        "title": {"name": "h1", "class_": "ui-pdp-title"},
        "price": {"name": "span", "class_": "andes-money-amount__fraction"},
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
    }
}
