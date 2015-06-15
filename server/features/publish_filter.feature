
Feature: Publish Filter

  @auth
  Scenario: Add a new publish filter
    Given empty "filter_condition"
    When we post to "/filter_condition" with success
    """
    [{"name": "sport", "field": "anpa-category", "operator": "in", "value": "4"}]
    """

    Then we get latest
#    When we post to "/filter_condition" with success
#    """
#    [{"name": "soccer", "field": "anpa-category", "operator": "in", "value": "1"},
#     {"name": "baseball", "field": "anpa-category", "operator": "in", "value": "2"},
#     {"name": "tennis", "field": "anpa-category", "operator": "in", "value": "3"},
#     {"name": "ski", "field": "anpa-category", "operator": "in", "value": "4"}]
#    """
    Given empty "publish_filter"
    When we post to "/publish_filter" with success
    """
    [{"publish_filter": [["#filter_condition._id#"]], "name": "soccer-only"}]
    """
    And we get "/publish_filter"
    Then we get list with 1 items
    """
    {
      "_items":
        [
          {"name": "soccer-only"}
        ]
    }
    """