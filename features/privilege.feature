Feature: Privilege

    @wip
    @auth
    Scenario: Get list of all privileges
        When we get "/privileges"
        Then we get list with 14 items
            """
            {"_items": [{"name": "ingest"}, {"name": "archive"}]}
            """
