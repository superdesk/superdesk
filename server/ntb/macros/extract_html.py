"""
    Delete from body_html all html tags except links
"""
from bs4 import BeautifulSoup


def npk_metadata_macro(item, **kwargs):
    if 'body_html' not in item:
        return None

    soup = BeautifulSoup(item['body_html'], "html.parser")

    links = {}
    count = 0
    # extract all links and add them to a dictionary with a unique
    # generated key for every link
    for a in soup.findAll('a'):
        links['__##link' + str(count) + '##__'] = str(a)
        count = count + 1

    # replace all text links with the generated keys
    # regenerate html back from soup in order to avoid issues
    # on link replacements where are used text links generated from soup
    body_html = str(soup)
    for link in links:
        body_html = body_html.replace(links[link], link)

    # extract text from the html that don't contains any link,
    # it just contains link keys that are not affected by text extraction
    # because they are already text
    soup = BeautifulSoup(body_html, "html.parser")
    body_html = soup.text

    # in extracted text replace the link keys with links
    for link in links:
        body_html = body_html.replace(link, links[link])

    item['body_html'] = body_html
    return item


name = 'Extract Html Macro'
label = 'Extract Html Macro'
callback = npk_metadata_macro
access_type = 'frontend'
action_type = 'direct'
