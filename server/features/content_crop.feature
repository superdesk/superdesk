Feature: Cropping the Image Articles

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
      When we patch "/archive/123"
      """
      {
        "renditions": {
          "4-3": {"CropLeft":0,"CropRight":800,"CropTop":0,"CropBottom":600},
          "16-9": {"CropLeft":0,"CropRight":1280,"CropTop":0,"CropBottom":720}
        }
      }
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


    @auth
    @vocabulary @test
    Scenario: Correct a picture with the crops succeeds
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
        },
        {
            "_id": "correct_picture",
            "act": "correct",
            "type": "picture",
            "schema": {
                "renditions": {
                    "type": "dict",
                    "required": false,
                    "schema": {
                        "4-3": {"type": "dict", "required": false},
                        "16-9": {"type": "dict", "required": false}
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
      When we patch "/archive/123"
      """
      {
        "renditions": {
          "4-3": {"CropLeft":0,"CropRight":800,"CropTop":0,"CropBottom":600},
          "16-9": {"CropLeft":0,"CropRight":1280,"CropTop":0,"CropBottom":720}
        }
      }
      """
      Then we get rendition "4-3" with mimetype "image/jpeg"
      And we get rendition "16-9" with mimetype "image/jpeg"
      When we post to "/subscribers" with success
      """
      {
      "name":"Channel 3","media_type":"media", "subscriber_type": "digital", "sequence_num_settings":{"min" : 1, "max" : 10}, "email": "test@test.com",
      "destinations":[{"name":"Test","format": "ninjs", "delivery_type":"PublicArchive","config":{"recipients":"test@test.com"}}]
      }
      """
      When we publish "123" with "publish" type and "published" state
      Then we get OK response
      When we publish "123" with "correct" type and "corrected" state
      """
      {
        "headline": "Testing",
        "renditions": {"4-3" : {"CropLeft":10,"CropRight":810,"CropTop":10,"CropBottom":610}}
      }
      """
      Then we get updated response
      """
      {
        "headline": "Testing",
        "renditions": {
          "4-3" : {"CropLeft":10,"CropRight":810,"CropTop":10,"CropBottom":610}
          }
      }
      """
      And we fetch a file "#rendition.4-3.href#"
      And we get error 404
      When we get "/archive/123"
      Then we get rendition "4-3" with mimetype "image/jpeg"
      And we get rendition "16-9" with mimetype "image/jpeg"
      And we fetch a file "#rendition.4-3.href#"
      And we get OK response


    @auth
    @vocabulary
    Scenario: Create a new crop of an Image Story succeeds using archive
      When upload a file "bike.jpg" to "archive" with "123"
      When we patch "/archive/123"
      """
      {"headline": "Adding Crop Image", "slugline": "crop image",
       "renditions": {
          "4-3": {"CropLeft":0,"CropRight":800,"CropTop":0,"CropBottom":600},
          "16-9": {"CropLeft":0,"CropRight":1280,"CropTop":0,"CropBottom":720}
        }
      }
      """
      Then we get OK response
      And we get rendition "4-3" with mimetype "image/jpeg"
      And we get rendition "16-9" with mimetype "image/jpeg"
      And we get existing resource
      """
      {"headline": "Adding Crop Image", "slugline": "crop image",
       "renditions": {
          "4-3": {
                    "CropLeft":0, "CropRight":800,
                    "CropTop":0,"CropBottom":600,
                    "mimetype": "image/jpeg",
                    "href": "#rendition.4-3.href#"
                 },
          "16-9": {
                    "CropLeft":0,
                    "CropRight":1280,
                    "CropTop":0,
                    "CropBottom":720,
                    "mimetype": "image/jpeg",
                    "href": "#rendition.16-9.href#"
                  }
        }
      }
      """
      And we fetch a file "#rendition.4-3.href#"
      And we get OK response
      When we patch "/archive/123"
      """
      {"headline": "replace crop", "slugline": "replace crop",
       "renditions": {
          "4-3": {"CropLeft":10,"CropRight":810,"CropTop":10,"CropBottom":610}
        }
      }
      """
      Then we get OK response
      And we fetch a file "#rendition.4-3.href#"
      And we get error 404
      When we get "/archive/123"
      Then we get rendition "4-3" with mimetype "image/jpeg"
      And we get rendition "16-9" with mimetype "image/jpeg"
      And we get existing resource
      """
      {"headline": "replace crop", "slugline": "replace crop",
       "renditions": {
          "4-3": {
                    "CropLeft":10, "CropRight":810,
                    "CropTop":10,"CropBottom":610,
                    "mimetype": "image/jpeg",
                    "href": "#rendition.4-3.href#"
                 },
          "16-9": {
                    "CropLeft":0,
                    "CropRight":1280,
                    "CropTop":0,
                    "CropBottom":720,
                    "mimetype": "image/jpeg",
                    "href": "#rendition.16-9.href#"
                  }
        }
      }
      """
      And we fetch a file "#rendition.4-3.href#"
      And we get OK response