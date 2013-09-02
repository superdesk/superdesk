Feature: Authentication

    Scenario: Authenticate existing user
        Given a user
        When we authenticate
        Then we get auth token

    Scenario: Authenticate existing user
        Given I have valid credentials
        When I send auth request
        Then I get status code 201
        And I get valid auth_token

    Scenario: Authenticate with bad credentials
        Given I have bad username
        When I send auth request
        Then I get status code 401
        And I get "username" in data

    Scenario: Authenticate with bad password
        Given I have bad password
        When I send auth request
        Then I get status code 401
        And I get "password" in data

    Scenario: Get items without token
        Given I have no token
        When I get "/items"
        Then I get status code 401

    Scenario: Get items with token
        Given I have auth token
        When I get "/items"
        Then I get status code 200
