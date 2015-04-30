Feature: Templates fetching

    @auth
    Scenario: Get predifined templates
        When we get "/templates"
        Then we get list with 1 items
        """
        {
        "_items": [
                {
                    "name": "kill",
                    "template": {
                        "headline": "Kill\/Takedown notice ~~~ Kill\/Takedown notice",
                        "abstract": "This article has been removed",
                        "anpa_take_key": "KILL\/TAKEDOWN",
                        "body_html": ""
                    }
                }
            ]
        }
        """
