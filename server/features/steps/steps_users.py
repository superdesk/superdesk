
from behave import then
from steps import json


@then('we get users')
def then_we_get_users(context):
    usernames = json.loads(context.text)
    response_users = json.loads(context.response.get_data())['_items']
    for i in range(len(usernames)):
        username = usernames[i]
        response_username = response_users[i]['username']
        assert username == response_username, \
            'user #{} should be {}, but it was {}'.format(i, username, response_username)
