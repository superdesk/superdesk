
import os
import xml.etree.ElementTree as etree

import superdesk
from .nitf import parse

PROVIDER = 'aap'

class AAPIngestService(object):

    def update(self, provider):
        path = provider.get('config', {}).get('path', None)
        if not path:
            return []

        for filename in os.listdir(path):
            with open(os.path.join(path, filename), 'r') as f:
                item = parse(f.read())
                item.setdefault('provider', provider.get('name', provider['type']))
                yield item

superdesk.provider(PROVIDER, AAPIngestService())