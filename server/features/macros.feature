Feature: Macros

    @auth
    Scenario: Get list of all macros
        When we get "/macros"
        Then we get list with 1+ items
            """
            {"_items": [{"name": "usd_to_aud", "label": "Convert USD to AUD", "shortcut": "c"}]}
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
