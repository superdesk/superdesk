Feature: Item resource

    Scenario: List empty items
        Given I have auth token
        When I get "/items"
        Then I get empty list

    Scenario: Save item
        Given I have auth token
        When I post item
        Then I get status code 201
        And I get item guid

    Scenario: Update item
        Given I have auth token
        And I have an item
        When I update item
        Then I get updated item
