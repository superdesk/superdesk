Feature: Move or Send Content to another desk

    @auth
    Scenario: Send Content from personal to another desk
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "archive"
        """
        [{"type":"text", "headline": "test1", "guid": "123", "state": "draft", "task": {"user": "#CONTEXT_USER_ID#"}}]
        """
        And we post to "/archive/123/move"
        """
        [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
        """
        Then we get OK response
        When we get "/archive/123?version=all"
        Then we get list with 2 items
        When we get "/archive/123"
        Then we get existing resource
        """
        { "headline": "test1", "guid": "123", "state": "submitted", "_version": 2,
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
        [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
        """
        Then we get OK response
        When we get "/archive/123"
        Then we get existing resource
        """
        { "headline": "test1", "guid": "123", "state": "submitted", "_version": 2,
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}
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
        [{}]
        """
        Then we get error 400
        """
        {"_issues": {"desk": {"required": 1}}}
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
        [{"desk": "#desks._id#"}]
        """
        Then we get error 400
        """
        {"_issues": {"stage": {"required": 1}}}
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
        [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
        """
        Then we get error 412
        """
        {"_message": "Workflow transition is invalid.", "_status": "ERR"}
        """

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
        And we login as user "foo" with password "bar"
        """
        {"user_type": "user", "email": "foo.bar@foobar.org"}
        """
        And we post to "/archive/123/move"
        """
        [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}]
        """
        Then we get response code 403
