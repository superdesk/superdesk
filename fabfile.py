from fabric.api import local
from fabric.context_managers import shell_env, prefix

TEST_DB = '_superdesk_test'

def test():
    with shell_env(MONGOHQ_URL=TEST_DB):
        local('lettuce')

def manage():
    local('python manage.py')

def server():
    local('python app.py')

def run():
    server()
