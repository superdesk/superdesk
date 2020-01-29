
from superdesk.etree import parse_html, to_string


def process_html(html, process, **kwargs):
    root = parse_html(html, 'html')

    for elem in root:
        if elem.tag in ('p', 'pre') and elem.text:
            elem.text = process(elem.text, **kwargs)

    return to_string(root, method='html')
