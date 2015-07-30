@wip
Feature: Workspace

    @auth
    Scenario: User can create its workspace
        When we post to "/workspaces"
        """
        {"user": "#CONTEXT_USER_ID#", "name": "test", "widgets": []}
        """
        Then we get new resource

    @auth
    Scenario: User can't change other users workspace
        Given "users"
        """
        [{"username": "foo"}]
        """
        When we post to "/workspaces"
        """
        {"user": "#users._id#"}
        """
        Then we get response code 403

    @auth
    Scenario: Workspace name should be unique per user
        When we post to "/workspaces"
        """
        {"user": "#CONTEXT_USER_ID#", "name": "test"}
        """
        And we post to "/workspaces"
        """
        {"user": "#CONTEXT_USER_ID#", "name": "test"}
        """
        Then we get response code 400

    @auth
    Scenario: Workspace name should be unique globally
        When we post to "/workspaces"
        """
        {"name": "test"}
        """
        And we post to "/workspaces"
        """
        {"name": "test"}
        """
        Then we get response code 400
