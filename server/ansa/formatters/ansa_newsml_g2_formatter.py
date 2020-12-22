import arrow
import superdesk

from lxml import etree
from lxml.etree import SubElement
from flask import current_app as app
from babel.dates import format_datetime, get_timezone

from superdesk.publish.formatters.newsml_g2_formatter import NewsMLG2Formatter, XML_LANG
from superdesk.text_utils import get_text
from superdesk.logging import logger

from superdesk import get_resource_service

CONTRIBUTOR_MAPPING = {
    'digitator': 'descrWriter',
    'coauthor': 'coAuthor',
    'supplier': 'supplier',
}


def is_user_journalist(user):
    role = get_user_role(user)
    return role and (role.get('name') == 'Gio' or role.get('name') == 'CoG')


def is_user_producer(user):
    role = get_user_role(user)
    return role and role.get('name') == 'Pro'


def get_user_role(user):
    return (
        get_resource_service('roles').find_one(req=None, _id=user['role'])
        if user.get('role')
        else None
    )


class ANSAPlainTextNewsMLG2Formatter(NewsMLG2Formatter):

    DATETIME_USE_CURRENT_TIME = True

    def _format_content(self, article, news_item, nitf):
        """Adds the content set to the xml.

        It outputs content as html doc instead of default nitf.

        :param dict article:
        :param Element newsItem:
        :param Element nitf:
        """
        content_set = etree.SubElement(news_item, 'contentSet')
        if article.get('body_html'):
            inline = etree.SubElement(
                content_set,
                'inlineXML',
                attrib={'contenttype': 'application/xhtml+xml'},
            )
            inline.append(self._build_html_doc(article))
        self._build_gallery(article, content_set)

    def _build_gallery(self, article, content_set):
        images = []
        for key, val in article.get('associations', {}).items():
            if key != 'featuremedia' and val and val.get('type') == 'picture':
                images.append(val)

        if images:
            inline = etree.SubElement(
                content_set,
                'inlineXML',
                attrib=dict(contenttype='application/xhtml+xml', rendition='gallery'),
            )

            html = etree.SubElement(inline, 'html')
            body = etree.SubElement(html, 'body')
            ul = etree.SubElement(body, 'ul')

            for image in images:
                orig = image.get('renditions', {}).get('original')
                if not orig:
                    continue
                li = etree.SubElement(ul, 'li')
                figure = etree.SubElement(li, 'figure')
                etree.SubElement(
                    figure,
                    'img',
                    attrib=dict(
                        src=self._publish_media(orig),
                        alt=image.get('alt_text', ''),
                        width=str(orig.get('width', '')),
                        height=str(orig.get('height', '')),
                    ),
                )
                figcaption = etree.SubElement(figure, 'figcaption')
                figcaption.text = image.get('headline', '')

    def _build_html_doc(self, article):
        try:
            content = article.get('body_html')
            preformatted = '<pre>' in content
            if not preformatted:
                content = article.get('body_html').replace('<br/>\n', '\n')
            html = etree.HTML(content)
            plaintext = "".join(html.itertext())
            if preformatted:
                html = etree.HTML('<pre>\n%s</pre>' % plaintext)
            else:
                html = etree.HTML('<pre>%s</pre>' % plaintext)
        except (etree.XMLSyntaxError, ValueError):
            if article.get('body_html'):
                logger.exception('XML parsing error')
            html = None
        return (
            html
            if html is not None
            else etree.HTML('<p>%s</p>' % article.get('headline') or '')
        )

    def _format_itemref(self, group, ref, item):
        itemRef = super()._format_itemref(group, ref, item)
        if item.get('body_html'):
            desc = etree.SubElement(
                itemRef, 'description', attrib={'role': 'drol:teaser'}
            )
            desc.append(self._build_html_doc(item))
        elif item.get('description_text'):
            desc = etree.SubElement(
                itemRef, 'description', attrib={'role': 'drol:caption'}
            )
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
        self._format_semantics(article, content_meta)
        self._format_keywords(article, content_meta)
        self._format_alt_text(article, content_meta)
        self._format_headline(article, content_meta)

    def _format_headline(self, article, content_meta):
        """Appends the headline element to the contentMeta element

        :param dict article:
        :param Element content_meta:
        """
        hl = article.get('headline', '').strip()
        p = article.get('priority', 4)
        if p == 2 and '+++' not in hl and '++' in hl:
            hl = '++ {} ++'.format(hl.replace('++', '').strip())

        # p=article.get('priority', 4)
        # if p == 2 and not '++' in hl:
        #    hl = '++ {} ++'.format(hl.strip())

        SubElement(content_meta, 'headline').text = hl

    def _format_alt_text(self, article, content_meta):
        if article.get('alt_text'):
            SubElement(
                content_meta, 'description', {'role': 'drol:altText'}
            ).text = article['alt_text']

    def _format_extra(self, article, content_meta):
        extra = article.get('extra', {})

        if extra.get('subtitle'):
            SubElement(
                content_meta,
                'headline',
                attrib={
                    'role': 'hld:subHeadline',
                },
            ).text = get_text(extra['subtitle'])

        if extra.get('shorttitle'):
            SubElement(
                content_meta,
                'headline',
                attrib={
                    'role': 'hld:shortHeadline',
                },
            ).text = get_text(extra['shorttitle'])

        for field, role in CONTRIBUTOR_MAPPING.items():
            if extra.get(field):
                elem = SubElement(
                    content_meta, 'contributor', {'role': 'ctrol:{}'.format(role)}
                )
                SubElement(elem, 'name').text = extra[field]

    def _format_sms(self, article, content_meta):
        if article.get('sms_message'):
            SubElement(
                content_meta,
                'headline',
                attrib={
                    'role': 'hld:sms',
                },
            ).text = article['sms_message']

    def _format_authors(self, article, content_meta):
        for author in article.get('authors', []):
            if author.get('parent'):
                user = superdesk.get_resource_service('users').find_one(
                    req=None, _id=author['parent']
                )
                if user:
                    creator = SubElement(
                        content_meta,
                        'contributor',
                        attrib={
                            'literal': user.get('sign_off', ''),
                            'role': 'ansactrol:{}'.format(
                                author.get('role') or 'writer'
                            ),
                        },
                    )
                    SubElement(creator, 'name').text = user.get(
                        'display_name', author.get('name', '')
                    )
            elif author.get('role') and author.get('sub_label'):
                contrib = SubElement(
                    content_meta,
                    'contributor',
                    attrib={
                        'literal': author.get('sub_label'),
                        'role': 'ansactrol:{}'.format(author.get('role')),
                    },
                )
                SubElement(contrib, 'name').text = author.get('sub_label')

    def _format_creator(self, article, content_meta):
        if article.get('byline'):
            SubElement(content_meta, 'by').text = article['byline']

    def _format_sign_off_sd(self, article, content_meta):
        if article.get('sign_off'):
            sd_sign_off = article['sign_off']

            if '-' not in sd_sign_off:
                author_sign = sd_sign_off.split('/')[0]
            else:
                author_sign = sd_sign_off.split('-')[0]

            author = get_resource_service('users').find_one(
                req=None, username=author_sign
            )

            xawes_sign_off = sd_sign_off.split('/')[0]
            """if  '/' in sd_sign_off:
                publisher = sd_sign_off.rsplit('/', 1)[1]
                if publisher.strip() and author and is_user_journalist(author):
                    xawes_sign_off += '/' + publisher.strip()
                else:
                    if '-' not in sd_sign_off:
                       xawes_sign_off += '-' + publisher.strip()
                    else:
                       xawes_sign_off += '/' + publisher.strip()
            """
            if '-' not in xawes_sign_off and '/' in sd_sign_off:
                publisher = sd_sign_off.rsplit('/', 1)[1]

                if not author or (
                    publisher.strip()
                    and author
                    and not is_user_journalist(author)
                    and not is_user_producer(author)
                ):
                    xawes_sign_off += '-' + publisher.strip()
                    xawes_sign_off = xawes_sign_off.strip('-/')

            if '-' not in xawes_sign_off and author and is_user_producer(author):
                xawes_sign_off = 'RED/' + xawes_sign_off.strip()

            SubElement(
                content_meta,
                'creator',
                attrib={
                    'literal': xawes_sign_off.upper(),
                },
            )

    def _format_sign_off_xawes(self, article, content_meta):
        extra = article.get('extra', {})
        if article.get('sign_off'):
            sd_sign_off = article['sign_off'].split('/')[0]
            try:
                author = get_text(extra['Autore']) or sd_sign_off
            except KeyError:
                author = sd_sign_off
            xawes_sign_off = author
            try:
                coauthor = get_text(extra['Co-Autore'])
                xawes_sign_off += "-" + coauthor
            except KeyError:
                pass
            try:
                digitator = get_text(extra['Digitatore'])
                xawes_sign_off += "/" + digitator
            except KeyError:
                pass
            SubElement(
                content_meta,
                'creator',
                attrib={
                    'literal': xawes_sign_off.upper(),
                },
            )

    def _format_sign_off(self, article, content_meta):
        profile = None
        if article.get('profile'):
            profile = get_resource_service('content_types').find_one(
                req=None, _id=article['profile']
            )
        if profile and profile['editor'].get('Autore'):
            self._format_sign_off_xawes(article, content_meta)
        else:
            self._format_sign_off_sd(article, content_meta)

    def _format_highlights(self, article, content_meta):
        """Adds highlights id as subject."""
        names = {}
        for highlight in article.get('highlights', []):
            highlight_id = str(highlight)
            if not names.get(highlight_id):
                names[highlight_id] = (
                    superdesk.get_resource_service('highlights')
                    .find_one(req=None, _id=highlight_id)
                    .get('name')
                )
            highlight_name = names.get(highlight_id)
            attrib = {'type': 'highlight', 'id': highlight_id}
            subject = SubElement(content_meta, 'subject', attrib=attrib)
            SubElement(subject, 'name').text = highlight_name

    def _format_item_meta(self, article, item_meta, item):
        super()._format_item_meta(article, item_meta, item)
        self._format_related(article, item_meta)
        self._format_desk(article, item_meta)
        self._format_source(article, item_meta)
        self._format_to(article, item_meta)
        self._format_update_notice(article, item_meta)

    def _format_source(self, article, item_meta):
        try:
            source = article['extra']['HeadingNews']
        except KeyError:
            source = '(ANSA)'
        etree.SubElement(item_meta, 'signal', {'qcode': 'source:{}'.format(source)})

    def _format_to(self, article, item_meta):
        try:
            to = article['extra']['EMAIL_TO'] or ''
        except KeyError:
            to = ''
        signal = etree.SubElement(item_meta, 'signal', {'qcode': 'mail:to'})
        SubElement(signal, 'name').text = to

    def _format_update_notice(self, article, item_meta):
        try:
            update_notice = article['extra']['update_notice'] or ''
        except KeyError:
            update_notice = ''
        signal = etree.SubElement(item_meta, 'signal', {'qcode': 'update_notice'})
        SubElement(signal, 'name').text = update_notice

    def _format_desk(self, article, item_meta):
        # store desk as service
        archive_item = superdesk.get_resource_service('archive').find_one(
            req=None, _id=article['guid']
        )
        if (
            archive_item is not None
            and archive_item.get('task')
            and archive_item['task'].get('desk')
        ):
            desk = superdesk.get_resource_service('desks').find_one(
                req=None, _id=archive_item['task']['desk']
            )
            try:
                stage = superdesk.get_resource_service('stages').find_one(
                    req=None, _id=archive_item['task']['stage']
                )
            except KeyError:
                stage = {}
            if desk and desk.get('name'):
                service = SubElement(item_meta, 'service')
                SubElement(service, 'name').text = desk['name']
                pieces = desk['name'].split(' - ')
                if len(pieces) == 2:
                    signal = SubElement(
                        item_meta,
                        'signal',
                        {'qcode': 'red-address:{}'.format(pieces[0].strip())},
                    )
                    SubElement(signal, 'name').text = ': '.join(
                        [x for x in ['desk', desk.get('name'), stage.get('name') if stage else None] if x]
                    )
            lookup = {'_id_document': archive_item['_id']}
            versions = (
                superdesk.get_resource_service('archive_versions')
                .find(where=lookup)
                .sort('_id')
            )
            first_desk = None
            for version in versions:
                if (
                    not first_desk
                    and version.get('task')
                    and version['task'].get('desk')
                ):
                    if desk and desk['_id'] == version['task']['desk']:
                        first_desk = desk
                    else:
                        first_desk = superdesk.get_resource_service('desks').find_one(
                            req=None, _id=version['task']['desk']
                        )
            if first_desk:
                pieces = first_desk['name'].split(' - ')
                if len(pieces) == 2:
                    SubElement(
                        item_meta,
                        'signal',
                        {'qcode': 'red-orig:{}'.format(pieces[0].strip())},
                    )

    def _format_related(self, article, item_meta):
        featured = article.get('associations', {}).get('featuremedia')
        if featured:
            orig = featured.get('renditions', {}).get('original')
            if orig:
                link = SubElement(
                    item_meta,
                    'link',
                    attrib={
                        'rel': 'irel:seeAlso',
                        'mimetype': orig.get('mimetype', featured.get('mimetype')),
                        'href': self._publish_media(orig),
                    },
                )
                if featured.get('headline'):
                    SubElement(link, 'title').text = featured['headline']

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
                    subj = SubElement(
                        content_meta,
                        'subject',
                        attrib={
                            'qcode': 'products:%s' % s['qcode'],
                        },
                    )

                    SubElement(subj, 'name', attrib={XML_LANG: 'it'}).text = s['name']
                elif 'qcode' in s:
                    if ':' in s['qcode']:
                        qcode = s['qcode']
                    else:
                        # qcode = '%s:%s' % (s.get('scheme', 'subj'), s['qcode'])
                        qcode = '%s:%s' % (s.get('scheme') or 'subj', s['qcode'])
                    subj = SubElement(
                        content_meta,
                        'subject',
                        attrib={'type': 'cpnat:abstract', 'qcode': qcode},
                    )
                    SubElement(subj, 'name', attrib={XML_LANG: 'en'}).text = s['name']
        # place name for pictures - single line
        if article.get('extra') and article['extra'].get('city'):
            subj = SubElement(
                content_meta,
                'subject',
                {
                    'type': 'cptType:5',
                    'literal': article['extra']['city'],
                },
            )
            SubElement(subj, 'name').text = article['extra']['city']
            if article['extra'].get('nation'):
                broader = SubElement(subj, 'broader', {'type': 'cptype:country'})
                SubElement(broader, 'name').text = article['extra']['nation']

    def _format_located(self, article, content_meta):
        """Appends the located element to the contentMeta element

        :param dict article:
        :param Element content_meta:
        """
        located = article.get('dateline', {}).get('located', {})
        if (
            located
            and located.get('place')
            and located.get('place').get('name').upper()
            in article.get('dateline').get('text').upper()
        ):
            self._format_geonames_place(located['place'], content_meta, 'located')
        elif located and located.get('city') and article.get('type') != 'picture':
            located_elm = SubElement(
                content_meta,
                'located',
                attrib={'qcode': 'city:%s' % located.get('city_code').upper()},
            )
            if located.get('state'):
                SubElement(
                    located_elm,
                    'broader',
                    attrib={'qcode': 'reg:%s' % located['state']},
                )
            if located.get('country'):
                SubElement(
                    located_elm,
                    'broader',
                    attrib={'qcode': 'cntry:%s' % located['country'].upper()},
                )

        if article.get('dateline'):
            try:
                self._format_dateline(article, content_meta, article.get('dateline'))
            except ValueError:
                pass

    def _format_dateline(self, article, content_meta, dateline):
        dateline_text = article.get('dateline', {}).get('text', '')
        if dateline.get('date') and dateline.get('text'):
            date = arrow.get(dateline['date']).datetime
            source = article.get('extra', {}).get(
                'HeadingNews', article.get('source', 'ANSA')
            )

            language = article.get('language', 'it')
            app_languages = {lang['language'] for lang in app.config['LANGUAGES']}
            if language not in app_languages:
                language = app.config['DEFAULT_LANGUAGE']

            kwargs = {
                'city': dateline['text'].split(',')[0],
                'date': self._format_dateline_date(
                    date, language, dateline['located'].get('tz')
                ),
                'source': source,
            }

            if language in ('it', 'en', 'de'):
                dateline_text = '{source} - {city}, {date} -'.format(**kwargs)
            elif language == 'es':
                dateline_text = '{source} - {city} {date} -'.format(**kwargs)
            elif language == 'pt':
                dateline_text = '{city}, {date} {source} -'.format(**kwargs)
            elif language == 'ar':
                dateline_text = '{source} - {date} - {city} -'.format(**kwargs)

        SubElement(content_meta, 'dateline').text = dateline_text

    def _format_dateline_date(self, date, language, tz=None):
        tzinfo = get_timezone('Europe/Rome')
        if tz:
            tzinfo = get_timezone(tz)
        _format = 'dd MMM'
        if language in ('en', 'ar'):
            _format = 'MMM d'
        elif language in ('es', 'pt', 'de'):
            _format = 'd MMM'
        datetime = None if self.DATETIME_USE_CURRENT_TIME else date
        return (
            format_datetime(
                datetime=datetime, format=_format, tzinfo=tzinfo, locale=language
            )
            .upper()
            .strip('.')
        )

    def _format_place(self, article, content_meta):
        super()._format_place(article, content_meta)
        for place in article.get('place', []):
            if (
                len(place.keys()) == 2 and place.get('name') and place.get('qcode')
            ):  # suggested places from semantics
                self._create_subject_element(
                    content_meta, place['name'], place['qcode'], 'cpnat:geoArea'
                )

    def _format_item_set(self, article, item_set, item_type):
        """Use original ansa id if available."""
        item = super()._format_item_set(article, item_set, item_type)
        if article.get('extra', {}).get('ansaid') and not article.get('original_id'):
            item.set('guid', article['extra']['ansaid'])
        elif article.get('rewrite_of'):
            item.set('guid', self._get_original_guid(article))
            item.set('version', str(article.get('rewrite_sequence') + 1))
        else:
            item.set('version', str(1))
        return item

    def _get_original_guid(self, article):
        guid = article['rewrite_of']
        for i in range(article.get('rewrite_sequence', 1)):
            prev = superdesk.get_resource_service('archive').find_one(
                req=None, _id=guid
            )
            if not prev or not prev.get('rewrite_of'):
                break
            guid = prev['rewrite_of']
        return guid

    def _format_rights(self, newsItem, article):
        if article.get('type') == 'picture':
            self._copy_rights_info(article, newsItem)
            return
        try:
            super()._format_rights(newsItem, article)
        except (KeyError, TypeError):
            pass

    def _copy_rights_info(self, article, news_item):
        rightsinfo = SubElement(news_item, 'rightsInfo')
        SubElement(
            rightsinfo,
            'copyrightHolder',
            {'literal': article.get('copyrightholder') or 'ANSA'},
        )
        if article.get('copyrightnotice'):
            SubElement(rightsinfo, 'copyrightNotice').text = article['copyrightnotice']
        if article.get('usageterms'):
            SubElement(rightsinfo, 'usageTerms').text = article['usageterms']

    def _format_semantics(self, article, content_meta):
        mapping = [('persons', 'cpnat:person'), ('organizations', 'cpnat:organisation')]
        semantics = article.get('semantics', {})
        for field, cpnat in mapping:
            if semantics.get(field):
                for item in semantics[field]:
                    subj = SubElement(content_meta, 'subject', attrib={'type': cpnat})
                    SubElement(subj, 'name').text = item

    def _format_geonames_place(self, place, content_meta, elem='subject'):
        cptype = 'country'
        if place.get('state'):
            cptype = 'region'
        if place.get('region'):
            cptype = 'statprov'
        if place.get('feature_class') == 'P':
            cptype = 'city'

        subject = SubElement(
            content_meta,
            elem,
            attrib={
                'type': 'cptype:%s' % cptype,
                'qcode': 'geo:%s' % place['code'],
            },
        )

        if place.get('name'):
            SubElement(subject, 'name').text = place['name']

        if place.get('continent_code'):
            SubElement(
                subject,
                'broader',
                attrib={
                    'type': 'cptype:continentalcode',
                    'qcode': 'geo:%s' % place['continent_code'],
                },
            )

        if place.get('country_code') and place.get('country') and cptype != 'country':
            country = SubElement(
                subject,
                'broader',
                attrib={
                    'type': 'cptype:country',
                    'qcode': 'geo:%s' % place['country_code'],
                },
            )
            SubElement(country, 'name').text = place['country']

        if place.get('state_code') and place.get('state') and cptype != 'region':
            state = SubElement(
                subject,
                'broader',
                attrib={
                    'type': 'cptype:region',
                    'qcode': 'geo:%s' % place['state_code'],
                },
            )
            SubElement(state, 'name').text = place['state']

        if place.get('region_code') and place.get('region') and cptype != 'statprov':
            region = SubElement(
                subject,
                'broader',
                attrib={
                    'type': 'cptype:statprov',
                    'qcode': 'geo:%s' % place['region_code'],
                },
            )
            SubElement(region, 'name').text = place['region']

        if elem == 'located' and place.get('location'):
            geo = SubElement(subject, 'geoAreaDetails')
            SubElement(
                geo,
                'position',
                attrib={
                    'latitude': str(place['location']['lat']),
                    'longitude': str(place['location']['lon']),
                },
            )

    def _format_genre(self, article, content_meta):
        if article.get('type') == 'picture':
            return
        if article.get('genre'):
            for g in article['genre']:
                if g.get('name'):
                    code = g.get('qcode', g['name'])
                    qcode = code if ':' in code else 'genre:%s' % code
                    genre = SubElement(content_meta, 'genre', attrib={'qcode': qcode})
                    SubElement(
                        genre, 'name', attrib={XML_LANG: article.get('language', 'en')}
                    ).text = g['name']

    def _format_creditline(self, article, content_meta):
        if article.get('copyrightholder'):
            etree.SubElement(content_meta, 'creditline').text = article[
                'copyrightholder'
            ]
        else:
            super()._format_creditline(article, content_meta)

    def _format_keywords(self, article, content_meta):
        if article.get('keywords'):
            for keyword in article['keywords']:
                if keyword:
                    etree.SubElement(content_meta, 'keyword').text = keyword


class ANSAHTMLNewsMLG2Formatter(ANSAPlainTextNewsMLG2Formatter):
    def _build_html_doc(self, article):
        try:
            html = etree.HTML(article.get('body_html'))
        except (etree.XMLSyntaxError, ValueError):
            if article.get('body_html'):
                logger.exception('XML parsing error')
            html = None
        return (
            html
            if html is not None
            else etree.HTML('<p>%s</p>' % article.get('headline') or '')
        )

    def can_format(self, format_type, article):
        return format_type == 'newsmlg2ansaHTML'
