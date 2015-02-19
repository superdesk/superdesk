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


from setuptools import setup, find_packages
import os

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
README_PATH = os.path.join(ROOT_PATH, 'README.md')
LONG_DESCRIPTION = open(README_PATH).read()

setup(
    name='Superdesk-Server',
    version='0.1.3-dev',
    description='Superdesk REST API server',
    long_description=LONG_DESCRIPTION,
    author='petr jasek',
    author_email='petr.jasek@sourcefabric.org',
    url='https://github.com/superdesk/superdesk-server',
    license='GPLv3',
    platforms=['any'],
    packages=find_packages(),
    install_requires=[
        'Eve>=0.4',
        'Eve-Elastic>=0.1.13',
        'Flask>=0.10,<0.11',
        'Flask-Mail>=0.9.0,<0.10',
        'Flask-Script==2.0.5,<2.1',
        'Flask-PyMongo>=0.3.0',
        'autobahn[asyncio]>=0.8.15',
        'celery[redis]>=3.1.13',
        'bcrypt>=1.0.2',
        'blinker>=1.3',
    ],
    scripts=[
        os.path.join(ROOT_PATH, 'settings.py'),
        os.path.join(ROOT_PATH, 'app.py'),
        os.path.join(ROOT_PATH, 'wsgi.py'),
        os.path.join(ROOT_PATH, 'ws.py'),
        os.path.join(ROOT_PATH, 'manage.py')
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ]
)
