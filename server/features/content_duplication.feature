Feature: Duplication of Content within Desk

    @auth
    Scenario: Duplicate a content with history
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{  "type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "submitted",
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      When we patch given
      """
      {"headline": "test2"}
      """
      And we patch latest
      """
      {"headline": "test3"}
      """
      Then we get updated response
      """
      {"headline": "test3", "state": "in_progress", "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}
      """
      And we get version 3
      When we get "/archive/123?version=all"
      Then we get list with 3 items
      When we post to "/archive/123/duplicate"
      """
      {"desk": "#desks._id#"}
      """
      When we get "/archive/#duplicate._id#"
      Then we get existing resource
      """
      {"state": "submitted", "_current_version": 4, "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}
      """
      When we get "/archive/#duplicate._id#?version=all"
      Then we get list with 4 items

      When we get "/archive/#duplicate._id#"
      Then we get existing resource
      """
      {"operation": "duplicate"}
      """

      When we get "/archive?q=#desks._id#"
      Then we get list with 2 items

    @auth
    Scenario: Duplicate a content with history doesn't change the state if it's submitted
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      When we post to "archive"
      """
      [{  "type":"text", "headline": "test1", "guid": "123", "original_creator": "#CONTEXT_USER_ID#", "state": "submitted",
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      And we post to "/archive/123/duplicate"
      """
      {"desk": "#desks._id#"}
      """
      When we get "/archive/#duplicate._id#"
      Then we get existing resource
      """
      {"state": "submitted", "_current_version": 2, "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}
      """
      When we get "/archive/#duplicate._id#?version=all"
      Then we get list with 2 items
      When we get "/archive?q=#desks._id#"
      Then we get list with 2 items

    @auth
    @provider
    Scenario: Duplicate a package
      Given empty "ingest"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And empty "archive"
      When we fetch from "reuters" ingest "tag_reuters.com_2014_newsml_KBN0FL0NM"
      And we post to "/ingest/#reuters.tag_reuters.com_2014_newsml_KBN0FL0NM#/fetch" with success
      """
      {
      "desk": "#desks._id#"
      }
      """
      Then we get "_id"
      When we post to "/archive/#_id#/duplicate"
      """
      {"desk": "#desks._id#"}
      """
      When we get "/archive?q=#desks._id#"
      Then we get list with 12 items

    @auth
    Scenario: Duplicate should fail when no desk specified
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{  "type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "submitted",
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      When we post to "/archive/123/duplicate"
      """
      {}
      """
      Then we get error 400
      """
      {"_issues": {"desk": {"required": 1}}}
      """

    @auth
    Scenario: Duplicate should fail if the source and destination desks are not same
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{  "type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "submitted",
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      When we post to "/desks"
      """
      [{"name": "Finance"}]
      """
      When we post to "/archive/123/duplicate"
      """
      {"desk": "#desks._id#"}
      """
      Then we get error 412
      """
      {"_message": "Duplicate is allowed within the same desk.", "_status": "ERR"}
      """

    @auth
    Scenario: User can't duplicate content without a privilege
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        And "archive"
        """
        [{  "type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "published",
            "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
        """
        When we login as user "foo" with password "bar"
        """
        {"user_type": "user", "email": "foo.bar@foobar.org"}
        """
        And we post to "/archive/123/duplicate"
        """
        [{"desk": "#desks._id#"}]
        """
        Then we get response code 403
