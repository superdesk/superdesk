@wip
Feature: Macros

    @auth
    Scenario: Get list of all macros
        When we get "/macros"
        Then we get list with 2+ items
            """
            {"_items": [{"name": "usd_to_aud", "label": "Convert USD to AUD", "description": "Convert USD to AUD.", "shortcut": "c"}]}
            """

    @auth
    Scenario: Get list of all macros by desk
        When we get "/macros?desk=POLITICS"
        Then we get list with 2 items
            """
            {"_items": [{"name": "mex_to_aud", "label": "Convert MEX to AUD", "description": "Convert MEX to AUD.", "shortcut": "c"}]}
            """

    @auth
    Scenario: Trigger macro via name
        When we post to "/macros"
            """
            {"macro": "usd_to_aud", "item": {"body_html": "$10"}}
            """
        Then we get new resource
            """
            {"item": {"body_html": "$12"}}
            """

    @auth
    Scenario: Return an error when triggering unknown macro
        When we post to "/macros"
            """
            {"macro": "this does not exist!", "item": {"body_html": "test"}}
            """
        Then we get response code 400
