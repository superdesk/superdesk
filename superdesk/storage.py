"""Storage module"""

import os
import requests

def fetch_url(url, target):
    """Fetch content from given url and store it into given target."""
    r = requests.get(url)
    with open(target, 'wb') as f:
        f.write(r.content)
        return os.path.basename(target)
