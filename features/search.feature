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

    @auth
    Scenario: Can limit search to 1 result per shard
        Given "archive"
            """
            [{"guid": "1", "task": {"desk": "5472718f3b80a10df7b489fb"}}]
            """
        When we post to "/archive"
            """
            [{"guid": "2", "task": {"desk": "5472718f3b80a10df7b489fb"}}]
            """
        When we post to "/archive"
            """
            [{"guid": "3", "task": {"desk": "5472718f3b80a10df7b489fb"}}]
            """

        When we post to "/archive"
            """
            [{"guid": "4", "task": {"desk": "5472718f3b80a10df7b489fb"}}]
            """

        When we post to "/archive"
            """
            [{"guid": "5", "task": {"desk": "5472718f3b80a10df7b489fb"}}]
            """

        When we post to "/archive"
            """
            [{"guid": "6", "task": {"desk": "5472718f3b80a10df7b489fb"}}]
            """

        When we post to "/archive"
            """
            [{"guid": "7", "task": {"desk": "5472718f3b80a10df7b489fb"}}]
            """

        When we post to "/archive"
            """
            [{"guid": "8", "task": {"desk": "5472718f3b80a10df7b489fb"}}]
            """

        When we post to "/archive"
            """
            [{"guid": "9", "task": {"desk": "5472718f3b80a10df7b489fb"}}]
            """

        Then we set elastic limit
        When we get "/search"
        Then we get list with 5 items