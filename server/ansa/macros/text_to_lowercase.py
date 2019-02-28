from .process_html import process_html

"""
    Text to lowercase macro will transform title and body to lowercase
"""


def lower_case(text='', **kwargs):
    return text.lower()


def lowercase_macro(item, **kwargs):
    item['title'] = process_html(item.get('title', ''), lower_case)
    item['body_html'] = process_html(item.get('body_html', ''), lower_case)

    return item


name = 'Text to lowercase'
label = 'Text to lowercase'
callback = lowercase_macro
access_type = 'frontend'
action_type = 'direct'
replace_type = 'keep-style-replace'
