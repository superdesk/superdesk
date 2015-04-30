Feature: Templates fetching

    @auth
    Scenario: Get predifined templates
    When we post to "content_templates"
    """
    {"template_name": "kill", "anpa_take_key": "TAKEDOWN"}
    """
    Then we get new resource
    """
    {"_id": "", "template_name": "kill", "anpa_take_key": "TAKEDOWN"}
    """
    When we get "content_templates/kill"
    Then we get existing resource
    """
    {"_id": "", "template_name": "kill", "anpa_take_key": "TAKEDOWN"}
    """
