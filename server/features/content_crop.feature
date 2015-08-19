Feature: Cropping the Image Articles

    @auth
    @vocabulary
    Scenario: Create a new crop of an Image Story succeeds
      When upload a file "bike.jpg" to "archive" with "123"
      When we post to "/archive/123/crop/4-3"
      """
      {"CropLeft":0,"CropRight":800,"CropTop":0,"CropBottom":600}
      """
      When we get "/archive/123"
      Then we get existing resource
      """
      {"renditions": {"4-3": {"mime_type": "image/jpeg", "CropBottom":600}}}
      """

    @auth
    @vocabulary
    Scenario: Create a new crop of an Image Story with random name fails
      When upload a file "bike.jpg" to "archive" with "123"
      When we post to "/archive/123/crop/little"
      """
      {"CropLeft":0,"CropRight":40,"CropTop":0,"CropBottom":30}
      """
      Then we get error 400
      """
      {"_message": "Unknown crop name!", "_status": "ERR"}
      """

    @auth
    @vocabulary
    Scenario: Create a new crop of an Image Story with wrong aspect ratio fails
      When upload a file "bike.jpg" to "archive" with "123"
      When we post to "/archive/123/crop/4-3"
      """
      {"CropLeft":0,"CropRight":850,"CropTop":0,"CropBottom": 900}
      """
      Then we get error 400
      """
      {"_message": "Wrong aspect ratio!", "_status": "ERR"}
      """

    @auth
    @vocabulary
    Scenario: Create a new crop of an Image Story with wrong width
      When upload a file "bike.jpg" to "archive" with "123"
      When we post to "/archive/123/crop/4-3"
      """
      {"CropLeft":0,"CropRight":400,"CropTop":0,"CropBottom": 700}
      """
      Then we get error 400
      """
      {"_message": "Wrong crop size. Minimum crop size is 800x600.", "_status": "ERR"}
      """

    @auth
    @vocabulary
    Scenario: Create a new crop of an Image Story with wrong height
      When upload a file "bike.jpg" to "archive" with "123"
      When we post to "/archive/123/crop/4-3"
      """
      {"CropLeft":0,"CropRight":800,"CropTop":0,"CropBottom": 500}
      """
      Then we get error 400
      """
      {"_message": "Wrong crop size. Minimum crop size is 800x600.", "_status": "ERR"}
      """

    @auth
    @vocabulary
    Scenario: Delete an existing crop of an Image Story succeeds
      When upload a file "bike.jpg" to "archive" with "123"
      When we post to "/archive/123/crop/4-3"
      """
      {"CropLeft":0,"CropRight":800,"CropTop":0,"CropBottom":600}
      """
      When we get "/archive/123"
      Then we get existing resource
      """
      {"renditions": {"4-3": {"mime_type": "image/jpeg", "CropRight": 800}}}
      """
      When we delete "/archive/123/crop/4-3"
      Then we get response code 204

    @auth
    Scenario: Publish a picture without the crops fails
      Given the "validators"
      """
        [
        {
            "_id": "publish_picture",
            "act": "publish",
            "type": "picture",
            "schema": {
                "renditions": {
                    "type": "dict",
                    "required": true,
                    "schema": {
                        "4-3": {"type": "dict", "required": true},
                        "16-9": {"type": "dict", "required": true}
                    }
                }
            }
        }
        ]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      When upload a file "bike.jpg" to "archive" with "123"
      And we post to "/archive/123/move"
      """
      [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
      """
      When we post to "/subscribers" with success
      """
      {
        "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
        "destinations":[{"name":"Test","format": "nitf", "delivery_type":"email","config":{"recipients":"test@test.com"}}]
      }
      """
      When we publish "123" with "publish" type and "published" state
      Then we get response code 400
      """
      {
          "_issues": {"validator exception": "[['RENDITIONS is a required field']]"}
      }
      """

    @auth
    @vocabulary
    Scenario: Publish a picture with the crops succeeds
      Given the "validators"
      """
        [
        {
            "_id": "publish_picture",
            "act": "publish",
            "type": "picture",
            "schema": {
                "renditions": {
                    "type": "dict",
                    "required": true,
                    "schema": {
                        "4-3": {"type": "dict", "required": true},
                        "16-9": {"type": "dict", "required": true}
                    }
                }
            }
        }
        ]
      """
      And "desks"
      """
      [{"name": "Sports"}]
      """
      When upload a file "bike.jpg" to "archive" with "123"
      And we post to "/archive/123/move"
      """
      [{"task": {"desk": "#desks._id#", "stage": "#desks.incoming_stage#"}}]
      """
      When we post to "/archive/123/crop/4-3"
      """
      {"CropLeft":0,"CropRight":800,"CropTop":0,"CropBottom":600}
      """
      When we post to "/archive/123/crop/16-9"
      """
      {"CropLeft":0,"CropRight":1280,"CropTop":0,"CropBottom":720}
      """
      When we post to "/subscribers" with success
      """
      {
      "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
      "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
      }
      """
      When we publish "123" with "publish" type and "published" state
      Then we get OK response
