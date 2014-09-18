Feature: News Items Archive Comments

    @auth
    Scenario: Create comment for item
        Given "archive"
        """
        [{"_id": "xyz", "guid": "testid", "headline": "test"}]
        """
        Given empty "item_comments"
        When we post to "/item_comments"
        """
        [{"text": "test comment", "item": "xyz"}]
        """
        And we get "/item_comments"
        Then we get list with 1 items
        """
        {"_items": [{"text": "test comment", "item": "xyz"}]}
        """

    @auth
    @wip
    Scenario: Create comments for item
        Given "archive"
        """
        [{"_id": "xyz", "guid": "testid", "headline": "test"}]
        """
        Given empty "item_comments"
        When we post to "/item_comments"
        """
        [{"text": "test comment", "item": "xyz"}]
        """
        When we post to "/item_comments"
        """
        [{"text": "test comment 1", "item": "xyz"}]
        """
        And we get "/item_comments"
        Then we get list with 2 items

        When we get "/activity"
        Then we get list with 4 items


    @auth
    Scenario: Create comment for item - get from /archive/_id/comments
        Given "archive"
        """
        [{"_id": "xyz", "guid": "testid", "headline": "test"}]
        """
        Given empty "item_comments"
        When we post to "/item_comments"
        """
        [{"text": "test comment", "item": "xyz"}]
        """
        And we get "/archive/xyz/comments"
        Then we get list with 1 items
        """
        {"_items": [{"text": "test comment", "item": "xyz"}]}
        """

    @auth
    Scenario: Create comment for item(Fail) - wrong user supplied
        Given "archive"
        """
        [{"_id": "xyz", "guid": "testid", "headline": "test"}]
        """
        Given empty "item_comments"
        When we post to "users"
        """
        {"username": "foo", "email": "foo@bar.com"}
        """
        When we post to "/item_comments"
        """
        [{"text": "test comment", "item": "xyz", "user": "#USERS_ID#"}]
        """
        Then we get error 400
        """
        {"_status": "ERR", "_issues": "Commenting on behalf of someone else is prohibited.", "_message": ""}
        """

    @auth
    Scenario: Create comment for item(Fail) - get from /archive/wrong_id/comments
        Given "archive"
        """
        [{"_id": "xyz", "guid": "testid", "headline": "test"}]
        """
        Given empty "item_comments"
        When we post to "/item_comments"
        """
        [{"text": "test comment", "item": "xyz"}]
        """
        And we get "/archive/wrong_id/comments"
        Then we get error 400
        """
        {"_message": "", "_issues": "Invalid content item ID provided: wrong_id", "_status": "ERR"}
        """


    @auth
    Scenario: Create comment for item(Fail) - wrong archive item supplied
        Given empty "archive"
        Given empty "item_comments"
        When we post to "/item_comments"
        """
        [{"text": "test comment", "item": "xyz"}]
        """
        Then we get error 400
        """
        {"_issues": {"item": "value 'xyz' must exist in resource 'archive', field '_id'."}, "_status": "ERR", "_error": {"code": 400, "message": "Insertion failure: 1 document(s) contain(s) error(s)"}}
        """
        
        
    @auth
    @notification
    Scenario: Create comment for item with user one mentions
        Given "archive"
        """
        [{"_id": "xyz", "guid": "testid", "headline": "test"}]
        """
        Given empty "item_comments"
        
        When we post to "/users"
        """
        {"username": "joe", "display_name": "Joe Black", "email": "joe@black.com"}
        """
        Then we get new resource
        """
        {"username": "joe", "display_name": "Joe Black", "email": "joe@black.com"}
        """
        When we post to "/item_comments"
        """
        [{"text": "test comment @no_user with one user mention @joe", "item": "xyz"}]
        """
        And we get "/item_comments"
        Then we get list with 1 items
        """
        {"_items": [{"text": "test comment @no_user with one user mention @joe", "item": "xyz", "mentioned_users": {"joe": "#USERS_ID#"}}]}
        """ 
        When we get "/users/test_user"
        Then we get "_id"
        And we get notifications
        """
        [{"event": "item:comment", "extra": {"item": "xyz"}, "_created": ""}, {"event": "activity"}]
        """
