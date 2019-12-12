import re
import superdesk

from enum import IntEnum
from superdesk.text_utils import get_char_count
from superdesk.signals import item_validate
from ansa.constants import GALLERY

MASK_FIELD = "output_code"


class Validators(IntEnum):
    HEADLINE_REQUIRED = 0
    SHORTTITLE_REQUIRED = 1
    SUBTITLE_REQUIRED = 2
    SUBJECT_REQUIRED = 3
    BODY_LENGTH_512 = 4
    BODY_LENGTH_6400 = 5
    BODY_LENGTH_2224 = 6
    FEATURED_REQUIRED = 7
    GALLERY_REQUIRED = 8


class Errors:
    AFP_IMAGE_USAGE = "AFP images could not be used"


def get_active_mask(products):
    mask = {}
    if products:
        cv = superdesk.get_resource_service("vocabularies").find_one(
            req=None, _id="products"
        )
        codes = {product["qcode"]: 1 for product in products}
        if cv and cv.get("items"):
            for item in cv["items"]:
                if (
                    codes.get(item.get("qcode"))
                    and item.get(MASK_FIELD)
                    and len(str(item[MASK_FIELD])) == 9
                ):
                    value = str(item[MASK_FIELD])
                    for i in range(9):
                        if value[i] == "1":
                            mask[i] = True
    return mask


def validate(sender, item, response, error_fields, **kwargs):
    if item.get("auto_publish"):
        for key in set(error_fields.keys()):
            error_fields.pop(key)
        response.clear()
        return

    products = [
        subject
        for subject in item.get("subject", [])
        if subject.get("scheme") == "products"
    ]
    mask = get_active_mask(products)
    extra = item.get("extra", {})
    length = get_char_count(item.get("body_html") or "<p></p>")

    # allow publishing of headline with update info (1,2,..) over limit
    if (
        item.get("headline")
        and re.search(r"\([0-9]+\)$", item["headline"])
        and len(item["headline"]) <= 64
        and "HEADLINE is too long" in response
    ):
        response.remove("HEADLINE is too long")
        error_fields.pop("headline", None)

    if mask.get(Validators.HEADLINE_REQUIRED):
        if not item.get("headline"):
            response.append("Headline is required")

    if mask.get(Validators.SHORTTITLE_REQUIRED):
        if not extra.get("shorttitle"):
            response.append("Short Title is required")

    if mask.get(Validators.SUBTITLE_REQUIRED):
        if not extra.get("subtitle"):
            response.append("Subtitle is required")

    if mask.get(Validators.SUBJECT_REQUIRED):
        subjects = [
            subject
            for subject in item.get("subject", [])
            if subject.get("scheme") is None
        ]
        if not len(subjects):
            response.append("Subject is required")

    if mask.get(Validators.BODY_LENGTH_512) and length > 512:
        response.append("Body is longer than 512 characters")
    elif mask.get(Validators.BODY_LENGTH_2224) and length > 2224:
        response.append("Body is longer than 2224 characters")
    elif mask.get(Validators.BODY_LENGTH_6400) and length > 6400:
        response.append("Body is longer than 6400 characters")

    associations = item.get("associations") or {}
    pictures = [
        val for val in associations.values() if val and val.get("type") == "picture"
    ]
    gallery = [
        val
        for key, val in associations.items()
        if val and val.get("type") == "picture" and key.startswith(GALLERY)
    ]

    if mask.get(Validators.FEATURED_REQUIRED):
        if not pictures:
            response.append("Photo is required")

    if mask.get(Validators.GALLERY_REQUIRED):
        if not gallery:
            response.append("Photo gallery is required")

    for picture in pictures:
        if (
            picture.get("extra")
            and picture["extra"].get("supplier")
            and picture["extra"]["supplier"].lower() == "afp"
        ):
            response.append(Errors.AFP_IMAGE_USAGE)
            break


def init_app(app):
    item_validate.connect(validate)
