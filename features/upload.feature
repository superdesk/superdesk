Feature: Upload

    @auth
    Scenario: Upload a binary file
        When we upload a binary file
        Then we get a file reference

    Scenario: Upload to local storage
        Given config
            """
            {"DEFAULT_FILE_STORAGE": "superdesk.storage.FileSystemStorage"}
            """

        When we upload a binary file
        Then we get a file reference
        And the file is stored localy
