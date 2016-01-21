Feature: Published Items Repo

    @auth
    Scenario: List empty published
        Given empty "published"
        When we get "/published"
        Then we get list with 0 items

    @auth
    Scenario: Get published items with published state
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
    Scenario: Insert published items with non-published state
        When we post to "published"
        """
        [{"_id": "tag:example.com,0000:newsml_BRE9A607", "state": "draft", "queue_state": "pending"}]
        """
        Then we get error 400
        """
         {"_status": "ERR", "_message": "Invalid state (draft) for the Published item."}
        """

    @auth
    Scenario: Update published items with non-published state
    	Given "archive"
    	"""
    	[{"_id": "tag:example.com,0000:newsml_BRE9A607", "guid": "tag:example.com,0000:newsml_BRE9A607"}]
    	"""
        When we post to "published" with success
        """
        [{"_id": "tag:example.com,0000:newsml_BRE9A607", "state": "published", "queue_state": "pending"}]
        """
        When we patch "/published/tag:example.com,0000:newsml_BRE9A607"
        """
        {"state": "corrected"}
        """
        Then we get OK response
        When we patch "/published/tag:example.com,0000:newsml_BRE9A607"
        """
        {"state": "draft"}
        """
        Then we get error 400
        """
        {"_status": "ERR", "_issues": {"validator exception": "400: Invalid state (draft) for the Published item."}}
        """
