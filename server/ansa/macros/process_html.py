from bs4 import BeautifulSoup


def process_html(html, process):
    soup = BeautifulSoup(html, 'html.parser')

    for paragraph in soup.find_all('p'):
        for text in paragraph._all_strings():
            new_text = process(text)
            html = html.replace(text, new_text)

    return html
