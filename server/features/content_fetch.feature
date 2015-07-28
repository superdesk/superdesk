Feature: Fetch Items from Ingest

    @auth
    @provider
    Scenario: Fetch an item
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And ingest from "reuters"
      """
      [{"guid": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E"}]
      """
      When we post to "/ingest/tag_reuters.com_2014_newsml_LOVEA6M0L7U2E/fetch"
      """
      {"desk": "#desks._id#"}
      """
      Then we get new resource
      When we get "/archive?q=#desks._id#"
      Then we get list with 1 items
      """
      {"_items": [
      	{
      		"family_id": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E", 
      		"ingest_id": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E",
      		"operation": "fetch"
      	}
      ]}
      """

    @auth
    @provider
    Scenario: Fetch an item of type Media
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      When we fetch from "reuters" ingest "tag_reuters.com_0000_newsml_GM1EA7M13RP01"
      And we post to "/ingest/#reuters.tag_reuters.com_0000_newsml_GM1EA7M13RP01#/fetch" with success
      """
      {
      "desk": "#desks._id#"
      }
      """
      Then we get "_id"
      When we get "/archive/#_id#"
      Then we get existing resource
      """
      {
          "renditions": {
              "baseImage": {"height": 845, "mimetype": "image/jpeg", "width": 1400},
              "original": {"height": 2113, "mimetype": "image/jpeg", "width": 3500},
              "thumbnail": {"height": 120, "mimetype": "image/jpeg", "width": 198},
              "viewImage": {"height": 386, "mimetype": "image/jpeg", "width": 640}
          }
      }
      """

    @auth
    @provider
    @test
    Scenario: Fetch a package
      Given empty "ingest"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      When we fetch from "reuters" ingest "tag_reuters.com_2014_newsml_KBN0FL0NM"
      And we post to "/ingest/#reuters.tag_reuters.com_2014_newsml_KBN0FL0NM#/fetch"
      """
      {
      "desk": "#desks._id#"
      }
      """
      And we get "archive"
      Then we get existing resource
      """
      {
          "_items": [
              {
                  "_current_version": 1,
                  "linked_in_packages": [{}],
                  "state": "fetched",
                  "type": "picture"
              },
              {
                  "_current_version": 1,
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
                  "state": "fetched",
                  "type": "composite"
              },
              {
                  "_current_version": 1,
                  "linked_in_packages": [{}],
                  "state": "fetched",
                  "type": "picture"
              },
              {
                  "_current_version": 1,
                  "linked_in_packages": [{}],
                  "state": "fetched",
                  "type": "text"
              },
              {
                  "_current_version": 1,
                  "linked_in_packages": [{}],
                  "state": "fetched",
                  "type": "picture"
              },
              {
                  "_current_version": 1,
                  "linked_in_packages": [{}],
                  "state": "fetched",
                  "type": "text"
              }
          ]
      }
      """

    @auth
    @provider
    Scenario: Fetch same ingest item to a desk twice
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And ingest from "reuters"
      """
      [{"guid": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E"}]
      """
      When we post to "/ingest/tag_reuters.com_2014_newsml_LOVEA6M0L7U2E/fetch"
      """
      {"desk": "#desks._id#"}
      """
      And we post to "/ingest/tag_reuters.com_2014_newsml_LOVEA6M0L7U2E/fetch"
      """
      {"desk": "#desks._id#"}
      """
      Then we get new resource
      When we get "/archive?q=#desks._id#"
      Then we get list with 2 items
      """
      {"_items": [
              {"family_id": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E"},
              {"family_id": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E"}
              ]}
      """

    @auth
    Scenario: Fetch should fail when invalid ingest id is passed
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And empty "ingest"
      When we post to "/ingest/invalid_id/fetch"
      """
      {
      "desk": "#desks._id#"
      }
      """
      Then we get error 404
      """
      {"_message": "Fail to found ingest item with _id: invalid_id", "_status": "ERR"}
      """

    @auth
    @provider
    Scenario: Fetch should fail when no desk is specified
      Given empty "archive"
      When we fetch from "reuters" ingest "tag_reuters.com_0000_newsml_GM1EA7M13RP01"
      When we post to "/ingest/tag_reuters.com_0000_newsml_GM1EA7M13RP01/fetch"
      """
      {}
      """
      Then we get error 400
      """
      {"_issues": {"desk": {"required": 1}}}
      """

    @auth
    @provider
    Scenario: Fetched item should have "in_progress" state when locked and edited
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And ingest from "reuters"
      """
      [{"guid": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E"}]
      """
      When we post to "/ingest/tag_reuters.com_2014_newsml_LOVEA6M0L7U2E/fetch"
      """
      {"desk": "#desks._id#"}
      """
      Then we get "_id"
      When we post to "/archive/#_id#/lock"
      """
      {}
      """
      And we patch "/archive/#_id#"
      """
      {"headline": "test 2"}
      """
      Then we get existing resource
      """
      {"headline": "test 2", "state": "in_progress", "task": {"desk": "#desks._id#"}}
      """

    @auth
    @provider
    Scenario: User can't fetch content without a privilege
      Given empty "archive"
      And "desks"
      """
      [{"name": "Sports"}]
      """
      And ingest from "reuters"
      """
      [{"guid": "tag_reuters.com_2014_newsml_LOVEA6M0L7U2E"}]
      """
      When we login as user "foo" with password "bar" and user type "user"
      """
      {"user_type": "user", "email": "foo.bar@foobar.org"}
      """
      And we post to "/ingest/tag_reuters.com_2014_newsml_LOVEA6M0L7U2E/fetch"
      """
      {"desk": "#desks._id#"}
      """
      Then we get response code 403
