Feature: Content Publishing

    @auth
    Scenario: Publish a user content
      Given "archive"
      """
      [{"headline": "test", "_version": 1, "state": "fetched"}]
      """
      When we publish "#archive._id#"
      Then we get OK response
      And we get existing resource
      """
      {"_version": 2, "state": "published"}
      """

    @auth
    Scenario: User can't publish without a privilege
      Given "archive"
      """
      [{"headline": "test", "_version": 1, "state": "fetched"}]
      """
      And we login as user "foo" with password "bar"
      """
      {"user_type": "user", "email": "foo.bar@foobar.org"}
      """
      When we publish "#archive._id#"
      Then we get response code 403

    @auth
    Scenario: User can't publish a draft item
      Given "archive"
      """
      [{"headline": "test", "_version": 1, "state": "draft"}]
      """
      When we publish "#archive._id#"
      Then we get response code 400

    @auth
    Scenario: User can't update a published item
      Given "archive"
      """
      [{"headline": "test", "_version": 1, "state": "fetched"}]
      """
      When we publish "#archive._id#"
      Then we get OK response
      When we patch "/archive/#archive._id#"
      """
      {"headline": "updating a published item"}
      """
      Then we get response code 400
