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
