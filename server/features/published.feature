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
        [{"_id": "tag:example.com,0000:newsml_BRE9A605", "state": "published", "allow_post_publish_actions": true}]
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

    @auth
    Scenario: Delete Item from archived
        Given "published"
	    """
        [{"_id": "tag:example.com,0000:newsml_BRE9A605", "type": "text", "state": "published", "allow_post_publish_actions": false}]
	    """
        When we patch "/users/#CONTEXT_USER_ID#"
        """
        {"user_type": "user", "privileges": {"archived": 1, "archive": 1, "unlock": 1, "tasks": 1, "users": 1}}
        """
        Then we get response code 200
        When we get "/archived"
        Then we get list with 1 items
	    """
        {"_items": [{"_id": "tag:example.com,0000:newsml_BRE9A605", "type": "text", "state": "published", "allow_post_publish_actions": false, "can_be_removed": false}]}
	    """
        When we delete "/archived/tag:example.com,0000:newsml_BRE9A605"
        Then we get response code 204
        When we get "/archived"
        Then we get list with 0 items

    @auth
    Scenario: Fails to delete from archived with no privilege
        Given "published"
	    """
        [{"_id": "tag:example.com,0000:newsml_BRE9A605", "type": "text", "state": "published", "allow_post_publish_actions": false}]
	    """
        When we patch "/users/#CONTEXT_USER_ID#"
        """
        {"user_type": "user", "privileges": {"archived": 0, "archive": 1, "unlock": 1, "tasks": 1, "users": 1}}
        """
        Then we get response code 200
        When we get "/archived"
        Then we get list with 1 items
	    """
        {"_items": [{"type": "text", "state": "published", "allow_post_publish_actions": false, "can_be_removed": false}]}
	    """
        When we delete "/archived/#published._id#"
        Then we get response code 403
