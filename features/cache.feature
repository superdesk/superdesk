Feature: HTTP Caching

    @auth
    Scenario: If-Modified-Since caching
        Given "users"
        """
        [{"username": "foo", "updated": "2012-12-12T10:11:12Z"}]
        """

        When we get "/users"
        """
        If-Modified-Since: 2014-12-12T10:10:10+0000
        """

        Then we get not modified response