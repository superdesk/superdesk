# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2026 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license

"""The ``planning_prepopulate`` endpoint of the superdesk-planning e2e server, for the documentation instance.

superdesk-planning keeps it in ``e2e/server/planning_prepopulate.py``, outside the installed package. The
screenshot seed ``seed_planning.py`` (superdesk-docs-user-guide, ``tools/screenshots``) posts events, planning
items, planning types, locations and vocabularies through it, as the default prepopulate user and without the
validation of the regular endpoints. Like the original it only exists when ``SUPERDESK_TESTING`` is on and
needs no login.

The original inserts through ``superdesk.tests.utils.post_items``. Importing ``superdesk.tests`` needs test
packages (``aiomoto``) that are not in requirements.txt, so the same insert is written out below.
"""

from superdesk import Resource, get_backend, get_resource_service
from superdesk.core import get_current_app, get_current_async_app
from superdesk.eve_async import AsyncBaseService
from apps.prepopulate.app_prepopulate import get_default_user, set_logged_user


def init_app(app) -> None:
    if app.config.get("SUPERDESK_TESTING"):
        PlanningPrepopulateResource(
            PlanningPrepopulateResource.endpoint_name,
            app=app,
            service=PlanningPrepopulateService(
                PlanningPrepopulateResource.endpoint_name, backend=get_backend()
            ),
        )


class PlanningPrepopulateResource(Resource):
    endpoint_name = url = "planning_prepopulate"
    resource_methods = public_methods = ["POST"]
    schema = {
        "resource": {"type": "string", "required": True},
        "items": {"type": "list", "schema": {"type": "dict"}},
    }


async def post_item(resource: str, item: dict) -> list:
    try:
        eve_service = get_resource_service(resource)
    except KeyError:
        eve_service = None

    if eve_service is None:
        created = (
            await get_current_async_app()
            .resources.get_resource_service(resource)
            .create([item])
        )
        return [doc.id for doc in created]

    get_current_app().data.mongo._mongotize(item, resource)
    if hasattr(eve_service, "post_async"):
        return await eve_service.post_async([item])
    return eve_service.post([item])


class PlanningPrepopulateService(AsyncBaseService):
    async def create_async(self, docs, **kwargs):
        ids = []
        user = get_default_user()
        await set_logged_user(user["username"], user["password"])
        for doc in docs:
            for item in doc.get("items") or []:
                ids.extend(await post_item(doc["resource"], item))
        return ids
