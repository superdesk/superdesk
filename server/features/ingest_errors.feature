Feature: Macros

    @auth
    Scenario: Get list of all errors
        When we get "/ingest_errors"
        Then we get list with 1 items
            """
            {"_items":[{"all_errors":{"1001":"Message could not be parsed","1002":"Ingest file could not be parsed","1004":"NewsML1 input could not be processed","1006":"NITF input could not be processed","1008":"ZCZC input could not be processed","1009":"IPTC7901 input could not be processed","2004":"Ingest error","4000":"Unknown API ingest error","4001":"API ingest connection has timed out.","4002":"API ingest has too many redirects","4003":"API ingest has request error","4004":"API ingest Unicode Encode Error","4005":"API ingest xml parse error","4006":"API service not found(404) error","4007":"API authorization error","5000":"FTP ingest error","5001":"FTP parser could not be found","6000":"Email authentication failure","6002":"Email ingest error"}}]}
            """

    @auth
    Scenario: Get list of all errors for reuters
        When we get "/ingest_errors?source_type=reuters"
        Then we get list with 1 items
            """
            {"_items":[{"all_errors":{"1001":"Message could not be parsed","1002":"Ingest file could not be parsed"},"source_errors":{"4000":"Unknown API ingest error","4001":"API ingest connection has timed out.","4002":"API ingest has too many redirects","4003":"API ingest has request error","4004":"API ingest Unicode Encode Error","4005":"API ingest xml parse error"}}]}
            """

    @auth
    Scenario: Get list of all errors for email
        When we get "/ingest_errors?source_type=email"
        Then we get list with 1 items
            """
            {"_items":[{"all_errors":{"1001":"Message could not be parsed","1002":"Ingest file could not be parsed"},"source_errors":{"6000":"Email authentication failure","6002":"Email ingest error"}}]}
            """