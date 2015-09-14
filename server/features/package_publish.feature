Feature: Package Publishing

    @auth
    @provider
    Scenario: Publish a package
        Given empty "archive"
        Given the "validators"
        """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
        """
    	And empty "ingest"
    	And "desks"
        """
        [{"name": "Sports"}]
        """
        When we post to "/subscribers" with success
        """
        {
        "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
        "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
        }
        """
    	When we fetch from "reuters" ingest "tag_reuters.com_2014_newsml_KBN0FL0NM"
        And we post to "/ingest/#reuters.tag_reuters.com_2014_newsml_KBN0FL0NM#/fetch"
        """
        {
        "desk": "#desks._id#"
        }
        """
        And we get "/archive"
        Then we get list with 6 items
        When we publish "#fetch._id#" with "publish" type and "published" state
        Then we get OK response
        When we get "/published"
        Then we get existing resource
		"""
		{
            "_items": [
                {
                    "_current_version": 2,
                    "state": "published"
                },
                {
                    "_current_version": 2,
                    "groups": [
                        {
                            "refs": [
                                {"itemClass": "icls:text"},
                                {"itemClass": "icls:picture"},
                                {"itemClass": "icls:picture"},
                                {"itemClass": "icls:picture"}
                            ]
                        },
                        {"refs": [{"itemClass": "icls:text"}]}
                    ],
                    "state": "published",
                    "type": "composite"
                },
                {
                    "_current_version": 2,
                    "state": "published"
                },
                {
                    "_current_version": 2,
                    "state": "published"
                },
                {
                    "_current_version": 2,
                    "state": "published"
                },
                {
                    "_current_version": 2,
                    "state": "published"
                }
            ]
        }
		"""

    @auth
    @notification
    Scenario: Publish a composite item with a locked story
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
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
      When we post to "/archive/tag:localhost:2015:515b895a-b336-48b2-a506-5ffaf561b916/lock"
      """
      {}
      """
      When we switch user
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
      When we patch "/desks/#desks._id#"
      """
        {"members":[{"user":"#USERS_ID#"},{"user":"#CONTEXT_USER_ID#"}]}
      """
      When we post to "/archive/compositeitem/lock"
      """
      {}
      """
      When we post to "/subscribers" with success
          """
          {
          "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
          "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }
          """
      And we publish "compositeitem" with "publish" type and "published" state
      Then we get error 400
      """
      {"_issues": {"validator exception": "['WA:Navy steps in with WA asylum-seeker boat: packaged item cannot be locked']"}, "_status": "ERR"}
      """

    @auth
    @notification
    Scenario: Publish a composite item with a story that does not validate
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{"abstract": {"type": "string","required": true,"maxlength": 160}}},
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
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get error 400
      """
        {"_issues": {"validator exception": "['WA:Navy steps in with WA asylum-seeker boat: ABSTRACT is a required field']"}, "_status": "ERR"}
      """

    @auth
    @notification
    Scenario: Try to kill an item that is in a published package
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
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
      When we publish "tag:localhost:2015:515b895a-b336-48b2-a506-5ffaf561b916" with "kill" type and "killed" state
      Then we get error 400
      """
      {"_issues": {"validator exception": "400: This item is in a package it needs to be removed before the item can be killed"}, "_status": "ERR"}
      """

    @auth
   @notification
    Scenario: Publish a composite item with a story that is spiked fails
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
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
              "state" : "spiked",
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
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get error 400
      """
        {"_issues": {"validator exception": "['Package cannot contain spiked item']"}, "_status": "ERR"}
      """



      @auth
      @notification
      Scenario: Publish a package with two text stories and one digital subscriber
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we post to "/subscribers" with success
          """
          {
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }
          """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "item-1 headline", "_current_version": 2, "state": "published"},
                   {"_id": "456", "guid": "456", "headline": "item-2 headline", "_current_version": 2, "state": "published"},
                   {"headline": "item-1 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "item-2 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "test package", "state": "published", "type": "composite"}
                  ]
      }
      """
      When we get "/publish_queue"
      Then we get list with 3 items



      @auth
      @notification
      Scenario: Publish a package with two text stories and one wire subscriber
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
          When we post to "/subscribers" with success
          """
          {
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "wire",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }
          """
          When we publish "compositeitem" with "publish" type and "published" state
          Then we get response code 200
          When we get "/published"
          Then we get existing resource
          """
          {"_items" : [{"_id": "123", "guid": "123", "headline": "item-1 headline", "_current_version": 2, "state": "published"},
                       {"_id": "456", "guid": "456", "headline": "item-2 headline", "_current_version": 2, "state": "published"},
                       {"headline": "test package", "state": "published", "type": "composite"}
                      ]
          }
          """
          When we get "/publish_queue"
          Then we get list with 2 items



      @auth
      @notification
      Scenario: Publish a package with two text stories and one wire and one digital subscriber
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      Given "subscribers"
          """
          [{
            "_id": "sub-1",
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "wire",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-2",
            "name":"Channel 4","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }]
          """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "item-1 headline", "_current_version": 2, "state": "published"},
                   {"_id": "456", "guid": "456", "headline": "item-2 headline", "_current_version": 2, "state": "published"},
                   {"headline": "item-1 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "item-2 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "test package", "state": "published", "type": "composite"}
                  ]
      }
      """
        When we get digital item of "123"
        When we get "/publish_queue"
        Then we get list with 5 items
        Then we get "#archive.123.take_package#" in formatted output as "main" story for subscriber "sub-2"



      @auth
      @notification
      Scenario: Publish two takes within a package in different groups with one wire and one digital subscriber
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
      """
      [{
          "guid": "123",
          "type": "text",
          "headline": "Take-1 soccer headline",
          "abstract": "Take-1 abstract",
          "task": {
              "user": "#CONTEXT_USER_ID#"
          },
          "body_html": "Take-1",
          "state": "draft",
          "slugline": "Take-1 slugline",
          "urgency": "4",
          "pubstatus": "usable",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "anpa_category": [{"qcode": "A", "name": "Sport"}],
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
      Then we get next take as "TAKE2"
      """
      {
          "type": "text",
          "headline": "Take-1 soccer headline",
          "slugline": "Take-1 slugline",
          "anpa_take_key": "Take=2",
          "state": "draft",
          "original_creator": "#CONTEXT_USER_ID#"
      }
      """
      When we patch "/archive/#TAKE2#"
      """
      {"body_html": "Take-2", "abstract": "Take-2 Abstract",
      "headline": "Take-2 soccer headline", "slugline": "Take-2 slugline"}
      """
      And we post to "/archive/#TAKE2#/move"
      """
      [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
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
                          "slugline": "Take-1 slugline",
                          "guid": "123",
                          "headline": "Take-1 soccer headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Take-2 slugline",
                          "guid": "#TAKE2#",
                          "headline": "Take-2 soccer headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "#TAKE2#"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      Given "subscribers"
          """
          [{
            "_id": "sub-1",
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "wire",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-2",
            "name":"Channel 4","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }]
          """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "Take-1 soccer headline", "_current_version": 4, "state": "published"},
                   {"_id": "#TAKE2#", "guid": "#TAKE2#", "headline": "Take-2 soccer headline", "_current_version": 4, "state": "published"},
                   {"headline": "Take-1 soccer headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "Take-2 soccer headline", "_current_version": 3, "state": "published", "package_type": "takes"},
                   {"headline": "test package", "state": "published", "type": "composite"}
                  ]
      }
      """
      When we get digital item of "123"
      When we get "/publish_queue"
      Then we get list with 5 items
      Then we get "#archive.123.take_package#" in formatted output as "main" story for subscriber "sub-2"
      Then we get "#archive.123.take_package#" in formatted output as "sidebars" story for subscriber "sub-2"



      @auth
      @notification
      @vocabulary
      Scenario: Publish two takes within a package in the same group with one wire and one digital subscriber
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
      """
      [{
          "guid": "123",
          "type": "text",
          "headline": "Take-1 soccer headline",
          "abstract": "Take-1 abstract",
          "task": {
              "user": "#CONTEXT_USER_ID#"
          },
          "body_html": "Take-1",
          "state": "draft",
          "slugline": "Take-1 slugline",
          "urgency": "4",
          "pubstatus": "usable",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "anpa_category": [{"qcode": "A", "name": "Sport"}],
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
      Then we get next take as "TAKE2"
      """
      {
          "type": "text",
          "headline": "Take-1 soccer headline",
          "slugline": "Take-1 slugline",
          "anpa_take_key": "Take=2",
          "state": "draft",
          "original_creator": "#CONTEXT_USER_ID#"
      }
      """
      When we patch "/archive/#TAKE2#"
      """
      {"body_html": "Take-2", "abstract": "Take-2 Abstract",
      "headline": "Take-2 soccer headline", "slugline": "Take-2 slugline"}
      """
      And we post to "/archive/#TAKE2#/move"
      """
      [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
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
                      }
                  ],
                  "role": "grpRole:NEP"
              },
              {
                  "id": "main",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Take-1 slugline",
                          "guid": "123",
                          "headline": "Take-1 soccer headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      },
                      {
                          "renditions": {},
                          "slugline": "Take-2 slugline",
                          "guid": "#TAKE2#",
                          "headline": "Take-2 soccer headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "#TAKE2#"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "compositeitem",
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite",
              "urgency": "4",
              "anpa_category": [{"qcode": "A", "name": "Sport"}]
          }]
          """
      Given "subscribers"
          """
          [{
            "_id": "sub-1",
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "wire",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-2",
            "name":"Channel 4","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "newsml12", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }]
          """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "Take-1 soccer headline", "_current_version": 4, "state": "published"},
                   {"_id": "#TAKE2#", "guid": "#TAKE2#", "headline": "Take-2 soccer headline", "_current_version": 4, "state": "published"},
                   {"headline": "Take-1 soccer headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "Take-2 soccer headline", "_current_version": 3, "state": "published", "package_type": "takes"},
                   {"headline": "test package", "state": "published", "type": "composite"}
                  ]
      }
      """
      When we get digital item of "123"
      When we get "/publish_queue"
      Then we get list with 5 items
      Then we get "#archive.123.take_package#" in formatted output as "NewsItemId" newsml12 story


      @auth
      @notification
      @vocabulary
      Scenario: Publish a package with a text and an image with one wire and one digital subscriber
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
          """
          When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 picture",
              "guid" : "456",
              "state" : "submitted",
              "type" : "picture",
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
              "groups": [
              {
                  "id": "root",
                  "refs": [
                      {
                          "idRef": "main"
                      }
                  ],
                  "role": "grpRole:NEP"
              },
              {
                  "id": "main",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "item-1 slugline",
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      },
                      {
                          "renditions": {},
                          "slugline": "item-2 slugline",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "picture",
                          "itemClass": "icls:text",
                          "residRef": "456"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "compositeitem",
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite",
              "urgency": "4",
              "anpa_category": [{"qcode": "A", "name": "Sport"}]
          }]
          """
      Given "subscribers"
          """
          [{
            "_id": "sub-1",
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "wire",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "nitf", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-2",
            "name":"Channel 4","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }]
          """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "item-1 headline", "_current_version": 2, "state": "published"},
                   {"_id": "456", "guid": "456", "headline": "item-2 picture", "_current_version": 2, "state": "published"},
                   {"headline": "item-1 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "test package", "state": "published", "type": "composite"}
                  ]
      }
      """
      When we get digital item of "123"
      When we get "/publish_queue"
      Then we get list with 4 items
      Then we get "#archive.123.take_package#" in formatted output as "main" story for subscriber "sub-2"



      @auth
      @notification
      @vocabulary
      Scenario: Publish a package with a text and an image with only one wire subscriber
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
          """
          When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 picture",
              "guid" : "456",
              "state" : "submitted",
              "type" : "picture",
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
              "groups": [
              {
                  "id": "root",
                  "refs": [
                      {
                          "idRef": "main"
                      }
                  ],
                  "role": "grpRole:NEP"
              },
              {
                  "id": "main",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "item-1 slugline",
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      },
                      {
                          "renditions": {},
                          "slugline": "item-2 slugline",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "picture",
                          "itemClass": "icls:text",
                          "residRef": "456"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "compositeitem",
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite",
              "urgency": "4",
              "anpa_category": [{"qcode": "A", "name": "Sport"}]
          }]
          """
      Given "subscribers"
          """
          [{
            "_id": "sub-1",
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "wire",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "nitf", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }]
          """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "item-1 headline", "_current_version": 2, "state": "published"},
                   {"_id": "456", "guid": "456", "headline": "item-2 picture", "_current_version": 2, "state": "published"},
                   {"headline": "test package", "state": "published", "type": "composite"}
                  ]
      }
      """
      When we get digital item of "123"
      When we get "/publish_queue"
      Then we get list with 1 items
      """
      {"_items" : [{"item_id": "123", "content_type": "text", "state": "pending"}]
      }
      """



      @auth
      @notification
      Scenario: Publish a package with two already published text stories and one digital subscriber
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }]
          """
      Given "subscribers"
      """
      [{
        "_id": "sub-2",
        "name":"Channel 3","media_type":"media",
        "subscriber_type": "digital",
        "sequence_num_settings":{"min" : 1, "max" : 10},
        "email": "test@test.com",
        "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
      }]
      """
      When we publish "123" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_id": "123", "state": "published"}
      """
      When we publish "456" with "publish" type and "published" state
      Then we get OK response
      And we get existing resource
      """
      {"_id": "456", "state": "published"}
      """
      When we get "/publish_queue"
      Then we get list with 2 items
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """

      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "item-1 headline", "_current_version": 2, "state": "published"},
                   {"_id": "456", "guid": "456", "headline": "item-2 headline", "_current_version": 2, "state": "published"},
                   {"headline": "item-1 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "item-2 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "test package", "state": "published", "type": "composite"}
                  ]
      }
      """
      When we get "/publish_queue"
      Then we get list with 3 items
      """
      {"_items" : [{"headline": "item-1 headline", "content_type": "composite", "state": "pending"},
                   {"headline": "item-2 headline", "content_type": "composite", "state": "pending"},
                   {"headline": "test package", "content_type": "composite", "state": "pending"}]
      }
      """
      Then we get "#archive.123.take_package#" in formatted output as "main" story for subscriber "sub-2"
      Then we get "#archive.456.take_package#" in formatted output as "sidebars" story for subscriber "sub-2"




      @auth
      @notification
      @vocabulary
      Scenario: Publish a package with three already published text stories being sent different subscribers
      Given empty "filter_conditions"
      Given empty "content_filters"
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
                  }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "urgency": "1",
              "body_html": "item-2 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
                  }
          }, {
              "headline" : "item-3 headline",
              "guid" : "789",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-3 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
                  }
          }]
          """
      When we post to "/filter_conditions" with success
      """
      [{"name": "sport", "field": "urgency", "operator": "in", "value": "1"}]
      """
      Then we get latest
      When we post to "/content_filters" with success
      """
      [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
      """
      Then we get latest
      Given "subscribers"
      """
      [{
            "_id": "sub-1",
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "wire",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "nitf", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-2",
            "name":"Channel 4","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "content_filter":{"filter_id":"#content_filters._id#", "filter_type":"blocking"},
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-3",
            "name":"Channel 5","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }]
      """
      When we publish "123" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "state": "published", "type": "text"},
      {"state": "published", "type": "composite", "headline": "item-1 headline"}]}
      """
      When we publish "456" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "456", "state": "published", "type": "text"},
      {"state": "published", "type": "composite", "headline": "item-2 headline"}]}
      """
      When we publish "789" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "789", "state": "published", "type": "text"},
      {"state": "published", "type": "composite", "headline": "item-3 headline"}]}
      """
      When we get "/publish_queue"
      Then we get list with 8 items
      """
      {"_items" : [
      {"headline": "item-1 headline", "content_type": "text", "subscriber_id": "sub-1"},
      {"headline": "item-1 headline", "content_type": "composite", "subscriber_id": "sub-2"},
      {"headline": "item-1 headline", "content_type": "composite", "subscriber_id": "sub-3"},
      {"headline": "item-2 headline", "content_type": "text", "subscriber_id": "sub-1"},
      {"headline": "item-2 headline", "content_type": "composite", "subscriber_id": "sub-3"},
      {"headline": "item-3 headline", "content_type": "text", "subscriber_id": "sub-1"},
      {"headline": "item-3 headline", "content_type": "composite", "subscriber_id": "sub-2"},
      {"headline": "item-3 headline", "content_type": "composite", "subscriber_id": "sub-3"}
      ]}
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
                      },
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "789",
                          "headline": "item-3 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "789"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """

      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "item-1 headline", "_current_version": 2, "state": "published"},
                   {"_id": "456", "guid": "456", "headline": "item-2 headline", "_current_version": 2, "state": "published"},
                   {"headline": "item-1 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "item-2 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "test package", "state": "published", "type": "composite"}
                  ]
      }
      """
      When we get "/publish_queue"
      Then we get list with 10 items
      """
      {"_items" : [
      {"headline": "test package", "content_type": "composite", "subscriber_id": "sub-2"},
      {"headline": "test package", "content_type": "composite", "subscriber_id": "sub-3"}
      ]}
      """
      Then we get "#archive.123.take_package#" in formatted output as "main" story for subscriber "sub-2"
      Then we get "#archive.789.take_package#" in formatted output as "sidebars" story for subscriber "sub-2"
      Then we get "#archive.123.take_package#" in formatted output as "main" story for subscriber "sub-3"
      Then we get "#archive.456.take_package#" in formatted output as "sidebars" story for subscriber "sub-3"
      Then we get "#archive.789.take_package#" in formatted output as "sidebars" story for subscriber "sub-3"


      @auth
      @notification
      @vocabulary
      Scenario: Publish a package with three already published text stories no subscribers matched so no package sent
      Given empty "filter_conditions"
      Given empty "content_filters"
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "urgency": "1",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
                  }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "urgency": "1",
              "body_html": "item-2 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
                  }
          }, {
              "headline" : "item-3 headline",
              "guid" : "789",
              "urgency": "1",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-3 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
                  }
          }]
          """
      When we post to "/filter_conditions" with success
      """
      [{"name": "sport", "field": "urgency", "operator": "in", "value": "1"}]
      """
      Then we get latest
      When we post to "/content_filters" with success
      """
      [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
      """
      Then we get latest
      Given "subscribers"
      """
      [{
            "_id": "sub-1",
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "wire",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "nitf", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-2",
            "name":"Channel 4","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "content_filter":{"filter_id":"#content_filters._id#", "filter_type":"blocking"},
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-3",
            "name":"Channel 5","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "content_filter":{"filter_id":"#content_filters._id#", "filter_type":"blocking"},
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }]
      """
      When we publish "123" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "state": "published", "type": "text"}]}
      """
      When we publish "456" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "456", "state": "published", "type": "text"}]}
      """
      When we publish "789" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "789", "state": "published", "type": "text"}]}
      """
      When we get "/publish_queue"
      Then we get list with 3 items
      """
      {"_items" : [
      {"headline": "item-1 headline", "content_type": "text", "subscriber_id": "sub-1"},
      {"headline": "item-2 headline", "content_type": "text", "subscriber_id": "sub-1"},
      {"headline": "item-3 headline", "content_type": "text", "subscriber_id": "sub-1"}
      ]}
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
                      },
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "789",
                          "headline": "item-3 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "789"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """

      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "item-1 headline", "_current_version": 2, "state": "published"},
                   {"_id": "456", "guid": "456", "headline": "item-2 headline", "_current_version": 2, "state": "published"},
                   {"_id": "789", "guid": "789", "headline": "item-3 headline", "_current_version": 2, "state": "published"},
                   {"headline": "test package", "state": "published", "type": "composite"}
                  ]
      }
      """
      When we get "/publish_queue"
      Then we get list with 3 items
      """
      {"_items" : [
      {"headline": "item-1 headline", "content_type": "text", "subscriber_id": "sub-1"},
      {"headline": "item-2 headline", "content_type": "text", "subscriber_id": "sub-1"},
      {"headline": "item-3 headline", "content_type": "text", "subscriber_id": "sub-1"}
      ]}
      """



      @auth
      @notification
      Scenario: Publish a nested package with two text stories and one digital subscriber
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }]
          """
      Given "subscribers"
      """
      [{
        "_id": "sub-2",
        "name":"Channel 3","media_type":"media",
        "subscriber_type": "digital",
        "sequence_num_settings":{"min" : 1, "max" : 10},
        "email": "test@test.com",
        "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
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
                          "guid": "compositeitem",
                          "headline": "test package",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "compositeitem"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "outercompositeitem",
              "headline" : "outer test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we publish "outercompositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get existing resource
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "item-1 headline", "_current_version": 2, "state": "published"},
                   {"_id": "456", "guid": "456", "headline": "item-2 headline", "_current_version": 2, "state": "published"},
                   {"headline": "item-1 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "item-2 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "test package", "state": "published", "type": "composite"},
                   {"headline": "outer test package", "state": "published", "type": "composite"}
                  ]
      }
      """
      When we get "/publish_queue"
      Then we get list with 4 items
      """
      {"_items" : [{"headline": "item-1 headline", "content_type": "composite", "subscriber_id": "sub-2"},
                   {"headline": "item-2 headline", "content_type": "composite", "subscriber_id": "sub-2"},
                   {"headline": "test package", "content_type": "composite", "subscriber_id": "sub-2"},
                   {"headline": "outer test package", "content_type": "composite", "subscriber_id": "sub-2"}]
      }
      """
      When we get digital item of "123"
      When we get "/publish_queue"
      Then we get "#archive.123.take_package#" as "main" story for subscriber "sub-2" in package "compositeitem"
      When we get digital item of "456"
      When we get "/publish_queue"
      Then we get "#archive.456.take_package#" as "sidebars" story for subscriber "sub-2" in package "compositeitem"
      Then we get "compositeitem" in formatted output as "main" story for subscriber "sub-2"
      When we get "/archive/compositeitem?version=all"
      Then we get list with 2 items
      When we get "/archive/outercompositeitem?version=all"
      Then we get list with 2 items





      @auth
      @notification
      @vocabulary
      Scenario: Publish a nested package with three inner packages and three digital subscribers
      Given empty "archive"
      Given empty "desks"
      Given empty "published"
      Given empty "publish_queue"
      Given empty "filter_conditions"
      Given empty "content_filters"
      Given empty "subscribers"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "11",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "22",
              "state" : "submitted",
              "type" : "text",
              "urgency": 1,
              "body_html": "item-2 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-3 headline",
              "guid" : "33",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
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
              "headline" : "ABC-4",
              "byline" : "PAUL MILLER",
              "source" : "AAP Image",
              "mimetype" : "image/jpeg",
              "type" : "picture",
              "urgency":1,
              "pubstatus" : "usable",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "44",
              "renditions" : {
                  "baseImage" : {
                      "height" : 1400,
                      "media" : "55b078b31d41c8e974d17ecf",
                      "href" : "http://localhost:5000/api/upload/55b078b31d41c8e974d17ecf/raw?_schema=http",
                      "mimetype" : "image/jpeg",
                      "width" : 933
                  }
              },
              "slugline" : "ABC SHOP CLOSURES"
        }, {
              "original_source" : "AAP Image/AAP",
              "description" : "A test picture",
              "state" : "submitted",
              "headline" : "ABC-5",
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
              "guid" : "55",
              "renditions" : {
                  "baseImage" : {
                      "height" : 1400,
                      "media" : "55b078b31d41c8e974d17ecf",
                      "href" : "http://localhost:5000/api/upload/55b078b31d41c8e974d17ecf/raw?_schema=http",
                      "mimetype" : "image/jpeg",
                      "width" : 933
                  }
              },
              "slugline" : "ABC SHOP CLOSURES"
        }, {
              "original_source" : "AAP Image/AAP",
              "description" : "A test picture",
              "state" : "submitted",
              "headline" : "ABC-6",
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
              "guid" : "66",
              "renditions" : {
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
        When we post to "/filter_conditions" with success
        """
        [{"name": "sport", "field": "urgency", "operator": "in", "value": "1"}]
        """
        Then we get latest
        When we post to "/content_filters" with success
        """
        [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
        """
        Then we get latest
        Given "subscribers"
        """
        [{
              "_id": "sub-1",
              "name":"Channel 3","media_type":"media",
              "subscriber_type": "digital",
              "sequence_num_settings":{"min" : 1, "max" : 10},
              "email": "test@test.com",
              "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
            }, {
              "_id": "sub-2",
              "name":"Channel 4","media_type":"media",
              "subscriber_type": "digital",
              "sequence_num_settings":{"min" : 1, "max" : 10},
              "email": "test@test.com",
              "content_filter":{"filter_id":"#content_filters._id#", "filter_type":"blocking"},
              "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
            }, {
              "_id": "sub-3",
              "name":"Channel 5","media_type":"media",
              "subscriber_type": "digital",
              "sequence_num_settings":{"min" : 1, "max" : 10},
              "email": "test@test.com",
              "content_filter":{"filter_id":"#content_filters._id#", "filter_type":"blocking"},
              "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
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
                          "guid": "11",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "11"
                      }, {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "44",
                          "headline": "item-1 image",
                          "location": "archive",
                          "type": "picture",
                          "itemClass": "icls:picture",
                          "residRef": "44"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "compositeitem1",
              "headline" : "test package 1",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      And we post to "archive" with success
          """
          [{
              "groups": [
              {
                  "id": "root",
                  "refs": [
                      {
                          "idRef": "main"
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
                          "guid": "22",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "22"
                      }, {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "55",
                          "headline": "item-2 image",
                          "location": "archive",
                          "type": "picture",
                          "itemClass": "icls:picture",
                          "residRef": "55"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "compositeitem2",
              "headline" : "test package 2",
              "state" : "submitted",
              "type" : "composite"
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
                          "guid": "33",
                          "headline": "item-3 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "33"
                      }, {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "66",
                          "headline": "item-3 image",
                          "location": "archive",
                          "type": "picture",
                          "itemClass": "icls:picture",
                          "residRef": "66"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "compositeitem3",
              "headline" : "test package 3",
              "state" : "submitted",
              "type" : "composite"
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
                          "guid": "compositeitem1",
                          "headline": "test package 1",
                          "location": "archive",
                          "type": "composite",
                          "itemClass": "icls:text",
                          "residRef": "compositeitem1"
                      },
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "compositeitem2",
                          "headline": "test package 2",
                          "location": "archive",
                          "type": "composite",
                          "itemClass": "icls:text",
                          "residRef": "compositeitem2"
                      },{
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "compositeitem3",
                          "headline": "test package 3",
                          "location": "archive",
                          "type": "composite",
                          "itemClass": "icls:text",
                          "residRef": "compositeitem3"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "outercompositeitem",
              "headline" : "outer test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we publish "outercompositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get list with 13 items
      Then we get existing resource
      """
      {"_items" : [{"_id": "11", "headline": "item-1 headline", "state": "published"},
                   {"_id": "22", "headline": "item-2 headline", "state": "published"},
                   {"_id": "33", "headline": "item-3 headline", "state": "published"},
                   {"_id": "44", "type": "picture", "state": "published"},
                   {"_id": "55", "type": "picture", "state": "published"},
                   {"_id": "66", "type": "picture", "state": "published"},
                   {"_id": "compositeitem1", "type": "composite", "state": "published"},
                   {"_id": "compositeitem2", "type": "composite", "state": "published"},
                   {"_id": "compositeitem3", "type": "composite", "state": "published"},
                   {"_id": "compositeitem3", "type": "composite", "state": "published"},
                   {"headline": "item-1 headline", "package_type": "takes"},
                   {"headline": "item-2 headline", "package_type": "takes"},
                   {"headline": "item-3 headline", "package_type": "takes"},
                   {"headline": "outer test package", "state": "published", "type": "composite"}
                  ]
      }
      """
      When we get "/publish_queue?max_results=100"
      Then we get list with 26 items
      """
      {"_items" : [{"headline": "item-1 headline", "content_type": "composite", "subscriber_id": "sub-1"},
                   {"headline": "ABC-4", "content_type": "picture", "subscriber_id": "sub-1"},
                   {"headline": "test package 1", "content_type": "composite", "subscriber_id": "sub-1"},
                   {"headline": "item-2 headline", "content_type": "composite", "subscriber_id": "sub-1"},
                   {"headline": "ABC-5", "content_type": "picture", "subscriber_id": "sub-1"},
                   {"headline": "test package 2", "content_type": "composite", "subscriber_id": "sub-1"},
                   {"headline": "item-3 headline", "content_type": "composite", "subscriber_id": "sub-1"},
                   {"headline": "ABC-6", "content_type": "picture", "subscriber_id": "sub-1"},
                   {"headline": "test package 3", "content_type": "composite", "subscriber_id": "sub-1"},
                   {"headline": "outer test package", "content_type": "composite", "subscriber_id": "sub-1"},
                   {"headline": "item-1 headline", "content_type": "composite", "subscriber_id": "sub-2"},
                   {"headline": "test package 1", "content_type": "composite", "subscriber_id": "sub-2"},
                   {"headline": "ABC-5", "content_type": "picture", "subscriber_id": "sub-2"},
                   {"headline": "test package 2", "content_type": "composite", "subscriber_id": "sub-2"},
                   {"headline": "item-3 headline", "content_type": "composite", "subscriber_id": "sub-2"},
                   {"headline": "ABC-6", "content_type": "picture", "subscriber_id": "sub-2"},
                   {"headline": "test package 3", "content_type": "composite", "subscriber_id": "sub-2"},
                   {"headline": "outer test package", "content_type": "composite", "subscriber_id": "sub-2"}]
      }
      """
      When we get digital item of "11"
      And we get "/publish_queue?max_results=100"
      Then we get "#archive.11.take_package#" as "main" story for subscriber "sub-1" in package "compositeitem1"
      And we get "compositeitem1" as "main" story for subscriber "sub-2" in package "outercompositeitem"
      And we get "compositeitem2" as "main" story for subscriber "sub-2" in package "outercompositeitem"
      And we get "compositeitem3" as "main" story for subscriber "sub-2" in package "outercompositeitem"


      @auth
      @notification
      Scenario: Correct a text story exists in a published package
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
          {"_id": "correct_composite", "act": "correct", "type": "composite", "schema":{}},
          {"_id": "correct_picture", "act": "correct", "type": "picture", "schema":{}},
          {"_id": "correct_text", "act": "correct", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we patch "/archive/123"
        """
        {"body_html": "xyz"}
        """
      When we post to "/subscribers" with success
          """
          {
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }
          """
      When we publish "compositeitem" with "publish" type and "published" state
        """
          {"groups": [
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
                      }
                  ],
                  "role": "grpRole:sidebars"
              }
          ]}
          """
      Then we get OK response
      When we get "/published"
      Then we get list with 5 items
      """
      {"_items" : [{"headline": "test package", "state": "published", "type": "composite",
                   "groups" : [{"role":"grpRole:main","id":"main",
                   "refs":[{"residRef":"123", "headline": "item-1 headline", "_current_version":3}]}]}]
      }
      """
      When we get "/publish_queue"
      Then we get list with 3 items
      When we publish "123" with "correct" type and "corrected" state
        """
        {"headline": "item-1.2 headline"}
        """
      Then we get OK response
      When we get "/published"
      Then we get list with 8 items
      """
      {"_items" : [{"headline": "item-1.2 headline", "type": "text", "state": "corrected"},
                   {"headline": "item-1.2 headline", "package_type": "takes", "state": "corrected"},
                   {"headline": "test package", "state": "corrected", "type": "composite",
                   "groups" : [{"role":"grpRole:main","id":"main",
                   "refs":[{"residRef":"123", "headline": "item-1.2 headline", "_current_version":4}]}]}]
      }
      """
      When we get "/publish_queue"
      Then we get list with 5 items
      """
      {"_items" : [{"headline": "item-1.2 headline", "publishing_action": "corrected"},
                   {"headline": "test package", "publishing_action": "corrected"}]
      }
      """


      @auth
      @notification
      Scenario: Correct a text story exists in a published package succeeds without a valid subscriber
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
          {"_id": "correct_composite", "act": "correct", "type": "composite", "schema":{}},
          {"_id": "correct_picture", "act": "correct", "type": "picture", "schema":{}},
          {"_id": "correct_text", "act": "correct", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get list with 3 items
      When we get "/publish_queue"
      Then we get list with 0 items
      When we publish "123" with "correct" type and "corrected" state
      Then we get OK response
      When we get "/published"
      Then we get list with 5 items
      """
      {"_items" : [{"_id": "123", "headline": "item-1 headline", "state": "corrected"},
                   {"headline": "test package", "state": "corrected", "type": "composite"}]
      }
      """
      When we get "/publish_queue"
      Then we get list with 0 items


      @auth
      @notification
      Scenario: Correct a text story exists in a non-published package doesn't correct the package
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
          {"_id": "correct_composite", "act": "correct", "type": "composite", "schema":{}},
          {"_id": "correct_picture", "act": "correct", "type": "picture", "schema":{}},
          {"_id": "correct_text", "act": "correct", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }]
          """
      When we post to "/subscribers" with success
          """
          {
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we publish "123" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get list with 2 items
      When we get "/publish_queue"
      Then we get list with 1 items
      When we publish "123" with "correct" type and "corrected" state
      Then we get OK response
      When we get "/published"
      Then we get list with 4 items
      """
      {"_items" : [{"_id": "123", "headline": "item-1 headline", "state": "corrected"}]
      }
      """
      When we get "/publish_queue"
      Then we get list with 2 items



      @auth
      @notification
      Scenario: Correct a story in a nested package
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
          {"_id": "correct_composite", "act": "correct", "type": "composite", "schema":{}},
          {"_id": "correct_picture", "act": "correct", "type": "picture", "schema":{}},
          {"_id": "correct_text", "act": "correct", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }]
          """
      Given "subscribers"
      """
      [{
        "_id": "sub-2",
        "name":"Channel 3","media_type":"media",
        "subscriber_type": "digital",
        "sequence_num_settings":{"min" : 1, "max" : 10},
        "email": "test@test.com",
        "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
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
                          "guid": "compositeitem",
                          "headline": "test package",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "compositeitem"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "outercompositeitem",
              "headline" : "outer test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we publish "outercompositeitem" with "publish" type and "published" state
        """
          {"groups": [
              {
                  "id": "root",
                  "refs": [
                      {
                          "idRef": "main"
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
                          "guid": "compositeitem",
                          "headline": "test package",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "compositeitem"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ]}
          """
      Then we get OK response
      When we get "/published"
      Then we get list with 6 items
      """
      {"_items" : [{"_id": "123", "guid": "123", "headline": "item-1 headline", "_current_version": 2, "state": "published"},
                   {"_id": "456", "guid": "456", "headline": "item-2 headline", "_current_version": 2, "state": "published"},
                   {"headline": "item-1 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "item-2 headline", "_current_version": 2, "state": "published", "package_type": "takes"},
                   {"headline": "test package", "state": "published", "type": "composite"},
                   {"headline": "outer test package", "state": "published", "type": "composite",
                   "groups" : [{"role":"grpRole:main", "id":"main",
                   "refs":[{"residRef":"compositeitem", "headline": "test package", "_current_version":1}]}]}
                  ]
      }
      """
      When we get "/publish_queue"
      Then we get list with 4 items
      """
      {"_items" : [{"headline": "item-1 headline", "content_type": "composite", "subscriber_id": "sub-2"},
                   {"headline": "item-2 headline", "content_type": "composite", "subscriber_id": "sub-2"},
                   {"headline": "test package", "content_type": "composite", "subscriber_id": "sub-2"},
                   {"headline": "outer test package", "content_type": "composite", "subscriber_id": "sub-2"}]
      }
      """
      When we publish "123" with "correct" type and "corrected" state
      """
      {"headline": "item-1.2 headline"}
      """
      Then we get OK response
      When we get "/published"
      Then we get list with 10 items
      """
      {"_items" : [{"headline": "test package", "state": "corrected", "type": "composite",
                     "groups" : [{"role":"grpRole:main", "id":"main",
                     "refs":[{"residRef":"123", "headline": "item-1.2 headline", "_current_version":3}]}]
                   },
                   {"headline": "outer test package", "state": "corrected", "type": "composite",
                     "groups" : [{"role":"grpRole:main", "id":"main",
                     "refs":[{"residRef":"compositeitem", "headline": "test package", "_current_version":2}]}]
                   }
                  ]
      }
      """
      When we get "/publish_queue"
      Then we get list with 7 items
      """
      {"_items" : [{"headline": "item-1.2 headline", "publishing_action": "corrected"},
                   {"headline": "test package", "publishing_action": "corrected"},
                   {"headline": "outer test package", "publishing_action": "corrected", "subscriber_id": "sub-2"}]
      }
      """
      When we get "/archive/123?version=all"
      Then we get list with 3 items
      When we get "/archive/compositeitem?version=all"
      Then we get list with 3 items
      When we get "/archive/outercompositeitem?version=all"
      Then we get list with 3 items


      @auth
      @notification
      Scenario: Killing a text story exists in a unpublished package fails
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
          {"_id": "correct_composite", "act": "correct", "type": "composite", "schema":{}},
          {"_id": "correct_picture", "act": "correct", "type": "picture", "schema":{}},
          {"_id": "correct_text", "act": "correct", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }]
          """
      When we post to "/subscribers" with success
          """
          {
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we publish "123" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get list with 2 items
      When we get "/publish_queue"
      Then we get list with 1 items
      When we publish "123" with "kill" type and "killed" state
      Then we get error 400
      """
      {"_issues": {"validator exception": "400: This item is in a package it needs to be removed before the item can be killed"}, "_status": "ERR"}
      """




      @auth
      @notification
      @vocabulary
      Scenario: Correct a published package by removing a story
      Given empty "archive"
      Given empty "desks"
      Given empty "published"
      Given empty "publish_queue"
      Given empty "filter_conditions"
      Given empty "content_filters"
      Given empty "subscribers"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
          {"_id": "correct_composite", "act": "correct", "type": "composite", "schema":{}},
          {"_id": "correct_picture", "act": "correct", "type": "picture", "schema":{}},
          {"_id": "correct_text", "act": "correct", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "urgency": "2",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "urgency": "2",
              "body_html": "item-2 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-3 headline",
              "guid" : "789",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-3 content",
              "urgency": "1",
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
              "groups": [
              {
                  "id": "root",
                  "refs": [
                      {
                          "idRef": "main"
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      },
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
                      },
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "789",
                          "headline": "item-3 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "789"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "compositeitem",
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we post to "/filter_conditions" with success
      """
      [{"name": "sport", "field": "urgency", "operator": "in", "value": "1,3"}]
      """
      Then we get latest
      When we post to "/content_filters" with success
      """
      [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
      """
      Then we get latest
      Given "subscribers"
      """
      [{
            "_id": "sub-1",
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "content_filter":{"filter_id":"#content_filters._id#", "filter_type": "blocking"},
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-2",
            "name":"Channel 4","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-3",
            "name":"Channel 5","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "content_filter":{"filter_id":"#content_filters._id#", "filter_type": "permitting"},
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }]
      """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get list with 7 items
      """
      {"_items" : [{"_id": "123", "headline": "item-1 headline", "state": "published"},
                   {"_id": "456", "headline": "item-2 headline", "state": "published"},
                   {"_id": "789", "headline": "item-3 headline", "state": "published"},
                   {"headline": "item-1 headline", "package_type": "takes", "state": "published"},
                   {"headline": "item-2 headline", "package_type": "takes", "state": "published"},
                   {"headline": "item-3 headline", "package_type": "takes", "state": "published"},
                   {"_id": "compositeitem", "headline": "test package", "state": "published", "type": "composite"}]
      }
      """
      When we get "/publish_queue"
      Then we get list with 9 items
      """
      {"_items" : [{"headline": "item-1 headline", "subscriber_id": "sub-1"},
                   {"headline": "item-2 headline", "subscriber_id": "sub-1"},
                   {"headline": "item-1 headline", "subscriber_id": "sub-2"},
                   {"headline": "item-2 headline", "subscriber_id": "sub-2"},
                   {"headline": "item-3 headline", "subscriber_id": "sub-2"},
                   {"headline": "item-3 headline", "subscriber_id": "sub-3"},
                   {"headline": "test package", "subscriber_id": "sub-1"},
                   {"headline": "test package", "subscriber_id": "sub-2"},
                   {"headline": "test package", "subscriber_id": "sub-3"}]
      }
      """
      When we publish "compositeitem" with "correct" type and "corrected" state
        """
          {
              "groups": [
              {
                  "id": "root",
                  "refs": [
                      {
                          "idRef": "main"
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      },
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "guid" : "compositeitem",
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }
          """
      Then we get OK response
      When we get "/published"
      Then we get list with 8 items
      """
      {"_items" : [{"headline": "test package", "state": "corrected", "type": "composite"}]
      }
      """
      When we get "/publish_queue"
      Then we get list with 12 items
      """
      {"_items" : [{"headline": "test package", "publishing_action": "corrected", "subscriber_id": "sub-1"},
                   {"headline": "test package", "publishing_action": "corrected", "subscriber_id": "sub-2"},
                   {"headline": "test package", "publishing_action": "corrected", "subscriber_id": "sub-3"}]
      }
      """
      When we get digital item of "789"
      When we get "/publish_queue"
      Then we get "#archive.789.take_package#" as "main" story for subscriber "sub-1" not in package "compositeitem" version "3"
      Then we get "#archive.789.take_package#" as "main" story for subscriber "sub-2" not in package "compositeitem" version "3"
      Then we get "#archive.789.take_package#" as "main" story for subscriber "sub-3" not in package "compositeitem" version "3"



      @auth
      @notification
      @vocabulary
      Scenario: Correct a published package by adding a story
      Given empty "archive"
      Given empty "subscribers"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
          {"_id": "correct_composite", "act": "correct", "type": "composite", "schema":{}},
          {"_id": "correct_picture", "act": "correct", "type": "picture", "schema":{}},
          {"_id": "correct_text", "act": "correct", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "urgency": "2",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "urgency": "2",
              "body_html": "item-2 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-3 headline",
              "guid" : "789",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-3 content",
              "urgency": "1",
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
              "groups": [
              {
                  "id": "root",
                  "refs": [
                      {
                          "idRef": "main"
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      },
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "compositeitem",
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we post to "/filter_conditions" with success
      """
      [{"name": "sport", "field": "urgency", "operator": "in", "value": "1,3"}]
      """
      Then we get latest
      When we post to "/content_filters" with success
      """
      [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
      """
      Then we get latest
      Given "subscribers"
      """
      [{
            "_id": "sub-1",
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "content_filter":{"filter_id":"#content_filters._id#", "filter_type": "blocking"},
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-2",
            "name":"Channel 4","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-3",
            "name":"Channel 5","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "content_filter":{"filter_id":"#content_filters._id#", "filter_type": "permitting"},
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }]
      """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get list with 5 items
      """
      {"_items" : [{"_id": "123", "headline": "item-1 headline", "state": "published"},
                   {"_id": "456", "headline": "item-2 headline", "state": "published"},
                   {"headline": "item-1 headline", "package_type": "takes", "state": "published"},
                   {"headline": "item-2 headline", "package_type": "takes", "state": "published"},
                   {"_id": "compositeitem", "headline": "test package", "state": "published", "type": "composite"}]
      }
      """
      When we get "/publish_queue"
      Then we get list with 6 items
      """
      {"_items" : [{"headline": "item-1 headline", "subscriber_id": "sub-1"},
                   {"headline": "item-2 headline", "subscriber_id": "sub-1"},
                   {"headline": "item-1 headline", "subscriber_id": "sub-2"},
                   {"headline": "item-2 headline", "subscriber_id": "sub-2"},
                   {"headline": "test package", "subscriber_id": "sub-1"},
                   {"headline": "test package", "subscriber_id": "sub-2"}]
      }
      """
      When we publish "compositeitem" with "correct" type and "corrected" state
        """
          {
              "groups": [
              {
                  "id": "root",
                  "refs": [
                      {
                          "idRef": "main"
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      },
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
                      },
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "789",
                          "headline": "item-3 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "789"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "guid" : "compositeitem",
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }
          """
      Then we get OK response
      When we get "/published"
      Then we get list with 8 items
      """
      {"_items" : [{"_id": "789", "headline": "item-3 headline", "state": "published"},
                   {"headline": "item-3 headline", "package_type": "takes", "state": "published"},
                   {"_id": "compositeitem", "headline": "test package", "state": "corrected", "type": "composite"}]
      }
      """
      When we get "/publish_queue"
      Then we get list with 11 items
      """
      {"_items" : [{"headline": "item-3 headline", "publishing_action": "published", "subscriber_id": "sub-3"},
                   {"headline": "item-3 headline", "publishing_action": "published", "subscriber_id": "sub-2"},
                   {"headline": "test package", "publishing_action": "corrected", "subscriber_id": "sub-1"},
                   {"headline": "test package", "publishing_action": "corrected", "subscriber_id": "sub-2"},
                   {"headline": "test package", "publishing_action": "corrected", "subscriber_id": "sub-3"}]
      }
      """
      When we get digital item of "789"
      When we get "/publish_queue"
      Then we get "#archive.789.take_package#" as "main" story for subscriber "sub-3" in package "compositeitem"
      Then we get "#archive.789.take_package#" as "main" story for subscriber "sub-2" in package "compositeitem"
      Then we get "#archive.789.take_package#" as "main" story for subscriber "sub-1" not in package "compositeitem" version "3"
      When we get digital item of "123"
      When we get "/publish_queue"
      Then we get "#archive.123.take_package#" as "main" story for subscriber "sub-3" not in package "compositeitem" version "3"
      Then we get "#archive.123.take_package#" as "main" story for subscriber "sub-2" in package "compositeitem"
      Then we get "#archive.123.take_package#" as "main" story for subscriber "sub-1" in package "compositeitem"
      When we get digital item of "456"
      When we get "/publish_queue"
      Then we get "#archive.456.take_package#" as "main" story for subscriber "sub-3" not in package "compositeitem" version "3"
      Then we get "#archive.456.take_package#" as "main" story for subscriber "sub-2" in package "compositeitem"
      Then we get "#archive.456.take_package#" as "main" story for subscriber "sub-1" in package "compositeitem"



      @auth
      @notification
      Scenario: Kill a published package
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
          {"_id": "correct_composite", "act": "kill", "type": "composite", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we post to "/subscribers" with success
          """
          {
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }
          """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get list with 5 items
      When we get "/publish_queue"
      Then we get list with 3 items
      When we publish "compositeitem" with "kill" type and "killed" state
      Then we get OK response
      When we get "/published"
      Then we get list with 6 items
      """
      {"_items" : [{"headline": "item-1 headline", "type": "text", "state": "published"},
                   {"headline": "item-1 headline", "package_type": "takes", "state": "published"},
                   {"headline": "test package", "state": "published", "type": "composite"},
                   {"headline": "test package", "state": "killed", "type": "composite", "pubstatus": "canceled"}]
      }
      """
      When we get "/publish_queue"
      Then we get list with 4 items
      """
      {"_items" : [{"headline": "test package", "publishing_action": "killed"}]
      }
      """


      @auth
      @notification
      Scenario: Killing the nested package fails
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
          {"_id": "kill_composite", "act": "kill", "type": "composite", "schema":{}},
          {"_id": "kill_text", "act": "kill", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }]
          """
      Given "subscribers"
      """
      [{
        "_id": "sub-2",
        "name":"Channel 3","media_type":"media",
        "subscriber_type": "digital",
        "sequence_num_settings":{"min" : 1, "max" : 10},
        "email": "test@test.com",
        "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
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
                          "guid": "compositeitem",
                          "headline": "test package",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "compositeitem"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "outercompositeitem",
              "headline" : "outer test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we publish "outercompositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get list with 6 items
      When we get "/publish_queue"
      Then we get list with 4 items
      When we publish "compositeitem" with "kill" type and "killed" state
      Then we get error 400
      """
      {"_issues": {"validator exception": "400: This item is in a package it needs to be removed before the item can be killed"}, "_status": "ERR"}
      """


      @auth
      @notification
      Scenario: Publishing an empty package fails
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
          {"_id": "kill_composite", "act": "kill", "type": "composite", "schema":{}},
          {"_id": "kill_text", "act": "kill", "type": "text", "schema":{}}]
          """
      Given "subscribers"
      """
      [{
        "_id": "sub-2",
        "name":"Channel 3","media_type":"media",
        "subscriber_type": "digital",
        "sequence_num_settings":{"min" : 1, "max" : 10},
        "email": "test@test.com",
        "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
      }]
      """
      When we post to "archive" with success
          """
          [{
              "groups" : [
                  {
                      "role" : "grpRole:NEP",
                      "id" : "root",
                      "refs" : [
                          {
                              "idRef" : "main"
                          }
                      ]
                  },
                  {
                      "role" : "grpRole:main",
                      "id" : "main",
                      "refs" : []
                  }
              ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "compositeitem",
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get error 400
      """
      {"_issues": {"validator exception": "400: Empty package cannot be published!"}, "_status": "ERR"}
      """



      @auth
      @notification
      @vocabulary
      Scenario: Correct a published package by removing all stories fails
      Given empty "archive"
      Given empty "desks"
      Given empty "published"
      Given empty "publish_queue"
      Given empty "filter_conditions"
      Given empty "content_filters"
      Given empty "subscribers"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
          {"_id": "correct_composite", "act": "correct", "type": "composite", "schema":{}},
          {"_id": "correct_picture", "act": "correct", "type": "picture", "schema":{}},
          {"_id": "correct_text", "act": "correct", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "urgency": "2",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "urgency": "2",
              "body_html": "item-2 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-3 headline",
              "guid" : "789",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-3 content",
              "urgency": "1",
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
              "groups": [
              {
                  "id": "root",
                  "refs": [
                      {
                          "idRef": "main"
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      },
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
                      },
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "789",
                          "headline": "item-3 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "789"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "compositeitem",
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we post to "/filter_conditions" with success
      """
      [{"name": "sport", "field": "urgency", "operator": "in", "value": "1,3"}]
      """
      Then we get latest
      When we post to "/content_filters" with success
      """
      [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
      """
      Then we get latest
      Given "subscribers"
      """
      [{
            "_id": "sub-1",
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "content_filter":{"filter_id":"#content_filters._id#", "filter_type": "blocking"},
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-2",
            "name":"Channel 4","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }, {
            "_id": "sub-3",
            "name":"Channel 5","media_type":"media",
            "subscriber_type": "digital",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "content_filter":{"filter_id":"#content_filters._id#", "filter_type": "permitting"},
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }]
      """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we publish "compositeitem" with "correct" type and "corrected" state
        """
          {
              "groups" : [
                  {
                      "role" : "grpRole:NEP",
                      "id" : "root",
                      "refs" : [
                          {
                              "idRef" : "main"
                          }
                      ]
                  },
                  {
                      "role" : "grpRole:main",
                      "id" : "main",
                      "refs" : []
                  }
              ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "compositeitem",
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }
          """
      Then we get error 400
      """
      {"_issues": {"validator exception": "400: Corrected package cannot be empty!"}, "_status": "ERR"}
      """



      @auth
      @notification
      Scenario: Correct a text story exists in a published package one wire subscriber
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{}},
          {"_id": "correct_composite", "act": "correct", "type": "composite", "schema":{}},
          {"_id": "correct_picture", "act": "correct", "type": "picture", "schema":{}},
          {"_id": "correct_text", "act": "correct", "type": "text", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
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
              "groups": [
              {
                  "id": "root",
                  "refs": [
                      {
                          "idRef": "main"
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "compositeitem",
              "headline" : "test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we post to "/subscribers" with success
          """
          {
            "name":"Channel 3","media_type":"media",
            "subscriber_type": "wire",
            "sequence_num_settings":{"min" : 1, "max" : 10},
            "email": "test@test.com",
            "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
          }
          """
      When we publish "compositeitem" with "publish" type and "published" state
      Then we get OK response
      When we get "/published"
      Then we get list with 2 items
      When we get "/publish_queue"
      Then we get list with 1 items
      When we publish "123" with "correct" type and "corrected" state
        """
        {"headline": "item-1.2 headline"}
        """
      Then we get OK response
      When we get "/published"
      Then we get list with 4 items
      """
      {"_items" : [{"headline": "item-1.2 headline", "type": "text", "state": "corrected"},
                   {"headline": "test package", "state": "corrected", "type": "composite"}]
      }
      """
      When we get "/publish_queue"
      Then we get list with 2 items
      """
      {"_items" : [{"headline": "item-1.2 headline", "publishing_action": "corrected"}]
      }
      """


    @auth
    @notification
    Scenario: Publish a nested package where inner package does not validate
      Given empty "archive"
      Given "desks"
          """
          [{"name": "test_desk1", "members":[{"user":"#CONTEXT_USER_ID#"}]}]
          """
      And the "validators"
          """
          [{"_id": "publish_composite", "act": "publish", "type": "composite", "schema":{"headline": {"type": "string","required": true, "maxlength": 160}}},
          {"_id": "publish_text", "act": "publish", "type": "text", "schema":{"abstract": {"type": "string","required": true,"maxlength": 160}}},
          {"_id": "publish_picture", "act": "publish", "type": "picture", "schema":{}}]
          """
      When we post to "archive" with success
          """
          [{
              "headline" : "item-1 headline",
              "guid" : "123",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-1 content",
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              }
          }, {
              "headline" : "item-2 headline",
              "guid" : "456",
              "state" : "submitted",
              "type" : "text",
              "body_html": "item-2 content",
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
                          "guid": "123",
                          "headline": "item-1 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "123"
                      }
                  ],
                  "role": "grpRole:main"
              },
              {
                  "id": "sidebars",
                  "refs": [
                      {
                          "renditions": {},
                          "slugline": "Boat",
                          "guid": "456",
                          "headline": "item-2 headline",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "456"
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
              "state" : "submitted",
              "type" : "composite"
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
                          "guid": "compositeitem",
                          "headline": "test package",
                          "location": "archive",
                          "type": "text",
                          "itemClass": "icls:text",
                          "residRef": "compositeitem"
                      }
                  ],
                  "role": "grpRole:main"
              }
          ],
              "task": {
                  "user": "#CONTEXT_USER_ID#",
                  "status": "todo",
                  "stage": "#desks.incoming_stage#",
                  "desk": "#desks._id#"
              },
              "guid" : "outercompositeitem",
              "headline" : "outer test package",
              "state" : "submitted",
              "type" : "composite"
          }]
          """
      When we publish "outercompositeitem" with "publish" type and "published" state
      Then we get error 400
      """
        {"_issues": {"validator exception": "['item-1 headline: ABSTRACT is a required field', 'item-2 headline: ABSTRACT is a required field', 'compositeitem: HEADLINE is a required field']"}, "_status": "ERR"}
      """