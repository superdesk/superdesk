
Feature: Publish Filter

  @auth
  @vocabulary
  Scenario: Add a new publish filter
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa-category", "operator": "in", "value": "4"}]
    """

    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters" with success
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer-only"}]
    """
    Then we get latest
    When we post to "/publish_filters" with success
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"], "pf": ["#publish_filters._id#"]}}], "name": "complex"}]
    """
    And we get "/publish_filters"
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