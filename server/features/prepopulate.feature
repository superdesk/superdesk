Feature: Prepopulate

	@auth
    @dbauth
    Scenario: Prepopulate and erase
        Given empty "roles"
        Given empty "desks"

        When we post to "/prepopulate"
        """
        {}
        """
        Then we get new resource
        """
        {"_status": "OK"}
        """

		When we setup test user

        When we get "/users"
        Then we get list with 6 items
        """
        {"_items": [{"username":"admin", "first_name":"first name", "last_name":"last name", "user_type": "administrator", "email": "a@a.com"},
                   {"username": "test_user"}]}
        """

        When we find for "users" the id as "user_admin" by "{"username": "admin"}"
        When we find for "users" the id as "user_admin1" by "{"username": "admin1"}"
        When we find for "users" the id as "user_admin2" by "{"username": "admin2"}"
        When we find for "users" the id as "user_admin3" by "{"username": "admin3"}"
        When we find for "users" the id as "user_admin4" by "{"username": "admin4"}"

        And we get "/desks"
        Then we get list with 2 items
        """
        {"_items": [{"members": [{"user": "#user_admin#"}, {"user": "#user_admin1#"}, {"user": "#user_admin2#"}, {"user": "#user_admin3#"}], "name": "Sports Desk"},
                    {"members": [{"user": "#user_admin#"}, {"user": "#user_admin4#"}, {"user": "#user_admin1#"}], "name": "Politic Desk"}
                   ]}
        """

        When we get "/roles"
        Then we get list with 4 items
        """
        {"_items": [
        	{"name": "Editor", "privileges": {"ingest": {"read": 1}}},
        	{"name": "Writer", "privileges": {"ingest": {"read": 1}}},
        	{"name": "Superadmin", "privileges": {"ingest": {"read": 1}}},
        	{"name": "admin", "privileges": {"ingest": {"read": 1}}}


        ]}
        """

	@auth
    @dbauth
    @notesting
    Scenario: Prepopulate and app not on testing mode
        Given empty "roles"
        Given empty "desks"

        When we post to "/prepopulate"
        """
        {}
        """
		Then we get error 404


    @auth
    @dbauth
    Scenario: Prepopulate and no erase
        Given empty "roles"
        Given empty "desks"

		When we post to "/users"
    	"""
        {"username": "foo", "password": "barbar", "email": "foo@bar.com", "sign_off": "abc"}
        """
        Then we get new resource
        """
        {"username": "foo", "email": "foo@bar.com"}
        """

        When we post to "/prepopulate"
        """
        {"remove_first": false}
        """
        Then we get new resource
        """
        {"_status": "OK"}
        """

        When we get "/users"
        Then we get list with 7 items
        """
        {"_items": [{"username":"admin", "first_name":"first name", "last_name":"last name", "user_type": "administrator", "email": "a@a.com"},
			        {"username":"admin1", "first_name":"first name1", "last_name":"last name1", "user_type": "administrator", "email": "a1@a.com"},
			        {"username":"admin2", "first_name":"first name2", "last_name":"last name2", "user_type": "administrator", "email": "a2@a.com"},
			        {"username":"admin3", "first_name":"first name3", "last_name":"last name3", "user_type": "administrator", "email": "a3@a.com"},
			        {"username":"admin4", "first_name":"first name4", "last_name":"last name4", "user_type": "administrator", "email": "a4@a.com"},
                    {"username": "foo", "email": "foo@bar.com"},
                    {"username": "test_user"}]}
        """


    @auth
    @dbauth
    Scenario: Prepopulate with custom profile
        Given empty "roles"
        Given empty "desks"

        When we post to "/prepopulate"
        """
        {"profile": "app_prepopulate_data_test"}
        """
        Then we get new resource
        """
        {"_status": "OK"}
        """

		When we setup test user

        When we get "/users"
        Then we get list with 2 items
        """
        {"_items": [{"username":"admin_other", "first_name":"first name other", "last_name":"last name other", "user_type": "administrator", "email": "a@a_other.com"},
                   {"username": "test_user"}]}
        """

        When we get "/roles"
        Then we get list with 0 items

        When we get "/desks"
        Then we get list with 0 items
