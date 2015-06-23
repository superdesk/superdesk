
Feature: Publish Filter

  @auth
  Scenario: Add a new publish filter
    Given empty "filter_condition"
    When we post to "/filter_condition" with success
    """
    [{"name": "sport", "field": "anpa-category", "operator": "in", "value": "4"}]
    """

    Then we get latest
    Given empty "publish_filter"
    When we post to "/publish_filter" with success
    """
    [{"publish_filter": [[{"fc": "#filter_condition._id#"}]], "name": "soccer-only"}]
    """
    Then we get latest
    When we post to "/publish_filter" with success
    """
    [{"publish_filter": [[{"fc": "#filter_condition._id#"}], [{"pf":"#publish_filter._id#"}]], "name": "complex"}]
    """
    And we get "/publish_filter"
    Then we get list with 2 items
    """
    {
      "_items":
        [
          {"name": "soccer-only"},
          {"name": "complex"}
        ]
    }
    """