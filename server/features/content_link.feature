Feature: Link content in takes

    @auth
    Scenario: Send Content and continue from personal space
        Given "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "archive"
        """
        [{
            "guid": "123",
            "type": "text",
            "headline": "test1",
            "slugline": "comics",
            "anpa_take_key": "Take",
            "guid": "123",
            "state": "draft",
            "task": {
                "user": "#CONTEXT_USER_ID#"
            }
        }]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
        Then we get OK response
        When we post to "archive/123/link"
        """
        [{}]
        """
        Then we get next take
        """
        {
            "type": "text",
            "headline": "test1=2",
            "slugline": "comics",
            "anpa_take_key": "Take=2",
            "state": "draft",
            "original_creator": "#CONTEXT_USER_ID#",
            "takes": {
                "_id": "#TAKE_PACKAGE#",
                "package_type": "takes",
                "type": "composite"
            },
            "linked_in_packages": [{"package_type" : "takes","package" : "#TAKE_PACKAGE#"}]
        }
        """
        When we get "archive"
        Then we get list with 3 items
        """
        {
            "_items": [
                {
                    "groups": [
                        {"id": "root", "refs": [{"idRef": "main"}]},
                        {
                            "id": "main",
                            "refs": [
                                {
                                    "headline": "test1",
                                    "slugline": "comics",
                                    "residRef": "123",
                                    "sequence": 1
                                },
                                {
                                    "headline": "test1=2",
                                    "slugline": "comics",
                                    "sequence": 2
                                }
                            ]
                        }
                    ],
                    "type": "composite",
                    "package_type": "takes",
                    "task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"},
                    "sequence": 2,
                    "last_take": ""
                },
                {
                    "headline": "test1=2",
                    "type": "text",
                    "linked_in_packages": [{"package_type": "takes"}],
                    "takes": {}
                },
                {
                    "guid": "123",
                    "headline": "test1",
                    "type": "text",
                    "linked_in_packages": [{"package_type": "takes"}],
                    "takes": {}
                }
            ]
        }
        """
        When we post to "archive/#TAKE#/link"
        """
        [{}]
        """
        Then we get next take
        """
        {
            "type": "text",
            "headline": "test1=3",
            "slugline": "comics",
            "anpa_take_key": "Take=3",
            "state": "draft",
            "original_creator": "#CONTEXT_USER_ID#",
            "takes": {
                "_id": "#TAKE_PACKAGE#",
                "package_type": "takes",
                "type": "composite"
            },
            "linked_in_packages": [{"package_type" : "takes","package" : "#TAKE_PACKAGE#"}]
        }
        """
        When we get "archive"
        Then we get list with 4 items
        """
        {
            "_items": [
                {
                    "groups": [
                        {"id": "root", "refs": [{"idRef": "main"}]},
                        {
                            "id": "main",
                            "refs": [
                                {
                                    "headline": "test1",
                                    "slugline": "comics",
                                    "residRef": "123",
                                    "sequence": 1
                                },
                                {
                                    "headline": "test1=2",
                                    "slugline": "comics",
                                    "sequence": 2
                                }
                            ]
                        }
                    ],
                    "type": "composite",
                    "package_type": "takes"
                },
                {
                    "headline": "test1=2",
                    "type": "text",
                    "linked_in_packages": [{"package_type": "takes"}],
                    "takes": {}
                },
                {
                    "guid": "123",
                    "headline": "test1",
                    "type": "text",
                    "linked_in_packages": [{"package_type": "takes"}],
                    "takes": {}
                },
                {
                    "guid": "#TAKE#",
                    "headline": "test1=3",
                    "type": "text",
                    "linked_in_packages": [{"package_type": "takes"}],
                    "takes": {}
                }
            ]
        }
        """


    @auth
    Scenario: Metadata is copied from published takes
        Given the "validators"
        """
        [{"_id": "publish", "schema":{}}]
        """
    	Given empty "ingest"
    	And "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "/subscribers" with success
        """
        [{"destinations" : [{"delivery_type" : "email", "name" : "Self_EMail", "config" : {"recipients" : "test@test.org"}}],
          "name" : "Email Subscriber", "is_active" : true
        }]
        """
        And we post to "/output_channels" with "channel1" and success
        """
        [{"name":"Channel 1", "is_digital": true, "description": "new stuff", "format": "nitf", "destinations": ["#subscribers._id#"]}]
        """
        And we post to "/output_channels" with "channel2" and success
        """
        [{"name":"Channel 2", "description": "new stuff", "format": "nitf", "destinations": ["#subscribers._id#"], "is_active": false}]
        """
        And we post to "/destination_groups" with "destgroup1" and success
        """
        [{
          "name":"Group 1", "description": "new stuff",
          "destination_groups": [],
          "output_channels": [{"channel":"#channel1#", "selector_codes": ["PXX", "XYZ"]}, {"channel":"#channel2#", "selector_codes": []}]
        }]
        """
    	When we post to "archive" with success
        """
        [{
            "guid": "123",
            "type": "text",
            "headline": "Take-1 headline",
            "abstract": "Take-1 abstract",
            "task": {
                "user": "#CONTEXT_USER_ID#"
            },
            "body_html": "Take-1",
            "state": "draft",
            "slugline": "Take-1 slugline",
            "urgency": "4",
            "pubstatus": "usable",
            "destination_groups":["#destgroup1#"],
            "subject":[{"qcode": "17004000", "name": "Statistics"}],
            "anpa-category": {"qcode": "A", "name": "Sport"},
            "anpa_take_key": "Take"
        }]
        """
        And we post to "/archive/123/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
        Then we get OK response
        When we post to "archive/123/link"
        """
        [{}]
        """
        Then we get next take
        """
        {
            "type": "text",
            "headline": "Take-1 headline=2",
            "slugline": "Take-1 slugline",
            "anpa_take_key": "Take=2",
            "state": "draft",
            "original_creator": "#CONTEXT_USER_ID#",
            "takes": {
                "_id": "#TAKE_PACKAGE#",
                "package_type": "takes",
                "type": "composite"
            },
            "linked_in_packages": [{"package_type" : "takes","package" : "#TAKE_PACKAGE#"}]
        }
        """
        When we patch "/archive/#TAKE#"
        """
        {"body_html": "Take-2", "abstract": "Take-1 abstract changed"}
        """
        And we post to "/archive/#TAKE#/move"
        """
        [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
        """
		And we get "/archive"
        Then we get list with 3 items
        When we publish "123" with "publish" type and "published" state
        Then we get OK response
        When we post to "archive/#TAKE#/link"
        """
        [{}]
        """
        Then we get next take
        """
        {
            "type": "text",
            "headline": "Take-1 headline=3",
            "slugline": "Take-1 slugline",
            "anpa_take_key": "Take=3",
            "state": "draft",
            "original_creator": "#CONTEXT_USER_ID#",
            "takes": {
                "_id": "#TAKE_PACKAGE#",
                "package_type": "takes",
                "type": "composite"
            },
            "linked_in_packages": [{"package_type" : "takes","package" : "#TAKE_PACKAGE#"}]
        }
        """
