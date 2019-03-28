from bs4 import BeautifulSoup


def process_html(html, process, **kwargs):
    soup = BeautifulSoup(html, 'html.parser')

    for paragraph in soup.find_all('p'):
        for text in paragraph._all_strings():
            new_text = process(text, **kwargs)
            html = html.replace(text, new_text)

    if not soup.find_all('p'):  # not html field
        html = process(soup.text, **kwargs)

    return html
