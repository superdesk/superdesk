
import superdesk

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
            if key != 'featuremedia' and val and val.get('type') == 'picture':
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
                    src=self._publish_media(orig),
                    alt=image.get('alt_text', ''),
                    width=str(orig.get('width', '')),
                    height=str(orig.get('height', '')),
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
        self._format_sign_off(article, content_meta)
        self._format_authors(article, content_meta)
        self._format_extra(article, content_meta)
        self._format_sms(article, content_meta)

    def _format_extra(self, article, content_meta):
        extra = article.get('extra', {})

        if extra.get('subtitle'):
            SubElement(content_meta, 'headline', attrib={
                'role': 'hld:subHeadline',
            }).text = extra['subtitle']

        if extra.get('shorttitle'):
            SubElement(content_meta, 'headline', attrib={
                'role': 'hld:shortHeadline',
            }).text = extra['shorttitle']

    def _format_sms(self, article, content_meta):
        if article.get('sms_message'):
            SubElement(content_meta, 'headline', attrib={
                'role': 'hld:sms',
            }).text = article['sms_message']

    def _format_authors(self, article, content_meta):
        for author in article.get('authors', []):
            if author.get('parent'):
                user = superdesk.get_resource_service('users').find_one(req=None, _id=author['parent'])
                if user:
                    creator = SubElement(content_meta, 'contributor', attrib={'literal': user.get('sign_off', '')})
                    SubElement(creator, 'name').text = user.get('display_name', author.get('name', ''))

    def _format_creator(self, article, content_meta):
        if article.get('byline'):
            SubElement(content_meta, 'by').text = article['byline']

    def _format_sign_off(self, article, content_meta):
        if article.get('sign_off'):
            SubElement(content_meta, 'creator', attrib={
                'literal': article['sign_off'],
            })

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
                    'href': self._publish_media(orig),
                })

    def _publish_media(self, rendition):
        if rendition.get('href'):
            return rendition['href']
        if rendition.get('media'):
            return app.media.url_for_media(rendition['media'])
        return ''

    def _format_subject(self, article, content_meta):
        """Appends the subject element to the contentMeta element

        :param dict article:
        :param Element content_meta:
        """
        if 'subject' in article and len(article['subject']) > 0:
            for s in article['subject']:
                if s.get('scheme') == 'products' and s.get('qcode'):
                    subj = SubElement(content_meta, 'subject', attrib={
                        'qcode': 'products:%s' % s['qcode'],
                    })

                    SubElement(subj, 'name', attrib={XML_LANG: 'it'}).text = s['name']
                elif 'qcode' in s:
                    if ':' in s['qcode']:
                        qcode = s['qcode']
                    else:
                        qcode = '%s:%s' % (s.get('scheme', 'subj'), s['qcode'])
                    subj = SubElement(content_meta, 'subject',
                                      attrib={'type': 'cpnat:abstract', 'qcode': qcode})
                    SubElement(subj, 'name', attrib={XML_LANG: 'en'}).text = s['name']

    def _format_located(self, article, content_meta):
        """Appends the located element to the contentMeta element

        :param dict article:
        :param Element content_meta:
        """
        located = article.get('dateline', {}).get('located', {})
        if located and located.get('city'):
            located_elm = SubElement(content_meta, 'located',
                                     attrib={'qcode': 'city:%s' % located.get('city').upper()})
            if located.get('state'):
                SubElement(located_elm, 'broader', attrib={'qcode': 'reg:%s' % located['state']})
            if located.get('country'):
                SubElement(located_elm, 'broader', attrib={'qcode': 'cntry:%s' % located['country'].upper()})

        if article.get('dateline', {}).get('text', {}):
            SubElement(content_meta, 'dateline').text = article.get('dateline', {}).get('text', {})
