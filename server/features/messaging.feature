Feature: Messaging

    @auth
    Scenario: Add users to a chat session
        Given empty "chat_sessions"
        When we post to "chat_sessions" with success
        """
        [{"users": []}]
        """
        Then we get existing resource
        """
        {"creator": "#CONTEXT_USER_ID#", "users": []}
        """
        When we post to "/users" with "foo" and success
        """
        {"username": "foo", "email": "foo@foo.com", "is_active": true, "sign_off": "foo"}
        """
        And we patch "chat_sessions/#chat_sessions._id#"
        """
        {"users": ["#foo#"]}
        """
        Then we get existing resource
        """
        {"creator": "#CONTEXT_USER_ID#", "users": ["#foo#"]}
        """

    @auth
    Scenario: Add Desk(s) to a chat session
        Given empty "chat_sessions"
        When we post to "users" with "bar" and success
        """
        {"username": "bar", "email": "bar@bar.com", "is_active": true, "sign_off": "bar"}
        """
        And we post to "/desks" with success
        """
        {"name": "Sports Desk", "members": [{"user": "#bar#"}]}
        """
        And we post to "chat_sessions" with success
        """
        {"desks": ["#desks._id#"]}
        """
        Then we get existing resource
        """
        {"creator": "#CONTEXT_USER_ID#", "desks": ["#desks._id#"]}
        """

    @auth
    Scenario: Add Group(s) to a chat session
        Given empty "chat_sessions"
        When we post to "users" with "foobar" and success
        """
        {"username": "foobar", "email": "foobar@foobar.com", "is_active": true, "sign_off": "foobar"}
        """
        And we post to "/groups"
        """
        {"name": "Sports group", "members": [{"user": "#foobar#"}]}
        """
        And we post to "chat_sessions" with success
        """
        {"groups": ["#groups._id#"]}
        """
        Then we get existing resource
        """
        {"creator": "#CONTEXT_USER_ID#", "groups": ["#groups._id#"]}
        """

    @auth
    @notification
    Scenario: Recipients receive message when sender sends message
        Given empty "chat_sessions"
        When we post to "chat_sessions" with success
        """
        [{"users": []}]
        """
        And we post to "/users" with "foo" and success
        """
        {"username": "foo", "email": "foo@foo.com", "is_active": true, "sign_off": "foo"}
        """
        And we patch "chat_sessions/#chat_sessions._id#"
        """
        {"users": ["#foo#"]}
        """
        Then we get existing resource
        """
        {"creator": "#CONTEXT_USER_ID#", "users": ["#foo#"]}
        """
        When we post to "chat_message" with success
        """
        [{"chat_session": "#chat_sessions._id#", "sender": "#CONTEXT_USER_ID#", "message": "Test Message"}]
        """
        Then we get notifications
        """
        [{"event": "*/new_message", "extra": {"message": "Test Message"}}]
        """
