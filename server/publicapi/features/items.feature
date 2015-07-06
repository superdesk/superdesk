Feature: Public content

    Scenario: Read an item
        Given "items"
        """
        [{
            "_id": "tag:example.com,0000:newsml_BRE9A605",
            "headline": "Breaking news in Timbuktu 123",
            "mimetype": "text/plain"
        }]
        """
        When we get "/items/tag:example.com,0000:newsml_BRE9A605"
        Then we get existing resource
        """
        {"headline": "Breaking news in Timbuktu 123", "mimetype": "text/plain"}
        """

    Scenario: Search by date interval
      Given "items"
        """
        [
            {
                "_id": "tag:example.com,0000:newsml_BRE9A605",
                "headline": "Breaking news in Timbuktu 123",
                "type": "text",
                "versioncreated": "2014-03-16T06:49:47+0000"
            },
            {
                "_id": "tag:example.com,0000:newsml_BRE9A606",
                "headline": "Breaking news in London 123",
                "type": "text",
                "versioncreated": "2014-03-15T06:49:47+0000"
            },
            {
                "_id": "tag:example.com,0000:newsml_BRE9A607",
                "headline": "Breaking news in Sydney",
                "type": "picture",
                "versioncreated": "2014-04-15T06:49:47+0000"
            }
        ]
        """
        When we get "/items?start_date=2014-03-16"
        Then we get list with 2 items
        """
        {
            "_items": [
                {
                    "headline": "Breaking news in Timbuktu 123",
                    "versioncreated": "2014-03-16T06:49:47+0000",
                    "type": "text",
                    "uri": "http:\/\/localhost:5050\/items\/tag%3Aexample.com%2C0000%3Anewsml_BRE9A605",
                    "_links": {
                        "self": {
                            "title": "Item",
                            "href": "items\/tag:example.com,0000:newsml_BRE9A605"
                        }
                    }
                },
                {
                    "headline": "Breaking news in Sydney",
                    "versioncreated": "2014-04-15T06:49:47+0000",
                    "type": "picture",
                    "uri": "http:\/\/localhost:5050\/items\/tag%3Aexample.com%2C0000%3Anewsml_BRE9A607",
                    "_links": {
                        "self": {
                            "title": "Item",
                            "href": "items\/tag:example.com,0000:newsml_BRE9A607"
                        }
                    }
                }
            ]
        }
        """
        When we get "/items?end_date=2014-03-16"
        Then we get list with 1 items
        """
        {
            "_items": [
                {
                    "headline": "Breaking news in Timbuktu 123",
                    "versioncreated": "2014-03-16T06:49:47+0000",
                    "type": "text",
                    "uri": "http:\/\/localhost:5050\/items\/tag%3Aexample.com%2C0000%3Anewsml_BRE9A605",
                    "_links": {
                        "self": {
                            "title": "Item",
                            "href": "items\/tag:example.com,0000:newsml_BRE9A605"
                        }
                    }
                }
           ]
        }
        """
        When we get "/items"
        Then we get list with 0 items
