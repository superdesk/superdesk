Feature: HTTP Caching

    @auth
    Scenario: If-Modified-Since caching
        Given "users"
        """
        [{"username": "foo", "_updated": "2012-12-12T10:11:12+0000"}]
        """

        When we get "/users"
        """
        If-Modified-Since: Tue, 18 Sep 2012 10:12:30 GMT
        """

        Then we get not modified response