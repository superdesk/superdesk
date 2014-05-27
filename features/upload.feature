@wip
Feature: Upload

    @auth
    Scenario: Upload a binary file
        When we upload a binary file
        Then we get a file reference
        And we can delete that file

    @auth
    Scenario: Upload a binary file with cropping
        When we upload a binary file with cropping
        Then we get a file reference
        And we get cropped data
        And we can fetch a data_uri
        And we can delete that file

    @auth
    Scenario: Upload a binary file to Amazon S3
        Given config
            """
            {
                "AMAZON_CONTAINER_NAME": "superdesk-test",
                "AMAZON_ACCESS_KEY_ID": "some-dummy-access-key",
                "AMAZON_SECRET_ACCESS_KEY": "dummy-secret-key",
                "AMAZON_REGION": "s3_eu_west"
            }
            """

        When we upload a binary file
        Then we get a file reference
        And we can delete that file


    @auth
    Scenario: Upload a binary file with cropping to Amazon S3
        Given config
            """
            {
                "AMAZON_CONTAINER_NAME": "superdesk-test",
                "AMAZON_ACCESS_KEY_ID": "some-dummy-access-key",
                "AMAZON_SECRET_ACCESS_KEY": "dummy-secret-key",
                "AMAZON_REGION": "s3_eu_west"
            }
            """

        When we upload a binary file with cropping
        Then we get a file reference
        And we get cropped data
        And we can fetch a data_uri
        And we can delete that file
    

    Scenario: Upload to local storage
        Given config
            """
            {"DEFAULT_FILE_STORAGE": "superdesk.storage.FileSystemStorage"}
            """

        When we upload a binary file
        Then we get a file reference
