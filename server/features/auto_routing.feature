Feature: Auto Routing

    @auth @provider @vocabulary
    Scenario: Content is fetched based on subject metadata
        Given empty "desks"
        Given "filter_conditions"
        """
        [{
            "_id": "1111111111aaaa1111111111",
            "name": "Finance Content",
            "field": "subject",
            "operator": "in",
            "value": "04000000"
        },
        {
            "_id": "2222222222bbbb2222222222",
            "name": "Sports Content",
            "field": "subject",
            "operator": "in",
            "value": "15000000"
        }]
        """
        Given "content_filters"
        """
        [{
            "_id": "0987654321dcba0987654321",
            "name": "Finance Content",
            "content_filter": [
                {
                    "expression": {
                        "fc": ["1111111111aaaa1111111111"]
                    }
                }
            ]
        },
        {
            "_id": "1234567890abcd1234567890",
            "name": "Sports Content",
            "content_filter": [
                {
                    "expression": {
                        "fc": ["2222222222bbbb2222222222"]
                    }
                }
            ]
        }]
        """
        When we post to "/desks"
        """
          {
            "name": "Sports Desk", "members": [{"user": "#CONTEXT_USER_ID#"}]
          }
        """
        Then we get response code 201
        When we post to "/routing_schemes"
        """
        [
          {
            "name": "routing rule scheme 1",
            "rules": [
              {
                "name": "Sports Rule",
                "filter": "1234567890abcd1234567890",
                "actions": {
                  "fetch": [
                    {
                      "desk": "#desks._id#",
                      "stage": "#desks.incoming_stage#"
                    }],
                  "exit": false
                }
              }
            ]
          }
        ]
        """
        Then we get response code 201
        When we post to "/desks"
        """
          {
            "name": "Finance Desk", "members": [{"user": "#CONTEXT_USER_ID#"}]
          }
        """
        Then we get response code 201
        When we patch routing scheme "/routing_schemes/#routing_schemes._id#"
        """
           {
              "name": "Finance Rule",
              "filter": "0987654321dcba0987654321",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}],
                "exit": false
              }
           }
        """
        Then we get response code 200
        When we fetch from "AAP" ingest "aap-finance.xml" using routing_scheme
        """
        #routing_schemes._id#
        """
        Then the ingest item is routed based on routing scheme and rule "Finance Rule"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#AAP.AFP.121974877.6504909#"
        }
        """
        Then the ingest item is not routed based on routing scheme and rule "Sports Rule"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#AAP.AFP.121974877.6504909#"
        }
        """
        When we fetch from "AAP" ingest "aap-sports.xml" using routing_scheme
        """
        #routing_schemes._id#
        """
        Then the ingest item is routed based on routing scheme and rule "Sports Rule"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#AAP.AAP.123253116.6697929#"
        }
        """
        Then the ingest item is not routed based on routing scheme and rule "Finance Rule"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#AAP.AAP.123253116.6697929#"
        }
        """

    @auth @provider @vocabulary
    Scenario: Package is routed automatically
        Given empty "desks"
        Given "filter_conditions"
        """
        [{
            "_id": "1111111111aaaa1111111111",
            "name": "Syria in Slugline",
            "field": "slugline",
            "operator": "like",
            "value": "syria"
        }]
        """
        Given "content_filters"
        """
        [{
            "_id": "1234567890abcd1234567890",
            "name": "Syria Content",
            "content_filter": [
                {
                    "expression": {
                        "fc": ["1111111111aaaa1111111111"]
                    }
                }
            ]
        }]
        """
        When we post to "/desks"
        """
          {
            "name": "World Desk", "members": [{"user": "#CONTEXT_USER_ID#"}]
          }
        """
        Then we get response code 201
        When we post to "/routing_schemes"
        """
        [
          {
            "name": "routing rule scheme 1",
            "rules": [
              {
                "name": "Syria Rule",
                "filter": "1234567890abcd1234567890",
                "actions": {
                  "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}],
                  "exit": false
                }
              }
            ]
          }
        ]
        """
        Then we get response code 201
        When we fetch from "reuters" ingest "tag_reuters.com_2014_newsml_KBN0FL0NM" using routing_scheme
        """
        #routing_schemes._id#
        """
        Then the ingest item is routed based on routing scheme and rule "Syria Rule"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#reuters.tag_reuters.com_2014_newsml_KBN0FL0NM#"
        }
        """

    @auth @provider @vocabulary
    Scenario: Content is fetched and published to different stages 1
        Given the "validators"
        """
          [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
        """
        Given empty "desks"
        Given "filter_conditions"
        """
        [{
            "_id": "2222222222bbbb2222222222",
            "name": "Finance Subject",
            "field": "subject",
            "operator": "in",
            "value": "04000000"
        }]
        """
        Given "content_filters"
        """
        [{
            "_id": "1234567890abcd1234567890",
            "name": "Finance Content",
            "content_filter": [
                {
                    "expression": {
                        "fc": ["2222222222bbbb2222222222"]
                    }
                }
            ]
        }]
        """

        When we post to "/desks"
        """
          {
            "name": "Finance Desk", "members": [{"user": "#CONTEXT_USER_ID#"}]
          }
        """
        Then we get response code 201
        When we post to "/routing_schemes"
        """
        [
          {
            "name": "routing rule scheme 1",
            "rules": [
              {
                "name": "Finance Rule 1",
                "filter": "1234567890abcd1234567890",
                "actions": {
                  "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}],
                  "exit": false
                }
              }
            ]
          }
        ]
        """
        Then we get OK response
        When we post to "/stages"
        """
        [
          {
            "name": "Published",
            "description": "Published Content",
            "task_status": "in_progress",
            "desk": "#desks._id#"
          }
        ]
        """
        Then we get "_id"
        When we post to "/stages"
        """
        [
          {
            "name": "Un Publsihed",
            "description": "Published Content",
            "task_status": "in_progress",
            "desk": "#desks._id#"
          }
        ]
        """
        Then we get OK response
        When we fetch from "AAP" ingest "aap-finance.xml" using routing_scheme
        """
        #routing_schemes._id#
        """
        Then the ingest item is routed based on routing scheme and rule "Finance Rule 1"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#AAP.AFP.121974877.6504909#"
        }
        """
        Then the ingest item is routed based on routing scheme and rule "Finance Rule 2"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#AAP.AFP.121974877.6504909#"
        }
        """
        When we fetch from "AAP" ingest "aap-finance1.xml" using routing_scheme
        """
        #routing_schemes._id#
        """
        Then the ingest item is routed based on routing scheme and rule "Finance Rule 2"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#AAP.AAP.0.6703189#"
        }
        """
        Then the ingest item is routed based on routing scheme and rule "Finance Rule 1"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#AAP.AAP.0.6703189#"
        }
        """

    @auth @provider @vocabulary
    Scenario: Content is fetched and published to different stages 2
        Given empty "desks"
        Given "filter_conditions"
        """
        [{
            "_id": "2222222222bbbb2222222222",
            "name": "Finance Subject",
            "field": "subject",
            "operator": "in",
            "value": "04000000"
        }]
        """
        Given "content_filters"
        """
        [{
            "_id": "1234567890abcd1234567890",
            "name": "Finance Content",
            "content_filter": [
                {
                    "expression": {
                        "fc": ["2222222222bbbb2222222222"]
                    }
                }
            ]
        }]
        """

        When we post to "/desks"
        """
          {
            "name": "Finance Desk", "members": [{"user": "#CONTEXT_USER_ID#"}]
          }
        """
        Then we get response code 201
        When we post to "/routing_schemes"
        """
        [
          {
            "name": "routing rule scheme 1",
            "rules": [
              {
                "name": "Finance Rule 1",
                "filter": "1234567890abcd1234567890",
                "actions": {
                  "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}],
                  "exit": false
                }
              }
            ]
          }
        ]
        """
        Then we get response code 201
        When we post to "/stages"
        """
        [
          {
            "name": "Published",
            "description": "Published Content",
            "task_status": "in_progress",
            "desk": "#desks._id#"
          }
        ]
        """
        When we patch routing scheme "/routing_schemes/#routing_schemes._id#"
        """
           {
              "name": "Finance Rule 2",
              "filter": "1234567890abcd1234567890",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#stages._id#"}],
                "exit": false
              }
           }
        """
        Then we get response code 200
        When we schedule the routing scheme "#routing_schemes._id#"
        When we fetch from "AAP" ingest "aap-finance.xml" using routing_scheme
        """
        #routing_schemes._id#
        """
        Then the ingest item is not routed based on routing scheme and rule "Finance Rule 1"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#AAP.AFP.121974877.6504909#"
        }
        """
        Then the ingest item is routed based on routing scheme and rule "Finance Rule 2"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#AAP.AFP.121974877.6504909#"
        }
        """


    @auth @provider @vocabulary
    Scenario: Content is fetched to desk in the ingested item
        Given empty "desks"
        Given "filter_conditions"
        """
        [{
            "_id": "2222222222bbbb2222222222",
            "name": "Finance Subject",
            "field": "subject",
            "operator": "in",
            "value": "04000000"
        }]
        """
        Given "content_filters"
        """
        [{
            "_id": "1234567890abcd1234567890",
            "name": "Finance Content",
            "content_filter": [
                {
                    "expression": {
                        "fc": ["2222222222bbbb2222222222"]
                    }
                }
            ]
        }]
        """

        When we post to "/desks"
        """
          {
            "name": "Finance Desk", "members": [{"user": "#CONTEXT_USER_ID#"}]
          }
        """
        Then we get response code 201
        When we post to "/routing_schemes"
        """
        [
          {
            "name": "routing rule scheme 1",
            "rules": [
              {
                "name": "Finance Rule 1",
                "filter": "1234567890abcd1234567890",
                "actions": {
                  "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}],
                  "preserve_desk": true,
                  "exit": false
                }
              }
            ]
          }
        ]
        """
        Then we get response code 201
        When we ingest and fetch "AAP" "aap-finance.xml" to desk "#desks._id#" stage "#desks.incoming_stage#" using routing_scheme
        """
        #routing_schemes._id#
        """
        When we get "/archive?q=#desks._id#"
        Then we get list with 1 items
        """
        {"_items": [
          {
              "headline": "ASIA:Samsung sells defence, petrochemical units"
          }
        ]}
        """


    @auth @provider @clean @vocabulary
    Scenario: Content is fetched and transformed different stages
        Given empty "desks"
        Given "filter_conditions"
        """
        [{
            "_id": "3333333333cccc3333333333",
            "name": "Politics Subject",
            "field": "subject",
            "operator": "in",
            "value": "04000000"
        }]
        """
        Given "content_filters"
        """
        [{
            "_id": "1234567890abcd1234567890",
            "name": "Politics Content",
            "content_filter": [
                {
                    "expression": {
                        "fc": ["3333333333cccc3333333333"]
                    }
                }
            ]
        }]
        """

        When we post to "/desks"
        """
          {
            "name": "Politics", "members": [{"user": "#CONTEXT_USER_ID#"}]
          }
        """
        Then we get response code 201
        Given we create a new macro "behave_macro.py"
        When we post to "/routing_schemes"
        """
        [
          {
            "name": "routing rule scheme 1",
            "rules": [
              {
                "name": "Politics Rule 1",
                "filter": "1234567890abcd1234567890",
                "actions": {
                  "fetch": [{"desk": "#desks._id#", "stage": "#desks.incoming_stage#", "macro": "update_fields"}],
                  "exit": false
                }
              }
            ]
          }
        ]
        """
        Then we get response code 201
        When we post to "/stages"
        """
        [
          {
            "name": "Published",
            "description": "Published Content",
            "task_status": "in_progress",
            "desk": "#desks._id#"
          }
        ]
        """
        When we patch routing scheme "/routing_schemes/#routing_schemes._id#"
        """
           {
              "name": "Politics Rule 2",
              "filter": "1234567890abcd1234567890",
              "actions": {
                "fetch": [{"desk": "#desks._id#", "stage": "#stages._id#", "macro": "update_fields"}],
                "exit": false
              }
           }
        """
        Then we get response code 200
        When we schedule the routing scheme "#routing_schemes._id#"
        When we fetch from "AAP" ingest "aap-finance.xml" using routing_scheme
        """
        #routing_schemes._id#
        """
        Then the ingest item is not routed based on routing scheme and rule "Politics Rule 1"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#AAP.AFP.121974877.6504909#"
        }
        """
        Then the ingest item is routed and transformed based on routing scheme and rule "Politics Rule 2"
        """
        {
          "routing_scheme": "#routing_schemes._id#",
          "ingest": "#AAP.AFP.121974877.6504909#"
        }
        """
