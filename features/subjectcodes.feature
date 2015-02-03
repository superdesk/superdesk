Feature: Subject codes api

    Scenario: Fetch subject codes
        When we get "/subjectcodes/"
        Then we get list with 1404 items
        """
        {"_items": [{"name": "arts, culture and entertainment" , "qcode": "01000000"}]}
        """