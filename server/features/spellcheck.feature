Feature: Spellcheck

    @auth
    Scenario: Spellcheck suggest corrections for word using all dicts for given language
        Given "dictionaries"
        """
        [{"name": "foo", "language_id": "en", "content": {"foo": 1}}, {"name": "bar", "language_id": "en", "content": {"bar": 2}}]
        """

        When we post to "spellcheck"
        """
        {"word": "foe", "language_id": "en"}
        """

        Then we get new resource
        """
        {"word": "foe", "corrections": ["foo"]}
        """

        When we post to "spellcheck"
        """
        {"word": "baz", "language_id": "en"}
        """

        Then we get new resource
        """
        {"word": "baz", "corrections": ["bar"]}
        """

    @auth
    Scenario: Spellcheck is using only active dictionaries
        Given "dictionaries"
        """
        [{"name": "inactive", "language_id": "en", "content": {"foo": 1}, "is_active": false}]
        """

        When we post to "spellcheck"
        """
        {"word": "foe", "language_id": "en"}
        """

        Then we get new resource
        """
        {"word": "foe", "corrections": "__any_value__"}
        """
