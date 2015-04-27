
Feature: Formatted Item

  @auth
  Scenario: Add a new formatted item
    Given empty "archive"
    Given empty "output_channels"
    Given empty "subscribers"
    When we post to "/archive"
    """
    [{"headline": "test"}]
    """
    When we post to "/formatted_item" with success
    """
    {
      "item_id":"#archive._id#","item_version":"2","formatted_item":"This is the formatted item","format": "nitf"
    }
    """
    And we get "/formatted_item"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"formatted_item":"This is the formatted item"}
        ]
    }
    """

  @auth
  Scenario: Patch a formatted item
    Given empty "archive"
    When we post to "/archive"
    """
    [{"headline": "test"}]
    """
    When we post to "/formatted_item" with success
    """
    {
      "item_id":"#archive._id#","item_version":"2","formatted_item":"This is the formatted item","format":"nitf"
    }
    """
    And we get "/formatted_item"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"format":"nitf"}
        ]
    }
    """
    When we patch "/formatted_item/#formatted_item._id#"
    """
    {
      "format": "xml"
    }
    """
    And we get "/formatted_item"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"format":"xml"}
        ]
    }
    """

