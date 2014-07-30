Feature: User Role Resource

    @auth
    Scenario: List empty user roles
        Given empty "user_roles"
        When we get "/user_roles"
        Then we get list with 0 items

    @auth
    Scenario: Create a new child role
        Given "user_roles"
            """
            [{"_id": "528de7b03b80a13eefc5e610", "name": "Administrator"}]
            """

        When we post to "/user_roles"
            """
            {"name": "Editor", "extends": "528de7b03b80a13eefc5e610"}
            """

        And we get "/user_roles"
        Then we get list with 2 items

    @auth
    Scenario: Set permissions for given role
        Given "user_roles"
            """
            [{"name": "Admin"}]
            """

        When we patch given
            """
            {"permissions": {"ingest": {"read": 1}, "archive": {"write": 1}}}
            """

        And we get given
        Then we get "permissions"

    @auth
    Scenario: Check permissions on read with role
        Given "user_roles"
            """
            [{"name": "User"}]
            """

        And we have "User" role
        When we get "/ingest"
        Then we get response code 401

    @auth
    Scenario: Check permissions on read with role and permissions
        Given "user_roles"
            """
            [{"name": "Editor", "permissions": {"ingest": {"read": 1}}}]
            """
        And we have "Editor" role
        When we get "/ingest"
        Then we get response code 200

    @auth
    Scenario: User has always permissions to edit himself
        Given "user_roles"
            """
            [{"name": "Subscriber"}]
            """
        And we have "Subscriber" role
        When we get user profile
        Then we get response code 200

    @auth
    Scenario: Inherit permissions from extended roles
        Given "user_roles"
            """
            [
                {"name": "Jurnalist", "permissions": {"ingest": {"read": 1}}},
                {"name": "Editor"}
            ]
            """

        And role "Editor" extends "Jurnalist"
        And we have "Editor" role
        When we get "/ingest"
        Then we get response code 200
        
        
  #  @auth
  #  Scenario: Set a role to a user
  #      
  #      Given empty "user_roles"
  #      
  #      When we post to "/user_roles"
  #          """
  #          {"name": "Editor"}
  #          """
  #
  #      When we patch "/users/test_user"
  #          """
  #          {"role": "#USER_ROLES_ID#"}
  #          """
  #           
  #     Then we get existing resource
  #      """
  #      {"username": "test_user", "role": "#USER_ROLES_ID#"}
  #      """             
