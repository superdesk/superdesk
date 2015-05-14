Feature: Returning error on invalid request parameters

    Scenario: Sending an unknown parameter when retrieving items
        When we get "/items?parameter_x=foo"
        Then we get error 422

    Scenario: Sending an unknown parameter when retrieving packages
        When we get "/packages?parameter_x=foo"
        Then we get response code 422

    Scenario: Trying to apply filters when fetching a single item
        When we get "/items/someItemId?q={\"language\": \"en\"}"
        Then we get error 422

    Scenario: Trying to apply filters when fetching a single package
        When we get "/packages/somePackageId?q={\"language\": \"en\"}"
        Then we get error 422
