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
      {"_issues": {"validator exception": "['A packaged item is locked']"}, "_status": "ERR"}
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
        {"_issues": {"validator exception": "[['ABSTRACT is a required field']]"}, "_status": "ERR"}
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
        {"_issues": {"validator exception": "['Package contains killed or spike item']"}, "_status": "ERR"}
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
      Then we get error 200
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
      Then we get error 200
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
        Then we get "#archive.123.take_package#" in formatted output as "main" story



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
      Then we get error 200
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
      Then we get "#archive.123.take_package#" in formatted output as "main" story
      Then we get "#archive.123.take_package#" in formatted output as "sidebars" story



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
      Then we get error 200
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
      Then we get error 200
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
      Then we get "#archive.123.take_package#" in formatted output as "main" story



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
      Then we get error 200
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