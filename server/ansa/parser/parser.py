
import json
import arrow

from superdesk.io.feed_parsers.newsml_2_0 import NewsMLTwoFeedParser
from superdesk.text_utils import get_word_count
from ansa.analysis.analysis import parse, apply
from superdesk import get_resource_service


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
                item['extra'] = {
                    'subtitle': headline.text,
                }

        subjects = meta.findall(self.qname('subject'))
        for subject in subjects:
            if subject.get('type') == 'cptype:cat':
                name = self.cat_map.get(subject.get('literal'))
                if name:
                    item['anpa_category'] = [{'name': name, 'qcode': name.lower()}]

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

    def parse_item(self, tree):
        item = super().parse_item(tree)
        if item.get('word_count') == 0 and item.get('type') == 'text':
            item['word_count'] = get_word_count(item.get('body_html', '<p></p>'))
        return item

    def datetime(self, string):
        return arrow.get(string).datetime

    def parse_content_subject(self, tree, item):
        super().parse_content_subject(tree, item)
        for subject in tree.findall(self.qname('subject')):
            qcode_parts = subject.get('qcode', '').split(':')
            if len(qcode_parts) == 2 and qcode_parts[0] == 'products':
                name = subject.find(self.qname('name'))
                item['subject'].append({
                    'scheme': qcode_parts[0],
                    'qcode': qcode_parts[1],
                    'name': name.text if name is not None else qcode_parts[1],
                })

    def parse_rights_info(self, tree, item):
        """Parse Rights Info tag"""
        info = tree.find(self.qname('rightsInfo'))
        if info is not None:
            item['usageterms'] = getattr(info.find(self.qname('usageTerms')), 'text', '').strip()
            item['copyrightholder'] = info.find(self.qname('copyrightHolder')).attrib['literal']
            item['copyrightnotice'] = getattr(info.find(self.qname('copyrightNotice')), 'text', None)
        if item.get('creditline'):
            item.setdefault('copyrightholder', item['creditline'])
        if item.get('copyrightholder') and not item.get('copyrightnotice') or not item.get('usageterms'):
            cv = get_resource_service('vocabularies').find_one(req=None, _id='rightsinfo')
            if cv:
                for rightsinfo in cv.get('items', []):
                    if rightsinfo.get('copyrightHolder', '').lower() == item['copyrightholder'].lower():
                        if rightsinfo.get('copyrightNotice') and not item.get('copyrightnotice'):
                            item['copyrightnotice'] = rightsinfo['copyrightNotice']
                        if rightsinfo.get('usageTerms') and not item.get('usageterms'):
                            item['usageterms'] = rightsinfo['usageTerms']
                        break
