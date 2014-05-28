'''
Created on May 23, 2014

@author: Ioan v. Pocol
'''

import superdesk


def import_ingest(data, docs, **kwargs):
    #TODO: implement
    return ['53720224779a072ec19cdb88' for doc in docs] 

def read_status_import_ingest(data, req, **lookup):
    #TODO: implement
    return {"_id": lookup["_id"], "ingest_guid": "fake ingest guid", "status":"fake ingest status", "progress": 99}

superdesk.connect('impl_insert:import_ingest', import_ingest)
superdesk.connect('impl_find_one:import_ingest', read_status_import_ingest)

superdesk.domain('import_ingest', {
    'url': 'import_ingest',
    'resource_title': 'import_ingest',
    'resource_methods': ['POST'],
    'item_methods': ['GET'],
    'schema': {    
        'ingest_guid': {
            'type': 'string',
            'required': True
        },
        'status': {
            'type': 'string',
            'readonly': True
        },
        'progress': {
            'type': 'integer',
            'readonly': True
        },
    },
    'datasource': {
        'backend': 'business'
    }
})
