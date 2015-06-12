
Feature: Filter Condition

  @auth
  Scenario: Add a new filter condition
    Given empty "filter_condition"
    When we post to "/filter_condition" with success
    """
    [{"name": "sport", "field": "anpa-category", "operator": "in", "value": "4"}]
    """
    And we get "/filter_condition"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"name": "sport"}
        ]
    }
    """