Feature: Legal archive

    @auth
    Scenario: List empty legal archive
        Given empty "legal_archive"
        Given "roles"
        """
        [{"name": "Manager", "privileges": {"legal_archive": 1}}]
        """
        Given we have "Manager" role
        When we get "legal_archive"
        Then we get list with 0 items

    @auth
    Scenario: Get archive items with published state
        Given "legal_archive"
        """
        [{"_id": "tag:example.com,0000:newsml_BRE9A605", "guid": "tag:example.com,0000:newsml_BRE9A605", "state": "published"}]
        """
        Given "roles"
        """
        [{"name": "Manager", "privileges": {"legal_archive": 1}}]
        """
        Given we have "Manager" role
        When we get "legal_archive"
        Then we get existing resource
        """
        {"_items": [{"_id": "tag:example.com,0000:newsml_BRE9A605", "state": "published"}]}
        """

    @auth
    Scenario: User can't fetch from legal archive without a privilege
      Given "legal_archive"
      """
      [{"_id": "tag:example.com,0000:newsml_BRE9A605", "guid": "tag:example.com,0000:newsml_BRE9A605",
        "headline": "test", "_current_version": 1, "state": "published"}]
      """
      And we login as user "foo" with password "bar" and user type "user"
      """
      {"user_type": "user", "email": "foo.bar@foobar.org"}
      """
      When we get "legal_archive"
      Then we get error 403
