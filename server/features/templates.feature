Feature: Templates

    @auth
    Scenario: Get predifined templates
    When we post to "content_templates"
    """
    {"template_name": "kill", "template_type": "kill", "anpa_take_key": "TAKEDOWN"}
    """
    Then we get new resource
    """
    {"_id": "__any_value__", "template_name": "kill", "template_type": "kill", "anpa_take_key": "TAKEDOWN"}
    """
    When we get "content_templates/kill"
    Then we get existing resource
    """
    {"_id": "__any_value__", "template_name": "kill", "anpa_take_key": "TAKEDOWN"}
    """

    @auth
    Scenario: User can create personal template
        When we post to "content_templates"
        """
        {"template_name": "personla", "template_type": "create", "template_desk": null}
        """
        Then we get new resource
        """
        {"template_desk": null}
        """

    @auth
    Scenario: User can schedule a content creation
        When we post to "content_templates"
        """
        {"template_name": "test", "template_type": "create", "headline": "test", "type": "text", "slugline": "test",
         "schedule": {"day_of_week": ["MON"], "create_at": "0815"}}
        """
        Then we get new resource
        And next run is on monday "0815"

        When we patch latest
        """
        {"schedule": {"day_of_week": ["MON"], "create_at": "0915"}}
        """
        Then next run is on monday "0915"
        And last run is set
