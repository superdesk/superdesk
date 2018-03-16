
import superdesk

from os import path
from lxml import etree
from lxml.etree import SubElement
from flask import current_app as app

from superdesk.publish.formatters.newsml_g2_formatter import NewsMLG2Formatter, XML_LANG


class ANSANewsMLG2Formatter(NewsMLG2Formatter):

    def _format_content(self, article, news_item, nitf):
        """Adds the content set to the xml.

        It outputs content as html doc instead of default nitf.

        :param dict article:
        :param Element newsItem:
        :param Element nitf:
        """
        content_set = etree.SubElement(news_item, 'contentSet')
        inline = etree.SubElement(content_set, 'inlineXML', attrib={'contenttype': 'application/xhtml+xml'})
        inline.append(self._build_html_doc(article))
        self._build_gallery(article, content_set)

    def _build_gallery(self, article, content_set):
        images = []
        for key, val in article.get('associations', {}).items():
            if key != 'featuremedia' and val.get('type') == 'picture':
                images.append(val)

        if images:
            inline = etree.SubElement(content_set, 'inlineXML', attrib=dict(
                contenttype='application/xhtml+xml',
                rendition='gallery'
            ))

            html = etree.SubElement(inline, 'html')
            body = etree.SubElement(html, 'body')
            ul = etree.SubElement(body, 'ul')

            for image in images:
                orig = image.get('renditions', {}).get('original')
                if not orig:
                    continue
                li = etree.SubElement(ul, 'li')
                figure = etree.SubElement(li, 'figure')
                etree.SubElement(figure, 'img', attrib=dict(
                    src=self._publish_media(orig.get('media')),
                    alt=image.get('alt_text', ''),
                    width=orig.get('width', ''),
                    height=orig.get('height', ''),
                ))
                figcaption = etree.SubElement(figure, 'figcaption')
                figcaption.text = image.get('headline', '')

    def _build_html_doc(self, article):
        try:
            html = etree.HTML(article.get('body_html'))
        except etree.XMLSyntaxError:
            html = None
        return html if html is not None else etree.HTML('<p></p>')

    def _format_itemref(self, group, ref, item):
        itemRef = super()._format_itemref(group, ref, item)
        if item.get('body_html'):
            desc = etree.SubElement(itemRef, 'description', attrib={'role': 'drol:teaser'})
            desc.append(self._build_html_doc(item))
        elif item.get('description_text'):
            desc = etree.SubElement(itemRef, 'description', attrib={'role': 'drol:caption'})
            desc.text = item.get('description_text')
        return itemRef

    def can_format(self, format_type, article):
        """Method check if the article can be formatted to NewsML G2 or not.

        :param str format_type:
        :param dict article:
        :return: True if article can formatted else False
        """
        return format_type == 'newsmlg2ansa'

    def _format_content_meta(self, article, content_meta, item):
        super()._format_content_meta(article, content_meta, item)
        self._format_highlights(article, content_meta)

    def _format_highlights(self, article, content_meta):
        """Adds highlights id as subject."""
        names = {}
        for highlight in article.get('highlights', []):
            highlight_id = str(highlight)
            if not names.get(highlight_id):
                names[highlight_id] = superdesk.get_resource_service('highlights') \
                    .find_one(req=None, _id=highlight_id) \
                    .get('name')
            highlight_name = names.get(highlight_id)
            attrib = {'type': 'highlight', 'id': highlight_id}
            subject = SubElement(content_meta, 'subject', attrib=attrib)
            SubElement(subject, 'name').text = highlight_name

    def _format_item_meta(self, article, item_meta, item):
        super()._format_item_meta(article, item_meta, item)
        self._format_related(article, item_meta)

    def _format_related(self, article, item_meta):
        featured = article.get('associations', {}).get('featuremedia')
        if featured:
            orig = featured.get('renditions', {}).get('original')
            if orig:
                SubElement(item_meta, 'link', attrib={
                    'rel': 'irel:seeAlso',
                    'mimetype': orig.get('mimetype', featured.get('mimetype')),
                    'href': self._publish_media(orig.get('media')),
                })

    def _publish_media(self, media):
        binary = app.media.get(media, 'upload')
        if binary:
            filename = '%s.jpg' % str(media)
            for dest in self.subscriber.get('destinations', []):
                if dest.get('config', {}).get('file_path'):
                    file_path = dest['config']['file_path']
                    if not path.isabs(file_path):
                        file_path = "/" + file_path
                    with open(path.join(file_path, filename), 'wb') as output:
                        output.write(binary.read())
                        binary.seek(0)
            return filename

    def _format_subject(self, article, content_meta):
        """Appends the subject element to the contentMeta element

        :param dict article:
        :param Element content_meta:
        """
        if 'subject' in article and len(article['subject']) > 0:
            for s in article['subject']:
                if 'qcode' in s:
                    if ':' in s['qcode']:
                        qcode = s['qcode']
                    else:
                        qcode = '%s:%s' % (s.get('scheme', 'subj'), s['qcode'])
                    subj = SubElement(content_meta, 'subject',
                                      attrib={'type': 'cpnat:abstract', 'qcode': qcode})
                    SubElement(subj, 'name', attrib={XML_LANG: 'en'}).text = s['name']
