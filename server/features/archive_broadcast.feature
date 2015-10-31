Feature: Archive Broadcast

  @auth @vocabulary
  Scenario: Create Archive Broadcast Content on a desk
    Given "desks"
      """
      [{"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}]
      """
    When we post to "archive"
      """
      [{
          "guid": "123",
          "type": "text",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key",
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "genre": [{"name": "Article", "value": "Article"}],
          "urgency": 1,
          "priority": 3,
          "family_id": "xyz",
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "body_html": "Take-1",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          }
      }]
      """
    Then we get OK response
    When we post to "archive/123/broadcast"
    """
    [{"desk": "#desks._id#"}]
    """
    Then we get OK response
    And we get updated response
      """
      {
          "type": "text",
          "slugline": "comics",
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "_current_version": 1,
          "urgency": 1,
          "priority": 3,
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "family_id": "xyz",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          },
          "genre": [{"name": "Broadcast Script", "value": "Broadcast Script"}],
          "broadcast": {
            "status": "",
            "master_id": "123"
          }
      }
      """
    When we get "archive/#broadcast._id#?version=all"
    Then we get list with 1 items
    And we get "archive/123" and match
      """
      {
          "guid": "123",
          "type": "text",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key",
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "broadcast_id": "#broadcast._id#",
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "genre": [{"name": "Article", "value": "Article"}],
          "urgency": 1,
          "priority": 3,
          "family_id": "xyz",
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "body_html": "Take-1",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          }
      }
      """

  @auth @vocabulary
  Scenario: Create Archive Broadcast Content on a personal workspace
    Given "desks"
      """
      [{"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}]
      """
    When we post to "archive"
      """
      [{
          "guid": "123",
          "type": "preformatted",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key",
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "genre": [{"name": "Article", "value": "Article"}],
          "urgency": 1,
          "priority": 3,
          "family_id": "xyz",
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "body_html": "Take-1",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          }
      }]
      """
    Then we get OK response
    When we post to "archive/123/broadcast"
    """
    [{}]
    """
    Then we get OK response
    And we get updated response
      """
      {
          "type": "preformatted",
          "slugline": "comics",
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "_current_version":1,
          "task": {
            "user": "#CONTEXT_USER_ID#"
          },
          "urgency": 1,
          "priority": 3,
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "family_id": "xyz",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          },
          "genre": [{"name": "Broadcast Script", "value": "Broadcast Script"}],
          "broadcast": {
            "status": "",
            "master_id": "123"
          }
      }
      """
    When we get "archive/#broadcast._id#?version=all"
    Then we get list with 1 items
    And we get "archive/123" and match
      """
      {
          "guid": "123",
          "type": "preformatted",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key",
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "broadcast_id": "#broadcast._id#",
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "genre": [{"name": "Article", "value": "Article"}],
          "urgency": 1,
          "priority": 3,
          "family_id": "xyz",
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "body_html": "Take-1",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          }
      }
      """

  @auth
  Scenario: Cannot create Archive Broadcast Content if Broadcast Script genre is not in vocabulary.
    Given "desks"
      """
      [{"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}]
      """
    When we post to "archive"
      """
      [{
          "guid": "123",
          "type": "text",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key",
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "genre": [{"name": "Article", "value": "Article"}],
          "urgency": 1,
          "priority": 3,
          "family_id": "xyz",
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "body_html": "Take-1",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          }
      }]
      """
    Then we get OK response
    When we post to "archive/123/broadcast"
    """
    [{}]
    """
    Then we get error 400
    """
    {"_message": "Cannot find the Broadcast Script genre."}
    """

  @auth @vocabulary
  Scenario: Cannot create Archive Broadcast Content if master story is not present
    Given "desks"
      """
      [{"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}]
      """
    When we post to "archive/123/broadcast"
    """
    [{}]
    """
    Then we get error 404
    """
    {"_message": "Cannot find the requested item id."}
    """

  @auth @vocabulary
  Scenario: Cannot create Archive Broadcast Content if content type is not text or preformatted
    Given "desks"
      """
      [{"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}]
      """
    When we post to "archive"
      """
      [{
          "guid": "123",
          "type": "picture",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key",
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "genre": [{"name": "Article", "value": "Article"}],
          "urgency": 1,
          "priority": 3,
          "family_id": "xyz",
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "body_html": "Take-1",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          }
      }]
      """
    Then we get OK response
    When we post to "archive/123/broadcast"
    """
    [{}]
    """
    Then we get error 400
    """
    {"_message": "Invalid content type."}
    """

  @auth @vocabulary
  Scenario: Cannot create Archive Broadcast Content if content state is spiked
    Given "desks"
      """
      [{"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}]
      """
    When we post to "archive"
      """
      [{
          "guid": "123",
          "type": "text",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key",
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "genre": [{"name": "Article", "value": "Article"}],
          "urgency": 1,
          "priority": 3,
          "family_id": "xyz",
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "body_html": "Take-1",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          }
      }]
      """
    Then we get OK response
    When we spike "123"
    Then we get OK response
    When we post to "archive/123/broadcast"
    """
    [{}]
    """
    Then we get error 400
    """
    {"_message": "Invalid content state."}
    """

  @auth @vocabulary
  Scenario: Cannot create Archive Broadcast Content if content state is killed
    Given "desks"
      """
      [{"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}]
      """
    And the "validators"
      """
      [
        {
            "schema": {},
            "type": "text",
            "act": "publish",
            "_id": "publish_text"
        },
        {
            "_id": "kill_text",
            "act": "kill",
            "type": "text",
            "schema": {}
        }
      ]
      """
    When we post to "archive"
      """
      [{
          "guid": "123",
          "type": "text",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key",
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "state": "in_progress",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "genre": [{"name": "Article", "value": "Article"}],
          "urgency": 1,
          "priority": 3,
          "family_id": "xyz",
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "body_html": "Take-1",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          }
      }]
      """
    Then we get OK response
    When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
    And we publish "#archive._id#" with "publish" type and "published" state
    Then we get OK response
    When we publish "#archive._id#" with "kill" type and "killed" state
    Then we get OK response
    When we post to "archive/123/broadcast"
    """
    [{}]
    """
    Then we get error 400
    """
    {"_message": "Invalid content state."}
    """

  @auth @vocabulary
  Scenario: Create Archive Broadcast Content if content state is published
    Given "desks"
      """
      [{"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}]
      """
    And the "validators"
      """
      [
        {
            "schema": {},
            "type": "text",
            "act": "publish",
            "_id": "publish_text"
        }
      ]
      """
    When we post to "archive"
      """
      [{
          "guid": "123",
          "type": "text",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key",
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "state": "in_progress",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "genre": [{"name": "Article", "value": "Article"}],
          "urgency": 1,
          "priority": 3,
          "family_id": "xyz",
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "body_html": "Take-1",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          }
      }]
      """
    Then we get OK response
    When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
    And we publish "#archive._id#" with "publish" type and "published" state
    Then we get OK response
    When we post to "archive/123/broadcast"
    """
    [{"desk": "#desks._id#"}]
    """
    Then we get OK response


  @auth @vocabulary
  Scenario: Create Archive Broadcast Content for takes package
    Given "desks"
      """
      [{"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}]
      """
    And the "validators"
      """
      [
        {
            "schema": {},
            "type": "text",
            "act": "publish",
            "_id": "publish_text"
        }
      ]
      """
    When we post to "archive"
      """
      [{
          "guid": "123",
          "type": "text",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key",
          "state": "in_progress",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "genre": [{"name": "Article", "value": "Article"}],
          "urgency": 1,
          "priority": 3,
          "family_id": "xyz",
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "body_html": "Take-1"
      }]
      """
    Then we get OK response
    When we post to "archive/123/link"
      """
      [{"desk": "#desks._id#"}]
      """
    Then we get next take as "TAKE"
      """
      {
          "type": "text",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key=2",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "state": "in_progress",
          "original_creator": "#CONTEXT_USER_ID#",
          "urgency": 1,
          "priority": 3
      }
      """
    When we post to "archive/#TAKE#/broadcast"
    """
    [{"desk": "#desks._id#"}]
    """
    Then we get OK response
    And we get updated response
      """
      {
          "type": "text",
          "slugline": "comics",
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "_current_version": 1,
          "urgency": 1,
          "priority": 3,
          "genre": [{"name": "Broadcast Script", "value": "Broadcast Script"}],
          "broadcast": {
            "status": "",
            "takes_package_id": "#TAKE_PACKAGE#",
            "master_id": "#TAKE#"
          }
      }
      """
    When we get "archive"
    Then we get list with 4 items
    """
    {
      "_items": [
        {
          "_id": "123",
          "type": "text",
          "slugline": "comics",
          "broadcast_id": "#broadcast._id#"
        },
        {
          "_id": "#TAKE#",
          "type": "text",
          "slugline": "comics",
          "broadcast_id": "#broadcast._id#"
        },
        {
          "_id": "#broadcast._id#",
          "type": "text",
          "slugline": "comics",
          "genre": [{"name": "Broadcast Script", "value": "Broadcast Script"}]
        },
        {
          "_id": "#TAKE_PACKAGE#",
          "type": "composite"
        }
      ]
    }
    """

  @auth @vocabulary
  Scenario: Spike the master story should spike the broadcast content
    Given "desks"
      """
      [{"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}]
      """
    When we post to "archive"
      """
      [{
          "guid": "123",
          "type": "text",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key",
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "genre": [{"name": "Article", "value": "Article"}],
          "urgency": 1,
          "priority": 3,
          "family_id": "xyz",
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "body_html": "Take-1",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          }
      }]
      """
    Then we get OK response
    When we post to "archive/123/broadcast"
    """
    [{"desk": "#desks._id#"}]
    """
    Then we get OK response
    And we get updated response
      """
      {
          "type": "text",
          "slugline": "comics",
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "_current_version": 1,
          "urgency": 1,
          "priority": 3,
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "family_id": "xyz",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          },
          "genre": [{"name": "Broadcast Script", "value": "Broadcast Script"}],
          "broadcast": {
            "status": "",
            "master_id": "123"
          }
      }
      """
    When we spike "123"
    Then we get OK response
    And we get "/archive/#broadcast._id#" and match
    """
    {
      "state": "spiked",
      "_id": "#broadcast._id#",
      "_current_version": 2,
      "broadcast": {
        "status": ""
      }
    }
    """

  @auth @vocabulary
  Scenario: Spike the broadcast content
    Given "desks"
      """
      [{"name": "Sports", "members": [{"user": "#CONTEXT_USER_ID#"}]}]
      """
    When we post to "archive"
      """
      [{
          "guid": "123",
          "type": "text",
          "headline": "headline",
          "slugline": "comics",
          "anpa_take_key": "take key",
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "genre": [{"name": "Article", "value": "Article"}],
          "urgency": 1,
          "priority": 3,
          "family_id": "xyz",
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "body_html": "Take-1",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          }
      }]
      """
    Then we get OK response
    When we post to "archive/123/broadcast"
    """
    [{"desk": "#desks._id#"}]
    """
    Then we get OK response
    And we get updated response
      """
      {
          "type": "text",
          "slugline": "comics",
          "state": "draft",
          "subject":[{"qcode": "17004000", "name": "Statistics"}],
          "anpa_category": [
                {"name": "Australian General News", "qcode": "a"}
          ],
          "task": {
              "user": "#CONTEXT_USER_ID#",
              "desk": "#desks._id#",
              "stage": "#desks.incoming_stage#"
          },
          "_current_version": 1,
          "urgency": 1,
          "priority": 3,
          "place": [{"qcode": "VIC", "name": "VIC"}],
          "family_id": "xyz",
          "dateline": {
            "source": "AAP",
            "text": "Los Angeles, Aug 11 AAP -"
          },
          "genre": [{"name": "Broadcast Script", "value": "Broadcast Script"}],
          "broadcast": {
            "status": "",
            "master_id": "123"
          }
      }
      """
    When we spike "#broadcast._id#"
    Then we get OK response
    And we get "/archive/#broadcast._id#" and match
    """
    {
      "state": "spiked",
      "_id": "#broadcast._id#",
      "_current_version": 2,
      "broadcast": {
        "status": ""
      }
    }
    """