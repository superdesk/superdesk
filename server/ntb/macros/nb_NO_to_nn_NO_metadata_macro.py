"""
    nb-NO to nn-NO Metadata Macro will perform the following changes to current content item:
    - change the byline to "(NPK-NTB)"
    - change the body footer to "(©NPK)" - NB: copyrightsign, not @
    - change the service to "NPKSisteNytt"
"""


def nb_NO_to_nn_NO_metadata_macro(item, **kwargs):
    item['byline'] = '(NPK-NTB)'
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


name = 'Bokmal to Nynorsk Metadata Macro'
label = 'Translate to Nynorsk Macro'
callback = nb_NO_to_nn_NO_metadata_macro
access_type = 'backend'
action_type = 'direct'
from_languages = ['nb-NO']
to_languages = ['nn-NO']
