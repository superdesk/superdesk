Feature: Upload

    @amazon
    Scenario: Upload a binary file
        When we upload a binary file to "/upload"
        Then we get a file reference
        And the file is not serialized in response
        And we can delete that file

    @amazon
    Scenario: Upload a binary file and enable file to be included in the response
        Given config
            """
            {"RETURN_MEDIA_AS_BASE64_STRING": "True"}
            """
        When we upload a binary file to "/upload"
        Then we get a file reference
        And the file is serialized in response
        And we can delete that file

    @amazon
    Scenario: Upload a binary file with cropping
        When we upload a binary file with cropping
        Then we get a file reference
        And the file is not serialized in response
        And we get cropped data
        And we can fetch a data_uri
        And we can delete that file

    Scenario: Upload to local storage
        Given config
            """
            {"DEFAULT_FILE_STORAGE": "superdesk.storage.FileSystemStorage"}
            """

        When we upload a binary file to "/upload"
        Then we get a file reference
