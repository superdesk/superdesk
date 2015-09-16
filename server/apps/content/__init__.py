"""Content related helpers and utils.
"""

from superdesk.notification import push_notification
from apps.auth import get_user


def push_content_notification(items):
    """Push content:update notification for multiple items.

    It can be also 2 versions of same item in updated handler
    so that we sent event with both old and new desk/stage.

    :param list items: list of items
    """
    ids = {}
    desks = {}
    stages = {}
    for item in items:
        ids[str(item.get('_id', ''))] = 1
        task = item.get('task', {})
        if task.get('desk'):
            desks[str(task.get('desk', ''))] = 1
        if task.get('stage'):
            stages[str(task.get('stage', ''))] = 1
    user = get_user()
    push_notification(
        'content:update',
        user=str(user.get('_id', '')),
        items=ids,
        desks=desks,
        stages=stages
    )
