Feature: Authentication
    In order to authenticate users
    As a user
    I want to get the auth_token

    Scenario: Authenticate non existing user
        Given I have no credentials
        When I send auth request
        Then I get response with code 401

    Scenario: Authenticate existing user
        Given I have valid credentials
        When I send auth request
        Then I get response with code 201
        And I get valid auth_token

    Scenario: Authenticate with bad credentials
        Given I have bad username
        When I send auth request
        Then I get response with code 401
        And I get "username" in data

    Scenario: Authenticate with bad password
        Given I have bad password
        When I send auth request
        Then I get response with code 401
        And I get "password" in data
