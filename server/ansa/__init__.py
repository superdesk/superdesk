import superdesk

def init_app(app):
    superdesk.privilege(
        name='ansa_metasearch',
        label='ANSA - metasearch',
        decsription=''
    )

    superdesk.privilege(
        name='ansa_live_assistant',
        label='ANSA - live assistant',
        decsription=''
    )

    superdesk.privilege(
        name='ansa_ai_news',
        label='ANSA - ai news',
        decsription=''
    )

   