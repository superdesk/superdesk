Feature: Subject codes api

    Scenario: Fetch subject codes
        When we get "/subjectcodes/"
        Then we get list with 1404 items
        """
        {"name": "arts, culture and entertainment" , "code": "01000000"}
        """