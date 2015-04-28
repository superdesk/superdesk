Feature: Prepopulate public content

    Scenario: Prepopulate content
    	When we post to "/prepopulate"
    	"""
    	[{}]
    	"""
        Then we get response code 201

        When we get "/items"
        Then we get list with 1 items
        """
        {
        	"_items": [
        		{
        			"uri": "http://localhost:5050/items/tag%3Aexample.com%2C0000%3Anewsml_BRE9A605",
        			"type": "picture"
        		}
        	]
        }
        """

        When we get "/packages"
        Then we get list with 1 items
        """
        {
        	"_items": [
        		{
        			"uri": "http://localhost:5050/packages/tag%3Aexample.com%2C0001%3Anewsml_BRE9A606",
        			"type": "composite",
        			"headline": "foo bar"
        		}
        	]
        }
        """

    Scenario: Prepopulate with invalid profile
    	When we post to "/prepopulate"
    	"""
    	[{"profile": "invalid profile"}]
    	"""
        Then we get error 404
