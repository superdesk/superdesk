
Feature: Publish Filter

  @auth
  @vocabulary
  Scenario: Add a new publish filter
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
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

  @auth
  @vocabulary
  Scenario: Add a new publish filter without global filter value
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """

    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters" with success
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer"}]
    """
    And we get "/publish_filters"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"is_global": false}
        ]
    }
    """

  @auth
  @vocabulary
  Scenario: Add a new publish filter with the same name fails
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """

    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters" with success
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer"}]
    """
    Then we get latest
    When we post to "/publish_filters"
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"], "pf": ["#publish_filters._id#"]}}], "name": "soccer"}]
    """
    Then we get error 400
    """
    {"_status": "ERR", "_issues": {"name": {"unique": 1}}}
    """

  @auth
  @vocabulary
  Scenario: Delete a referenced publish filter fails
    Given empty "filter_conditions"
    When we post to "/filter_conditions" with success
    """
    [{"name": "sport", "field": "anpa_category", "operator": "in", "value": "4"}]
    """

    Then we get latest
    Given empty "publish_filters"
    When we post to "/publish_filters" with success
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"]}}], "name": "soccer"}]
    """
    Then we get latest
    When we post to "/publish_filters" with success
    """
    [{"publish_filter": [{"expression": {"fc": ["#filter_conditions._id#"], "pf": ["#publish_filters._id#"]}}], "name": "tennis"}]
    """
    When we delete publish filter "soccer"
    Then we get error 400
    When we delete publish filter "tennis"
    Then we get error 204