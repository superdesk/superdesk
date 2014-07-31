Feature: Upload

    @auth
    Scenario: Upload a binary file
        When we upload a file "bike.jpg" to "/upload"
        Then we get a file reference
        Then we get file metadata
        And we get "avatar" renditions
        And we can delete that file

    @auth
    Scenario: Upload a binary file with cropping
        When we upload a binary file with cropping
        Then we get a file reference
        Then we get file metadata
        And we get "avatar" renditions
        And we get cropped data smaller than "25000"
        And we can fetch a data_uri
        And we can delete that file
 
    @auth
    Scenario: Upload a file from URL with cropping
        When we upload a file from URL with cropping
        Then we get a file reference
        Then we get file metadata
        And we get "avatar" renditions
        And we get cropped data smaller than "30000"
        And we can fetch a data_uri
        And we can delete that file

    @auth
    Scenario: Upload a file from URL
        When we upload a file from URL
        Then we get a file reference
        Then we get file metadata
        And we get "avatar" renditions
        And we can fetch a data_uri
        And we can delete that file
 
    @amazon
    @auth
    Scenario: Upload a binary file
        When we upload a file "bike.jpg" to "/upload"
        Then we get a file reference
        Then we get file metadata
        And we get "avatar" renditions
        And we can delete that file

    @amazon
    @auth
    Scenario: Upload a binary file with cropping
        When we upload a binary file with cropping
        Then we get a file reference
        Then we get file metadata
        And we get cropped data smaller than "25000"
        And we can fetch a data_uri
        And we can delete that file
