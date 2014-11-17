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
        And we get aggregations "type,desk,urgency,stage,category,source,spiked,day,week,month"


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
		        "guid": "tag:reuters.com,2014:newsml_LYNXMPEA6F0MS"
		    }, {
		        "type": "composite",
		        "usageterms": "NO ARCHIVAL USE",
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
		        "guid": "tag:reuters.com,2014:newsml_LYNXMPEA6F0MT"
		    }, {
		        "type": "text",
		        "guid": "tag:reuters.com,2014:newsml_KBN0FL0ZP"
		    }, {
		        "type": "picture",
		        "guid": "tag:reuters.com,2014:newsml_LYNXMPEA6F13M"
		    }, {
		        "type": "text",
		        "guid": "tag:reuters.com,2014:newsml_KBN0FL0NN"
		    }]
		} 
  		"""