"""
    En to NO Metadata Macro will perform the following changes to current content item:
    - change the byline to "(NPK-NTB)"
    - change the signoff to "npk@npk.no"
    - change the body footer to "(©NPK)" - NB: copyrightsign, not @
    - change the service to "NPKSisteNytt"
"""


def en_to_no_metadata_macro(item, **kwargs):
    item['byline'] = '(NPK-NTB)'
    item['sign_off'] = 'npk@npk.no'
    item['body_footer'] = '(©NPK)'
    item['language'] = 'nn-NO'
    item['anpa_category'] = [
        {
            'qcode': 's',
            'single_value': True,
            'name': 'NPKSisteNytt',
            'language': 'nn-NO',
            'scheme': None
        }
    ]
    return item


name = 'EN to NO Metadata Macro'
label = 'EN to NO Metadata Macro'
callback = en_to_no_metadata_macro
access_type = 'backend'
action_type = 'direct'
from_languages = ['en']
to_languages = ['nn-NO', 'nb-NO']
