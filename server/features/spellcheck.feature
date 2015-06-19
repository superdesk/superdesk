@wip
Feature: Spellcheck

    @auth
    Scenario: Spellcheck suggest corrections for word
        Given "dictionaries"
        """
        [{"name": "en", "language_id": "en", "content": {"foo": 1, "bar": 2}}]
        """

        When we post to "spellcheck"
        """
        {"word": "foe", "language_id": "en"}
        """

        Then we get new resource
        """
        {"word": "foe", "corrections": ["foo"]}
        """
