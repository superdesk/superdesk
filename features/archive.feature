Feature: News Items Archive

    @auth
    Scenario: List empty archive
        Given empty "archive"
        When we get "/archive"
        Then we get list with 0 items


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
        And we get archive ingest result
        """
        {"state": "PROGRESS",  "current": 2, "total": 2}
        """     

    @auth
    Scenario: Get archive item by guid
        Given "archive"
        """
        [{"guid": "tag:example.com,0000:newsml_BRE9A605"}]
        """

        When we get "/archive/tag:example.com,0000:newsml_BRE9A605"
        Then we get existing resource
        """
        {"guid": "tag:example.com,0000:newsml_BRE9A605"}
        """

    @auth
    Scenario: Update item
        Given "archive"
        """
        [{"_id": "xyz", "guid": "testid", "headline": "test"}]
        """

        When we patch given
        """
        {"headline": "TEST 2", "urgency": 2}
        """

        And we patch latest
        """
        {"headline": "TEST 3"}
        """

        Then we get updated response
        And we get version 3
        And we get etag matching "/archive/xyz"

        When we get "/archive/xyz?version=all"
        Then we get list with 3 items


	@auth
	Scenario: Restore version
        Given "archive"
        """
        [{"guid": "testid", "headline": "test"}]
        """
        When we patch given
        """
        {"headline": "TEST 2", "urgency": 2}
        """
		And we restore version 1

        Then we get version 3
        And the field "headline" value is "test"


    @wip
    @auth
    Scenario: Upload image into archive
        Given empty "archive"
        When we upload a file "bike.jpg" to "archive_media"
        Then we get new resource
        """
        {"guid": "", "firstcreated": "", "versioncreated": ""}
        """
        And we get "bike.jpg" metadata
        And we get "picture" renditions

        When we patch latest
        """
        {"headline": "flower", "byline": "foo", "description_text": "flower desc"}
        """

        When we get "/archive"
        Then we get list with 1 items
        """
        {"headline": "flower", "byline": "foo", "description_text": "flower desc"}
        """

    @auth
    Scenario: Upload audio file into archive
        Given empty "archive"
        When we upload a file "green.ogg" to "archive_media"
        Then we get new resource
        """
        {"guid": ""}
        """
        And we get "green.ogg" metadata
        Then original rendition is updated with link to file having mimetype "audio/ogg"
        When we patch latest
        """
        {"headline": "green", "byline": "foo", "description_text": "green music"}
        """
        When we get "/archive"
        Then we get list with 1 items
        """
        {"headline": "green", "byline": "foo", "description_text": "green music"}
        """

    @auth
    Scenario: Upload video file into archive
        Given empty "archive"
        When we upload a file "this_week_nasa.mp4" to "archive_media"
        Then we get new resource
        """
        {"guid": ""}
        """
        And we get "this_week_nasa.mp4" metadata
        Then original rendition is updated with link to file having mimetype "video/mp4"
        When we patch latest
        """
        {"headline": "week @ nasa", "byline": "foo", "description_text": "nasa video"}
        """
        When we get "/archive"
        Then we get list with 1 items
        """
        {"headline": "week @ nasa", "byline": "foo", "description_text": "nasa video"}
        """

    @auth
    Scenario: Cancel audio upload
        Given empty "archive"
        When we upload a file "green.ogg" to "archive_media"
        And we delete latest
        Then we get deleted response

    @auth
    Scenario: Cancel upload
        Given empty "archive"
        When we upload a file "bike.jpg" to "archive_media"
        And we delete latest
        Then we get deleted response

    @auth
    Scenario: Browse content
        Given the "archive"
        """
        [{"type":"text", "headline": "test1", "guid": "testid1", "creator": "abc"}, {"type":"text", "headline": "test2", "guid": "testid2", "creator": "abc"}]
        """
        When we get "/archive"
        Then we get list with 2 items

    @auth
    @ticket-sd-360
    Scenario: Delete archive item with guid starting with "-"
        Given empty "archive"
        When we post to "/archive"
        """
        [{"guid": "-abcde1234567890", "type": "text"}]
        """
        And we delete latest
        Then we get deleted response

    @auth
    Scenario: Create new text item
        Given empty "archive"
        When we post to "/archive"
        """
        [{"type": "text"}]
        """
        Then we get new resource
        """
        {"_id": "", "guid": "", "type": "text"}
        """
