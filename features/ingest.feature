Feature: Ingest


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
                "guid": "tag:example.com,0000:newsml_BRE9A605",
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
    	When we fetch from "reuters" ingest "tag:reuters.com,2014:newsml_KBN0FL0NM"
        And we get "/ingest"
        Then we get existing resource
		"""
		{
		    "_items": [{
		        "type": "picture",
		        "guid": "tag:reuters.com,2014:newsml_LYNXMPEA6F0MS",
		        "state":"ingested",
		        "ingest_provider_sequence" : "4"
		    }, {
		        "type": "composite",
		        "usageterms": "NO ARCHIVAL USE",
		        "state":"ingested",
		        "ingest_provider_sequence": "1",
		        "groups": [{
		            "refs": [{
		                "itemClass": "icls:text",
		                "residRef": "tag:reuters.com,2014:newsml_KBN0FL0NN"
		            }, {
		                "itemClass": "icls:picture",
		                "residRef": "tag:reuters.com,2014:newsml_LYNXMPEA6F13M"
		            }, {
		                "itemClass": "icls:picture",
		                "residRef": "tag:reuters.com,2014:newsml_LYNXMPEA6F0MS"
		            }, {
		                "itemClass": "icls:picture",
		                "residRef": "tag:reuters.com,2014:newsml_LYNXMPEA6F0MT"
		            }]
		        }, {
		            "refs": [{
		                "itemClass": "icls:text",
		                "residRef": "tag:reuters.com,2014:newsml_KBN0FL0ZP"
		            }]
		        }],
		        "guid": "tag:reuters.com,2014:newsml_KBN0FL0NM"
		    }, {
		        "type": "picture",
		        "guid": "tag:reuters.com,2014:newsml_LYNXMPEA6F0MT",
		        "state":"ingested",
		        "ingest_provider_sequence" : "3"
		    }, {
		        "type": "text",
		        "guid": "tag:reuters.com,2014:newsml_KBN0FL0ZP",
		        "state":"ingested",
		        "ingest_provider_sequence" : "2"
		    }, {
		        "type": "picture",
		        "guid": "tag:reuters.com,2014:newsml_LYNXMPEA6F13M",
		        "state":"ingested",
		        "ingest_provider_sequence" : "5"
		    }, {
		        "type": "text",
		        "guid": "tag:reuters.com,2014:newsml_KBN0FL0NN",
		        "state":"ingested",
		        "ingest_provider_sequence" : "6"
		    }]
		} 
  		"""

    @auth
    @provider
    Scenario: Check if Ingest Provider Sequence Number is per channel
    	Given empty "ingest"
    	When we fetch from "reuters" ingest "tag:reuters.com,2014:newsml_LYNXMPEA6F0MS"
        And we fetch from "AAP" ingest "aap.xml"
        And we get "/ingest/tag:reuters.com,2014:newsml_LYNXMPEA6F0MS"
        Then we get existing resource
		"""
		{
          "type": "picture",
          "guid": "tag:reuters.com,2014:newsml_LYNXMPEA6F0MS",
          "state":"ingested",
          "ingest_provider_sequence" : "1"
		}
  		"""
        When we get "/ingest/AAP.115314987.5417374"
        Then we get existing resource
		"""
		{
          "type": "text",
          "guid": "AAP.115314987.5417374",
          "state":"ingested",
          "ingest_provider_sequence" : "1747"
		}
  		"""
