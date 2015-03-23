Feature: Upload

    @auth
    Scenario: Upload a new dictionary and patch it
        When we upload a new dictionary with success
        """
        {"name": "test", "language_id": "en", "language_name": "English"}
        """
        Then we get new resource
        """
        {"name": "test", "language_id": "en", "language_name": "English"}
        """

        When we upload to an existing dictionary with success
        """
        {"name": "test", "language_id": "en", "language_name": "English"}
        """
        Then we get existing resource
        """
        {"name": "test", "language_id": "en", "language_name": "English", "content": ["alpha", "beta", "gamma"]}
        """
