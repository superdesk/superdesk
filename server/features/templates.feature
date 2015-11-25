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
    Scenario: User can create highlight template
        When we post to "content_templates"
        """
        {"template_name": "default highlight", "template_type": "highlights", 
         "body_html": "{% for item in items %} <h2>{{ item.headline }}</h2> {{ item.body_html }} <p></p> {% endfor %}"
        }
        """
        Then we get new resource
        """
        {"template_name": "default highlight", "template_type": "highlights"}
        """

    @auth
    Scenario: User can schedule a content creation
        Given "desks"
        """
        [{"name": "sports"}]
        """
        And "stages"
        """
        [{"name": "schedule", "desk": "#desks._id#"}]
        """

        When we post to "content_templates"
        """
        {"template_name": "test", "template_type": "create", "headline": "test", "type": "text", "slugline": "test",
         "schedule": {"day_of_week": ["MON"], "create_at": "0815", "is_active": true},
         "template_desk": "#desks._id#", "template_stage": "#stages._id#"}
        """
        Then we get new resource
        And next run is on monday "0815"

        When we patch latest
        """
        {"schedule": {"day_of_week": ["MON"], "create_at": "0915", "is_active": true}}
        """
        Then next run is on monday "0915"

        When we run create content task
        And we run create content task
        And we get "/archive"
        Then we get list with 1 items

    @auth @test
    Scenario: Apply template to an item
        When we post to "content_templates"
        """

            {
            "body_html": "<p>Please kill story slugged {{ item.slugline }} ex {{ item.dateline['text'] }} at {{item.versioncreated | format_datetime(date_format='%d %b %Y %H:%S %Z')}}.<\/p>",
            "type": "text",
            "abstract": "This article has been removed",
            "headline": "Kill\/Takedown notice ~~~ Kill\/Takedown notice",
            "urgency": 1, "priority": 1,
            "template_name": "kill",
            "template_type": "kill",
            "anpa_take_key": "KILL\/TAKEDOWN"
            }
        """
        Then we get new resource
        When we post to "content_templates_apply"
        """
            {
                "template_name": "kill",
                "item": {
                    "headline": "Test", "_id": "123",
                    "body_html": "test", "slugline": "testing",
                    "abstract": "abstract",
                    "urgency": 5, "priority": 6,
                    "dateline": {
                        "text": "Prague, 9 May (SAP)"
                    },
                    "versioncreated": "2015-01-01T22:54:53+0000"
                }
            }
        """
        Then we get updated response
        """
        {
          "_id": "123",
          "headline": "Kill\/Takedown notice ~~~ Kill\/Takedown notice",
          "body_html": "<p>Please kill story slugged testing ex Prague, 9 May (SAP) at 01 Jan 2015 23:53 CET.<\/p>",
          "anpa_take_key": "KILL\/TAKEDOWN",
          "slugline": "testing",
          "urgency": 1, "priority": 1,
          "abstract": "This article has been removed",
          "dateline": {
            "text": "Prague, 9 May (SAP)"
          },
          "versioncreated": "2015-01-01T22:54:53+0000"

        }
        """