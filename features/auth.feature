Feature: Authentication

    Scenario: Authenticate existing user
        Given a user
        When we authenticate
        Then we get auth token

    Scenario: Authenticate with wrong password returns error
        Given a user
        When we authenticate with wrong password
        Then we get status code "401"
        And we get "invalid credentials" in response

    Scenario: Authenticate with non existing username
        Given a user
        When we authenticate with wrong username
        Then we get status code "401"
        And we get "username not found" in response

    Scenario: Get auth info without token
        Given a user
        When we get auth info
        Then we get status code "401"

    Scenario: Get auth info with auth token
        Given a user
        When we authenticate
        And we get auth info
        Then we get status code "200"
        And we get "user" in response
