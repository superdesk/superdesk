Feature: Ingest

    @auth
    Scenario: List empty ingest
        Given empty "ingest"
        When we get "/ingest"
        Then we get list with 0 items

    @auth
    Scenario: List ingest with items
        Given "ingest"
            """
            [{
                "guid": "tag:example.com,0000:newsml_BRE9A605",
                "urgency": "1",
                "provider": "example.com",
                "versioncreated": "2013-11-11T11:11:11+00:00"
            }]
            """

        When we get "/ingest"
        Then we get list with 1 items
        And we get facets "type,provider,urgency,subject,place"
