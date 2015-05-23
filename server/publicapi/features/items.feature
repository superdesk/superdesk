Feature: Public content

    Scenario: Read an item
        Given "items"
        """
        [{"_id": "tag:example.com,0000:newsml_BRE9A605", "mimetype": "text/plain"}]
        """
        When we get "/items/tag:example.com,0000:newsml_BRE9A605"
        Then we get existing resource
        """
        {"_id": "tag:example.com,0000:newsml_BRE9A605", "mimetype": "text/plain"}
        """
