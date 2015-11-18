Feature: Publish content to the public API

  @auth
  @notification
  Scenario: Publish a text item
    Given "desks"
        """
        [{"name": "test_desk1"}]
        """
    And "archive"
        """
        [
            {
                "_current_version": 1,
                "body_html": "item content",
                "slugline": "some slugline",
                "headline": "some headline",
                "language": "en",
                "byline": "John Doe",
                "urgency": 1,
                "pubstatus": "usable",
                "state": "submitted",
                "task": {
                "user": "#CONTEXT_USER_ID#",
                "status": "todo",
                "stage": "#desks.incoming_stage#",
                "desk": "#desks._id#"
                },
                "anpa_category": [
                {
                    "qcode": "a"
                }
                ],
                "subject": [
                {
                    "qcode": "07005000",
                    "parent": "07000000",
                    "name": "medical research"
                }
                ],
                "versioncreated": "2015-06-01T22:19:08+0000",
                "original_creator": "#CONTEXT_USER_ID#",
                "type": "text",
                "version": "1",
                "unique_name": "#9028",
                "guid": "item1"
            }
        ]
        """
    And the "validators"
        """
        [{"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
        """
    When we post to "/subscribers" with success
        """
        {
        "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
        }
        """
    And we publish "item1" with "publish" type and "published" state
    Then we get OK response
    And we get notifications
        """
        [{"event": "item:publish", "extra": {"item": "item1"}}]
        """
    And we get existing resource
        """
        {"_current_version": 2, "state": "published", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
        """
    When we get "/publish_queue"
    Then we get existing resource
        """
        {"_items": [{"state": "pending"}]}
        """
    When we get "/published"
    Then we get existing resource
        """
        {"_items" : [{"guid": "item1", "_current_version": 2, "state": "published"}]}
        """

  @auth
  @notification
  Scenario: Publish a picture item to the API
    Given "desks"
        """
        [{"name": "test_desk1"}]
        """
    And "archive"
        """
        [
           {
                "task": {
                    "user": "#CONTEXT_USER_ID#",
                    "status": "todo",
                    "stage": "#desks.incoming_stage#",
                    "desk": "#desks._id#"
                },
                "_current_version" : 1,
                "slugline" : "AMAZING PICTURE",
                "original_source" : "AAP",
                "renditions" : {
                    "viewImage" : {
                        "width" : 640,
                        "href" : "http://localhost:5000/api/upload/55b032041d41c8d278d21b6f/raw?_schema=http",
                        "mimetype" : "image/jpeg",
                        "height" : 401
                    },
                    "original_source" : {
                        "href" : "https://one-api.aap.com.au/api/v3/Assets/20150723001158606583/Original/download",
                        "mimetype" : "image/jpeg"
                    },
                    "thumbnail" : {
                        "width" : 191,
                        "href" : "http://localhost:5000/api/upload/55b032051d41c8d278d21b73/raw?_schema=http",
                        "mimetype" : "image/jpeg",
                        "height" : 120
                    },
                    "baseImage" : {
                        "width" : 1400,
                        "href" : "http://localhost:5000/api/upload/55b032051d41c8d278d21b71/raw?_schema=http",
                        "mimetype" : "image/jpeg",
                        "height" : 878
                    },
                    "original" : {
                        "width" : 2828,
                        "href" : "http://localhost:5000/api/upload/55b032041d41c8d278d21b6b/raw?_schema=http",
                        "mimetype" : "image/jpeg",
                        "height" : 1775
                    }
                },
                "byline" : "MICKEY MOUSE",
                "original_creator" : "#CONTEXT_USER_ID#",
                "family_id" : "20150723001158606583",
                "version_creator" : "#CONTEXT_USER_ID#",
                "operation" : "create",
                "headline" : "AMAZING PICTURE",
                "ingest_id" : "20150723001158606583",
                "unique_id" : 85,
                "marked_for_not_publication" : false,
                "unique_name" : "#85",
                "versioncreated" : "2015-07-23T00:15:00.000Z",
                "mimetype" : "image/jpeg",
                "language" : "en",
                "state" : "submitted",
                "ednote" : "TEST ONLY",
                "sign_off" : "mar",
                "type" : "picture",
                "pubstatus" : "usable",
                "source" : "AAP",
                "description" : "The most amazing picture you will ever see",
                "guid" : "20150723001158606583",
                "expiry" : "2015-09-02T16:15:01.000Z",
                "more_coming" : false,
                "_etag" : "05b475af5ed0d752c618636da89baf0eaf245cb1",
                "lock_time" : null,
                "lock_user" : null,
                "lock_session" : null,
                "force_unlock" : true
            }
        ]
        """
    And the "validators"
        """
        [{"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}}]
        """
    When we post to "/subscribers" with success
        """
        {
        "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
        "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
        }
        """
    And we publish "20150723001158606583" with "publish" type and "published" state
    Then we get OK response
    And we get notifications
        """
        [{"event": "item:publish", "extra": {"item": "20150723001158606583"}}]
        """
    And we get existing resource
        """
        {"_current_version": 2, "state": "published", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
        """
    When we get "/publish_queue"
    Then we get existing resource
        """
        {"_items": [{"state": "pending"}]}
        """
    When we get "/published"
    Then we get existing resource
        """
        {"_items" : [{"guid": "20150723001158606583", "_current_version": 2, "state": "published"}]}
        """


  @auth
  @notification
  Scenario: Publish a composite item with a story and a picture to the API
    Given empty "archive"
    Given "desks"
        """
        [{"name": "test_desk1"}]
        """
    And the "validators"
        """
        [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
        {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
        {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}}]
        """
    When we post to "archive" with success
        """
        [{
            "headline" : "WA:Navy steps in with WA asylum-seeker boat",
            "guid" : "tag:localhost:2015:515b895a-b336-48b2-a506-5ffaf561b916",
            "state" : "submitted",
            "type" : "text",
            "body_html": "item content",
            "task": {
                "user": "#CONTEXT_USER_ID#",
                "status": "todo",
                "stage": "#desks.incoming_stage#",
                "desk": "#desks._id#"
            }
        }]
        """
    When we post to "archive" with success
      """
      [{
            "original_source" : "AAP Image/AAP",
            "description" : "A test picture",
            "state" : "submitted",
            "headline" : "ABC SHOP CLOSURES",
            "byline" : "PAUL MILLER",
            "source" : "AAP Image",
            "mimetype" : "image/jpeg",
            "type" : "picture",
            "pubstatus" : "usable",
            "task": {
                "user": "#CONTEXT_USER_ID#",
                "status": "todo",
                "stage": "#desks.incoming_stage#",
                "desk": "#desks._id#"
            },
            "guid" : "urn:newsml:localhost:2015-07-24T15:04:29.589984:af3bef9a-5002-492b-a15a-8b460e69b164",
            "renditions" : {
                "original_source" : {
                    "href" : "https://one-api.aap.com.au/api/v3/Assets/20150723001158639795/Original/download",
                    "mimetype" : "image/jpeg"
                },
                "original" : {
                    "height" : 4176,
                    "media" : "55b078b21d41c8e974d17ec5",
                    "href" : "http://localhost:5000/api/upload/55b078b21d41c8e974d17ec5/raw?_schema=http",
                    "mimetype" : "image/jpeg",
                    "width" : 2784
                },
                "thumbnail" : {
                    "height" : 120,
                    "media" : "55b078b41d41c8e974d17ed3",
                    "href" : "http://localhost:5000/api/upload/55b078b41d41c8e974d17ed3/raw?_schema=http",
                    "mimetype" : "image/jpeg",
                    "width" : 80
                },
                "viewImage" : {
                    "height" : 640,
                    "media" : "55b078b31d41c8e974d17ed1",
                    "href" : "http://localhost:5000/api/upload/55b078b31d41c8e974d17ed1/raw?_schema=http",
                    "mimetype" : "image/jpeg",
                    "width" : 426
                },
                "baseImage" : {
                    "height" : 1400,
                    "media" : "55b078b31d41c8e974d17ecf",
                    "href" : "http://localhost:5000/api/upload/55b078b31d41c8e974d17ecf/raw?_schema=http",
                    "mimetype" : "image/jpeg",
                    "width" : 933
                }
            },
            "slugline" : "ABC SHOP CLOSURES"
      }]
      """
    When we post to "archive" with success
        """
        [{
            "groups": [
            {
                "id": "root",
                "refs": [
                    {
                        "idRef": "main"
                    },
                    {
                        "idRef": "sidebars"
                    }
                ],
                "role": "grpRole:NEP"
            },
            {
                "id": "main",
                "refs": [
                    {
                        "renditions": {},
                        "slugline": "Boat",
                        "guid": "tag:localhost:2015:515b895a-b336-48b2-a506-5ffaf561b916",
                        "headline": "WA:Navy steps in with WA asylum-seeker boat",
                        "location": "archive",
                        "type": "text",
                        "itemClass": "icls:text",
                        "residRef": "tag:localhost:2015:515b895a-b336-48b2-a506-5ffaf561b916"
                    }
                ],
                "role": "grpRole:main"
            },
            {
                "id": "sidebars",
                "refs": [
                    {
                        "renditions": {
                            "original_source": {
                                "href": "https://one-api.aap.com.au/api/v3/Assets/20150723001158639795/Original/download",
                                "mimetype": "image/jpeg"
                            },
                            "original": {
                                "width": 2784,
                                "height": 4176,
                                "href": "http://localhost:5000/api/upload/55b078b21d41c8e974d17ec5/raw?_schema=http",
                                "mimetype": "image/jpeg",
                                "media": "55b078b21d41c8e974d17ec5"
                            },
                            "thumbnail": {
                                "width": 80,
                                "height": 120,
                                "href": "http://localhost:5000/api/upload/55b078b41d41c8e974d17ed3/raw?_schema=http",
                                "mimetype": "image/jpeg",
                                "media": "55b078b41d41c8e974d17ed3"
                            },
                            "viewImage": {
                                "width": 426,
                                "height": 640,
                                "href": "http://localhost:5000/api/upload/55b078b31d41c8e974d17ed1/raw?_schema=http",
                                "mimetype": "image/jpeg",
                                "media": "55b078b31d41c8e974d17ed1"
                            },
                            "baseImage": {
                                "width": 933,
                                "height": 1400,
                                "href": "http://localhost:5000/api/upload/55b078b31d41c8e974d17ecf/raw?_schema=http",
                                "mimetype": "image/jpeg",
                                "media": "55b078b31d41c8e974d17ecf"
                            }
                        },
                        "slugline": "ABC SHOP CLOSURES",
                        "type": "picture",
                        "guid": "urn:newsml:localhost:2015-07-24T15:04:29.589984:af3bef9a-5002-492b-a15a-8b460e69b164",
                        "headline": "ABC SHOP CLOSURES",
                        "location": "archive",
                        "itemClass": "icls:picture",
                        "residRef": "urn:newsml:localhost:2015-07-24T15:04:29.589984:af3bef9a-5002-492b-a15a-8b460e69b164"
                    }
                ],
                "role": "grpRole:sidebars"
            }
        ],
            "task": {
                "user": "#CONTEXT_USER_ID#",
                "status": "todo",
                "stage": "#desks.incoming_stage#",
                "desk": "#desks._id#"
            },
            "guid" : "compositeitem",
            "headline" : "WA:Navy steps in with WA asylum-seeker boat",
            "state" : "submitted",
            "type" : "composite"
        }]
        """
    When we post to "/subscribers" with success
        """
        {
        "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
        "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
        }
        """
    And we publish "compositeitem" with "publish" type and "published" state
    Then we get OK response
    And we get notifications
        """
        [{"event": "item:publish", "extra": {"item": "compositeitem"}}]
        """
    And we get existing resource
        """
        {"_current_version": 2, "state": "published", "task":{"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}
        """
    When we get "/publish_queue"
    Then we get existing resource
        """
        {"_items": [{"state": "pending"}]}
        """
    When we get "/published/compositeitem"
    Then we get existing resource
        """
        {"guid": "compositeitem", "_current_version": 2, "state": "published"}
        """
