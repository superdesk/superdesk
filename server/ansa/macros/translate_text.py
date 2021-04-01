import json
import requests
from flask import current_app as app
from .process_html import process_html
from superdesk.editor_utils import generate_fields, TEXT_FIELDS

"""
    Translate text from body_html
"""

FIELDS = ('headline', 'slugline', 'abstract', 'body_html', 'description_text', 'extra>subtitle')

sess = requests.Session()


def translate(text='', **kwargs):
    URL_TRANSLATION = app.config["ANSA_TRANSLATION_URL"]
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'text': text,
        'lang': kwargs.get('lang', 'en'),
        'target': kwargs.get('target', 'it')
    }

    if not text:
        return text

    try:
        result = sess.post(URL_TRANSLATION, data=data, headers=headers, timeout=(5, 30))
        response = json.loads(result.text)
        return response.get('translatedtext', text)
    except requests.exceptions.ReadTimeout:
        return text


def translate_text_macro(item, **kwargs):
    lang = 'en' if item.get('language', 'en') == 'en' else 'it'
    target = 'it' if lang == 'en' else 'en'

    lang = kwargs.get('from_language', lang)
    target = kwargs.get('to_language', target)

    for field in FIELDS:
        if item.get(field):
            item[field] = process_html(item[field], translate, lang=lang, target=target)
        elif 'extra>' in field:
            extra_field = field.replace('extra>', '')
            if item.get('extra') and item['extra'].get(extra_field):
                item['extra'][extra_field] = process_html(
                    item['extra'][extra_field],
                    translate, lang=lang, target=target)
            if field not in TEXT_FIELDS:  # needed for generate fields later
                TEXT_FIELDS.append(field)

    generate_fields(item, FIELDS, force=True)

    return item


name = 'Translate text'
label = 'Translate text'
callback = translate_text_macro
access_type = 'backend'
action_type = 'direct'
replace_type = 'simple-replace'
from_languages = ['it', 'en', 'es', 'pt', 'de', 'ar']
to_languages = ['it', 'en', 'es', 'pt', 'de', 'ar']
