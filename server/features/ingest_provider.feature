Feature: Ingest Provider

    @auth
    Scenario: List empty providers
        Given empty "ingest_providers"
        When we get "/ingest_providers"
        Then we get list with 0 items

    @auth
    @notification
    Scenario: Create new ingest_provider
        Given empty "ingest_providers"
        When we post to "ingest_providers"
	    """
        [{
          "type": "reuters",
          "name": "reuters 4",
          "source": "reuters",
          "is_closed": false,
          "config": {"username": "foo", "password": "bar"}
        }]
	    """
        And we get "/ingest_providers"
        Then we get list with 1 items
	    """
        {"_items": [{
          "type": "reuters",
          "name": "reuters 4",
          "content_expiry": 2880,
          "source": "reuters",
          "is_closed": false,
          "config": {"username": "foo", "password": "bar"},
          "notifications": {
              "on_update": true,
              "on_error": true,
              "on_close": true,
              "on_open": true
          }
        }]}
	    """
        When we get "/activity/"
        Then we get existing resource
        """
        {"_items": [{"data": {"name": "reuters 4"}, "message": "created Ingest Channel {{name}}"}]}
        """
        Then we get notifications
        """
        [{"event": "activity", "extra": {"_dest": {"#CONTEXT_USER_ID#": 0}}}]
        """
        Then we get emails
        """
        [
          {"body": "created Ingest Channel reuters 4"}
        ]

        """

    @auth
    @notification
    Scenario: Update ingest_provider
        Given "ingest_providers"
	    """
        [{
        "type": "reuters",
        "name": "reuters 4",
        "source": "reuters",
        "is_closed": false,
        "config": {"username": "foo", "password": "bar"}
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
        Then we get notifications
        """
        [{"event": "activity", "extra": {"_dest": {"#CONTEXT_USER_ID#": 0}}}]
        """
        Then we get emails
        """
        [
          {"body": "updated Ingest Channel the test of the test ingest_provider modified"}
        ]

        """

    @auth
    @notification
    Scenario: Open/Close ingest_provider
        Given "ingest_providers"
	    """
        [{
        "type": "reuters",
        "name": "reuters 4",
        "source": "reuters",
        "is_closed": false,
        "config": {"username": "foo", "password": "bar"}
        }]
	    """
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
         {"_items":
            [
              {"data": {"name": "reuters 4"}, "message": "updated Ingest Channel {{name}}"},
              {"data": {"status": "closed", "name": "reuters 4"},
                "message": "{{status}} Ingest Channel {{name}}"
               }
            ]
         }
         """
        Then we get notifications
        """
        [{"event": "activity", "extra": {"_dest": {"#CONTEXT_USER_ID#": 0}}}]
        """
        Then we get emails
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
        Given "ingest_providers"
	    """
        [{
        "type": "reuters",
        "name": "reuters 4",
        "source": "reuters",
        "is_closed": false,
        "config": {"username": "foo", "password": "bar"},
        "notifications": {
              "on_update": false,
              "on_error": false,
              "on_close": false,
              "on_open": false
        }
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
        Then we get no email
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
        Then we get no email
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
        Then we get no email