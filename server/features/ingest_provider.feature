@tobefixed
Feature: Ingest Provider

    @auth
    Scenario: List empty providers
        Given empty "ingest_providers"
        When we get "/ingest_providers"
        Then we get list with 0 items

    @auth @notification
    Scenario: Create new ingest_provider
        Given empty "ingest_providers"
        When we post to "ingest_providers"
	    """
        [{"name": "reuters 4", "source": "reuters", "feeding_service": "reuters_http", "feed_parser": "newsml2",
          "is_closed": false, "content_expiry": 0, "config": {"username": "foo", "password": "bar"}
        }]
	    """
        And we get "/ingest_providers"
        Then we get list with 1 items
	    """
        {"_items": [{"name": "reuters 4", "content_expiry": 2880, "source": "reuters", "is_closed": false,
         "config": {"username": "foo", "password": "bar"}, "notifications": {"on_update": true, "on_error": true, "on_close": true, "on_open": true},
         "last_opened": {"opened_by": "#CONTEXT_USER_ID#"}}]
         }
	    """
        When we get "/activity/"
        Then we get existing resource
        """
        {"_items": [{"data": {"name": "reuters 4"}, "message": "Created Ingest Channel {{name}}"}]}
        """
        Then we get notifications
        """
        [
          {"event": "create", "extra": {"_dest": [{"user_id": "#CONTEXT_USER_ID#", "read": false}]}},
          {"event": "ingest_provider:create", "extra": {"provider_id": "#ingest_providers._id#"}}
        ]
        """
        Then we get emails
        """
        [{"body": "Created Ingest Channel reuters 4"}]
        """

    @auth
    Scenario: Update ingest_provider aliases
        Given "ingest_providers"
	    """
        [{"config": {"field_aliases": [{"content": "body_text"}]}, "is_closed": false, "name": "reuters 4",
         "source": "reuters",  "feeding_service": "reuters_http", "feed_parser": "newsml2"}]
	    """
        When we patch "/ingest_providers/#ingest_providers._id#"
        """
        {"config": {"field_aliases": [{"summary": "summary_alias"}, {"title": "headline"}]}}
        """
        Then expect json in "config/field_aliases"
        """
        [{"summary": "summary_alias"}, {"title": "headline"}]
        """

    @auth
    @notification
    Scenario: Update ingest_provider
        Given "ingest_providers"
	    """
        [{"name": "reuters 4", "source": "reuters", "is_closed": false, "config": {"username": "foo", "password": "bar"},
          "feeding_service": "reuters_http", "feed_parser": "newsml2"}]
	    """
        When we patch "/ingest_providers/#ingest_providers._id#"
        """
        {"name":"the test of the test ingest_provider modified", "content_expiry": 0}
        """
        Then we get updated response
        """
        {"name":"the test of the test ingest_provider modified", "content_expiry": 2880}
        """
        When we get "/activity/"
        Then we get existing resource
         """
         {"_items": [{"data": {"name": "the test of the test ingest_provider modified"}, "message": "updated Ingest Channel {{name}}"}]}
         """
        Then we get notifications
        """
        [{"event": "update", "extra": {"_dest": [{"user_id": "#CONTEXT_USER_ID#", "read": false}]}},
         {"event": "ingest_provider:create", "extra": {"provider_id": "#ingest_providers._id#"}},
         {"event": "ingest_provider:update", "extra": {"provider_id": "#ingest_providers._id#"}}]
        """
        Then we get emails
        """
        [{"body": "updated Ingest Channel the test of the test ingest_provider modified"}]
        """

    @auth @notification
    Scenario: Update critical errors for ingest_provider
        Given "ingest_providers"
	    """
        [{"name": "reuters 4", "source": "reuters", "is_closed": false, "config": {"username": "foo", "password": "bar"},
          "feeding_service": "reuters_http", "feed_parser": "newsml2"}]
	    """
        When we patch "/ingest_providers/#ingest_providers._id#"
        """
        {"critical_errors":{"6000":true, "6001":true}}
        """
        Then we get updated response
        """
        {"critical_errors":{"6000":true, "6001":true}}
        """

    @auth @notification
    Scenario: Open/Close ingest_provider
        Given "ingest_providers"
	    """
        [{"name": "reuters 4", "source": "reuters", "is_closed": false, "config": {"username": "foo", "password": "bar"},
          "feeding_service": "reuters_http", "feed_parser": "newsml2"}]
	    """
        When we patch "/ingest_providers/#ingest_providers._id#"
        """
        {"is_closed": true, "last_closed": {"message": "system misbehaving."}}
        """
        Then we get updated response
        """
        {"is_closed": true,  "last_closed": {"closed_by":"#CONTEXT_USER_ID#", "message": "system misbehaving."}}
        """
        When we get "/activity/"
        Then we get existing resource
         """
         {"_items":
            [
              {"data": {"name": "reuters 4"}, "message": "updated Ingest Channel {{name}}"},
              {"data": {"status": "closed", "name": "reuters 4"},
                "message": "{{status}} Ingest Channel {{name}}"
               }
            ]
         }
         """
        And we get notifications
        """
        [{"event": "create", "extra": {"_dest": [{"user_id": "#CONTEXT_USER_ID#", "read": false}]}},
         {"event": "ingest_provider:create", "extra": {"provider_id": "#ingest_providers._id#"}},
         {"event": "ingest_provider:update", "extra": {"provider_id": "#ingest_providers._id#"}}]
        """
        And we get emails
        """
        [
          {"body":"updated Ingest Channel reuters 4"},
          {"body":"closed Ingest Channel reuters 4"}
        ]
        """

    @auth
    @notification
    Scenario: Switch Off Notification on update ingest_provider
        Given empty "ingest_providers"
        And "ingest_providers"
	    """
        [{"name": "reuters 4", "source": "reuters", "is_closed": false, "config": {"username": "foo", "password": "bar"},
          "feeding_service": "reuters_http", "feed_parser": "newsml2",
          "notifications": {"on_update": false, "on_error": false, "on_close": false, "on_open": false}
        }]
        """
        When we patch "/ingest_providers/#ingest_providers._id#"
        """
        {"name":"the test of the test ingest_provider modified"}
        """
        Then we get updated response
        """
        {"name":"the test of the test ingest_provider modified"}
        """
        When we get "/activity/"
        Then we get existing resource
        """
        {"_items": [{"data": {"name": "the test of the test ingest_provider modified"}, "message": "updated Ingest Channel {{name}}"}]}
        """
        Then we get 0 emails
        When we patch "/ingest_providers/#ingest_providers._id#"
        """
        {"is_closed": true}
        """
        Then we get updated response
        """
        {"is_closed": true}
        """
        When we get "/activity/"
        Then we get existing resource
        """
         {"_items": [{"data": {"name": "the test of the test ingest_provider modified", "status": "closed"}, "message": "{{status}} Ingest Channel {{name}}"}]}
        """
        Then we get 0 emails
        When we patch "/ingest_providers/#ingest_providers._id#"
        """
        {"is_closed": false}
        """
        Then we get updated response
        """
        {"is_closed": false}
        """
        When we get "/activity/"
        Then we get existing resource
        """
         {"_items": [{"data": {"name": "the test of the test ingest_provider modified", "status": "opened"}, "message": "{{status}} Ingest Channel {{name}}"}]}
        """
        Then we get 0 emails

    @auth @notification
    Scenario: Delete an Ingest Provider which hasn't received items
        Given empty "ingest_providers"
        When we post to "ingest_providers"
	    """
        [{"name": "reuters 4", "source": "reuters", "is_closed": false, "config": {"username": "foo", "password": "bar"},
          "feeding_service": "reuters_http", "feed_parser": "newsml2"}]
	    """
        And we get "/ingest_providers"
        Then we get list with 1 items
        When we delete "/ingest_providers/#ingest_providers._id#"
        Then we get deleted response
        When we get "/activity/"
        Then we get existing resource
        """
        {"_items": [{"data": {"name": "reuters 4"}, "message": "Deleted Ingest Channel {{name}}"}]}
        """
        And we get notifications
        """
        [
          {"event": "delete", "extra": {"_dest": [{"user_id": "#CONTEXT_USER_ID#", "read": false}]}},
          {"event": "ingest_provider:delete", "extra": {"provider_id": "#ingest_providers._id#"}}
        ]
        """

    @auth @notification
    Scenario: Disabled/Inactive Administrators don't receive emails when an Ingest Provider is created
        Given empty "ingest_providers"
        When we post to "/users"
        """
        {"username": "foo", "email": "foo@bar.com", "sign_off": "fb", "user_type": "administrator", "is_active": false, "is_enabled": false}
        """
        And we post to "ingest_providers"
	    """
        [{"name": "reuters 4", "source": "reuters", "is_closed": false, "config": {"username": "foo", "password": "bar"},
          "feeding_service": "reuters_http", "feed_parser": "newsml2"}]
	    """
        Then we get 1 emails


    @auth
    Scenario: Creating a Ingest Provider with same name fails
        Given empty "ingest_providers"
        When we post to "ingest_providers"
	    """
        [{"name": "reuters 4", "source": "reuters", "feeding_service": "reuters_http", "feed_parser": "newsml2",
          "is_closed": false, "content_expiry": 0, "config": {"username": "foo", "password": "bar"}
        }]
	    """
        And we get "/ingest_providers"
        Then we get list with 1 items
	    """
        {"_items": [{"name": "reuters 4", "content_expiry": 2880, "source": "reuters", "is_closed": false,
         "config": {"username": "foo", "password": "bar"}, "notifications": {"on_update": true, "on_error": true, "on_close": true, "on_open": true},
         "last_opened": {"opened_by": "#CONTEXT_USER_ID#"}}]
         }
	    """
        When we post to "ingest_providers"
	    """
        [{"name": "reuters 4", "source": "reuters", "feeding_service": "reuters_http", "feed_parser": "newsml2",
          "is_closed": false, "content_expiry": 0, "config": {"username": "foo", "password": "bar"}
        }]
	    """
        Then we get error 400
        """
        {"_issues": {"name": {"unique": 1}}, "_status": "ERR"}
        """