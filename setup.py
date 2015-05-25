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
from pip.req import parse_requirements
from pip.download import PipSession
import os

SOURCE_FOLDER = 'server'
LONG_DESCRIPTION = open(os.path.join(SOURCE_FOLDER, 'README.md')).read()
REQUIREMENTS = [str(ir.req) for ir in parse_requirements('server/requirements.txt', session=PipSession())
                if not (getattr(ir, 'link', False) or getattr(ir, 'url', False))]

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
    package_dir={'': SOURCE_FOLDER},
    packages=find_packages(SOURCE_FOLDER),
    install_requires=REQUIREMENTS,
    scripts=[
        os.path.join(SOURCE_FOLDER, 'settings.py'),
        os.path.join(SOURCE_FOLDER, 'app.py'),
        os.path.join(SOURCE_FOLDER, 'wsgi.py'),
        os.path.join(SOURCE_FOLDER, 'ws.py'),
        os.path.join(SOURCE_FOLDER, 'manage.py')
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
