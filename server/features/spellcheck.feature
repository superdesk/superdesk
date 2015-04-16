Feature: Spellcheck

    @auth
    Scenario: Spellcheck word
        Given "dictionaries"
        """
        [{"name": "en", "content": {"foo": 1, "bar": 2}}]
        """

        When we post to "spellcheck"
        """
        {"word": "foe", "dict": "#dictionaries._id#"}
        """

        Then we get new resource
        """
        {"word": "foe", "corrections": ["foo"]}
        """
