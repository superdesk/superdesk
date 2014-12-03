Feature: Search Feature

    @auth
    Scenario: Can search ingest
        Given "ingest"
            """
            [{"guid": "1"}]
            """
        When we get "/search"
        Then we get list with 1 items

    @auth
    Scenario: Can search archive
        Given "archive"
            """
            [{"guid": "1", "task": {"desk": "5472718f3b80a10df7b489fb"}}]
            """
        When we get "/search"
        Then we get list with 1 items

    @auth
    Scenario: Can not search private content
        Given "archive"
            """
            [{"guid": "1"}]
            """
        When we get "/search"
        Then we get list with 0 items