Feature: Upload

    @auth
    Scenario: Upload a binary file
        When we upload a binary file
        Then we get a file reference
