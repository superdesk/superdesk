Feature: Templates fetching

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
