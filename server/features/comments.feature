Feature: Default Comments

    @auth
    Scenario: Create comment
        Given empty "comments"
        When we post to "/comments" with success
        """
        [{"text": "test comment", "item": "xyz"}]
        """
        And we get "/comments"
        Then we get list with 1 items
        """
        {"_items": [{"text": "test comment", "item": "xyz"}]}
        """

    @auth
    Scenario: Create comments
        Given empty "comments"
        When we post to "/comments" with success
        """
        [{"text": "test comment", "item": "xyz"}]
        """
        When we post to "/comments" with success
        """
        [{"text": "test comment 1", "item": "xyz"}]
        """
        And we get "/comments"
        Then we get list with 2 items


    @auth
    Scenario: Create comment (Fail) - wrong user supplied
        Given empty "comments"
        When we post to "users" with success
        """
        {"username": "foo", "email": "foo@bar.com", "is_active": true, "sign_off": "abc"}
        """
        When we post to "/comments"
        """
        [{"text": "test comment", "item": "xyz", "user": "#users._id#"}]
        """
        Then we get error 403
        """
        {"_status": "ERR", "_message": "Commenting on behalf of someone else is prohibited."}
        """


    @auth
    @notification
    Scenario: Create comment with one user mention
        Given empty "comments"
        When we post to "/users"
        """
        {"username": "joe", "display_name": "Joe Black", "email": "joe@black.com", "is_active": true, "sign_off": "abc"}
        """
        Then we get new resource
        """
        {"username": "joe", "display_name": "Joe Black", "email": "joe@black.com"}
        """
        When we mention user in comment for "/comments"
        """
        [{"text": "test comment @no_user with one user mention @joe", "item": "xyz"}]
        """
        And we get "/comments"
        Then we get list with 1 items
        """
        {"_items": [{"text": "test comment @no_user with one user mention @joe", "item": "xyz", "mentioned_users": {"joe": "#users._id#"}}]}
        """
        When we get "/users/test_user"
        Then we get "_id"
        And we get notifications
        """
        [{"event": "comments", "extra": {"item": "xyz"}, "_created": "__any_value__"}, {"event": "activity"}]
        """
