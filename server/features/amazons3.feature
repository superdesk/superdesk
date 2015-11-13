Feature: Amazon S3 integration

    @auth
    @amazons3
    Scenario: Upload image into archive with storage on amazon S3
        Given empty "archive"
        When we upload a file "bike.jpg" to "archive"
        
        When we get "/archive"
        Then we get list with 1 items
        """
        {"_items": [{
        "renditions" : {
            "viewImage" : {
                "href" : "http://superdesk-test-eu-west-1.s3-eu-west-1.amazonaws.com/#archive.renditions.viewImage.media#",
                "mimetype" : "image/jpeg",
                "width" : 480,
                "media" : "#archive.renditions.viewImage.media#",
                "height" : 640
            },
            "thumbnail" : {
                "href" : "http://superdesk-test-eu-west-1.s3-eu-west-1.amazonaws.com/#archive.renditions.thumbnail.media#",
                "mimetype" : "image/jpeg",
                "width" : 90,
                "media" : "#archive.renditions.thumbnail.media#",
                "height" : 120
            },
            "original" : {
                "href" : "http://superdesk-test-eu-west-1.s3-eu-west-1.amazonaws.com/#archive.renditions.original.media#",
                "mimetype" : "image/jpeg",
                "width" : 1200,
                "media" : "#archive.renditions.original.media#",
                "height" : 1600
            },
            "baseImage" : {
                "href" : "http://superdesk-test-eu-west-1.s3-eu-west-1.amazonaws.com/#archive.renditions.baseImage.media#",
                "mimetype" : "image/jpeg",
                "width" : 1050,
                "media" : "#archive.renditions.baseImage.media#",
                "height" : 1400
            }
        }   
        }]}
        """