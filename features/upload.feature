@wip
Feature: Upload

    @auth
    Scenario: Upload a binary file
        When we upload a binary file
        Then we get a file reference

    @auth
    Scenario: Upload a binary file with cropping
        When we upload a binary file with cropping
        Then we get a cropped file reference


    Scenario: Upload to local storage
        Given config
            """
            {"DEFAULT_FILE_STORAGE": "superdesk.storage.FileSystemStorage"}
            """

        When we upload a binary file
        Then we get a file reference
