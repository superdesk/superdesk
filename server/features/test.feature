Feature: Test
    Scenario: Test scenario
        When we get "/"
        Then we get existing resource
        """
        {"_links": []}
        """

