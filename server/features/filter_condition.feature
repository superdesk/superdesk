
Feature: Filter Condition

  @auth
  Scenario: Add a new filter condition
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa-category", "operator": "in", "value": "4"}]
    """
    And we get "/filter_conditions"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"name": "sport"}
        ]
    }
    """

  @auth
  Scenario: Add a new filter condition with identical values fails
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa-category", "operator": "in", "value": "4"}]
    """
    And we get "/filter_conditions"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"name": "sport"}
        ]
    }
    """
    When we post to "/filter_conditions"
    """
    [{"name": "sport2", "field": "anpa-category", "operator": "in", "value": "4"}]
    """
    Then we get error 400
    """
    {"_status": "ERR", "_message": "Filter condition:sport has identical settings"}
    """

  @auth
  Scenario: Edit filter condition
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa-category", "operator": "in", "value": "4"}]
    """
    And we get "/filter_conditions"
    When we patch "/filter_conditions/#filter_conditions._id#"
    """
    {"name": "politics"}
    """
    Then we get error 200