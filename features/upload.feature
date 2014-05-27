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

    @amazon
    Scenario: Upload a binary file to Amazon S3
        When we upload a binary file
        Then we get a file reference
        And we can delete that file


    @amazon
    Scenario: Upload a binary file with cropping to Amazon S3
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
