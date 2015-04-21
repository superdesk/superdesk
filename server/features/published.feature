Feature: Published Items Repo

    @auth
    Scenario: List empty published
        Given empty "published"
        When we get "/published"
        Then we get list with 0 items

    @auth
    Scenario: Get archive items with published state
        Given "published"
        """
        [{"_id": "tag:example.com,0000:newsml_BRE9A605", "state": "published"}]
        """

        When we get "/published"
        Then we get existing resource
        """
        {"_items": [{"_id": "tag:example.com,0000:newsml_BRE9A605", "state": "published"}]}
        """
    @auth
    Scenario: Get archive items with non-published state
        Given "published"
        """
        [{"_id": "tag:example.com,0000:newsml_BRE9A607", "state": "draft"}]
        """

        When we get "/published"
        Then we get list with 0 items