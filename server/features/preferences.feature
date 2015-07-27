Feature: User preferences
    @auth
    Scenario: List empty preferences
        Given empty "preferences"
        When we get "/preferences"
        Then we get error 405
        """
        {"_error": {"message": "The method is not allowed for the requested URL.", "code": 405}, "_status": "ERR"}
        """

    @auth
    Scenario: Fetch old preferences using new session
        When we get "/preferences/54d876dc102454a053a6d786"
        Then we get error 404

    @auth
    Scenario: Create new preference
        Given we have sessions "/sessions"

        When we get "/preferences/#SESSION_ID#"
        Then we get default preferences

    @auth
    Scenario: Update user archive view preference settings
        Given we have sessions "/sessions"

        When we get "/preferences/#SESSION_ID#"
        When we patch latest
        """
        {"user_preferences": {"archive:view": {"view": "compact" }}}
        """

        Then we get existing resource
        """
        {
            "user_preferences": {
                "archive:view": {
                    "category": "archive",
                    "default": "mgrid",
                    "label": "Users archive view format",
                    "type": "string",
                    "view": "compact"
                }
            }
        }
        """

    @auth
    Scenario: Update user feature preview preference settings
        Given we have sessions "/sessions"

        When we patch "/preferences/#SESSION_ID#"
        """
        {"user_preferences": {
            "feature:preview": {"enabled": true},
            "editor:theme": {"label": "Editor"}
        }}
        """
        Then we get existing resource
        """
        {
            "user_preferences": {
                "feature:preview": {
                    "category": "feature",
                    "default": false,
                    "enabled": true,
                    "label": "Enable Feature Preview",
                    "type": "bool"
                },
                "editor:theme": {"type": "string"}
            }
        }
        """
        And there is no "label" in "editor:theme" preferences


    @auth
    Scenario: Update user preference settings
        Given we have sessions "/sessions"

        When we patch "/preferences/#SESSION_ID#"
        """
        {"user_preferences": {"email:notification": {"enabled": false }}}
        """
        Then we get existing resource
        """
        {
            "user_preferences": {
                "email:notification": {
                    "category": "notifications",
                    "default": true,
                    "enabled": false,
                    "label": "Send notifications via email",
                    "type": "bool"
                }
            }
        }
        """

    @auth
    Scenario: Update editor theme user preference settings
        Given we have sessions "/sessions"

        When we patch "/preferences/#SESSION_ID#"
        """
        {"user_preferences": {"editor:theme": {"theme": "railscast", "category": "editor"}}}
        """

        When we get "/preferences/#SESSION_ID#"
        Then we get existing resource
        """
        {
            "user_preferences": {
                "editor:theme": {
                    "theme": "railscast",
                    "type": "string"
                }
            }
        }
        """

    @auth
    Scenario: Update user preference settings - wrong preference
        Given we have sessions "/sessions"
        When we get "/preferences/#SESSION_ID#"

        When we patch "/preferences/#SESSION_ID#"
        """
        {"user_preferences": {"email:bad_name": {"enabled": false }}}
        """
        Then we get error 400
        """
        {"_status": "ERR", "_issues": {"validator exception": "Invalid preference: email:bad_name"}}
        """

    @auth
    Scenario: Update session preference settings
        Given we have sessions "/sessions"
        When we get "/preferences/#SESSION_ID#"
        When we patch "/preferences/#SESSION_ID#"
        """
        {"session_preferences": {"desk:items": [123]}}
        """

        Then we get existing resource
        """
        {"session_preferences": {"desk:items": [123]}}
        """
        When we delete "/auth/#SESSION_ID#"
        Given we login as user "test_user" with password "test_password" and user type "user"
        When we get "/preferences/#SESSION_ID#"
        Then we get error 404

    @auth
    Scenario: Get active privileges from user with preferences
        Given we have sessions "/sessions"

        When we patch "/users/#users._id#"
        """
        {"user_type": "user", "privileges": {"archive:spike": 1}}
        """

        When we get "/preferences/#SESSION_ID#"
        Then we get existing resource
        """
        {
            "active_privileges": {"archive:spike": 1},
            "user_preferences": {
                "feature:preview": {
                    "category": "feature",
                    "default": false,
                    "enabled": false,
                    "label": "Enable Feature Preview",
                    "type": "bool"
                }
            }
        }
        """

    @auth
    Scenario: Get active privileges from user and role with preferences
        Given we have sessions "/sessions"

        Given "roles"
        """
        [{"name": "A" , "privileges": {"fungi": 1}}]
        """

        When we patch "/users/#users._id#"
        """
        {"role": "#roles._id#", "user_type": "user", "privileges": {"spike": 1}}
        """

        When we get "/preferences/#SESSION_ID#"
        Then we get existing resource
        """
        {
            "active_privileges": {"fungi": 1, "spike": 1},
            "allowed_actions": [
                {
                    "exclude_states": ["spiked", "published", "killed"],
                    "include_states": [],
                    "name": "spike",
                    "privileges": ["spike"]
                }
            ],
            "user_preferences": {
                "feature:preview": {
                    "category": "feature",
                    "default": false,
                    "enabled": false,
                    "label": "Enable Feature Preview",
                    "type": "bool"
                }
            }
        }
        """

    @auth
    Scenario: Get all active privileges from administrator with preferences
        Given we have sessions "/sessions"

        When we patch "/users/#users._id#"
        """
        {"user_type": "administrator", "privileges": {}}
        """

        When we get "/preferences/#SESSION_ID#"
        Then we get existing resource
        """
        {
            "active_privileges": {"spike": 1},
            "allowed_actions": [
                {
                    "exclude_states": ["spiked", "published", "killed"],
                    "include_states": [],
                    "name": "spike",
                    "privileges": ["spike"]
                }
            ],
            "user_preferences": {
                "feature:preview": {
                    "category": "feature",
                    "default": false,
                    "enabled": false,
                    "label": "Enable Feature Preview",
                    "type": "bool"
                }
            }
        }
        """

    @auth
    Scenario: Session Preferences are deleted when user logsout of Superdesk
      Given I logout
      When we login as user "foo" with password "bar" and user type "user"
      Then we get "/users/test_user" and match
      """
      {"username": "test_user", "session_preferences": {}}
      """
