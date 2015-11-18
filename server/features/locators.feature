Feature: Locators API

    Scenario: Find Cities across all countries
        When we get "/cities/"
        Then we get list with +1 items

    Scenario: Find Cities in Australia
        When we get "/country/AU"
        Then we get list with +1 items
        """
        {"_items": [{"country": "Australia", "country_code": "AU"}]}
        """

    Scenario: Find Cities in NSW, Australia
        When we get "/country/AU/state/NSW"
        Then we get list with +1 items
        """
        {"_items": [{"state": "New South Wales", "state_code": "NSW", "country": "Australia", "country_code": "AU"}]}
        """
