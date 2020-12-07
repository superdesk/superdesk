from datetime import timedelta

from superdesk.utc import utcnow, utc_to_local
from superdesk.metadata.item import PUBLISH_SCHEDULE, SCHEDULE_SETTINGS
from apps.archive.common import update_schedule_settings
from ansa.constants import ROME_TZ as TZ


def schedule(item, time):
    now = utcnow()
    local = utc_to_local(TZ, now).replace(microsecond=0)

    if local.time() >= time:
        local += timedelta(days=1)

    local = local.replace(
        hour=time.hour, minute=time.minute, second=time.second, microsecond=0
    )

    item[SCHEDULE_SETTINGS] = {"time_zone": TZ}
    item[PUBLISH_SCHEDULE] = local
    update_schedule_settings(item, PUBLISH_SCHEDULE, item[PUBLISH_SCHEDULE])
    item[PUBLISH_SCHEDULE] = item[PUBLISH_SCHEDULE].replace(tzinfo=None)

    return item
