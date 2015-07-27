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

    Scenario: Filter by date interval
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
        When we get "/items?start_date=2015-02-01&end_date=2014-03-5"
        Then we get error 10002
        """
        {"_issues": "Start date must not be greater than end date", "_status": "ERR", "_message": "Bad parameter value."}
        """

    Scenario: Error on missing rendition
        Given "items"
        """
        [
            {
                "_id": "tag:example.com,0000:newsml_BRE9A605",
                "headline": "Breaking news in Timbuktu 123",
                "type": "picture",
                "versioncreated": "2014-03-16T06:49:47+0000",
                "renditions": {
                    "original": {
                        "width": "1496",
                        "height": "805",
                        "media": "6590c3cd46e6da7ea5e70b90"
                    }
                }
            }
        ]
        """
        When we get "/items/tag%3Aexample.com%2C0000%3Anewsml_BRE9A605"
        Then we get existing resource
        """
        {
            "headline": "Breaking news in Timbuktu 123",
            "type": "picture",
            "versioncreated": "2014-03-16T06:49:47+0000",
            "renditions": {
                "original": {
                    "width": "1496",
                    "height": "805",
                    "media": "6590c3cd46e6da7ea5e70b90",
                    "href": "http://localhost:5050/assets/6590c3cd46e6da7ea5e70b90/raw"
                }
            }
        }
        """
        When we get "/assets/6590c3cd46e6da7ea5e70b90/raw"
        Then we get error 10003
        """
        {"_issues": "File not found on media storage.", "_status": "ERR", "_message": "File not found."}
        """

    Scenario: Search by text
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
        When we get "/items?start_date=2014-03-16&q=Timbuktu"
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
        When we get "/items?start_date=2014-03-16&q=Timbuktu,Sydney"
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
