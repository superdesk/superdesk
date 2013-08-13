Feature: Item resource

    Scenario: List empty items
        Given I have auth token
        When I get "/items/"
        Then I get empty list

    Scenario: Save item
        Given I have auth token
        When I post item
        Then I get status code 200
        And I get "OK" in data
