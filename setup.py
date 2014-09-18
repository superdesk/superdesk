#!/usr/bin/env python

from setuptools import setup, find_packages

LONG_DESCRIPTION = open('README.md').read()

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
    scripts=['settings.py', 'app.py', 'wsgi.py', 'ws.py', 'manage.py'],
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
