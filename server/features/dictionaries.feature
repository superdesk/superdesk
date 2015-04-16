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
