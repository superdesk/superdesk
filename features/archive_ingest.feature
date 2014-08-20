Feature: Archive Ingest

@auth
    Scenario: Move item into archive - tag not on ingest
        Given empty "archive"
		And empty "ingest"

        When we post to "/archive_ingest"
        """
        {
        "guid": "not_on_ingest_tag"
        }
        """

        Then we get error 400
		"""
		{"_message": "", "_issues": "Fail to found ingest item with guid: not_on_ingest_tag", "_status": "ERR"}
		"""


    @auth
    Scenario: Move item into archive - no provider
        Given empty "archive"
        And "ingest"
        """
        [{"guid": "tag:reuters.com,0000:newsml_GM1EA6A1P8401"}]
        """

        When we post to "/archive_ingest"
        """
        {
        "guid": "tag:reuters.com,0000:newsml_GM1EA6A1P8401"
        }
        """

        Then we get archive ingest result
        """
        {"state": "FAILURE",  "error": "For ingest with guid= tag:reuters.com,0000:newsml_GM1EA6A1P8401, failed to retrieve provider with _id=None"}
        """

        		
    @auth
    @provider
    Scenario: Move item into archive - success
        Given empty "archive"
        And ingest from "reuters"
        """
        [{"guid": "tag:reuters.com,0000:newsml_GM1EA7M13RP01"}]
        """

        When we post to "/archive_ingest"
        """
        {
        "guid": "tag:reuters.com,0000:newsml_GM1EA7M13RP01"
        }
        """
        And we get "/archive/tag:reuters.com,0000:newsml_GM1EA7M13RP01"

        Then we get existing resource
		"""
		{"renditions": {
	        "viewImage": {
	            "sizeinbytes": 190880,
	            "rendition": "viewImage",
	            "residRef": "tag:reuters.com,0000:binary_GM1EA7M13RP01-VIEWIMAGE"
	        },
	        "thumbnail": {
	            "sizeinbytes": 16418,
	            "rendition": "thumbnail",
	            "residRef": "tag:reuters.com,0000:binary_GM1EA7M13RP01-THUMBNAIL"
	        },
	        "baseImage": {
	            "sizeinbytes": 726349,
	            "rendition": "baseImage",
	            "residRef": "tag:reuters.com,0000:binary_GM1EA7M13RP01-BASEIMAGE"
	        }},
		 "task_id": ""}  
  		"""
        And we get archive ingest result
        """
        {"state": "PROGRESS",  "current": 4, "total": 4}
        """

            
    @auth
    @provider
    Scenario: Move package into archive - check progress status
        Given empty "archive"
        And ingest from "reuters"
        """
        [{"guid": "tag:reuters.com,2014:newsml_KBN0FL0NM"}]
        """

        When we post to "/archive_ingest"
        """
        {
        "guid": "tag:reuters.com,2014:newsml_KBN0FL0NM"
        }
        """
        And we get "/archive/tag:reuters.com,2014:newsml_KBN0FL0NM"

        Then we get existing resource
		"""
		{"task_id": ""}  
  		"""
        And we get archive ingest result
        """
        {"state": "PROGRESS",  "current": 18, "total": 18}
        """



    @auth
    @provider
    Scenario: Move package into archive - check items
        Given empty "archive"
        And ingest from "reuters"
        """
        [{"guid": "tag:reuters.com,2014:newsml_KBN0FL0NM"}]
        """

        When we post to "/archive_ingest"
        """
        {
        "guid": "tag:reuters.com,2014:newsml_KBN0FL0NM"
        }
        """
		And we get "/archive"
        Then we get existing resource
		"""
		{
		    "_items": [{
		        "type": "picture",
		        "guid": "tag:reuters.com,2014:newsml_LYNXMPEA6F0MS"
		    }, {
		        "type": "composite",
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
        
        
    @auth
    @provider
    Scenario: Move audio item into archive - success
        Given empty "archive"
        And ingest from "reuters"
        """
        [{
          "renditions": {
            "stream": {
                "mimetype": "audio/mpeg",
                "residRef": "tag:reuters.com,0000:binary_LOVEA6M0L7U2E-STREAM:22.050:MP3",
                "href": "http://content.reuters.com/auth-server/content/tag:reuters.com,2014:newsml_OV0TUFYV5:2/tag:reuters.com,0000:binary_LOVEA6M0L7U2E-STREAM:22.050:MP3?auth_token=token",
                "rendition": "stream",
                "sizeinbytes": 602548
            }
          },
          "guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E"
        }]
        """

        When we post to "/archive_ingest"
        """
        {
        "guid": "tag:reuters.com,2014:newsml_LOVEA6M0L7U2E"
        }
        """
        
        And we get "/archive/tag:reuters.com,2014:newsml_LOVEA6M0L7U2E"
      
        Then we get existing resource
		"""
		{"renditions": {
            "stream": {
                "mimetype": "audio/mpeg",
                "residRef": "tag:reuters.com,0000:binary_LOVEA6M0L7U2E-STREAM:22.050:MP3",
                "rendition": "stream",
                "sizeinbytes": 602548
            }
        },
		 "task_id": ""}  
  		"""
  		And we get rendition "stream" with mimetype "audio/mpeg"
  		
        And we get archive ingest result
        """
        {"state": "PROGRESS",  "current": 2, "total": 2}
        """     
