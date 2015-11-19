Feature: Subject codes api

    Scenario: Fetch subject codes
        When we get "/subjectcodes/"
        Then we get list with 300+ items
