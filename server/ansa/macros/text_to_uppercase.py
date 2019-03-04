from .process_html import process_html

"""
    Text to uppercase macro will transform title and body to uppercase
"""


def upper_case(text='', **kwargs):
    return text.upper()


def uppercase_macro(item, **kwargs):
    item['title'] = process_html(item.get('title', ''), upper_case)
    item['body_html'] = process_html(item.get('body_html', ''), upper_case)

    return item


name = 'Text to uppercase'
label = 'Text to uppercase'
callback = uppercase_macro
access_type = 'frontend'
action_type = 'direct'
replace_type = 'keep-style-replace'
