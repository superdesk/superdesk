#!/usr/bin/env python3
import feedparser
import fileinput
import re

TO_BE_UPDATED = [
    # superdesk-core
    {
        'feed_url': 'https://github.com/superdesk/superdesk-core/commits/master.atom',
        'file_name': 'server/requirements.txt',
        'pattern': 'superdesk-core.git@([a-f0-9]*)'
    },
    # superdesk-client-core
    {
        'feed_url': 'https://github.com/superdesk/superdesk-client-core/commits/master.atom',
        'file_name': 'client/package.json',
        'pattern': 'superdesk-client-core#([a-f0-9]*)'
    }
]

def get_last_commit(url):
    feed = feedparser.parse(url)
    return feed['entries'][0]['id'].split('/')[1][:9]


def replace_in_file(filename, search, new_value):
    textfile = open(filename, 'r')
    filetext = textfile.read()
    textfile.close()
    matches = re.findall(search, filetext)
    with fileinput.FileInput(filename, inplace=True) as file:
        for line in file:
            print(line.replace(matches[0], new_value), end='')

if __name__ == '__main__':
    for repo in TO_BE_UPDATED:
        last_commit_hash = get_last_commit(repo['feed_url'])
        replace_in_file(repo['file_name'], repo['pattern'], last_commit_hash)
