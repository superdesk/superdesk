Feature: Fetch From Ingest


    @auth
    Scenario: List empty ingest
        Given empty "ingest"
        When we get "/ingest"
        Then we get list with 0 items


    @auth
    Scenario: List ingest with items for aggregates
        Given "ingest"
            """
            [{
                "guid": "tag_example.com_0000_newsml_BRE9A605",
                "urgency": "1",
                "source": "example.com",
                "versioncreated": "2013-11-11T11:11:11+00:00"
            }]
            """

        When we get "/ingest"
        Then we get list with 1 items
        And we get aggregations "type,desk,urgency,stage,category,source,state,day,week,month"


    @auth
    @provider
    Scenario: Fetch an ingest package
    	Given empty "ingest"
    	When we fetch from "reuters" ingest "tag_reuters.com_2014_newsml_KBN0FL0NM"
        And we get "/ingest"
        Then we get existing resource
		"""
		{
            "_items": [
                {
                    "guid": "tag_reuters.com_2014_newsml_LYNXMPEA6F0MS",
                    "ingest_provider_sequence": "3",
                    "state": "ingested",
                    "type": "picture"
                },
                {
                    "groups": [
                        {
                            "refs": [
                                {"itemClass": "icls:text", "guid": "tag_reuters.com_2014_newsml_KBN0FL0NN"},
                                {"itemClass": "icls:picture", "guid": "tag_reuters.com_2014_newsml_LYNXMPEA6F13M"},
                                {"itemClass": "icls:picture", "guid": "tag_reuters.com_2014_newsml_LYNXMPEA6F0MS"},
                                {"itemClass": "icls:picture", "guid": "tag_reuters.com_2014_newsml_LYNXMPEA6F0MT"}
                            ]
                        },
                        {"refs": [{"itemClass": "icls:text", "guid": "tag_reuters.com_2014_newsml_KBN0FL0ZP"}]}
                    ],
                    "guid": "tag_reuters.com_2014_newsml_KBN0FL0NM",
                    "ingest_provider_sequence": "6",
                    "state": "ingested",
                    "type": "composite",
                    "usageterms": "NO ARCHIVAL USE"
                },
                {
                    "guid": "tag_reuters.com_2014_newsml_LYNXMPEA6F0MT",
                    "ingest_provider_sequence": "2",
                    "state": "ingested",
                    "type": "picture"
                },
                {
                    "guid": "tag_reuters.com_2014_newsml_KBN0FL0ZP",
                    "ingest_provider_sequence": "1",
                    "state": "ingested",
                    "type": "text"
                },
                {
                    "guid": "tag_reuters.com_2014_newsml_LYNXMPEA6F13M",
                    "ingest_provider_sequence": "4",
                    "state": "ingested",
                    "type": "picture"
                },
                {
                    "guid": "tag_reuters.com_2014_newsml_KBN0FL0NN",
                    "ingest_provider_sequence": "5",
                    "state": "ingested",
                    "type": "text"
                }
            ]
        }
  		"""

    @auth
    @provider
    Scenario: Check if Ingest Provider Sequence Number is per channel
    	Given empty "ingest"
    	When we fetch from "reuters" ingest "tag_reuters.com_2014_newsml_LYNXMPEA6F0MS"
        And we fetch from "AAP" ingest "aap.xml"
        And we get "/ingest/#reuters.tag_reuters.com_2014_newsml_LYNXMPEA6F0MS#"
        Then we get existing resource
		"""
		{
          "type": "picture",
          "guid": "tag_reuters.com_2014_newsml_LYNXMPEA6F0MS",
          "state":"ingested",
          "ingest_provider_sequence" : "1"
		}
  		"""
        When we get "/ingest/#AAP.AAP.115314987.5417374#"
        Then we get existing resource
		"""
		{
          "type": "text",
          "guid": "AAP.115314987.5417374",
          "state":"ingested",
          "ingest_provider_sequence" : "1747"
		}
  		"""

    @auth
    @provider
    Scenario: Test iptc code expansion
        Given empty "ingest"
        When we fetch from "teletype" ingest "Standings__2014_14_635535729050675896.tst"
        And we get "/ingest"
        Then we get existing resource
		"""
		{
                    "_items": [
                        {
                            "type": "text",
                            "subject": [
                                {
                                    "name": "Formula One",
                                    "qcode": "15039001"
                                },
                                {
                                    "name": "sport",
                                    "qcode": "15000000"
                                },
                                {
                                    "name": "motor racing",
                                    "qcode": "15039000"
                                }
                            ]
                        }
                    ]
                }
  		"""

    @auth
    @provider
    Scenario: Deleting an Ingest Provider after receiving items should be prohibited
    	Given empty "ingest"
    	When we fetch from "AAP" ingest "aap.xml"
        And we get "/ingest/#AAP.AAP.115314987.5417374#"
        Then we get "ingest_provider"
        When we delete "/ingest_providers/#ingest_provider#"
        Then we get error 403
        """
        {"_message": "Deleting an Ingest Source after receiving items is prohibited."}
        """

    @auth
    Scenario: Ingested item must have unique id and unique name
        Given "ingest"
            """
            [{
                "guid": "tag_example.com_0000_newsml_BRE9A605",
                "urgency": "1",
                "source": "example.com",
                "versioncreated": "2013-11-11T11:11:11+00:00"
            }]
            """
        Then we get "unique_id" in "/ingest/tag_example.com_0000_newsml_BRE9A605"
        And we get "unique_name" in "/ingest/tag_example.com_0000_newsml_BRE9A605"

    @auth
    @provider
    Scenario: Check if Ingest from AAP populates all subjects with qcode
    	Given empty "ingest"
        When we fetch from "AAP" ingest "aap.xml"
        And we get "/ingest"
        Then we get existing resource
		"""
		{
		"_items": [
		  {
		    "type": "text",
		    "subject" : [
              {
                  "name" : "Justice",
                  "qcode" : "02000000"
              },
              {
                  "name" : "Police",
                  "qcode" : "02003000"
              }
              ]
		  }
		  ]
		}
  		"""

    @auth
    @provider
    Scenario: Check if Ingest of IPTC sample NITF populates all subjects with qcode
    	Given empty "ingest"
        When we fetch from "AAP" ingest "nitf-fishing.xml"
        And we get "/ingest"
        Then we get existing resource
		"""
		{
		"_items": [
		  {
		    "type": "text",
		    "subject" : [
              {
                  "name" : "Weather",
                  "qcode" : "17000000"
              },
              {
                  "name" : "Statistics",
                  "qcode" : "17004000"
              },
              {
                  "name" : "Fishing Industry",
                  "qcode" : "04001002"
              }
              ]
		  }
		  ]
		}
  		"""

    @auth
    @provider
    Scenario: Check if Ingest of IPTC sample NITF populates anpa category based on mapping
        Given empty "ingest"
        Given the "vocabularies"
        """
          [{
              "_id": "iptc_category_map",
              "items": [
                {"name" : "Finance", "category" : "f", "subject" : "04000000", "is_active" : true},
                {"name" : "Weather", "category" : "b", "subject" : "17000000", "is_active" : true}
              ]
           },
           {
              "_id": "categories",
              "items": [
                {"is_active": true, "name": "Australian Weather", "qcode": "b", "subject": "17000000"},
                {"is_active": true, "name": "Finance", "qcode": "f", "subject": "04000000"}
              ]
           }
          ]
        """
        When we fetch from "AAP" ingest "nitf-fishing.xml"
        And we get "/ingest"
        Then we get existing resource
		"""
		{
		"_items": [
		  {
		    "type": "text",
		    "anpa_category" : [
              {
                  "name" : "Australian Weather",
                  "qcode" : "b"
              },
              {
                  "name" : "Finance",
                  "qcode" : "f"
              }
              ]
		  }
		  ]
		}
  		"""

    @auth
    @provider
    Scenario: Check given an item with an anpa category the iptc subject is derived
    	Given empty "ingest"
        Given the "vocabularies"
        """
          [
           {
              "_id": "categories",
              "items": [
                {"is_active": true, "name": "Overseas Sport", "qcode": "s", "subject": "15000000"}
              ]
           }
          ]
        """
        When we fetch from "DPA" ingest "IPTC7901_odd_charset.txt"
        And we get "/ingest"
        Then we get existing resource
		"""
		{
		"_items": [
		  {
		    "subject" : [
              {
                  "name" : "sport",
                  "qcode" : "15000000"
              }
              ]
		  }
		  ]
		}
  		"""
