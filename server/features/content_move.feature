Feature: Move or Send Content to another desk

    @auth
    Scenario: Send Content from personal to another desk
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "archive"
        """
        [{"guid": "123", "type":"text", "headline": "test1", "guid": "123", "state": "draft", "task": {"user": "#CONTEXT_USER_ID#"}}]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
        Then we get OK response
        When we get "/archive/123?version=all"
        Then we get list with 2 items
        When we get "/archive/123"
        Then we get existing resource
        """
        { "headline": "test1", "guid": "123", "state": "submitted", "_current_version": 2,
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}
        """

    @auth
    Scenario: Send Content from one desk to another desk
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "archive"
        """
        [{  "type":"text", "headline": "test1", "guid": "123", "state": "submitted",
            "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        And we post to "/desks"
        """
        [{"name": "Finance"}]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
        Then we get OK response
        When we get "/archive/123"
        Then we get existing resource
        """
        { "operation": "move", "headline": "test1", "guid": "123", "state": "submitted", "_current_version": 2,
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}
        """

    @auth
    Scenario: Send Content from one stage to another stage with same desk
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "archive"
        """
        [{  "type":"text", "headline": "test1", "guid": "123", "state": "submitted",
            "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        And we post to "/stages"
        """
        [
          {
          "name": "another stage",
          "description": "another stage",
          "task_status": "in_progress",
          "desk": "#desks._id#"
          }
        ]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#stages._id#"}}]
        """
        Then we get OK response
        When we get "/archive/123"
        Then we get existing resource
        """
        { "headline": "test1", "guid": "123", "state": "submitted", "_current_version": 2,
          "task": {"desk": "#desks._id#", "stage": "#stages._id#", "user": "#CONTEXT_USER_ID#"}}
        """

    @auth
    @clean
    Scenario: Send Content from one stage to another stage with incoming validation rule fails
        Given "desks"
        """
        [{"name": "Politics"}]
        """
        Given we create a new macro "validate_headline_macro.py"
        When we post to "archive"
        """
        [{  "type":"text", "guid": "123", "state": "submitted",
            "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        And we post to "/stages"
        """
        [
          {
          "name": "another stage",
          "description": "another stage",
          "task_status": "in_progress",
          "desk": "#desks._id#",
          "incoming_macro": "validate_headline"
          }
        ]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#stages._id#"}}]
        """
        Then we get error 400
        """
        {"_message": "Error:'Headline cannot be empty!' in incoming rule:Validate Headline for stage:another stage"}
        """

    @auth
    @clean
    Scenario: Send Content from one stage to another stage with incoming rule succeeds
        Given "desks"
        """
        [{"name": "Politics"}]
        """
        Given we create a new macro "behave_macro.py"
        When we post to "archive"
        """
        [{  "type":"text", "guid": "123", "state": "submitted",
            "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        And we post to "/stages"
        """
        [
          {
          "name": "another stage",
          "description": "another stage",
          "task_status": "in_progress",
          "desk": "#desks._id#",
          "incoming_macro": "update_fields"
          }
        ]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#stages._id#"}}]
        """
        Then we get OK response
        When we get "/archive/123"
        Then we get existing resource
        """
        { "guid": "123", "state": "submitted", "_current_version": 2,
          "abstract": "Abstract has been updated",
          "task": {"desk": "#desks._id#", "stage": "#stages._id#", "user": "#CONTEXT_USER_ID#"}}
        """

    @auth
    @clean
    Scenario: Send Content from one stage to another stage with outgoing validation rule fails
        Given "desks"
        """
        [{"name": "Politics"}]
        """
        Given we create a new macro "validate_headline_macro.py"
        When we get "/stages/#desks.incoming_stage#"
        When we patch "/stages/#desks.incoming_stage#"
        """
        {
          "outgoing_macro": "validate_headline"
        }
        """
        When we post to "archive"
        """
        [{  "type":"text", "guid": "123", "state": "submitted",
            "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        And we post to "/stages"
        """
        [
          {
          "name": "another stage",
          "description": "another stage",
          "task_status": "in_progress",
          "desk": "#desks._id#"
          }
        ]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#stages._id#"}}]
        """
        Then we get error 400
        """
        {"_message": "Error:'Headline cannot be empty!' in outgoing rule:Validate Headline for stage:New"}
        """

    @auth
    @clean
    Scenario: Send Content from one stage to another stage with outgoing rule succeeds
        Given "desks"
        """
        [{"name": "Politics"}]
        """
        Given we create a new macro "behave_macro.py"
        When we get "/stages/#desks.incoming_stage#"
        When we patch "/stages/#desks.incoming_stage#"
        """
        {
          "outgoing_macro": "update_fields"
        }
        """
        When we post to "archive"
        """
        [{  "type":"text", "guid": "123", "state": "submitted",
            "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        And we post to "/stages"
        """
        [
          {
          "name": "another stage",
          "description": "another stage",
          "task_status": "in_progress",
          "desk": "#desks._id#"
          }
        ]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#stages._id#"}}]
        """
        Then we get OK response
        When we get "/archive/123"
        Then we get existing resource
        """
        { "guid": "123", "state": "submitted", "_current_version": 2,
          "abstract": "Abstract has been updated",
          "task": {"desk": "#desks._id#", "stage": "#stages._id#", "user": "#CONTEXT_USER_ID#"}}
        """

    @auth
    Scenario: Move should fail if no desk is specified
        Given "archive"
        """
        [{  "type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "submitted",
            "task": {"user": "#CONTEXT_USER_ID#"}}]
        """
        When we post to "/archive/123/move"
        """
        [{"task": {}}]
        """
        Then we get error 400
        """
        {"_issues": {"task": {"stage": {"required": 1}, "desk": {"required": 1}}}}
        """

    @auth
    Scenario: Move should fail if desk and no stage is specified
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        And "archive"
        """
        [{  "type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "submitted",
            "task": {"user": "#CONTEXT_USER_ID#"}}]
        """
        When we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#"}}]
        """
        Then we get error 400
        """
        {"_issues": {"task": {"stage": {"required": 1}}}}
        """

    @auth
    Scenario: Move should fail if desk and stage are same
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        And "archive"
        """
        [{  "type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "submitted",
            "task": {"desk":"#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        When we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
        Then we get error 412
        """
        {"_message":"Move is not allowed within the same stage.", "_status": "ERR"}
        """

    @auth
    Scenario: Move should fail if user trying to move a published content
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        And "archive"
        """
        [{  "type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "published",
            "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        When we post to "/desks"
        """
        [{"name": "Finance"}]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
        Then we get response code 201

    @auth
    Scenario: User can't move content without a privilege
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        And "archive"
        """
        [{  "type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "published",
            "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        When we post to "/desks"
        """
        [{"name": "Finance"}]
        """
        And we login as user "foo" with password "bar" and user type "user"
        """
        {"user_type": "user", "email": "foo.bar@foobar.org"}
        """
        And we post to "/archive/123/move"
        """
        [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
        """
        Then we get response code 403
