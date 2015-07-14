Feature: Copy Content in Personal Workspace

    @auth
    Scenario: Copy content in personal workspace
      Given "archive"
      """
      [{"type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "draft"}]
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
      {"headline": "test3"}
      """
      When we post to "/archive/123/copy"
      """
      {}
      """
      When we get "/archive/#copy._id#"
      Then we get existing resource
      """
      {"state": "draft"}
      """
      And we get version 4
      When we get "/archive/#copy._id#?version=all"
      Then we get list with 4 items
      When we get "/archive/"
      Then we get list with 2 items

    @auth
    Scenario: Copy should fail if copying an item in a desk
      Given "desks"
      """
      [{"name": "Sports"}]
      """
      And "archive"
      """
      [{  "type":"text", "headline": "test1", "guid": "123", "original_creator": "abc", "state": "submitted",
          "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "user": "#CONTEXT_USER_ID#"}}]
      """
      When we post to "/archive/123/copy"
      """
      {}
      """
      Then we get error 412
      """
      {"_message": "Copy is not allowed on items in a desk.", "_status": "ERR"}
      """
