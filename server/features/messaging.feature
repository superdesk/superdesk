Feature: Messaging

  @auth
  @notification
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
  @notification
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
  @notification
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
    When we post to "/users" with "foo" and success
    """
    {"username": "foo", "email": "foo@foo.com", "is_active": true, "sign_off": "foo"}
    """
    And we post to "chat_sessions" with success
    """
    {"users": ["#foo#"]}
    """
    Then we get existing resource
    """
    {"creator": "#CONTEXT_USER_ID#", "users": ["#foo#"]}
    """
    When we post to "chat_messages" with success
    """
    [{"chat_session": "#chat_sessions._id#", "sender": "#CONTEXT_USER_ID#", "message": "Test Message"}]
    """
    Then we get notifications
    """
    [{"event": "*/new_message", "extra": {"message": "Test Message"}}]
    """

  @auth
  @notification
  Scenario: Deleting a Chat Session should automatically delete Chat Messages
    Given empty "chat_sessions"
    When we post to "/users" with "foo" and success
    """
    {"username": "foo", "email": "foo@foo.com", "is_active": true, "sign_off": "foo"}
    """
    And we post to "chat_sessions" with success
    """
    {"users": ["#foo#"]}
    """
    Then we get existing resource
    """
    {"creator": "#CONTEXT_USER_ID#", "users": ["#foo#"]}
    """
    When we post to "chat_messages" with success
    """
    [{"chat_session": "#chat_sessions._id#", "sender": "#CONTEXT_USER_ID#", "message": "Test Message"}]
    """
    And we delete "/chat_sessions/#chat_sessions._id#"
    And we get "chat_messages?chat_session=#chat_sessions._id#"
    Then we get list with 0 items

  @auth
  @notification
  Scenario: User receives a notification when added to a Chat Session
    Given empty "chat_sessions"
    When we post to "/users" with "foo" and success
    """
    {"username": "foo", "email": "foo@foo.com", "is_active": true, "sign_off": "foo"}
    """
    And we post to "chat_sessions" with success
    """
    {"users": ["#foo#"]}
    """
    Then we get notifications
    """
    [{"event": "messaging:user:added"}]
    """
    And we get existing resource
    """
    {"creator": "#CONTEXT_USER_ID#", "users": ["#foo#"]}
    """

  @auth
  @notification
  Scenario: Find the number of chat sessions a user is participating
    Given empty "chat_sessions"
    When we post to "/users" with "foo" and success
    """
    {"username": "foo", "email": "foo@foo.com", "is_active": true, "sign_off": "foo"}
    """
    And we post to "chat_sessions" with success
    """
    {"users": ["#foo#"]}
    """
    And we login as user "bar" with password "foo"
    """
    {"user_type": "user", "email": "foo.bar@foobar.org"}
    """
    And we post to "chat_sessions" with success
    """
    {"users": ["#foo#"]}
    """
    And we get "/chat_sessions"
    Then we get list with 2 items
    When we get "/chat_sessions?recipients=#foo#"
    Then we get list with 2 items

  @auth
  @notification
  Scenario: Removing a Desk(s) to a chat session
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
    And we delete "/desks/#desks._id#"
    Then we get notifications
    """
    [{"event": "chat_session_end", "extra": {"message": "Chat Session Ends as the Desk(s) is removed"}}]
    """
    When we get "/chat_sessions/#chat_sessions._id#"
    Then we get error 404

  @auth
  @notification
  Scenario: Removing a Group(s) to a chat session
    Given empty "chat_sessions"
    When we post to "users" with "bar" and success
    """
    {"username": "bar", "email": "bar@bar.com", "is_active": true, "sign_off": "bar"}
    """
    And we post to "/groups"
    """
    {"name": "Sports group", "members": [{"user": "#bar#"}]}
    """
    And we post to "chat_sessions" with success
    """
    {"groups": ["#groups._id#"]}
    """
    And we delete "/groups/#groups._id#"
    Then we get notifications
    """
    [{"event": "chat_session_end", "extra": {"message": "Chat Session Ends as the Group(s) is removed"}}]
    """
    When we get "/chat_sessions/#chat_sessions._id#"
    Then we get error 404
