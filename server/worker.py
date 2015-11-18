#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# This file is part of Superdesk.
#
# Copyright 2013, 2014, 2015 Sourcefabric z.u. and contributors.
#
# For the full copyright and license information, please see the
# AUTHORS and LICENSE files distributed with this source code, or
# at https://www.sourcefabric.org/superdesk/license


import logging
from logging.handlers import SysLogHandler

from app import get_app
from settings import LOG_SERVER_ADDRESS, LOG_SERVER_PORT


logging.basicConfig(handlers=[logging.StreamHandler(), SysLogHandler(address=(LOG_SERVER_ADDRESS, LOG_SERVER_PORT))])
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


celery = get_app().celery
