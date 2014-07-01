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
        'Eve==0.4-dev',
        'Eve-Elastic==0.1.10',
        'Eve-Docs==0.1.2',
        'Flask-Script==2.0.3',
        'Pillow==2.4.0',
    ],
    scripts=['settings.py', 'app.py', 'wsgi.py', 'manage.py', 'docs.py'],
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
