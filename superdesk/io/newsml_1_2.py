import datetime
from ..etree import etree
from superdesk.io import Parser


class NewsMLOneParser(Parser):
    """NewsMl xml 1.2 parser"""

    def parse_message(self, tree):
        """Parse NewsMessage."""
        item = {}
        self.root = tree

        parsed_el = tree.find('NewsItem/NewsComponent/AdministrativeMetadata/Source')
        if parsed_el is not None:
            item['original_source'] = parsed_el.find('Party').get('FormalName', '')

        parsed_el = tree.find('NewsEnvelope/TransmissionId')
        if parsed_el is not None:
            item['ingest_provider_sequence'] = parsed_el.text

        self.parse_news_identifier(item, tree)
        self.parse_newslines(item, tree)
        self.parse_news_management(item, tree)

        parsed_el = tree.findall('NewsItem/NewsComponent/DescriptiveMetadata/Language')
        if parsed_el is not None:
            language = self.parse_attributes_as_dictionary(parsed_el)
            item['language'] = language[0]['FormalName'] if len(language) else ''

        keywords = tree.findall('NewsItem/NewsComponent/DescriptiveMetadata/Property')
        item['keywords'] = self.parse_attribute_values(keywords, 'Keyword')

        subjects = tree.findall('NewsItem/NewsComponent/DescriptiveMetadata/SubjectCode/SubjectDetail')
        subjects += tree.findall('NewsItem/NewsComponent/DescriptiveMetadata/SubjectCode/SubjectMatter')
        subjects += tree.findall('NewsItem/NewsComponent/DescriptiveMetadata/SubjectCode/Subject')

        item['Subjects'] = self.parse_attributes_as_dictionary(subjects)

        # item['ContentItem'] = self.parse_attributes_as_dictionary(
        #    tree.find('NewsItem/NewsComponent/ContentItem'))
        # item['Content'] = etree.tostring(
        # tree.find('NewsItem/NewsComponent/ContentItem/DataContent/nitf/body/body.content'))

        item['body_html'] = etree.tostring(
            tree.find('NewsItem/NewsComponent/ContentItem/DataContent/nitf/body/body.content'))

        parsed_el = tree.findall('NewsItem/NewsComponent/ContentItem/Characteristics/Property')
        characteristics = self.parse_attribute_values(parsed_el, 'Words')
        item['word_count'] = characteristics[0] if len(characteristics) else None

        parsed_el = tree.find('NewsItem/NewsComponent/RightsMetadata/UsageRights/UsageType')
        if parsed_el is not None:
            item.setdefault('usageterms', parsed_el.text)

        return self.populate_fields(item)

    def parse_elements(self, tree):
        items = {}
        for item in tree:
            if item.text is None:
                # read the attribute for the item
                if item.tag != 'HeadLine':
                    items[item.tag] = item.attrib
            else:
                # read the value for the item
                items[item.tag] = item.text
        return items

    def parse_multivalued_elements(self, tree):
        items = {}
        for item in tree:
            if item.tag not in items:
                items[item.tag] = [item.text]
            else:
                items[item.tag].append(item.text)

        return items

    def parse_attributes_as_dictionary(self, items):
        attributes = [item.attrib for item in items]
        return attributes

    def parse_attribute_values(self, items, attribute):
        attributes = []
        for item in items:
            if item.attrib['FormalName'] == attribute:
                attributes.append(item.attrib['Value'])
        return attributes

    def datetime(self, string):
        return datetime.datetime.strptime(string, '%Y%m%dT%H%M%S+0000')

    def populate_fields(self, item):
        item['type'] = 'text'
        item['subject'] = item['Subjects']
        return item

    def parse_news_identifier(self, item, tree):
        parsed_el = self.parse_elements(tree.find('NewsItem/Identification/NewsIdentifier'))
        item['guid'] = parsed_el['PublicIdentifier']
        item['version'] = parsed_el['RevisionId']

    def parse_news_management(self, item, tree):
        parsed_el = self.parse_elements(tree.find('NewsItem/NewsManagement'))
        item['urgency'] = parsed_el['Urgency']['FormalName']
        item['versioncreated'] = self.datetime(parsed_el['ThisRevisionCreated'])
        item['firstcreated'] = self.datetime(parsed_el['FirstCreated'])
        item['pubstatus'] = parsed_el['Status']['FormalName']
        # if parsed_el['NewsItemType']['FormalName'] == 'Alert':
        #    parsed_el['headline'] = 'Alert'

    def parse_newslines(self, item, tree):
        parsed_el = self.parse_elements(tree.find('NewsItem/NewsComponent/NewsLines'))
        item['headline'] = parsed_el.get('HeadLine', '')
        item['dateline'] = parsed_el.get('DateLine', '')
        item['slugline'] = parsed_el.get('SlugLine', '')
        item['byline'] = parsed_el.get('ByLine', '')

