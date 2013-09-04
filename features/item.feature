Feature: Item resource

    @auth
    Scenario: List empty items
        Given no items
        When we get items
        Then we get empty list

    @auth
    Scenario: Create item
        Given no items
        When we post new item
        Then we get status code "201"
        And we get "headline" in item
        And we get "guid" in item
        And we get "versionCreated" in item
        And we get "firstCreated" in item

    @auth
    Scenario: Update item
        Given an item
        When we update item
        Then we get updated item
