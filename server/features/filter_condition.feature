
Feature: Filter Condition

  @auth
  @vocabulary
  Scenario: Add a new filter condition
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
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
  @vocabulary
  Scenario: Add second filter condition with same name fails
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
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
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "5"}]
    """
    Then we get error 400
    """
    {"_status": "ERR", "_issues": {"name": {"unique": 1}}}
    """

  @auth
  @vocabulary
  Scenario: Add a new filter condition with identical values fails
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
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
    [{"name": "sport2", "field": "anpa_category", "operator": "in", "value": "4"}]
    """
    Then we get error 400
    """
    {"_status": "ERR", "_message": "Filter condition:sport has identical settings"}
    """

  @auth
  @vocabulary
  Scenario: Add a new filter condition with invalid field fails

    Given empty "filter_conditions"

    When we post to "/filter_conditions"
    """
    [{"name": "sport", "field": "anpa_category", "operator": "like", "value": "4"}]
    """
    Then we get error 400
    """
    {"_status": "ERR", "_message": "Filter condition:sport has unidentified operator: like"}
    """

  @auth
  @vocabulary
  Scenario: Edit filter condition
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """
    And we get "/filter_conditions"
    When we patch "/filter_conditions/#filter_conditions._id#"
    """
    {"name": "politics"}
    """
    Then we get error 200

  @auth
  @vocabulary
  Scenario: Delete a referenced filter condition fails
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """

    Then we get latest
    Given empty "content_filters"
    When we post to "/content_filters" with success
    """
    [{"content_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer"}]
    """
    When we delete "/filter_conditions/#filter_conditions._id#"
    Then we get error 400
    """
    {"_status": "ERR", "_message": "Filter condition has been referenced in pf:soccer"}
    """