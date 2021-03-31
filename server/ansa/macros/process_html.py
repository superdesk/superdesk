
from superdesk.etree import parse_html, to_string


def process_html(html, process, **kwargs):
    if '<p' not in html:  # text field
        return process(html, **kwargs)

    root = parse_html(html, 'html')

    for elem in root:
        if elem.tag in ('p', 'pre') and elem.text:
            text = "".join(elem.itertext())
            for child in elem:
                elem.remove(child)
            elem.text = process(text, **kwargs)

    return to_string(root, method='html')
