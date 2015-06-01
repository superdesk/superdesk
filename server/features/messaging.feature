Feature: Messaging

    @auth
    Scenario: Add users to a chat session
        Given empty "chat_session"
        When we post to "chat_session" with success
        """
        [{"users": []}]
        """
        Then we get existing resource
        """
        {"creator": "#CONTEXT_USER_ID#", "users": []}
        """
        When we post to "/users" with "foo" and success
        """
        {"username": "foo", "email": "foo@bar.com", "is_active": true, "sign_off": "abc"}
        """
        When we patch "chat_session/#chat_session._id#"
        """
        {"users": ["#foo#"]}
        """
        Then we get existing resource
        """
        {"creator": "#CONTEXT_USER_ID#", "users": ["#foo#"]}
        """
        When we post to "users" with "bar" and success
        """
        {"username": "bar", "email": "foobar@bar.com", "is_active": true, "sign_off": "foobar"}
        """
        When we post to "/desks" with success
        """
        {"name": "Sports Desk", "members": [{"user": "#bar#"}]}
        """
        When we patch "chat_session/#chat_session._id#"
        """
        {"desks": ["#desks._id#"]}
        """
        Then we get existing resource
        """
        {"creator": "#CONTEXT_USER_ID#", "users": ["#foo#"], "desks": ["#desks._id#"]}
        """
