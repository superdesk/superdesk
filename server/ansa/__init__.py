import superdesk

from .constants import PRODUCTS_ID


def on_update(resource, updates, original):
    if resource == 'archive_publish':
        on_publish(updates, original)
        return


def on_publish(updates, original):
    associations = updates.get('associations')
    if not associations:
        return
    for key, item in associations.items():
        if not item.get('type') == 'picture':
            continue
        subject = item.setdefault('subject', [])
        product = next((subj for subj in subject if subj.get('scheme') == PRODUCTS_ID), None)
        if not product:
            subject.append({
                'name': 'Browser Allegati',
                'qcode': '0050000100002',
                'scheme': PRODUCTS_ID,
            })
        item['auto_publish'] = True  # toggles auto validation
        original.setdefault('associations', {})[key].update(item)


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

    app.on_update += on_update
