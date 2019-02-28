from .process_html import process_html

"""
    Format text to 60 chars macro will transform the text from body to have max 60 chars width
"""


def split_text(text='', **kwargs):
    width = 60
    new_text = ''
    space = ''
    length = 0

    words = text.split(' ')
    for word in words:
        if length + len(word) > width or length == 0 and len(word) > width:
            length = 0
            new_text = new_text + '\n'
            space = ''

        length = length + len(word)
        new_text = new_text + space + word
        space = ' '

    return new_text


def format_text_macro(item, **kwargs):
    item['body_html'] = process_html(item.get('body_html', ''), split_text)

    return item


name = 'Format text to 60 chars'
label = 'Format text to 60 chars'
callback = format_text_macro
access_type = 'frontend'
action_type = 'direct'
replace_type = 'keep-style-replace'
