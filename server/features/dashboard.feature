Feature: Dashboard

    @auth
    Scenario: User can create its dashboard
        When we post to "/dashboards"
        """
        {"user": "#CONTEXT_USER_ID#", "name": "test", "widgets": []}
        """
        Then we get new resource

    @auth
    Scenario: User can't change other users dashboard
        Given "users"
        """
        [{"username": "foo"}]
        """
        When we post to "/dashboards"
        """
        {"user": "#users._id#"}
        """
        Then we get response code 403
