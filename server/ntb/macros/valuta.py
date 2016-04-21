"""
    Getting currency exchange rates for today and yesterday. The source is an XML file
    Source of data is http://www.ecb.int/stats/eurofxref/eurofxref-hist-90d.xml

    (c) NTB 2007-: Trond Husoe (510 / thu@ntb.no)
    This solution gets data form http://www.dnbnor.no until the bank of norway sets up an xml-feed.
    Version 0.9
    Corrected fetching data from ebc and corrected decimals
"""

import xml.etree.cElementTree as ElementTree
import urllib3
import datetime


currencies = [
    {'currency': 'USD', 'name': 'US dollar', 'multiplication': 1},
    {'currency': 'NOK', 'name': 'EURO', 'multiplication': 0},
    {'currency': 'CHF', 'name': 'Sveitiske franc', 'multiplication': 100},
    {'currency': 'DKK', 'name': 'Danske kroner', 'multiplication': 100},
    {'currency': 'GBP', 'name': 'Britiske pund ', 'multiplication': 1},
    {'currency': 'SEK', 'name': 'Svenske kroner', 'multiplication': 100},
    {'currency': 'CAD', 'name': 'Canadiske dollar', 'multiplication': 1},
    {'currency': 'JPY', 'name': 'Japanske yen', 'multiplication': 100}
]

template = '<tr><td>{name}&nbsp;({currency})</td><td>{today}</td><td>({yesterday})</td></tr>'


def generate_row(currency, name, multiplication, euro_currency, today_currency, yesterday_currency):
    todayRate = today_currency if multiplication == 0 else ''
    yesterdayRate = yesterday_currency if multiplication == 0 else ''

    if today_currency and multiplication:
        todayRate = "{0:.4f}".format(float(euro_currency) * multiplication / float(today_currency))

    if yesterday_currency and multiplication:
        yesterdayRate = "{0:.4f}".format(float(euro_currency) * multiplication / float(yesterday_currency))

    return template.format(currency=currency, name=name, today=todayRate, yesterday=yesterdayRate)


def get_currency(today):

    try:
        yesterday = today - datetime.timedelta(days=1)

        # Getting data from The European Central Bank
        urlXml = "http://www.ecb.int/stats/eurofxref/eurofxref-hist-90d.xml"
        http = urllib3.PoolManager()
        response = http.request('GET', urlXml, headers={'User-Agent': 'Mozilla/5.0'})
        xmlDoc = response.data.decode('UTF-8')

        doc = ElementTree.fromstring(xmlDoc)
        namespaces = {'gesmes': 'http://www.gesmes.org/xml/2002-08-01',
                      'eurofxref': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}

        xpathEuroString = ".//eurofxref:Cube[@time='{date}']/eurofxref:Cube[@currency='NOK']"

        euroQuery = doc.find(xpathEuroString.format(date=today.date()), namespaces)
        if euroQuery is None:
            return ['Dagens valutakurser ikke klare ennå']

        euro = euroQuery.attrib["rate"]
        allCurrencies = ".//eurofxref:Cube[@time='{date}']/eurofxref:Cube"

        nodesToday = doc.findall(allCurrencies.format(date=today.date()), namespaces)
        todayDictionary = {cube.attrib["currency"]: cube.attrib["rate"] for cube in nodesToday}

        nodesYesterday = doc.findall(allCurrencies.format(date=yesterday.date()), namespaces)
        yesterdayDictionary = {cube.attrib["currency"]: cube.attrib["rate"] for cube in nodesYesterday}

        arrayStoreString = [generate_row(currency['currency'], currency['name'], currency['multiplication'], euro,
                                         todayDictionary.get(currency['currency'], ''),
                                         yesterdayDictionary.get(currency['currency'], ''))
                            for currency in currencies]

        return arrayStoreString

    except Exception as ex:
        return ['Error: ', str(ex)]


def ntb_currency_macro(item, **kwargs):
    # headline
    # this one is the correct one, just that the clock is past 00:00 datetime.datetime.now().date()
    today = datetime.datetime.now()
    yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
    headline = "Valutakurser {} ({})"
    headline = headline.format(today.strftime("%d.%m"), yesterday.date().strftime("%d.%m"))
    abstract = "Representative markedskurser for valuta fra Norges Bank"

    item['headline'] = headline
    item['abstract'] = abstract
    item['body_html'] = '<table>' + ''.join(line for line in get_currency(today)) + '</table>'

    return item


name = 'NTB Currency Macro'
label = 'NTB Currency Macro'
callback = ntb_currency_macro
access_type = 'frontend'
action_type = 'direct'
