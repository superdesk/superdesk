import re
import superdesk
import logging
import requests

from enum import IntEnum
from superdesk.text_utils import get_char_count
from superdesk.signals import item_validate
from ansa.constants import GALLERY

MASK_FIELD = "output_code"

logger = logging.getLogger(__name__)


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
    PRODUCT_ALLOWED = 9


class Errors:
    AFP_IMAGE_USAGE = "AFP images could not be used"
    IMAGE_NOT_FOUND = "Image not found"
    IMAGE_RENDITION_NOT_FOUND = "Image rendition not found"
    XINHUA_IMAGE_USAGE = "XINHUA IMAGES could not be used"


def is_user_external(user):
    role = get_user_role(user)
    return role and role.get('name') == 'Ext'


def get_user_role(user):
    return (
        superdesk.get_resource_service('roles').find_one(req=None, _id=user['role'])
        if user.get('role')
        else None
    )


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
                    and len(str(item[MASK_FIELD])) >= 9
                ):
                    value = str(item[MASK_FIELD])
                    for i in range(len(str(item[MASK_FIELD]))):
                        if value[i] == "1":
                            mask[i] = True
    return mask


def url_exists(url):
    infourl = url.replace("binfilebymd5", "infofilebymd5")
    resp = requests.get(infourl, timeout=5)
    return resp.status_code == requests.codes.ok and "errors" not in resp.text


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
    try:
        sign_off_author = (item['sign_off']).split('/')[0]
        user = superdesk.get_resource_service('users').find_one(
            req=None, username=sign_off_author
        )
    except KeyError:
        user = None
    desk = superdesk.get_resource_service('desks').find_one(
        req=None, _id=item['task']['desk']
    )

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

    if user and is_user_external(user) and not mask.get(Validators.PRODUCT_ALLOWED):
        response.append("Products not allowed to external User")

    for picture in pictures:
        if (
            picture.get("extra")
            and picture["extra"].get("supplier")
            and picture["extra"]["supplier"].lower() == "afp"
        ):
            response.append(Errors.AFP_IMAGE_USAGE)
            break

        if (
            picture.get("extra")
            and picture["extra"].get("supplier")
            and picture["extra"]["supplier"].lower() == "xinhua"
            and "TAP" not in desk['name']
        ):
            response.append(Errors.XINHUA_IMAGE_USAGE)
            break

        if picture.get("renditions", {}).get("original", {}).get("href"):
            if not url_exists(picture["renditions"]["original"]["href"]):
                response.append(
                    "{}. Image: {}".format(
                        Errors.IMAGE_NOT_FOUND,
                        picture.get("headline", picture.get("_id", "")),
                    )
                )
                break
        else:
            response.append(
                "{}. Image: {}".format(
                    Errors.IMAGE_RENDITION_NOT_FOUND,
                    picture.get("headline", picture.get("_id", "")),
                )
            )
            break


def init_app(app):
    item_validate.connect(validate)
