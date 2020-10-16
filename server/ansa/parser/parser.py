import json
import arrow

from superdesk.io.feed_parsers.newsml_2_0 import NewsMLTwoFeedParser
from superdesk.text_utils import get_word_count
from ansa.analysis.analysis import parse, apply
from superdesk import get_resource_service
from ansa.geonames import get_place_by_id
from superdesk.utc import local_to_utc
from ansa.constants import PHOTO_CATEGORIES_ID, FEATURED, GALLERY, ROME_TZ

MONTHS_IT = [
    '',
    'gen',
    'feb',
    'mar',
    'apr',
    'mag',
    'giu',
    'lug',
    'ago',
    'set',
    'ott',
    'nov',
    'dic',
]


def get_text(elem):
    try:
        return getattr(elem, 'text').strip()
    except AttributeError:
        return ''


def get_literal(elem):
    try:
        return elem.attrib['literal'].strip()
    except (AttributeError, KeyError):
        return ''


class ANSAParser(NewsMLTwoFeedParser):

    cat_map = {
        'ACE': 'Entertainment',
        'CLJ': 'Chronicle',
        'DIS': 'Chronicle',
        'FIN': 'Business',
        'EDU': 'Chronicle',
        'ENV': 'Chronicle',
        'HTH': 'Chronicle',
        'HUM': 'Chronicle',
        'LAB': 'Chronicle',
        'LIF': 'Entertainment',
        'REL': 'Chronicle',
        'SCI': 'Chronicle',
        'SOI': 'Chronicle',
        'WAR': 'Chronicle',
        'WEA': 'Chronicle',
        'SPR': 'Sport',
        'SPO': 'Sport',
        'POL': 'Politics',
        'CRO': 'Chronicle',
        'SPE': 'Entertainment',
        'EST': 'WORLD',
        'ECO': 'Business',
        'PEC': 'Business',
    }

    def parse_content_meta(self, tree, item):
        super().parse_content_meta(tree, item)
        meta = tree.find(self.qname('contentMeta'))

        headlines = meta.findall(self.qname('headline'))
        for headline in headlines:
            if headline.get('role') == 'hld:subHeadline':
                item.setdefault('extra', {})['subtitle'] = headline.text

        subjects = meta.findall(self.qname('subject'))
        for subject in subjects:
            if subject.get('type') == 'cptype:cat':
                if not item.get('subject'):
                    item['subject'] = []
                code = subject.get('literal')
                if item.get('type') != 'picture':
                    item['subject'].append(
                        {'name': code, 'qcode': code, 'scheme': 'FIEG_Categories'}
                    )
                else:
                    item['subject'].append(
                        {'name': code, 'qcode': code, 'scheme': PHOTO_CATEGORIES_ID}
                    )
                name = self.cat_map.get(code)
                if name:
                    item['anpa_category'] = [{'name': name, 'qcode': name.lower()}]
            elif subject.get('type') == 'cptType:5':
                item.setdefault('extra', {})['city'] = subject.get('literal')
                broader = subject.find(self.qname('broader'))
                if broader is not None and broader.find(self.qname('name')) is not None:
                    item['extra']['nation'] = broader.find(self.qname('name')).text

        if item.get('description_text'):
            item['description_text'] = item['description_text'].strip()

        descriptions = meta.findall(self.qname('description'))
        for description in descriptions:
            if description.get('role') == 'semantics':
                try:
                    semantics = parse(json.loads(description.text))
                    apply(semantics, item)
                except ValueError:
                    pass

        creditline = meta.find(self.qname('creditline'))
        if creditline is not None:
            item['creditline'] = creditline.text

        located = meta.find(self.qname('located'))
        if located is not None and located.get('qcode'):
            code = located.get('qcode')
            if code and 'geo:' in code and code.replace('geo:', '').strip():
                place = get_place_by_id(code.replace('geo:', ''))
                item.setdefault('dateline', {})
                item.setdefault('semantics', {})
                item['dateline']['located'] = {
                    "tz": place.get('tz', ROME_TZ),
                    "country_code": place.get('country_code'),
                    "dateline": "city",
                    "city_code": place.get('name'),
                    "state": place.get('state'),
                    "alt_name": "",
                    "state_code": place.get('state_code'),
                    "country": place.get('country'),
                    "city": place.get('name'),
                    "place": place,
                }

                time = item.get('firstcreated')
                if time:
                    item['dateline']['date'] = time
                    item['dateline']['text'] = '%s, %d %s' % (
                        place.get('name', '').upper(),
                        int(time.strftime('%d')),
                        MONTHS_IT[time.month].upper(),
                    )
        keywords = meta.findall(self.qname('keyword'))
        for keyword in keywords:
            if keyword.text and keyword.text.strip():
                item.setdefault('keywords', []).append(keyword.text.strip())

    def parse_authors(self, meta, item):
        creator = meta.find(self.qname('creator'))
        if creator is not None and creator.get('literal'):
            item['sign_off'] = creator.get('literal').upper()
            item.setdefault('extra', {})['Autore'] = creator.get('literal').upper()

        contribs = meta.findall(self.qname('contributor'))
        for contrib in contribs:
            name = contrib.find(self.qname('name'))
            role = contrib.get('role')
            if name is None or not role:
                continue
            if contrib.get('role') == 'ctrol:descrWriter':
                item.setdefault('extra', {})['Digitatore'] = name.text
            if contrib.get('role') == 'ansactrol:co-author':
                item.setdefault('extra', {})['Co-Autore'] = name.text
                if item.get('sign_off'):
                    item['sign_off'] += '-' + name.text.upper()
                else:
                    item['sign_off'] = name.text.upper()

    def parse_item(self, tree):
        item = super().parse_item(tree)
        if item.get('word_count') == 0 and item.get('type') == 'text':
            item['word_count'] = get_word_count(item.get('body_html', '<p></p>'))
        item['guid'] = tree.attrib['guid']
        item.setdefault('extra', {})['ansaid'] = item['guid']
        return item

    def datetime(self, string):
        local = arrow.get(string).datetime
        return local_to_utc(ROME_TZ, local)

    def parse_content_subject(self, tree, item):
        super().parse_content_subject(tree, item)
        for subject in tree.findall(self.qname('subject')):
            qcode_parts = subject.get('qcode', '').split(':')
            if len(qcode_parts) == 2 and qcode_parts[0] == 'products':
                name = subject.find(self.qname('name'))
                item['subject'].append(
                    {
                        'scheme': qcode_parts[0],
                        'qcode': qcode_parts[1],
                        'name': name.text if name is not None else qcode_parts[1],
                    }
                )

    def parse_rights_info(self, tree, item):
        """Parse Rights Info tag"""
        info = tree.find(self.qname('rightsInfo'))
        if info is not None:
            item['usageterms'] = get_text(info.find(self.qname('usageTerms')))
            item['copyrightholder'] = get_literal(
                info.find(self.qname('copyrightHolder'))
            )
            item['copyrightnotice'] = get_text(info.find(self.qname('copyrightNotice')))
        if item.get('creditline'):
            item.setdefault('copyrightholder', item['creditline'])
        if (
            item.get('copyrightholder')
            and not item.get('copyrightnotice')
            or not item.get('usageterms')
        ):
            cv = get_resource_service('vocabularies').find_one(
                req=None, _id='rightsinfo'
            )
            if cv:
                for rightsinfo in cv.get('items', []):
                    if (
                        rightsinfo.get('copyrightHolder', '').lower()
                        == item['copyrightholder'].lower()
                    ):
                        if rightsinfo.get('copyrightNotice') and not item.get(
                            'copyrightnotice'
                        ):
                            item['copyrightnotice'] = rightsinfo['copyrightNotice']
                        if rightsinfo.get('usageTerms') and not item.get('usageterms'):
                            item['usageterms'] = rightsinfo['usageTerms']
                        break

    def parse_item_meta(self, tree, item):
        super().parse_item_meta(tree, item)
        meta = tree.find(self.qname('itemMeta'))

        provider = meta.find(self.qname('provider'))
        if provider is not None and provider.get('literal'):
            item.setdefault('extra', {})['supplier'] = provider.get('literal')

        self.parse_links(meta, item)

    def parse_links(self, meta, item):
        """Parse links to pictures and populate associations."""
        links = meta.findall(self.qname('link'))
        for link in links:
            if (
                link.get('residref')
                and link.get('rel')
                and link.get('rel') in (FEATURED, GALLERY)
            ):
                item.setdefault('associations', {})
                dest = FEATURED
                if link.get('rel') == GALLERY:
                    counter = 1
                    for key in item['associations']:
                        if key.startswith(GALLERY):
                            counter += 1
                    dest = '{}--{}'.format(GALLERY, counter)
                item['associations'][dest] = {'residRef': link.get('residref')}
                title = link.find(self.qname('title'))
                if title is not None and title.text:
                    item['associations'][dest]['description_text'] = title.text

    def getVocabulary(self, voc_id, qcode, name):
        """Use name from xml."""
        return name
