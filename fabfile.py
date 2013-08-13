from fabric.api import local
from fabric.context_managers import shell_env

def test():
    with shell_env(MONGOHQ_URL='superdesk_lettuce'):
        local('lettuce')

def server():
    local('python app.py')
