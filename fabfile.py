from fabric.api import local
from fabric.context_managers import shell_env, prefix

import settings

TEST_DB = '_superdesk_test'

def test():
    with shell_env(MONGOHQ_URL=TEST_DB):
        local('lettuce')

def upgrade():
    local('pip install -r requirements.txt --upgrade')

def manage():
    local('python manage.py')

def server():
    local('python app.py')

def servemedia():
    with prefix('cd %s' % settings.MEDIA_ROOT):
        local('python -m SimpleHTTPServer')

def run():
    server()
