from lettuce import *
from flask import json

from superdesk import app, connect_db
from superdesk import models
from superdesk import users

@before.all
def set_app():
    app.config['TESTING'] = True
    app.config['DB_NAME'] = 'superdesk_lettuce'
    connect_db()
    world.app = app.test_client()

@after.each_scenario
def drop_users(scenario):
    models.User.drop_collection()

@step('I have no credentials')
def have_no_credentials(step):
    world.credentials = {}

@step('I have valid credentials')
def have_user_credentials(step):
    world.credentials = {
        'username': 'test',
        'password': 'test'
        }
    users.create_user(**world.credentials)

@step('I have bad username')
def have_non_existing_username(step):
    world.credentials = {
        'username': 'nonexistingone'
        }

@step('I have bad password')
def have_bad_password(step):
    world.credentials = {
        'username': 'test',
        'password': 'test',
        }
    users.create_user(**world.credentials)
    world.credentials['password'] = 'notest'

@step('I send auth request')
def send_auth_request(step):
    world.response = world.app.post('/auth', data=world.credentials)

@step('I get response with code (\d+)')
def get_response_with_code(step, expected_code):
    expected_code = int(expected_code)
    assert world.response.status_code == expected_code, \
        "Got %d" % world.response.status_code

@step('I get "([_a-z]+)" in data')
def get_auth_token(step, expected_key):
    expected_key = str(expected_key)
    assert expected_key in world.response.get_data(), \
        "Got %s" % world.response.get_data()

@step('I get valid auth_token')
def get_valid_auth_token(step):
    data = json.loads(world.response.get_data())
    assert users.is_valid_token(data.get('auth_token')), \
        "Got %s" % data.get('auth_token')
