from .process_html import process_html

"""
Format text to 60 chars macro will transform the text from body to have predefined width
"""

WIDTH = 64


def split_text(text='', **kwargs):
    lines = text.split('\n')
    output = []
    words = []

    for i, line in enumerate(lines):
        if len(line) <= WIDTH:
            output.append(line)
        else:
            words = ' '.join(lines[i:]).split(' ')
            break

    text = ''
    for word in words:
        if len(text) + len(word) + 1 > WIDTH:
            output.append(text.strip())
            text = ''
        else:
            text += ' '
        text += word
    if text.strip():
        output.append(text.strip())
    return '\n'.join(output)


def format_text_macro(item, **kwargs):
    item['body_html'] = process_html(item.get('body_html', ''), split_text)

    return item


name = 'Format text to {} chars'.format(WIDTH)
label = 'Format text to {} chars'.format(WIDTH)
callback = format_text_macro
access_type = 'frontend'
action_type = 'direct'
replace_type = 'keep-style-replace'
