Feature: Dictionaries Upload

    @auth
    Scenario: Upload a new dictionary and patch it
        When we upload a new dictionary with success
        """
        {"name": "test", "language_id": "en"}
        """
        Then we get new resource
        """
        {"name": "test", "language_id": "en"}
        """

        When we upload to an existing dictionary with success
        """
        {"name": "test", "language_id": "en"}
        """
        Then we get existing resource
        """
        {"name": "test", "language_id": "en"}
        """

    @auth
    Scenario: Update dictionary
        When we upload a new dictionary with success
        """
        {"name": "dict", "language_id": "en"}
        """

        And we patch latest
        """
        {"content": {"foo": 1, "bar": 0}}
        """

        Then we get updated response
        """
        {}
        """

        When we delete latest
        Then we get ok response

    @auth
    Scenario: User dictionary
        When we post to "/users"
            """
            {"username": "foo", "email": "foo@bar.com", "is_active": true, "sign_off": "abc"}
            """
        And we post to "/dictionaries"
            """
            {"name": "#users._id#", "language_id": "en", "user": "#users._id#"}
            """
        Then we get new resource

        When we patch latest
            """
            {"content": {"foo": 1}}
            """
        Then we get updated response
            """
            {}
            """

        When we get "/dictionaries"
        Then we get list with 1 items
            """
            {"_items": [{"content": {"foo": 1}}]}
            """
